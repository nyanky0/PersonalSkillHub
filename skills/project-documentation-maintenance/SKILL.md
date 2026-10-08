---
name: project-documentation-maintenance
description: Use when reconciling repository docs with software behavior.
---

# Project Documentation Maintenance

## Workflow

1. **Locate the authoritative note set.** Search the repository for note directories, indexes, and local documentation rules. Read the index/rules before module notes; follow their established naming, language, and update conventions.
2. **Establish current facts.** Check working-tree status and focused diffs, then inspect the relevant implementation and tests. Separate three things in your working notes: (a) user-confirmed requirements, (b) behavior proven by current code and fresh tests, and (c) planned or unverified work.
3. **Choose the smallest documentation surface.** Update the existing module notes and, only if useful, the index or shared policy note. Avoid duplicating one feature narrative across broad FDDs, architecture reports, and every module note.
4. **Write truthful state.** Document business requirements as requirements, not proof of implementation. Mark incomplete or unverified behavior as open; specify what UI surfaces/modules and tests remain. Preserve conflicting but valid behavior explicitly (for example, a module can hide financial display while retaining data needed by integrations).
5. **Validate edits.** Review the documentation diff, ensure headings/list numbering/links remain valid, and run `git diff --check -- <docs paths>`. Report exactly which notes changed and what remains unverified.

## Rules

- Never label behavior implemented merely because a patch was attempted, a build passed, or a combined command exited zero; require focused code inspection and relevant test output.
- Do not convert a product request into an implementation fact. Keep scope boundaries explicit: UI/print presentation, stored values, and outbound integration payloads are distinct concerns.
- Preserve each note's existing structure and numbering; insert a new topical bullet without renumbering unrelated material unless the section is being deliberately renumbered in full.
- Keep plans actionable: name the remaining surfaces and verification gates, not vague TODO language.
- Prefer concise module notes over session logs; omit dates, incident narratives, transient command failures, and credentials.
- Match the repository's existing language and vocabulary. Avoid rewriting unrelated documentation.
