# Workflow docx lampiran + referensi arsitektur (proyek IBT)

## Lampiran ringkasan ke Blueprint IBT.docx (python-docx)

Alur yang terbukti: ekstrak semua docx sumber ke txt (`getattr(b.style,'name',None) or 'Normal'` — style bisa None), baca per file, susun ringkasan per tanggal, lalu append dengan 3 script terpisah yang tiap-tiap buka-save docx yang sama (konten besar → pecah; tiap script butuh import sendiri `Cm/Pt/RGBColor`).

### Pitfall style bawaan hilang (berlaku umum)

Dokumen yang dibersihkan bisa kehilangan style `Table Grid` / `List Bullet` / `List Number` → `t.style='Table Grid'` atau `style="List Bullet"` langsung `KeyError`. Probe dulu: `{s.name for s in doc.styles}`. Workaround:
- Border tabel manual via `w:tblBorders` (top/left/bottom/right/insideH/insideV, `w:val=single`, `w:sz=4`).
- Bullet manual: indentasi gantung `left_indent=Cm(0.63)` + `first_line_indent=Cm(-0.63)` + karakter `•`, penomoran eksplisit `f"{i}. "`.

### Deliver via MEDIA: (Hermes desktop)

Nama file ber-spasi atau `%20` bikin tombol download gagal → salin dulu ke nama tanpa spasi (`Blueprint_IBT_2026-09-14.docx`), kirim link MEDIA: ke salinan itu; file asli tetap utuh di folder.

## Referensi arsitektur web IBT

`D:\Metrodata\IBT\maul\IBT-Laravel-React-Inertia.js-\docs\development\AI_DEVELOPMENT_GUIDE.md` — knowledge base arsitektur (tech stack Laravel 11 + React/Inertia + SAP B1 Service Layer, sistem penomoran dokumen, aturan "DI RL TIDAK ADA HARGA", RFQ Excel 22 kolom, siklus 10 modul, approval 3 stage, staging & sinkronisasi SAP, cheat sheet seeder). Baca ini dulu saat kerja implementasi/dev web IBT. Salinan ada di `documentation/development/`.
