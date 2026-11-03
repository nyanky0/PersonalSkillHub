---
name: enterprise-fdd-master
description: "Unified Master Suite for engineering enterprise Functional Design Documents (FDD) for SAP Business One & Web Add-on integrations. Consolidates fdd-generation-workflow, sap-b1-fdd-author, concise-fdd-writing, and validation-trigger-analyzer with zero-hallucination, 4-tier parity, Soltius flowchart standards (#4F88BB), Black Table styling, validation code taxonomy, and Bab 4 UI patent standard (Desktop & Mobile pairing, ruler 0.63cm/1.27cm, bold/italic captions)."
version: 3.0.0
author: Hermes Agent & Antigravity
metadata:
  hermes:
    tags: [fdd, documentation, sap-b1, laravel, enterprise, flowchart, mockups, validation, black-table, concise-writing, consolidated-all-in-one]
    consolidates: [fdd-generation-workflow, sap-b1-fdd-author, sap-b1-validation-trigger-analyzer, concise-fdd-writing]
    related_skills: [corporate-flowchart-architect, drawio-skill, office-docx-master, office-xlsx-master, simple-english]
---

# Enterprise FDD Master Playbook (Unified Single Source of Truth)

## 1. Overview, Core Philosophies & Orchestration Map

**Functional Design Document (FDD)** kelas enterprise bukanlah dokumen formalitas atau proposal teoretis, melainkan **Kontrak Rekayasa Fungsional (Functional Engineering Contract)** yang mengikat antara pemangku kepentingan bisnis, tim operasional lapangan, konsultan SAP, dan pengembang perangkat lunak.

Skill ini merupakan **Master Konsolidasi Tunggal (All-in-One Single Source of Truth)** yang menggabungkan seluruh standar pembuatan FDD dari hulu ke hilir:
- Standar Diagram Alir Proses Bisnis Soltius Corporate Blue (`#4F88BB`).
- Arsitektur Basis Data "Black Table Style" (Bab 3).
- Taksonomi Validasi Berbasis Kode Unik (`VAL-XXX-NNN`) & Matriks Excel 10-Kolom.
- **Standar Paten Bab 4 (Design User Interface)**: Pasangan Desktop & Mobile wireframe, posisi ruler bullet (0,63 cm / 1,27 cm), dan captioning baku.
- **Gaya Penulisan Ultra-Singkat & Anti-AI Slop (ASD-STE100 / simple-english)**: Bahasa lugas, to-the-point, maksimal 20 kata per instruksi, kondisi sebelum perintah, mempertahankan istilah asli SAP B1 & UI bahasa Inggris, mudah dipahami anak-anak.

### 5 Pilar Rekayasa FDD Enterprise:
1. **Reality-First & Zero-Hallucination**: Sumber kebenaran mutlak (*Single Source of Truth*) adalah kenyataan kode program (*codebase*) atau spesifikasi bisnis yang telah diverifikasi secara fisik. Dilarang mengarang form, tombol, endpoint, atau status fiktif.
2. **Dekomposisi Bertahap (Iterative Surgical Chunking)**: Pembuatan FDD dilakukan secara modular dalam 5 fase berurutan: Flowchart $\rightarrow$ Backend Reality Check $\rightarrow$ UI Wireframing $\rightarrow$ Data Structure Dictionaries $\rightarrow$ Validation Matrix.
3. **Kepekaan Konteks Lapangan & Industri (Domain Realism)**: Wajib mengakomodasi batasan fisik industri riil (misal maritim: regulasi *ISM Code Price Blindness*, batas sounding tangki bunker ROB, rotasi pelabuhan tanpa batas SLA 30 hari retur, izin duplikasi baris item untuk alokasi mesin yang berbeda).
4. **Pemisahan Domain yang Tegas (Separation of Concerns)**: Menjaga kemurnian dokumen fungsional dengan membuang "sampah teknis" (*technical slop*): kode galat HTTP mentah (403, 422, 500) dan pengulangan panjang karakter kolom database (`varchar 30`) dibersihkan dari narasi bisnis.
5. **Paritas 4-Lapisan (The 4-Tier Traceability Parity)**:
   $$\text{Diagram Alir (Bab 2)} \longleftrightarrow \text{Kamus Data (Bab 3)} \longleftrightarrow \text{Tampilan Layar (Bab 4)} \longleftrightarrow \text{Kode Controller Ril}$$

