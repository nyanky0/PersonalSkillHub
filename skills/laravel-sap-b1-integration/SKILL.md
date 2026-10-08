---
name: laravel-sap-b1-integration
description: Use when a Laravel app syncs SAP B1 via Service Layer.
---

# Laravel ↔ SAP B1 Service Layer (sisi aplikasi)

Untuk **membangun sisi aplikasinya**: tabel mirror, command sync, push master data + UDF, filter
display, dan verifikasi. Referensi API Service Layer-nya ada di skill `sap-b1-sl-api` (user-owned) —
skill ini soal cara memakainya dari Laravel tanpa jebakan.

## Aturan yang menentukan

- **Satu tabel mirror per objek SAP** yang dipakai UI, bukan memanggil Service Layer langsung dari
  halaman. Alasannya bukan sekadar cache: UI harus tetap jalan saat SAP mati, dan filter/pencarian
  lokal jauh lebih murah daripada request per keystroke.
- **UDF SAP jadi kolom biasa**, dan petanya disimpan SEKALI sebagai konstanta di model
  (`const CATALOG_UDF_MAP = ['U_SOL_PartNumber' => 'part_number', ...]`) supaya sync, `$select`, dan
  payload push memakai sumber pemetaan yang sama. Menulis daftar UDF di tiga tempat menjamin ketiganya
  lambat laun berbeda.
- **Kolom bendera hasil sync** (mis. `has_catalog_params`) untuk kriteria "lengkap atau tidak" yang
  dipakai UI. Hitung sekali saat sync — menghitung ulang di setiap query membuat filter lambat dan
  tersebar di banyak tempat.
- **Item yang sudah ada di SAP bukan kegagalan push.** Push item+UDF wajib menangani
  `400 already_exists` / kode `-10` / `-2035` dengan `PATCH` field UDF saja. Kalau dianggap gagal,
  sinkronisasi tidak akan pernah selesai untuk item yang sudah ada.
- **Endpoint UDO baru balas `Service Not Found` sampai Service Layer di-restart** — model objek
  dibangun saat service start dan login ulang tidak menolong. Verifikasi deploy lewat
  `/UserObjectsMD` dan `/UserTablesMD` (registry itu selalu bisa dibaca) sebelum menyalahkan kode.
  Fallback bacanya: `GET /SQLQueries('<QueryCode>')/List` dengan query tanpa placeholder form —
  tetapi **buktikan dulu fallback-nya benar-benar ada**: `GET /SQLQueries?$select=SqlCode,SqlName`
  yang kosong berarti query-nya memang belum terbuat di SAP, dan query Formatted Search yang memakai
  placeholder form (`$[$38.1]`) tidak bisa dijalankan headless. Jangan menyusun rencana di atas jalur
  yang belum diverifikasi. Jangan buru-buru menyimpulkan "deploy gagal".
- **Restart Service Layer itu tindakan milik user, bukan sesuatu yang bisa kamu lakukan sendiri.**
  Hentikan/restart service Windows butuh hak Administrator dan tidak ada jalur non-admin (di sesi
  non-admin `net stop` balas `System error 5`). Yang bisa kamu lakukan: minta izin, picu prompt UAC
  **dari sesi non-admin** dengan `Start-Process -Verb RunAs`, dan baca hasilnya dari file log karena
  proses elevated tidak mewarisi stdout. Perintah lengkapnya di `references/recipes.md` §8. Jangan
  pernah melaporkan "sudah di-restart" sebelum `$metadata` benar-benar memuat kode UDO-nya.
- **`success` ≠ ada isinya.** Sumber yang balas sukses dengan 0 baris berarti **tidak ada data**, bukan
  **tidak tersedia**. Rantai dual-path yang memakai `!empty($data)` sebagai syarat "sumber tersedia"
  akan melaporkan "UDO belum terekspos" padahal UDO-nya sudah jalan dan kebetulan masih kosong —
  gejalanya justru muncul tepat sesudah restart, saat tabelnya wajar kosong. Pisahkan status tersedianya
  sumber dari jumlah barisnya (mis. `[$rows, $source, $available]`), dan uji eksplisit jalur kosong itu:
  hasilnya harus "Synced 0 …", bukan error yang menyuruh restart lagi.
