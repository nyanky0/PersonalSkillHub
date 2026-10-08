# Micro-interactions & scroll animations (landing page, CSS-only + minimal JS)

Pattern yang terbukti di landing page Laravel + Tailwind 4 (IBM Carbon, anti-slop).
Semua hormati `prefers-reduced-motion` dan guard `.js` di `<html>`.

## 1. Toggle widget — WAJIB state machine (bug nyata)

Satu listener yang jalanin flow yang sama untuk semua state = bug klasik.
Contoh nyata: tombol "CONNECT SERVICE LAYER" → setelah connect jadi "DISCONNECT",
tapi klik DISCONNECT malah jalanin flow connect lagi (reset output + ngetik ulang).

```js
let connected = false;
btn.addEventListener('click', () => {
    if (connected) {
        // teardown branch — jangan re-run setup
        pushLine('> DELETE /b1s/v1/Logout');
        pushLine('Status: 204 OK — Session closed');
        connected = false;
        btn.textContent = 'CONNECT SERVICE LAYER';
        setIdleStyle();
        return;
    }
    // setup flow (async, btn.disabled selama jalan)
    connected = true;
});
```

Aturan: listener membaca state dulu, branch teardown vs setup. Disable tombol selama
async flow berjalan (cegah double-click).

## 2. Micro-chart CSS-only (trigger pakai .reveal.is-visible yang ada — tanpa observer baru)

Semua state awal di `.js .reveal <child>`, state akhir di `.js .reveal.is-visible <child>`.
Parent section tinggal pakai class `reveal` biasa.

### Sparkline (SVG draw)
```html
<svg viewBox="0 0 100 20" fill="none" preserveAspectRatio="none">
  <path class="sparkline-path" pathLength="1" d="M0,18 Q25,15 50,8 T100,2"
        stroke="var(--color-blue-60)" stroke-width="1.5" stroke-linecap="round"/>
</svg>
```
```css
.sparkline-path {
  stroke-dasharray: 1;
  stroke-dashoffset: 1;               /* pathLength="1" → offset 1 = hidden penuh */
  transition: stroke-dashoffset 1.3s cubic-bezier(0.4,0,0.2,1) 0.15s;
}
.js .reveal.is-visible .sparkline-path { stroke-dashoffset: 0; }
```
`pathLength="1"` WAJIB — tanpa itu dasharray pakai panjang path asli yang tidak diketahui.

### Sparkbar (bar tumbuh)
```css
.js .reveal .sparkbar-bar { transform: scaleY(0); transform-origin: bottom center; }
.js .reveal.is-visible .sparkbar-bar { transform: scale(1); }
```
Delay per bar via inline `transition-delay` (mis. 100ms, 160ms, ... 520ms; bar terakhir solid/warna penuh).

### Dot (pop)
```css
.js .reveal .sparkbar-dot { transform: scale(0); }
.js .reveal.is-visible .sparkbar-dot { transform: scale(1); }
```
Dots pakai `scale()` bukan `scaleY()` (scaleY bikin bulat jadi garis).

### Progress bar (fill)
```html
<div class="h-1 w-full bg-line overflow-hidden rounded-full">
  <div class="sparkbar-fill h-full bg-blue-60 w-0 transition-all duration-1000" ...></div>
</div>
```
```css
.js .reveal.is-visible .sparkbar-fill { width: 100%; }
```
CSS rule (specificity 0,3,0) mengalahkan utility `.w-0` (0,1,0) — tidak perlu JS.

### Track warna yang ikut dark mode
Pakai token semantik `bg-line` (dari `--color-line`) bukan warna keras — otomatis flip di `.dark`.

## 3. Infinite ticker/marquee

