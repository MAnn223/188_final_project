"""
Hand Gesture Detector - Open / Closed Hand
Uses the NEW MediaPipe Tasks API (mediapipe >= 0.10).

Install dependencies:
    pip install mediapipe opencv-python

Usage:
    python hand_gesture_detector.py

The GestureDetector class can be imported and polled from your robosuite loop.
"""

import cv2
import mediapipe as mp
from mediapipe.tasks import python as mp_python
from mediapipe.tasks.python import vision as mp_vision
import urllib.request
import os
import subprocess
subprocess.run(["python3", "-c", "import cv2; cv2.VideoCapture(0)"])
# ── Download the hand landmarker model if not present ────────────────────────
MODEL_PATH = os.path.expanduser("~/hand_landmarker.task")
MODEL_URL  = "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/latest/hand_landmarker.task"

def _ensure_model():
    if not os.path.exists(MODEL_PATH):
        print(f"Downloading hand landmarker model to '{MODEL_PATH}' …")
        urllib.request.urlretrieve(MODEL_URL, MODEL_PATH)
        print("Download complete.")

# ── Landmark indices ──────────────────────────────────────────────────────────
FINGER_TIPS = [8, 12, 16, 20]   # index, middle, ring, pinky tips
FINGER_PIPS = [6, 10, 14, 18]   # corresponding PIP joints
THUMB_TIP   = 4
THUMB_IP    = 3


def _fingers_extended(landmarks) -> list:
    """Return [thumb, index, middle, ring, pinky] booleans."""
    extended = []
    # Thumb: tip x < IP x (works on mirrored frame)
    extended.append(landmarks[THUMB_TIP].x < landmarks[THUMB_IP].x)
    # Four fingers: tip y < pip y means finger is pointing up / extended
    for tip, pip in zip(FINGER_TIPS, FINGER_PIPS):
        extended.append(landmarks[tip].y < landmarks[pip].y)
    return extended


def classify_gesture(landmarks) -> str:
    """Returns 'OPEN', 'CLOSED', or 'OTHER'."""
    ext   = _fingers_extended(landmarks)
    count = sum(ext)
    if count >= 4:
        return "OPEN"
    elif count <= 1:
        return "CLOSED"
    return "OTHER"


# ── Drawing helper (no longer needs mp.solutions) ────────────────────────────
HAND_CONNECTIONS = [
    (0,1),(1,2),(2,3),(3,4),
    (0,5),(5,6),(6,7),(7,8),
    (5,9),(9,10),(10,11),(11,12),
    (9,13),(13,14),(14,15),(15,16),
    (13,17),(17,18),(18,19),(19,20),
    (0,17),
]

def _draw_landmarks(frame, landmarks):
    h, w = frame.shape[:2]
    pts = [(int(lm.x * w), int(lm.y * h)) for lm in landmarks]
    for a, b in HAND_CONNECTIONS:
        cv2.line(frame, pts[a], pts[b], (0, 220, 0), 2)
    for x, y in pts:
        cv2.circle(frame, (x, y), 5, (255, 255, 255), -1)
        cv2.circle(frame, (x, y), 5, (0, 150, 0), 1)


class GestureDetector:
    """
    Poll-based gesture detector for use in a robosuite control loop:

        detector = GestureDetector()
        while True:
            gesture = detector.get_gesture()  # 'OPEN' | 'CLOSED' | 'OTHER' | None
        detector.release()
    """

    def __init__(self, camera_index: int = 0, min_detection_confidence: float = 0.7):
        _ensure_model()
        base_opts = mp_python.BaseOptions(model_asset_path=MODEL_PATH)
        opts = mp_vision.HandLandmarkerOptions(
            base_options=base_opts,
            num_hands=1,
            min_hand_detection_confidence=min_detection_confidence,
            min_hand_presence_confidence=0.5,
            min_tracking_confidence=0.5,
            running_mode=mp_vision.RunningMode.IMAGE,
        )
        self._detector = mp_vision.HandLandmarker.create_from_options(opts)
        self._cap = cv2.VideoCapture(camera_index)
        self.gesture = None

    def get_gesture(self):
        """Read one webcam frame and return the detected gesture string."""
        ok, frame = self._cap.read()
        if not ok:
            return None
        frame  = cv2.flip(frame, 1)
        rgb    = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_img = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
        result = self._detector.detect(mp_img)

        if result.hand_landmarks:
            self.gesture = classify_gesture(result.hand_landmarks[0])
        else:
            self.gesture = None
        return self.gesture

    def release(self):
        self._cap.release()
        self._detector.close()


def run_demo():
    _ensure_model()
    cap = cv2.VideoCapture(0)

    base_opts = mp_python.BaseOptions(model_asset_path=MODEL_PATH)
    opts = mp_vision.HandLandmarkerOptions(
        base_options=base_opts,
        num_hands=1,
        min_hand_detection_confidence=0.7,
        min_hand_presence_confidence=0.5,
        min_tracking_confidence=0.5,
        running_mode=mp_vision.RunningMode.IMAGE,
    )
    detector = mp_vision.HandLandmarker.create_from_options(opts)

    COLOURS = {
        "OPEN":   (0, 200, 0),
        "CLOSED": (0, 0, 220),
        "OTHER":  (0, 165, 255),
        "-":      (180, 180, 180),
    }

    print("Press  Q  to quit.")
    print("OPEN = open hand  |  CLOSED = fist\n")

    while True:
        ok, frame = cap.read()
        if not ok:
            break

        frame  = cv2.flip(frame, 1)
        rgb    = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_img = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
        result = detector.detect(mp_img)

        gesture = "-"
        if result.hand_landmarks:
            lms     = result.hand_landmarks[0]
            gesture = classify_gesture(lms)
            _draw_landmarks(frame, lms)

        colour = COLOURS[gesture]
        cv2.putText(frame, f"Gesture: {gesture}", (20, 55),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.5, colour, 3)

        cv2.imshow("Hand Gesture Detector  (Q to quit)", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    detector.close()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    run_demo()