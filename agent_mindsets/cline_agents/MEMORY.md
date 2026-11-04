Skill laravel-sap-b1-integration dobel & SKILL.md terkunci → tulis via write_file ke references/.
§
Dokumen "otak" SAP: Desktop/SAP_B1_Otak_Skills.md + salinan di tiap skill sap-b1/references/otak-skills.md. Folder Help SDK (Program Files) butuh admin — jangan elevation.
§
SkillHub: D:\SkillHub\skills (collect/push). agy.exe baca C:\Users\yudah\.agents\skills (sama dgn Cline) → push cline = nyebar ke agy. Auto-sync hermes-skill-auto-sync; PRISM di semua agent.
§
Hermes TUI/npm engine & install-scripts → skill hermes-node-diagnostics.
§
curl size_download sering 0 → tulis file + stat; write_file >8K token timeout (pecah); web_search Exa/reddit 403 host ini → web_extract/curl raw.githubusercontent.
§
Browser = Edge (tak ada Chrome; jangan install). browser_exec Hermes jangan dipakai. Verifikasi UI: preview pane (desktop_preview) utk viewport sempit; layar lebar → Playwright + Edge channel:'msedge' (npx cache, Node 24). Action 'type' di preview tak memicu onChange React → pakai URL deep link + read.
§
Laptop ADVAN AI Gen 1406: M.2 2280 terisi; slot kosong kemungkinan 2230 → SSD 2230 (WD SN740/Sabrent). Monitor ext 240Hz; charger 100W USB-C PD.
§
SAP B1 client 10.0.331: duplikat Alt+Tab = entry basi shell/explorer; fix restart explorer.exe; jangan kill B1Browser.exe. Cek kustomisasi tanpa buka SAP: `sqlcmd -S localhost -E -d IBTWEBAPP` → CUFD=UDF, OUTB=UDT, OUDO=UDO.
§
Prinsip kerja user: pakai helper yang sudah ada di repo (mis. Utils.CreateUDF), jangan bikin wrapper sendiri; kalau minta fix, ubah seminimal mungkin — jangan refactor blok lain yang sedang jalan.
§
Arsitektur web IBT (acuan dev): .../maul/IBT-Laravel-React-Inertia.js-/docs/development/AI_DEVELOPMENT_GUIDE.md
§
OmniRoute ~/.omniroute; dash :20128; `.env` perlu RATE_LIMIT_MAX_WAIT_MS=120000 (default 15s → cfr 504). bdb DISABLED; combo-cfr/-mix/-gratis; alias omni→combo-cfr. Compression caveman ON (tulis DB key_value ns=compression; route PUT AUTH_001). opencode Zen oc/: free cuma via omni executor. zaiplat → api.z.ai/api/paas/v4. keys {omniroute-api-key,gemini-key,free-keys}.txt; config.yaml agent-diblokir → hermes config set.