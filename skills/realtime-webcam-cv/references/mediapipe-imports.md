# MediaPipe Tasks Vision — Verified Import Paths (v0.10.13)

Tested and working as of this session. MediaPipe breaks imports between versions — pin exactly.

## CDN (ES Modules, no build step)

```html
<script type="module">
import { HandLandmarker, FilesetResolver } 
  from 'https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@0.10.13';

const vision = await FilesetResolver.forVisionTasks(
  'https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@0.10.13/wasm'
);

const landmarker = await HandLandmarker.createFromOptions(vision, {
  baseOptions: {
    modelAssetPath: 'https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/latest/hand_landmarker.task',
    delegate: 'GPU'
  },
  runningMode: 'VIDEO',
  numHands: 1,
  minHandDetectionConfidence: 0.7,
  minHandPresenceConfidence: 0.5,
  minTrackingConfidence: 0.5
});
</script>
```

## NPM (with bundler: Vite, Webpack, etc.)

```bash
npm i @mediapipe/tasks-vision@0.10.13
```

```js
import { HandLandmarker, FilesetResolver } from '@mediapipe/tasks-vision';

const vision = await FilesetResolver.forVisionTasks(
  // WASM files must be copied to public/ or served statically
  // Vite: place in public/wasm/ and reference '/wasm/'
  '/wasm/'
);

const landmarker = await HandLandmarker.createFromOptions(vision, {
  baseOptions: {
    modelAssetPath: '/models/hand_landmarker.task',  // copy to public/models/
    delegate: 'GPU'
  },
  runningMode: 'VIDEO',
  numHands: 1,
  minHandDetectionConfidence: 0.7,
  minHandPresenceConfidence: 0.5,
  minTrackingConfidence: 0.5
});
```

### Vite config for WASM + model

```js
// vite.config.js
export default {
  publicDir: 'public',
  build: {
    rollupOptions: {
      output: {
        manualChunks: undefined
      }
    }
  }
};
// Copy @mediapipe/tasks-vision/wasm/* to public/wasm/
// Copy hand_landmarker.task to public/models/
```

## Model URLs (Google Cloud Storage, stable)

| Task | Model URL |
|------|-----------|
| Hand Landmarker | `https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/latest/hand_landmarker.task` |
| Face Landmarker | `https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/latest/face_landmarker.task` |
| Pose Landmarker (Lite) | `https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_lite/float16/latest/pose_landmarker_lite.task` |
| Pose Landmarker (Full) | `https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_full/float16/latest/pose_landmarker_full.task` |
| Pose Landmarker (Heavy) | `https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_heavy/float16/latest/pose_landmarker_heavy.task` |

## Running Modes

| Mode | Use Case | Method |
|------|----------|--------|
| `IMAGE` | Single image | `detect(image)` |
| `VIDEO` | Video stream / webcam | `detectForVideo(video, timestampMs)` |
| `LIVE_STREAM` | Async callbacks | `detectAsync(image, timestampMs)` + `resultCallback` |

**For webcam: always `VIDEO` mode with `performance.now()` timestamp.**

## Landmark Indices (Hand, 21 points)

| Index | Name | Description |
|-------|------|-------------|
| 0 | WRIST | Root |
| 1 | THUMB_CMC | Thumb base |
| 2 | THUMB_MCP | Thumb knuckle |
| 3 | THUMB_IP | Thumb joint |
| 4 | THUMB_TIP | **Thumb tip** |
| 5 | INDEX_FINGER_MCP | Index knuckle |
| 6 | INDEX_FINGER_PIP | Index joint |
| 7 | INDEX_FINGER_DIP | Index joint |
| 8 | INDEX_FINGER_TIP | **Index tip** |
| 9 | MIDDLE_FINGER_MCP | **Palm center (MCP)** |
| 10 | MIDDLE_FINGER_PIP | Middle joint |
| 11 | MIDDLE_FINGER_DIP | Middle joint |
| 12 | MIDDLE_FINGER_TIP | Middle tip |
| 13 | RING_FINGER_MCP | Ring knuckle |
| 14 | RING_FINGER_PIP | Ring joint |
| 15 | RING_FINGER_DIP | Ring joint |
| 16 | RING_FINGER_TIP | Ring tip |
| 17 | PINKY_MCP | Pinky knuckle |
| 18 | PINKY_PIP | Pinky joint |
| 19 | PINKY_DIP | Pinky joint |
| 20 | PINKY_TIP | Pinky tip |

## Common Landmark References

```js
const landmarks = results.landmarks[0];  // NormalizedLandmark[] (x,y,z in 0..1)

// Key points
const thumbTip = landmarks[4];
const indexTip = landmarks[8];
const middleTip = landmarks[12];
const ringTip = landmarks[16];
const pinkyTip = landmarks[20];
const palmCenter = landmarks[9];        // Middle MCP — best palm proxy
const wrist = landmarks[0];
const indexMcp = landmarks[5];
const middleMcp = landmarks[9];
const ringMcp = landmarks[13];
const pinkyMcp = landmarks[17];
```

## Normalized → Pixel Conversion

```js
// Video is MIRRORED via ctx.scale(-1, 1)
const cx = videoWidth * (1 - landmark.x);   // flip X
const cy = videoHeight * landmark.y;        // Y as-is
const cz = landmark.z;                      // relative depth (negative = closer)
```

## Delegates

| Delegate | Backend | Performance | Fallback |
|----------|---------|-------------|----------|
| `'GPU'` | WebGL2 | Best | Auto CPU |
| `'CPU'` | WASM (XNNPACK) | Good | — |
| `'AUTO'` | Browser chooses | — | — |

Check console: "Created TensorFlow Lite XNNPACK delegate for CPU" = CPU fallback active.

## Version Compatibility Matrix

| Package | Version | Notes |
|---------|---------|-------|
| `@mediapipe/tasks-vision` | 0.10.13 | Current stable web |
| `@mediapipe/tasks-vision` | 0.10.0-0.10.12 | Older, similar API |
| `mediapipe` (Python) | 0.10.x | Has `solutions.hands` |
| `mediapipe` (Python) | 1.0.x | **Breaking** — no `solutions`, only `tasks` |

**Python 1.x and Web 0.10.x are different APIs** — do not mix patterns.