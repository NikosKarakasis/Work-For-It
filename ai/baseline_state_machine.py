"""Heuristic rep counter: a down/up state machine over the primary joint angle.

Usage:
    python baseline_state_machine.py --exercise push-up --angles_csv data/push_up_angles.csv
"""

import argparse

import numpy as np
import pandas as pd

from features import EXERCISE_CONFIGS


def smooth(series: pd.Series, window: int = 5) -> pd.Series:
    return series.rolling(window=window, center=True, min_periods=1).mean()


def calibrate_thresholds(angle_values: np.ndarray, down_frac: float = 0.35, up_frac: float = 0.65,
                          min_range_degrees: float = 15.0):
    """Derive down/up thresholds from THIS clip's own observed angle range.

    A single global threshold (e.g. "elbow < 95 degrees") assumes one body,
    camera angle, and push-up style. Diamond/wide-grip push-ups, different
    limb lengths, and different camera angles all shift the range of elbow
    angles a full rep actually covers, even in a real full-range rep. Instead,
    calibrate to the range this specific video shows: down_frac/up_frac of the
    way between this clip's own 5th/95th percentile angle.
    """
    valid = angle_values[~np.isnan(angle_values)]
    if len(valid) == 0:
        return None, None
    low = np.percentile(valid, 5)
    high = np.percentile(valid, 95)
    if high - low < min_range_degrees:
        # too little motion in this clip to be a real rep cycle
        return None, None
    span = high - low
    return low + down_frac * span, low + up_frac * span


def count_reps(angle_values: np.ndarray, down_threshold: float | None = None, up_threshold: float | None = None,
               min_rep_frames: int = 8):
    """Down -> up -> down transition counts as one rep. Returns (count, rep_frame_ranges).

    If down_threshold/up_threshold are omitted, they're calibrated from this
    clip's own angle range via calibrate_thresholds (recommended — see there
    for why a fixed global threshold breaks on exercise-style variations).

    min_rep_frames rejects blips that cross the thresholds too quickly to be
    a real rep (jitter in the landmark signal near the threshold boundary
    otherwise gets counted as several fake short "reps").
    """
    if down_threshold is None or up_threshold is None:
        down_threshold, up_threshold = calibrate_thresholds(angle_values)
        if down_threshold is None:
            return 0, []

    state = "up"  # assume the clip starts near the top position
    reps = []
    rep_start = None
    for i, angle in enumerate(angle_values):
        if np.isnan(angle):
            continue
        if state == "up" and angle <= down_threshold:
            state = "down"
            rep_start = i
        elif state == "down" and angle >= up_threshold:
            state = "up"
            if rep_start is not None and (i - rep_start) >= min_rep_frames:
                reps.append((rep_start, i))
    return len(reps), reps


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--exercise", required=True, choices=list(EXERCISE_CONFIGS.keys()))
    parser.add_argument("--angles_csv", required=True)
    parser.add_argument("--smooth_window", type=int, default=5)
    parser.add_argument("--use_fixed_thresholds", action="store_true",
                         help="Use the fixed degree thresholds from features.py instead of per-clip calibration")
    args = parser.parse_args()

    config = EXERCISE_CONFIGS[args.exercise]
    primary = config["primary_angle"]
    df = pd.read_csv(args.angles_csv)

    for video_name, group in df.groupby("video"):
        group = group.sort_values("frame")
        smoothed = smooth(group[primary], window=args.smooth_window).to_numpy()
        if args.use_fixed_thresholds:
            count, reps = count_reps(smoothed, config["down_threshold"], config["up_threshold"])
        else:
            down, up = calibrate_thresholds(smoothed)
            count, reps = count_reps(smoothed, down, up)
        print(f"{video_name}: {count} reps detected (frames: {reps})")


if __name__ == "__main__":
    main()
