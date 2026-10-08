"""
Minimal Hand Tracking Boilerplate — MediaPipe Tasks API + OpenCV
=================================================================
Copy this file and modify for your use case.
"""

import cv2
import math
from mediapipe.tasks.python.vision import HandLandmarker, HandLandmarkerOptions
from mediapipe.tasks.python.vision.core.vision_task_running_mode import VisionTaskRunningMode
from mediapipe.tasks.python.core.base_options import BaseOptions
from mediapipe.tasks.python.vision.core.image import Image as MPImage, ImageFormat


# ============================================================
# CONFIGURATION
# ============================================================
MODEL_PATH = "hand_landmarker.task"  # Download from GCS if missing
VIDEO_SOURCE = 0                      # 0 = webcam, or "video.mp4"
PINCH_THRESHOLD = 40                  # pixels for pinch gesture


# ============================================================
# HELPER FUNCTIONS
# ============================================================
def load_model():
    """Initialize HandLandmarker in VIDEO mode."""
    base_options = BaseOptions(model_asset_path=MODEL_PATH)
    options = HandLandmarkerOptions(
        base_options=base_options,
        running_mode=VisionTaskRunningMode.VIDEO,
        num_hands=1,
        min_hand_detection_confidence=0.7,
        min_hand_presence_confidence=0.5,
        min_tracking_confidence=0.5,
    )
    return HandLandmarker.create_from_options(options)


def get_landmark_px(landmark, w, h):
    """Convert normalized landmark to pixel coordinates."""
    return (int(landmark.x * w), int(landmark.y * h))


def draw_landmarks(frame, landmarks, w, h, connections=True):
    """Draw hand landmarks and connections on frame."""
    # Draw points
    for lm in landmarks:
        px, py = get_landmark_px(lm, w, h)
        cv2.circle(frame, (px, py), 4, (0, 255, 0), -1)

    # Draw connections (MediaPipe hand skeleton)
    if connections:
        HAND_CONNECTIONS = [
            (0, 1), (1, 2), (2, 3), (3, 4),        # thumb
            (0, 5), (5, 6), (6, 7), (7, 8),        # index
            (5, 9), (9, 10), (10, 11), (11, 12),   # middle
            (9, 13), (13, 14), (14, 15), (15, 16), # ring
            (13, 17), (17, 18), (18, 19), (19, 20),# pinky
            (0, 17),                                # palm
        ]
        for a, b in HAND_CONNECTIONS:
            pa = get_landmark_px(landmarks[a], w, h)
            pb = get_landmark_px(landmarks[b], w, h)
            cv2.line(frame, pa, pb, (255, 0, 0), 2)


def detect_pinch(landmarks, w, h, threshold=40):
    """Return (pinch_detected, thumb_tip, index_tip, palm_center)."""
    thumb = get_landmark_px(landmarks[4], w, h)   # THUMB_TIP
    index = get_landmark_px(landmarks[8], w, h)   # INDEX_FINGER_TIP
    palm  = get_landmark_px(landmarks[9], w, h)   # MIDDLE_FINGER_MCP
    dist = math.hypot(thumb[0] - index[0], thumb[1] - index[1])
    return dist < threshold, thumb, index, palm


def overlay_alpha(bg, overlay, x, y):
    """Alpha blend overlay (BGRA) onto background (BGR)."""
    h, w = overlay.shape[:2]
    x1, y1 = max(x, 0), max(y, 0)
    x2, y2 = min(x + w, bg.shape[1]), min(y + h, bg.shape[0])
    if x2 <= x1 or y2 <= y1:
        return bg
    crop = overlay[y1 - y:y2 - y, x1 - x:x2 - x]
    alpha = crop[:, :, 3:4] / 255.0
    bg[y1:y2, x1:x2] = (crop[:, :, :3] * alpha + bg[y1:y2, x1:x2] * (1 - alpha)).astype(bg.dtype)
    return bg


# ============================================================
# MAIN LOOP
# ============================================================
def main():
    # Check model
    import os
    if not os.path.exists(MODEL_PATH):
        print(f"[ERROR] Model not found: {MODEL_PATH}")
        print("Download from: https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/latest/hand_landmarker.task")
        return

    # Init
    landmarker = load_model()
    cap = cv2.VideoCapture(VIDEO_SOURCE)

    if not cap.isOpened():
        print(f"[ERROR] Cannot open video source: {VIDEO_SOURCE}")
        print("WSL users: use video file path instead of 0")
        landmarker.close()
        return

    print("Running... press 'q' to quit")
    frame_idx = 0

    while True:
        ok, frame = cap.read()
        if not ok:
            if isinstance(VIDEO_SOURCE, str):  # loop video file
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                continue
            break

        # Mirror for mirror-like feel
        frame = cv2.flip(frame, 1)
        h, w = frame.shape[:2]

        # Convert to MediaPipe Image
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_img = MPImage(image_format=ImageFormat.SRGB, data=rgb)

        # Timestamp for VIDEO mode
        timestamp_ms = int(frame_idx * 1000 / 30)  # assume 30 FPS
        frame_idx += 1

        # Detect
        result = landmarker.detect_for_video(mp_img, timestamp_ms)

        # Process results
        if result.hand_landmarks:
            for hand_lms in result.hand_landmarks:
                # Draw landmarks
                draw_landmarks(frame, hand_lms, w, h)

                # Pinch detection
                pinch, thumb, index, palm = detect_pinch(hand_lms, w, h, PINCH_THRESHOLD)

                # Visual: draw pinch line
                cv2.line(frame, thumb, index, (0, 0, 255), 3)

                if pinch:
                    # YOUR CUSTOM ACTION HERE
                    cv2.putText(frame, "PINCH!", (palm[0] - 40, palm[1] - 60),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
                    # Example: draw circle at palm
                    cv2.circle(frame, palm, 80, (0, 215, 255), 3, cv2.LINE_AA)

        # Show
        cv2.imshow("Hand Tracking", frame)

        # Exit
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Cleanup
    cap.release()
    cv2.destroyAllWindows()
    landmarker.close()


if __name__ == "__main__":
    main()