"""Human-in-the-loop labeling helper: turns "watch and count every video" into
"glance at a thumbnail strip and correct the number the heuristic guessed."

For each video, the heuristic (calibrate_thresholds + count_reps) proposes rep
boundaries. This script grabs the actual video frame at the DEEPEST point of
each proposed rep, builds a labeled thumbnail strip (a "contact sheet") image,
and flags any rep whose form_angle (body_line for push-ups, hip for squats)
deviates a lot from this person's own top-position posture — a likely sign of
back/hip sagging, often from fatigue — with a red border, so you know exactly
which reps are worth a second look instead of scanning the whole clip.

It also writes a template CSV with the heuristic's count pre-filled, so you
only need to fill in `corrected_count` (and notes) after checking the sheet.

Usage:
    python label_reps.py --exercise push-up --angles_csv data/push_up_angles_sample.csv --video_dir "../archive (3)/verified_data/verified_data/data_btc_10s/push-up" --output_dir review/push_up
"""

import argparse
import pathlib

import cv2
import numpy as np
import pandas as pd
from PIL import Image, ImageDraw

from baseline_state_machine import calibrate_thresholds, count_reps, smooth
from features import EXERCISE_CONFIGS

THUMB_SIZE = (160, 160)
FORM_DEVIATION_FLAG_DEGREES = 15.0


def grab_frame(video_path: pathlib.Path, frame_number: int):
    cap = cv2.VideoCapture(str(video_path))
    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
    ok, frame = cap.read()
    cap.release()
    if not ok:
        return None
    return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)


def make_thumbnail(video_path: pathlib.Path, frame_number: int, rep_index: int, flagged: bool) -> Image.Image:
    rgb = grab_frame(video_path, frame_number)
    thumb = Image.new("RGB", THUMB_SIZE, (60, 60, 60)) if rgb is None else Image.fromarray(rgb).resize(THUMB_SIZE)
    draw = ImageDraw.Draw(thumb)
    draw.rectangle([0, 0, 46, 18], fill=(0, 0, 0))
    draw.text((3, 2), f"#{rep_index}", fill=(255, 255, 0))
    if flagged:
        draw.rectangle([0, 0, THUMB_SIZE[0] - 1, THUMB_SIZE[1] - 1], outline=(255, 0, 0), width=5)
    return thumb


def assemble_sheet(thumbs: list, video_name: str) -> Image.Image:
    w, h = THUMB_SIZE
    sheet = Image.new("RGB", (w * max(len(thumbs), 1), h + 22), (255, 255, 255))
    ImageDraw.Draw(sheet).text((3, 2), video_name, fill=(0, 0, 0))
    for i, thumb in enumerate(thumbs):
        sheet.paste(thumb, (i * w, 22))
    return sheet


def process_video(video_path: pathlib.Path, group: pd.DataFrame, config: dict):
    """Detect reps, build one flagged thumbnail per rep, return (count, thumbs, flagged_indices)."""
    group = group.sort_values("frame").reset_index(drop=True)
    primary_raw = group[config["primary_angle"]].to_numpy()
    smoothed = smooth(group[config["primary_angle"]]).to_numpy()
    down, up = calibrate_thresholds(smoothed)
    count, reps = count_reps(smoothed, down, up)

    form_col = config["form_angle"]
    top_mask = primary_raw >= (up if up is not None else np.nanmax(primary_raw))
    top_form_baseline = (np.nanmedian(group[form_col].to_numpy()[top_mask]) if top_mask.any()
                          else np.nanmedian(group[form_col]))

    thumbs, flagged_indices = [], []
    for rep_index, (start, end) in enumerate(reps):
        deepest_pos = start + int(np.nanargmin(primary_raw[start:end + 1]))
        frame_number = int(group["frame"].iloc[deepest_pos])
        form_value = group[form_col].iloc[deepest_pos]
        flagged = bool(abs(form_value - top_form_baseline) > FORM_DEVIATION_FLAG_DEGREES)
        if flagged:
            flagged_indices.append(rep_index)
        thumbs.append(make_thumbnail(video_path, frame_number, rep_index, flagged))

    return count, thumbs, flagged_indices


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--exercise", required=True, choices=list(EXERCISE_CONFIGS.keys()))
    parser.add_argument("--angles_csv", required=True)
    parser.add_argument("--video_dir", required=True, help="Folder containing the original video files")
    parser.add_argument("--output_dir", required=True, help="Where to save contact sheets and the labels template CSV")
    args = parser.parse_args()

    config = EXERCISE_CONFIGS[args.exercise]
    df = pd.read_csv(args.angles_csv)
    video_dir = pathlib.Path(args.video_dir)
    output_dir = pathlib.Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    template_rows = []
    for video_name, group in df.groupby("video"):
        matches = list(video_dir.rglob(video_name))
        if not matches:
            print(f"[warn] couldn't find {video_name} under {video_dir}, skipping")
            continue
        video_path = matches[0]

        count, thumbs, flagged_indices = process_video(video_path, group, config)

        sheet = assemble_sheet(thumbs, video_name)
        sheet_path = output_dir / f"{pathlib.Path(video_name).stem}.png"
        sheet.save(sheet_path)

        notes = f"check reps {flagged_indices} for possible back/hip sag" if flagged_indices else ""
        template_rows.append({
            "video": video_name,
            "heuristic_count": count,
            "corrected_count": "",  # fill this in after checking the contact sheet
            "notes": notes,
        })
        flag_note = f" (flagged reps: {flagged_indices})" if flagged_indices else ""
        print(f"[ok] {video_name}: {count} reps, sheet -> {sheet_path}{flag_note}")

    template_path = output_dir / f"{args.exercise.replace('-', '_')}_labels_template.csv"
    pd.DataFrame(template_rows).to_csv(template_path, index=False)
    print(f"\nWrote labels template to {template_path} — open the contact sheets in {output_dir}, "
          f"then fill in the corrected_count column.")


if __name__ == "__main__":
    main()
