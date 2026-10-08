---
name: sap-b1-fdd-author
description: Use when user asks to create an FDD (Functional Design Documentation) for a SAP Business One add-on directly from source code — triggers: "buat FDD", "generate FDD", "FDD dari source code", "functional design documentation", "dokumentasi add-on". Orchestrates the five SAP B1 documentation skills (sap-b1-udt-udf-schema-extractor, sap-b1-business-logic-translator, sap-b1-validation-trigger-analyzer, sap-b1-integration-mapper, sap-b1-visual-logic-mapper) and assembles output into the PT Soltius Indonesia FDD template: cover, disclaimer, DAFTAR ISI, Pendahuluan, Business Process + Mermaid diagram + Journal entry, Design Struktur Data (Tables/Fields/UDT/UDF/UDO + Validasi), Design User Interface, Approval.
---

# SAP B1 FDD Author (Orchestrator)

## Overview

**Core principle:** FDD is a client-facing contract artifact. One call → one complete structured FDD (markdown), assembled from the five SAP B1 documentation skills invoked in a fixed order, mapped to the PT Soltius FDD template. Never produce a partial FDD (missing cover, TOC, or Approval) — the template is the contract.

This is the **master skill**. The five sub-skills each own one concern; this skill owns the document skeleton and assembly.

## Orchestration Map (sub-skills → FDD sections)

| FDD Section | Sub-skill to invoke | What it feeds |
|---|---|---|
| 2.1 Business Process (diagram) | `sap-b1-visual-logic-mapper` | Mermaid flowchart per transaction flow, decision nodes |
| 2.1 Business Process (narrative) | `sap-b1-business-logic-translator` | "Keterangan proses" steps + PIC + Dokumen pendukung + Journal entry |
| 2.3 Integration / AP Invoice | `sap-b1-integration-mapper` | Service Layer / A/P Invoice payload notes, sync flow |
| 3.1-3.3 Tables/Fields/UDT/UDF/UDO | `sap-b1-udt-udf-schema-extractor` | Field spec tables: No. \| Field ID \| Type \| Sub-Type \| Size \| Notes |
| 3.4 Validasi | `sap-b1-validation-trigger-analyzer` | Bulleted "Validasi" section from code guards |

Invoke each sub-skill (via the skills tool) in that order during analysis; assemble in the template order below.

## Source Scan (first step)

1. Identify add-on type from repo:
   - **C# UI API add-on** (`IBT_SAP_Customization_Setup.cs`, `UserTablesMD`/`UserFieldsMD`, `ItemEvent`/`FormDataEvent`) → UDT/UDF/UDO + UI event flow
   - **Laravel web + Service Layer** (controllers, `SapB1Service`, `buildDocumentPayload`, `/b1s/v2`) → business process + integration payloads
   - **SQL/HANA install scripts** (`CREATE TABLE "@TBL"`, UDF DDL) → schema tables
2. Enumerate modules/menus (e.g. Expense Request, Settlement; IFRS 16, IFRS16 Run Preview).
3. For each module: flow → narrative → schema → validations → UI.

### Cover
```markdown
FUNCTIONAL DESIGN DOCUMENTATION
(FDD)

{NAMA ADD-ON / MODUL}

DEVELOPED BY
PT SOLTIUS INDONESIA

FOR
{NAMA CLIENT}

{TAHUN}
```

### Disclaimer
```markdown
Disclaimer and Confidentiality Statement
This document is a DRAFT document. PT Soltius Indonesia and {CLIENT} representatives accept that this document reflects the mutually agreed scope and approach. This document has been submitted on a confidential basis solely for the purpose of supplying information to {CLIENT} and is not for use by any other persons. Whilst every care has been taken with the preparation of this document, PT Soltius Indonesia accepts no responsibility for any errors or omissions within this document, and readers are advised to obtain further advice regarding specific matters within this document before acting on them.
```

### DAFTAR ISI
Numbered list of the 5 chapters + subsections (placeholder page numbers omitted or marked `...`).

