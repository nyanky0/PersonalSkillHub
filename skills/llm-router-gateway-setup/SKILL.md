---
name: llm-router-gateway-setup
description: "Use when wiring a local LLM router gateway (combos, keys)."
version: 1.0.0
platforms: [windows, linux, macos]
---

# Local LLM Router Gateway Setup (OmniRoute / 9Router)

These gateways sit in front of N upstream OpenAI-compatible endpoints and expose one `/v1` on
localhost (default port **20128**). OmniRoute 3.x is the current name of the 9Router lineage —
same port, same `prefix/model` naming, same `sk-...` client keys — so the procedure below applies to
both. The task class is: add upstream credentials, expose every upstream model, fold several providers
into one combo, issue a key for a client tool, and prove routing works.

## The four config layers (in this order)

1. **connection / provider node** — upstream base URL + credential, gets a short **prefix**.
2. **provider** — node assignment + API key + `defaultModel`.
3. **combo** — ordered list of `prefix/model` ids exposed as ONE virtual model name.
4. **client key** — `sk-...` used by clients (Hermes, Cline, VS2022) against `http://localhost:20128/v1`.
5. **client wiring** — the client's own config gains the gateway as a named provider (base URL + key
   env + default model). A gateway no client points at is not finished; see "Wiring a client" below.

Clients may address models as `prefix/model`, or by a bare id when a combo carries that name.

## Procedure

1. **Record upstream truth BEFORE configuring anything.** Dump each upstream's own list with its own
   key: `curl -s -H "Authorization: Bearer $UPSTREAM_KEY" <baseUrl>/models -o m1.json`. Those counts
   are the yardstick you reconcile against in step 7 — without them you cannot claim "all models are
   exposed".
2. **Confirm the server owns the port.** `curl -s http://127.0.0.1:20128/api/health` →
   `{"status":"ok"}`. Start headless with `omniroute --no-open` in the background, then verify the
   listener PID actually holds 20128 — a previous instance may still own it and answer stale.
3. **Get admin auth right (two different credentials).** Admin routes take
   `x-omniroute-cli-token: <token>`; the token comes from the package's `bin/cli/utils/cliToken.mjs`
   → `getCliToken()`, and the call **must be awaited** (unawaited it prints `[object Promise]`). That
   token authorizes `/api/provider-nodes`, `/api/providers`, `/api/combos`, `/api/keys` — it does
   **not** authorize `/v1/*` or model-sync. Those need a real client key as `Authorization: Bearer`.
4. **Create the node, then the connection, then confirm the prefix.** `POST /api/provider-nodes`
   (`type:"openai-compatible"`, `name`, `prefix`, `apiType:"chat"`, `baseUrl`) returns 201 with the node
   id; only then `POST /api/providers` with `{provider: <that node id>, apiKey, name, defaultModel}`.
   The connection body carries **no** base URL — it is bound to the node. The `prefix` must not collide
   with a built-in provider id/alias (`zai`, `glm`, `gemini`, …): built-ins own `<prefix>/model`, so a
   collision is rejected with `400 … is a reserved provider prefix`; use `<vendor><role>` (`zaiplat`).
   Confirm the prefix appears in `GET /v1/models` before moving on.
   For a vendor the package already knows (`omniroute providers available --search <vendor>`), add it by
   **vendor id** instead of hand-building a node:
   `omniroute providers add <vendorId> --name "…" --credential-stdin --default-model <vendor-model-id> --yes < keyfile`.
   The package's own entry carries the endpoint, so **the credential is the only required datum** — read
   that entry (`src/shared/constants/providers/apikey/*.ts`) before asking the user for extra fields like
   project id, region, or billing: if the entry has no such field, the gateway does not want it, and the
   project id/number belong in the user's own quota console. Model ids surface as `<vendorPrefix>/<id>`.
   A connection added this way can come back `unknown` (and answer `401 No active credentials` at call
   time despite the key being stored encrypted) until activated: `omniroute providers edit <id> --active`.
