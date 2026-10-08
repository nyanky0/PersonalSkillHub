# Doctor Strange — Hand Gesture Spell Engine (worked example)

Real project at `/mnt/c/laragon/www/Dr Strange/` — reference for building a
webcam→hand-gesture→canvas-overlay app that runs from a phone/PC over LAN.
Two parallel implementations with identical core logic.

## Architecture (dual-track)

| | magic_circle.py (Python/OpenCV) | index.html (browser JS) |
|---|---|---|
| Detection | server-side, MediaPipe Tasks Python | client-side, `@mediapipe/tasks-vision` CDN |
| Video source | webcam (Windows native) or file fallback `test_input.mp4` | `getUserMedia` (HP/PC), camera switch |
| Pinch threshold | `math.hypot` px distance < 40 (at ~640x480) | normalized distance lm[4]–lm[8] < 0.055 |
| Hands | 2 | 2 |
| Effects | 1 gold circle (ring + arc + hexagram + dots) | 5 spell palettes + particle system + shockwaves + dual-hand energy tether |
| Sound | none | Web Audio synth (oscillator freq sweep per spell) |
| Camera handling | retry backends DSHOW/MSMF/DEFAULT, verify frame read | enumerate devices, facingMode user/environment, mirror auto-adjust |
| Mirroring | `cv2.flip(frame, 1)` | `ctx.scale(-1,1)`; palm x = `videoWidth * (1 - lm.x)` |

`server.py` — dual static server: HTTP :8000 + HTTPS :8443 (self-signed
cert.pem/key.pem, `Access-Control-Allow-Origin: *`). HTTPS required for
`getUserMedia` on phones; users click Advanced→Proceed on the cert warning.
Serves the folder so phones reach `https://<lan-ip>:8443`.

## Gesture logic (both tracks)
1. HandLandmarker VIDEO mode, numHands=2, minHandDetectionConfidence 0.65.
2. Landmarks: 4 = thumb tip, 8 = index tip, 9 = palm center (MCP middle).
3. Pinch when dist(4,8) < threshold → spawn spell circle at landmark 9.
4. Progress ramps up (dt*4) while pinching, decays (dt*2.5) after — smooth fade.
5. Dual-hand: two circles + lightning tether beam between palms (sine-jittered path).

## Bugs found & fixed (2026-08)
1. `const particles` declared TWICE at module top level — SyntaxError killed the
   entire module: blank page, loading overlay never cleared. Fix: delete the
   stale duplicate (keep the one near `spawnPortalSparks`/`updateParticles`).
2. `drawParticles(ctx)` called in render loop but never defined — ReferenceError
   every frame after camera init. Fix: add the function:
   `globalAlpha = clamp(life)`, `shadowColor = color`, `shadowBlur = 6*life`,
   `arc(0,0, size*life)` with `translate` + `rotate(p.rotation)`.
3. `const particles`/`MAX_PARTICLES` duplicated as dead code (`200` vs `250`).

## Verification without a webcam
- `node --check` on the extracted module script → syntax gate.
- Grep every called identifier for a `function`/`const` definition → catches
  called-but-undefined (ReferenceError class).
- Serve + load in browser: loading overlay hidden ⇒ init reached camera step;
  canvas shows motion-trail pixels ⇒ render loop alive; only expected console
  error is the handled `getUserMedia: Requested device not found` (headless).

## Notes
- WSL has no webcam — run the Python track on Windows native or feed a video
  file via `VIDEO_SOURCE`; the browser track works from any device on the LAN.
- index.html uses CDN model+wasm (needs internet); `hand_landmarker.task` in the
  folder is only used by the Python track.
- Stray debug files: test_frame.jpg, test_input.mp4, __pycache__ — safe to prune.