```html
<div class="bg-section-dark overflow-hidden" aria-hidden="true">
  <div class="ticker-track flex w-max whitespace-nowrap will-change-transform">
    <span class="ticker-group ...">ITEM · ITEM · ITEM · </span>
    <span class="ticker-group ...">ITEM · ITEM · ITEM · </span>  <!-- duplikat identik -->
  </div>
</div>
```
```css
.ticker-track { animation: ticker-scroll 36s linear infinite; }
.ticker-track:hover { animation-play-state: paused; }
@keyframes ticker-scroll { from { transform: translateX(0); } to { transform: translateX(-50%); } }
@media (prefers-reduced-motion: reduce) { .ticker-track { animation: none; } }
```
- Loop seamless: 2 group identik + `-50%` translate (bukan `-100%` satu group).
- `w-max whitespace-nowrap` biar track selebar konten, bukan viewport.
- `aria-hidden="true"` — duplikat teks noise buat screen reader.
- Reduced-motion: `animation: none` (konten tampil statis). Jangan display:none — strip dekoratif tetap layak tampil.

## 4. Inline transition-delay membunuh animasi filter/hide

Row hasil loop punya `style="transition-delay:{{ $i * 45 }}ms"` (stagger reveal).
Pas filter fade-out, delay inline bikin row terakhir nunggu 450ms dulu — terasa lambat.

```css
.js .reveal.project-row.is-filtered-out {
  opacity: 0;
  transform: translateY(-4px);
  transition-delay: 0ms !important;   /* hide cepat serempak */
}
```
Show (unfilter) boleh cascade lagi via delay inline — efek bagus.

## 5. Reveal direction variants — specificity JANGAN dilupakan

```css
.js .reveal.reveal-left  { transform: translateX(-24px); }
.js .reveal.reveal-right { transform: translateX(24px); }
/* specificity harus LEBIH TINGGI dari default (.js .reveal = 0,3,0 sama!) */
.js .reveal.is-visible.reveal-left,
.js .reveal.is-visible.reveal-right { transform: none; }
```
`.js .reveal` vs `.js .reveal.reveal-left` sama-sama 0,3,0 — kalau reset cuma
`.js .reveal.is-visible` (0,3,0), ORDER file yang menang, bukan intent. Tulis reset
dengan 4 selector (0,4,0) atau pastikan reset muncul SETELAH variant di file.

## 6. `--d` inherit — delay cascade dari parent

Custom property ikut turun. Parent li punya `style="--d: 60ms"` (dari loop),
child animation tinggal:
```css
.js .reveal.is-visible .cert-fill {
  transform: scaleX(1);
  transition: transform 0.7s cubic-bezier(0.4,0,0.2,1) var(--d, 0ms);
}
```
Child scaleX origin-left — bar tumbuh dari kiri, delay nyambung ke posisi parent di list.

## 7. Cross-link antar section (skill tag → filter ledger)

- Mapping di blade: `@php $filters = ['Skill A' => 'integration', ...]; $f = $filters[$item] ?? 'all'; @endphp`
  di dalam `@foreach` — array asosiatif item→filter, default 'all'.
- Tag = `<button type="button" class="skill-tag" data-filter="...">` + `title` hint
  (a11y: bukan span — elemen interaktif harus button).
- JS: klik → `document.querySelector('.project-filter[data-filter="' + f + '"]').click()`
  — REUSE listener filter yang sudah ada, jangan duplikasi logic filter.
- Lalu `document.getElementById('projects')?.scrollIntoView({ behavior: 'smooth', block: 'start' })`.
- Hover state: `hover:bg-blue-60 hover:text-white` + `transition-colors duration-150` —
  jangan timpa transition pop-in (opacity/transform) yang sudah ada.

## 8. Header shadow saat scroll — satu handler, jangan dua

Scroll handler rAF-throttled yang sudah ada (progress + back-to-top) cukup ditambah:
```js
const siteHeader = document.querySelector('header');
// guard jadi: if (progressBar || backToTop || siteHeader) {
// update(): if (siteHeader) siteHeader.classList.toggle('is-scrolled', window.scrollY > 8);
```
```css
.site-header { transition: box-shadow 0.25s ease; }
.site-header.is-scrolled { box-shadow: 0 2px 12px rgba(0,0,0,0.28); }
```
Header perlu class `site-header` eksplisit di HTML — selector `header` telanjang
berisiko kena elemen lain.

## 9. Data nyata = visual yang kredibel

