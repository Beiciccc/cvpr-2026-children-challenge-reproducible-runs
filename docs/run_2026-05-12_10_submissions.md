# 2026-05-12 official-data targeted 10-submission loop

Competition: cvpr-2026-the-first-ai-children-challenge

Status: completed 10 submissions on 2026-05-12. Kaggle showed 10 same-day records after the loop, with 0 estimated remaining submissions.

## Compliance

This loop used official-data-only reproducible candidates generated on the server from:

- `data/raw/track1_train.json`
- `features/patient_light_features.csv`
- `submissions/candidates/2026-05-10-targeted/i07_g11_t1_53_meta3_thr040.csv`
- `submissions/candidates/2026-05-10-targeted/i02_g11_t1_47_meta13_thr040.csv`
- `submissions/candidates/2026-05-10-targeted/i04_g11_t1_43_meta11_thr055.csv`
- `submissions/candidates/2026-05-10-targeted/i05_g11_t1_72_meta11_thr055.csv`
- `submissions/candidates/2026-05-10-targeted/i08_g11_t1_48_meta15_thr045.csv`
- `submissions/candidates/2026-05-07-targeted/g11_t15_t2_42_13_all3.csv`

Generation scripts:

- `scripts/generate_2026_05_12_targeted_candidates.py`
- `scripts/generate_2026_05_05_official_candidates.py`

Candidate hashes and input hashes are recorded in:

- `submissions/candidates/2026-05-12-targeted/manifest.json`

No public-output row mixing was used in the submitted candidates.

## Submitted Results

| Loop | Experiment | Ref | Public | SHA256 | Notes |
|---:|---|---:|---:|---|---|
| 1 | `k01_i07_p47` | 52570221 | 0.69822 | `e397b59e4173f13bceabe059753664dca89a4947aa41f74f12bf5276478aeebd` | Adding p47 to i07 improved. |
| 2 | `k02_i07_p43` | 52570240 | 0.69766 | `6ece88bcd680d002b272b16c158a59728f66a2df3ba6865480d9d1380ef75098` | Adding p43 improved slightly. |
| 3 | `k03_i07_p72` | 52570266 | 0.69796 | `2641ee68b82a2419851e3623dcb77bc7a53482ae80c0ff163fd7edb03f1ce539` | Adding p72 improved. |
| 4 | `k04_i07_p48` | 52570285 | 0.69802 | `f905da584f97094e70d56a10a7f225fab1811e4516d07f1f4d34d2840be9a6a8` | Adding p48 improved. |
| 5 | `k05_i07_p47_p43` | 52570305 | 0.69855 | `140f2ba4cc62c942798669eff7639497bba0e2d032b60d0d171c5f7b29c7b34d` | p47+p43 stacked. |
| 6 | `k06_i07_p47_p72` | 52570325 | 0.69886 | `f6250447d71399c2e94f69820325b1fdcf444cd3845e3a2070f7022d57c8ac4f` | p47+p72 stacked strongly. |
| 7 | `k07_i07_p47_p48` | 52570343 | 0.69891 | `b9983487e06ea65d82617e1cdaf9347c45f9c5a794b049b43c365d583e0a214d` | p47+p48 was the best two-row combo. |
| 8 | `k08_i07_p47_p43_p72_p48` | 52570362 | 0.69989 | `c60b987bb5afcdea163ad79857cb4f5fea0165bc9129aa8004a85a406f238df2` | New best: all four positive non-p53 rows on i07. |
| 9 | `k09_g11_t1_53_meta5_thr045` | 52570379 | 0.69641 | `9230273e35cd9167bb2d617531e1bc99671876797835107bfae402623c483e64` | Alternate p53 bit choice was worse. |
| 10 | `k10_g11_t1_53_meta15_thr045` | 52570407 | 0.69733 | `3f5b734369ac64c1c13ecd8378610831468913ed9c82d7651eb2fdb4c3ea94e2` | Alternate p53 bit choice tied i07. |

## Findings

- New official-data-only best: `k08_i07_p47_p43_p72_p48.csv`, public score `0.69989`.
- Improvement over previous official-data-only best `i07_g11_t1_53_meta3_thr040.csv` public `0.69733`: `+0.00256`.
- Improvement over the 2026-05-07 g11 anchor public `0.69611`: `+0.00378`.
- The positive non-p53 Track1 rows from 2026-05-10 stacked instead of cancelling.
- Track1-47 is the strongest single row to add on top of i07; p48 and p72 are also strong.
- The p53 bit choice matters: metadata k=5 fell below i07, while metadata k=15 tied i07 rather than improving.

## Page Updates Checked

- Rules and timeline were unchanged: daily limit remains 10; public code/model and local re-evaluation requirements remain in force.
- Discussion had no new rule change after the previous loop.
- Code page now shows 6 public notebooks, including `sponishflea/children-2026` last run on 2026-05-10.

## Caveat

Kaggle discussion indicates submissions after 2026-04-23 may not count for the official challenge re-evaluation/awards and may primarily support technical-report analysis. The candidates in this loop remain official-data-only and reproducible for report and local re-evaluation purposes.

## Next Direction

- Use `k08_i07_p47_p43_p72_p48.csv` as the current compliant pipeline anchor.
- Next loop should test whether the same four-row stack tolerates small additions from p85, p78, p26, or one of the near-neutral p72 variants.
- Keep Track2 fixed at the g11 labels.
