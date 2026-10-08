# Laravel/PHP static export → Vercel

Proven recipe: Laravel 12 + Tailwind 4 + Vite landing page deployed to Vercel as a static site.

## Why static

Vercel has no native PHP runtime. A Laravel app that is effectively one page renders fine as
static HTML + assets. Full Laravel on Vercel needs community PHP runtimes — overkill for a
landing page.

## Serve Laravel from WSL (no PHP in WSL)

- WSL often lacks PHP; Laragon Windows PHP works: `/mnt/c/laragon/bin/php/php-8.3.30-Win32-vs16-x64/php.exe`.
- `php artisan serve --host=0.0.0.0 --port=8899` (background process).
- WSL2 NAT: Windows `127.0.0.1` is NOT reachable from WSL. Reach the Windows server via the
  gateway IP: `GW=$(ip route show default | awk '{print $3}')` → `http://$GW:8899`.
- `artisan serve` on Windows may die with exit 255 after a while — health-check
  (`curl -s -o /dev/null -w "%{http_code}" http://$GW:8899/`) and restart if dead.
- Syntax-check blade/PHP with the same `php.exe`, but it is a WINDOWS binary — it cannot
  open `/mnt/c/...` paths. Pass the Windows path: `php.exe -l 'C:\laragon\www\<proj>\resources\views\welcome.blade.php'`.

## Render static folder

```bash
cd <project> && rm -rf dist && mkdir -p dist
GW=$(ip route show default | awk '{print $3}')
curl -s "http://$GW:8899/" -o dist/index.html
sed -i "s|http://$GW:8899||g" dist/index.html   # @vite emits ABSOLUTE host URLs → root-relative
cp -r public/build dist/build
cp -r public/images dist/images
cp public/favicon-32.png public/favicon-192.png public/apple-touch-icon.png dist/
cp public/cv.pdf public/sitemap.xml public/robots.txt dist/   # CV + SEO files (if present)
```

## Download CV (PDF) button

Consultant landing pages get a "Download CV" link → `/cv.pdf`. Generate the PDF with
reportlab (venv `~/.venvs/pdf/bin/python` has it — no pip install needed): platypus A4,
Helvetica family, dark section bars (`#161616`) + blue accent (`#0f62fe`) to match the
Carbon look. Source content from the user's existing CV docx (`read_file` auto-extracts
.docx). Drop the file at `public/cv.pdf` BEFORE exporting; the recipe copies it to dist.
Verify with pypdf (same venv): page count + first-page text extract.

**Regenerating an existing CV**: the reportlab generator script is `/tmp/cv_gen.py` (ad-hoc,
not committed). Edit it → run `~/.venvs/pdf/bin/python /tmp/cv_gen.py` (writes `public/cv.pdf`)
→ verify with pypdf text extraction (`pages == expected`, and the removed fields are GONE:
`'gmail' in txt` / `'+62' in txt` must be `False`) → `cp public/cv.pdf dist/cv.pdf` →
deploy. User preference: NO phone/email anywhere public (page or CV) — contact line = location
+ GitHub only.

## Blade edits vs rebuild order (hash drift trap)

Order matters: `npm run build` FIRST, then render dist, then deploy. Tailwind 4's generated
CSS hash can change between builds even with ZERO source changes — deploy-then-rebuild leaves
dist referencing the OLD hashed asset name → live CSS 404s. After any build, sanity-check
dist against the fresh build (compare BASENAMES — comparing full paths exits 1 and looks
like a failed check):
`diff <(ls public/build/assets/*.css public/build/assets/*.js | xargs -n1 basename) <(ls dist/build/assets/*.css dist/build/assets/*.js | xargs -n1 basename)`
Mismatch → re-render dist and redeploy. Blade-only edits need no vite build (server-side
rendered), but still re-render dist + redeploy.

Verify only root-relative + external URLs remain:
`grep -oE '(href|src)="[^"]*"' dist/index.html | grep -v '^href="#' | sort -u`

## Pitfalls discovered

- **Tailwind 4 class scan happens at build time**: any class first used in a blade/HTML edit
  (e.g. `h-44`, `object-cover`) is MISSING from the previously built CSS until `npm run build`
  runs again — elements render at natural size / unstyled. After adding classes: rebuild, then
  re-render dist and redeploy. Verify computed style in browser before claiming done.
