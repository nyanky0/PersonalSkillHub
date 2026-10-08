---
name: token-efficiency
description: "Hemat token saat coding: baca bertarget, diff minimal."
version: 1.0.0
license: MIT
platforms: [windows]
metadata:
  hermes:
    tags: [token, context, efficiency, hemat, pasif, ponytail, caveman]
    related_skills: [ponytail, karpathy-guidelines, caveman, codebase-inspection, subagent-driven-development, session-librarian]
---

# Token Efficiency — protokol pasif semua agent

Potong token **input** (baca file / riwayat / konteks) dan **output** (prosa balasan) tanpa
menghentikan proses development dan tanpa menurunkan pemahaman kode.
Slogan: **hemat baca, hemat tulis, jangan hemat mikir.**

## 5 hukum — berlaku setiap giliran

1. **Jangan dump file utuh.** Cari dulu (`search_files` → `path:line`), baru baca jendela
   ±40 baris di sekitar baris yang relevan (`read_file` offset/limit).
2. **Rujuk `path:line`, jangan tempel isi.** Kutipan maksimal 5 baris, hanya yang menentukan.
3. **Batch tool call paralel.** Semua pembacaan independen dalam SATU giliran — tiap giliran
   tambahan mengirim ulang seluruh konteks.
4. **Diff minimal (ponytail).** Tangga: perlu ada sama sekali? → sudah ada di repo? → stdlib?
   → fitur native? → dependency terpasang? → satu baris? → baru kode minimum.
5. **Hasil dulu, prosa belakangan.** Tanpa preamble, tanpa recap, tanpa narasi tool call.

## Memahami kode dengan murah (ini yang TIDAK boleh dihemat)

Urutan termurah → termahal:

| Butuh | Pakai | Biaya |
|---|---|---|
| Peta repo, ukuran, bahasa | `codebase-inspection` (pygount) | sangat murah |
| Lokasi definisi/pemakaian | `search_files` → `path:line` | murah |
| Struktur satu file | `grep -n "^\\(class\\|def\\|public\\|function\\)"` | murah |
| Isi satu fungsi | `read_file` offset + limit | sedang |
| File > 300 baris utuh | hindari — baca bertarget | mahal |
| Riwayat sesi panjang | ringkas / buang tool result besar | mahal |

Bug: temukan akar masalah dulu (`systematic-debugging`). Tiap patch coba-coba yang gagal =
satu babak konteks penuh terbuang.

## Tuas pasif (tanpa dipanggil)

- **Agregasi di kode, bukan di kepala model** — hitung, dedupe, sort, bandingkan pakai script.
- **Delegasi kerja berisik** (`dispatching-parallel-agents`, `subagent-driven-development`):
  eksplorasi luas / log panjang di subagent; konteks utama hanya menerima kesimpulan.
- **Kebersihan sesi** (`session-librarian`): topik baru → sesi baru; jangan menumpuk riwayat.
- **Output terse** (`caveman` lite/full) untuk kerja teknis: narasi tool, ringkasan diff,
  laporan debug. Bahasa user tetap; caveman memampatkan gaya, bukan bahasa.
- **`coding_context` Hermes**: di workspace kode, kategori skill non-coding otomatis
  diturunkan jadi nama-saja → daftar skill di system prompt mengecil sendiri.

## Wiring pasif (SUDAH dipasang — jangan bikin skill baru untuk ini)

| Agent | File pasif | Mekanisme |
|---|---|---|
| Hermes | `E:\HERMES\SOUL.md` | selalu dimuat tiap sesi |
| Hermes | `config.yaml → agent.coding_instructions` | disisipkan ke coding brief |
| Antigravity IDE / Cline / agy | `C:\Users\yudah\.agents\AGENTS.md` | aturan global |
| Gemini (agent Antigravity) | `C:\Users\yudah\.gemini\config\AGENTS.md` | aturan global |
| Gemini CLI | `C:\Users\yudah\.gemini\GEMINI.md` | konteks global |

Ubah aturannya: edit file di tabel, **bukan** tambah skill. Teks kanonisnya ada di
`references/passive-rules.md`; penyebar idempotent-nya `scripts/install_passive_rules.py`.

## Verifikasi

```bash
python "E:/HERMES/skills/token-efficiency/scripts/token_audit.py"
```

Laporan: ukuran tiap file aturan pasif, jumlah skill per agent, 10 SKILL.md terbesar
(kandidat pemangkasan), estimasi token daftar skill per giliran.

## Pemangkasan duplikat (tuas terbesar)

Daftar skill di prompt memuat SETIAP `SKILL.md` yang ditemukan. Satu skill di top-level DAN
di subfolder kategori = dibayar dua kali, dan `skill_view` gagal dengan "Ambiguous skill name".

