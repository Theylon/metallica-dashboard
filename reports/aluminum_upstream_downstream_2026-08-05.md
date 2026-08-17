# Aluminum: upstream rally vs downstream collapse — investigation & remap

**Date:** 2026-08-05 · **Sources:** owner-supplied component decomposition, MetalMiner MCP
(MMO August 2026, published 2026-08-03; June 2026 Annual Outlook), live book (`data/positions.json`),
OM linkage research (`data/micro.json`).

## What's happening

The aluminum complex has split in two:

| Component | 21-session | 63-session |
|---|---|---|
| LME primary cash | **+4.87%** | −9.95% |
| China primary cash | +3.27% | −2.87% |
| India primary | +3.59% | −7.06% |
| US Midwest premium | −0.23% | −6.30% |
| US sheet/plate (all 6 grades) | **−3.5% to −4.2%** | −6.4% to −7.7% |
| Aluminum MMI (composite) | +3.19% | −4.20% |

The rally is **upstream primary metal**; the weakness is **US semi-fabricated products**.
A US sheet price ≈ LME primary + Midwest premium + conversion margin. With LME up ~5%
in a month and the premium flat, the sheet decline means the **conversion (fabrication)
margin collapsed** — roughly $4,310/t → $3,850/t of sheet-minus-LME spread, mills giving
back ~$460/t (~11% of the spread) in 21 sessions.

## MetalMiner verification (MMO August 2026, June 2026 Annual Outlook)

- **Primary bottomed and is consolidating**: "Following sharp declines throughout June,
  aluminum prices found a bottom and consolidated in July. Prices witnessed a modest 2.15%
  month-over-month increase to close July at **$3,179/mt**." Drivers scored: Iran conflict (+),
  Chinese exports (−), Midwest Premium (+), lower USD (+).
- **Supply-side tightness is real**: Gulf conflict left an estimated **2–3.5M mt of smelter
  capacity offline** (two Gulf smelters damaged; Hormuz/Red Sea logistics constrained;
  Norsk Hydro warning of deepening deficits). Offset: Chinese smelters at 99% capacity,
  Chinese aluminum **exports +45% in June**. The Annual Outlook flags a deficit year and a
  "higher price floor," and notes Century Aluminum restart timelines run "well beyond a
  normal ramp-up period" — supply relief will be slow.
- **Midwest premium consolidating, not rising**: "Both LME prices and the Midwest Premium
  appeared to consolidate following sharp declines the previous month." (June baseline:
  $1.17/lb, +29.2% YTD — the premium has since faded, consistent with −6.3%/63-session.)
- **Downstream is mixed-to-weak on price despite busy mills**: common-alloy semis "remain
  well-supplied" (only specialty 6000-series plate/tread is tight); for the 2027 contracting
  season, "domestic producers are quoting a wide range (**25–35 cents**) for conversion
  costs" — mills competing on the conversion component, exactly the margin that collapsed.
- **Buying stance stays neutral**: "organizations may continue to **purchase as needed**"
  until a confirmed breakout — unchanged from July, i.e. MetalMiner is not yet calling the
  primary rally a resumed uptrend.

**Net read:** a global/upstream primary rally (supply outages, tight metal units, LME
backwardation) coinciding with weak US downstream demand and import-fed conversion-price
competition. Buyers of metal units pay more; buyers of finished sheet pay less. Both are true.

## What it means for the book

- **AA (short 2 sh, avg 43.49, last 47.51) and CENX (short 2 sh, avg 43.01, last 46.92)**
  are **smelters, priceSens 3/3** (AA: "$40M/yr per $100 LME move"; CENX: "LME/Midwest/EDPP
  explicit revenue components"). They are long the leg that is rallying. Both shorts are
  ~9% underwater; realized to date AA −21.63, CENX −8.78, winRate 0.0 across the aluminum
  complex. The standing "KEEP" recommendations in micro.json date from the falling-LME
  thesis (bias asOf 2026-07-12, built on June's −15.6%) that has since reversed.
  **Recommendation (analysis only, no order prepared): reassess the AA/CENX shorts —
  the physical-market evidence (deficit, slow restarts, backwardation) argues the squeeze
  can continue; if the house view stays short aluminum, the cleaner expression is the
  downstream/conversion-margin leg, not smelter equity.**
- **KALU (fabricator, priceSens 1, "passes LME through to customers") was the one name the
  physical data fit** — and it was exited today (−26.13 realized, 0% winrate, flagged at
  entry by both review reports as "not an aluminum-price short"). Post-mortem: the mapping
  scored it inside the same aluminum bucket as the smelters, so the strategy couldn't see
  the distinction it had itself researched.
- **Signal note:** the spread signal that would capture this cleanly (momentum of US sheet
  minus LME — `al_premium_spread`, family 5) lives in the metallica-fund research record and
  was not promoted into the frozen v1 menu. Promotion is a metallica-fund change, out of
  scope here, but this episode is the evidence case for it.

## Remap shipped with this report

`scripts/exposure.py` now tiers each name's primary-metal link by its curated price
sensitivity (micro.json OM linkage): **priceSens 3 → T1 (1.0), 2 → T2 (0.5), 1 → no
metal-price link** (mined correlations are also suppressed for priceSens-1 names). Effects
on the live book: KALU/CSTM would carry no aluminum link (conversion-margin businesses);
MTUS and PKX (surcharge/partial pass-through, priceSens 2) drop to half weight; LAC
(priceSens 2) halves; AA/CENX stay full-weight aluminum — which is what makes the current
short-vs-rally tension visible on the dashboard instead of averaged away.
`scripts/verify_data.py` treats priceSens-1 names as legitimately unmapped.

## Data gaps this episode exposed (follow-ups, not fixed here)

1. **No aluminum price series in the repo at all**: `enrich.py` `METAL_SPOT` is
   Lithium/Copper/Cobalt/Nickel — aluminum never lands in `data/metals_spot.json`.
2. **No downstream/semi-fab or Midwest-premium series anywhere** — the runbooks
   (`scripts/altdata_refresh.md`, `scripts/micro_refresh_research.md`) query primary LME
   only; add canonical queries for US sheet/plate and the Midwest premium so the
   upstream/downstream spread is observable.
3. **Commodity bias staleness**: the aluminum bias driving shorts was 24 days old and
   predicated on a falling LME; the divergence was structurally invisible to the pipeline.
