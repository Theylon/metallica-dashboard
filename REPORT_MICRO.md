# Metallica — Micro-Analysis & Stock-Picking Report

**As of:** 2026-07-12 · **NAV:** ~$10,953 · **Book:** 27 positions, gross ~69%, net ~-31%
**Sources:** IBKR (live positions), FMP (quotes/momentum), TipRanks (analyst refresh), Bigdata.com (news/filings/transcripts), Carbon Arc (US vehicle registrations), MetalMiner Excel universe (204 names, OM linkage + enrichment).
**Not available this session:** MetalMiner MCP (tool calls require approval) — commodity biases were derived from FMP price series + ETF momentum + Bigdata.com narrative instead. FMP is on the Free plan (per-symbol commodity quotes and analyst endpoints blocked; batch quotes worked).

---

## 1. Commodity bias layer (top-down sign per group)

| Material | Bias | Conf. | Core evidence |
|---|---|---|---|
| Carbon/Raw Steel | **LONG** | high | US HRC >$1,100/st, 50% S232 tariffs, imports -26% YoY, tight supply |
| Copper | **LONG** | med | LME ~$13.4K, falling stocks, negative TCs, US tariff decision = live bullish catalyst |
| Rare Earths | **LONG** | med | NdPr +73.6% YoY H1, supply gap widening (CITIC), equities lag the commodity |
| Zinc/Lead/**Tin** | **LONG** | med | Tin $53K: Myanmar supply broken + AI solder demand; zinc mine supply tight |
| Lithium | neutral | low | Carbonate +1/3 YTD & DoD $300M stockpile vs CATL restart + W-Africa supply wave |
| Nickel & Stainless | neutral | med | Weak oscillation; Indonesia July quota decision is the swing factor |
| Aluminum | **SHORT** | med | War premium unwound (June -16%, worst since 2008); China/Indonesia supply up |
| Gold / Silver | **SHORT** | med/low | Hawkish Fed, 64% Sept-hike odds, HSBC cuts; but Q4 dollar-downtrend = rebound risk |
| PGM | **SHORT** | high | Platinum -21..27% off record, UBS cut $300/oz, palladium structural surplus |

**Macro overlay:** hawkish Fed + strong dollar + US-Iran headline volatility; the whole metals complex is correcting off a H1 melt-up (GDX -14% below 200DMA, REMX -16% below 50DMA, silver halved from the January $115 squeeze peak). Watch **US CPI July 14**.

## 2. The headline finding: the steel shorts fight their own commodity

The book's largest gross block (~$2.8K short: NUE, STLD, RS, CLF) is short the **strongest** commodity group on the board. Within-group micro makes it worse:

| Name | Held | Consensus | PT / upside | Micro read |
|---|---|---|---|---|
| NUE | short | Buy (8/2/0) | $270 / +18.8% | HRC margin leader, +23% in 3M — **cover** |
| STLD | short | Buy (6/3/0) | $265 / +16.1% | Sinton ramp + aluminum optionality — **cover** |
| RS | short | Neutral (2/4/1) | $381 / **+0.5%** | Fully-valued distributor — the one street-endorsed short — **keep** |
| CLF | short | Neutral (**0 buys**) | $11.25 / +19.7% | -23%/month, negative EPS revisions — right short, but **7/23 earnings is binary → trim 1/3** |
| CMC | — | Buy (8/3/0) | $80.45 / +28.4% | Best long candidate in the group |
| ASTL (new) | — | — | — | Canadian mill selling into the tariff wall, -23% vs 50DMA — replacement short |

## 3. Lithium/EV complex — keep the pair, fix two legs

* **Longs confirmed:** SGML is the strongest micro in the complex (Q2 production beat +6%, AISC $710→$620/t, CF-positive at $1,500/t; financials 8/14). ALB (Zacks #1, Q1 EBITDA +148% YoY, Buy +71% PT — but sell-side PTs still being cut), SQM (cost-curve winner), LAC (funded Thacker-Pass option: DOE $2.23B, >95% engineering; GS initiated Neutral $4.50 — keep small, no add).
* **TSLA short is the weak leg:** record Q2 deliveries 480K (+25% YoY, beat by 74K); Carbon Arc US registrations accelerate every month (Jan 30.3K → May 47.4K); UBS expects a margin beat on **July 22**. Cover before earnings; KARS (China-heavy EV ETF, no earnings date) stays as the downstream-EV short.
* **BATT + LIT double-short is redundant** — both hold ALB/SQM (you are shorting your own longs twice). Keep LIT only.

## 4. Precious & PGM shorts — mostly right, one wrong name

* **PGM shorts validated (best block in the book):** SBSW -42% YTD with loss-making Stillwater palladium ops, high debt, SA restructuring — in a structurally-surplus palladium market. IMPUY -34% YTD. PLG pre-revenue developer — keep but don't add (micro-cap squeeze risk).
* **Silver shorts:** keep the high-beta trio AG (2-3x unhedged beta), CDE, HL. **Cover PAAS** — quality large-cap, Buy 5/2, +56% PT: it's the wrong name to short in the complex.
* **Gap:** no gold short while gold bias is down → optional new short **HMY** (high-cost SA producer).
* If CPI (7/14) triggers precious stabilization, the quality rebound longs are WPM / AEM / KGC (royalty/low-cost) — not yet.

## 5. Aluminum — right thesis, one wrong instrument

AA + CENX (pure smelters, leveraged to falling LME) and NHYDY are consistent with the short bias. **CSTM is a fabricator that passes metal cost through — falling LME helps its margins** (Buy 4/1, +25% PT). Cover CSTM.

## 6. Portfolio gaps found by the universe scan

1. **Copper — zero exposure** against a long-bias, tight market with a live tariff catalyst. Add **FCX** (12/15 buys, +17% PT). Optional pair: short **SCCO** — the street's only Sell consensus in the universe (PT -14%) — makes copper market-neutral.
2. **Rare earths — zero exposure** while NdPr is +74% YoY and equities lag. Add **MP** (11/11 buys, +48.7% PT). High-octane satellite: USAR (7/7 buys).
3. **Tin** — tightest metal on the board; optional **AFM.V** (~7% of world supply) if TSXV is tradable; DRC risk = small.
4. **TiO2 swap:** TROX (Neutral 1/5/1, levered) → **KRO** (Zacks Buy, volumes +4%, +33%/yr vs industry -10%). Same commodity, better name.
5. **ATI:** 6/6 buys but PT +2% — hold, don't add.

## 7. New tickers discovered (not in the Excel universe)

23 vetted, liquid additions written into the universe with `discovered: true`, notably: **uranium complex** (CCJ, UEC, NXE, DNN, LEU — a whole group missing from the map), gold/silver bench (HMY, AGI, BTG, EGO, ORLA, EXK, FSM, SSRM, TFPM), **antimony policy plays** (PPTA, UAMY), US critical-minerals developers (NB, CRML, METC, SLI, IE, LZM) and steel short ASTL.

## 8. Proposed trade list (nothing executed)

| # | Side | Ticker | ~Size | Why |
|---|---|---|---|---|
| 1 | COVER | NUE | 3 sh / $682 | thesis conflict with bullish steel |
| 2 | COVER | STLD | 3 sh / $685 | thesis conflict with bullish steel |
| 3 | COVER ⅓ | CLF | 23 of 73 sh / $216 | de-risk crowded short into 7/23 earnings |
| 4 | COVER | TSLA | 1 sh / $408 | record deliveries + 7/22 margin-beat risk |
| 5 | COVER | BATT | 30 sh / $440 | redundant with LIT short |
| 6 | COVER | CSTM | 2 sh / $59 | fabricator gains from falling LME |
| 7 | COVER | PAAS | 2 sh / $87 | quality name — wrong silver short |
| 8 | BUY | FCX | 11 sh / $677 | copper gap, tariff catalyst, 12/15 buys |
| 9 | BUY | MP | 9 sh / $470 | RE leader, 11/11 buys, commodity +74% YoY |
| 10 | BUY | SGML | 17 sh / $202 | add to strongest lithium micro |
| 11 | SELL→BUY | TROX → KRO | ~$110 | TiO2 name-for-name upgrade |
| 12 | SHORT | ASTL | 97 sh / $351 | tariff-losing steel replaces mill shorts |
| 13 | SHORT (opt) | SCCO | 2 sh / $352 | Sell-consensus pair vs FCX |
| 14 | SHORT (opt) | HMY | 17 sh / $257 | missing gold-downside short |
| 15 | BUY (opt) | AFM.V | ~C$250 | tin tightness pure-play |

**Post-trade book:** gross ~64% (from 69%), net ~**-14%** (from -31%). The net-short cut is deliberate: the three strongest commodity biases (steel, copper, RE) are long, while the shorts concentrate where weakness is confirmed (PGM, silver beta, aluminum smelters, idiosyncratic CLF/RS).

**Catalyst calendar:** Jul 14 US CPI · Jul 22 TSLA earnings · Jul 23 CLF earnings · late-Jul NUE/STLD/FCX earnings · Aug 14 SGML financials · July Indonesia nickel quotas · H2 US copper-tariff decision.

## 9. Methodology

Composite micro-score (0-100) per name = momentum 20% (price vs 50/200DMA + 52w-range position) + commodity-alignment 20% (material bias × OM linkage 0-9) + deep-dive 15% (evidence-based judgment) + analyst 15% (consensus + PT upside, TipRanks refresh where covered) + SmartScore 10% + news sentiment 10% + quality 10% (cap/role/mcap). Missing sub-scores redistribute weight; `coverage` shows how much of the model was available. **High score = long candidate, low score on a liquid name = short candidate**, ranked within material group. Rebuild via `scripts/build_universe.py` + `scripts/micro_build.py`; rendered in the dashboard's **Stock Picks** tab.

*Caveats: analyst PTs across the metals complex are partly stale after the June-July correction (upside percentages inflated); foreign-listed names have no TipRanks coverage; 12 tickers carry a `quoteSuspect` flag (renamed/delisted mappings like GOLD→B, ACH, NVL); Bigdata.com content is news/filings-derived, not investment advice.*
