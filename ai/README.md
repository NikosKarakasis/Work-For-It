# Push-Up & Squat Detection AI

Detects and counts push-up and squat reps from video using MediaPipe pose
estimation, with both an offline pipeline (for training/evaluating on
recorded footage) and a live pipeline (webcam demo + FastAPI wrapper for the
iOS app / Chrome extension to call).

## Setup

```powershell
cd ai
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Download the pose detection model (one-time, ~5.7MB, not committed to git):
```powershell
mkdir models
curl -L -o models\pose_landmarker_lite.task "https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_lite/float16/1/pose_landmarker_lite.task"
```

## How it works

1. **MediaPipe Pose** extracts body landmarks (shoulders, elbows, wrists, hips, knees, ankles) from each frame.
2. Landmarks get converted into joint angles per exercise (`features.py`) — elbow angle for push-ups, knee angle for squats.
3. A rep counter watches that angle rise and fall (down → up = one rep), calibrated to the specific clip/session rather than one fixed number for everyone (different bodies/camera angles/push-up styles have different angle ranges).
4. Two extra checks keep it from miscounting: a **position gate** (is the body actually horizontal for a push-up / vertical for a squat, not just standing around) and a **tracking-confidence check** (is the pose estimate actually trustworthy right now, or is it guessing due to occlusion/bad lighting).

## Offline pipeline — analyzing a folder of recorded clips

Use this to build/evaluate the counting logic against your video library, not for live use.

**1. Flag likely non-representative clips** (produced videos with timer/logo overlays that distort framing — not a "real vs fake" detector, see the docstring in the script):
```powershell
python detect_screen_recordings.py --input_dir "path\to\push-up\clips" --output_csv data\push_up_overlay_flags.csv
```

**2. Extract pose/angle data**, excluding flagged clips:
```powershell
python extract_keypoints.py --exercise push-up --input_dir "path\to\push-up\clips" --output_csv data\push_up_angles.csv --skip_csv data\push_up_overlay_flags.csv
```
Add `--limit 10` for a fast test run on a handful of clips before processing everything.

**3. Run the heuristic rep counter**:
```powershell
python baseline_state_machine.py --exercise push-up --angles_csv data\push_up_angles.csv
```

**4. Build a labeled eval set** — generates one thumbnail contact-sheet image per video (so you can glance instead of watching full clips) plus a CSV template pre-filled with the heuristic's guess, for you to correct:
```powershell
python label_reps.py --exercise push-up --angles_csv data\push_up_angles.csv --video_dir "path\to\push-up\clips" --output_dir review\push_up
```
Open the PNGs in `review\push_up\`, fill in `corrected_count` in the generated `*_labels_template.csv`.

**5. Train/compare models** against those labels (`video, rep_index, valid` format — see each script's docstring):
```powershell
python train_classifier.py --exercise push-up --angles_csv data\push_up_angles.csv --labels_csv data\push_up_rep_labels.csv
python train_temporal_model.py --exercise push-up --angles_csv data\push_up_angles.csv --labels_csv data\push_up_rep_labels.csv   # only if the classifier above isn't accurate enough
```

**6. Compare rep-count accuracy** against manually-counted ground truth (`video, true_rep_count` CSV):
```powershell
python eval.py --exercise push-up --angles_csv data\push_up_angles.csv --eval_labels_csv data\push_up_eval_labels.csv
```

Everything above works the same for `--exercise squat`, just pointed at squat clips.

## Live pipeline — webcam demo and API

**Local webcam demo** (proof of concept — not accuracy-tested the way the offline pipeline is):
```powershell
python live_demo.py --exercise push-up
```
Shows the skeleton overlay, live joint angle, rep count, and whether you're currently "IN POSITION." Press `q` to quit.

**FastAPI server** (for the iOS app / Chrome extension to connect to over a WebSocket instead of running MediaPipe on-device):
```powershell
uvicorn api:app --host 0.0.0.0 --port 8000
```
Protocol: client opens `ws://<server-ip>:8000/ws/count_reps?exercise=push-up`, sends each camera frame as a JPEG binary message, gets back `{"rep_count": int, "in_position": bool, "well_tracked": bool, "angle": float, "error": str|null}` per frame. See the docstring in `api.py` for the full protocol and its trade-offs (network round-trip latency vs. not needing to port this to Swift/Core ML yet).

## Known limitations (be honest about these)

- The live counter has NOT been accuracy-tested the way the offline pipeline has — it's a working demo, tune it further before trusting it for real gating.
- Dark/baggy clothing in dim lighting genuinely degrades pose tracking — the `well_tracked` check now surfaces this instead of silently miscounting, but can't fully fix it. Better lighting and more fitted clothing will always track better.
- The offline dataset (`archive (2)`/`archive (3)`) is clip-level exercise-type labeled only, not per-rep — you need to build your own small labeled eval set (via `label_reps.py`) for real accuracy numbers.
- `calibrate_thresholds()` (offline) and `LiveRepCounter` (live) use different calibration strategies — offline looks at a whole clip at once, live uses a rolling window since it has no "whole clip" yet. Don't expect identical counts between them on the same footage.

## File map

| File | Purpose |
|---|---|
| `features.py` | Landmark indices, per-exercise angle/config definitions, position gating, tracking-confidence checks |
| `extract_keypoints.py` | Batch pose extraction from a folder of video clips → CSV |
| `detect_screen_recordings.py` | Flags clips with static graphic overlays (timers/watermarks) before extraction |
| `baseline_state_machine.py` | Heuristic rep counter (calibrated per-clip) |
| `label_reps.py` | Generates contact-sheet thumbnails + labels template for building an eval set |
| `train_classifier.py` | scikit-learn rep-validity classifier |
| `train_temporal_model.py` | PyTorch 1D-CNN alternative (only if the classifier underperforms) |
| `eval.py` | Compares model rep-count accuracy against manually-counted ground truth |
| `live_demo.py` | Local webcam demo with skeleton overlay, position gating, tracking-confidence |
| `api.py` | FastAPI WebSocket server wrapping the live pipeline for iOS/extension to call |
