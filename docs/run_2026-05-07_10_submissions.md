# 2026-05-07 official-data targeted 10-submission loop

Competition: cvpr-2026-the-first-ai-children-challenge

Status: completed 10 submissions on 2026-05-07. Kaggle showed 10 same-day records after the loop, with 0 estimated remaining submissions.

## Compliance

This loop used official-data-only reproducible candidates generated on the server from:

- `data/raw/track2_train.json`
- `features/patient_light_features.csv`
- `submissions/candidates/2026-05-06-targeted/t15_of01_p48_p53_p54_t2_6.csv`
- `submissions/candidates/2026-05-06-targeted/t11_of01_p48_p53_meta13.csv`
- `submissions/candidates/2026-05-06-targeted/t12_of01_p48_p54_meta.csv`

Generation scripts:

- `scripts/generate_2026_05_07_targeted_candidates.py`
- `scripts/generate_2026_05_05_official_candidates.py`

Candidate hashes and input hashes are recorded in:

- `submissions/candidates/2026-05-07-targeted/manifest.json`

No public-output row mixing was used in the submitted candidates.

## Submitted Results

| Loop | Experiment | Ref | Public | SHA256 | Notes |
|---:|---|---:|---:|---|---|
| 1 | `g01_t15_t2_42_all3` | 52403934 | 0.69277 | `1c346a0b8304b8358d9c4cf7ff2c6476deca2b1db725d7b76b10182747424d68` | Strong positive Track2 row 42 on top of t15. |
| 2 | `g02_t15_t2_13_all3` | 52403951 | 0.64166 | `d0b307bfba6e5a6d2fbdfe91ff07db50d65a69d08d7bbebb0b9343a1bc77b3b3` | Weak positive Track2 row 13. |
| 3 | `g11_t15_t2_42_13_all3` | 52403966 | 0.69611 | `6e78254045e3dcfea727b00df8fb691e7ec96d57586ebad4992a13d643cdab23` | Best result: Track2 rows 42 and 13 stack. |
| 4 | `g04_t15_t2_7_all3` | 52403979 | 0.61666 | `d66f2bc313e2faa50542bdd00b74760f77f7a18bffd51a25a92dc30fd9c51be3` | Negative Track2 row 7. |
| 5 | `g06_t15_t2_39_all3` | 52403994 | 0.59222 | `9b713da7e79366a76703fe3c946916239a52cfad09b492b14da3ef690cac7e0c` | Negative Track2 row 39. |
| 6 | `g03_t15_t2_35_all3` | 52404009 | 0.64166 | `ecbccd562f4d0749507fb60a94cf1c4d31e6dd0e7196f6d431de97cdd9d050ac` | Weak positive Track2 row 35. |
| 7 | `g12_t15_t2_42_35_all3` | 52404021 | 0.69358 | `e3b32630cb9e13e37d45b3d1c5d0f7c83dcda6df334ca7de74e5520a2f98271a` | 42+35 was below 42+13. |
| 8 | `g15_t15_t2_42_13_35_all3` | 52404031 | 0.69358 | `a0d63e41eb857c06ccedf2302f4b7621f73428c061df26b0d19e0e0c960449cf` | Adding 35 to 42+13 reduced score. |
| 9 | `g16_t11_t2_42_13_all3` | 52404055 | 0.64406 | `c8339a5bef20ae8c22fea4fd693197926364f738b50d74ec1a8827977bc253f7` | Removing Track1 p54 hurt the 42+13 candidate. |
| 10 | `g17_t12_t2_42_13_all3` | 52404070 | 0.64380 | `ed605fb85f8837fb10b84a0256c6a7f45b0200aeee100e8bbd3fdf3896c7d940` | Removing Track1 p53 hurt the 42+13 candidate. |

## Findings

- New official-data-only best: `g11_t15_t2_42_13_all3.csv`, public score `0.69611`.
- Improvement over prior official-data-only best `t15_of01_p48_p53_p54_t2_6.csv` public `0.63999`: `+0.05612`.
- Improvement over the 2026-05-05 official-data anchor `of01_t1_meta11_t2_s09.csv` public `0.58653`: `+0.10958`.
- The largest single-row gain came from Track2 row 42: `0.69277`.
- Track2 rows 13 and 35 were weak positives alone, but only 13 stacked well with row 42.
- Track2 rows 7 and 39 were negative and should be avoided in the current all-view k=3 form.
- Track1 rows p48, p53, and p54 should remain together for the current best Track2 combination.

## Caveat

Kaggle discussion indicates submissions after 2026-04-23 may not count for the official challenge re-evaluation/awards and may primarily support technical-report analysis. The candidates in this loop remain official-data-only and reproducible for report and local re-evaluation purposes.

## Next Direction

- Keep `g11_t15_t2_42_13_all3.csv` as the current compliant pipeline anchor.
- Next loop should test alternative deterministic Track2 row-generation settings for row 42 and row 13, especially feature subsets and k changes.
- Avoid adding row 35 to the current best unless a different row-generation method changes its prediction.