Cert validity bars: sisa bulan / horizon 36 bulan (umum untuk sertifikasi 3 tahunan).
`29 MO LEFT` (biru, width 80%) vs `EXPIRED` (abu, width 6% biar ada garis).
Hitung dari "sekarang" saat implementasi; label teks tetap informatif tanpa bar.

## 10. Hover effect WAJIB di-guard fine-pointer

Modal `:hover` di touch device bikin state hover stuck (macet setelah tap). Pattern:

```css
.project-row {
    border-left: 2px solid transparent;
    transition: background-color 0.15s ease, border-left-color 0.2s ease, transform 0.2s ease;
}
@media (hover: hover) and (pointer: fine) {
    .project-row:hover {
        background-color: var(--color-surface-2);
        border-left-color: var(--color-blue-60);  /* indicator list-item ala IBM */
        transform: translateX(4px);               /* geser halus ke kanan */
    }
}
.project-row:hover .client-name { color: var(--color-blue-60); }
```

Blade: hapus utility `transition-colors duration-150 hover:bg-surface-2` dari class
row (bentrok dengan transition CSS custom), taruh transition di CSS class sendiri.
Client name butuh class ekstra (`client-name`) supaya child color bisa di-target.

## 11. Headline gradient drift (background-clip text)

```css
.hero-name {
    background: linear-gradient(100deg, var(--color-ink) 10%, var(--color-blue-60) 30%, var(--color-ink) 55%);
    background-size: 200% auto;
    -webkit-background-clip: text;
    background-clip: text;
    -webkit-text-fill-color: transparent;
    color: transparent;
    animation: hero-name-drift 9s ease-in-out infinite;
}
@keyframes hero-name-drift {
    0%, 100% { background-position: 0% center; }
    50%      { background-position: 100% center; }
}
@media (prefers-reduced-motion: reduce) {
    .hero-name {
        background: none;
        -webkit-text-fill-color: var(--color-ink);  /* JANGAN tinggal gradient statis */
        color: var(--color-ink);
        animation: none;
    }
}
```

`background-position` animasi = kompositor-friendly (background-clip:text walau
paint, tetap ringan untuk satu elemen headline). Reduced-motion: reset ke solid —
gradient diam di teks itu justru noise buat reduser.

## 12. Duotone foto (grayscale → warna saat hover)

```css
.profile-img {
    transition: transform 0.3s ease, filter 0.3s ease;
    filter: grayscale(0.85);          /* default: duotone kalem */
}
.group:hover .profile-img, .group:focus-visible .profile-img {
    transform: scale(1.02);
    filter: grayscale(0);
}
@media (prefers-reduced-motion: reduce) {
    .profile-img { filter: none; }    /* jangan biarkan foto abu-abu permanen */
}
```

Focus-visible ikut di-guard — keyboard user dapat feedback yang sama.

## 13. Parallax bounded — satu scroll handler, aktif hanya di hero

```js
const heroProfil = document.querySelector('.hero-profil');
if (progressBar || backToTop || siteHeader || heroProfil) {   // guard include elemen baru
    const update = () => {
        // ...progress bar + back-to-top + header shadow...
        if (heroProfil && !window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
            const heroBottom = heroProfil.closest('section')?.offsetHeight ?? 0;
            heroProfil.style.transform = window.scrollY < heroBottom
                ? `translateY(${window.scrollY * 0.08}px)`   // drift pelan (8% scroll)
                : '';                                          // reset di luar hero
        }
        ticking = false;
    };
}
```

- Parallax scroll pakai `translateY` — kompositor, tidak reflow.
- Bounded: cek `scrollY < heroBottom` biar kolom profil tidak melayang ke section
  berikutnya saat scroll jauh.
- Reduced-motion guard di JS (bukan CSS) karena transform di-set inline — CSS
  media query tidak bisa override inline transform tanpa `!important` (boleh juga,
  tapi guard JS lebih bersih).
- Tetap satu handler rAF-throttled — jangan buat handler scroll kedua (lihat §8).
- CSS pendamping: `.hero-profil { will-change: transform; }` + reset
  `transform:none !important` di media reduce (fallback kalau JS mati).
