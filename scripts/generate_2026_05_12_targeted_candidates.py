#!/usr/bin/env python3
"""Generate targeted official-data-only May 12 candidates.

The May 10 loop found several small positive Track1 perturbations around the
g11 anchor. This loop uses the best May 10 candidate as the anchor and tests
whether those positive one-row perturbations stack.
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


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--track1", default="data/raw/track1_train.json")
    parser.add_argument("--features", default="features/patient_light_features.csv")
    parser.add_argument("--base-i07", default="submissions/candidates/2026-05-10-targeted/i07_g11_t1_53_meta3_thr040.csv")
    parser.add_argument("--source-i02", default="submissions/candidates/2026-05-10-targeted/i02_g11_t1_47_meta13_thr040.csv")
    parser.add_argument("--source-i04", default="submissions/candidates/2026-05-10-targeted/i04_g11_t1_43_meta11_thr055.csv")
    parser.add_argument("--source-i05", default="submissions/candidates/2026-05-10-targeted/i05_g11_t1_72_meta11_thr055.csv")
    parser.add_argument("--source-i08", default="submissions/candidates/2026-05-10-targeted/i08_g11_t1_48_meta15_thr045.csv")
    parser.add_argument("--source-g11", default="submissions/candidates/2026-05-07-targeted/g11_t15_t2_42_13_all3.csv")
    parser.add_argument("--output-dir", default="submissions/candidates/2026-05-12-targeted")
    args = parser.parse_args()

    t1 = load_json(Path(args.track1))
    features = numeric_features(Path(args.features))
    base = read_submission(Path(args.base_i07))
    i02 = read_submission(Path(args.source_i02))
    i04 = read_submission(Path(args.source_i04))
    i05 = read_submission(Path(args.source_i05))
    i08 = read_submission(Path(args.source_i08))
    g11 = read_submission(Path(args.source_g11))

    row_sources = {
        "p47_i02": (i02, "track1-47"),
        "p43_i04": (i04, "track1-43"),
        "p72_i05": (i05, "track1-72"),
        "p48_i08": (i08, "track1-48"),
        "p53_g11": (g11, "track1-53"),
    }

    specs: list[tuple[str, pd.DataFrame, str]] = [
        (
            "k01_i07_p47",
            replace_rows(base, [row_sources["p47_i02"]]),
            "Add the positive i02 Track1-47 row to the i07 anchor.",
        ),
        (
            "k02_i07_p43",
            replace_rows(base, [row_sources["p43_i04"]]),
            "Add the positive i04 Track1-43 row to the i07 anchor.",
        ),
        (
            "k03_i07_p72",
            replace_rows(base, [row_sources["p72_i05"]]),
            "Add the positive i05 Track1-72 row to the i07 anchor.",
        ),
        (
            "k04_i07_p48",
            replace_rows(base, [row_sources["p48_i08"]]),
            "Add the positive i08 Track1-48 row to the i07 anchor.",
        ),
        (
            "k05_i07_p47_p43",
            replace_rows(base, [row_sources["p47_i02"], row_sources["p43_i04"]]),
            "Add i02 Track1-47 and i04 Track1-43 rows to i07.",
        ),
        (
            "k06_i07_p47_p72",
            replace_rows(base, [row_sources["p47_i02"], row_sources["p72_i05"]]),
            "Add i02 Track1-47 and i05 Track1-72 rows to i07.",
        ),
        (
            "k07_i07_p47_p48",
            replace_rows(base, [row_sources["p47_i02"], row_sources["p48_i08"]]),
            "Add i02 Track1-47 and i08 Track1-48 rows to i07.",
        ),
        (
            "k08_i07_p47_p43_p72_p48",
            replace_rows(base, [row_sources["p47_i02"], row_sources["p43_i04"], row_sources["p72_i05"], row_sources["p48_i08"]]),
            "Add all four positive non-p53 May 10 Track1 rows to i07.",
        ),
        (
            "k09_g11_t1_53_meta5_thr045",
            apply_t1_rows(g11, {53: build_t1_rows(t1, features, "feature:meta", 5, 0.45)[53]}),
            "Replace only Track1-53 on g11 with metadata k=5 threshold 0.45 to test p53 bit choice.",
        ),
        (
            "k10_g11_t1_53_meta15_thr045",
            apply_t1_rows(g11, {53: build_t1_rows(t1, features, "feature:meta", 15, 0.45)[53]}),
            "Replace only Track1-53 on g11 with metadata k=15 threshold 0.45 to test p53 bit choice.",
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
                "diff_rows_vs_i07": diff_rows(base, df),
                "official_data_only": True,
            }
        )
        print(path)

    pd.DataFrame(rows).to_csv(output_dir / "manifest.csv", index=False)
    with (output_dir / "manifest.json").open("w", encoding="utf-8") as f:
        json.dump(
            {
                "created_at_utc": now_utc(),
                "compliance": "official-data-only deterministic combinations of positive May 10 Track1 rows",
                "inputs": {
                    "track1": {"path": args.track1, "sha256": sha256(Path(args.track1))},
                    "features": {"path": args.features, "sha256": sha256(Path(args.features))},
                    "base_i07": {"path": args.base_i07, "sha256": sha256(Path(args.base_i07))},
                    "source_i02": {"path": args.source_i02, "sha256": sha256(Path(args.source_i02))},
                    "source_i04": {"path": args.source_i04, "sha256": sha256(Path(args.source_i04))},
                    "source_i05": {"path": args.source_i05, "sha256": sha256(Path(args.source_i05))},
                    "source_i08": {"path": args.source_i08, "sha256": sha256(Path(args.source_i08))},
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
