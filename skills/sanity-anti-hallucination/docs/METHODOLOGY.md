# SANITY Methodology — Deep Dive

## REALE Framework — Penjelasan Mendalam

### Mengapa 5 Pilar?

Hallucination AI tidak punya satu penyebab tunggal. Ada banyak titik kegagalan:
- **Training data bias** → model "ingat" pattern yang tidak akurat
- **Completion pressure** → model dipaksa complete meski tidak punya data
- **Confidence miscalibration** → model tidak tahu kapan tidak tahu
- **Recency blindness** → model tidak sadar knowledge-nya sudah outdated

REALE Framework menyasar setiap titik kegagalan ini.

---

## Pillar 1: READ — Verifikasi File-Level

### Prinsip Dasar
Model bahasa tidak "punya" konten file. Yang dimiliki model adalah *pattern* tentang bagaimana file biasanya terlihat. Ketika model mengklaim "file X berisi Y," itu adalah **prediksi berbasis pattern**, bukan **fakta berbasis observasi**.

SANITY memaksa perpindahan dari prediksi ke observasi.

### Decision Tree: Kapan Harus Read?

```
Apakah klaim menyebut isi, struktur, atau konten file tertentu?
│
├─ YA → Read file sekarang
│       ├─ File ada → Quote baris spesifik, sebutkan nomor baris
│       └─ File tidak ada → "File tidak ditemukan di path tersebut"
│
└─ TIDAK → Apakah klaim menyebut function/class/variable spesifik?
           │
           ├─ YA → Grep/Search untuk konfirmasi
           │       ├─ Found → Cite path:baris
           │       └─ Not found → "Tidak ditemukan dalam codebase"
           │
           └─ TIDAK → Apakah klaim tentang perilaku runtime?
                      ├─ YA → Run dulu, baru claim
                      └─ TIDAK → Lanjut ke Pillar 2
```

### Contoh Nyata

**Sebelum SANITY:**
```
User: "Apa yang dilakukan fungsi auth di project ini?"
AI: "Fungsi `authenticate()` di `lib/auth.dart` melakukan OAuth flow 
     dengan token refresh setiap 30 menit menggunakan JWT."
[HALLUCINATION: Tidak ada yang diverifikasi]
```

**Setelah SANITY:**
```
User: "Apa yang dilakukan fungsi auth di project ini?"
AI: [Bash: grep -rn "authenticate\|auth" lib/] 
    [Read: lib/auth/auth_service.dart]
    
    "Berdasarkan `lib/auth/auth_service.dart:45-89`:
    - `authenticate()` melakukan email/password validation (baris 47)
    - Token disimpan di SecureStorage (baris 61)
    - Refresh terjadi via `refreshToken()` di baris 78
    
    [🟢 CONFIRMED dari direct read — baris dikutip dengan akurat]"
```

---

## Pillar 2: EVIDENCE — Hierarchy Bukti

### The Evidence Pyramid

```
            ┌─────────────┐
            │  DIRECT OBS │  🔬 Baca/Run sendiri sekarang
            └──────┬──────┘
                   │
            ┌──────▼──────┐
            │  DOCUMENTED │  📄 Docs resmi, source code terbuka
            └──────┬──────┘
                   │
            ┌──────▼──────┐
            │   LOGICAL   │  🔗 Derivasi dari fakta terverifikasi
            └──────┬──────┘
                   │
            ┌──────▼──────┐
            │   TRAINED   │  💭 Knowledge dari training (dengan label)
            └──────┬──────┘
                   │
            ┌──────▼──────┐
            │  SPECULATION│  ❓ Wajib dilabeli, tidak bisa disajikan sbg fakta
            └─────────────┘
```

### Aturan Per Level

**Level 1 — Direct Observation:**
- Boleh disampaikan dengan confidence penuh
- Wajib sertakan tool call result atau output aktual

**Level 2 — Documented Source:**
- Sertakan link atau nama dokumen
- Acknowledge bahwa docs bisa outdated

**Level 3 — Logical Derivation:**
- Tunjukkan chain of reasoning
- Identify premises yang digunakan
- Acknowledge jika ada premise yang belum terverifikasi

**Level 4 — Trained Knowledge:**
- WAJIB label: `[Training Knowledge, cutoff Aug 2025]`
- WAJIB rekomendasikan verifikasi ke sumber primer
- TIDAK boleh sebut sebagai fakta mutlak

**Level 5 — Speculation:**
- WAJIB label: `[Spekulasi]` atau `[Perlu Verifikasi]`
- TIDAK boleh disajikan tanpa label
- Selalu sertakan cara untuk memverifikasi spekulasi

---

## Pillar 3: ASSUME — Asumsi Management

### Taxonomy Asumsi

```
ASUMSI ENVIRONMENT    → OS, versi tool, konfigurasi lokal
ASUMSI DEPENDENCY     → Package ter-install, versi kompatibel
ASUMSI STATE          → Data yang ada di database, file yang ada
ASUMSI BEHAVIOR       → Bagaimana library/framework berperilaku
ASUMSI REQUIREMENTS   → Apa yang user inginkan
```

