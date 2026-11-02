# Anti-Patterns — 10 Hallucination Patterns yang Dieliminasi SANITY

Dokumen ini mendokumentasikan 10 pola hallucination paling merusak yang sering terjadi dalam AI coding assistants, beserta mekanisme deteksi dan pencegahannya.

---

## 1. 👻 Phantom Function Syndrome

**Definisi:** Menyebut API, function, atau method yang tidak ada dalam library atau codebase.

**Contoh:**
```python
# ❌ HALLUCINATION
"Gunakan `df.sort_smart(by='date', infer_types=True)` untuk sort dengan type inference otomatis."
# pandas tidak punya method sort_smart()

# ✅ SETELAH SANITY (setelah grep/docs check)
"Gunakan `df.sort_values(by='date')` — diverifikasi dari pandas docs [🟢 CONFIRMED]"
```

**Dampak:** User menghabiskan waktu debugging `AttributeError` yang seharusnya tidak terjadi.

**SANITY Prevention:** Setiap function yang disebutkan wajib diverifikasi via grep atau dokumentasi resmi.

---

## 2. 💀 Ghost File Hallucination

**Definisi:** Mengklaim konten, struktur, atau keberadaan file tanpa membacanya.

**Contoh:**
```
# ❌ HALLUCINATION
"Di file `lib/config/database.dart`, connection string sudah di-configure untuk production."
[Tidak pernah buka file ini]

# ✅ SETELAH SANITY
[Read: lib/config/database.dart]
"File ini berisi dev config (baris 12-19). Production config belum ada — 
perlu ditambahkan. [🟢 CONFIRMED dari direct read]"
```

**Dampak:** Bug production karena user percaya config sudah benar.

**SANITY Prevention:** Wajib Read() sebelum klaim apapun tentang konten file.

---

## 3. 🕰️ Version Confidence Fraud

**Definisi:** Menyatakan fitur atau behavior untuk versi library yang tidak ada dalam training data, atau salah menyebut compatibility.

**Contoh:**
```javascript
// ❌ HALLUCINATION
"Next.js 17 memperkenalkan Server Actions 2.0 yang mendukung offline-first..."
// Next.js 17 belum ada di training data

// ✅ SETELAH SANITY
"Per data training saya (Next.js 15 RC, Aug 2025), Server Actions bekerja dengan...
Untuk versi 17+, cek docs resmi Next.js. [⚠️ Training Knowledge, cutoff Aug 2025]"
```

**Dampak:** Implementasi berdasarkan API yang tidak ada atau sudah berubah.

**SANITY Prevention:** Selalu label versi dengan training cutoff, rekomendasikan docs terbaru.

---

## 4. 🎭 False Certainty Masking

**Definisi:** Menyatakan diagnosa atau conclusion dengan confidence yang tidak sesuai dengan evidence yang ada.

**Contoh:**
```
# ❌ HALLUCINATION
User: "App saya crash setelah 30 detik."
AI: "Masalahnya pasti memory leak di ListView builder kamu."
[Tidak ada stack trace, tidak ada kode yang dilihat]

# ✅ SETELAH SANITY
User: "App saya crash setelah 30 detik."
AI: "[🔴 UNCERTAIN tanpa stack trace] Ada beberapa kemungkinan:
- Memory leak (paling umum untuk timing seperti ini)
- Timer/animation yang tidak di-disposed
- Network timeout yang mishandled

Tolong share stack trace atau error log — saya akan diagnosa dari bukti konkret."
```

**Dampak:** User menghabiskan waktu pada root cause yang salah.

**SANITY Prevention:** Tingkat confidence harus match dengan evidence yang ada.

---

## 5. ✍️ Confident Completion Fabrication

**Definisi:** Mengisi implementasi "lengkap" untuk API atau sistem yang sebenarnya tidak dikenal.

**Contoh:**
```python
# ❌ HALLUCINATION
"Ini implementasi lengkap untuk integrate dengan API Tokopedia kamu:"
[Menulis 100 baris kode dengan endpoint, auth, dan error handling yang sepenuhnya dibuat-buat]

# ✅ SETELAH SANITY
"Saya tidak punya dokumentasi Tokopedia API internal kamu. Yang bisa saya berikan:
- Skeleton structure yang perlu kamu isi [🟢 CONFIRMED pattern dari REST API best practices]
- Saya butuh: endpoint docs, auth method, sample request/response

[PERLU INPUT] Share API docs atau spec, saya akan implement dengan akurat."
```

**Dampak:** Production bugs dari API call yang salah, security vulnerability dari auth yang salah.

**SANITY Prevention:** Identifikasi knowledge gap sebelum implement, minta dokumentasi.

---

## 6. 📰 Recency Abuse

**Definisi:** Menggunakan kata "baru-baru ini", "terbaru", "latest" tanpa mengetahui konteks temporal yang sebenarnya.

**Contoh:**
```
# ❌ HALLUCINATION
"Google baru-baru ini mengupdate Firebase Auth untuk mendukung passkeys secara native."
[Tidak tahu kapan "baru-baru ini" dari perspektif user]

# ✅ SETELAH SANITY
"Per data training saya (Aug 2025), Firebase Auth mendukung passkeys via FirebaseUI.
Untuk update terbaru setelah Aug 2025, cek https://firebase.google.com/docs/auth
[⚠️ Training Knowledge — fitur bisa sudah berubah]"
```

