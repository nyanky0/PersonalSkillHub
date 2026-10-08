# Push master data katalog ke SAP B1: item group → item master

Urutan, bentuk payload, dan klasifikasi balasan yang sudah terbukti untuk push massal dari tabel
katalog lokal ke `OITB` + `OITM`. Dipakai bersama tombol push 1-per-1 di halaman konfigurasi SAP.

## 1. Urutan wajib

1. **Push Item Group dulu** — `ItemsGroupCode` di payload item harus menunjuk grup yang sudah ada
   di SAP; item yang menunjuk grup tak dikenal ditolak.
2. **Baru item master, DI PECAH PER MEREK** — bukan sekali borongan. Tiap batch bisa diperiksa dan
   diulang sendiri, dan kegagalan satu merek tidak menahan merek lain.
3. Yang dikirim ke OITM **hanya baris daun katalog** (part). Baris equipment/komponen di atasnya cuma
   simpul navigasi tanpa nomor part.

Uji idempotensi dengan menjalankan tiap push DUA KALI: run kedua harus `0 dibuat`, bukan `0 gagal`.

## 2. Item group: key Service Layer-nya `Number`, bukan `Code`

```php
$payload = ['Number' => 1001, 'GroupName' => mb_substr('Assembly', 0, 100)];
$this->sap->request('POST', 'ItemGroups', $payload);
```

- `'Code' => …` ditolak `Property 'Code' of 'ItemGroups' is invalid` — field itu tidak ada di entitas
  ini. Buktikan nama field dari `GET /ItemGroups` (yang muncul: `Number`, `ItmsGrpNam`); jangan
  menyimpulkan dari pola umum, karena `OITM` memakai `ItemCode` sedangkan `OITB` memakai `Number`.
- `PATCH /ItemGroups(<nomor>)` balas `-2028 (no matching records)` **walau grupnya jelas ada** —
  endpoint detailnya tidak resolve lewat URL kunci. Pola aman: `POST` → kalau balasan duplikat,
  `PATCH`; kalau PATCH balas `-2028`, perlakukan sebagai **sudah ada**, bukan `failed` — `POST`
  duplikat sudah membuktikan grupnya ada.
- Kode grup: pakai zona angka di atas grup bawaan demo (100–102), mis. `1001+`, ditentukan dari urutan
  **abjad** kolom dasarnya (mis. `type`) supaya stabil antar-run.

## 3. Item master: `ItemCode` dari kolom hasil generate, bukan nomor part

```php
$payload = [
    'ItemCode'    => mb_substr((string) $item->item_code, 0, 50),   // {MFG}-{MODEL}-{SEQ}
    'ItemName'    => mb_substr((string) $item->part_name, 0, 200),
    'ForeignName' => mb_substr((string) ($item->eng_name ?: "{$item->manufacturer} {$item->model_type}"), 0, 200),
    'InventoryUOM' => $uom, 'SalesUnit' => $uom, 'PurchaseUnit' => $uom,
    'ItemType'      => 'itItems',
    'ItemsGroupCode'=> $item->item_group_code,
    // + UDF katalog, masing-masing dipotong sesuai panjang field SAP-nya
];
$payload = array_filter($payload, static fn ($v) => $v !== null && $v !== '');
```

- Mengisi `ItemCode` dengan nomor part adalah penyebab `-8112 Value too long in property 'ItemCode'`
  pada data nyata: nomor part sumber bisa ratusan karakter. Generate `{MFG}-{MODEL}-{SEQ}` dengan
  counter urut per `MFG|MODEL` (mis. `AKA-7UEC37LA-000001`) dan jaga hasilnya tetap ≤ 50 karakter.
- Nomor part aslinya satu-ke-banyak dan terus diperbarui → simpan sebagai **daftar di UDO detail**
  (lihat §10 di `references/recipes.md`), bukan sebagai UDF OITM. Dengan begitu perubahan part number
  tidak menyentuh master item sama sekali.

## 4. Klasifikasi balasan error: token utuh, bukan substring

```php
protected function isDuplicateItemError(string $err): bool
{
    if ($err === '') { return false; }
    if (stripos($err, 'already exists') !== false) { return true; }
    if (str_contains($err, '-2035')) { return true; }
    // HANYA -10. str_contains($err, '-10') juga cocok dengan -1000
    // ("Property 'X' of 'Items' is invalid") -> tiap gagal dilaporkan "sudah ada".
    return preg_match('/"code"\s*:\s*"-10"/', $err) === 1;
}
```

- Balasan duplikat → `PATCH /Items('<kode>')` berisi **hanya** field UDF, status `updated`.
- **Kalau PATCH-nya sendiri gagal, statusnya `failed` — bukan `exists`.** Melaporkan `exists` untuk
  payload yang ditolak SAP menyembunyikan penyebab sebenarnya; akibatnya push massal "sukses semua"
  padahal tidak satu pun field UDF terkirim.
- Penyebab paling sering kegagalan yang tersembunyi itu: **UDF-nya belum ada di SAP.** UDF baru dibuat
  lewat `.cs` setup yang harus dijalankan user di sisi SAP — selama itu belum jalan, push item memang
  gagal dengan `Property 'U_SOL_…' of 'Items' is invalid`, dan itu benar, bukan bug. Sampaikan urutan
  ini ke user secara eksplisit: run `.cs` dulu → baru push.

## 5. Log Excel per push

Satu `.xlsx` per push di `storage/app/push-logs/`, nama menyertakan cakupan + timestamp
(`item-master-<merek>-<Ymd-His>.xlsx`) supaya riwayat batch bisa dibandingkan tanpa saling menimpa.

```
No | Item Code | Part No | Part Name | Item Group | Status | Pesan | Waktu | Body/Detail
```

- **Body JSON mentah ditulis di SATU cell** (wrap text), bukan dipecah per kolom — user membacanya
  sebagai tabel, dan payload panjang tetap terbaca utuh.
- Baris ringkasan ditulis di atas tabel: total, dibuat, diperbarui, sudah ada, gagal, mode online/offline.
- `Status` ∈ `created` / `updated` / `exists` / `failed`; `Pesan` = pesan SAP apa adanya, supaya user
  tidak perlu membuka log aplikasi untuk tahu penyebabnya.
- Direktori log lewat config, supaya `php artisan test` tidak menumpuk file "Mode: Offline" di folder
  log produksi.
- Bungkus penulisannya dengan `try/catch` + `Log::warning`: **gagal menulis log tidak boleh menggagalkan
  push**, karena log itu konsumsi manusia, bukan bagian transaksi.
