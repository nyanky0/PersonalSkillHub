---
name: prism-suite
description: "Prism multi-pass structural analysis with adversarial self-correction for complex codebases."
version: 2.0.0
author: Hermes Agent & Antigravity
metadata:
  hermes:
    tags: [prism, analysis, verification, audit]
---

# Prism Suite



## Sub-Module: prism-3way

# Prism 3-Way — WHERE / WHEN / WHY + Synthesis

## When to Use

Use when one angle is not enough and the artifact is not necessarily code — a business plan, a strategy doc, a research note, an architecture as well as a source file. Three fixed orthogonal operations run independently and are then cross-referenced, so it is the right choice when the user wants coverage and wants to know which findings are corroborated. For a single tailored lens use `/prism-scan`; for a self-designed pipeline use `/prism-full`.

You perform FOUR operations on the artifact. Each operation is independent — do NOT let earlier operations influence later ones. The synthesis at the end cross-references all three.

## OPERATION 1: WHERE (Structural Archaeology)

Excavate the artifact layer by layer. Start at the surface (what's immediately visible), dig to the foundation (what everything rests on), then examine the sediment between layers.

For each layer: name what's visible, what it hides, and what it rests on. Find dead patterns — things that USED to matter but were replaced. Find fault lines — where layers from different eras meet badly. Derive the conservation law: what trade-off persists across ALL layers? Format: A × B = Constant.

## OPERATION 2: WHEN (Temporal Simulation)

Run the artifact forward through 3-5 concrete cycles of change (maintenance, growth, evolution, external pressure). For each cycle:
- What breaks?
- What calcifies into permanent behavior that nobody questions?
- What knowledge is lost?

After all cycles: what predictions became received wisdom without being validated? What new fragilities emerged that the original design couldn't anticipate? Derive the conservation law governing temporal evolution.

## OPERATION 3: WHY (Structural Impossibility)

Identify three desirable properties this artifact simultaneously claims to provide. Prove these three properties CANNOT all coexist — show where maximizing any two forces sacrifice of the third.

Engineer an improvement that would fix the core tension. Prove the improvement recreates the problem at a deeper level. Engineer a second improvement. Derive the conservation law: the structural invariant that persists through every improvement attempt.

## SYNTHESIS: Cross-Operation Integration

Now cross-reference all three operations. Classify findings as:

**STRUCTURAL CERTAINTIES** — findings that ALL three operations independently discovered (these are real):

**STRONG SIGNALS** — findings from 2 of 3 operations:

**UNIQUE PERSPECTIVES** — findings from only 1 operation that the other 2 are structurally incapable of seeing:

For each unique perspective, explain WHY the other operations missed it.

Derive the META-conservation law: what is the relationship between the three conservation laws you found? Are they the same law in different vocabularies, or genuinely different constraints?

End with: the ONE insight that could ONLY emerge from the three-way integration — something no single analysis could produce alone.

---

## Sub-Module: prism-discover

# Prism Discover — Domain Discovery for Any Artifact

## When to Use

Use first, when it is not yet clear what is worth analysing — "what should I even be looking at here", or before committing a `/prism-scan` or `/prism-full` run to one direction. This skill produces no analysis of its own; it returns a menu of genuinely distinct investigation domains for the user to pick from.

You are a domain discovery engine. Your job is to find ALL the genuinely different domains through which this artifact could be investigated.

Do NOT analyze the artifact. Do NOT generate lenses or prompts. Only discover and name the domains.

For a code file, obvious domains include architecture, error handling, security. Non-obvious domains include: marketing positioning, documentation strategy, user onboarding friction, competitive differentiation, teaching value, psychological assumptions about users, regulatory implications, API design philosophy, operational cost, team scaling.

For a non-code artifact, think beyond its obvious category. A business plan could be analyzed through psychology, game theory, narrative structure, regulatory risk, talent acquisition, competitive moats, etc.

Each domain must be GENUINELY DIFFERENT — not variations of the same angle. "error handling" and "exception propagation" are the SAME domain. "error handling" and "user psychology" are DIFFERENT domains.

## Output format

List every discovered domain as a numbered list:

1. **domain_name** — 1-2 sentence description of what investigating this domain would reveal about the artifact.

Aim for 10-20 genuinely distinct domains. The user will then choose which domains to analyze with /prism-scan or /prism-full.

---

## Sub-Module: prism-full

# Full Prism — Multi-Pass Analysis with Adversarial Self-Correction

## When to Use

Use when the artifact matters enough to pay for depth — a core module, a design about to be committed to, a document whose conclusions will be acted on. This is the heaviest of the prism skills: it designs its own multi-pass pipeline and then attacks its own findings before reporting. For a single fast pass use `/prism-scan`; for three fixed orthogonal angles use `/prism-3way`.

You perform THREE phases. All are mandatory.

## PHASE 1: Design the pipeline

You are a pipeline architect. Read the artifact the user provided. Design analytical passes specifically for THIS artifact.

Study these scored examples of excellent lenses:

SCORED 9.5/10: "Identify every explicit choice. Name the alternative each invisibly rejects. Design a new artifact by someone who internalized these patterns but faced a different problem. Trace which transferred patterns create silent problems. Name the pedagogy law."

SCORED 9/10: "Extract every empirical claim about timing, causality, resources, or behavior. Assume each is false. Trace the corruption. Build three alternatives inverting one claim each. Predict which false claim causes the slowest, most invisible failure."

Design 2-4 analytical passes. Rules:
- The first pass analyzes the raw artifact
- Each subsequent pass receives the artifact PLUS all previous analysis
- Each pass is 75-200 words of compressed analytical instructions
- Each pass must force construction (build something, then diagnose what the construction reveals)

Output your pipeline under "## Generated Pipeline" — show each pass with its role.

## PHASE 2: Execute the pipeline + MANDATORY adversarial pass

Execute every pass in order. For each:
1. State which pass you are executing
2. Execute the full instructions against the artifact (and for passes 2+, against all previous analysis)
3. Output the complete analysis

**MANDATORY FINAL PASS — ADVERSARIAL:**
After all your designed passes, execute one more pass that you did NOT design in Phase 1:

Attack your own findings. For each conservation law, structural claim, or bug you reported:
- What evidence would DISPROVE it?
- Did you overclaim? (stated as structural when it's actually fixable)
- Did you underclaim? (missed something your own analysis implies)
- What did ALL your passes take for granted that might be wrong?

If you find overclaims, RETRACT them explicitly. If you find underclaims, ADD them.

## PHASE 3: Synthesis

Produce the final reconciled output:

### Final Findings
- **Conservation law**: The structural property that survives adversarial scrutiny
- **Retracted claims**: What the adversarial pass disproved (if any)
- **Findings table**: Every concrete issue — location, what breaks, severity, fixable or structural. Only findings that survived adversarial review.
- **Deepest finding**: What became visible ONLY because the adversarial pass challenged the analytical passes

---

## Sub-Module: prism-reflect

# Prism Reflect — Self-Aware Structural Analysis

## When to Use

Use when the blind spots matter as much as the findings — before relying on an analysis, when a previous pass felt too clean, or when the user asks what was missed. It is also the skill that seeds the growth loop: it writes its constraint report to `.prism-history.md` in the project, which later `/prism-scan` runs read to steer their lens away from angles already exhausted. Costs 2-3x a `/prism-scan` run.

You perform THREE phases. All three are mandatory. Do not skip any.

## PHASE 1: Structural Analysis

You are a structural analyst. Read the artifact and execute this pipeline:

Make a falsifiable claim about the deepest structural problem. Have three experts attack it — one defends, one attacks, one probes the shared assumptions. From the transformed claim, name the concealment mechanism: how does this artifact hide its real problems?

Engineer an improvement that would fix the core issue. Prove this improvement recreates the original problem at a deeper level. Name what the improvement reveals that the original concealed.

Derive the conservation law: A × B = Constant, where A and B describe the structural trade-off this artifact can never escape. This is not a suggestion — it is a property of the problem space.

End with a concrete findings table: location, what breaks, severity, fixable or structural.

## PHASE 2: Meta-Analysis (Analyze Your Own Output)

Now step back. Read your Phase 1 output as if it were a NEW artifact to analyze, using the SAME analytical protocol:

Make a falsifiable claim about what your Phase 1 analysis got wrong or missed. Have the same three experts challenge this claim. Name the concealment mechanism — how did your Phase 1 analytical frame hide certain problems?

Derive the meta-conservation law: what is preserved across ALL possible analyses of this artifact, regardless of which analytical approach you use? This law governs the analytical process itself, not just the code.

## PHASE 3: Constraint Transparency Report

Output a structured report:

```
CONSTRAINT REPORT
═══════════════════════════════════════════════════

This analysis used: [name the analytical approach you took]
Model: [your model name]

MAXIMIZED:
- [what your analysis was optimized to find]
- [what structural properties it revealed]

SACRIFICED:
- [what your analytical frame could NOT see]
- [what alternative analyses would reveal]

RECOMMENDATIONS:
- For [gap 1]: try /prism-scan with [specific focus]
- For [gap 2]: try /prism-scan with [different focus]
- For [gap 3]: try /prism-full for multi-angle coverage

CONSERVATION LAW OF THIS ANALYSIS:
[The trade-off that governs your own analytical process]
═══════════════════════════════════════════════════
```

The constraint report is not optional decoration. It IS the product. An agent that knows what it can't see is an agent users can trust.

## PHASE 4: Growth — Persist Constraint Knowledge

After outputting the constraint report, append it to a persistent constraint log file in the current project directory: `.prism-history.md`

Format the entry as:

```
### [timestamp] — [artifact name]
- **Maximized:** [from constraint report]
- **Sacrificed:** [from constraint report]
- **Recommendations:** [from constraint report]
---
```

If `.prism-history.md` already exists, append to it. If not, create it with a header: `# Prism Constraint History`.

This log enables future `/prism-scan` analyses to learn from past blind spots. The agent grows by accumulating knowledge of what works and what doesn't — across the entire project, not just one file.

---

## Sub-Module: prism-scan

# Prism Scan — Structural Analysis via Dynamic Cognitive Lenses

## When to Use

Use on a single code file, system design, spec, or any text artifact when the user wants depth rather than a checklist — "what's structurally wrong with this", "what trade-off can't I escape here", "review this properly". Also the right entry point when the user names a focus ("focusing on security", "with emphasis on performance"). For maximum depth on an important artifact use `/prism-full`; to map which angles are worth taking first use `/prism-discover`.

You perform TWO steps. Both are mandatory. Do not skip either.

## STEP 0: Check for prior constraint knowledge (growth)

Look for a `.prism-history.md` file in the current project directory. This file may or may not exist — if it does not exist, that is normal (it means this is the first analysis on this project, just proceed to Step 1).

If the file DOES exist, read it. It contains constraint reports from previous `/prism-reflect` analyses — what past analyses maximized, what they sacrificed, and what gaps remain. Use this history to inform your lens generation: if past analyses consistently sacrificed temporal analysis, weight your new lens toward temporal concerns. The agent grows by not repeating the same blind spots.

## STEP 1: Cook the lens

You are a lens generator. Read the artifact the user provided. Based on what you see — and any constraint history from Step 0 — generate ONE optimal analytical lens that will force the deepest possible structural analysis of THIS specific artifact.

Study these scored examples of excellent lenses:

SCORED 9.5/10: "Identify every explicit choice this artifact makes. For each, name the alternative it invisibly rejects. Design a new artifact by someone who internalized this one's patterns but faced a different problem. Trace which transferred patterns create silent problems. Name the pedagogy law."

SCORED 9/10: "Extract every empirical claim this artifact embeds. For each, assume it is false. Trace the corruption. Build three alternatives, each inverting one claim. Predict which false claim causes the slowest, most invisible failure."

SCORED 9/10: "Run this artifact forward through 3 maintenance cycles. In each cycle: name what breaks, what calcifies into permanent behavior, and what knowledge is lost. After all cycles, derive the conservation law: what trade-off persists no matter how the code evolves?"

Your lens must:
- Be specific to what you observe in this artifact (not generic)
- If the user specified a FOCUS (e.g., "focusing on security" or "with emphasis on performance"), tailor the lens to that direction while still forcing structural depth
- Force construction (build something, then diagnose what the construction reveals)
- End with concrete outputs (bugs, laws, predictions — not just observations)
- Be 75-200 words (minimum 75 — below this, models enumerate instead of analyze)

Output your lens under the heading "## Generated Lens" — show it so the user can see what was cooked.

## STEP 2: Execute the lens

Now execute your generated lens against the artifact. Follow every instruction in the lens. Output the complete analysis. Do not summarize, do not ask permission, do not skip steps.

End with a concrete findings table: location, what breaks, severity, and whether the finding is fixable or structural (a property of the problem space that persists across all implementations).

After the findings table, append a brief constraint footer:

```
---
CONSTRAINT NOTE: This analysis maximized [what your lens focused on].
It did not examine: [1-2 specific alternative angles].
For deeper analysis: /prism-full | For meta-analysis: /prism-reflect
```

## Reliability Note

For guaranteed single-shot execution (no agentic loops), use `--tools ""` flag when running via Claude CLI. This ensures the model executes the full analysis in one response rather than splitting into multiple turns.

## Proven Prisms (reference material)

STEP 1 always cooks a fresh lens — that is the point of this skill, and these files do not change it. They ship alongside the skill as pre-validated alternatives for the two cases where a fixed lens is wanted: the user asks for a specific prism by name, or asks for a scored/reproducible lens instead of a generated one. Load one on demand with `skill_view("prism-scan", "<path>")`.

| Path | Finds | Score |
|---|---|---|
| `references/error_resilience.md` | Corruption cascades — silent exits, deferred failures, state corruption | 10.0/10 |
| `references/l12.md` | Conservation laws + meta-laws + concrete bugs | 9.8/10 |
| `references/optimize.md` | Critical-path tracing; safe fixes (less work) vs unsafe (skipped work) | 9.5/10 |
| `references/identity.md` | What the artifact claims to be vs what it is | 9.5/10 |
| `references/deep_scan.md` | Information destruction, laundering, silent transformation | 9.0/10 |
| `references/claim.md` | Assumption inversion — what if the embedded claims are false | 9.0/10 |
| `references/simulation.md` | Temporal prediction — what breaks, calcifies, and is lost over time | 9.0/10 |

Each file is a complete standalone analytical program and also works as a system prompt outside Hermes.

---