# Resep: Laravel ↔ SAP B1 Service Layer

Diasumsikan ada satu service class (`SapServiceLayerManager`) yang membungkus HTTP client
(`SapB1Service::request($method, $endpoint, $payload)` → `['success','status','data','error']`).

## 1. Bentuk method sync

```php
try {
    $result = $this->fetchAllFromSap('<Entity>?$select=...');   // sudah menangani paging + nextLink
    if (! $result['success']) {
        return $this->buildSyncResult(false, 'Failed to sync <Module>: ' . $result['message'], '<Module>');
    }

    $count = 0;
    DB::transaction(function () use ($result, &$count) {
        foreach ($result['data'] as $row) {
            Model::updateOrCreate(['<key>' => $row['<KeyField>']], [...]);
            $count++;
        }
    });

    Cache::forget('<cache-key-yang-terdampak>');
    return $this->buildSyncResult(true, "Synced {$count} <Module> dari SAP.", '<Module>', '<Service>');
} catch (\Throwable $e) {
    return $this->buildSyncResult(false, '<Module> sync error: ' . $e->getMessage(), '<Module>');
}
```

- **Selalu invalidate cache entitas terkait** setelah sync — UI-nya hampir pasti di-cache.
- Untuk tabel anak UDO yang isinya terus berubah: hapus lalu insert ulang baris anak per header
  (`where(<parent>)->delete()` baru `create()`). Jangan mencoba diff.
- Kirim `$select` eksplisit termasuk SEMUA UDF yang dipakai; jangan `$select` kosong lalu berharap
  UDF ikut terambil.
- Ekspos sebagai command artisan (`sap:sync-...`) **dan** seeder bila datanya dipakai membangun master
  data lokal. Command yang dipanggil tanpa data harus balas pesan actionable
  ("jalankan dulu `php artisan ...`"), bukan sukses palsu.

## 2. Mengumpulkan anak dari header UDO

Endpoint UDO mengembalikan anak di properti `<ChildTable>Collection` (mis. `SOL_PNUM_DCollection`),
**tapi jangan asumsikan namanya**. Cek beberapa varian (`<ChildTable>Collection`,
`<ObjectCode>Collection`, `Lines`), normalisasi header+anak ke bentuk **flat** dulu, baru kelompokkan
per `Code` di PHP. Dengan begitu satu method melayani endpoint UDO maupun fallback
`SQLQueries(...)/List` (yang hasilnya sudah flat) — tidak perlu dua jalur kode.

## 3. Push item + UDF

```php
$payload = [
    'ItemCode' => $item->part_no,
    'ItemName' => mb_substr((string) $item->part_name, 0, 100),
    'InventoryUOM' => $uom, 'SalesUnit' => $uom, 'PurchaseUnit' => $uom,
    'ItemType' => 'itItems',
    'U_SOL_PartNumber' => $this->truncateUdfValue($item->main_part_no ?: $item->part_no, 50),
    // ... UDF lain, masing-masing dipotong sesuai panjang field di SAP
];
$payload = array_filter($payload, static fn ($v) => $v !== null && $v !== '');
```

Saat `POST /Items` balas `400` dengan `already exists` / `-10` / `-2035`, kirim
`PATCH /Items('<kode>')` berisi **hanya** field UDF, lalu tandai status `updated` (bukan `failed`).
Selalu mirror hasilnya ke tabel item lokal supaya UI langsung konsisten.

### Batas panjang field (referensi DB SAP B1)

| Objek.field | Kolom | Maks |
|---|---|---|
| `OITM.ItemCode` | `ItemCode` | **50** |
| `OITM.ItemName` | `ItemName` | **200** |
| `OITM.ForeignName` | `FrgnName` | **200** |
| `OITB.ItmsGrpNam` | Group Name | 100 |
| UDT MasterData | `Code` | ±20 |

`$metadata` **tidak** memuat `MaxLength` — jangan mengandalkannya untuk mencari batas ini:

