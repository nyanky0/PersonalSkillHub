---
name: ui-design-blueprint-prompt
description: Authoring and enforcing ultra-strict AI Context Prompts for UI Design (Zero-Slop, Exact Tailwind, Exact Schema).
---

# UI Design Blueprint Prompt Methodology
**For AI Agents Authoring UI Documentation**

This skill defines the methodology for creating "AI Context Prompts" (UI Design Standards) that enforce absolute consistency across a codebase. When the user asks to document a design, or when establishing a UI standard (e.g., IBT Web App), you MUST use this blueprint format.

## The Problem
Standard design documentation (like generic `DESIGN.md` or Figma handoffs) is often too vague for AI coding agents. AI agents tend to "hallucinate" or add "AI slop" (unnecessary badges, verbose helper texts, redundant cards) when generating UI components if the rules are not programmatic.

## The Solution: AI Context Prompt
An AI Context Prompt is a Markdown file (e.g., `UI_DESIGN_STANDARDS.md`) that acts as a strict programmatic blueprint. If another AI copies the file, it must be able to reconstruct the React component pixel-perfectly without any ambiguity.

### Key Pillars of a Blueprint Prompt:

1. **Zero Hallucination / Zero Slop Enforcement**:
   - Explicitly list what is FORBIDDEN.
   - Example: *"DILARANG merender teks narasi mekanik sistem seperti 'Konfigurasi akan disalin'."*
   - Example: *"DILARANG menambahkan badge 'Status' ganda di dalam card."*

2. **Exact Structural Hierarchy**:
   - Do not just say "Make a grid". Write the exact CSS/Tailwind wrapper.
   - Example: `div.bg-white.border.border-slate-200.rounded-xl.shadow-sm.space-y-6`
   - Example: `div.grid.grid-cols-1.md:grid-cols-3.gap-4`

3. **Data Field Schemas & State**:
   - List the exact payload names used in form state (e.g., `useForm`).
   - Detail the dropdown options explicitly so the AI doesn't invent new ones.
   - Example: `urgency_category`: `OPERATIONAL_STOPPAGE`, `SAFETY_CRITICAL`.

4. **State vs Document Status Separation**:
   - Explicitly define how document statuses should behave during approvals.
   - Example: *"Document `status` must remain exactly `draft` during the approval process. DO NOT use `pending-stage-X` in the main status. Track approval stages using a separate `approval_status` field."*

5. **Component-Level Styling**:
   - Provide the exact Tailwind classes for buttons, inputs, and labels.
   - Example: `w-full px-3.5 py-2.5 rounded-xl border border-slate-300 focus:ring-ibt-500/20`
   - Example: Button CTA: `bg-ibt-600 hover:bg-ibt-700 active:bg-ibt-800 text-white`

6. **Typography & Capitalization Rules**:
   - Explicitly define text casing rules.
   - Example: *"Semua badge status WAJIB menggunakan huruf kapital di awal (Title Case), gunakan class Tailwind `capitalize`."*

## Example Blueprint Structure

```md
# UI & Design Standards Handbook (AI Context Prompt)

## 1. Page Name (Index/List)
*File Utama: `resources/js/Pages/Path/To/File.jsx`*

*   **Pembungkus Utama**: `div.bg-white.border.border-slate-200.rounded-xl.shadow-sm.overflow-hidden`
*   **Kolom Tabel (`thead > tr`)**: `No. Transaksi`, `Branch`, `Aksi`.
*   **Larangan**:
    *   DILARANG merender kolom `Nilai Transaksi`.

## 2. Page Name (Create/Edit Form)
*   **State & Payload Data (`useForm`)**:
    *   Fields: `branch_code`, `department_code`, `requisition_type`.
*   **Komponen Input Standar (Tailwind)**:
    *   Label: `label.block.text-xs.font-semibold.text-slate-700.uppercase`
    *   Input: `w-full px-3.5 py-2.5 rounded-xl border border-slate-300`
*   **Dropdown Options Khusus**:
    *   `requisition_type`:
        *   `purchasing` (Pembelian Baru)
        *   `transfer` (Transfer Stok Gudang)
```

## When to Use This Skill
- When the user asks you to "document the design page" or "create a UI standard".
- When you are establishing a new module and need to lock in the layout so future agents don't drift from the visual language.
- When cleaning up "AI slop" from an application.

## Workflow
1. Read the existing component files (`.jsx`, `.tsx`, etc.) to extract the exact Tailwind classes and state schemas.
2. Draft the `UI_DESIGN_STANDARDS.md` (or equivalent file) using the pillars above.
3. Inject a rule in the project's root AI instructions (e.g., `AI_DEVELOPMENT_GUIDE.md` or `.cursorrules`) that mandates agents to read the blueprint before altering the UI.
