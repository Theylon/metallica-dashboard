# MetalMiner series quality

Source dump: `historical_latest.json.gz` · as of 2026-09-07 · 169 series.

Grades: **tradable** = daily, fresh, not frozen, no suspicious jumps; **level_only** = usable for direction/level, not for return signals (weekly/monthly cadence, partly frozen, or thin recent history); **rejected** = composite index, stopped, frozen list price, or unit flip. `public` = exchange-quoted (LME/COMEX), so no information edge.

Counts: {"rejected": 85, "level_only": 58, "tradable": 26, "tradable_public": 21, "tradable_proprietary": 5}

| category | series | tradable (proprietary / public) | level_only | rejected |
|---|---|---|---|---|
| battery prices | 7 | 0 (0 / 0) | 7 | 0 |
| ferro alloys | 2 | 0 (0 / 0) | 0 | 2 |
| minor metals | 8 | 0 (0 / 0) | 0 | 8 |
| mmi index values | 10 | 0 (0 / 0) | 0 | 10 |
| non ferrous metals | 42 | 20 (4 / 16) | 6 | 16 |
| precious metals | 9 | 5 (1 / 4) | 4 | 0 |
| rare earth metals | 35 | 0 (0 / 0) | 5 | 30 |
| scrap | 12 | 0 (0 / 0) | 12 | 0 |
| stainless steel | 12 | 0 (0 / 0) | 3 | 9 |
| stainless surcharges | 2 | 0 (0 / 0) | 1 | 1 |
| steel | 30 | 1 (0 / 1) | 20 | 9 |

## Stale: last observation > 30d before as-of (50)

