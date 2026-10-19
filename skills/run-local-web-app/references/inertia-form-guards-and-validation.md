# Validasi & guard di halaman Inertia/React (Laravel + React)

Catatan lapangan untuk bug yang muncul di halaman form Inertia. Dipakai saat gejalanya "tidak bisa save",
"popup muncul sekejap lalu halaman pergi", atau "link/panel tidak muncul padahal kodenya ada".

## Bug “field must be an integer” saat kolomnya desimal

Gejala: dokumen lama tidak bisa di-save ulang; validasi menolak `quantity`/`qty` padahal user tidak mengubah
apa pun.

Sebelum menyalahkan datanya, **ukur DB-nya**:

```sql
SELECT COUNT(*) FROM tabel WHERE kolom != CAST(kolom AS INTEGER);
```

Kalau nol, sumber errornya payload halaman, bukan baris tersimpan. Perlu kejelian: driver mengembalikan
`decimal` sebagai string `"2.7500"`, jadi baris itu lolos dari pengecekan `!= 2` di Python namun dikirim ke
validasi sebagai string yang gagal rule `integer`.

**Aturan: cast di tempat validasi, bukan setelahnya.** `$request->validate()` dan `withValidator` menerima
array mentah sebelum cast apa pun di service. Jadi menambahkan `(int)` di service sambil membiarkan rule
`integer` **tidak memperbaiki apa-apa** — request tetap 422 lebih dulu.

| Aturan | Efek |
|---|---|
| rule `integer` + cast `(int)` di service | desimal **ditolak** di validasi; cast tidak pernah tercapai |
| rule `numeric` + `floor((float)$v)` di service | menerima payload desimal (termasuk baris lama) dan menyimpannya bulat |

Pakai yang kedua kalau kolomnya sudah `decimal` dan ada baris lama: rule disesuaikan dulu, cast menyusul.
Lalu **uji langsung dengan Validator**, bukan lewat endpoint — satu perintah membuktikan `2.0` diterima
sementara `1.5` / `"2.50"` ditolak.

Tambahan: `FormRequest::make()` di dalam unit test mengembalikan instance yang belum melewati
`withValidator` — panggil `->after()` manual, atau uji lewat endpoint sungguhan dengan `actingAs()`, kalau
tidak test-nya hijau sementara aturan aslinya tidak diuji sama sekali.

## Guard navigasi client (unsaved-changes) vs router Inertia

`window.history.state` **milik Inertia** (berisi `page`), bukan milik halaman.
`history.pushState(myState, ...)` menggantinya dengan state yang ditolak Inertia, lalu Inertia yang memegang
listener `popstate` ikut jalan dan menavigasi keluar — dialog muncul sekejap lalu halaman benar-benar pergi.

Yang bekerja: tandai entri penjaga dengan marker sendiri dan baca state dengan spread.

```js
const OWN = "__guard";
const handlePopState = (event) => {
    if (!guardArmed()) return;      // hanya saat form kotor & bukan sedang discard
    if (event.state?.[OWN]) return; // popstate dari pushState kita sendiri: abaikan
    window.history.pushState({ ...(window.history.state || {}), [OWN]: true }, "", window.location.href);
    setPendingNavigation({ type: "history_back" });
    setDiscardModalOpen(true);
};
window.addEventListener("popstate", handlePopState, true); // capture: jalan sebelum Inertia
```

- **popstate tidak bisa di-cancel** (`preventDefault()` tidak berpengaruh). Satu-satunya cara menahan user di
  halaman adalah re-push entri penjaga; itulah satu-satunya sebab desain ini ada.
- `beforeunload` tetap perlu terpisah untuk reload/tutup tab/ketik URL — popstate tidak menangkap itu.
- `router.on("before", …)` tetap dipakai untuk klik link, tapi jangan mengandalkannya untuk tombol back.
- **Jangan tambah timer buatan pada guard.** Menghentikan guard beberapa detik setelah render (supaya user
  “sempat membaca”) justru membiarkan back lolos di jendela itu; dialog + konfirmasi eksplisit sudah cukup.
  `countdown` pada tombol konfirmasi hanya menghambat alur normal.

### Verifikasi guard sebagai logika murni, bukan lewat klik

Fake-`history` kecil — `pushState` (dengan splice + index) dan array entri — plus pemanggilan handler
popstate langsung, menguji tiga hal yang penting tanpa browser sama sekali:

1. back ditekan saat form kotor → **masih di dokumen**;
2. popstate lanjutan dari `pushState` kita sendiri → **diabaikan**, tidak mundur dua langkah;
3. setelah user memilih keluar → **pergi tepat satu langkah**.

Simpan sebagai test runnable (`node buat/guard.test.mjs`, tanpa framework) di sebelah kode, dan cetak
`PASS/FAIL` + `exit 1` supaya bisa dipakai ulang.

## Section yang “tidak pernah dirender”

Elemen yang dilaporkan hilang sering **sudah ada di kode, tapi di dalam cabang ternary mode**.
Cari `{mode ? (form) : (view)}` sebelum menyimpulkan komponennya tidak dibuat: section yang hidup di cabang
form hanya tampil saat mode itu aktif. Perbaikannya = pindahkan section ke cabang yang juga tampil di mode
baca, bukan menambah komponen kedua yang isinya berulang.

Gejala saudaranya: **komponen muncul dua kali** di layar padahal kodenya satu. Itu tanda prop sumbernya
berbeda — payload halaman datang terlampau gemuk dan komponen menerima daftar tak terfilter. Periksa berapa
kali elemen itu benar-benar dirender, jangan berhenti pada kemunculan pertama.

## Textarea vs hyperlink

Remarks bertaut butuh **dua** jalur render:

- **mode edit** → `<textarea>` untuk mengetik (tidak bisa diklik), jadi render preview bertaut di bawahnya
  supaya link lama tetap bisa diklik tanpa keluar dari mode edit;
- **mode baca** → render teks bertaut, jangan hanya `<textarea readOnly>`, kalau tidak link tampak sebagai
  teks polos.

Satukan auto-link (regex `/(https?:\/\/[^\s]+)/g` + `target="_blank" rel="noopener noreferrer"` +
`stopPropagation` supaya klik tidak ikut memicu context menu baris) ke **satu komponen bersama**, bukan
salin-tempel di tiap tempat — begitu ada tiga salinan, satu tempat akan tertinggal saat aturannya berubah.
