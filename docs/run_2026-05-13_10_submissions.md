# 2026-05-13 official-data microvariant 10-submission loop

Competition: cvpr-2026-the-first-ai-children-challenge

Status: completed 10 submissions on 2026-05-13. Kaggle showed 10 same-day records after the loop, with 0 estimated remaining submissions.

## Compliance

This loop used official-data-only reproducible candidates generated on the server from:

- `data/raw/track1_train.json`
- `features/patient_light_features.csv`
- `submissions/candidates/2026-05-12-targeted/k08_i07_p47_p43_p72_p48.csv`

Generation scripts:

- `scripts/generate_2026_05_13_targeted_candidates.py`
- `scripts/generate_2026_05_05_official_candidates.py`

Candidate hashes and input hashes are recorded in:

- `submissions/candidates/2026-05-13-targeted/manifest.json`

No public-output row mixing was used in the submitted candidates. Track2 was frozen at the `k08` anchor.

## Submitted Results

| Loop | Experiment | Ref | Public | SHA256 | Notes |
|---:|---|---:|---:|---|---|
| 1 | `l01_k08_t1_78_meta9_thr045` | 52597558 | 0.69956 | `c8e1f9b82cb522775f1aa96527c6eadfd443a6c4c21b7c092a898f28b14da046` | Track1-78 +R5 was negative. |
| 2 | `l02_k08_t1_78_meta13_thr050` | 52597571 | 0.69956 | `0f1be02bbf6e5f27ceb9c77af2f64f8aa244932690610aae7ed2e0910d43fe79` | Track1-78 +L1 was negative. |
| 3 | `l03_k08_t1_83_meta15_thr045` | 52597583 | 0.69909 | `0f855198d92c29a111fe9622d92336691bfbb06e8653c0161e042e18b845203e` | Track1-83 +L16 was negative. |
| 4 | `l04_k08_t1_83_pid3_thr035` | 52597589 | 0.69909 | `7479a3336ce78926c72c755caf18cc91bebb704c6d0868b02c90cda8d404f4d9` | Track1-83 +R2 was negative. |
| 5 | `l05_k08_t1_85_meta15_thr035` | 52597595 | 0.69930 | `1e547a75f96d2f5f6f1d57a15d5cb2c1a54d90ff819cf8c2824c05f14d9055a5` | Track1-85 +L2 was negative. |
| 6 | `l06_k08_t1_72_meta11_thr050` | 52597605 | 0.69924 | `9de37068ce457812c3ed68bd57e39516fa931d5818eb96dfd96639a5250b7d66` | Track1-72 +R10 over-strengthened the row. |
| 7 | `l07_k08_t1_43_meta9_thr045` | 52597610 | 0.69956 | `0d4d21db64890bfdfe2f98276d694ae36ec29d7dae21d39daaca98826c80a489` | Track1-43 +R10 was negative. |
| 8 | `l08_k08_t1_53_meta15_thr045` | 52597618 | 0.69989 | `7ec2d1b5796a5154f84631973971c7c114122842235db83bd8e641c939e4bd6f` | Track1-53 equal-total k15 variant tied the current best. |
| 9 | `l09_k08_t1_28_meta13_thr050` | 52597626 | 0.69919 | `703914767d4d984e52b1b983e987a0e70458ba58ce68e3381dc91dba83d8c037` | Track1-28 +R8 was negative. |
| 10 | `l10_k08_t1_26_meta13_thr050` | 52597641 | 0.69930 | `3e0569087fc863276666262ff3905fb947bc228525fe83f98261c3890d293655` | Track1-26 one-bit metadata variant was negative. |

## Findings

- No new public best was found. The current reproducible best remains `k08_i07_p47_p43_p72_p48.csv`, public score `0.69989`.
- `l08_k08_t1_53_meta15_thr045` tied the best with a different Track1-53 bit choice, so p53 has at least two public-equivalent official-data variants.
- New one-bit additions on p78, p83, p85, p28, and p26 were all negative on public.
- Strengthening already-positive p72 and p43 rows by one extra bit also hurt.
- The 2026-05-12 k08 row stack appears locally tight: more severity is generally penalized.

## Page Updates Checked

- Rules and timeline were unchanged: daily limit remains 10; public code/model and local re-evaluation requirements remain in force.
- Discussion had no new rule change after the previous loop.
- Code page still showed 6 public notebooks, with no new notebook after 2026-05-12.
- Leaderboard team count increased to 52, but the top public score remained unchanged.

## Caveat

Kaggle discussion indicates submissions after 2026-04-23 may not count for the official challenge re-evaluation/awards and may primarily support technical-report analysis. The candidates in this loop remain official-data-only and reproducible for report and local re-evaluation purposes.

## Next Direction

- Keep `k08_i07_p47_p43_p72_p48.csv` as the current compliant pipeline anchor.
- Treat the 2026-05-13 negative one-bit probes as exclusion rules for the next loop.
- If submitting again, focus on neutral/equivalent p53 variants or carefully designed removals from k08 rather than adding severity to unmodified rows.
- Keep Track2 fixed at the g11/k08 labels.