```bash
python C:/Users/yudah/.sap-b1-skills/search_sap.py dbfields OITM | grep -i "ItemCode\|ItemName\|FrgnName"
```

Yang paling sering lolos pemeriksaan adalah `ItemCode`; balasannya:
`-8112 CServiceData::SetPropertyValueString failed; Value too long in property 'ItemCode' of 'Item'`.
Audit panjang di sisi lokal SEBELUM push massal — kunci yang ratusan karakter berarti datanya rusak
(lihat §9), bukan sekadar perlu dipotong:

```php
foreach (['part_no', 'part_name'] as $c) {
    printf("%s: max %d | >50 %d\n", $c,
        DB::table('t')->max(DB::raw("length($c)")),
        DB::table('t')->whereRaw("length($c) > 50")->count());
}
```

## 4. Gambar/lampiran dari satu folder di luar proyek

Bila semua instance harus membaca folder yang sama (mis. drive `C:`), **jangan** salin ke `public/`
dan jangan bikin symlink. Config + route penyaji:

```php
// config/<nama>.php
return [
    'path'       => env('IBT_ITEM_IMAGE_PATH', 'C:/IBT_ItemImages'),
    'extensions' => ['jpg', 'jpeg', 'png', 'webp', 'gif', 'bmp'],
];
```

```php
public function itemImage(Request $request, string $code)
{
    $safe = preg_replace('/[^A-Za-z0-9._ -]/', '', $code);   // cegah path traversal
    if (empty($safe)) {
        abort(404);
    }

    foreach (config('<nama>.extensions') as $ext) {
        $file = rtrim((string) config('<nama>.path'), '/\\') . DIRECTORY_SEPARATOR . $safe . ".{$ext}";
        if (is_file($file)) {
            return response()->file($file, ['Cache-Control' => 'public, max-age=86400']);
        }
    }

    abort(404);
}
```

- Nama file = kode item. Seeder/command mencocokkan nama file (tanpa ekstensi, uppercase) ke kolom
  kode, lalu mengisi kolom URL dengan `route('...', ['code' => $kode], false)` (URL relatif).
- Taruh route di dalam grup auth, dan tulis `README.txt` di foldernya berisi aturan penamaan — folder
  itu diisi manual oleh user.
- Uji: gambar ada → 200; kode tanpa gambar → 404; kode berisi `../` → 404.

## 5. Scope filter display

```php
public function scopeCatalogReady($query)
{
    return $query->whereNotNull('part_no')->where('part_no', '!=', '')
        ->where(function ($q) { /* minimal satu atribut teknis terisi */ });
}
```

Terapkan ke query list, tree, opsi filter, DAN statistik. Uji dengan fixture yang sengaja TIDAK
lengkap dan assert item itu benar-benar tidak muncul di halaman.

## 6. Perintah verifikasi

```bash
# buktikan kegagalan test pre-existing
HEAD=$(git rev-parse HEAD)
git checkout <commit-sebelum-perubahan> -- app/ config/ routes/ tests/
php -d memory_limit=-1 vendor/bin/phpunit tests/Feature/<File>.php
git checkout "$HEAD" -- app/ config/ routes/ tests/
git status --short          # pastikan bersih setelah restore

# isolasi OOM/crash: loop per file
for f in tests/Feature/*.php; do php -d memory_limit=512M vendor/bin/phpunit "$f"; done
```

Kalau hasilnya identik dengan sebelum perubahan, laporkan sebagai pre-existing **dengan angkanya**
(jumlah test/assertion/failure), bukan sebagai dugaan.

- Kalau `php artisan tinker --execute="..."` (atau command artisan lain) balas `stdin is not a tty`,
  jalankan command yang sama dengan `< /dev/null` dan secara **sinkron** (foreground): artisan yang
  dijalankan sebagai proses background di host ini gagal dengan pesan yang sama. Output-nya pendek, jadi
  tidak perlu background.

## 7. Atribut anak UDO dipakai untuk display + pencarian item

