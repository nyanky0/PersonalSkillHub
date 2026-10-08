# Free-tier inventory (which upstreams cost nothing, and what they need)

## Where the truth lives

| Source | Holds |
|---|---|
| `GET /api/free-tier/summary` (admin token) | pool-level `steadyRecurringTokens` + `perModel[]`; the payload the dashboard free-tiers page renders |
| `<pkg>/open-sse/config/freeModelCatalog.data.ts` | one record per free model: `provider, modelId, displayName, monthlyTokens, creditTokens, freeType, poolKey, tos` |
| `<pkg>/open-sse/config/freeTierCatalog.ts` | per-vendor free-type policy + the `"avoid"` list |
| `omniroute -q --no-color providers available --json` | whole provider catalog: `hasFree`, `category`, `website`, `deprecated` |

CLI `--json` output is prefixed by env-loading banner lines (ANSI included) — parse from the first
`\n{` in the string, not from byte 0, and aggregate in code (hundreds of entries). The dashboard routes
(`/free-tier`, `/providers`) can answer `404` with an SPA fallback body while `/` and `/dashboard`
`307`-redirect: treat the API route as the source of truth rather than guessing dashboard URLs.

## Field semantics

- `freeType`: `recurring-uncapped` (no published monthly cap — best kind), `recurring-daily`,
  `recurring-monthly`, `first-month-credit` (one-off signup grant, not recurring).
- `poolKey`: models sharing one provider-side quota pool. Summing `monthlyTokens` across models in one
  pool double-counts — use the summary route's pool totals for headline numbers, per-model numbers only
  for relative weight.
- `tos`: `ok` / `caution` / `avoid`. Advisory only (see SKILL.md).

## Category → setup cost

| category | what it means for the user |
|---|---|
| `api-key` | vendor signup + key mandatory; free tiers here usually need no credit card |
| `noauth` | no credential; routing support varies — some ids exist only in the catalog |
| `oauth` | rides a consumer subscription/CLI login; highest ban risk |
| `web-cookie` | scrapes a web UI session; unstable and ToS-hostile |
| `search` | grounding/search tools, not chat models |
| `local` | local runtime (image/audio); no quota, needs the local service |

## Report shape for "what in here gives free AI?"

1. Headline counts: providers in the catalog, how many `hasFree`, pools/models in the free catalog,
   steady recurring tokens per month (pool-deduped, not summed per model).
2. Table of free models **reachable today** through already-installed providers, with quota + one-line caveat.
3. Table of free providers worth adding: signup URL, quota, free models, ToS flag.
4. The keyless short list split into "installs and answers" vs "listed but not implemented".
5. What still needs a credential from the user, as `provider=KEY` lines they can paste.

Label every row with what was actually verified by a completion call vs what is catalog data only.

## Batch-adding credentialed free providers

```bash
while IFS='=' read -r P K; do
  case "$P" in ''|'#'*) continue;; esac
  printf '%s' "$K" | tr -d ' \r\n' > "$HOME/.omniroute/.k.tmp"
  omniroute providers add "$P" --name "$P (free)" --credential-stdin --yes < "$HOME/.omniroute/.k.tmp"
  rm -f "$HOME/.omniroute/.k.tmp"
done < "$HOME/.omniroute/free-keys.txt"

omniroute -q --no-color providers list   # confirm each connection went active
```

Then smoke-test each new `prefix/model` with a realistic `max_tokens` and only keep the ones that answer
(`scripts/combo-append.py <combo> <id> ...`). Community/crowd-sourced free pools are hit-or-miss per
model: two ids from the same pool can differ between "answers in 3 s" and "504 after two minutes".

## Verifying "free" at the vendor

If a vendor's docs site publishes `/llms.txt`, fetch it for the page list, then take pages as `*.md`
(`curl https://docs.<vendor>/<page>.md`) — clean tables, while the HTML is an SPA shell that needs
tag-stripping. A pricing table's `Free` row (input/output/cache all Free) is the authoritative list of
model ids that cost nothing on that account tier, and it settles "free account vs paid plan" questions
without guessing. Vendor API-key pages are usually reachable directly
(`/manage-apikey/apikey-list`-style) and the key is the only datum the gateway needs.

## OpenCode Zen (provider `opencode`, prefix `oc/`)

- Keys: `https://opencode.ai/auth` → create API key (`sk-…`, not `oc_…`). Several accounts = several
  connections (`opencode`, `opencode2`, …) pooled as one prefix. `GET https://opencode.ai/zen/v1/models`
  is public (no auth) for id discovery.
- **The Zen free tier is client-locked.** A direct `POST …/zen/v1/chat/completions` with a valid key
  answers `400 MissingSessionID` — "OpenCode's free tier can only be used in OpenCode" — and paid ids
  answer `401 CreditsError` (no payment method). The omni `opencode` executor sends whatever session
  the gateway expects, so the SAME free ids answer 200 THROUGH omni (`oc/big-pickle` …) and fail
  direct. Register the provider, then test via `/v1/chat/completions` with model `oc/<id>` — never
  judge Zen free tier by a direct curl.
- `/v1/models` also lists `oc/` ids that do NOT serve: `hy3-free`/`north-mini-code-free` (`400 … not
  available in the active live catalog`), `deepseek-v4-flash-free` (upstream unavailable),
  `muse-spark-1.3-contributor-free` (500). Verified-serving free ids: `big-pickle` (strongest),
  `nemotron-3.5-lightning-free`, `nemotron-3-ultra-free` (1M ctx, slow — allow >120 s),
  `mimo-v2.5-free` + `ling-3.0-flash-fin-free` (reasoning models: output lands in `message.reasoning`,
  `content: null` at small `max_tokens` — naive parsers score them as failures and the combo rolls on;
  see the max_tokens pitfall in SKILL.md).
- Same rule for other catalog providers: an id listed in `/v1/models` can 404 at call time
  (measured: `gemini/gemini-2.5-flash` 404 while `gemini/gemini-flash-latest` and
  `gemini/gemma-4-26b-a4b-it` 200). Probe every entry once before pinning it in a combo; the combo
  survives dead entries via fallback but each attempt burns its timeout.
