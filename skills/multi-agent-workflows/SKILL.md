---
name: multi-agent-workflows
description: "Build 9Router multi-agent pipelines with FastAPI + SSE UI."
tags: [9router, multi-agent, workflow, fastapi]
source: session
date_added: "2026-09-07"
---

# Multi-Agent Workflows (9Router)

> ⚠️ **Superseded.** For current working implementation use skill: **`9router-agents`** (autonomous-ai-agents category). That skill has verified templates, correct WSL IP handling, async callback patterns, and working model configs.

## Quick redirect

The working project is at `/home/maulana/project-automation/`:
- Server: `http://localhost:8765`
- Run: `~/.venvs/project-automation/bin/uvicorn server:app --host 0.0.0.0 --port 8765`
- 9Router base: `http://172.26.176.1:20128/v1` (WSL: use Windows host IP, NOT localhost)

## Legacy notes (may be stale — see 9router-agents)

- Model combo format: `ds/deepseek-v4-flash-0731`, `glm/glm-5.1-flash`, `kr/kimi-k3`
- File extraction: `re.search(r"### FILE:\s*(.+)", raw)` + strip fences
- SSE via `sse_starlette.sse.EventSourceResponse`
- Background task callback: `lambda phase, data: asyncio.create_task(queue.put(...))` — **BROKEN**, see 9router-agents for correct async pattern

> **Do not use the legacy patterns above** — the current working version uses `stream=False`, path-fallback from task title, longest-fence code extraction, and properly awaited async callbacks. See `9router-agents`.


# Multi-Agent Workflows (9Router)

Build sequential multi-agent pipelines where each agent role routes to a different model via 9Router, with a FastAPI web UI streaming progress via SSE.

## When to Use

- User wants a team of AI agents with distinct roles working sequentially
- Need a web UI to monitor real-time agent progress
- 9Router available as local proxy (http://localhost:20128/v1)
- Output: generated code files written to disk

## Architecture Pattern

```
User Input
    │
    ▼
[ PM Agent ]      → deepseek-v4-flash (ds/)
    │              Breaks requirement into tasks
    ▼
[ Backend Dev ]   → glm-5.1-flash (glm/)
    │              Writes backend code per task
    ▼
[ Frontend Dev ]  → deepseek-v4-flash (same or diff model)
    │              Writes frontend code per task
    ▼
[ QA Reviewer ]   → kimi-k3 (kr/)
    │              Reviews all generated code
    ▼
[ Architect ]     → deepseek-v4-flash
                    Consolidates, resolves conflicts
    ▼
Files written to output/
```

## File Layout

```
project-automation/
├── config.py        # AGENTS dict, SYSTEM_PROMPTS, OUTPUT_DIR
├── router.py        # 9Router OpenAI-compatible client
├── orchestrator.py  # Sequential pipeline + file writer
├── server.py        # FastAPI + SSE endpoints
├── templates/
│   └── index.html   # Web UI (dark, pipeline progress bars)
├── run.sh           # Launcher script
└── output/          # Generated project files
```

## Working Config (verified 2026-09-07)

**WSL: use Windows host IP, NOT localhost.**
```python
# config.py
ROUTER_BASE = "http://172.26.176.1:20128/v1"  # Windows host IP from WSL
ROUTER_API_KEY = "sk-e15710fc0fb1da0e-3h140a-b0417849"  # from 9Router dashboard

# Working free models (most paid DS/GLM/Kiro return Insufficient Balance):
AGENTS = {
    "pm":        "KIR/minimax/minimax-m3:free",
    "backend":   "KIR/minimax/minimax-m3:free",
    "frontend":  "KIR/minimax/minimax-m2.7:free",
    "qa":        "KIR/minimax/minimax-m3:free",
    "architect": "KIR/minimax/minimax-m3:free",
}
```

Verify model works:
```bash
curl -s --max-time 10 \
  -H "Authorization: Bearer $ROUTER_API_KEY" \
  http://172.26.176.1:20128/v1/chat/completions \
  -d '{"model":"KIR/minimax/minimax-m3:free","messages":[{"role":"user","content":"hi"}],"stream":false}'
```

## 9Router Client Pattern — stream=False REQUIRED

```python
# router.py — stream=False or response is SSE garbage
async def chat_complete(model: str, messages: list) -> str:
    async with httpx.AsyncClient(timeout=120) as client:
        resp = await client.post(
            f"{ROUTER_BASE}/chat/completions",
            json={"model": model, "messages": messages, "stream": False},
            headers={"Authorization": f"Bearer {ROUTER_API_KEY}"}
        )
        return resp.json()["choices"][0]["message"]["content"]
```

## Orchestrator — async emit() callback (NOT lambda)

```python
# orchestrator.py
async def run_workflow(requirement: str, progress_callback=None):
    async def emit(phase: str, data: dict):
        if progress_callback:
            await progress_callback(phase, data)  # MUST await!

    await emit("phase:PM", {"status": "running", "phase": "Project Manager"})
    pm_out = await run_pm(requirement)
    await emit("phase:PM", {"status": "done", "result": pm_out})
    # ... continues for DEV, QA, ARCH phases
```

## File + Code Extraction

```python
# Extract file path: try header first, then task title fallback
file_path_match = re.search(r"(?:### FILE|### Path|File:)\s*[:`]*\s*(.+?)(?:\n|$)", raw)
path = file_path_match.group(1).strip().strip("`") if file_path_match else None
if not path and task.get("title"):
    m = re.search(r"[\w./\\]+\.\w+", task["title"])
    if m:
        path = m.group(0)

# Extract code: take longest fenced block (handles multiple blocks)
code_blocks = re.findall(r"```(?:[\w-]+)?\s*([\s\S]*?)```", raw)
code = max(code_blocks, key=len).strip() if code_blocks else ""
```

## Project Location
**Working project at `/home/maulana/project-automation/`** — running on port 8765.

## Known Pitfalls (tested & fixed 2026-09-07)

- `ImportError: cannot import name 'SSEResponse'` — use `sse_starlette.sse.EventSourceResponse` directly
- SSE stuck at "job started" — add `"stream": False` to router, OR 9Router unreachable (use `172.26.176.1` not `localhost`)
- `result: null` after job completes — callback was sync lambda, must use `async def emit()` with `await`
- `output/` dir empty — path extraction failed; add task-title fallback + longest-fence code extraction
- Background server from old session — kill and restart after code changes

## References

- `references/project-automation-ref.md` — 9Router API format, model combos, known working configs, test commands
- Project at `/home/maulana/project-automation/` — running on port 8765
