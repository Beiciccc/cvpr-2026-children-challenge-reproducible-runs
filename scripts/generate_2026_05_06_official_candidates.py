#!/usr/bin/env python3
"""Generate official-data-only May 6 candidate submissions.

The candidates continue from the May 5 compliant best:
Track1 metadata KNN k=11 plus the s09 Track2 anchor. Public feedback showed
Track2 metadata KNN was harmful, so this script keeps Track2 fixed and tests
Track1 threshold, neighbor-count, and feature-family variants.
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any

import pandas as pd

from generate_2026_05_05_official_candidates import (
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


def add_candidate(
    specs: list[tuple[str, pd.DataFrame, str]],
    s09: pd.DataFrame,
    t1_rows: list[dict[str, Any]],
    features: pd.DataFrame,
    experiment_id: str,
    method: str,
    k: int,
    threshold: float,
    description: str,
) -> None:
    rows = build_t1_rows(t1_rows, features, method, k, threshold)
    specs.append((experiment_id, apply_t1_rows(s09, rows), description))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--track1", default="data/raw/track1_train.json")
    parser.add_argument("--track2", default="data/raw/track2_train.json")
    parser.add_argument("--features", default="features/patient_light_features.csv")
    parser.add_argument("--s09", default="submissions/candidates/s09_t1_id_t2_feature_nopid.csv")
    parser.add_argument("--output-dir", default="submissions/candidates/2026-05-06-official")
    args = parser.parse_args()

    t1 = load_json(Path(args.track1))
    track2_path = Path(args.track2)
    features = numeric_features(Path(args.features))
    s09 = read_submission(Path(args.s09))
    output_dir = Path(args.output_dir)

    specs: list[tuple[str, pd.DataFrame, str]] = []
    add_candidate(
        specs,
        s09,
        t1,
        features,
        "d01_t1_meta11_thr045_t2_s09",
        "feature:meta",
        11,
        0.45,
        "Track1 metadata KNN k=11 with lower positive threshold 0.45; Track2 s09 anchor.",
    )
    add_candidate(
        specs,
        s09,
        t1,
        features,
        "d02_t1_meta11_thr055_t2_s09",
        "feature:meta",
        11,
        0.55,
        "Track1 metadata KNN k=11 with stricter positive threshold 0.55; Track2 s09 anchor.",
    )
    add_candidate(
        specs,
        s09,
        t1,
        features,
        "d03_t1_meta11_thr036_t2_s09",
        "feature:meta",
        11,
        0.36,
        "Track1 metadata KNN k=11 with low positive threshold 0.36; Track2 s09 anchor.",
    )
    add_candidate(
        specs,
        s09,
        t1,
        features,
        "d04_t1_meta11_thr064_t2_s09",
        "feature:meta",
        11,
        0.64,
        "Track1 metadata KNN k=11 with high positive threshold 0.64; Track2 s09 anchor.",
    )
    add_candidate(
        specs,
        s09,
        t1,
        features,
        "d05_t1_meta7_thr050_t2_s09",
        "feature:meta",
        7,
        0.50,
        "Track1 metadata KNN k=7 at majority threshold; Track2 s09 anchor.",
    )
    add_candidate(
        specs,
        s09,
        t1,
        features,
        "d06_t1_meta7_thr043_t2_s09",
        "feature:meta",
        7,
        0.43,
        "Track1 metadata KNN k=7 with lower threshold admitting 3/7 positives; Track2 s09 anchor.",
    )
    add_candidate(
        specs,
        s09,
        t1,
        features,
        "d07_t1_meta13_thr045_t2_s09",
        "feature:meta",
        13,
        0.45,
        "Track1 metadata KNN k=13 with lower threshold admitting 6/13 positives; Track2 s09 anchor.",
    )
    add_candidate(
        specs,
        s09,
        t1,
        features,
        "d08_t1_side11_thr050_t2_s09",
        "feature:side",
        11,
        0.50,
        "Track1 side-specific light-feature KNN k=11; Track2 s09 anchor.",
    )
    add_candidate(
        specs,
        s09,
        t1,
        features,
        "d09_t1_all11_thr050_t2_s09",
        "feature:all",
        11,
        0.50,
        "Track1 all-view light-feature KNN k=11; Track2 s09 anchor.",
    )
    add_candidate(
        specs,
        s09,
        t1,
        features,
        "d10_t1_full11_thr050_t2_s09",
        "feature:full",
        11,
        0.50,
        "Track1 full light-feature KNN k=11; Track2 s09 anchor.",
    )

    rows: list[dict[str, Any]] = []
    output_dir.mkdir(parents=True, exist_ok=True)
    for experiment_id, df, description in specs:
        path = output_dir / f"{experiment_id}.csv"
        df.to_csv(path, index=False, quoting=csv.QUOTE_MINIMAL, lineterminator="\r\n")
        status, errors = validate(df)
        rows.append(
            {
                "created_at_utc": now_utc(),
                "experiment_id": experiment_id,
                "description": description,
                "path": str(path),
                "sha256": sha256(path),
                "validation_status": status,
                "validation_errors": errors,
                "diff_rows_vs_s09": diff_rows(s09, df),
                "official_data_only": True,
            }
        )
        print(path)

    pd.DataFrame(rows).to_csv(output_dir / "manifest.csv", index=False)
    with (output_dir / "manifest.json").open("w", encoding="utf-8") as f:
        json.dump(
            {
                "created_at_utc": now_utc(),
                "compliance": "official-data-only deterministic light-feature candidates",
                "rationale": "Track2 stays at s09 because May 5 isolated Track2 metadata KNN scored 0.42915.",
                "inputs": {
                    "track1": {"path": args.track1, "sha256": sha256(Path(args.track1))},
                    "track2": {"path": args.track2, "sha256": sha256(track2_path)},
                    "features": {"path": args.features, "sha256": sha256(Path(args.features))},
                    "s09_anchor": {"path": args.s09, "sha256": sha256(Path(args.s09))},
                },
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
