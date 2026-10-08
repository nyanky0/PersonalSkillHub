# Diagnosing a "slow agent" spawned from a web tool

The `local-web-tool-bridge` pattern spawns `hermes chat -q` in the background. When the
user reports "kenapa lama banget eksekusinya, padahal cuma landing page", the cause is
almost never network or model speed. Reproduce this diagnosis:

## 1. Check the process and log volume

```bash
# where did it write? (the bridge logs to ~/prd-outbox/<name>/run.log)
cat ~/prd-outbox/<name>/.run.pid
ps -p $(cat ~/prd-outbox/<name>/.run.pid) -o pid,etime,cmd
wc -l ~/prd-outbox/<name>/run.log   # 4000+ lines = fix-loop, not progress
```

## 2. Grep the log for loop signatures

```bash
grep -n -i "rewrite\|strip\|sentinel\|issue\|overcomplicating\|loop" ~/prd-outbox/<name>/run.log | tail -40
```

Repeated occurrences of "empty parens strip", "rewrite with sentinels", "I'm
overcomplicating", "repair script" = the agent is fighting the paren-strip bug
(same class as this skill's Empty-parens section) instead of building.

## 3. Check for scope creep (the other half)

```bash
find ~/prd-outbox/<name> -maxdepth 1 -type d | head
ls ~/prd-outbox/<name>/node_modules 2>/dev/null | wc -l   # 300+ dirs = over-engineered
```

A "landing page" PRD that produced Next.js + Supabase + framer-motion + 3D scene =
the stack was chosen too big at GENERATE time.

## The three-layer fix (apply all three, not one)

1. `--max-turns 60` on the spawn — bounded budget stops the loop.
2. `--skills safe-code-authoring` on the spawn — the agent starts with sentinel/repair
   tactics instead of discovering the bug mid-build.
3. Stack-scope rules in the PRD/AGENTS/SKILL generator prompts — "landing page / website
   statis = single-file HTML+CSS+vanilla JS, TANPA framework/build step/backend".
   Generation-time constraint beats execution-time hoping.

## Verify the fix landed

- `python3 -m py_compile <server>.py`
- extract the inline `<script>` and `node --check` it
- `grep -n "max-turns\|safe-code-authoring" <server>.py` — flags present
- the generator template contains the stack-scope sentence

## Stale process cleanup

Kill the stuck agent: `kill $(cat ~/prd-outbox/<name>/.run.pid)`. Old runs often already
died on their own — `ps -p <pid>` will say so. No orphaned `hermes chat -q` procs remain
once the pid-guard is in place.
