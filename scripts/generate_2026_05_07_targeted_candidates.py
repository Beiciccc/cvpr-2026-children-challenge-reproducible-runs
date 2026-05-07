#!/usr/bin/env python3
"""Generate targeted official-data-only May 7 candidates.

These candidates continue from the May 6 official-data best:
t15_of01_p48_p53_p54_t2_6. The focus is Track2 all-view KNN single-row and
combination probes, plus checks of the Track2-6 row against smaller positive
Track1 combinations.
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
    apply_t2_rows,
    build_t2_rows,
    diff_rows,
    load_json,
    now_utc,
    numeric_features,
    read_submission,
    sha256,
    validate,
)


def subset_t2(rows: dict[int, tuple[str, str]], pids: list[int]) -> dict[int, tuple[str, str]]:
    return {pid: rows[pid] for pid in pids}


def add_t2(
    specs: list[tuple[str, pd.DataFrame, str]],
    base: pd.DataFrame,
    rows: dict[int, tuple[str, str]],
    experiment_id: str,
    pids: list[int],
    description: str,
) -> None:
    specs.append((experiment_id, apply_t2_rows(base, subset_t2(rows, pids)), description))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--track2", default="data/raw/track2_train.json")
    parser.add_argument("--features", default="features/patient_light_features.csv")
    parser.add_argument("--base-t15", default="submissions/candidates/2026-05-06-targeted/t15_of01_p48_p53_p54_t2_6.csv")
    parser.add_argument("--base-t13", default="submissions/candidates/2026-05-06-targeted/t13_of01_p48_p53_p54_meta.csv")
    parser.add_argument("--base-t11", default="submissions/candidates/2026-05-06-targeted/t11_of01_p48_p53_meta13.csv")
    parser.add_argument("--base-t12", default="submissions/candidates/2026-05-06-targeted/t12_of01_p48_p54_meta.csv")
    parser.add_argument("--base-t06", default="submissions/candidates/2026-05-06-targeted/t06_of01_p48_meta13.csv")
    parser.add_argument("--base-t01", default="submissions/candidates/2026-05-06-targeted/t01_of01_p53_meta13.csv")
    parser.add_argument("--output-dir", default="submissions/candidates/2026-05-07-targeted")
    args = parser.parse_args()

    t2 = load_json(Path(args.track2))
    features = numeric_features(Path(args.features))
    t2_all3 = build_t2_rows(t2, features, "feature:all", 3)
    bases = {
        "t15": read_submission(Path(args.base_t15)),
        "t13": read_submission(Path(args.base_t13)),
        "t11": read_submission(Path(args.base_t11)),
        "t12": read_submission(Path(args.base_t12)),
        "t06": read_submission(Path(args.base_t06)),
        "t01": read_submission(Path(args.base_t01)),
    }

    specs: list[tuple[str, pd.DataFrame, str]] = []
    add_t2(specs, bases["t15"], t2_all3, "g01_t15_t2_42_all3", [42], "Add official Track2 all-view KNN k=3 row track2-42 to t15.")
    add_t2(specs, bases["t15"], t2_all3, "g02_t15_t2_13_all3", [13], "Add official Track2 all-view KNN k=3 row track2-13 to t15.")
    add_t2(specs, bases["t15"], t2_all3, "g03_t15_t2_35_all3", [35], "Add official Track2 all-view KNN k=3 row track2-35 to t15.")
    add_t2(specs, bases["t15"], t2_all3, "g04_t15_t2_7_all3", [7], "Add official Track2 all-view KNN k=3 row track2-7 to t15.")
    add_t2(specs, bases["t15"], t2_all3, "g05_t15_t2_26_all3", [26], "Add official Track2 all-view KNN k=3 row track2-26 to t15.")
    add_t2(specs, bases["t15"], t2_all3, "g06_t15_t2_39_all3", [39], "Add official Track2 all-view KNN k=3 row track2-39 to t15.")
    add_t2(specs, bases["t11"], t2_all3, "g07_t11_t2_6_all3", [6], "Add track2-6 all-view KNN row to p48+p53 Track1 base, leaving p54 out.")
    add_t2(specs, bases["t12"], t2_all3, "g08_t12_t2_6_all3", [6], "Add track2-6 all-view KNN row to p48+p54 Track1 base, leaving p53 out.")
    add_t2(specs, bases["t06"], t2_all3, "g09_t06_t2_6_all3", [6], "Add track2-6 all-view KNN row to p48-only Track1 base.")
    add_t2(specs, bases["t01"], t2_all3, "g10_t01_t2_6_all3", [6], "Add track2-6 all-view KNN row to p53-only Track1 base.")
    add_t2(specs, bases["t15"], t2_all3, "g11_t15_t2_42_13_all3", [42, 13], "Add track2-42 and track2-13 all-view KNN rows to t15.")
    add_t2(specs, bases["t15"], t2_all3, "g12_t15_t2_42_35_all3", [42, 35], "Add track2-42 and track2-35 all-view KNN rows to t15.")
    add_t2(specs, bases["t15"], t2_all3, "g13_t15_t2_42_7_all3", [42, 7], "Add track2-42 and track2-7 all-view KNN rows to t15.")
    add_t2(specs, bases["t15"], t2_all3, "g14_t15_t2_13_35_all3", [13, 35], "Add track2-13 and track2-35 all-view KNN rows to t15.")
    add_t2(specs, bases["t15"], t2_all3, "g15_t15_t2_42_13_35_all3", [42, 13, 35], "Add track2-42, track2-13, and track2-35 all-view KNN rows to t15.")
    add_t2(specs, bases["t11"], t2_all3, "g16_t11_t2_42_13_all3", [42, 13], "Add track2-42 and track2-13 all-view KNN rows to p48+p53 Track1 base.")
    add_t2(specs, bases["t12"], t2_all3, "g17_t12_t2_42_13_all3", [42, 13], "Add track2-42 and track2-13 all-view KNN rows to p48+p54 Track1 base.")

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, Any]] = []
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
                "diff_rows_vs_t15": diff_rows(bases["t15"], df),
                "official_data_only": True,
            }
        )
        print(path)

    pd.DataFrame(rows).to_csv(output_dir / "manifest.csv", index=False)
    with (output_dir / "manifest.json").open("w", encoding="utf-8") as f:
        json.dump(
            {
                "created_at_utc": now_utc(),
                "compliance": "official-data-only deterministic Track2 probes around t15",
                "inputs": {
                    "track2": {"path": args.track2, "sha256": sha256(Path(args.track2))},
                    "features": {"path": args.features, "sha256": sha256(Path(args.features))},
                    "base_t15": {"path": args.base_t15, "sha256": sha256(Path(args.base_t15))},
                    "base_t13": {"path": args.base_t13, "sha256": sha256(Path(args.base_t13))},
                    "base_t11": {"path": args.base_t11, "sha256": sha256(Path(args.base_t11))},
                    "base_t12": {"path": args.base_t12, "sha256": sha256(Path(args.base_t12))},
                    "base_t06": {"path": args.base_t06, "sha256": sha256(Path(args.base_t06))},
                    "base_t01": {"path": args.base_t01, "sha256": sha256(Path(args.base_t01))},
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
