---
name: run-local-web-app
description: "Use when asked to run a local app: serve it and verify."
version: 1.0.0
metadata:
  hermes:
    tags: [web, local-server, verification, static-app]
    related_skills: []
---

# Menjalankan & memverifikasi app lokal sampai bisa dibuka user

Untuk permintaan seperti "run app-nya, buka ke browser", "kok error", "aku mau cek". Deliverable-nya
bukan "server sudah distart" tapi **URL yang terbukti memuat**, plus sebab persisnya kalau appnya error.

## Urutan kerja

1. **Petakan dulu sebelum mengeksekusi apa pun.** Cari entry point, skrip server, launcher, dan folder
   aset (`find . -maxdepth 3 -type d`), lalu baca `index.html` + skrip server + `.bat` launcher. Cek juga
   `__pycache__` — itu tanda app python, bukan app statis biasa.
2. **Baca dulu isi launcher `.bat`.** Kalau dia menjalankan build/compile sebelum membuka browser,
   **jangan pakai launcher itu** untuk sekadar membuka app: build yang gagal akan menolak membuka browser
   dan menyembunyikan fakta bahwa app + datanya sendiri sehat. Jalankan servernya langsung, diagnosa
   build-nya terpisah.
3. **Nyalakan server app-nya sendiri** (`template_server.py`, `manage.py runserver`, dst) dengan
   `terminal(background=true)`. Kalau appnya murni statis tanpa skrip server, `py -3 -m http.server <port>`.
   Pilih port bebas — cek `netstat -ano | grep <port>` lebih dulu.
4. **Verifikasi SEMUA endpoint dengan curl SEBELUM membuka browser:** `index.html`, tiap js/css yang
   direferensikan, berkas data terbesar, satu aset biner (gambar/pdf), dan API apa pun yang dipanggil
   halaman. Cek `status` + `Content-Length` + `Content-type`, bukan cuma "ada respons".
5. **Baru buka browser user:** `cmd /c start "" "http://127.0.0.1:<port>/index.html"`.
6. **Konfirmasi browser benar-benar memuat**, jangan berasumsi: poll log proses server
   (`process_manage action=poll`) dan pastikan baris akses 200 untuk `index.html` + seluruh js.
   `favicon.ico` 404 itu normal, bukan temuan.

Kalau ada dua salinan app/katalog, jalankan **satu server per salinan dengan port berbeda** dan sebutkan
port mana = salinan mana saat melapor; dua salinan dengan slug/aset berbeda gampang tertukar.

## Aturan yang menentukan

- **Jangan pernah serahkan `file://`.** App yang "cukup di-double-click" tetap harus di-serve lewat HTTP:
  `fetch()`/XHR ke path API relatif gagal di `file://`, jadi halaman tampak rusak padahal datanya utuh.
  Serve lewat HTTP selalu, sekalipun appnya statis.
- **Root yang dihitung dari lokasi skrip (`APP_DIR.parent.parent`) rusak diam-diam saat folder dipindah.**
  Gejalanya bukan satu berkas hilang, tapi **semua** sumber yang dikonfigurasi dilaporkan hilang
  sekaligus **dan** semua yang ditemukan dilaporkan "belum dikonfigurasi" — jadi build berhenti. Periksa
  derivasi root itu sebelum mencurigai datanya; perbaikannya = taruh app di kedalaman folder yang
  diharapkan, atau override konstantanya saat runtime. Buktikan dengan membandingkan `SOURCE_ROOT` yang
  dihitung skrip terhadap lokasi folder sumber yang sebenarnya.
- **Memakai ulang skrip server milik app untuk doc root lain** (biar API app tetap hidup untuk salinan
  kedua tanpa mengedit app-nya):
  ```python
  sys.path.insert(0, str(APP_V1))
  import template_server as ts
  ts.APP_DIR = folder_katalog_lain
  ts.TEMPLATE_DIR = APP_V1 / "TEMPLATES"
  ThreadingHTTPServer(("127.0.0.1", port), ts.SparePartsHandler).serve_forever()
  ```
  Simpan wrapper-nya di luar folder app (mis. `$LOCALAPPDATA/Temp/`), jangan menambah berkas ke folder
  milik user.
- **Jangan mengubah app user supaya bisa dijalankan.** Perbaikan tambahan yang jelas aman (mis. menyalin
  satu aset yang hilang ke tempat yang direferensikan data) boleh, tapi sebutkan di laporan.
- **`curl -o /dev/null` di git-bash Windows melaporkan `bytes=0` + exit 23** (write error), dan itu bukan
  kegagalan server. Tulis ke berkas temp nyata (`$LOCALAPPDATA/Temp/...`) atau pipe ke `wc -c`, baru
  simpulkan.
- **Nama berkas berspasi harus di-URL-encode saat diprobe** (`urllib.parse.quote`), kalau tidak probe-nya
  balas `URL can't contain control characters` dan menghasilkan 404 palsu.

