# MetalMiner series quality

Source dump: `historical_latest.json.gz` · as of 2026-11-18 · 169 series.

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
| 356 | aluminum (non ferrous metals, korea, commercial 1050 sheet, kilogram) | 2025-11-20 | 363 | 265 |
| 581 | aluminum (non ferrous metals, korea, 5052 coil premium over 1050, kilo | 2025-11-20 | 363 | 268 |
| 1044 | aluminum (non ferrous metals, korea, 3003 coil premium over 1050, kilo | 2025-11-20 | 363 | 270 |
| 618 | steel (steel, korea, rebar, metric ton) | 2026-01-01 | 321 | 359 |
| 1136 | steel (steel, korea, hrc, metric ton) | 2026-01-01 | 321 | 283 |

## Frozen: > 40% unchanged steps or flat run > 60 (23)

| id | series | flatShare | longestFlatRun | obs | medianGapDays |
|---|---|---|---|---|---|
| 827 | 201 (stainless steel, united states, 2b ctl (0.075 in x 48 in) sheet,  | 0.936 | 34 | 1344 | 1 |
| 468 | 409 (stainless steel, united states, 2d (0.06 in x 48 in) sheet, pound | 0.8365 | 32 | 527 | 1.0 |
| 191 | 304 (stainless steel, united states, #4 polish vinyl ctl (0.048 in x 4 | 0.7456 | 34 | 398 | 1 |
| 5 | steel (steel, united states, wire rod, cwt) | 0.7269 | 22 | 1839 | 1.0 |
| 538 | 304 (stainless steel, united states, 2b (0.075 in x 48 in) sheet, poun | 0.7164 | 34 | 336 | 1 |
| 434 | 316l (stainless steel, united states, 2b ctl (0.075 in x 48 in) sheet, | 0.7009 | 34 | 342 | 1 |
| 235 | 430 (stainless steel, united states, #4 polish vinyl ctl (0.048 in x 4 | 0.6148 | 32 | 245 | 1.0 |
| 29004 | aluminum (non ferrous metals, europe, 6082 T6 (0.08 in x 48 in) sheet, | 0.6074 | 19 | 1463 | 1.0 |
| 29003 | aluminum (non ferrous metals, europe, 5251 H32 (0.08 in x 48 in) sheet | 0.6068 | 19 | 1461 | 1.0 |
| 523 | steel (steel, united states, aluminized dds astm a463 t1 40 (0.05 in x | 0.5131 | 17 | 726 | 1 |
| 1346 | aluminum (non ferrous metals, united states, 5083 h321 (1 in x 60 in)  | 0.4816 | 13 | 1880 | 1 |
| 916 | aluminum (non ferrous metals, united states, 5052 h32 (0.06 in x 60 in | 0.4811 | 13 | 1876 | 1 |
| 1040 | aluminum (non ferrous metals, united states, 6061 t651 (0.5 in x 48 in | 0.4763 | 13 | 1859 | 1.0 |
| 663 | aluminum (non ferrous metals, united states, 3003 h14 (0.08 in x 48 in | 0.4681 | 13 | 1832 | 1 |
| 1281 | aluminum (non ferrous metals, united states, 6061 t6 (0.08 in x 48 in) | 0.4671 | 13 | 1827 | 1.0 |
| 1477 | rare earths mmi (mmi index values, global, na, index) | 0.4599 | 34 | 1984 | 1 |
| 503 | aluminum (non ferrous metals, united states, 1100 h14 (0.08 in x 48 in | 0.4489 | 13 | 1966 | 1 |
| 72095 | lmo hydroxide-based (battery prices, global, index, index) | 0.2647 | 92 | 2415 | 1.0 |
| 72097 | nmc811 hydroxide-based (battery prices, global, index, index) | 0.2634 | 92 | 2419 | 1.0 |
| 1248 | steel (steel, china, crc, metric ton) | 0.2299 | 91 | 1858 | 1 |
| 393 | steel (steel, china, plate, metric ton) | 0.2039 | 91 | 2095 | 1.0 |
| 258 | steel (steel, china, hrc, short ton) | 0.1967 | 91 | 2172 | 1 |
| 733 | steel (steel, china, rebar, metric ton) | 0.1894 | 91 | 2250 | 1 |

## Holes: max gap > 120d in a daily/weekly series (16)

| id | series | maxGapDays | medianGapDays | obs |
|---|---|---|---|---|
| 356 | aluminum (non ferrous metals, korea, commercial 1050 sheet, kilogram) | 815 | 8.0 | 265 |
| 581 | aluminum (non ferrous metals, korea, 5052 coil premium over 1050, kilo | 815 | 8 | 268 |
| 1044 | aluminum (non ferrous metals, korea, 3003 coil premium over 1050, kilo | 815 | 8 | 270 |
| 1248 | steel (steel, china, crc, metric ton) | 401 | 1 | 1858 |
| 613 | yttria (rare earth metals, china, 99.99-99.999% avg ref price, metric  | 395 | 15 | 174 |
| 94902 | ruthenium (precious metals, united states, granules min. 99.90%, kilog | 347 | 2 | 1524 |
| 414 | steel (steel, china, hdg coil, metric ton) | 316 | 5 | 460 |
| 199342 | lanthanum-cerium mixed metal (rare earth metals, china, trem>99%;ce/tr | 316 | 7.0 | 229 |
| 982 | steel (steel, china, slab, metric ton) | 314 | 2.0 | 1539 |
| 539 | aluminum (non ferrous metals, china, aluminum billet, metric ton) | 302 | 1.0 | 1771 |
| 1477 | rare earths mmi (mmi index values, global, na, index) | 243 | 1 | 1984 |
| 1478 | raw steels mmi (mmi index values, global, na, index) | 125 | 1.0 | 2001 |
| 1479 | renewables mmi (mmi index values, global, na, index) | 124 | 1 | 1966 |
| 1472 | automotive mmi (mmi index values, global, na, index) | 122 | 1 | 1992 |
| 199344 | neodymium metal (rare earth metals, china, trem>99%;nd/rem:99~99.9%;fe | 122 | 2 | 1184 |
| 1471 | aluminum mmi (mmi index values, global, na, index) | 121 | 1.0 | 1959 |

## Jumps: single-step move > 50% (14)

| id | series | bigJumps | obs | start | end |
|---|---|---|---|---|---|
| 94320 | steel (steel, korea, hr plate, kilogram) | 5 | 79 | 2020-01-01 | 2026-11-06 |
| 80746 | goes (grain oriented electrical steel) (steel, europe, coil (>600mm),  | 4 | 118 | 2017-01-01 | 2026-11-06 |
| 613 | yttria (rare earth metals, china, 99.99-99.999% avg ref price, metric  | 3 | 174 | 2011-12-15 | 2026-10-29 |
| 42605 | 430 (stainless steel, europe, cr coil, metric ton) | 3 | 153 | 2014-01-01 | 2026-11-06 |
| 1228 | nickel (non ferrous metals, india, primary, kilogram) | 2 | 3364 | 2011-12-30 | 2026-11-17 |
| 184 | palladium (precious metals, united states, sponge 99.95% purity, troy  | 1 | 3316 | 2012-01-03 | 2026-11-18 |
| 468 | 409 (stainless steel, united states, 2d (0.06 in x 48 in) sheet, pound | 1 | 527 | 2020-01-01 | 2026-11-18 |
| 1189 | 430-coil (stainless surcharges, united states, nas surcharge, pound) | 1 | 159 | 2011-10-26 | 2026-10-26 |
| 33076 | steel (steel, europe, crc, metric ton) | 1 | 155 | 2014-01-01 | 2026-11-06 |
| 49797 | 304 (stainless steel, europe, round bar (<25mm), metric ton) | 1 | 155 | 2014-01-01 | 2026-11-06 |
| 80747 | goes (grain oriented electrical steel) (steel, europe, coil (<600mm),  | 1 | 117 | 2017-01-01 | 2026-11-06 |
| 82101 | aluminum (non ferrous metals, united states, aup (mw premium) future 3 | 1 | 1196 | 2019-01-01 | 2026-11-17 |
| 82102 | aluminum (non ferrous metals, united states, aup (mw premium) spot, po | 1 | 1337 | 2019-01-01 | 2026-11-17 |
| 229605 | yttrium (rare earth metals, northeast asia, , kilogram) | 1 | 69 | 2020-12-01 | 2026-11-01 |

## Tradable, proprietary (the series worth building signals on) (38)

| id | series | obs | start | recentObs | staleDays |
|---|---|---|---|---|---|
| 187 | platinum (precious metals, united states, sponge 99.95% purity, troy o | 3430 | 2012-01-03 | 711 | 0 |
| 457 | nickel (non ferrous metals, china, primary, metric ton) | 3146 | 2011-12-30 | 615 | 0 |
| 821 | zinc (non ferrous metals, china, primary cash, metric ton) | 3060 | 2011-12-30 | 613 | 0 |
| 1072 | aluminum (non ferrous metals, india, primary cash, kilogram) | 3467 | 2011-12-30 | 637 | 1 |
| 1337 | zinc (non ferrous metals, india, primary cash, kilogram) | 3481 | 2011-12-31 | 642 | 1 |
| 270581 | dysprosium oxide (rare earth metals, china, 99.5%min fob, kilogram) | 3072 | 2013-03-21 | 670 | 0 |
| 270585 | electrical steel (stainless steel, china, grain oriented 130 0.3*980mm | 3289 | 2012-06-14 | 662 | 0 |
| 270601 | ferro-chrome (ferro alloys, china, kazakhstan cr 68%min, c 8.5%max in  | 1970 | 2017-12-18 | 661 | 0 |
| 270612 | ferro-holmium (rare earth metals, china, 80% exw, kilogram) | 3173 | 2012-10-29 | 657 | 0 |
| 270704 | h-beam steel (steel, shanghai, q235 200*200mm in warehouse, metric ton | 3359 | 2012-03-08 | 664 | 0 |
| 270787 | lithium carbonate (minor metals, america, 99.5%min fob south, kilogram | 1835 | 2018-01-31 | 640 | 0 |
| 270789 | lithium hydroxide monohydrate (minor metals, china, lioh 56.5%min, mag | 2482 | 2015-10-29 | 663 | 0 |
| 270800 | lutetium oxide (rare earth metals, exw, exw, kilogram) | 1508 | 2019-11-21 | 662 | 0 |
| 270840 | manganese dioxide (minor metals, china, alkaline 91%min exw, metric to | 3155 | 2013-01-04 | 663 | 0 |
| 270860 | manganese sulfate (minor metals, china, mn 32%min exw, metric ton) | 1983 | 2017-11-22 | 663 | 0 |
| 270879 | molybdenum bar (minor metals, china, 99.9%min exw, kilogram) | 3349 | 2011-12-30 | 654 | 0 |
| 270898 | ndfeb (rare earth metals, china, sintered rough 35m exw, kilogram) | 1187 | 2021-02-22 | 641 | 0 |
| 270899 | ndfeb (rare earth metals, china, sintered rough 45m exw, kilogram) | 1182 | 2021-02-22 | 641 | 0 |
| 270900 | ndfeb (rare earth metals, china, sintered rough 50m exw, kilogram) | 1192 | 2021-02-22 | 646 | 0 |
| 270901 | ndfeb (rare earth metals, china, sintered rough 35h exw, kilogram) | 1189 | 2021-02-22 | 647 | 0 |
| 270902 | ndfeb (rare earth metals, china, sintered rough 45h exw, kilogram) | 1191 | 2021-02-22 | 646 | 0 |
| 270903 | ndfeb (rare earth metals, china, sintered rough 48h exw, kilogram) | 1191 | 2021-02-22 | 646 | 0 |
| 270904 | ndfeb (rare earth metals, china, sintered rough 50h exw, kilogram) | 1190 | 2021-02-22 | 644 | 0 |
| 270905 | neodymium metal (rare earth metals, china, 99%min exw, kilogram) | 3379 | 2011-12-30 | 656 | 0 |
| 270906 | neodymium metal (rare earth metals, china, 99%min fob, kilogram) | 3359 | 2011-12-30 | 669 | 0 |
| 270907 | neodymium oxide (rare earth metals, china, 99.5%min exw, kilogram) | 2995 | 2013-08-19 | 658 | 0 |
| 270908 | neodymium oxide (rare earth metals, china, 99.5%min fob, kilogram) | 3347 | 2011-12-30 | 668 | 0 |
| 270914 | nickel sulfate (non ferrous metals, china, ni 22%min; co 0.05%max exw, | 3332 | 2012-04-17 | 665 | 0 |
| 270922 | praseodymium metal (rare earth metals, china, 99.5%min fob, kilogram) | 3350 | 2011-12-30 | 667 | 0 |
| 270923 | praseodymium oxide (rare earth metals, china, 99.5%min exw, kilogram) | 3120 | 2013-01-11 | 659 | 0 |
| 270924 | praseodymium oxide (rare earth metals, china, 99.5%min fob, kilogram) | 3351 | 2011-12-30 | 670 | 0 |
| 270928 | prnd mischmetal (rare earth metals, china, pr 25%, nd 75% exw, kilogra | 3391 | 2011-12-30 | 663 | 0 |
| 270929 | prnd mischmetal (rare earth metals, china, pr 25%, nd 75% fob, kilogra | 3064 | 2013-03-25 | 668 | 0 |
| 270930 | prnd oxide (rare earth metals, china, pr6o11 25%, nd2o3 75% exw, kilog | 3206 | 2012-09-20 | 659 | 0 |
| 271053 | terbium metal (rare earth metals, china, 99.9%min fob, kilogram) | 1674 | 2019-01-28 | 670 | 0 |
| 271055 | terbium oxide (rare earth metals, china, 99.99%min fob, kilogram) | 1685 | 2019-01-16 | 671 | 0 |
| 271075 | titanium plate (minor metals, china, ta2 2mm exw, kilogram) | 3148 | 2012-04-16 | 615 | 0 |
| 271078 | titanium sponge (minor metals, china, 99.7%min exw, metric ton) | 3263 | 2012-07-24 | 660 | 0 |
