---
name: render-html-to-image
description: Use when rendering an HTML mockup or page to a PNG image.
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [windows]
metadata:
  hermes:
    tags: [html, screenshot, mockup, preview, headless, chromium]
    related_skills: []
---

# Render HTML to Image

Turn an HTML file into a PNG with a headless Chromium-based browser. Used to hand the user a **picture** of a UI / layout / mockup / poster, or a "what will it look like" preview, when there is no live page to screenshot and the browser-automation backend has no Chromium of its own.

## When to Use

- User asks how something will look and wants an image ("generate a preview", "cuma butuh foto")
- You built an HTML artifact and need a static render to deliver via `MEDIA:<path>`
- Don't use for: interactive widgets meant to live *in* chat (use the `::preview{file="..."}` directive instead); PDFs (use a PDF skill)

## Prerequisites

- A Chromium-based browser. On Windows **Edge ships by default**: `C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe`. Chrome also works.
- `PIL` optional, only to confirm output dimensions.

## How to Run

`bash scripts/render_html_preview.sh <in.html> <out.png> [width] [height] [scale]`

Defaults 1600x900 at scale 2 → a 3200x1800 PNG.

## Procedure

1. Write the HTML as a **fixed-size standalone page**: `html,body{width:<W>px;height:<H>px;overflow:hidden}`. A standalone page sets its own background/font/margins; an in-chat widget must NOT (the app injects those).
2. Render: run the script. It locates Edge/Chrome, converts paths to native form, and screenshots.
3. Verify the output: `python -c "from PIL import Image; print(Image.open('out.png').size)"` — must equal `W*scale x H*scale`.
4. Deliver with `MEDIA:<absolute path>`, and state plainly it is a **render**, not a live screenshot, plus any caveat (e.g. fonts, apps that won't actually change in the real thing).

## Pitfalls

- **MSYS path conversion is OFF for native programs**: passing `/c/Users/...` to `msedge.exe` is read as a literal path and fails. Always give the browser `C:/...` paths — the script's `nat()` does this with `cygpath -m`.
- Use `--headless=new` (not the old bare `--headless`); add `--force-device-scale-factor=2` for crisp text and to match a Retina-style mockup.
- `backdrop-filter: blur()` is often skipped in headless without GPU — always pair it with a solid/gradient fallback background so the layout still reads.
- Don't background the browser (`&` / `start`) from git-bash; run it foreground — headless exits on its own when the screenshot is written.
- Emoji/CJK glyphs render only if a font is present; verify when the mockup depends on them.

## Verification

- PNG exists and its pixel size equals `width*scale x height*scale`.
- Visual sanity: the delivered file has the expected aspect and is not blank (check file size is non-trivial, or open the dimensions).
