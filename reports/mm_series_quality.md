# MetalMiner series quality

Source dump: `historical_latest.json.gz` · as of 2026-10-26 · 169 series.

Grades: **tradable** = daily, fresh, not frozen, no suspicious jumps; **level_only** = usable for direction/level, not for return signals (weekly/monthly cadence, partly frozen, or thin recent history); **rejected** = composite index, stopped, frozen list price, or unit flip. `public` = exchange-quoted (LME/COMEX), so no information edge.

Counts: {"rejected": 44, "level_only": 66, "tradable": 59, "tradable_public": 21, "tradable_proprietary": 38}

| category | series | tradable (proprietary / public) | level_only | rejected |
|---|---|---|---|---|
| battery prices | 7 | 0 (0 / 0) | 7 | 0 |
| ferro alloys | 2 | 1 (1 / 0) | 1 | 0 |
| minor metals | 8 | 7 (7 / 0) | 1 | 0 |
| mmi index values | 10 | 0 (0 / 0) | 0 | 10 |
| non ferrous metals | 42 | 21 (5 / 16) | 6 | 15 |
| precious metals | 9 | 5 (1 / 4) | 4 | 0 |
| rare earth metals | 35 | 22 (22 / 0) | 11 | 2 |
| scrap | 12 | 0 (0 / 0) | 12 | 0 |
| stainless steel | 12 | 1 (1 / 0) | 3 | 8 |
| stainless surcharges | 2 | 0 (0 / 0) | 1 | 1 |
| steel | 30 | 2 (1 / 1) | 20 | 8 |

## Stale: last observation > 30d before as-of (9)