5. **Fold providers into one combo and pin the default by ORDER.**
   `omniroute combo create <name> --strategy priority --models "a/deepseek...,b/deepseek..."`
   (or POST `/api/combos`). Entry order *is* the priority *is* the fallback order, and **entry 1 is
   the effective default model**. Re-read the combo afterwards (`GET /api/combos`) instead of
 trusting the create output.
 To add fallbacks to a **live** combo later (new vendor, new key) splice, do not rebuild: GET the
 combo, insert `{id, kind:'model', model:'prefix/model', providerId:'prefix', weight:0}` at the wanted
 index — after entry 1 whenever the user's declared default must survive — then
 `PUT /api/combos/<uuid>` with the full `{name, models, strategy, config}` object (200 = applied) and
 re-GET to confirm the entry count and order. Give inserted entries fresh unique ids; do not renumber
 the existing ones.
   When a model id itself contains slashes (e.g. Cloudflare `@cf/meta/llama-3.3-70b-…`), pass the
   splice entry as the OBJECT `{kind:'model', model:'<full id>', providerId:'<prefix>', weight:0}` — a
   `prefix/model` STRING splits on the first slash and yields a wrong `providerId` (`@cf`), so the
   entry never resolves.
   If the only key on hand is a routing key (see pitfall: inference-scoped `sk-` key), GET/PUT the
   combo through the CLI helpers instead — they auto-auth with the machine token:
   `omniroute --output json api combos get-api-combos` (note: `--output json` must precede the
   subcommand; output is ANSI banner lines then JSON — slice from the first bare `{` line), then
   `omniroute api combos put-api-combos-id- --id <uuid> --body "@$LOCALAPPDATA/Temp/body.json"`.
   The PUT body needs only `{"models": [...]}`; a models array replaces wholesale.
6. **Issue the client key and capture it at birth.** POST `/api/keys {"name":"..."}`; write the
   returned value straight into a file inside the gateway data dir and tell the user the path. Never
   echo the raw key into the transcript or onto a shell command line.
7. **Verify end to end, then report.** Per-prefix model counts vs step 1; a chat completion through
   the combo name with a realistic `max_tokens`; and the serving entry confirmed from the log/DB
   (see `references/omniroute-cli-api.md`).

## Verification rules (this is where the honesty lives)

- **Reconcile counts per prefix, and explain the extras.** Gateways synthesize auxiliary model ids
  (per-effort twins like `-low/-medium/-high/-xhigh` of one base model, provider `auto` entries), so
  a gateway count above the upstream count is normal. Report the delta per prefix as
  "N upstream + M synthetic" rather than silently showing a bigger number.
- **The `model` field in a response is not proof of what served.** It can echo the combo alias or a
  fallback entry. Determine the serving entry from the application log (`Trying model N/M: ...`,
  `succeeded (Xms, Y fallbacks)`) or the sqlite `session_model_history`.
- **State what is NOT done.** Admin dashboard password not yet created, host still bound to `0.0.0.0`,
  clients not yet pointed at the gateway — list these explicitly at the end instead of presenting the
  plan as complete.

## Adding free capacity (free-tier inventory)

When the ask is "what in here gives free AI / add the free ones to my combo", the gateway ships its own
audited free-model catalog — read it, never infer from the UI or from a vendor's marketing:

- **`hasFree` is a flag, not connectability.** Category `api-key` means a credential from that vendor is
  mandatory; `providers add <id>` without one fails (`Invalid request`), and some `noauth` catalog ids
  have no routing implementation at all (`Invalid provider`). Only add + a real
  `POST /v1/chat/completions` proves a provider works — plan the report around verified entries.
- **`tos: "avoid"` is advisory and does not block routing** — those providers still serve and still sit
  in combos by default. Surface the flag and let the user choose; do not silently include or exclude.
- **Check where the free models actually live before promising them.** Endpoint + auth for a
  vendor-preset provider live in `open-sse/config/providers/registry/<vendor>/index.ts`. A preset can
  point at a *subscription* endpoint while the vendor's free tier sits on its general platform endpoint
  (measured case: the `glm` preset targets the coding-plan path, while the free Flash models are on the
  general platform path) — the key is valid but the route rejects it. Fix is a custom
  OpenAI-compatible node at the platform base URL, not a different credential.
- **A vendor's own docs/example may showcase a model that is NOT free on that account tier.**
  Cloudflare's Workers AI REST example uses `@cf/moonshotai/kimi-k2.7-code` — that id answers 403
  (upgrade plan) while `llama-3.3-70b-fp8`, `qwen2.5-coder-32b`, `qwq-32b`, `glm-4.7-flash` and
  others on the same account answer 200. Trust the registry's model list + a per-id probe, never the
  vendor's marketing curl. See `references/free-tier-inventory.md` → Cloudflare / OpenCode Zen for the
  credential shapes (Workers AI needs `accountId` + `cfut_`-prefixed token, passed as
  `--provider-specific-data '{"accountId":"…"}'`; a `cfk_`-prefixed key is the account-level Global
  API key, Bearer-incompatible, and will fail the token-verify endpoint).
  what the account can *address*, not what is free — the same key on the correct endpoint answers `200`
  for some ids and `429 {"code":"1113","message":"Insufficient balance or no resource package"}` for
  their siblings. Ground truth for the free set is the pricing page's per-model input/output/cache
  **Free** column, then one direct `curl` at `<platformBaseUrl>/chat/completions` per id before adding
  it to a combo. Free Flash tiers also run at concurrency 1–2 and 15–25 s per answer: tail-of-combo
  fallback, not a parallel workhorse.
