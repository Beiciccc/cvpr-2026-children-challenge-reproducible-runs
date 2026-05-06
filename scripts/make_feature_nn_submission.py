#!/usr/bin/env python3
"""Build feature-nearest-neighbor submission candidates from extracted CGPS JSON.

This is intentionally lightweight: it samples frames from each pose sequence,
builds patient-level summary features, and uses standardized nearest-neighbor
matching within each labeled track.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
from collections import Counter
from pathlib import Path
from typing import Any

import numpy as np


TRACK1_TEST_IDS = [4, 5, 18, 26, 28, 40, 42, 43, 47, 48, 53, 54, 72, 78, 83, 85]
TRACK2_TEST_IDS = [4, 6, 7, 13, 26, 35, 39, 42, 50]
ITEMS = [str(i) for i in range(1, 18)]
DIRS = ["left", "right", "forward", "backward"]
KP = list(range(0, 23))


def load_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def mode(values: list[Any]) -> Any:
    counts = Counter(values)
    return sorted(counts.items(), key=lambda kv: (-kv[1], str(kv[0])))[0][0]


def direction_from_name(name: str) -> str | None:
    for d in DIRS:
        if f"_{d}_" in name:
            return d
    return None


def sample_files(files: list[Path], max_frames: int) -> list[Path]:
    if len(files) <= max_frames:
        return files
    idx = np.linspace(0, len(files) - 1, max_frames).round().astype(int)
    return [files[int(i)] for i in idx]


def frame_vector(path: Path) -> np.ndarray | None:
    try:
        obj = load_json(path)
        inst = obj["instance_info"][0]
        pts = np.asarray(inst["keypoints"], dtype=np.float32)
        scores = np.asarray(inst.get("keypoint_scores", np.ones(len(pts))), dtype=np.float32)
        bbox = np.asarray(inst.get("gt_bbox_xywh_px", [0, 0, 1, 1]), dtype=np.float32)
    except Exception:
        return None
    if pts.ndim != 2 or pts.shape[0] <= max(KP):
        return None
    x, y, w, h = bbox[:4]
    scale = max(float(w), float(h), 1.0)
    center = np.asarray([x + w / 2.0, y + h / 2.0], dtype=np.float32)
    p = (pts[KP] - center) / scale
    s = scores[KP].reshape(-1, 1)
    body = np.concatenate([p, s], axis=1).reshape(-1)
    bbox_feat = np.asarray([x / 1920.0, y / 1080.0, w / 1920.0, h / 1080.0, w / max(h, 1.0)], dtype=np.float32)
    return np.concatenate([body, bbox_feat])


def summarize_matrix(mat: np.ndarray) -> np.ndarray:
    if mat.size == 0:
        width = len(KP) * 3 + 4 + 1
        return np.zeros(width * 4 + 2, dtype=np.float32)
    mean = np.nanmean(mat, axis=0)
    std = np.nanstd(mat, axis=0)
    lo = np.nanmin(mat, axis=0)
    hi = np.nanmax(mat, axis=0)
    return np.concatenate([mean, std, hi - lo, np.nanmedian(mat, axis=0), [len(mat), np.isfinite(mat).mean()]]).astype(np.float32)


def patient_features(dataset_root: Path, pid: int, max_frames_per_seq: int) -> np.ndarray:
    pdir = dataset_root / f"{pid:04d}"
    by_dir: dict[str, list[np.ndarray]] = {d: [] for d in DIRS}
    if pdir.exists():
        for seq_dir in sorted(x for x in pdir.iterdir() if x.is_dir()):
            d = direction_from_name(seq_dir.name)
            if d is None:
                continue
            files = sorted(seq_dir.glob("*.json"))
            for fp in sample_files(files, max_frames_per_seq):
                vec = frame_vector(fp)
                if vec is not None:
                    by_dir[d].append(vec)
    chunks = []
    for d in DIRS:
        mat = np.vstack(by_dir[d]) if by_dir[d] else np.empty((0, 0), dtype=np.float32)
        chunks.append(summarize_matrix(mat))
    chunks.append(np.asarray([pid / 110.0], dtype=np.float32))
    return np.concatenate(chunks)


def feature_table(dataset_root: Path, pids: list[int], max_frames_per_seq: int) -> dict[int, np.ndarray]:
    out: dict[int, np.ndarray] = {}
    for i, pid in enumerate(sorted(set(pids)), 1):
        out[pid] = patient_features(dataset_root, pid, max_frames_per_seq)
        if i % 10 == 0:
            print(f"features {i}/{len(set(pids))}", flush=True)
    return out


def nearest_by_features(features: dict[int, np.ndarray], train_ids: list[int], test_id: int, use_pid: bool) -> int:
    train = np.vstack([features[i] for i in train_ids])
    test = features[test_id].copy()
    if not use_pid:
        train = train[:, :-1]
        test = test[:-1]
    mean = np.nanmean(train, axis=0)
    std = np.nanstd(train, axis=0)
    keep = np.isfinite(mean) & np.isfinite(std) & (std > 1e-6)
    train_z = (train[:, keep] - mean[keep]) / std[keep]
    test_z = (test[keep] - mean[keep]) / std[keep]
    train_z = np.nan_to_num(train_z, nan=0.0, posinf=0.0, neginf=0.0)
    test_z = np.nan_to_num(test_z, nan=0.0, posinf=0.0, neginf=0.0)
    dist = np.sqrt(np.mean((train_z - test_z) ** 2, axis=1))
    best = int(np.argmin(dist))
    return train_ids[best]


def nearest_by_id(train_ids: list[int], test_id: int) -> int:
    return min(train_ids, key=lambda x: (abs(x - test_id), x))


def write_submission(
    path: Path,
    track1_rows: list[dict[str, Any]],
    track2_rows: list[dict[str, Any]],
    features: dict[int, np.ndarray],
    t1_source: str,
    t2_source: str,
    use_pid_feature: bool,
) -> None:
    t1_by_id = {r["patient_id"]: r for r in track1_rows}
    t2_by_id = {r["patient_id"]: r for r in track2_rows}
    t1_ids = sorted(t1_by_id)
    t2_ids = sorted(t2_by_id)
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
        for pid in TRACK1_TEST_IDS:
            src = nearest_by_features(features, t1_ids, pid, use_pid_feature) if t1_source == "feature" else nearest_by_id(t1_ids, pid)
            row = t1_by_id[src]
            left = [int(row["left"][item]) for item in ITEMS]
            right = [int(row["right"][item]) for item in ITEMS]
            writer.writerow([f"track1-{pid}", *left, *right, sum(left) + sum(right), -1, -1])
            print("track1", pid, "source", src, t1_source)
        for pid in TRACK2_TEST_IDS:
            src = nearest_by_features(features, t2_ids, pid, use_pid_feature) if t2_source == "feature" else nearest_by_id(t2_ids, pid)
            row = t2_by_id[src]
            writer.writerow(
                [
                    f"track2-{pid}",
                    *([-1] * 35),
                    row["left"]["gait_subtype"],
                    row["right"]["gait_subtype"],
                ]
            )
            print("track2", pid, "source", src, t2_source, row["left"]["gait_subtype"], row["right"]["gait_subtype"])


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset-root", default="data/external/dataset")
    parser.add_argument("--data-dir", default="data/raw")
    parser.add_argument("--output-dir", default="submissions/candidates")
    parser.add_argument("--max-frames-per-seq", type=int, default=16)
    parser.add_argument("--with-pid-feature", action="store_true")
    args = parser.parse_args()

    data_dir = Path(args.data_dir)
    t1 = load_json(data_dir / "track1_train.json")
    t2 = load_json(data_dir / "track2_train.json")
    pids = [r["patient_id"] for r in t1] + [r["patient_id"] for r in t2] + TRACK1_TEST_IDS + TRACK2_TEST_IDS
    features = feature_table(Path(args.dataset_root), pids, args.max_frames_per_seq)
    suffix = "pidfeat" if args.with_pid_feature else "nopid"
    write_submission(
        Path(args.output_dir) / f"s09_t1_id_t2_feature_{suffix}.csv",
        t1,
        t2,
        features,
        "id",
        "feature",
        args.with_pid_feature,
    )
    write_submission(
        Path(args.output_dir) / f"s10_t1_feature_t2_id_{suffix}.csv",
        t1,
        t2,
        features,
        "feature",
        "id",
        args.with_pid_feature,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

