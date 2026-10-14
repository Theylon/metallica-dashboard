# MetalMiner series quality

Source dump: `historical_latest.json.gz` · as of 2026-10-14 · 169 series.

Grades: **tradable** = daily, fresh, not frozen, no suspicious jumps; **level_only** = usable for direction/level, not for return signals (weekly/monthly cadence, partly frozen, or thin recent history); **rejected** = composite index, stopped, frozen list price, or unit flip. `public` = exchange-quoted (LME/COMEX), so no information edge.

Counts: {"rejected": 46, "level_only": 65, "tradable": 58, "tradable_public": 21, "tradable_proprietary": 37}

| category | series | tradable (proprietary / public) | level_only | rejected |
|---|---|---|---|---|
| battery prices | 7 | 0 (0 / 0) | 7 | 0 |
| ferro alloys | 2 | 1 (1 / 0) | 1 | 0 |
| minor metals | 8 | 6 (6 / 0) | 2 | 0 |
| mmi index values | 10 | 0 (0 / 0) | 0 | 10 |
| non ferrous metals | 42 | 21 (5 / 16) | 6 | 15 |
| precious metals | 9 | 5 (1 / 4) | 4 | 0 |
| rare earth metals | 35 | 22 (22 / 0) | 11 | 2 |
| scrap | 12 | 0 (0 / 0) | 10 | 2 |
| stainless steel | 12 | 1 (1 / 0) | 3 | 8 |
| stainless surcharges | 2 | 0 (0 / 0) | 1 | 1 |
| steel | 30 | 2 (1 / 1) | 20 | 8 |

## Stale: last observation > 30d before as-of (12)

