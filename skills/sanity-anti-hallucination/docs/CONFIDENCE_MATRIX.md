# SANITY Confidence Matrix — Reference Guide

## Overview

Confidence Matrix adalah sistem 4-tier untuk mengkomunikasikan tingkat kepercayaan
terhadap setiap klaim secara akurat dan konsisten.

---

## The Four Tiers

### 🟢 CONFIRMED — Verified by Direct Observation

**Definisi:** Klaim yang diverifikasi secara langsung melalui tool call dalam sesi aktif.

**Syarat untuk label ini:**
- [ ] File telah dibaca dengan Read() tool
- [ ] Function telah dicari dengan Bash grep
- [ ] Test telah dijalankan dan output terlihat
- [ ] Command telah di-execute dan result tersedia

**Format penggunaan:**
```
[🟢 CONFIRMED: src/auth/login.dart:45] Token di-set dengan expiry 24 jam.
[🟢 CONFIRMED dari test output] Test berhasil: 23 passed, 0 failed.
[🟢 CONFIRMED] Function `authenticate()` ada di `lib/auth.dart:89`.
```

**JANGAN gunakan untuk:**
- Klaim yang tidak diverifikasi di sesi ini
- Klaim berdasarkan "biasanya" atau "umumnya"
- Klaim tentang behavior yang belum ditest

---

### 🟡 INFERRED — Logical Conclusion from Evidence

**Definisi:** Kesimpulan yang secara logis valid berdasarkan evidence yang ada, tapi belum diverifikasi secara langsung.

**Syarat untuk label ini:**
- Evidence yang mendukung inferensi ada dan terverifikasi
- Chain of reasoning eksplisit dan valid
- Tidak ada counterevidence yang diketahui

**Format penggunaan:**
```
[🟡 INFERRED dari stack trace baris 3] Kemungkinan null pointer di user.profile.
[🟡 INFERRED dari timing] Error terjadi setelah 30 detik → kemungkinan timeout.
[🟡 INFERRED dari pattern] Ini classic race condition berdasarkan async structure.
```

**JANGAN gunakan untuk:**
- Inferensi yang lemah atau speculative
- Klaim yang bisa langsung diverifikasi (gunakan 🟢 sebagai gantinya)
- Kesimpulan yang bergantung pada asumsi yang belum diverifikasi

---

### 🔴 UNCERTAIN — Speculation or Outdated Knowledge

**Definisi:** Klaim yang berdasarkan pengetahuan training yang mungkin outdated, atau spekulasi yang belum diverifikasi.

**Syarat untuk label ini:**
- Bisa jadi benar, tapi belum diverifikasi
- Berdasarkan training knowledge dengan potential expiry
- Speculative tanpa strong evidence

**Format penggunaan:**
```
[🔴 UNCERTAIN] Mungkin ada memory leak di ListView — perlu profiling untuk konfirmasi.
[🔴 Training Knowledge, cutoff Aug 2025] Go 1.23 mendukung rangefunc iterators.
[🔴 UNCERTAIN] Behavior ini bisa berbeda di iOS vs Android.
```

**Kapan WAJIB gunakan:**
- Semua klaim tentang library behavior tanpa direct verification
- Semua klaim tentang versi library tanpa cek manifest
- Semua spekulasi tentang root cause tanpa evidence

---

### ⚫ UNKNOWN — Outside Knowledge Boundaries

**Definisi:** Area yang benar-benar di luar batas pengetahuan yang bisa diklaim.

**Syarat untuk label ini:**
- Tidak ada data yang cukup untuk membuat klaim
- API/system/codebase yang tidak diketahui
- Pertanyaan yang membutuhkan akses eksternal yang tidak ada

**Format penggunaan:**
```
[⚫ UNKNOWN] Saya tidak punya informasi tentang internal API perusahaanmu ini.
[⚫ UNKNOWN] Versi library ini belum ada dalam training data saya.
[⚫ UNKNOWN] Saya butuh lihat error log untuk bisa menjawab ini.
```

**Statement yang tepat saat UNKNOWN:**
- "Saya tidak tahu dan saya menyatakannya."
- "Saya butuh [informasi X] sebelum bisa menjawab ini."
- "Ini di luar batas pengetahuan saya — cek [sumber yang tepat]."

---

## Confidence Escalation Protocol

Ketika confidence berubah selama respons:

```
AWAL: [🔴 UNCERTAIN] Kemungkinan masalahnya di connection pool...
      [Melakukan verifikasi — Read log file]
UPGRADE: [🟢 CONFIRMED] Ternyata benar: baris 234 di app.log menunjukkan 
          connection pool exhausted setelah 1000 concurrent requests.
```

```
AWAL: [🟢 CONFIRMED] Function ini ada di lib/utils.dart:45...
      [User mengatakan "tapi itu di branch lama"]
DOWNGRADE: [⚫ UNKNOWN] Saya melihat versi lama. Perlu baca versi terbaru dulu.
```

---

## Integration dengan REALE Framework

```
Pillar 1 (READ)         → Menghasilkan 🟢 CONFIRMED
Pillar 2 (EVIDENCE)     → Menentukan tier berdasarkan evidence quality
Pillar 3 (ASSUME)       → Asumsi selalu minimum 🔴 UNCERTAIN
Pillar 4 (LIMITS)       → Menginformasikan kapan ⚫ UNKNOWN diperlukan
Pillar 5 (ERROR-CHECK)  → Memverifikasi consistency confidence labels
```

---

## Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│              CONFIDENCE QUICK REFERENCE                  │
├──────┬──────────────┬──────────────────────────────────┤
│  Tag │   Label      │ Kapan Digunakan                  │
├──────┼──────────────┼──────────────────────────────────┤
│  🟢  │ CONFIRMED    │ Sudah diverifikasi langsung       │
│  🟡  │ INFERRED     │ Kesimpulan logis dari evidence   │
│  🔴  │ UNCERTAIN    │ Spekulasi / training knowledge   │
│  ⚫  │ UNKNOWN      │ Di luar batas pengetahuan        │
└──────┴──────────────┴──────────────────────────────────┘

ATURAN EMAS: Jika ragu, turunkan satu level.
             🟢 → 🟡 → 🔴 → ⚫
             Selalu lebih baik under-claim daripada over-claim.
```
