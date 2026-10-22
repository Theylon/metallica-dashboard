# MetalMiner series quality

Source dump: `historical_latest.json.gz` · as of 2026-10-22 · 169 series.

Grades: **tradable** = daily, fresh, not frozen, no suspicious jumps; **level_only** = usable for direction/level, not for return signals (weekly/monthly cadence, partly frozen, or thin recent history); **rejected** = composite index, stopped, frozen list price, or unit flip. `public` = exchange-quoted (LME/COMEX), so no information edge.

Counts: {"rejected": 56, "level_only": 54, "tradable": 59, "tradable_public": 21, "tradable_proprietary": 38}

| category | series | tradable (proprietary / public) | level_only | rejected |
|---|---|---|---|---|
| battery prices | 7 | 0 (0 / 0) | 7 | 0 |
| ferro alloys | 2 | 1 (1 / 0) | 1 | 0 |
| minor metals | 8 | 7 (7 / 0) | 1 | 0 |
| mmi index values | 10 | 0 (0 / 0) | 0 | 10 |
| non ferrous metals | 42 | 21 (5 / 16) | 6 | 15 |
| precious metals | 9 | 5 (1 / 4) | 4 | 0 |
| rare earth metals | 35 | 22 (22 / 0) | 11 | 2 |
| scrap | 12 | 0 (0 / 0) | 0 | 12 |
| stainless steel | 12 | 1 (1 / 0) | 3 | 8 |
| stainless surcharges | 2 | 0 (0 / 0) | 1 | 1 |
| steel | 30 | 2 (1 / 1) | 20 | 8 |

## Stale: last observation > 30d before as-of (21)

