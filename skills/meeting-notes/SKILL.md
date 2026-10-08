---
name: meeting-notes
description: "Use when tidying raw meeting notes into minutes docx."
version: 1.0.0
author: Hermes curator session
---

# Meeting Notes Tidy-Up

Raw consultant/customer meeting notes → polished structured .docx deliverable. Typical trigger: user blue-printing with a customer, attaches "Note DDMMYYYY.docx", asks to "rapihin dokumentasi gw".

## When to Use
- User attaches/points to a messy notes file (Word, txt) from a meeting, workshop, or blueprint session and wants it cleaned up.
- Notes contain mixed Indonesian/English, abbreviations (RL, ATK, RF, docnum, PIC), half-sentences, and dangling remarks.
- User has MULTIPLE notes files from different sessions/dates and wants them combined into one structured document (multi-file merge pattern — see below).

## Workflow
1. Read source with `read_file` (auto-extracts .docx). Keep the original file UNTOUCHED — write output as a new file, e.g. `Note <date> - RAPIH.docx` in the same folder.
2. Restructure by session/section: heading per session, sub-heading per topic. Preserve the chronological grouping the note-taker used.
3. Classify every fragment into: fact/flow, decision/policy, open question, ambiguous remark. Use visual callout boxes:
   - Decision → green box (E2EFDA fill / 375623 text), label "KESIMPULAN"
   - Open question → yellow box (FFF2CC / 7F6000), label "PERTANYAAN TERBUKA"
   - Ambiguous source remark → blue info box, explain it needs customer confirmation — never silently drop or silently reinterpret it
4. End with an ACTION ITEMS table (No / Action Item / PIC / Status). Derive items from open questions and TODO-ish remarks; mark all "Open" if PIC unknown — user fills PIC.
5. Build with the docx skill (docx-js npm). Copy `templates/meeting-notes.js` as the starting point — full pattern: meta table (Tanggal/Topik/Peserta), callouts, action table, Calibri, A4.
6. Verify: structural check via python zipfile if no renderer available (extract `<w:t>` runs, count `<w:tbl>` and `<w:numPr>`); render to PDF + vision check when soffice exists.
7. Report to user: list every interpretation/inference ADDED beyond the source (e.g. "field biaya kirim opsional" inferred from "tidak semua pengiriman ada biaya") so they can veto. Never present inferences as verbatim notes.

## Pitfalls
- Do NOT resolve ambiguity by guessing meaning — surface it (source phrase "Jangan sampai terjadi" with no context became both an info box AND an action item to confirm).
- Keep domain abbreviations verbatim (RL = Requisition List, ATK = alat tulis kantor, RF = Request Fulfillment, docnum, PIC). Expanding once in parentheses on first use is fine.
- Write output next to the source file (same directory), never overwrite the source.
- Docx-js gotchas (table dual widths DXA, ShadingType.CLEAR, numbering for bullets) — see the docx skill.

## Multi-file merge pattern

When user has multiple notes files from different sessions/dates and wants them combined into one structured document:

1. Read all source files via `read_file` (auto-extracts .docx text with line numbers).
2. Reorganize by TOPIC, not by source — group related content across documents together. Don't concatenate source files sequentially.
3. Deduplicate overlapping content (same field list in two meetings → merge into one section).
4. Preserve source attribution — add `Sumber: Sesi XX September 2026` line under each heading.
5. Consolidate all action items + open questions into unified tables at the end (merge + renumber, don't keep per-session tables).
6. Number sections sequentially (1, 2, 3...) by topic, not by source session.
7. Build with docx npm — use `templates/merge-notes.js` as starting point (helpers: h1/h2/h3, bullet, bulletRich, table, cell, cellMulti, page break, header/footer with page numbers).
8. Verify: `soffice --headless --convert-to pdf` + `pdfinfo | grep Pages` + `pdftotext | head/tail` for content check. Vision verify if model available.
9. Output filename: `Gabungan Notes <Topic> - <Month Year>.docx` in same directory as sources.

### Pitfalls for merge
- Late-added source files (e.g. user drops a 4th file after initial merge) require re-reading the build script, adding a new section, AND updating consolidated tables (action items, open questions) — not just appending content.
- Action items table: renumber sequentially after merging from multiple sources. Don't keep per-source numbering.
- Open questions: deduplicate similar questions across sessions before merging.
- Section numbering: if adding a new section in the middle, ALL subsequent sections + action items table must be renumbered. Use search-replace on `h1("N.` → `h1("(N+1).` pattern.

## Support files
- `templates/meeting-notes.js` — known-good docx-js builder for single-file tidy (meta table, callout boxes, action-items table). Verified 2026-09-02, IBT blueprint session.
- `templates/merge-notes.js` — known-good docx-js builder for multi-file merge (helpers: h1/h2/h3, bullet, bulletRich, table, cell, cellMulti, header/footer with page numbers, US Letter). Verified 2026-09-08, IBT blueprint merge of 4 source files → 12-page output.
- `references/fdd-gap-analysis.md` — pattern for cross-checking FDD vs meeting notes to find mismatches. 22 common gap categories for SAP B1 web add-on FDDs.
- `references/ibt-fdd-v2-gap-analysis.md` — real worked example of FDD gap analysis: 15 items from Chemical.docx notes checked against FDD v1.5, classified as MISMATCH / PARTIAL MATCH / MATCH, with the resulting FDD v2.0 rebuild that incorporated all findings.
