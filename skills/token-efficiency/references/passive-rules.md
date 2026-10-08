<!-- TOKEN-EFFICIENCY:RULES (kanonis — disebar oleh scripts/install_passive_rules.py) -->
<!-- TOKEN-EFFICIENCY:BEGIN -->

## Token Efficiency Protocol (PASIF — aktif tiap sesi)

Hemat baca, hemat tulis, **jangan hemat mikir**. Berlaku untuk semua kerja teknis.

**Baca**
- Jangan dump file utuh. `search_files`/grep dulu → baru baca ±40 baris di sekitar baris relevan.
- Rujuk `path:line`. Kutipan maksimal 5 baris, hanya yang menentukan.
- Batch semua pembacaan independen dalam SATU giliran tool call.
- Peta repo: pakai `codebase-inspection` (pygount) sebelum membaca file apa pun.
- Bug: cari akar masalah sebelum patch. Percobaan gagal = satu babak konteks terbuang.

**Tulis**
- Diff minimal: perlu ada? → sudah ada di repo? → stdlib? → fitur native? → dependency terpasang? → satu baris?
- Hasil dulu, prosa belakangan. Tanpa preamble, tanpa recap, tanpa narasi tool call.
- Agregasi pakai script (hitung/dedupe/sort), bukan membaca ratusan hasil manual.

**Perintah tool (RTK setara — nol efek ke isi hasil)**
- Perintah berisik dipakai versi terse: `git diff --stat` / `--no-color`, `grep -m 5` / `rg -c`,
  `ls -1`, `tree -L 2`, log `| tail -40`. Yang dipotong cuma bagian yang tak dibutuhkan.
- Hasil tool >8000 char → ringkas jadi temuan + `path:line` sebelum lanjut ke langkah berikutnya.

**Gaya output**
- Default: `caveman lite` saat balas user, `full` untuk langkah teknis internal.
- `ultra`/`wenyan` hanya kalau user minta eksplisit — risiko salah baca, bukan salah isi.
- Keamanan, aksi ireversibel, urutan langkah, atau user minta klarifikasi → drop caveman
  (aturan Auto-Clarity). Jangan pernah padatkan sampai makna jadi ambigu.

**Konteks**
- Eksplorasi luas → delegasikan ke subagent; konteks utama terima kesimpulan saja.
- Topik baru → sesi baru. Riwayat panjang yang tak terpakai = token terbakar tiap giliran.
- Skill dimuat hanya saat deskripsinya cocok. Jangan tempel isi skill ke prompt.
- **Jangan pasang proxy kompresor di jalur request** (9router RTK, Headroom). Proxy memutasi isi
  request di wire → prefix cache provider ke-break, dan kompresinya lossy (Kompress/RETIRED
  llmlingua menjatuhkan token by scoring). Pengganti native Hermes:
  `compression.proactive_prune_tokens: 48000` — hanya menyentuh hasil tool LAMA di luar
  `protect_last_n`, tanpa panggilan model, gate `min_reclaim` bikin break episodic.

Skill pendukung: `token-efficiency`, `ponytail`, `caveman`, `karpathy-guidelines`,
`codebase-inspection`, `systematic-debugging`, `subagent-driven-development`, `session-librarian`.

<!-- TOKEN-EFFICIENCY:END -->
