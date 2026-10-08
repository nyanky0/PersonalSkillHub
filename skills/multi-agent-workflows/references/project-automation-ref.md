# Project Automation — Reference (2026-09-07)

## 9Router Config

**Base URL:** `http://172.26.176.1:20128/v1` (WSL: Windows host IP, NOT localhost)
**API Key:** `sk-e15710fc0fb1da0e-3h140a-b0417849` (user's key — update as needed)
**⚠️ Always include `"stream":false`** — without it, response is SSE garbage, not JSON.

## Model Combo Prefixes

| Prefix | Provider |
|--------|----------|
| `KIR/` | Kiro routed models |
| `CF/` | CFRouter models |
| `tes/` | Tesla models |
| `ds/` | DeepSeek direct |
| `glm/` | GLM direct |

## Verified Working Models (balance checked 2026-09-07)

| Model | Status | Best for |
|-------|--------|----------|
| `KIR/minimax/minimax-m3:free` | ✅ OK | PM, architect, backend |
| `KIR/minimax/minimax-m2.7:free` | ✅ OK | frontend, lighter tasks |
| `KIR/minimax/minimax-m2.5-highspeed:free` | ✅ OK | fast responses |
| `tes/auto` | ✅ OK | auto-fallback |
| `CF/deepseek-v4-flash-0731` | ⚠️ slow | paid, test first |
| `ds/deepseek-v4-flash-0731` | ❌ Insufficient Balance | — |
| `glm/glm-5.1-flash` | ❌ No active credentials | — |
| `kr/kimi-k3` | ❌ 403 Forbidden | — |

## Test a Model

```bash
curl -s --max-time 15 \
  -H "Authorization: Bearer sk-e15710fc0fb1da0e-3h140a-b0417849" \
  -H "Content-Type: application/json" \
  -d '{"model":"KIR/minimax/minimax-m3:free","messages":[{"role":"user","content":"hi"}],"stream":false}' \
  http://172.26.176.1:20128/v1/chat/completions
```

## Running Server

```bash
cd /home/maulana/project-automation
~/.venvs/project-automation/bin/uvicorn server:app --host 0.0.0.0 --port 8765
```

## Web UI

http://localhost:8765

## Output Location

`/home/maulana/project-automation/output/<project_name>/`

## Debug: List Available Models

```bash
curl -s -H "Authorization: Bearer sk-e15710fc0fb1da0e-3h140a-b0417849" \
  http://172.26.176.1:20128/v1/models
```
