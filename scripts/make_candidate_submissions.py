#!/usr/bin/env python3
"""Generate deterministic label-only submission candidates.

These candidates are intentionally simple and reproducible. They are useful
as leaderboard anchors before heavier keypoint models finish.
"""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path
from typing import Any


TRACK1_TEST_IDS = [4, 5, 18, 26, 28, 40, 42, 43, 47, 48, 53, 54, 72, 78, 83, 85]
TRACK2_TEST_IDS = [4, 6, 7, 13, 26, 35, 39, 42, 50]
ITEMS = [str(i) for i in range(1, 18)]
SUBTYPES = ["WNL", "type1", "type2", "type3", "type4"]


def load_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def mode(values: list[Any]) -> Any:
    counts = Counter(values)
    return sorted(counts.items(), key=lambda kv: (-kv[1], str(kv[0])))[0][0]


def track1_modes(rows: list[dict[str, Any]]) -> dict[str, dict[str, int]]:
    out: dict[str, dict[str, int]] = {"left": {}, "right": {}}
    for limb in ("left", "right"):
        for item in ITEMS:
            out[limb][item] = int(mode([r[limb][item] for r in rows]))
    return out


def track2_modes(rows: list[dict[str, Any]]) -> dict[str, str]:
    return {
        limb: str(mode([r[limb]["gait_subtype"] for r in rows]))
        for limb in ("left", "right")
    }


def nearest_row(rows: list[dict[str, Any]], pid: int) -> dict[str, Any]:
    return min(rows, key=lambda r: (abs(r["patient_id"] - pid), r["patient_id"]))


def window_rows(rows: list[dict[str, Any]], pid: int, k: int) -> list[dict[str, Any]]:
    return sorted(rows, key=lambda r: (abs(r["patient_id"] - pid), r["patient_id"]))[:k]


def track1_pred(kind: str, rows: list[dict[str, Any]], pid: int) -> tuple[list[int], list[int]]:
    modes = track1_modes(rows)
    if kind == "majority":
        left = [modes["left"][item] for item in ITEMS]
        right = [modes["right"][item] for item in ITEMS]
    elif kind == "zero":
        left = [0] * 17
        right = [0] * 17
    elif kind == "one":
        left = [1] * 17
        right = [1] * 17
    elif kind == "nearest":
        row = nearest_row(rows, pid)
        left = [int(row["left"][item]) for item in ITEMS]
        right = [int(row["right"][item]) for item in ITEMS]
    elif kind.startswith("knn"):
        k = int(kind[3:])
        near = window_rows(rows, pid, k)
        left = [int(mode([r["left"][item] for r in near])) for item in ITEMS]
        right = [int(mode([r["right"][item] for r in near])) for item in ITEMS]
    elif kind == "meanprob":
        left = []
        right = []
        for limb, target in [("left", left), ("right", right)]:
            for item in ITEMS:
                p = sum(r[limb][item] for r in rows) / len(rows)
                target.append(int(p >= 0.45))
    else:
        raise ValueError(kind)
    return left, right


def track2_pred(kind: str, rows: list[dict[str, Any]], pid: int) -> tuple[str, str]:
    modes = track2_modes(rows)
    if kind == "majority":
        return modes["left"], modes["right"]
    if kind == "type3":
        return "type3", "type3"
    if kind == "type2":
        return "type2", "type2"
    if kind == "type2type3":
        return "type2", "type3"
    if kind == "nearest":
        row = nearest_row(rows, pid)
        return str(row["left"]["gait_subtype"]), str(row["right"]["gait_subtype"])
    if kind.startswith("knn"):
        k = int(kind[3:])
        near = window_rows(rows, pid, k)
        return (
            str(mode([r["left"]["gait_subtype"] for r in near])),
            str(mode([r["right"]["gait_subtype"] for r in near])),
        )
    raise ValueError(kind)


def write_submission(
    path: Path,
    track1: list[dict[str, Any]],
    track2: list[dict[str, Any]],
    t1_kind: str,
    t2_kind: str,
) -> None:
    header = (
        ["ID"]
        + [f"L{i}" for i in range(1, 18)]
        + [f"R{i}" for i in range(1, 18)]
        + ["Total", "Left_gait_subtype", "Right_gait_subtype"]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        for pid in sorted(TRACK1_TEST_IDS):
            left, right = track1_pred(t1_kind, track1, pid)
            writer.writerow([f"track1-{pid}", *left, *right, sum(left) + sum(right), -1, -1])
        for pid in sorted(TRACK2_TEST_IDS):
            left_label, right_label = track2_pred(t2_kind, track2, pid)
            if left_label not in SUBTYPES or right_label not in SUBTYPES:
                raise ValueError((left_label, right_label))
            writer.writerow([f"track2-{pid}", *([-1] * 35), left_label, right_label])


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", default="data/raw")
    parser.add_argument("--output-dir", default="submissions/candidates")
    args = parser.parse_args()

    data_dir = Path(args.data_dir)
    out_dir = Path(args.output_dir)
    t1 = load_json(data_dir / "track1_train.json")
    t2 = load_json(data_dir / "track2_train.json")

    specs = [
        ("s02_zero_t1_modes_t2", "zero", "majority"),
        ("s03_nearest_id", "nearest", "nearest"),
        ("s04_knn3_id", "knn3", "knn3"),
        ("s05_knn5_id", "knn5", "knn5"),
        ("s06_majority_t2_type3", "majority", "type3"),
        ("s07_nearest_t1_majority_t2", "nearest", "majority"),
        ("s08_knn3_t1_majority_t2", "knn3", "majority"),
        ("s09_meanprob45_t1_majority_t2", "meanprob", "majority"),
        ("s10_majority_t1_nearest_t2", "majority", "nearest"),
    ]
    for name, t1_kind, t2_kind in specs:
        path = out_dir / f"{name}.csv"
        write_submission(path, t1, t2, t1_kind, t2_kind)
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

