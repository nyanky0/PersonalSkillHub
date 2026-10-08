---
name: mediapipe-computer-vision
description: MediaPipe Tasks + OpenCV for real-time landmark detection.
trigger: Use when building real-time CV apps with MediaPipe + OpenCV on Linux/WSL/Windows.
---

# MediaPipe Computer Vision Skill

## Overview
MediaPipe Tasks API (v0.10.30+ / v1.0+) is the **only supported API** for landmark detection. The legacy `mp.solutions.hands` / `mp.solutions.pose` / `mp.solutions.face_mesh` was **removed in v1.0** and is not available on Python 3.14+ wheels.

## Core Pattern: Hand Landmarker (Tasks API)

```python
from mediapipe.tasks.python.vision import HandLandmarker, HandLandmarkerOptions
from mediapipe.tasks.python.vision.core.vision_task_running_mode import VisionTaskRunningMode
from mediapipe.tasks.python.core.base_options import BaseOptions
from mediapipe.tasks.python.vision.core.image import Image as MPImage, ImageFormat

# 1. Load model (.task file from Google Cloud Storage)
base_options = BaseOptions(model_asset_path="hand_landmarker.task")
options = HandLandmarkerOptions(
    base_options=base_options,
    running_mode=VisionTaskRunningMode.VIDEO,  # or IMAGE / LIVE_STREAM
    num_hands=1,
    min_hand_detection_confidence=0.7,
    min_hand_presence_confidence=0.5,
    min_tracking_confidence=0.5,
)
landmarker = HandLandmarker.create_from_options(options)

# 2. Per-frame processing (VIDEO mode needs timestamp_ms)
rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
mp_image = MPImage(image_format=ImageFormat.SRGB, data=rgb)
timestamp_ms = int(frame_idx * (1000 / 30))  # assume 30 FPS
result = landmarker.detect_for_video(mp_image, timestamp_ms)

# 3. Extract landmarks (normalized 0..1)
if result.hand_landmarks:
    lm = result.hand_landmarks[0]  # list of 21 NormalizedLandmark
    thumb_tip  = (lm[4].x * w, lm[4].y * h)   # landmark 4
    index_tip  = (lm[8].x * w, lm[8].y * h)   # landmark 8
    palm_center = (lm[9].x * w, lm[9].y * h)  # landmark 9 (MCP middle)
```

## Key Landmarks (Hand)
| Index | Name | Use Case |
|-------|------|----------|
| 0 | WRIST | Hand position anchor |
| 4 | THUMB_TIP | Pinch gesture (with 8) |
| 8 | INDEX_FINGER_TIP | Pinch / pointing |
| 9 | MIDDLE_FINGER_MCP | Palm center |
| 12 | MIDDLE_FINGER_TIP | |
| 16 | RING_FINGER_TIP | |
| 20 | PINKY_TIP | |

## Pinch Gesture Detection
```python
distance = math.hypot(thumb_tip[0] - index_tip[0], thumb_tip[1] - index_tip[1])
if distance < PINCH_THRESHOLD:  # ~40px at 640x480
    # trigger action
```

## Model Files (.task)
Download from Google Cloud Storage (auto on first run, or manual):
```
Hand:      https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/latest/hand_landmarker.task
Face:      https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/latest/face_landmarker.task
Pose:      https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker/float16/latest/pose_landmarker.task
Object:    https://storage.googleapis.com/mediapipe-models/object_detector/efficientdet_lite0/float16/latest/efficientdet_lite0.task
```
Place in working dir or pass full path to `BaseOptions(model_asset_path=...)`.

## WSL Webcam Limitation ⚠️
**WSL2 has no direct USB/webcam access** (no `/dev/video0`). Workarounds:
1. **Run on Windows native** (PowerShell/CMD with Windows Python) — recommended for webcam apps
2. **Use video file** as input: `VIDEO_SOURCE = "test_input.mp4"` in script
3. **USBIP / v4l2loopback** — complex, not recommended for dev

### WSL GUI Display Issue
`cv2.imshow()` requires an X server (VcXsrv/Xming) or WSLg running on Windows host.
- No X server → window never appears, program hangs on `waitKey()`
- Quick test: `cv2.VideoCapture("file.mp4")` + `cv2.imwrite()` works headless
- Fix: Install VcXsrv on Windows, set `export DISPLAY=:0` in WSL, or run on Windows native

### Video Source Pattern (Environment Variable)
```python
import os
VIDEO_SOURCE = os.environ.get("VIDEO_SOURCE", "test_input.mp4")  # default to video file
# Usage: VIDEO_SOURCE=0 python script.py  (webcam)
#        VIDEO_SOURCE="my.mp4" python script.py  (file)
```

## OpenCV Integration Patterns

### Alpha Blend Overlay (PNG with transparency)
```python
def overlay_image_alpha(bg, overlay, x, y):
    h, w = overlay.shape[:2]
    x1, y1 = max(x, 0), max(y, 0)
    x2, y2 = min(x + w, bg.shape[1]), min(y + h, bg.shape[0])
    if x2 <= x1 or y2 <= y1: return bg
    crop = overlay[y1-y:y2-y, x1-x:x2-x]
    alpha = crop[:, :, 3:4] / 255.0
    bg[y1:y2, x1:x2] = (crop[:, :, :3] * alpha + bg[y1:y2, x1:x2] * (1-alpha)).astype(np.uint8)
    return bg
```