## Verifikasi bundel data hasil generate

App katalog/dashboard biasanya memuat satu berkas raksasa (`assets/js/data.js` berisi
`const APP_DATA = {...}`, atau `data.json`). Periksa berlapis, jangan cukup "halaman kebuka":

1. **Validitas:** regex `const APP_DATA\s*=\s*(\{.*\})\s*;\s*$` (atau baca langsung .json) lalu
   `json.loads`. JSON rusak = halaman blank tanpa error yang terlihat. Cek juga `NaN`/`Infinity` yang
   bukan JSON valid.
2. **Jumlah:** bandingkan `meta.totalParts`/`totalMachines` dengan panjang list sebenarnya, dan dengan
   angka di laporan/report build. Angka yang diklaim adalah assertion — kalau beda, hitung ulang.
3. **Rujukan aset:** ambil satu `imageRef` per entitas dari indeks galeri dan tiap `manualFile`/berkas
   lampiran dari data mesin, lalu HTTP-probe semuanya (`urllib.request` + `quote`). Hitung 200 vs gagal.
4. **Cocokkan kunci data dengan nama folder aset.** Kalau generator mengubah slug antar-generasi
   (mis. `man-bw-l35mc` → `man-b-w-l35mc`), gambar tidak muncul **tanpa error apa pun** — cek
   `machines.keys()` vs isi folder `images/`.
5. **Bandingkan antar-generasi** (versi lama vs hasil scrape baru): jumlah gambar per mesin yang turun =
   drawing hilang; jumlah part yang sama tapi isi berubah (mis. part number terpotong) = bug generator,
   bukan bug app.
6. Laporkan angka ("21 dicek, 1 gagal"), bukan "sepertinya aman".

## Pilih permukaan browser yang benar

Tiga permukaan berbeda, dan salah pilih itu biaya paling mahal di skill ini:

- **`drive_preview` / `desktop_preview` (preview pane Hermes)** — yang paling cepat untuk memeriksa halaman
  app lokal: `desktop_preview open` → `drive_preview elements` → `read`. `elements` mengembalikan ref elemen
  beserta **perannya** (`link`, `button`, `input`), dan itu sudah cukup untuk memutuskan di mana bug berada.
  Nama ref yang mengungkap tipe elemen (mis. `lnk-https-facebook-com` = benar-benar `<a>`, bukan teks polos)
  adalah bukti yang jauh lebih kuat daripada membaca JSX.
- **Playwright + Edge headless** — untuk asertion otomatis, viewport desktop lebar, dan screenshot
  (lihat bagian di bawah). Pakai ini kalau butuh script yang bisa dijalankan ulang.
- **`file://`** tidak pernah boleh diserahkan ke user (lihat aturan di bawah).

Urutan yang hemat: cek port dulu (`netstat -ano | grep -E ":(<port>)"`), karena dev server sering **sudah
hidup** di mesin user — jangan start satu lagi di port berbeda lalu memeriksa app yang salah.

Login ke app yang punya halaman quick-test biasanya lebih cepat lewat tombol auto-fill-nya: klik auto-fill,
lalu `type` password dengan `submit: true` pada field terakhir. Kalau app punya pemilihan cabang, tekan
submit-nya dulu — `open`/`goto` ke URL target sebelum cabang aktif akan memantul balik ke halaman pemilihan.

Mode yang tidak punya URL sendiri (mis. tombol Edit yang mengubah state React) **tidak bisa** dipicu lewat
preview pane secara andal. Kalau verifikasi butuh mode itu, beralih ke Playwright atau minta user
mengkliknya — dan katakan terus terang bahwa bagian itu belum terverifikasi.

## Verifikasi UI di browser asli (layar lebar)

Preview pane Hermes sempit → tata letak desktop (sidebar tetap, kolom tabel) masuk breakpoint
mobile dan tidak pernah terlihat di sana. Untuk itu pakai **browser yang sudah terpasang di mesin
user** lewat Playwright — jangan memasang browser baru (kalau user anti Chrome, pakai Edge).

1. `playwright` biasanya sudah ada dari `npx playwright install` sebelumnya. Script cukup
   `require('playwright')`; kalau gagal, cari `<home>/AppData/Local/npm-cache/_npx/*/node_modules/playwright`
   dan `require` dari path itu — supaya menjalankannya cukup `node scripts/verify-*.cjs`, tanpa `NODE_PATH`.
2. `chromium.launch({ channel: 'msedge', headless: true })` + viewport ≥ 1680×1000. Sebutkan browser
yang dipakai di laporan.
3. **Jangan menebak nama field form login.** Dump dulu
   `[...document.querySelectorAll('input')].map(i => ({name: i.name, type: i.type}))` — app sering
   memakai `username` (bukan `email`), dan kredensial yang sah tidak selalu berupa alamat email.
   Login gagal → baca pesan validasinya, jangan ulang berkali-kali (kena throttle).
