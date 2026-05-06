# 2026-05-05 official-data 5-submission loop

Competition: cvpr-2026-the-first-ai-children-challenge

Status: completed 5 additional submissions on 2026-05-05. Kaggle showed 10 same-day records after the loop, with 0 estimated remaining submissions.

## Compliance

This loop used official-data-only reproducible candidates. Candidate files were generated on the server from:

- `data/raw/track1_train.json`
- `data/raw/track2_train.json`
- `features/patient_light_features.csv`
- `submissions/candidates/s09_t1_id_t2_feature_nopid.csv`

The generation script records input hashes and candidate hashes in `submissions/candidates/2026-05-05-official/manifest.json`. No public-output row mixing was used in these five submissions.

Generation script:

- `scripts/generate_2026_05_05_official_candidates.py`

## Submitted Results

| Loop | Experiment | Ref | Public | SHA256 | Notes |
|---:|---|---:|---:|---|---|
| 6 | `of02_t1_pid5_t2_s09` | 52344140 | 0.58315 | `35d140b3a263a5f1c842340f439948968ec80b1fd6469aaff0d541588cb1ab05` | Track1 pid k5/thr .45 under official-data anchor. |
| 7 | `of01_t1_meta11_t2_s09` | 52344168 | 0.58653 | `ccf4fe7704851b7fc8bb60206fb656fd697a3b0ae316cde874ec1a79054f73f4` | New official-data-only best. |
| 8 | `of07_t1_s09_t2_meta3` | 52344188 | 0.42915 | `6aa0d15e20a5a6f9e13984f24f7df5d4529d483033d175f13c1d6a5cc5ded121` | Track2 metadata k3 is harmful. |
| 9 | `of09_t1_meta9_t2_s09` | 52344283 | 0.58281 | `1dcc6fbf5f7ec4390bd2d642626efb883c6d903a08f9bdba405bc828e97ff07b` | Track1 metadata k9 below k11. |
| 10 | `of10_t1_meta13_t2_s09` | 52344297 | 0.57858 | `693045755a6ca1b99fb52270ca2281e8be4f5225ac1f7f8e7f1e0c0703a432d6` | Track1 metadata k13 below k11. |

## Findings

- The best compliant submission from this loop is `of01_t1_meta11_t2_s09.csv` with public score `0.58653`.
- This improves the prior official-data-only anchor `s09_t1_id_t2_feature_nopid.csv` public score `0.58470` by `+0.00183`.
- Track1 light metadata KNN has a narrow optimum around `k=11` in this candidate family: `k=9` and `k=13` both dropped.
- Track2 metadata KNN k3 is not viable as implemented; isolated Track2 replacement dropped to `0.42915`.
- The diagnostic public best remains `b01_m33_p53_morepos.csv` public score `0.89510`, but that family is not award-compliant unless rebuilt from a public, reproducible code/model pipeline without public-output leakage.

## Next Direction

- Keep `of01_t1_meta11_t2_s09.csv` as the official-data-only best anchor.
- Do not spend further submissions on Track2 metadata KNN without a stronger local validation signal.
- Next compliant work should focus on Track1 metadata KNN feature subsets, threshold calibration around 0.50, and a reproducible Track2 model that does not degrade the s09 Track2 anchor.
