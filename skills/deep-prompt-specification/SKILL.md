---
name: deep-prompt-specification
description: "Author comprehensive, ultra-detailed agentic coding prompts and task specifications blending empirical evidence, strict negative constraints, deep schema definitions, and automated verification loops."
---

# Deep Prompt Specification & Enterprise Agentic Task Architecture

Skill ini adalah panduan otoritatif dalam menyusun **spesifikasi prompt coding agentik tingkat enterprise (Ultra-Detailed Prompt)** yang siap dieksekusi secara otonom oleh AI Coding Assistant (Antigravity, Claude Code, Cline, Cursor) dengan tingkat presisi 100%, nihil halusinasi, dan zero re-prompt.

Formula ini disusun dari sintesis empiris tugas nyata pengembangan sistem ERP maritim (*Master Data HS Code & Stock per Warehouse*) yang digabungkan dengan **Karpathy Guidelines**, **Ponytail Principles**, dan **Token Efficiency Protocol**.

---

## 1. Anatomi 7-Lapisan Prompt Ultra-Detail (The 7-Layer Architecture)

Setiap prompt spesifikasi komprehensif wajib memuat 7 lapisan terstruktur:

```
┌─────────────────────────────────────────────────────────────┐
│ 1. Context Anchor & Executive Intent (Tujuan & Batasan Sesi)│
├─────────────────────────────────────────────────────────────┤
│ 2. Negative Constraints & Scope Locks (Daftar Larangan Keras)│
├─────────────────────────────────────────────────────────────┤
│ 3. Current-State Empirical Audit (Fakta Riil di Database/Kode)│
├─────────────────────────────────────────────────────────────┤
│ 4. Deep Technical Specifications (Skema DB, Model, Sync, UI) │
├─────────────────────────────────────────────────────────────┤
│ 5. Mathematical & Business Formula Integrity (Aturan Baku)  │
├─────────────────────────────────────────────────────────────┤
│ 6. Verification Gates & Test Criteria (Kriteria Lulus Uji)  │
├─────────────────────────────────────────────────────────────┤
│ 7. Post-Implementation Deliverables (FDD, Guide, Excel, Hub)│
└─────────────────────────────────────────────────────────────┘
```

---

### Layer 1: Context Anchor & Executive Intent
- **Lokasi & Jalur Kerja**: Tentukan direktori absolut repositori, branch aktif, dan modul terkait.
- **Tujuan Bisnis**: Nyatakan dalam 2-3 kalimat apa nilai bisnis yang dicapai (mengapa fitur ini dibuat).
- **Aturan Eksekusi Otonom**: Berikan mandat otonom (pre-approved execution) agar AI tidak berhenti meminta izin untuk perintah terminal atau manipulasi file.

### Layer 2: Negative Constraints & Scope Locks (DILARANG MENYENTUH)
Kelemahan terbesar LLM adalah *over-engineering* dan merombak kode yang sedang berjalan sehat. Lapisan ini mengunci batasan secara tegas:
- **Protected Files**: Misal: *"DILARANG menyentuh navbar `resources/js/Layouts/AppLayout.jsx`"*.
- **Anti-Refactor Rule**: *"Ubah seminimal mungkin (surgical changes), jangan merefaktor komponen atau method yang sedang berjalan normal!"*.
- **YAGNI / Ponytail Rule**: Tentukan secara eksplisit fitur masa depan yang **TIDAK BOLEH** dibuat sekarang (contoh: *"Jangan tambah kolom tarif bm_rate/ppn_rate sekarang; buat master baru hanya untuk kebutuhan saat ini"*).
- **Network Boundaries**: *"Jangan hardcode URL — gunakan `config('...')`"*.

