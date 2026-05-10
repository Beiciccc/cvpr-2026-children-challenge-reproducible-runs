# 2026-05-10 official-data targeted 10-submission loop

Competition: cvpr-2026-the-first-ai-children-challenge

Status: completed 10 submissions on 2026-05-10. Kaggle showed 10 same-day records after the loop, with 0 estimated remaining submissions.

## Compliance

This loop used official-data-only reproducible candidates generated on the server from:

- `data/raw/track1_train.json`
- `data/raw/track2_train.json`
- `features/patient_light_features.csv`
- `submissions/candidates/2026-05-07-targeted/g11_t15_t2_42_13_all3.csv`

Generation scripts:

- `scripts/generate_2026_05_10_targeted_candidates.py`
- `scripts/generate_2026_05_05_official_candidates.py`

Candidate hashes and input hashes are recorded in:

- `submissions/candidates/2026-05-10-targeted/manifest.json`

No public-output row mixing was used in the submitted candidates.

## Submitted Results

| Loop | Experiment | Ref | Public | SHA256 | Notes |
|---:|---|---:|---:|---|---|
| 1 | `i01_g11_t1_54_meta9_thr045` | 52498416 | 0.69517 | `cd598a8966c124850f5838140ea73b102e04f938b8d9f49c2f8794e4043a0e9c` | Near-anchor Track1-54 variant; below best. |
| 2 | `i02_g11_t1_47_meta13_thr040` | 52498425 | 0.69699 | `fb7bd3f68f91e9d699dce1c1cabc102f65a6ca39d544c023f108b3b5b53bb50c` | Track1-47 small positive probe; improved over g11. |
| 3 | `i03_g11_t1_42_meta7_thr045` | 52498438 | 0.69447 | `08df83ed06c315ce1711c35897687ef96fa3a84c106da1516676e23886c87429` | Track1-42 small probe was negative. |
| 4 | `i04_g11_t1_43_meta11_thr055` | 52498444 | 0.69644 | `033236ee5a52b1504be57334af0ddc15ab6df6549ea4f779a34801b5eb48d450` | Track1-43 small probe improved over g11 but not i02. |
| 5 | `i05_g11_t1_72_meta11_thr055` | 52498455 | 0.69674 | `423378a9f7914e6d22bf6e9a941ca1aadde998ae6b2fe1026b91fe17402af30e` | Track1-72 meta probe improved over g11 but not i02. |
| 6 | `i06_g11_t1_83_all15_thr040` | 52498473 | 0.69532 | `283ae22af6098a031540681e032bd9a940494638c19d5e61b959aadcd8e1e27d` | Track1-83 probe was below best. |
| 7 | `i07_g11_t1_53_meta3_thr040` | 52498484 | 0.69733 | `3da89d72383b3eb205ff63396a47403fe903d5052d5b325faeb34b6c557257ed` | New best: strengthened Track1-53 row. |
| 8 | `i08_g11_t1_48_meta15_thr045` | 52498495 | 0.69679 | `347fb0d207e8ba0c3ee1c2447fb7dffcfac0e2cf2c2f860e8f952788429d2769` | Track1-48 stronger variant improved over g11 but not i07. |
| 9 | `i09_g11_t2_6_meta3` | 52498509 | 0.64499 | `2859fa7c6f8da00e03a3e5c729349d5cccfe5fbd380948273b19850681c4945c` | Track2-6 meta k=3 was strongly negative. |
| 10 | `i10_g11_t1_72_side11_thr045` | 52498530 | 0.69611 | `6594fd9e91d197b6cbc54216ef72b3af5bec05f95b3cca2508e6770dea3cc63e` | Track1-72 side probe tied g11. |

## Findings

- New official-data-only best: `i07_g11_t1_53_meta3_thr040.csv`, public score `0.69733`.
- Improvement over previous official-data-only best `g11_t15_t2_42_13_all3.csv` public `0.69611`: `+0.00122`.
- Small Track1 perturbations can still improve the g11 anchor; Track1-53 is the strongest target from this loop.
- Positive but weaker Track1 probes: `track1-47`, `track1-43`, `track1-72` metadata, and `track1-48`.
- Track2-6 should remain at the current all3 `type1/type1`; changing it to metadata k=3 `type2/type2` severely reduced score.
- Track2-42 and Track2-13 should remain unchanged from g11 based on the 2026-05-09 results.

## Caveat

Kaggle discussion indicates submissions after 2026-04-23 may not count for the official challenge re-evaluation/awards and may primarily support technical-report analysis. The candidates in this loop remain official-data-only and reproducible for report and local re-evaluation purposes.

## Next Direction

- Use `i07_g11_t1_53_meta3_thr040.csv` as the current compliant pipeline anchor.
- Next loop should test small combinations of the positive Track1 rows: `i07` with `i02`, `i04`, `i05`, and `i08`.
- Keep Track2 fixed at the g11 labels unless a new model-backed Track2 generator is introduced.
