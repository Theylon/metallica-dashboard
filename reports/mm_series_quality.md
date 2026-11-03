# MetalMiner series quality

Source dump: `historical_latest.json.gz` · as of 2026-11-03 · 169 series.

Grades: **tradable** = daily, fresh, not frozen, no suspicious jumps; **level_only** = usable for direction/level, not for return signals (weekly/monthly cadence, partly frozen, or thin recent history); **rejected** = composite index, stopped, frozen list price, or unit flip. `public` = exchange-quoted (LME/COMEX), so no information edge.

Counts: {"rejected": 40, "level_only": 70, "tradable": 59, "tradable_public": 21, "tradable_proprietary": 38}

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
| stainless steel | 12 | 1 (1 / 0) | 3 | 8 |
| stainless surcharges | 2 | 0 (0 / 0) | 1 | 1 |
| steel | 30 | 2 (1 / 1) | 20 | 8 |

## Stale: last observation > 30d before as-of (5)

| id | series | end | staleDays | obs |
|---|---|---|---|---|
| 356 | aluminum (non ferrous metals, korea, commercial 1050 sheet, kilogram) | 2025-11-20 | 348 | 265 |
| 581 | aluminum (non ferrous metals, korea, 5052 coil premium over 1050, kilo | 2025-11-20 | 348 | 268 |
| 1044 | aluminum (non ferrous metals, korea, 3003 coil premium over 1050, kilo | 2025-11-20 | 348 | 270 |
| 618 | steel (steel, korea, rebar, metric ton) | 2026-01-01 | 306 | 359 |
| 1136 | steel (steel, korea, hrc, metric ton) | 2026-01-01 | 306 | 283 |

## Frozen: > 40% unchanged steps or flat run > 60 (23)

| id | series | flatShare | longestFlatRun | obs | medianGapDays |
|---|---|---|---|---|---|
| 827 | 201 (stainless steel, united states, 2b ctl (0.075 in x 48 in) sheet,  | 0.936 | 34 | 1344 | 1 |
| 468 | 409 (stainless steel, united states, 2d (0.06 in x 48 in) sheet, pound | 0.8317 | 32 | 512 | 1 |
| 191 | 304 (stainless steel, united states, #4 polish vinyl ctl (0.048 in x 4 | 0.7356 | 34 | 383 | 1.0 |
| 5 | steel (steel, united states, wire rod, cwt) | 0.7252 | 22 | 1824 | 1 |
| 538 | 304 (stainless steel, united states, 2b (0.075 in x 48 in) sheet, poun | 0.7164 | 34 | 336 | 1 |
| 434 | 316l (stainless steel, united states, 2b ctl (0.075 in x 48 in) sheet, | 0.6871 | 34 | 327 | 1.0 |
| 235 | 430 (stainless steel, united states, #4 polish vinyl ctl (0.048 in x 4 | 0.6148 | 32 | 245 | 1.0 |
| 29004 | aluminum (non ferrous metals, europe, 6082 T6 (0.08 in x 48 in) sheet, | 0.6102 | 19 | 1448 | 1 |
| 29003 | aluminum (non ferrous metals, europe, 5251 H32 (0.08 in x 48 in) sheet | 0.6097 | 19 | 1446 | 1 |
| 523 | steel (steel, united states, aluminized dds astm a463 t1 40 (0.05 in x | 0.5084 | 17 | 715 | 1.0 |
| 1346 | aluminum (non ferrous metals, united states, 5083 h321 (1 in x 60 in)  | 0.4834 | 13 | 1865 | 1.0 |
| 916 | aluminum (non ferrous metals, united states, 5052 h32 (0.06 in x 60 in | 0.4828 | 13 | 1861 | 1.0 |
| 1040 | aluminum (non ferrous metals, united states, 6061 t651 (0.5 in x 48 in | 0.478 | 13 | 1844 | 1 |
| 663 | aluminum (non ferrous metals, united states, 3003 h14 (0.08 in x 48 in | 0.4697 | 13 | 1817 | 1.0 |
| 1281 | aluminum (non ferrous metals, united states, 6061 t6 (0.08 in x 48 in) | 0.4688 | 13 | 1812 | 1 |
| 1477 | rare earths mmi (mmi index values, global, na, index) | 0.4624 | 34 | 1969 | 1.0 |
| 503 | aluminum (non ferrous metals, united states, 1100 h14 (0.08 in x 48 in | 0.4503 | 13 | 1951 | 1.0 |
| 72095 | lmo hydroxide-based (battery prices, global, index, index) | 0.2655 | 92 | 2400 | 1 |
| 72097 | nmc811 hydroxide-based (battery prices, global, index, index) | 0.2643 | 92 | 2404 | 1 |
| 1248 | steel (steel, china, crc, metric ton) | 0.2307 | 91 | 1843 | 1.0 |
| 393 | steel (steel, china, plate, metric ton) | 0.2044 | 91 | 2080 | 1 |
| 258 | steel (steel, china, hrc, short ton) | 0.1971 | 91 | 2157 | 1.0 |
| 733 | steel (steel, china, rebar, metric ton) | 0.1898 | 91 | 2235 | 1.0 |

## Holes: max gap > 120d in a daily/weekly series (16)

| id | series | maxGapDays | medianGapDays | obs |
|---|---|---|---|---|
| 356 | aluminum (non ferrous metals, korea, commercial 1050 sheet, kilogram) | 815 | 8.0 | 265 |
| 581 | aluminum (non ferrous metals, korea, 5052 coil premium over 1050, kilo | 815 | 8 | 268 |
| 1044 | aluminum (non ferrous metals, korea, 3003 coil premium over 1050, kilo | 815 | 8 | 270 |
| 1248 | steel (steel, china, crc, metric ton) | 401 | 1.0 | 1843 |
| 613 | yttria (rare earth metals, china, 99.99-99.999% avg ref price, metric  | 395 | 15 | 174 |
| 94902 | ruthenium (precious metals, united states, granules min. 99.90%, kilog | 347 | 2.0 | 1515 |
| 414 | steel (steel, china, hdg coil, metric ton) | 316 | 5 | 454 |
| 199342 | lanthanum-cerium mixed metal (rare earth metals, china, trem>99%;ce/tr | 316 | 7.0 | 229 |
| 982 | steel (steel, china, slab, metric ton) | 314 | 2.0 | 1533 |
| 539 | aluminum (non ferrous metals, china, aluminum billet, metric ton) | 302 | 1 | 1760 |
| 1477 | rare earths mmi (mmi index values, global, na, index) | 243 | 1.0 | 1969 |
| 1478 | raw steels mmi (mmi index values, global, na, index) | 125 | 1 | 1986 |
| 1479 | renewables mmi (mmi index values, global, na, index) | 124 | 1.0 | 1951 |
| 1472 | automotive mmi (mmi index values, global, na, index) | 122 | 1.0 | 1977 |
| 199344 | neodymium metal (rare earth metals, china, trem>99%;nd/rem:99~99.9%;fe | 122 | 2 | 1182 |
| 1471 | aluminum mmi (mmi index values, global, na, index) | 121 | 1 | 1944 |

## Jumps: single-step move > 50% (14)

| id | series | bigJumps | obs | start | end |
|---|---|---|---|---|---|
| 94320 | steel (steel, korea, hr plate, kilogram) | 5 | 78 | 2020-01-01 | 2026-10-06 |
| 80746 | goes (grain oriented electrical steel) (steel, europe, coil (>600mm),  | 4 | 117 | 2017-01-01 | 2026-10-06 |
| 613 | yttria (rare earth metals, china, 99.99-99.999% avg ref price, metric  | 3 | 174 | 2011-12-15 | 2026-10-29 |
| 42605 | 430 (stainless steel, europe, cr coil, metric ton) | 3 | 152 | 2014-01-01 | 2026-10-06 |
| 1228 | nickel (non ferrous metals, india, primary, kilogram) | 2 | 3356 | 2011-12-30 | 2026-11-03 |
| 184 | palladium (precious metals, united states, sponge 99.95% purity, troy  | 1 | 3305 | 2012-01-03 | 2026-11-03 |
| 468 | 409 (stainless steel, united states, 2d (0.06 in x 48 in) sheet, pound | 1 | 512 | 2020-01-01 | 2026-11-03 |
| 1189 | 430-coil (stainless surcharges, united states, nas surcharge, pound) | 1 | 159 | 2011-10-26 | 2026-10-26 |
| 33076 | steel (steel, europe, crc, metric ton) | 1 | 154 | 2014-01-01 | 2026-10-06 |
| 49797 | 304 (stainless steel, europe, round bar (<25mm), metric ton) | 1 | 154 | 2014-01-01 | 2026-10-06 |
| 80747 | goes (grain oriented electrical steel) (steel, europe, coil (<600mm),  | 1 | 116 | 2017-01-01 | 2026-10-06 |
| 82101 | aluminum (non ferrous metals, united states, aup (mw premium) future 3 | 1 | 1184 | 2019-01-01 | 2026-10-29 |
| 82102 | aluminum (non ferrous metals, united states, aup (mw premium) spot, po | 1 | 1326 | 2019-01-01 | 2026-10-30 |
| 229605 | yttrium (rare earth metals, northeast asia, , kilogram) | 1 | 69 | 2020-12-01 | 2026-11-01 |

## Tradable, proprietary (the series worth building signals on) (38)

| id | series | obs | start | recentObs | staleDays |
|---|---|---|---|---|---|
| 187 | platinum (precious metals, united states, sponge 99.95% purity, troy o | 3419 | 2012-01-03 | 710 | 0 |
| 457 | nickel (non ferrous metals, china, primary, metric ton) | 3135 | 2011-12-30 | 613 | 0 |
| 821 | zinc (non ferrous metals, china, primary cash, metric ton) | 3049 | 2011-12-30 | 611 | 0 |
| 1072 | aluminum (non ferrous metals, india, primary cash, kilogram) | 3458 | 2011-12-30 | 635 | 0 |
| 1337 | zinc (non ferrous metals, india, primary cash, kilogram) | 3472 | 2011-12-31 | 642 | 0 |
| 270581 | dysprosium oxide (rare earth metals, china, 99.5%min fob, kilogram) | 3061 | 2013-03-21 | 668 | 0 |
| 270585 | electrical steel (stainless steel, china, grain oriented 130 0.3*980mm | 3278 | 2012-06-14 | 660 | 0 |
| 270601 | ferro-chrome (ferro alloys, china, kazakhstan cr 68%min, c 8.5%max in  | 1959 | 2017-12-18 | 659 | 0 |
| 270612 | ferro-holmium (rare earth metals, china, 80% exw, kilogram) | 3162 | 2012-10-29 | 655 | 0 |
| 270704 | h-beam steel (steel, shanghai, q235 200*200mm in warehouse, metric ton | 3348 | 2012-03-08 | 662 | 0 |
| 270787 | lithium carbonate (minor metals, america, 99.5%min fob south, kilogram | 1824 | 2018-01-31 | 638 | 0 |
| 270789 | lithium hydroxide monohydrate (minor metals, china, lioh 56.5%min, mag | 2471 | 2015-10-29 | 661 | 0 |
| 270800 | lutetium oxide (rare earth metals, exw, exw, kilogram) | 1497 | 2019-11-21 | 660 | 0 |
| 270840 | manganese dioxide (minor metals, china, alkaline 91%min exw, metric to | 3144 | 2013-01-04 | 661 | 0 |
| 270860 | manganese sulfate (minor metals, china, mn 32%min exw, metric ton) | 1973 | 2017-11-22 | 662 | 0 |
| 270879 | molybdenum bar (minor metals, china, 99.9%min exw, kilogram) | 3338 | 2011-12-30 | 652 | 0 |
| 270898 | ndfeb (rare earth metals, china, sintered rough 35m exw, kilogram) | 1176 | 2021-02-22 | 639 | 0 |
| 270899 | ndfeb (rare earth metals, china, sintered rough 45m exw, kilogram) | 1171 | 2021-02-22 | 639 | 0 |
| 270900 | ndfeb (rare earth metals, china, sintered rough 50m exw, kilogram) | 1181 | 2021-02-22 | 644 | 0 |
| 270901 | ndfeb (rare earth metals, china, sintered rough 35h exw, kilogram) | 1178 | 2021-02-22 | 645 | 0 |
| 270902 | ndfeb (rare earth metals, china, sintered rough 45h exw, kilogram) | 1180 | 2021-02-22 | 644 | 0 |
| 270903 | ndfeb (rare earth metals, china, sintered rough 48h exw, kilogram) | 1180 | 2021-02-22 | 644 | 0 |
| 270904 | ndfeb (rare earth metals, china, sintered rough 50h exw, kilogram) | 1179 | 2021-02-22 | 642 | 0 |
| 270905 | neodymium metal (rare earth metals, china, 99%min exw, kilogram) | 3368 | 2011-12-30 | 654 | 0 |
| 270906 | neodymium metal (rare earth metals, china, 99%min fob, kilogram) | 3348 | 2011-12-30 | 667 | 0 |
| 270907 | neodymium oxide (rare earth metals, china, 99.5%min exw, kilogram) | 2984 | 2013-08-19 | 656 | 0 |
| 270908 | neodymium oxide (rare earth metals, china, 99.5%min fob, kilogram) | 3336 | 2011-12-30 | 666 | 0 |
| 270914 | nickel sulfate (non ferrous metals, china, ni 22%min; co 0.05%max exw, | 3321 | 2012-04-17 | 663 | 0 |
| 270922 | praseodymium metal (rare earth metals, china, 99.5%min fob, kilogram) | 3339 | 2011-12-30 | 665 | 0 |
| 270923 | praseodymium oxide (rare earth metals, china, 99.5%min exw, kilogram) | 3109 | 2013-01-11 | 657 | 0 |
| 270924 | praseodymium oxide (rare earth metals, china, 99.5%min fob, kilogram) | 3340 | 2011-12-30 | 668 | 0 |
| 270928 | prnd mischmetal (rare earth metals, china, pr 25%, nd 75% exw, kilogra | 3380 | 2011-12-30 | 661 | 0 |
| 270929 | prnd mischmetal (rare earth metals, china, pr 25%, nd 75% fob, kilogra | 3053 | 2013-03-25 | 666 | 0 |
| 270930 | prnd oxide (rare earth metals, china, pr6o11 25%, nd2o3 75% exw, kilog | 3195 | 2012-09-20 | 656 | 0 |
| 271053 | terbium metal (rare earth metals, china, 99.9%min fob, kilogram) | 1663 | 2019-01-28 | 668 | 0 |
| 271055 | terbium oxide (rare earth metals, china, 99.99%min fob, kilogram) | 1674 | 2019-01-16 | 669 | 0 |
| 271075 | titanium plate (minor metals, china, ta2 2mm exw, kilogram) | 3137 | 2012-04-16 | 613 | 0 |
| 271078 | titanium sponge (minor metals, china, 99.7%min exw, metric ton) | 3252 | 2012-07-24 | 658 | 0 |
