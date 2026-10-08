---
name: frontend-conditional-edits
description: "Use when editing JSX conditions. Verify scope and build."
---

# React/JSX Conditional Edits

- Trace the relevant UI branch from its module/type discriminator through the component; inspect sibling branches and wrappers before changing a guard.
- Use a unique, complete local anchor for patches. Avoid broad or truncated match text; partial anchors can wrap the wrong sibling while leaving the intended panel untouched.
- Before editing, identify every UI surface that reveals the data: list columns, row hover/popovers, detail summaries and line tables, status/approval cards, print templates, and aliases. Trace each branch from its module discriminator; hiding one table does not hide duplicate values in another component.
- After each structural JSX edit, read the opening condition and matching closing tags, then inspect the focused diff before continuing. Prefer a small data-driven guard or a shared component over manual wrapping of several nested branches; repeated edits to complex JSX can introduce mismatched closures or subtly wrong scope while still compiling. For module-specific guards, verify both excluded and neighboring allowed types, preserving table column alignment and existing render branches.
- Run the production build immediately after structural edits to catch duplicate declarations and parse errors before they are compounded; then run focused tests and inspect the rendered path when possible.
- Verify scope by searching for the exact financial/approval labels and fields in every applicable list, detail, create/edit, and print view; absence from one surface does not prove the document family is clean. For Inertia detail routes, inspect the rendered HTML and the embedded page-props payload separately: conditional JSX hides DOM values but does not remove sensitive fields from serialized props.
- For each supported document type, test both UI and print output using representative authenticated fixtures, including every alias/module code; assert exact forbidden labels/values are absent, not merely that the response is 200. Keep fixture creation aligned with dedicated model schemas: some module models do not have every shared transaction field, and a broad database seeder can fail before the presentation assertion runs. Prefer the smallest module-specific fixture and seed only required dependencies.
- Treat failure in unrelated existing tests as a separate baseline until tracing its assertion and production path; report it without broadening a narrow presentation task into unrelated business-logic changes.
- If build output writes generated assets into tracked paths, restore only generated output after recording the successful build; never discard unrelated working-tree changes.
- Before restoring or discarding any tracked file, inspect its current diff and confirm the exact scope; build success after restoring a broken or experimental edit verifies only the restored baseline, not the requested behavior. Keep the user-requested change until it passes, or report the build failure and leave the task explicitly incomplete. Never restore unrelated dirty tracked files; scope cleanup to files you changed and confirm their pre-existing diffs are preserved.
- Separate presentation acceptance from transport acceptance: for financial fields allowed in an outbound integration payload, assert at the actual outbound request/service seam that the payload still contains them, while separately asserting they are absent from rendered UI and print HTML; never sanitize shared persisted models or outbound data to satisfy a UI-only restriction.

For UI edits requiring only visual polish, follow the existing frontend design skill; this skill covers conditional logic and verification, not design direction.
