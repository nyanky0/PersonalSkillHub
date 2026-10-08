---
name: enterprise-web-blueprint
description: "Architect data-dense enterprise B2B web applications with robust patterns."
version: 1.0.0
author: Hermes Agent (synthesized from scraped public docs)
license: MIT
tags: [enterprise, dashboard, erp, laravel, tailwind, vue, react, api, rest, design-system, b2b]
platforms: [linux, macos, windows]
triggers:
  - build an ERP dashboard
  - enterprise web app
  - B2B tool UI
  - admin panel
  - data table
  - Laravel backend pattern
  - REST API design
  - internal web tools
  - cuci steam app
  - business application UI
---

# Enterprise Web Blueprint

Data-dense, enterprise-grade patterns for ERP/B2B web apps. Synthesized from: shadcn/ui data-table guide (TanStack Table), TailAdmin template, IBM Carbon, Vercel Design, Laravel Best Practices, Microsoft Azure REST API Guidelines. Apply when building business tools (SAP B1 integrations, internal apps, admin panels) — NOT marketing/landing pages (use `popular-web-designs` + `frontend-design` for those).

## Related skills

- `popular-web-designs` — visual tokens (color/font) per brand when user wants a specific look
- `frontend-design` — design process & taste for distinctive landing/marketing pages
- `laravel` / `laravel-api` — deep Laravel implementation details
- `frontend-implementation` — building/verifying web UI pages

## Design Principles (ERP/B2B)

1. **High density wins.** Compact tables, tight forms, visible grid lines. Users scan, not browse.
2. **1 neutral + 1 brand + text shades.** No multi-color gradients, no glassmorphism, no oversized rounding.
3. **Borders over shadows.** `#E5E7EB` hairlines communicate structure; heavy shadows = consumer feel.
4. **Typography:** Inter / Segoe UI / system-ui, 13–14px base for data UI, tight line-height (1.4–1.5), font-medium for emphasis not bold everywhere.
5. **Real components, always:** pagination, sort indicators, badge statuses, empty states, row selection, keyboard nav, quick filters.
6. **No decorative SVG/hero/abstract graphics** in data tools. Icons only when they carry function (sort arrows, action menus, status dots).
7. **Accessibility floor:** visible keyboard focus, focus-visible rings, semantic HTML, sr-only labels on icon buttons.

## UI Patterns (synthesized from shadcn + TailAdmin + Carbon)

### Data Table (the centerpiece)
Structure — reusable `DataTable` wrapper around a headless table lib (TanStack Table for React; for Vue use TanStack Table Vue or build on plain `<table>`):

- **Column definitions are data, not markup**: `accessor` for data columns, `display` for action columns. Formatting lives in the column def (e.g. `Intl.NumberFormat` for currency, right-aligned numeric cells).
- **Row actions**: `display` column with `id: "actions"`, DropdownMenu trigger (⋯ icon, `sr-only` label), actions use `row.original` to get the record — e.g. copy ID, view detail, delete (confirm first).
- **Pagination**: prev/next buttons + page size selector + "X of Y row(s) selected" counter. Server-side pagination for real data (page, pageSize, total from API response).
- **Sorting**: header cell button toggles asc/desc; show ArrowUpDown icon. Server-side: sort param `?sort=field&dir=asc`.
- **Filtering**: search input above table bound to column filter. Server-side: `?q=` debounced 300ms.
- **Column visibility**: dropdown with checkboxes (nice-to-have, skip if YAGNI).
- **Empty state**: `colSpan={columns.length}` row, "No results." — better: contextual empty state with CTA.
- **Row selection**: checkboxes + bulk action bar. Reserved for tables that need batch ops.
- **Data fetching**: page.tsx/server component fetches → passes `data` to client `DataTable`. Client does NOT own fetching.

Key shadcn pattern: "Every data table I've created has been unique... provide a guide on how to build your own" — build a base `<DataTable>` per project, don't install a kitchen-sink component.

### Layout (TailAdmin pattern)
- App shell: fixed sidebar + top header + scrollable content area.
- Sidebar: nav groups with section labels, active item highlighted with brand color + subtle bg, collapsible on mobile (overlay).
- Header: page title, global search, user menu, dark-mode toggle (persisted to localStorage).
- Content grid: `grid-cols-12` with `xl:col-span-*` for metric cards + charts + tables. Cards = border + small radius (0.5rem max), not shadow.
- Metric cards: label (small, muted), value (2xl semibold), delta (green/red with arrow).

