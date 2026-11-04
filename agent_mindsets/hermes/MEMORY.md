Prinsip kerja user: pakai helper yg sudah ada (mis. Utils.CreateUDF), jangan bikin wrapper sendiri; fix seminimal mungkin, jangan refactor blok lain; tiap fix wajib diuji dampaknya (gejala asli hilang + cek efek samping) sebelum klaim selesai.
§
IBT: app kapal (offline) → web app HUAWEI Cloud remote desktop (orang kantor) → SAP Integration Hub (scheduler, HUAWEI) → SAP B1 Service Layer. Acuan: docs/development/AI_DEVELOPMENT_GUIDE.md
§
LLM: CFRouter custom2 = key lama ...974a18 (non-TRIO); custom3 = key TRIO ...61e09f (HERMES_CUSTOM_CUSTOM3_API_KEY). Alias trio-glm/trio-ds/trio-luna → custom3. OmniRoute :20128.
§
Antigravity 2.0: Office Game :3210 (scratch/office-game). Tim virtual — Mas Eko (Laravel), Arya (React/Inertia), Mbak Siti (UI), Pak Budi (SAP B1), Rei-san (QA/Sec), Kevin (DevOps).
§
Laravel IBT: v11.56.1, PHP 8.4, support 2 thn seragam (1 bugfix+1 security). Cek laravel.com/docs/<ver>/releases, jangan dari ingatan.
§
Nyan-mem grill: one focused question/turn; record decisions in `C:\Users\yudah\.nyan-mem\docs\ui-ux-grill.md`; distinguish proposals from approved choices; wait for approval before implementing.
§
User expects authorized local service restarts (e.g. MCP) handled autonomously: check port/process, restart safely, verify health/tools/dashboard/DB integrity; skip step-by-step progress reports when they say continue, but report completion and remaining blockers at the end.
§
For feature/creative work and multi-step plans, use brainstorming before choosing behavior and writing-plans before implementation; skip for simple questions.
§
When modifying existing code, if edits spiral or tests reveal unrelated/pre-existing failures, stop, compare the full diff against HEAD, revert only the agent's unintended edits, and rerun focused plus baseline tests before claiming completion.
§
IBT rates RL line quantities as whole numbers: RequisitionListRequest rules lines.*.quantity/qty_buy/qty_transfer as `integer` while DB columns are decimal(18,4). Numeric+decimal:N is a pending business decision, not a bugfix.
§
IBT app UI must be fully English — no Indonesian copy in resources/js or resources/views.