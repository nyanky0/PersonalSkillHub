# Hand Landmarker API Reference (MediaPipe Tasks 0.10.30)

Extracted from `mediapipe/tasks/python/test/vision/hand_landmarker_test.py` and source.

## Main Classes

### HandLandmarker
```python
HandLandmarker.create_from_options(options: HandLandmarkerOptions) -> HandLandmarker
HandLandmarker.create_from_model_path(model_path: str) -> HandLandmarker
```

**Methods:**
- `detect(image: MPImage) -> HandLandmarkerResult` — IMAGE mode
- `detect_for_video(image: MPImage, timestamp_ms: int) -> HandLandmarkerResult` — VIDEO mode
- `detect_async(image: MPImage, timestamp_ms: int) -> None` — LIVE_STREAM mode (callback)
- `close() -> None` — release resources

### HandLandmarkerOptions
```python
HandLandmarkerOptions(
    base_options: BaseOptions,
    running_mode: VisionTaskRunningMode,  # VIDEO | IMAGE | LIVE_STREAM
    num_hands: int = 1,
    min_hand_detection_confidence: float = 0.5,
    min_hand_presence_confidence: float = 0.5,
    min_tracking_confidence: float = 0.5,
    result_callback: Optional[Callable] = None,  # for LIVE_STREAM
)
```

### HandLandmarkerResult
```python
HandLandmarkerResult(
    handedness: List[List[Category]],       # [[Category(index=0/1, score, display_name="Left"/"Right"), ...], ...]
    hand_landmarks: List[List[NormalizedLandmark]],  # 21 landmarks per hand
    hand_world_landmarks: List[List[Landmark]],      # 3D world coords
)
```

### NormalizedLandmark (2D)
```python
NormalizedLandmark(x: float, y: float, z: float, visibility: float, presence: float)
# x, y in [0, 1] relative to image width/height
# z: depth, smaller = closer to camera
```

### Landmark (3D World)
```python
Landmark(x: float, y: float, z: float, visibility: float, presence: float)
# x, y, z in meters, origin at wrist
```

### Category (Handedness)
```python
Category(index: int, score: float, display_name: str, category_name: str)
# index: 0=Right, 1=Left (MediaPipe convention)
# display_name: "Right" or "Left"
```

### VisionTaskRunningMode
```python
class VisionTaskRunningMode(Enum):
    IMAGE = 0
    VIDEO = 1
    LIVE_STREAM = 2
```

## Landmark Indices (21 points)

| Index | Constant | Description |
|-------|----------|-------------|
| 0 | WRIST | Hand root |
| 1 | THUMB_CMC | Thumb base |
| 2 | THUMB_MCP | Thumb knuckle |
| 3 | THUMB_IP | Thumb interphalangeal |
| 4 | THUMB_TIP | **Thumb tip** (pinch) |
| 5 | INDEX_FINGER_MCP | Index knuckle |
| 6 | INDEX_FINGER_PIP | Index PIP |
| 7 | INDEX_FINGER_DIP | Index DIP |
| 8 | INDEX_FINGER_TIP | **Index tip** (pinch/point) |
| 9 | MIDDLE_FINGER_MCP | **Middle MCP** (palm center) |
| 10 | MIDDLE_FINGER_PIP | Middle PIP |
| 11 | MIDDLE_FINGER_DIP | Middle DIP |
| 12 | MIDDLE_FINGER_TIP | Middle tip |
| 13 | RING_FINGER_MCP | Ring MCP |
| 14 | RING_FINGER_PIP | Ring PIP |
| 15 | RING_FINGER_DIP | Ring DIP |
| 16 | RING_FINGER_TIP | Ring tip |
| 17 | PINKY_MCP | Pinky MCP |
| 18 | PINKY_PIP | Pinky PIP |
| 19 | PINKY_DIP | Pinky DIP |
| 20 | PINKY_TIP | Pinky tip |

## Import Paths (critical — submodules, not top-level)
```python
from mediapipe.tasks.python.vision import HandLandmarker, HandLandmarkerOptions
from mediapipe.tasks.python.vision.core.vision_task_running_mode import VisionTaskRunningMode
from mediapipe.tasks.python.core.base_options import BaseOptions
from mediapipe.tasks.python.vision.core.image import Image as MPImage, ImageFormat
```

## Running Modes Comparison

| Mode | Use Case | Timestamp Required | Callback |
|------|----------|-------------------|----------|
| IMAGE | Single images | No | No |
| VIDEO | Video files / pre-recorded | Yes (ms) | No |
| LIVE_STREAM | Real-time webcam | Yes (ms) | Yes (async) |

## Confidence Thresholds (recommended)
- `min_hand_detection_confidence`: 0.7 (reduce false positives)
- `min_hand_presence_confidence`: 0.5
- `min_tracking_confidence`: 0.5 (tracking between frames)

## Example: Minimal Working Script
```python
import cv2
from mediapipe.tasks.python.vision import HandLandmarker, HandLandmarkerOptions
from mediapipe.tasks.python.vision.core.vision_task_running_mode import VisionTaskRunningMode
from mediapipe.tasks.python.core.base_options import BaseOptions
from mediapipe.tasks.python.vision.core.image import Image as MPImage, ImageFormat

landmarker = HandLandmarker.create_from_model_path("hand_landmarker.task")
cap = cv2.VideoCapture(0)
frame_idx = 0

while True:
    ok, frame = cap.read()
    if not ok: break
    frame = cv2.flip(frame, 1)
    h, w = frame.shape[:2]
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    mp_img = MPImage(image_format=ImageFormat.SRGB, data=rgb)
    ts = int(frame_idx * 1000 / 30)
    frame_idx += 1
    result = landmarker.detect_for_video(mp_img, ts)
    if result.hand_landmarks:
        lm = result.hand_landmarks[0]
        print(f"Thumb: {lm[4].x:.3f},{lm[4].y:.3f}  Index: {lm[8].x:.3f},{lm[8].y:.3f}")
    cv2.imshow("Hand", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'): break

cap.release()
cv2.destroyAllWindows()
landmarker.close()
```