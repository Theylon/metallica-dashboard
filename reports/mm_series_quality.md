# MetalMiner series quality

Source dump: `historical_latest.json.gz` · as of 2026-11-09 · 169 series.

Grades: **tradable** = daily, fresh, not frozen, no suspicious jumps; **level_only** = usable for direction/level, not for return signals (weekly/monthly cadence, partly frozen, or thin recent history); **rejected** = composite index, stopped, frozen list price, or unit flip. `public` = exchange-quoted (LME/COMEX), so no information edge.

Counts: {"rejected": 47, "level_only": 63, "tradable": 59, "tradable_public": 21, "tradable_proprietary": 38}

| category | series | tradable (proprietary / public) | level_only | rejected |
|---|---|---|---|---|
| battery prices | 7 | 0 (0 / 0) | 7 | 0 |
| ferro alloys | 2 | 1 (1 / 0) | 1 | 0 |
| minor metals | 8 | 7 (7 / 0) | 1 | 0 |
| mmi index values | 10 | 0 (0 / 0) | 0 | 10 |
| non ferrous metals | 42 | 21 (5 / 16) | 10 | 11 |
| precious metals | 9 | 5 (1 / 4) | 4 | 0 |
| rare earth metals | 35 | 22 (22 / 0) | 11 | 2 |
| scrap | 12 | 0 (0 / 0) | 12 | 0 |
| stainless steel | 12 | 1 (1 / 0) | 0 | 11 |
| stainless surcharges | 2 | 0 (0 / 0) | 1 | 1 |
| steel | 30 | 2 (1 / 1) | 16 | 12 |

## Stale: last observation > 30d before as-of (18)

