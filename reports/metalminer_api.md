# MetalMiner API: what it offers, what we use, what's broken

As of 2026-10-10. Sources: the MetalMiner *Prices API Documentation* (Rev 3/23),
the MetalMiner MCP server page (agmetalminer.com/mcp-metal-prices), the fetch
Action's logs (run 955, 2026-10-09 21:27Z), and the committed derived files
(`data/mm_series_registry.json`, `data/mm_freshness.json` and their git history
since 2026-09-03). No licensed price values appear here, only metadata.

## TL;DR

1. **The REST pull works.** It returned 169 series and 253,215 rows in about 60s with
   0 failed chunks, every day since 2026-09-03.
2. **The China assessments arrive in batches, not on a fixed lag.** These are the
   proprietary series that are the reason to pay for MetalMiner: rare earths, Li, Mn,
   Mo, Ti, Ni sulfate and FeCr. Batches landed on Sep 8, 16, 22 and 24, each covering
   data up to 1–4 days old. **Nothing has arrived since 2026-09-24.** The last
   observation is 2026-09-23, 16 days stale on Oct 9. China's National Day holiday
   (Oct 1–7) explains part of the gap, but not Sep 24–30. Because of this,
   `mm_freshness.json` `lagDays` is not "the publication delay". It is a sawtooth that
   depends on when you sample it.
3. **The strategy barely uses the data it pays for.** Of 37 tradable proprietary
   series, 8 feed a T1/T2 link. None of the 22 tradable rare-earth series do, NdPr oxide
   included. MP, REMX and UUUU are linked at T1 to cobalt sulfate, LCO and rhodium.
4. **The API can do more than we ask of it.** It has `forecast=True` (short- and
   long-term support/resistance), currency and unit conversion, and `price_future`
   and `currency` fields. `mm_fetch.py` uses none of these, and drops `currency`.
5. **Two of the four access paths are down in Claude sessions.** The `metalminer`
   connector fails with a DNS error. The proxy-injected `MM` credential for
   `indx.metalminerindx.com` doesn't reach the API in a form it accepts, so the API
   answers `{"error": "No token provided"}`.

## Access paths

| Path | Auth | Status 2026-10-10 | Notes |
|---|---|---|---|
| REST `GET https://indx.metalminerindx.com/api/commodities/2/all_prices` | `token` query param (Actions secret `METALMINER_API_TOKEN`) | **Works** in the fetch Action | The path MetalMiner gave us on 2026-09-02. The Rev 3/23 doc shows the older `/api/1/all_prices`. |
| Same host from a Claude session (proxy credential `MM`) | Proxy-injected | **Rejected**: HTTP 400 `No token provided` | Whatever the proxy injects isn't the `token` query param this endpoint reads. This is an environment setting, not a code fix. |
| `metalminer` connector in Claude sessions (`mcp__metalminer__ask`) | Connector | **Down**: `[Errno -2] Name or service not known` | DNS failure on the connector's backend. Retried 3×. |
| MetalMiner MCP server `https://mcp.metalminer.com/mcp` | OAuth 2.0 (PKCE) or `X-API-Key` header | Not connected here | 20+ tools: prices, 10y history, support/resistance, trend, correlation and lead/lag, units/FX, research search. **Premium tier:** 12-month forecasts with confidence intervals, scenario simulation, should-cost. Claude Code: `claude mcp add --transport http metalminer https://mcp.metalminer.com/mcp`. |

## REST reference (Rev 3/23 doc plus observed behaviour)

**Query parameters**

| param | values | we use it? |
|---|---|---|
| `token` | API token | yes |
| `commodity_id` | comma list | yes, in chunks of 20 |
| `historical` | `True`: full history since 2012 | yes. Every pull re-downloads all history, about 253k rows. |
| `format` | `json` / `xml` | `json` |
| `forecast` | `True`: adds `st_support`, `st_resistance`, `lt_support`, `lt_resistance` where a forecast exists | **no** |
| `currency` | `usd cny eur gbp inr jpy krw` | **no** |
| `unit` | `pound`, `metric ton`, `kilogram`, `ounce`, `short ton`, `troy ounce`, `gross ton`, `cwt` | **no** |

**Row fields:** `collection_date`, `commodity_id`, `category`, `type`, `origin`,
`description`, `unit`, `value` (original currency and unit), `currency`
(`index` for MMIs), `price_future` (`spot` or a futures expiry), plus converted
`USD/usd/cad/cny/eur/gbp/inr/jpy/krw` for non-index rows.

`mm_fetch.py` keeps only the 8 dump fields (`ROW_FIELDS`). That drops:
- **`currency`.** A CNY-quoted China assessment and a USD one look the same in the
  dump. Returns on a CNY series include USD/CNY moves. This doesn't matter for
  grading, but it does for lead/lag against USD equities.
- **`price_future`.** If a series is a futures contract rather than spot, a roll
  shows up as a price jump.

## What our tier holds

169 series. Grades come from `mm_series_quality.py` (full table in
[`mm_series_quality.md`](mm_series_quality.md)): 58 tradable (37 proprietary,
21 exchange-public), 62 level_only, 49 rejected.