Pola: satu resolver yang mengumpulkan SEMUA nilai anak per item, dipakai bersama oleh dokumen dan picker.

```php
class ItemPartNumberResolver
{
    protected static ?array $map = null;

    public static function flush(): void { static::$map = null; }

    /** item_code (UPPERCASE) => ['main' => ?string, 'all' => string[]] */
    public static function map(): array { /* header UDO + details, lalu fallback UDF OITM */ }

    public static function forItem(?string $itemCode): array { /* map()[key] ?? kosong */ }

    /** Tambahkan part_number + part_numbers ke tiap item (Collection model ATAU array of array) */
    public static function decorate($items) { /* model -> setAttribute(); array -> array_merge */ }
}
```

- Panggil `decorate()` **setelah** `Cache::remember(...)`, bukan di dalam closure-nya: cache tetap
  ringan dan atribut baru selalu ikut walau cache-nya lama.
- Panggil `flush()` di setiap jalur sync/push, berdampingan dengan `Cache::forget` daftar item.
- `decorate()` harus menerima dua bentuk (model Collection dan array) — daftar item sering dibangun ulang
  sebagai array di jalur lain (template, export), dan versi model-only akan meledak di sana.
- Sisi UI: tambahkan atribut ke predikat filter picker (nilai utama **dan** tiap elemen array-nya),
tampilkan badge-nya di baris, dan isi field baris dokumen saat item dipilih. Field baris dokumen biasanya
sudah ada di payload JSON dokumen, jadi tidak perlu migrasi.
- Uji resolver tanpa menyentuh SAP: buat header+detail UDO di DB test lalu assert `main`/`all`, plus satu
  kasus item tanpa atribut sama sekali (harus balas kosong, bukan error).

## 8. Restart Service Layer setelah membuat/mengubah UDO

Wajib tiap kali UDO/UDT/UDF baru dibuat — kalau tidak, endpoint UDO-nya balas `400 Service Not Found`.

Buktikan dulu bahwa restart memang yang dibutuhkan (jangan menebak):

```bash
COOKIE=$(mktemp)
curl -s -c "$COOKIE" -X POST "http://localhost:50001/b1s/v2/Login" \
  -H 'Content-Type: application/json' \
  -d '{"CompanyDB":"<db>","UserName":"<user>","Password":"<pass>"}' > /dev/null
curl -s -b "$COOKIE" "http://localhost:50001/b1s/v2/\$metadata" | grep -c '<KodeUDO>'
# 0  -> Service Layer belum memuatnya, restart memang perlu
# >0 -> sudah ada, cari sebab lain
```

Restart butuh Administrator. Pola yang bekerja dari sesi non-admin: skrip yang menulis hasilnya ke file,
lalu dipicu lewat UAC (proses elevated tidak mewarisi stdout, jadi log file itu satu-satunya umpan balik).

```powershell
# restart_sl.ps1
$log = Join-Path $PSScriptRoot 'restart_sl.log'
"=== START $(Get-Date -Format o) ===" | Out-File $log -Encoding utf8
Restart-Service -Name 'B1ServerTools64ServiceLayerController' -Force -ErrorAction SilentlyContinue
Start-Sleep 8
foreach ($n in @(Get-Service -Name 'b1s*' | Select-Object -ExpandProperty Name)) {
    try   { Restart-Service -Name $n -Force -ErrorAction Stop; "OK   $n" | Out-File $log -Append }
    catch { "FAIL $n :: $($_.Exception.Message)" | Out-File $log -Append }
}
"=== DONE $(Get-Date -Format o) ===" | Out-File $log -Append
```

```bash
# 1) picu UAC — user meng-ACC prompt-nya, proses jalan terpisah
powershell -NoProfile -Command "Start-Process -FilePath 'powershell' -Verb RunAs -ArgumentList @('-NoProfile','-ExecutionPolicy','Bypass','-File','<path>/restart_sl.ps1')"

# 2) tunggu selesai lalu baca log (jangan asumsikan langsung beres)
for i in $(seq 1 60); do grep -q DONE <path>/restart_sl.log 2>/dev/null && break; sleep 5; done
cat <path>/restart_sl.log
```