| id | series | end | staleDays | obs |
|---|---|---|---|---|
| 356 | aluminum (non ferrous metals, korea, commercial 1050 sheet, kilogram) | 2025-11-20 | 291 | 265 |
| 581 | aluminum (non ferrous metals, korea, 5052 coil premium over 1050, kilo | 2025-11-20 | 291 | 268 |
| 1044 | aluminum (non ferrous metals, korea, 3003 coil premium over 1050, kilo | 2025-11-20 | 291 | 270 |
| 618 | steel (steel, korea, rebar, metric ton) | 2026-01-01 | 249 | 359 |
| 1136 | steel (steel, korea, hrc, metric ton) | 2026-01-01 | 249 | 283 |
| 290 | aluminum (non ferrous metals, europe, 6082 plate, metric ton) | 2026-08-03 | 35 | 173 |
| 408 | aluminum (non ferrous metals, europe, 5083 plate, metric ton) | 2026-08-03 | 35 | 177 |
| 429 | aluminum (non ferrous metals, europe, 6082 bar, metric ton) | 2026-08-03 | 35 | 171 |
| 552 | aluminum (non ferrous metals, europe, commercial 1050 sheet, metric to | 2026-08-03 | 35 | 180 |
| 270764 | lanthanum metal (rare earth metals, china, 99%min exw, kilogram) | 2026-08-03 | 35 | 2495 |
| 270557 | cobalt sulfate (minor metals, china, 20.5%min delivered, kilogram) | 2026-08-07 | 31 | 2351 |
| 270581 | dysprosium oxide (rare earth metals, china, 99.5%min fob, kilogram) | 2026-08-07 | 31 | 3008 |
| 270585 | electrical steel (stainless steel, china, grain oriented 130 0.3*980mm | 2026-08-07 | 31 | 3225 |
| 270596 | ferro-chrome (ferro alloys, rotterdam, cr 60%min, c 8%max in warehouse | 2026-08-07 | 31 | 1822 |
| 270601 | ferro-chrome (ferro alloys, china, kazakhstan cr 68%min, c 8.5%max in  | 2026-08-07 | 31 | 1906 |
| 270612 | ferro-holmium (rare earth metals, china, 80% exw, kilogram) | 2026-08-07 | 31 | 3109 |
| 270704 | h-beam steel (steel, shanghai, q235 200*200mm in warehouse, metric ton | 2026-08-07 | 31 | 3295 |
| 270748 | ionic re conc. (rare earth metals, china, treo 92%min in port, metric  | 2026-08-07 | 31 | 475 |
| 270765 | lanthanum metal (rare earth metals, china, 99%min fob, kilogram) | 2026-08-07 | 31 | 2638 |
| 270766 | lanthanum oxide (rare earth metals, china, 99.9%min exw, kilogram) | 2026-08-07 | 31 | 1845 |
| 270767 | lanthanum oxide (rare earth metals, china, 99.9%min fob, kilogram) | 2026-08-07 | 31 | 2038 |
| 270768 | lanthanum oxide (rare earth metals, china, 99.999%min exw, kilogram) | 2026-08-07 | 31 | 2655 |
| 270787 | lithium carbonate (minor metals, america, 99.5%min fob south, kilogram | 2026-08-07 | 31 | 1771 |
| 270789 | lithium hydroxide monohydrate (minor metals, china, lioh 56.5%min, mag | 2026-08-07 | 31 | 2418 |
| 270800 | lutetium oxide (rare earth metals, exw, exw, kilogram) | 2026-08-07 | 31 | 1444 |
| 270840 | manganese dioxide (minor metals, china, alkaline 91%min exw, metric to | 2026-08-07 | 31 | 3091 |
| 270860 | manganese sulfate (minor metals, china, mn 32%min exw, metric ton) | 2026-08-07 | 31 | 1920 |
| 270879 | molybdenum bar (minor metals, china, 99.9%min exw, kilogram) | 2026-08-07 | 31 | 3285 |
| 270898 | ndfeb (rare earth metals, china, sintered rough 35m exw, kilogram) | 2026-08-07 | 31 | 1123 |
| 270899 | ndfeb (rare earth metals, china, sintered rough 45m exw, kilogram) | 2026-08-07 | 31 | 1118 |
| 270900 | ndfeb (rare earth metals, china, sintered rough 50m exw, kilogram) | 2026-08-07 | 31 | 1128 |
| 270901 | ndfeb (rare earth metals, china, sintered rough 35h exw, kilogram) | 2026-08-07 | 31 | 1125 |
| 270902 | ndfeb (rare earth metals, china, sintered rough 45h exw, kilogram) | 2026-08-07 | 31 | 1127 |
| 270903 | ndfeb (rare earth metals, china, sintered rough 48h exw, kilogram) | 2026-08-07 | 31 | 1127 |
| 270904 | ndfeb (rare earth metals, china, sintered rough 50h exw, kilogram) | 2026-08-07 | 31 | 1126 |
| 270905 | neodymium metal (rare earth metals, china, 99%min exw, kilogram) | 2026-08-07 | 31 | 3315 |
| 270906 | neodymium metal (rare earth metals, china, 99%min fob, kilogram) | 2026-08-07 | 31 | 3295 |
| 270907 | neodymium oxide (rare earth metals, china, 99.5%min exw, kilogram) | 2026-08-07 | 31 | 2931 |
| 270908 | neodymium oxide (rare earth metals, china, 99.5%min fob, kilogram) | 2026-08-07 | 31 | 3283 |
| 270914 | nickel sulfate (non ferrous metals, china, ni 22%min; co 0.05%max exw, | 2026-08-07 | 31 | 3268 |
| 270922 | praseodymium metal (rare earth metals, china, 99.5%min fob, kilogram) | 2026-08-07 | 31 | 3286 |
| 270923 | praseodymium oxide (rare earth metals, china, 99.5%min exw, kilogram) | 2026-08-07 | 31 | 3056 |
| 270924 | praseodymium oxide (rare earth metals, china, 99.5%min fob, kilogram) | 2026-08-07 | 31 | 3287 |
| 270928 | prnd mischmetal (rare earth metals, china, pr 25%, nd 75% exw, kilogra | 2026-08-07 | 31 | 3327 |
| 270929 | prnd mischmetal (rare earth metals, china, pr 25%, nd 75% fob, kilogra | 2026-08-07 | 31 | 3000 |
| 270930 | prnd oxide (rare earth metals, china, pr6o11 25%, nd2o3 75% exw, kilog | 2026-08-07 | 31 | 3142 |
| 271053 | terbium metal (rare earth metals, china, 99.9%min fob, kilogram) | 2026-08-07 | 31 | 1610 |
| 271055 | terbium oxide (rare earth metals, china, 99.99%min fob, kilogram) | 2026-08-07 | 31 | 1621 |
| 271075 | titanium plate (minor metals, china, ta2 2mm exw, kilogram) | 2026-08-07 | 31 | 3084 |
| 271078 | titanium sponge (minor metals, china, 99.7%min exw, metric ton) | 2026-08-07 | 31 | 3199 |

## Frozen: > 40% unchanged steps or flat run > 60 (23)

| id | series | flatShare | longestFlatRun | obs | medianGapDays |
|---|---|---|---|---|---|
| 827 | 201 (stainless steel, united states, 2b ctl (0.075 in x 48 in) sheet,  | 0.9357 | 34 | 1292 | 1 |
| 468 | 409 (stainless steel, united states, 2d (0.06 in x 48 in) sheet, pound | 0.8172 | 32 | 455 | 1.0 |
| 538 | 304 (stainless steel, united states, 2b (0.075 in x 48 in) sheet, poun | 0.7229 | 34 | 333 | 1.0 |
| 191 | 304 (stainless steel, united states, #4 polish vinyl ctl (0.048 in x 4 | 0.7216 | 34 | 353 | 1.0 |
| 5 | steel (steel, united states, wire rod, cwt) | 0.7203 | 22 | 1767 | 1.0 |
| 434 | 316l (stainless steel, united states, 2b ctl (0.075 in x 48 in) sheet, | 0.6655 | 34 | 297 | 1.0 |
| 235 | 430 (stainless steel, united states, #4 polish vinyl ctl (0.048 in x 4 | 0.6208 | 32 | 241 | 1.0 |
| 29004 | aluminum (non ferrous metals, europe, 6082 T6 (0.08 in x 48 in) sheet, | 0.6036 | 19 | 1391 | 1.0 |
| 29003 | aluminum (non ferrous metals, europe, 5251 H32 (0.08 in x 48 in) sheet | 0.603 | 19 | 1389 | 1.0 |
| 523 | steel (steel, united states, aluminized dds astm a463 t1 40 (0.05 in x | 0.5107 | 17 | 702 | 1 |
| 1346 | aluminum (non ferrous metals, united states, 5083 h321 (1 in x 60 in)  | 0.4842 | 13 | 1808 | 1 |
| 916 | aluminum (non ferrous metals, united states, 5052 h32 (0.06 in x 60 in | 0.4836 | 13 | 1804 | 1 |
| 1040 | aluminum (non ferrous metals, united states, 6061 t651 (0.5 in x 48 in | 0.4787 | 13 | 1787 | 1.0 |
| 663 | aluminum (non ferrous metals, united states, 3003 h14 (0.08 in x 48 in | 0.4702 | 13 | 1760 | 1 |
| 1281 | aluminum (non ferrous metals, united states, 6061 t6 (0.08 in x 48 in) | 0.4692 | 13 | 1755 | 1.0 |
| 1477 | rare earths mmi (mmi index values, global, na, index) | 0.4563 | 34 | 1912 | 1 |
| 503 | aluminum (non ferrous metals, united states, 1100 h14 (0.08 in x 48 in | 0.4501 | 13 | 1894 | 1 |
| 72095 | lmo hydroxide-based (battery prices, global, index, index) | 0.2553 | 92 | 2343 | 1.0 |
| 72097 | nmc811 hydroxide-based (battery prices, global, index, index) | 0.2545 | 92 | 2347 | 1.0 |
| 1248 | steel (steel, china, crc, metric ton) | 0.2179 | 91 | 1786 | 1 |
| 393 | steel (steel, china, plate, metric ton) | 0.1924 | 91 | 2023 | 1.0 |
| 258 | steel (steel, china, hrc, short ton) | 0.1853 | 91 | 2100 | 1 |
| 733 | steel (steel, china, rebar, metric ton) | 0.1782 | 91 | 2178 | 1 |

## Holes: max gap > 120d in a daily/weekly series (16)

| id | series | maxGapDays | medianGapDays | obs |
|---|---|---|---|---|
| 356 | aluminum (non ferrous metals, korea, commercial 1050 sheet, kilogram) | 815 | 8.0 | 265 |
| 581 | aluminum (non ferrous metals, korea, 5052 coil premium over 1050, kilo | 815 | 8 | 268 |
| 1044 | aluminum (non ferrous metals, korea, 3003 coil premium over 1050, kilo | 815 | 8 | 270 |
| 1248 | steel (steel, china, crc, metric ton) | 401 | 1 | 1786 |
| 613 | yttria (rare earth metals, china, 99.99-99.999% avg ref price, metric  | 395 | 15 | 172 |
| 94902 | ruthenium (precious metals, united states, granules min. 99.90%, kilog | 347 | 2.0 | 1489 |
| 414 | steel (steel, china, hdg coil, metric ton) | 316 | 5 | 442 |
| 199342 | lanthanum-cerium mixed metal (rare earth metals, china, trem>99%;ce/tr | 316 | 7.0 | 227 |
| 982 | steel (steel, china, slab, metric ton) | 314 | 2.0 | 1519 |
| 539 | aluminum (non ferrous metals, china, aluminum billet, metric ton) | 302 | 1.0 | 1727 |
| 1477 | rare earths mmi (mmi index values, global, na, index) | 243 | 1 | 1912 |
| 1478 | raw steels mmi (mmi index values, global, na, index) | 125 | 1.0 | 1929 |
| 1479 | renewables mmi (mmi index values, global, na, index) | 124 | 1 | 1894 |
| 1472 | automotive mmi (mmi index values, global, na, index) | 122 | 1 | 1920 |
| 199344 | neodymium metal (rare earth metals, china, trem>99%;nd/rem:99~99.9%;fe | 122 | 2.0 | 1175 |
| 1471 | aluminum mmi (mmi index values, global, na, index) | 121 | 1.0 | 1887 |

## Jumps: single-step move > 50% (14)

| id | series | bigJumps | obs | start | end |
|---|---|---|---|---|---|
| 94320 | steel (steel, korea, hr plate, kilogram) | 5 | 77 | 2020-01-01 | 2026-09-07 |
| 80746 | goes (grain oriented electrical steel) (steel, europe, coil (>600mm),  | 4 | 116 | 2017-01-01 | 2026-09-07 |
| 613 | yttria (rare earth metals, china, 99.99-99.999% avg ref price, metric  | 3 | 172 | 2011-12-15 | 2026-08-14 |
| 42605 | 430 (stainless steel, europe, cr coil, metric ton) | 3 | 151 | 2014-01-01 | 2026-09-07 |
| 1228 | nickel (non ferrous metals, india, primary, kilogram) | 2 | 3320 | 2011-12-30 | 2026-09-07 |
| 184 | palladium (precious metals, united states, sponge 99.95% purity, troy  | 1 | 3268 | 2012-01-03 | 2026-09-07 |
| 468 | 409 (stainless steel, united states, 2d (0.06 in x 48 in) sheet, pound | 1 | 455 | 2020-01-01 | 2026-09-07 |
| 1189 | 430-coil (stainless surcharges, united states, nas surcharge, pound) | 1 | 157 | 2011-10-26 | 2026-08-27 |
| 33076 | steel (steel, europe, crc, metric ton) | 1 | 153 | 2014-01-01 | 2026-09-07 |
| 49797 | 304 (stainless steel, europe, round bar (<25mm), metric ton) | 1 | 153 | 2014-01-01 | 2026-09-07 |
| 80747 | goes (grain oriented electrical steel) (steel, europe, coil (<600mm),  | 1 | 115 | 2017-01-01 | 2026-09-07 |
| 82101 | aluminum (non ferrous metals, united states, aup (mw premium) future 3 | 1 | 1154 | 2019-01-01 | 2026-09-03 |
| 82102 | aluminum (non ferrous metals, united states, aup (mw premium) spot, po | 1 | 1296 | 2019-01-01 | 2026-09-04 |
| 229605 | yttrium (rare earth metals, northeast asia, , kilogram) | 1 | 67 | 2020-12-01 | 2026-09-01 |

## Tradable, proprietary (the series worth building signals on) (5)

| id | series | obs | start | recentObs | staleDays |
|---|---|---|---|---|---|
| 187 | platinum (precious metals, united states, sponge 99.95% purity, troy o | 3383 | 2012-01-03 | 711 | 0 |
| 457 | nickel (non ferrous metals, china, primary, metric ton) | 3104 | 2011-12-30 | 615 | 0 |
| 821 | zinc (non ferrous metals, china, primary cash, metric ton) | 3017 | 2011-12-30 | 612 | 0 |
| 1072 | aluminum (non ferrous metals, india, primary cash, kilogram) | 3422 | 2011-12-30 | 636 | 0 |
| 1337 | zinc (non ferrous metals, india, primary cash, kilogram) | 3437 | 2011-12-31 | 644 | 0 |
