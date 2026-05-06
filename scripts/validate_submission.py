#!/usr/bin/env python3
"""Validate a CVPR 2026 Children Challenge submission CSV."""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

import pandas as pd


TRACK1_TEST_IDS = [4, 5, 18, 26, 28, 40, 42, 43, 47, 48, 53, 54, 72, 78, 83, 85]
TRACK2_TEST_IDS = [4, 6, 7, 13, 26, 35, 39, 42, 50]
SUBTYPES = {"WNL", "type1", "type2", "type3", "type4"}
HEADER = (
    ["ID"]
    + [f"L{i}" for i in range(1, 18)]
    + [f"R{i}" for i in range(1, 18)]
    + ["Total", "Left_gait_subtype", "Right_gait_subtype"]
)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("csv_path")
    parser.add_argument("--allow-total-override", action="store_true")
    args = parser.parse_args()

    path = Path(args.csv_path)
    df = pd.read_csv(path)
    errors: list[str] = []
    warnings: list[str] = []

    if list(df.columns) != HEADER:
        errors.append("header mismatch")
    if len(df) != 25:
        errors.append(f"row count {len(df)} != 25")

    expected_ids = [f"track1-{pid}" for pid in TRACK1_TEST_IDS] + [f"track2-{pid}" for pid in TRACK2_TEST_IDS]
    if df["ID"].tolist() != expected_ids:
        errors.append("ID order/content mismatch")

    item_cols = [f"L{i}" for i in range(1, 18)] + [f"R{i}" for i in range(1, 18)]
    t1 = df.iloc[:16]
    t2 = df.iloc[16:]
    for col in item_cols:
        bad_t1 = sorted(set(t1[col].tolist()) - {0, 1})
        bad_t2 = sorted(set(t2[col].tolist()) - {-1})
        if bad_t1:
            errors.append(f"{col} Track1 non-binary values {bad_t1}")
        if bad_t2:
            errors.append(f"{col} Track2 non -1 values {bad_t2}")

    t1_subtypes = set(map(str, t1["Left_gait_subtype"].tolist())) | set(map(str, t1["Right_gait_subtype"].tolist()))
    if t1_subtypes != {"-1"}:
        errors.append("Track1 subtype columns must be -1")
    for col in ["Left_gait_subtype", "Right_gait_subtype"]:
        bad = sorted(set(map(str, t2[col].tolist())) - SUBTYPES)
        if bad:
            errors.append(f"{col} Track2 invalid labels {bad}")

    if sorted(set(t2["Total"].tolist())) != [-1]:
        errors.append("Track2 Total must be -1")
    for total in t1["Total"].tolist():
        if int(total) < 0 or int(total) > 34:
            errors.append(f"Track1 Total out of range: {total}")

    item_sums = t1[item_cols].sum(axis=1).astype(int)
    totals = t1["Total"].astype(int)
    mismatch = (item_sums != totals)
    if mismatch.any():
        msg = f"{int(mismatch.sum())} Track1 Total values differ from item sums"
        if args.allow_total_override:
            warnings.append(msg)
        else:
            errors.append(msg)

    print(f"path={path}")
    print(f"sha256={sha256(path)}")
    print(f"rows={len(df)}")
    print(f"cols={len(df.columns)}")
    print(f"header_valid={list(df.columns) == HEADER}")
    print(f"range_valid={not errors}")
    if warnings:
        print("warnings=" + " | ".join(warnings))
    if errors:
        print("errors=" + " | ".join(errors))
        return 1
    print("status=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
