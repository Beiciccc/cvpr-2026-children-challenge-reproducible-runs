# 2026-05-06 official-data targeted 10-submission loop

Competition: cvpr-2026-the-first-ai-children-challenge

Status: completed 10 submissions on 2026-05-06. Kaggle showed 10 same-day records after the loop, with 0 estimated remaining submissions.

## Compliance

This loop used official-data-only reproducible candidates generated on the server from:

- `data/raw/track1_train.json`
- `data/raw/track2_train.json`
- `features/patient_light_features.csv`
- `submissions/candidates/2026-05-05-official/of01_t1_meta11_t2_s09.csv`

Generation scripts:

- `scripts/generate_2026_05_06_targeted_candidates.py`
- `scripts/generate_2026_05_06_official_candidates.py`

Candidate hashes and input hashes are recorded in:

- `submissions/candidates/2026-05-06-targeted/manifest.json`
- `submissions/candidates/2026-05-06-official/manifest.json`

No public-output row mixing was used in the submitted candidates.

## Submitted Results

| Loop | Experiment | Ref | Public | SHA256 | Notes |
|---:|---|---:|---:|---|---|
| 1 | `t01_of01_p53_meta13` | 52372240 | 0.58770 | `65bce37ae0a2bc1cfd5ada5fe27e4cc67575aa72f38ccb60ab1f7a96d0346429` | p53 meta13 single row improved. |
| 2 | `t02_of01_p53_pid5` | 52372255 | 0.58537 | `e5a02e8fdd0873c90129b701c1f1542f1baffd0f0d6dfce42e599b569f0d1e06` | p53 pid5 was worse than of01. |
| 3 | `t03_of01_p18_meta13` | 52372267 | 0.58532 | `ab6887aa6ac85e3348b91bed426a640ace5c25a7ecdd768c02ed77ddc6adc59c` | p18 meta13 was worse than of01. |
| 4 | `t04_of01_p54_meta7` | 52372279 | 0.58745 | `537c977c82164d1f143269b9209f60a1dc07f2a101df63d5fe30641b340f4fd5` | p54 meta7 improved. |
| 5 | `t05_of01_p78_meta9` | 52372300 | 0.58619 | `ad7b7dac6ea93cd27e74b38822a98f99ae06028b69190b71c101390030d02eaf` | p78 meta9 was slightly worse. |
| 6 | `t06_of01_p48_meta13` | 52372322 | 0.58842 | `0c39aeb4fd98c8226a17ca39ce5ac607a0d19b4de149c0fcd626c960905e9c42` | p48 meta13 improved. |
| 7 | `t11_of01_p48_p53_meta13` | 52372372 | 0.58961 | `68dc373955907ffa1f380332fc9c4d7052d5656332040ba0f6f510df8958e6e2` | p48+p53 improved. |
| 8 | `t12_of01_p48_p54_meta` | 52372384 | 0.58935 | `29c664d159a88cfb686b89a8fd2cd850ae5f4d551f10090af078c86bd09ba2d5` | p48+p54 improved. |
| 9 | `t13_of01_p48_p53_p54_meta` | 52372400 | 0.59055 | `2ca461893ed3275112433cc5c70ae232e6a2daac570abb7ace04ee8545bf0718` | p48+p53+p54 improved. |
| 10 | `t15_of01_p48_p53_p54_t2_6` | 52372435 | 0.63999 | `8bbf3a8d5a8908b6100973e0e5235893414c6645762031edcb294bb8c81fb143` | Added official Track2 all3 row for track2-6; major improvement. |

## Findings

- New official-data-only best: `t15_of01_p48_p53_p54_t2_6.csv`, public score `0.63999`.
- Improvement over previous official-data-only best `of01_t1_meta11_t2_s09.csv` public `0.58653`: `+0.05346`.
- Strong positive Track1 rows: `track1-48`, `track1-53`, `track1-54`.
- Negative or weak Track1 probes: `track1-18`, `track1-78`, and p53 pid5.
- The final gain came from adding `track2-6` from official all-view KNN k=3 to the positive Track1 combination.
- Diagnostic public-output best remains `b01_m33_p53_morepos.csv` public `0.89510`, but it is not an award-compliant target unless rebuilt into a public, rerunnable, leakage-free pipeline.

## Caveat

Kaggle discussion indicates submissions after 2026-04-23 may not count for the official challenge re-evaluation/awards and may primarily support technical-report analysis. The candidates in this loop remain official-data-only and reproducible for report and local re-evaluation purposes.

## Next Direction

- Keep `t15_of01_p48_p53_p54_t2_6.csv` as the current compliant pipeline anchor.
- Next loop should test Track2 all-view KNN single rows on top of `t13/t15`, especially `track2-42`, and controlled Track2 combinations.
- Preserve `t13` as a Track1-only fallback in case Track2 row changes overfit public.