- **Filter display lewat scope model**, dan terapkan ke SEMUA query halaman (list, tree, opsi filter,
  statistik). Kalau hanya list yang difilter, angka statistik tidak akan cocok dengan yang terlihat.
- **Impor CSV: validasi header terhadap skema yang diharapkan, jangan fallback ke baris mentah.** Satu
  folder sumber bisa memuat lebih dari satu skema (file "manual book"/tree memakai
  `Item Title`+`Tree Path`+`Reference No`, file item-master memakai `Name`+`Classification`). Impor yang
  memetakan kolom per nama akan menyimpan **seluruh baris CSV** sebagai nilai begitu header yang dicari
  tidak ada — hasilnya kunci item sepanjang ratusan karakter yang baru ketahuan saat SAP menolaknya.
  Cocokkan header lebih dulu per skema, **lewati + laporkan** file yang tidak dikenali, dan **assert
  jumlah file/entitas yang terimpor sama dengan jumlah yang ditemukan**: penelusuran folder bersarang
  (`X/X/data/`) membuat sebagian besar file tidak pernah terlihat tanpa error apa pun.
- **Halaman katalog dengan data nyata tidak boleh mengirim pohon penuh ke Inertia.** Batasi prop tree ke
  2 level (root → anak langsung) + `children_count` per anak, dan sediakan baris lengkap lewat view
  ter-paginasi. Pohon penuh dari puluhan ribu baris menghasilkan payload belasan MB **dan** hidrasi
  Eloquent yang menembus `memory_limit` PHP (128 MB di mesin dev) — gejalanya halaman mati dengan
  “This page isn't working” tanpa error PHP yang terlihat di browser, sementara di log muncul
  `Allowed memory size ... exhausted` di `Illuminate/Cache/DatabaseStore.php` (tulis cache metadata).
  Angka sebelum/sesudah & cara mengukurnya: `references/recipes.md` §11.
- **Pohon navigasi katalog DITURUNKAN dari kolom part saat dibaca, bukan dari `parent_id`.** Group by
  kategori → merek → model → classification → komponen, lalu rangkai jadi trie di PHP. Satu hierarki yang
  tersimpan permanen hanya bisa menampilkan satu bentuk: begitu user minta setting “gabung merek+model”
  atau “pisahkan classification/komponen”, hierarki turunan cukup mengganti kunci `group by`-nya — tanpa
  migrasi, tanpa kolom baru, dan bisa dibangun ulang setelah impor ulang. `parent_id` tetap dipakai untuk
  alur push UDO, jangan dihapus. Sumbernya seluruh baris daun katalog, jadi ambil kolom agregatnya saja
  dan iterasi dengan `cursor()`.
- **Setiap node pohon membawa payload filter siap pakai (`node.filter`), dan klik memakai payload itu apa
  adanya.** Jangan menyusun ulang filter dari label yang tampil: label bisa berupa gabungan/kependekan
  yang berbeda dari nilai kolom. Filter node harus lewat **query string**, bukan state client — itulah
  yang membuat tiap node bisa diverifikasi (dan dibagikan) lewat satu URL.