Staleness by category at the 2026-10-09 pull, in days behind the pull:

| category | n | median lag | min | max |
|---|---|---|---|---|
| battery prices | 7 | 0 | 0 | 0 |
| mmi index values | 10 | 0 | 0 | 8 |
| non ferrous metals | 42 | 1 | 0 | 323 |
| precious metals | 9 | 1 | 0 | 3 |
| steel | 30 | 3 | 0 | 281 |
| stainless surcharges | 2 | 11 | 11 | 11 |
| stainless steel | 12 | 13 | 0 | 32 |
| ferro alloys | 2 | 16 | 16 | 16 |
| minor metals | 8 | 16 | 16 | 16 |
| rare earth metals | 35 | 16 | 8 | 56 |
| scrap | 12 | 18 | 18 | 46 |

The 16s are all the same China batch, described next.

## Finding: China assessments are released in batches

Last observation of PrNd oxide (270930), by the first pull that saw it. The other
2708xx–2710xx China series move in lockstep:

| first seen (pull, UTC) | data through | age at arrival | days since previous batch |
|---|---|---|---|
| 2026-09-03 11:55 | 2026-08-07 | 27d (initial backlog) | — |
| 2026-09-08 13:14 | 2026-09-04 | 4d | 5 |
| 2026-09-16 13:12 | 2026-09-15 | 1d | 8 |
| 2026-09-22 14:14 | 2026-09-21 | 1d | 6 |
| 2026-09-24 15:12 | 2026-09-23 | 1d | 2 |
| *(none through 2026-10-10)* | — | — | 16+ |

The "first seen" times are when our 4×/day schedule first saw a batch. The release
itself happened somewhere between that pull and the one before it.

What this means:
- **For a backtest, the honest delay is "first seen minus observation date", per
  row.** That needs a point-in-time (vintage) record. `lagDays` sampled at pull time
  swings between 1 and 16+ on the same feed. The workflow uses it as `--delay` for the
  rare-earth lead/lag test, so the delay assumption moves with the calendar.
- A backtest that assumes daily availability will look ahead on these series by up to
  a week, or more over Chinese holidays.
- The current 16-day silence is the longest on record. Ask MetalMiner whether the
  rare-earth feed is paused or broken. Use support@metalminer.com and quote ids 270930
  and 270581.

## Finding: the linkage map ignores the proprietary series

- 160 T1/T2 links point at 37 distinct series: 45 links on tradable series,
  **91 on level_only**, 24 on rejected.
- 8 of the 37 tradable proprietary series are used. Unused:
  - all rare earths: NdPr oxide 270930, Nd/Pr oxide and metal, Dy, Tb, Lu, Ho, the NdFeB grades
  - Ni sulfate 270914
  - China Ni 457 and Zn 821
  - India Zn 1337 and Al 1072
  - US platinum sponge 187
- **MP / REMX / UUUU** are linked at T1 to *cobalt sulfate*, *LCO* and *rhodium*,
  which look like spurious mined correlations. The only rare-earth link is the Rare
  Earths MMI at T4. `verify_data.py` already warns that the Rare Earth cluster has
  zero exposure until PrNd/NdPr oxide is mined in. The fix belongs in the upstream
  `metallica-fund` linkage miner, not here.

## Plumbing gaps found along the way

- `scripts/rare_earth_leadlag.py` is not on `master`. The Action guards on
  `[ -f … ]`, so that step, and the daily `mm_equities.py` Yahoo pull feeding it,
  silently do nothing useful.
- `mm_fetch.py` re-downloads full history (`historical=True`) for all 169 ids on every
  run (4×/day). That is fine at about 60s, but an incremental pull is the natural place
  to also record first-seen dates (next section).

## Recommended next steps

1. **Point-in-time capture (highest value).** In `mm_fetch.py`, keep a small derived
   file of `{commodity_id: {obs_date: first_seen_utc}}` for recent rows. This yields
   the true per-observation delay for backtests and for `--delay`. It is metadata
   only, so it is safe to commit.
2. **Keep `currency` and `price_future`** in the dump rows (add them to
   `ROW_FIELDS`). Have `mm_series_quality.py` flag non-USD series and futures-based
   series.
3. **Try `forecast=True`** once in the Action to see which series carry
   support/resistance in our tier. If populated, it is a cheap extra feature.
4. **Ask MetalMiner** about the rare-earth batch cadence and the current gap, whether
   the `/api/commodities/2/` route documents more endpoints (catalogue, deltas
   since a date), and whether our tier includes the MCP server's Premium forecasts.
5. **Upstream:** mine NdPr oxide, Dy and Tb oxides for MP/REMX/UUUU, and drop the
   cobalt, LCO and rhodium links.
6. **Session access (environment settings, not code):** fix the `MM` network secret
   so it lands as the `token` query param, or connect the MetalMiner MCP server via
   OAuth. Either lets research sessions query MetalMiner directly instead of only the
   nightly Action.