---

## 2. Source Code Scanning & Orchestration Workflow

Sebelum mulai menulis dokumen, lakukan identifikasi tipe add-on dari codebase proyek:

1. **Jalur Web Add-on (Laravel + React/Inertia + SAP B1 Service Layer)**:
   - Identifikasi controllers, `SapB1Service`, `buildDocumentPayload`, endpoint `/b1s/v2/`.
   - Analisis model database lokal (`transactions`, `lines`, `approval_stages`, `equipment_catalogs`).
   - Fokuskan Bab 3 pada tabel lokal Web Add-on (menghilangkan tabel internal SAP B1 agar relevan).
2. **Jalur Native SAP B1 Add-on (C# UI API / DI API / HANA DDL)**:
   - Identifikasi `UserTablesMD`, `UserFieldsMD`, event handler (`ItemEvent`, `FormDataEvent`).
   - Ekstrak skema tabel UDT (`@SOL_*`), kolom UDF, dan UDO (Services: Find, Log, Manage Series).
3. **Pemetaan Modul Transaksi**:
   - Petakan setiap siklus: Requisition List (RL) $\rightarrow$ Quotation (PQ) $\rightarrow$ Comparison (PQC) $\rightarrow$ Purchase Order (PO) $\rightarrow$ Goods Receipt PO (GRPO) $\rightarrow$ Packing List $\rightarrow$ Goods Return (GRE).

---

## 3. Kerangka Baku Dokumen FDD (5 Bab Standar Soltius)

Dokumen FDD standar Soltius wajib mematuhi anatomi berikut:

```text
COVER PAGE (Judul Dokumen, Logo Klien, Dikembangkan oleh PT Soltius Indonesia, Tahun)
DISCLAIMER & CONFIDENTIALITY STATEMENT (Pernyataan Kerahasiaan & Batasan Tanggung Jawab)
DAFTAR ISI (Otomatis / Terstruktur)

1. PENDAHULUAN
   1.1 Latar Belakang (Latar belakang operasional dan inisiatif digitalisasi)
   1.2 Tujuan Development (Sasaran terukur yang ingin dicapai)
   1.3 Ruang Lingkup (Batasan modul dan fungsionalitas yang dikembangkan)

2. PENJELASAN PROSES DEVELOPMENT & INTEGRASI
   2.1 Business Process (Diagram Alir & Narasi Rinci Tiap Siklus Transaksi)
       2.1.1 s.d. 2.1.N: Siklus Transaksi 1 s.d. N (Lengkap dengan swimlane peran)
   2.2 Urutan Development (Tahapan pengerjaan pengembang)
   2.3 Mekanisme Layanan Pendukung (Layanan Email Vendor, Engine Cetak Modular)

3. DESIGN STRUKTUR DATA
   3.1 Struktur Data Web Add-On / UDT Overview (Ringkasan Entitas Basis Data)
   3.2 Struktur Field Tabel Database (Kamus Data Field Detail - Black Table Style)
   3.3 Validasi Fungsional & Aturan Bisnis (Aturan Bisnis Terstruktur per Modul)

4. DESIGN USER INTERFACE
   4.1 Standar Layout dan Navigasi (Sistem grid, tema, sidebar, breadcrumb)
   4.2 s.d. 4.N: Halaman Antarmuka 1 s.d. N (Standar Paten Pasangan Desktop & Mobile)
   4.Y: Standar Formulir Cetak Dokumen Modular (Print Engine Layout)

5. APPROVAL
   Lembar Pengesahan Tanda Tangan Stakeholder (Nama, Jabatan, Tanggal, Tanda Tangan)
```

### Template Cover, Disclaimer & Approval Matrix (Bab 5)
```markdown
FUNCTIONAL DESIGN DOCUMENTATION (FDD)
{NAMA APLIKASI / ADD-ON / MODUL}
DEVELOPED BY PT SOLTIUS INDONESIA FOR {NAMA KLIEN} - {TAHUN}
```
```markdown
Disclaimer and Confidentiality Statement
This document is a DRAFT document. PT Soltius Indonesia and {CLIENT} representatives accept that this document reflects the mutually agreed scope and approach. This document has been submitted on a confidential basis solely for the purpose of supplying information to {CLIENT} and is not for use by any other persons. Whilst every care has been taken with the preparation of this document, PT Soltius Indonesia accepts no responsibility for any errors or omissions within this document, and readers are advised to obtain further advice regarding specific matters within this document before acting on them.
```
```markdown
| Role / Stakeholder | Nama Pejabat | Jabatan | Tanggal | Tanda Tangan |
|---|---|---|---|---|
| Project Manager (Soltius) | {Nama PM Soltius} | Project Manager | ... | ... |
| Lead Consultant (Soltius) | {Nama Lead} | Senior Functional Consultant | ... | ... |
| Project Manager (Client) | {Nama PM Klien} | Project Manager | ... | ... |
| Business Owner / Sponsor | {Nama Sponsor} | Division Head / Director | ... | ... |
```

---

## 4. Standar Bab 2: Diagram Alir Soltius Corporate Blue (`#4F88BB`)

- **Format Resmi Client Deliverable (Draw.io Native)**:
  - Header Banner & Swimlane Sidebar: `#4F88BB` (Soltius Corporate Blue).
  - Penomoran bulat sequential integer ($1, 2, 3, \dots, N$) tanpa format sub-indeks pecah seperti 1a/1b.
  - Decision node blending: Kondisi keputusan (rhombus) dilebur ke aksi proses demi efisiensi visual.
  - Berkas disimpan dalam format XML `.drawio` dan diekspor ke PNG resolusi tinggi.
- **Narasi Rincian Langkah**: Setiap langkah proses wajib memuat:
  - PIC (Penanggung Jawab Aksi).
  - Dokumen Pendukung (Lampiran fisik / file).
  - Implikasi Jurnal Akuntansi / SAP B1 Posting (bila transaksi menyentuh persediaan/GL).

---

## 5. Standar Bab 3: Desain Struktur Data ("Black Table Style")

Seluruh tabel Bab 3 (Subbab 3.1 & 3.2) wajib diformat dengan **Black Table Style**:
- **Border**: Full black box tebal pada tepi luar (`w:val="single" w:sz="6" w:color="000000"`), serta garis pembatas horizontal & vertikal dalam (`w:sz="4" w:color="000000"`).
- **Tipografi & Spasi Standar**: Font **Cambria**, ukuran **11 pt**, line spacing **1.0** (single), spacing before = 0 pt, after = 0 pt.
- **Header Row**: Background hitam pekat (`#000000`), teks warna putih tebal (*bold* `#FFFFFF`), font Cambria 11 pt, rata tengah (*center*).
- **Data Rows**: Background putih bersih (`#FFFFFF`), teks warna hitam non-bold (`#000000`), font Cambria 11 pt, line & paragraph spacing 1.0, rata kiri (kolom Nomor rata tengah).

### Format Kolom Tabel:
- **Tabel 3.1 (Ikhtisar Entitas)**: `No. | Nama Tabel | Deskripsi Fungsi | Tipe Data (Master/Transaksi)`
- **Tabel 3.2 (Kamus Field Detail)**: `No. | Nama Field | Tipe Data & Panjang | Keterangan & Aturan Bisnis`
  *(Untuk Native SAP UDT: `No. | Field ID | Deskripsi | Tipe Data | Sub-Type | Ukuran | Valid Values / Notes`)*.

---

## 6. Standar Bab 3.3: Taksonomi Validasi & Kamus Error (`VAL-XXX-NNN`)

1. **Format Kode Validasi**:
   $$\text{\textbf{VAL-[KODE\_MODUL]-[NOMOR\_URUT]}}$$
   Contoh: `VAL-AUTH-001`, `VAL-RL-003`, `VAL-PO-005`, `VAL-GRPO-002`, `VAL-FILE-001`.
2. **Matriks Kamus Validasi Excel (10 Kolom Wajib)**:
   `No | Modul | Dokumen | Kode Validasi | Output Saat Terkena Validasi | Validasi Fungsi Untuk Apa | Biar Tidak Terkena Validasi Harus Apa | Lapisan Validasi | Status di Web App | Skenario Pengujian (QA Test Case)`.
3. **Dua Varian Dokumen Teks Validasi**:
   - Versi Ber-Kode (`VALIDASI_FDD_SIAP_PAKAI.txt`): Untuk developer & QA testing.
   - Versi Tanpa Kode (`VALIDASI_FDD_TANPA_KODE.txt`): Narasi aturan bisnis bersih untuk klien eksekutif.

---

## 7. STANDAR PATEN BAB 4: Design User Interface (SAP Soltius Standard)

> [!IMPORTANT]
> **STANDAR PATEN BAB 4 FDD SOLTIUS**: Bagian ini adalah standar paten tunggal resmi dan permanen. Seluruh format mockup yang bertentangan dinyatakan gugur (*superseded*).

```text
4. DESIGN USER INTERFACE                    <-- Style: SOL-Level 1 (Cambria 12pt Bold)
Bagian ini menjelaskan rancangan antarmuka...  <-- Style: SOL-Par1 (Cambria 11pt, 1-2 kalimat)

4.1. Halaman Login dan Pemilihan Cabang      <-- Style: SOL-Level 2 (Cambria 12pt Bold)
Halaman awal untuk autentikasi pengguna...   <-- Style: SOL-Par1 (Cambria 11pt, 1 kalimat)
• Username & Password : Input identitas akun.<-- Style: SOL-List (Indents: left=1.27cm/720 dxa, hanging=0.63cm/360 dxa)
• Branch / Vessel : Pilih unit kantor/kapal. <-- Style: SOL-List (Prefix bold + colon)
• Login Button : Tombol eksekusi masuk.      <-- Style: SOL-List (DILARANG indent tengah 6cm!)

[ Gambar Mockup Desktop View ]               <-- Style: SOL-Free (Centered, Width: 4.59" - 6.20")
Gambar 4.1.1. Halaman Login Desktop View     <-- Style: SOL-Free (Centered, 10pt Cambria: 'Gambar 4.1.1. ' BOLD, 'Judul...' ITALIC NON-BOLD)

[ Gambar Mockup Mobile View ]                <-- Style: SOL-Free (Centered, Width: 2.05")
Gambar 4.1.2. Halaman Login Mobile View      <-- Style: SOL-Free (Centered, 10pt Cambria: 'Gambar 4.1.2. ' BOLD, 'Judul...' ITALIC NON-BOLD)
```

### Aturan Wajib Bab 4:
1. **Dual-View Mockup Pairing**: Setiap sub-bab antarmuka (4.1 s.d. 4.N) **wajib menyajikan pasangan mockup berurutan**:
   - **Desktop View**: Rata tengah (*Center*), lebar proporsional A4 (`width: 4.59"` s.d. `6.20"`), style `SOL-Free`.
   - **Mobile View**: Wireframe monokrom bersih tepat di bawah Desktop View (`width: 2.05"`), rata tengah (*Center*), style `SOL-Free`.
   - Mockup bersih (latar `#FFFFFF`, border `#1A202C`, isian `#F7FAFC`), tanpa frame laptop/HP dan tanpa logo dekoratif palsu.
2. **Aturan Captioning Gambar Resmi (Bold Prefix + Italic Title)**:
   - Font: **Cambria 10 pt**, spasi 1.0, posisi *Center*, warna hitam murni (`#000000`), style `SOL-Free`.
   - **Hanya teks nomor gambar yang dicetak TEBAL (BOLD)**:
     - **`Gambar 4.x.1. `** / **`Gambar 4.x.2. `** $\rightarrow$ Bold, tegak (*non-italic*).
   - **Teks judul gambar di belakangnya dicetak MIRING (ITALIC) & TIDAK TEBAL (NON-BOLD)**:
     - *`[Nama Layar] Desktop View`* / *`[Nama Layar] Mobile View`* $\rightarrow$ Italic, *non-bold*.
   - Contoh Baku:
     - **`Gambar 4.1.1. `** *`Halaman Login dan Pemilihan Cabang Desktop View`*
     - **`Gambar 4.1.2. `** *`Halaman Login dan Pemilihan Cabang Mobile View`*
3. **Posisi Ruler Bullet List (`SOL-List`)**:
   - Dilarang keras memakai indent tengah bawaan template Word (`3478 dxa` / 6,13 cm).
   - **Terkunci permanen pada posisi ruler**:
     - **Bullet (`•`)**: Menggantung di **0,63 cm** (`w:hanging="360"` / `0.25"`).
     - **Teks Awal & Wrap Baris Kedua**: Rata kiri di **1,27 cm** (`w:ind w:left="720"` / `0.5"`).
   - Wajib diatur pada XML paragraf `<w:pPr><w:ind w:left="720" w:hanging="360"/></w:pPr>` serta pada level penomoran `abstractNum` (Level 0).

---

## 8. Gaya Bahasa & Penulisan Anti-AI Slop (Singkat, Padat & Anak Paham)

1. **Ultra-Singkat, Padat & To The Point (Cukup Beberapa Kata)**:
   - Format standar perincian elemen form / field:
     ```text
     [Nama Komponen / Field] : [Fungsi Inti 3-7 kata].
     ```
   - Cukup 3 sampai 7 kata per fungsi jika esensinya sudah jelas! Jangan membuat kalimat majemuk bertingkat.
2. **Eliminasi Basa-Basi Pembuka (No Preamble Slop)**:
   - Hapus kalimat pembuka birokratis (*“Bagian ini menjelaskan secara mendalam mengenai rancangan komprehensif...”*).
   - Ganti dengan 1 kalimat pengantar yang lugas dan gamblang (*“Formulir permohonan pengadaan barang dari kru kapal atau staf kantor.”*).
3. **Terminologi Asli SAP B1 & UI (No Forced Translation)**:
   - Jika istilah modul, menu, tombol, atau field lebih ringkas dan standar dalam bahasa Inggris (ekosistem SAP Business One), **BIARKAN DALAM BAHASA INGGRIS**:
     - `Branch`, `Item Code`, `Qty`, `UoM`, `Warehouse`, `Cost Center`, `Draft`, `Submit Approval`, `Header`, `Item Lines`.
     - `Requisition List (RL)`, `Price Quotation (PQ)`, `Quotation Comparison (PQC)`, `Purchase Order (PO)`, `Goods Receipt PO (GRPO)`, `Goods Return (GRE)`, `Packing List IN / OUT`.
     - Status: `Draft`, `Pending Approval`, `Approved`, `Rejected`, `Closed`.
4. **Bersihkan Kata Klise AI Slop**:
   - Dilarang kata-kata: *komprehensif, holistik, sinergi, berkesinambungan, mutakhir, terpadu yang seamless, krusial, esensial, optimalisasi yang signifikan, memberdayakan*.
   - Hapus kode galat HTTP mentah (403, 422) dan tipe data skema (`varchar 30`) dari narasi bisnis.

### Matriks Perbandingan Penulisan:
| Modul / Layar | Penulisan Lama (AI Slop & Bertele-tele) | Penulisan Baru (Singkat, Padat & Anak Paham) |
|---|---|---|
| **Dashboard** | *Panel antrean persetujuan berfungsi memfasilitasi peninjauan komprehensif dokumen pengadaan yang menunggu otorisasi pejabat terkait.* | **Approval Inbox Panel** : Daftar antrean dokumen yang menunggu persetujuan pimpinan. |
| **Request List (RL)** | *Bagian baris daftar item memuat spesifikasi rincian suku cadang mencakup kode inventaris barang, nama deskripsi barang, jumlah kuantitas, satuan pengukuran, lokasi penyimpanan gudang, dan alokasi pusat biaya operasional.* | **Item Lines Grid** : Rincian Item Code, Deskripsi, Qty, UoM, Warehouse, dan Cost Center. |
| **Katalog Sparepart** | *Bilah ringkasan item terpilih secara terpadu menampilkan akumulasi total unit barang yang dipilih dan tombol navigasi untuk menginisiasi dokumen permohonan belanja baru.* | **Floating Cart Summary** : Total item terpilih dan tombol langsung 'Buat Dokumen RL'. |
| **PO ke SAP B1** | *Mekanisme sinkronisasi latar belakang menjalankan transmisi data pemesanan secara seketika menuju endpoint Service Layer SAP Business One untuk pembuatan dokumen purchase order resmi.* | **Status SAP B1** : Indikator sinkronisasi otomatis pesanan ke SAP Business One. |
| **Approval Stages** | *Formulir konfigurasi hierarki tahapan persetujuan multi-tier dan penetapan batas limit nominal wewenang biaya per tingkatan jabatan struktural.* | **Batas Nominal Anggaran** : Syarat nilai belanja yang mewajibkan persetujuan Direktur (misal: > Rp 50 juta). |

---

## 9. Python Automation Recipes (Generator Helpers)

### A. Generator Bab 4 Standar Paten (Soltius Dual-View Pairing + Ruler + Caption)
```python
import os
import docx
from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

def fix_numbering_indents(doc):
    """Kunci abstractNum level 0 agar bullet tidak loncat ke 6 cm"""
    try:
        num_part = doc.part.numbering_part
        for ab in num_part._element.findall(qn("w:abstractNum")):
            if ab.get(qn("w:abstractNumId")) == "24":
                for lvl in ab.findall(qn("w:lvl")):
                    if lvl.get(qn("w:ilvl")) == "0":
                        pPr = lvl.find(qn("w:pPr"))
                        if pPr is not None:
                            ind = pPr.find(qn("w:ind"))
                            if ind is not None:
                                ind.set(qn("w:left"), "720")
                                ind.set(qn("w:hanging"), "360")
    except Exception as e:
        pass

def add_bab4_screen(doc, sec_num, title, intro, bullets, desktop_img, mobile_img, desktop_w=6.20, mobile_w=2.05):
    # Heading 2
    doc.add_paragraph(title, style="SOL-Level 2")
    # Intro
    doc.add_paragraph(intro, style="SOL-Par1")
    # Bullets (Locked Ruler Indent: left=1.27cm, hanging=0.63cm)
    for prefix, desc in bullets:
        p = doc.add_paragraph(style="SOL-List")
        pPr = p._element.get_or_add_pPr()
        ind = pPr.find(qn("w:ind"))
        if ind is None:
            ind = OxmlElement("w:ind")
            pPr.append(ind)
        ind.set(qn("w:left"), "720")
        ind.set(qn("w:hanging"), "360")
        
        r_b = p.add_run(prefix + " : ")
        r_b.bold = True
        r_b.font.name = "Cambria"
        r_d = p.add_run(desc)
        r_d.bold = False
        r_d.font.name = "Cambria"
    
    # Desktop Image & Caption
    p_di = doc.add_paragraph(style="SOL-Free")
    p_di.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_di.add_run().add_picture(desktop_img, width=Inches(desktop_w))
    
    p_dc = doc.add_paragraph(style="SOL-Free")
    p_dc.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_dn = p_dc.add_run(f"Gambar {sec_num}.1. ")
    r_dn.bold = True
    r_dn.font.name = "Cambria"
    r_dn.font.size = Pt(10)
    r_dt = p_dc.add_run(f"{title} Desktop View")
    r_dt.italic = True
    r_dt.font.name = "Cambria"
    r_dt.font.size = Pt(10)

    # Mobile Image & Caption
    p_mi = doc.add_paragraph(style="SOL-Free")
    p_mi.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_mi.add_run().add_picture(mobile_img, width=Inches(mobile_w))
    
    p_mc = doc.add_paragraph(style="SOL-Free")
    p_mc.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_mn = p_mc.add_run(f"Gambar {sec_num}.2. ")
    r_mn.bold = True
    r_mn.font.name = "Cambria"
    r_mn.font.size = Pt(10)
    r_mt = p_mc.add_run(f"{title} Mobile View")
    r_mt.italic = True
    r_mt.font.name = "Cambria"
    r_mt.font.size = Pt(10)
    
    # Spacing
    doc.add_paragraph(style="SOL-Free")
```

### B. Styling Black Table Bab 3
```python
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls

def apply_black_table_style(table):
    tblPr = table._tbl.tblPr
    borders = parse_xml(
        f'<w:tblBorders {nsdecls("w")}>'
        '<w:top w:val="single" w:sz="6" w:space="0" w:color="000000"/>'
        '<w:bottom w:val="single" w:sz="6" w:space="0" w:color="000000"/>'
        '<w:left w:val="single" w:sz="6" w:space="0" w:color="000000"/>'
        '<w:right w:val="single" w:sz="6" w:space="0" w:color="000000"/>'
        '<w:insideH w:val="single" w:sz="4" w:space="0" w:color="000000"/>'
        '<w:insideV w:val="single" w:sz="4" w:space="0" w:color="000000"/>'
        '</w:tblBorders>'
    )
    tblPr.append(borders)
    for cell in table.rows[0].cells:
        tcPr = cell._tc.get_or_add_tcPr()
        tcPr.append(parse_xml(f'<w:shd {nsdecls("w")} w:fill="000000"/>'))
```

---

## 10. Quality Gates & Checklist Verifikasi Mandiri (Before Delivery)

Sebelum dokumen diserahkan kepada klien atau disimpan sebagai deliverable resmi:
- [ ] **Cover, Disclaimer, TOC & Approval Matrix Lengkap**: Tidak ada bab wajib yang terlewat.
- [ ] **Paritas 4-Lapisan Terverifikasi**: Alur proses di Bab 2 konsisten dengan tabel di Bab 3 dan layar di Bab 4.
- [ ] **Bab 4 Paten Soltius Terpenuhi**:
  - [ ] Setiap layar menyajikan pasangan Desktop View dan Mobile View berurutan.
  - [ ] Caption berformat: **`Gambar 4.x.y. `** (Bold) dilanjutkan *`[Judul] View`* (Italic Non-bold), Cambria 10 pt Center.
  - [ ] Posisi ruler bullet terkunci rapi: bullet di 0,63 cm dan teks wrap di 1,27 cm (tidak bergeser ke tengah).
- [ ] **Gaya Bahasa Bersih & Mudah Dipahami**:
  - [ ] Format list: `Prefix Bold : Fungsi 3-7 kata`.
  - [ ] Anak-anak atau konsultan non-teknis dapat langsung paham fungsi tiap modul.
  - [ ] Istilah asli SAP B1 & UI bahasa Inggris dipertahankan tanpa terjemahan paksa.
  - [ ] Seluruh kata AI slop (*komprehensif, holistik, sinergi, mutakhir, optimalisasi*) sudah bersih 100%.
- [ ] **Tabel Bab 3 Berformat Black Table Style**: Border hitam pekat, header hitam berteks putih tebal, baris data putih font Cambria 11 pt spasi 1.0.
- [ ] **Taksonomi Kode Validasi Unik**: Tersedia kode unik `VAL-XXX-NNN` dan file rekapitulasi Excel 10 kolom pendamping.
