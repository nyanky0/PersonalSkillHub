---
name: vercel-static-deploy
description: Deploy static sites to Vercel via CLI/API.
version: 1.0.0
author: Hermes Agent
license: MIT
tags: [vercel, deploy, static, hosting, laravel, php]
platforms: [linux, macos, windows, wsl]
triggers:
  - deploy to vercel
  - upload to vercel
  - vercel deploy
  - laravel/php site to vercel
  - vercel custom domain
  - vercel rename project
---

# Vercel Static Deploy

Deploy a static build folder to Vercel from the CLI. Covers: first deploy, project linking,
rename via API, project domains, and exporting a PHP/Laravel page to static HTML.

## Core workflow

1. **Prepare static folder** (for PHP/Laravel see `references/laravel-static-export.md`).
   All asset paths must be root-relative (`/build/...`), never absolute host URLs.
2. **Login**: `npx -y vercel@latest login` — prints a device URL (e.g. `https://vercel.com/oauth/device?user_code=XXXX-XXXX`); user opens it in a browser and approves. CLI waits.
3. **Link the folder to the right project BEFORE deploying** — run in the deploy dir:
   `npx -y vercel@latest link --yes --project <name>` → writes `.vercel/project.json` automatically, no API token needed. Fallback if linking misbehaves: write `<deploy-dir>/.vercel/project.json` by hand:
   ```json
   {"projectId":"prj_...","orgId":"<user-id>"}
   ```
   `orgId` for a personal account = the user id from `GET https://api.vercel.com/v2/user` (response is wrapped: `d.user.id`, not top-level). Project id can be read from any deploy inspect URL or `npx vercel projects ls`.
4. **Deploy**: `npx -y vercel@latest deploy <dir> --prod --yes` → prints production URL. Verify every asset with curl (`index`, css, js, images, favicon → 200).

## Pitfalls

- **Deploy without `.vercel/project.json`** → CLI creates a NEW project named after the folder. If you renamed the project via API afterwards, subsequent deploys land in the OLD project name (silently — `vercel ls <project>` shows the wrong deployment list). Always write project.json first.
- **`rm -rf dist` deletes the hidden `.vercel/` link** — re-link before every deploy: run `npx -y vercel@latest link --yes --project <name>` inside the deploy dir (writes `.vercel/project.json`; also refreshes expired CLI tokens). Check first: `cat dist/.vercel/project.json`.
- **Path double when deploying from inside the dir**: `cd dist && npx vercel deploy dist --prod` fails with `Could not find ".../dist/dist"`. After `cd` into the deploy dir, deploy with `.`: `npx vercel@latest deploy . --prod --yes`. To keep the link across `rm -rf dist`, back up first: `cp -r dist/.vercel /tmp/vercel-backup` → re-render → `cp -r /tmp/vercel-backup dist/.vercel`.
- **CLI has no rename command** — use API: `PATCH https://api.vercel.com/v9/projects/{oldName}` body `{"name":"new-name"}`. Verify: `npx vercel projects ls`.
- **Each deployment gets a random 3-word URL** (dist-nine-rust-90.vercel.app). The stable URL is the project domain `<project>.vercel.app` — set it explicitly:
  `POST https://api.vercel.com/v9/projects/{id}/domains` body `{"name":"<project>.vercel.app"}` (auto-verified). Without this, a project renamed via API serves the OLD deployment under its random URL and the new domain 404s.
- **OG/meta URLs must point at the stable project domain**, never a random deployment URL — they'd rot on every deploy.
- **Auth file location**: `~/.local/share/com.vercel.cli/auth.json` (NOT `~/.vercel/auth.json`). Extract token with `node -e "console.log(JSON.parse(require('fs').readFileSync('<path>')).token)"`. Never print the token.
- **Stored OAuth token EXPIRES** — auth.json holds `token`/`refreshToken`/`expiresAt`; raw `curl` API calls with the stored token fail once expired. The CLI auto-refreshes on every run. Before raw-API work (rename, domains, delete): run any CLI command first (`npx -y vercel@latest whoami` or `link`) to refresh the stored token, THEN re-extract it. Or skip raw API entirely — `vercel link --yes --project <name>` does linking without a token. Note: `npx vercel whoami` may print only npm notices (empty output) on the first run while refreshing — check exit code or run it twice.
- **Cleanup**: delete stray duplicated projects via `DELETE https://api.vercel.com/v9/projects/{name}` (204 = ok).
- Node version drift: `npx -y vercel@latest` avoids stale global installs.

## API quick reference

| Action | Endpoint |
|---|---|
| User id (orgId) | `GET /v2/user` → `d.user.id` |
| Rename project | `PATCH /v9/projects/{name}` `{"name":"..."}` |
| Add project domain | `POST /v9/projects/{id}/domains` `{"name":"x.vercel.app"}` |
| Delete project | `DELETE /v9/projects/{name}` |

All with header `Authorization: Bearer <token>`.

## PHP/Laravel static export

Vercel has no native PHP runtime. For a Laravel app that is effectively one static page:
render the blade view to `index.html`, copy `public/build` + `public/images` + favicons into the
deploy dir, rewrite absolute asset URLs to root-relative, then deploy. Full recipe in
`references/laravel-static-export.md`.

## Verification checklist

- [ ] `curl -o /dev/null -w "%{http_code}" <url>/` → 200
- [ ] CSS/JS/font/image/favicon assets → 200
- [ ] `<meta property="og:url">` points at stable domain
- [ ] `npx vercel ls <project>` shows the intended deployment
