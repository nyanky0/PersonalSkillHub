# Pohon navigasi katalog sparepart

Hirarki browse dibangun **saat dibaca** dari kolom part, bukan dari `parent_id`. Yang disimpan di tabel
adalah rantai push (`parent_id`, `hierarchy_level`, `hierarchy_path`); yang dilihat user adalah trie yang
dirakit ulang dari kolom-kolomnya.

## 1. Merakit trie

```php
// sumber: HANYA baris daun, kolom agregatnya saja
foreach (EquipmentCatalog::query()
    ->where('is_active', true)->where('hierarchy_level', 3)->catalogReady()
    ->select('category', 'manufacturer', 'model_type', 'classification', 'part_no')
    ->orderBy('category')->orderBy('manufacturer')
    ->cursor() as $row) {
    // segmen = kolom classification SETELAH membuang 2 segmen pertama (kategori + nama mesin):
    // 'Aux Engine > Daihatsu 6DL-16Ae > Main Parts > 1 ENGINE FRAME > 1.1 ENGINE FRAME'
    $segments = array_map('trim', explode('>', (string) $row->classification));
    $path = array_slice($segments, 2);      // kedalaman variabel: 1–4 segmen
    // ... dorong ke trie: category > manufacturer > model_type > $path...
}
```

Bentuk node yang dikirim ke UI — **payload filter, bukan instruksi parsing**:

```php
$node = [
    'id'     => 'classification|' . substr(md5($key), 0, 12),
    'label'  => $segment,
    'level'  => 'classification',
    'count'  => $count,
    'filter' => array_filter([
        'category'            => $ctx['category'],
        'manufacturer'        => $ctx['manufacturer'],
        'model_type'          => $ctx['model_type'],
        'classification_like' => $rawPrefix,      // string ASLI dari kolom
        'component'           => $leafSegment,
    ]),
    'children' => $children,
];
```

Handler klik cukup `router.visit(route('catalog.index', node.filter))`. Kalau UI mulai menebak filter dari
`label`, tampilan dan data akan melenceng begitu format label berubah.

## 2. Filter `LIKE` wajib pakai string asli

Nama mesin di dalam kolom `classification` **tidak selalu sama** dengan gabungan
`manufacturer` + `model_type`:

| Sumber | Nilai |
|---|---|
| kolom `manufacturer` + `model_type` | `DAIHATSU` + `8DCM-32eF` |
| segmen di dalam `classification` | `Daihatsu - 8DCM-32eF` |

Pola yang dirakit dari kolom akan menghasilkan **0 baris** dan terlihat seperti fitur rusak, padahal
backend-nya benar. Ambil segmennya dari string aslinya, escape wildcard, baru tempelkan `%`:

```php
$rawPrefix = implode(' > ', array_slice($segments, 0, $depth));
$escaped   = str_replace(['\\', '%', '_'], ['\\\\', '\\%', '\\_'], $rawPrefix);
$query->where('classification', 'like', $escaped . '%');
```

## 3. Setting tampilan = kunci `group by` yang berbeda

Tidak perlu kolom atau migrasi baru; cukup ubah pengelompokan waktu merakit trie.

| Param query | Efek |
|---|---|
| `merge_mfr_model=1` | `manufacturer` + `model_type` jadi SATU level (`"Daihatsu 8DCM-32eF"`) |
| `merge_mfr_model=0` (default) | dua level terpisah (merek, lalu model) |
| `merge_classification_component=1` (default) | segmen terakhir digabung bila namanya sama dengan segmen sebelumnya |
| `merge_classification_component=0` | biarkan dua node terpisah |

- **Ikutkan opsi ini di key cache metadata** (`equipment_catalog_meta_{$branch}_{$a}_{$b}`). Kalau tidak,
nilai cache satu mode tersaji untuk mode lain dan seolah-olah user melihat angka yang salah — itu bug key
cache, bukan bug kueri.
- Ukuran terukur untuk 29.177 part: default **1.256 node / 293 KB** · `merge_mfr_model=1` 1.242 / 291 KB ·
`merge_classification_component=0` 1.796 / 449 KB. Ukur tiap kombinasi sebelum melaporkan.

## 4. Sisi React

- Render anak **hanya saat node di-expand** (`expanded.has(node.id)`); kotak cari pohon meng-expand
  otomatis. Merender seluruh level sekaligus untuk ~1,2rb node membuat halaman berat.
- Panel hirarki ini **bagian inti navigasi katalog**, jadi tampilkan di kedua layout (modern & classic).
- Simpan versi **ringan** (kategori → merek → model, ~37 node) untuk prop SHARED sidebar di
  `HandleInertiaRequests`, dan pohon penuh hanya di halaman katalog. Efek sampingnya bagus: payload
  halaman utama ikut turun (mis. `/` 305 KB → 133 KB) karena pohon shared tidak lagi memuat part.
- Layout lama yang membaca field lain (mis. `node.part_name`) harus ikut disesuaikan saat bentuk prop
  pohon berubah — kalau tidak, sidebar-nya blank tanpa error.

## 5. Loop verifikasi (tanpa membuka browser)

Semua filter node harus bisa dipanggil dari query string, supaya tiap node punya URL dan bisa diuji:

```bash
for q in "/catalog?category=Main+Engine" \
         "/catalog?category=Main+Engine&manufacturer=DAIHATSU" \
         "/catalog?classification_like=Main+Engine+%3E+Daihatsu+-+8DCM-32eF" \
         "/catalog?component=1.1+ENGINE+FRAME&manufacturer=DAIHATSU" ; do
  printf '%s -> ' "$q"
  curl -s -b "$CJ" "http://localhost:8112$q" -o p.html -w 'HTTP %{http_code} %{size_download}B'
  # lalu baca props.items.total dari atribut data-page dan bandingkan dengan count node-nya
  echo
done
```

- Bandingkan `count` tiap node dengan jumlah baris hasil filter URL-nya — **itu** bukti hierarkinya benar.
  Status `200` saja tidak membuktikan apa-apa.
- Jumlah tiap level harus ≤ level di atasnya. Angka sama di dua level wajar (semua baris satu model),
  tapi angka yang NAIK berarti segmen path salah dipotong.

## 6. Mutu kolom sumber

Kolom mentah dari sumber manual book baru ketahuan kotornya saat dipakai jadi filter/pencarian:
`Ref. Pos. No.` memuat `""`, `"!"`, `"(header)"`, `"(ref)"`. Bersihkan saat membangun table explorer;
jangan dipakai apa adanya sebagai nilai filter.
