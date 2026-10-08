# IBT FDD v2.0 Gap Analysis — Worked Example

Real example of cross-checking FDD v1.5 vs meeting notes (Chemical.docx), finding mismatches, and rebuilding as FDD v2.0.

## Context

- FDD: `D:\SOLTIUS\FDD\FDD\FDD - IBT Request Fulfillment v1.5.docx` (web-based SAP B1 add-on, Laravel+React+Vite)
- Notes source: Chemical.docx — raw notes from customer meeting with item classifications, RL grouping, urgent sub-categories, store management, docking, audit log
- 3 earlier meeting notes already merged into `Gabungan Notes Blueprint - September 2026.docx`

## Method

1. Read FDD v1.5 (headings + tables via python-docx).
2. Read Chemical.docx (read_file auto-extracts .docx).
3. For each item in Chemical.docx, classify against FDD:
   - **MISMATCH** — FDD contradicts or doesn't have the feature at all
   - **PARTIAL MATCH** — FDD has something related but incomplete
   - **MATCH** — FDD already covers it

## Findings (15 items)

### MISMATCH (11 items)

| # | Notes Item | FDD v1.5 Status | Action in v2.0 |
|---|-----------|-----------------|----------------|
| 1 | Klasifikasi Store/Deck/Engine (40 sub-kategori) | FDD has ABC criticality classification only | Added category_type + category_code fields, 3 group with 40 sub-categories in scope |
| 2 | RL grouping (item sama + vendor sama + periode) | Not in FDD | Added to RL scope + grouping logic |
| 3 | RL urgent sub-kategori (safety/operational/financial) | FDD has flat "emergency" only | Added urgent_category field (safety/operational/financial_risk) |
| 4 | RL urgent bypass admin | FDD emergency still goes through web app | Clarified: bypass approval stages entirely, not just auto-approve |
| 5 | RL tipe/flag (Regular/Docking/Urgent/Scheduled) | FDD has is_recurring only for template | Added rl_type + rl_flag + is_scheduled + is_docking fields |
| 6 | Alert kapal belum bikin RL | Not in FDD | Added to notification scope |
| 7 | Alert item expired | Not in FDD | Added to notification scope + store management |
| 8 | Suggest quantity + maintain expired date | Not in FDD | Added to store management scope |
| 9 | Flag docking dari SI | Not in FDD | Added is_docking field + SI dock approval routing |
| 10 | SI dock approval saat di dock yard | Not in FDD | Added is_docking_route in approval_stages |
| 11 | NARO FIELD COA mapping per item (hidden) | Not in FDD | Added naro_coa field in equipment_catalogs (hidden in UI) |

### PARTIAL MATCH (3 items)

| # | Notes Item | FDD v1.5 Status | Action in v2.0 |
|---|-----------|-----------------|----------------|
| 12 | Store 6-level (Vessel>Storage>Area>Rack>Shelf>Bin) | FDD caches sap_warehouses + sap_bin_locations | Added explicit store_locations table with 6-level structure |
| 13 | Item maintain stock di kapal | FDD has vessel_codes per item but no stock level per vessel | Clarified: maintain stock per vessel via store_locations |
| 14 | Subsidi silang antar kapal | FDD ITR/IT supports whse-to-whse transfer | Explicitly mentioned subsidi silang in ITR scope |

### MATCH (1 item)

| # | Notes Item | FDD v1.5 Status |
|---|-----------|-----------------|
| 15 | Urgency remarks (free text alasan urgent) | FDD has urgency_remarks field — already matches |

## Additional gaps from 04 Sept notes (also missing in v1.5)

- Cost Center (vessel vs TTWS workshop) — added cost_center field
- Approval by item group hierarchy — added item_group in approval_stages
- Notify PQ overdue — added to notification scope
- Edit PO after GRPO parsial (qty lock) — added to PO scope + validation rule + Error Code 10006
- UDF: Required Date, Quoted Date, Estimated Delivery Days (+7 auto) — added as UDF fields
- Draft hapus ke SAP B1, draft only web — added to batasan
- Alternate Part Number — added alternate_part_no field in equipment_catalogs
- Nomor IMPA — added impa_code field
- Master email template (PQC winner/loser) — added to notification scope
- Upload PDF ke NAS Synology — added to print/export scope

## FDD v2.0 rebuild

Result: 29-page FDD v2.0 at `D:\SOLTIUS\FDD\FDD\FDD - IBT Request Fulfillment v2.0.docx`

Key structural changes v1.5 → v2.0:
- 26 tables (down from ~30, consolidated)
- +6 new fields in transactions header (rl_type, rl_flag, urgent_category, cost_center, is_scheduled, is_docking)
- +4 new fields in approval_stages (item_group, cost_center, is_docking_route, currency)
- +5 new fields in equipment_catalogs (alternate_part_no, impa_code, category_type, category_code, naro_coa)
- +3 new tables (store_locations, item_classifications, transaction_comments)
- +2 error codes (10006 qty lock, 20003 sync failed)
- +2 UI pages (Catalog Item, Store Management)
- Role-based access: user kapal explicitly "tanpa harga, tidak buat PO"

## Lesson

FDD gap analysis = read FDD + read notes → classify each note item → rebuild. The classification (MISMATCH/PARTIAL/MATCH) makes it easy to communicate findings to user before rebuilding. Always check:
1. Schema fields — does the table have a column for this?
2. Scope statement — is this feature mentioned in ruang lingkup?
3. Business process — does the flowchart/keterangan cover this scenario?
4. Validasi — are the rules for this feature present?
5. UI — is there a form/page for this?
A feature can appear in scope but be missing from schema = still a mismatch.
