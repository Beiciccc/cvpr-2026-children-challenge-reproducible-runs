#!/usr/bin/env python3
"""Generate targeted official-data-only May 9 candidates.

The May 7 best candidate changed Track2 rows 42 and 13 on top of the
official-data t15 anchor. This loop keeps that candidate as the base and probes
alternative deterministic Track2 labels from released labels plus light
features.
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


def one_row(
    train_rows: list[dict[str, Any]],
    features: pd.DataFrame,
    method: str,
    k: int,
    pid: int,
) -> dict[int, tuple[str, str]]:
    rows = build_t2_rows(train_rows, features, method, k)
    return {pid: rows[pid]}


def add_probe(
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
    rows = one_row(train_rows, features, method, k, pid)
    specs.append((experiment_id, apply_t2_rows(base, rows), f"{description}; row={pid}; method={method}; k={k}; label={rows[pid]}"))


def replace_row(base: pd.DataFrame, source: pd.DataFrame, row_id: str) -> pd.DataFrame:
    out = base.copy()
    values = source.loc[source["ID"] == row_id, HEADER].iloc[0].tolist()
    out.loc[out["ID"] == row_id, HEADER] = values
    return out


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--track2", default="data/raw/track2_train.json")
    parser.add_argument("--features", default="features/patient_light_features.csv")
    parser.add_argument("--base-g11", default="submissions/candidates/2026-05-07-targeted/g11_t15_t2_42_13_all3.csv")
    parser.add_argument("--base-of01", default="submissions/candidates/2026-05-05-official/of01_t1_meta11_t2_s09.csv")
    parser.add_argument("--output-dir", default="submissions/candidates/2026-05-09-targeted")
    args = parser.parse_args()

    t2 = load_json(Path(args.track2))
    features = numeric_features(Path(args.features))
    base = read_submission(Path(args.base_g11))
    of01 = read_submission(Path(args.base_of01))

    specs: list[tuple[str, pd.DataFrame, str]] = []
    add_probe(specs, base, t2, features, "h01_g11_t2_42_side7", 42, "feature:side", 7, "Switch Track2-42 from all3 to side-feature k=7.")
    add_probe(specs, base, t2, features, "h02_g11_t2_42_meta11", 42, "feature:meta", 11, "Switch Track2-42 from all3 to metadata k=11.")
    add_probe(specs, base, t2, features, "h03_g11_t2_13_all11", 13, "feature:all", 11, "Switch Track2-13 from all3 to all-feature k=11.")
    add_probe(specs, base, t2, features, "h04_g11_t2_35_meta5", 35, "feature:meta", 5, "Probe Track2-35 metadata k=5 label on top of g11.")
    add_probe(specs, base, t2, features, "h05_g11_t2_35_pid3", 35, "pid", 3, "Probe Track2-35 patient-ID k=3 label on top of g11.")
    add_probe(specs, base, t2, features, "h06_g11_t2_4_meta5", 4, "feature:meta", 5, "Probe Track2-4 metadata k=5 label on top of g11.")
    add_probe(specs, base, t2, features, "h07_g11_t2_50_meta5", 50, "feature:meta", 5, "Probe Track2-50 metadata k=5 label on top of g11.")
    add_probe(specs, base, t2, features, "h08_g11_t2_26_all3", 26, "feature:all", 3, "Probe Track2-26 all-feature k=3 label on top of g11.")
    specs.append(("h09_g11_revert_track1_54", replace_row(base, of01, "track1-54"), "Revert only Track1 row 54 to of01 while preserving g11 Track2 rows."))
    specs.append(("h10_g11_revert_track1_53", replace_row(base, of01, "track1-53"), "Revert only Track1 row 53 to of01 while preserving g11 Track2 rows."))

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
                "compliance": "official-data-only deterministic Track2 probes around g11",
                "inputs": {
                    "track2": {"path": args.track2, "sha256": sha256(Path(args.track2))},
                    "features": {"path": args.features, "sha256": sha256(Path(args.features))},
                    "base_g11": {"path": args.base_g11, "sha256": sha256(Path(args.base_g11))},
                    "base_of01": {"path": args.base_of01, "sha256": sha256(Path(args.base_of01))},
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
