---
name: laravel-landing-pages
description: Build/polish Laravel landing pages; deploy to Vercel.
version: 1.0.0
tags: [laravel, tailwind, vite, landing-page, vercel, wsl, blade]
triggers:
  - buatkan landing page
  - landing page
  - perbagus UI
  - tambah animasi
  - deploy vercel
---

# Laravel Landing Pages (blade + Tailwind 4 + Vite)

Workflow untuk membangun/polish halaman di proyek Laravel (`resources/views/*.blade.php`, Tailwind 4 via `@tailwindcss/vite`), preview lokal via Laragon (WSL2), dan deploy ke Vercel sebagai static export.

## Setup yang perlu dicek dulu

- `resources/views/welcome.blade.php` — halaman utama (route `/` di `routes/web.php`)
- `resources/css/app.css` — `@import 'tailwindcss'` + `@theme { --color-*, --font-* }` (custom tokens via `--color-<name>-<shade>` otomatis jadi class `bg-<name>-<shade>` dst)
- `vite.config.js` — fonts self-hosted via `bunny('Font Name', { weights: [...] })` (offline aman, ga butuh Google Fonts CDN)
- Verify: `npm run build` (WAJIB — lihat pitfall di bawah). WSL + Tailwind 4 vite plugin: transform ~45s → timeout 60s default kena (exit 124); retry dengan `timeout=300` jalan. Bukan error permanen — retry pattern, jangan panik.

## Pitfall: class baru di blade TIDAK langsung jalan

Tailwind scan source file saat build. Class yang belum pernah muncul di file manapun TIDAK ada di CSS build lama → elemen render natural size / broken layout (contoh nyata: `h-44 w-44` baru dipasang, img render 512px penuh).

**Setiap ganti/add class di blade → `npm run build` dulu, baru verify browser.** Blade text edits aja (tanpa class baru) auto-render tanpa build.

## Pitfall: dist sync — blade edits tidak otomatis masuk dist/

`dist/index.html` adalah statis, bukan rendered blade. Kalau kamu edit blade (tambah class, ubah markup), dist/index.html TIDAK otomatis update. Dua jalur:

1. **Server jalan** (recommended): `curl -s "http://$GW:8899/" -o dist/index.html` + `sed` hapus absolute host. Ini render blade via PHP.
2. **Server mati**: edit dist/index.html manual — apply class/markup changes yang sama ke dist. Juga update asset references kalau hash berubah: cek `public/build/manifest.json` untuk nama file baru (`app-XXXXX.css`, `app-XXXXX.js`), lalu update `<link>` dan `<script>` di dist/index.html.

**Setelah edit dist, WAJIB juga copy build assets:** `cp -r public/build/* dist/build/`

## Pitfall CSS: animation fill-mode vs hover transform

`animation: x 0.6s ease-out both` nge-hold keyframe akhir permanen → menimpa `:hover { transform: ... }` selamanya. Kalau elemen beranimasi load DAN butuh hover transform (scale/translate), pakai `fill-mode: backwards` — efek sama selama delay+run, lepas setelah selesai.

## Preview lokal (WSL2 + Laragon — PHP tidak ada di WSL)

```bash
# serve pakai php.exe Windows, WAJIB bind 0.0.0.0:
/mnt/c/laragon/bin/php/php-8.3.30-Win32-vs16-x64/php.exe artisan serve --host=0.0.0.0 --port=8899
# akses dari WSL: gateway IP (bukan 127.0.0.1 — loopback Windows ≠ WSL):
GW=$(ip route show default | awk '{print $3}')   # mis. 172.x.x.1
# dari browser Windows: http://127.0.0.1:8899/
```
Server mati diam-diam (exit 255) → cek `process poll` lalu restart.

## Verify visual tanpa vision provider

