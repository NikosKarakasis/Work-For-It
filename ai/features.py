"""Per-exercise landmark/angle definitions shared by every script in ai/."""

import numpy as np

# MediaPipe Pose landmark indices (33-point model)
LM = {
    "left_shoulder": 11, "right_shoulder": 12,
    "left_elbow": 13, "right_elbow": 14,
    "left_wrist": 15, "right_wrist": 16,
    "left_hip": 23, "right_hip": 24,
    "left_knee": 25, "right_knee": 26,
    "left_ankle": 27, "right_ankle": 28,
}

# One entry per in-scope exercise. Adding a new exercise later means adding
# another entry here, not new extraction/windowing/eval code.
EXERCISE_CONFIGS = {
    "push-up": {
        # angle_name -> (point_a, vertex, point_c), each a side-agnostic landmark pair
        "angles": {
            "elbow": (("left_shoulder", "right_shoulder"), ("left_elbow", "right_elbow"), ("left_wrist", "right_wrist")),
            "body_line": (("left_shoulder", "right_shoulder"), ("left_hip", "right_hip"), ("left_ankle", "right_ankle")),
        },
        "primary_angle": "elbow",
        "form_angle": "body_line",  # ~180 deg = straight back; hip sag/pike (often from fatigue) pulls it away from 180
        "down_threshold": 95.0,   # elbow angle below this = bottom of rep
        "up_threshold": 160.0,    # elbow angle above this = top of rep
        "body_orientation": "horizontal",  # shoulder-hip line should be roughly horizontal (plank), not upright/standing
        "tracking_landmarks": ("left_shoulder", "right_shoulder", "left_elbow", "right_elbow", "left_wrist", "right_wrist"),
        "min_calibration_range_degrees": 45.0,  # a real rep's range is ~65deg; small shoulder shrugs are <20deg
    },
    "squat": {
        "angles": {
            "knee": (("left_hip", "right_hip"), ("left_knee", "right_knee"), ("left_ankle", "right_ankle")),
            "hip": (("left_shoulder", "right_shoulder"), ("left_hip", "right_hip"), ("left_knee", "right_knee")),
        },
        "primary_angle": "knee",
        "form_angle": "hip",  # excessive forward lean/rounding shows up as a smaller hip angle at the bottom
        "down_threshold": 100.0,
        "up_threshold": 165.0,
        "body_orientation": "vertical",  # shoulder-hip line should be roughly vertical (standing), not lying down
        "tracking_landmarks": ("left_hip", "right_hip", "left_knee", "right_knee", "left_ankle", "right_ankle"),
        "min_calibration_range_degrees": 45.0,
    },
}


def calculate_angle(a: np.ndarray, b: np.ndarray, c: np.ndarray) -> float:
    """Angle at vertex b (degrees), formed by points a-b-c."""
    ba = a - b
    bc = c - b
    denom = np.linalg.norm(ba) * np.linalg.norm(bc)
    if denom == 0:
        return np.nan
    cosine = np.clip(np.dot(ba, bc) / denom, -1.0, 1.0)
    return float(np.degrees(np.arccos(cosine)))


def pick_side_point(landmarks, left_name: str, right_name: str, visibility_threshold: float = 0.5):
    """Pick whichever side (left/right) MediaPipe is more confident about.

    Uses x, y, and z (MediaPipe's relative depth) so the resulting angle is the
    true 3D joint angle, not a 2D projection that varies with hand placement
    (e.g. diamond vs. wide push-ups) or camera angle.
    """
    left = landmarks[LM[left_name]]
    right = landmarks[LM[right_name]]
    if left.visibility >= right.visibility and left.visibility >= visibility_threshold:
        return np.array([left.x, left.y, left.z])
    if right.visibility >= visibility_threshold:
        return np.array([right.x, right.y, right.z])
    # fall back to whichever is higher-confidence even if below threshold
    return np.array([left.x, left.y, left.z]) if left.visibility >= right.visibility else np.array([right.x, right.y, right.z])


def compute_frame_angles(landmarks, exercise: str) -> dict:
    """Given one frame's MediaPipe pose landmarks, return {angle_name: degrees}."""
    config = EXERCISE_CONFIGS[exercise]
    result = {}
    for angle_name, (a_names, b_names, c_names) in config["angles"].items():
        a = pick_side_point(landmarks, *a_names)
        b = pick_side_point(landmarks, *b_names)
        c = pick_side_point(landmarks, *c_names)
        result[angle_name] = calculate_angle(a, b, c)
    return result


def in_expected_position(landmarks, exercise: str, angle_tolerance_degrees: float = 40.0) -> bool:
    """Is the body actually oriented the way this exercise requires right now?

    This exists because a rep counter that only watches a joint angle can't
    tell the difference between "bending your elbow during an actual push-up"
    and "bending your elbow while standing up" — both cross the same angle
    range. Gate counting on body ORIENTATION (shoulder-hip line horizontal for
    push-ups, vertical for squats) so standing around, getting into position,
    or mimicking the motion off the floor doesn't get counted as a rep.
    """
    shoulder = pick_side_point(landmarks, "left_shoulder", "right_shoulder")[:2]
    hip = pick_side_point(landmarks, "left_hip", "right_hip")[:2]
    dx = abs(hip[0] - shoulder[0])
    dy = abs(hip[1] - shoulder[1])
    if dx + dy == 0:
        return False
    angle_from_horizontal = np.degrees(np.arctan2(dy, dx))

    expected = EXERCISE_CONFIGS[exercise]["body_orientation"]
    if expected == "horizontal":
        return bool(angle_from_horizontal <= angle_tolerance_degrees)
    return bool(angle_from_horizontal >= (90 - angle_tolerance_degrees))


def tracking_confidence(landmarks, exercise: str) -> float:
    """Average MediaPipe visibility score across the landmarks this exercise
    actually needs. Low confidence usually means occlusion (e.g. an arm
    covering the legs), baggy/dark clothing the model can't read body outline
    from, or dim lighting — not a real rep, just a bad estimate.
    """
    names = EXERCISE_CONFIGS[exercise]["tracking_landmarks"]
    return float(np.mean([landmarks[LM[name]].visibility for name in names]))


def primary_angle_confidence(landmarks, exercise: str) -> float:
    """Visibility of specifically the 3 points that drive the counted angle.

    tracking_confidence() averages over more landmarks, which can hide one
    badly-placed point (e.g. an elbow/wrist misdetected as being where a leg
    actually is under occlusion/dim light) behind good visibility elsewhere.
    This is the stricter, more targeted check: the weakest of the 3 points
    actually used to compute primary_angle for this frame.
    """
    a_names, b_names, c_names = EXERCISE_CONFIGS[exercise]["angles"][EXERCISE_CONFIGS[exercise]["primary_angle"]]
    def best_visibility(names):
        return max(landmarks[LM[n]].visibility for n in names)
    return float(min(best_visibility(a_names), best_visibility(b_names), best_visibility(c_names)))


def is_well_tracked(landmarks, exercise: str, threshold: float = 0.5) -> bool:
    return primary_angle_confidence(landmarks, exercise) >= threshold


def window_sequence(values: np.ndarray, window_size: int, step: int):
    """Slide fixed-size windows over a 1D/2D angle sequence for ML features.

    Returns a list of (start_idx, end_idx, window_array).
    """
    n = len(values)
    windows = []
    start = 0
    while start + window_size <= n:
        end = start + window_size
        windows.append((start, end, values[start:end]))
        start += step
    return windows
