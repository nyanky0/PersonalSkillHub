# PRD Research Detail

Session: build a local tool that turns raw AI prompts into structured PRDs. Sources consulted and key findings.

## Sources

1. **Atlassian Agile Coach — "How to create a product requirements document" (Dan Radigan)**
   URL: https://www.atlassian.com/agile/product-management/requirements
   Fetch: curl + Chrome UA; page is huge (2.4MB) — main content buried after ~30KB of nav; find article body with `body.find('How to create a product requirements document')` on stripped text.
   Key content:
   - PRD = "single source of truth" defining purpose, features, functionality, behavior
   - Agile: shared understanding + empathy for customer; implementation detail left to dev team
   - **"What should a PRD include" (their exact 8 items)**:
     1. Project specifics: participants, status (on target/at risk/delayed/deferred), target release
     2. Team goals and business objectives
     3. Background and strategic fit
     4. Assumptions
     5. User stories (+ links to customer interviews, screenshots, success metrics)
     6. User interaction and design (link wireframes/explorations)
     7. Questions ("things we need to decide or research" table)
     8. What we're NOT doing (out of scope)
   - Anti-patterns: full spec before engineering, iron-clad sign-off before work, requirements never updated, PO writes solo
   - Benefits: one-page landing hub, extra agility, "just enough" detail, living stories, collaboration

2. **AungMyoKyaw/prd-creator** (29★, TypeScript/Next.js 15, Gemini AI) — the most complete OSS PRD generator
   Repo: https://github.com/AungMyoKyaw/prd-creator
   - 3-step wizard: Input → Generate → Review
   - Input form = 11 fields in 4 sections: (1) Core Product Idea: productName, problemStatement, proposedSolution; (2) Audience & Market: targetAudience, businessGoals; (3) Features & Scope: coreFeatures, futureFeatures; (4) Technical: techStack, constraints
   - Output PRD structure (from `src/lib/prd.ts`, `generatePreviewMarkdown`/`buildGenerationPrompt`):
     1. Introduction & Vision (problem, solution, vision [AI])
     2. Target Audience & User Personas (audience, 2-3 personas [AI])
     3. Product Goals & Success Metrics (goals, SMART KPIs [AI])
     4. Features & Requirements (MVP core features, 2-3 user stories per feature [AI], future features)
     5. Technical Considerations (stack, constraints/dependencies)
     6. Out of Scope [AI]
   - Prompt engineering pattern: bracket instructions for AI-filled lines, fallback defaults for empty inputs ("Not specified. Generate reasonable business goals like user acquisition, engagement, and revenue generation.")
   - User stories format: "As a [user type], I want to [action], so that I can [benefit]."
   - Export: markdown download, clipboard; drafts in IndexedDB (12 max), localStorage fallback; PWA
   - API key stored in browser localStorage, calls Gemini directly (no server)
   - Key source file: https://raw.githubusercontent.com/AungMyoKyaw/prd-creator/master/src/lib/prd.ts

3. **cdeust/ai-prd-generator** (10★, Claude Code plugin, commercial) — advanced enterprise pattern
   - Multi-round clarification: asks structured questions until confidence ≥92% (95% preferred, 100% auto-generate); free tier 3 rounds
   - 8 PRD types: Feature, Bug, Incident, Proposal, MVP, POC, Release, CI/CD — each with tailored sections/depth
   - 15 thinking strategies (ToT, GoT, ReAct, Reflexion, self-consistency...) from MIT/Stanford/Harvard/Anthropic papers
   - Multi-judge verification: 6 algorithms, atomic claim decomposition, every claim verified
   - 4-file export: PRD.md + JIRA tickets (Fibonacci points, acceptance criteria, sprint phasing) + test cases (unit/integration/e2e with traceability matrix) + verification report
   - Codebase context indexing for architecture-aware PRDs

4. **Don Cheli SDD framework** (doncheli/don-cheli-sdd, 57★) — specification-driven development for AI agents, 88+ commands; adjacent concept (spec-first AI coding), not PRD-specific.

## Other repos surfaced (lower stars)
- scalershare/prd-generator (16★) — "production-grade PRD generator, Claude Code skill, for non-technical users; output ready for AI development"
- ssyamv/ArchMind (6★) — local RAG-based PRD & prototype generator (local-running MVP pattern)
- jamiul-islam/codeWinter (5★), PAIPalooza/prdgenerator (4★), aymuos19/astra-qa-ai-testgen (13★, BRD/PRD → test cases, 4-agent)

## Build decision for this user
User picked: single-file HTML+JS local app, OpenAI-compatible endpoint (existing proxy 172.26.176.1:20128), localStorage history, export markdown. Rejected Next.js clone (overkill) and Laravel (no multi-user need yet).
