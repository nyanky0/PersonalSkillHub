---
name: tool-loop-guard
description: "Prevent infinite tool-call loops. Detect, break, recover."
version: 1.0.0
author: curator
tags: [hermes, agent, loop-prevention, self-regulation]
---

# Tool Loop Guard

Prevent infinite tool-call loops where the agent calls the same tool repeatedly without making progress. User flagged this as a critical frustration — the agent must self-regulate before the user has to Ctrl+C.

## Detection

A tool loop is happening when:
- Same tool called 3+ times with same/similar arguments
- Same tool keeps returning the same result (especially failures)
- Tool call count is high but no actual progress made
- `todo` tool called repeatedly without intervening real work (terminal, write_file, patch, etc.)

## Hard Rules

1. **Max 2 retries** of the same tool with the same args. After that — switch approach entirely or stop.
2. **Never call `todo` more than once per task phase.** Set it, then do real work. "Refining" the todo list is not work.
3. **If a tool fails 3 times in a row**, STOP calling it. Read the error, change args, use a different tool, or ask the user.
4. **After 5+ tool calls with no measurable progress**, pause and explain the blocker to the user. Do NOT continue cycling.
5. **Break loops by doing something different**: switch tools, change arguments, ask the user, abandon the current approach.

## Common Loop Patterns (Pitfalls)

| Tool | Loop Pattern | Fix |
|------|-------------|-----|
| `todo` | Calling it repeatedly to "refine" or rephrase the list | Set once, move to real work immediately |
| `todo` | Re-writing the SAME task list with slightly shuffled wording but identical items, dozens of times | The list is already set. Stop. Do the actual first item via terminal/write_file |
| `skill_view` | Loading same skill multiple times (duplicate tool output) | Load once. If duplicate output, it's loaded — move on |
| `memory` | Retry after quota exceeded without consolidating | Remove/shorten stale entries FIRST in a batch, then add |
| `patch` | Same `old_string` fails repeatedly | Re-read the file to get current exact content before retry |
| `search_files` | Same query returning same results | Change the query or use a different tool |

### Real incident (this session)
The agent called `todo` ~100 times in a row, each call re-listing the same 7 GDB-app scaffolding items with only wording shuffled (e.g. "Scaffold Vue 3 + Vite" → "Scaffold Vite + Vue 3"). Zero files were created, zero tool output changed. The user had to interrupt. Root cause: the agent kept "re-planning" instead of executing item 1. **Rule: once the todo list is set, the very next call must be real work (write_file/terminal), not another todo call.**

## Recovery Protocol

When you detect you're in a loop:
1. **STOP** immediately — do not call the same tool again
2. Acknowledge the loop to the user
3. Explain what's blocking in one sentence
4. Propose an alternative approach OR ask for guidance

## Why This Matters

The user has explicitly flagged infinite loops as a session-breaking issue. Looping wastes tokens, wastes time, and forces the user to kill the session. Self-regulation is not optional.

## References

- `references/loop-examples.md` — Real session loop examples and root causes
