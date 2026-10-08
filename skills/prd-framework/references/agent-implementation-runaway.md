# Agent implementation runaway — scope creep + empty-parens loop

Failure mode seen when a PRD/agent-pack is handed to an autonomous agent (`hermes chat -q`
via the browser-to-cli bridge `auto_run` toggle) to "implement the MVP".

## Symptoms
- A "landing page" PRD produced a full-stack Next.js 16 app: React 19, TypeScript, Tailwind 4,
  framer-motion, gsap, zod v4, Supabase (+ auth-js/webauthn), @react-three/fiber + drei + three
  (a 3D low-poly hero). 343 node_modules dirs, `.next` build, tsc passes.
- Same run ALSO loops on the empty-parens-strip bug (empty `` stripped by the toolchain every
  time it writes code). React/TS is dense with `useState`, `useEffect( =>`, `Math.random`,
  arrow params — so the agent kept writing → parens stripped → write a repair script → rewrite
  with a sentinel (`P`/`E`) → sentinel mismatch → tsc errors → rewrite again.
- Result: process alive 49+ minutes, `run.log` at 4800+ lines, still mid-rewrite of `ScrollSync.tsx`.

## Root cause — two compounding problems
1. **No scope constraint in the PRD.** The agent is told "implement the MVP per acceptance
   criteria" with no pinned tech stack, so it freely picks the heaviest plausible stack. For a
   static landing page that is pure waste (npm install, build, tsc, tree-shaking all eat minutes).
2. **Empty-parens density.** JS frameworks (hooks, arrow functions, IIFEs) are the WORST case for
   the safe-code-authoring empty-parens strip bug. A static-vanilla-JS page barely uses empty
   parens, so it would sail through.

## The rule to bake into PRD + AGENTS when auto-run is on
- Pin the implementation explicitly. For a landing page: **single-file static HTML + CSS + vanilla
  JS**, no framework, no build step, no `npm install`, no backend. "Buka langsung di browser."
  Reserve frameworks for PRDs that genuinely need them (auth, data, routing, server).
- In `AGENTS.md`, add a hard rule: load the `safe-code-authoring` skill before writing code, write
  empty parens as the ``-sentinel and repair with a script, OR (better) avoid arrow functions /
  IIFEs / hooks entirely — prefer function declarations and flat statements.
- Explicitly forbid scope creep in AGENTS.md ("jangan tambah fitur di luar scope"), and add a
  "stack" line in the PRD's technical-considerations section that the agent must honor.

## Diagnosis recipe (how to spot this fast)
- `ls ~/prd-outbox/<name>/` — count `node_modules/`, look for `package.json` deps heaviness.
- `cat .run.pid` → `ps -p <pid> -o etime` to see how long it's been "running".
- `grep -i "paren\|strip\|sentinel\|rewrite" run.log | tail` — a long chain of rewrite/fix loops
  is the tell. Note the sentinel-mismatch pattern (used `P` in one file, `E` elsewhere).
- Landing-page PRD + heavy framework + repeated paren-rewrite log entries = this exact failure.

## Relation to other skills
- `safe-code-authoring` is the canonical skill for the empty-parens strip bug itself.
- `prd-authoring` (user-owned sibling) documents the bridge/auto-run mechanism end to end.