---
name: logfare
version: "1.0.0"
description: Use when integrating the Logfare free API gateway.
---

# Logfare API (`logfare.ai`)

Free OpenAI-compatible API gateway. **Key trait: NO user rate limit — but ALL requests are logged by the service** (jangan kirim data rahasia).

## Auth

- Key format: `lfu_…` (register gratis di logfare.ai; tanpa web UI pun bisa via `POST /v1/auth/register`).
- Header: `Authorization: Bearer lfu_…` (endpoint `/v1/messages` juga terima `x-api-key`).
- `GET /v1/models` — list model, **tanpa auth**.

## Base URL

`https://logfare.ai/v1` (OpenAI-compatible: `OpenAI(base_url="https://logfare.ai/v1", api_key=…)`)

## Endpoints

| Method | Endpoint | Fungsi |
|---|---|---|
| POST | `/v1/chat/completions` | Chat (SSE streaming `stream:true`) |
| POST | `/v1/completions` | Legacy completion |
| POST | `/v1/messages` | Anthropic-style (`x-api-key` + `anthropic-version: 2023-06-01`) |
| POST | `/v1/responses` | OpenAI Responses API |
| POST | `/v1/images/generations` | Image gen (`model`, `prompt`, `n`, `size` "WxH", `steps`, `response_format` b64_json|url) |
| POST | `/v1/images/edits` | Edit image |
| POST | `/v1/audio/speech` | TTS (`model`, `input`, `voice`) |
| POST | `/v1/audio/transcriptions` | STT (multipart) |
| POST | `/v1/embeddings` | Embedding (`model`, `input`) |
| GET | `/v1/models` | List model (no auth) |
| GET | `/v1/status` | Health status |

## Free models (tier 1, tanpa opt-in)

**Chat:** `logfare/auto` (alias `auto`, `logfare/random` — auto-routing ke model terbaik sesuai kualitas, fallback berantai kalau provider gagal), `mimo-v2.5`, `gemma-4-26b`.

**Image:** `flux-1-schnell` (generations only), `flux-2-dev`, `flux-2-klein-4b`, `flux-2-klein-9b`, `sdxl-lightning` (generations + edits, kecuali flux-1-schnell).

**Tier 2 (butuh `training_optin` → 403 `training_optin_required`):** `kimi-k2.6`, `qwen-3.8-27b`, `glm-5.3`, `moondream3.1`, `whisper-large-v3-turbo`. Standard model tetap jalan tanpa opt-in.

## Error codes

| Status | Type | Arti |
|---|---|---|
| 401 | authentication_error | Key salah/hilang |
| 403 | permission_error | Model tidak tersedia utk key / butuh opt-in |
| 404 | not_found_error | Model tidak ditemukan |
| 429 | rate_limit_error | Provider overloaded (bukan rate limit user — retry) |
| 5xx | server_error | Upstream error — coba model lain |

## Wiring di OmniRoute

```bash
omniroute providers add logfare --name "logfare (free)" --credential-stdin --default-model logfare/auto --yes
# tes langsung via gateway:
curl -s http://localhost:20128/v1/chat/completions -H "Authorization: Bearer $LFU_KEY" \
  -H 'Content-Type: application/json' -d '{"model":"logfare/auto","messages":[{"role":"user","content":"hi"}]}'
```

Masuk combo: `python combo-add.py combo-utama logfare/auto logfare/gemma-4-26b`.

## Pitfalls

- Model reasoning (`logfare/auto`, `gemma-4-26b`) mengisi **`reasoning_content`**, field `content` bisa kosong → normal, bukan error.
- `mimo-v2.5` pernah 429 "Provider overloaded" sesaat → retry.
- `combo-add.py` butuh env `OMNI_CLI_TOKEN`; tanpa itu → **HTTP 403 Forbidden**.

## Account API (tanpa web UI)

`POST /v1/auth/register` {username, password} → dapat key; juga `/v1/auth/login`, `/v1/auth/me`, `/v1/auth/regenerate-key`, `/v1/auth/consent`, `DELETE /v1/me/delete`.