**Dampak:** User membuat keputusan berdasarkan informasi yang mungkin sudah outdated.

**SANITY Prevention:** Ganti "baru-baru ini" dengan explicit timestamp dari training data.

---

## 7. 📚 Stack Overflow Paraphrase Bug

**Definisi:** Memberikan solusi yang valid di masa lalu tapi API-nya sudah deprecated atau berubah.

**Contoh:**
```javascript
// ❌ HALLUCINATION
"Gunakan componentWillMount() untuk fetch data saat component pertama kali load."
// componentWillMount() sudah DEPRECATED sejak React 16.3

// ✅ SETELAH SANITY
"componentWillMount() sudah deprecated sejak React 16.3 [🟢 CONFIRMED dari training].
Gunakan useEffect(() => { fetchData(); }, []) atau componentDidMount() sebagai gantinya.
[⚠️ Untuk React 19+, cek official migration guide — ada perubahan lifecycle]"
```

**Dampak:** Deprecated API di production, warning yang mengotori logs.

**SANITY Prevention:** Flag semua API yang diketahui deprecated, rekomendasikan modern alternative.

---

## 8. 🔗 Citation Fabrication

**Definisi:** Membuat referensi, link, atau kutipan yang tidak ada.

**Contoh:**
```
# ❌ HALLUCINATION
"Menurut RFC 9876 section 4.2, JWT harus menggunakan RS256 untuk production..."
[RFC 9876 tidak ada]

# ✅ SETELAH SANITY
"Best practice JWT untuk production (berdasarkan training knowledge tentang security):
- Gunakan RS256 untuk asymmetric signing
- Set expiry pendek (15-60 menit)
[💭 Training Knowledge — verifikasi dengan OWASP JWT Cheat Sheet untuk current guidance]"
```

**Dampak:** Trust collapse ketika user tidak menemukan referensi yang disebutkan.

**SANITY Prevention:** Jangan cite dokumen yang tidak bisa diverifikasi keberadaannya.

---

## 9. 🧮 Math Confidence Skip

**Definisi:** Memberikan hasil kalkulasi tanpa menunjukkan cara kerja, membuat silent math error.

**Contoh:**
```
# ❌ HALLUCINATION
"Dengan 10,000 users dan rata-rata 50 query/user/hari, database kamu akan handle 
500,000 queries/hari atau sekitar 5.8 queries/detik." 
[5.8 salah: 500,000 / 86,400 = 5.78 — hampir benar tapi tanpa verification trail]

Lebih parah:
"Dengan cache hit rate 85%, effective queries = 10,000 * 50 * 0.15 = 52,500/hari"
[Benar tapi user tidak bisa verifikasi tanpa show work]

# ✅ SETELAH SANITY
"Mari hitung step by step:
- Total queries/hari: 10,000 users × 50 queries = 500,000 queries/hari
- Per detik: 500,000 / 86,400 detik = 5.787 queries/detik ≈ 5.8 q/s [🟢 CONFIRMED]
- Dengan 85% cache: 500,000 × (1 - 0.85) = 500,000 × 0.15 = 75,000 DB queries/hari
- Effective DB load: 75,000 / 86,400 = 0.868 q/s ke database [🟢 CONFIRMED]"
```

**Dampak:** Kapasitas planning yang salah, over/under provisioning.

**SANITY Prevention:** Show work untuk semua kalkulasi, enable user verification.

---

## 10. 🔄 Self-Contradiction Blindness

**Definisi:** Menyatakan hal yang saling berkontradiksi dalam satu respons tanpa menyadarinya.

**Contoh:**
```dart
// ❌ HALLUCINATION (dalam satu respons)
// Paragraf 1:
"Gunakan StatelessWidget untuk screen ini karena tidak perlu state management."

// [50 baris kemudian...]

// Paragraf 4:
"Di initState(), fetch data dari API dan simpan ke state variable..."
[initState() hanya ada di StatefulWidget — KONTRADIKSI!]

// ✅ SETELAH SANITY (dengan pre-delivery self-check)
"Karena screen ini butuh fetch data dan simpan hasilnya, gunakan StatefulWidget.
Di initState(), fetch data dari API dan simpan ke state variable dengan setState()."
[Konsisten dari awal sampai akhir]
```

**Dampak:** Code yang tidak bisa dikompilasi, confusion dan rework.

**SANITY Prevention:** Pre-delivery checklist mencari naming/type/logic inconsistencies.

---

## Severity Matrix

| Anti-Pattern | Security Risk | Time Waste | Trust Impact | Recovery Cost |
|---|:---:|:---:|:---:|:---:|
| Phantom Function | Low | High | Medium | Medium |
| Ghost File | Medium | High | High | High |
| Version Fraud | High | Medium | High | High |
| False Certainty | Low | Very High | High | Medium |
| Confident Completion | Very High | Very High | Very High | Very High |
| Recency Abuse | Medium | Medium | Medium | Low |
| SO Paraphrase | Medium | High | Medium | Medium |
| Citation Fabrication | Low | Low | Very High | Low |
| Math Skip | Medium | Medium | Medium | Low |
| Self-Contradiction | Low | High | Medium | Medium |

---

*Anti-Patterns ini dikumpulkan dari real-world hallucination cases. Jika kamu menemukan pattern baru, [report di GitHub Issues](https://github.com/verycoolapps/sanity-anti-hallucination-skill/issues).*