- **Filter prefix (`LIKE`) untuk node hierarki wajib memakai string ASLI dari kolomnya, bukan hasil rakit
  ulang dari kolom lain.** Segmen path yang tersimpan (`Main Engine > Daihatsu - 8DCM-32eF > …`) sering
  berbeda dari gabungan `manufacturer` + `' '` + `model_type` (`DAIHATSU 8DCM-32eF`) — bedanya case dan
  pemisah — sehingga pola yang dirakit balik mengembalikan **0 baris** dan terlihat seperti fitur rusak.
  Escape `\`, `%`, `_` sebelum menempelkan `%` di ujung pola.
- **Node pohon di React dirender malas: anak hanya dibuat saat node di-expand.** Pohon katalog bisa
  ribuan node; komponen yang merender semua level sekaligus membuat halaman berat walaupun payload
  JSON-nya wajar. Ukur jumlah node + ukuran JSON untuk TIAP kombinasi setting (pisah/gabung) sebelum
  melaporkan selesai, dan simpan pohon versi **ringan** untuk prop SHARED sidebar — pohon penuh hanya di
  halaman katalognya.
- **Kalau folder sumber memuat `.xlsx`, baca xlsx-nya (PhpSpreadsheet) dengan daftar sumber dari SATU
  manifest; jangan scan CSV.** Satu folder mesin bisa memuat CSV skema-manual-book DAN xlsx item-master
  sekaligus, dan pemetaan per-nama kolom akan salah pada salah satunya. Cocokkan berkas lewat **nama
  dasarnya**, bukan path yang tertulis di manifest: kunci manifest sering memakai underscore sementara
  nama folder asli memakai spasi (`Akasakan_6UEC37LA` vs `Akasakan 6UEC37LA`) — bangun peta
  `basename() => path` dari hasil penelusuran sebelum menyatakan file tidak ada.
- **Kalau SEMUA halaman blank sekaligus, periksa prop SHARED di `HandleInertiaRequests` lebih dulu,
  baru controller halaman.** Prop shared dibangun di setiap request, jadi satu pohon tanpa batas di sana
  (mis. `'catalog_tree' => Cache::remember(...)` berisi root → komponen → part) mematikan seluruh
  aplikasi, bukan hanya halaman katalog — sementara memperbaiki controller halaman tidak mengubah apa pun
  dan menghabiskan satu putaran perbaikan. Batasi pohon shared ke 2 level + `children_count`, dan
  `select()` hanya kolom yang dipakai layout: sidebar cuma butuh id, parent_id, nama, dan field navigasi
  klik, sedangkan memilih seluruh kolom membuat nilainya berkali-kali lebih besar.
- **Semua query yang bisa menyentuh seluruh tabel katalog harus streaming** (`->orderBy('id')->cursor()`),
  termasuk endpoint daftar item untuk push dan loop push massal. Satu `->get()` atas ~18rb baris ≈ 80 MB.
  Untuk cek “ada isinya atau tidak” pada query berat, pakai `(clone $query)->exists()` lalu iterasi
  `cursor()` — jangan `->get()` dulu baru `isEmpty()`.
- **Panjang field SAP B1 itu batas keras, dan `ItemCode` yang paling sering terlewat.**
  `OITM.ItemCode` 50, `ItemName` 200, `FrgnName`/ForeignName 200, `OITB.ItmsGrpNam` 100, `Code` pada
  UDT MasterData ±20. Lewat dari itu SAP menolak dengan
  `-8112 ... Value too long in property 'ItemCode' of 'Item'` dan **seluruh** request item gagal — jadi
  potong di titik payload dibentuk, jangan berharap SAP memotong. `ItemName`/`ForeignName` biasanya sudah
  dipotong, `ItemCode` justru sering dikirim apa adanya. **Batasnya tidak ada di `$metadata`** (SAP tidak
  mengirim `MaxLength`); ambil dari referensi DB (`search_sap.py dbfields OITM`) — tabelnya di
  `references/recipes.md` §3.
- **Cache master data yang di-`remember` wajib punya SATU sumber kebenaran untuk key-nya.** Key
  ber-versi (`..._v2`, `..._v3`) di dua berkas berbeda gampang melenceng: kode membaca `..._v3`
  sementara sync `forget('..._v2')`, jadi UI tetap menyajikan data basi setelah sync — kelihatannya
  seperti sync gagal padahal berhasil. Simpan key sebagai konstanta/helper, atau `forget` semua versi
  sekaligus begitu bentuk datanya berubah.
- **Menambah atribut yang bisa dicari di picker master data itu TIGA perubahan, bukan satu:**
  (a) server melengkapi daftar item dengan atribut itu, (b) predikat filter di komponen picker
  menyertakannya, (c) form mengisi/menampilkannya saat item dipilih. Sangat mudah hanya mengerjakan
  (a) lalu menganggap fitur "pencarian"-nya selesai. Bentuk data daftar berubah ⇒ naikkan juga versi
  cache key-nya.
- **Jangan mengubah warna/brand tombol yang sudah ada.** Permintaan "tambah tombol" = section + tombol
  baru yang mengikuti gaya tombol push yang sudah ada, bukan restyle.
- **Sesudah menambah section/tombol di halaman push, jalankan pemeriksa impor komponen dulu baru
  `npm run build`** (`scripts/check-jsx-imports.py`, lihat bagian Perkakas). `vite build` TIDAK gagal saat
  ada komponen JSX yang dipakai tapi belum di-import — errornya muncul saat halaman dibuka sebagai
  `ReferenceError: <Nama> is not defined` dan halaman blank. Bangun sukses bukan bukti halaman jalan.
- **Push master data selalu 1-per-1** lewat `<fitur>-items-for-push` + `<fitur>-push-item` dengan
  progress bar. Satu request untuk semua item gampang timeout dan menyulitkan pelacakan per item.
- **Item group SAP itu datar dan satu level** (`OITB.ItmsGrpCod` = angka, nama maks 100), jadi bukan
  tempat menaruh hierarki katalog. Pembagian perannya: kategori fungsional (6–8 grup) di
  `ItemsGroupCode`, equipment/vessel di UDF yang sudah ada, hierarki penuh tetap di katalog aplikasi.
  Grup **harus sudah ada di SAP** sebelum bisa dipakai item, dan halaman Item Groups di aplikasi hanya
  **menarik** dari SAP — jangan menjanjikan tombol push grup tanpa membangunnya. Detail: §12 recipes.
- **Dua tombol push yang bersumber dari tabel katalog yang sama WAJIB memakai SATU helper pemilihan
  baris yang sama.** Kalau tombol “push katalog” mengirim level teratas sementara tombol “isi UDO”
  memilih level lain, UDO-nya merujuk kode item yang tidak pernah dibuat di SAP — dan karena field
  penghubungnya bertipe link ke OITM, SAP menolak/mengosongkannya. Uji: kedua endpoint harus melaporkan
  jumlah item yang sama.
- **Menulis ke UDO = header + collection anak dalam SATU payload**, dan field `Code` pada UDT
  `bott_MasterData` pendek (±20 karakter). Kalau kode item lebih panjang, potong lalu tambahkan suffix
  hash pendek supaya tetap unik — mengirim kode penuh dan berharap SAP memotongnya akan membuat dua item
  berprefiks sama bertabrakan. Resep lengkapnya di `references/recipes.md` §10.
- **Sesudah push UDO berhasil, tulis payload yang baru saja dikirim itu ke tabel mirror lokal**
  (header + anak), lalu `flush()` resolver dan `forget` cache daftar item. Tanpa itu data baru hanya
  terlihat setelah sync balik dari SAP — padahal kita yang baru mengirimnya, dan user akan menganggap
  push-nya gagal.
- **Baris sumber untuk header UDO = level terdalam yang masih punya anak** (“induk dari part”):
  `whereHas('children')` + `whereDoesntHave('children')`. Memakai level teratas membuat satu UDO
  menampung seluruh parts list equipment; memakai level daun membuat tiap UDO hanya berisi dirinya
  sendiri. Uji dengan fixture bertingkat dan assert level yang terpilih.
- **Seeder dokumen demo yang meniru hasil push** (dokumen + timeline approval) mengikuti skill
  `laravel-demo-seeders`: nomor dokumen lewat service penomoran aplikasi, idempotent lewat penanda baris.

## Cara kerja dengan user

- **Kerjakan sendiri langkah terminalnya** — impor, seeder, command artisan, sync, restart service.
  Sisakan hanya klik tombol di web untuk user. Kalau kamu menyodorkan urutan kerja, tandai eksplisit mana
  yang sudah kamu jalankan dan mana yang user tinggal klik; user sengaja menjalankan tombol push 1-per-1
  sendiri supaya bisa memeriksa tiap POST.
- Untuk uji sinkronisasi dokumen, verifikasi Hub API, profil/company SAP aktif, dan antrean staging sebelum menulis; cocokkan BP/item, warehouse, VAT, duplikasi, serta dampak jumlah/nilai sebelum memilih dokumen. Proses satu dokumen uji yang teridentifikasi, bukan bulk scheduler jika ada antrean lain. Proses berjalan, route Swagger, atau HTTP 200 tidak membuktikan transaksi diproses; baca kembali status staging dan DocEntry SAP.
- Untuk master data lewat Hub, inspeksi handler dan target konfigurasi sebelum POST: `isFallback=true` berarti fallback, bukan data SAP; `success=true` bukan bukti write bila handler hanya mengubah DB eksternal atau menelan exception. Terima integrasi hanya setelah Service Layer/DI API menulis dan exact key terbaca kembali. Untuk BP dengan numbering otomatis, verifikasi `CardCode` yang dibuat sama dengan kode sumber; jika ditolak atau berubah, berhenti dan minta pemetaan yang disepakati—jangan retry buta atau ubah dokumen antrean.
- Jangan proses antrean pending yang asal/tujuannya belum dipastikan: scheduler bulk dapat membuat dokumen SAP yang tidak dimaksud. Sebelum POST, cocokkan master BP/item, gudang, pajak, duplikasi, dan pemetaan fallback; ungkapkan efek samping dokumen/kuantitas sebelum memilih test case.
- Setelah staging POST, baca kembali status dengan WebTxNumber; respons sukses saja tidak membuktikan record tersimpan. Klaim end-to-end hanya setelah staging status dan dokumen SAP yang dibuat sama-sama diverifikasi.
- **Selalu perbarui `docs/development/AI_DEVELOPMENT_GUIDE.md` setiap ada perubahan pada proyek ini —
  user menganggapnya WAJIB, bukan opsional.** Setelah tiap fase (model data, importer, push, UI, skema
  field), tambahkan bab baru atau perbarui bab yang terdampak, dan sebutkan perubahan itu di laporan.
  Jangan menunggu diminta; panduan itu adalah kontrak yang user pakai untuk meng-audit pekerjaanmu.

## Perkakas

- `scripts/check-jsx-imports.py` — daftar komponen JSX yang dipakai tapi belum di-import di sebuah berkas
  `.jsx`. Jalankan atas `resources/js` sebelum build setiap kali menyentuh halaman React.

## Verifikasi sebelum melaporkan

- **Buktikan kegagalan test itu pre-existing**, jangan mengklaim "sepertinya bukan dari perubahan saya".
  Jalankan file test yang sama pada commit SEBELUM perubahan, bandingkan angkanya, baru laporkan.
- Jalankan `php -d memory_limit=-1 vendor/bin/phpunit` langsung (bukan `artisan test`) supaya limit
  memori benar-benar berlaku ke runner; `artisan test` men-spawn subprocess dengan limit berbeda.
- Isolasi OOM/crash dengan loop per file test — lebih cepat menunjuk biang kerok daripada menerka dari
  output runner yang penuh.
- **Jangan mengklaim halaman sudah sehat hanya dari skrip CLI.** Skrip bootstrap yang memanggil method
  controller **tidak menjalankan middleware**, jadi prop shared dan `session()` tidak ikut dihitung dan
  halaman bisa dilaporkan `200` sementara browser user tetap blank — persis di situ satu putaran
  perbaikan terbuang. Bukti yang sah untuk halaman = request HTTP sungguhan dengan sesi login (curl:
  ambil CSRF dari `GET /login`, `POST /login`, lalu `GET` setiap halaman dan cek status + ukuran +
  ketiadaan penanda error). Resepnya di `references/recipes.md` §11c.
- **Verifikasi hierarki lewat URL filter, bukan dengan mata di UI.** Uji turun per level: jumlah baris
  tiap level harus ≤ level di atasnya, dan `count` yang dilaporkan tiap node harus cocok dengan jumlah
  baris hasil filter URL-nya. Halaman `200` tidak membuktikan hierarkinya benar. Kalau verifikasi hanya
  bisa sampai tingkat data (props Inertia + HTTP) karena alat peramban belum siap di mesin ini, **sebutkan
  tingkat buktinya di laporan** — jangan menyiratkan sudah dilihat di UI.

Resep kode lengkap (sync, UDO header+anak, push UDF, batas panjang field SAP, gambar dari folder luar
proyek, scope filter, impor CSV multi-skema, impor xlsx + skema ItemCode, payload Inertia & memori
termasuk prop shared dan verifikasi HTTP bersesi, item group): `references/recipes.md`.

Pohon navigasi katalog (hierarki turunan, bentuk node + `node.filter`, filter `LIKE` dari string asli,
setting gabung/pisah, ukuran payload, loop verifikasi lewat URL filter, jebakan mutu kolom sumber):
`references/catalog-browse-tree.md`.

Katalog sparepart juga punya app offline terpisah (Spare Parts Browser HTML) yang **bukan** bagian app
Laravel ini — cara menyalakan, memverifikasi assetnya, dan jebakan mutu datanya ada di skill
`run-local-web-app`.
