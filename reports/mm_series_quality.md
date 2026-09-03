# MetalMiner series quality

Source dump: `a3b27724-historical_20260818.json.gz` · as of 2026-08-18 · 164 series.

Grades: **tradable** = daily, fresh, not frozen, no suspicious jumps; **level_only** = usable for direction/level, not for return signals (weekly/monthly cadence, partly frozen, or thin recent history); **rejected** = composite index, stopped, frozen list price, or unit flip. `public` = exchange-quoted (LME/COMEX), so no information edge.

Counts: {"rejected": 42, "level_only": 65, "tradable": 57, "tradable_public": 21, "tradable_proprietary": 36}

| category | series | tradable (proprietary / public) | level_only | rejected |
|---|---|---|---|---|
| battery prices | 7 | 0 (0 / 0) | 7 | 0 |
| ferro alloys | 2 | 1 (1 / 0) | 1 | 0 |
| minor metals | 8 | 6 (6 / 0) | 2 | 0 |
| mmi index values | 10 | 0 (0 / 0) | 0 | 10 |
| non ferrous metals | 42 | 21 (5 / 16) | 10 | 11 |
| precious metals | 9 | 5 (1 / 4) | 4 | 0 |
| rare earth metals | 30 | 17 (17 / 0) | 11 | 2 |
| scrap | 12 | 0 (0 / 0) | 12 | 0 |
| stainless steel | 12 | 1 (1 / 0) | 3 | 8 |
| stainless surcharges | 2 | 0 (0 / 0) | 1 | 1 |
| steel | 30 | 6 (5 / 1) | 14 | 10 |

## Stale: last observation > 30d before as-of (6)