| id | series | end | staleDays | obs |
|---|---|---|---|---|
| 356 | aluminum (non ferrous metals, korea, commercial 1050 sheet, kilogram) | 2025-11-20 | 328 | 265 |
| 581 | aluminum (non ferrous metals, korea, 5052 coil premium over 1050, kilo | 2025-11-20 | 328 | 268 |
| 1044 | aluminum (non ferrous metals, korea, 3003 coil premium over 1050, kilo | 2025-11-20 | 328 | 270 |
| 618 | steel (steel, korea, rebar, metric ton) | 2026-01-01 | 286 | 359 |
| 1136 | steel (steel, korea, hrc, metric ton) | 2026-01-01 | 286 | 283 |
| 290 | aluminum (non ferrous metals, europe, 6082 plate, metric ton) | 2026-08-03 | 72 | 173 |
| 408 | aluminum (non ferrous metals, europe, 5083 plate, metric ton) | 2026-08-03 | 72 | 177 |
| 429 | aluminum (non ferrous metals, europe, 6082 bar, metric ton) | 2026-08-03 | 72 | 171 |
| 552 | aluminum (non ferrous metals, europe, commercial 1050 sheet, metric to | 2026-08-03 | 72 | 180 |
| 613 | yttria (rare earth metals, china, 99.99-99.999% avg ref price, metric  | 2026-08-14 | 61 | 172 |
| 213 | steel (scrap, united states, north central / east #1 heavy melting ste | 2026-08-24 | 51 | 173 |
| 260 | steel (scrap, united states, south #1 heavy melting steel, gross ton) | 2026-08-24 | 51 | 177 |

## Frozen: > 40% unchanged steps or flat run > 60 (23)

| id | series | flatShare | longestFlatRun | obs | medianGapDays |
|---|---|---|---|---|---|
| 827 | 201 (stainless steel, united states, 2b ctl (0.075 in x 48 in) sheet,  | 0.9367 | 34 | 1329 | 1.0 |
| 468 | 409 (stainless steel, united states, 2d (0.06 in x 48 in) sheet, pound | 0.8289 | 32 | 492 | 1 |
| 191 | 304 (stainless steel, united states, #4 polish vinyl ctl (0.048 in x 4 | 0.7353 | 34 | 375 | 1.0 |
| 5 | steel (steel, united states, wire rod, cwt) | 0.7238 | 22 | 1804 | 1 |
| 538 | 304 (stainless steel, united states, 2b (0.075 in x 48 in) sheet, poun | 0.7207 | 34 | 334 | 1 |
| 434 | 316l (stainless steel, united states, 2b ctl (0.075 in x 48 in) sheet, | 0.6855 | 34 | 319 | 1.0 |
| 235 | 430 (stainless steel, united states, #4 polish vinyl ctl (0.048 in x 4 | 0.6183 | 32 | 242 | 1 |
| 29004 | aluminum (non ferrous metals, europe, 6082 T6 (0.08 in x 48 in) sheet, | 0.6083 | 19 | 1428 | 1 |
| 29003 | aluminum (non ferrous metals, europe, 5251 H32 (0.08 in x 48 in) sheet | 0.6077 | 19 | 1426 | 1 |
| 523 | steel (steel, united states, aluminized dds astm a463 t1 40 (0.05 in x | 0.5071 | 17 | 707 | 1.0 |
| 1346 | aluminum (non ferrous metals, united states, 5083 h321 (1 in x 60 in)  | 0.4837 | 13 | 1845 | 1.0 |
| 916 | aluminum (non ferrous metals, united states, 5052 h32 (0.06 in x 60 in | 0.4832 | 13 | 1841 | 1.0 |
| 1040 | aluminum (non ferrous metals, united states, 6061 t651 (0.5 in x 48 in | 0.4783 | 13 | 1824 | 1 |
| 663 | aluminum (non ferrous metals, united states, 3003 h14 (0.08 in x 48 in | 0.4699 | 13 | 1797 | 1.0 |
| 1281 | aluminum (non ferrous metals, united states, 6061 t6 (0.08 in x 48 in) | 0.469 | 13 | 1792 | 1 |
| 1477 | rare earths mmi (mmi index values, global, na, index) | 0.4646 | 34 | 1949 | 1.0 |
| 503 | aluminum (non ferrous metals, united states, 1100 h14 (0.08 in x 48 in | 0.4503 | 13 | 1931 | 1.0 |
| 72095 | lmo hydroxide-based (battery prices, global, index, index) | 0.2652 | 92 | 2380 | 1 |
| 72097 | nmc811 hydroxide-based (battery prices, global, index, index) | 0.2644 | 92 | 2384 | 1 |
| 1248 | steel (steel, china, crc, metric ton) | 0.2316 | 91 | 1823 | 1.0 |
| 393 | steel (steel, china, plate, metric ton) | 0.205 | 91 | 2060 | 1 |
| 258 | steel (steel, china, hrc, short ton) | 0.1976 | 91 | 2137 | 1.0 |
| 733 | steel (steel, china, rebar, metric ton) | 0.1902 | 91 | 2215 | 1.0 |

## Holes: max gap > 120d in a daily/weekly series (16)

| id | series | maxGapDays | medianGapDays | obs |
|---|---|---|---|---|
| 356 | aluminum (non ferrous metals, korea, commercial 1050 sheet, kilogram) | 815 | 8.0 | 265 |
| 581 | aluminum (non ferrous metals, korea, 5052 coil premium over 1050, kilo | 815 | 8 | 268 |
| 1044 | aluminum (non ferrous metals, korea, 3003 coil premium over 1050, kilo | 815 | 8 | 270 |
| 1248 | steel (steel, china, crc, metric ton) | 401 | 1.0 | 1823 |
| 613 | yttria (rare earth metals, china, 99.99-99.999% avg ref price, metric  | 395 | 15 | 172 |
| 94902 | ruthenium (precious metals, united states, granules min. 99.90%, kilog | 347 | 2.0 | 1507 |
| 414 | steel (steel, china, hdg coil, metric ton) | 316 | 5.0 | 447 |
| 199342 | lanthanum-cerium mixed metal (rare earth metals, china, trem>99%;ce/tr | 316 | 7 | 228 |
| 982 | steel (steel, china, slab, metric ton) | 314 | 2 | 1524 |
| 539 | aluminum (non ferrous metals, china, aluminum billet, metric ton) | 302 | 1.0 | 1747 |
| 1477 | rare earths mmi (mmi index values, global, na, index) | 243 | 1.0 | 1949 |
| 1478 | raw steels mmi (mmi index values, global, na, index) | 125 | 1 | 1966 |
| 1479 | renewables mmi (mmi index values, global, na, index) | 124 | 1.0 | 1931 |
| 1472 | automotive mmi (mmi index values, global, na, index) | 122 | 1.0 | 1957 |
| 199344 | neodymium metal (rare earth metals, china, trem>99%;nd/rem:99~99.9%;fe | 122 | 2.0 | 1177 |
| 1471 | aluminum mmi (mmi index values, global, na, index) | 121 | 1 | 1924 |

## Jumps: single-step move > 50% (14)

| id | series | bigJumps | obs | start | end |
|---|---|---|---|---|---|
| 94320 | steel (steel, korea, hr plate, kilogram) | 5 | 78 | 2020-01-01 | 2026-10-06 |
| 80746 | goes (grain oriented electrical steel) (steel, europe, coil (>600mm),  | 4 | 117 | 2017-01-01 | 2026-10-06 |
| 613 | yttria (rare earth metals, china, 99.99-99.999% avg ref price, metric  | 3 | 172 | 2011-12-15 | 2026-08-14 |
| 42605 | 430 (stainless steel, europe, cr coil, metric ton) | 3 | 152 | 2014-01-01 | 2026-10-06 |
| 1228 | nickel (non ferrous metals, india, primary, kilogram) | 2 | 3344 | 2011-12-30 | 2026-10-14 |
| 184 | palladium (precious metals, united states, sponge 99.95% purity, troy  | 1 | 3293 | 2012-01-03 | 2026-10-14 |
| 468 | 409 (stainless steel, united states, 2d (0.06 in x 48 in) sheet, pound | 1 | 492 | 2020-01-01 | 2026-10-14 |
| 1189 | 430-coil (stainless surcharges, united states, nas surcharge, pound) | 1 | 158 | 2011-10-26 | 2026-09-28 |
| 33076 | steel (steel, europe, crc, metric ton) | 1 | 154 | 2014-01-01 | 2026-10-06 |
| 49797 | 304 (stainless steel, europe, round bar (<25mm), metric ton) | 1 | 154 | 2014-01-01 | 2026-10-06 |
| 80747 | goes (grain oriented electrical steel) (steel, europe, coil (<600mm),  | 1 | 116 | 2017-01-01 | 2026-10-06 |
| 82101 | aluminum (non ferrous metals, united states, aup (mw premium) future 3 | 1 | 1174 | 2019-01-01 | 2026-10-08 |
| 82102 | aluminum (non ferrous metals, united states, aup (mw premium) spot, po | 1 | 1312 | 2019-01-01 | 2026-10-12 |
| 229605 | yttrium (rare earth metals, northeast asia, , kilogram) | 1 | 68 | 2020-12-01 | 2026-10-01 |

## Tradable, proprietary (the series worth building signals on) (37)

| id | series | obs | start | recentObs | staleDays |
|---|---|---|---|---|---|
| 187 | platinum (precious metals, united states, sponge 99.95% purity, troy o | 3406 | 2012-01-03 | 712 | 0 |
| 457 | nickel (non ferrous metals, china, primary, metric ton) | 3123 | 2011-12-30 | 615 | 0 |
| 821 | zinc (non ferrous metals, china, primary cash, metric ton) | 3038 | 2011-12-30 | 614 | 0 |
| 1072 | aluminum (non ferrous metals, india, primary cash, kilogram) | 3445 | 2011-12-30 | 636 | 0 |
| 1337 | zinc (non ferrous metals, india, primary cash, kilogram) | 3460 | 2011-12-31 | 644 | 0 |
| 270581 | dysprosium oxide (rare earth metals, china, 99.5%min fob, kilogram) | 3015 | 2013-03-21 | 636 | 21 |
| 270585 | electrical steel (stainless steel, china, grain oriented 130 0.3*980mm | 3232 | 2012-06-14 | 629 | 21 |
| 270601 | ferro-chrome (ferro alloys, china, kazakhstan cr 68%min, c 8.5%max in  | 1913 | 2017-12-18 | 628 | 21 |
| 270612 | ferro-holmium (rare earth metals, china, 80% exw, kilogram) | 3116 | 2012-10-29 | 623 | 21 |
| 270704 | h-beam steel (steel, shanghai, q235 200*200mm in warehouse, metric ton | 3302 | 2012-03-08 | 631 | 21 |
| 270787 | lithium carbonate (minor metals, america, 99.5%min fob south, kilogram | 1777 | 2018-01-31 | 606 | 21 |
| 270789 | lithium hydroxide monohydrate (minor metals, china, lioh 56.5%min, mag | 2425 | 2015-10-29 | 630 | 21 |
| 270800 | lutetium oxide (rare earth metals, exw, exw, kilogram) | 1451 | 2019-11-21 | 628 | 21 |
| 270840 | manganese dioxide (minor metals, china, alkaline 91%min exw, metric to | 3098 | 2013-01-04 | 630 | 21 |
| 270860 | manganese sulfate (minor metals, china, mn 32%min exw, metric ton) | 1927 | 2017-11-22 | 631 | 21 |
| 270879 | molybdenum bar (minor metals, china, 99.9%min exw, kilogram) | 3292 | 2011-12-30 | 620 | 21 |
| 270898 | ndfeb (rare earth metals, china, sintered rough 35m exw, kilogram) | 1130 | 2021-02-22 | 606 | 21 |
| 270899 | ndfeb (rare earth metals, china, sintered rough 45m exw, kilogram) | 1125 | 2021-02-22 | 605 | 21 |
| 270900 | ndfeb (rare earth metals, china, sintered rough 50m exw, kilogram) | 1135 | 2021-02-22 | 610 | 21 |
| 270901 | ndfeb (rare earth metals, china, sintered rough 35h exw, kilogram) | 1132 | 2021-02-22 | 611 | 21 |
| 270902 | ndfeb (rare earth metals, china, sintered rough 45h exw, kilogram) | 1134 | 2021-02-22 | 610 | 21 |
| 270903 | ndfeb (rare earth metals, china, sintered rough 48h exw, kilogram) | 1134 | 2021-02-22 | 610 | 21 |
| 270904 | ndfeb (rare earth metals, china, sintered rough 50h exw, kilogram) | 1133 | 2021-02-22 | 609 | 21 |
| 270905 | neodymium metal (rare earth metals, china, 99%min exw, kilogram) | 3322 | 2011-12-30 | 621 | 21 |
| 270906 | neodymium metal (rare earth metals, china, 99%min fob, kilogram) | 3302 | 2011-12-30 | 635 | 21 |
| 270907 | neodymium oxide (rare earth metals, china, 99.5%min exw, kilogram) | 2938 | 2013-08-19 | 623 | 21 |
| 270908 | neodymium oxide (rare earth metals, china, 99.5%min fob, kilogram) | 3290 | 2011-12-30 | 634 | 21 |
| 270914 | nickel sulfate (non ferrous metals, china, ni 22%min; co 0.05%max exw, | 3275 | 2012-04-17 | 632 | 21 |
| 270922 | praseodymium metal (rare earth metals, china, 99.5%min fob, kilogram) | 3293 | 2011-12-30 | 633 | 21 |
| 270923 | praseodymium oxide (rare earth metals, china, 99.5%min exw, kilogram) | 3063 | 2013-01-11 | 624 | 21 |
| 270924 | praseodymium oxide (rare earth metals, china, 99.5%min fob, kilogram) | 3294 | 2011-12-30 | 636 | 21 |
| 270928 | prnd mischmetal (rare earth metals, china, pr 25%, nd 75% exw, kilogra | 3334 | 2011-12-30 | 628 | 21 |
| 270929 | prnd mischmetal (rare earth metals, china, pr 25%, nd 75% fob, kilogra | 3007 | 2013-03-25 | 634 | 21 |
| 270930 | prnd oxide (rare earth metals, china, pr6o11 25%, nd2o3 75% exw, kilog | 3149 | 2012-09-20 | 624 | 21 |
| 271053 | terbium metal (rare earth metals, china, 99.9%min fob, kilogram) | 1617 | 2019-01-28 | 636 | 21 |
| 271055 | terbium oxide (rare earth metals, china, 99.99%min fob, kilogram) | 1628 | 2019-01-16 | 637 | 21 |
| 271078 | titanium sponge (minor metals, china, 99.7%min exw, metric ton) | 3206 | 2012-07-24 | 627 | 21 |
