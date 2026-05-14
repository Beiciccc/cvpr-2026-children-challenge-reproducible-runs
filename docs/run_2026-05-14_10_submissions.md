# 2026-05-14 official-data targeted 10-submission loop

Competition: cvpr-2026-the-first-ai-children-challenge

Status: completed 10 submissions on 2026-05-14. Kaggle showed 10 same-day records after the loop, with 0 estimated remaining submissions.

## Compliance

This loop used official-data-only reproducible candidates generated on the server from:

- `data/raw/track1_train.json`
- `features/patient_light_features.csv`
- `submissions/candidates/2026-05-12-targeted/k08_i07_p47_p43_p72_p48.csv`
- `submissions/candidates/2026-05-13-targeted/l08_k08_t1_53_meta15_thr045.csv`
- `submissions/candidates/2026-05-07-targeted/g11_t15_t2_42_13_all3.csv`

Generation scripts:

- `scripts/generate_2026_05_14_targeted_candidates.py`
- `scripts/generate_2026_05_05_official_candidates.py`

Candidate hashes and input hashes are recorded in:

- `submissions/candidates/2026-05-14-targeted/manifest.json`

No public-output row mixing was used in the submitted candidates. Track2 was frozen at the `k08` anchor.

## Submitted Results

| Loop | Experiment | Ref | Public | SHA256 | Notes |
|---:|---|---:|---:|---|---|
| 1 | `m01_k08_t1_72_meta9_thr060` | 52633191 | 0.70047 | `2dae0cb702427e1e21b5ca97419ff48a492dad24bfdff0ae49ac2e9eb607b566` | New best: reduce Track1-72 by one bit from k08. |
| 2 | `m02_l08_t1_72_meta9_thr060` | 52633204 | 0.70047 | `aedcda4901af43528072f284f4f6c417b11b53b0eabae9097151a97bdf8c0cc6` | Tied new best with the alternate p53 anchor. |
| 3 | `m03_k08_t1_48_side15_thr045` | 52633209 | 0.69827 | `3bd3e162cde0431ce47193782108061c47b576062a5caea21442a434ac684ff2` | p48 side-feature replacement hurt. |
| 4 | `m04_l08_t1_48_side15_thr045` | 52633219 | 0.69827 | `e01ac89ec12b41d9f06bdd08fba7e0677ef76ffc7041b3dd9a53d0d490d0e799` | Same p48 replacement hurt under l08. |
| 5 | `m05_k08_t1_43_meta15_thr055` | 52633230 | 0.69924 | `a5712610d2b6c4faf81746691cc372eaa9fde99f9869567965a3a607ae451a8f` | Conservative p43 replacement hurt. |
| 6 | `m06_l08_t1_43_meta15_thr055` | 52633240 | 0.69924 | `3b87a18fc4eda77b7d4f246dc94c62a5a7d18621343dfccedef34b246bc9a0a9` | Same p43 replacement hurt under l08. |
| 7 | `m07_k08_t1_53_meta11_thr040` | 52633246 | 0.69866 | `80442b1521e49d5a33d785874552a302d6683beeedffa679738bd3767820fae9` | Removing p53 strengthening bits hurt. |
| 8 | `m08_k08_t1_53_meta13_thr040` | 52633251 | 0.70042 | `eba28f6b9b47ffe88cd93a3ba22d27f988300535ad5160908391f266b9276189` | Nearby p53 variant nearly tied the new best. |
| 9 | `m09_l08_revert_t1_47_g11` | 52633258 | 0.69899 | `cb9d3e7a2151c75d17a0ce99326c56c126bb831c6af559bbec5bc17456f57973` | Reverting p47 hurt. |
| 10 | `m10_l08_revert_t1_48_g11` | 52633265 | 0.69919 | `d21b9e14965a5dad67fb41484633f2dd794170770d7c8dfe16a8ddace8c7565d` | Reverting p48 hurt. |

## Findings

- New official-data-only best: `m01_k08_t1_72_meta9_thr060.csv`, public score `0.70047`.
- `m02_l08_t1_72_meta9_thr060.csv` tied the new best, confirming the p53 `k08` and `l08` anchors remain public-equivalent after the p72 severity reduction.
- Improvement over the previous reproducible best `k08_i07_p47_p43_p72_p48.csv` public `0.69989`: `+0.00058`.
- Track1-72 should be reduced by one bit from the May 12 k08 row: remove `R15`.
- Track1-48 and Track1-47 remain necessary; replacing or reverting them hurt.
- Track1-43 remains necessary; the conservative replacement hurt.
- p53 strengthening remains necessary; however, `m08` shows a nearby p53 row remains competitive at `0.70042`.

## Page Updates Checked

- Rules and timeline were unchanged: daily limit remains 10; public code/model and local re-evaluation requirements remain in force.
- Discussion had no new rule change after the previous loop.
- Code page still showed 6 public notebooks, with no new notebook after 2026-05-13.
- Leaderboard team count increased to 53. Top public score remained `0.92989`.

## Caveat

Kaggle discussion indicates submissions after 2026-04-23 may not count for the official challenge re-evaluation/awards and may primarily support technical-report analysis. The candidates in this loop remain official-data-only and reproducible for report and local re-evaluation purposes.

## Next Direction

- Use `m01_k08_t1_72_meta9_thr060.csv` as the current compliant pipeline anchor.
- Treat `m02` as an equivalent alternate anchor if p53 bit-choice interaction is useful.
- Next loop should test very small changes around the new p72-reduced anchor, especially p53 `meta13` variants and cautious one-row removals, while keeping Track2 fixed.