Node `b1s*` bisa belasan; restart penuh butuh beberapa menit. Sesudah itu verifikasi ulang `$metadata`
(>0) **dan** endpoint UDO-nya (`200`, `count=0` tetap sah sebagai bukti endpoint hidup).

## 9. Impor master katalog dari CSV ke tabel self-referential 3 level

Kasus: satu CSV per equipment berisi baris part yang harus dirantai jadi `Equipment > Component > Part`.

- Bentuk tree dengan `parent_id` + `hierarchy_level` + `hierarchy_path`, dan **idempotency key =
  (natural key, parent_id)**: `updateOrCreate(['part_no' => $x, 'parent_id' => $parentId], [...])`.
  Nomor part yang sama di komponen berbeda tetap jadi baris terpisah. Duplikat dalam parent yang sama
  akan tergabung — itu dedupe yang diinginkan, tapi **hitung dan laporkan selisih barisnya** supaya tidak
  terlihat seperti data hilang.
- **Nama entitas root (L1) harus diambil dari sumber yang TETAP (nama folder), bukan dari kolom hierarki
  per baris.** Menugaskan ulang variabel nama equipment di dalam loop baris dari kolom hierarki membuat
  root “melayang” mengikuti baris terakhir: hasilnya 80 root dari 12 folder, bukan 12. Baris per-baris
  hanya mengisi level anak (segmen terakhir kolomnya); root tetap dari konteks yang tidak berubah.
- Cache tree di halaman katalog dibangun dari SELURUH tabel. Impor puluhan ribu baris membuat render
  tree berat — sediakan `--equipment=` dan `--limit=`, impor bertahap, dan `Cache::forget` metadata
  katalog untuk SEMUA branch (bukan hanya `ALL`) di akhir. Batas 2 level + `cursor()`-nya di §11.
- **Counter yang dilaporkan harus menghitung ENTITAS, bukan iterasi loop.** Menambah counter di dalam
  loop baris melaporkan "1311 equipment" untuk satu folder. Naikkan sekali per folder/entitas.
- `fgetcsv` menyisakan BOM (`\x{FEFF}`) di kolom pertama header — bersihkan sebelum memetakan kolom,
  kalau tidak nama kolom pertama tidak akan pernah cocok.
- **Satu folder sumber bisa berisi LEBIH DARI SATU skema CSV.** File tree/manual book memakai
  `Reference No` + `Item Title` + `Tree Path` + `Maker`/`Model`; file item-master memakai `Item No.` +
  `Name` + `Classification` + `Reference No`. Jangan memetakan kolom per nama begitu saja: begitu header
  yang dicari tidak ada, fallback-nya menyimpan **baris CSV utuh** sebagai nilai kolom kunci. Kenali skema
  dari himpunan headernya, pilih pemetaan yang cocok, dan **lewati + laporkan** file yang tidak dikenali —
  lebih baik satu equipment belum masuk daripada ribuan baris kunci palsu.
- **Deteksi salah-parse lewat sebaran panjang, bukan lewat mata.** `max(length(part_no))` yang mencapai
  ratusan karakter (normalnya belasan) sudah cukup untuk menunjuk file yang bermasalah. Jalankan audit ini
  langsung sesudah impor, sebelum push apa pun ke SAP.
- **Telusuri CSV secara rekursif dan bandingkan jumlah yang ditemukan dengan yang benar-benar terimpor.**
  Folder bersarang (`Equipment/Equipment/data/`) membuat penelusuran satu level hanya menemukan sebagian:
  laporan "12 equipment" padahal ada 22 CSV berarti 10 equipment tidak pernah masuk tanpa satu pun error.
  Assert `jumlah terimpor == jumlah ditemukan` dan tampilkan daftar yang belum masuk.
