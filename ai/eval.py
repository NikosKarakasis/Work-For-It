"""Compare rep-count accuracy of the heuristic baseline vs a trained classifier
against a small manually-counted ground-truth set.

eval_labels_csv columns: video, true_rep_count

Usage:
    python eval.py --exercise push-up --angles_csv data/push_up_angles.csv --eval_labels_csv data/push_up_eval_labels.csv
    python eval.py --exercise push-up --angles_csv data/push_up_angles.csv --eval_labels_csv data/push_up_eval_labels.csv --classifier data/push_up_classifier.joblib
"""

import argparse

import numpy as np
import pandas as pd

from baseline_state_machine import calibrate_thresholds, count_reps, smooth
from features import EXERCISE_CONFIGS
from train_classifier import rep_features


def evaluate(exercise: str, angles_csv: str, eval_labels_csv: str, classifier_path: str | None):
    config = EXERCISE_CONFIGS[exercise]
    angle_names = list(config["angles"].keys())
    df = pd.read_csv(angles_csv)
    eval_labels = pd.read_csv(eval_labels_csv).set_index("video")["true_rep_count"].to_dict()

    clf = None
    if classifier_path:
        import joblib
        clf = joblib.load(classifier_path)

    rows = []
    for video_name, group in df.groupby("video"):
        if video_name not in eval_labels:
            continue
        group = group.sort_values("frame").reset_index(drop=True)
        smoothed_primary = smooth(group[config["primary_angle"]]).to_numpy()
        down, up = calibrate_thresholds(smoothed_primary)
        heuristic_count, reps = count_reps(smoothed_primary, down, up)

        classifier_count = heuristic_count
        if clf is not None and reps:
            feats = np.array([rep_features(group, s, e, angle_names) for s, e in reps])
            valid_mask = clf.predict(feats)
            classifier_count = int(valid_mask.sum())

        true_count = eval_labels[video_name]
        rows.append({
            "video": video_name,
            "true_count": true_count,
            "heuristic_count": heuristic_count,
            "heuristic_error": heuristic_count - true_count,
            "classifier_count": classifier_count,
            "classifier_error": classifier_count - true_count,
        })

    return pd.DataFrame(rows)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--exercise", required=True, choices=list(EXERCISE_CONFIGS.keys()))
    parser.add_argument("--angles_csv", required=True)
    parser.add_argument("--eval_labels_csv", required=True)
    parser.add_argument("--classifier", default=None, help="Optional path to a trained classifier from train_classifier.py")
    args = parser.parse_args()

    results = evaluate(args.exercise, args.angles_csv, args.eval_labels_csv, args.classifier)
    if results.empty:
        raise SystemExit("No overlap between angles_csv videos and eval_labels_csv — check video names match.")

    print(results.to_string(index=False))
    print()
    print(f"{args.exercise} — heuristic MAE: {results['heuristic_error'].abs().mean():.2f}, "
          f"exact matches: {(results['heuristic_error'] == 0).mean():.0%}")
    if args.classifier:
        print(f"{args.exercise} — classifier-corrected MAE: {results['classifier_error'].abs().mean():.2f}, "
              f"exact matches: {(results['classifier_error'] == 0).mean():.0%}")


if __name__ == "__main__":
    main()