- **Split combos by tier instead of building one giant list.** The shape a user actually picks from is
  three names: the paid/subscription upstream alone, that upstream plus all the free capacity, and free
  capacity alone (`combo-cfr` / `combo-mix` / `combo-gratis`). Inside the mixed combo the free entries go
  FIRST and the paid champion LAST — free quota is finite and should be burned before the metered
  upstream, which is the opposite of the tail-append rule below. Both orders are legitimate; ask which one
  the ask implies (or build both variants) rather than assuming.
- **"Default model" and "entry 1" can point at different entries.** When the free-first order is in play,
  the id the user calls their default (`deepseek-v4.1-flash`) is the tail entry, so quoting ".models[0]"
  as "the default" misreports the setup: state entry 1 (what actually serves first) AND the declared
  default id separately in the report.
- **Append free/community models at the TAIL, after the user's declared champion, and verify each one
  before keeping it.** A dead entry in a priority combo is not inert: every fallback through it burns
  its timeout (measured 120 s before control moved on), and a payload-rejecting entry never serves at
  all. Remove entries that 504 or reject instead of leaving them "for later".
- **Batch credentials through files.** One `provider=KEY` file, then loop
  `providers add <id> --credential-stdin --yes < tmpfile` — never the key on the command line. Fold the
  resulting ids into the combo with `scripts/combo-append.py` (idempotent; preserves entry 1 and order).

Commands, field semantics, category table and the report shape for a "what's free in here?" answer:
`references/free-tier-inventory.md`.

## Pitfalls

- **Raw keys are unrecoverable after creation.** `POST /api/keys` responses, the dashboard, and the
  sqlite `api_keys.key` column all hold a MASKED value (the column stores mask + hash). Capture the
  raw value at creation time in a file; never plan to "look it up later".
- **Regenerating a key kills the old value instantly.** Clients still holding the previous value start
  returning `401 invalid_api_key`, and any scratch file with the old value is now stale garbage. After
  a rotate, overwrite the file the clients read and re-point every consumer.
- **A 401 on `/v1/models` with a "working" key is a stale/masked value, not a broken server.** Check
  which string the client actually sends before touching gateway state.
- **The gateway's client key (`omniroute-api-key.txt`, `sk-…`) is inference-scoped: `/v1/*` answers
  200, `/api/*` answers `403 Invalid management token`.** Do not debug combo/admin operations through
  it, and do not blame a hand-rolled combo script that only holds it — the fix is the CLI `api`
  subcommand (machine-token auth) or a manage-scoped key from the dashboard.
- **A tiny `max_tokens` can make a passing smoke test lie.** A 200 whose content is empty (reasoning
  ate every output token) is scored as a failed attempt and the combo silently rolls to the next
  entry — you think you validated the default and actually exercised a fallback. Use a realistic
  `max_tokens` and read the log for which entry succeeded.
- **A 504 on a combo whose upstream answers 200 is the local rate-limit queue timing out, not a broken
  combo or a defective provider.** The queue caps how long a request may WAIT before dispatch at
  `RATE_LIMIT_MAX_WAIT_MS`, default **15000 ms**, so an upstream that legitimately takes ~20 s never gets
  to answer, the entry is scored failed and control rolls on (measured: `cfr/deepseek-v4.1-flash` 200 in
  19.9 s direct, 504 through the combo). Raise it in the data-dir `.env` → `RATE_LIMIT_MAX_WAIT_MS=120000`,
  restart, re-test; the fix is proven when the combo answers 200 with a `time_total` LARGER than the old cap.
- **Default bind can be `0.0.0.0`.** `/v1` still requires a client key and the dashboard requires
  login, but anything on the LAN can reach the admin surface if unauthenticated. For a single-machine
  setup put `OMNIROUTE_SERVER_HOST=127.0.0.1` in the data-dir `.env` and restart.
- **`curl -o` writes nothing to an MSYS-style path.** Native Windows `curl` receives `/c/Users/...`
  verbatim (no path translation), so the response body is lost and no file appears. Send scratch output
  to `$LOCALAPPDATA/Temp/<file>` or a `C:/...` path, and read `HTTP=200 bytes=0` plus a missing file as
  the tell rather than as an empty response from the server.
- **`omniroute providers test <id>` answers "Provider test not supported" for vendor-catalog providers**
  (the probe covers some types only). Prove the credential with a real call instead: `POST /v1/chat/completions`
  with `model: "<prefix>/<vendor-model-id>"` and a realistic `max_tokens`.
