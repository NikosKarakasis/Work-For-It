"""Live webcam rep counter — visual proof-of-concept, separate from the offline
training/eval pipeline. Draws the detected skeleton, the live joint angle, and
a running rep count directly on your webcam feed.

Two things this handles that the naive version didn't (found by testing it
live on real camera footage):

1. POSITION GATING: watching a joint angle alone can't tell "bending your
   elbow during a real push-up" apart from "bending your elbow while standing
   up" or mimicking the motion off the floor — both cross the same angle
   range. in_expected_position() in features.py checks the body's actual
   ORIENTATION (horizontal for push-ups, vertical for squats) and reps only
   count while that holds.
2. MULTIPLE PEOPLE: MediaPipe alone just returns whichever pose(s) it's most
   confident about each frame — if a second person walks into frame, tracking
   can flip to them mid-session, making the tracked angle jump between two
   different bodies. choose_primary_pose() locks onto one person (largest in
   frame first, then whoever is closest to last frame's position) instead of
   re-picking freely every frame.

IMPORTANT — this uses a DIFFERENT threshold calibration than the offline
scripts. calibrate_thresholds() in baseline_state_machine.py looks at an
entire clip's min/max angle at once, which only works after the fact. Live
video doesn't have a "whole clip" yet, so this uses a rolling window of the
last few seconds instead, continuously recalibrating as you move. That means
it needs a couple of reps to "warm up," and it can drift if you change
position/camera angle mid-session. This has NOT been accuracy-tested the way
the offline pipeline is meant to be — treat it as a demo of the concept.

Usage:
    python live_demo.py --exercise push-up
    python live_demo.py --exercise squat --camera_index 1

Press q to quit the window.
"""

import argparse
import pathlib
import time
from collections import deque

import cv2
import mediapipe as mp
import numpy as np

from extract_keypoints import DEFAULT_MODEL_PATH, make_landmarker
from features import LM, EXERCISE_CONFIGS, compute_frame_angles, in_expected_position, is_well_tracked, primary_angle_confidence

POSE_CONNECTIONS = [
    ("left_shoulder", "right_shoulder"),
    ("left_shoulder", "left_elbow"), ("left_elbow", "left_wrist"),
    ("right_shoulder", "right_elbow"), ("right_elbow", "right_wrist"),
    ("left_shoulder", "left_hip"), ("right_shoulder", "right_hip"), ("left_hip", "right_hip"),
    ("left_hip", "left_knee"), ("left_knee", "left_ankle"),
    ("right_hip", "right_knee"), ("right_knee", "right_ankle"),
]


def _centroid(landmarks):
    xs = [lm.x for lm in landmarks]
    ys = [lm.y for lm in landmarks]
    return (sum(xs) / len(xs), sum(ys) / len(ys))


def _bbox_area(landmarks):
    xs = [lm.x for lm in landmarks]
    ys = [lm.y for lm in landmarks]
    return (max(xs) - min(xs)) * (max(ys) - min(ys))


def choose_primary_pose(pose_landmarks_list, previous_centroid):
    """Lock onto one person across frames instead of re-picking every frame.

    No previous person tracked yet -> assume the largest (closest) person in
    frame is the one exercising. Once locked, stick with whoever is closest
    to where that person was last frame, so someone else walking into frame
    doesn't hijack tracking.
    """
    if not pose_landmarks_list:
        return None, previous_centroid

    if previous_centroid is None:
        best = max(pose_landmarks_list, key=_bbox_area)
    else:
        best = min(pose_landmarks_list,
                    key=lambda lms: (_centroid(lms)[0] - previous_centroid[0]) ** 2
                    + (_centroid(lms)[1] - previous_centroid[1]) ** 2)
    return best, _centroid(best)


