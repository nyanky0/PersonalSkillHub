# Python MediaPipe Tasks API — Hand Landmarker

Native Python implementation using `mediapipe==0.10.30` (Tasks API, NOT legacy `solutions.hands`).

## Install

```bash
pip install opencv-python-headless mediapipe==0.10.30 numpy
```

## Model

`hand_landmarker.task` — download from:
```
https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/latest/hand_landmarker.task
```

Place in same directory as script.

## Key API (VIDEO mode for stream)

```python
from mediapipe.tasks import python as mp_python
from mediapipe.tasks.python import vision
from mediapipe.tasks.python.vision import (
    HandLandmarker, HandLandmarkerOptions, HandLandmarkerResult
)
from mediapipe.tasks.python.vision.core.vision_task_running_mode import VisionTaskRunningMode
from mediapipe.tasks.python.core.base_options import BaseOptions
from mediapipe.tasks.python.vision.core.image import Image as MPImage
from mediapipe.tasks.python.vision.core.image import ImageFormat

base_options = BaseOptions(model_asset_path=MODEL_PATH)
options = HandLandmarkerOptions(
    base_options=base_options,
    running_mode=VisionTaskRunningMode.VIDEO,
    num_hands=1,
    min_hand_detection_confidence=0.7,
    min_hand_presence_confidence=0.5,
    min_tracking_confidence=0.5,
)
landmarker = HandLandmarker.create_from_options(options)

# In loop:
rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
mp_image = MPImage(image_format=ImageFormat.SRGB, data=rgb)
timestamp_ms = int(frame_idx * (1000 / 30))  # monotonic ms
result: HandLandmarkerResult = landmarker.detect_for_video(mp_image, timestamp_ms)

# result.hand_landmarks = list of NormalizedLandmark lists (x,y,z in 0..1)
```

## Landmark Indices (21 points)

| Index | Name | Use |
|-------|------|-----|
| 0 | Wrist | Reference |
| 4 | Thumb tip | Pinch detection |
| 8 | Index tip | Pinch detection |
| 9 | Middle MCP | Palm center |
| 12 | Middle tip | |
| 16 | Ring tip | |
| 20 | Pinky tip | |

## Pinch Gesture

```python
thumb_tip = (int(lm[4].x * w), int(lm[4].y * h))
index_tip = (int(lm[8].x * w), int(lm[8].y * h))
distance = math.hypot(thumb_tip[0] - index_tip[0], thumb_tip[1] - index_tip[1])
if distance < PINCH_THRESHOLD:  # e.g. 40px
    # trigger effect at palm center (landmark 9)
```

## ⚠️ WSL Limitation

**Webcam NOT accessible in WSL2** — no `/dev/video0` by default.
- Run Python script on **Windows native Python** (PowerShell/CMD)
- Or use video file input: `VIDEO_SOURCE = 'test_input.mp4'`
- Web version (this skill's main approach) runs in Windows browser via HTTP server — RECOMMENDED

## Full Working Example

See `magic_circle.py` in project root — complete Doctor Strange magic circle with:
- Real-time webcam feed (mirrored)
- Pinch gesture detection
- Multi-layer animated magic circle (gold/orange)
- Optional transparent PNG overlay (spell array)
- 60fps animation loop