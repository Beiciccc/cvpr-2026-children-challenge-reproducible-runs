# 2026-05-09 official-data targeted 10-submission loop

Competition: cvpr-2026-the-first-ai-children-challenge

Status: completed 10 submissions on 2026-05-09. Kaggle showed 10 same-day records after the loop, with 0 estimated remaining submissions.

## Compliance

This loop used official-data-only reproducible candidates generated on the server from:

- `data/raw/track2_train.json`
- `features/patient_light_features.csv`
- `submissions/candidates/2026-05-07-targeted/g11_t15_t2_42_13_all3.csv`
- `submissions/candidates/2026-05-05-official/of01_t1_meta11_t2_s09.csv`

Generation scripts:

- `scripts/generate_2026_05_09_targeted_candidates.py`
- `scripts/generate_2026_05_05_official_candidates.py`

Candidate hashes and input hashes are recorded in:

- `submissions/candidates/2026-05-09-targeted/manifest.json`

No public-output row mixing was used in the submitted candidates.

## Submitted Results

| Loop | Experiment | Ref | Public | SHA256 | Notes |
|---:|---|---:|---:|---|---|
| 1 | `h01_g11_t2_42_side7` | 52470037 | 0.66952 | `08b54c00bab13cb8ab3d8a3f4f2a64dc1d9fbec9a69bdfde3666fac4844a925b` | Track2-42 side k=7, label type2/type3, was worse. |
| 2 | `h02_g11_t2_42_meta11` | 52470057 | 0.67251 | `776f8919e156afb8a2986ed8962e4df1f5cac6da6961869cfbd5093639f8a3ed` | Track2-42 meta k=11, label type2/type1, was worse. |
| 3 | `h03_g11_t2_13_all11` | 52470071 | 0.69166 | `948aecdaa2e22b0688118409d2e190d53f84421e85442d33517f2e14692255b6` | Track2-13 all k=11 was below g11. |
| 4 | `h04_g11_t2_35_meta5` | 52470094 | 0.69166 | `5bdc8408812ec2cf66b57206b193636512826c00bf99afbffe2f8453a5defeac` | Track2-35 meta k=5 was below g11. |
| 5 | `h05_g11_t2_35_pid3` | 52470105 | 0.69358 | `b1c37547a23cea5caaa7934f529119a9c2734e82e632eeeaa032aefeafa6d5e1` | Track2-35 pid k=3 was close but below g11. |
| 6 | `h06_g11_t2_4_meta5` | 52470118 | 0.64166 | `fce4ea6f33a73123a275d39e67f6d96c7d304f5132dd3f5a11c3b47cf9382513` | Track2-4 meta k=5 was strongly negative. |
| 7 | `h07_g11_t2_50_meta5` | 52470126 | 0.64690 | `8919a9e201285cd17a80a9fb371bca48a7d925ba2b0a86f868d04cdddaf61e36` | Track2-50 meta k=5 was negative. |
| 8 | `h08_g11_t2_26_all3` | 52470144 | 0.62499 | `c4ad506524802bae761c431cae7a93ca57fbad2bfb3ea547bbe31aa8eef03ccf` | Track2-26 all k=3 was strongly negative. |
| 9 | `h09_g11_revert_track1_54` | 52470153 | 0.69517 | `15ccfd5622f4a38994b8c0be7b66e90983d6d8a80d5fd3b0cf6a07f4b7a2e013` | Pure Track1-54 rollback was slightly below g11. |
| 10 | `h10_g11_revert_track1_53` | 52470186 | 0.69491 | `a08398c7c779dc264d8da5425ef86237ecaf90c9026634958731da4b2a7898e8` | Pure Track1-53 rollback was slightly below g11. |

## Findings

- Current official-data-only best remains `g11_t15_t2_42_13_all3.csv`, public score `0.69611`.
- No 2026-05-09 candidate exceeded the 2026-05-07 best.
- Track2-42 is highly sensitive: alternatives `type2/type3` and `type2/type1` both reduced score, so the current `type2/type2` label should be preserved.
- Track2-13 current all3 label remains better than the all11 alternative.
- Track2-35 variants are near but below the best; row 35 should not be added with the tested labels.
- Track2-4, Track2-26, and Track2-50 replacements are negative and should be avoided.
- Pure Track1-53 and Track1-54 rollback tests are only slightly worse, confirming the current Track1 rows are useful but low-margin.

## Caveat

Kaggle discussion indicates submissions after 2026-04-23 may not count for the official challenge re-evaluation/awards and may primarily support technical-report analysis. The candidates in this loop remain official-data-only and reproducible for report and local re-evaluation purposes.

## Next Direction

- Keep `g11_t15_t2_42_13_all3.csv` as the current compliant pipeline anchor.
- Avoid changing Track2-42 away from `type2/type2`.
- Further work should shift from one-row KNN probes to either a stronger public, releasable model pipeline or local cross-validation analysis of Track2 label uncertainty.