| id | series | end | staleDays | obs |
|---|---|---|---|---|
| 356 | aluminum (non ferrous metals, korea, commercial 1050 sheet, kilogram) | 2025-11-20 | 354 | 265 |
| 581 | aluminum (non ferrous metals, korea, 5052 coil premium over 1050, kilo | 2025-11-20 | 354 | 268 |
| 1044 | aluminum (non ferrous metals, korea, 3003 coil premium over 1050, kilo | 2025-11-20 | 354 | 270 |
| 618 | steel (steel, korea, rebar, metric ton) | 2026-01-01 | 312 | 359 |
| 1136 | steel (steel, korea, hrc, metric ton) | 2026-01-01 | 312 | 283 |
| 33075 | steel (steel, europe, hrc, metric ton) | 2026-10-06 | 34 | 154 |
| 33076 | steel (steel, europe, crc, metric ton) | 2026-10-06 | 34 | 154 |
| 33077 | steel (steel, europe, plate, metric ton) | 2026-10-06 | 34 | 154 |
| 33920 | steel (steel, europe, hdg, metric ton) | 2026-10-06 | 34 | 153 |
| 42604 | 304 (stainless steel, europe, cr coil, metric ton) | 2026-10-06 | 34 | 153 |
| 42605 | 430 (stainless steel, europe, cr coil, metric ton) | 2026-10-06 | 34 | 152 |
| 49796 | 304 (stainless steel, europe, round bar (25-80 mm), metric ton) | 2026-10-06 | 34 | 154 |
| 49797 | 304 (stainless steel, europe, round bar (<25mm), metric ton) | 2026-10-06 | 34 | 154 |
| 49798 | 304 (stainless steel, europe, square bar, metric ton) | 2026-10-06 | 34 | 153 |
| 80746 | goes (grain oriented electrical steel) (steel, europe, coil (>600mm),  | 2026-10-06 | 34 | 117 |
| 80747 | goes (grain oriented electrical steel) (steel, europe, coil (<600mm),  | 2026-10-06 | 34 | 116 |
| 94320 | steel (steel, korea, hr plate, kilogram) | 2026-10-06 | 34 | 78 |
| 94323 | steel (steel, korea, cr coil, kilogram) | 2026-10-06 | 34 | 78 |

## Frozen: > 40% unchanged steps or flat run > 60 (23)

| id | series | flatShare | longestFlatRun | obs | medianGapDays |
|---|---|---|---|---|---|
| 827 | 201 (stainless steel, united states, 2b ctl (0.075 in x 48 in) sheet,  | 0.936 | 34 | 1344 | 1 |
| 468 | 409 (stainless steel, united states, 2d (0.06 in x 48 in) sheet, pound | 0.8337 | 32 | 518 | 1 |
| 191 | 304 (stainless steel, united states, #4 polish vinyl ctl (0.048 in x 4 | 0.7397 | 34 | 389 | 1.0 |
| 5 | steel (steel, united states, wire rod, cwt) | 0.7261 | 22 | 1830 | 1 |
| 538 | 304 (stainless steel, united states, 2b (0.075 in x 48 in) sheet, poun | 0.7164 | 34 | 336 | 1 |
| 434 | 316l (stainless steel, united states, 2b ctl (0.075 in x 48 in) sheet, | 0.6928 | 34 | 333 | 1.0 |
| 235 | 430 (stainless steel, united states, #4 polish vinyl ctl (0.048 in x 4 | 0.6148 | 32 | 245 | 1.0 |
| 29004 | aluminum (non ferrous metals, europe, 6082 T6 (0.08 in x 48 in) sheet, | 0.6091 | 19 | 1454 | 1 |
| 29003 | aluminum (non ferrous metals, europe, 5251 H32 (0.08 in x 48 in) sheet | 0.6085 | 19 | 1452 | 1 |
| 523 | steel (steel, united states, aluminized dds astm a463 t1 40 (0.05 in x | 0.5084 | 17 | 717 | 1.0 |
| 1346 | aluminum (non ferrous metals, united states, 5083 h321 (1 in x 60 in)  | 0.4824 | 13 | 1871 | 1.0 |
| 916 | aluminum (non ferrous metals, united states, 5052 h32 (0.06 in x 60 in | 0.4818 | 13 | 1867 | 1.0 |
| 1040 | aluminum (non ferrous metals, united states, 6061 t651 (0.5 in x 48 in | 0.477 | 13 | 1850 | 1 |
| 663 | aluminum (non ferrous metals, united states, 3003 h14 (0.08 in x 48 in | 0.4687 | 13 | 1823 | 1.0 |
| 1281 | aluminum (non ferrous metals, united states, 6061 t6 (0.08 in x 48 in) | 0.4678 | 13 | 1818 | 1 |
| 1477 | rare earths mmi (mmi index values, global, na, index) | 0.4615 | 34 | 1975 | 1.0 |
| 503 | aluminum (non ferrous metals, united states, 1100 h14 (0.08 in x 48 in | 0.4494 | 13 | 1957 | 1.0 |
| 72095 | lmo hydroxide-based (battery prices, global, index, index) | 0.2653 | 92 | 2406 | 1 |
| 72097 | nmc811 hydroxide-based (battery prices, global, index, index) | 0.264 | 92 | 2410 | 1 |
| 1248 | steel (steel, china, crc, metric ton) | 0.2305 | 91 | 1849 | 1.0 |
| 393 | steel (steel, china, plate, metric ton) | 0.2043 | 91 | 2086 | 1 |
| 258 | steel (steel, china, hrc, short ton) | 0.197 | 91 | 2163 | 1.0 |
| 733 | steel (steel, china, rebar, metric ton) | 0.1897 | 91 | 2241 | 1.0 |

## Holes: max gap > 120d in a daily/weekly series (16)

| id | series | maxGapDays | medianGapDays | obs |
|---|---|---|---|---|
| 356 | aluminum (non ferrous metals, korea, commercial 1050 sheet, kilogram) | 815 | 8.0 | 265 |
| 581 | aluminum (non ferrous metals, korea, 5052 coil premium over 1050, kilo | 815 | 8 | 268 |
| 1044 | aluminum (non ferrous metals, korea, 3003 coil premium over 1050, kilo | 815 | 8 | 270 |
| 1248 | steel (steel, china, crc, metric ton) | 401 | 1.0 | 1849 |
| 613 | yttria (rare earth metals, china, 99.99-99.999% avg ref price, metric  | 395 | 15 | 174 |
| 94902 | ruthenium (precious metals, united states, granules min. 99.90%, kilog | 347 | 2.0 | 1517 |
| 414 | steel (steel, china, hdg coil, metric ton) | 316 | 5.0 | 457 |
| 199342 | lanthanum-cerium mixed metal (rare earth metals, china, trem>99%;ce/tr | 316 | 7.0 | 229 |
| 982 | steel (steel, china, slab, metric ton) | 314 | 2 | 1534 |
| 539 | aluminum (non ferrous metals, china, aluminum billet, metric ton) | 302 | 1 | 1764 |
| 1477 | rare earths mmi (mmi index values, global, na, index) | 243 | 1.0 | 1975 |
| 1478 | raw steels mmi (mmi index values, global, na, index) | 125 | 1 | 1992 |
| 1479 | renewables mmi (mmi index values, global, na, index) | 124 | 1.0 | 1957 |
| 1472 | automotive mmi (mmi index values, global, na, index) | 122 | 1.0 | 1983 |
| 199344 | neodymium metal (rare earth metals, china, trem>99%;nd/rem:99~99.9%;fe | 122 | 2.0 | 1183 |
| 1471 | aluminum mmi (mmi index values, global, na, index) | 121 | 1 | 1950 |

## Jumps: single-step move > 50% (14)

| id | series | bigJumps | obs | start | end |
|---|---|---|---|---|---|
| 94320 | steel (steel, korea, hr plate, kilogram) | 5 | 78 | 2020-01-01 | 2026-10-06 |
| 80746 | goes (grain oriented electrical steel) (steel, europe, coil (>600mm),  | 4 | 117 | 2017-01-01 | 2026-10-06 |
| 613 | yttria (rare earth metals, china, 99.99-99.999% avg ref price, metric  | 3 | 174 | 2011-12-15 | 2026-10-29 |
| 42605 | 430 (stainless steel, europe, cr coil, metric ton) | 3 | 152 | 2014-01-01 | 2026-10-06 |
| 1228 | nickel (non ferrous metals, india, primary, kilogram) | 2 | 3359 | 2011-12-30 | 2026-11-06 |
| 184 | palladium (precious metals, united states, sponge 99.95% purity, troy  | 1 | 3309 | 2012-01-03 | 2026-11-09 |
| 468 | 409 (stainless steel, united states, 2d (0.06 in x 48 in) sheet, pound | 1 | 518 | 2020-01-01 | 2026-11-09 |
| 1189 | 430-coil (stainless surcharges, united states, nas surcharge, pound) | 1 | 159 | 2011-10-26 | 2026-10-26 |
| 33076 | steel (steel, europe, crc, metric ton) | 1 | 154 | 2014-01-01 | 2026-10-06 |
| 49797 | 304 (stainless steel, europe, round bar (<25mm), metric ton) | 1 | 154 | 2014-01-01 | 2026-10-06 |
| 80747 | goes (grain oriented electrical steel) (steel, europe, coil (<600mm),  | 1 | 116 | 2017-01-01 | 2026-10-06 |
| 82101 | aluminum (non ferrous metals, united states, aup (mw premium) future 3 | 1 | 1189 | 2019-01-01 | 2026-11-06 |
| 82102 | aluminum (non ferrous metals, united states, aup (mw premium) spot, po | 1 | 1330 | 2019-01-01 | 2026-11-05 |
| 229605 | yttrium (rare earth metals, northeast asia, , kilogram) | 1 | 69 | 2020-12-01 | 2026-11-01 |

## Tradable, proprietary (the series worth building signals on) (38)

| id | series | obs | start | recentObs | staleDays |
|---|---|---|---|---|---|
| 187 | platinum (precious metals, united states, sponge 99.95% purity, troy o | 3423 | 2012-01-03 | 710 | 0 |
| 457 | nickel (non ferrous metals, china, primary, metric ton) | 3139 | 2011-12-30 | 613 | 0 |
| 821 | zinc (non ferrous metals, china, primary cash, metric ton) | 3053 | 2011-12-30 | 611 | 0 |
| 1072 | aluminum (non ferrous metals, india, primary cash, kilogram) | 3462 | 2011-12-30 | 635 | 0 |
| 1337 | zinc (non ferrous metals, india, primary cash, kilogram) | 3476 | 2011-12-31 | 642 | 0 |
| 270581 | dysprosium oxide (rare earth metals, china, 99.5%min fob, kilogram) | 3065 | 2013-03-21 | 669 | 0 |
| 270585 | electrical steel (stainless steel, china, grain oriented 130 0.3*980mm | 3282 | 2012-06-14 | 661 | 0 |
| 270601 | ferro-chrome (ferro alloys, china, kazakhstan cr 68%min, c 8.5%max in  | 1963 | 2017-12-18 | 660 | 0 |
| 270612 | ferro-holmium (rare earth metals, china, 80% exw, kilogram) | 3166 | 2012-10-29 | 656 | 0 |
| 270704 | h-beam steel (steel, shanghai, q235 200*200mm in warehouse, metric ton | 3352 | 2012-03-08 | 663 | 0 |
| 270787 | lithium carbonate (minor metals, america, 99.5%min fob south, kilogram | 1828 | 2018-01-31 | 639 | 0 |
| 270789 | lithium hydroxide monohydrate (minor metals, china, lioh 56.5%min, mag | 2475 | 2015-10-29 | 662 | 0 |
| 270800 | lutetium oxide (rare earth metals, exw, exw, kilogram) | 1501 | 2019-11-21 | 661 | 0 |
| 270840 | manganese dioxide (minor metals, china, alkaline 91%min exw, metric to | 3148 | 2013-01-04 | 662 | 0 |
| 270860 | manganese sulfate (minor metals, china, mn 32%min exw, metric ton) | 1977 | 2017-11-22 | 663 | 0 |
| 270879 | molybdenum bar (minor metals, china, 99.9%min exw, kilogram) | 3342 | 2011-12-30 | 653 | 0 |
| 270898 | ndfeb (rare earth metals, china, sintered rough 35m exw, kilogram) | 1180 | 2021-02-22 | 640 | 0 |
| 270899 | ndfeb (rare earth metals, china, sintered rough 45m exw, kilogram) | 1175 | 2021-02-22 | 640 | 0 |
| 270900 | ndfeb (rare earth metals, china, sintered rough 50m exw, kilogram) | 1185 | 2021-02-22 | 645 | 0 |
| 270901 | ndfeb (rare earth metals, china, sintered rough 35h exw, kilogram) | 1182 | 2021-02-22 | 646 | 0 |
| 270902 | ndfeb (rare earth metals, china, sintered rough 45h exw, kilogram) | 1184 | 2021-02-22 | 645 | 0 |
| 270903 | ndfeb (rare earth metals, china, sintered rough 48h exw, kilogram) | 1184 | 2021-02-22 | 645 | 0 |
| 270904 | ndfeb (rare earth metals, china, sintered rough 50h exw, kilogram) | 1183 | 2021-02-22 | 643 | 0 |
| 270905 | neodymium metal (rare earth metals, china, 99%min exw, kilogram) | 3372 | 2011-12-30 | 655 | 0 |
| 270906 | neodymium metal (rare earth metals, china, 99%min fob, kilogram) | 3352 | 2011-12-30 | 668 | 0 |
| 270907 | neodymium oxide (rare earth metals, china, 99.5%min exw, kilogram) | 2988 | 2013-08-19 | 657 | 0 |
| 270908 | neodymium oxide (rare earth metals, china, 99.5%min fob, kilogram) | 3340 | 2011-12-30 | 667 | 0 |
| 270914 | nickel sulfate (non ferrous metals, china, ni 22%min; co 0.05%max exw, | 3325 | 2012-04-17 | 664 | 0 |
| 270922 | praseodymium metal (rare earth metals, china, 99.5%min fob, kilogram) | 3343 | 2011-12-30 | 666 | 0 |
| 270923 | praseodymium oxide (rare earth metals, china, 99.5%min exw, kilogram) | 3113 | 2013-01-11 | 658 | 0 |
| 270924 | praseodymium oxide (rare earth metals, china, 99.5%min fob, kilogram) | 3344 | 2011-12-30 | 669 | 0 |
| 270928 | prnd mischmetal (rare earth metals, china, pr 25%, nd 75% exw, kilogra | 3384 | 2011-12-30 | 662 | 0 |
| 270929 | prnd mischmetal (rare earth metals, china, pr 25%, nd 75% fob, kilogra | 3057 | 2013-03-25 | 667 | 0 |
| 270930 | prnd oxide (rare earth metals, china, pr6o11 25%, nd2o3 75% exw, kilog | 3199 | 2012-09-20 | 657 | 0 |
| 271053 | terbium metal (rare earth metals, china, 99.9%min fob, kilogram) | 1667 | 2019-01-28 | 669 | 0 |
| 271055 | terbium oxide (rare earth metals, china, 99.99%min fob, kilogram) | 1678 | 2019-01-16 | 670 | 0 |
| 271075 | titanium plate (minor metals, china, ta2 2mm exw, kilogram) | 3141 | 2012-04-16 | 614 | 0 |
| 271078 | titanium sponge (minor metals, china, 99.7%min exw, metric ton) | 3256 | 2012-07-24 | 659 | 0 |
