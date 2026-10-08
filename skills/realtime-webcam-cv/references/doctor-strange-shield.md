# Doctor Strange Shield — 9-Layer Sacred Geometry Implementation

Complete reference implementation from the session (see `index.html` in project root). This is the canonical "good" version to copy/modify for similar effects.

## Layer Breakdown

| Layer | Description | Key Technique |
|-------|-------------|---------------|
| 0 | Outer aura glow | Radial gradient fillRect |
| 1 | Concentric rings (3x) | `setLineDash` + `lineDashOffset` animation, counter-rotating |
| 2 | Main shield ring | Linear gradient stroke, thick, inner white highlight |
| 3 | Sacred polygons | Hexagram, dual triangles, pentagon, center triangle — independent rotation |
| 4 | Glyph/rune rings (4x) | Small triangles at circumference, 4 radii, alternating rotation |
| 5 | Inner mandala (8-fold) | 3 sub-layers, petal lines + connecting rings, breathing |
| 6 | Central core | Pulsing radial gradient (white→gold→orange), `sin(time*5)` pulse |
| 7 | Radial energy beams | Intermittent (threshold on `sin(t*3)`), linear gradient strokes |
| 8 | Outer rune text ring | Simulated with dashed ring, slow rotation |

## Core Drawing Functions

```js
// Polygon helper
function polygon(sides, radius, rotation, strokeStyle, lineWidth, fillStyle = null, dash = null) {
  ctx.save();
  ctx.strokeStyle = strokeStyle;
  ctx.lineWidth = lineWidth;
  if (fillStyle) ctx.fillStyle = fillStyle;
  if (dash) ctx.setLineDash(dash);
  ctx.beginPath();
  for (let i = 0; i <= sides; i++) {
    const a = rotation + (i / sides) * Math.PI * 2 - Math.PI / 2;
    const x = cx + Math.cos(a) * radius;
    const y = cy + Math.sin(a) * radius;
    if (i === 0) ctx.moveTo(x, y);
    else ctx.lineTo(x, y);
  }
  ctx.closePath();
  if (fillStyle) ctx.fill();
  ctx.stroke();
  ctx.restore();
}

// Glow circle helper
function glowCircle(radius, strokeStyle, lineWidth, glowColor, glowBlur, dash = null, rotation = 0) {
  ctx.save();
  ctx.strokeStyle = strokeStyle;
  ctx.lineWidth = lineWidth;
  ctx.shadowColor = glowColor;
  ctx.shadowBlur = glowBlur * progress;
  if (dash) {
    ctx.setLineDash(dash);
    ctx.lineDashOffset = -t * (dash[0] + dash[1]) * (rotation > 0 ? 50 : -30);
  }
  ctx.beginPath();
  ctx.arc(cx, cy, radius * breath, 0, Math.PI * 2);
  ctx.stroke();
  ctx.restore();
}

// Glyph ring helper
function glyphRing(radius, glyphCount, glyphSize, rotationSpeed, strokeStyle, lineWidth, glowColor, glowBlur) {
  const angle = t * rotationSpeed;
  ctx.save();
  ctx.strokeStyle = strokeStyle;
  ctx.lineWidth = lineWidth;
  ctx.shadowColor = glowColor;
  ctx.shadowBlur = glowBlur * progress;
  ctx.translate(cx, cy);
  ctx.rotate(angle);
  ctx.translate(-cx, -cy);
  // Ring
  ctx.beginPath();
  ctx.arc(cx, cy, radius * breath, 0, Math.PI * 2);
  ctx.stroke();
  // Glyphs
  ctx.fillStyle = strokeStyle;
  for (let i = 0; i < glyphCount; i++) {
    const a = (i / glyphCount) * Math.PI * 2;
    const x = cx + Math.cos(a) * radius * breath;
    const y = cy + Math.sin(a) * radius * breath;
    ctx.save();
    ctx.translate(x, y);
    ctx.rotate(a + Math.PI/2);
    ctx.beginPath();
    ctx.moveTo(0, -glyphSize);
    ctx.lineTo(glyphSize * 0.7, glyphSize * 0.5);
    ctx.lineTo(-glyphSize * 0.7, glyphSize * 0.5);
    ctx.closePath();
    ctx.fill();
    ctx.restore();
  }
  ctx.restore();
}
```

## Animation State

