# Paritas dengan implementasi acuan (HTML/legacy) + desain verifier

Dipakai saat webapp (Laravel/Inertia/React) harus menampilkan data **sama persis** dengan
aplikasi acuan yang sudah ada (mis. browser katalog HTML lama), atau saat membangun ulang
logika yang sudah ada di tempat lain. Aturan user: "ikutin acuan, jangan bikin sendiri
nanti jatohnya berbeda" — berlaku ke SELURUH kolom/tampilan, bukan cuma yang dikeluhkan.

## 1. Derivasi nilai: port aturan acuan, jangan didekati aritmetika

- Baca fungsi acuan (mis. `derive_path`/`splitClassification` di `assets/js/data.js` atau
  di command importer) dan salin **aturan + daftar kandidatnya** apa adanya.
- ❌ "Buang 2 segmen pertama" selalu pecah: ada baris yang prefix-nya 1 segmen saja, dan ada
  yang 4. Aturan acuan bersifat semantik ("buang segmen yang sama dengan kategori / nama
  mesin / merek / model"), jadi implementasinya juga harus semantik.
- Kandidat yang tak bisa disusun ulang dari kolom DB harus diambil dari data lain: nama
  mesin diambil dari baris node induk (mis. baris L1 `Equipment: <nama>`) + cache statis
  per request (`machineNameFor()`); fallback lookup supaya accessor tetap benar walau
  query parsial.
- ⚠️ Nilai mentah di DB sering = jalur penuh (hasil importer), sedangkan yang ditampilkan
  acuan = bentuk turunannya. Jangan render nilai mentah hanya karena ada di DB.

## 2. Satu sumber kebenaran untuk nilai turunan

- Taruh aturan di model: `static splitClassificationPath(...)` + accessor
  (`getXRelativeAttribute()`). Panggil dari SEMUA jalur: kolom daftar, detail, export CSV,
  pohon/filter sidebar, breadcrumb, script verifier.
- Kalau aturan harus ditulis ulang di JS (breadcrumb), beri komentar silang di kedua sisi —
  ubah satu, ubah yang lain.
- Nilai turunan dipakai sebagai kunci filter juga (`classification_like` memakai segmen
  hasil turunan), supaya pohon dan kolom tidak bisa berbeda.

## 3. Verifier: bandingkan dengan data acuan, bukan dengan ekspektasi sendiri

- Dump data dari berkas acuan itu sendiri (`data.js`/CSV sumber) dan bandingkan **seluruh
  baris**, bukan sampel. Lulus = 0 beda; cetak jumlah baris yang dicek.
- **Baris ambigu dilewati sebagai warning, bukan FAIL.** Kalau satu part number muncul di >1
  baris acuan dengan nilai berbeda, tidak ada jawaban benar → hitung `$ambiguous`, laporkan,
  jangan jadikan kegagalan.
- **Query verifier harus memuat kolom yang sama dengan jalur produksi.** Accessor yang
  butuh `category`/`model_type` menghasilkan nilai salah kalau `select()` tak memuatnya →
  "produk salah" padahal harness-nya cacat. Sebelum mengubah produk karena verifier merah,
  periksa dulu harness-nya (probe baris per baris, cetak nilai mentah + hasil turunan).
- Ekspektasi jangan aritmetika tetap ("harus = buang 2 segmen"); periksa **kaidahnya**
  (mis. "segmen pertama hasil tidak boleh sama dengan kandidat prefix mana pun").

## 4. Verifier UI (Playwright/Edge)

- Assertion DOM jangan bergantung teks insidental atau panjang teks; pakai hook stabil:
  `aria-label`, `data-*`, role/struktur tabel. Saat menambah UI baru, sekalian tambahkan
  hook `data-*` yang akan dipakai verifier.
- Klaim perilaku diuji lewat computed style (mis. `text-overflow: ellipsis` untuk klaim
  "satu baris"), bukan "teks panjang > N karakter" (jumlahnya berubah saat data berubah).
- Kalau assertion lama tiba-tiba gagal setelah UI pindah tempat (mis. chip jumlah item pindah
  ke dalam breadcrumb), **perbarui assertion-nya**, jangan pindahkan UI-nya kembali.

## 5. Serahkan konfirmasi visual pada user

Verifikasi otomatis tidak menggantikan pemeriksaan mata. Akhiri dengan: jalankan
`npm run build`, minta user `Ctrl+Shift+R`, dan sebutkan contoh konkret (nama mesin/folder)
untuk dicek. Kalau user menyebut satu kasus, buktikan kasus itu eksplisit di probe/laporan.