```bash
python "E:/HERMES/skills/token-efficiency/scripts/prune_duplicate_skills.py"           # dry-run
python "E:/HERMES/skills/token-efficiency/scripts/prune_duplicate_skills.py" --apply    # pindah ke karantina
```

Karantina = `E:\HERMES\.skill-quarantine\<timestamp>` (di luar pohon skill, jadi tidak
terbaca agen). Reversibel dengan `--restore <folder>`.

Aturan pemilihan pemenang (jangan diubah tanpa alasan):

1. Duplikat dikelompokkan pakai **`name:` di frontmatter**, bukan nama folder.
2. Pemenang = salinan **byte-identik dengan hub** (`D:/SkillHub/skills/<name>`), lalu folder
yang namanya sama dengan `name`, lalu yang paling dangkal.
3. Bundel plugin vendored (`*/plugin/skills/*`) tidak pernah dipindah.

Urutan aman: sync dulu (`collect` + `pushall`) → baru prune → cek `skill_view(name)` untuk
nama yang tadi ambigu. Hasil terukur 2026-09: 359 → 251 entri, 250 nama unik, 1 tabrakan
sisa (bundel plugin api-gateway).

## Vendor: rtk / caveman ultra / headroom — mana yang aman

Diverifikasi dari dokumentasi 9router + `headroomlabs-ai/headroom`:

| Fitur | Apa itu | Efek ke kualitas hasil | Keputusan |
|---|---|---|---|
| **RTK** | filter tool_result (`git diff`, `grep`, `ls`, `tree`, log) di dalam proxy 9router | kompresi klaim "lossless" + fallback ke teks asli kalau filter gagal/membesar | **aman, tapi jangan lewat proxy** → pakai versi sumber: perintah terse + `compression.proactive_prune_tokens` bawaan Hermes |
| **Caveman ultra** | prompt "terse" → output dipadatkan | substansi teknis dipertahankan; yang turun keterbacaan. ultra membuang konjungsi & bikin frasa satu kata → rawan salah baca, dan skill-nya sendiri memaksa drop caveman di peringatan keamanan/aksi ireversibel/urutan langkah | **pasang di level `lite`/`full`**; `ultra` hanya on-demand |
| **Headroom** | proxy `pip install headroom-ai[proxy]`, `POST /v1/compress` | **berisiko**: `--mode token` menulis ulang riwayat sebelumnya, ML Kompress menjatuhkan token by retention scoring (lossy), semantic caching bisa mengembalikan jawaban basi, `--no-ccr` dilabeli lossy sendiri | **jangan pasang** — arsitekturnya sama seperti 9router (harus ganti base_url) |

Catatan penting: RTK/Headroom hanya menghemat token **di jalur request**. Kalau Hermes/agy tidak
mengarahkan request ke proxy itu, keduanya nol efek — sedangkan aturan pasif + disiplin perintah
terse di atas bekerja tanpa mengubah endpoint.

## Pitfalls

- Hemat token dengan **tidak membaca kode** = menukar token dengan bug. Dilarang.
- Duplikat **wajib** dikelompokkan pakai `name:` frontmatter: folder `lazy-dev/` berisi
  `name: ponytail` sehingga tetap menabrak `ponytail/`. Kalau pemenangnya folder yang salah
  nama, tabrakan itu muncul lagi tiap kali sync jalan.
- Salinan hasil batch rename massal bukan "versi lebih baru": pernah ketemu
  `related_skills: [pdf, pdf]` dan `github-code-review` → `github`. Kalau ragu antara dua
  salinan, pilih yang identik dengan hub — jangan yang mtime-nya lebih muda.
- `*/plugin/skills/*` (bundel plugin vendored, mis. provider Claude di dalam skill
  `api-gateway`) jangan dipindah: manifest plugin-nya menunjuk path itu.
- `agent.coding_context: focus` **bukan** penghemat besar: kategori non-coding yang
  diturunkan jadi nama-saja cuma ~140 token/giliran karena hampir semua skill di sini sudah
  coding. Tuas utamanya ada di mengecilkan daftar skill (prune) dan disiplin baca.
- `install_passive_rules.py` wajib idempotent: kalau blok ada di baris 1, kepala file kosong →
  `base` harus `""`; kalau `"\n"`, file nambah satu baris kosong tiap dijalankan.
- Pangkas hanya skill yang tak pernah dipanggil; jangan pangkas yang sering dipakai.
- `AGENTS.md` > 20.000 char dipotong head+tail → jaga file aturan tetap kecil.
- Deskripsi skill dipotong di **60 char** di prompt Hermes → taruh trigger di awal deskripsi.
- Emoji, tabel dekoratif, dan narasi tool call = token output termahal; buang kecuali diminta.
