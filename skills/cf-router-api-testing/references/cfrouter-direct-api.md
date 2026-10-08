# CFRouter — direct API (bypass any local router)

The user's production path is DIRECT to CFRouter. Do not route CFRouter work
through a local router unless asked: the extra hop adds latency and rewrites model
names.

## Endpoints
- Base: `https://api.cfrouter.my.id/v1` (mirror `https://api.cfrouter.site/v1`)
- Auth: `Authorization: Bearer <key>`. Key sits in `~/.omniroute/free-keys.txt` or
  `~/.omniroute/*-key.txt`. Pass it via an env var in scripts, never hardcode it.
- OpenAI-compatible: `GET /v1/models`, `POST /v1/chat/completions`.

## Rule: model names are exact, and /v1/models is the source of truth
`GET /v1/models` returns the authoritative id list (~25). Never guess a variant:
`deepseek-v4-pro` is NOT served — the real id is `deepseek-v4-pro-0813`.
A stale name fails as `HTTP 404 {"error":{"message":"Upstream temporarily unavailable"}}`,
which reads like an outage but is a name mismatch. Fetch the catalog first, then
iterate it — that removes the entire class of bug.

## Rule: detect aliasing with the response `model` field
The response `model` echoes the id actually served.
- request `qwen3.8-max` -> response `deepseek-v4.1-flash` => something in the middle aliased it
- request `solar-pro4`   -> response `solar-pro4`           => served as-is
Direct CFRouter requests come back unchanged. Prefixes such as `cfr/`, `oc/`,
`opencode/`, `auto/` are router-side namespaces — the provider catalog never
contains them, so strip them before testing a provider directly.

## Quota multiple (billing multiplier, not a rate limit)
Non-GPT models cost x2. The GPT family is charged more, tiered by request input size.

| Model          | <=272k input | >272k input |
|----------------|--------------|-------------|
| gpt-5.6-sol    | 2x           | 4x          |
| gpt-6-luna     | 2x           | 4x          |
| gpt-6-sol      | 6x           | 10x         |
| gpt-6-astra    | 6x           | 12x         |
| non-GPT models | 2x           | 2x          |

Context limit is 272k input per request. A 6x flagship burns quota 3x faster than
a standard model before output length is even counted — never make it the default
model, and say so explicitly when recommending one.

## Usage / quota reporting
There is no public usage API: `/api/usage`, `/api/v1/usage`, `/v1/usage`,
`/api/user/usage`, `/api/stats` all 404 and `/usage` 301s to the SPA. Measure by
reading the `usage` object (prompt_tokens / completion_tokens) out of each chat
response — per-request truth, no extra endpoint. The web dashboard at
`https://cfrouter.my.id/` shows history but needs the key pasted into the browser.

## Measuring cost-efficiency
Efficiency = completion_tokens / prompt_tokens, on the SAME prompt for every model.
Watch prompt_tokens: a model whose input count is wildly above its peers for an
identical short prompt is doing hidden reasoning and will bill for it (observed:
one flagship at ~4.8k input against ~0.4-0.7k for its peers, same 18-word prompt).

## Expert cross-check sources (for "which model is better" questions)
- `quesma.com` Baba Is Bench — pass@1 plus turns / output tokens / total cost
- `modelmarkets.ai/compare/<a>-vs-<b>` — head-to-head: ARC-AGI, LMArena, LiveBench
- `techtimes.com/ai-benchmarks` — Artificial Analysis Intelligence Index, ECI, FrontierMath
- `codingfleet.com` DeepSWE leaderboard — agentic coding pass@1
- `o-mega.ai/articles` — pricing guides with per-MTok cost tables

Report the user's own latency/usage numbers alongside vendor claims; they diverge.
Reasoning-effort labels (`high`, `medium`) are NOT separate model ids — they are
thinking-budget settings on one model, and they only exist on the vendor's own API.

## Answer shape the user expects
"Which is better / more efficient — test it." Deliver: (1) availability check
against `GET /v1/models`, (2) per-model time + prompt/completion tokens + efficiency
ratio on one shared prompt, (3) ranking by both speed and efficiency, (4) the
expert-benchmark verdict, (5) an explicit pick per use case and what to skip.