| id | series | end | staleDays | obs |
|---|---|---|---|---|
| 356 | aluminum (non ferrous metals, korea, commercial 1050 sheet, kilogram) | 2025-11-20 | 271 | 265 |
| 581 | aluminum (non ferrous metals, korea, 5052 coil premium over 1050, kilo | 2025-11-20 | 271 | 268 |
| 1044 | aluminum (non ferrous metals, korea, 3003 coil premium over 1050, kilo | 2025-11-20 | 271 | 270 |
| 618 | steel (steel, korea, rebar, metric ton) | 2026-01-01 | 229 | 359 |
| 1136 | steel (steel, korea, hrc, metric ton) | 2026-01-01 | 229 | 283 |
| 982 | steel (steel, china, slab, metric ton) | 2026-07-07 | 42 | 1512 |

## Frozen: > 40% unchanged steps or flat run > 60 (19)

| id | series | flatShare | longestFlatRun | obs | medianGapDays |
|---|---|---|---|---|---|
| 827 | 201 (stainless steel, united states, 2b ctl (0.075 in x 48 in) sheet,  | 0.9355 | 34 | 1272 | 1 |
| 468 | 409 (stainless steel, united states, 2d (0.06 in x 48 in) sheet, pound | 0.8111 | 32 | 435 | 1.0 |
| 538 | 304 (stainless steel, united states, 2b (0.075 in x 48 in) sheet, poun | 0.7251 | 34 | 332 | 1 |
| 5 | steel (steel, united states, wire rod, cwt) | 0.7184 | 22 | 1748 | 1 |
| 191 | 304 (stainless steel, united states, #4 polish vinyl ctl (0.048 in x 4 | 0.7155 | 34 | 342 | 1 |
| 434 | 316l (stainless steel, united states, 2b ctl (0.075 in x 48 in) sheet, | 0.6561 | 34 | 286 | 1 |
| 235 | 430 (stainless steel, united states, #4 polish vinyl ctl (0.048 in x 4 | 0.6234 | 32 | 240 | 1 |
| 29004 | aluminum (non ferrous metals, europe, 6082 T6 (0.08 in x 48 in) sheet, | 0.6051 | 19 | 1371 | 1.0 |
| 29003 | aluminum (non ferrous metals, europe, 5251 H32 (0.08 in x 48 in) sheet | 0.6045 | 19 | 1369 | 1.0 |
| 523 | steel (steel, united states, aluminized dds astm a463 t1 40 (0.05 in x | 0.5136 | 17 | 698 | 1 |
| 1346 | aluminum (non ferrous metals, united states, 5083 h321 (1 in x 60 in)  | 0.4868 | 13 | 1788 | 1 |
| 916 | aluminum (non ferrous metals, united states, 5052 h32 (0.06 in x 60 in | 0.4863 | 13 | 1784 | 1 |
| 1040 | aluminum (non ferrous metals, united states, 6061 t651 (0.5 in x 48 in | 0.4813 | 13 | 1767 | 1.0 |
| 663 | aluminum (non ferrous metals, united states, 3003 h14 (0.08 in x 48 in | 0.4727 | 13 | 1740 | 1 |
| 1281 | aluminum (non ferrous metals, united states, 6061 t6 (0.08 in x 48 in) | 0.4717 | 13 | 1735 | 1.0 |
| 503 | aluminum (non ferrous metals, united states, 1100 h14 (0.08 in x 48 in | 0.4522 | 13 | 1874 | 1 |
| 1477 | rare earths mmi (mmi index values, global, na, index) | 0.4506 | 34 | 1892 | 1 |
| 72095 | lmo hydroxide-based (battery prices, global, index, index) | 0.2489 | 92 | 2323 | 1.0 |
| 72097 | nmc811 hydroxide-based (battery prices, global, index, index) | 0.2481 | 92 | 2327 | 1.0 |

## Holes: max gap > 120d in a daily/weekly series (16)

| id | series | maxGapDays | medianGapDays | obs |
|---|---|---|---|---|
| 356 | aluminum (non ferrous metals, korea, commercial 1050 sheet, kilogram) | 815 | 8.0 | 265 |
| 581 | aluminum (non ferrous metals, korea, 5052 coil premium over 1050, kilo | 815 | 8 | 268 |
| 1044 | aluminum (non ferrous metals, korea, 3003 coil premium over 1050, kilo | 815 | 8 | 270 |
| 1248 | steel (steel, china, crc, metric ton) | 401 | 1.0 | 1765 |
| 613 | yttria (rare earth metals, china, 99.99-99.999% avg ref price, metric  | 395 | 15 | 172 |
| 94902 | ruthenium (precious metals, united states, granules min. 99.90%, kilog | 347 | 2 | 1478 |
| 414 | steel (steel, china, hdg coil, metric ton) | 316 | 5 | 438 |
| 199342 | lanthanum-cerium mixed metal (rare earth metals, china, trem>99%;ce/tr | 316 | 7.0 | 227 |
| 982 | steel (steel, china, slab, metric ton) | 314 | 2 | 1512 |
| 539 | aluminum (non ferrous metals, china, aluminum billet, metric ton) | 302 | 1 | 1712 |
| 1477 | rare earths mmi (mmi index values, global, na, index) | 243 | 1 | 1892 |
| 1478 | raw steels mmi (mmi index values, global, na, index) | 125 | 1.0 | 1909 |
| 1479 | renewables mmi (mmi index values, global, na, index) | 124 | 1 | 1874 |
| 1472 | automotive mmi (mmi index values, global, na, index) | 122 | 1 | 1900 |
| 199344 | neodymium metal (rare earth metals, china, trem>99%;nd/rem:99~99.9%;fe | 122 | 2 | 1174 |
| 1471 | aluminum mmi (mmi index values, global, na, index) | 121 | 1.0 | 1867 |

## Jumps: single-step move > 50% (15)

| id | series | bigJumps | obs | start | end |
|---|---|---|---|---|---|
| 94320 | steel (steel, korea, hr plate, kilogram) | 5 | 76 | 2020-01-01 | 2026-08-06 |
| 80746 | goes (grain oriented electrical steel) (steel, europe, coil (>600mm),  | 4 | 115 | 2017-01-01 | 2026-08-06 |
| 613 | yttria (rare earth metals, china, 99.99-99.999% avg ref price, metric  | 3 | 172 | 2011-12-15 | 2026-08-14 |
| 1228 | nickel (non ferrous metals, india, primary, kilogram) | 2 | 3305 | 2011-12-30 | 2026-08-17 |
| 33076 | steel (steel, europe, crc, metric ton) | 2 | 152 | 2014-01-01 | 2026-08-06 |
| 42605 | 430 (stainless steel, europe, cr coil, metric ton) | 2 | 150 | 2014-01-01 | 2026-08-06 |
| 184 | palladium (precious metals, united states, sponge 99.95% purity, troy  | 1 | 3254 | 2012-01-03 | 2026-08-17 |
| 468 | 409 (stainless steel, united states, 2d (0.06 in x 48 in) sheet, pound | 1 | 435 | 2020-01-01 | 2026-08-18 |
| 1189 | 430-coil (stainless surcharges, united states, nas surcharge, pound) | 1 | 156 | 2011-10-26 | 2026-07-27 |
| 33077 | steel (steel, europe, plate, metric ton) | 1 | 152 | 2014-01-01 | 2026-08-06 |
| 49797 | 304 (stainless steel, europe, round bar (<25mm), metric ton) | 1 | 152 | 2014-01-01 | 2026-08-06 |
| 80747 | goes (grain oriented electrical steel) (steel, europe, coil (<600mm),  | 1 | 114 | 2017-01-01 | 2026-08-06 |
| 82101 | aluminum (non ferrous metals, united states, aup (mw premium) future 3 | 1 | 1140 | 2019-01-01 | 2026-08-14 |
| 82102 | aluminum (non ferrous metals, united states, aup (mw premium) spot, po | 1 | 1281 | 2019-01-01 | 2026-08-14 |
| 229605 | yttrium (rare earth metals, northeast asia, , kilogram) | 1 | 66 | 2020-12-01 | 2026-08-01 |

## Tradable, proprietary (the series worth building signals on) (36)

| id | series | obs | start | recentObs | staleDays |
|---|---|---|---|---|---|
| 187 | platinum (precious metals, united states, sponge 99.95% purity, troy o | 3369 | 2012-01-03 | 711 | 1 |
| 258 | steel (steel, china, hrc, short ton) | 2079 | 2011-12-30 | 934 | 1 |
| 393 | steel (steel, china, plate, metric ton) | 2002 | 2011-12-30 | 929 | 1 |
| 457 | nickel (non ferrous metals, china, primary, metric ton) | 3089 | 2011-12-30 | 613 | 1 |
| 733 | steel (steel, china, rebar, metric ton) | 2157 | 2011-12-28 | 926 | 1 |
| 821 | zinc (non ferrous metals, china, primary cash, metric ton) | 3002 | 2011-12-30 | 610 | 1 |
| 1072 | aluminum (non ferrous metals, india, primary cash, kilogram) | 3407 | 2011-12-30 | 634 | 1 |
| 1248 | steel (steel, china, crc, metric ton) | 1765 | 2011-12-22 | 896 | 1 |
| 1337 | zinc (non ferrous metals, india, primary cash, kilogram) | 3422 | 2011-12-31 | 642 | 1 |
| 270585 | electrical steel (stainless steel, china, grain oriented 130 0.3*980mm | 3225 | 2012-06-14 | 647 | 11 |
| 270601 | ferro-chrome (ferro alloys, china, kazakhstan cr 68%min, c 8.5%max in  | 1906 | 2017-12-18 | 646 | 11 |
| 270612 | ferro-holmium (rare earth metals, china, 80% exw, kilogram) | 3109 | 2012-10-29 | 641 | 11 |
| 270704 | h-beam steel (steel, shanghai, q235 200*200mm in warehouse, metric ton | 3295 | 2012-03-08 | 649 | 11 |
| 270787 | lithium carbonate (minor metals, america, 99.5%min fob south, kilogram | 1771 | 2018-01-31 | 625 | 11 |
| 270789 | lithium hydroxide monohydrate (minor metals, china, lioh 56.5%min, mag | 2418 | 2015-10-29 | 648 | 11 |
| 270800 | lutetium oxide (rare earth metals, exw, exw, kilogram) | 1444 | 2019-11-21 | 646 | 11 |
| 270840 | manganese dioxide (minor metals, china, alkaline 91%min exw, metric to | 3091 | 2013-01-04 | 648 | 11 |
| 270860 | manganese sulfate (minor metals, china, mn 32%min exw, metric ton) | 1920 | 2017-11-22 | 649 | 11 |
| 270879 | molybdenum bar (minor metals, china, 99.9%min exw, kilogram) | 3285 | 2011-12-30 | 638 | 11 |
| 270898 | ndfeb (rare earth metals, china, sintered rough 35m exw, kilogram) | 1123 | 2021-02-22 | 622 | 11 |
| 270899 | ndfeb (rare earth metals, china, sintered rough 45m exw, kilogram) | 1118 | 2021-02-22 | 623 | 11 |
| 270900 | ndfeb (rare earth metals, china, sintered rough 50m exw, kilogram) | 1128 | 2021-02-22 | 627 | 11 |
| 270901 | ndfeb (rare earth metals, china, sintered rough 35h exw, kilogram) | 1125 | 2021-02-22 | 627 | 11 |
| 270902 | ndfeb (rare earth metals, china, sintered rough 45h exw, kilogram) | 1127 | 2021-02-22 | 626 | 11 |
| 270903 | ndfeb (rare earth metals, china, sintered rough 48h exw, kilogram) | 1127 | 2021-02-22 | 627 | 11 |
| 270904 | ndfeb (rare earth metals, china, sintered rough 50h exw, kilogram) | 1126 | 2021-02-22 | 626 | 11 |
| 270905 | neodymium metal (rare earth metals, china, 99%min exw, kilogram) | 3315 | 2011-12-30 | 638 | 11 |
| 270906 | neodymium metal (rare earth metals, china, 99%min fob, kilogram) | 3295 | 2011-12-30 | 653 | 11 |
| 270907 | neodymium oxide (rare earth metals, china, 99.5%min exw, kilogram) | 2931 | 2013-08-19 | 640 | 11 |
| 270914 | nickel sulfate (non ferrous metals, china, ni 22%min; co 0.05%max exw, | 3268 | 2012-04-17 | 650 | 11 |
| 270922 | praseodymium metal (rare earth metals, china, 99.5%min fob, kilogram) | 3286 | 2011-12-30 | 650 | 11 |
| 270923 | praseodymium oxide (rare earth metals, china, 99.5%min exw, kilogram) | 3056 | 2013-01-11 | 641 | 11 |
| 270928 | prnd mischmetal (rare earth metals, china, pr 25%, nd 75% exw, kilogra | 3327 | 2011-12-30 | 645 | 11 |
| 270929 | prnd mischmetal (rare earth metals, china, pr 25%, nd 75% fob, kilogra | 3000 | 2013-03-25 | 651 | 11 |
| 270930 | prnd oxide (rare earth metals, china, pr6o11 25%, nd2o3 75% exw, kilog | 3142 | 2012-09-20 | 641 | 11 |
| 271078 | titanium sponge (minor metals, china, 99.7%min exw, metric ton) | 3199 | 2012-07-24 | 645 | 11 |
