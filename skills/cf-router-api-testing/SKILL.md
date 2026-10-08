---
name: cf-router-api-testing
description: "Use when testing or wiring CF Router (cfrouter) models. Direct API checks, catalog facts, quota multiples."
version: 2.0.0
platforms: [windows, linux, macos]
---

# CF Router API Testing

CFRouter is an OpenAI-compatible gateway. Test models **directly** against it — an intermediate router (OmniRoute etc.) adds a proxy layer that changes model names and adds latency.

## Endpoints

- Base: `https://api.cfrouter.my.id/v1` (mirror `https://api.cfrouter.site/v1`)
- Auth: `Authorization: Bearer sk-...` — key from the `@CFrouter_bot` Telegram bot
- Catalog is small and fixed (~25 models). Always fetch the live list rather than trusting a saved one.

## Procedure

```bash
KEY=sk-...
# 1. live catalog
curl -s -H "Authorization: Bearer $KEY" https://api.cfrouter.my.id/v1/models \
  | python3 -c "import sys,json;print('\n'.join(sorted(m['id'] for m in json.load(sys.stdin)['data'])))"
# 2. per-model chat probe
curl -s -H "Authorization: Bearer $KEY" -H "Content-Type: application/json" \
  -d '{"model":"glm-5.3","messages":[{"role":"user","content":"Reply: pong"}],"max_tokens":10}' \
  https://api.cfrouter.my.id/v1/chat/completions
```

Read `usage` from each response — that is the only programmatic token accounting available.

## Facts that matter

- **Model names are ORIGINAL at CFRouter — no masking.** The response `model` field equals the request name. Masking such as `qwen3.8-max` → `deepseek-v4.1-flash` is an **OmniRoute** proxy artifact, not CFRouter behaviour. Do not blame CFRouter for names changing.
- **Dotted / suffixed names must match exactly.** `deepseek-v4-pro` → HTTP 404 `Upstream temporarily unavailable`; `deepseek-v4-pro-0813` works. Likewise `deepseek-v4-flash-0731`. A 404 here means wrong name, not a dead provider.
- **Catalog rotates — always fetch `/v1/models` live, never trust a saved list.** Verified Oct 2026: `gpt-6-luna`, `deepseek-v4.1-flash`, `glm-5.3-flash`, `gpt-5.6-sol` are GONE (probe → `model_not_found`); current live list is only ~19 models (see `gpt-6-astra`, `gpt-6-sol`, `claude-opus-5`, `hy4-preview`, `minimax-m2.7`, `qwen3.8-omni-flash`, `qwen3.8-27b`, `agnes-3.0-flash`, `apodex-1.1`, `mimo-v2.6-flash`). A stale model returns `model_not_found`, not a proxy error.
- **`gpt-6-*` are OpenAI-lineage models on CFRouter** — not aliases to DeepSeek.
- **Quota multiples burn the plan, they are not free:**

  | model | ≤272k input | >272k input |
  |---|---|---|
  | most non-GPT models | 2× | 2× |
  | `gpt-5.6-sol`, `gpt-6-luna` | 2× | 4× |
  | `gpt-6-sol` | 6× | 10× |
  | `gpt-6-astra` | 6× | 12× |

- **No public usage API.** `/api/usage`, `/api/v1/usage`, `/v1/usage`, `/api/user/usage`, `/api/stats` all 404; `/usage` 301s to a SPA. Token totals come from the dashboard (`https://cfrouter.my.id/`, paste the key in a browser) or per-response `usage`.
- **Flaky models (verified Sep 2026):** `gemini-3.8-flash` intermittently returns non-JSON; `muse-spark-1.3` → HTTP 400; `gpt-6-sol` and `gpt-5.6-sol` frequently hit the ~20s upstream timeout. Treat them as best-effort, not defaults.

## Measured token efficiency (identical prompt, Sep 2026)

| model | wall | input tok | output tok | out/in |
|---|---|---|---|---|
| deepseek-v4-flash-0731 | 4.3s | 403 | 290 | **0.72** |
| deepseek-v4.1-flash | 8.2s | 704 | 364 | 0.52 |
| deepseek-v4-pro-0813 | 6.0s | 402 | 173 | 0.43 |
| gpt-6-astra | 21.2s | 4775 | 176 | 0.04 |

`gpt-6-astra` billed ~4775 input tokens for an 18-word prompt — combine that with its 6× multiple before making it a default. Cheapest + fastest reliable is `deepseek-v4-flash-0731` (best all-round `deepseek-v4.1-flash` has since been retired — see catalog-rotation note).

## Registering models into Hermes

Set the provider's model map with a JSON value, because `hermes config set` splits the key on `.` and would nest dotted model names:

```bash
hermes config set providers.custom2.models \
  '{"glm-5.3": {}, "qwen3.8-max": {}, "deepseek-v4-pro-0813": {}}'
hermes config set model.aliases.cf-astra 'custom2/gpt-6-astra'
```

Alias *keys* have no dots, so per-alias dotted paths are safe. Re-read `config.yaml` after batch sets to confirm nothing got nested.

## Wiring a (new) key into Hermes — full order

1. **Always verify the key live first** — `GET /v1/models` + one chat probe with the new key BEFORE writing any config. If the probe 401s, stop: the key is dead and no config change is needed.
2. **Store the key in `.env`, never in `config.yaml`.** Convention: env var `HERMES_CUSTOM_<PROVIDERNAME>_API_KEY` (provider `custom2` → `HERMES_CUSTOM_CUSTOM2_API_KEY`), referenced via `key_env:` in the provider block. If an equivalent key for the same host already exists in `.env` (compare prefix/suffix — read values through python, not raw `read_file`, which redacts `sk-` secrets), reuse it; do not create a second credential slot for one host.
3. **Register the models + aliases** (previous section). For a key tied to a named package/plan, give aliases plan-scoped names (e.g. `trio-glm` → `custom2/glm-5.3-flash`) so `/model` stays self-documenting.
4. **De-duplicate before adding credentials.** If an `auxiliary.*` block (or any config section) already carries a literal `api_key:` + `base_url:` equal to a provider's, delete the literals and let the block resolve through the provider's `key_env` — a literal secret duplicated in config.yaml is a stale-credential trap the moment the `.env` key rotates.
5. **Config changes apply next session only** (prompt caching) — tell the user the current session keeps its model; aliases are testable from the next session via `/model <alias>`.

## Pitfalls (config side)

- `read_file` and `terminal` output redact `sk-…` secrets — you cannot see full values to compare keys. Read them in-process (python open+compare, print prefix/suffix only) and patch with a regex anchored on the env-var name, never on the secret literal.
- A model missing from `/v1/models` that belongs to the key's advertised package usually means the package is not yet activated server-side — still register the model + alias so it works the moment the gateway lists it, but tell the user it is not live yet rather than claiming the wiring failed.
- **Duplicate skills exist for this domain:** `cf-router-api-testing` is present both at top level and under `backend/` (same name, two copies). They drift independently — patch whichever the session loaded and note the divergence; consolidation belongs to the curator.