Kalau `browser_vision`/`vision_analyze` gagal (provider belum dikonfigurasi), verifikasi via `browser_console` computed styles:
- bg/warna/ukuran/radius elemen kunci, `img.naturalWidth`, overflow: `document.body.scrollWidth - window.innerWidth` (scrollbar bikin -15px, itu normal, bukan overflow)
- JS error: `browser_console` kosong = bersih

## Pola animasi yang sudah terbukti (restrained, anti-slop)

- Scroll reveal: `.js` guard di `<html>` (JS-only, no-JS user tetap lihat konten), IntersectionObserver, unobserve setelah trigger, `prefers-reduced-motion` → langsung tampil. CSS: `.js .reveal { opacity:0; translateY(16px); transition }` + `.js .reveal.is-visible { ... }`
- Stagger: `transition-delay` inline / custom property `--d: ...ms` per item (loop blade `$i * 45ms`)
- Pop-in stagger (tags/items): `.js .reveal .pop-in { --d }` → `.is-visible .pop-in`
- Count-up stats: `[data-count]` + `data-decimals`, IntersectionObserver threshold 0.5, rAF ease-out cubic, reduced-motion → nilai final instan, `aria-label` nilai akhir di parent
- Typewriter: span kosong di HTML + `<span class="sr-only">` teks penuh (a11y) + span aria-hidden; reduced/no-JS → isi penuh langsung
- Draw-line: `scaleX(0)` origin-left → `scaleX(1)` saat parent `.reveal.is-visible`
- Progress bar + back-to-top: satu scroll handler rAF-throttled + passive, `scaleX(scrollY/max)`, toggle `.visible` di >600px
- Hover micro: arrow slide (`group-hover:translate-x-1 opacity-0→100`), underline grow (`.link-underline::after` scaleX), foto ring (`-inset-1` ring + `scale(1.02)`)
- Semua transform/opacity-only (compositor friendly), `motion-safe:` untuk load animasi, override transition none di media query reduced-motion

## Micro-interactions lanjutan (terbukti di iterasi 2)

Pola lengkap + CSS/JS exact: `references/micro-interactions.md`. Ringkasnya:

- **Toggle widget state machine** — satu listener untuk semua state = bug. Contoh nyata: tombol API console, klik "DISCONNECT" malah connect ulang karena listener jalanin flow connect terus. Fix: flag `connected` + branch di awal listener (state connected → jalankan teardown, bukan re-run setup).
- **Micro-chart CSS-only (tanpa JS tambahan)**: sparkline SVG `pathLength="1"` + `stroke-dasharray:1; stroke-dashoffset:1→0`; sparkbar `scaleY(0)` + `transform-origin: bottom`; dots `scale(0)`; progress bar `width:0→100%` lewat CSS `.js .reveal.is-visible .sparkbar-fill { width:100% }` (CSS override utility/inline width). Semua trigger pakai class `.reveal.is-visible` yang sudah ada — nol observer tambahan.
- **Infinite ticker/marquee**: dua group konten identik + track `flex w-max whitespace-nowrap` + `translateX(-50%)` loop; `:hover { animation-play-state: paused }`; reduced-motion → `animation: none` (konten tetap tampil statis, jangan display:none — dekoratif tapi hidup). Pakai `aria-hidden="true"` (duplikat teks = noise screen reader).
- **Inline `transition-delay` membunuh animasi filter** — row dengan stagger `transition-delay: {{$i*45}}ms` inline: fade-out pas filter lambat berantai (row terakhir delay 450ms). Fix: `.is-filtered-out { transition-delay: 0ms !important }` (hide cepat serempak, show boleh cascade lagi).
- **Reveal direction variants**: `.js .reveal.reveal-left { transform: translateX(-24px) }` + rule reset dengan specificity TINGGI `.js .reveal.is-visible.reveal-left { transform:none }` — kalau specificity sama, order di file menentukan dan default `.is-visible` bisa kalah.
- **`--d` inherit**: custom property `--d` di parent li ikut ke child — child animation pakai `transition-delay: var(--d, 0ms)` tanpa set ulang per elemen (contoh: cert validity bar di dalam li pop-in).
- **Cross-link interaksi antar section**: skill tag → filter ledger. Mapping skill→kategori via `@php $filters = [...]` di dalam `@foreach` blade; klik tag → `document.querySelector('.project-filter[data-filter="X"]').click()` (reuse listener filter yang sudah ada, jangan duplikasi logic) + `scrollIntoView({behavior:'smooth'})`.
- **Status/validity bars pakai data nyata**: cert validity = sisa bulan / 36 horizon, label "29 MO LEFT" / "EXPIRED", warna biru vs abu — informatif bukan hiasan.

