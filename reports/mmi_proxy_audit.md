# MMI proxy audit

Source dump: `a3b27724-historical_20260818.json.gz` · window 2013-08-19 → 2026-08-07 (666 ISO weeks, last observation per week, forward-filled).

| id | series | raw obs | weeks observed | weekly vol | flat weeks |
|---|---|---|---|---|---|
| 1477 | rare earths mmi (mmi index values, global, na, index) | 1892 | 321 | 0.0359 | 55.5% |
| 270930 | prnd oxide (rare earth metals, china, pr6o11 25%, nd2o3 75% exw, kilogram) | 3142 | 646 | 0.0337 | 3.0% |
| 270907 | neodymium oxide (rare earth metals, china, 99.5%min exw, kilogram) | 2931 | 646 | 0.0330 | 3.0% |
| 270923 | praseodymium oxide (rare earth metals, china, 99.5%min exw, kilogram) | 3056 | 646 | 0.0271 | 3.0% |
| 270928 | prnd mischmetal (rare earth metals, china, pr 25%, nd 75% exw, kilogram) | 3327 | 647 | 0.0320 | 2.9% |

Weekly log-return correlation (n = overlapping weeks):

| a | b | r | n |
|---|---|---|---|
| rare earths mmi | prnd oxide | 0.22 | 659 |
| rare earths mmi | neodymium oxide | 0.25 | 659 |
| rare earths mmi | praseodymium oxide | 0.22 | 659 |
| rare earths mmi | prnd mischmetal | 0.23 | 659 |
| neodymium oxide | prnd oxide | 0.94 | 665 |
| neodymium oxide | praseodymium oxide | 0.81 | 665 |
| neodymium oxide | prnd mischmetal | 0.93 | 665 |
| praseodymium oxide | prnd oxide | 0.79 | 665 |
| praseodymium oxide | prnd mischmetal | 0.82 | 665 |
| prnd mischmetal | prnd oxide | 0.97 | 665 |

Index vs assessments: r = 0.22–0.25; assessments among themselves: r = 0.79–0.97. Index weeks observed / reference: 321/646; index vol / reference vol: 1.07×.

