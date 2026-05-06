#!/usr/bin/env python3
"""Generate official-data-only May 5 candidate submissions.

These candidates use only the released train labels and patient-level light
features extracted from the official keypoint dataset. The prior s09 CSV is
used only as an official-data reproducible anchor for one track at a time.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler


TRACK1_TEST_IDS = [4, 5, 18, 26, 28, 40, 42, 43, 47, 48, 53, 54, 72, 78, 83, 85]
TRACK2_TEST_IDS = [4, 6, 7, 13, 26, 35, 39, 42, 50]
ITEMS = [str(i) for i in range(1, 18)]
SUBTYPES = {"WNL", "type1", "type2", "type3", "type4"}
HEADER = (
    ["ID"]
    + [f"L{i}" for i in range(1, 18)]
    + [f"R{i}" for i in range(1, 18)]
    + ["Total", "Left_gait_subtype", "Right_gait_subtype"]
)


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def stable_mode(values: list[Any]) -> Any:
    counts = Counter(values)
    return sorted(counts.items(), key=lambda kv: (-kv[1], str(kv[0])))[0][0]


def read_submission(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    if list(df.columns) != HEADER:
        raise ValueError(f"unexpected header in {path}")
    return df


def numeric_features(path: Path) -> pd.DataFrame:
    frame = pd.read_csv(path).set_index("patient_id")
    frame = frame.drop(columns=[c for c in ["patient_dir"] if c in frame.columns])
    return frame.apply(pd.to_numeric, errors="coerce")


def feature_cols(features: pd.DataFrame, family: str) -> list[str]:
    if family == "meta":
        return [
            c
            for c in features.columns
            if c in {"n_sequences", "n_frames"} or c.endswith("_n_sequences") or c.endswith("_n_frames")
        ]
    if family == "all":
        return [c for c in features.columns if c.startswith("all_") or c in {"n_sequences", "n_frames"}]
    if family == "side":
        return [
            c
            for c in features.columns
            if c.startswith("left_")
            or c.startswith("right_")
            or c in {"left_n_sequences", "right_n_sequences", "left_n_frames", "right_n_frames", "n_sequences", "n_frames"}
        ]
    if family == "full":
        return list(features.columns)
    raise ValueError(family)


def nearest_feature_ids(
    features: pd.DataFrame,
    train_ids: list[int],
    test_ids: list[int],
    family: str,
    k: int,
) -> dict[int, list[int]]:
    cols = feature_cols(features, family)
    x_train = features.loc[train_ids, cols]
    imp = SimpleImputer(strategy="median")
    scaler = StandardScaler()
    train_z = scaler.fit_transform(imp.fit_transform(x_train))
    out: dict[int, list[int]] = {}
    for pid in test_ids:
        test_z = scaler.transform(imp.transform(features.loc[[pid], cols]))[0]
        dist = np.sqrt(np.mean((train_z - test_z) ** 2, axis=1))
        order = np.argsort(dist)[: min(k, len(train_ids))]
        out[pid] = [train_ids[int(i)] for i in order]
    return out


def nearest_id_ids(train_ids: list[int], pid: int, k: int) -> list[int]:
    return sorted(train_ids, key=lambda x: (abs(x - pid), x))[:k]


def build_t1_rows(
    train_rows: list[dict[str, Any]],
    features: pd.DataFrame,
    method: str,
    k: int,
    threshold: float,
) -> dict[int, tuple[list[int], list[int]]]:
    by_id = {int(r["patient_id"]): r for r in train_rows}
    train_ids = sorted(by_id)
    if method.startswith("feature:"):
        family = method.split(":", 1)[1]
        neighbors = nearest_feature_ids(features, train_ids, TRACK1_TEST_IDS, family, k)
    elif method == "pid":
        neighbors = {pid: nearest_id_ids(train_ids, pid, k) for pid in TRACK1_TEST_IDS}
    elif method == "majority":
        neighbors = {pid: train_ids for pid in TRACK1_TEST_IDS}
    else:
        raise ValueError(method)

    out: dict[int, tuple[list[int], list[int]]] = {}
    for pid in TRACK1_TEST_IDS:
        near = [by_id[src] for src in neighbors[pid]]
        left = []
        right = []
        for limb, target in [("left", left), ("right", right)]:
            for item in ITEMS:
                p = float(np.mean([int(r[limb][item]) for r in near]))
                target.append(int(p >= threshold))
        out[pid] = (left, right)
    return out


def build_t2_rows(
    train_rows: list[dict[str, Any]],
    features: pd.DataFrame,
    method: str,
    k: int,
) -> dict[int, tuple[str, str]]:
    by_id = {int(r["patient_id"]): r for r in train_rows}
    train_ids = sorted(by_id)
    if method.startswith("feature:"):
        family = method.split(":", 1)[1]
        neighbors = nearest_feature_ids(features, train_ids, TRACK2_TEST_IDS, family, k)
    elif method == "pid":
        neighbors = {pid: nearest_id_ids(train_ids, pid, k) for pid in TRACK2_TEST_IDS}
    elif method == "majority":
        neighbors = {pid: train_ids for pid in TRACK2_TEST_IDS}
    else:
        raise ValueError(method)

    out: dict[int, tuple[str, str]] = {}
    for pid in TRACK2_TEST_IDS:
        near = [by_id[src] for src in neighbors[pid]]
        left = str(stable_mode([r["left"]["gait_subtype"] for r in near]))
        right = str(stable_mode([r["right"]["gait_subtype"] for r in near]))
        out[pid] = (left, right)
    return out


def apply_t1_rows(df: pd.DataFrame, rows: dict[int, tuple[list[int], list[int]]]) -> pd.DataFrame:
    out = df.copy()
    for pid, (left, right) in rows.items():
        values = [f"track1-{pid}", *left, *right, int(sum(left) + sum(right)), -1, -1]
        out.loc[out["ID"] == f"track1-{pid}", HEADER] = values
    return out


def apply_t2_rows(df: pd.DataFrame, rows: dict[int, tuple[str, str]]) -> pd.DataFrame:
    out = df.copy()
    for pid, (left, right) in rows.items():
        if left not in SUBTYPES or right not in SUBTYPES:
            raise ValueError((pid, left, right))
        values = [f"track2-{pid}", *([-1] * 35), left, right]
        out.loc[out["ID"] == f"track2-{pid}", HEADER] = values
    return out


def validate(df: pd.DataFrame) -> tuple[str, str]:
    errors: list[str] = []
    expected_ids = [f"track1-{pid}" for pid in TRACK1_TEST_IDS] + [f"track2-{pid}" for pid in TRACK2_TEST_IDS]
    if list(df.columns) != HEADER:
        errors.append("header mismatch")
    if df["ID"].tolist() != expected_ids:
        errors.append("ID order/content mismatch")
    if len(df) != 25:
        errors.append(f"row count {len(df)} != 25")
    item_cols = [f"L{i}" for i in range(1, 18)] + [f"R{i}" for i in range(1, 18)]
    t1 = df.iloc[:16]
    t2 = df.iloc[16:]
    for col in item_cols:
        if sorted(set(t1[col].tolist()) - {0, 1}):
            errors.append(f"{col} Track1 non-binary")
        if sorted(set(t2[col].tolist()) - {-1}):
            errors.append(f"{col} Track2 non -1")
    item_sums = t1[item_cols].sum(axis=1).astype(int)
    if not (item_sums.to_numpy() == t1["Total"].astype(int).to_numpy()).all():
        errors.append("Track1 Total differs from item sums")
    for col in ["Left_gait_subtype", "Right_gait_subtype"]:
        bad = sorted(set(map(str, t2[col].tolist())) - SUBTYPES)
        if bad:
            errors.append(f"{col} invalid Track2 labels {bad}")
    return ("fail", "; ".join(errors)) if errors else ("pass", "")


def diff_rows(base: pd.DataFrame, df: pd.DataFrame) -> str:
    b = base.set_index("ID")
    x = df.set_index("ID").reindex(index=b.index, columns=b.columns)
    return "|".join((b != x).any(axis=1).loc[lambda s: s].index)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--track1", default="data/raw/track1_train.json")
    parser.add_argument("--track2", default="data/raw/track2_train.json")
    parser.add_argument("--features", default="features/patient_light_features.csv")
    parser.add_argument("--s09", default="submissions/candidates/s09_t1_id_t2_feature_nopid.csv")
    parser.add_argument("--output-dir", default="submissions/candidates/2026-05-05-official")
    args = parser.parse_args()

    t1 = load_json(Path(args.track1))
    t2 = load_json(Path(args.track2))
    features = numeric_features(Path(args.features))
    s09 = read_submission(Path(args.s09))
    output_dir = Path(args.output_dir)

    t1_meta7 = build_t1_rows(t1, features, "feature:meta", 7, 0.50)
    t1_meta9 = build_t1_rows(t1, features, "feature:meta", 9, 0.50)
    t1_meta11 = build_t1_rows(t1, features, "feature:meta", 11, 0.50)
    t1_meta13 = build_t1_rows(t1, features, "feature:meta", 13, 0.50)
    t1_all11 = build_t1_rows(t1, features, "feature:all", 11, 0.50)
    t1_pid5 = build_t1_rows(t1, features, "pid", 5, 0.45)
    t1_majority = build_t1_rows(t1, features, "majority", len(t1), 0.50)
    t2_meta3 = build_t2_rows(t2, features, "feature:meta", 3)
    t2_all3 = build_t2_rows(t2, features, "feature:all", 3)
    t2_side3 = build_t2_rows(t2, features, "feature:side", 3)

    specs = [
        ("of01_t1_meta11_t2_s09", apply_t1_rows(s09, t1_meta11), "Track1 light metadata KNN k=11; Track2 s09 feature NN anchor."),
        ("of02_t1_pid5_t2_s09", apply_t1_rows(s09, t1_pid5), "Track1 patient-ID KNN k=5 threshold 0.45; Track2 s09 feature NN anchor."),
        ("of03_t1_meta11_t2_meta3", apply_t2_rows(apply_t1_rows(s09, t1_meta11), t2_meta3), "Track1 metadata KNN k=11; Track2 metadata KNN k=3."),
        ("of04_t1_majority_t2_meta3", apply_t2_rows(apply_t1_rows(s09, t1_majority), t2_meta3), "Track1 global majority; Track2 metadata KNN k=3."),
        ("of05_t1_all11_t2_side3", apply_t2_rows(apply_t1_rows(s09, t1_all11), t2_side3), "Track1 all-view light KNN k=11; Track2 side-light KNN k=3."),
        ("of06_t1_s09_t2_all3", apply_t2_rows(s09, t2_all3), "Track1 s09 ID anchor; Track2 all-view light KNN k=3."),
        ("of07_t1_s09_t2_meta3", apply_t2_rows(s09, t2_meta3), "Track1 s09 ID anchor; Track2 metadata KNN k=3."),
        ("of08_t1_meta7_t2_s09", apply_t1_rows(s09, t1_meta7), "Track1 light metadata KNN k=7; Track2 s09 feature NN anchor."),
        ("of09_t1_meta9_t2_s09", apply_t1_rows(s09, t1_meta9), "Track1 light metadata KNN k=9; Track2 s09 feature NN anchor."),
        ("of10_t1_meta13_t2_s09", apply_t1_rows(s09, t1_meta13), "Track1 light metadata KNN k=13; Track2 s09 feature NN anchor."),
    ]

    rows: list[dict[str, Any]] = []
    for experiment_id, df, description in specs:
        output_dir.mkdir(parents=True, exist_ok=True)
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
                "inputs": {
                    "track1": {"path": args.track1, "sha256": sha256(Path(args.track1))},
                    "track2": {"path": args.track2, "sha256": sha256(Path(args.track2))},
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
