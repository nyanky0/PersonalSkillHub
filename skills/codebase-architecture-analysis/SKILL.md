---
name: codebase-architecture-analysis
description: "Use when explaining an unfamiliar application codebase."
version: 1.0.0
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [codebase, architecture, application-analysis, reverse-engineering, onboarding]
---

# Codebase Architecture Analysis

Analyze an unfamiliar application repository and explain **what it builds, how it is structured, and how its major workflows connect**. This complements LOC-oriented inspection: metrics are supporting evidence, not the deliverable.

## Outcomes

Produce a grounded explanation covering:

- application purpose and user roles
- stack and architectural style
- source-tree responsibilities
- major feature modules
- request/data/event flows
- important data relationships
- authorization, concurrency, reporting, and deployment patterns
- verification status and a short list of evidence-backed risks

## Workflow

### 1. Resolve and verify the repository

Translate host paths when needed (for example, `C:\\project` to `/mnt/c/project` in WSL), verify the directory exists, and check whether it is a Git worktree. Do not modify the repository during analysis.

### 2. Separate source from generated/runtime content

Exclude dependency, cache, build, and runtime trees before counting or sampling. Typical exclusions:

```text
.git, vendor, node_modules, storage, bootstrap/cache,
public/build, dist, build, coverage, .next, venv, .venv
```

Generated views, logs, sessions, and compiled assets can otherwise dominate file discovery and hide the actual application.

### 3. Identify the stack from manifests

Read the relevant manifests and entry points, such as:

- `composer.json`, `package.json`, lockfiles
- framework CLI/bootstrap files
- `Dockerfile`, Compose files, web-server configuration
- `README`, `.env.example`, build configuration

Use manifest versions as evidence. Do not infer a framework version from folder shape alone.

### 4. Build a structural inventory

Map, count, and sample the directories that carry behavior:

- routes/endpoints
- controllers/handlers
- models/entities
- services/use cases
- events/listeners/jobs
- templates/views/components
- migrations/schema and seeders/fixtures
- tests

Report counts only after exclusions. Prefer semantic groupings over dumping every filename.

### 5. Trace workflows vertically

For each major feature, follow a full path:

```text
route or UI entry
→ controller/handler
→ service/domain logic
→ model/database writes
→ event/listener or job
→ response/view/export
```

Start with routes because they expose the real user-facing surface. Use seeders and permissions to identify intended roles and default business configuration. Inspect events/listeners to find side effects that are not visible in controllers.

### 6. Reconstruct the data model

Use migrations as schema truth and models as relationship/behavior evidence. Explain relationships in a compact conceptual diagram. Call out polymorphic relations, soft deletes, audit tables, status fields, and derived ledgers when present.

### 7. Inspect cross-cutting behavior

Explicitly check:

- authentication, roles, permissions, and route guards
- transactions, locks, uniqueness, overlap checks, and idempotency
- uploads and validation
- caching and invalidation
- exports and reports
- deployment topology
- default credentials or hardcoded development secrets

### 8. Verify executable claims

Run low-risk framework introspection such as route listing, config validation, or test discovery. Run the test suite when practical.

A stream of progress dots is **not** a passing test result. Report tests as passed only after the process exits successfully and prints a final summary. If it hangs, record the elapsed behavior, stop it cleanly, and say verification is incomplete rather than guessing.

On WSL repositories intended for a Windows runtime, invoke the project's Windows executable through `cmd.exe /c` when native WSL tooling is absent or would use a different environment. Treat this as environment selection, not a permanent limitation.

### 9. Report evidence separately from findings

Use this order:

1. Executive summary
2. Stack and architecture
3. Source-tree map
4. Major modules and user flows
5. Data model and relationships
6. Security/concurrency/deployment behavior
7. Verification performed
8. Prioritized observations or risks

Clearly distinguish:

- **Observed:** directly present in routes/code/schema
- **Inferred:** likely intent based on naming or incomplete implementation
- **Verified:** exercised successfully by a command/test

## Quality Rules

- Explain the product, not merely the framework conventions.
- Cite representative paths and functions instead of pasting large files.
- Do not expose seeded passwords or secrets verbatim; describe the risk and location.
- Do not claim a feature is active merely because a table/model exists; confirm it is reached from routes or application flow.
- When duplicate domain logic exists in controller and service layers, flag divergence risk and identify which path is actually called.
- For suspicious ORM comparisons, distinguish column-to-column operations from comparisons against string literals.
- Keep the main explanation readable; move framework-specific checklists into `references/`.

## References

- See `references/laravel-application-analysis.md` for a Laravel-specific inspection checklist and common evidence traps.