### Rotate Image Without Cropping
```python
def rotate_image(img, angle):
    h, w = img.shape[:2]
    M = cv2.getRotationMatrix2D((w//2, h//2), angle, 1.0)
    cos, sin = abs(M[0,0]), abs(M[0,1])
    nW, nH = int(h*sin + w*cos), int(h*cos + w*sin)
    M[0,2] += nW/2 - w/2
    M[1,2] += nH/2 - h/2
    return cv2.warpAffine(img, M, (nW, nH))
```

## Dependencies (PEP 668: use venv)
```bash
python3 -m venv .venv
. .venv/bin/activate
pip install opencv-python-headless mediapipe==0.10.30 numpy
# mediapipe 0.10.30 is last version with Tasks API on Python 3.14
```

## Browser (JS) — MediaPipe Tasks on webcam
Client-side detection with `@mediapipe/tasks-vision` from CDN, no Python needed. Target: phone/PC on LAN, multi-spell overlays, dual-hand effects.

```html
<script type="module">
import { HandLandmarker, FilesetResolver } from 'https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@0.10.13';
// 1. init
const vision = await FilesetResolver.forVisionTasks('https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@0.10.13/wasm');
const handLandmarker = await HandLandmarker.createFromOptions(vision, {
  baseOptions: { modelAssetPath: 'https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/latest/hand_landmarker.task', delegate: 'GPU' },
  runningMode: 'VIDEO', numHands: 2,
  minHandDetectionConfidence: 0.65, minHandPresenceConfidence: 0.5, minTrackingConfidence: 0.5
});
// 2. camera
const stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: 'user', width: { ideal: 1280 }, height: { ideal: 720 } }, audio: false });
// 3. per frame (requestAnimationFrame): detectForVideo(video, performance.now())
//    pinch: normalized distance lm[4]–lm[8] < ~0.055 (JS landmarks are 0..1, NOT px — Python threshold ~40px)
//    mirroring: draw with ctx.scale(-1,1); palm x = videoWidth * (1 - palm.x)
</script>
```

Key differences vs Python: landmarks normalized 0..1 (threshold ~0.055, not 40px); model+wasm load from CDN; `detectForVideo(video, performance.now())` takes the live `<video>` element; motion-trail via translucent fill each frame; module script = top-level `const` is module-scoped (NOT on window — don't probe via `window.x`).

### JS browser bug class: duplicate module-scope declarations kill the whole script
A module script dies ENTIRELY on the first SyntaxError (blank page, loading overlay never clears, no interactive element). Two real bugs from the "Doctor Strange" spell engine:
1. **Duplicate `const` at top level** — same name declared twice (`const particles = []` at two places) = SyntaxError. Symptom: page totally dead. Fix: delete the stale duplicate (keep the one near its functions).
2. **Function called but never defined** — `drawParticles(ctx)` invoked in the render loop with no definition anywhere = ReferenceError every frame (only visible once a frame actually runs). Symptom: render loop crashes after camera init. Fix: define it (render `particles` array: globalAlpha=life, shadowBlur glow, arc at p.size*p.life, rotate by p.rotation).

Verification recipe (headless-safe, no webcam): extract the module script to a file, `node --check` for syntax; grep that each called function name has a `function name` definition; then serve + load in browser and confirm the loading overlay hides (init reached camera step) and no console errors besides the handled `getUserMedia` failure.

## Common Pitfalls
| Issue | Fix |
|-------|-----|
| `AttributeError: module 'mediapipe' has no attribute 'solutions'` | Use Tasks API (`HandLandmarker`), not `solutions.hands` |
| `ImportError: cannot import VisionTaskRunningMode` | Import from `vision_task_running_mode` submodule |
| `ImportError: cannot import BaseOptions` | Import from `base_options` submodule |
| `ImportError: cannot import Image/ImageFormat` | Import from `image` submodule |
| Webcam not found in WSL | Use video file or run on Windows host |
| Model file not found | Download `.task` from GCS URL above |
| **Browser: `NotReadableError: Could not start video source`** | Camera busy by another app (Zoom/Teams). Stop other apps, enumerate devices first, retry with loose constraints `{facingMode: 'user'}`, then specific `deviceId`. |
| **Browser: `NotAllowedError` / Permission denied** | User blocked camera. Guide to click 🔒 icon in address bar → Allow → Refresh. |
| **Browser: `OverconstrainedError`** | Camera doesn't support requested resolution. Fallback to no constraints. |

## References
- `references/hand-landmarker-api.md` — API reference extracted from test files
- `references/web-hand-tracking.md` — JS browser hand tracking (CDN, camera, dual-hand state machine, duplicate-const pitfall)
- `references/doctor-strange-hand-gesture.md` — full worked example (Python + JS dual-track spell engine, bugs fixed, headless verification recipe)
- `references/model-urls.md` — Official model download URLs
- `templates/hand-tracking-boilerplate.py` — Minimal starter template

## Related Skills
- `mlops/serving-llms-vllm` — for model serving (different domain)
- `software-development/systematic-debugging` — for debugging CV pipelines