| id | series | end | staleDays | obs |
|---|---|---|---|---|
| 356 | aluminum (non ferrous metals, korea, commercial 1050 sheet, kilogram) | 2025-11-20 | 336 | 265 |
| 581 | aluminum (non ferrous metals, korea, 5052 coil premium over 1050, kilo | 2025-11-20 | 336 | 268 |
| 1044 | aluminum (non ferrous metals, korea, 3003 coil premium over 1050, kilo | 2025-11-20 | 336 | 270 |
| 618 | steel (steel, korea, rebar, metric ton) | 2026-01-01 | 294 | 359 |
| 1136 | steel (steel, korea, hrc, metric ton) | 2026-01-01 | 294 | 283 |
| 290 | aluminum (non ferrous metals, europe, 6082 plate, metric ton) | 2026-08-03 | 80 | 173 |
| 408 | aluminum (non ferrous metals, europe, 5083 plate, metric ton) | 2026-08-03 | 80 | 177 |
| 429 | aluminum (non ferrous metals, europe, 6082 bar, metric ton) | 2026-08-03 | 80 | 171 |
| 552 | aluminum (non ferrous metals, europe, commercial 1050 sheet, metric to | 2026-08-03 | 80 | 180 |
| 213 | steel (scrap, united states, north central / east #1 heavy melting ste | 2026-08-24 | 59 | 173 |
| 260 | steel (scrap, united states, south #1 heavy melting steel, gross ton) | 2026-08-24 | 59 | 177 |
| 48 | steel (scrap, united states, total us prompt industrial comp., gross t | 2026-09-21 | 31 | 173 |
| 132 | steel (scrap, united states, south prompt industrial comp., gross ton) | 2026-09-21 | 31 | 178 |
| 153 | steel (scrap, united states, total us shredded scrap (#2), gross ton) | 2026-09-21 | 31 | 177 |
| 486 | steel (scrap, united states, north midwest #1 heavy melting steel, gro | 2026-09-21 | 31 | 176 |
| 561 | steel (scrap, united states, north central / east prompt industrial co | 2026-09-21 | 31 | 161 |
| 671 | steel (scrap, united states, north midwest shredded scrap (#2), gross  | 2026-09-21 | 31 | 176 |
| 715 | steel (scrap, united states, south shredded scrap (#2), gross ton) | 2026-09-21 | 31 | 173 |
| 1152 | steel (scrap, united states, total us #1 heavy melting steel, gross to | 2026-09-21 | 31 | 177 |
| 1373 | steel (scrap, united states, north midwest prompt industrial comp., gr | 2026-09-21 | 31 | 171 |
| 1456 | steel (scrap, united states, north central / east shredded scrap (#2), | 2026-09-21 | 31 | 163 |

## Frozen: > 40% unchanged steps or flat run > 60 (23)

| id | series | flatShare | longestFlatRun | obs | medianGapDays |
|---|---|---|---|---|---|
| 827 | 201 (stainless steel, united states, 2b ctl (0.075 in x 48 in) sheet,  | 0.9371 | 34 | 1337 | 1.0 |
| 468 | 409 (stainless steel, united states, 2d (0.06 in x 48 in) sheet, pound | 0.8317 | 32 | 500 | 1 |
| 191 | 304 (stainless steel, united states, #4 polish vinyl ctl (0.048 in x 4 | 0.7353 | 34 | 375 | 1.0 |
| 5 | steel (steel, united states, wire rod, cwt) | 0.7245 | 22 | 1812 | 1 |
| 538 | 304 (stainless steel, united states, 2b (0.075 in x 48 in) sheet, poun | 0.7207 | 34 | 334 | 1 |
| 434 | 316l (stainless steel, united states, 2b ctl (0.075 in x 48 in) sheet, | 0.6855 | 34 | 319 | 1.0 |
| 235 | 430 (stainless steel, united states, #4 polish vinyl ctl (0.048 in x 4 | 0.6183 | 32 | 242 | 1 |
| 29004 | aluminum (non ferrous metals, europe, 6082 T6 (0.08 in x 48 in) sheet, | 0.6105 | 19 | 1436 | 1 |
| 29003 | aluminum (non ferrous metals, europe, 5251 H32 (0.08 in x 48 in) sheet | 0.6099 | 19 | 1434 | 1 |
| 523 | steel (steel, united states, aluminized dds astm a463 t1 40 (0.05 in x | 0.5064 | 17 | 708 | 1 |
| 1346 | aluminum (non ferrous metals, united states, 5083 h321 (1 in x 60 in)  | 0.4833 | 13 | 1853 | 1.0 |
| 916 | aluminum (non ferrous metals, united states, 5052 h32 (0.06 in x 60 in | 0.4827 | 13 | 1849 | 1.0 |
| 1040 | aluminum (non ferrous metals, united states, 6061 t651 (0.5 in x 48 in | 0.4779 | 13 | 1832 | 1 |
| 663 | aluminum (non ferrous metals, united states, 3003 h14 (0.08 in x 48 in | 0.4695 | 13 | 1805 | 1.0 |
| 1281 | aluminum (non ferrous metals, united states, 6061 t6 (0.08 in x 48 in) | 0.4686 | 13 | 1800 | 1 |
| 1477 | rare earths mmi (mmi index values, global, na, index) | 0.4632 | 34 | 1957 | 1.0 |
| 503 | aluminum (non ferrous metals, united states, 1100 h14 (0.08 in x 48 in | 0.4499 | 13 | 1939 | 1.0 |
| 72095 | lmo hydroxide-based (battery prices, global, index, index) | 0.2648 | 92 | 2388 | 1 |
| 72097 | nmc811 hydroxide-based (battery prices, global, index, index) | 0.2639 | 92 | 2392 | 1 |
| 1248 | steel (steel, china, crc, metric ton) | 0.2311 | 91 | 1831 | 1.0 |
| 393 | steel (steel, china, plate, metric ton) | 0.2046 | 91 | 2068 | 1 |
| 258 | steel (steel, china, hrc, short ton) | 0.1973 | 91 | 2145 | 1.0 |
| 733 | steel (steel, china, rebar, metric ton) | 0.1899 | 91 | 2223 | 1.0 |

## Holes: max gap > 120d in a daily/weekly series (16)

| id | series | maxGapDays | medianGapDays | obs |
|---|---|---|---|---|
| 356 | aluminum (non ferrous metals, korea, commercial 1050 sheet, kilogram) | 815 | 8.0 | 265 |
| 581 | aluminum (non ferrous metals, korea, 5052 coil premium over 1050, kilo | 815 | 8 | 268 |
| 1044 | aluminum (non ferrous metals, korea, 3003 coil premium over 1050, kilo | 815 | 8 | 270 |
| 1248 | steel (steel, china, crc, metric ton) | 401 | 1.0 | 1831 |
| 613 | yttria (rare earth metals, china, 99.99-99.999% avg ref price, metric  | 395 | 15.0 | 173 |
| 94902 | ruthenium (precious metals, united states, granules min. 99.90%, kilog | 347 | 2 | 1510 |
| 414 | steel (steel, china, hdg coil, metric ton) | 316 | 5 | 450 |
| 199342 | lanthanum-cerium mixed metal (rare earth metals, china, trem>99%;ce/tr | 316 | 7 | 228 |
| 982 | steel (steel, china, slab, metric ton) | 314 | 2.0 | 1527 |
| 539 | aluminum (non ferrous metals, china, aluminum billet, metric ton) | 302 | 1 | 1752 |
| 1477 | rare earths mmi (mmi index values, global, na, index) | 243 | 1.0 | 1957 |
| 1478 | raw steels mmi (mmi index values, global, na, index) | 125 | 1 | 1974 |
| 1479 | renewables mmi (mmi index values, global, na, index) | 124 | 1.0 | 1939 |
| 1472 | automotive mmi (mmi index values, global, na, index) | 122 | 1.0 | 1965 |
| 199344 | neodymium metal (rare earth metals, china, trem>99%;nd/rem:99~99.9%;fe | 122 | 2 | 1178 |
| 1471 | aluminum mmi (mmi index values, global, na, index) | 121 | 1 | 1932 |

## Jumps: single-step move > 50% (14)

| id | series | bigJumps | obs | start | end |
|---|---|---|---|---|---|
| 94320 | steel (steel, korea, hr plate, kilogram) | 5 | 78 | 2020-01-01 | 2026-10-06 |
| 80746 | goes (grain oriented electrical steel) (steel, europe, coil (>600mm),  | 4 | 117 | 2017-01-01 | 2026-10-06 |
| 613 | yttria (rare earth metals, china, 99.99-99.999% avg ref price, metric  | 3 | 173 | 2011-12-15 | 2026-10-19 |
| 42605 | 430 (stainless steel, europe, cr coil, metric ton) | 3 | 152 | 2014-01-01 | 2026-10-06 |
| 1228 | nickel (non ferrous metals, india, primary, kilogram) | 2 | 3349 | 2011-12-30 | 2026-10-22 |
| 184 | palladium (precious metals, united states, sponge 99.95% purity, troy  | 1 | 3298 | 2012-01-03 | 2026-10-22 |
| 468 | 409 (stainless steel, united states, 2d (0.06 in x 48 in) sheet, pound | 1 | 500 | 2020-01-01 | 2026-10-22 |
| 1189 | 430-coil (stainless surcharges, united states, nas surcharge, pound) | 1 | 158 | 2011-10-26 | 2026-09-28 |
| 33076 | steel (steel, europe, crc, metric ton) | 1 | 154 | 2014-01-01 | 2026-10-06 |
| 49797 | 304 (stainless steel, europe, round bar (<25mm), metric ton) | 1 | 154 | 2014-01-01 | 2026-10-06 |
| 80747 | goes (grain oriented electrical steel) (steel, europe, coil (<600mm),  | 1 | 116 | 2017-01-01 | 2026-10-06 |
| 82101 | aluminum (non ferrous metals, united states, aup (mw premium) future 3 | 1 | 1180 | 2019-01-01 | 2026-10-21 |
| 82102 | aluminum (non ferrous metals, united states, aup (mw premium) spot, po | 1 | 1319 | 2019-01-01 | 2026-10-21 |
| 229605 | yttrium (rare earth metals, northeast asia, , kilogram) | 1 | 68 | 2020-12-01 | 2026-10-01 |

## Tradable, proprietary (the series worth building signals on) (38)

| id | series | obs | start | recentObs | staleDays |
|---|---|---|---|---|---|
| 187 | platinum (precious metals, united states, sponge 99.95% purity, troy o | 3411 | 2012-01-03 | 712 | 0 |
| 457 | nickel (non ferrous metals, china, primary, metric ton) | 3128 | 2011-12-30 | 616 | 0 |
| 821 | zinc (non ferrous metals, china, primary cash, metric ton) | 3042 | 2011-12-30 | 614 | 0 |
| 1072 | aluminum (non ferrous metals, india, primary cash, kilogram) | 3450 | 2011-12-30 | 637 | 0 |
| 1337 | zinc (non ferrous metals, india, primary cash, kilogram) | 3465 | 2011-12-31 | 645 | 0 |
| 270581 | dysprosium oxide (rare earth metals, china, 99.5%min fob, kilogram) | 3051 | 2013-03-21 | 667 | 0 |
| 270585 | electrical steel (stainless steel, china, grain oriented 130 0.3*980mm | 3266 | 2012-06-14 | 658 | 0 |
| 270601 | ferro-chrome (ferro alloys, china, kazakhstan cr 68%min, c 8.5%max in  | 1948 | 2017-12-18 | 658 | 0 |
| 270612 | ferro-holmium (rare earth metals, china, 80% exw, kilogram) | 3150 | 2012-10-29 | 652 | 0 |
| 270704 | h-beam steel (steel, shanghai, q235 200*200mm in warehouse, metric ton | 3338 | 2012-03-08 | 662 | 0 |
| 270787 | lithium carbonate (minor metals, america, 99.5%min fob south, kilogram | 1811 | 2018-01-31 | 635 | 0 |
| 270789 | lithium hydroxide monohydrate (minor metals, china, lioh 56.5%min, mag | 2460 | 2015-10-29 | 660 | 0 |
| 270800 | lutetium oxide (rare earth metals, exw, exw, kilogram) | 1485 | 2019-11-21 | 657 | 0 |
| 270840 | manganese dioxide (minor metals, china, alkaline 91%min exw, metric to | 3130 | 2013-01-04 | 657 | 0 |
| 270860 | manganese sulfate (minor metals, china, mn 32%min exw, metric ton) | 1962 | 2017-11-22 | 661 | 0 |
| 270879 | molybdenum bar (minor metals, china, 99.9%min exw, kilogram) | 3325 | 2011-12-30 | 649 | 0 |
| 270898 | ndfeb (rare earth metals, china, sintered rough 35m exw, kilogram) | 1165 | 2021-02-22 | 636 | 0 |
| 270899 | ndfeb (rare earth metals, china, sintered rough 45m exw, kilogram) | 1161 | 2021-02-22 | 636 | 0 |
| 270900 | ndfeb (rare earth metals, china, sintered rough 50m exw, kilogram) | 1167 | 2021-02-22 | 637 | 0 |
| 270901 | ndfeb (rare earth metals, china, sintered rough 35h exw, kilogram) | 1166 | 2021-02-22 | 640 | 0 |
| 270902 | ndfeb (rare earth metals, china, sintered rough 45h exw, kilogram) | 1170 | 2021-02-22 | 641 | 0 |
| 270903 | ndfeb (rare earth metals, china, sintered rough 48h exw, kilogram) | 1166 | 2021-02-22 | 637 | 0 |
| 270904 | ndfeb (rare earth metals, china, sintered rough 50h exw, kilogram) | 1168 | 2021-02-22 | 639 | 0 |
| 270905 | neodymium metal (rare earth metals, china, 99%min exw, kilogram) | 3358 | 2011-12-30 | 652 | 0 |
| 270906 | neodymium metal (rare earth metals, china, 99%min fob, kilogram) | 3336 | 2011-12-30 | 664 | 0 |
| 270907 | neodymium oxide (rare earth metals, china, 99.5%min exw, kilogram) | 2974 | 2013-08-19 | 654 | 0 |
| 270908 | neodymium oxide (rare earth metals, china, 99.5%min fob, kilogram) | 3324 | 2011-12-30 | 663 | 0 |
| 270914 | nickel sulfate (non ferrous metals, china, ni 22%min; co 0.05%max exw, | 3309 | 2012-04-17 | 661 | 0 |
| 270922 | praseodymium metal (rare earth metals, china, 99.5%min fob, kilogram) | 3328 | 2011-12-30 | 663 | 0 |
| 270923 | praseodymium oxide (rare earth metals, china, 99.5%min exw, kilogram) | 3098 | 2013-01-11 | 654 | 0 |
| 270924 | praseodymium oxide (rare earth metals, china, 99.5%min fob, kilogram) | 3328 | 2011-12-30 | 665 | 0 |
| 270928 | prnd mischmetal (rare earth metals, china, pr 25%, nd 75% exw, kilogra | 3369 | 2011-12-30 | 658 | 0 |
| 270929 | prnd mischmetal (rare earth metals, china, pr 25%, nd 75% fob, kilogra | 3042 | 2013-03-25 | 664 | 0 |
| 270930 | prnd oxide (rare earth metals, china, pr6o11 25%, nd2o3 75% exw, kilog | 3183 | 2012-09-20 | 653 | 0 |
| 271053 | terbium metal (rare earth metals, china, 99.9%min fob, kilogram) | 1653 | 2019-01-28 | 667 | 0 |
| 271055 | terbium oxide (rare earth metals, china, 99.99%min fob, kilogram) | 1663 | 2019-01-16 | 667 | 0 |
| 271075 | titanium plate (minor metals, china, ta2 2mm exw, kilogram) | 3126 | 2012-04-16 | 612 | 0 |
| 271078 | titanium sponge (minor metals, china, 99.7%min exw, metric ton) | 3241 | 2012-07-24 | 657 | 0 |
