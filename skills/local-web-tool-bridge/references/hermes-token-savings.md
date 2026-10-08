# Token savings — Hermes config knobs (user's custom DeepSeek provider)

Context: user runs Hermes with a custom provider (DeepSeek via api.cfrouter.site/v1,
~128K window). "Hemat token" means tuning Hermes' own compression machinery —
NOT installing tamp / oc-context-optimizer, which target OpenClaw/Anthropic only.

## Verified config changes (hermes config set, applied 2026-08-23)

```bash
hermes config set compression.proactive_prune_tokens 48000
hermes config set compression.idle_compact_after_seconds 1800
hermes config set agent.max_turns 90
hermes config set model.context_length 131072
hermes config set compression.protect_last_n 25
```

All via `hermes config set` (never hand-edit config.yaml). Effects land on /reset
(new session) to preserve prompt caching.

## Why each one

- `proactive_prune_tokens` — the biggest win on large-window models. Default
  threshold 0.5×context rarely fires at 128K, so old tool output (big reads/greps)
  rides in history and is re-sent every turn. This deterministically prunes large
  tool results (min_result_chars 8000, min_reclaim_tokens 4096) with NO LLM call,
  gated so prompt-cache breaks stay episodic. 0 = off (default).
- `idle_compact_after_seconds` — 0 = disabled (default). >0 compacts accumulated
  history up-front when a session resumes after N seconds idle, so a long-lived
  thread resumed later doesn't re-read full stale context each turn. 1800 = 30 min.
- `agent.max_turns` — cap tool-call iterations per turn (default 90, was 150 for
  this user); bounds fix-loops like the empty-parens strip saga.
- `model.context_length` — was unset; compressor needs it to compute the real
  threshold. 131072 = 128K.
- `protect_last_n` — recent messages kept uncompressed through compaction.

## Hermes' built-in compression (already on, don't re-add)

- `compression.enabled: true` — lossy summarization at `threshold` (0.5) down to
  `target_ratio` (0.2). Engine "compressor" (agent/context_compressor.py
  ContextCompressor). Alternative engines plug in via plugins/context_engine/<name>/
  selected by `context.engine` in config (only one active at a time).
- `prompt_caching: cache_ttl 5m` — ONLY effective for Anthropic/OpenRouter. Custom
  OpenAI-compat providers (chat_completions) don't get prefix caching; don't promise
  savings from it there.

## Decision knobs left for the user (not changed)

- `compression.threshold` 0.5 → 0.40 for more aggressive/earlier compaction (quality trade-off).
- `compression.min_tail_user_messages` 1 → 3 to keep last 3 real user turns verbatim.
- `model_thresholds` — per-model override map, substring-matched, longest wins;
  small-context floor 0.75 for <512K models raises any override below it.

## Verified paths in the source (hermes-agent/ repo, git install)

- compression defaults + comments: hermes_cli/config_defaults.py (~line 520-580,
  640-680 for model_thresholds / idle_compact_after_seconds)
- ContextCompressor: agent/context_compressor.py (should_compress 2354,
  compress 4990, proactive prune in __init__ ~2063)
- `hermes tools` is TTY-only — can't enumerate toolsets non-interactively.

## What does NOT save tokens here (checked)

- `tamp` (proxy compress tool_result for Anthropic) — OpenClaw/Anthropic only.
- `oc-context-optimizer` (microcompact/autocompact/tool_defer suite) — OpenClaw runtime.
- Skills are lazy-loaded, not per-prompt; preloading all 131 inflates the system
  prompt and wastes tokens. Memory + wiki (llm-wiki) save tokens long-term by
  avoiding re-derivation, not per-request.
