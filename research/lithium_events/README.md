# Lithium event history — Bigdata.com (step 5 of the price-vs-earnings test)

A dated, source-cited list of company events for five lithium producers, built to test
MetalMiner lithium prices against each company's earnings and share-price returns.

| File | What |
|------|------|
| `events.json` | Full dataset: per-company metadata + coverage notes, and every event with its metrics and up to 3 sources. |
| `events.csv` | Flat view, one row per event (metrics joined into one column; first source only). |

**Not a dashboard input.** Nothing in `index.html` reads these files and no refresh script
writes them; they are a one-off research pull (generated 2026-09-29).

## Scope

Window **2022-01-01 → 2026-09-29**. 338 events.

| Ticker | Company | Bigdata.com id | MetalMiner series | Events |
|--------|---------|----------------|-------------------|--------|
| PLS (ASX) | PLS Group (ex-Pilbara Minerals) | `9561FC` | 271019 SC6 spodumene | 63 |
| SGML (Nasdaq) | Sigma Lithium | `032C6D` | 271019, adjusted for grade/basis | 78 |
| LTR (ASX) | Liontown | `1772EC` | 271019 | 73 |
| CXO (ASX) | Core Lithium | `128A7F` | 271019 | 76 |
| LAR (NYSE) | Lithium Argentina | `C0FA69` | 270784 China carbonate, 270787 S. America carbonate | 48 |

## Event record

| Field | Meaning |
|-------|---------|
| `date` / `first_seen` | Earliest Bigdata.com publication time found for the event (UTC). Use this as the event date for return windows. |
| `period` | Reporting period the figures refer to (e.g. `Jun-2024 quarter`), or null. |
| `categories` | One or more of: production, guidance, realised_price, sales_shipments, unit_costs, recoveries, expansion_ramp, curtailment_restart, financing_debt, offtake, m_and_a, governance, earnings. |
| `headline`, `summary` | Paraphrased — no licensed text is reproduced. |
| `metrics` | Figures **stated in the source**, with units exactly as stated (currency, grade, price basis). Nothing is inferred or converted; ranges stay strings. |
| `impact` | positive / negative / mixed / neutral — a reading of the news for company fundamentals, **a judgement, not a measured sentiment score**. |
| `sources` | Bigdata.com document links (need a Bigdata.com login), doc id, timestamp. |

## Read before testing

- **`date` can trail the real announcement.** It is the first document Bigdata.com returned,
  not the exchange release. Most lag by hours at most — ASX releases made before the
  open fall on the previous UTC day. A few events surfaced only in later coverage and are dated to it;
  each is listed in that company's `coverage_notes` (e.g. PLS P680 FID — June 2022, dated
  2022-07-11; SGML Labor Ministry order of 5 Dec 2025, dated to the 15 Jan 2026 Reuters report).
- **Date-only timestamps.** Company-announcement feeds (PubT, Model ML) stamp `T00:00:00Z`;
  treat those as day-level. Where a timed copy existed it was used instead. For LAR, two results
  (Q3-2024, FY-2024) have an aggregator copy ~2.5 h before the ~22:05 UTC newswire, i.e. during
  US trading hours — use the newswire time if you apply an after-close convention.
- **Price basis is not uniform — normalise before comparing to 271019.**
  - PLS: SC6 CIF (2022) → ~SC5.3–5.4 with an SC6-equivalent where given (late 2022 on) → SC5.2 (2026).
  - SGML: nominal 5.5% Li2O, sold 5.0–5.5%; priced at 9% of the lithium hydroxide price
    FOB Vitória, provisional (2023–early 2024, large later settlements) → CIF China (from Q2-24) →
    SC6 CIF netted for grade (2025) → Q1-26 stated on SC5.
  - LTR: US$/dmt CIF, SC6-normalised, or A$/dmt depending on the report.
  - CXO: DSO (1.4% Li2O), delivered-grade and SC6-equivalent prices; fines priced separately.
  - LAR: US$/t carbonate, from Q3-2024; earlier only the formula (China battery-grade less VAT
    and a US$2,000/t — later US$1,500/t — processing deduction).
- **LAR is 100% Cauchari-Olaroz basis** (LAR's economic interest is 44.8%). For 2022–Sep 2023
  the entity is the pre-split Lithium Americas Corp.; its EPS/cash include Thacker Pass.
- **Conflicting figures** between outlets were resolved in favour of the company's own
  document and noted in `coverage_notes`.
- Known gaps (per company) are in `companies[].coverage_notes` in `events.json`.

## How it was built

Bigdata.com search (`bigdata_search`, fast mode, entity filter, NEWS + TRANSCRIPT, per-year
windows across operations / strategy / capital themes — 151 searches in total, each logged
under `companies[].searches` in `events.json`) through the Bigdata.com connector in a Claude session. The
Bigdata.com **API key** could not be used: it is refused (403) on `cqs/query-chunks`,
`cqs/discovery-panel` and `user-data/chats`, so this cannot yet be rerun from a script or the
scheduled Action. Co-mentions (`discovery-panel`) are not included.
