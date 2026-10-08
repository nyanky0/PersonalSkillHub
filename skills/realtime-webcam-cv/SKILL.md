---
name: realtime-webcam-cv
description: Webcam CV effects via MediaPipe WASM + Canvas.
version: 1.0.0
tags: [webcam, mediapipe, wasm, canvas, computer-vision, hand-tracking, gesture, animation]
platforms: [linux, macos, windows]
triggers:
  - webcam hand tracking in browser
  - mediapipe tasks vision wasm
  - real-time gesture detection web
  - canvas animation over webcam feed
  - doctor strange magic circle effect
  - interactive webcam effects
---

# Real-time Webcam Computer Vision Effects (Browser)

Build interactive webcam effects using **MediaPipe Tasks Vision (WASM)** + `getUserMedia` + Canvas 2D. Runs entirely client-side, no server needed.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  Browser                                                    │
│  ┌──────────────┐    ┌─────────────────┐    ┌────────────┐  │
│  │ getUserMedia │───▶│ HandLandmarker  │───▶│ Canvas 2D  │  │
│  │ (webcam)     │    │ (WASM model)    │    │ (render)   │  │
│  └──────────────┘    └─────────────────┘    └────────────┘  │
│         │                    │                      │        │
│         ▼                    ▼                      ▼        │
│  MediaStream          .task model           requestAnimationFrame
│  (video element)      (GPU delegate)         60fps loop
└─────────────────────────────────────────────────────────────┘
```

## Core Setup (Minimal Boilerplate)

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

// In render loop:
const results = landmarker.detectForVideo(videoElement, performance.now());
// results.landmarks[0] = array of 21 NormalizedLandmark {x,y,z} (0..1)
</script>
```

## Critical Pitfalls (learned the hard way)

### 1. **ES Modules + WASM + getUserMedia require HTTP(S)**
- `file://` opens fail: CORS blocks WASM load, `getUserMedia` requires secure context
- **Must serve via local server**: `python3 -m http.server 8080` or `npx serve` or VS Code Live Server
- `localhost` works for dev; production needs HTTPS

### 2. **MediaPipe API versions are NOT compatible**
- `mediapipe@1.x` (Python) ≠ `@mediapipe/tasks-vision@0.10.x` (Web)
- Web uses **Tasks Vision API** (`HandLandmarker`, `FaceLandmarker`, `PoseLandmarker`)
- Old `solutions.hands` (Python) has no direct web equivalent — use Tasks
- Import paths are specific: CDN as above or npm `mediapipe/tasks/vision/hand_landmarker`

### 3. **`detectForVideo` requires monotonic timestamp (ms)**
```js
// CORRECT
landmarker.detectForVideo(video, performance.now());

// WRONG - breaks tracking
landmarker.detectForVideo(video, frameIndex);
landmarker.detectForVideo(video, Date.now());
```

### 4. **Mirror the video for "selfie" UX**
```js
ctx.save();
ctx.scale(-1, 1);
ctx.drawImage(video, -w, 0, w, h);
ctx.restore();
// Landmark x from LEFT — mirror: cx = w * (1 - lm.x)
```

### 5. **Normalized landmarks → canvas pixels**
```js
const cx = canvasWidth * (1 - landmark.x);   // mirrored X
const cy = canvasHeight * landmark.y;        // Y unchanged
```

### 6. **GPU delegate optional but recommended**
```js
delegate: 'GPU'  // WebGL2; auto-fallback to CPU
```

### 7. **Model loads once, caches in browser**
- First load: ~15MB total, 3-5s
- Subsequent: instant from cache
- Show loading UI until `createFromOptions` resolves

## Gesture Detection Patterns

### Pinch (thumb tip + index tip)
```js
const thumb = landmarks[4];
const index = landmarks[8];
const dist = Math.hypot(thumb.x - index.x, thumb.y - index.y);
if (dist < 0.045) { /* trigger */ }
```

### Palm center
```js
const palm = landmarks[9];  // middle finger MCP
```

### Fist (all fingertips near palm)
```js
const tips = [4, 8, 12, 16, 20];
const palm = landmarks[0];
const isFist = tips.every(i => 
  Math.hypot(landmarks[i].x - palm.x, landmarks[i].y - palm.y) < 0.15
);
```

### Pointing (index extended, others curled)
```js
const indexTip = landmarks[8];
const indexMcp = landmarks[5];
const middleTip = landmarks[12];
const isPointing = 
  (indexTip.y < indexMcp.y - 0.05) &&  // index up
  (middleTip.y > landmarks[9].y);      // middle down
```

## Animation Loop Best Practices

```js
let lastTime = 0;
function render(time) {
  const dt = (time - lastTime) / 1000;
  lastTime = time;
  
  ctx.clearRect(0, 0, w, h);
  ctx.save(); ctx.scale(-1, 1);
  ctx.drawImage(video, -w, 0, w, h);
  ctx.restore();
  
  const results = landmarker.detectForVideo(video, performance.now());
  if (results.landmarks.length) {
    drawEffects(ctx, results.landmarks[0], time, dt);
  }
  
  updateParticles(dt);
  drawParticles(ctx);
  
  requestAnimationFrame(render);
}
```

## Sacred Geometry / Complex Animation Reference

See `references/doctor-strange-shield.md` for complete 9-layer Doctor Strange shield:
- Concentric counter-rotating rings (dashed, glowing)
- Sacred polygons (hexagram, dual triangles, pentagon, center triangle)
- Glyph/rune rings at multiple radii
- 8-fold mandala with breathing animation
- Pulsing central core with radial gradient
- Particle burst on activation
- Smooth activation/deactivation progress (0→1)

Key techniques:
- `ctx.shadowBlur` + `ctx.shadowColor` for glow (cheap, no shaders)
- `ctx.setLineDash()` + `lineDashOffset` for rotating dashes
- `Math.sin(time * freq)` for breathing/pulsing
- Separate rotation speeds per layer
- `progress` parameter (0-1) for fade-in/out without popping

## Performance Notes

| Technique | Cost | Notes |
|-----------|------|-------|
| Canvas 2D + shadowBlur | Low-Med | GPU accelerated; 60fps at 1280×720 |
| OffscreenCanvas + Worker | Low | Move detection off main thread |
| WebGL shaders | Lowest | For 1000+ particles |
| Reduce `numHands` | - | Default 1; linear cost |
| Lower video resolution | - | 640×480 often enough |

## Browser Support (2024+)

| Feature | Chrome | Firefox | Safari | Edge |
|---------|--------|---------|--------|------|
| getUserMedia | ✅ | ✅ | ✅ | ✅ |
| WASM (MediaPipe) | ✅ | ✅ | ✅ | ✅ |
| WebGL2 (GPU delegate) | ✅ | ✅ | ✅ | ✅ |
| OffscreenCanvas | ✅ | ✅ | ⚠️ | ✅ |

## References

- `references/doctor-strange-shield.md` — 9-layer sacred geometry implementation
- `references/mediapipe-imports.md` — Verified import paths for 0.10.13
- `references/python-mediapipe-tasks.md` — Python Tasks API (mediapipe 0.10.30), WSL limitations
- `templates/hand-tracking-boilerplate.html` — Minimal working starter
- MediaPipe Tasks Vision docs: https://developers.google.com/edge/mediapipe/solutions/vision/hand_landmarker/web_js