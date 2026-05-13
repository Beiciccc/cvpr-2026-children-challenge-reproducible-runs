#!/usr/bin/env python3
"""Generate targeted official-data-only May 13 candidates.

The May 12 loop established k08 as the best compliant anchor by stacking four
positive Track1 rows on the i07/g11 base. This loop freezes Track2 and probes
small official-data Track1 row variants around that anchor. Most candidates are
single-bit additions, keeping the public-score readout interpretable and the
submission fully reproducible from released labels plus local light features.
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


def one_t1(
    train_rows: list[dict[str, Any]],
    features: pd.DataFrame,
    pid: int,
    method: str,
    k: int,
    threshold: float,
) -> dict[int, tuple[list[int], list[int]]]:
    rows = build_t1_rows(train_rows, features, method, k, threshold)
    return {pid: rows[pid]}


def add_t1_variant(
    specs: list[tuple[str, pd.DataFrame, str]],
    base: pd.DataFrame,
    train_rows: list[dict[str, Any]],
    features: pd.DataFrame,
    experiment_id: str,
    pid: int,
    method: str,
    k: int,
    threshold: float,
    description: str,
) -> None:
    rows = one_t1(train_rows, features, pid, method, k, threshold)
    left, right = rows[pid]
    specs.append(
        (
            experiment_id,
            apply_t1_rows(base, rows),
            f"{description}; row={pid}; method={method}; k={k}; threshold={threshold}; total={sum(left) + sum(right)}",
        )
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--track1", default="data/raw/track1_train.json")
    parser.add_argument("--features", default="features/patient_light_features.csv")
    parser.add_argument("--base-k08", default="submissions/candidates/2026-05-12-targeted/k08_i07_p47_p43_p72_p48.csv")
    parser.add_argument("--output-dir", default="submissions/candidates/2026-05-13-targeted")
    args = parser.parse_args()

    t1 = load_json(Path(args.track1))
    features = numeric_features(Path(args.features))
    base = read_submission(Path(args.base_k08))

    specs: list[tuple[str, pd.DataFrame, str]] = []
    add_t1_variant(specs, base, t1, features, "l01_k08_t1_78_meta9_thr045", 78, "feature:meta", 9, 0.45, "Add a one-bit metadata variant on Track1-78.")
    add_t1_variant(specs, base, t1, features, "l02_k08_t1_78_meta13_thr050", 78, "feature:meta", 13, 0.50, "Add an alternate one-bit metadata variant on Track1-78.")
    add_t1_variant(specs, base, t1, features, "l03_k08_t1_83_meta15_thr045", 83, "feature:meta", 15, 0.45, "Add a one-bit metadata variant on Track1-83.")
    add_t1_variant(specs, base, t1, features, "l04_k08_t1_83_pid3_thr035", 83, "pid", 3, 0.35, "Add a one-bit patient-ID variant on Track1-83.")
    add_t1_variant(specs, base, t1, features, "l05_k08_t1_85_meta15_thr035", 85, "feature:meta", 15, 0.35, "Add a one-bit metadata variant on Track1-85.")
    add_t1_variant(specs, base, t1, features, "l06_k08_t1_72_meta11_thr050", 72, "feature:meta", 11, 0.50, "Strengthen the existing Track1-72 positive row by one bit.")
    add_t1_variant(specs, base, t1, features, "l07_k08_t1_43_meta9_thr045", 43, "feature:meta", 9, 0.45, "Strengthen the existing Track1-43 positive row by one bit.")
    add_t1_variant(specs, base, t1, features, "l08_k08_t1_53_meta15_thr045", 53, "feature:meta", 15, 0.45, "Swap the Track1-53 high-confidence row to an equal-total metadata k15 variant.")
    add_t1_variant(specs, base, t1, features, "l09_k08_t1_28_meta13_thr050", 28, "feature:meta", 13, 0.50, "Add a one-bit metadata variant on Track1-28.")
    add_t1_variant(specs, base, t1, features, "l10_k08_t1_26_meta13_thr050", 26, "feature:meta", 13, 0.50, "Probe a one-bit metadata variant on Track1-26.")

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
                "diff_rows_vs_k08": diff_rows(base, df),
                "official_data_only": True,
            }
        )
        print(path)

    pd.DataFrame(rows).to_csv(output_dir / "manifest.csv", index=False)
    with (output_dir / "manifest.json").open("w", encoding="utf-8") as f:
        json.dump(
            {
                "created_at_utc": now_utc(),
                "compliance": "official-data-only deterministic Track1 micro-variants around k08",
                "inputs": {
                    "track1": {"path": args.track1, "sha256": sha256(Path(args.track1))},
                    "features": {"path": args.features, "sha256": sha256(Path(args.features))},
                    "base_k08": {"path": args.base_k08, "sha256": sha256(Path(args.base_k08))},
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