### 1. Pendahuluan
- **1.1 Latar Belakang** — why the add-on exists; the SAP B1 standard limitation it overcomes (2-3 sentences).
- **1.2 Tujuan Development** — numbered goals, each starting "Add-on ... bertujuan ...".
- **1.3 Ruang Lingkup** — "Function:" bullets; the X main scopes/menus/modules; what is in and out of scope (e.g. "Add-on berjalan di dalam SAP Business One", "Tidak terdapat menu ... pada ...").

### 2. Penjelasan Proses Development
- **2.1 Business Process** — one subsection per transaction flow (e.g. `2.1.1 Expense Request`). Content per flow:
  - Mermaid flowchart (from visual-logic-mapper)
  - "Keterangan proses:" numbered narrative steps (from business-logic-translator)
  - Per step where relevant: **PIC :** actor, **Dokumen pendukung :** input doc, **Journal entry :** D:/C: table
- **2.2 Simulasi** (only when the add-on has calculation, e.g. IFRS16) — worked numeric example, exact formulas.
- **Urutan Development** — ordered list of development tasks (form → automation → log).

### 3. Design Struktur Data
- **3.1 Tables / UDT** — for web tables: `No. | Table Name | Table ID | Type | Notes`; for SAP: UDT list (Type = Dokumen / Dokumen Detail / Master Data).
- **3.2 Fields / UDF** — per table, header then detail:
  ```markdown
  | No. | Field ID | Type | Sub-Type | Size | Notes |
  ```
  - Web tables: prefix `EXP_`/`PRU_`, Type = Numeric/Alphanumeric/DATE/DOUBLE, Notes describe purpose + PK/FK.
  - SAP UDT/UDF: add `Field Name` column; include UDO default fields `DocEntry`, `DocNum`, `LineId` with Notes "Default field dari UDO Creation SAP Business One"; mark Valid Values inline.
- **3.x UDO** (if present): `No. | Object Name | Object Id | Object Table | Object Type | Object Services | Notes` (Services: Find, Log, Manage Series).
- **3.y Validasi** — bulleted list from validation-trigger-analyzer, grouped per menu/module.

### 4. Design User Interface
Per screen:
```markdown
### 4.1.1 {Nama Layar}

Gambar 4.1.1. {Nama Layar}
```
(Placeholder for screenshot; note "Gambar 4.x.x" caption convention — add screenshots if available in repo/docs.)

### 5. Approval
```markdown
SIGNED FOR PT SOLTIUS INDONESIA
NAME | DATE | SIGNED
- Quality Assurance
- Project Manager
- Technical Consultant

SIGNED FOR {CLIENT}
NAME | DATE | SIGNED
- Project Manager
- {Team(s)}
```

## Deliverable

- File: `FDD - {Add-on Name} v1.0.md` in project `docs/` (or working dir).
- Follow repo language of existing docs (Indonesian template above unless docs are English — the Production Standard Cost doc has an English variant; match the client's language).
- One FDD per add-on/module; if repo has multiple modules (e.g. Expense Claim has ER + Settlement), keep them in one FDD with per-module subsections.

## Quality Gates (verify before delivering)

- [ ] Cover, disclaimer, DAFTAR ISI, 5 chapters present.
- [ ] Every business flow has: diagram + narrative + PIC + Dokumen pendukung + Journal entry.
- [ ] Field tables complete: no invented Type/Size; PK/FK flagged in Notes; UDO defaults marked.
- [ ] Validasi matches guards actually found in code (not fabricated).
- [ ] TOC headings match final headings.
- [ ] No real credentials, passwords, or connection strings (reference `.env` keys only).

## Common Mistakes

- Dropping cover/disclaimer/TOC/Approval (template is the contract).
- Writing "Keterangan proses" without PIC / Dokumen pendukung / Journal entry.
- Mixing web-table format (EXP_/PRU_) with SAP UDT/UDF format (`SOL_*` + UDO defaults) in section 3.
- Omitting Validasi or inventing validations not in code.
- Forgetting Urutan Development.
- Leaving Gambar captions unnumbered (`Gambar 4.1.1` sequence must match UI subsection order).