- Ganti key natural (nomor part) dengan fallback slug nama saat kolomnya kosong, agar baris tanpa nomor
  tetap punya identitas stabil dan re-run tetap idempotent.
- Impor lewat command artisan (opsi `--path/--equipment/--limit/--fresh`) + seeder tipis yang memanggil
  command itu, supaya bisa dijalankan bertahap tanpa memuat semuanya.
- Untuk gambar per baris yang berupa scan halaman (banyak baris berbagi satu file), tambahkan route
  kedua yang melayani `<root>/<equipment>/images/<file>` dan isi URL-nya dengan `route(..., false)`.
  Jangan menyalin ribuan scan ke folder gambar item.

## 10. Menulis UDO (header + anak) dari data lokal

Satu record UDO = header + collection anak, dikirim dalam satu payload:

```php
$payload = [
    'Code'             => $this->makeUdoCode((string) $item->part_no),   // UDT MasterData: <= 20 char
    'Name'             => mb_substr((string) $item->part_name, 0, 100),
    'U_SOL_ItemCode'   => mb_substr((string) $item->part_no, 0, 50),
    'U_SOL_ItemName'   => mb_substr((string) $item->part_name, 0, 200),
    'U_SOL_MainPartNo' => $this->truncateUdfValue($item->main_part_no ?: $item->part_no, 50),
    '<ChildTable>Collection' => $lines,   // mis. SOL_PNUM_DCollection
];
$payload = array_filter($payload, static fn ($v) => $v !== null && $v !== '');
```

```php
/** Kode UDO unik tapi tetap muat batas panjang field Code. */
protected function makeUdoCode(string $value): string
{
    $clean = strtoupper(preg_replace('/[^A-Za-z0-9]/', '', $value) ?? '');
    if ($clean === '')        { $clean = 'PN' . strtoupper(substr(md5($value), 0, 6)); }
    if (strlen($clean) <= 20) { return $clean; }
    return substr($clean, 0, 14) . '-' . strtoupper(substr(md5($value), 0, 5));
}
```

- Perlakuan sama seperti item: balasan `400 already exists` / `-10` / `-2035` →
  `PATCH /<ObjectCode>('<Code>')` dengan payload yang sama, tandai `updated` (bukan `failed`).
- **Sesudah push (sukses maupun mode offline), cerminkan payload itu ke tabel mirror lokal**: hapus
  anak lama per header lalu insert ulang, dan taruh baris header-nya. Baru setelah itu `flush()` resolver
  + `forget` cache daftar item. Ini yang membuat fitur “isi part number” langsung terpakai tanpa
  menunggu sync balik dari SAP.
- Header dipilih dari baris yang punya anak, sementara anaknya tidak punya anak lagi
  (`whereHas('children')` + `whereDoesntHave('children')`), supaya daftar anaknya benar-benar berupa
  daftar part number milik item itu.
- Setiap baris anak dipotong sesuai panjang field SAP-nya masing-masing (`mb_substr` per UDF), karena
  deskripsi/ref manual jauh lebih panjang dari field di UDT.

## 11. Payload Inertia & memori: batasi pohon, streaming sisanya

Realita yang muncul begitu katalog diisi data nyata (12 equipment / ~640 komponen / ~18.800 baris,
`memory_limit` 128 MB): halaman katalog mati dengan “This page isn't working”, dan log menunjukkan
`Allowed memory size ... exhausted` di `Illuminate/Cache/DatabaseStore` — bukan di view, karena yang
meledak adalah hidrasi model + tulis cache metadata.

Aturannya:

| Jangan | Pakai |
|---|---|
| Prop tree berisi root → komponen → part | 2 level + `children_count`, part lewat view ter-paginasi |
| `Model::where(...)->get()` untuk seluruh tabel | `->orderBy('id')->cursor()` lalu susun array sendiri |
| `$q->get()->isEmpty()` pada query berat | `(clone $q)->exists()` lalu `foreach ($q->cursor() ...)` |

