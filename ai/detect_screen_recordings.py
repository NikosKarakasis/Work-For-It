"""Flag clips with a static, high-contrast graphic overlay (app-style timer/
counter HUDs, channel watermarks/logos) baked into the frame.

IMPORTANT — this is NOT a "real person vs. fake/synthetic" detector, and
testing showed it can't reliably be one from pixels alone: both clips flagged
in initial testing turned out to be real people on real cameras, just from
produced fitness videos with a composited timer graphic or watermark. What it
actually flags is "this footage was edited/produced," which still matters —
those overlays often crop the person into only part of the frame (a
picture-in-picture layout next to a timer panel, say), so the person appears
at a different scale/position than a normal full-frame webcam shot would show
your live camera feed. Treat a flag as "probably not representative of raw
webcam footage, go look" rather than "not a real person."

The signal: a region that's (a) perfectly static across the whole clip (real
handheld/tripod cameras still have tiny sensor jitter — a sample-frame-
identical region is a strong tell), (b) high-contrast edges (text/icons), and
(c) near-extreme brightness (white/black text and counters, unlike natural
room lighting gradients).

Meant for fast triage across hundreds of clips before the much slower pose-
extraction step — not a final verdict. Always spot-check flagged AND unflagged
clips yourself (e.g. via label_reps.py's contact sheets) before trusting it.

Usage:
    python detect_screen_recordings.py --input_dir "../archive (3)/verified_data/verified_data/data_btc_10s/push-up" --output_csv data/push_up_screen_recording_flags.csv
"""

import argparse
import pathlib

import cv2
import numpy as np
import pandas as pd

VIDEO_EXTENSIONS = {".mp4", ".mov", ".avi", ".mkv"}


def overlay_score(video_path: pathlib.Path, sample_frames: int = 12,
                   static_std_threshold: float = 4.0) -> float | None:
    """Fraction of pixels that look like a static, high-contrast HUD overlay."""
    cap = cv2.VideoCapture(str(video_path))
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    if total <= 0:
        cap.release()
        return None

    indices = np.linspace(0, total - 1, num=min(sample_frames, total), dtype=int)
    frames = []
    for idx in indices:
        cap.set(cv2.CAP_PROP_POS_FRAMES, int(idx))
        ok, frame = cap.read()
        if ok:
            frames.append(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY))
    cap.release()
    if len(frames) < 3:
        return None

    stack = np.stack(frames).astype(np.float32)
    pixel_std = stack.std(axis=0)                      # (a) near-zero across every sampled frame = static
    static_mask = pixel_std < static_std_threshold

    median_frame = np.median(stack, axis=0).astype(np.uint8)
    edges = cv2.Canny(median_frame, 80, 160) > 0        # (b) crisp edges = text/icon shapes

    extreme_luminance = (median_frame > 220) | (median_frame < 12)  # (c) near-pure white/black = UI text/counters

    overlay_mask = static_mask & edges & extreme_luminance
    return float(overlay_mask.sum()) / overlay_mask.size


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_dir", required=True, help="Folder of video clips to scan (searched recursively)")
    parser.add_argument("--output_csv", required=True)
    parser.add_argument("--flag_threshold", type=float, default=0.0003,
                         help="overlay_score above this = flagged as having a likely static graphic overlay. "
                              "Scores in the 0.0001-0.0003 band were found to mostly be false positives from "
                              "ordinary blurred side-padding (portrait video reformatted to landscape), not real "
                              "overlays — see the module docstring.")
    args = parser.parse_args()

    input_dir = pathlib.Path(args.input_dir)
    videos = sorted(p for p in input_dir.rglob("*") if p.suffix.lower() in VIDEO_EXTENSIONS)
    if not videos:
        raise SystemExit(f"No video files found under {input_dir}")

    rows = []
    for video_path in videos:
        score = overlay_score(video_path)
        if score is None:
            print(f"[warn] couldn't read {video_path.name}, skipping")
            continue
        flagged = score > args.flag_threshold
        rows.append({"video": video_path.name, "overlay_score": round(score, 5), "flagged_overlay": flagged})
        if flagged:
            print(f"[flagged] {video_path.name}: overlay_score={score:.5f}")

    df = pd.DataFrame(rows)
    output_path = pathlib.Path(args.output_csv)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)

    n_flagged = int(df["flagged_overlay"].sum())
    print(f"\n{n_flagged} of {len(df)} clips flagged as likely having a static graphic overlay (timer/watermark/etc). Wrote {output_path}")
    print("This is a heuristic, not a real-vs-fake detector — spot-check flagged AND unflagged clips before trusting it.")


if __name__ == "__main__":
    main()
