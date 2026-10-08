---
name: pre-existing-failure-triage
description: "Use when tests fail and you must find your own regressions."
---

# Pre-existing failure triage (baseline vs regresi)

Dipakai saat suite test / lint / build gagal, dan kamu harus melaporkan mana yang
**regresi dari perubahanmu** dan mana yang **sudah rusak sebelumnya**.

Aturan dasar: jangan pernah menuliskan "test-nya lewat semua" atau "yang gagal cuma X"
tanpa membuktikan status baseline. Klaim "semua pre-existing" itu klaim keras — buktikan
atau jangan ucapkan.

## Langkah

### 1. Jalankan cakupan tersempit dulu
Filter per kelas/fitur yang kamu sentuh. Cepat dan langsung memberi sinyal:

```bash
php -d memory_limit=-1 artisan test --filter="NamaKelasTest"
```

### 2. Pindai per-file untuk menemukan file yang bermasalah
Suite penuh sering OOM atau membanjiri output. Jalankan satu file per proses supaya
kegagalan bisa diatribusikan — pakai `scripts/test_sweep.sh`:

```bash
bash scripts/test_sweep.sh tests/Feature 512M scratch/sweep.txt
```

Catatan penting: `-d memory_limit=...` **tidak selalu diwariskan** ke proses anak yang
di-spawn test runner. Kalau suite penuh tetap OOM walau limit sudah dinaikkan, jangan
terus menaikkan limit — pecah per-file (limit ikut terpasang di proses itu) dan cari
file pemicunya.

### 3. BUKTIKAN pre-existing dengan baseline
Kalau perubahan sudah ter-commit, `git stash` tidak berguna. Checkout file sumber dari
commit **sebelum** perubahan, jalankan subset yang sama, lalu kembalikan:

```bash
HEAD=$(git rev-parse HEAD)
git checkout <BASE_COMMIT> -- app/ config/ routes/ tests/ resources/
php -d memory_limit=-1 vendor/bin/phpunit tests/Feature/BermasalahTest.php tests/Feature/LainTest.php
git checkout $HEAD -- app/ config/ routes/ tests/ resources/
git status --short                                   # harus kosong
```

- Pakai **subset yang sama persis** di baseline dan di HEAD. Membandingkan angka agregat
dari suite yang berbeda bukan bukti.
- Jumlah failure/error identik ⇒ pre-existing.
- Migrasi DB boleh dibiarkan ter-apply saat baseline run: kolom ekstra umumnya tidak
menggagalkan kode lama. Kalau ragu, persempit `--filter`-nya.
- Selalu kembalikan file dan pastikan `git status --short` bersih, plus
`git rev-list --left-right --count origin/<branch>...HEAD` = `0 0`.

### 4. Pisahkan saat melapor
Sajikan dua blok: **"dari perubahan ini"** dan **"pre-existing (dibuktikan vs baseline)"**,
masing-masing dengan angka nyata dan nama file/method yang gagal — bukan hanya total.

## Pitfalls

- **"Lulus semua" berdasarkan filter sempit itu menyesatkan** — filter tidak menyentuh
kode lain. Selalu sebutkan cakupan yang benar-benar dijalankan.
- **Suite penuh OOM bukan bukti perubahanmu salah.** Cari file pemicunya lewat sweep,
lalu bandingkan file itu ke baseline.
- **Jangan menghijaukan test dengan melonggarkan assertion** saat perilakunya memang
sengaja berubah. Perbarui fixture **dan** tambahkan test baru yang menegaskan perilaku
baru; sebutkan keduanya di laporan.
- **Jangan membungkus rangkaian percobaan gagal sebagai "workflow yang tervalidasi".**
Kalau akar masalah belum ketemu, katakan belum ketemu dan sebutkan langkah verifikasi
manual untuk user.
- Kegagalan yang hilang setelah retry bukan pelajaran; polanya (retry, jalankan ulang
dengan limit lebih besar, persempit scope) yang dilaporkan.

## Berkas pendukung

- `scripts/test_sweep.sh` — pindai test per-file (PHPUnit/Laravel-shaped), tulis hasil
PASS/FAIL/UNKNOWN per berkas ke satu file hasil. Adaptasi perintah runner-nya untuk
stack lain.