### Format Labeling

```markdown
[ASUMSI ENVIRONMENT]   Kamu menggunakan macOS dengan Xcode 16+.
[ASUMSI DEPENDENCY]    Package `shared_preferences` sudah ada di pubspec.yaml.
[ASUMSI STATE]         Database sudah ter-migrate ke schema versi terbaru.
[ASUMSI BEHAVIOR]      `setState()` akan trigger rebuild di semua widget yang affected.
[PERLU KONFIRMASI]     Apakah menggunakan null safety di project ini?
```

### Kapan Asumsi Boleh Dibuat?

Asumsi **boleh** dibuat jika:
- Sangat umum untuk konteks yang ada
- Disebutkan secara eksplisit dalam prompt sebelumnya
- Bisa diverifikasi dengan mudah

Asumsi **TIDAK boleh** dibuat jika:
- Menyangkut data sensitif atau security
- Berpengaruh besar pada arsitektur solusi
- Tidak konsisten dengan informasi yang sudah diketahui

---

## Pillar 4: LIMITS — Knowledge Boundary Management

### Jenis Knowledge Limits

**1. Temporal Limits (Paling Umum)**
```
Training cutoff: Agustus 2025
Risiko: Library update, API breaking changes, deprecated features
Mitigasi: Label semua facts dengan "[Per Aug 2025]", rekomendasikan cek docs terbaru
```

**2. Domain Limits**
```
Areas di luar keahlian: legal, medical, financial (detail spesifik)
Risiko: Advice yang tampak valid tapi berbahaya
Mitigasi: Selalu recommend professional consultation
```

**3. Access Limits**
```
Yang tidak bisa diakses: API eksternal, database produksi, sistem tertutup
Risiko: Claim tentang data/state yang tidak bisa diverifikasi
Mitigasi: "Saya tidak punya akses ke X, jadi saya tidak bisa verifikasi..."
```

**4. Scope Limits**
```
Kondisi: File tidak dibaca, context tidak diberikan
Risiko: Klaim tentang kode yang tidak dilihat
Mitigasi: "Saya belum melihat kodenya — tolong share atau izinkan saya membacanya"
```

### Knowledge Limit Declaration Template

```
[KNOWLEDGE LIMIT] Saya tidak punya informasi tentang [X] karena:
- [Alasan: temporal/domain/access/scope]
- Untuk mendapatkan informasi ini, kamu perlu [langkah konkret]
- [Opsional] Yang BISA saya bantu: [alternatif yang bisa dilakukan]
```

---

## Pillar 5: ERROR-CHECK — Self-Validation Protocol

### Pre-Delivery Checklist

Sebelum setiap respons di-deliver, jalankan checklist ini secara mental:

```
□ Apakah ada klaim tentang file yang belum dibaca?
□ Apakah ada function/API disebutkan yang belum diverifikasi?
□ Apakah ada versi library disebutkan tanpa konfirmasi?
□ Apakah nama variable/function konsisten sepanjang respons?
□ Apakah contoh kode syntactically valid?
□ Apakah solusi menjawab pertanyaan aktual yang diajukan?
□ Apakah ada pernyataan di bagian awal yang berkontradiksi bagian akhir?
□ Apakah confidence level sudah di-label dengan benar?
□ Apakah asumsi sudah ditandai?
□ Apakah training knowledge sudah diberi expiry warning?
```

### Contradiction Detection Patterns

**Type 1: Naming Inconsistency**
```
Baris 3: "Gunakan `UserController` untuk handle request..."
Baris 47: "...seperti yang dilakukan `UserManager`..."
[KONTRADIKSI: dua nama berbeda untuk hal yang sama?]
```

**Type 2: Version Inconsistency**
```
Baris 12: "Flutter 3.24 mendukung..."
Baris 89: "Di Flutter 3.22, kita harus..."
[KONTRADIKSI: Versi mana yang relevan?]
```

**Type 3: Logic Inconsistency**
```
Baris 5: "Function ini tidak memerlukan authentication..."
Baris 67: "Pastikan user sudah login sebelum call function ini..."
[KONTRADIKSI: Perlu auth atau tidak?]
```

---

## Implementation Notes untuk Claude Code

### Ketika di-invoke via `/sanity`

1. Load semua 5 pillar ke working memory
2. Set confidence labeling ke mandatory
3. Enable pre-delivery checklist
4. Switch vocabulary ke uncertainty-aware mode
5. Acknowledge kepada user bahwa SANITY Protocol aktif

### Ketika integrated via CLAUDE.md

- SANITY berjalan di background setiap respons
- Tidak perlu announce — langsung apply protocol
- User hanya melihat output yang lebih akurat, bukan process

### Performance Considerations

SANITY menambah latency karena:
- Read tool calls tambahan untuk verifikasi
- Grep/search untuk function verification
- Mental checklist sebelum deliver

Trade-off ini **selalu worth it** karena satu hallucination bisa menyebabkan jam debugging.
