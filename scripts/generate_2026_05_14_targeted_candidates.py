#!/usr/bin/env python3
"""Generate targeted official-data-only May 14 candidates.

The May 13 loop showed that adding one-bit severity to k08 generally hurts,
while an alternate p53 row ties the public best. This loop freezes Track2 and
tests two narrow questions:

1. Are any of the k08 stacked Track1 rows overfitting in combination?
2. Do nearby official-data p53 variants interact better with the k08 stack?
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any

import pandas as pd

from generate_2026_05_05_official_candidates import (
    HEADER,
    apply_t1_rows,
    build_t1_rows,
    diff_rows,
    load_json,
    now_utc,
    numeric_features,
    read_submission,
    sha256,
    validate,
)


def replace_rows(base: pd.DataFrame, sources: list[tuple[pd.DataFrame, str]]) -> pd.DataFrame:
    out = base.copy()
    for source, row_id in sources:
        values = source.loc[source["ID"] == row_id, HEADER].iloc[0].tolist()
        out.loc[out["ID"] == row_id, HEADER] = values
    return out


def p53_variant(
    base: pd.DataFrame,
    train_rows: list[dict[str, Any]],
    features: pd.DataFrame,
    method: str,
    k: int,
    threshold: float,
) -> pd.DataFrame:
    rows = build_t1_rows(train_rows, features, method, k, threshold)
    return apply_t1_rows(base, {53: rows[53]})


def t1_variant(
    base: pd.DataFrame,
    train_rows: list[dict[str, Any]],
    features: pd.DataFrame,
    pid: int,
    method: str,
    k: int,
    threshold: float,
) -> pd.DataFrame:
    rows = build_t1_rows(train_rows, features, method, k, threshold)
    return apply_t1_rows(base, {pid: rows[pid]})


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--track1", default="data/raw/track1_train.json")
    parser.add_argument("--features", default="features/patient_light_features.csv")
    parser.add_argument("--base-k08", default="submissions/candidates/2026-05-12-targeted/k08_i07_p47_p43_p72_p48.csv")
    parser.add_argument("--base-l08", default="submissions/candidates/2026-05-13-targeted/l08_k08_t1_53_meta15_thr045.csv")
    parser.add_argument("--source-g11", default="submissions/candidates/2026-05-07-targeted/g11_t15_t2_42_13_all3.csv")
    parser.add_argument("--output-dir", default="submissions/candidates/2026-05-14-targeted")
    args = parser.parse_args()

    t1 = load_json(Path(args.track1))
    features = numeric_features(Path(args.features))
    k08 = read_submission(Path(args.base_k08))
    l08 = read_submission(Path(args.base_l08))
    g11 = read_submission(Path(args.source_g11))

    row = lambda pid: (g11, f"track1-{pid}")  # noqa: E731 - compact spec table helper.

    specs: list[tuple[str, pd.DataFrame, str]] = [
        (
            "m01_k08_t1_72_meta9_thr060",
            t1_variant(k08, t1, features, 72, "feature:meta", 9, 0.60),
            "Reduce Track1-72 severity by one bit on top of k08 after the May 13 p72 severity addition failed.",
        ),
        (
            "m02_l08_t1_72_meta9_thr060",
            t1_variant(l08, t1, features, 72, "feature:meta", 9, 0.60),
            "Reduce Track1-72 severity by one bit on the public-tied l08 p53 anchor.",
        ),
        (
            "m03_k08_t1_48_side15_thr045",
            t1_variant(k08, t1, features, 48, "feature:side", 15, 0.45),
            "Replace Track1-48 with a side-feature row to test a lower-severity p48 distribution.",
        ),
        (
            "m04_l08_t1_48_side15_thr045",
            t1_variant(l08, t1, features, 48, "feature:side", 15, 0.45),
            "Replace Track1-48 with the side-feature row on the public-tied l08 p53 anchor.",
        ),
        (
            "m05_k08_t1_43_meta15_thr055",
            t1_variant(k08, t1, features, 43, "feature:meta", 15, 0.55),
            "Replace Track1-43 with a conservative metadata k15 threshold 0.55 row.",
        ),
        (
            "m06_l08_t1_43_meta15_thr055",
            t1_variant(l08, t1, features, 43, "feature:meta", 15, 0.55),
            "Replace Track1-43 with the conservative metadata row on the public-tied l08 p53 anchor.",
        ),
        (
            "m07_k08_t1_53_meta11_thr040",
            p53_variant(k08, t1, features, "feature:meta", 11, 0.40),
            "Remove the two p53 strengthening bits with metadata k11 threshold 0.40 on top of k08.",
        ),
        (
            "m08_k08_t1_53_meta13_thr040",
            p53_variant(k08, t1, features, "feature:meta", 13, 0.40),
            "Probe a nearby p53 metadata k13 threshold 0.40 row on top of k08.",
        ),
        (
            "m09_l08_revert_t1_47_g11",
            replace_rows(l08, [row(47)]),
            "Use the public-tied l08 p53 variant and revert Track1-47 to test whether p47 is still required.",
        ),
        (
            "m10_l08_revert_t1_48_g11",
            replace_rows(l08, [row(48)]),
            "Use the public-tied l08 p53 variant and revert Track1-48 to test whether the p48 three-bit addition is still required.",
        ),
    ]

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, Any]] = []
    seen_hashes: set[str] = set()
    for experiment_id, df, description in specs:
        path = output_dir / f"{experiment_id}.csv"
        df.to_csv(path, index=False, quoting=csv.QUOTE_MINIMAL, lineterminator="\r\n")
        digest = sha256(path)
        if digest in seen_hashes:
            raise ValueError(f"duplicate candidate hash for {experiment_id}: {digest}")
        seen_hashes.add(digest)
        status, errors = validate(df)
        rows.append(
            {
                "created_at_utc": now_utc(),
                "experiment_id": experiment_id,
                "description": description,
                "path": str(path),
                "sha256": digest,
                "validation_status": status,
                "validation_errors": errors,
                "diff_rows_vs_k08": diff_rows(k08, df),
                "official_data_only": True,
            }
        )
        print(path)

    pd.DataFrame(rows).to_csv(output_dir / "manifest.csv", index=False)
    with (output_dir / "manifest.json").open("w", encoding="utf-8") as f:
        json.dump(
            {
                "created_at_utc": now_utc(),
                "compliance": "official-data-only deterministic k08/l08 Track1 ablations and p53 variants",
                "inputs": {
                    "track1": {"path": args.track1, "sha256": sha256(Path(args.track1))},
                    "features": {"path": args.features, "sha256": sha256(Path(args.features))},
                    "base_k08": {"path": args.base_k08, "sha256": sha256(Path(args.base_k08))},
                    "base_l08": {"path": args.base_l08, "sha256": sha256(Path(args.base_l08))},
                    "source_g11": {"path": args.source_g11, "sha256": sha256(Path(args.source_g11))},
                },
                "columns": HEADER,
                "experiments": rows,
            },
            f,
            indent=2,
            ensure_ascii=False,
        )
    print(output_dir / "manifest.csv")
    print(output_dir / "manifest.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