- **CSS `animation` fill-mode**: `animation: x 0.6s ease-out both` keeps the keyframe's final
  `transform` applied forever, overriding hover transforms on the same element (e.g. photo
  hover scale never fires). Use fill-mode `backwards` (applies `from` during delay, releases
  after finish) so hover transforms work. Verify with `element.getAnimations()` — empty array
  means released.
- **Blade edits need no build** (rendered server-side per request) — only CSS/JS edits do.
- **Bulk class-rename substring collision**: replace_all `bg-carbon-10` → `bg-surface-2` ALSO
  rewrites `bg-carbon-100` → `bg-surface-20` (prefix match + leftover char) — a nonexistent
  class → element loses its background silently. Symptom: computed style `backgroundColor`
  = `rgba(0, 0, 0, 0)` on a section that should be dark. Order replacements longest-token-first
  (rename `bg-carbon-100` before `bg-carbon-10`), then grep the file for any `bg-surface-20`-
  style leftovers. If a collision already happened, `sed -i 's/bg-surface-20/bg-section-dark/g'`
  fixes it — verify with grep counts.
- **Dark mode via Tailwind 4 semantic tokens** (Carbon palette): define tokens in `@theme`
  (`--color-ink/-muted/-surface/-surface-2/-line/-section-dark/-accent-soft/-accent-strong`),
  then one unlayered `.dark { --color-*: <dark values>; color-scheme: dark }` block overrides
  them all — utilities are generated from the tokens so every `text-ink`/`bg-surface` class
  flips automatically. Keep genuinely-fixed colors (`bg-carbon-100` on the always-dark header/
  stats/contact sections → use a dedicated `--color-section-dark` token instead of flipping).
  FOUC guard: tiny inline `<script>` in `<head>` BEFORE `@vite` reads
  `localStorage['maul-theme']` else `prefers-color-scheme`, sets `document.documentElement.classList.toggle('dark', ...)`.
  Toggle button JS: `aria-pressed`, swap sun/moon icon `hidden` classes (sun shown in dark,
  moon in light — easy to invert), persist choice, and only follow OS `change` events when no
  stored choice exists. Icon-rotation/hover micro-animations need their own `transition` rule
  — Tailwind `transition-transform` on the parent doesn't cover them.
- **Verify theming WITHOUT a vision provider**: don't trust screenshots; read computed styles
  via `browser_console`: `getComputedStyle(document.body).backgroundColor` should be
  `rgb(22, 22, 22)` dark / `rgb(255, 255, 255)` light, and dark-section bg `rgb(38, 38, 38)`
  when `--color-section-dark` = `#262626` in dark. Also assert `localStorage` was written.
- **Expandable rows / disclosure panels**: animate with `display:grid; grid-template-rows:0fr`
  → `.open { grid-template-rows:1fr }` + inner `overflow:hidden` — no JS height math, smooth
  both directions. Add `visibility:hidden→visible` so collapsed content is out of the a11y tree;
  toggle via `aria-expanded`/`aria-controls` on a real `<button>`; `transition: grid-template-rows,
  visibility` and disable transitions under `prefers-reduced-motion`. Icon rotate 45° makes a
  `+` become `×`. Note `getBoundingClientRect().height` is 0 mid-transition — check after
  ~350 ms or assert the class, not the height.
- **JSON-LD `"@context"` breaks Blade**: Laravel 12 has a real `@context` directive, so a raw
  `"@context": "https://schema.org"` in a blade file compiles into PHP `if (context()->has(...))`
  → "syntax error, unexpected end of file, expecting elseif/else/endif" → HTTP 500 on every page.
  `view:cache` reports success (it doesn't lint the generated PHP) — debug by running
  `php.exe -l` on the compiled file in `storage/framework/views/`. Fix: write `"@@context"` in
  blade (renders literal `@context`). Other `@type`/`@id` keys are fine (not registered directives).
- Keep the dev server running for re-renders; blade is re-rendered fresh on each `curl`.

## Image processing without PIL/ImageMagick

WSL python3 (3.14, no pip, PEP 668) lacks imaging libs. Laragon's PHP has GD enabled:
write a small PHP script (imagecreatefromjpeg → imagecrop center square → imagescale →
imagepng/jpeg) and run it with `php.exe`. `imagejpeg` fails if the destination directory
does not exist — `mkdir` first. Favicon set (32/192/180) from the same script; delete the
script after running.

## OG meta for the deployed site

- `og:url` / `og:image` must be absolute URLs pointing at the STABLE project domain
  (`https://<project>.vercel.app/`), not the random per-deployment URL.
- Also add favicon `<link>` tags + `theme-color` before export so they land in the static copy.