### Layer 3: Current-State Empirical Audit (Fakta Kondisi Sekarang)
Jangan biarkan AI menebak-nebak kondisi basis data. Berikan hasil audit nyata:
- Nama tabel eksisting, kolom eksisting, dan status isinya (contoh: *"Field `transactions.hs_code` saat ini terisi 0 baris, kolom `hs_alert` bertipe tinyint tapi tidak pernah dibaca di kode UI"*).
- Ketidakhadiran objek terkait (contoh: *"Belum ada tabel `sap_hs_codes`, belum ada UDT `@SOL_HSCODE`"*).
- Perilaku UI saat ini (contoh: *"Field input saat ini masih bertipe free-text di dalam modal X"*).

### Layer 4: Deep Technical Specifications
Spesifikasi teknis harus rigid dan tidak membuka ruang tafsir ganda:
1. **Skema Basis Data**:
   - Sajikan dalam tabel Markdown: Nama Kolom, Tipe Data, Keterangan, Indeks, Batasan Unik (Unique / Composite Unique).
   - Format penulisan data spesifik (contoh: *"Kode HS wajib disimpan berformat titik `8481.80.90`"*).
2. **ERP & Third-Party Metadata**:
   - Nama UDT (`@SOL_HSCODE`), UDF (`U_SOL_HS`), tipe ukuran data, dan nilai valid (*ValidValues*).
3. **Eloquent Model**:
   - Table name, `$fillable`, `$casts`, scopes (`scopeActive`), relasi antar-tabel, dan accessor.
4. **Sinkronisasi & Endpoint**:
   - Metode paging (`$top=100&$skip=...`), normalisasi data (`null` -> `0`, string casing), batching transaction per page untuk mencegah kegagalan parsial, audit timestamps.
5. **Controller & Inline Validations**:
   - Aturan regex spesifik (`/^[0-9.]{4,20}$/`), unique ignore on update, penanganan error 422 terstandar.
6. **Antarmuka Pengguna (UI/UX)**:
   - Komponen halaman: Index (filter, KPI card, badge), Create, Edit, Modal integrasi.
   - Kompatibilitas data historis: data lama yang tidak terdaftar di master tetap bisa disimpan dengan label penanda "Tidak terdaftar di master".

### Layer 5: Mathematical & Business Formula Integrity
Kunci rumus kalkulasi agar AI tidak mengganti logika bisnis:
- Formula eksplisit: `Available = InStock - Committed` (bukan OnHand + OnOrder - Committed).
- Aturan penanganan nilai khusus: *"Nilai stok minus dari SAP B1 diizinkan (jangan di-clamp ke 0) dan ditandai secara visual dengan warna coral/rose"*.

### Layer 6: Verification Gates & Definition of Done
Tentukan kriteria kelulusan biner (Pass/Fail):
- Perintah tes otomatis: `php artisan test --compact` wajib 100% hijau.
- Tes baru yang wajib dibuat: Migration check, unique constraint, validasi format, formula kalkulasi.
- Runtime smoke test: Jalankan serve lokal, buka halaman terkait, pastikan tidak ada layar putih (*white screen* / `public/hot`).
- Rollback test: Pastikan `migrate:rollback` dan `migrate` berjalan bersih.

### Layer 7: Post-Implementation Deliverables (Pasca-Koding)
Fitur enterprise tidak selesai hanya dengan koding:
1. **Changelog & Guide**: Update panduan arsitektur (misal `AI_DEVELOPMENT_GUIDE.md`) dengan kronologi keputusan teknis.
2. **Dokumen FDD (Functional Design Document)**:
   - Gunakan template berkas resmi.
   - Hanya perbarui teks validasi dan struktur data tanpa merubah warna, font, margin, atau layout tabel.
3. **Kamus Validasi Spreadsheet**: Update matriks kode validasi di file Excel resmi (`VALIDASI_WEB_APP_IBT_ONE.xlsx`).
4. **Integrasi Antar-Sistem**: Buat draf prompt siap kirim untuk tim pengembang integrasi (Integration Hub) yang memuat kontrak REST API JSON.
5. **Kebersihan Migrasi**: Folder migrasi harus rapi dan konsisten hanya memuat pembuatan tabel-tabel terdedikasi (`create_*_table.php`).

