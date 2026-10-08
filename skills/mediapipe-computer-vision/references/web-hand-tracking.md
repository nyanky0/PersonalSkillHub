# Web Hand Tracking with MediaPipe Tasks Vision (JavaScript)

## Overview
Browser-based hand landmark detection using MediaPipe Tasks Vision WASM + WebRTC `getUserMedia`. No Python/backend needed.

## CDN Imports
```html
<script type="module">
import { HandLandmarker, FilesetResolver } from 'https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@0.10.13';
```

## Initialization Pattern
```javascript
const vision = await FilesetResolver.forVisionTasks(
  'https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@0.10.13/wasm'
);

const handLandmarker = await HandLandmarker.createFromOptions(vision, {
  baseOptions: {
    modelAssetPath: 'https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/latest/hand_landmarker.task',
    delegate: 'GPU'  // GPU delegate if available, falls back to CPU
  },
  runningMode: 'VIDEO',  // 'IMAGE' | 'VIDEO' | 'LIVE_STREAM'
  numHands: 1,
  minHandDetectionConfidence: 0.7,
  minHandPresenceConfidence: 0.5,
  minTrackingConfidence: 0.5
});
```

## Per-Frame Detection (VIDEO mode)
```javascript
// video = HTMLVideoElement from getUserMedia
// timestamp_ms = performance.now() or frame_index * (1000/30)
const results = handLandmarker.detectForVideo(video, timestamp_ms);

if (results.landmarks.length > 0) {
  const lm = results.landmarks[0];  // 21 NormalizedLandmark {x, y, z}
  // x, y in [0,1] relative to video dimensions
  const thumbTip = lm[4];
  const indexTip = lm[8];
  const palmCenter = lm[9];
}
```

## Camera Access with Robust Fallback
```javascript
async function getCameraStream() {
  // 1. Enumerate devices first
  const devices = await navigator.mediaDevices.enumerateDevices();
  const videoDevices = devices.filter(d => d.kind === 'videoinput');
  if (videoDevices.length === 0) throw new Error('No camera found');
  
  // 2. Stop existing tracks
  if (video.srcObject) {
    video.srcObject.getTracks().forEach(t => t.stop());
  }
  
  // 3. Try constraints with fallback
  const constraintsList = [
    { video: { facingMode: 'user', width: { ideal: 1280 }, height: { ideal: 720 } } },
    { video: { facingMode: 'user' } },
    { video: { deviceId: { exact: videoDevices[0].deviceId } } }
  ];
  
  for (const constraints of constraintsList) {
    try {
      return await navigator.mediaDevices.getUserMedia({ ...constraints, audio: false });
    } catch (e) {
      console.warn('Camera constraint failed:', e.message);
    }
  }
  throw new Error('All camera constraints failed');
}
```

## Error Handling (User-Friendly)
```javascript
try {
  const stream = await getCameraStream();
  video.srcObject = stream;
  await video.play();
} catch (err) {
  let msg = err.message;
  if (msg.includes('NotAllowedError') || msg.includes('Permission')) {
    msg = 'Camera permission denied. Click 🔒 in address bar → Allow → Refresh.';
  } else if (msg.includes('NotFoundError') || msg.includes('OverconstrainedError')) {
    msg = 'No camera found or resolution not supported.';
  } else if (msg.includes('NotReadableError') || msg.includes('Could not start video source')) {
    msg = 'Camera busy by another app (Zoom/Teams). Close them and refresh.';
  }
  showError(msg);
}
```

## Coordinate Mapping (Video → Canvas)
```javascript
// video: HTMLVideoElement
// canvas: HTMLCanvasElement (same dimensions as video)
// Mirror for selfie view: ctx.scale(-1, 1); ctx.drawImage(video, -w, 0, w, h);

// Landmark to canvas coordinates (accounting for mirror):
const canvasX = canvas.width * (1 - landmark.x);  // mirror X
const canvasY = canvas.height * landmark.y;
```

## Performance Tips
- Use `VIDEO` mode for webcam (not `LIVE_STREAM` — simpler, no callback complexity)
- Reuse single `HandLandmarker` instance
- Limit `numHands: 1` for single-hand apps
- GPU delegate (`delegate: 'GPU'`) auto-fallbacks to CPU
- Model loads once, cached by browser (~10MB)
- Run detection in `requestAnimationFrame` loop, not `setInterval`

## Dual-Hand Gesture State Machine (proven pattern)
For 2-hand apps (e.g. "cast spell with both palms"), track per-hand state OUTSIDE the frame loop, not per-frame booleans. Pattern from a working 2-hand spell app:

```javascript
const handsState = [
  { active: false, x: 0, y: 0, progress: 0, pinchDist: 1 },
  { active: false, x: 0, y: 0, progress: 0, pinchDist: 1 }
];

// Per frame, per detected hand idx (0..numHands-1):
const isPinching = pinchDist < 0.055;              // normalized dist thumb(4)-index(8)
handsState[idx].active = isPinching;
handsState[idx].x = px;                            // palm landmark 9 → screen coords
handsState[idx].y = py;
if (isPinching) {
  if (handsState[idx].progress === 0) {
    // edge trigger: fire SFX / shockwave exactly once on gesture START
    playIgniteSFX(currentSpell);
  }
  handsState[idx].progress = Math.min(handsState[idx].progress + dt * 4, 1.0);  // ramp up
} else {
  handsState[idx].progress = Math.max(handsState[idx].progress - dt * 2.5, 0.0); // decay
}
// Undetected hands (idx >= detectedCount): decay progress too
```

Key insights:
- **progress (0→1) as smoothing ramp** — effect draws with `progress` scaling radius/alpha, so the circle "grows in" on pinch and "fades out" on release instead of popping. No debounce timers needed.
- **Edge trigger on `progress === 0`** — the one-shot event (sound, shockwave) fires exactly once at gesture start; checking `isPinching` alone would fire every frame.
- **`activeHandsList` pattern** — only hands with `progress > 0.5` count as "engaged"; with 2 engaged hands draw a dual-hand tether beam between their palm positions.
- Works the same in Python/OpenCV: keep per-hand state dict across frames, use the same progress ramp + edge trigger.

## Pitfall: Duplicate `const` Declaration Kills the Whole Script
A single `const X = ...` declared twice in the same scope throws `SyntaxError: Identifier 'X' has already been declared` — the ENTIRE script fails to parse, page renders blank with only the loading overlay stuck (no partial execution). Seen in a real 1130-line app: `const particles = []` at line ~372 AND again at line ~485 (with `MAX_PARTICLES` also doubled 200 vs 250) — second declaration was a leftover from copy-paste during a feature addition.

- Symptom: loading overlay never hides, console shows the SyntaxError, nothing renders.
- Detection: `grep -n "const particles" index.html` → 2 hits; any duplicated `const` in one scope.
- Fix: delete the duplicate block (or rename to `let` + merge if it's an intended extension).
- After any large edit, sanity-check: open the file in a browser and confirm the script actually ran (console clean, overlay hidden) — don't assume "looks fine" from reading.

## Complete Minimal Example
See `templates/web-hand-tracking-minimal.html` for a ready-to-serve file.