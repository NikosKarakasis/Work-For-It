"""Run MediaPipe Pose over a folder of clips and write per-frame joint angles to CSV.

Uses MediaPipe's Tasks API (PoseLandmarker) since the legacy `mp.solutions.pose`
API isn't shipped in current mediapipe wheels for recent Python versions.
Requires the pose landmarker model bundle at models/pose_landmarker_lite.task
(download once: see README note below, or re-run the download command in the
project setup instructions).

Usage:
    python extract_keypoints.py --exercise push-up --input_dir "../archive (3)/raw_data/raw_data/data-btc/push-up" --output_csv data/push_up_angles.csv
"""

import argparse
import pathlib

import cv2
import mediapipe as mp
import pandas as pd
from mediapipe.tasks.python import vision as mp_vision
from mediapipe.tasks.python.core.base_options import BaseOptions

from features import EXERCISE_CONFIGS, compute_frame_angles

VIDEO_EXTENSIONS = {".mp4", ".mov", ".avi", ".mkv"}
DEFAULT_MODEL_PATH = pathlib.Path(__file__).parent / "models" / "pose_landmarker_lite.task"


def make_landmarker(model_path: pathlib.Path, num_poses: int = 1) -> mp_vision.PoseLandmarker:
    options = mp_vision.PoseLandmarkerOptions(
        base_options=BaseOptions(model_asset_path=str(model_path)),
        running_mode=mp_vision.RunningMode.VIDEO,
        num_poses=num_poses,
    )
    return mp_vision.PoseLandmarker.create_from_options(options)


def extract_video(video_path: pathlib.Path, exercise: str, landmarker: mp_vision.PoseLandmarker) -> pd.DataFrame:
    cap = cv2.VideoCapture(str(video_path))
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    rows = []
    frame_idx = 0
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
        timestamp_ms = int((frame_idx / fps) * 1000)
        result = landmarker.detect_for_video(mp_image, timestamp_ms)
        if result.pose_landmarks:
            angles = compute_frame_angles(result.pose_landmarks[0], exercise)
            row = {"frame": frame_idx, "time_s": frame_idx / fps, **angles}
            rows.append(row)
        frame_idx += 1
    cap.release()
    return pd.DataFrame(rows)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--exercise", required=True, choices=list(EXERCISE_CONFIGS.keys()))
    parser.add_argument("--input_dir", required=True, help="Folder of video clips for this exercise")
    parser.add_argument("--output_csv", required=True, help="Where to write the combined per-frame angle CSV")
    parser.add_argument("--model_path", default=str(DEFAULT_MODEL_PATH), help="Path to the pose_landmarker .task model file")
    parser.add_argument("--limit", type=int, default=None, help="Only process the first N videos (for a fast test run before the full batch)")
    parser.add_argument("--skip_csv", default=None,
                         help="CSV from detect_screen_recordings.py — videos with flagged_overlay=True are skipped")
    args = parser.parse_args()

    input_dir = pathlib.Path(args.input_dir)
    videos = sorted(p for p in input_dir.rglob("*") if p.suffix.lower() in VIDEO_EXTENSIONS)
    if not videos:
        raise SystemExit(f"No video files found under {input_dir}")

    if args.skip_csv:
        flags = pd.read_csv(args.skip_csv)
        skip_names = set(flags.loc[flags["flagged_overlay"], "video"])
        before = len(videos)
        videos = [v for v in videos if v.name not in skip_names]
        print(f"[info] --skip_csv: excluded {before - len(videos)} flagged-overlay clips")

    if args.limit is not None:
        videos = videos[:args.limit]
        print(f"[info] --limit {args.limit}: processing {len(videos)} of the available videos")

    model_path = pathlib.Path(args.model_path)
    if not model_path.exists():
        raise SystemExit(
            f"Pose landmarker model not found at {model_path}. Download it with:\n"
            f'  curl -L -o "{model_path}" '
            f'"https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_lite/float16/1/pose_landmarker_lite.task"'
        )

    all_frames = []
    for video_path in videos:
        landmarker = make_landmarker(model_path)  # fresh instance per video: VIDEO mode requires monotonically increasing timestamps
        df = extract_video(video_path, args.exercise, landmarker)
        landmarker.close()
        if df.empty:
            print(f"[warn] no pose detected in {video_path.name}, skipping")
            continue
        df.insert(0, "video", video_path.name)
        all_frames.append(df)
        print(f"[ok] {video_path.name}: {len(df)} frames with pose")

    if not all_frames:
        raise SystemExit("No pose was detected in any video — check the input videos/model.")

    combined = pd.concat(all_frames, ignore_index=True)
    output_path = pathlib.Path(args.output_csv)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    combined.to_csv(output_path, index=False)
    print(f"Wrote {len(combined)} rows across {len(all_frames)} videos to {output_path}")


if __name__ == "__main__":
    main()