## Micro-interactions iterasi 3 (hover depth + hero)

Pola lengkap + CSS/JS exact: `references/micro-interactions.md` §10–13. Ringkasnya:

- **Hover effect harus di-guard `@media (hover:hover) and (pointer:fine)`** — jangan modal `:hover` saja; touch device bikin state hover macet (stuck). Contoh: project-row geser `translateX(4px)` + border-left biru, client name berubah biru.
- **Headline gradient drift**: `background-clip:text` + `background-size:200%` + keyframes `background-position` drift (9s loop). Reduced-motion → reset ke `-webkit-text-fill-color: var(--color-ink)` polos (jangan tinggalin gradient di aksen statis — itu overkill untuk reduser).
- **Duotone foto**: default `filter: grayscale(0.85)`, hover → `grayscale(0)` + `scale(1.02)`. Reduced-motion → `filter:none` (jangan biarkan foto abu-abu permanen).
- **Parallax bounded**: translateY(scrollY * 0.08) di profil hero — cuma aktif selama hero di viewport (cek `scrollY < hero.offsetHeight`), reset transform di luar itu. Masuk ke scroll handler rAF yang sudah ada, jangan handler baru. JS guard reduced-motion (CSS media query tidak sampai ke transform inline).

## Pitfall: header shadow + scroll handler guard

Tambah elemen baru ke scroll handler yang sudah ada (progress bar/back-to-top) — jangan buat handler kedua. Guard `if (a || b || c)` harus include elemen baru, dan `update()` toggle class (`header.classList.toggle('is-scrolled', scrollY > 8)`). Header perlu class `site-header` di HTML supaya selector CSS/JS konsisten.

## Pier88-style premium motion (teardown pier88coast.com)

Klien minta "animasi kayak [situs premium]" — rahasianya bukan library, tapi kombinasi timing + blur + parallax CSS-var. Full code: `references/pier88-teardown.md`.

- **Cinematic reveal** = `opacity 0→1` + `filter: blur(5px→0)` + `translate3d(0,24px→0)`, timing via CSS custom props, IO `threshold .18, rootMargin "0px 0px -8%"`, unobserve. Blur-nya yang bikin sinematik.
- **Split-line heading**: `.split-line{overflow:hidden}` > `.line-inner{translateY(110%→0)}` `cubic-bezier(.19,1,.22,1)`; kata aksen script italic serif mid-line.
- **Parallax tanpa ScrollTrigger**: rAF + ticking guard → scroll set CSS var `--bg-y = centerOffset*46px` → bg gerak berlawanan konten. Pinned-drift: container `height~5000px` relative → inner sticky → transform anak per progress.
- **Carousel**: GSAP `fromTo` 0.46s stagger .04 power3.out; WAJIB `gsap.set` non-aktif slide hidden di init. **Kalau CDN gagal load, vanilla translateX + transition cukup** — lib CDN = progressive enhancement, core UX jangan bergantung.
- **Jangan pasang elemen dekoratif floating yang ke-parallax** — user tolak foto gulai mengambang di hero ("aneh ngikutin turun"). Parallax background = premium; parallax foto produk random = rusak.

## Desain anti-AI-slop (preferensi user)