| id | series | end | staleDays | obs |
|---|---|---|---|---|
| 356 | aluminum (non ferrous metals, korea, commercial 1050 sheet, kilogram) | 2025-11-20 | 340 | 265 |
| 581 | aluminum (non ferrous metals, korea, 5052 coil premium over 1050, kilo | 2025-11-20 | 340 | 268 |
| 1044 | aluminum (non ferrous metals, korea, 3003 coil premium over 1050, kilo | 2025-11-20 | 340 | 270 |
| 618 | steel (steel, korea, rebar, metric ton) | 2026-01-01 | 298 | 359 |
| 1136 | steel (steel, korea, hrc, metric ton) | 2026-01-01 | 298 | 283 |
| 290 | aluminum (non ferrous metals, europe, 6082 plate, metric ton) | 2026-08-03 | 84 | 173 |
| 408 | aluminum (non ferrous metals, europe, 5083 plate, metric ton) | 2026-08-03 | 84 | 177 |
| 429 | aluminum (non ferrous metals, europe, 6082 bar, metric ton) | 2026-08-03 | 84 | 171 |
| 552 | aluminum (non ferrous metals, europe, commercial 1050 sheet, metric to | 2026-08-03 | 84 | 180 |

## Frozen: > 40% unchanged steps or flat run > 60 (23)

| id | series | flatShare | longestFlatRun | obs | medianGapDays |
|---|---|---|---|---|---|
| 827 | 201 (stainless steel, united states, 2b ctl (0.075 in x 48 in) sheet,  | 0.9373 | 34 | 1341 | 1.0 |
| 468 | 409 (stainless steel, united states, 2d (0.06 in x 48 in) sheet, pound | 0.833 | 32 | 504 | 1 |
| 191 | 304 (stainless steel, united states, #4 polish vinyl ctl (0.048 in x 4 | 0.7353 | 34 | 375 | 1.0 |
| 5 | steel (steel, united states, wire rod, cwt) | 0.7245 | 22 | 1816 | 1 |
| 538 | 304 (stainless steel, united states, 2b (0.075 in x 48 in) sheet, poun | 0.7207 | 34 | 334 | 1 |
| 434 | 316l (stainless steel, united states, 2b ctl (0.075 in x 48 in) sheet, | 0.6855 | 34 | 319 | 1.0 |
| 235 | 430 (stainless steel, united states, #4 polish vinyl ctl (0.048 in x 4 | 0.6183 | 32 | 242 | 1 |
| 29004 | aluminum (non ferrous metals, europe, 6082 T6 (0.08 in x 48 in) sheet, | 0.6101 | 19 | 1440 | 1 |
| 29003 | aluminum (non ferrous metals, europe, 5251 H32 (0.08 in x 48 in) sheet | 0.6096 | 19 | 1438 | 1 |
| 523 | steel (steel, united states, aluminized dds astm a463 t1 40 (0.05 in x | 0.5063 | 17 | 710 | 1 |
| 1346 | aluminum (non ferrous metals, united states, 5083 h321 (1 in x 60 in)  | 0.4833 | 13 | 1857 | 1.0 |
| 916 | aluminum (non ferrous metals, united states, 5052 h32 (0.06 in x 60 in | 0.4827 | 13 | 1853 | 1.0 |
| 1040 | aluminum (non ferrous metals, united states, 6061 t651 (0.5 in x 48 in | 0.4779 | 13 | 1836 | 1 |
| 663 | aluminum (non ferrous metals, united states, 3003 h14 (0.08 in x 48 in | 0.4696 | 13 | 1809 | 1.0 |
| 1281 | aluminum (non ferrous metals, united states, 6061 t6 (0.08 in x 48 in) | 0.4687 | 13 | 1804 | 1 |
| 1477 | rare earths mmi (mmi index values, global, na, index) | 0.4633 | 34 | 1961 | 1.0 |
| 503 | aluminum (non ferrous metals, united states, 1100 h14 (0.08 in x 48 in | 0.4501 | 13 | 1943 | 1.0 |
| 72095 | lmo hydroxide-based (battery prices, global, index, index) | 0.2652 | 92 | 2392 | 1 |
| 72097 | nmc811 hydroxide-based (battery prices, global, index, index) | 0.2643 | 92 | 2396 | 1 |
| 1248 | steel (steel, china, crc, metric ton) | 0.2312 | 91 | 1835 | 1.0 |
| 393 | steel (steel, china, plate, metric ton) | 0.2047 | 91 | 2072 | 1 |
| 258 | steel (steel, china, hrc, short ton) | 0.1974 | 91 | 2149 | 1.0 |
| 733 | steel (steel, china, rebar, metric ton) | 0.19 | 91 | 2227 | 1.0 |

## Holes: max gap > 120d in a daily/weekly series (16)

| id | series | maxGapDays | medianGapDays | obs |
|---|---|---|---|---|
| 356 | aluminum (non ferrous metals, korea, commercial 1050 sheet, kilogram) | 815 | 8.0 | 265 |
| 581 | aluminum (non ferrous metals, korea, 5052 coil premium over 1050, kilo | 815 | 8 | 268 |
| 1044 | aluminum (non ferrous metals, korea, 3003 coil premium over 1050, kilo | 815 | 8 | 270 |
| 1248 | steel (steel, china, crc, metric ton) | 401 | 1.0 | 1835 |
| 613 | yttria (rare earth metals, china, 99.99-99.999% avg ref price, metric  | 395 | 15.0 | 173 |
| 94902 | ruthenium (precious metals, united states, granules min. 99.90%, kilog | 347 | 2.0 | 1511 |
| 414 | steel (steel, china, hdg coil, metric ton) | 316 | 5.0 | 451 |
| 199342 | lanthanum-cerium mixed metal (rare earth metals, china, trem>99%;ce/tr | 316 | 7 | 228 |
| 982 | steel (steel, china, slab, metric ton) | 314 | 2.0 | 1529 |
| 539 | aluminum (non ferrous metals, china, aluminum billet, metric ton) | 302 | 1 | 1754 |
| 1477 | rare earths mmi (mmi index values, global, na, index) | 243 | 1.0 | 1961 |
| 1478 | raw steels mmi (mmi index values, global, na, index) | 125 | 1 | 1978 |
| 1479 | renewables mmi (mmi index values, global, na, index) | 124 | 1.0 | 1943 |
| 1472 | automotive mmi (mmi index values, global, na, index) | 122 | 1.0 | 1969 |
| 199344 | neodymium metal (rare earth metals, china, trem>99%;nd/rem:99~99.9%;fe | 122 | 2 | 1180 |
| 1471 | aluminum mmi (mmi index values, global, na, index) | 121 | 1 | 1936 |

## Jumps: single-step move > 50% (14)

| id | series | bigJumps | obs | start | end |
|---|---|---|---|---|---|
| 94320 | steel (steel, korea, hr plate, kilogram) | 5 | 78 | 2020-01-01 | 2026-10-06 |
| 80746 | goes (grain oriented electrical steel) (steel, europe, coil (>600mm),  | 4 | 117 | 2017-01-01 | 2026-10-06 |
| 613 | yttria (rare earth metals, china, 99.99-99.999% avg ref price, metric  | 3 | 173 | 2011-12-15 | 2026-10-19 |
| 42605 | 430 (stainless steel, europe, cr coil, metric ton) | 3 | 152 | 2014-01-01 | 2026-10-06 |
| 1228 | nickel (non ferrous metals, india, primary, kilogram) | 2 | 3350 | 2011-12-30 | 2026-10-23 |
| 184 | palladium (precious metals, united states, sponge 99.95% purity, troy  | 1 | 3299 | 2012-01-03 | 2026-10-26 |
| 468 | 409 (stainless steel, united states, 2d (0.06 in x 48 in) sheet, pound | 1 | 504 | 2020-01-01 | 2026-10-26 |
| 1189 | 430-coil (stainless surcharges, united states, nas surcharge, pound) | 1 | 159 | 2011-10-26 | 2026-10-26 |
| 33076 | steel (steel, europe, crc, metric ton) | 1 | 154 | 2014-01-01 | 2026-10-06 |
| 49797 | 304 (stainless steel, europe, round bar (<25mm), metric ton) | 1 | 154 | 2014-01-01 | 2026-10-06 |
| 80747 | goes (grain oriented electrical steel) (steel, europe, coil (<600mm),  | 1 | 116 | 2017-01-01 | 2026-10-06 |
| 82101 | aluminum (non ferrous metals, united states, aup (mw premium) future 3 | 1 | 1181 | 2019-01-01 | 2026-10-23 |
| 82102 | aluminum (non ferrous metals, united states, aup (mw premium) spot, po | 1 | 1321 | 2019-01-01 | 2026-10-23 |
| 229605 | yttrium (rare earth metals, northeast asia, , kilogram) | 1 | 68 | 2020-12-01 | 2026-10-01 |

## Tradable, proprietary (the series worth building signals on) (38)

| id | series | obs | start | recentObs | staleDays |
|---|---|---|---|---|---|
| 187 | platinum (precious metals, united states, sponge 99.95% purity, troy o | 3413 | 2012-01-03 | 710 | 0 |
| 457 | nickel (non ferrous metals, china, primary, metric ton) | 3130 | 2011-12-30 | 614 | 0 |
| 821 | zinc (non ferrous metals, china, primary cash, metric ton) | 3044 | 2011-12-30 | 612 | 0 |
| 1072 | aluminum (non ferrous metals, india, primary cash, kilogram) | 3452 | 2011-12-30 | 635 | 0 |
| 1337 | zinc (non ferrous metals, india, primary cash, kilogram) | 3467 | 2011-12-31 | 643 | 0 |
| 270581 | dysprosium oxide (rare earth metals, china, 99.5%min fob, kilogram) | 3055 | 2013-03-21 | 667 | 0 |
| 270585 | electrical steel (stainless steel, china, grain oriented 130 0.3*980mm | 3272 | 2012-06-14 | 660 | 0 |
| 270601 | ferro-chrome (ferro alloys, china, kazakhstan cr 68%min, c 8.5%max in  | 1953 | 2017-12-18 | 659 | 0 |
| 270612 | ferro-holmium (rare earth metals, china, 80% exw, kilogram) | 3156 | 2012-10-29 | 654 | 0 |
| 270704 | h-beam steel (steel, shanghai, q235 200*200mm in warehouse, metric ton | 3342 | 2012-03-08 | 662 | 0 |
| 270787 | lithium carbonate (minor metals, america, 99.5%min fob south, kilogram | 1818 | 2018-01-31 | 638 | 0 |
| 270789 | lithium hydroxide monohydrate (minor metals, china, lioh 56.5%min, mag | 2465 | 2015-10-29 | 661 | 0 |
| 270800 | lutetium oxide (rare earth metals, exw, exw, kilogram) | 1491 | 2019-11-21 | 659 | 0 |
| 270840 | manganese dioxide (minor metals, china, alkaline 91%min exw, metric to | 3138 | 2013-01-04 | 661 | 0 |
| 270860 | manganese sulfate (minor metals, china, mn 32%min exw, metric ton) | 1967 | 2017-11-22 | 662 | 0 |
| 270879 | molybdenum bar (minor metals, china, 99.9%min exw, kilogram) | 3332 | 2011-12-30 | 652 | 0 |
| 270898 | ndfeb (rare earth metals, china, sintered rough 35m exw, kilogram) | 1170 | 2021-02-22 | 637 | 0 |
| 270899 | ndfeb (rare earth metals, china, sintered rough 45m exw, kilogram) | 1165 | 2021-02-22 | 637 | 0 |
| 270900 | ndfeb (rare earth metals, china, sintered rough 50m exw, kilogram) | 1175 | 2021-02-22 | 642 | 0 |
| 270901 | ndfeb (rare earth metals, china, sintered rough 35h exw, kilogram) | 1172 | 2021-02-22 | 643 | 0 |
| 270902 | ndfeb (rare earth metals, china, sintered rough 45h exw, kilogram) | 1174 | 2021-02-22 | 642 | 0 |
| 270903 | ndfeb (rare earth metals, china, sintered rough 48h exw, kilogram) | 1174 | 2021-02-22 | 642 | 0 |
| 270904 | ndfeb (rare earth metals, china, sintered rough 50h exw, kilogram) | 1173 | 2021-02-22 | 640 | 0 |
| 270905 | neodymium metal (rare earth metals, china, 99%min exw, kilogram) | 3362 | 2011-12-30 | 652 | 0 |
| 270906 | neodymium metal (rare earth metals, china, 99%min fob, kilogram) | 3342 | 2011-12-30 | 666 | 0 |
| 270907 | neodymium oxide (rare earth metals, china, 99.5%min exw, kilogram) | 2978 | 2013-08-19 | 654 | 0 |
| 270908 | neodymium oxide (rare earth metals, china, 99.5%min fob, kilogram) | 3330 | 2011-12-30 | 665 | 0 |
| 270914 | nickel sulfate (non ferrous metals, china, ni 22%min; co 0.05%max exw, | 3315 | 2012-04-17 | 663 | 0 |
| 270922 | praseodymium metal (rare earth metals, china, 99.5%min fob, kilogram) | 3333 | 2011-12-30 | 664 | 0 |
| 270923 | praseodymium oxide (rare earth metals, china, 99.5%min exw, kilogram) | 3103 | 2013-01-11 | 655 | 0 |
| 270924 | praseodymium oxide (rare earth metals, china, 99.5%min fob, kilogram) | 3334 | 2011-12-30 | 667 | 0 |
| 270928 | prnd mischmetal (rare earth metals, china, pr 25%, nd 75% exw, kilogra | 3374 | 2011-12-30 | 659 | 0 |
| 270929 | prnd mischmetal (rare earth metals, china, pr 25%, nd 75% fob, kilogra | 3047 | 2013-03-25 | 665 | 0 |
| 270930 | prnd oxide (rare earth metals, china, pr6o11 25%, nd2o3 75% exw, kilog | 3189 | 2012-09-20 | 655 | 0 |
| 271053 | terbium metal (rare earth metals, china, 99.9%min fob, kilogram) | 1657 | 2019-01-28 | 667 | 0 |
| 271055 | terbium oxide (rare earth metals, china, 99.99%min fob, kilogram) | 1668 | 2019-01-16 | 668 | 0 |
| 271075 | titanium plate (minor metals, china, ta2 2mm exw, kilogram) | 3131 | 2012-04-16 | 613 | 0 |
| 271078 | titanium sponge (minor metals, china, 99.7%min exw, metric ton) | 3246 | 2012-07-24 | 658 | 0 |
