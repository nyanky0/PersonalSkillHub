---
name: test-and-verification-suite
description: "Unified Quality Gate & Testing Suite. Combines Red-Green-Refactor TDD, empirical verification evidence gates, LLM benchmark evaluations, and 4-phase systematic debugging."
version: 1.0.0
author: Hermes Agent (Miku) & Senpai
license: MIT
platforms: [windows, linux, macos]
metadata:
  hermes:
    tags: [testing, verification, tdd, eval, debugging, quality-gate, harness]
    related_skills: [test-driven-development, verification-before-completion, evaluating-llms-harness, systematic-debugging]
---

# Test & Verification Master Suite (Unified Quality Gate)

Master standard untuk pengujian perangkat lunak, evaluasi output model, dan verifikasi klaim berbasis bukti (*evidence-based claims*).

---

## 1. The Iron Law of Verification (Pintu Gerbang Utama)

```
NO COMPLETION CLAIMS WITHOUT FRESH VERIFICATION EVIDENCE
```

Dilarang menyatakan fitur selesai, bug diperbaiki, atau tes lulus tanpa bukti eksekusi perintah terminal segar (*fresh verification evidence*).

### The Gate Function
Sebelum menyatakan status apa pun kepada user:
1. **IDENTIFY**: Perintah apa yang membuktikan klaim ini secara objektif? (e.g. `php artisan test`, `npx vitest run`, `dotnet test`).
2. **RUN**: Eksekusi perintah secara penuh (fresh, lengkap).
3. **READ**: Baca seluruh output, cek exit code, dan hitung kegagalan.
4. **VERIFY**: Apakah output mengonfirmasi klaim?
   - Jika **TIDAK**: Nyatakan status riil dengan bukti kegagalan.
   - Jika **YA**: Nyatakan klaim disertai bukti eksekusi.
5. **ONLY THEN**: Sampaikan bahwa pekerjaan selesai.

---

## 2. Red-Green-Refactor Cycle (TDD Flow)

1. **RED**: Tulis unit/integration test minimal yang mencerminkan requirement baru atau mendeteksi kegagalan bug. Jalankan test dan pastikan gagal.
2. **GREEN**: Tulis implementasi kode yang paling minimal (*surgical change*, zero-bloat) sampai test lulus.
3. **REFACTOR**: Rapikan struktur kode tanpa merusak contract dan pastikan semua test tetap hijau.

---

## 3. Systematic Debugging Loop (4-Phase Protocol)

Jika terjadi kegagalan/regression:
1. **Reproduce**: Isolasi test case terkecil yang memicu error secara konsisten.
2. **Isolate**: Bedah root cause (jangan tebak-tebak atau trial-and-error).
3. **Surgical Fix**: Lakukan perbaikan minimal hanya pada akar masalah.
4. **Verify**: Jalankan ulang test suite dan verifikasi tidak ada regression.

---

## 4. LLM & Agent Evaluation Harness (Agentic Eval)

Mengadopsi prinsip dari `awesome-harness-engineering`:
- Tetapkan evaluasi deterministik (assert regex, JSON schema validation, exit code, token usage).
- Evaluasi agen terhadap task benchmark sebelum deploy perubahan besar.
