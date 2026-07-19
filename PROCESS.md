# The Quantitative Investment Process

This document codifies the process the dashboard implements: how raw information
channels are validated, how validated channels become scores and recommendations,
and the hard risk rules that override everything else. The goal is to minimize
subjective judgment — data flows into the system, the system produces the decision
and records *why*, and the record is reviewed against outcomes.

```
information channels          validation                 decision layer
────────────────────          ──────────────────         ─────────────────────────
alt-data KPIs (CarbonArc,     channel_accuracy.py        micro scores 0-100
 FMP consensus, MetalMiner)    · MedAE vs actuals         (micro_build / micro_refresh)
analyst consensus + accuracy   · ≥80% trust gate                │
insiders / politicians        signal_ic.py                recommendations
 (positioning_build.py)        · rank-IC vs fwd returns    (action + urgency)
sentiment / SmartScore        cross-validation                 │
momentum (90d price action)    (Yahoo vs FMP/TipRanks)    decision_log.jsonl
commodity bias (MetalMiner)                                (trigger + outcome review)
                                                               │
                                                          hard risk rules
                                                           (alerts_build.py)
```

## 1. Channel validation — earn trust before driving decisions

Every channel is backtested against the thing it claims to predict
(`scripts/channel_accuracy.py` → `data/channel_accuracy.json`, Process tab):

- **KPI channels** (consensus, and our own alt-data nowcasts once calibrated) are
  measured per quarter against reported actuals over the tracked history (target:
  4–12 quarters). Error metric: **Median Absolute Error** (MedAE) of the estimate
  vs reported; `accuracy % = 100 − MedAE`. Our nowcasts additionally track
  `beatConsensusPct` — the share of quarters we were closer to reported than the
  street was.
- **Score channels** (the eight micro sub-scores + composite) are measured by the
  rank-IC engine (`signal_ic.py`): Spearman correlation of each score with the
  20-day-forward return; accuracy = the hit rate of positive-IC windows.
- **Direction channels** (commodity bias, insiders, politicians) are measured as
  the hit rate of each directional call vs the 20-snapshot-forward return of the
  named ticker.
- **Cross-validation** (Yahoo vs FMP/TipRanks) is a consistency measure between
  similar sources to catch bias in either — informational, never gated.

**The 80% gate.** A channel is **trusted** only when its accuracy clears **80%**
on enough observations (KPI: ≥2 quarters; scores: ≥5 IC windows; direction: ≥10
aged calls). Measured-but-below is **probation**: it stays on the dashboard for
observation but is *display-only — never a decision input*. Channels without
enough history are **accumulating** and are treated like probation until they
graduate.

## 2. Target prediction

Where a trusted alt-data channel exists for a KPI, the strongest channels are
combined into our own estimate (`kpi.ourEst` in `data/altdata.json`, per
`scripts/altdata_refresh.md` Phase 2). The estimate is compared retroactively to
consensus and to actuals over at least 4 quarters before it may influence a
position around an earnings event — and even then, rule 4a still applies.

## 3. Scoring and recommendations

Validated inputs feed the composite micro-score (0–100, weights in
`data/micro.json.methodology`), with momentum — the most consistently profitable
factor — carrying the largest weight, measured over ~90 days (vs 50/200-DMA and
the 52-week range). Scores rank within material groups; recommendations
(action + urgency) are generated per held leg and for new ideas.

## 4. Hard risk rules

These override any score or signal (surfaced by `scripts/alerts_build.py` on the
Process tab and the Overview banner):

- **4a. Close/reduce before earnings.** A held single-stock position into an
  earnings print is a binary bet on a high-volatility event; the process closes
  or reduces it beforehand *even when the alt-data is favorable* (e.g. the TSLA
  Jul-22 case: bullish registrations data, position still covered pre-print).
- **4b. Sector hedging via ETFs.** Prefer expressing sector-level risk through
  ETFs (XME for metals, KARS for EV) over adding single-name event risk,
  accepting that an ETF never fully covers the residual name-specific risk.
- **4c. Leading indicators over lagging prints.** For steel shorts (CLF, STLD,
  NUE), the HRC (Hot-Rolled Coil) price is the leading indicator: HRC strength /
  tight domestic supply ⇒ cover or avoid shorts on domestic mills regardless of
  the equity screen.
- **4d. Insider asymmetry.** There are many reasons for an insider to sell (tax,
  RSU vesting, 10b5-1 plans, diversification) but only one reason to buy — the
  belief the price will rise. Open-market buys are always a signal; sells count
  only when classified discretionary (`scripts/positioning_build.py`).
- **4e. Micro overrides must be logged.** Macro (commodity bias) sets the
  default direction; a micro stock-pick may contradict it, but the contradiction
  is flagged (`microOverride`) in the decision log and stays visible as an alert
  until resolved.

## 5. The decision log — record the "why", review the outcome

Every recommendation change (action/urgency) and every held-side change is
appended to `data/decision_log.jsonl` automatically by the build/refresh
pipeline (`scripts/decision_log.py` hooked into `micro_build.py` /
`micro_refresh.py`): the trigger (which sub-scores moved, composite from→to), a
price/score snapshot, the macro context, the `microOverride` flag and the
source. After 30 and 90 days the entry's `outcome` is backfilled with the raw
forward price return (interpret against `snapshot.held`: a short wants a
negative number). The Process tab renders the log filterable; the review
question is always *"was the trigger right, and did the process follow its own
rules?"* — not merely whether the trade made money.

## 6. What accumulates, and when each gate turns on

| Piece | Turns on |
|---|---|
| KPI consensus channels | live now (3 quarters tracked per name) |
| `kpi.ourEst.*` (our nowcasts) | after altdata Phase 2 calibration (≥2 paired quarters) |
| Score channels (rank-IC) | ≥25 daily snapshots (`signal_scorecard.json` shows progress) |
| Commodity-bias direction channel | ≥25 snapshot days of `biasDir` (recorded from 2026-07-20) |
| Insider / politician channels | ≥10 calls aged ≥20 snapshots after the first positioning Routine run |
| Decision-log outcomes | 30/90 days after each entry |