### Forms (enterprise)
- Compact: label above input, 14px input height ~38px, grid 2-col for related fields.
- Inline validation: error text under field, red border on invalid, validate on blur or submit — not keystroke.
- Buttons: primary (brand bg), secondary (outline), danger (red), ghost (row actions). Destructive actions need confirm dialog.
- Keyboard: Tab order follows visual order; Enter submits; Esc closes dialogs; focus returns to trigger on close.

### Badges / Status
- Status colors: success=green, warning=amber, danger=red, neutral=gray, info=blue.
- Badge = small pill, `bg-{color}-50 text-{color}-700 border border-{color}-200` (Tailwind), dot + label for live status.
- Never rely on color alone — pair with text label (accessibility).

## Backend Patterns

### Laravel (from laravel-best-practices)
1. **Fat models, skinny controllers.** Business logic → Service classes.
2. **Methods do one thing.** Controllers thin: validate → call service → return.
3. **Validation** in FormRequest classes, not inline in controller.
4. **No queries in Blade; eager load (N+1).** `with()` relationships, `cursor()`/`chunk()` for data-heavy exports.
5. **Mass assignment:** use `$fillable`, never pass raw request to create.
6. **Config/language files** for strings, not hardcoded text. Constants for statuses.
7. **Service container** — inject via DI, not `new Class()`.
8. **Dates:** store standard format, use accessors/mutators for display format.
9. **Don't read `.env` directly** in app code — use `config()`. (But `config:cache` in prod.)
10. **Naming conventions:** controllers plural (`OrdersController`), models singular (`Order`), tables plural (`orders`), pivot alphabetical (`order_product`).

### REST API (from Azure guidelines)
1. **Resource-oriented URLs, plural nouns**: `/api/orders`, not `/api/getOrders`.
2. **Collections**: GET list (with pagination/filter), POST create, GET/PATCH/DELETE single item. Use PATCH for partial update, PUT for full replace.
3. **Versioning**: `/api/v1/` — date-based or major.minor; never break clients silently. Deprecate with notice period.
4. **Repeatability**: `Idempotency-Key` header for POST (critical for payments/orders).
5. **Status codes**: 200/201/204, 400 (bad request), 401 (unauthenticated), 403 (forbidden), 404, 409 (conflict), 422 (validation), 429 (rate limit), 500. Error body: `{ "error": { "code": "VALIDATION_ERROR", "message": "...", "details": [...] } }`.
6. **Pagination convention**: `?page=1&pageSize=50` or cursor; response `{ "data": [...], "meta": { "total", "page", "pageSize", "totalPages" } }`.
7. **Conditional requests**: ETag / If-Match for optimistic concurrency on updates.
8. **Long-running ops**: 202 Accepted + job ID + status endpoint, not a blocking request.
9. **Retry**: client retries on 429/5xx with exponential backoff + jitter. For SAP B1 Service Layer: session cookie refresh on 401 → retry once.
10. **Tracing**: `X-Request-Id` header end-to-end for debugging.

## SAP B1 Service Layer specifics
- Cookie-based session (`B1SESSION`) or basic auth; on 401 re-login and retry (max 1 retry per request).
- OData `$top/$skip/$filter/$orderby` for pagination — map server-side pagination to these.
- Wrap writes in transaction semantics where possible; use `$batch` for multi-entity operations.
- Dates in OData: `odata:type="Edm.DateTimeOffset"`, ISO 8601.

## Verification Checklist
- [ ] Table: sortable headers, pagination, empty state, row actions — all present
- [ ] No decorative elements; every icon serves function
- [ ] Keyboard: Tab order sane, focus visible, Esc closes dialogs
- [ ] Colors: 1 neutral + 1 brand + status colors only
- [ ] Server-side: pagination/sort/filter params wired, N+1 avoided
- [ ] API: consistent error shape, status codes correct, idempotency for writes
- [ ] Responsive: sidebar collapses, tables scroll horizontally on mobile

## Anti-patterns (AI slop to avoid)
- Rainbow gradients, glassmorphism, dark-only default, giant rounded corners (20px+), decorative hero graphics in tools
- Generic "lorem ipsum" dashboards with fake charts — build with real data shape
- 400px-tall cards for 2 numbers
- Comments explaining what code does instead of why
- `new Class()` everywhere instead of DI; queries in Blade; N+1
