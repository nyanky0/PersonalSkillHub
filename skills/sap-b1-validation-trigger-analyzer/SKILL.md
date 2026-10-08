---
name: sap-b1-validation-trigger-analyzer
description: "Analyze SAP B1 business validation rules and SP_TransactionNotification triggers."
---

# SAP B1 Validation & Trigger Analyzer

## Overview

**Core principle:** Every guard that can block, warn, or auto-act on a document must appear as a traceable, testable validation point — grouped into BEFORE-POST, POST-TIME, and EVENT-TRIGGER sets. No silent validation is left undocumented.

> [!TIP]
> Untuk dokumentasi FDD fungsional dan pengujian QA terpusat (taksonomi kode validasi `VAL-XXX-NNN`, matriks Excel 10-kolom, dan penulisan teks FDD bebas error HTTP), gunakan master skill **[`enterprise-fdd-master`](../enterprise-fdd-master/SKILL.md)**.

## What Counts as a Validation/Trigger

| Category | Example source | Where found |
|----------|----------------|-------------|
| **Pre-post guard** | mandatory field check, qty ≤ open qty, price ≥ 0 | C# `ItemEvent` at `et_ADD`, `et_UPDATE`; Controller `validate()` |
| **Document check** | document must be approved before post, status transition guard | Laravel `Authorize`/validation in `sync-sap`; C# status handler |
| **Error handling** | `catch` block, message to user, cancel/suspend | C# `throw` / message; Laravel exception → flash |
| **Trigger / auto-action** | auto-approve, auto-sync to Service Layer, series/sequence assignment | event subscriptions, `SAP_B1_AUTO_POST` flag |
| **Server-side constraint** | UDF valid values, Formatted Search (FMS) `U_SOL_*` | SAP B1 setup, FMS definitions |
| **Uniqueness / integrity** | duplicate `U_SOL_WebTxId` check, QR hash uniqueness | DB unique index, app check |

## Analysis Steps

1. Sample the post path: where the document *leaves* the app (C# `Item_Event` + `FormDataEvent`, Laravel `post/publish/sync-sap` controller).
2. Enumerate every `if`/`switch`/`try-catch`/`throw`/`Validate()` on that path. Treat each as a validation point.
3. Classify each point by type (mandatory, range, cross-field, status, business rule, side-effect trigger).
4. For each point capture:
   - **Kondisi** (condition in business terms)
   - **Level** `Block` | `Warning` | `Auto`
   - **Pesan / Aksi** (message shown or action taken when violated)
   - **Kapan** (BEFORE post, AT post, AFTER post / trigger)
5. Emit the "Validasi Dokumen" set, grouped by the document/transaction type.

## "Validasi Dokumen" Output Format

```markdown
## Validasi Dokumen — Purchase Order (PO)

Validasi berikut dievaluasi **sebelum** dokumen di-post ke SAP Business One:

| # | Validasi (kondisi bisnis) | Level | Kapan | Pesan / Aksi |
|---|---|---|---|---|
| 1 | Vendor wajib terisi (CardCode) | Block | Sebelum post | "Vendor harus dipilih" |
| 2 | Qty tiap baris ≤ Qty terbuka PO asal | Block | Sebelum post | "Qty melebihi sisa PO" |
| 3 | Dokumen harus ber-status Approved | Block | Sebelum post | "Dokumen belum disetujui" |
| 4 | Duplikasi U_SOL_WebTxId | Block | Setelah post | Tolak & log |
| 5 | SAP_B1_AUTO_POST aktif | Auto | Setelah post | Auto-sync ke Service Layer |

### Trigger tambahan
- **Auto series:** saat post, nomor seri diambil dari `SeriesService_GetDocumentSeries`.
```

## Rules of Engagement

1. **Order by severity** then by execution order (worst blocker first).
2. **Tag custom vs standard.** Mark which validations come from the add-on (`CUSTOM`) versus SAP B1 native. Auditors care.
3. **Never merge two distinct guards** into one row — one condition per row.
4. **Keep the trigger's threshold exact** (`qty > 0` and `qty ≥ 1` are different guards).
5. **Record the "happy path" too**: document the check that *passes* so readers know what unblocks the post.
6. Include the source anchor (`Class.method`, `routes/web.php`, migration index) as a final trailer per section.
7. If a guard only fires in UDF mode, tie it to the toggle (e.g. `SAP_ENABLE_CUSTOM_UDF`) in Notes.

## SP_TransactionNotification & Object Key Standards

Ketika menganalisis atau mendokumentasikan trigger `SP_TransactionNotification` dan `SP_PostTransactionNotice`:
1. **Wajib Cantumkan Object Type & Primary Key**:
   - Parameter `@object_type` mencocokkan kode integer string **Object Type**.
   - Parameter `@list_of_cols_val_tab_del` mencocokkan kolom **Primary Key** tabel terkait.
   - Analis/developer **WAJIB** merujuk pada tabel master di `sap-b1-suite` untuk memastikan nama tabel, primary key, dan objtype 100% presisi (contoh: `@object_type = '22'` -> OPOR, DocEntry; `'17'` -> ORDR, DocEntry; `'2'` -> OCRD, CardCode; `'4'` -> OITM, ItemCode).
2. **Format Dokumentasi Trigger SP**:
   Setiap poin validasi trigger SP harus mencantumkan:
   - **Object Type**: Nilai integer (`@object_type`)
   - **Target Table & PK**: Nama tabel header + Primary Key (`@list_of_cols_val_tab_del`)
   - **Transaction Type**: `'A'` (Add), `'U'` (Update), `'C'` (Cancel), `'D'` (Delete), `'L'` (Close)
   - **Error Code & Error Message**: Kode error integer unik + pesan blokir

## Quick reference

| Level | Meaning |
|-------|---------|
| `Block` | Violation stops the action (document not posted / not saved) |
| `Warning` | Allows but surfaces warning |
| `Auto` | No user decision; system auto-acts (auto-approve, auto-post, series assign) |

## Common mistakes

- Listing validations without "Kapan" (before/at/after post) — auditors need the lifecycle position.
- Forgetting non-blocking Auto triggers.
- Writing condition as raw code (`if (oItem.Qty > 0)`) instead of business terms.
- Dropping the toggle-dependence (`SAP_ENABLE_CUSTOM_UDF`) of custom guards.
- Ignoring error-handling paths (the outer `catch` is itself a validation boundary).