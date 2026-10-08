---
name: ai-slop-audit
description: "Advanced AI-slop audit — batch image validation, slop pattern detection, CSS analysis, CTA integrity, auto-report generation."
---

# AI-Slop Audit (Advanced)

Audit komprehensif halaman web untuk mendeteksi AI-slop: broken images, fake stats, copy palsu, CSS issues, CTA integrity. Output: structured report + auto-fix suggestions.

## Kapan dipakai
- User nanya "cek AI slop apa nggak", "audit ini", "review halaman"
- QA sebelum production deploy
- Review landing/copy untuk klien

## Verdict dulu, baru fix
Kalibrasi jujur: banyak output LLM yang copy & desainnya udah rapi — bedakan "tanda slop spesifik" vs "assemble bagus". Jangan langsung vonis "slop total".

## Workflow

### Phase 1: Collect
1. Baca full file HTML/CSS/JS atau navigate ke URL via browser
2. Ekstrak semua elemen potensial slop:
   - Gambar (`<img>`, `background-image`, `url()`)
   - Teks copy (heading, paragraf, CTA)
   - CSS variables (`:root`, `var()`)
   - Angka/statistik (`\d+\+`, `\d+%`)
   - CTA buttons & forms

### Phase 2: Detect (Batch)

#### 1. Image Validation
```bash
# HEAD-check SEMUA URL gambar (bukan cuma eyeball)
for url in $(grep -oP '(?<=src=")[^"]+|(?<=url\()[""][^""]+[""]]' index.html | grep -v 'data:image'); do
  curl -I "$url" 2>/dev/null | head -1
done
```
- 404 = bug, bukan slop
- ⚠️ URL Unsplash: `photo-*` di `images.unsplash.com`, `premium_photo-*` di `plus.unsplash.com`
- ⚠️ Jangan declare 404 "rusak" kalau cuma salah host — cek ulang di host bener (lihat skill `stock-media-sourcing`)
- ⚠️ Kalau nyari URL via search API (`unsplash.com/napi/search/photos`), `results[].id` itu slug PENDEK, BUKAN nama file CDN. Segment `photo-<id>` / `premium_photo-<id>` yang bener ada di `results[].urls.raw`. Jangan construct URL dari `.id` langsung — pasti 404.
  - Contoh: `.id == "5Zwpg2QJq7g"` → 404 kalau jadi `photo-5Zwpg2QJq7g`
  - Tapi `urls.raw` ngasih `premium_photo-1755004626852-61ae2838a84e` → 200
- Timestamp URL aneh (misal `photo-1755...` tahun 2026, gak match pola slug normal) = indikasi URL di-hallucinate
- Duplikasi gambar yang sama dipakai di 2 tempat (hero + band) = tanda males/gak kaya

#### 2. Copywriting — Pola Fingerprint AI Slop
```bash
# Grep pola slop
grep -P '\d+\+ (Menu|Item|Varian|Produk|Parfum|Klien|Proyek)' index.html
grep -P '\d+% (Manual|Puas|Bergaransi|Bebas|Gratis)' index.html
grep -P 'bikin .* kayak baru|langganan balik lagi' index.html
```
- Pola angka berulang `X+` / `X%` (`15+ Menu`, `10+ Varian`, `20+ Parfum`, `100% Manual`) = slop paling umum
- Klaim kosong ("bikin mobil kayak baru", "langganan balik lagi") tanpa angka/rasa lokal
- Statistik yang gak nyambung ke bisnis real (angkanya cuma tempelan)
- Yang justru BAGUS & manusiawi (pertahankan): split-line headline, kosakata kasual lokal ("Perut kenyang", "Nunggu mobil sambil santap"), struktur 3-part

#### 3. CSS & Teknis
```bash
# Grep var CSS undefined
grep -oP 'var\(--[\w-]+\)' index.html | sort -u | while read var; do
  if ! grep -q "$var" index.html | grep -q ':root'; then
    echo "UNDEFINED: $var"
  fi
done

# Emoji corrupt
grep -P '[\x{fffd}-\x{10ffff}]' index.html
```
- Variable CSS yang dipakai tapi gak dideklarasiin (misal `var(--paper)` ga ada di :root)
- Grid kolom kosong (grid `repeat(3,1fr)` tapi cuma 2 card)
- Emoji corrupt (`�`) / placeholder nomor telepon `08xx-xxxx-xxxx`
- Hardcode count/teks yang udah di-update JS (false-positive, jangan laporin)

#### 4. CTA Integrity
- Booking form / tombol "Booking" di bisnis walk-in yang selalu rame = UX lie (janji slot yang gak bisa dipenuhi)
- Lebih jujur & lebih konversi: ganti ke "OTW ke Tempat" / link Google Maps langsung
- Hapus nomor telepon kalau emang belum siap di-call — jangan tinggalin placeholder 08xx

### Phase 3: Report
Struktur output:

```
## AI-SLOP AUDIT REPORT
**Halaman:** [URL/filename]
**Tanggal:** [date]

### [BUG] Issues
- [broken image / 404 / broken link]

### [SLOP] AI-generated markers
- [pola angka X+, klaim kosong, copy generic]

### [GOOD] Things to keep
- [copy yang manusiawi, struktur bagus]

### [FIX] Auto-fix suggestions
- [placeholder:angka, angka placeholder ditandai manual]
- [CTA rewrite, gambar replace]
```

## Prinsip anti-slop waktu FIX
- JANGAN ngarang angka buat ngisi. Pakai fakta yang UDAH ADA di halaman (jam buka, harga, hitungan layanan).
- Angka placeholder (harga service baru) WAJIB kasih tau user buat dicek-ganti sendiri, jangan pass off as final.
- Udah salah diagnosa → koreksi eksplisit dalam response, jangan diam.