---

## 2. Templat Standar Prompt Ultra-Detail (Copy-Paste Ready)

Gunakan struktur di bawah ini saat menyusun prompt fitur enterprise:

````markdown
# PROMPT SPESIFIKASI: [Nama Modul / Fitur]

### ATURAN UTAMA SEBELUM MULAI
1. **Mandat Otonom**: Eksekusi secara otonom seluruh perintah teknis dan verifikasi hasil tanpa meminta konfirmasi yes/no.
2. **Surgical Changes**: Sentuh hanya baris yang relevan. Jangan ubah format atau refaktor kode yang sudah normal.
3. **Protected Boundaries**: Jangan sentuh [File / Navbar / Modul yang dilindungi].
4. **Non-Breaking Compatibility**: Data historis tetap valid dan tidak boleh tertolak oleh validasi baru.

---

### FAKTA KONDISI SEKARANG
- Kondisi tabel saat ini: [sebutkan tabel, kolom, dan jumlah baris terisi]
- Kondisi kode saat ini: [sebutkan komponen/controller yang menangani]
- Masalah/kebutuhan: [akar masalah teknis yang ingin diselesaikan]

---

### SPESIFIKASI FITUR 1: [Nama Sub-Fitur 1]
**1a. Skema Database Lokal (`create_..._table.php`)**:
| Kolom | Tipe Data | Keterangan & Index |
|---|---|---|
| `id` | bigint, pk | Auto increment |
| ... | ... | ... |

**1b. Kustomisasi ERP / SAP B1**:
- UDT: `@[NAMA_UDT]` dengan field [...]
- UDF: `[TABEL].U_[NAMA_UDF]`

**1c. Eloquent Model & Sync Service**:
- Model: `App\Models\[ModelName]` (fillable, casts, scopes)
- Sync Method: Paging `$top=100&$skip=...`, normalisasi data, batch commit.

**1d. Controller, Routing & UI**:
- Controller: Inline validation, regex, unique ignore.
- UI: Halaman Index, Form Create/Edit, Integrasi Modal transaksi.

---

### BATASAN (OUT OF SCOPE)
- JANGAN buat fitur [fitur spekulatif masa depan].
- JANGAN ubah formula [rumus bisnis baku].

---

### DEFINITION OF DONE & POST-DEVELOPMENT DELIVERABLES
1. `php artisan test --compact` 100% HIJAU (tulis unit & feature tests baru).
2. Runtime smoke test: buka halaman di web browser lokal, bebas white screen.
3. Update `AI_DEVELOPMENT_GUIDE.md` pada bab changelog rilis.
4. Update dokumen FDD Word (buat file revisi bernomor baru dari template asli, fokus ubah teks validasi & struktur data tanpa merusak styling).
5. Update file Excel kamus validasi sistem.
6. Susun teks prompt resmi untuk tim pengembang Integration Hub / API mitra.
7. Pastikan folder migrasi rapi dan bersih.
````

---

## 3. Checklist Verifikasi Mandiri Pembuat Prompt

Sebelum memberikan prompt kepada AI Agent, lakukan checklist:
- [ ] Apakah ada file yang rawan rusak yang sudah diberi pagar pelindung (*Protected Boundary*)?
- [ ] Apakah tipe data dan batasan unik sudah didefinisikan secara presisi (bukan sekadar "buatkan tabel")?
- [ ] Apakah formula matematika/bisnis sudah dikunci agar tidak diimprovisasi oleh LLM?
- [ ] Apakah ada instruksi penanganan data historis agar tidak menimbulkan kegagalan validasi masif?
- [ ] Apakah kriteria pengujian otomatis dan deliverables dokumen pasca-koding sudah tertera lengkap?