- Rujuk design system nyata: load `frontend-design` + `popular-web-designs` (template `templates/ibm.md` — IBM Carbon — cocok untuk tema enterprise/SAP/konsultan)
- Hindari 3 default AI: cream+terracotta serif, near-black+acid green, broadsheet hairline
- Satu aksen warna, 0 radius (Carbon), flat tanpa shadow, mono untuk data (IBM Plex Mono, tabular-nums)
- **Jangan usulkan loading screen untuk page statis** — pattern AI-slop, user ditanya dan menolak
- Data asli user = signature (contoh: project ledger pakai SO number SAP asli)

## Aksesibilitas baseline (dari Web Interface Guidelines review)

skip link ke #main, `:focus-visible` outline global, heading hierarkis, `scroll-mt-24` pada section ber-id (sticky nav), `tabular-nums` angka, `text-wrap: balance` h2, `meta theme-color`, `translate="no"` pada SO number/brand teknis, `alt` + `width/height` img (anti-CLS), `fetchpriority="high"` LCP image.

## Pitfall: hero dua-kolom tinggi tidak seimbang → void gede

Gejala umum: ada space kosong besar di section awal/hero. Biangnya bukan padding — **dua flex column tinggi beda lancip** + `items-center`.

Contoh nyata: kiri = teks (name+para+CTA, ~360px), kanan = foto+lokasi+2 widget terminal numpuk jadi 732px. `items-center` nge-center kolom PENDEK terhadap kolom PANJANG → void gede, bergeser kiri↔kanan tergantung kolom mana yang lebih pendek. Pertama void 274px di bawah CTA kiri; setelah widget dipindah, void 491px di kanan bawah foto. `lg:py-32` (128px) ikut menggembungkan hero ke ~919-988px.

**Diagnosis tanpa vision provider** (browser_vision/vision_analyze 401): ukur pake `browser_console`:
```js
const r=hero.getBoundingClientRect(), L=leftCol.getBoundingClientRect(), R=rightCol.getBoundingClientRect();
({heroH:Math.round(r.height), leftBottom_rel:Math.round(L.bottom-r.top), rightBottom_rel:Math.round(R.bottom-r.top), gapRight:Math.round(r.bottom-R.bottom), gapLeft:Math.round(r.bottom-L.bottom)})
```
Gap besar di sisi mana = di sanalah void. Kalau salah satu gap gede banget (~300px+), itu kolom pendek ke-center vs kolom panjang.

**Fix (urut):**
1. `lg:items-center` → `items-start` (top-align). Kedua kolom rata atas, void jadi whitespace bawah natural, BUKAN void tengah mencolok.
2. **Sebarkan widget, jangan numpuk di satu kolom.** Kanan (foto+lokasi+SYS_BRIEF) vs kiri (teks+CTA+API_console) → tinggi seimbang (~500 vs ~660), gap turun ke level padding normal (~128px).
3. Kalau masih tinggi, potong `lg:py-32` → `lg:py-24`; jangan nambah konten fiktif cuma buat nyamain tinggi.
- Mobile: `flex-col-reverse` → child DOM pertama tampil paling atas. Atur urutan DOM supaya foto di atas teks di mobile, dan kiri↔kanan di desktop (satu struktur kolom ini).

## Deploy Vercel (static export — Laravel tidak jalan native di Vercel)

```bash
npm run build
rm -rf dist && mkdir -p dist
curl -s "http://$GW:8899/" -o dist/index.html
sed -i 's|http://172.26.176.1:8899||g' dist/index.html   # @vite render absolute host — wajib root-relative
cp -r public/build dist/build && cp -r public/images dist/images
npx -y vercel@latest deploy dist --prod --yes
```
Detail CLI/auth/API rename: `references/vercel-cli.md`

## Verifikasi deploy

`curl -s -o /dev/null -w "%{http_code}" <url>` untuk index + css + js + gambar (semua harus 200), lalu `browser_navigate` ke URL production, cek struktur + 0 JS error.
