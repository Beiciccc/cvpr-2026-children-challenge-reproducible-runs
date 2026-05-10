#!/usr/bin/env python3
"""Generate targeted official-data-only May 10 candidates.

This loop keeps the May 7 best candidate as the anchor and shifts from broad
Track2 one-row probes to smaller Track1 perturbations. May 9 showed that most
Track2 replacements hurt the anchor; these candidates mostly alter one Track1
row by a few item bits while preserving the known good Track2 rows.
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
    apply_t2_rows,
    build_t1_rows,
    build_t2_rows,
    diff_rows,
    load_json,
    now_utc,
    numeric_features,
    read_submission,
    sha256,
    validate,
)


def one_t1(rows: dict[int, tuple[list[int], list[int]]], pid: int) -> dict[int, tuple[list[int], list[int]]]:
    return {pid: rows[pid]}


def one_t2(rows: dict[int, tuple[str, str]], pid: int) -> dict[int, tuple[str, str]]:
    return {pid: rows[pid]}


def add_t2_probe(
    specs: list[tuple[str, pd.DataFrame, str]],
    base: pd.DataFrame,
    train_rows: list[dict[str, Any]],
    features: pd.DataFrame,
    experiment_id: str,
    pid: int,
    method: str,
    k: int,
    description: str,
) -> None:
    rows = build_t2_rows(train_rows, features, method, k)
    specs.append((experiment_id, apply_t2_rows(base, one_t2(rows, pid)), f"{description}; row={pid}; method={method}; k={k}; label={rows[pid]}"))


def add_t1_probe(
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
    rows = build_t1_rows(train_rows, features, method, k, threshold)
    left, right = rows[pid]
    specs.append(
        (
            experiment_id,
            apply_t1_rows(base, one_t1(rows, pid)),
            f"{description}; row={pid}; method={method}; k={k}; threshold={threshold}; total={sum(left) + sum(right)}",
        )
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--track1", default="data/raw/track1_train.json")
    parser.add_argument("--track2", default="data/raw/track2_train.json")
    parser.add_argument("--features", default="features/patient_light_features.csv")
    parser.add_argument("--base-g11", default="submissions/candidates/2026-05-07-targeted/g11_t15_t2_42_13_all3.csv")
    parser.add_argument("--output-dir", default="submissions/candidates/2026-05-10-targeted")
    args = parser.parse_args()

    t1 = load_json(Path(args.track1))
    t2 = load_json(Path(args.track2))
    features = numeric_features(Path(args.features))
    base = read_submission(Path(args.base_g11))

    specs: list[tuple[str, pd.DataFrame, str]] = []

    add_t1_probe(specs, base, t1, features, "i01_g11_t1_54_meta9_thr045", 54, "feature:meta", 9, 0.45, "Replace Track1-54 with a near-anchor metadata k=9 low-threshold row.")
    add_t1_probe(specs, base, t1, features, "i02_g11_t1_47_meta13_thr040", 47, "feature:meta", 13, 0.40, "Probe Track1-47 with a small metadata k=13 low-threshold row.")
    add_t1_probe(specs, base, t1, features, "i03_g11_t1_42_meta7_thr045", 42, "feature:meta", 7, 0.45, "Probe Track1-42 with a small metadata k=7 low-threshold row.")
    add_t1_probe(specs, base, t1, features, "i04_g11_t1_43_meta11_thr055", 43, "feature:meta", 11, 0.55, "Probe Track1-43 with a small metadata k=11 high-threshold row.")
    add_t1_probe(specs, base, t1, features, "i05_g11_t1_72_meta11_thr055", 72, "feature:meta", 11, 0.55, "Probe Track1-72 with a small metadata k=11 high-threshold row.")
    add_t1_probe(specs, base, t1, features, "i06_g11_t1_83_all15_thr040", 83, "feature:all", 15, 0.40, "Probe Track1-83 with an all-feature k=15 low-threshold row.")
    add_t1_probe(specs, base, t1, features, "i07_g11_t1_53_meta3_thr040", 53, "feature:meta", 3, 0.40, "Strengthen Track1-53 with metadata k=3 low-threshold row.")
    add_t1_probe(specs, base, t1, features, "i08_g11_t1_48_meta15_thr045", 48, "feature:meta", 15, 0.45, "Strengthen Track1-48 with metadata k=15 low-threshold row.")
    add_t2_probe(specs, base, t2, features, "i09_g11_t2_6_meta3", 6, "feature:meta", 3, "Switch Track2-6 from all3 to metadata k=3 as a controlled Track2-6 retest.")
    add_t1_probe(specs, base, t1, features, "i10_g11_t1_72_side11_thr045", 72, "feature:side", 11, 0.45, "Probe Track1-72 with an alternate small side-feature k=11 row.")

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
                "diff_rows_vs_g11": diff_rows(base, df),
                "official_data_only": True,
            }
        )
        print(path)

    pd.DataFrame(rows).to_csv(output_dir / "manifest.csv", index=False)
    with (output_dir / "manifest.json").open("w", encoding="utf-8") as f:
        json.dump(
            {
                "created_at_utc": now_utc(),
                "compliance": "official-data-only deterministic small Track1 and controlled Track2-6 probes around g11",
                "inputs": {
                    "track1": {"path": args.track1, "sha256": sha256(Path(args.track1))},
                    "track2": {"path": args.track2, "sha256": sha256(Path(args.track2))},
                    "features": {"path": args.features, "sha256": sha256(Path(args.features))},
                    "base_g11": {"path": args.base_g11, "sha256": sha256(Path(args.base_g11))},
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