```php
// tree: root + anak langsung + jumlah cucu, tanpa memuat cucunya
$tree = EquipmentCatalog::whereNull('parent_id')->where('is_active', true)->catalogReady()
    ->withCount(['children as children_count' => fn ($q) => $q->where('is_active', true)->catalogReady()])
    ->with(['children' => function ($q) {
        $q->where('is_active', true)->catalogReady()
          ->withCount(['children as children_count' => fn ($sq) => $sq->where('is_active', true)->catalogReady()]);
    }])
    ->orderBy('manufacturer')->orderBy('part_no')->get();
```

- Node tanpa `children` yang dimuat tapi `children_count > 0` cukup ditandai badge di sisi React —
  jangan diam-diam kehilangan informasinya.
- Sisi UI harus tetap benar untuk node tanpa cucu (`hasChildren = node.children?.length > 0`), termasuk
  tidak menampilkan panah expand.

**Ukur dulu, jangan menebak.** Skrip scratch yang membuktikan angka sebelum/sesudah (jalankan dengan
limit aslinya, bukan `-1`):

```php
<?php
// scratch/verify_page.php — ukur halaman Inertia apa adanya, termasuk payload yang benar-benar dikirim
require __DIR__ . '/../vendor/autoload.php';
$app = require_once __DIR__ . '/../bootstrap/app.php';
$app->make(Illuminate\Contracts\Console\Kernel::class)->bootstrap();

echo 'memory_limit : ' . ini_get('memory_limit') . "\n";

$user = App\Models\User::find(1);
auth()->login($user);
$request = Illuminate\Http\Request::create('/catalog', 'GET');
$request->setUserResolver(fn () => $user);
Illuminate\Support\Facades\Cache::forget('equipment_catalog_meta_ALL');   // paksa dibangun ulang

$t0 = microtime(true);
$resp = app(App\Http\Controllers\CatalogController::class)->index($request);
$html = $resp->toResponse($request)->getContent();   // DI SINI payload Inertia dirender

preg_match('/data-page="([^"]*)"/', $html, $m);
$page = json_decode(html_entity_decode($m[1] ?? '', ENT_QUOTES), true);

printf("waktu %.0f ms | payload %.2f MB | items %d\n",
    (microtime(true) - $t0) * 1000, strlen($m[1] ?? '') / 1048576,
    count($page['props']['items']['data'] ?? []));
printf("PEAK %.1f MB\n", memory_get_peak_usage(true) / 1048576);
```

- **Render respons-nya (`toResponse()` + baca atribut `data-page`)**; kalau hanya memanggil method
  controller-nya, payload dan memorinya belum benar-benar dihitung dan OOM-nya tidak akan terlihat.
- Ukur juga endpoint push-nya terpisah (`getItemsForPush()`), karena ia bisa lolos sendiri sementara
  halaman utamanya sudah sehat.
- Hasil nyata sesudah perbaikan: index 328 ms · payload 0,45 MB · peak 20 MB (semula OOM);
  `getItemsForPush` peak 44 MB (semula 102 MB); tree 644 node / 0,42 MB (semula 14.071 node / 9,72 MB).

### 11b. Kalau yang meledak prop SHARED (semua halaman blank)

Gejala pembeda: **setiap** halaman mati, bukan hanya halaman katalog — termasuk `/`, `/settings/*`,
`/templates`. Penyebabnya prop di `HandleInertiaRequests::share()` yang dibangun di setiap request:

```php
'auth' => [
    'catalog_tree' => fn () => Cache::remember("global_catalog_tree_{$branch}", 300, fn () =>
        Model::whereNull('parent_id')->with(['children' => fn ($q) => $q->with(['children' => ...])])->get()
    ),   // <- pohon 3 level tanpa batas; nilainya ~25 MB untuk ~18rb baris
],
```

