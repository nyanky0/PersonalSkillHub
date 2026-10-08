# Paritas Field: Database Lokal ↔ UDF SAP B1

Dipakai saat user bertanya "masih ada field yang perlu ditambah di tabel / di SAP?" atau
saat menyiapkan CompanyDB baru. Tujuannya: web app tidak lagi menemukan field yang kurang
setelah dokumen mulai di-push (payload ditolak Service Layer, kolom null karena migrasi
menyusul).

## Tiga lapis yang harus diaudit, bukan satu

| Lapis | Cara cek | Kalau kurang |
|---|---|---|
| Kolom tabel lokal (level header) | `PRAGMA table_info(<tabel>)` / `Schema::hasColumn` | migrasi baru, **satu** migrasi berisi semua kolom + tabel pendukung |
| Field baris dokumen | cek kolom JSON `items_payload` | **jangan** buat kolom — baris dokumen hidup di JSON |
| UDF sisi SAP | grep deklarasi UDF di `IBT_SAP_Customization_Setup.cs` | tambah deklarasi UDF, lalu script dijalankan di SAP |

Field yang **hanya** muncul di tabel dokumen SAP (AWB, courier, HS alert, expiry, last PO,
price konversi, qty order/ready, part number lama) tetap dicatat di migrasi lokal hanya
kalau level **header** — kalau level baris, cukup di `items_payload`.

## Pola deklarasi UDF di `IBT_SAP_Customization_Setup.cs`

Ikuti gaya data-driven yang sudah ada: array definisi `{ Field, Desc, Size }` lalu loop ke
tabel tujuan. Satu set header di-loop ke semua tabel header dokumen pengadaan, satu set baris
ke semua tabel baris:

```csharp
// header: OPRQ (RL), OPQT (PQ), OPOR (PO)
foreach (var t in new[] { "OPRQ", "OPQT", "OPOR" }) AddUdfSet(t, headerUdfs);
// baris: PRQ1, PQT1, POR1
foreach (var t in new[] { "PRQ1", "PQT1", "POR1" }) AddUdfSet(t, lineUdfs);
```

Aturan:
- Daftarkan method baru itu di titik orkestrasi setup (tempat `CreateCatalogOITMUDFs()` dipanggil).
- Semua UDF bersifat **idempoten**: yang sudah ada hanya memunculkan warning — aman dijalankan ulang.
- Nama UDF selalu berprefix `U_SOL_`, size string dibatasi (nVarChar 50–254).

## CompanyDB baru = script UDF wajib dijalankan dulu

UDF/UDT/UDO tidak ikut pindah saat ganti CompanyDB. Jadi setiap kali basis data SAP baru
dipakai (mis. `IBTWEBAPP` menggantikan DB demo), `IBT_SAP_Customization_Setup.cs` **harus
dijalankan ulang di DB itu** sebelum push dokumen dari web app — kalau tidak, SAP menolak
field yang tidak dikenal. Sebutkan ini eksplisit di laporan/handover, karena ini pekerjaan
sisi SAP yang cuma bisa dilakukan user.

Urutan prasyarat yang sama berlaku untuk bin location: sublevel warehouse (SL1–SL4) harus
dibuat dulu di SAP, baru push bin dari web app diterima.

## Migrasi aman untuk basis data yang sudah terisi

- Bungkus tiap kolom dengan `if (!Schema::hasColumn(...))` (atau map definisi lalu loop) supaya
  migrasi aman diulang dan tidak meledak di DB yang sudah punya kolom itu.
- Kolom baru: `nullable()` atau `default()`. Jangan `->after()` (tidak didukung sqlite).
- Tabel pendukung baru: `if (!Schema::hasTable(...))` di `up()`, dan `dropIfExists` di `down()`.
- `down()` wajib ada dan menghapus tepat apa yang `up()` tambahkan.
- **Jangan** `migrate:fresh` di basis data kerja — katalog/seed bisa hilang. Verifikasi kolom
  dengan probe read-only.

## Seeder & DatabaseSeeder

- Seeder dalam proyek ini didaftarkan satu per satu (`$this->call(X::class);`), bukan array —
  pasang di blok terakhir dengan komentar bernomor lanjut, dan tulis dengan `updateOrInsert`
  berkunci natural key supaya idempoten.
- Seeder isi konfigurasi (template email, cost center, kredensial) sebaiknya bawa data default
  yang bisa langsung dipakai, bukan tabel kosong.

## Verifikasi yang meyakinkan

1. `php -l` untuk setiap file PHP baru.
2. Probe read-only `scratch/verify_*.php` yang mencetak `ADA`/`HILANG` per kolom + jumlah baris
   tabel baru — bukan `SELECT` manual yang harus dibaca mata.
3. Baca ulang commit-message/artefak hasil generate: exit code bukan bukti isi (lihat bawah).

## Jebakan: exit code 0 dengan artefak kosong

Perintah yang mengalihkan output ke file (`php artisan route:list --json > scratch/routes.json`)
bisa selesai dengan **exit 0 tapi file 0 byte** — terlihat sukses, isi tidak ada. Karena itu:

- Setiap artefak hasil redirect diverifikasi ukurannya (`wc -c` / jumlah baris) sebelum dipakai
  atau dilaporkan.
- Jangan pernah menyimpulkan "tidak ada masalah" dari exit code saja; kalau laporan sebelumnya
  bersandar pada artefak itu, katakan artefaknya yang gagal, bukan menutupinya.
- Hasil berukuran wajar tapi isi dipertanyakan → jalankan ulang di foreground, bukan di
  background wrapper.
