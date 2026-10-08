# Ukur per-prop, lalu ganti daftar opsi dengan typeahead

Angka di bawah dari halaman katalog nyata (Laravel + Inertia + React): 3 dropdown filter memakan
169 KB dari 826 KB HTML halaman. Setelah dibuang dari prop bersama: prop `options` 148 KB → 2 KB,
halaman 826 KB → 612 KB.

| Bagian | Entri | Berat di payload |
|---|---|---|
| dropdown posisi | 2.826 | 21 KB |
| dropdown komponen | 1.205 | 40 KB |
| dropdown klasifikasi | 1.357 | 107 KB |

## 1. Ukur berat tiap prop

Props Inertia ada di atribut `data-page` pada HTML respons (butuh sesi login — prop shared hanya dihitung
pada request sungguhan).

```python
import re, json, html, sys
h = open(sys.argv[1], encoding='utf-8').read()
props = json.loads(html.unescape(re.search(r'data-page="([^"]*)"', h).group(1)))['props']
for k, v in sorted(props.items(), key=lambda kv: -len(json.dumps(kv[1]))):
    print(f"{len(json.dumps(v)):>9,}  {k}")
```

Ambil HTML-nya: login lewat curl (CSRF dari `GET /login`, lalu `POST /login`) dengan cookie jar, lalu
`curl -b jar -o hasil.html <url>`; `stat -c%s hasil.html` untuk ukurannya.

Ukur ulang setelah tiap perubahan — angka inilah yang dilaporkan ke user.

## 2. Endpoint saran berbatas

```php
Route::get('/catalog/api/options', [EquipmentCatalogController::class, 'apiOptions'])
    ->name('catalog.api.options');
```

```php
private const SUGGESTABLE = ['component', 'classification', 'position', 'part_no'];

public function apiOptions(Request $request): JsonResponse
{
    $field = (string) $request->get('field');
    if (! in_array($field, self::SUGGESTABLE, true)) {
        abort(422, 'Unknown field.');
    }

    $q = addcslashes((string) $request->get('q'), '%_\\');
    $limit = min(max((int) $request->get('limit', 25), 1), 50);

    $rows = $this->baseQuery()                 // scope filter/visibilitas yang sama dengan tabel
        ->when($q !== '', fn ($query) => $query->where($field, 'like', "%{$q}%"))
        ->select($field)->distinct()
        ->orderBy($field)
        ->limit($limit)
        ->pluck($field);

    return response()->json(['success' => true, 'values' => $rows]);
}
```

Catatan: `$field` sudah dijamin whitelist, jadi aman dipakai sebagai nama kolom — jangan menyusun nama
kolom dari input bebas meski terlihat "sudah difilter".

## 3. Komponen typeahead (React)

```jsx
const [value, setValue] = useState('');        // '' = tanpa filter, bukan 'ALL'
const [suggestions, setSuggestions] = useState([]);

useEffect(() => {
  const t = setTimeout(() => {
    if (value.trim() === '') { setSuggestions([]); return; }
    fetch(route('catalog.api.options', { field: 'component', q: value }))
      .then((r) => r.json())
      .then((d) => setSuggestions(d.values ?? []))
      .catch(() => setSuggestions([]));
  }, 300);
  return () => clearTimeout(t);
}, [value]);

<input list="component-suggest" value={value} onChange={(e) => setValue(e.target.value)}
       onBlur={() => applyFilters({ component_like: value })} />
<datalist id="component-suggest">
  {suggestions.map((v) => <option key={v} value={v} />)}
</datalist>
```

Semantik parameter: `*_like` = awalan (cocok untuk nilai satu token), `*_q` = mengandung (cocok untuk
kotak ketik bebas dan nilai berupa path panjang).

## 4. Verifikasi filter dengan curl

Uji satu per satu di saat cache sudah dibersihkan, dan periksa **jumlah barisnya**, bukan cuma HTTP 200:

- nilai mengandung pada kolom path panjang → harus mengembalikan baris (awalan akan mengembalikan 0 dan
  itulah bug yang mudah lolos);
- nilai awalan pada kolom satu token → harus mengecil dari tanpa filter;
- nilai kosong → sama dengan tanpa filter;
- `?field=kolom_ngawur` → 422, bukan diterima;
- filter yang sama di jalur ekspor → jumlah baris ekspor cocok dengan tabel.
