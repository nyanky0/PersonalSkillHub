---
name: instabox
description: "Manage InstaBox cloud sandboxes (Firecracker microVMs), deploy web applications, configure public HTTPS port ingress, handle 30m idle auto-suspend/resume lifecycles, and execute remote server maintenance via CLI, SDK, and HTTP API."
version: 1.1.0
author: hermes-cindy-merged
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [instabox, sandbox, cloud, deploy, vps, tunnel, port-forward, devops, vm, microvm, firecracker]
    category: devops
    requires_toolsets: [terminal]
---

# InstaBox Sandbox Engineering & Maintenance Skill 📦⚡

InstaBox (`instabox.sh`) provides isolated cloud Linux machines running as Firecracker microVMs (Debian 13 trixie amd64, 4 vCPUs, 8 GiB RAM, 16 GiB root, and 20 GiB persistent storage at `/data`).

This skill governs the end-to-end lifecycle of deploying web applications, configuring external network ingress, and maintaining services inside InstaBox sandboxes.

---

## 1. Core Architecture & Mental Model

- **MicroVM Hardware Profile**: 4 vCPUs / 8 GiB RAM default per machine.
- **Storage Topology**:
  - `/` (Root Disk, 16 GiB): Template-managed OS root. Changes outside `/data` do not survive template reprovisioning.
  - `/data` (Persistent Disk, 20 GiB): Persistent storage surviving stops/reboots. User home is `/data/home`, and work projects can be hosted under `/data/workspace` or `/data/home`. **Store all application code, git repos, databases, and uploaded assets under `/data/`**.
- **Lifecycle & Idle Suspend States**:
  - `running` -> `suspended` (auto-suspend after 30 minutes of idle).
  - When suspended, **RAM state is frozen to disk**. Active background processes remain intact.
  - **Auto-Wake**: Incoming HTTP traffic to published public ports, SSH connections, or `instabox wake <machine>` automatically resumes the VM without losing memory state.
  - `stopped`: Full power-off state. RAM is cleared; on reboot, processes must be re-started (best automated via `systemd` enabled services or process managers).
  - `restart`: Power-cycles a hung machine while preserving all persistent `/data` disks.

---

## 2. CLI, Auth & Environment Setup

Authentication uses the `INSTABOX_API_KEY` (`ibk_...`) or interactive device login:

```bash
# 1. Install CLI
curl -fsSL https://api.instabox.sh/install.sh | sh
# Or via Node: npx instabox@latest sh

# 2. Authentication
export INSTABOX_API_KEY="ibk_..."
# Or interactive login:
instabox login

# 3. Verify identity and quotas
instabox whoami
instabox usage
instabox ls --json
```

---

## 3. Provisioning & Machine Creation

```bash
# Create standard developer sandbox (agent-browser / universal template)
instabox create --name web-sandbox --template universal --meta env=production

# Inspect status and IP endpoints
instabox get web-sandbox --json
```

---

## 4. Web App Deployment Protocol

### A. Code Ingestion
Push code directly to `/data/workspace/<app>` or `/data/home/<app>`:

```bash
# Method 1: Push local directory (respects .gitignore by default)
instabox push web-sandbox ./my-web-app /data/workspace/my-web-app --all

# Method 2: Copy archive file
instabox cp ./app.tar.gz web-sandbox:/data/workspace/app.tar.gz
instabox exec web-sandbox -- 'tar -xzf /data/workspace/app.tar.gz -C /data/workspace/my-web-app'

# Method 3: Git clone inside machine (Recommended for updates)
instabox exec web-sandbox -- 'cd /data/workspace && git clone <repo_url> my-web-app'
```

### B. Dependency & Build Phase
```bash
# Node.js / Bun
instabox exec web-sandbox -- 'cd /data/workspace/my-web-app && npm ci && npm run build'

# PHP / Composer
instabox exec web-sandbox -- 'cd /data/workspace/my-web-app && composer install --no-dev --optimize-autoloader'

# Python venv
instabox exec web-sandbox -- 'cd /data/workspace/my-web-app && python3 -m venv .venv && .venv/bin/pip install -r requirements.txt'
```

### C. Daemonization & Process Survival (CRITICAL)

> [!WARNING]
> `instabox exec` terminates when the remote command finishes. If a background process attempts to write stdout/stderr to an exited exec session, it crashes with a `Broken Pipe`. Never run raw foreground servers inside `exec`. **Always bind `0.0.0.0` (not `127.0.0.1`) for public accessibility.**

#### Option 1: Native Systemd Service (Best for Debian 13 VM & Auto-Boot)
Because the Firecracker VM runs `systemd` as PID 1, systemd unit files survive power reboots and auto-start on boot:

