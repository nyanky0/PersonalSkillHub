# 🧠 PersonalSkillHub — Central Master AI Agent Skills Warehouse

Gudang pusat (*Single Source of Truth / SSOT*) untuk seluruh **Agent Skills** lintas platform AI Coding (Hermes Agent, Cline, Antigravity 2.0, Antigravity IDE, dan Gemini CLI).

Repo ini dirancang dengan prinsip **Zero-AI-Slop**, presisi tinggi, dan efisiensi token maksimal untuk menunjang pengembangan perangkat lunak tingkat enterprise.

---

## 🏛️ Arsitektur Sinkronisasi Lintas Agent

Setiap skill yang ada di repo ini disinkronkan secara atomik ke 4 lokasi lokal:

```
┌────────────────────────────────────────────────────────────────────────┐
│               MASTER REPOSITORY: D:\SkillHub\skills\                   │
├───────────────────┬────────────────────────────────────────────────────┤
│ Target Environment│ Lokasi Lokal di Mesin                              │
├───────────────────┼────────────────────────────────────────────────────┤
│ 1. Hermes Agent   │ E:\HERMES\skills\                                  │
│ 2. Cline / AGY IDE│ C:\Users\yudah\.agents\skills\                     │
│ 3. Gemini CLI     │ C:\Users\yudah\.gemini\config\skills\              │
│ 4. Antigravity CLI│ Otomatis membaca dari .agents\skills\              │
└───────────────────┴────────────────────────────────────────────────────┘
```

---

## 🏆 17 Master Bundled Suites Aktif

Seluruh micro-skills telah dikonsolidasikan ke dalam **17 Master Suites** komprehensif:

1. **`ai-agent-brain`**: Otak utama arsitektur AI (Dual-Layer Engine, Karpathy Discipline, Ruflow Triad).
2. **`ui-antislop-master-suite`**: Standar UI anti-slop, kontras WCAG 4.5:1, Tailwind exact tokens, mobile reflow.
3. **`test-and-verification-suite`**: The Iron Law (*No Completion Claims Without Fresh Verification Evidence*), TDD Red-Green-Refactor, dan 4-phase systematic debugging.
4. **`impeccable`**: Panduan desain UI profesional, 24 perintah desain (`polish`, `audit`, `distill`, `animate`), 60 deterministic rule detector.
5. **`agent-reach`**: Universal internet routing engine (Jina Reader, Twitter/X, GitHub CLI, YouTube yt-dlp, Reddit, RSS) dengan fallback otomatis.
6. **`i-have-adhd`**: Format komunikasi cepat to-the-point berorientasi aksi pertama, penomoran langkah, dan estimasi waktu terukur.
7. **`laravel-fullstack-suite`**: Service Layer, React/Inertia payload budget, dan SAP B1 Service Layer sync.
8. **`sap-b1-suite`**: SAP Business One SDK, DI API / UI API, UDF/UDT metadata, dan SP_TransactionNotification trigger.
9. **`dotnet-csharp-master`**: Modern .NET 8/9 & C# 12, ASP.NET Core, Akka.NET actor systems, SignalR, dan gRPC.
10. **`enterprise-fdd-master`**: Dokumen Functional Design Document (FDD) Soltius standard: flowchart `#4F88BB` dan tabel formal.
11. **`windows-hardware-tuning`**: Optimasi sistem operasi Windows, dev environment APU/iGPU, dan WSL.
12. **`github-master-workflow`**: Otomasi Git & GitHub lifecycle, conventional commits, dan PR review via `gh` CLI.
13. **`security-hardening-suite`**: Audit OWASP Top 10, sanitasi IDOR/BOLA, SQLi, dan pembersihan secret sebelum commit.
14. **`office-docx-master`**: Manipulasi dan pembuatan dokumen Word (.docx) formal secara headless.
15. **`office-pdf-master`**: Parsing, OCR, dan text replacement in-place pada dokumen PDF.
16. **`office-xlsx-master`**: Pembuatan laporan Excel (.xlsx) headless lengkap dengan formula dan conditional formatting.
17. **`prism-suite`**: Analisis kode multi-pass dan adversarial self-correction untuk refactoring arsitektur skala besar.

*Plus pendukung inti:* `ponytail-suite` (surgical refactoring), `caveman-suite` (token efficiency), dan `hermes-agent-suite` (terminal styling & persona).

---

## ⚙️ Skrip Otomasi Sinkronisasi (`scripts/sync_skills.py`)

Gunakan skrip sinkronisasi bawaan untuk menjaga integritas file lintas mesin:

```bash
# 1. Kumpulkan skill baru dari seluruh agent ke Master Hub:
python scripts/sync_skills.py collect

# 2. Sebarkan seluruh skill dari Hub ke Hermes + Cline + Gemini:
python scripts/sync_skills.py pushall

# 3. Perbarui katalog manifest manusia & mesin:
python scripts/sync_skills.py manifest
```

---

## 🛡️ Anti-Slop & Quality Enforcement

Repo ini tunduk pada aturan ketat **Anti-AI-Slop**:
- Tanpa dependensi dummy atau boilerplate fiktif.
- Kode dan instruksi selalu berbasis fakta teknis empiris (*zero-hallucination*).
- Setiap pembaruan wajib lulus gerbang pengujian kualitas sebelum disatukan ke branch utama.
