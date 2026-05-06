#!/usr/bin/env python3
"""Generate targeted official-data-only May 6 candidates.

These are single-row probes around the May 5 compliant best
of01_t1_meta11_t2_s09. They use only official train labels/features and avoid
the public-output diagnostic rows that are not award-compliant.
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


def one_t1(source_rows: dict[int, tuple[list[int], list[int]]], pid: int) -> dict[int, tuple[list[int], list[int]]]:
    return {pid: source_rows[pid]}


def one_t2(source_rows: dict[int, tuple[str, str]], pid: int) -> dict[int, tuple[str, str]]:
    return {pid: source_rows[pid]}


def combine_t1(
    source_rows: dict[int, tuple[list[int], list[int]]],
    pids: list[int],
) -> dict[int, tuple[list[int], list[int]]]:
    return {pid: source_rows[pid] for pid in pids}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--track1", default="data/raw/track1_train.json")
    parser.add_argument("--track2", default="data/raw/track2_train.json")
    parser.add_argument("--features", default="features/patient_light_features.csv")
    parser.add_argument("--base", default="submissions/candidates/2026-05-05-official/of01_t1_meta11_t2_s09.csv")
    parser.add_argument("--output-dir", default="submissions/candidates/2026-05-06-targeted")
    args = parser.parse_args()

    t1 = load_json(Path(args.track1))
    t2 = load_json(Path(args.track2))
    features = numeric_features(Path(args.features))
    base = read_submission(Path(args.base))
    output_dir = Path(args.output_dir)

    t1_meta7 = build_t1_rows(t1, features, "feature:meta", 7, 0.50)
    t1_meta9 = build_t1_rows(t1, features, "feature:meta", 9, 0.50)
    t1_meta13 = build_t1_rows(t1, features, "feature:meta", 13, 0.50)
    t1_pid5 = build_t1_rows(t1, features, "pid", 5, 0.45)
    t2_all3 = build_t2_rows(t2, features, "feature:all", 3)

    specs: list[tuple[str, pd.DataFrame, str]] = [
        (
            "t01_of01_p53_meta13",
            apply_t1_rows(base, one_t1(t1_meta13, 53)),
            "Single-row Track1 probe: track1-53 from official metadata KNN k=13; Track2 remains of01/s09.",
        ),
        (
            "t02_of01_p53_pid5",
            apply_t1_rows(base, one_t1(t1_pid5, 53)),
            "Single-row Track1 probe: track1-53 from official patient-ID KNN k=5 threshold 0.45; Track2 remains of01/s09.",
        ),
        (
            "t03_of01_p18_meta13",
            apply_t1_rows(base, one_t1(t1_meta13, 18)),
            "Single-row Track1 probe: track1-18 from official metadata KNN k=13; Track2 remains of01/s09.",
        ),
        (
            "t04_of01_p54_meta7",
            apply_t1_rows(base, one_t1(t1_meta7, 54)),
            "Single-row Track1 probe: track1-54 from official metadata KNN k=7; Track2 remains of01/s09.",
        ),
        (
            "t05_of01_p78_meta9",
            apply_t1_rows(base, one_t1(t1_meta9, 78)),
            "Single-row Track1 probe: track1-78 from official metadata KNN k=9; Track2 remains of01/s09.",
        ),
        (
            "t06_of01_p48_meta13",
            apply_t1_rows(base, one_t1(t1_meta13, 48)),
            "Single-row Track1 probe: track1-48 from official metadata KNN k=13; Track2 remains of01/s09.",
        ),
        (
            "t07_of01_t2_6_all3",
            apply_t2_rows(base, one_t2(t2_all3, 6)),
            "Single-row Track2 probe: track2-6 from official all-view KNN k=3; Track1 remains of01.",
        ),
        (
            "t08_of01_t2_42_all3",
            apply_t2_rows(base, one_t2(t2_all3, 42)),
            "Single-row Track2 probe: track2-42 from official all-view KNN k=3; Track1 remains of01.",
        ),
        (
            "t09_of01_p53_p18_meta13",
            apply_t1_rows(base, combine_t1(t1_meta13, [53, 18])),
            "Two-row Track1 probe: track1-53 and track1-18 from official metadata KNN k=13; Track2 remains of01/s09.",
        ),
        (
            "t10_of01_p53_p54_meta",
            apply_t1_rows(apply_t1_rows(base, one_t1(t1_meta13, 53)), one_t1(t1_meta7, 54)),
            "Two-row Track1 probe: track1-53 from meta13 plus track1-54 from meta7; Track2 remains of01/s09.",
        ),
        (
            "t11_of01_p48_p53_meta13",
            apply_t1_rows(base, combine_t1(t1_meta13, [48, 53])),
            "Two-row Track1 follow-up: combine the positive track1-48 and track1-53 metadata KNN k=13 rows; Track2 remains of01/s09.",
        ),
        (
            "t12_of01_p48_p54_meta",
            apply_t1_rows(apply_t1_rows(base, one_t1(t1_meta13, 48)), one_t1(t1_meta7, 54)),
            "Two-row Track1 follow-up: combine positive track1-48 meta13 and track1-54 meta7 rows; Track2 remains of01/s09.",
        ),
        (
            "t13_of01_p48_p53_p54_meta",
            apply_t1_rows(apply_t1_rows(base, combine_t1(t1_meta13, [48, 53])), one_t1(t1_meta7, 54)),
            "Three-row Track1 follow-up: combine positive p48, p53, and p54 official-feature rows; Track2 remains of01/s09.",
        ),
        (
            "t14_of01_p48_t2_6_all3",
            apply_t2_rows(apply_t1_rows(base, one_t1(t1_meta13, 48)), one_t2(t2_all3, 6)),
            "Mixed follow-up: keep positive track1-48 meta13 and test one official all-view KNN Track2 row track2-6.",
        ),
        (
            "t15_of01_p48_p53_p54_t2_6",
            apply_t2_rows(
                apply_t1_rows(apply_t1_rows(base, combine_t1(t1_meta13, [48, 53])), one_t1(t1_meta7, 54)),
                one_t2(t2_all3, 6),
            ),
            "Final adaptive probe: add official all-view KNN track2-6 row to the best p48+p53+p54 Track1 combination.",
        ),
    ]

    rows: list[dict[str, Any]] = []
    output_dir.mkdir(parents=True, exist_ok=True)
    for experiment_id, df, description in specs:
        path = output_dir / f"{experiment_id}.csv"
        df.to_csv(path, index=False, quoting=csv.QUOTE_MINIMAL, lineterminator="\r\n")
        status, errors = validate(df)
        changed = diff_rows(base, df)
        rows.append(
            {
                "created_at_utc": now_utc(),
                "experiment_id": experiment_id,
                "description": description,
                "path": str(path),
                "sha256": sha256(path),
                "validation_status": status,
                "validation_errors": errors,
                "diff_rows_vs_of01": changed,
                "official_data_only": True,
            }
        )
        print(path)

    pd.DataFrame(rows).to_csv(output_dir / "manifest.csv", index=False)
    with (output_dir / "manifest.json").open("w", encoding="utf-8") as f:
        json.dump(
            {
                "created_at_utc": now_utc(),
                "compliance": "official-data-only deterministic single-row probes around of01",
                "inputs": {
                    "track1": {"path": args.track1, "sha256": sha256(Path(args.track1))},
                    "track2": {"path": args.track2, "sha256": sha256(Path(args.track2))},
                    "features": {"path": args.features, "sha256": sha256(Path(args.features))},
                    "base": {"path": args.base, "sha256": sha256(Path(args.base))},
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
