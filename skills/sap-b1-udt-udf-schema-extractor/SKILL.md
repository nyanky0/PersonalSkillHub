---
name: sap-b1-udt-udf-schema-extractor
description: "Extract and document UDT/UDF metadata and SQL/HANA schemas from SAP B1 databases."
---

# SAP B1 UDT/UDF Schema Extractor

## Overview

**Core principle:** Produce a complete, non-deduped field specification table directly sourced from the code or install script — never invent types/sizes, and never drop a field without flagging it.

Output is a data dictionary ready to paste into add-on documentation: one row per field, columns `Table Name | Field ID | Type | Size | Notes`.

## Supported Sources (scan priority)

| Source | Where to look | How DDL is born |
|--------|---------------|-----------------|
| C# DI API add-on | `UserTablesMD`, `UserFieldsMD`, `_oUserTablesMD.Fields.Add(...)`, `SolutionPackager` / `.b1p` | Extracted from `CreateTable` + `Field.Add` calls with `.Type` + `.EditSize` |
| MS SQL install script | `CREATE TABLE "@TBL"`, `ALTER TABLE ... ADD "U_SOL_*"`, `NVARCHAR`, `INT`, `NUMERIC(19,6)` | Parsed from DDL type + length |
| HANA install script | `CREATE COLUMN TABLE "@TBL"`, `NVARCHAR(...)`, `DECIMAL(19,6)`, column-comment block | Parsed from DDL + comments |
| Laravel migration/model | `Schema::create`, `$table->string('u_sol_x', 50)` | Column def + cast |
| SAP B1 Customization Requirements doc | Existing tables like `@SOL_VESSELS` | Reuse existing spec, update deltas |

## Extraction Rules

1. **Field ID** = SAP B1 DB/API field name verbatim (`U_SOL_` prefix preserved). For UDT, `Code` and `Name` are implicit system columns — add them first when missing.
2. **Type mapping** (map source type to SAP B1 type vocabulary):

| Source type | SAP B1 Type (`Type`) |
|-------------|----------------------|
| `string` / `NVARCHAR(n)` / `VarChar` | `AlphaNumeric` |
| `int` / `integer` / `INT` / `Numeric(11)` | `Numeric` |
| `decimal` / `DECIMAL(19,6)` / `NUMERIC(x,6)` | `Number` (money/precision) |
| `bool` / `TINYINT` | `AlphaNumeric` `Y`/`N` |
| `date` / `DATETIME` / `Date` | `Date` |
| `float` / `REAL` | `Number` |
| `link` / FK reference | `AlphaNumeric` numeric-sized or link |

3. **Size** = raw length from source. If absent, put `-`.
   - SAP B1 `EditSize` scale: `AlphaNumeric` sized 1–254; `Numeric` sized 1–11; `Number` uses scale not size.
   - Flag violations of hard limits: `UserFieldsMD.Name` ≤ 18, `Description` ≤ 30, `TableDescription` ≤ 20, `ValidValues.Value` ≤ 10, `Description` ≤ 30.
4. **Notes** column captures: purpose/function, valid values with defaults, linked master data (e.g. `@SOL_VESSELS.Code → OITM`), and the target SAP table (`OPOR`, `POR1`, `OITM`, `OCRD`).
5. **Never auto-fill** Type/Size when source is ambiguous — mark `?` in Notes, do not guess.

## Output Format

Emit one markdown table per target table/object:

```markdown
### UDF Header — Target: OPOR, OPDN, ORPC (Marketing Documents - Title)

| Table Name | Field ID | Type | Size | Notes |
|---|---|---|---|---|
| OPOR | U_SOL_WebTxNumber | AlphaNumeric | 50 | Nomor dokumen unik Web App (#PO-2026-001) |
| OPOR | U_SOL_WebDocStatus | AlphaNumeric | 10 | DRAFT/APPROVED/CLOSED/CANCELLED |
```

Group by section: UDF Header, UDF Rows, UDT Master Data, UDT Document. Keep a per-field "source=" comment chain only when debugging extraction — strip for final doc.

## Workflow

1. Locate installation/add-on source (`.cs`, `.sql`, `.hdb`/`.migration`, `database/migrations/*.php`).
2. Extract field list per object; dedupe by (Table, Field ID).
3. Build Type/Size from mapping; resolve ambiguity in Notes.
4. Flag any field with unreadable type or truncated data.
5. Emit tables; cross-link to any existing `SAP_B1_CUSTOMIZATION_REQUIREMENTS.md`.

## Quick reference

| Ask | Do |
|-----|----|
| "list my UDFs" | Extract from UDF source, group by target table |
| "what fields on @SOL_VESSELS" | Extract UDT block, prepend Code/Name |
| "any type violations?" | Check hard-limit list in API constants |
| "only standard SAP fields" | Note absence of `U_SOL_` prefix → standard mode |
| "table structure too wide" | Field ID ≤18 must hold — collapse names, note original |

## Common mistakes

- Reporting `Description` as `Field ID` (they diverge: `SOL_WebTxNumber` vs `U_SOL_WebTxNumber`).
- Dropping `Code`/`Name` on UDT.
- Mistaking SAP `Flags`/`LinkedTable` for data columns.
- Guessing size for `Number` type fields (uses scale, not length).
- Copying a stale older UDF list into a new schema without diffing deltas.