# New Positions — Micro-Level Analysis

**As of:** 2026-07-15 (live intraday prices) · research reused from `data/micro.json` (researchAsOf 2026-07-14)
**Book:** "Metallica" systematic long/short industrial-metals equity · **NAV ≈ $10,852** · current net −32.7% / gross 68.7%
**Scope:** the **13 proposed positions not currently held** (existing holdings are already covered in the Stock Picks micro layer)
**Sources:** live quotes/DMA/52w — FMP; analyst consensus — TipRanks; thesis/catalysts/risks/composite/hedge-fund verdict — this dashboard's `micro.json`; commodity bias — `micro.json.commodityBias`. FX approximate. *Analysis, not investment advice.*

---

## TL;DR — three findings dominate

1. **Most of the new shorts fight this dashboard's own signals.** Six of the twelve proposed new shorts are on names the bottom-up engine scores **bullish** or on a metal whose commodity bias is **long** — most acutely the **tin/zinc complex** (AFM.V, TINS.JK, ELT.AX, HINDZINC.NS) where the desk's own bias is **long tin (+1, "tin is the star", $53K)** and the composites are among the highest on the board (TINS.JK 73.7, AFM.V 70.7). You would be shorting the engine's top-ranked tin longs.

2. **9 of the 13 are flagged non-tradable** (`tradable=false`) — every foreign listing (`.AX/.PA/.TO/.L/.JK/.NS/.V`). Of the twelve proposed **shorts**, only **CMC and KALU** are actually tradable in the IBKR account (BEP too, but it's the odd one out — see below). A short you can't borrow is not a position; it's an intention.

3. **The long/aligned names are the good ones — but they're lumpy and stale-priced.** HWM (long, composite 77.1, StrongBuy) is the standout, but at **1 share** it can't be sized and its target was struck ~39% below live. KALU's target is +44% below live. Re-strike share counts before executing.

**Net effect of the 13:** +$2,841 gross (**26% of NAV**), of which only HWM is long → **~−$2,294 net (−21% of NAV)**, deepening an already net-short book and concentrating the incremental risk in exactly the complexes (tin/zinc) the desk is otherwise bullish.

---

## Conflict matrix — does the micro picture support the proposed side?

| Ticker | Side | Metal | Commodity bias | Micro verdict (composite) | Analyst | Tradable | Side supported? |
|---|---|---|---|---|---|---|---|
| **AFM.V** | SHORT | Tin | **LONG +1** | **bullish (70.7)** | — | ❌ | **No — backwards** |
| **TINS.JK** | SHORT | Tin | **LONG +1** | **bullish (73.7)** | BMI: elevated '26 | ❌ | **No — backwards** |
| **ELT.AX** | SHORT | Tin | **LONG +1** | bullish (47.4) | — | ❌ | No (but binary dev) |
| **HINDZINC.NS** | SHORT | Zinc | **LONG +1** | bullish (53.9) | — | ❌ | No — but idiosyncratic bear hooks |
| **S32.AX** | SHORT | Aluminum | short −1 | **bullish (54.9)** | — | ❌ | **No — exiting aluminum** |
| **CMC** | SHORT | Steel | **LONG +2 (high)** | bullish (61.5) | **Buy +22%** | ✅ | No — fights steel tape (two-sided) |
| **KALU** | SHORT | Aluminum | short −1 | neutral (50.1) | Neutral +2.7% | ✅ | Weak — valuation short, not Al |
| **BEP** | SHORT | Renewables | n/a (not a metal) | *new* | **Buy +14.5%** | ✅ | Weak — thin metals link |
| **NIC.AX** | SHORT | Nickel | neutral (bottoming) | bearish (44.1) | Jefferies Hold ↓ | ❌ | Yes, but late-cycle |
| **ERA.PA** | SHORT | Nickel | neutral | neutral (34.4) | Oddo Neutral | ❌ | Yes — distressed/thin |
| **S.TO** | SHORT | Nickel | neutral | bearish (43.9) | — | ❌ | Direction yes / **penny squeeze** |
| **FRES.L** | SHORT | Silver | **short −1** | bearish (30.0) | Berenberg Hold | ❌ | **Yes — cleanest short** |
| **HWM** | LONG | Titanium/aero | neutral | **bullish (77.1)** | **StrongBuy +15%** | ✅ | **Yes — best of the batch** |

Aligned shorts: **FRES.L, NIC.AX** (and directionally S.TO/ERA.PA). Aligned long: **HWM**. Everything else is fighting either the commodity bias, the bottom-up score, or the analyst tape.

## Sizing / FX reality (NAV $10,852)

| Ticker | Side | Target $ | Shares | Live | Actual USD | Drift vs target | NAV % |
|---|---|---|---|---|---|---|---|
| BEP | S | 786 | 23 | $32.62 | $750 | −5% | **6.9%** |
| HWM | L | 196 | 1 | $273.16 | $273 | **+39%** | 2.5% |
| S.TO | S | 262 | 2,374 | C$0.155 | $269 | +3% | 2.5% |
| ERA.PA | S | 262 | 5 | €43.62 | $253 | −3% | 2.3% |
| NIC.AX | S | 262 | 420 | A$0.875 | $241 | −8% | 2.2% |
| FRES.L | S | 180 | 5 | 2515p | $170 | −6% | 1.6% |
| KALU | S | 112 | 1 | $161.05 | $161 | **+44%** | 1.5% |
| AFM.V | S | 112 | 128 | C$1.42 | $133 | +18% | 1.2% |
| CMC | S | 157 | 2 | $66.10 | $132 | −16% | 1.2% |
| TINS.JK | S | 112 | 584 | Rp3,500 | $125 | +12% | 1.2% |
| HINDZINC.NS | S | 112 | 20 | ₹527.75 | $122 | +9% | 1.1% |
| S32.AX | S | 112 | 40 | A$4.06 | $106 | −5% | 1.0% |
| ELT.AX | S | 112 | 486 | A$0.33 | $105 | −6% | 1.0% |

Lumpiness: **HWM, KALU (1 sh)** and **CMC (2 sh)** cannot track a target weight on this NAV — one tick of the underlying moves the position size several percent. **HWM +39% / KALU +44%** drift says the target-share counts were struck at prices well below live (stale snapshot or lagging feed) — re-strike before trading.

---

## Per-name micro cards (grouped by complex)

### Tin / Zinc — the core conflict (commodity bias = LONG tin +1, zinc tight)

- **AFM.V — Alphamin Resources (tin, DRC Bisie ~7% of world supply).** Live C$1.42, flat vs 50DMA, **+13% vs 200DMA, near 52w high** while the complex corrects. Composite **70.7 bullish** — the engine's flagship tin long ("tightest metal on the board, Myanmar broken, AI-solder demand, LME $53K"). The micro `recommendation` literally reads *"OPTIONAL NEW LONG ~$250."* **Proposing it as a SHORT is the single most contradictory line in the rebalance.** Only bear hook: DRC/M23 security + TSXV borrow (which also makes it **non-tradable/non-shortable** here). → **Skip the short; if anything, it's a long.**
- **TINS.JK — PT Timah (tin, Indonesia SOE).** Live Rp3,500, **above both DMAs.** Composite **73.7 bullish** — Q1 refined tin +82% YoY, exports normalizing, BMI sees elevated tin through 2026 (H2 moderation risk). Non-tradable (JKT). → **Skip the short.** The only pro-short nuance is BMI's H2 supply-easing caveat — not enough.
- **ELT.AX — Elementos (pre-production tin developer, Spain Oropesa).** Live A$0.33, −14% vs 50DMA. Composite 47.4 bullish but this is a **binary, pre-revenue single-project** name (OPI permitting catalyst June). A$112M micro-cap, non-tradable. Shorting a dev-stage option is a coin-flip either way. → **Skip.**
- **HINDZINC.NS — Hindustan Zinc (Vedanta).** Live ₹527.75, −10% vs 50DMA. Composite 53.9 bullish (record mined output, Q4 profit +68%), **but** −16% in June on falling silver (≈45% of profitability) + Vedanta ED/FEMA probe + government stake-sale overhang. This is the **one tin/zinc short with a real bear case** — yet it's an idiosyncratic (silver + governance) short, not a zinc short, and it's non-tradable (NSE) with a ~64% controlled float (no borrow). → **Skip on tradability; the thesis is silver/governance, not zinc.**

### Nickel — commodity bias neutral ("bottoming, pessimism priced")

- **NIC.AX — Nickel Industries.** Live A$0.875, −11% vs 50DMA, near 52w low. Composite **44.1 bearish** — Jefferies Hold with PT drifting A$1.20→1.00 on Indonesia's HPM price-formula risk. **Cleanest nickel short thesis**, but nickel is bottoming so it's late-cycle, and it's **non-tradable** (ASX). → Directionally fine, not executable as-is.
- **ERA.PA — Eramet (nickel + manganese).** Live €43.62, **at its 52w low, −50% from 52w high (€88).** Composite 34.4 neutral — Oddo "largely uninvestable" (ND/EBITDA >5x, €500M capital-increase + CEO/governance overhang). As a short: already crushed, **squeeze risk on any relief**, thin liquidity (~27k sh/day), non-tradable. H1 results Jul 29. → Marginal; distressed-short late.
- **S.TO — Sherritt International.** Live **C$0.155 penny stock (C$76M cap), +24% TODAY**, cease-trade order only lifted Jul 10, Cuba-sanctions supply hit (Q1 Ni −36% YoY). Composite 43.9 bearish on fundamentals, **but** shorting 2,374 shares of a sub-C$0.20 penny that's ripping intraday is an uncontrollable squeeze — and it's non-tradable. → **Hard skip.**

### Silver — commodity bias SHORT −1

- **FRES.L — Fresnillo (world's largest silver).** Live 2,515p, **−19% vs 50DMA, −44% from 52w high.** Composite **30.0 bearish** — Berenberg Hold, PT cut on MXN, Q1 volumes down YoY. **The one short that aligns on commodity bias + score + tape.** Caveats: silver is squeeze-prone/volatile and already halved from the Jan spike; LSE/GBP borrow (**non-tradable** here). → Best short thesis of the batch, but execution-blocked.

### Steel / Aluminum — bias LONG steel +2 (high) / SHORT aluminum −1

- **CMC — Commercial Metals (rebar/long products).** Live $66.10, −6.5% vs 50DMA, off a $84.87 high. **TipRanks Buy, PT $80.45 (+22%)**, composite 61.5 bullish, steel bias **LONG +2**. Shorting it fights a strong steel tape. *Two-sided:* momentum is rolling over, hedge-fund aggregate is actually bearish (rebar oversupply / scrap-spread), and it's **the only tradable "conflict" short.** → If you must express short-steel, CMC is the wrong vehicle (rebar ≠ HRC); at least it's tradable. Small or skip.
- **KALU — Kaiser Aluminum (fabricator).** Live $161.05, −9.5% vs 50DMA but **+23% vs 200DMA (from a $71 low)**. Composite 50.1 neutral, **Neutral consensus +2.7%, Wells Fargo Underweight $158.** Direction (short) is defensible as a **valuation/mean-reversion** short into Q2 earnings (Jul 22–23) — **but not as an aluminum-price short**: KALU passes LME through to customers (priceSens 1/3). Tradable. → OK as a small valuation short; re-strike the 1-share size.
- **S32.AX — South32.** Live A$4.06. Composite **54.9 bullish** — **agreed to sell its entire bauxite/alumina/aluminum arm to Alcoa (~$4.1B + $750M CVR)** and is pivoting to the Hermosa Arizona **zinc**-manganese growth project. Shorting S32 to express *short aluminum* is backwards: **it's exiting aluminum**, and the pending deal is a re-rating catalyst (deal risk cuts both ways, close H1'27). Non-tradable. → **Skip / wrong thesis.**

### Renewables — the outlier

- **BEP — Brookfield Renewable.** Live $32.62, −6% vs 50DMA / +5% vs 200DMA. **Largest single new position ($786 ≈ 6.9% of NAV)** yet the **weakest fit for a metals book** — a contracted hydro/wind yieldco whose only tie is the thematic "short EV/renewables demand" leg (alongside TSLA/BATT/KARS/LIT). **TipRanks Buy, PT $37.39 (+14.5%).** Functionally this is a **rates/duration short**, not a materials short. → If kept, size it down and re-label the thesis; a 6.9% NAV short on a Buy-rated yieldco is a lot of conviction for a thin link.

---

## Book-level roll-up

- **Direction & concentration:** the 13 add ~$2.8k gross (26% of NAV), **~$2.3k net short (−21% of NAV)** — 12 shorts vs 1 long (HWM). This pushes an already −33% net book meaningfully more net-short, and **correlates the additions**: nickel (3), tin (3), zinc (1), silver (1) miners tend to move together on a risk-off metals tape, so the diversification is less than 13 names implies.
- **Tradability is the binding constraint:** only **CMC, KALU, HWM (+ BEP)** are tradable. The other **9 are non-tradable foreign listings** — and foreign small/micro-cap **shorts** additionally need a locate/borrow that generally isn't available. Practically, the executable slice is **HWM long + CMC/KALU/BEP shorts.**
- **Signal coherence:** the executable shorts are the ones with the **weakest** short cases (CMC fights steel +2; KALU is aluminum-neutral valuation; BEP is Buy-rated) while the **strongest** short case (FRES.L) and the biggest conflicts (tin/zinc) are all non-tradable. The tradable set is close to the inverse of the conviction set.

## Recommendations (per name)

| Action | Names | Why |
|---|---|---|
| **Keep (aligned)** | HWM (long) | Composite 77.1, StrongBuy +15%, aerospace demand — best in batch. Re-strike (1 sh too lumpy). |
| **OK, small, fix rationale/size** | KALU (valuation short, not Al), BEP (size down, re-label as rates short) | Tradable; direction defensible but not for the stated reason. |
| **Skip — fights the desk's own signal** | AFM.V, TINS.JK, S32.AX, ELT.AX, HINDZINC.NS | Bullish composite / long commodity bias; several exiting-aluminum or dev-stage. |
| **Skip — execution/borrow** | FRES.L, NIC.AX, ERA.PA | Directionally reasonable but non-tradable / thin / distressed. |
| **Hard skip — squeeze** | S.TO | Sub-C$0.20 penny +24% intraday; uncontrollable short. |
| **Small or skip** | CMC | Only tradable "conflict" short; wrong vehicle for short-steel, two-sided. |

**Bottom line:** the *long* leg (HWM) and the *silver/nickel* short logic are sound, but the rebalance's new **shorts are mostly pointed at the wrong complex (tin/zinc, where the desk is long) and are mostly un-executable.** Before trading: (1) drop or flip the tin/zinc shorts, (2) confirm IBKR borrow on every foreign short (expect most to fail), (3) re-strike the 1–2 share names, (4) reconsider BEP's 6.9% weight and rationale.
