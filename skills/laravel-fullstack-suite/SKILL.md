---
name: laravel-fullstack-suite
description: "Master Laravel & PHP Fullstack Engineering Suite."
version: 2.0.0
author: Hermes Agent & Antigravity
metadata:
  hermes:
    tags: [laravel, php, inertia, react, tailwind, security, api, fullstack]
---

# Laravel Fullstack Master Suite

Standar rekayasa perangkat lunak modern Laravel + React + Inertia:



## Sub-Module: laravel

## Quick Reference

| Topic | File |
|-------|------|
| N+1 queries, eager loading, accessors, observers | `eloquent.md` |
| Validation, middleware order, dependency injection | `controllers.md` |
| Job serialization, retries, failed jobs | `queues.md` |
| Guards, policies, gates, Sanctum tokens | `auth.md` |
| XSS escaping, components, slots | `blade.md` |
| Commands, scheduling, tinker | `artisan.md` |

## Critical Rules

- Eager load relationships — `with('posts')` not lazy `->posts` in loop (N+1)
- `preventLazyLoading()` in dev AppServiceProvider — crashes on N+1, catches early
- `env()` only in config files — returns null after `config:cache`
- `$fillable` whitelist fields — `$guarded = []` allows mass assignment attacks
- `find()` returns null — use `findOrFail()` to avoid null checks
- Job properties serialize models as ID — re-fetched on process, may be stale/deleted
- `route:cache` requires controller routes — closures break cached routes
- `DB::transaction()` doesn't catch `exit`/timeout — only exceptions roll back
- `RefreshDatabase` uses transactions — faster than `DatabaseMigrations`
- `{!! $html !!}` skips escaping — XSS vector, use `{{ }}` by default
- Middleware order matters — earlier middleware wraps later execution
- `required` validation passes empty string — use `required|filled` for content
- `firstOrCreate` persists immediately — `firstOrNew` returns unsaved model
- Route model binding uses `id` — override `getRouteKeyName()` for slug

## Inertia.js + React Enterprise Performance Rules

1. **Strict Payload Throttling (No Full-Tree Dumps)**:
   - For deeply nested hierarchical data (e.g., sparepart catalogs, asset trees), NEVER pass the full recursive tree in Inertia props. Limit props to 2 levels (root → direct children) + `children_count`, and fetch sub-branches via paginated / shallow endpoints. Passing tens of thousands of rows crashes PHP with `memory_limit` (128MB) and balloons JSON props to 15MB+.
2. **Deep Link State over DOM Events**:
   - In preview panes or headless browser testing, simulated input actions do not reliably trigger React `onChange`. Always rely on URL deep links + server-side reads to hydrate modal and filter state.
3. **Staging Table Architecture for SAP B1 Integration**:
   - Always maintain a mirror/staging table per SAP object (`sap_items`, `sap_business_partners`) rather than calling the Service Layer synchronously on page loads. Staging tables guarantee UI availability when SAP is offline and make local search/filtering instantaneous.
4. **Idempotent Sync & Conflict Handling**:
   - When pushing items/UDFs to SAP B1, catch `400 already_exists` (error codes `-10`, `-2035`) and immediately fallback to `PATCH` for UDF fields.
5. **Single UDF Mapping Constant**:
   - Define UDF mappings once in the model (`const CATALOG_UDF_MAP = [...]`) so `$select`, sync scripts, and payload builders share a single source of truth.
6. **Helper Reuse Discipline**:
   - Always reuse existing repo helpers (e.g., `Utils.CreateUDF`). Never introduce redundant or competing wrappers.

---

## Sub-Module: laravel-api

# Laravel API - Steve's Architecture

Build Laravel REST APIs with clean, stateless, resource-scoped architecture.

## Quick Start

When user requests a Laravel API, follow this workflow:

1. **Understand requirements** - What resources? What operations? Authentication needed?
2. **Initialize project structure** - Set up routing, remove frontend bloat
3. **Build first resource** - Complete CRUD to establish pattern
4. **Add authentication** - JWT via PHP Open Source Saver
5. **Iterate on remaining resources** - Follow established pattern

## Core Architecture Principles

Read `references/architecture.md` for comprehensive details. Key principles:

1. **Stateless by design** - No hidden dependencies, explicit data flow
2. **Boundary-first** - Clear separation of HTTP, business logic, data layers
3. **Resource-scoped** - Routes, controllers organized by resource
4. **Version discipline** - Namespace-based versioning, HTTP Sunset headers

## Code Quality Standards

All code must follow Laravel best practices and PSR-12 standards:

1. **Preserve Functionality** - Refactorings change HOW code works, never WHAT it does
2. **Explicit Over Implicit** - Prefer clear, readable code over clever shortcuts
3. **Type Declarations** - Always use return types on methods, parameter types where beneficial
4. **Avoid Nested Ternaries** - Use match expressions, switch, or if/else for clarity
5. **Consistent Naming** - Follow PSR-12 and Laravel conventions strictly
6. **Proper Namespacing** - Organize imports logically, use full type hints

**When reviewing or refactoring code:**
- Focus on clarity and maintainability over cleverness
- Simplify complex nested logic into readable structures
- Extract magic values into named constants or config
- Remove unnecessary complexity while preserving exact behavior

## Project Structure

```
routes/api/
  routes.php              # Main entry point, version grouping
  tasks.php               # All task routes, all versions
  projects.php            # All project routes, all versions

app/Http/
  Controllers/{Resource}/V1/
    StoreController.php   # Always invokable
    IndexController.php
    ShowController.php
  Requests/{Resource}/V1/
    StoreTaskRequest.php  # Validation + payload() method
  Payloads/{Resource}/
    StoreTaskPayload.php  # Simple DTOs with toArray()
  Responses/
    JsonDataResponse.php  # Implements Responsable
    JsonErrorResponse.php
  Middleware/
    HttpSunset.php

app/Actions/{Resource}/
  CreateTask.php          # Single-purpose business logic

app/Services/             # Only when logic too complex for Actions

app/Models/
  Task.php                # HasUlids trait, simple data access
```

## Building a New Resource Endpoint

### Step 1: Model

Always use ULIDs. Keep models simple - data access only.

```php
<?php

declare(strict_types=1);

namespace App\Models;

use Illuminate\Database\Eloquent\Concerns\HasUlids;
use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;

final class Task extends Model
{
    use HasFactory;
    use HasUlids;
    
    protected $fillable = [
        'title',
        'description',
        'status',
        'project_id',
    ];

    protected $casts = [
        'created_at' => 'datetime',
        'updated_at' => 'datetime',
    ];

    public function project(): BelongsTo
    {
        return $this->belongsTo(Project::class);
    }
}
```

### Step 2: Routes

Create resource route file at `routes/api/{resource}.php`:

```php
use App\Http\Controllers\Tasks\V1;

Route::middleware(['auth:api'])->group(function () {
    Route::get('/tasks', V1\IndexController::class);
    Route::post('/tasks', V1\StoreController::class);
    Route::get('/tasks/{task}', V1\ShowController::class);
    Route::patch('/tasks/{task}', V1\UpdateController::class);
    Route::delete('/tasks/{task}', V1\DestroyController::class);
});
```

Include in `routes/api/routes.php`:

```php
Route::prefix('v1')->group(function () {
    require __DIR__ . '/tasks.php';
});
```

### Step 3: DTO (Payload)

Create at `app/Http/Payloads/{Resource}/{Operation}Payload.php`:

```php
<?php

declare(strict_types=1);

namespace App\Http\Payloads\Tasks;

final readonly class StoreTaskPayload
{
    public function __construct(
        public string $title,
        public ?string $description,
        public string $status,
        public string $projectId,
    ) {}

    public function toArray(): array
    {
        return [
            'title' => $this->title,
            'description' => $this->description,
            'status' => $this->status,
            'project_id' => $this->projectId,
        ];
    }
}
```

### Step 4: Form Request

Create at `app/Http/Requests/{Resource}/V1/{Operation}Request.php`:

```php
<?php

declare(strict_types=1);

namespace App\Http\Requests\Tasks\V1;

use App\Http\Payloads\Tasks\StoreTaskPayload;
use Illuminate\Foundation\Http\FormRequest;
use Illuminate\Validation\Rule;

final class StoreTaskRequest extends FormRequest
{
    public function authorize(): bool
    {
        return true;
    }

    public function rules(): array
    {
        return [
            'title' => ['required', 'string', 'max:255'],
            'description' => ['nullable', 'string', 'max:1000'],
            'status' => ['required', Rule::in(['pending', 'in_progress', 'completed'])],
            'project_id' => ['required', 'string', 'exists:projects,id'],
        ];
    }

    public function payload(): StoreTaskPayload
    {
        return new StoreTaskPayload(
            title: $this->string('title')->toString(),
            description: $this->string('description')->toString(),
            status: $this->string('status')->toString(),
            projectId: $this->string('project_id')->toString(),
        );
    }
}
```

### Step 5: Action

Create at `app/Actions/{Resource}/{Operation}.php`:

```php
<?php

declare(strict_types=1);

namespace App\Actions\Tasks;

use App\Http\Payloads\Tasks\StoreTaskPayload;
use App\Models\Task;

final readonly class CreateTask
{
    public function handle(StoreTaskPayload $payload): Task
    {
        return Task::create($payload->toArray());
    }
}
```

### Step 6: Controller

Create invokable controller at `app/Http/Controllers/{Resource}/V1/{Operation}Controller.php`:

```php
<?php

declare(strict_types=1);

namespace App\Http\Controllers\Tasks\V1;

use App\Actions\Tasks\CreateTask;
use App\Http\Requests\Tasks\V1\StoreTaskRequest;
use App\Http\Responses\JsonDataResponse;
use Illuminate\Http\JsonResponse;

final readonly class StoreController
{
    public function __construct(
        private CreateTask $createTask,
    ) {}

    public function __invoke(StoreTaskRequest $request): JsonResponse
    {
        $task = $this->createTask->handle(
            payload: $request->payload(),
        );

        return new JsonDataResponse(
            data: $task,
            status: 201,
        );
    }
}
```

## Response Format

Standard format for all responses:

**Success:**
```json
{
    "data": {...},
    "meta": {...}
}
```

**Error (Problem+JSON):**
```json
{
    "type": "about:blank",
    "title": "Validation Failed",
    "status": 422,
    "detail": "The given data was invalid",
    "errors": {...}
}
```

## Query Building

Use Spatie Query Builder for filtering, sorting, includes:

```php
use Spatie\QueryBuilder\QueryBuilder;

$tasks = QueryBuilder::for(Task::class)
    ->allowedFilters(['status', 'priority'])
    ->allowedSorts(['created_at', 'due_date'])
    ->allowedIncludes(['project', 'assignee'])
    ->paginate();
```

## Versioning Endpoints

When creating V2:

1. Create V2 namespace: `App\Http\Controllers\Tasks\V2\`
2. Add V2 route group in resource file
3. Add Sunset middleware to V1 routes:

```php
Route::middleware(['auth:api', 'http.sunset:2025-12-31'])->group(function () {
    // V1 routes
});
```

## Authentication Setup

Use PHP Open Source Saver JWT package:

```bash
composer require php-open-source-saver/jwt-auth
php artisan vendor:publish --provider="PHPOpenSourceSaver\JWTAuth\Providers\LaravelServiceProvider"
php artisan jwt:secret
```

Configure in `config/auth.php`:

```php
'guards' => [
    'api' => [
        'driver' => 'jwt',
        'provider' => 'users',
    ],
],
```

## Essential Setup

Add to `app/Providers/AppServiceProvider.php`:

```php
use Illuminate\Database\Eloquent\Model;

public function boot(): void
{
    Model::shouldBeStrict(); // Prevent N+1 queries
}
```

Register HttpSunset middleware in `app/Http/Kernel.php`:

```php
protected $middlewareAliases = [
    'http.sunset' => \App\Http\Middleware\HttpSunset::class,
];
```

## Anti-Patterns to Avoid

- Using auto-increment IDs instead of ULIDs
- Business logic in models
- Multiple actions per controller
- Accessing request data directly in controllers/actions
- Hidden query scopes
- Service classes when an Action would suffice
- Breaking changes without versioning
- Inconsistent response formats
- Nested ternary operators (use match expressions instead)
- Missing type declarations on methods and parameters
- Overly compact "clever" code that sacrifices readability

## Code Review & Refactoring

When reviewing or refactoring Laravel API code, apply these principles:

### Simplification Checklist

1. **Preserve Functionality** - Ensure refactorings don't change behavior
2. **Check Type Safety** - Add missing return types and parameter types
3. **Simplify Logic** - Replace nested ternaries with match expressions
4. **Extract Complexity** - Move complex conditions into named methods
5. **Verify Standards** - Ensure PSR-12 compliance with declare(strict_types=1)
6. **Improve Naming** - Use descriptive names that reveal intent

### Match Expression Pattern

Replace nested ternaries with match for clarity:

```php
// ❌ Avoid: Nested ternary
$status = $task->completed_at 
    ? ($task->verified ? 'verified' : 'completed')
    : ($task->started_at ? 'in_progress' : 'pending');

