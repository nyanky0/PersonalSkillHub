# Spare Parts Browser (katalog sparepart IBT)

App HTML/JS statis + server python kecil untuk membaca katalog parts dari Excel item master
(`Final_Inventory_Tree*.xlsx`). Berdiri sendiri, bukan bagian dari app Laravel.

## Dua salinan yang beredar

| peran | folder | isi |
|---|---|---|
| app lengkap + compiler | `Sparepart HTML v1/SPAREPART_BROWSER` | `index.html`, `assets/{css,js}`, `images/`, `manuals/`, `TEMPLATES/`, `template_server.py`, `compile_catalog.py`, `catalog_sources.json`, `OPEN_BROWSER.bat`, `UPDATE_CATALOG.bat` |
| salinan katalog saja | `Sparepart Catalog/Sparepart Browser/SPAREPART_BROWSER` | `index.html`, `assets/`, `images/`, `manuals/`, `OPEN_BROWSER.bat` (tanpa server & compiler) |

Folder mesin (`Daihatsu 8DCM-32eF/`, `MAN L35MC/`, …) masing-masing punya `data/`, `images/`, `manuals/`.

**Selalu pilih salinan dengan `assets/js/data.js` termuda** dan pastikan folder `images/`/`manuals/`
berasal dari generasi yang sama — dua salinan ini punya slug, jumlah gambar, dan format part number yang
berbeda.

## Menjalankannya

- `template_server.py` = `SimpleHTTPRequestHandler` yang serve `APP_DIR` (= folder skripnya sendiri),
  default `127.0.0.1:8765`, `Cache-Control: no-store`.
- API order-template: `GET /api/templates` (daftar), `GET|PUT|DELETE /api/templates/<file>.csv`, backed by
  `TEMPLATES/` (maks 5 MB, UTF-8). Halaman order (cart) memanggil ini relatif — jadi **wajib HTTP**, dan
  folder yang tidak punya `TEMPLATES/` akan tampak error di drawer order.
- Untuk men-serve salinan katalog yang tidak punya server sendiri sambil mempertahankan API, pakai pola
  wrapper di SKILL.md dengan `ts.APP_DIR = folder_katalog`, `ts.TEMPLATE_DIR = <app lengkap>/TEMPLATES`.
- Port yang dipakai: 8765 = katalog terbaru (hasil scraping), 8766 = salinan app lengkap.

## Compiler & kenapa `OPEN_BROWSER.bat` menolak membuka browser

`compile_catalog.py` menghitung `SOURCE_ROOT = APP_DIR.parent.parent` — jadi app **harus** berada dua level
di bawah folder yang memuat semua folder mesin. `catalog_sources.json` memuat path relatif terhadap
`SOURCE_ROOT` + kategori `Main Engine`/`Aux Engine` per mesin.

Build **berhenti** kalau ada workbook yang ditemukan tapi tidak terdaftar:
`Catalog compile failed: Unconfigured machinery workbook(s) were found...`. `OPEN_BROWSER.bat` memanggil
compiler dengan `--if-changed` lebih dulu dan **tidak membuka browser** saat exit code bukan 0 — inilah
"errornya" yang dikeluhkan user. `data.js` lama tidak ditimpa saat gagal, jadi katalog sebelumnya aman.

Cara membuktikan akar masalahnya: bandingkan `SOURCE_ROOT` yang dihitung (`APP_DIR.parent.parent`) dengan
lokasi sebenarnya folder-folder mesin, lalu jalankan compiler dan lihat daftar "belum terdaftar". Kalau
folder mesin dipindah dari layout aslinya, **semua** path config jadi hilang sekaligus dan build berhenti
— bukan salah data.

Jebakan saat memperbaiki config: nama folder mesin sering melenceng dari `catalog_sources.json`
(`Akasakan` vs `Akasaka`, `Daihatsu 6DL-16Ae` vs `Daihatsu 6DL-16`, `Daihatsu 6PK16` vs `Daihatsu_6PK16`)
dan mesin baru bisa belum terdaftar sama sekali. Hitung dulu: berapa path config yang cocok, dan berapa
workbook ditemukan yang belum terdaftar.

`compile_catalog.py` hanya mengimpor stdlib — `openpyxl` **tidak** dibutuhkan untuk menjalankannya.

## Bentuk `assets/js/data.js`

`const APP_DATA = {"parts": [...], "machines": {slug: {...}}, "gallery": {slug: [...]}, "sidebar": ...,
"meta": {...}}`. Tiap entri galeri: `{imageRef, drawingNo, subPath, partCount, partIds}`; tiap mesin:
`{slug, name, manufacturer, rootCategory, totalParts, totalDrawings, manualFile, manualAvailable, tree}`.
`manualFile` bisa menunjuk berkas datar di `manuals/` (`manuals/xxx.pdf`) **atau** subfolder per-mesin
(`manuals/<slug>/xxx.pdf`) — dua konvensi ini hidup berdampingan, jadi jangan menganggap salah satu saja.

## Jebakan mutu data yang pernah terbukti

- **Part number terpotong di generator generasi baru** (`00234-046` padahal harusnya `00234-04620`) —
  ratusan part tanpa `partNo`. Bandingkan langsung nilai `partNo` versi lama vs baru; ini bug generator
  scrape, bukan bug app, dan fatal kalau katalog dipakai untuk order.
- **Slug mesin berubah antar-generasi** (`man-bw-l35mc` → `man-b-w-l35mc`, `mitsubishi-s6r-mpta` →
  `mitsubishi-s6r-mpta-mptk`). Nama folder gambar ikut berubah, jadi aman selama `data.js` dan folder
  gambar berasal dari generasi yang sama — campur keduanya dan gambar hilang tanpa error.
- **Manual tidak ikut tersalin** saat scrape (satu PDF masih menunjuk ke folder lama) → 404 hanya di mesin
  itu. Cek semua `manualFile`, bukan satu sampel.
- Jumlah gambar naik di generasi baru itu wajar (scrape lebih lengkap); yang perlu dicurigai justru
  penurunan per mesin.
