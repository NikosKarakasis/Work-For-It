"""Baseline scikit-learn rep-validity classifier.

Takes reps detected by baseline_state_machine.count_reps and a small manually
labeled CSV saying which of those detected reps were actually valid full reps
(vs. partial/bad-form movement the heuristic mistook for a rep), then trains
a classifier on hand-engineered features of each rep window.

labels_csv columns: video, rep_index, valid   (rep_index = nth rep found by the
state machine for that video, 0-based; valid = 0 or 1)

Usage:
    python train_classifier.py --exercise push-up --angles_csv data/push_up_angles.csv --labels_csv data/push_up_rep_labels.csv
"""

import argparse

import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.model_selection import cross_val_score

from baseline_state_machine import calibrate_thresholds, count_reps, smooth
from features import EXERCISE_CONFIGS


def rep_features(group: pd.DataFrame, start: int, end: int, angle_names: list[str]) -> list[float]:
    segment = group.iloc[start:end + 1]
    feats = []
    for name in angle_names:
        values = segment[name].to_numpy()
        feats.extend([np.nanmin(values), np.nanmax(values), np.nanmean(values), np.nanmax(values) - np.nanmin(values)])
    feats.append(end - start)  # rep duration in frames
    return feats


def build_dataset(exercise: str, angles_csv: str, labels_csv: str):
    config = EXERCISE_CONFIGS[exercise]
    angle_names = list(config["angles"].keys())
    df = pd.read_csv(angles_csv)
    labels = pd.read_csv(labels_csv)

    X, y = [], []
    for video_name, group in df.groupby("video"):
        group = group.sort_values("frame").reset_index(drop=True)
        smoothed_primary = smooth(group[config["primary_angle"]]).to_numpy()
        down, up = calibrate_thresholds(smoothed_primary)
        _, reps = count_reps(smoothed_primary, down, up)

        video_labels = labels[labels["video"] == video_name]
        for rep_index, (start, end) in enumerate(reps):
            label_row = video_labels[video_labels["rep_index"] == rep_index]
            if label_row.empty:
                continue  # no manual label for this detected rep, skip
            X.append(rep_features(group, start, end, angle_names))
            y.append(int(label_row.iloc[0]["valid"]))

    return np.array(X), np.array(y)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--exercise", required=True, choices=list(EXERCISE_CONFIGS.keys()))
    parser.add_argument("--angles_csv", required=True)
    parser.add_argument("--labels_csv", required=True)
    args = parser.parse_args()

    X, y = build_dataset(args.exercise, args.angles_csv, args.labels_csv)
    if len(X) < 10:
        raise SystemExit(f"Only {len(X)} labeled reps found — label more reps before training.")

    clf = GradientBoostingClassifier()
    scores = cross_val_score(clf, X, y, cv=min(5, len(X)))
    print(f"{args.exercise}: {len(X)} labeled reps, cross-val accuracy = {scores.mean():.3f} (+/- {scores.std():.3f})")

    clf.fit(X, y)
    import joblib
    out_path = f"data/{args.exercise.replace('-', '_')}_classifier.joblib"
    joblib.dump(clf, out_path)
    print(f"Saved trained classifier to {out_path}")


if __name__ == "__main__":
    main()
