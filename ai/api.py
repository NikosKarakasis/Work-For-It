"""FastAPI wrapper around the live rep-counting pipeline, so the iOS app (or
any client) can call it over a WebSocket instead of needing to run MediaPipe
on-device directly.

TRADE-OFF — be aware of this: every camera frame gets sent over the network
to wherever this server runs, which adds latency (network round trip) and
means the phone needs a live connection during the whole exercise check. Fine
for a hackathon/MVP and for a "prove you did a few reps before unlocking"
gate that doesn't need to be frame-perfect in real time. NOT what you'd want
for a fully polished, low-latency final product — that would eventually mean
porting this pose/counting logic to run on-device (MediaPipe iOS SDK / Core
ML), with no server round trip at all. Treat this as the fast way to connect
what already works, not the final architecture.

Protocol:
  1. Client opens a WebSocket to /ws/count_reps?exercise=push-up
  2. Client sends each camera frame as a JPEG-encoded BINARY websocket message
  3. Server replies with one JSON TEXT message per frame:
     {"rep_count": int, "in_position": bool, "well_tracked": bool, "angle": float | null, "error": str | null}
     well_tracked=false means confidence in the pose estimate is too low right
     now (occlusion, bad lighting, baggy/dark clothing) to trust it — the
     client should show something like "move into better light" rather than
     treat rep_count as reliable in that moment.
  4. Closing the WebSocket ends the session (all state for it is discarded)

Run:
    uvicorn api:app --host 0.0.0.0 --port 8000

Then point the iOS app at ws://<this machine's LAN IP>:8000/ws/count_reps?exercise=push-up
(not localhost — the phone is a different device on the network).
"""

import pathlib

import cv2
import mediapipe as mp
import numpy as np
from fastapi import FastAPI, WebSocket, WebSocketDisconnect

from extract_keypoints import DEFAULT_MODEL_PATH, make_landmarker
from features import EXERCISE_CONFIGS, compute_frame_angles, in_expected_position, primary_angle_confidence
from live_demo import LiveRepCounter, choose_primary_pose

app = FastAPI()


@app.get("/health")
def health():
    return {"status": "ok", "exercises": list(EXERCISE_CONFIGS.keys())}


@app.websocket("/ws/count_reps")
async def count_reps_ws(websocket: WebSocket):
    exercise = websocket.query_params.get("exercise", "push-up")
    if exercise not in EXERCISE_CONFIGS:
        await websocket.close(code=1008, reason=f"unknown exercise '{exercise}'")
        return

    await websocket.accept()
    landmarker = make_landmarker(pathlib.Path(DEFAULT_MODEL_PATH), num_poses=3)
    config = EXERCISE_CONFIGS[exercise]
    counter = LiveRepCounter(min_range_degrees=config["min_calibration_range_degrees"])
    previous_centroid = None
    frame_index = 0

    try:
        while True:
            data = await websocket.receive_bytes()
            frame = cv2.imdecode(np.frombuffer(data, dtype=np.uint8), cv2.IMREAD_COLOR)
            if frame is None:
                await websocket.send_json({"rep_count": counter.count, "in_position": False, "well_tracked": False,
                                            "angle": None, "error": "couldn't decode frame"})
                continue

            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
            frame_index += 1
            timestamp_ms = frame_index * 33  # assume ~30fps; only needs to be strictly increasing
            result = landmarker.detect_for_video(mp_image, timestamp_ms)

            landmarks, previous_centroid = choose_primary_pose(result.pose_landmarks, previous_centroid)
            if landmarks is None:
                await websocket.send_json({"rep_count": counter.count, "in_position": False, "well_tracked": False,
                                            "angle": None, "error": None})
                continue

            angles = compute_frame_angles(landmarks, exercise)
            primary_value = angles[config["primary_angle"]]
            position_ok = in_expected_position(landmarks, exercise)
            confidence = primary_angle_confidence(landmarks, exercise)
            well_tracked = confidence >= 0.5

            if not well_tracked:
                # Don't update OR reset — a brief occlusion shouldn't wipe
                # calibration, but this frame's angle isn't trustworthy either.
                count = counter.count
            elif position_ok:
                count, _, _ = counter.update(primary_value, timestamp_ms / 1000)
            else:
                counter.reset_for_out_of_position()
                count = counter.count

            await websocket.send_json({
                "rep_count": count,
                "in_position": position_ok,
                "well_tracked": well_tracked,
                "angle": round(float(primary_value), 1),
                "error": None,
            })
    except WebSocketDisconnect:
        pass
    finally:
        landmarker.close()