class LiveRepCounter:
    """Streaming version of baseline_state_machine's calibrate+count logic.

    Recalibrates from a rolling window of recent angle readings instead of a
    whole clip, since live video has no "whole clip" to look at yet.
    """

    def __init__(self, window_seconds: float = 4.0, fps_estimate: int = 20,
                 down_frac: float = 0.35, up_frac: float = 0.65,
                 min_range_degrees: float = 15.0, min_rep_seconds: float = 0.3):
        self.buffer = deque(maxlen=int(window_seconds * fps_estimate))
        self.down_frac = down_frac
        self.up_frac = up_frac
        self.min_range_degrees = min_range_degrees
        self.min_rep_seconds = min_rep_seconds
        self.state = "up"
        self.count = 0
        self.rep_start_time = None

    def update(self, angle: float, timestamp_s: float):
        """Call only while in_expected_position() is True for this frame."""
        self.buffer.append(angle)
        if len(self.buffer) < 10:
            return self.count, None, None

        low = np.percentile(self.buffer, 5)
        high = np.percentile(self.buffer, 95)
        if high - low < self.min_range_degrees:
            return self.count, None, None
        span = high - low
        down_threshold = low + self.down_frac * span
        up_threshold = low + self.up_frac * span

        if self.state == "up" and angle <= down_threshold:
            self.state = "down"
            self.rep_start_time = timestamp_s
        elif self.state == "down" and angle >= up_threshold:
            self.state = "up"
            if self.rep_start_time is not None and (timestamp_s - self.rep_start_time) >= self.min_rep_seconds:
                self.count += 1

        return self.count, down_threshold, up_threshold

    def reset_for_out_of_position(self):
        """Call when in_expected_position() is False, instead of update().

        Clears the calibration buffer (angles measured while out of position,
        e.g. standing, aren't meaningful for this exercise's range) and drops
        any in-progress rep so leaving position mid-rep can't get counted.
        """
        self.state = "up"
        self.rep_start_time = None
        self.buffer.clear()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--exercise", required=True, choices=list(EXERCISE_CONFIGS.keys()))
    parser.add_argument("--camera_index", type=int, default=0)
    parser.add_argument("--model_path", default=str(DEFAULT_MODEL_PATH))
    parser.add_argument("--max_people", type=int, default=3, help="How many people MediaPipe should detect per frame before we pick the primary one")
    args = parser.parse_args()

    config = EXERCISE_CONFIGS[args.exercise]
    landmarker = make_landmarker(pathlib.Path(args.model_path), num_poses=args.max_people)
    counter = LiveRepCounter(min_range_degrees=config["min_calibration_range_degrees"])
    previous_centroid = None

    cap = cv2.VideoCapture(args.camera_index)
    if not cap.isOpened():
        raise SystemExit(
            f"Couldn't open webcam at index {args.camera_index} — try --camera_index 1, "
            f"check no other app is using the camera, and that you're not running over SSH/headless."
        )

    start_time = time.time()
    try:
        while True:
            ok, frame = cap.read()
            if not ok:
                print("[warn] failed to read a frame, stopping")
                break

            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
            timestamp_s = time.time() - start_time
            result = landmarker.detect_for_video(mp_image, int(timestamp_s * 1000))

            display = frame.copy()
            h, w = display.shape[:2]

            landmarks, previous_centroid = choose_primary_pose(result.pose_landmarks, previous_centroid)
            if landmarks is not None:
                angles = compute_frame_angles(landmarks, args.exercise)
                primary_value = angles[config["primary_angle"]]
                position_ok = in_expected_position(landmarks, args.exercise)
                confidence = primary_angle_confidence(landmarks, args.exercise)
                well_tracked = confidence >= 0.5

                if not well_tracked:
                    # Don't update OR reset — a brief occlusion (arm crossing legs,
                    # bad lighting) shouldn't wipe calibration, but we also can't
                    # trust this frame's angle enough to count anything from it.
                    count, down_t, up_t = counter.count, None, None
                elif position_ok:
                    count, down_t, up_t = counter.update(primary_value, timestamp_s)
                else:
                    counter.reset_for_out_of_position()
                    count, down_t, up_t = counter.count, None, None

                for a_name, b_name in POSE_CONNECTIONS:
                    a, b = landmarks[LM[a_name]], landmarks[LM[b_name]]
                    cv2.line(display, (int(a.x * w), int(a.y * h)), (int(b.x * w), int(b.y * h)), (0, 255, 0), 2)
                for idx in LM.values():
                    lm = landmarks[idx]
                    cv2.circle(display, (int(lm.x * w), int(lm.y * h)), 4, (0, 0, 255), -1)

                cv2.putText(display, f"Reps: {count}", (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 255), 3)
                cv2.putText(display, f"{config['primary_angle']}: {primary_value:.0f} deg", (20, 90),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
                if not well_tracked:
                    cv2.putText(display, f"CAN'T TRACK YOU CLEARLY ({confidence:.0%} confidence)", (20, 125),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 0, 255), 2)
                else:
                    position_label = "IN POSITION" if position_ok else "GET INTO POSITION"
                    position_color = (0, 255, 0) if position_ok else (0, 140, 255)
                    cv2.putText(display, position_label, (20, 125), cv2.FONT_HERSHEY_SIMPLEX, 0.7, position_color, 2)
                if down_t is not None:
                    cv2.putText(display, f"down<{down_t:.0f} up>{up_t:.0f}", (20, 155),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)
            else:
                cv2.putText(display, "No person detected", (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 2)

            cv2.imshow("Live rep counter (press q to quit)", display)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
    finally:
        cap.release()
        cv2.destroyAllWindows()
        landmarker.close()


if __name__ == "__main__":
    main()
