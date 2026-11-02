# SQLite fallback untuk service Node/Express berdesain PostgreSQL

Skenario: service ditulis untuk `pg` (placeholder `$1`, `NOW()`, schema-qualified tabel), tapi Docker
/ PostgreSQL tidak tersedia di mesin dev. Jangan start server dengan DB kosong — jalankan di SQLite dengan
satu wrapper yang meniru bentuk balikan pg, lalu biarkan kode route tetap pakai `await db.query(sql, params)`
persis seperti semula. Seed kredensial dev di awal supaya login API bisa diuji sejak start pertama.

## Wrapper pg-compatible (bentuk yang terbukti jalan)

```ts
// db = new (require('sqlite3').verbose()).Database(path)
const run = (sql: string, params: any[] = []) =>
  new Promise<void>((res, rej) => db.run(sql, params, (e: any) => e ? rej(e) : res()));
const all = (sql: string, params: any[] = []) =>
  new Promise<any[]>((res, rej) => db.all(sql, params, (e: any, r: any[]) => e ? rej(e) : res(r)));
const get = (sql: string, params: any[] = []) =>
  new Promise<any>((res, rej) => db.get(sql, params, (e: any, r: any) => e ? rej(e) : res(r)));

db.query = async (sql: string, params: any[] = []) => {
  const q = sql.replace(/\$\d+/g, '?');
  if (/^\s*(SELECT|PRAGMA|WITH)/i.test(sql)) {
    const rows = await all(q, params);
    return { rows, rowCount: rows.length };
  }
  if (/^\s*INSERT/i.test(sql)) {
    await run(q, params);
    const table = q.match(/into\s+"?([\w_]+)"?/i)?.[1] ?? '';
    const row = await get(`SELECT * FROM ${table} ORDER BY rowid DESC LIMIT 1`);
    return { rows: row ? [row] : [], rowCount: 1 };
  }
  const rowCount = await new Promise<number>((res, rej) =>
    db.run(q, params, function (e: any) { e ? rej(e) : res(this.changes); }));
  return { rows: [], rowCount };
};
```

`rowid DESC LIMIT 1` untuk "row yang barusan di-INSERT" hanya aman untuk dev satu user — ganti `RETURNING`
asli saat pindah ke Postgres; tandai dengan komentar upgrade path.

## Bedah dialect — lakukan SEMUA di tepi wrapper/schema, bukan menyimpan

- **Placeholder:** `$1..$n` → `?` (sudah ditangani wrapper di atas).
- **`NOW()` hanya Postgres.** Ganti `datetime("now")`. Di dalam string JS ber-kutip tunggal, WAJIB kutip
  ganda `datetime("now")` — `datetime('now')` menutup string JS lebih awal dan esbuild meledak dengan
  `Expected ")" but found "now"` di titik itu.
- **Table schema-qualified `schema.tabel` tidak ada di SQLite** — `identity.users` dibaca sebagai schema
  `identity` yang tidak ada → `no such table`. Rename flat (`identity_users`). Replacernya harus menangkap
  bentuk quoted (`"identity.users"`) DAN unquoted (`identity.users`) — sed yang hanya menargetkan bentuk
  ber-quotes melewatkan semua query unquoted di route.
- **`db.run()` di node-sqlite3 hanya mengeksekusi statement PERTAMA** dari string multi-statement, sisa-nya
  tidak jalan tanpa error → chaining CREATE TABLE dalam satu string berarti tabel-tabel belakangan tidak
  pernah dibuat. Pisahkan jadi array statement, jalankan berurutan (await satu-satu).
- **Inisialisasi schema + seed harus SELESAI sebelum `app.listen`.** Bukti: server hidup, healthz hijau,
  tapi request pertama gagal `no such table` kalau seed masih jalan paralel. Kemas dalam satu async
  function dan `await` di awal `startServer()`.
- `TRUE`/`FALSE` dikenali SQLite 3.23+ — aman biarkan.

## Jebakan serialisasi yang tidak menghasilkan error — hanya 'invalid'

- **Object `Date` di-serialize driver sqlite3 menjadi string epoch-milidetik** (`"1793340189096.0"`), bukan
  tanggalteks. Perbandingan `expires_at > datetime("now")` lalu leksikografis salah selamanya → filter
  `invalid token`/`invalid session` tanpa error log apa pun. Simpan tanggalteks: `.toISOString()` di SETIAP
  kolom waktu yang dikirim sebagai param (login, refresh rotation — keduanya, bukan salah satu).
- **Kelupaan satu kolom di SELECT menghasilkan 'invalid' palsu, bukan error.** Query yang melakukan
  `bcrypt.compare(token, session.refresh_token)` harus benar-benar memilih `s.refresh_token` — kolom yang
  tidak ada datanya jadi `undefined`, compare = false, semua yang tersimpan dianggap token salah.
- **Cek format tersimpan langsung ke DB, bukan lewat API.** Satu script `node -e` dengan driver mentah yang
  `SELECT` barisnya (termasuk `typeof()` kolom) mendeteksi mismatch format dalam sekali jalan — error API
  ('invalid token') tidak pernah menunjukkan bahwa yang salah adalah REPRESENTASI data, bukan token atau
  logika bisnisnya.

## Pilih driver

Di Windows + Node baru, prefer driver dengan prebuilt binary (`sqlite3`) di atas yang butuh node-gyp build
(`better-sqlite3`) — kompilasi node-gyp gagal berulang kali tanpa toolchain lengkap. Tapi jangan memindahkan
gaya API-nya: `sqlite3` async callback, `better-sqlite3` sinkron — wrapper async di atas untuk sqlite3.

## Checklist start service (urutan yang menutup semua ini)

1. Kill pemilik lama port + verifikasi port kosong (lihat SKILL.md utama).
2. Start → baca log boot SEBELUM curl apa pun: 'DB initialized' harus muncul sebelum 'Started'.
3. curl healthz, lalu endpoint paling sensitif (login) dengan kredensial seed — bukan cukup healthz hijau.
4. Kalau endpoint 500: **tail log service dulu** — pesan `SQLITE_ERROR: no such table ...` sudah tertulis di
   sana; jangan menebak dari bentuk respons HTTP.