- **Reverse-engineering the installed package: search targeted dirs, never the tree.** The package is
  ~0.5 GB with a bundled `dist/`, and a recursive `grep -r` over it times out (exit 124) without
  answering. Read `open-sse/config/providers/registry/<vendor>/index.ts` for the real base URL, auth
  header and model ids, and `src/shared/constants/providers/apikey/*.ts` for the display entry. When the
  string you want is an error from the **running server**, don't grep for it — probe candidate routes for
  their status codes (`GET /api/provider-nodes` → 200 vs `/api/providers/nodes`, `/api/nodes`,
  `/api/compatible-nodes` → 404) and read the response body.
- **Park, do not delete, a connection whose endpoint rejects the credential.** A vendor preset aimed at
  a subscription endpoint (resource-package wall) fails every call while the key itself is fine; keep it
  for the day the user upgrades and set `PATCH /api/providers/<id> {"isActive": false}` so it stops
  burning attempts and polluting the log.
- **A provider just added via `providers add` can sit in `unknown` status and answer `401 No active
  credentials` even though the key is in the DB** (`provider_connections.api_key` = `enc:v1`). Fix:
  `omniroute providers edit <id> --active`. `providers test <id>` replying "Provider test not
  supported" is normal for catalog providers — prove the credential with a real completion through
  `/v1` (`oc/big-pickle`, `prefix/model` of the provider's verified id).
- **`providers edit <id> --inactive` flips the DB (`is_active=0`) but `providers list` may keep
  printing `active`** — stale display on some versions, the table is not authoritative. Confirm
  disablements in sqlite (`provider_connections.is_active`), not from the CLI table.
- **Settings WRITE routes reject the CLI machine token that read routes accept.** `PUT
  /api/settings/compression` answers `AUTH_001 Authentication required` / `Unauthorized`, and the GET can
  answer `{}` — those handlers want an interactive dashboard admin session (a fresh install has
  `requireLogin=true`) while the CLI token is machine/inference-scoped, so no key the agent can mint
  unlocks them. The settings are plain rows in `storage.sqlite`, so set them there instead of reporting
  "knobs found, auth pending": back up the DB, then write the target namespace's `key_value` rows with
  JSON-encoded values and re-read. Recipe + key list: `references/compression-token-saver.md`.
- **`omniroute restart` can outlive a foreground call indefinitely** while the old process releases the
  port, and looks hung. The restart still completes in the background — poll `GET /api/health` and
  `~/.omniroute/supervisor/.pid` before re-issuing the command, or you start a second server.
- **Prefer the HTTP admin API over the CLI** once a subcommand stops producing parseable output
  (`--output json` exiting 1, ANSI-wrapped tables). The route handlers are the stable contract.

## Wiring a client

Point the client at `http://127.0.0.1:20128/v1` as a **named custom provider**; do not reuse the
client's top-level `model.base_url` — that key belongs to a single upstream, not to the router.

1. Put the client key in the client's own secret file (Hermes: `$HERMES_HOME/.env`) under a name
   matching its existing convention (`HERMES_CUSTOM_<SLUG>_API_KEY`). Append it from a script that
   preserves the file's line endings and dedupes by variable name, so a re-run cannot stack copies.
2. Create the provider with the client's own config command (`hermes config set providers.<slug>.<field>`
   for `name`, `base_url`, `model`, `discover_models`, `key_env`). Never hand-edit the client's config
   file. The gateway's combo name is the provider's `model` — that is how the combo becomes the default.
3. Verify with real runs through the client, not by re-reading config: one-shot chat with the combo,
   then again **without** a model flag (proves the provider default resolves), then once with an id
   outside the declared list.
4. Pin a small curated model set instead of exposing everything: pickers cap and allowlist what they
   list, and "combo name + the two fallback ids behind it" is what a user actually picks from.
5. Leave the client's default model for the user to choose. Switching a client's default to a
   localhost gateway makes every session depend on the gateway being up — offer the switch and the
   gateway's autostart together.

Exact commands, verification snippets and client quirks: `references/client-wiring-hermes.md`.

## References

- `references/omniroute-cli-api.md` — routes, payloads, CLI commands, log/DB verification queries.
- `references/upstream-tos-risk.md` — answering "is provider X bannable if driven through here?".
- `references/free-tier-inventory.md` — free-tier catalog routes/files, category→setup table, free report shape.
- `references/compression-token-saver.md` — enabling the built-in prompt-compression (Caveman) engine straight in the settings DB, key list, verification.
- `scripts/combo-append.py` — idempotently append `prefix/model` ids to a live combo via the admin API.
- `references/client-wiring-hermes.md` — wiring Hermes to the gateway: config commands, verification, quirks.
