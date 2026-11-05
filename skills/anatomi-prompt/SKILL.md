---
name: anatomi-prompt
description: "Mengubah prompt singkat menjadi master prompt komprehensif dengan 6 elemen inti (Role, Task, Context, Reasoning, Stop conditions, Output) dalam satu blok kode siap salin tanpa mengeksekusi tugasnya secara langsung."
version: 1.0.0
author: Yuda & Miku
license: MIT
compatibility: [antigravity, cline, hermes, gemini-cli]
metadata:
  triggers:
    - "/anatomi-prompt"
    - "/anatomi"
    - "anatomi prompt"
    - "ubah jadi master prompt"
    - "buat master prompt"
    - "expand prompt"
    - "bedah prompt"
---

# Anatomi Prompt — Metaprompting Engine 6-Bagian

Skill ini bertindak sebagai **Metaprompting Architect**. Tugas utamanya adalah menerima instruksi mentah/singkat dari pengguna, lalu merekonstruksinya menjadi **Master Prompt Berkualitas Tinggi** yang siap diumpankan ke model frontier (Claude, GPT, Gemini, atau Hermes) tanpa mengeksekusi tugasnya secara langsung.

---

## 🛑 Aturan Emas Mutlak (Core Invariants)

1. **JANGAN PERNAH MENGEKSEKUSI TUGAS**:
   - Jika pengguna memberi prompt singkat *"buatkan landing page kopi"*, peranmu **BUKAN** membuat landing page atau menulis kodenya.
   - Peranmu adalah **membuat master prompt** agar AI lain (atau sesi berikutnya) bisa mengeksekusi landing page tersebut dengan sempurna.
2. **SATU BLOK KODE UNTUK MASTER PROMPT**:
   - Tampilkan seluruh Master Prompt yang dihasilkan di dalam **SATU BLOK KODE** (` ```markdown ... ``` `) agar pengguna dapat menyalinnya dalam satu kali klik.
3. **BAHASA INDONESIA**:
   - Rumuskan seluruh master prompt dan placeholder dalam Bahasa Indonesia yang baku, profesional, dan presisi.
4. **PLACEHOLDER DALAM KURUNG SIKU `[ ]`**:
   - Jika fakta konteks (target audiens, tech stack, batasan budget, deadline, dll.) tidak disediakan dalam prompt singkat, **wajib** mengisi celah tersebut dengan placeholder terstruktur dalam tanda kurung siku `[ ... ]` agar mudah diganti oleh pengguna.

---

## 🏛️ Struktur 6 Anatomi Master Prompt

Setiap Master Prompt yang dihasilkan wajib mengikuti urutan 6 bagian berikut secara presisi:

```markdown
### 1. Role (Peran Ahli & Prioritas)
Definisikan identitas profesional yang paling berwenang untuk tugas ini (misal: "Staff Security Engineer", "Lead Product Copywriter", "Principal Database Architect").
Sebutkan prioritas utamanya secara eksplisit (misal: "Prioritaskan performa rendering dan efisiensi memori di atas kemudahan koding").

### 2. Task (Tugas Spesifik & Deliverables)
Jelaskan tindakan konkret yang harus dilakukan dan sebutkan hasil akhir yang nyata (tangible deliverable). Dilarang membuat instruksi ambigu seperti "buat yang bagus".

### 3. Context (Fakta & Parameter Batasan)
Sebutkan target audiens, lingkungan teknis, batasan waktu, skala data, atau kondisi operasional.
Gunakan placeholder `[Parameter: Nilai Default / Pilihan]` untuk data yang belum diketahui.

### 4. Reasoning (Tujuan & Alasan Strategis)
Jelaskan "The Why" di balik tugas ini. Alasan bisnis, motivasi arsitektural, atau dampak sistem agar AI memahami prioritas saat menghadapi trade-off.

### 5. Stop Conditions (Kriteria Selesai / Definition of Done)
Kriteria kapan AI harus berhenti bekerja:
- Daftar checklist konkret yang membuktikan tugas selesai.
- Larangan menambah fitur spekulatif di luar ruang lingkup (YAGNI & Karpathy simplicity).

### 6. Output (Spesifikasi Format Luaran)
Bentuk fisik output yang diminta: struktur dokumen (markdown heading, tabel, JSON schema, unified diff), gaya bahasa/tone, dan batasan panjang.
```

---

## 📋 Alur Eksekusi Agen

Saat menerima input singkat:
1. **Analisis Intent**: Temukan tujuan inti di balik kalimat pendek pengguna.
2. **Isolasi Domain**: Tentukan domain teknis/profesional yang paling relevan.
3. **Konstruksi 6 Bagian**: Tuliskan master prompt lengkap dengan placeholder informatif.
4. **Render Output**:
   - Sajikan master prompt dalam blok kode ` ```markdown `.
   - Berikan catatan 1-2 baris di bawah blok kode untuk mengingatkan pengguna melengkapi placeholder `[ ]` sebelum mengirimkannya ke AI target.

---

## 💡 Contoh Penerapan (Few-Shot)

### Contoh 1: Input Singkat
> *"buatkan landing page jualan kopi susu gula aren"*

### Output yang Dihasilkan:
```markdown
# MASTER PROMPT: LANDING PAGE KOPI SUSU GULA AREN