// ✅ Prefer: Match expression
$status = match (true) {
    $task->completed_at && $task->verified => 'verified',
    $task->completed_at => 'completed',
    $task->started_at => 'in_progress',
    default => 'pending',
};
```

## References

- **architecture.md** - Comprehensive architectural patterns and principles
- **code-examples.md** - Complete working examples for every component
- **code-quality.md** - Laravel best practices, refactoring patterns, and PSR-12 standards

## Templates

Template files in `assets/templates/` for quick scaffolding:
- Controller.php
- FormRequest.php
- Payload.php
- Action.php
- Model.php

---

## Sub-Module: laravel-best-practices

# Laravel Best Practices

Best practices for Laravel, organized as an index of rule files. Each rule file teaches what to do and why. For exact API syntax, verify with `search-docs`.

## Consistency First

Before applying any rule, check what the application already does. Laravel offers multiple valid approaches, and the best choice is the one the codebase already uses, even if another pattern would be theoretically better. Inconsistency is worse than a suboptimal pattern.

Check sibling files, related controllers, models, or tests for established patterns. If one exists, follow it. Don't introduce a second way. These rules are defaults for when no pattern exists yet, not overrides.

## How to Apply

1. Check the changed files, nearby code, project configuration, and relevant tests for established patterns. Deviate only for a correctness or security defect, and call the deviation out.
2. Map every affected concern to the rule index below. Read each mapped rule file before editing. Skip unrelated rule files.
3. Make the smallest coherent change. Keep the application's architecture and naming instead of introducing a second pattern for the same job.
4. Verify version-sensitive Laravel APIs for the installed version with `search-docs`, or inspect the installed framework when it is unavailable.
5. Run the narrowest relevant tests first, then the project's formatting and static-analysis checks when the change warrants them.
6. Re-read the diff against every mapped rule before finishing.

## Rule Index

Cross-cutting changes often need more than one rule file.

| Concern | Read |
| --- | --- |
| Query count, eager loading, indexes, large datasets | [`rules/db-performance.md`](rules/db-performance.md) |
| Subqueries, aggregates, complex ordering and query plans | [`rules/advanced-queries.md`](rules/advanced-queries.md) |
| Models, relationships, scopes, casts | [`rules/eloquent.md`](rules/eloquent.md) |
| Authentication, authorization, input safety, secrets, uploads | [`rules/security.md`](rules/security.md) |
| Form Requests and validation rules | [`rules/validation.md`](rules/validation.md) |
| Controllers, route binding, resources, middleware | [`rules/routing.md`](rules/routing.md) |
| Schema changes, columns, foreign keys, indexes | [`rules/migrations.md`](rules/migrations.md) |
| Jobs, retries, uniqueness, batches, Horizon | [`rules/queue-jobs.md`](rules/queue-jobs.md) |
| Cache lifetime, invalidation, locks, memoization | [`rules/caching.md`](rules/caching.md) |
| Outbound requests, retries, timeouts, fakes | [`rules/http-client.md`](rules/http-client.md) |
| Exceptions, reporting, rendering, log context | [`rules/error-handling.md`](rules/error-handling.md) |
| Events and notifications | [`rules/events-notifications.md`](rules/events-notifications.md) |
| Mailables and mail assertions | [`rules/mail.md`](rules/mail.md) |
| Scheduled tasks and overlap protection | [`rules/scheduling.md`](rules/scheduling.md) |
| Collections, lazy iteration, bulk operations | [`rules/collections.md`](rules/collections.md) |
| Blade components, attributes, composers | [`rules/blade-views.md`](rules/blade-views.md) |
| Environment values and application configuration | [`rules/config.md`](rules/config.md) |
| Tests: coverage, factories, fakes, and assertions | the `testing-best-practices` skill |
| Naming, helpers, file boundaries, PHP style | [`rules/style.md`](rules/style.md) |
| Actions, services, dependencies, application structure | [`rules/architecture.md`](rules/architecture.md) |

## Decision Rules

- Prefer framework features and existing application abstractions over new helpers or dependencies.
- Avoid speculative abstractions. Extract code when it creates a clear domain boundary, removes meaningful duplication, or makes behavior independently testable.
- Keep database access out of Blade views and prevent hidden N+1 queries across controllers, resources, jobs, and serialization.

---

## Sub-Module: laravel-demo-seeders

# Laravel — Seeder Data Demo

Untuk seeder yang mengisi **riwayat** (dokumen, approval, timeline, log), bukan sekadar master data.
Dua sifat yang menentukan nilainya: bisa dijalankan **berkali-kali tanpa menggandakan data**, dan
menghasilkan nilai yang **konsisten dengan service aplikasi** — bukan angka yang app sendiri tidak akan
pernah keluarkan.

## Aturan yang menentukan

- **Nomor dokumen dibuat lewat service penomoran aplikasi**, bukan literal di dalam seeder. Setelah
  rangkaian seeder selesai, rekonsiliasi sequence dengan data yang sudah ada (mis.
  `DocumentNumbering::syncWithExistingTransactions()`). Seeder yang menyisipkan nomor manual tanpa
  memperbarui `current_number` membuat nomor berikutnya yang di-generate UI tabrakan atau melompat.
- **Idempotent lewat penanda baris, bukan lewat nomor.** Pilih kolom stabil yang tidak dipakai untuk
  hal lain (mis. `department_name`) dan isi dengan nilai penanda khas; di awal `run()` hapus baris
  berpenanda itu **beserta data turunannya** (activity log, approval log, lampiran) sebelum membuat
  ulang. Mencocokkan nomor dokumen tidak akan pernah cocok karena nomornya berubah tiap kali dijalankan.
- **Timeline historis harus dipaksa, bukan dibiarkan.** Set `$model->timestamps = false` lalu isi
  `created_at`/`updated_at` eksplisit pada dokumen DAN pada setiap log. Tanpa itu seluruh audit trail
  bertumpuk di detik seed dijalankan dan urutan kronologisnya hilang — padahal urutan itulah yang
  sedang didemokan.
- **Sebelum mengisi relasi “copy-to” antar dokumen**, baca dokumen sumbernya dari model yang baru dibuat
  (mis. `$po->items_payload`), jangan menulis ulang payload-nya. Salinan manual akan melenceng dari
  dokumen sumber begitu seeder-nya berubah.
- **Satu tabel, banyak sumber: pilih baris sumber lewat penanda kolom yang stabil**, bukan lewat
  urutan atau ID. Data bawaan dan data hasil impor user bisa sama-sama ada di satu tabel, dan
  `orderBy('id')` akan selalu memilih yang lebih dulu masuk. Susun prioritas bertingkat dengan fallback,
  dan pastikan fallback terakhir benar-benar “apa saja yang tersedia”.
- **Daftarkan di `DatabaseSeeder` dengan guard.** Kalau sumber datanya kosong, cetak peringatan yang
  menyebut perintah pengisi datanya (“jalankan dulu `php artisan ...`”) lalu `return`; jangan
  menggagalkan seluruh `migrate:fresh --seed` karena satu seeder opsional.
- **Logika impor/berat tinggal di command artisan; seeder-nya pembungkus tipis** yang memanggil command
  itu. Dengan begitu impor bisa dijalankan bertahap dengan opsi (`--limit`, `--only=`) tanpa memuat
  semuanya sekaligus, dan seeder tetap bisa dipanggil dengan cara yang seragam.

## Verifikasi sebelum bilang “beres”

- Jalankan seeder **dua kali** dan bandingkan jumlah baris — harus sama (bukti idempotency), bukan
  bertambah terus.
- Tunjukkan satu baris hasilnya beserta asal datanya, mis. dokumen yang itemnya benar-benar berasal dari
  katalog impor — bukan baris demo bawaan yang kebetulan terpilih lebih dulu.
- Kalau seeder tidak dijalankan karena sumbernya kosong, laporkan itu sebagai hasil (beserta perintah
  pengisinya), bukan sebagai sukses.

---

## Sub-Module: laravel-expert

# Laravel Expert

## Skill Metadata

Name: laravel-expert  
Focus: General Laravel Development  
Scope: Laravel Framework (10/11+)

---

## Role

You are a Senior Laravel Engineer.

You provide production-grade, maintainable, and idiomatic Laravel solutions.

You prioritize:

- Clean architecture
- Readability
- Testability
- Security best practices
- Performance awareness
- Convention over configuration

You follow modern Laravel standards and avoid legacy patterns unless explicitly required.

---

## Use This Skill When

- Building new Laravel features
- Refactoring legacy Laravel code
- Designing APIs
- Creating validation logic
- Implementing authentication/authorization
- Structuring services and business logic
- Optimizing database interactions
- Reviewing Laravel code quality

---

## Do NOT Use When

- The project is not Laravel-based
- The task is framework-agnostic PHP only
- The user requests non-PHP solutions
- The task is unrelated to backend engineering

---

## Engineering Principles

### Architecture

- Keep controllers thin
- Move business logic into Services
- Use FormRequest for validation
- Use API Resources for API responses
- Use Policies/Gates for authorization
- Apply Dependency Injection
- Avoid static abuse and global state

### Routing

- Use route model binding
- Group routes logically
- Apply middleware properly
- Separate web and api routes

### Validation

- Always validate input
- Never use request()->all() blindly
- Prefer FormRequest classes
- Return structured validation errors for APIs

### Eloquent & Database

- Use guarded/fillable correctly
- Avoid N+1 (use eager loading)
- Prefer query scopes for reusable filters
- Avoid raw queries unless necessary
- Use transactions for critical operations

### API Development

- Use API Resources
- Standardize JSON structure
- Use proper HTTP status codes
- Implement pagination
- Apply rate limiting

### Authentication

- Use Laravel’s native auth system
- Prefer Sanctum for SPA/API
- Implement password hashing securely
- Never expose sensitive data in responses

### Queues & Jobs

- Offload heavy operations to queues
- Use dispatchable jobs
- Ensure idempotency where needed

### Caching

- Cache expensive queries
- Use cache tags if supported
- Invalidate cache properly

### Blade & Views

- Escape user input
- Avoid business logic in views
- Use components for reuse

---

## Anti-Patterns to Avoid

- Fat controllers
- Business logic in routes
- Massive service classes
- Direct model manipulation without validation
- Blind mass assignment
- Hardcoded configuration values
- Duplicated logic across controllers

---

## Response Standards

When generating code:

- Provide complete, production-ready examples
- Include namespace declarations
- Use strict typing when possible
- Follow PSR standards
- Use proper return types
- Add minimal but meaningful comments
- Do not over-engineer

When reviewing code:

- Identify structural problems
- Suggest Laravel-native improvements
- Explain tradeoffs clearly
- Provide refactored example if necessary

---

## Output Structure

When designing a feature:

1. Architecture Overview
2. File Structure
3. Code Implementation
4. Explanation
5. Possible Improvements

When refactoring:

1. Identified Issues
2. Refactored Version
3. Why It’s Better

---

## Behavioral Constraints

- Prefer Laravel-native solutions over third-party packages
- Avoid unnecessary abstractions
- Do not introduce microservice architecture unless requested
- Do not assume cloud infrastructure
- Keep solutions pragmatic and realistic

## Limitations
- Use this skill only when the task clearly matches the scope described above.
- Do not treat the output as a substitute for environment-specific validation, testing, or expert review.
- Stop and ask for clarification if required inputs, permissions, safety boundaries, or success criteria are missing.

---

## Sub-Module: laravel-frontend-build

# Laravel Frontend Build (WSL agent + Laragon Windows host)

Build/verify Laravel frontends when the agent runs in WSL and the project lives under Laragon on Windows (`/mnt/c/laragon/www/<project>`).

## Stack check first

- `package.json` scripts: usually `"build": "vite build"` — that is the project's verification command.
- `node_modules` may be missing → `npm install` before `npm run build`.
- PHP may NOT exist in WSL (`php: command not found`). Laragon ships its own:
  `/mnt/c/laragon/bin/php/php-<version>-Win32-vs16-x64/php.exe`
  List `/mnt/c/laragon/bin/php/` to find the version. Always use this exe for `artisan`.

## Tailwind 4 patterns that worked

- **Design tokens**: define in `resources/css/app.css` under `@theme { --color-<name>-<n>: #hex; }`. Custom names like `--color-carbon-100` generate utilities `bg-carbon-100`, `text-carbon-60`, etc. Also override `--font-sans` / `--font-mono` there.
- **Base styles**: `@layer base { body { @apply ... } }` for global focus-visible ring, selection color, `touch-action: manipulation`, `h2 { text-wrap: balance }`, `font-variant-numeric: tabular-nums` on `[class*="font-mono"]` (number columns align).
- **Animation + reduced motion**: define `@keyframes` + `@utility hero-fade { animation: hero-fade .6s ease-out both; }` in app.css, then apply as `motion-safe:hero-fade` with inline `style="animation-delay:.08s"` for stagger. PITFALL: arbitrary `animate-[fade_.6s_ease-out_both]` classes generate escaped selectors — manual `@media (prefers-reduced-motion: reduce)` overrides against them are fragile and break. `motion-safe:` variant handles reduced motion for free.
- **Scroll reveal (progressive section entrance)**: `app.js` adds `.js` to `<html>` first, then IntersectionObserver (threshold ~0.12, `rootMargin: '0px 0px -40px 0px'`) toggles `is-visible` and unobserves each element. CSS: `.js .reveal { opacity:0; transform:translateY(16px); transition:opacity .7s ease, transform .7s ease; }` and `.js .reveal.is-visible { opacity:1; transform:none; }`. The `.js` prefix is the no-JS guard — without it, content would stay hidden if JS fails. Reset both inside `@media (prefers-reduced-motion: reduce)`. Fallback when `IntersectionObserver` is missing: add `is-visible` to all immediately. Stagger grid siblings with inline `style="transition-delay:{{ $i * 70 }}ms"` (blade loop index).
- **Micro-interactions that match system personality**: CTA arrow slide — `group inline-flex ... gap-2` on the anchor + `<svg class="transition-transform duration-200 group-hover:translate-x-1">` (transform-only, compositor-friendly). Ambient status-dot pulse — `@keyframes soft-pulse { 0%,100%{opacity:1} 50%{opacity:.35} }` + `.animate-soft-pulse { animation: soft-pulse 2.4s ease-in-out infinite; }`, disabled in the reduced-motion block. Motion rule: one orchestrated moment (hero load + scroll reveal) + 1–2 micro-interactions max; scattered effects read as AI-generated.
- **Self-hosted fonts, no CDN**: `vite.config.js` → `laravel({ fonts: [ bunny('IBM Plex Sans', {weights:[300,400,600]}), bunny('IBM Plex Mono', {weights:[400,600]}) ] })`. Build emits `@font-face` + woff2 into `public/build/` — offline-safe, no Google Fonts dependency.

## Serve + verify loop (WSL → Windows PHP)

1. `npm run build` — if WSL node fails with `MODULE_NOT_FOUND` on `rolldown/dist/shared/binding-*.mjs` (Vite 8 native binding is win32; the `node_modules` was built by Windows npm), run via the Windows host: `cmd.exe /c "npm run build"`. Confirm `✓ built`.
2. Serve in background: `/mnt/c/laragon/bin/php/php-*/php.exe artisan serve --host=0.0.0.0 --port=8899` via terminal(background=true).
3. WSL cannot reach Windows `127.0.0.1` (separate network namespace) — `--host=0.0.0.0` alone is NOT enough; reach it via the Windows gateway IP: `GW=$(ip route show default | awk '{print $3}')` then `curl http://$GW:8899/`. See references/laragon-wsl-serving.md for the full pattern. From the Windows browser the user opens `http://127.0.0.1:8899/` directly.
4. Verify in browser: navigate to `http://<gateway>:8899/`, check accessibility snapshot, `browser_console` for JS errors, then computed-style checks.

## Verify design without a vision provider

When vision is unconfigured (browser_vision returns "No LLM provider configured for task=vision"), verify visually via `browser_console` with an expression returning `getComputedStyle` values: body font-family/background, h1 size/weight/color, button background/borderRadius/height, masthead bg/height, `document.fonts.check('16px "IBM Plex Sans"')` for font load, `document.body.scrollWidth vs window.innerWidth` for horizontal overflow. CAUTION: pick the intended element — `document.querySelector('a[href="#projects"]')` can match a nav link instead of the hero CTA; disambiguate with `.bg-blue-60` or other class selectors.

## Design direction

- Pair with `frontend-design` (process/taste) and `popular-web-designs` (token catalog) skills.
- Subject-grounded signature works: for an SAP/enterprise consultant CV page, IBM Carbon (`templates/ibm.md`) — white canvas, gray-10 layering, single blue `#0f62fe`, 0 radius, IBM Plex 300 display — read as authentic enterprise, not AI slop. Light theme with dark gray-100 masthead + footer, mono data labels, and a "project ledger" table using real artifacts (sales-order numbers) carried the identity. Numbered section markers only when content is a real sequence.
- After building, self-review against Web Interface Guidelines (web-design-guidelines skill): fetch `https://raw.githubusercontent.com/vercel-labs/web-interface-guidelines/main/command.md`, then check skip link, focus-visible, semantic HTML, scroll-mt on anchored sections, tabular-nums, text-balance, translate="no" on code-like tokens (SO numbers, tech names), theme-color meta.

## Pitfalls

- Blade-only edits (resources/views/*.blade.php) render on refresh with NO rebuild — the PHP server re-renders per request. Only `resources/css/*` and `resources/js/*` changes require `npm run build`. Don't waste a 50s Vite build on a pure blade edit.
- Hardcoded marketing numbers in landing views (e.g. "2 Lapangan Ready", "2 ARENA") drift from DB reality — render counts from the model (`Field::where('is_active', true)->count()`) and pass via route closure. If the route then queries a table, guard with `Schema::hasTable()` so unmigrated smoke tests (ExampleTest hits `/`) still return 200.

## Runtime debugging

For live-verify bugs beyond frontend (broken login/redirects from `URL::forceRootUrl`, broken
storage/`public/storage` on Windows so uploads 404, MySQL-only SQL on sqlite, double-income from
double-verifying a booking payment, spatie seeder drift → 403, route-query breaking ExampleTest,
curl smoke-testing authed routes, non-live "Live slot" landing grid), see
`references/runtime-debugging.md`.
- Hardcoded marketing numbers in landing views (e.g. "2 Lapangan Ready", "2 ARENA") drift from DB reality — render counts from the model (`Field::where('is_active', true)->count()`) and pass via route closure. If the route then queries a table, guard with `Schema::hasTable()` so unmigrated smoke tests (ExampleTest hits `/`) still return 200.
- Do NOT background a serve command with shell `&` in foreground terminal — use terminal(background=true).
- `php artisan serve` default host binds Windows loopback; from WSL it times out. Always `--host=0.0.0.0` + gateway IP.
- Windows file locks: rebuilds while a Windows app holds files may fail with `cp: cannot remove Permission denied` (write via a new filename or close the app).
- Keep the serve process as a tracked background session; it exits silently otherwise.

---

## Sub-Module: laravel-inertia-react

# Laravel + Inertia.js + React

Comprehensive patterns for building modern monolithic applications with Laravel, Inertia.js, and React. Contains 30+ rules for seamless full-stack development.

## When to Apply

Reference these guidelines when:
- Creating Inertia page components
- Handling forms with useForm hook
- Managing shared data and authentication
- Implementing persistent layouts
- Navigating between pages

## Rule Categories by Priority

| Priority | Category | Impact | Prefix |
|----------|----------|--------|--------|
| 1 | Page Components | CRITICAL | `page-` |
| 2 | Forms & Validation | CRITICAL | `form-` |
| 3 | Navigation & Links | HIGH | `nav-` |
| 4 | Shared Data | HIGH | `shared-` |
| 5 | Layouts | MEDIUM | `layout-` |
| 6 | File Uploads | MEDIUM | `upload-` |
| 7 | Advanced Patterns | LOW | `advanced-` |

## Quick Reference

### 1. Page Components (CRITICAL)

- `page-props-typing` - Type page props from Laravel
- `page-component-structure` - Standard page component pattern
- `page-head-management` - Title and meta tags with Head
- `page-default-layout` - Assign layouts to pages

### 2. Forms & Validation (CRITICAL)

- `form-useform-basic` - Basic useForm usage
- `form-validation-errors` - Display Laravel validation errors
- `form-processing-state` - Handle form submission state
- `form-reset-preserve` - Reset vs preserve form data
- `form-nested-data` - Handle nested form data
- `form-transform` - Transform data before submit

### 3. Navigation & Links (HIGH)

- `nav-link-component` - Use Link for navigation
- `nav-preserve-state` - Preserve scroll and state
- `nav-partial-reloads` - Reload only what changed
- `nav-replace-history` - Replace vs push history

### 4. Shared Data (HIGH)

- `shared-auth-user` - Access authenticated user
- `shared-flash-messages` - Handle flash messages
- `shared-global-props` - Access global props
- `shared-typescript` - Type shared data

### 5. Layouts (MEDIUM)

- `layout-persistent` - Persistent layouts pattern
- `layout-nested` - Nested layouts
- `layout-default` - Default layout assignment
- `layout-conditional` - Conditional layouts

### 6. File Uploads (MEDIUM)

- `upload-basic` - Basic file upload
- `upload-progress` - Upload progress tracking
- `upload-multiple` - Multiple file uploads

### 7. Advanced Patterns (LOW)

- `advanced-polling` - Real-time polling
- `advanced-prefetch` - Prefetch pages
- `advanced-modal-pages` - Modal as pages
- `advanced-infinite-scroll` - Infinite scrolling

## Essential Patterns

### Page Component with TypeScript

```tsx
// resources/js/Pages/Posts/Index.tsx
import { Head, Link } from '@inertiajs/react'

interface Post {
  id: number
  title: string
  excerpt: string
  created_at: string
  author: {
    id: number
    name: string
  }
}

interface Props {
  posts: {
    data: Post[]
    links: { url: string | null; label: string; active: boolean }[]
  }
  filters: {
    search?: string
  }
}

export default function Index({ posts, filters }: Props) {
  return (
    <>
      <Head title="Posts" />

      <div className="container mx-auto py-8">
        <h1 className="text-2xl font-bold mb-6">Posts</h1>

        <div className="space-y-4">
          {posts.data.map((post) => (
            <article key={post.id} className="p-4 bg-white rounded-lg shadow">
              <Link href={route('posts.show', post.id)}>
                <h2 className="text-xl font-semibold hover:text-blue-600">
                  {post.title}
                </h2>
              </Link>
              <p className="text-gray-600 mt-2">{post.excerpt}</p>
              <p className="text-sm text-gray-400 mt-2">
                By {post.author.name}
              </p>
            </article>
          ))}
        </div>
      </div>
    </>
  )
}
```

### Form with useForm

```tsx
// resources/js/Pages/Posts/Create.tsx
import { Head, useForm, Link } from '@inertiajs/react'
import { FormEvent } from 'react'

interface Category {
  id: number
  name: string
}

interface Props {
  categories: Category[]
}

export default function Create({ categories }: Props) {
  const { data, setData, post, processing, errors, reset } = useForm({
    title: '',
    body: '',
    category_id: '',
  })

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault()
    post(route('posts.store'), {
      onSuccess: () => reset(),
    })
  }

  return (
    <>
      <Head title="Create Post" />

      <form onSubmit={handleSubmit} className="max-w-2xl mx-auto py-8">
        <div className="mb-4">
          <label htmlFor="title" className="block font-medium mb-1">
            Title
          </label>
          <input
            id="title"
            type="text"
            value={data.title}
            onChange={(e) => setData('title', e.target.value)}
            className="w-full border rounded px-3 py-2"
          />
          {errors.title && (
            <p className="text-red-500 text-sm mt-1">{errors.title}</p>
          )}
        </div>

        <div className="mb-4">
          <label htmlFor="category" className="block font-medium mb-1">
            Category
          </label>
          <select
            id="category"
            value={data.category_id}
            onChange={(e) => setData('category_id', e.target.value)}
            className="w-full border rounded px-3 py-2"
          >
            <option value="">Select a category</option>
            {categories.map((category) => (
              <option key={category.id} value={category.id}>
                {category.name}
              </option>
            ))}
          </select>
          {errors.category_id && (
            <p className="text-red-500 text-sm mt-1">{errors.category_id}</p>
          )}
        </div>

        <div className="mb-4">
          <label htmlFor="body" className="block font-medium mb-1">
            Content
          </label>
          <textarea
            id="body"
            value={data.body}
            onChange={(e) => setData('body', e.target.value)}
            rows={10}
            className="w-full border rounded px-3 py-2"
          />
          {errors.body && (
            <p className="text-red-500 text-sm mt-1">{errors.body}</p>
          )}
        </div>

        <div className="flex gap-4">
          <button
            type="submit"
            disabled={processing}
            className="px-4 py-2 bg-blue-600 text-white rounded disabled:opacity-50"
          >
            {processing ? 'Creating...' : 'Create Post'}
          </button>

          <Link
            href={route('posts.index')}
            className="px-4 py-2 border rounded"
          >
            Cancel
          </Link>
        </div>
      </form>
    </>
  )
}
```

### Persistent Layout

```tsx
// resources/js/Layouts/AppLayout.tsx
import { Link, usePage } from '@inertiajs/react'
import { ReactNode } from 'react'

interface Props {
  children: ReactNode
}

export default function AppLayout({ children }: Props) {
  const { auth } = usePage().props as { auth: { user: { name: string } } }

  return (
    <div className="min-h-screen bg-gray-100">
      <nav className="bg-white shadow">
        <div className="container mx-auto px-4 py-3 flex justify-between">
          <Link href="/" className="font-bold">
            My App
          </Link>
          <span>Welcome, {auth.user.name}</span>
        </div>
      </nav>

      <main className="container mx-auto px-4 py-8">
        {children}
      </main>
    </div>
  )
}

// resources/js/Pages/Dashboard.tsx
import AppLayout from '@/Layouts/AppLayout'

export default function Dashboard() {
  return <h1>Dashboard</h1>
}

// Assign persistent layout
Dashboard.layout = (page: ReactNode) => <AppLayout>{page}</AppLayout>
```

### Laravel Controller

```php
<?php

namespace App\Http\Controllers;

use App\Http\Requests\StorePostRequest;
use App\Models\Post;
use App\Models\Category;
use Illuminate\Http\RedirectResponse;
use Inertia\Inertia;
use Inertia\Response;

class PostController extends Controller
{
    public function index(): Response
    {
        return Inertia::render('Posts/Index', [
            'posts' => Post::with('author:id,name')
                ->latest()
                ->paginate(10),
            'filters' => request()->only('search'),
        ]);
    }

    public function create(): Response
    {
        return Inertia::render('Posts/Create', [
            'categories' => Category::all(['id', 'name']),
        ]);
    }

    public function store(StorePostRequest $request): RedirectResponse
    {
        $post = Post::create([
            ...$request->validated(),
            'user_id' => auth()->id(),
        ]);

        return redirect()
            ->route('posts.show', $post)
            ->with('success', 'Post created successfully.');
    }

    public function show(Post $post): Response
    {
        return Inertia::render('Posts/Show', [
            'post' => $post->load('author', 'category'),
        ]);
    }
}
```

### Shared Data (HandleInertiaRequests)

```php
<?php

namespace App\Http\Middleware;

use Illuminate\Http\Request;
use Inertia\Middleware;

class HandleInertiaRequests extends Middleware
{
    public function share(Request $request): array
    {
        return array_merge(parent::share($request), [
            'auth' => [
                'user' => $request->user() ? [
                    'id' => $request->user()->id,
                    'name' => $request->user()->name,
                    'email' => $request->user()->email,
                ] : null,
            ],
            'flash' => [
                'success' => $request->session()->get('success'),
                'error' => $request->session()->get('error'),
            ],
        ]);
    }
}
```

### Flash Messages Component

```tsx
// resources/js/Components/FlashMessages.tsx
import { usePage } from '@inertiajs/react'
import { useEffect, useState } from 'react'

export default function FlashMessages() {
  const { flash } = usePage().props as {
    flash: { success?: string; error?: string }
  }
  const [visible, setVisible] = useState(false)

  useEffect(() => {
    if (flash.success || flash.error) {
      setVisible(true)
      const timer = setTimeout(() => setVisible(false), 3000)
      return () => clearTimeout(timer)
    }
  }, [flash])

  if (!visible) return null

  return (
    <div className="fixed top-4 right-4 z-50">
      {flash.success && (
        <div className="bg-green-500 text-white px-4 py-2 rounded shadow">
          {flash.success}
        </div>
      )}
      {flash.error && (
        <div className="bg-red-500 text-white px-4 py-2 rounded shadow">
          {flash.error}
        </div>
      )}
    </div>
  )
}
```

## How to Use

Read individual rule files for detailed explanations and code examples:

```
rules/form-useform-basic.md
rules/page-props-typing.md
rules/layout-persistent.md
```

## Project Structure

```
laravel-inertia-react/
├── SKILL.md                 # This file - overview and examples
├── README.md                # Quick reference guide
├── AGENTS.md                # Integration guide for AI agents
├── metadata.json            # Skill metadata and references
└── rules/
    ├── _sections.md         # Rule categories and priorities
    ├── _template.md         # Template for new rules
    ├── page-*.md            # Page component patterns (6 rules)
    ├── form-*.md            # Form handling patterns (8 rules)
    ├── nav-*.md             # Navigation patterns (5 rules)
    ├── shared-*.md          # Shared data patterns (4 rules)
    └── layout-*.md          # Layout patterns (1 rule)
```

## References

- [Inertia.js Documentation](https://inertiajs.com/) - Official Inertia.js docs
- [Laravel Documentation](https://laravel.com/docs) - Laravel framework docs
- [React Documentation](https://react.dev/) - Official React docs
- [Ziggy](https://github.com/tighten/ziggy) - Laravel route helper for JavaScript

## License

MIT License. This skill is provided as-is for educational and development purposes.

## Metadata

- **Version**: 1.0.1
- **Last Updated**: 2026-01-17
- **Maintainer**: Asyraf Hussin
- **Rule Count**: 24 rules across 6 categories
- **Tech Stack**: Laravel 10+, Inertia.js 1.0+, React 18+, TypeScript 5+

---

## Sub-Module: laravel-landing-pages

# Laravel Landing Pages (blade + Tailwind 4 + Vite)

Workflow untuk membangun/polish halaman di proyek Laravel (`resources/views/*.blade.php`, Tailwind 4 via `@tailwindcss/vite`), preview lokal via Laragon (WSL2), dan deploy ke Vercel sebagai static export.

## Setup yang perlu dicek dulu

- `resources/views/welcome.blade.php` — halaman utama (route `/` di `routes/web.php`)
- `resources/css/app.css` — `@import 'tailwindcss'` + `@theme { --color-*, --font-* }` (custom tokens via `--color-<name>-<shade>` otomatis jadi class `bg-<name>-<shade>` dst)
- `vite.config.js` — fonts self-hosted via `bunny('Font Name', { weights: [...] })` (offline aman, ga butuh Google Fonts CDN)
- Verify: `npm run build` (WAJIB — lihat pitfall di bawah). WSL + Tailwind 4 vite plugin: transform ~45s → timeout 60s default kena (exit 124); retry dengan `timeout=300` jalan. Bukan error permanen — retry pattern, jangan panik.

## Pitfall: class baru di blade TIDAK langsung jalan

Tailwind scan source file saat build. Class yang belum pernah muncul di file manapun TIDAK ada di CSS build lama → elemen render natural size / broken layout (contoh nyata: `h-44 w-44` baru dipasang, img render 512px penuh).

**Setiap ganti/add class di blade → `npm run build` dulu, baru verify browser.** Blade text edits aja (tanpa class baru) auto-render tanpa build.

## Pitfall: dist sync — blade edits tidak otomatis masuk dist/

`dist/index.html` adalah statis, bukan rendered blade. Kalau kamu edit blade (tambah class, ubah markup), dist/index.html TIDAK otomatis update. Dua jalur:

1. **Server jalan** (recommended): `curl -s "http://$GW:8899/" -o dist/index.html` + `sed` hapus absolute host. Ini render blade via PHP.
2. **Server mati**: edit dist/index.html manual — apply class/markup changes yang sama ke dist. Juga update asset references kalau hash berubah: cek `public/build/manifest.json` untuk nama file baru (`app-XXXXX.css`, `app-XXXXX.js`), lalu update `<link>` dan `<script>` di dist/index.html.

**Setelah edit dist, WAJIB juga copy build assets:** `cp -r public/build/* dist/build/`

## Pitfall CSS: animation fill-mode vs hover transform

`animation: x 0.6s ease-out both` nge-hold keyframe akhir permanen → menimpa `:hover { transform: ... }` selamanya. Kalau elemen beranimasi load DAN butuh hover transform (scale/translate), pakai `fill-mode: backwards` — efek sama selama delay+run, lepas setelah selesai.

## Preview lokal (WSL2 + Laragon — PHP tidak ada di WSL)

```bash
# serve pakai php.exe Windows, WAJIB bind 0.0.0.0:
/mnt/c/laragon/bin/php/php-8.3.30-Win32-vs16-x64/php.exe artisan serve --host=0.0.0.0 --port=8899
# akses dari WSL: gateway IP (bukan 127.0.0.1 — loopback Windows ≠ WSL):
GW=$(ip route show default | awk '{print $3}')   # mis. 172.x.x.1
# dari browser Windows: http://127.0.0.1:8899/
```
Server mati diam-diam (exit 255) → cek `process poll` lalu restart.

## Verify visual tanpa vision provider

Kalau `browser_vision`/`vision_analyze` gagal (provider belum dikonfigurasi), verifikasi via `browser_console` computed styles:
- bg/warna/ukuran/radius elemen kunci, `img.naturalWidth`, overflow: `document.body.scrollWidth - window.innerWidth` (scrollbar bikin -15px, itu normal, bukan overflow)
- JS error: `browser_console` kosong = bersih

## Pola animasi yang sudah terbukti (restrained, anti-slop)

- Scroll reveal: `.js` guard di `<html>` (JS-only, no-JS user tetap lihat konten), IntersectionObserver, unobserve setelah trigger, `prefers-reduced-motion` → langsung tampil. CSS: `.js .reveal { opacity:0; translateY(16px); transition }` + `.js .reveal.is-visible { ... }`
- Stagger: `transition-delay` inline / custom property `--d: ...ms` per item (loop blade `$i * 45ms`)
- Pop-in stagger (tags/items): `.js .reveal .pop-in { --d }` → `.is-visible .pop-in`
- Count-up stats: `[data-count]` + `data-decimals`, IntersectionObserver threshold 0.5, rAF ease-out cubic, reduced-motion → nilai final instan, `aria-label` nilai akhir di parent
- Typewriter: span kosong di HTML + `<span class="sr-only">` teks penuh (a11y) + span aria-hidden; reduced/no-JS → isi penuh langsung
- Draw-line: `scaleX(0)` origin-left → `scaleX(1)` saat parent `.reveal.is-visible`
- Progress bar + back-to-top: satu scroll handler rAF-throttled + passive, `scaleX(scrollY/max)`, toggle `.visible` di >600px
- Hover micro: arrow slide (`group-hover:translate-x-1 opacity-0→100`), underline grow (`.link-underline::after` scaleX), foto ring (`-inset-1` ring + `scale(1.02)`)
- Semua transform/opacity-only (compositor friendly), `motion-safe:` untuk load animasi, override transition none di media query reduced-motion

## Micro-interactions lanjutan (terbukti di iterasi 2)

Pola lengkap + CSS/JS exact: `references/micro-interactions.md`. Ringkasnya:

- **Toggle widget state machine** — satu listener untuk semua state = bug. Contoh nyata: tombol API console, klik "DISCONNECT" malah connect ulang karena listener jalanin flow connect terus. Fix: flag `connected` + branch di awal listener (state connected → jalankan teardown, bukan re-run setup).
- **Micro-chart CSS-only (tanpa JS tambahan)**: sparkline SVG `pathLength="1"` + `stroke-dasharray:1; stroke-dashoffset:1→0`; sparkbar `scaleY(0)` + `transform-origin: bottom`; dots `scale(0)`; progress bar `width:0→100%` lewat CSS `.js .reveal.is-visible .sparkbar-fill { width:100% }` (CSS override utility/inline width). Semua trigger pakai class `.reveal.is-visible` yang sudah ada — nol observer tambahan.
- **Infinite ticker/marquee**: dua group konten identik + track `flex w-max whitespace-nowrap` + `translateX(-50%)` loop; `:hover { animation-play-state: paused }`; reduced-motion → `animation: none` (konten tetap tampil statis, jangan display:none — dekoratif tapi hidup). Pakai `aria-hidden="true"` (duplikat teks = noise screen reader).
- **Inline `transition-delay` membunuh animasi filter** — row dengan stagger `transition-delay: {{$i*45}}ms` inline: fade-out pas filter lambat berantai (row terakhir delay 450ms). Fix: `.is-filtered-out { transition-delay: 0ms !important }` (hide cepat serempak, show boleh cascade lagi).
- **Reveal direction variants**: `.js .reveal.reveal-left { transform: translateX(-24px) }` + rule reset dengan specificity TINGGI `.js .reveal.is-visible.reveal-left { transform:none }` — kalau specificity sama, order di file menentukan dan default `.is-visible` bisa kalah.
- **`--d` inherit**: custom property `--d` di parent li ikut ke child — child animation pakai `transition-delay: var(--d, 0ms)` tanpa set ulang per elemen (contoh: cert validity bar di dalam li pop-in).
- **Cross-link interaksi antar section**: skill tag → filter ledger. Mapping skill→kategori via `@php $filters = [...]` di dalam `@foreach` blade; klik tag → `document.querySelector('.project-filter[data-filter="X"]').click()` (reuse listener filter yang sudah ada, jangan duplikasi logic) + `scrollIntoView({behavior:'smooth'})`.
- **Status/validity bars pakai data nyata**: cert validity = sisa bulan / 36 horizon, label "29 MO LEFT" / "EXPIRED", warna biru vs abu — informatif bukan hiasan.

## Micro-interactions iterasi 3 (hover depth + hero)

Pola lengkap + CSS/JS exact: `references/micro-interactions.md` §10–13. Ringkasnya:

- **Hover effect harus di-guard `@media (hover:hover) and (pointer:fine)`** — jangan modal `:hover` saja; touch device bikin state hover macet (stuck). Contoh: project-row geser `translateX(4px)` + border-left biru, client name berubah biru.
- **Headline gradient drift**: `background-clip:text` + `background-size:200%` + keyframes `background-position` drift (9s loop). Reduced-motion → reset ke `-webkit-text-fill-color: var(--color-ink)` polos (jangan tinggalin gradient di aksen statis — itu overkill untuk reduser).
- **Duotone foto**: default `filter: grayscale(0.85)`, hover → `grayscale(0)` + `scale(1.02)`. Reduced-motion → `filter:none` (jangan biarkan foto abu-abu permanen).
- **Parallax bounded**: translateY(scrollY * 0.08) di profil hero — cuma aktif selama hero di viewport (cek `scrollY < hero.offsetHeight`), reset transform di luar itu. Masuk ke scroll handler rAF yang sudah ada, jangan handler baru. JS guard reduced-motion (CSS media query tidak sampai ke transform inline).

## Pitfall: header shadow + scroll handler guard

Tambah elemen baru ke scroll handler yang sudah ada (progress bar/back-to-top) — jangan buat handler kedua. Guard `if (a || b || c)` harus include elemen baru, dan `update()` toggle class (`header.classList.toggle('is-scrolled', scrollY > 8)`). Header perlu class `site-header` di HTML supaya selector CSS/JS konsisten.

## Pier88-style premium motion (teardown pier88coast.com)

Klien minta "animasi kayak [situs premium]" — rahasianya bukan library, tapi kombinasi timing + blur + parallax CSS-var. Full code: `references/pier88-teardown.md`.

- **Cinematic reveal** = `opacity 0→1` + `filter: blur(5px→0)` + `translate3d(0,24px→0)`, timing via CSS custom props, IO `threshold .18, rootMargin "0px 0px -8%"`, unobserve. Blur-nya yang bikin sinematik.
- **Split-line heading**: `.split-line{overflow:hidden}` > `.line-inner{translateY(110%→0)}` `cubic-bezier(.19,1,.22,1)`; kata aksen script italic serif mid-line.
- **Parallax tanpa ScrollTrigger**: rAF + ticking guard → scroll set CSS var `--bg-y = centerOffset*46px` → bg gerak berlawanan konten. Pinned-drift: container `height~5000px` relative → inner sticky → transform anak per progress.
- **Carousel**: GSAP `fromTo` 0.46s stagger .04 power3.out; WAJIB `gsap.set` non-aktif slide hidden di init. **Kalau CDN gagal load, vanilla translateX + transition cukup** — lib CDN = progressive enhancement, core UX jangan bergantung.
- **Jangan pasang elemen dekoratif floating yang ke-parallax** — user tolak foto gulai mengambang di hero ("aneh ngikutin turun"). Parallax background = premium; parallax foto produk random = rusak.

## Desain anti-AI-slop (preferensi user)

- Rujuk design system nyata: load `frontend-design` + `popular-web-designs` (template `templates/ibm.md` — IBM Carbon — cocok untuk tema enterprise/SAP/konsultan)
- Hindari 3 default AI: cream+terracotta serif, near-black+acid green, broadsheet hairline
- Satu aksen warna, 0 radius (Carbon), flat tanpa shadow, mono untuk data (IBM Plex Mono, tabular-nums)
- **Jangan usulkan loading screen untuk page statis** — pattern AI-slop, user ditanya dan menolak
- Data asli user = signature (contoh: project ledger pakai SO number SAP asli)

## Aksesibilitas baseline (dari Web Interface Guidelines review)

skip link ke #main, `:focus-visible` outline global, heading hierarkis, `scroll-mt-24` pada section ber-id (sticky nav), `tabular-nums` angka, `text-wrap: balance` h2, `meta theme-color`, `translate="no"` pada SO number/brand teknis, `alt` + `width/height` img (anti-CLS), `fetchpriority="high"` LCP image.

## Pitfall: hero dua-kolom tinggi tidak seimbang → void gede

Gejala umum: ada space kosong besar di section awal/hero. Biangnya bukan padding — **dua flex column tinggi beda lancip** + `items-center`.

Contoh nyata: kiri = teks (name+para+CTA, ~360px), kanan = foto+lokasi+2 widget terminal numpuk jadi 732px. `items-center` nge-center kolom PENDEK terhadap kolom PANJANG → void gede, bergeser kiri↔kanan tergantung kolom mana yang lebih pendek. Pertama void 274px di bawah CTA kiri; setelah widget dipindah, void 491px di kanan bawah foto. `lg:py-32` (128px) ikut menggembungkan hero ke ~919-988px.

**Diagnosis tanpa vision provider** (browser_vision/vision_analyze 401): ukur pake `browser_console`:
```js
const r=hero.getBoundingClientRect(), L=leftCol.getBoundingClientRect(), R=rightCol.getBoundingClientRect();
({heroH:Math.round(r.height), leftBottom_rel:Math.round(L.bottom-r.top), rightBottom_rel:Math.round(R.bottom-r.top), gapRight:Math.round(r.bottom-R.bottom), gapLeft:Math.round(r.bottom-L.bottom)})
```
Gap besar di sisi mana = di sanalah void. Kalau salah satu gap gede banget (~300px+), itu kolom pendek ke-center vs kolom panjang.

**Fix (urut):**
1. `lg:items-center` → `items-start` (top-align). Kedua kolom rata atas, void jadi whitespace bawah natural, BUKAN void tengah mencolok.
2. **Sebarkan widget, jangan numpuk di satu kolom.** Kanan (foto+lokasi+SYS_BRIEF) vs kiri (teks+CTA+API_console) → tinggi seimbang (~500 vs ~660), gap turun ke level padding normal (~128px).
3. Kalau masih tinggi, potong `lg:py-32` → `lg:py-24`; jangan nambah konten fiktif cuma buat nyamain tinggi.
- Mobile: `flex-col-reverse` → child DOM pertama tampil paling atas. Atur urutan DOM supaya foto di atas teks di mobile, dan kiri↔kanan di desktop (satu struktur kolom ini).

## Deploy Vercel (static export — Laravel tidak jalan native di Vercel)

```bash
npm run build
rm -rf dist && mkdir -p dist
curl -s "http://$GW:8899/" -o dist/index.html
sed -i 's|http://172.26.176.1:8899||g' dist/index.html   # @vite render absolute host — wajib root-relative
cp -r public/build dist/build && cp -r public/images dist/images
npx -y vercel@latest deploy dist --prod --yes
```
Detail CLI/auth/API rename: `references/vercel-cli.md`

## Verifikasi deploy

`curl -s -o /dev/null -w "%{http_code}" <url>` untuk index + css + js + gambar (semua harus 200), lalu `browser_navigate` ke URL production, cek struktur + 0 JS error.

---

## Sub-Module: laravel-modul-removal

# Menghapus / menggabungkan modul dokumen (Laravel)

Modul yang dipakai di banyak map (routing, config, seeder, peta relasi, permission) tidak bisa
dihapus dengan find-replace. Urutan yang terbukti aman:

1. **Peta dulu, baru ubah.** `grep -rn "<MODUL>" app config database resources/js tests routes`
   dengan `output_mode=count` per file. Tandai mana array-key, mana string literal.
2. **Strip bertahap, self-verifying.** Jangan buang token inline mentah. Untuk file PHP, terapkan
   kandidat edit per baris lalu `php -l` file itu: kalau gagal parse, kembalikan baris tersebut dan
   catat untuk edit manual. Blind replace pernah menghasilkan `['code' => , 'name' => ...]`.
3. **Cek 4 jebakan ini setiap kali:**
   - **Key array ganda** — `'ITR' => X` menjadi `'IT' => X` di map yang sudah punya `'IT'`:
     nilai lama hilang tanpa error.
   - **Loop diri sendiri** — peta copy-to/relasi yang jadi `'IT' => [IT]` membuat rekursi tanpa
     henti. Gejala: fatal memory di `helpers.php`/`ReportTrimmer`, bukan stack overflow. Modul
     terminal tidak boleh punya target dirinya sendiri.
   - **Token inline hilang** — `['RL','PO','ITR']` → `['RL','PO']` tetap valid sintaks tapi salah
     arti. Hanya test yang bisa menangkap ini.
   - **Nomor dokumen demo bentrok** — dua seeder bisa menulis nomor sama setelah modul digabung →
     `UNIQUE constraint failed`. Beri nomor unik saat menyentuh seeder.
4. **Bersihkan datanya juga, secara generik:** scan semua tabel untuk kolom teks bernilai modul
   (`LIKE '%<MODUL>%'`), hapus baris ber-kolom modul, rombak sel JSON terpisah.
5. **Verifikasi:** seluruh test suite hijau + `grep -rn "<MODUL>"` = 0 di
   `app config database resources/js tests`. Kalau suite tidak jalan / error-nya hilang,
   baca `references/test-suite-triage.md`.

---

## Sub-Module: laravel-security-audit

# Laravel Security Audit & Hardening

Audit a Laravel (typically Inertia + React) app for security gaps, fix them minimally, and prove no regression. Applies when findings come from a prior report, a reference/dummy checkout, or a fresh review.

## Workflow (in order)

1. **Verify every finding against the live code first.** Audit reports often reference a different checkout (dummy/staging) or stale line numbers. Grep the actual pattern — `getFile\(\)|getLine\(\)`, `approvalEngine->approve(`, `isSuperAdmin`, the route group — a finding may already be fixed, partially fixed, or moved. Patch only the real gaps.
2. **Fix the root cause with a single source of truth.** Put a shared rule in the service/middleware layer so every caller inherits it (e.g. amount-limit check inside `ApprovalEngineService::approve` rather than per controller).
3. **Match existing conventions.** Same guard style, same `abort(403, '...')` wording, same log facade usage.
4. **Prove no regression with a baseline test.** Run the affected test files, then `git stash` → run the SAME files on HEAD → `git stash pop`. A failure identical before and after is pre-existing; leave it and say so — do not call it a regression or chase it.
5. **Document each finding + fix** (severity, file, exact change, verification) in one review report; list anything left pending as a decision for the user.

## Vulnerability classes → minimal fix

- **Mutating route without role guard** → move into `Route::middleware([EnsureUserHasRole::class.':superadmin'])->group(...)` AND add an `abort(403)` guard in the controller (defense-in-depth).
- **IDOR / BOLA (ownership)** → guard `if ($model->created_by !== auth()->id() && ! auth()->user()->isSuperAdmin()) abort(403, ...)` on submit/update/destroy/duplicate.
- **Over-exposed public endpoint** → replace `Model::with([...])` with an explicit column whitelist `first(['a','b','c'])` on public/QR-verify routes.
- **Path/line leak in flash messages** → `Log::error($e->getMessage(), ['file'=>$e->getFile(),'line'=>$e->getLine()])`, return a generic message to the user.
- **Approval-limit bypass via bulk endpoint** → enforce the limit in the shared service `approve()` method, gated to non-stage approvers (see pitfall below).
- **Missing CSP** → add a CSP that lists the app's real asset sources (see pitfall).
- **Session cookie not `secure`** → `'secure' => env('SESSION_SECURE_COOKIE', env('APP_ENV') === 'production')`.
- **User/delegation enumeration** → scope list queries to the current user (unless superadmin) and `select()` minimal columns.

## Pitfalls

- **Approval amount limit must apply only to non-stage approvers** (`! $canApproveStage`). A stage approver is explicitly assigned to the document and is NOT bound by the SAP B1 authorization amount — a naive limit check inside `approve()` breaks legitimate approvals. Copy the existing condition from the single-approve controller.
- **Run the baseline test before claiming a regression.** Test setup drift and hand-written mocks cause pre-existing failures unrelated to your change.
- **Big test suites exhaust the 128M default and print `Allowed memory size exhausted`.** Run `php -d memory_limit=-1 artisan test ...`.
- **Unicode/emoji in source renders as `�` or `***` in terminal/tool output** — `::where(` can display as `::***`. Do not edit code based on that rendering; confirm with `hexdump`/`php -l` first (the file is usually fine).
- **patch fuzzy-matching finds the real emoji** even when you paste `�` in `old_string` — you don't need the exact codepoint to delete an emoji.
- **Find emojis in UI code:** `rg -n --pcre2 '[\x{1F300}-\x{1FAFF}\x{2600}-\x{27BF}\x{2B00}-\x{2BFF}\x{FE0F}]' -g '*.jsx'`; add `\x{2300}-\x{23FF}` to catch symbols like ⏱️. Replace emojis in rendered UI with Lucide icons or clean text (keep console.log debug emojis — not user-facing).
- **A CSP that misses real sources breaks the app.** Include Google Fonts (`style-src`/`font-src`/`connect-src`), `cdn.tailwindcss.com` for standalone print Blade views, and `ws: wss: http://localhost:*` for Vite HMR.
- **`composer` is often not on PATH.** Invoke the phar with a native Windows path: `php C:/Users/<user>/.../composer.phar audit` — never `/c/...` (MSYS path conversion breaks it).

---

## Sub-Module: laravel-security-hardening

# Laravel Security Audit & Hardening

Audit source-first: find REAL exploitable issues, not OWASP checklist padding. Fix with minimal diff. Verify with PHPUnit + artisan.

## Workflow

1. Map input surface first: `routes/web.php` + `routes/api.php` (which routes are PUBLIC or only `auth` — not superadmin), controllers, middleware (Laravel 11: `bootstrap/app.php`).
2. Grep vuln classes (see references/vuln-patterns.md for code-level detail):
   - `env('X', 'default')` in config — hardcoded default credentials
   - `if ($signature)` — optional webhook HMAC = auth bypass
   - POST routes outside the admin middleware group that call `Artisan::call` or trigger SAP/external writes
   - Controllers with route-model binding + NO ownership check (IDOR)
   - `two_factor` columns written but never checked in login flow (dead 2FA)
   - Uploads validated only `file|max:` without `mimes:` — + missing `storage:link` = dormant RCE
   - `fputcsv`/export with user-controlled cells (CSV formula injection)
   - login route without `throttle`
   - `count()+1` sequence generation (race → duplicate numbers)
   - DB writes inside GET handlers (violates idempotency → duplicate records on refresh, race conditions)
   - API fields with implicit enum (kategori, type, status) validated only `required` — arbitrary strings pass through
   - Third-party API tokens hardcoded in controllers or route closures instead of `config()` + `.env`
- `dangerouslySetInnerHTML` in React frontends displaying backend error messages (XSS vector)
- Inertia over-shared props: `Inertia::render(..., ['user' => $user])` full model (hash/2FA/tokens) — whitelist via `->only()`; `HandleInertiaRequests::share()` dumping whole `auth()->user()`; authz skipped because "button hidden in React" — every mutating action still needs policy check
- Bearer/auth token in localStorage (Inertia or SPA) — XSS reads it; keep cookie-based server auth
3. Confirm dynamically when possible (server up, real requests). If not, mark "requires deployment testing" — never claim confirmed.
4. Report only exploitable findings; note what's SOLID (no SQLi, escaped blades, CSRF) — builds trust.

## Fix patterns (verified)

- **Authorization helper** — add to controller: `canManage($tx)` = `superadmin || creator || approver-of-current-stage`. Use for cancel/retry/attachment access. Approve/reject often already guarded by engine — check before adding.
- **Admin routes**: move to `Route::middleware([EnsureUserHasRole::class . ':superadmin'])->group(...)`. Monitor/index views stay `auth`; only mutating actions move.
- **Webhook**: signature REQUIRED, `hash_equals`, secret from `env()` only — never a default in code. Empty secret = reject all (401) by design.
- **Login throttle**: `Route::post('/login', ...)->middleware('throttle:5,1')`.
- **APP_DEBUG off in production**: grep `.env` — `APP_DEBUG=true` exposes `/_ignition/health-check` returning `{"can_execute_commands":true}` and a live `execute-solution` endpoint (CRITICAL surface + guaranteed stack-trace/env leak on error pages). One-line fix: `APP_DEBUG=false`. The recurring failure: local `.env` copied to deploy as-is. Note: `spatie/laravel-ignition` 2.x ≠ CVE-2021-3129 (that was `facade/ignition`) — don't claim the CVE, claim the surface + leak.
- **Security headers**: Laravel 11 emits none by default. Add X-Frame-Options: SAMEORIGIN, X-Content-Type-Options: nosniff (minimum), CSP if feasible — via `$middleware->web(append: [...])` in `bootstrap/app.php` or web-server level. `expose_php=Off` in php.ini kills the `X-Powered-By` fingerprint.
- **CSV cells**: prefix `'` when cell starts with `= + - @`.
- **Sequence race**: wrap in `DB::transaction` + `lockForUpdate()` on last row of same prefix, read seq from `substr($number, -4)`.
- **Passwords**: `min:8` in user create/update validation.
- **GET side effects**: move DB writes from GET handlers to scheduled Artisan commands or dedicated POST endpoints. Keep GET read-only. If a fallback check must stay in GET, wrap in `DB::transaction` + `lockForUpdate` to prevent race-condition doubles.
- **Enum validation**: `'kategori' => 'required|in:a,b,c'` + `'jumlah' => 'required|numeric|min:1'`. Never accept bare `required` on fields with a known value set.
- **Hardcoded tokens**: move to `config/services.php` → `env()`. Grep for string literals in controllers/closures that look like API keys.
- **Inertia over-shared props**: pass explicit whitelisted arrays or `Model::only([...])`-style selects; strip `HandleInertiaRequests::share()` to known-safe keys (`auth.user` → pick fields: id, name, role). Never send password_hash, two_factor_secret, remember_token, api tokens as props.

- **Read-route IDOR (GET often forgotten)**: same `canManage`-style helper but read scope — `canView($tx)` = superadmin || creator || current approver || user_id in approval_logs. One-line `abort(403)` at top of `show()`, `printPdf()`, `export()`, compare/copy views. `export()` for non-admins: `->where('created_by', $id)->orWhereIn('id', ApprovalLog::where('user_id',$id)->pluck('transaction_id'))`.
- **Public hash-lookup route DoS**: delete fallback `->get()` loops (unique index makes `where()` sufficient), add `->middleware('throttle:10,1')`.
- **QR for 2FA secrets**: never an external QR image API (`api.qrserver.com?data=otpauth://...` leaks the TOTP secret). Use `qrcode.react` (`QRCodeSVG`) client-side — zero transitive deps; `npm install qrcode.react --save` + swap the `<img src>` for `<QRCodeSVG value={uri}>`. Do NOT hand-roll a QR encoder — format-spec bugs make unscannable codes; this is the rare case a tiny dep is the correct call.
- **Exception leak in flash**: replace `'... ' . $e->getMessage()` in user-facing `back()->with('error', ...)` with generic text + `Log::warning(...$e->getMessage())`. In Laravel 11 without `use Log`, use FQCN `\Illuminate\Support\Facades\Log::warning(...)` inline.
- **Accessor masking NULL columns**: if `getXAttribute()` derives a value for NULL, `where('x', $model->x)` silently never matches. When deleting fallback lookup loops, drop such accessors too, generate on `creating()`, backfill legacy rows via migration (`whereNull('x')` loop with fresh hashes).

## 2FA TOTP without dependencies

Full RFC 6238 TOTP in ~70 lines, no package: copy `templates/TotpService.php`. Base32 secret (A-Z2-7), SHA1, 6 digits, 30s, ±1 window. Verify against RFC 6238 test vector: secret base32 `GEZDGNBVGY3TQOJQGEZDGNBVGY3TQOJQ` (ASCII "12345678901234567890"), counter 1 (T=59) → `287082`.

Login flow that avoids remember-cookie bypass:
1. Manual verify: `Hash::check($password, $user->password)` instead of `Auth::attempt`.
2. If 2FA enabled: `session()->put('2fa:user_id', ...)` + `2fa:remember` → redirect challenge. NO `Auth::login` yet (no remember token issued).
3. Challenge POST: verify TOTP → `Auth::login($user, $remember)` → `session()->regenerate()`.
4. Enable/disable: require current password + valid TOTP code. Stage pending secret in session during setup (`2fa:pending_secret`), only show secret on setup page, never persistently.

## Verification on WSL (Laragon project, no Linux php)

```bash
PHP="/mnt/c/laragon/bin/php/php-8.3.30-Win32-vs16-x64/php.exe"
"$PHP" -l <file>                          # syntax per file
"$PHP" vendor/bin/phpunit                 # sqlite :memory: per phpunit.xml
"$PHP" vendor/bin/pint <changed-files>    # format only touched files
"$PHP" artisan route:list -v              # verify middleware guards on moved routes
```

## Pitfalls

- **Pint rewrites routes**: it converts `\App\Http\Controllers\X::class` fully-qualified refs into `use` imports. A route you added with a short name but forgot the import compiles fine (`php -l` passes) but dies at `artisan route:list` with `ReflectionException: Class "XController" does not exist`. ALWAYS run `route:list` after pint on routes files.
- **Old tests assert insecure behavior** (webhook without signature returns 200, 2FA enable without code). Update them to the new secure behavior — including a negative assertion (unsigned → 401) — instead of deleting.
- **Don't pint-reformat the whole repo** — pre-existing non-clean files (migrations, seeders) produce huge diffs. Only files you touched.
- `.env` may lack the new required keys (e.g. `SAP_WEBHOOK_SECRET`) — app then rejects webhooks by design. Hand the user a `.env` template; don't write secrets into source.
- Repos often have large pre-existing uncommitted changes — `git diff --stat` mixes them with yours. Check `git status` per file before claiming what you changed.
- **Route-order shadowing**: a literal route (`/resource/create`) in a later stricter middleware group is captured by an earlier `{param}` route in a weaker group → binding ModelNotFound 404 (or worse, weaker-guard reachability). Fix: `->whereNumber('param')` on the param route. Diagnose via scratch feature test printing `$response->exception` — the real exception behind a bare 404. Use `git stash` + re-run to prove whether YOUR diff caused it (working trees are often already dirty). Confirm against HEAD: `git show HEAD:routes/web.php | grep <route>` — if the literal route sits in a different group in HEAD than in the working tree, the shadowing came from someone else's uncommitted move, not your patch.
- **Run the FULL test suite after every fix batch** — deleting redundant/fallback code can surface bugs the dead code was masking (e.g. fallback lookup loop hiding an accessor-NULL mismatch). Grep and `php -l` do not catch this; the suite does.
- PHPUnit may drop a custom assertStatus message — when a route-coverage loop fails with no URI info, temporarily add `assertSame(200, $response->status(), "DEBUG route [uri]")` in the loop, re-run, remove after.
- **Patch-tool brace duplication**: the fuzzy patch tool can collapse/dupe closing braces when the anchor string appears twice — after any multi-line patch, re-read the file (or `php -l`) before running tests; LSP "Undefined method 'id'" on Eloquent models is a false positive, syntax errors are not.
- **Second-sweep guard reuse**: when a user asks to crosscheck after the main fix pass, expect to find (a) JSON GET actions (`relationshipMap`, lineage trees) still unguarded and (b) secondary controllers (comments) on the primary resource's route prefix missing the parent's guard. Reuse the main controller's `canView()` — make it public, call via `app(TransactionController::class)->canView($tx)` — rather than extracting a service mid-fix. Verify with `php -l` + full suite + `npm run build` (front-end fixes need the build check too).
- **`composer audit` needs composer.phar**: Laragon ships php.exe but not a WSL-callable composer. If `composer` not on PATH, fetch once: `curl -sS https://getcomposer.org/installer | "$PHP"` then `"$PHP" composer.phar audit` in the repo. Never fabricate audit results when the tool is missing — report "dependency check skipped" instead.

## Support files

- `templates/TotpService.php` — dependency-free RFC 6238 TOTP implementation.
- `references/vuln-patterns.md` — code-level before/after examples for each vuln class found in real audits.

---

## Sub-Module: laravel-specialist

# Laravel Specialist

Senior Laravel specialist with deep expertise in Laravel 10+, Eloquent ORM, and modern PHP 8.2+ development.

## Core Workflow

1. **Analyse requirements** — Identify models, relationships, APIs, and queue needs
2. **Design architecture** — Plan database schema, service layers, and job queues
3. **Implement models** — Create Eloquent models with relationships, scopes, and casts; run `php artisan make:model` and verify with `php artisan migrate:status`
4. **Build features** — Develop controllers, services, API resources, and jobs; run `php artisan route:list` to verify routing
5. **Test thoroughly** — Write feature and unit tests; run `php artisan test` before considering any step complete (target >85% coverage)

## Reference Guide

Load detailed guidance based on context:

| Topic | Reference | Load When |
|-------|-----------|-----------|
| Eloquent ORM | `references/eloquent.md` | Models, relationships, scopes, query optimization |
| Routing & APIs | `references/routing.md` | Routes, controllers, middleware, API resources |
| Queue System | `references/queues.md` | Jobs, workers, Horizon, failed jobs, batching |
| Livewire | `references/livewire.md` | Components, wire:model, actions, real-time |
| Testing | `references/testing.md` | Feature tests, factories, mocking, Pest PHP |

## Constraints

### MUST DO
- Use PHP 8.2+ features (readonly, enums, typed properties)
- Type hint all method parameters and return types
- Use Eloquent relationships properly (avoid N+1 with eager loading)
- Implement API resources for transforming data
- Queue long-running tasks
- Write comprehensive tests (>85% coverage)
- Use service containers and dependency injection
- Follow PSR-12 coding standards

### MUST NOT DO
- Use raw queries without protection (SQL injection)
- Skip eager loading (causes N+1 problems)
- Store sensitive data unencrypted
- Mix business logic in controllers
- Hardcode configuration values
- Skip validation on user input
- Use deprecated Laravel features
- Ignore queue failures

## Code Templates

Use these as starting points for every implementation.

### Eloquent Model

```php
<?php

declare(strict_types=1);

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;
use Illuminate\Database\Eloquent\Relations\HasMany;
use Illuminate\Database\Eloquent\SoftDeletes;

final class Post extends Model
{
    use HasFactory, SoftDeletes;

    protected $fillable = ['title', 'body', 'status', 'user_id'];

    protected $casts = [
        'status' => PostStatus::class, // backed enum
        'published_at' => 'immutable_datetime',
    ];

    // Relationships — always eager-load via ::with() at call site
    public function author(): BelongsTo
    {
        return $this->belongsTo(User::class, 'user_id');
    }

    public function comments(): HasMany
    {
        return $this->hasMany(Comment::class);
    }

    // Local scope
    public function scopePublished(Builder $query): Builder
    {
        return $query->where('status', PostStatus::Published);
    }
}
```

### Migration

```php
<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('posts', function (Blueprint $table): void {
            $table->id();
            $table->foreignId('user_id')->constrained()->cascadeOnDelete();
            $table->string('title');
            $table->text('body');
            $table->string('status')->default('draft');
            $table->timestamp('published_at')->nullable();
            $table->softDeletes();
            $table->timestamps();
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('posts');
    }
};
```

### API Resource

```php
<?php

declare(strict_types=1);

namespace App\Http\Resources;

use Illuminate\Http\Request;
use Illuminate\Http\Resources\Json\JsonResource;

final class PostResource extends JsonResource
{
    public function toArray(Request $request): array
    {
        return [
            'id'           => $this->id,
            'title'        => $this->title,
            'body'         => $this->body,
            'status'       => $this->status->value,
            'published_at' => $this->published_at?->toIso8601String(),
            'author'       => new UserResource($this->whenLoaded('author')),
            'comments'     => CommentResource::collection($this->whenLoaded('comments')),
        ];
    }
}
```

### Queued Job

```php
<?php

declare(strict_types=1);

namespace App\Jobs;

use App\Models\Post;
use Illuminate\Bus\Queueable;
use Illuminate\Contracts\Queue\ShouldQueue;
use Illuminate\Foundation\Bus\Dispatchable;
use Illuminate\Queue\InteractsWithQueue;
use Illuminate\Queue\SerializesModels;

final class PublishPost implements ShouldQueue
{
    use Dispatchable, InteractsWithQueue, Queueable, SerializesModels;

    public int $tries = 3;
    public int $backoff = 60;

    public function __construct(
        private readonly Post $post,
    ) {}

    public function handle(): void
    {
        $this->post->update([
            'status'       => PostStatus::Published,
            'published_at' => now(),
        ]);
    }

    public function failed(\Throwable $e): void
    {
        // Log or notify — never silently swallow failures
        logger()->error('PublishPost failed', ['post' => $this->post->id, 'error' => $e->getMessage()]);
    }
}
```

### Feature Test (Pest)

```php
<?php

use App\Models\Post;
use App\Models\User;

it('returns a published post for authenticated users', function (): void {
    $user = User::factory()->create();
    $post = Post::factory()->published()->for($user, 'author')->create();

    $response = $this->actingAs($user)
        ->getJson("/api/posts/{$post->id}");

    $response->assertOk()
        ->assertJsonPath('data.status', 'published')
        ->assertJsonPath('data.author.id', $user->id);
});

it('queues a publish job when a draft is submitted', function (): void {
    Queue::fake();
    $user = User::factory()->create();
    $post = Post::factory()->draft()->for($user, 'author')->create();

    $this->actingAs($user)
        ->postJson("/api/posts/{$post->id}/publish")
        ->assertAccepted();

    Queue::assertPushed(PublishPost::class, fn ($job) => $job->post->is($post));
});
```

## Validation Checkpoints

Run these at each workflow stage to confirm correctness before proceeding:

| Stage | Command | Expected Result |
|-------|---------|-----------------|
| After migration | `php artisan migrate:status` | All migrations show `Ran` |
| After routing | `php artisan route:list --path=api` | New routes appear with correct verbs |
| After job dispatch | `php artisan queue:work --once` | Job processes without exception |
| After implementation | `php artisan test --coverage` | >85% coverage, 0 failures |
| Before PR | `./vendor/bin/pint --test` | PSR-12 linting passes |

## Knowledge Reference

Laravel 10+, Eloquent ORM, PHP 8.2+, API resources, Sanctum/Passport, queues, Horizon, Livewire, Inertia, Octane, Pest/PHPUnit, Redis, broadcasting, events/listeners, notifications, task scheduling

[Documentation](https://jeffallan.github.io/claude-skills/skills/backend/laravel-specialist/)

---

## Sub-Module: laravel-tailwind-ui

# Laravel + Tailwind 4 UI / Landing Pages

Building styled pages (landing, portfolio, CV, marketing) inside a Laravel 12 project using Tailwind CSS v4 via Vite. Covers design-system setup, the rebuild pitfall that bites everyone, and running the dev server from WSL with Laragon.

## Stack layout (Laravel 12 default)

- `vite.config.js` — `laravel-vite-plugin` + `@tailwindcss/vite`; fonts via `bunny('Font Name', { weights: [...] })` in the `fonts` array (self-hosted, offline-safe — no CDN dependency)
- `resources/css/app.css` — starts with `@import 'tailwindcss';`
- `resources/views/welcome.blade.php` — page markup; route `/` already returns it
- Verify: `npm run build` (project's canonical build)

## Tailwind 4 specifics (v3 knowledge does NOT apply)

- **Custom tokens live in `@theme {}` in app.css.** Define `--color-carbon-100: #161616;` → use `bg-carbon-100`, `text-carbon-60` etc. anywhere in blade. `--font-sans` / `--font-mono` overrides change the default `font-sans`/`font-mono` utilities.
- **Custom animation/utility classes use `@utility name { ... }`** (e.g. `@utility hero-fade { animation: hero-fade 0.6s ease-out both; }` with `@keyframes` beside it). Use with `motion-safe:` variant so `prefers-reduced-motion` kills it automatically.
- Global styles (focus ring, `::selection`, `touch-action: manipulation`, `-webkit-tap-highlight-color`, `text-wrap: balance` on h2, `tabular-nums` on mono data) go in `@layer base {}`.

## PITFALL: new blade classes need a rebuild (cost a real bug)

Tailwind scans source files at build time. A class used in blade but never present in any earlier build is **missing from the compiled CSS** until you run `npm run build` again. Symptom seen: `<img>` with `h-28 w-28 lg:h-44 lg:w-44` rendered at its natural 512px — `rounded-full` worked (already used elsewhere), size classes didn't (never seen before). Verify with `getComputedStyle`: if `renderedSize` == `naturalWidth`, the size classes are not in the CSS → rebuild.

Rule: **blade edits render live (no rebuild); any new CSS/JS or new utility class → `npm run build`.** After build, hard-refresh the browser (stale CSS cache looks identical to a broken build).

## Serving from WSL with Laragon (no PHP in WSL)

- WSL often has no PHP. Use Laragon's Windows PHP: `/mnt/c/laragon/bin/php/php-8.3.30-Win32-vs16-x64/php.exe` (find exact version: `ls /mnt/c/laragon/bin/php/`)
- WSL2 cannot reach Windows `127.0.0.1`. Serve with `--host=0.0.0.0`, then reach it from WSL via the gateway IP: `GW=$(ip route show default | awk '{print $3}')` → `http://$GW:8899/`. Windows browser uses `http://127.0.0.1:8899/` directly.
- Start server with `terminal(background=true)`; verify with `curl -s -o /dev/null -w "%{http_code}" http://$GW:PORT/`.

## Design workflow (anti-AI-slop)

1. Load `frontend-design` (process/taste) + `popular-web-designs` (real design systems). Pick a system that fits the subject's world — for enterprise/ERP subjects, IBM Carbon (`templates/ibm.md`) fits: monochrome grays + one blue accent, 0px radius, flat surfaces (no shadows), IBM Plex Sans 300 display + IBM Plex Mono for data, 0.16px tracking at 14px.
2. Ground the design in the subject: use real artifacts as the signature element. This session: project "ledger" table showing SAP sales-order numbers (`SO 2686004823`) in mono — real, specific, not placeholder.
3. Restraint: one signature + quiet everywhere else. Motion: hero fade + scroll reveal only, all `motion-safe:` guarded.
4. Content notes: numbers/codes get `translate="no"`; `<meta name="theme-color">`; headings `text-balance`.

## Motion patterns (accessible animation kit)

All motion: transform/opacity only, no-JS safe, and disabled under `prefers-reduced-motion`.

- **Scroll reveal**: gate the hidden state on `.js` (class added to `<html>` first thing in app.js) so no-JS users see content instantly. IntersectionObserver `{threshold:.12, rootMargin:'0px 0px -40px 0px'}`, add `.is-visible`, then `unobserve`. Stagger via inline `transition-delay` (`$i * 70ms` in blade loops).
- **Pop-in stagger (children of a reveal)**: `.js .reveal .pop-in { opacity:0; transform:translateY(10px); transition:opacity .35s ease, transform .35s ease; transition-delay:var(--d,0ms); }` + `.js .reveal.is-visible .pop-in { opacity:1; transform:none; }`. Per-element `style="--d: {{ $j * 35 + $i * 40 }}ms"` — index math in blade loops gives a wave (tags, list rows).
- **Count-up stats**: `<span data-count="3.5" data-decimals="1">0</span>`; IO `{threshold:.5}`, rAF ~1100ms, ease-out cubic `1 - Math.pow(1-p, 3)`, `unobserve` after; reduced-motion → set final value instantly. Put the final value in `aria-label` on the `<dd>` so SR users never read counting text.
- **Typewriter (hero eyebrow)**: ship full text in an `sr-only` span (SR + no-JS), visible `<span id="typewriter" aria-hidden="true">` typed by JS (45ms/char, ~450ms start delay); reduced-motion → set full text immediately. Cursor: `.type-cursor::after { content:'▍'; animation: cursor-blink 1.1s step-end infinite; }`.
- **Micro-interactions**: CTA arrow slide-in (`-translate-x-1 opacity-0 group-hover:translate-x-0 group-hover:opacity-100`), row hover `transition-colors duration-150`, ledger ↗ arrow `opacity-0 group-hover:opacity-100`.
- **Active section nav highlight**: IntersectionObserver on `main > section[id]`, rootMargin `'-20% 0px -60% 0px'` (triggers when section crosses upper-middle viewport). Toggle `.is-active` on matching nav links (`href === '#' + id`). Cover both desktop (`nav[aria-label="Primary"]`) and mobile (`nav[aria-label="Mobile"]`) selectors. CSS: `.link-underline.is-active { color: white; }` + `.link-underline.is-active::after { transform: scaleX(1); }` — reuses existing underline pseudo-element. No reduced-motion override needed (instant state change, no animation).
- **Gradient section dividers**: Replace `border-b border-carbon-20` with `.section-divider` class using `::after` pseudo-element: `linear-gradient(to right, transparent, var(--color-carbon-20) 20%, var(--color-carbon-20) 80%, transparent)`. Fades at edges, centered solid line. Dark sections: `.section-divider-dark` variant using `--color-carbon-80`. CSS: `.section-divider { border-bottom: none !important; position: relative; }` + `.section-divider::after { content:''; position:absolute; bottom:0; left:0; right:0; height:1px; background:... }`.
- **Smooth scroll**: `html { scroll-behavior: smooth }` in base, `scroll-behavior: auto` inside the reduced-motion media query.
- The reduced-motion media query must override EVERY pattern (`.reveal`, `.pop-in`, cursor; counters handle it in JS via `matchMedia`).

## Verification without a vision provider

If `browser_vision`/`vision_analyze` fail ("No LLM provider configured for task=vision"), verify via `browser_console` computed styles + DOM instead — fully conclusive:
- font: `document.fonts.check('16px "IBM Plex Sans"')`
- layout: `getComputedStyle` on hero/buttons (backgroundColor `rgb(15, 98, 254)`, borderRadius `0px`, height `48px`)
- overflow: scan `scrollWidth` vs `innerWidth` — a ~15px negative delta is the scrollbar, not overflow; walk `getBoundingClientRect` for real offenders
- interactions: dispatch `click`/`KeyboardEvent('keydown', {key:'Escape'})` and assert state changes
- JS errors: `browser_console` empty `js_errors`

## Accessibility checklist (from web-design-guidelines)

Skip link, `:focus-visible` ring, semantic HTML (dl/dt/dd for stats, article, nav), single h1 + ordered h2/h3, `scroll-mt-24` on anchor sections, `aria-expanded`+`aria-controls`+Escape-close+auto-close-on-tap for mobile menus, `width`/`height` attrs on img (anti-CLS), `fetchpriority="high"` on above-fold images, icon-only SVGs `aria-hidden="true"`, tabular-nums for data columns, no `transition: all`.

## Support files

- `references/ibm-carbon-tailwind4.md` — full Carbon-in-Tailwind-4 recipe from a working landing page: tokens, hero with dot-grid + identity card, ledger table, mobile menu, reveal animation, avatar resize
- `templates/carbon-tokens.css` — ready-to-paste Carbon @theme block + base layer + reveal CSS
- `scripts/resize_avatar.php` — PHP GD center-crop-to-square + resize for profile photos (works with Laragon php.exe)

---

## Sub-Module: laravel-wsl-laragon

# Laravel on WSL + Laragon (Windows PHP)

Workflow for developing Laravel apps whose PHP lives in Laragon (Windows) while the agent runs in WSL. Project files live under `/mnt/c/laragon/www/<project>`. For runtime code traps in this stack (SQLite vs MySQL raw SQL, `URL::forceRootUrl`, spatie permissions missing from existing DB, curl auth `_token`, broken `public/storage` junction to a Docker path, filesystems `'url'` pinning APP_URL, landing-page hardcoded counts vs DB, undefined `route()` names, double-income on duplicate verified payments) see `references/laravel-driver-and-auth-traps.md`. For GDB (Gaji Dana Bahagia) project specifics — schema, audit fixes, remaining TODO — see `references/gdb-project-reference.md`.

## Serve the app

WSL has no PHP; use Laragon's php.exe (check version dir):

```bash
/mnt/c/laragon/bin/php/php-<ver>-Win32-vs16-x64/php.exe artisan serve --host=0.0.0.0 --port=8899
```

Run via terminal(background=true) — it is a long-lived server process.

## Reaching the server

WSL2 is NAT'd: Windows `127.0.0.1` is NOT reachable from WSL, and vice-versa.

- From WSL/browser (Hermes browser runs in WSL): use the Windows gateway IP:
  `GW=$(ip route show default | awk '{print $3}')` → `http://$GW:8899/`
- From Windows browser (user's side): `http://127.0.0.1:8899/` works.
- Bind `--host=0.0.0.0` or the gateway IP will refuse connection.
- Windows Firewall may block the first connection — retry once; Laragon setups usually already allow php.exe.
- Spawning php.exe from WSL via terminal(background=true) works, but the server binds in Windows: WSL curl and the Hermes browser (runs in WSL) both fail against `http://localhost:8000` (curl `000`, browser `ERR_CONNECTION_REFUSED`) even while the process log shows "Server running". Do NOT loop retrying — if the user declines gateway-IP access, stop network verification and ask them to open `http://127.0.0.1:<port>` in the Windows browser; `npm run build` still verifies code correctness in the meantime.

## Tailwind 4 + Vite pitfalls

- **NEW Tailwind classes added to a blade require `npm run build`** — Tailwind scans source files at build time and only emits classes it has seen. A class first used in an edit (e.g. `h-44 w-44 object-cover`) will silently not exist in the old CSS build; the element renders at its natural/HTML-attribute size. Symptom: `getComputedStyle` shows default values while sibling utilities (already-built classes) apply fine.
- **Vite 8 / rolldown: `npm run build` from WSL node fails with `MODULE_NOT_FOUND` loading `rolldown/dist/shared/binding-*.mjs`** — rolldown ships a win32 native binding in the `node_modules` that Windows npm installed; WSL node cannot load it. Run the build from the Windows host instead: `cmd.exe /c "npm run build"` (works from the WSL cwd). Same applies to any package carrying Windows-only native bindings (esbuild pre-Vite-8, sharp, etc.). Don't conclude the project is broken — a Windows-built `node_modules` just won't run under WSL node.
- **Tailwind 4 + lightningcss: `npm run build` from WSL fails with `Cannot find module '../lightningcss.linux-x64-gnu.node'`** — same native-binding problem as rolldown above. `node_modules` was `npm install`-ed on Windows so only `lightningcss.win32-x64-msvc.node` exists. `npm rebuild lightningcss` does NOT fix it (it rebuilds the same platform binary). Fix: `npm install lightningcss-linux-x64-gnu --no-save`. For Next.js projects this is sufficient; Tailwind/PostCSS picks up the Linux binary. Same pattern applies to any `@<pkg>/<platform>` optional native dep — install the Linux variant alongside the Windows one.
- **Blade-only edits (text, structure, classes already in the build) render per-request — NO rebuild needed.** The artisan server recompiles views automatically.
- After any build, `npm run build` is also the project's verify command; grep output for `✓ built`.
- When scaffolding a new Laravel backend inside Docker with pre-existing project files, see `references/laravel-docker-scaffold-trap.md` for the composer create-project pitfall and multi-stage fix.

## Verifying UI without a vision provider

If `browser_vision`/`vision_analyze` fail ("No LLM provider configured for task=vision"), verify via browser_console computed styles — this is fully conclusive for layout/typography/color checks:

```js
(() => {
  const img = document.querySelector('img[alt="..."]');
  const s = getComputedStyle(img);
  const r = img.getBoundingClientRect();
  return { rendered: r.width + 'x' + r.height, radius: s.borderRadius,
           objectFit: s.objectFit, loaded: img.complete && img.naturalWidth > 0,
           overflow: document.body.scrollWidth - window.innerWidth };
})()
```

Notes: check `document.fonts.check('16px "IBM Plex Sans"')` for font load; `document.body.scrollWidth` is ~15px less than `innerWidth` when a scrollbar exists — do NOT flag that as horizontal overflow; instead scan for elements with `getBoundingClientRect().right > innerWidth`. `document.querySelector` can match nav links before hero CTAs — target by stable class (`.bg-blue-60`) not ambiguous href.

## PHP GD image processing (avatar/profile crops)

Laragon php.exe ships GD (`php.exe -m | grep -i gd`). Reusable center-crop + resize script: `scripts/resize_square.php` (see below). Pitfalls:

- **`imagejpeg` fails if the destination directory does not exist** — `mkdir -p public/images` first; PHP does not auto-create dirs.
- Windows paths in PHP: use `C:\\...` backslashes; run from project root with `php.exe` so `__DIR__` resolves to the Windows path.
- WhatsApp photos are ~1600px; crop to square + scale to 512 before shipping (58KB vs 220KB).
- Clean up the temp resize script after use.

## Next.js frontend + Laragon backend (WSL)

Pattern: Laravel API on Windows (Laragon php.exe) + Next.js dev server on WSL. Browser runs in Windows.

**Backend — MUST use `cmd.exe /c` to make server reachable from Windows browser:**
```bash
cmd.exe /c "cd C:\\laragon\\www\\<project> && C:\\laragon\\bin\\php\\php-<ver>\\php.exe artisan serve --host=0.0.0.0 --port=8000"
```
Spawning `php.exe` directly from WSL terminal makes the server unreachable from Windows browser (connection refused even though netstat shows LISTENING). `cmd.exe /c` runs it as a proper Windows process.

**Frontend — must bind `0.0.0.0` or Windows browser cannot reach WSL dev server:**
```bash
npx next dev -H 0.0.0.0 -p 3000
```

**API URL in Next.js (`NEXT_PUBLIC_API_URL`):**
- This var is baked into the client bundle at compile time — browser runs on Windows, API runs on Windows.
- From Windows browser, `localhost:8000` should work IF php.exe was started via `cmd.exe /c` (proper Windows process).
- From WSL curl/browser, `localhost` = WSL loopback, NOT Windows — use gateway IP `172.26.176.1` instead.
- `.env.local` example: `NEXT_PUBLIC_API_URL=http://172.26.176.1:8000/api` (safe for both Windows browser and WSL).
- Code fallback: `process.env.NEXT_PUBLIC_API_URL || \`http://\${hostname}:8000/api\`` — the `hostname` fallback works when user opens `http://172.26.176.1:3000` directly.
- After changing `.env.local`, restart the Next.js dev server — `NEXT_PUBLIC_*` vars are injected at compile time.

**lightningcss Linux binary (Next.js build from WSL with Windows node_modules):**
If `node_modules` was `npm install`-ed on Windows, `npm run build` from WSL fails: `Cannot find module '../lightningcss.linux-x64-gnu.node'`. Fix: `npm install lightningcss-linux-x64-gnu --no-save`. Already documented above but confirmed again for Next.js projects specifically.

**MySQL startup from WSL:**
```bash
/mnt/c/laragon/bin/mysql/mysql-<ver>/bin/mysqld.exe --defaults-file="C:\\laragon\\bin\\mysql\\mysql-<ver>\\my.ini"
```
Run via terminal(background=true). Takes ~3-4 seconds to accept connections.

## Cloudflare Tunnel (cloudflared) — expose local dev to internet for free

Quick Tunnel (`trycloudflare.com`) gives a random HTTPS URL — no signup, no account. Each restart gets a new URL.

### Install

```bash
curl -fsSL https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 -o ~/.local/bin/cloudflared && chmod +x ~/.local/bin/cloudflared
```

### Single-tunnel pattern (recommended for Next.js + Laravel)

Instead of 2 tunnels (frontend + backend), use **1 tunnel + Next.js rewrite proxy**:

1. Laravel API runs on Windows (Laragon `php.exe` via `cmd.exe /c`)
2. Next.js runs on WSL (`npx next dev -H 0.0.0.0 -p 3000`)
3. `next.config.ts` rewrites `/api/:path*` → Laravel backend
4. Frontend code auto-detects tunnel hostname and uses `${window.location.origin}/api`
5. One `cloudflared tunnel --url http://localhost:3000` exposes everything

**next.config.ts rewrite:**
```ts
const nextConfig = {
  async rewrites() {
    return [{ source: '/api/:path*', destination: 'http://172.26.176.1:8000/api/:path*' }]
  },
  allowedDevOrigins: ['trycloudflare.com'],
};
```

**Frontend API URL auto-detect (in page.tsx useEffect):**
```ts
const hostname = window.location.hostname;
const isTunnel = hostname.includes('trycloudflare.com');
const baseUrl = isTunnel
  ? `${window.location.origin}/api`     // proxied through Next.js rewrite
  : `http://${hostname}:8000/api`;       // direct to Laravel
setApiUrl(baseUrl);
```

### Why NOT `NEXT_PUBLIC_API_URL` env var for tunnels

`NEXT_PUBLIC_*` vars are baked into the client bundle at **compile time**. Quick tunnel URLs change every session, creating a chicken-and-egg problem: you need the tunnel URL to set the env var, but you need to restart Next.js after changing the env var. Runtime hostname detection avoids this entirely.

### `allowedDevOrigins` pitfall

Next.js dev blocks cross-origin requests to HMR/font resources. When accessing via `*.trycloudflare.com`, you get "Blocked cross-origin request" errors. Fix: add `allowedDevOrigins: ['trycloudflare.com']` in `next.config.ts`. Must be the bare domain — subdomains are matched automatically.

### Startup script pattern

Reusable launcher at `scripts/gdb-tunnel.sh` — starts MySQL + Laravel + Next.js + cloudflared, prints public URL.

Key trick — wait for URL in cloudflared output:
```bash
cloudflared tunnel --url http://localhost:3000 > "$LOG" 2>&1 &
for i in $(seq 1 30); do
  URL=$(grep -oP 'https://[a-z0-9-]+\.trycloudflare\.com' "$LOG" 2>/dev/null | head -1)
  [ -n "$URL" ] && break
  sleep 2
done
```

### Limitations

- Quick tunnel URLs are temporary — change every restart. For persistent URLs, create a Cloudflare account + named tunnel (also free).
- Computer must stay on + internet active while tunnel runs.
- `cloudflared` tunnel log in background mode may not surface the URL immediately — use the grep-wait pattern above.

## Landing page conventions for this user

- User works in `/mnt/c/laragon/www/Landing-Page` (Laravel 12, Tailwind 4 via Vite, `resources/css/app.css` with `@theme` tokens, `resources/views/welcome.blade.php` as the page).
- User explicitly wants non-AI-slop design — follow the frontend-design skill process (token system, signature element, avoid cream+terracotta / black+acid-green / broadsheet defaults).
- Always state absolute file paths of what you created/changed; user asked "where did you put the code" when this was unclear.
- Serve + verify flow: edit → `npm run build` if new classes → reload browser → browser_console checks.

## Scroll-reveal pattern (restrained, accessible)

Reusable entrance animation that never hides content without JS:

```css
.js .reveal { opacity: 0; transform: translateY(16px); transition: opacity .7s ease, transform .7s ease; }
.js .reveal.is-visible { opacity: 1; transform: none; }
@media (prefers-reduced-motion: reduce) { .js .reveal { opacity: 1; transform: none; transition: none; } }
```

```js
document.documentElement.classList.add('js');
const els = document.querySelectorAll('.reveal');
if (!('IntersectionObserver' in window) || !els.length) els.forEach(e => e.classList.add('is-visible'));
else { const o = new IntersectionObserver(es => { for (const e of es) if (e.isIntersecting) { e.target.classList.add('is-visible'); o.unobserve(e.target); } }, { threshold: 0.12, rootMargin: '0px 0px -40px 0px' }); els.forEach(e => o.observe(e)); }
```

Stagger siblings with inline `style="transition-delay:..."`; `motion-safe:` variants for load animations; animate transform/opacity only.

## Micro-animation toolkit (CSS-only, same `.is-visible` hook, no extra JS)

SVG line draw without path-length math — set `pathLength="1"` on the `<path>`:
```css
.sparkline-path { stroke-dasharray: 1; stroke-dashoffset: 1; transition: stroke-dashoffset 1.3s cubic-bezier(.4,0,.2,1) .15s; }
.js .reveal.is-visible .sparkline-path { stroke-dashoffset: 0; }
```

Bars grow / dots pop — hidden scale + `transform-origin`, stagger via inline `transition-delay`:
```css
.js .reveal .sparkbar-bar { transform: scaleY(0); transform-origin: bottom center; }
.js .reveal .sparkbar-dot { transform: scale(0); }
.js .reveal.is-visible .sparkbar-bar, .js .reveal.is-visible .sparkbar-dot { transform: scale(1); }
```

Vertical timeline line draws downward: `transform: scaleY(0); transform-origin: top center;` → `scaleY(1)` on `.is-visible` (node = absolutely-positioned dot with a `color-mix` glow ring).

Cursor spotlight (desktop fine pointers only): an absolutely-positioned div with `background: radial-gradient(420px circle at var(--mx,50%) var(--my,10%), rgba(15,98,254,.08), transparent 70%)`; JS writes `--mx/--my` in a rAF-throttled `pointermove` on the section; gate JS with `matchMedia('(hover:hover) and (pointer:fine)')` and CSS with `@media (hover:none),(pointer:coarse){ display:none }`. Keep it `opacity:0` → `.is-active` on first move so it never flashes.

Filter tabs (Carbon-style): `aria-pressed` + CSS `[aria-pressed="true"]` for the active pill; rows carry `data-tags="implode(' ', $tags)"`; JS toggles `.is-filtered-out`. PITFALL: rows also carry inline `transition-delay` for entrance stagger — that delay applies to fade-out too, making hiding sluggish (last row waits N×45ms). Override with `.js .reveal.project-row.is-filtered-out { transition-delay: 0ms !important; }`; fade-in keeps the original cascade.

Every new animation needs matching rules in the existing `prefers-reduced-motion: reduce` block: snap states (`transform:none`, `stroke-dashoffset:0`), drop transitions, `display:none` for filtered rows and the spotlight.

---

## Sub-Module: php-development

# PHP Development

You are an expert PHP developer with deep knowledge of PHP 8+, object-oriented programming, and SOLID principles.

## Core Principles

- Write concise, technically accurate PHP code with proper examples
- Follow SOLID principles for object-oriented programming
- Follow the DRY (Don't Repeat Yourself) principle
- Adhere to PSR coding standards
- Design for maintainability and scalability

## PHP Standards

- Use PHP 8.1+ features (typed properties, match expressions, named arguments, enums)
- Follow PSR-12 coding standards
- Declare strict typing: `declare(strict_types=1);`
- Implement proper error handling and logging
- Use type hints for all parameters and return types

## Best Practices

### Code Organization
- Use PSR-4 autoloading with Composer
- Implement Repository pattern for data access logic
- Use dependency injection for loose coupling
- Leverage interfaces for abstraction
- Implement proper caching strategies

### Naming Conventions
- Use PascalCase for class names
- Use camelCase for method and variable names
- Use SCREAMING_SNAKE_CASE for constants
- Use meaningful, descriptive names

### Type Declarations
- Always declare parameter types
- Always declare return types
- Use union types when appropriate
- Use nullable types with `?` prefix when needed

### Documentation
- Write complete PHPDoc blocks for classes, methods, and properties
- Document parameter types and descriptions
- Include `@return` tags with type information
- Document exceptions with `@throws`

### Error Handling
- Use try-catch blocks for expected exceptions
- Create custom exception classes for domain-specific errors
- Log errors appropriately with context information
- Never expose sensitive information in error messages

### Security Practices
- Sanitize all user input
- Use prepared statements for database queries
- Implement CSRF protection for forms
- Validate and escape output appropriately

### Testing
- Write unit tests for all business logic
- Use PHPUnit for testing framework
- Follow Arrange-Act-Assert pattern
- Mock external dependencies in unit tests

---

## Sub-Module: php-full-stack-developer

# PHP Full-Stack Developer Skills (Senior)

## Trigger Conditions
Use this skill when:
- The user requests engineering work: backend/frontend/DB/devops/CI, debugging, refactors, migrations, API work.
- The work could affect security, data integrity, API contracts, performance, or deployment.
- You need repeatable execution across sessions (memory + logs).
- There is uncertainty, contradictions, or multiple valid approaches.

Do not apply to unprompted agent-initiated work; log later if needed.

## Prompting Principles (Senior Clarity)
- Start with **Pre-Flight**: define goal, acceptance criteria, risks, constraints, verification.
- Ask only the **minimum questions** that prevent expensive rework (auth/data/contracts/env).
- Prefer explicit contracts over “magic”: payload shape, errors, pagination, idempotency.
- Prefer reversible changes and staged rollout for risky work.
- Always produce “How to test” steps.

## Two governance questions (required)
1) Should I make and log this into a project to store it in memory?
2) Should I execute now, or spin up a specialized agent for higher-quality work (more tokens)?

## Stop-Work Rules (quick gates)
Stop and log a conflict if:
- Auth/authz rules are unclear for protected resources.
- DB change is destructive or constraints are unknown.
- API/UI contract change has unknown consumers.
- Runtime versions (PHP/framework/DB) are unknown for P1+ work.
- Rollback/rollout is missing for P1+ work.

Routing: see `INFO_GOVERNANCE.md` + `LOG_CONFLICTS.md`.

---

## Sub-Module: inertia-payload-budget

# Anggaran payload halaman Inertia

Untuk halaman Laravel + Inertia (React/Vue) yang mengirim banyak prop dalam satu request — katalog,
daftar master data, halaman dengan dropdown filter besar. Tujuannya menurunkan berat halaman **tanpa
menghapus fiturnya**, dan memverifikasinya tanpa browser.

## Urutan kerja

1. **Ukur per-prop, jangan menebak.** Ambil HTML yang benar-benar dikirim (dengan sesi login), parse
   atribut `data-page`, urutkan prop dari yang terberat. Skripnya di
   `references/typeahead-and-measurement.md`. Skrip bootstrap yang memanggil controller langsung **tidak**
   menghitung prop shared — angkanya akan menyesatkan.
2. **Yang terberat hampir selalu daftar opsi filter**: `SELECT DISTINCT` atas kolom bernilai unik banyak
   yang dikirim sebagai prop bersama, padahal `<select>` berisi ribuan opsi tidak terpakai siapa pun.
3. **Pindahkan daftar itu ke endpoint saran berbatas** (`field` whitelist, `q`, `limit` di-cap 25–50),
   lalu ganti `<select>` menjadi `<input list>` + `<datalist>` yang mengambil saran saat mengetik
   (debounce ±300 ms). Resep lengkapnya di `references/typeahead-and-measurement.md`.
4. **Penyaringan tetap di server.** Daftar barisnya sudah ter-paginasi, jadi memfilter di client hanya
   menyaring satu halaman dan menyesatkan. Setelah mengganti nama query param, uji tiap kombinasi dengan
   curl (nilai awalan, nilai mengandung, nilai kosong) dan cek jumlah barisnya — bukan cuma HTTP 200.
5. **Ukur ulang setelah setiap perubahan** dan laporkan angka sebelum/sesudah. "Halaman jadi ringan" bukan
   laporan; "826 KB → 612 KB, prop `options` 148 KB → 2 KB" adalah laporan.
6. **Perbarui dokumentasi proyek pada langkah yang sama** kalau repo punya panduan pengembangan wajib —
   perubahan payload/filter yang tidak tercatat akan dianggap belum selesai.

## Aturan yang menentukan

- **Nilai filter yang panjang/bertingkat butuh “mengandung”, bukan awalan.** Path hierarki
  (`Main Engine > Akasaka 7UEC37LA > Engine Frame`) tidak pernah cocok dengan `LIKE 'Engine%'`; user
  melihat “0 hasil” untuk kata yang jelas ada di datanya dan membacanya sebagai fitur rusak. Sediakan DUA
  parameter: `*_like` (awalan, untuk nilai satu token supaya angka node/hierarki tetap akurat) dan `*_q`
  (mengandung, untuk kotak ketik bebas).
- **Escape wildcard sebelum masuk `LIKE`** (`addcslashes($v, '%_\\')`). `%` yang lolos jadi wildcard dan
  diam-diam mengembalikan seluruh tabel.
- **Samakan filter baru di SEMUA jalur** yang membaca kumpulan data yang sama: tabel, ekspor CSV,
  statistik, endpoint saran. Kalau tidak, jumlah baris ekspor tidak cocok dengan yang terlihat.
- **Endpoint saran tetap tunduk pada scope filter/visibilitas** — jangan bocorkan nilai dari baris yang
  tidak boleh dilihat user, dan jangan menyusun nama kolom dari input (whitelist array, sisanya 422).
- **Menambah atribut yang bisa dicari itu tiga perubahan**: server melengkapi data, predikat filter
  komponen pencarian menyertakannya, dan form mengisi/menampilkannya. Sangat mudah hanya mengerjakan yang
  	pertama lalu menganggap fiturnya selesai.
- **Cache key daftar master data ber-versi wajib punya satu sumber kebenaran.** Kode membaca key `..._v3`
  sementara invalidasi menyentuh `..._v2` → UI menyajikan data basi setelah perubahan bentuk data, dan itu
  tampak seperti perubahan yang tidak bekerja.

## Artefak hasil jalan tidak boleh mendarat di folder produksi saat test

Penulis log/ekspor (mis. log Excel per push, hasil ekspor, file generate) tetap menulis file di setiap test
yang menjalankan perintah terkait — jalur offline pun mengeluarkan log. Folder hasil produksi jadi bercampur
sampah test dan user menemukannya sebagai “file hantu” yang sulit dibedakan dari hasil asli. Percabangkan di
SATU tempat penulisnya:

```php
$dir = app()->runningUnitTests()
    ? storage_path('app/push-logs/tests')
    : storage_path('app/push-logs');
```

Buktikan dengan menghitung jumlah file folder produksi **sebelum vs sesudah** `php artisan test` — harus
sama, sementara subfolder `tests/` bertambah.

## Verifikasi tanpa browser

- `npm run build` sukses bukan bukti halaman jalan: komponen JSX yang dipakai tapi belum di-import hanya
  meledak saat halaman dibuka (`ReferenceError` → halaman blank). Jalankan pemeriksa impor lebih dulu.
- Bukti sah untuk halaman = request HTTP sungguhan dengan sesi login, lalu cek status, ukuran byte, dan
  ketiadaan penanda error. Simpan HTML-nya ke file; `curl -o /dev/null -w '%{size_download}'` bisa
  melaporkan `0` di git-bash Windows walau responsnya penuh (`stat -c%s` pada file hasil).
- Uji juga jalur negatif: `field` di luar whitelist harus 422, bukan diterima sebagai nama kolom.

Skrip pengukuran per-prop, resep endpoint saran + komponen typeahead, dan cara mengukur ulang ada di
`references/typeahead-and-measurement.md`.

---