```js
let activationTime = 0;  // 0 to 1
let lastPinchState = false;

function render(time) {
  const dt = (time - lastTime) / 1000;
  lastTime = time;
  
  // ... detect pinch ...
  const shieldActive = pinchDist < PINCH_THRESHOLD;
  
  // Smooth progress
  if (shieldActive) {
    activationTime = Math.min(activationTime + dt * 3, 1);
    if (!lastPinchState) spawnParticles(palmX, palmY, radius, 20);
  } else {
    activationTime = Math.max(activationTime - dt * 2, 0);
  }
  lastPinchState = shieldActive;
  
  if (activationTime > 0.01) {
    drawSacredGeometry(ctx, palmX, palmY, baseRadius, time, activationTime);
  }
  
  // ... particles, UI ...
}
```

## Color Palette (Film-Accurate)

```js
const COLORS = {
  GOLD:       '#FFD700',
  GOLD_DIM:   'rgba(255, 215, 0, 0.6)',
  ORANGE:     '#FF8C00',
  ORANGE_DIM: 'rgba(255, 140, 0, 0.5)',
  AMBER:      '#FFAA00',
  WHITE:      '#FFFFFF',
  WHITE_DIM:  'rgba(255, 255, 255, 0.4)',
  CYAN:       '#00FFFF',
  CYAN_DIM:   'rgba(0, 255, 255, 0.3)'
};
```

## Breathing Animation

```js
const breath = Math.sin(t * 2.5) * 0.02 + 1.0;  // subtle 2% scale pulse
// Apply to all radii: radius * breath
```

## Particle System

```js
const particles = [];
function spawnParticles(cx, cy, radius, count) {
  for (let i = 0; i < count; i++) {
    const angle = Math.random() * Math.PI * 2;
    const dist = radius * (0.9 + Math.random() * 0.3);
    particles.push({
      x: cx + Math.cos(angle) * dist,
      y: cy + Math.sin(angle) * dist,
      vx: Math.cos(angle) * (0.5 + Math.random() * 1.5),
      vy: Math.sin(angle) * (0.5 + Math.random() * 1.5),
      life: 1.0,
      decay: 0.015 + Math.random() * 0.02,
      size: 1.5 + Math.random() * 2.5,
      color: Math.random() > 0.6 ? COLORS.GOLD : (Math.random() > 0.5 ? COLORS.ORANGE : COLORS.WHITE),
      rotation: Math.random() * Math.PI * 2,
      rotSpeed: (Math.random() - 0.5) * 0.1
    });
  }
}

function updateParticles(dt) {
  for (let i = particles.length - 1; i >= 0; i--) {
    const p = particles[i];
    p.x += p.vx * dt * 60;
    p.y += p.vy * dt * 60;
    p.vx *= 0.985;
    p.vy *= 0.985;
    p.life -= p.decay * dt * 60;
    p.rotation += p.rotSpeed * dt * 60;
    if (p.life <= 0) particles.splice(i, 1);
  }
}

function drawParticles(ctx) {
  particles.forEach(p => {
    const alpha = p.life;
    ctx.save();
    ctx.translate(p.x, p.y);
    ctx.rotate(p.rotation);
    ctx.globalAlpha = alpha;
    ctx.fillStyle = p.color;
    ctx.shadowColor = p.color;
    ctx.shadowBlur = 8 * alpha;
    const s = p.size * alpha;
    ctx.beginPath();
    ctx.moveTo(0, -s);
    ctx.lineTo(s * 0.6, 0);
    ctx.lineTo(0, s);
    ctx.lineTo(-s * 0.6, 0);
    ctx.closePath();
    ctx.fill();
    ctx.restore();
  });
}
```

## Key Parameters for Tuning

| Parameter | Value | Effect |
|-----------|-------|--------|
| `PINCH_THRESHOLD` | 0.045 | Normalized distance for activation |
| `baseRadius` | `min(w,h) * 0.28` | Shield size relative to viewport |
| `activationTime` rate | `dt * 3` (in), `dt * 2` (out) | Fade speed |
| Ring rotation speeds | 0.15, -0.2, 0.25, -0.3, 0.5 rad/s | Layer separation |
| Mandala rotation | 0.4, 0.55, 0.7 rad/s | Complexity |
| Core pulse | `sin(t * 5) * 0.1` | 10% radius oscillation |
| Beam trigger | `sin(t * 3) > 0.7` | ~30% duty cycle |

## Full Working File

See project root `index.html` — single-file, no dependencies beyond CDN MediaPipe. Run with:
```bash
python3 -m http.server 8080
# open http://localhost:8080
```