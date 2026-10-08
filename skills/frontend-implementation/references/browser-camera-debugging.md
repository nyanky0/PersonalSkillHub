# Browser Camera Access Troubleshooting (getUserMedia + MediaPipe)

## Common Errors & Fixes

| Error | Cause | Fix |
|-------|-------|-----|
| `NotAllowedError` / `PermissionDeniedError` | User blocked camera permission | Guide user: click 🔒/📷 icon in address bar → Allow → Refresh page |
| `NotReadableError: Could not start video source` | Camera busy by another app (Zoom, Teams, Meet, OBS, Discord, Chrome tab) | Close ALL apps using camera → Refresh page |
| `NotFoundError` | No camera hardware detected / disabled in BIOS / privacy settings | Check Windows Settings → Privacy & Security → Camera → "Camera access" = On, "Let apps access your camera" = On, Desktop apps = On |
| `OverconstrainedError` | Requested resolution/framerate not supported by camera | Fallback: try `{facingMode: 'user'}` (no constraints), then specific `deviceId` |
| `AbortError` | Stream stopped / track ended before use | Re-request stream, ensure video element stays attached |
| `TypeError: Failed to execute 'getUserMedia'` | Insecure context (not HTTPS, not localhost) | Must serve via `localhost` or HTTPS — `file://` or bare IP won't work |

## Robust Camera Initialization Pattern

```javascript
async function getCameraStream(videoEl) {
  // 1. Enumerate devices first
  const devices = await navigator.mediaDevices.enumerateDevices();
  const videoDevices = devices.filter(d => d.kind === 'videoinput');
  if (videoDevices.length === 0) {
    throw new Error('NotFoundError: No camera devices found');
  }
  console.log('Available cameras:', videoDevices.map(d => d.label || d.deviceId));
  
  // 2. Stop any existing tracks
  if (videoEl.srcObject) {
    videoEl.srcObject.getTracks().forEach(t => t.stop());
  }
  
  // 3. Try constraints with progressive fallback
  const constraintsList = [
    // Attempt 1: Ideal HD
    { video: { facingMode: 'user', width: { ideal: 1280 }, height: { ideal: 720 } } },
    // Attempt 2: Loose constraints
    { video: { facingMode: 'user' } },
    // Attempt 3: Specific device (first available)
    { video: { deviceId: { exact: videoDevices[0].deviceId } } }
  ];
  
  let lastError;
  for (let i = 0; i < constraintsList.length; i++) {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        ...constraintsList[i],
        audio: false
      });
      console.log(`Camera initialized with constraints attempt ${i + 1}`);
      return stream;
    } catch (e) {
      lastError = e;
      console.warn(`Camera attempt ${i + 1} failed:`, e.name, e.message);
      if (i < constraintsList.length - 1) {
        await new Promise(r => setTimeout(r, 500 * (i + 1))); // brief delay before retry
      }
    }
  }
  throw lastError || new Error('All camera constraints failed');
}
```

## Waiting for Video Ready

```javascript
video.srcObject = stream;

// Wait for metadata (dimensions known) before play()
await new Promise((resolve, reject) => {
  video.onloadedmetadata = () => resolve();
  video.onerror = reject;
  setTimeout(() => reject(new Error('Video load timeout')), 10000);
});

await video.play(); // Must await in some browsers
```

## MediaPipe Tasks Vision + WebRTC Integration

```javascript
import { HandLandmarker, FilesetResolver } from 'https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@0.10.13';

const vision = await FilesetResolver.forVisionTasks(
  'https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@0.10.13/wasm'
);

const handLandmarker = await HandLandmarker.createFromOptions(vision, {
  baseOptions: {
    modelAssetPath: 'https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/latest/hand_landmarker.task',
    delegate: 'GPU'  // Auto-fallbacks to CPU
  },
  runningMode: 'VIDEO',
  numHands: 1,
  minHandDetectionConfidence: 0.7,
  minHandPresenceConfidence: 0.5,
  minTrackingConfidence: 0.5
});

// In animation loop:
const results = handLandmarker.detectForVideo(video, performance.now());
// results.landmarks = Array of 21 NormalizedLandmark {x,y,z} per hand
```

## Coordinate Mapping: Video → Canvas (Mirrored Selfie View)

```javascript
// Canvas setup
const dpr = window.devicePixelRatio || 1;
canvas.width = video.videoWidth * dpr;
canvas.height = video.videoHeight * dpr;
ctx.scale(dpr, dpr);
canvas.style.width = video.videoWidth + 'px';
canvas.style.height = video.videoHeight + 'px';

// Draw mirrored (selfie) view
ctx.save();
ctx.scale(-1, 1);
ctx.drawImage(video, -video.videoWidth, 0, video.videoWidth, video.videoHeight);
ctx.restore();

// Landmark to canvas coordinates (accounting for mirror):
const canvasX = video.videoWidth * (1 - landmark.x);  // mirror X
const canvasY = video.videoHeight * landmark.y;
```

## User-Friendly Error Messages

```javascript
function getCameraErrorMessage(err) {
  const msg = err.message || err.name || 'Unknown camera error';
  
  if (msg.includes('NotAllowedError') || msg.includes('Permission')) {
    return 'Camera permission denied. Click 🔒/📷 in address bar → Allow → Refresh.';
  }
  if (msg.includes('NotFoundError') || msg.includes('OverconstrainedError')) {
    return 'No camera found or resolution not supported. Check Windows Privacy Settings → Camera.';
  }
  if (msg.includes('NotReadableError') || msg.includes('Could not start video source')) {
    return 'Camera busy by another app (Zoom/Teams/Meet/Discord/OBS). Close them and refresh.';
  }
  if (msg.includes('AbortError')) {
    return 'Camera stream was interrupted. Please refresh the page.';
  }
  if (msg.includes('timeout')) {
    return 'Camera slow to respond. Try refreshing the page.';
  }
  return 'Camera error: ' + msg;
}
```

## Debugging Checklist

1. **HTTPS/localhost required** — `file://` or raw IP won't work for `getUserMedia`
2. **Browser permissions** — Check 🔒 icon in address bar, site settings
3. **Windows Privacy** — Settings → Privacy & Security → Camera → all toggles On
4. **Exclusive access** — Only ONE app can use camera at a time on Windows
5. **Device enumeration** — `navigator.mediaDevices.enumerateDevices()` must show videoinput devices
6. **MediaPipe model** — Loads from GCS CDN (~10MB), cached by browser
7. **GPU delegate** — `delegate: 'GPU'` auto-fallbacks to CPU; no error if WebGPU unavailable

## Minimal Test Page

See `templates/web-hand-tracking-minimal.html` — serves as a standalone camera test without any app logic.