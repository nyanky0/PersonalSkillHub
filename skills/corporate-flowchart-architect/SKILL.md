---
name: corporate-flowchart-architect
description: Master architectural standard for Soltius Corporate Draw.io & FDD Process Flowcharts. Enforces zero-hallucination, strict integer sequential numbering (1..N), decision node blending, semantic mxGraph shapes, Soltius visual styling (#4F88BB), and 4-layer parity (diagram, narrative, FDD script, code).
version: 1.0.0
author: Hermes Agent (Miku) & Senpai
license: MIT
platforms: [windows, linux, macos]
metadata:
  hermes:
    tags: [drawio, flowchart, fdd, soltius, sap-b1, process-flow, architecture, laravel]
    related_skills: [drawio-skill, flowchart-generation, fdd-generation-workflow, karpathy-guidelines, anti-ai-slop-writing, sap-b1-suite, laravel-fullstack-suite]
---

# Corporate Flowchart Architect (Soltius Corporate Draw.io & FDD Standard)

Standar arsitektur resmi untuk perancangan, pembaruan, dan pemeliharaan diagram alur proses bisnis enterprise (*Flowchart*) berbasis Draw.io XML dan integrasi Functional Design Document (FDD) Soltius / SAP Business One.

---

## 1. Trigger & Auto-Bridge Integration

### A. Auto-Activation Trigger
Skill ini **wajib aktif secara otomatis** setiap kali agen AI mendeteksi permintaan atau konteks yang berkaitan dengan:
- Pembuatan, perbaikan, atau audit diagram alur (`drawio`, `flowchart`, `diagram alur`, `alur proses bisnis`).
- Dokumentasi modul FDD proses bisnis (`pembelian barang`, `penerimaan barang`, `pengembalian barang`, `transfer gudang`, `pembatalan dokumen`).
- Pembacaan atau modifikasi file berekstensi `.drawio` atau file skrip penyusun FDD (`scripts/build_fdd_*.py`).

### B. Auto-Bridged Skills (Orkestrasi Otomatis)
Saat skill ini aktif, agen secara otomatis menyelaraskan dan mematuhi direktif dari kumpulan skills terkait:
1. **`drawio-skill`**: Manipulasi sintaks XML native Draw.io (`<mxGraphModel>`, `<mxCell>`, geometri, vertex, edge).
2. **`flowchart-generation`**: Validasi koordinat geometri, perataan kotak (*alignment*), dan pencegahan tumpang tindih panah (*edge routing*).
3. **`fdd-generation-workflow`**: Injeksi diagram dan teks narasi proses ke dokumen resmi Microsoft Word FDD Soltius.
4. **`karpathy-guidelines`**: Perubahan bedah presisi (*surgical diff*), kesederhanaan implementasi, dan larangan merombak kode/blok yang tidak bersangkutan.
5. **`anti-ai-slop-writing`**: Penyusunan narasi proses menggunakan kalimat aktif teknis, lugas, padat fakta, dan bebas istilah klise generik AI.
6. **`sap-b1-suite` & `laravel-fullstack-suite`**: Pemetaan entitas data riil (Service Layer OData, Integration Hub buffer, UDF/UDT, dan tabel staging database).

---

## 2. Core Architectural Philosophy (Logika Cara Berpikir)

### 1. Zero-Hallucination & Reality Anchor (Audit Form Riil)
* **Aturan Mutlak**: Dilarang keras mencantumkan suatu form, antarmuka web, atau langkah pencatatan fisik ke dalam diagram jika pada aplikasi web (`IBT One`) aslinya tidak terdapat layar atau *field* bersangkutan.
* Selalu verifikasi controller, route, dan view (Blade/React Inertia) sebelum memodelkan suatu langkah sebagai proses sistem add-on.
* Verifikasi fisik lapangan tanpa antarmuka web (misalnya: inspeksi visual di dermaga) harus dimodelkan sebagai instruksi logis, bukan form transaksi web.

### 2. Strict Integer Sequential Indexing (1..N Murni)
* **Anti-Fragmentasi**: Dilarang menggunakan sub-penomoran atau desimal (seperti `1a`, `1b`, `8a`, `8b`, `7.1`).
* Seluruh rangkaian proses wajib menggunakan bilangan bulat murni ($1, 2, 3, \dots, N$).
* Jika terdapat beberapa sub-aktivitas yang berurutan erat pada fase yang sama, gabungkan ke dalam satu nomor langkah (contoh: *No. 8 Lanjut ke Transfer Gudang (PL OUT & PL IN ke Kapal)*).
* **Tujuan**: Memastikan korelasi 1-banding-1 yang sempurna saat pengguna atau auditor membaca nomor node di diagram visual dan mencocokkannya ke teks penjelas di bawahnya.

### 3. Decision Node Blending (Peleburan Logika Keputusan)
* Simbol *Decision* (belah ketupat / rhombus) di diagram visual tetap digambar secara eksplisit untuk memperlihatkan logika percabangan.
* Namun pada narasi teks penjelas, logika *decision* tersebut **wajib dilebur** ke dalam nomor langkah yang memicunya (atau langkah penentunya), merinci cabang positif (*Approved/Reguler/Selesai*) dan cabang negatif (*Rejected/Revisi/Direct PO*).

### 4. 4-Layer Surgical Parity (Konsistensi Lintas Dokumen)
Setiap ada perubahan kebutuhan atau arsitektur bisnis, sinkronisasi wajib dieksekusi serentak ke 4 layer:
1. **File XML Draw.io** (`addon flowchart/*.drawio` dan `note/drawio/*.drawio`).
2. **File Narasi Teks** (`addon flowchart/penjelasan_flow/0x_*.txt`).
3. **Script Generator FDD** (`scripts/build_fdd_*.py`).
4. **Source Code Aplikasi** (Controller, Service, Route, Mailable).

---

## 3. Shape Taxonomy & Semantic Meaning

Penggunaan bentuk shape pada Draw.io wajib mengikuti kaidah semantik baku:

| Komponen | Bentuk Shape | mxGraph Style Baku | Makna & Penggunaan |
| :--- | :--- | :--- | :--- |
| **Terminal** | Kapsul / Oval Bulat | `rounded=1;arcSize=50;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#000000;strokeWidth=1.5;fontColor=#000000;fontSize=11;fontStyle=1;align=center;shadow=0;` | Titik awal (*Mulai*) atau titik akhir (*Selesai*) proses. |
| **Input / Data Manual** | Jajaran Genjang (*Parallelogram*) | `shape=parallelogram;perimeter=parallelogramPerimeter;whiteSpace=wrap;html=1;fixedSize=1;strokeWidth=1.5;align=center;fillColor=#FFFFFF;strokeColor=#000000;fontColor=#000000;fontSize=10;spacingLeft=8;spacingRight=8;shadow=0;` | Input data oleh user, inisiasi transaksi manual, unggah file, atau pemilihan dari katalog. |
| **Proses Sistem** | Persegi Panjang (*Rectangle*) | `rounded=0;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#000000;strokeWidth=1.5;fontColor=#000000;fontSize=10;align=center;spacingLeft=8;spacingRight=8;shadow=0;` | Pemrosesan backend, submit formulir, validasi data, generate dokumen otomatis, atau transmisi payload API. |
| **Decision** | Belah Ketupat (*Rhombus*) | `rhombus;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#000000;strokeWidth=1.5;fontColor=#000000;fontSize=9;fontStyle=1;align=center;spacingLeft=4;spacingRight=4;shadow=0;` | Pengecekan kondisi, status persetujuan (*Approved?*), jenis dokumen, atau rute tujuan akhir barang. |
| **Dokumen / File** | Bentuk Dokumen (*Document*) | `shape=document;whiteSpace=wrap;html=1;boundedLbl=1;fillColor=#FFFFFF;strokeColor=#000000;strokeWidth=1.5;fontColor=#000000;fontSize=10;align=center;spacingLeft=8;spacingRight=8;shadow=0;` | Dokumen fisik, berkas ekspor/impor Excel RFQ, formulir cetak PDF resmi, atau berkas tanda terima. |
| **System Badge** | Kotak Mini Rounded | `rounded=1;arcSize=30;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#000000;strokeWidth=1;fontColor=#000000;fontSize=8;fontStyle=1;align=center;shadow=0;` | Label sistem penanggung jawab yang diposisikan persis di atas pojok kiri node (misal: `ADD-ON`, `HUB`, `SAP B1`). |

---

## 4. Visual Design & Soltius Corporate Palette

Semua diagram wajib menggunakan palet warna korporat Soltius yang bersih dan profesional:

```
┌────────────────────────────────────────────────────────────────────────┐
│  HEADER BANNER: #4F88BB (Soltius Blue) | Text: #FFFFFF Bold 14px       │
├─────────┬──────────────────────────────────────────────────────────────┤
│ SIDEBAR │                                                              │
│ #4F88BB │   SWIMLANE WORK AREA: Background #FFFFFF                      │
│ Text    │                                                              │
│ #FFFFFF │   • Node Fill: #FFFFFF (Putih Bersih)                        │
│ 11px    │   • Node Stroke: #000000 (Hitam Pekat), strokeWidth=1.5      │
│ Bold    │   • Connectors: #000000 Orthogonal, strokeWidth=1.5          │
│ Width:  │   • Decision Labels: Text tegak 9px (Yes, No, Kapal, Gudang) │
│ 90px    │   • Badge: #FFFFFF, border 1px, font 8px Bold                │
│         │                                                              │
└─────────┴──────────────────────────────────────────────────────────────┘
```

### Konfigurasi Teknis XML:
1. **Header Banner**:
   `fillColor=#4F88BB;strokeColor=#000000;strokeWidth=1.5;fontColor=#FFFFFF;fontSize=14;fontStyle=1;align=left;spacingLeft=16;`
2. **Swimlane Sidebar**:
   `fillColor=#4F88BB;strokeColor=#000000;strokeWidth=1.5;fontColor=#FFFFFF;fontSize=11;fontStyle=1;align=center;`
3. **Konektor Ortogonal (*Edge Style*)**:
   `edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#000000;strokeWidth=1.5;endArrow=classic;endFill=1;`
4. **Tipografi Baku**:
   - Header: 14px Bold
   - Swimlane Title: 11px Bold
   - Nama Node / Nomor: 10px Bold (`<b>1. Judul Langkah</b>`)
   - Detail Keterangan Node: 8px Regular (`<span style="font-size: 8px;">(...)</span>`)
   - Decision Diamond: 9px Bold
   - System Badge: 8px Bold

---

## 5. Standard Operating Procedure (SOP) Eksekusi

Saat ditugaskan membuat atau merevisi flowchart:

1. **Tahap 1: Verifikasi Lapangan (*Codebase Audit*)**
   - Periksa tabel database, model Eloquent, controller, route web/api, dan view terkait.
   - Pastikan setiap proses yang digambar memang memiliki basis kode nyata.
2. **Tahap 2: Formulasi Rangkaian Teks (1..N)**
   - Buat urutan angka bulat dari 1 hingga N.
   - Peleburan *decision branch* langsung dituliskan di bawah nomor pemantiknya.
3. **Tahap 3: Konstruksi Visual Draw.io XML**
   - Susun baris aliran modular (Row 1 kiri-ke-kanan, Row 2 kanan-ke-kiri / kiri-ke-kanan, Row 3 integrasi SAP).
   - Pastikan badge sistem (`ADD-ON`, `HUB`, `SAP B1`) tersemat pada tiap node operasional.
4. **Tahap 4: Sinkronisasi Multi-Direktori**
   - Simpan file `.drawio` dan teks deskripsi ke seluruh direktori aktif:
     - `D:\Metrodata\IBT\addon flowchart\`
     - `D:\Metrodata\IBT\note\drawio\`
     - `D:\Metrodata\IBT\addon flowchart\penjelasan_flow\`
   - Update skrip FDD Word (`scripts/build_fdd_*.py`) agar deskripsi bab FDD selalu sinkron dengan kondisi diagram terkini.
