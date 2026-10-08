# Laravel Application Analysis Checklist

Use this reference after the general repository inventory identifies a Laravel application.

## High-value files

1. `composer.json` — PHP/Laravel versions and domain packages
2. `package.json` and `vite.config.*` — frontend stack
3. `routes/web.php`, `routes/api.php`, route modules — actual application surface
4. `app/Http/Controllers/` — orchestration and validation
5. `app/Services/`, actions, jobs — domain logic and background work
6. `app/Models/` — casts, fillable fields, relationships, soft deletes
7. `app/Events/` and `app/Listeners/` — hidden side effects
8. `database/migrations/` — schema truth, constraints, indexes
9. `database/seeders/` — roles, permissions, defaults, demo credentials
10. `resources/views/` or SPA entry points — user-facing capabilities
11. `tests/` — intended behavior and uncovered risks
12. `Dockerfile`, Compose, Nginx/Apache configuration — runtime topology

## Useful verification

Run with the executable that belongs to the project environment:

```bash
php artisan route:list --json
php artisan about
php artisan test --compact
```

On WSL with a Laragon-hosted project, a representative pattern is:

```bash
cmd.exe /c "cd /d C:\\path\\to\\project && C:\\path\\to\\php.exe artisan route:list --json"
```

Do not hardcode a Laragon PHP version; discover the installed executable first.

## Evidence traps

### Route cache and generated views

`bootstrap/cache/routes-*.php` and `storage/framework/views/*.php` are generated output. Inspect source routes and Blade templates instead.

### Models do not prove active features

A model or migration can be unused scaffolding. Confirm an active route/controller/service path before describing it as implemented.

### Seed data is not production state

Seeders describe intended defaults and expose security risks, but they do not prove the current database still contains those records.

### Dynamic pricing

The presence of a pricing table does not mean checkout uses it. Trace the actual price calculation from controller/service to the selected column or query.

### Service-layer drift

If a domain service exists but the controller duplicates its calculations, identify the invoked path and flag inconsistent behavior risk. Do not assume the service is authoritative merely because it is better organized.

### ORM column comparisons

In Laravel query builder:

```php
where('start_time', '>', 'end_time')
```

usually compares against the literal string `end_time`. A column comparison requires:

```php
whereColumn('start_time', '>', 'end_time')
```

Treat this as a suspected defect until confirmed by tests or database behavior.

### Polymorphic payments and side effects

When a `Payment` morphs to multiple payable entities, inspect event listeners for status updates and ledger entries. Check idempotency by looking for unique constraints or explicit “already exists” guards.

### Test progress is not completion

Dots from PHPUnit/Pest only show tests have progressed. Require a process exit and final test summary before saying the suite passed. If the run stalls, report it as incomplete and isolate the hanging test in a dedicated debugging task.