```ini
# /etc/systemd/system/webapp.service
[Unit]
Description=My Web Application
After=network.target

[Service]
Type=simple
User=user
WorkingDirectory=/data/workspace/my-web-app
ExecStart=/usr/bin/node /data/workspace/my-web-app/server.js
Restart=always
RestartSec=5
StandardOutput=append:/data/workspace/my-web-app/storage/logs/server.log
StandardError=append:/data/workspace/my-web-app/storage/logs/server.log

[Install]
WantedBy=multi-user.target
```
Enable & start:
```bash
instabox exec web-sandbox -- 'sudo systemctl daemon-reload && sudo systemctl enable --now webapp.service'
```

#### Option 2: InstaBox Managed Background Jobs
```bash
instabox exec --background web-sandbox --cwd /data/workspace/my-web-app -- npm start
# Track background job:
instabox jobs ls web-sandbox
instabox jobs logs web-sandbox <job-id>
```

#### Option 3: Process Manager (PM2) or Nohup with Redirection
```bash
# PM2
instabox exec web-sandbox -- npm install -g pm2
instabox exec web-sandbox --cwd /data/workspace/my-web-app -- pm2 start npm --name "my-app" -- start
instabox exec web-sandbox -- pm2 save

# Nohup (Must redirect stdout and stderr)
instabox exec web-sandbox -- 'cd /data/workspace/my-web-app && nohup npm start --host 0.0.0.0 --port 3000 > server.log 2>&1 &'
```

---

## 5. Ingress & Exposing Ports to the Internet

### A. Public HTTPS URL (Wildcard Cloud Ingress)
Expose an internal server port to a secure public HTTPS URL:

```bash
# Expose port (e.g. 8000 or 3000)
instabox port publish web-sandbox 8000 --name "Production App"

# List published endpoints and retrieve assigned URL
instabox port ls web-sandbox
```
- **Generated URL format**: `https://<port>-<machine_id_without_m_>.instabox.tech/` (or `.instabox.sh/`)
- **Auto-Wake Feature**: Visiting this URL automatically triggers an auto-resume if the machine was suspended due to 30-minute idle timeout.
- **Unpublish**:
  ```bash
  instabox port unpublish web-sandbox 8000
  ```

### B. Private Port Forwarding (Local Dev Tunnel)
If the port should remain private to the developer's computer:
```bash
# Tunnel remote 8000 to local 8080
instabox port-forward web-sandbox 8080:8000
```

### C. In-Machine CLI (`instabox-port`)
Inside the sandbox, `instabox-port` is pre-installed at `/usr/local/bin`:
```bash
# Publish port directly from inside the sandbox
instabox-port publish 8000

# Quick static file server
instabox-port serve ./public --port 8080
```

---

## 6. Maintenance, Diagnostics & Telemetry

```bash
# Process list
instabox ps web-sandbox

# Boot and console logs (does NOT wake a sleeping machine)
instabox logs web-sandbox -f

# Check listening ports
instabox exec web-sandbox -- 'ss -ltnp'

# Soft restart if hung (power-cycles microVM while keeping /data)
instabox restart web-sandbox

# Quotas and usage
instabox usage

# Snapshots & Rollback
instabox snapshot save web-sandbox --name v1.0-stable
instabox snapshot ls
instabox fork web-sandbox          # Snapshot + clone into new machine
```

---

## 7. Pitfalls & Troubleshooting Matrix

| Trap | Root Cause | Solution |
|------|------------|----------|
| **Server dies after exec returns** | Background process writes stdout/stderr to closed pipe | Redirect `>server.log 2>&1 &` or use `systemd` service |
| **URL unreachable from outside (502/Connection Refused)** | Server listening on `127.0.0.1` instead of all interfaces | Bind server to `0.0.0.0` |
| **URL returns 503 Service Unavailable** | Machine is stopped or shut down (not suspended) | Run `instabox start web-sandbox` and start processes |
| **Asset URL broken in browser (e.g. Laravel Vite)** | HTML generates links with `http://127.0.0.1` | Set `APP_URL=https://<port>-<machine>.instabox.tech` in `.env` |
| **Database TCP access denied (MariaDB)** | MariaDB default user is socket-auth only for `localhost` | Create/alter user with password or set `127.0.0.1` user privileges |
| **Exec output truncated** | Non-streaming output truncated at 1 MiB | Use `instabox exec --stream` or `instabox cp` / `instabox pull` |
| **Delete command fails** | API enforces confirmation | Use `instabox rm web-sandbox --yes` |

---

## 8. HTTP API Fallback (When CLI is Unavailable)

Base URL: `https://api.instabox.sh/v1`  
Auth Header: `X-API-Key: $INSTABOX_API_KEY`

```bash
# List machines
curl -s -H "X-API-Key: $INSTABOX_API_KEY" https://api.instabox.sh/v1/machines

# Execute command
curl -s -X POST https://api.instabox.sh/v1/machines/<machine_id>/exec \
  -H "X-API-Key: $INSTABOX_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"cmd": "uptime"}'

# Upload file via signed URL
# 1. Get signed URL
curl -s -X POST https://api.instabox.sh/v1/machines/<machine_id>/files/upload-url \
  -H "X-API-Key: $INSTABOX_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"path": "/data/workspace/app.zip"}'
# 2. PUT data to the returned upload_url
```
