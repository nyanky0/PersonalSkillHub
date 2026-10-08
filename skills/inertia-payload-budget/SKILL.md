---
name: inertia-payload-budget
description: Use when an Inertia page payload is too heavy to ship.
---

# Anggaran payload halaman Inertia

Untuk halaman Laravel + Inertia (React/Vue) yang mengirim banyak prop dalam satu request — katalog,
daftar master data, halaman dengan dropdown filter besar. Tujuannya menurunkan berat halaman **tanpa
menghapus fiturnya**, dan memverifikasinya tanpa browser.

## Urutan kerja

1. **Ukur per-prop, jangan menebak.** Ambil HTML yang benar-benar dikirim (dengan sesi login), parse
   atribut `data-page`, urutkan prop dari yang terberat. Skripnya di
   `references/typeahead-and-measurement.md`. Skrip bootstrap yang memanggil controller langsung **tidak**
   menghitung prop shared — angkanya akan menyesatkan.
2. **Yang terberat hampir selalu daftar opsi filter**: `SELECT DISTINCT` atas kolom bernilai unik banyak
   yang dikirim sebagai prop bersama, padahal `<select>` berisi ribuan opsi tidak terpakai siapa pun.
3. **Pindahkan daftar itu ke endpoint saran berbatas** (`field` whitelist, `q`, `limit` di-cap 25–50),
   lalu ganti `<select>` menjadi `<input list>` + `<datalist>` yang mengambil saran saat mengetik
   (debounce ±300 ms). Resep lengkapnya di `references/typeahead-and-measurement.md`.
4. **Penyaringan tetap di server.** Daftar barisnya sudah ter-paginasi, jadi memfilter di client hanya
   menyaring satu halaman dan menyesatkan. Setelah mengganti nama query param, uji tiap kombinasi dengan
   curl (nilai awalan, nilai mengandung, nilai kosong) dan cek jumlah barisnya — bukan cuma HTTP 200.
5. **Ukur ulang setelah setiap perubahan** dan laporkan angka sebelum/sesudah. "Halaman jadi ringan" bukan
   laporan; "826 KB → 612 KB, prop `options` 148 KB → 2 KB" adalah laporan.
6. **Perbarui dokumentasi proyek pada langkah yang sama** kalau repo punya panduan pengembangan wajib —
   perubahan payload/filter yang tidak tercatat akan dianggap belum selesai.

## Aturan yang menentukan

- **Nilai filter yang panjang/bertingkat butuh “mengandung”, bukan awalan.** Path hierarki
  (`Main Engine > Akasaka 7UEC37LA > Engine Frame`) tidak pernah cocok dengan `LIKE 'Engine%'`; user
  melihat “0 hasil” untuk kata yang jelas ada di datanya dan membacanya sebagai fitur rusak. Sediakan DUA
  parameter: `*_like` (awalan, untuk nilai satu token supaya angka node/hierarki tetap akurat) dan `*_q`
  (mengandung, untuk kotak ketik bebas).
- **Escape wildcard sebelum masuk `LIKE`** (`addcslashes($v, '%_\\')`). `%` yang lolos jadi wildcard dan
  diam-diam mengembalikan seluruh tabel.
- **Samakan filter baru di SEMUA jalur** yang membaca kumpulan data yang sama: tabel, ekspor CSV,
  statistik, endpoint saran. Kalau tidak, jumlah baris ekspor tidak cocok dengan yang terlihat.
- **Endpoint saran tetap tunduk pada scope filter/visibilitas** — jangan bocorkan nilai dari baris yang
  tidak boleh dilihat user, dan jangan menyusun nama kolom dari input (whitelist array, sisanya 422).
- **Menambah atribut yang bisa dicari itu tiga perubahan**: server melengkapi data, predikat filter
  komponen pencarian menyertakannya, dan form mengisi/menampilkannya. Sangat mudah hanya mengerjakan yang
  	pertama lalu menganggap fiturnya selesai.
- **Cache key daftar master data ber-versi wajib punya satu sumber kebenaran.** Kode membaca key `..._v3`
  sementara invalidasi menyentuh `..._v2` → UI menyajikan data basi setelah perubahan bentuk data, dan itu
  tampak seperti perubahan yang tidak bekerja.

## Artefak hasil jalan tidak boleh mendarat di folder produksi saat test

Penulis log/ekspor (mis. log Excel per push, hasil ekspor, file generate) tetap menulis file di setiap test
yang menjalankan perintah terkait — jalur offline pun mengeluarkan log. Folder hasil produksi jadi bercampur
sampah test dan user menemukannya sebagai “file hantu” yang sulit dibedakan dari hasil asli. Percabangkan di
SATU tempat penulisnya:

```php
$dir = app()->runningUnitTests()
    ? storage_path('app/push-logs/tests')
    : storage_path('app/push-logs');
```

Buktikan dengan menghitung jumlah file folder produksi **sebelum vs sesudah** `php artisan test` — harus
sama, sementara subfolder `tests/` bertambah.

## Verifikasi tanpa browser

- `npm run build` sukses bukan bukti halaman jalan: komponen JSX yang dipakai tapi belum di-import hanya
  meledak saat halaman dibuka (`ReferenceError` → halaman blank). Jalankan pemeriksa impor lebih dulu.
- Bukti sah untuk halaman = request HTTP sungguhan dengan sesi login, lalu cek status, ukuran byte, dan
  ketiadaan penanda error. Simpan HTML-nya ke file; `curl -o /dev/null -w '%{size_download}'` bisa
  melaporkan `0` di git-bash Windows walau responsnya penuh (`stat -c%s` pada file hasil).
- Uji juga jalur negatif: `field` di luar whitelist harus 422, bukan diterima sebagai nama kolom.

Skrip pengukuran per-prop, resep endpoint saran + komponen typeahead, dan cara mengukur ulang ada di
`references/typeahead-and-measurement.md`.
