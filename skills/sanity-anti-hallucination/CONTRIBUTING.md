# Contributing to SANITY

Terima kasih sudah ingin berkontribusi ke SANITY — Anti-Hallucination Supremacy Protocol!

## 🎯 Cara Berkontribusi

### 1. Report Hallucination yang Lolos

Menemukan kasus di mana SANITY tidak berhasil mencegah hallucination? **Ini adalah kontribusi paling berharga!**

Gunakan template [Hallucination Report](.github/ISSUE_TEMPLATE/hallucination_report.md):
- Deskripsikan klaim yang salah
- Tunjukkan klaim apa yang seharusnya diverifikasi
- Berikan langkah reproduksi

### 2. Tambah Anti-Pattern Baru

Temukan pola hallucination yang belum ada di BLACKLIST? 

1. Fork repo ini
2. Tambah ke `docs/ANTI_PATTERNS.md` dengan format:
   ```markdown
   ### ❌ [Nama Anti-Pattern]
   SALAH: [contoh hallucination]
   BENAR: [verifikasi yang seharusnya dilakukan]
   DAMPAK: [kenapa ini berbahaya]
   ```
3. Submit Pull Request

### 3. Tambah Verification Playbook

Punya kategori klaim yang butuh playbook spesifik?

1. Tambah ke `docs/METHODOLOGY.md` dalam section Playbooks
2. Ikuti format: Trigger → Protocol → Steps → Anti-pattern
3. Submit PR dengan deskripsi use case

### 4. Improve Uncertainty Vocabulary

Temukan framing yang lebih baik untuk mengkomunikasikan uncertainty?

- Submit di `docs/CONFIDENCE_MATRIX.md`
- Sertakan contoh before/after

### 5. Terjemahan

SANITY saat ini tersedia dalam Bahasa Indonesia dan Inggris. Bantu kami porting ke bahasa lain!

## 📋 Pull Request Guidelines

- PR title harus deskriptif: `feat: add playbook for GraphQL schema validation`
- Sertakan contoh konkret untuk setiap perubahan
- Pastikan tidak ada typo atau inkonsistensi
- Update CHANGELOG.md dengan perubahan kamu

## 🤔 Pertanyaan?

Buka Issue dengan label `question` — kami akan respons secepat mungkin.
