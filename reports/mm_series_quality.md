# MetalMiner series quality

Source dump: `historical_latest.json.gz` · as of 2026-09-10 · 169 series.

Grades: **tradable** = daily, fresh, not frozen, no suspicious jumps; **level_only** = usable for direction/level, not for return signals (weekly/monthly cadence, partly frozen, or thin recent history); **rejected** = composite index, stopped, frozen list price, or unit flip. `public` = exchange-quoted (LME/COMEX), so no information edge.

Counts: {"rejected": 44, "level_only": 67, "tradable": 58, "tradable_public": 21, "tradable_proprietary": 37}

| category | series | tradable (proprietary / public) | level_only | rejected |
|---|---|---|---|---|
| battery prices | 7 | 0 (0 / 0) | 7 | 0 |
| ferro alloys | 2 | 1 (1 / 0) | 1 | 0 |
| minor metals | 8 | 6 (6 / 0) | 2 | 0 |
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
| 356 | aluminum (non ferrous metals, korea, commercial 1050 sheet, kilogram) | 2025-11-20 | 294 | 265 |
| 581 | aluminum (non ferrous metals, korea, 5052 coil premium over 1050, kilo | 2025-11-20 | 294 | 268 |
| 1044 | aluminum (non ferrous metals, korea, 3003 coil premium over 1050, kilo | 2025-11-20 | 294 | 270 |
| 618 | steel (steel, korea, rebar, metric ton) | 2026-01-01 | 252 | 359 |
| 1136 | steel (steel, korea, hrc, metric ton) | 2026-01-01 | 252 | 283 |
| 290 | aluminum (non ferrous metals, europe, 6082 plate, metric ton) | 2026-08-03 | 38 | 173 |
| 408 | aluminum (non ferrous metals, europe, 5083 plate, metric ton) | 2026-08-03 | 38 | 177 |
| 429 | aluminum (non ferrous metals, europe, 6082 bar, metric ton) | 2026-08-03 | 38 | 171 |
| 552 | aluminum (non ferrous metals, europe, commercial 1050 sheet, metric to | 2026-08-03 | 38 | 180 |

## Frozen: > 40% unchanged steps or flat run > 60 (23)

| id | series | flatShare | longestFlatRun | obs | medianGapDays |
|---|---|---|---|---|---|
| 827 | 201 (stainless steel, united states, 2b ctl (0.075 in x 48 in) sheet,  | 0.9359 | 34 | 1295 | 1.0 |
| 468 | 409 (stainless steel, united states, 2d (0.06 in x 48 in) sheet, pound | 0.8184 | 32 | 458 | 1 |
| 191 | 304 (stainless steel, united states, #4 polish vinyl ctl (0.048 in x 4 | 0.7239 | 34 | 356 | 1 |
| 538 | 304 (stainless steel, united states, 2b (0.075 in x 48 in) sheet, poun | 0.7229 | 34 | 333 | 1.0 |
| 5 | steel (steel, united states, wire rod, cwt) | 0.7207 | 22 | 1770 | 1 |
| 434 | 316l (stainless steel, united states, 2b ctl (0.075 in x 48 in) sheet, | 0.6689 | 34 | 300 | 1 |
| 235 | 430 (stainless steel, united states, #4 polish vinyl ctl (0.048 in x 4 | 0.6208 | 32 | 241 | 1.0 |
| 29004 | aluminum (non ferrous metals, europe, 6082 T6 (0.08 in x 48 in) sheet, | 0.6037 | 19 | 1394 | 1 |
| 29003 | aluminum (non ferrous metals, europe, 5251 H32 (0.08 in x 48 in) sheet | 0.6032 | 19 | 1392 | 1 |
| 523 | steel (steel, united states, aluminized dds astm a463 t1 40 (0.05 in x | 0.5107 | 17 | 702 | 1 |
| 1346 | aluminum (non ferrous metals, united states, 5083 h321 (1 in x 60 in)  | 0.4845 | 13 | 1811 | 1.0 |
| 916 | aluminum (non ferrous metals, united states, 5052 h32 (0.06 in x 60 in | 0.4839 | 13 | 1807 | 1.0 |
| 1040 | aluminum (non ferrous metals, united states, 6061 t651 (0.5 in x 48 in | 0.479 | 13 | 1790 | 1 |
| 663 | aluminum (non ferrous metals, united states, 3003 h14 (0.08 in x 48 in | 0.4705 | 13 | 1763 | 1.0 |
| 1281 | aluminum (non ferrous metals, united states, 6061 t6 (0.08 in x 48 in) | 0.4696 | 13 | 1758 | 1 |
| 1477 | rare earths mmi (mmi index values, global, na, index) | 0.4566 | 34 | 1915 | 1.0 |
| 503 | aluminum (non ferrous metals, united states, 1100 h14 (0.08 in x 48 in | 0.4504 | 13 | 1897 | 1.0 |
| 72095 | lmo hydroxide-based (battery prices, global, index, index) | 0.2559 | 92 | 2346 | 1 |
| 72097 | nmc811 hydroxide-based (battery prices, global, index, index) | 0.255 | 92 | 2350 | 1 |
| 1248 | steel (steel, china, crc, metric ton) | 0.2187 | 91 | 1789 | 1.0 |
| 393 | steel (steel, china, plate, metric ton) | 0.1931 | 91 | 2026 | 1 |
| 258 | steel (steel, china, hrc, short ton) | 0.186 | 91 | 2103 | 1.0 |
| 733 | steel (steel, china, rebar, metric ton) | 0.1789 | 91 | 2181 | 1.0 |

## Holes: max gap > 120d in a daily/weekly series (16)

| id | series | maxGapDays | medianGapDays | obs |
|---|---|---|---|---|
| 356 | aluminum (non ferrous metals, korea, commercial 1050 sheet, kilogram) | 815 | 8.0 | 265 |
| 581 | aluminum (non ferrous metals, korea, 5052 coil premium over 1050, kilo | 815 | 8 | 268 |
| 1044 | aluminum (non ferrous metals, korea, 3003 coil premium over 1050, kilo | 815 | 8 | 270 |
| 1248 | steel (steel, china, crc, metric ton) | 401 | 1.0 | 1789 |
| 613 | yttria (rare earth metals, china, 99.99-99.999% avg ref price, metric  | 395 | 15 | 172 |
| 94902 | ruthenium (precious metals, united states, granules min. 99.90%, kilog | 347 | 2.0 | 1491 |
| 414 | steel (steel, china, hdg coil, metric ton) | 316 | 5.0 | 443 |
| 199342 | lanthanum-cerium mixed metal (rare earth metals, china, trem>99%;ce/tr | 316 | 7.0 | 227 |
| 982 | steel (steel, china, slab, metric ton) | 314 | 2.0 | 1519 |
| 539 | aluminum (non ferrous metals, china, aluminum billet, metric ton) | 302 | 1 | 1730 |
| 1477 | rare earths mmi (mmi index values, global, na, index) | 243 | 1.0 | 1915 |
| 1478 | raw steels mmi (mmi index values, global, na, index) | 125 | 1 | 1932 |
| 1479 | renewables mmi (mmi index values, global, na, index) | 124 | 1.0 | 1897 |
| 1472 | automotive mmi (mmi index values, global, na, index) | 122 | 1.0 | 1923 |
| 199344 | neodymium metal (rare earth metals, china, trem>99%;nd/rem:99~99.9%;fe | 122 | 2 | 1176 |
| 1471 | aluminum mmi (mmi index values, global, na, index) | 121 | 1 | 1890 |

## Jumps: single-step move > 50% (14)

| id | series | bigJumps | obs | start | end |
|---|---|---|---|---|---|
| 94320 | steel (steel, korea, hr plate, kilogram) | 5 | 77 | 2020-01-01 | 2026-09-07 |
| 80746 | goes (grain oriented electrical steel) (steel, europe, coil (>600mm),  | 4 | 116 | 2017-01-01 | 2026-09-07 |
| 613 | yttria (rare earth metals, china, 99.99-99.999% avg ref price, metric  | 3 | 172 | 2011-12-15 | 2026-08-14 |
| 42605 | 430 (stainless steel, europe, cr coil, metric ton) | 3 | 151 | 2014-01-01 | 2026-09-07 |
| 1228 | nickel (non ferrous metals, india, primary, kilogram) | 2 | 3322 | 2011-12-30 | 2026-09-09 |
| 184 | palladium (precious metals, united states, sponge 99.95% purity, troy  | 1 | 3271 | 2012-01-03 | 2026-09-10 |
| 468 | 409 (stainless steel, united states, 2d (0.06 in x 48 in) sheet, pound | 1 | 458 | 2020-01-01 | 2026-09-10 |
| 1189 | 430-coil (stainless surcharges, united states, nas surcharge, pound) | 1 | 157 | 2011-10-26 | 2026-08-27 |
| 33076 | steel (steel, europe, crc, metric ton) | 1 | 153 | 2014-01-01 | 2026-09-07 |
| 49797 | 304 (stainless steel, europe, round bar (<25mm), metric ton) | 1 | 153 | 2014-01-01 | 2026-09-07 |
| 80747 | goes (grain oriented electrical steel) (steel, europe, coil (<600mm),  | 1 | 115 | 2017-01-01 | 2026-09-07 |
| 82101 | aluminum (non ferrous metals, united states, aup (mw premium) future 3 | 1 | 1156 | 2019-01-01 | 2026-09-09 |
| 82102 | aluminum (non ferrous metals, united states, aup (mw premium) spot, po | 1 | 1298 | 2019-01-01 | 2026-09-09 |
| 229605 | yttrium (rare earth metals, northeast asia, , kilogram) | 1 | 67 | 2020-12-01 | 2026-09-01 |

## Tradable, proprietary (the series worth building signals on) (37)

| id | series | obs | start | recentObs | staleDays |
|---|---|---|---|---|---|
| 187 | platinum (precious metals, united states, sponge 99.95% purity, troy o | 3385 | 2012-01-03 | 712 | 0 |
| 457 | nickel (non ferrous metals, china, primary, metric ton) | 3106 | 2011-12-30 | 616 | 0 |
| 821 | zinc (non ferrous metals, china, primary cash, metric ton) | 3020 | 2011-12-30 | 614 | 0 |
| 1072 | aluminum (non ferrous metals, india, primary cash, kilogram) | 3424 | 2011-12-30 | 637 | 1 |
| 1337 | zinc (non ferrous metals, india, primary cash, kilogram) | 3439 | 2011-12-31 | 645 | 1 |
| 270581 | dysprosium oxide (rare earth metals, china, 99.5%min fob, kilogram) | 3012 | 2013-03-21 | 644 | 6 |
| 270585 | electrical steel (stainless steel, china, grain oriented 130 0.3*980mm | 3229 | 2012-06-14 | 637 | 6 |
| 270601 | ferro-chrome (ferro alloys, china, kazakhstan cr 68%min, c 8.5%max in  | 1910 | 2017-12-18 | 636 | 6 |
| 270612 | ferro-holmium (rare earth metals, china, 80% exw, kilogram) | 3113 | 2012-10-29 | 631 | 6 |
| 270704 | h-beam steel (steel, shanghai, q235 200*200mm in warehouse, metric ton | 3299 | 2012-03-08 | 639 | 6 |
| 270787 | lithium carbonate (minor metals, america, 99.5%min fob south, kilogram | 1774 | 2018-01-31 | 614 | 6 |
| 270789 | lithium hydroxide monohydrate (minor metals, china, lioh 56.5%min, mag | 2422 | 2015-10-29 | 638 | 6 |
| 270800 | lutetium oxide (rare earth metals, exw, exw, kilogram) | 1448 | 2019-11-21 | 636 | 6 |
| 270840 | manganese dioxide (minor metals, china, alkaline 91%min exw, metric to | 3095 | 2013-01-04 | 638 | 6 |
| 270860 | manganese sulfate (minor metals, china, mn 32%min exw, metric ton) | 1924 | 2017-11-22 | 639 | 6 |
| 270879 | molybdenum bar (minor metals, china, 99.9%min exw, kilogram) | 3289 | 2011-12-30 | 628 | 6 |
| 270898 | ndfeb (rare earth metals, china, sintered rough 35m exw, kilogram) | 1127 | 2021-02-22 | 613 | 6 |
| 270899 | ndfeb (rare earth metals, china, sintered rough 45m exw, kilogram) | 1122 | 2021-02-22 | 613 | 6 |
| 270900 | ndfeb (rare earth metals, china, sintered rough 50m exw, kilogram) | 1132 | 2021-02-22 | 618 | 6 |
| 270901 | ndfeb (rare earth metals, china, sintered rough 35h exw, kilogram) | 1129 | 2021-02-22 | 619 | 6 |
| 270902 | ndfeb (rare earth metals, china, sintered rough 45h exw, kilogram) | 1131 | 2021-02-22 | 617 | 6 |
| 270903 | ndfeb (rare earth metals, china, sintered rough 48h exw, kilogram) | 1131 | 2021-02-22 | 618 | 6 |
| 270904 | ndfeb (rare earth metals, china, sintered rough 50h exw, kilogram) | 1130 | 2021-02-22 | 617 | 6 |
| 270905 | neodymium metal (rare earth metals, china, 99%min exw, kilogram) | 3319 | 2011-12-30 | 629 | 6 |
| 270906 | neodymium metal (rare earth metals, china, 99%min fob, kilogram) | 3299 | 2011-12-30 | 643 | 6 |
| 270907 | neodymium oxide (rare earth metals, china, 99.5%min exw, kilogram) | 2935 | 2013-08-19 | 631 | 6 |
| 270908 | neodymium oxide (rare earth metals, china, 99.5%min fob, kilogram) | 3287 | 2011-12-30 | 642 | 6 |
| 270914 | nickel sulfate (non ferrous metals, china, ni 22%min; co 0.05%max exw, | 3272 | 2012-04-17 | 640 | 6 |
| 270922 | praseodymium metal (rare earth metals, china, 99.5%min fob, kilogram) | 3290 | 2011-12-30 | 641 | 6 |
| 270923 | praseodymium oxide (rare earth metals, china, 99.5%min exw, kilogram) | 3060 | 2013-01-11 | 632 | 6 |
| 270924 | praseodymium oxide (rare earth metals, china, 99.5%min fob, kilogram) | 3291 | 2011-12-30 | 644 | 6 |
| 270928 | prnd mischmetal (rare earth metals, china, pr 25%, nd 75% exw, kilogra | 3331 | 2011-12-30 | 636 | 6 |
| 270929 | prnd mischmetal (rare earth metals, china, pr 25%, nd 75% fob, kilogra | 3004 | 2013-03-25 | 642 | 6 |
| 270930 | prnd oxide (rare earth metals, china, pr6o11 25%, nd2o3 75% exw, kilog | 3146 | 2012-09-20 | 632 | 6 |
| 271053 | terbium metal (rare earth metals, china, 99.9%min fob, kilogram) | 1614 | 2019-01-28 | 644 | 6 |
| 271055 | terbium oxide (rare earth metals, china, 99.99%min fob, kilogram) | 1625 | 2019-01-16 | 645 | 6 |
| 271078 | titanium sponge (minor metals, china, 99.7%min exw, metric ton) | 3203 | 2012-07-24 | 635 | 6 |
