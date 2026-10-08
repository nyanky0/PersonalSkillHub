# MediaPipe Model URLs (Official Google Cloud Storage)

All models are hosted at `https://storage.googleapis.com/mediapipe-models/`
Float16 versions balance accuracy and size (~2-12 MB each).

## Hand Landmarker
- **hand_landmarker.task** (21 hand landmarks)
  - URL: `https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/latest/hand_landmarker.task`
  - Size: ~7.5 MB

## Face Landmarker
- **face_landmarker.task** (478 face landmarks)
  - URL: `https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/latest/face_landmarker.task`
  - Size: ~12 MB

- **face_landmarker_with_blendshapes.task** (478 landmarks + 52 blendshapes)
  - URL: `https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker_with_blendshapes/float16/latest/face_landmarker_with_blendshapes.task`
  - Size: ~12 MB

## Pose Landmarker
- **pose_landmarker_lite.task** (33 pose landmarks, lightweight)
  - URL: `https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_lite/float16/latest/pose_landmarker_lite.task`
  - Size: ~5 MB

- **pose_landmarker_full.task** (33 pose landmarks, higher accuracy)
  - URL: `https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_full/float16/latest/pose_landmarker_full.task`
  - Size: ~10 MB

- **pose_landmarker_heavy.task** (33 pose landmarks, highest accuracy)
  - URL: `https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_heavy/float16/latest/pose_landmarker_heavy.task`
  - Size: ~25 MB

## Object Detector
- **efficientdet_lite0.task** (80 COCO classes, fast)
  - URL: `https://storage.googleapis.com/mediapipe-models/object_detector/efficientdet_lite0/float16/latest/efficientdet_lite0.task`
  - Size: ~5 MB

- **efficientdet_lite2.task** (80 COCO classes, more accurate)
  - URL: `https://storage.googleapis.com/mediapipe-models/object_detector/efficientdet_lite2/float16/latest/efficientdet_lite2.task`
  - Size: ~15 MB

## Gesture Recognizer
- **gesture_recognizer.task** (hand gestures: thumbs_up, victory, etc.)
  - URL: `https://storage.googleapis.com/mediapipe-models/gesture_recognizer/gesture_recognizer/float16/latest/gesture_recognizer.task`
  - Size: ~8 MB

## Image Classifier
- **efficientnet_lite0.task** (1000 ImageNet classes)
  - URL: `https://storage.googleapis.com/mediapipe-models/image_classifier/efficientnet_lite0/float16/latest/efficientnet_lite0.task`
  - Size: ~8 MB

## Image Segmenter
- **deeplab_v3.task** (semantic segmentation)
  - URL: `https://storage.googleapis.com/mediapipe-models/image_segmenter/deeplab_v3/float16/latest/deeplab_v3.task`
  - Size: ~20 MB

---

## Download Helper (Python)

```python
import urllib.request
import os

MODEL_URLS = {
    "hand_landmarker.task": "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/latest/hand_landmarker.task",
    "face_landmarker.task": "https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/latest/face_landmarker.task",
    "pose_landmarker_lite.task": "https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_lite/float16/latest/pose_landmarker_lite.task",
    "efficientdet_lite0.task": "https://storage.googleapis.com/mediapipe-models/object_detector/efficientdet_lite0/float16/latest/efficientdet_lite0.task",
    "gesture_recognizer.task": "https://storage.googleapis.com/mediapipe-models/gesture_recognizer/gesture_recognizer/float16/latest/gesture_recognizer.task",
}

def download_model(name, dest_dir="."):
    url = MODEL_URLS.get(name)
    if not url:
        raise ValueError(f"Unknown model: {name}")
    path = os.path.join(dest_dir, name)
    if os.path.exists(path):
        print(f"Already exists: {path}")
        return path
    print(f"Downloading {name}...")
    urllib.request.urlretrieve(url, path)
    print(f"Saved to {path}")
    return path

# Usage
download_model("hand_landmarker.task")
```

## Download Helper (Shell)

```bash
# Hand landmarker
wget -q https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/latest/hand_landmarker.task -O hand_landmarker.task

# Face landmarker
wget -q https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/latest/face_landmarker.task -O face_landmarker.task

# Pose landmarker (lite)
wget -q https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_lite/float16/latest/pose_landmarker_lite.task -O pose_landmarker_lite.task

# Object detector
wget -q https://storage.googleapis.com/mediapipe-models/object_detector/efficientdet_lite0/float16/latest/efficientdet_lite0.task -O efficientdet_lite0.task
```

## Notes
- Models are versioned by MediaPipe; `latest` redirects to current stable
- Float16 = 16-bit quantization (good accuracy/size tradeoff)
- Some models have INT8 variants for mobile (smaller, less accurate)
- License: Apache 2.0 (check MediaPipe terms for commercial use)