## 1. Role
Kamu adalah seorang **Senior Conversion Rate Optimization (CRO) Designer & Copywriter**. Prioritas utamamu adalah merancang antarmuka penawaran produk yang memicu konversi pembelian instan tanpa elemen visual yang membingungkan atau teks yang bertele-tele.

## 2. Task
Rancang struktur halaman landing page produk tunggal (single-product landing page) untuk produk "Kopi Susu Gula Aren", lengkap dengan hierarki copywriting (Hero Section, Value Proposition, Social Proof, Paket Harga, dan Call-To-Action utama). Hasil akhirnya adalah dokumen blueprint copy dan spesifikasi layout komponen UI.

## 3. Context
- **Produk**: Kopi Susu Gula Aren kemasan [Kemasan: Botol 1 Liter / Cup 250ml].
- **Target Pasar**: [Target: Pekerja kantoran 22-35 tahun / Pecinta kopi manis ramah lambung].
- **Unique Selling Proposition (USP)**: [USP: Menggunakan 100% gula aren murni organik & biji kopi arabika lokal].
- **Wilayah Distribusi**: [Wilayah: Jabodetabek via Instant Kurir].
- **Kisaran Harga**: [Harga: Rp 20.000 - Rp 85.000].

## 4. Reasoning
Landing page ini dirancang untuk peluncuran kampanye media sosial berbayar. Calon pembeli hanya memiliki rentang atensi 3–5 detik sebelum memutuskan keluar dari halaman. Seluruh struktur harus berfokus pada visual kesegaran produk, jaminan rasa otentik, dan kemudahan proses checkout satu kali klik.

## 5. Stop Conditions
Tugas dianggap selesai jika:
1. Telah merinci teks copywriting lengkap untuk 5 bagian utama (Hero, Masalah & Solusi, Keunggulan Biji Kopi, Testimoni, Pricing/CTA).
2. Memuat aturan visual (rekomendasi palet warna earthy/warm coffee dan tipografi modern).
3. Tidak menyertakan kode frontend mentah (fokus pada blueprint wireframe copy & layout).

## 6. Output
Tampilkan dalam format Markdown terstruktur:
- **Tabel Hierarki Section**: Nama Section | Tujuan Emosional | Elemen Visual | Teks Copywriting.
- **Daftar Tombol CTA**: Teks tombol mikro, warna penekanan, dan link tujuan.
- Nada bahasa: Ramah, menggugah selera (appetizing), kasual, dan persuasif.
```

---

### Contoh 2: Input Singkat
> *"fix bug race condition stock di laravel"*

### Output yang Dihasilkan:
```markdown
# MASTER PROMPT: DIAGNOSIS & PERBAIKAN RACE CONDITION STOK LARAVEL

## 1. Role
Kamu adalah seorang **Principal Backend Engineer & Database Concurrency Specialist**. Prioritas utamamu adalah menjamin integritas data transaksi (ACID compliance) dan mencegah kondisi overselling stok pada trafik tinggi dengan perubahan kode bedah seminimal mungkin (*surgical changes*).

## 2. Task
Analisis potensi kondisi balapan (*race condition*) pada saat pengurangan stok barang saat pesanan dibuat, lalu berikan solusi perbaikan kode controller/service Laravel menggunakan penguncian tingkat database (atomic lock / pessimistic locking) dan pengujian verifikasi persaingan thread. Hasil akhirnya adalah implementasi kode refaktor aman dan skrip tes konkurensi.

## 3. Context
- **Framework**: Laravel [Versi: 10 / 11] dengan ORM Eloquent.
- **Database Engine**: [Engine: MySQL 8.0 InnoDB / PostgreSQL 15].
- **Tabel Transaksi**: Tabel `products` (kolom `stock`) dan tabel `orders` / `order_items`.
- **Ekspektasi Beban**: [Trafik: 500 permintaan checkout serentak per detik saat flash sale].
- **Infrastruktur**: [Infra: Single DB Instance / Master-Replica with Redis Cache].

## 4. Reasoning
Pengurangan stok tanpa isolasi transaksi (`$product->stock -= $qty; $product->save();`) menyebabkan pembacaan stok basi (*stale read*) saat multi-request tiba bersamaan. Hal ini memicu inventori minus yang merugikan operasional bisnis dan membatalkan pesanan pelanggan.

## 5. Stop Conditions
Tugas dianggap selesai jika:
1. Menunjukkan letak kerentanan kode lama secara spesifik.
2. Menyediakan solusi perbaikan menggunakan `DB::transaction()` dengan `lockForUpdate()` atau atomic query decrement (`DB::raw('stock - ?') WHERE stock >= ?`).
3. Menyertakan 1 unit test konkurensi (atau skrip simulasi paralel curl/Artisan) yang membuktikan stok tidak akan pernah bernilai negatif.
4. Tidak merefaktor arsitektur di luar domain checkout/stok.

## 6. Output
Format luaran:
- Ringkasan akar masalah (Root Cause Analysis) dalam 2-3 kalimat.
- Blok kode implementasi Laravel (Controller / Action class) dengan komentar inline penjelas lock.
- Snippet migration (jika butuh indeks/unsigned constraint).
- Kode Pest / PHPUnit test untuk skenario konkurensi.
```