Perbaikannya sama seperti prop halaman: 2 level + `children_count`, plus `select()` hanya kolom yang
benar-benar dipakai layout. Sesudah diperbaiki: 652 node · 1,20 MB · 28 ms · peak 8 MB. Ubah juga key
cache-nya ke versi baru supaya nilai lama yang besar tidak terbaca lagi, dan `cache:clear` sekali.

**Urutan diagnosis saat banyak halaman blank sekaligus:** prop shared di `HandleInertiaRequests` dulu →
controller halaman → query. Memperbaiki controller halaman lebih dulu memakan satu putaran penuh tanpa
mengubah apa pun, karena prop shared tetap membangun pohon penuh pada request berikutnya.

### 11c. Verifikasi halaman lewat HTTP bersesi (bukan skrip CLI)

Skrip bootstrap yang memanggil method controller **tidak menjalankan middleware**, jadi prop shared dan
`session()` tidak ikut dihitung — halaman bisa dilaporkan sehat sementara browser user tetap blank.
Bukti yang sah = request HTTP sungguhan:

```bash
CJ="$LOCALAPPDATA/Temp/cj.txt"; rm -f "$CJ"
TOKEN=$(curl -s -c "$CJ" http://localhost:8112/login | grep -o 'csrf-token" content="[^"]*"' | head -1 | sed 's/.*content="//;s/"//')
curl -s -b "$CJ" -c "$CJ" -X POST http://localhost:8112/login \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  --data-urlencode "_token=$TOKEN" --data-urlencode "email=<user>" --data-urlencode "password=<pass>"

for r in / /catalog /settings/sap /approval/inbox; do
  printf '%-20s ' "$r"
  curl -s -b "$CJ" "http://localhost:8112$r" -o pg.html -w "HTTP %{http_code} %{size_download}B %{time_total}s"
  grep -q "Allowed memory" pg.html && printf ' | OOM'
  grep -qo "Whoops\|Fatal error" pg.html && printf ' | ERROR'
  echo
done
```

- Props yang benar-benar dikirim bisa dibaca dari respons: atribut `data-page="..."` berisi JSON dengan
  `component`, `props`, dan ukuran pohonnya — cetak `count(props.treeRoots)`, `props.items.data`, dst.
- Kredensial user demo project ini ada di seeder (`Hash::make('password')`), jadi login otomatis bisa.

## 12. Item group (OITB) dari katalog

Fakta yang menentukan desainnya:

| Yang dicek | Hasil |
|---|---|
| Tabel | `OITB`, `ItmsGrpCod` = **Int** (angka), `ItmsGrpNam` maks 100 |
| Struktur | **datar, satu level** — tidak bisa menampung hierarki katalog |
| Penugasan | `ItemsGroupCode` di payload item; grup **harus sudah ada di SAP** lebih dulu |
| Halaman Item Groups di aplikasi | hanya **menarik** dari SAP (`GET /ItemGroups`) — tidak membuat/menugaskan |

Jadi jangan memaksakan Equipment > Component > Part masuk ke item group. Pembagian perannya:

| Peran | Tempat |
|---|---|
| Kategori fungsional (6–8 grup) | `OITB` → `ItemsGroupCode` |
| Equipment/vessel per item | UDF yang sudah ada (mis. `U_SOL_VesselEquip`) |
| Hierarki penuh | tetap di tabel katalog aplikasi (`hierarchy_path`) |

- Kode grup: pakai zona angka yang tidak bertabrakan dengan grup bawaan demo (100–102), mis. 101–199.
- Penentuannya harus deterministik dari kolom yang sudah terisi (manufacturer / kategori / posisi) —
  jangan bergantung pada kolom `Item Group No.` di CSV sumber: pada data nyata kolom itu kosong.
- Selalu cek dulu grup apa yang benar-benar ada (`GET /ItemGroups`, atau tabel mirror `sap_item_groups`)
  dan berapa item yang sudah punya `ItemsGroupCode`; perusahaan demo biasanya hanya punya grup bawaan.
