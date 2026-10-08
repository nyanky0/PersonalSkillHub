# Meeting Notes Format (blueprint sessions)

Target shape for summarizing raw meeting notes or live transcripts into .docx (build with docx npm skill, A4, Calibri, navy/blue palette). Proven format from IBT blueprint sessions.

## Document structure

1. **Header block** — centered title "NOTES DISKUSI BLUEPRINT", subtitle project name; meta table (Tanggal / Topik / Peserta).
2. **Per session (SESI N — Topic)**, subsections numbered `N.1, N.2...` per topic.
3. Bullets for facts; bold-label bullets (`Pola rotasi:`, `Frekuensi:`) for key-value facts.
4. **Callout boxes** (single-cell shaded table, thick left border):
   - green `KESIMPULAN / KEBIJAKAN` — decisions & policies agreed
   - yellow `PERTANYAAN TERBUKA` — open questions
   - blue `CATATAN` — ambiguous source notes that need clarification
5. **ACTION ITEMS** table at the end: No / Action Item / PIC-Status (zebra rows).

## Rules

- Interpretation added by the agent must be explicitly flagged (e.g. "inferensi dari X — cek ya"), never silently inserted.
- Ambiguous source phrases ("jangan sampai terjadi") go in a CATATAN box + an action item to confirm with customer — never dropped, never guessed.
- For live transcripts: group by topic not timestamp; mark mis-heard terms as "perlu konfirmasi".
- Keep the user's original raw file untouched; write to a new `... - RAPIH.docx`.
