---
name: word-report-docx
description: Use when asked for a polished Word (.docx) report or manual.
---

# Laporan Word (.docx) yang rapi & reproducible

## Kapan dipakai

User minta "dokumentasi / laporan / manual dalam bentuk Word yang enak dilihat". Jangan susun .docx satu-satu
secara manual — buat **script generator** (python-docx) supaya isi bisa di-update dan di-regenerate.
Prasyarat: `pip install python-docx`.

## Aturan inti

1. **Satu helper gaya + satu script per dokumen.**
   - `docs/laporan/word_style.py` → class `Doc` (cover, heading, paragraf, bullet/numbered, tabel berwarna,
     callout, daftar isi manual, footer nomor halaman).
   - `docs/laporan/build_0X_<topik>.py` → import `Doc`, tulis isi, `d.save(OUT)`.
   - Simpan generator **di repo** bersama .docx-nya; di guide tulis "jangan edit .docx langsung — edit build
     script lalu regenerate".
2. **Pecah jadi beberapa file kecil.** `write_file` konten >±8K token bisa putus di tengah stream.
   Satu script = satu dokumen.
3. **Verifikasi hasil, jangan hanya percaya exit code 0.** Buka balik dengan python-docx:
   `Document(f)` → cetak `len(d.paragraphs)`, `len(d.tables)`, jumlah sel; cek 3–5 paragraf pertama (judul
   cover) dan jumlah tabel sesuai rencana isi.
4. **Isi harus akurat & bisa ditelusuri.** Tiap klaim status (SELESAI / SEBAGIAN / BELUM) butuh bukti kode
   (grep, migrasi, keluaran skrip). Yang belum diperiksa → tulis "PERLU VERIFIKASI", jangan ditebak.

## Style yang dipakai (dan kenapa)

- Warna aksen biru korporat + netral slate; font Calibri/Segoe UI; header tabel berwarna aksen, teks putih.
- Kolom status diberi warna sel sendiri (hijau = selesai, kuning = sebagian, merah = belum) supaya pembaca
  bisa memindai tanpa membaca.
- Cover: label kecil (organisasi · jenis laporan), judul besar, subjudul, meta (versi/tanggal).
- Daftar isi ditulis manual sebagai daftar bernomor (bukan field TOC) agar langsung terlihat tanpa F9.
- Callout = kotak berisi satu paragraf tegas untuk peringatan/info penting.
- Lebar kolom tabel dijumlahkan ±16,5 cm (A4, margin 2,5 cm) supaya tidak meluber.

## Bahasa & nada dokumen

Dokumen deliverable memakai bahasa formal dan padat — **bukan** gaya obrolan persona. Kalimat datar, istilah
konsisten, tanpa basa-basi. (Persona chat hanya untuk balasan ke user.)

## API helper

- `d.h1/h2/h3(teks)`, `d.p(teks)`, `d.bullets([...])`, `d.numbered([...])`, `d.page_break()`
- `d.table(headers, rows, widths=[cm...], status_col=i)` — kolom status otomatis berwarna
- `d.callout(judul, isi, "warn"|"info")`, `d.toc([...])`, `d.save(path)`
- Teks mendukung penanda `**tebal**` sederhana.

Template helper siap pakai: lihat `templates/word_style.py` pada skill ini.
