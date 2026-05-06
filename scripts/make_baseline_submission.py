#!/usr/bin/env python3
"""Create a majority-label baseline submission CSV."""

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
SUBTYPE_LABELS = {"type1", "type2", "type3", "type4", "WNL"}


def load_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def mode(values: list[Any]) -> Any:
    counts = Counter(values)
    return sorted(counts.items(), key=lambda kv: (-kv[1], str(kv[0])))[0][0]


def build_track1_modes(rows: list[dict[str, Any]]) -> dict[str, dict[str, int]]:
    modes: dict[str, dict[str, int]] = {"left": {}, "right": {}}
    for limb in ("left", "right"):
        for item in ITEMS:
            modes[limb][item] = int(mode([row[limb][item] for row in rows]))
    return modes


def build_track2_modes(rows: list[dict[str, Any]]) -> dict[str, str]:
    modes: dict[str, str] = {}
    for limb in ("left", "right"):
        pred = str(mode([row[limb]["gait_subtype"] for row in rows]))
        if pred not in SUBTYPE_LABELS:
            raise ValueError(f"Unexpected subtype label: {pred}")
        modes[limb] = pred
    return modes


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", default="data/raw")
    parser.add_argument("--output", default="submissions/baseline_majority.csv")
    args = parser.parse_args()

    data_dir = Path(args.data_dir)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)

    track1 = load_json(data_dir / "track1_train.json")
    track2 = load_json(data_dir / "track2_train.json")
    track1_modes = build_track1_modes(track1)
    track2_modes = build_track2_modes(track2)

    header = (
        ["ID"]
        + [f"L{i}" for i in range(1, 18)]
        + [f"R{i}" for i in range(1, 18)]
        + ["Total", "Left_gait_subtype", "Right_gait_subtype"]
    )

    with output.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(header)

        for pid in sorted(TRACK1_TEST_IDS):
            left = [track1_modes["left"][item] for item in ITEMS]
            right = [track1_modes["right"][item] for item in ITEMS]
            total = sum(left) + sum(right)
            writer.writerow([f"track1-{pid}", *left, *right, total, -1, -1])

        for pid in sorted(TRACK2_TEST_IDS):
            writer.writerow(
                [
                    f"track2-{pid}",
                    *([-1] * 34),
                    -1,
                    track2_modes["left"],
                    track2_modes["right"],
                ]
            )

    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