4. Kalau app punya pemilihan cabang/tenant/workspace, selesaikan dulu (tekan tombol submit-nya)
   baru `goto` URL target — tree/menu banyak yang baru terisi setelah cabang aktif.
5. **Assert dari teks DOM, bukan screenshot** (model belum tentu punya vision). Ambil
   `textContent`/`innerText` dari selector spesifik lalu cetak daftarnya. Cara menemukan kontainer
   section yang benar: filter elemen yang `textContent`-nya memuat judul section **dan** punya ≥2
   `<button>` (baris pohon/menu punya tombol chevron), lalu ambil yang paling kecil — menghindari
   kejebak elemen pembungkus halaman.
6. Hasilnya daftar assertion `PASS/FAIL` + `exit code 1` kalau ada yang gagal, plus screenshot
   sebagai lampiran laporan. Simpan scriptnya (`scripts/verify-*.cjs`) supaya bisa dijalankan ulang.
7. Kalau app di-build (Vite/webpack), pastikan nama chunk yang dikirim **berubah** setelah
   `npm run build` (cek `public/build/manifest.json`); hash yang tetap = yang diuji masih bundle lama.

### Baris kosong = sentuhan pertama bug key
Kalau satu komponen UI diberi data dari **dua sumber** (props Inertia untuk level atas + lazy fetch
untuk anaknya), tiap sumber sering memakai nama field berbeda untuk hal yang sama. Gejala di layar:
**baris/folder muncul tapi tanpa tulisan**, dan user membacanya sebagai "fitur belum dikerjakan".
Jadi assertion wajib: hitung elemen label yang teksnya kosong — "0 label kosong" itu bukti, bukan
asumsi. Perbaikan ada di pembaca (`node.part_name ?? node.label` sebagai fallback), bukan di backend.

### Baca DOM dulu, baru simpulkan bug — dua kali nyaris salah
Layar **teks** sudah cukup untuk memutuskan di mana bug UI Inertia/Livewire berada. Kalau sebuah elemen
terlihat "hilang" atau "belum dikerjakan", buka halamannya lalu inventaris elemen sebelum membaca kode.
Dua bacaan yang paling sering menyelamatkan:

- **Hitung elemen yang sama, bukan yang pertama.** Kalau elemen muncul dua kali di layar padahal
  kodenya hanya satu, prop sumber sudah berisi nilai yang berbeda — payload yang datang ke halaman terlalu
  gemuk dan komponennya menerima daftar tak terfilter. Cek berapa kali elemen itu benar-benar dirender;
  jangan berhenti pada kemunculan pertama.
- **Elemen yang “tidak dirender” biasanya memang ada di kode, tapi di dalam cabang ternary mode.** Cari
  `{mode ? (form) : (view)}` sebelum menyimpulkan komponennya hilang: section yang hidup di cabang form
  hanya ada saat mode itu aktif, sehingga dari luar tampak tidak pernah dibuat. Perbaikannya = pindahkan
  section ke cabang yang juga tampil di mode baca, bukan menambah komponen kedua yang isinya berulang.

Corollary: fitur yang gagal aktif setelah hot-reload sering **sudah benar** dan hanya kurang hard reload +
bundle hash baru. Cek `public/build/manifest.json`; hash chunk yang tidak berubah = yang diuji masih bundle
lama, dan itu penyebab tersering dari “perbaikanku tidak bekerja”.

### Jebakan waktu menulis script verifier
Glob di dalam komentar blok JS/TS seperti `_npx/*/node_modules` **menutup komentar lebih awal**
(`*/`) → `SyntaxError: Unexpected token`. Tulis path contoh tanpa glob, atau pakai komentar `//`.

## Melapor

- Sebutkan **URL siap klik per port + folder yang di-serve**, dan bahwa servernya hidup sebagai proses
  background (jangan suruh user menutup terminal).
- Kalau ada error: **kutip pesan error persisnya** dan sebutkan langkah mana yang gagal, plus akar
  penyebabnya — bukan "coba jalankan ulang".
- Pisahkan tegas: (a) app jalan, (b) build/compile gagal beserta sebabnya, (c) temuan mutu data. Jangan
  campur "appnya sehat" dengan "katalognya masih ada bug".
- Bahasa Indonesia.

## Referensi

- `templates/edge-ui-verify.cjs` — kerangka script verifikasi UI (Edge + Playwright: login → pilih
  cabang → assert teks DOM → screenshot → exit code) untuk disalin ke `scripts/` project.
- `references/inertia-form-guards-and-validation.md` — bug form Inertia/React: validasi desimal vs kolom
  `decimal`, guard tombol back vs router Inertia (plus cara mengujinya sebagai logika murni), section yang
  hidup di cabang ternary mode, dan remarks bertaut di mode edit vs mode baca.
- `references/spare-part-browser.md` — layout, server, compiler, dan jebakan mutu data app Spare Parts
  Browser katalog IBT (di bawah `D:\Metrodata\IBT\TEST`).
