# MetalMiner series quality

Source dump: `historical_latest.json.gz` · as of 2026-11-16 · 169 series.

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
| 356 | aluminum (non ferrous metals, korea, commercial 1050 sheet, kilogram) | 2025-11-20 | 361 | 265 |
| 581 | aluminum (non ferrous metals, korea, 5052 coil premium over 1050, kilo | 2025-11-20 | 361 | 268 |
| 1044 | aluminum (non ferrous metals, korea, 3003 coil premium over 1050, kilo | 2025-11-20 | 361 | 270 |
| 618 | steel (steel, korea, rebar, metric ton) | 2026-01-01 | 319 | 359 |
| 1136 | steel (steel, korea, hrc, metric ton) | 2026-01-01 | 319 | 283 |

## Frozen: > 40% unchanged steps or flat run > 60 (23)

| id | series | flatShare | longestFlatRun | obs | medianGapDays |
|---|---|---|---|---|---|
| 827 | 201 (stainless steel, united states, 2b ctl (0.075 in x 48 in) sheet,  | 0.936 | 34 | 1344 | 1 |
| 468 | 409 (stainless steel, united states, 2d (0.06 in x 48 in) sheet, pound | 0.8359 | 32 | 525 | 1.0 |
| 191 | 304 (stainless steel, united states, #4 polish vinyl ctl (0.048 in x 4 | 0.7443 | 34 | 396 | 1 |
| 5 | steel (steel, united states, wire rod, cwt) | 0.7266 | 22 | 1837 | 1.0 |
| 538 | 304 (stainless steel, united states, 2b (0.075 in x 48 in) sheet, poun | 0.7164 | 34 | 336 | 1 |
| 434 | 316l (stainless steel, united states, 2b ctl (0.075 in x 48 in) sheet, | 0.6991 | 34 | 340 | 1 |
| 235 | 430 (stainless steel, united states, #4 polish vinyl ctl (0.048 in x 4 | 0.6148 | 32 | 245 | 1.0 |
| 29004 | aluminum (non ferrous metals, europe, 6082 T6 (0.08 in x 48 in) sheet, | 0.6075 | 19 | 1461 | 1.0 |
| 29003 | aluminum (non ferrous metals, europe, 5251 H32 (0.08 in x 48 in) sheet | 0.607 | 19 | 1459 | 1.0 |
| 523 | steel (steel, united states, aluminized dds astm a463 t1 40 (0.05 in x | 0.5118 | 17 | 724 | 1 |
| 1346 | aluminum (non ferrous metals, united states, 5083 h321 (1 in x 60 in)  | 0.4816 | 13 | 1878 | 1 |
| 916 | aluminum (non ferrous metals, united states, 5052 h32 (0.06 in x 60 in | 0.481 | 13 | 1874 | 1 |
| 1040 | aluminum (non ferrous metals, united states, 6061 t651 (0.5 in x 48 in | 0.4763 | 13 | 1857 | 1.0 |
| 663 | aluminum (non ferrous metals, united states, 3003 h14 (0.08 in x 48 in | 0.468 | 13 | 1830 | 1 |
| 1281 | aluminum (non ferrous metals, united states, 6061 t6 (0.08 in x 48 in) | 0.4671 | 13 | 1825 | 1.0 |
| 1477 | rare earths mmi (mmi index values, global, na, index) | 0.4604 | 34 | 1982 | 1 |
| 503 | aluminum (non ferrous metals, united states, 1100 h14 (0.08 in x 48 in | 0.4488 | 13 | 1964 | 1 |
| 72095 | lmo hydroxide-based (battery prices, global, index, index) | 0.2649 | 92 | 2413 | 1.0 |
| 72097 | nmc811 hydroxide-based (battery prices, global, index, index) | 0.2637 | 92 | 2417 | 1.0 |
| 1248 | steel (steel, china, crc, metric ton) | 0.2302 | 91 | 1856 | 1 |
| 393 | steel (steel, china, plate, metric ton) | 0.2041 | 91 | 2093 | 1.0 |
| 258 | steel (steel, china, hrc, short ton) | 0.1969 | 91 | 2170 | 1 |
| 733 | steel (steel, china, rebar, metric ton) | 0.1896 | 91 | 2248 | 1 |

## Holes: max gap > 120d in a daily/weekly series (16)

| id | series | maxGapDays | medianGapDays | obs |
|---|---|---|---|---|
| 356 | aluminum (non ferrous metals, korea, commercial 1050 sheet, kilogram) | 815 | 8.0 | 265 |
| 581 | aluminum (non ferrous metals, korea, 5052 coil premium over 1050, kilo | 815 | 8 | 268 |
| 1044 | aluminum (non ferrous metals, korea, 3003 coil premium over 1050, kilo | 815 | 8 | 270 |
| 1248 | steel (steel, china, crc, metric ton) | 401 | 1 | 1856 |
| 613 | yttria (rare earth metals, china, 99.99-99.999% avg ref price, metric  | 395 | 15 | 174 |
| 94902 | ruthenium (precious metals, united states, granules min. 99.90%, kilog | 347 | 2 | 1522 |
| 414 | steel (steel, china, hdg coil, metric ton) | 316 | 5 | 458 |
| 199342 | lanthanum-cerium mixed metal (rare earth metals, china, trem>99%;ce/tr | 316 | 7.0 | 229 |
| 982 | steel (steel, china, slab, metric ton) | 314 | 2.0 | 1537 |
| 539 | aluminum (non ferrous metals, china, aluminum billet, metric ton) | 302 | 1.0 | 1769 |
| 1477 | rare earths mmi (mmi index values, global, na, index) | 243 | 1 | 1982 |
| 1478 | raw steels mmi (mmi index values, global, na, index) | 125 | 1.0 | 1999 |
| 1479 | renewables mmi (mmi index values, global, na, index) | 124 | 1 | 1964 |
| 1472 | automotive mmi (mmi index values, global, na, index) | 122 | 1 | 1990 |
| 199344 | neodymium metal (rare earth metals, china, trem>99%;nd/rem:99~99.9%;fe | 122 | 2.0 | 1183 |
| 1471 | aluminum mmi (mmi index values, global, na, index) | 121 | 1.0 | 1957 |

## Jumps: single-step move > 50% (14)

| id | series | bigJumps | obs | start | end |
|---|---|---|---|---|---|
| 94320 | steel (steel, korea, hr plate, kilogram) | 5 | 79 | 2020-01-01 | 2026-11-06 |
| 80746 | goes (grain oriented electrical steel) (steel, europe, coil (>600mm),  | 4 | 118 | 2017-01-01 | 2026-11-06 |
| 613 | yttria (rare earth metals, china, 99.99-99.999% avg ref price, metric  | 3 | 174 | 2011-12-15 | 2026-10-29 |
| 42605 | 430 (stainless steel, europe, cr coil, metric ton) | 3 | 153 | 2014-01-01 | 2026-11-06 |
| 1228 | nickel (non ferrous metals, india, primary, kilogram) | 2 | 3362 | 2011-12-30 | 2026-11-13 |
| 184 | palladium (precious metals, united states, sponge 99.95% purity, troy  | 1 | 3314 | 2012-01-03 | 2026-11-16 |
| 468 | 409 (stainless steel, united states, 2d (0.06 in x 48 in) sheet, pound | 1 | 525 | 2020-01-01 | 2026-11-16 |
| 1189 | 430-coil (stainless surcharges, united states, nas surcharge, pound) | 1 | 159 | 2011-10-26 | 2026-10-26 |
| 33076 | steel (steel, europe, crc, metric ton) | 1 | 155 | 2014-01-01 | 2026-11-06 |
| 49797 | 304 (stainless steel, europe, round bar (<25mm), metric ton) | 1 | 155 | 2014-01-01 | 2026-11-06 |
| 80747 | goes (grain oriented electrical steel) (steel, europe, coil (<600mm),  | 1 | 117 | 2017-01-01 | 2026-11-06 |
| 82101 | aluminum (non ferrous metals, united states, aup (mw premium) future 3 | 1 | 1194 | 2019-01-01 | 2026-11-13 |
| 82102 | aluminum (non ferrous metals, united states, aup (mw premium) spot, po | 1 | 1335 | 2019-01-01 | 2026-11-13 |
| 229605 | yttrium (rare earth metals, northeast asia, , kilogram) | 1 | 69 | 2020-12-01 | 2026-11-01 |

## Tradable, proprietary (the series worth building signals on) (38)

| id | series | obs | start | recentObs | staleDays |
|---|---|---|---|---|---|
| 187 | platinum (precious metals, united states, sponge 99.95% purity, troy o | 3428 | 2012-01-03 | 710 | 0 |
| 457 | nickel (non ferrous metals, china, primary, metric ton) | 3144 | 2011-12-30 | 614 | 0 |
| 821 | zinc (non ferrous metals, china, primary cash, metric ton) | 3058 | 2011-12-30 | 612 | 0 |
| 1072 | aluminum (non ferrous metals, india, primary cash, kilogram) | 3465 | 2011-12-30 | 636 | 3 |
| 1337 | zinc (non ferrous metals, india, primary cash, kilogram) | 3479 | 2011-12-31 | 641 | 3 |
| 270581 | dysprosium oxide (rare earth metals, china, 99.5%min fob, kilogram) | 3070 | 2013-03-21 | 669 | 0 |
| 270585 | electrical steel (stainless steel, china, grain oriented 130 0.3*980mm | 3287 | 2012-06-14 | 661 | 0 |
| 270601 | ferro-chrome (ferro alloys, china, kazakhstan cr 68%min, c 8.5%max in  | 1968 | 2017-12-18 | 660 | 0 |
| 270612 | ferro-holmium (rare earth metals, china, 80% exw, kilogram) | 3171 | 2012-10-29 | 656 | 0 |
| 270704 | h-beam steel (steel, shanghai, q235 200*200mm in warehouse, metric ton | 3357 | 2012-03-08 | 663 | 0 |
| 270787 | lithium carbonate (minor metals, america, 99.5%min fob south, kilogram | 1833 | 2018-01-31 | 639 | 0 |
| 270789 | lithium hydroxide monohydrate (minor metals, china, lioh 56.5%min, mag | 2480 | 2015-10-29 | 662 | 0 |
| 270800 | lutetium oxide (rare earth metals, exw, exw, kilogram) | 1506 | 2019-11-21 | 661 | 0 |
| 270840 | manganese dioxide (minor metals, china, alkaline 91%min exw, metric to | 3153 | 2013-01-04 | 662 | 0 |
| 270860 | manganese sulfate (minor metals, china, mn 32%min exw, metric ton) | 1981 | 2017-11-22 | 662 | 0 |
| 270879 | molybdenum bar (minor metals, china, 99.9%min exw, kilogram) | 3347 | 2011-12-30 | 653 | 0 |
| 270898 | ndfeb (rare earth metals, china, sintered rough 35m exw, kilogram) | 1185 | 2021-02-22 | 640 | 0 |
| 270899 | ndfeb (rare earth metals, china, sintered rough 45m exw, kilogram) | 1180 | 2021-02-22 | 640 | 0 |
| 270900 | ndfeb (rare earth metals, china, sintered rough 50m exw, kilogram) | 1190 | 2021-02-22 | 645 | 0 |
| 270901 | ndfeb (rare earth metals, china, sintered rough 35h exw, kilogram) | 1187 | 2021-02-22 | 646 | 0 |
| 270902 | ndfeb (rare earth metals, china, sintered rough 45h exw, kilogram) | 1189 | 2021-02-22 | 645 | 0 |
| 270903 | ndfeb (rare earth metals, china, sintered rough 48h exw, kilogram) | 1189 | 2021-02-22 | 645 | 0 |
| 270904 | ndfeb (rare earth metals, china, sintered rough 50h exw, kilogram) | 1188 | 2021-02-22 | 643 | 0 |
| 270905 | neodymium metal (rare earth metals, china, 99%min exw, kilogram) | 3377 | 2011-12-30 | 655 | 0 |
| 270906 | neodymium metal (rare earth metals, china, 99%min fob, kilogram) | 3357 | 2011-12-30 | 668 | 0 |
| 270907 | neodymium oxide (rare earth metals, china, 99.5%min exw, kilogram) | 2993 | 2013-08-19 | 657 | 0 |
| 270908 | neodymium oxide (rare earth metals, china, 99.5%min fob, kilogram) | 3345 | 2011-12-30 | 667 | 0 |
| 270914 | nickel sulfate (non ferrous metals, china, ni 22%min; co 0.05%max exw, | 3330 | 2012-04-17 | 664 | 0 |
| 270922 | praseodymium metal (rare earth metals, china, 99.5%min fob, kilogram) | 3348 | 2011-12-30 | 666 | 0 |
| 270923 | praseodymium oxide (rare earth metals, china, 99.5%min exw, kilogram) | 3118 | 2013-01-11 | 658 | 0 |
| 270924 | praseodymium oxide (rare earth metals, china, 99.5%min fob, kilogram) | 3349 | 2011-12-30 | 669 | 0 |
| 270928 | prnd mischmetal (rare earth metals, china, pr 25%, nd 75% exw, kilogra | 3389 | 2011-12-30 | 662 | 0 |
| 270929 | prnd mischmetal (rare earth metals, china, pr 25%, nd 75% fob, kilogra | 3062 | 2013-03-25 | 667 | 0 |
| 270930 | prnd oxide (rare earth metals, china, pr6o11 25%, nd2o3 75% exw, kilog | 3204 | 2012-09-20 | 658 | 0 |
| 271053 | terbium metal (rare earth metals, china, 99.9%min fob, kilogram) | 1672 | 2019-01-28 | 669 | 0 |
| 271055 | terbium oxide (rare earth metals, china, 99.99%min fob, kilogram) | 1683 | 2019-01-16 | 670 | 0 |
| 271075 | titanium plate (minor metals, china, ta2 2mm exw, kilogram) | 3146 | 2012-04-16 | 614 | 0 |
| 271078 | titanium sponge (minor metals, china, 99.7%min exw, metric ton) | 3261 | 2012-07-24 | 659 | 0 |
