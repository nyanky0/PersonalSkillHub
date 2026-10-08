# PRD Frameworks & Research Notes

Sources synthesized for the PRD structure (riset 2026-08): Atlassian PRD guide, AungMyoKyaw/prd-creator (Gemini PRD generator, Next.js), cdeust/ai-prd-generator (multi-LLM verification).

## Atlassian "What should a PRD include" (8 sections)
1. Project specifics: participants (PO, team, stakeholders), status (on target / at risk / delayed / deferred), target release
2. Team goals & business objectives — clear, brief, no room for assumptions
3. Background & strategic fit — motivation + alignment with company goals
4. Assumptions — tech, business, user behavior; revisit throughout project
5. User stories — link interviews, screenshots, success metrics
6. User interaction & design — link wireframes/explorations
7. Questions — table of "things we need to decide or research"
8. What we're NOT doing — explicit out-of-scope, flag for later

Agile anti-patterns (Atlassian): full spec before engineering, iron-clad sign-off before work, requirements never updated, PO writes requirements without team, dev/design not in customer interviews.

## prd-creator (AungMyoKyaw) — prompt-to-PRD wizard
Flow: Setup (API key+model) → Input (quick-start AI autofill OR manual form) → Generate → Review (view/export/save draft).
Input fields (11): productName, targetAudience, problemStatement, proposedSolution, coreFeatures, keyFeatures, businessGoals, successMetrics, futureFeatures, techStack, constraints (+ images).
Generation output structure (6 sections): Intro & Vision (problem/solution/vision) → Audience & Personas (primary + 2-3 personas w/ goals+frustrations) → Goals & Success Metrics (SMART KPIs) → Features & Requirements (MVP core features, 2-3 user stories per feature "As a [user], I want [action], so that [benefit]", post-MVP) → Technical Considerations (stack, constraints/dependencies) → Out of Scope.
PWA, exports Markdown, draft management via IndexedDB.

## ai-prd-generator (cdeust) — enterprise ideas worth stealing
- 8 PRD types: Feature, Bug, Incident, Proposal, MVP, POC, Release, CI/CD — each has tailored clarification depth + section count
- Clarification loop: interactive multi-choice questions until confidence ≥95%, then generate (rounds capped on free tier)
- Multi-judge verification: atomic claim decomposition, consensus with early stopping — verify every claim in the PRD
- 4-file export: PRD.md + jira.md (story points Fibonacci, acceptance criteria, sprint phasing) + tests.md (unit/integration/e2e + traceability matrix) + verification.md (claim-by-claim audit + confidence scores)
- Codebase context analysis: extract architecture patterns (Repository/Service/Factory/MVVM), entities, dependencies; cite file:line in PRD

## Prompt engineering notes for PRD generation
- System prompt must be strict: "output pure markdown, no fenced code blocks, no preamble/closing" — otherwise LLM wraps output in ``` fences that break file writing.
- Language direction (id/en) goes in the user prompt as a rule.
- One LLM call per output file keeps each call focused; injecting prior outputs (PRD into AGENTS/tasks prompts) chains context.
- Clarification answers injected as "## Jawaban klarifikasi dari user" section — keeps raw prompt untouched, adds constraints as context.

## Gemini OpenAI-compatible endpoint
- Base URL: `https://generativelanguage.googleapis.com/v1beta/openai/` + `chat/completions`
- Works with `Authorization: Bearer <API key>` (AI Studio key), model `gemini-2.5-flash`.
- Any OpenAI-compatible provider works: OpenRouter, local proxies. Local proxy on WSL host (e.g. `http://172.26.176.1:PORT/v1/`) may still require its own API key (401 "API key required for remote API access").
