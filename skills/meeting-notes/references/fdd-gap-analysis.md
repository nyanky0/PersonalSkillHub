# FDD Gap Analysis Pattern

Cross-check FDD (Functional Design Document) vs meeting notes/blueprint sessions to find mismatches.

## When to use

User asks "ada yang mismatch kah?" between an FDD and meeting notes, or asks to review FDD against latest session findings.

## Workflow

1. Read FDD fully (read_file, multiple offsets — FDDs can be 1000+ lines, 1390 lines seen).
2. Read all meeting notes (read_file auto-extracts .docx).
3. Load sap-b1-fdd skill for FDD structure/conventions reference.
4. Cross-check every item from meeting notes against FDD: schema (tables/fields), business process, scope, UI, validation rules.
5. Classify each finding:
   - **MATCH** — FDD covers it fully.
   - **PARTIAL MATCH** — FDD has related field/concept but incomplete coverage.
   - **MISMATCH** — FDD missing entirely.
6. Present grouped by severity: MISMATCH first, then PARTIAL MATCH, then MATCH (match optional, only mention if notable).
7. For each mismatch, cite the FDD field/section that should cover it and what's missing.

## Common gap categories (SAP B1 web add-on)

From IBT Request Fulfillment FDD v1.5 vs 4 meeting notes sessions:

1. **Operational classification** — Meeting notes define Store/Deck/Engine categories (Chemical, Lube Oil, LSA, FFA, Main Engine, Boiler, etc.). FDD schema has `classification` = Class A/B/C criticality, `type` = Mechanical/Electrical/Consumable. Different axis entirely.

2. **RL grouping** — Meeting notes: group RL by same item + same vendor + period. FDD: only has `is_recurring`/`recurring_period` for template, no grouping of existing RLs.

3. **Urgent sub-categories** — Meeting notes: urgent = keselamatan (safety) vs operasional (kapal berhenti operasi). FDD: flat `priority_level=emergency`, no sub-category.

4. **RL urgent skip admin** — Meeting notes: "RL Urgent tidak melalui proses admin." FDD: Emergency Fast-Track still goes through web app (create → auto-approve → sync). Ambiguous whether "skip admin" = bypass web entirely or just bypass approval.

5. **Alerts** — Meeting notes: alert fleet for kapal belum bikin RL, alert item hampir expired. FDD: `in_app_notifications` only for approval pending + dokumen returned.

6. **Suggest quantity + maintain expired date** — Meeting notes mention these features. FDD: not present.

7. **Store hierarchy** — Meeting notes: 6-level (Vessel → Storage → Area → Rack → Shelf → Bin). FDD: cache `sap_warehouses` + `sap_bin_locations` from SAP, no explicit 6-level hierarchy.

8. **Item maintain stock per kapal** — FDD: Sertica integration for stock-take, `vessel_codes` on Equipment Catalogs. No explicit stock level per vessel.

9. **Subsidi silang** — FDD: ITR/IT handle vessel_to_main, whse_to_whse. Subsidi silang (vessel-to-vessel) technically possible but not named.

10. **Flag docking** — Meeting notes: flag from SI, separate RL docking vs regular. FDD: no docking flag.

11. **SI dock approval** — Meeting notes: if kapal di dock yard, approval by SI dock. FDD: approval stages based on amount/branch/module/priority, no dock routing.

12. **Cost center** — Meeting notes: kapal vs workshop TTWS. FDD: not present.

13. **Approval by item group hierarchy** — Meeting notes mention this. FDD: approval based on amount/branch/module, not item group.

14. **Notify PQ overdue** — Meeting notes. FDD: not present.

15. **Edit PO after GRPO partial** — Meeting notes: qty lock below received qty, disabled rows. FDD: no such validation rule.

16. **UDF fields** — Meeting notes: Required Date, Quoted Date, Estimated Delivery Days (+7 auto). FDD: has `doc_due_date` but not these specific fields.

17. **Draft SAP dihapus** — Meeting notes: draft only in web. FDD: still has `sap_draft_entry` field.

18. **Alternate Part Number** — Meeting notes: old vs new part number, dropdown. FDD: Equipment Catalogs has no alternate part number field.

19. **Master email template** — Meeting notes: PQC winner/loser notification body template. FDD: email notification for PQC status + wrong spec, no winner/loser template.

20. **Upload PDF to NAS** — Meeting notes mention NAS Synology. FDD: not present.

21. **Audit log with jabatan** — FDD: `activity_logs` has action, description, properties JSON. No explicit jabatan/position text field.

22. **NARO FIELD COA mapping** — Meeting notes: per item, di-hide. FDD: not present.

## Pitfalls

- FDD filename version may differ from cover page version (file "v1.5", cover says "Version 1.3"). Use filename version as truth for referencing.
- Meeting notes may contain informal shorthand ("anjay", "gini", broken English) — extract the business requirement, not the phrasing.
- Some meeting notes are raw brain dumps with no structure — categorize every fragment before cross-checking.
- FDD may be 1000+ lines — read in multiple offsets to get full schema (transactions table, approval stages, equipment catalogs, validation rules, UI descriptions, role matrix).
