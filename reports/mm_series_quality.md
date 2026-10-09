# MetalMiner series quality

Source dump: `historical_latest.json.gz` · as of 2026-10-09 · 169 series.

Grades: **tradable** = daily, fresh, not frozen, no suspicious jumps; **level_only** = usable for direction/level, not for return signals (weekly/monthly cadence, partly frozen, or thin recent history); **rejected** = composite index, stopped, frozen list price, or unit flip. `public` = exchange-quoted (LME/COMEX), so no information edge.

Counts: {"rejected": 49, "level_only": 62, "tradable": 58, "tradable_public": 21, "tradable_proprietary": 37}

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
| stainless steel | 12 | 1 (1 / 0) | 0 | 11 |
| stainless surcharges | 2 | 0 (0 / 0) | 1 | 1 |
| steel | 30 | 2 (1 / 1) | 20 | 8 |

## Stale: last observation > 30d before as-of (17)

| id | series | end | staleDays | obs |
|---|---|---|---|---|
| 356 | aluminum (non ferrous metals, korea, commercial 1050 sheet, kilogram) | 2025-11-20 | 323 | 265 |
| 581 | aluminum (non ferrous metals, korea, 5052 coil premium over 1050, kilo | 2025-11-20 | 323 | 268 |
| 1044 | aluminum (non ferrous metals, korea, 3003 coil premium over 1050, kilo | 2025-11-20 | 323 | 270 |
| 618 | steel (steel, korea, rebar, metric ton) | 2026-01-01 | 281 | 359 |
| 1136 | steel (steel, korea, hrc, metric ton) | 2026-01-01 | 281 | 283 |
| 290 | aluminum (non ferrous metals, europe, 6082 plate, metric ton) | 2026-08-03 | 67 | 173 |
| 408 | aluminum (non ferrous metals, europe, 5083 plate, metric ton) | 2026-08-03 | 67 | 177 |
| 429 | aluminum (non ferrous metals, europe, 6082 bar, metric ton) | 2026-08-03 | 67 | 171 |
| 552 | aluminum (non ferrous metals, europe, commercial 1050 sheet, metric to | 2026-08-03 | 67 | 180 |
| 613 | yttria (rare earth metals, china, 99.99-99.999% avg ref price, metric  | 2026-08-14 | 56 | 172 |
| 213 | steel (scrap, united states, north central / east #1 heavy melting ste | 2026-08-24 | 46 | 173 |
| 260 | steel (scrap, united states, south #1 heavy melting steel, gross ton) | 2026-08-24 | 46 | 177 |
| 42604 | 304 (stainless steel, europe, cr coil, metric ton) | 2026-09-07 | 32 | 152 |
| 42605 | 430 (stainless steel, europe, cr coil, metric ton) | 2026-09-07 | 32 | 151 |
| 49796 | 304 (stainless steel, europe, round bar (25-80 mm), metric ton) | 2026-09-07 | 32 | 153 |
| 49797 | 304 (stainless steel, europe, round bar (<25mm), metric ton) | 2026-09-07 | 32 | 153 |
| 49798 | 304 (stainless steel, europe, square bar, metric ton) | 2026-09-07 | 32 | 152 |

## Frozen: > 40% unchanged steps or flat run > 60 (23)

| id | series | flatShare | longestFlatRun | obs | medianGapDays |
|---|---|---|---|---|---|
| 827 | 201 (stainless steel, united states, 2b ctl (0.075 in x 48 in) sheet,  | 0.9365 | 34 | 1324 | 1 |
| 468 | 409 (stainless steel, united states, 2d (0.06 in x 48 in) sheet, pound | 0.8272 | 32 | 487 | 1.0 |
| 191 | 304 (stainless steel, united states, #4 polish vinyl ctl (0.048 in x 4 | 0.7353 | 34 | 375 | 1.0 |
| 5 | steel (steel, united states, wire rod, cwt) | 0.7236 | 22 | 1799 | 1.0 |
| 538 | 304 (stainless steel, united states, 2b (0.075 in x 48 in) sheet, poun | 0.7207 | 34 | 334 | 1 |
| 434 | 316l (stainless steel, united states, 2b ctl (0.075 in x 48 in) sheet, | 0.6855 | 34 | 319 | 1.0 |
| 235 | 430 (stainless steel, united states, #4 polish vinyl ctl (0.048 in x 4 | 0.6183 | 32 | 242 | 1 |
| 29004 | aluminum (non ferrous metals, europe, 6082 T6 (0.08 in x 48 in) sheet, | 0.6069 | 19 | 1423 | 1.0 |
| 29003 | aluminum (non ferrous metals, europe, 5251 H32 (0.08 in x 48 in) sheet | 0.6063 | 19 | 1421 | 1.0 |
| 523 | steel (steel, united states, aluminized dds astm a463 t1 40 (0.05 in x | 0.5078 | 17 | 706 | 1 |
| 1346 | aluminum (non ferrous metals, united states, 5083 h321 (1 in x 60 in)  | 0.4829 | 13 | 1840 | 1 |
| 916 | aluminum (non ferrous metals, united states, 5052 h32 (0.06 in x 60 in | 0.4823 | 13 | 1836 | 1 |
| 1040 | aluminum (non ferrous metals, united states, 6061 t651 (0.5 in x 48 in | 0.4774 | 13 | 1819 | 1.0 |
| 663 | aluminum (non ferrous metals, united states, 3003 h14 (0.08 in x 48 in | 0.469 | 13 | 1792 | 1 |
| 1281 | aluminum (non ferrous metals, united states, 6061 t6 (0.08 in x 48 in) | 0.4681 | 13 | 1787 | 1.0 |
| 1477 | rare earths mmi (mmi index values, global, na, index) | 0.4632 | 34 | 1944 | 1 |
| 503 | aluminum (non ferrous metals, united states, 1100 h14 (0.08 in x 48 in | 0.4494 | 13 | 1926 | 1 |
| 72095 | lmo hydroxide-based (battery prices, global, index, index) | 0.2637 | 92 | 2375 | 1.0 |
| 72097 | nmc811 hydroxide-based (battery prices, global, index, index) | 0.2628 | 92 | 2379 | 1.0 |
| 1248 | steel (steel, china, crc, metric ton) | 0.2295 | 91 | 1818 | 1 |
| 393 | steel (steel, china, plate, metric ton) | 0.203 | 91 | 2055 | 1.0 |
| 258 | steel (steel, china, hrc, short ton) | 0.1957 | 91 | 2132 | 1 |
| 733 | steel (steel, china, rebar, metric ton) | 0.1883 | 91 | 2210 | 1 |

## Holes: max gap > 120d in a daily/weekly series (16)

| id | series | maxGapDays | medianGapDays | obs |
|---|---|---|---|---|
| 356 | aluminum (non ferrous metals, korea, commercial 1050 sheet, kilogram) | 815 | 8.0 | 265 |
| 581 | aluminum (non ferrous metals, korea, 5052 coil premium over 1050, kilo | 815 | 8 | 268 |
| 1044 | aluminum (non ferrous metals, korea, 3003 coil premium over 1050, kilo | 815 | 8 | 270 |
| 1248 | steel (steel, china, crc, metric ton) | 401 | 1 | 1818 |
| 613 | yttria (rare earth metals, china, 99.99-99.999% avg ref price, metric  | 395 | 15 | 172 |
| 94902 | ruthenium (precious metals, united states, granules min. 99.90%, kilog | 347 | 2 | 1504 |
| 414 | steel (steel, china, hdg coil, metric ton) | 316 | 5.0 | 447 |
| 199342 | lanthanum-cerium mixed metal (rare earth metals, china, trem>99%;ce/tr | 316 | 7 | 228 |
| 982 | steel (steel, china, slab, metric ton) | 314 | 2 | 1524 |
| 539 | aluminum (non ferrous metals, china, aluminum billet, metric ton) | 302 | 1 | 1744 |
| 1477 | rare earths mmi (mmi index values, global, na, index) | 243 | 1 | 1944 |
| 1478 | raw steels mmi (mmi index values, global, na, index) | 125 | 1.0 | 1961 |
| 1479 | renewables mmi (mmi index values, global, na, index) | 124 | 1 | 1926 |
| 1472 | automotive mmi (mmi index values, global, na, index) | 122 | 1 | 1952 |
| 199344 | neodymium metal (rare earth metals, china, trem>99%;nd/rem:99~99.9%;fe | 122 | 2.0 | 1177 |
| 1471 | aluminum mmi (mmi index values, global, na, index) | 121 | 1.0 | 1919 |

## Jumps: single-step move > 50% (14)

| id | series | bigJumps | obs | start | end |
|---|---|---|---|---|---|
| 94320 | steel (steel, korea, hr plate, kilogram) | 5 | 78 | 2020-01-01 | 2026-10-06 |
| 80746 | goes (grain oriented electrical steel) (steel, europe, coil (>600mm),  | 4 | 117 | 2017-01-01 | 2026-10-06 |
| 613 | yttria (rare earth metals, china, 99.99-99.999% avg ref price, metric  | 3 | 172 | 2011-12-15 | 2026-08-14 |
| 42605 | 430 (stainless steel, europe, cr coil, metric ton) | 3 | 151 | 2014-01-01 | 2026-09-07 |
| 1228 | nickel (non ferrous metals, india, primary, kilogram) | 2 | 3341 | 2011-12-30 | 2026-10-09 |
| 184 | palladium (precious metals, united states, sponge 99.95% purity, troy  | 1 | 3290 | 2012-01-03 | 2026-10-09 |
| 468 | 409 (stainless steel, united states, 2d (0.06 in x 48 in) sheet, pound | 1 | 487 | 2020-01-01 | 2026-10-09 |
| 1189 | 430-coil (stainless surcharges, united states, nas surcharge, pound) | 1 | 158 | 2011-10-26 | 2026-09-28 |
| 33076 | steel (steel, europe, crc, metric ton) | 1 | 154 | 2014-01-01 | 2026-10-06 |
| 49797 | 304 (stainless steel, europe, round bar (<25mm), metric ton) | 1 | 153 | 2014-01-01 | 2026-09-07 |
| 80747 | goes (grain oriented electrical steel) (steel, europe, coil (<600mm),  | 1 | 116 | 2017-01-01 | 2026-10-06 |
| 82101 | aluminum (non ferrous metals, united states, aup (mw premium) future 3 | 1 | 1173 | 2019-01-01 | 2026-10-07 |
| 82102 | aluminum (non ferrous metals, united states, aup (mw premium) spot, po | 1 | 1309 | 2019-01-01 | 2026-10-07 |
| 229605 | yttrium (rare earth metals, northeast asia, , kilogram) | 1 | 68 | 2020-12-01 | 2026-10-01 |

## Tradable, proprietary (the series worth building signals on) (37)

| id | series | obs | start | recentObs | staleDays |
|---|---|---|---|---|---|
| 187 | platinum (precious metals, united states, sponge 99.95% purity, troy o | 3404 | 2012-01-03 | 713 | 0 |
| 457 | nickel (non ferrous metals, china, primary, metric ton) | 3121 | 2011-12-30 | 616 | 0 |
| 821 | zinc (non ferrous metals, china, primary cash, metric ton) | 3035 | 2011-12-30 | 614 | 0 |
| 1072 | aluminum (non ferrous metals, india, primary cash, kilogram) | 3442 | 2011-12-30 | 637 | 0 |
| 1337 | zinc (non ferrous metals, india, primary cash, kilogram) | 3457 | 2011-12-31 | 644 | 1 |
| 270581 | dysprosium oxide (rare earth metals, china, 99.5%min fob, kilogram) | 3015 | 2013-03-21 | 637 | 16 |
| 270585 | electrical steel (stainless steel, china, grain oriented 130 0.3*980mm | 3232 | 2012-06-14 | 630 | 16 |
| 270601 | ferro-chrome (ferro alloys, china, kazakhstan cr 68%min, c 8.5%max in  | 1913 | 2017-12-18 | 629 | 16 |
| 270612 | ferro-holmium (rare earth metals, china, 80% exw, kilogram) | 3116 | 2012-10-29 | 624 | 16 |
| 270704 | h-beam steel (steel, shanghai, q235 200*200mm in warehouse, metric ton | 3302 | 2012-03-08 | 632 | 16 |
| 270787 | lithium carbonate (minor metals, america, 99.5%min fob south, kilogram | 1777 | 2018-01-31 | 607 | 16 |
| 270789 | lithium hydroxide monohydrate (minor metals, china, lioh 56.5%min, mag | 2425 | 2015-10-29 | 631 | 16 |
| 270800 | lutetium oxide (rare earth metals, exw, exw, kilogram) | 1451 | 2019-11-21 | 629 | 16 |
| 270840 | manganese dioxide (minor metals, china, alkaline 91%min exw, metric to | 3098 | 2013-01-04 | 631 | 16 |
| 270860 | manganese sulfate (minor metals, china, mn 32%min exw, metric ton) | 1927 | 2017-11-22 | 632 | 16 |
| 270879 | molybdenum bar (minor metals, china, 99.9%min exw, kilogram) | 3292 | 2011-12-30 | 621 | 16 |
| 270898 | ndfeb (rare earth metals, china, sintered rough 35m exw, kilogram) | 1130 | 2021-02-22 | 607 | 16 |
| 270899 | ndfeb (rare earth metals, china, sintered rough 45m exw, kilogram) | 1125 | 2021-02-22 | 606 | 16 |
| 270900 | ndfeb (rare earth metals, china, sintered rough 50m exw, kilogram) | 1135 | 2021-02-22 | 611 | 16 |
| 270901 | ndfeb (rare earth metals, china, sintered rough 35h exw, kilogram) | 1132 | 2021-02-22 | 612 | 16 |
| 270902 | ndfeb (rare earth metals, china, sintered rough 45h exw, kilogram) | 1134 | 2021-02-22 | 611 | 16 |
| 270903 | ndfeb (rare earth metals, china, sintered rough 48h exw, kilogram) | 1134 | 2021-02-22 | 611 | 16 |
| 270904 | ndfeb (rare earth metals, china, sintered rough 50h exw, kilogram) | 1133 | 2021-02-22 | 610 | 16 |
| 270905 | neodymium metal (rare earth metals, china, 99%min exw, kilogram) | 3322 | 2011-12-30 | 622 | 16 |
| 270906 | neodymium metal (rare earth metals, china, 99%min fob, kilogram) | 3302 | 2011-12-30 | 636 | 16 |
| 270907 | neodymium oxide (rare earth metals, china, 99.5%min exw, kilogram) | 2938 | 2013-08-19 | 624 | 16 |
| 270908 | neodymium oxide (rare earth metals, china, 99.5%min fob, kilogram) | 3290 | 2011-12-30 | 635 | 16 |
| 270914 | nickel sulfate (non ferrous metals, china, ni 22%min; co 0.05%max exw, | 3275 | 2012-04-17 | 633 | 16 |
| 270922 | praseodymium metal (rare earth metals, china, 99.5%min fob, kilogram) | 3293 | 2011-12-30 | 634 | 16 |
| 270923 | praseodymium oxide (rare earth metals, china, 99.5%min exw, kilogram) | 3063 | 2013-01-11 | 625 | 16 |
| 270924 | praseodymium oxide (rare earth metals, china, 99.5%min fob, kilogram) | 3294 | 2011-12-30 | 637 | 16 |
| 270928 | prnd mischmetal (rare earth metals, china, pr 25%, nd 75% exw, kilogra | 3334 | 2011-12-30 | 629 | 16 |
| 270929 | prnd mischmetal (rare earth metals, china, pr 25%, nd 75% fob, kilogra | 3007 | 2013-03-25 | 635 | 16 |
| 270930 | prnd oxide (rare earth metals, china, pr6o11 25%, nd2o3 75% exw, kilog | 3149 | 2012-09-20 | 625 | 16 |
| 271053 | terbium metal (rare earth metals, china, 99.9%min fob, kilogram) | 1617 | 2019-01-28 | 637 | 16 |
| 271055 | terbium oxide (rare earth metals, china, 99.99%min fob, kilogram) | 1628 | 2019-01-16 | 638 | 16 |
| 271078 | titanium sponge (minor metals, china, 99.7%min exw, metric ton) | 3206 | 2012-07-24 | 628 | 16 |
