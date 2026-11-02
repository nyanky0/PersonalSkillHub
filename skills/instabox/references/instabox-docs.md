# InstaBox docs

> InstaBox gives each agent a Linux machine of its own in the cloud. Start with one command, then read only the page you need.

---

# Quick start

https://instabox.sh/docs/start.md

From nothing to a shell in your own cloud machine.

### One command
```
npx instabox@latest sh
```
It signs you in with a device code, starts a new machine, installs the `instabox` CLI and the instabox agent skills (in `~/.claude/skills` and `~/.agents/skills`), and opens a shell in the machine over SSH. `--no-skills` leaves your skills alone and `--no-cli` skips the CLI; everything else is the same.

### Or step by step
```
curl -fsSL https://api.instabox.sh/install.sh | sh    # install the CLI
instabox login                             # sign in with a device code
instabox create --name dev                 # template agent-browser, the default
instabox ssh dev
```
It prints a page and a code: open the page on any device and enter the code, so it works over SSH too.

### When you are done
```
instabox suspend dev    # pause: files, memory and running processes are kept
instabox resume dev     # carry on where you left off
```

> In the dashboard, **Create machine** on the **Machines** page does what `instabox create` does. Programs, CI jobs and agents use an API key instead of a sign-in: see [Integrate with the SDK](https://instabox.sh/docs/integrate.md) and [API keys and SDK](https://instabox.sh/docs/keys-sdk.md).

---

# Concepts

https://instabox.sh/docs/concepts.md

The few words the dashboard, the CLI and the API use.

| Word | What it is |
|---|---|
| **Machine** | A Linux VM of your own in the cloud, with its own kernel, root and Docker. Files under `/data` (home is `/data/home`) and the software you install stay. |
| **Template** | What a new machine starts from: `agent-browser`, `universal`, `herdr` or `orca`. `instabox templates` lists them. |
| **Snapshot** | A saved copy of one of your machines, private to you. New machines can start from it. |
| **Operation** | A change to a machine (create, start, stop, pause, resume, delete). You follow it until it succeeds or fails. |
| **API key** | `ibk_...`: how programs, CI jobs and agents sign in. |
| **Org Secrets** | Encrypted credentials that sandboxes see as placeholders; the outbound proxy adds them to HTTPS headers for allowed hosts. |

### Running, paused, stopped
| State | Files | Memory and processes | Use it to |
|---|---|---|---|
| Running | kept | running | work |
| Paused | kept | kept | step away and come back to the same session |
| Stopped | kept | lost | shut down; the next start boots fresh |
| Deleted | gone | gone | free the machine for a new one |

A new machine pauses once it has been idle for 30 minutes. On a paid plan you can choose 5 to 30 minutes, or `instabox auto-suspend <machine> 0` to turn that off; below 5 or above 30 minutes is refused. On the free plan it stays 30 minutes, and `--auto-suspend` with another value is refused. Commands, files, SSH and a visit to one of its public port URLs resume it by themselves. One you paused or stopped waits for **Resume** or **Start**.

> The API and CLI say `suspend`, `suspending` and `suspended` for pause, Pausing and Paused, and `error` for Failed.

---

# Integrate with the SDK

https://instabox.sh/docs/integrate.md

The calls an app needs: create, pause and resume, delete, a shell, the desktop, and usage.

Everything below runs on your server with an API key (`ibk_...`, from **API keys** in the dashboard sidebar). Never send the key to a browser.
```
npm install @insforge/instabox-sdk
export INSTABOX_API_KEY=ibk_...
```
The SDK reads `INSTABOX_API_KEY` from the environment, so the `apiKey` option below is optional. Pass it when the key comes from somewhere else, such as your own secret store. Without a key, every call throws `InstaboxAuthError` (`missing_api_key`) before sending a request.

### 1. Create a machine
```
import { Sandbox } from '@insforge/instabox-sdk'

const sbx = await Sandbox.create('agent-browser', {
  // optional: the env var works without this line
  apiKey: process.env.INSTABOX_API_KEY,
  // your own tags, to find it later
  metadata: { customer: 'acme' },
  // disable personal Vault delivery; no Secret selections are supplied
  vault: false,
})
// m_...: store it with your user
console.log(sbx.sandboxId)
```
`agent-browser` is the default template: Linux, a desktop and a browser. Later, from another request: `const sbx = await Sandbox.connect(id)`. `Sandbox.list({ metadata: { customer: 'acme' } })` finds machines by tag.

### 2. Pause and resume
```
// memory, files and running processes are kept
await sbx.pause()
// carries on where it left off, usually in about a second
await sbx.resume()
// connect also resumes a paused machine
const again = await Sandbox.connect(id)
// look without waking it
const peek = await Sandbox.connect(id, { resume: false })
```
Idle machines pause by themselves after 30 minutes.

### 3. Delete it
```
// deletes the machine and its disks; false if already gone
await sbx.kill()
// the same, by ID
await Sandbox.kill(id)
```

### 4. A shell
For commands from your code:
```
const r = await sbx.commands.run('python3 -c "print(6 * 7)"', {
  cwd: '/data/home',
  timeoutMs: 60_000,
})
// a non-zero exit throws CommandExitError (stdout, stderr, exitCode)
console.log(r.stdout, r.exitCode)
await sbx.files.write('/data/home/app.py', 'print("hi")')
console.log(await sbx.files.read('/data/home/app.py'))
```
For an interactive SSH session (your public key in, a short-lived certificate out):
```
const ssh = await sbx.sshCredentials(publicKey, { ttlSeconds: 3600 })
// save ssh.certificate as <key>-cert.pub next to the private key,
// add ssh.knownHostsLine to known_hosts, then:
// ssh -p ${ssh.port} ${ssh.username}@${ssh.host}
```
See [SSH](https://instabox.sh/docs/ssh.md) for the details.

### 5. The desktop (VNC)
```
// starts the desktop; safe to call again
await sbx.desktop.start()

// Let people watch it: a link to one machine's desktop,
// for a new tab or an <iframe>
const { url } = await sbx.desktop.streamUrl({
  viewOnly: true,
  ttlSeconds: 3600,
})

// Let an agent use it
await sbx.desktop.open('https://example.com')
const png = await sbx.desktop.screenshot()
await sbx.desktop.click(640, 400)
await sbx.desktop.type('hello')
await sbx.desktop.press('Enter')

// Take the links away (e.g. when a user's access ends);
// open viewers close within seconds
await sbx.desktop.revokeStreamUrls()
```
See [Desktop](https://instabox.sh/docs/desktop.md) for embedding the link and a full agent loop.

### 6. Watch load and bill per machine
```
// CPU and memory, one sample per 30 s, oldest first
const samples = await sbx.getMetrics()
// bill a customer: running seconds of their machines this month
const machines = await Sandbox.list({ metadata: { customer: 'acme' } })
let seconds = 0
for (const m of machines) {
  const u = await Sandbox.getUsage(m.sandboxId)
  seconds += u.runningSeconds
}
```
`getUsage` covers the current UTC month by default and counts running time only, not paused or stopped. See [Metrics and usage](https://instabox.sh/docs/sdk.md) for every field.

### Errors
Calls throw `InstaboxError` with `status` and `code` (`not_found`, `quota_exceeded`, ...); a missing or bad key throws `InstaboxAuthError`. The same calls over HTTP:

| SDK | HTTP |
|---|---|
| `Sandbox.create` | `POST /v1/machines` |
| `pause` / `resume` | `POST /v1/machines/{id}/suspend` / `.../resume` |
| `kill` | `DELETE /v1/machines/{id}` |
| `commands.run` | `POST /v1/machines/{id}/exec` |
| `sshCredentials` | `POST /v1/machines/{id}/connections` |
| `desktop.start` | `POST /v1/machines/{id}/desktop` |
| `desktop.streamUrl` / `revokeStreamUrls` | `POST` / `DELETE /v1/machines/{id}/desktop/stream` |
| `getMetrics` | `GET /v1/machines/{id}/metrics` |
| `getUsage` | `GET /v1/machines/{id}/usage` |
| `Sandbox.usage` | `GET /v1/usage` |

Every endpoint: the [API reference](https://instabox.sh/docs/api.md).

### SDK operations
Every call in the SDK, by task. `sbx` is a `Sandbox` object.

| Operation | Call | What it does |
|---|---|---|
| **1. Create and find** | | |
| Create | `Sandbox.create(template?, opts?)` | New machine, waits until it runs |
| Connect | `Sandbox.connect(id, opts?)` | Attach by ID; resumes it |
| List | `Sandbox.list(opts?)` | Your machines, filter by metadata |
| Info | `sbx.getInfo()` | State, metadata, auto-pause |
| Running? | `sbx.isRunning()` | True if running now |
| **2. Pause and resume** | | |
| Pause | `sbx.pause()` | Suspend, memory kept |
| Resume | `sbx.resume()` | Resume or start it |
| Stop | `sbx.stop()` | Shut down, `/data` kept |
| Idle pause | `sbx.setAutoSuspend(idleMs)` | Pause it when idle |
| **3. Delete** | | |
| Delete | `sbx.kill()` | Delete it and its disks |
| Delete by ID | `Sandbox.kill(id, opts?)` | The same, by ID |
| **4. Shell** | | |
| Run | `sbx.commands.run(cmd, opts?)` | Run a command, get its output |
| Raw exec | `sbx.commands.exec(cmd, opts?)` | Run, no throw on non-zero exit |
| Read file | `sbx.files.read(path, opts?)` | Text, or bytes |
| Write file | `sbx.files.write(path, data)` | Create or replace a file |
| List files | `sbx.files.list(path)` | A directory's entries |
| Remove file | `sbx.files.remove(path)` | A file or a directory |
| File exists? | `sbx.files.exists(path)` | True if it exists |
| SSH | `sbx.sshCredentials(publicKey, opts?)` | A short-lived certificate |
| **5. Desktop and VNC** | | |
| Start | `sbx.desktop.start(opts?)` | Start the desktop |
| Status | `sbx.desktop.status()` | Running, screen size |
| Share link | `sbx.desktop.streamUrl(opts?)` | A link to watch it |
| Revoke links | `sbx.desktop.revokeStreamUrls()` | End every link and viewer |
| Screenshot | `sbx.desktop.screenshot()` | A PNG of the screen |
| Click | `sbx.desktop.click(x, y, opts?)` | Click at a point |
| Move | `sbx.desktop.move(x, y)` | Move the pointer |
| Drag | `sbx.desktop.drag(from, to)` | Drag with the left button |
| Scroll | `sbx.desktop.scroll(opts)` | Turn the wheel |
| Type | `sbx.desktop.type(text, opts?)` | Type text |
| Press | `sbx.desktop.press(keys)` | A key or a chord |
| Open URL | `sbx.desktop.open(url)` | Open it in the browser |
| Pointer | `sbx.desktop.cursorPosition()` | Where the pointer is |
| **6. Metrics and usage** | | |
| Metrics | `sbx.getMetrics(opts?)` | CPU and memory samples |
| Metrics by ID | `Sandbox.getMetrics(id, opts?)` | The same, by ID |
| Usage | `sbx.getUsage(opts?)` | Running time, for billing |
| Usage by ID | `Sandbox.getUsage(id, opts?)` | The same, by ID |
| Account usage | `Sandbox.usage(opts?)` | Counts, storage, limits |
| **7. Also** | | |
| Labels | `sbx.setMetadata(metadata)` | Replace its metadata |
| Save snapshot | `sbx.createSnapshot(opts)` | Save its disks |
| Copy | `Sandbox.create(snapshot.id)` | A new machine from a snapshot |
| List snapshots | `Sandbox.listSnapshots(opts?)` | Your snapshots |
| Get snapshot | `Sandbox.getSnapshot(id, opts?)` | One snapshot |
| Delete snapshot | `Sandbox.deleteSnapshot(id, opts?)` | Delete a snapshot |

Full details: [SDK reference](https://instabox.sh/docs/sdk.md).

---

# Machines

https://instabox.sh/docs/machines.md

Lifecycle, sizes, auto-pause, logs, labels and secrets.

### Lifecycle
- Every change is an **operation**, and a machine has at most one at a time. The dashboard shows them in the operations tray.
- **Resume** brings back a paused machine's memory and processes. If that is not possible it starts fresh: files are kept, processes are not.
- A paused machine cannot be stopped: resume or delete it.
- **Restart** (`instabox restart <machine>`, or `recover`) power-cycles a machine that stopped answering: stop, then start. The root disk and `/data` are kept; processes and memory are not. Stop asks the guest to power off, then sends Ctrl+Alt+Del, and kills the VM once the timeout runs out (60 seconds, or `--timeout` up to 10 minutes), so a hung guest comes back too; writes it had not flushed can be lost. A machine stuck in `starting` with no start in progress cannot be power-cycled.
- A reboot from inside (`sudo reboot`, `systemctl reboot`, `shutdown -r`) reboots the machine: it shows Starting, then Running again on the same disks, with new processes. A shutdown from inside (`sudo poweroff`, `halt`, `shutdown -h`) stops it until a start. Machines created from a template older than this change stop on a reboot too; a machine that reboots more than 5 times in 10 minutes is left stopped.
- The dashboard's states: Creating, Starting, Running, Stopping, Stopped, Pausing, Paused, Resuming, Deleting, Failed.

### Sizes
A machine is 4 vCPUs and 8 GiB of memory unless the create names another size of your plan, with both the vCPUs and the memory in MiB:

| Plan | Sizes (vCPUs / MiB) |
|---|---|
| Free | 4 / 8192 |
| Pro | 2 / 4096, 4 / 8192 (default), 8 / 16384 |
| Team | 2 / 4096, 4 / 8192 (default) up to 32 / 65536 |

`GET /v1/orgs` (`instabox workspace ls --json`) lists each workspace's as `allowedSpecs`. Another size is `400 spec_not_allowed`. A paid machine moves to another size of its plan while stopped (`PATCH /v1/machines/{id}` `{"vcpus": N, "memMiB": M}`, `instabox resize --vcpus N --mem-mib M`), applied at its next start (which fails with `no_capacity` if the host has no room for the new size, or `host_unavailable` if its node-agent cannot resize yet; the machine stays stopped at the new size); a free machine's size is fixed.
```
instabox create --name big --vcpus 8 --mem-mib 16384
instabox create --name job --template universal@2026-10-15.4   # or --template-version
```
Over the API these are `vcpus`, `memMiB` and `templateVersion` on [Create a machine](https://instabox.sh/docs/api/machines.md#create).

### Auto-pause
A running machine pauses once it has been idle for 30 minutes. On a paid plan (Pro, Team, Enterprise) you choose 5, 10, 15, 20, 25 or 30 minutes (a time between rounds up to the next; below 5 or above 30 minutes is refused), or `0` to turn it off. On the free plan it is fixed at 30 minutes, and another value is refused. Commands, files, SSH and a visit to a public port URL resume it.
```
instabox auto-suspend job 10m   # pause after 10 idle minutes
instabox auto-suspend job 0     # never pause when idle
```

### Logs
`instabox logs` prints a machine's console log and its last 20 operations (create, start, stop, pause, resume, with their errors). The console log is the serial console: kernel and systemd boot messages, anything written to /dev/console, and errors from the VM monitor. It is kept on the host across stops, pauses and restarts (the last 8 MiB). Reading it works in every state and never wakes the machine, so use it when a machine does not boot, is unreachable, or a start or resume failed.
```
instabox logs job                 # the last 200 console lines and the operations
instabox logs job --tail 50 -f    # follow new output (Ctrl-C stops)
instabox logs job --json          # GET /v1/machines/{id}/logs
```
Over the API, `GET /v1/machines/{id}/logs?tail=N` (scope `machines:read`) returns `console`, `cursor`, `state` and `operations` (oldest first). To follow it, pass `cursor` as `after` on the next request to get only newer output. When the console cannot be read, for example because the machine's disks are in storage, the response is still 200, with `consoleUnavailable` and the operations. A command's own output is kept with its background job, and the full guest journal is read over exec:
```
instabox jobs logs job <job-id>
instabox exec job -- sudo journalctl -b --no-pager   # this boot
```

### Labels
Up to 32 `key=value` labels (metadata) per machine. They are stored in plain text: use them for labels, not secrets.
```
instabox create --name job --meta task=review
instabox ls --meta task=review     # GET /v1/machines?metadata=task:review
```

### Secrets
Use [Org Secrets](https://instabox.sh/docs/secrets.md) for named credentials shared within an org. A sandbox sees placeholders, and the outbound proxy adds the credentials to HTTPS headers sent to each Secret's allowed hosts. Manage values and sandbox selections in the dashboard's Secrets page, the CLI or the API.

### Vault
The per-user Vault continues to support environment variables, home files and metadata selectors alongside Org Secrets. Upgrading does not migrate items or enroll existing sandboxes in Secrets. Manage Vault items with `instabox vault set`, `set-file`, `import`, `ls`, `rm`, `show` and `push`. See [Secrets](https://instabox.sh/docs/secrets.md) for explicit org-owned credentials.

---

# Snapshots

https://instabox.sh/docs/snapshots.md

Save a machine once, start new ones from it.

A snapshot holds a machine's installed software and its files under `/data`: home, workspace and saved sign-ins (gh, Claude, Codex, git, SSH). It does not hold memory or running processes. Snapshots are private to you.

### Save one, start from it
```
instabox snapshot save dev --name dev-base
instabox create --name dev2 --snapshot dev-base
instabox snapshot ls
```
In the dashboard: **Save snapshot** in a machine's menu, then **New machine from it**, now or later on the **Snapshots** page.

### Fork a machine
```
instabox fork dev --name dev2
instabox fork dev --name try --count 3 --json
```
`fork` (or `clone`) saves a snapshot of the machine, creates one machine (or `--count`, up to 5, named `try-1` to `try-3`) from it with the same template and size, waits until they run, then deletes the snapshot (also on error or Ctrl-C) unless `--keep-snapshot`. The source machine is not changed. It is snapshot save plus create, so it takes about as long as those two. Each new machine counts toward your plan's machine starts a minute; `fork` waits that out.

### Set up once, reuse everywhere
In the **Playground**, start a machine, install your tools, repos and agent sign-ins in its terminal, then **Save as snapshot**. Every machine you start from it is set up.

### Good to know
- Saving stops a running or paused machine first: processes end, files are kept. Where the server allows it, a running machine is saved while it keeps running; that snapshot leaves out data programs have not written to disk yet.
- `snapshot save` waits until it is saved; `--no-wait` returns at once.
- `--root-only` saves the installed software only: machines from it start with an empty home and workspace, as do older snapshots that hold installed software only.
- Saving refused because the machine has unsaved changes? Stop it again, then retry.
- `instabox snapshot files dev-base /etc` lists its files without starting a machine.
- Deleting a machine keeps its snapshots; deleting a snapshot does not affect machines made from it.
- Over HTTP: `POST /v1/machines/{id}/snapshots` saves one, `GET /v1/snapshots` lists them, `POST /v1/machines` with `"snapshotId"` starts a machine from one.

---

# Connecting over SSH

https://instabox.sh/docs/ssh.md

With the CLI, or one ssh line for any terminal.

### With the CLI
```
instabox ssh dev                 # certificate, known_hosts and ssh in one step
instabox ssh dev -- uname -a     # run one command
instabox mosh dev                # like instabox ssh, with mosh
instabox ssh-config dev          # print a ~/.ssh/config Host block
instabox ssh-cert dev            # refresh only the certificate
```

### Port forwarding
`instabox port-forward dev 8080:3000` (or `forward`) makes port 3000 in the machine reachable at `http://127.0.0.1:8080` on your computer until you press Ctrl-C. `LOCAL` defaults to `REMOTE` (`instabox port-forward dev 3000`), and one command can forward several ports (`instabox port-forward dev 8080:3000 5432`). It is `ssh -N -L` with the instabox certificate, so it reaches any TCP service, and only you can use it: it listens on 127.0.0.1 unless `--address` says otherwise. For a URL other people can open, use [public ports](https://instabox.sh/docs/ports.md) instead.

### From any terminal, without the CLI
A machine's **Connect** section has **SSH tokens**: **Create token** gives one `ssh ibssh_…@<host>` line to paste anywhere, no CLI or SSH key needed. It stays in that section, ready to copy, and works until you revoke it (or for the time you pick). From the CLI: `instabox ssh-token dev`. The first time, ssh asks you to confirm the gateway's host key.

### mosh
[mosh](https://mosh.org) keeps a session alive through sleep, network changes and packet loss. Install it on your computer (macOS: `brew install mosh`), then run `instabox mosh dev` or the mosh command **Create token** shows. Snapshots made before mosh was added need `sudo apt install mosh` once.

### How it works
The instabox gateway terminates SSH: `ssh -p <port> <machine-id>@<host>`, with a short-lived user certificate, and a known_hosts line `@cert-authority [<host>]:<port> <host CA key>` to trust the gateway. It relays mosh's UDP too, so only the gateway has to be reachable.
- Supported: sessions (pty, shell, exec, subsystem, env, signals) and local port forwarding.
- Not supported: agent forwarding, X11, remote forwarding.
- Connections close when the machine stops, pauses or is deleted.

---

# Public ports

https://instabox.sh/docs/ports.md

Give a web server in a machine an HTTPS URL.

```
instabox port publish dev 3000 --name 'Web app'   # prints the URL
instabox port ls dev
instabox port unpublish dev 3000
```
Inside the machine, an agent does the same with `instabox-port` (`instabox port setup dev` installs it where it is missing):
```
instabox-port publish 3000 --name 'Web app'
instabox-port serve ./report --port 8080          # serve a folder with an index.html
```
- The URL is `https://<port>-<machine id without m_>.<domain>/`. It is not a secret: once published, anyone can reach the whole service until you unpublish it.
- A visit wakes a machine that paused itself for being idle (the 30-minute idle pause): the request waits for it to resume, so a phone app or webhook can reach the URL without starting it first. `instabox wake <machine>` does the same without a request. A machine you paused or stopped stays offline until you resume or start it, at the same URL. After a stop, start your server again.
- Up to 16 public ports per machine. In the dashboard, a machine's **Ports** tab publishes and unpublishes them.
- To reach a port only from your own computer, without a public URL, use `instabox port-forward dev 8080:3000` (see [Connecting over SSH](https://instabox.sh/docs/ssh.md)).

---

# Desktop: see it and control it

https://instabox.sh/docs/desktop.md

Watch a machine's desktop, let an agent drive it, and share a link to it.

Machines from the `agent-browser` template (shown as **standard**) have a Linux desktop with a browser. You can watch it, let an agent drive it, and give other people a link to it.

### In the dashboard
Open a machine and choose the **Computer** tab. Click the desktop to take control; it goes back to the agent after a minute idle.

### Let an agent drive it (SDK)
```
import { Sandbox } from '@insforge/instabox-sdk'

const sbx = await Sandbox.create('agent-browser')
await sbx.desktop.start({ width: 1280, height: 800 })

await sbx.desktop.open('https://example.com')        // opens the browser
const png = await sbx.desktop.screenshot()           // PNG bytes, e.g. for a vision model
await sbx.desktop.click(640, 400)                    // { button: 'right' }, { double: true }
await sbx.desktop.press(['ctrl', 'l'])               // a key or a chord
await sbx.desktop.type('instabox.sh')                // any text, quotes and unicode included
await sbx.desktop.press('Enter')
await sbx.desktop.scroll({ direction: 'down', amount: 5 })
```
Also: `move(x, y)`, `drag([x1, y1], [x2, y2])`, `cursorPosition()`, `status()`. `start()` is safe to call again; it leaves a running desktop alone.

A minimal agent loop:
```
for (let step = 0; step < 20; step++) {
  const png = await sbx.desktop.screenshot()
  const action = await yourModel.nextAction(png)     // { type: 'click', x, y } | { type: 'type', text } | { type: 'done' }
  if (action.type === 'done') break
  if (action.type === 'click') await sbx.desktop.click(action.x, action.y)
  if (action.type === 'type') await sbx.desktop.type(action.text)
}
```

### Share a link to the desktop
`streamUrl()` makes a link to a full-screen viewer of one machine's desktop. It works without signing in and can be embedded in an `<iframe>`:
```
const { url, expiresAt } = await sbx.desktop.streamUrl({
  viewOnly: true,        // the default: the viewer can watch, not type or click
  ttlSeconds: 3600,      // 60 to 86400; the default is one hour
})
```
```
<iframe src="LINK_URL" width="1280" height="800" style="border:0"></iframe>
```
- **One machine.** A link opens that machine's desktop only. It is not an API key and cannot call the API.
- **View-only is enforced by the server.** Keyboard, mouse and clipboard input from a view-only link never reach the machine. Pass `viewOnly: false` for a link that can control it.
- **Expiry stops new connections.** A viewer that is already connected stays connected until it leaves.
- **Revoke ends everything.** `revokeStreamUrls()` invalidates every link for the machine and closes open viewers within a few seconds. Deleting the machine does the same.

### Building a service for your own users
Keep your API key on your server, never in a browser. Make a fresh link each time a user opens their desktop, and revoke when their access ends:
```
// your server, e.g. Express
app.get('/api/desktop-link', async (req, res) => {
  const machineId = await machineOf(req.user)       // your own user-to-machine mapping
  const sbx = await Sandbox.connect(machineId)
  res.json(await sbx.desktop.streamUrl({ viewOnly: !req.user.canControl, ttlSeconds: 600 }))
})

// when the user's access ends
await (await Sandbox.connect(machineId)).desktop.revokeStreamUrls()
```
Tag machines with metadata, such as `{ customer: 'acme' }`, to find them later with `Sandbox.list({ metadata })`.

### Over HTTP
```
H="X-API-Key: $INSTABOX_API_KEY"
curl -s -H "$H" -H 'Content-Type: application/json' \
  -d '{"action": "start", "width": 1280, "height": 800}' "$INSTABOX_API_URL/v1/machines/m_.../desktop"
curl -s -H "$H" -H 'Content-Type: application/json' \
  -d '{"viewOnly": true, "ttlSeconds": 3600}' "$INSTABOX_API_URL/v1/machines/m_.../desktop/stream"   # {url, expiresAt}
curl -s -X DELETE -H "$H" "$INSTABOX_API_URL/v1/machines/m_.../desktop/stream"                     # revoke
```
Both stream calls need a key with `machines:write`.

---

# Org Secrets

https://instabox.sh/docs/secrets.md

Credentials added to HTTPS headers by the outbound proxy, scoped to your org.

Secrets are encrypted key=value pairs owned by an org. A sandbox can only use Secrets from its own org. Each Secret lists the exact hosts it may be sent to, or `*` for every public HTTPS destination. Partial wildcards such as `*.example.com` are not supported. Once Secrets is enabled for your account and supported by the server, new Dashboard sandboxes receive all current and future proxy Secrets from their workspace. Existing sandboxes keep their selections. Use the CLI or HTTP API to change a sandbox's selection.

### How a Secret reaches an API
The sandbox sees the named environment variable, but its value is an opaque placeholder. Applications keep their normal HTTPS URL and header name. The outbound proxy checks sandbox authorization, host scope and the upstream TLS certificate before replacing the placeholder within a header value. Version one supports HTTPS on port 443; URL parameters and request bodies are not substituted. HTTP Basic auth in `Authorization` is decoded, the placeholder inside `user:password` is replaced, and the credential is re-encoded; any other encoding or signing of the placeholder prevents replacement.

### Save and select
Sign in with the CLI as an org owner or admin, or run it headless with the workspace's `workspace:admin` API key in `INSTABOX_API_KEY` (org commands then default to the key's org, and `secrets rm` needs `--yes` without a terminal). Values below are read from stdin or a prompt without echo:
```sh
instabox secrets set SERVICE_API_KEY --org team --host api.example.com
instabox create --name app --org team --secrets all
instabox secrets show app
```

Omitting `secrets` in CLI or API creation keeps the existing Vault behavior without enrolling the sandbox in Secrets. To disable delivery from both stores on a fresh sandbox, pass `--no-vault --secrets none`. Without `--host`, a Secret may be sent to every public HTTPS destination (`*`); pass `--host` to limit it.

With `*`, any process in an enrolled sandbox can send the Secret to any public HTTPS destination, including a host it controls. All supported HTTPS hosts are intercepted, even without a placeholder. Intercepted connections to private addresses are closed, WebSocket upgrades are unsupported, and clients must trust the sandbox CA without certificate pinning. Prefer exact hosts when the credential must stay with a specific service.

The application reads `SERVICE_API_KEY` as a sandbox-specific placeholder and sends it in its usual header, such as `Authorization: Bearer <placeholder>` or `X-Api-Key: <placeholder>`. No separate Secret retrieval API is needed.

Git over HTTPS sends the token as Basic auth, so `git clone` and `git push` to private repos work with a placeholder too. Add `github.com` (git) to the Secret's hosts next to `api.github.com` (`gh`), and give git a credential helper that returns the placeholder, such as `gh auth setup-git` for `GH_TOKEN`.

For bulk import, `instabox secrets import .env --org team --host api.example.com` validates and writes the whole file atomically; all entries share that host scope. Importing Secrets does not authorize any sandbox to receive them.

### Update a running sandbox
```sh
instabox secrets select app --secrets SERVICE_API_KEY
instabox secrets push app
instabox secrets show app
```
The supplied selection replaces the previous one. Removing and recreating a Secret with the same name does not restore an explicit grant to the old Secret. `all` includes newly created Secrets.

`instabox secrets show` reports proxy authorization and placeholder setup in the sandbox independently. A proxy update is pending until acknowledged, and an acknowledged lease expires within at most 60 seconds without renewal. Requests already admitted, including streams, may finish.

Rotating an existing value keeps its placeholder, so applications need no restart.

### Save a Secret with the HTTP API
`PUT /v1/orgs/{id}/secrets/{name}` creates or replaces a Secret. The body has three fields:

| Field | Required | Meaning |
| --- | --- | --- |
| `value` | yes | The credential, up to 64 KiB of UTF-8. Proxy values must fit in an HTTP header. |
| `delivery` | yes | `"proxy"` or `"env"`, on every write, including a rotation. Without it the request fails with `400 delivery is required`; nothing is inferred from the name or value. |
| `hosts` | proxy only | Up to 32 exact hostnames (no scheme, port, path or wildcard); `"*"` allows every public HTTPS destination. Omitted or `[]` means `["*"]`. An env Secret with non-empty `hosts` is rejected. |

The caller must be an org owner or admin, signed in. After `instabox login`, the CLI's access token works (`instabox whoami` refreshes it first). A workspace API key with `workspace:admin` also works for its workspace, sent as `X-API-Key`. This saves a proxy Secret in your personal org:
```sh
instabox whoami >/dev/null
AUTH=$(mktemp)
jq -r '"Authorization: Bearer " + .accessToken' "${XDG_CONFIG_HOME:-$HOME/.config}/instabox/credentials.json" >"$AUTH"
ORG=$(curl -sS "https://api.instabox.sh/v1/orgs" -H @"$AUTH" | jq -r '.orgs[] | select(.personal) | .id')
curl -sS -X PUT "https://api.instabox.sh/v1/orgs/$ORG/secrets/SERVICE_API_KEY" -H @"$AUTH" -H 'Content-Type: application/json' --data-binary @- <<'EOF'
{"value":"example-api-key","delivery":"proxy","hosts":["api.example.com"]}
EOF
rm -f "$AUTH"
```
The token header is read from a mode 0600 file and the body from stdin, so neither appears in the process list. A heredoc you type still lands in shell history: for a real credential, build the body from a file instead, `jq -Rs '{value: rtrimstr("\n"), delivery: "proxy", hosts: ["api.example.com"]}' <key.txt`, and pipe it into the same `curl`.

A new Secret answers `201 Created`, a replacement `200 OK`, with the Secret's metadata and never its value: `id`, `orgId`, `name`, `delivery`, `hosts`, `version`, `size`, `createdAt`, `updatedAt`. For an env Secret, send `{"value":"postgresql://app:example-password@db.example.com/app","delivery":"env"}` to `.../secrets/DATABASE_URL`. `POST /v1/orgs/{id}/secrets/import` takes `{"values":{...},"delivery":...,"hosts":[...]}` with the same rules for every entry, except that a missing `delivery` there answers `400 delivery must be proxy or env`. The CLI always saves `proxy`.

Where each mode exposes the value:

| Delivery | In the sandbox | Where the real value appears |
| --- | --- | --- |
| `proxy` | `NAME=ibsec_...`, a sandbox-specific placeholder | Only in HTTPS request headers (port 443) to the Secret's `hosts`, where the outbound proxy swaps it in. Never in the sandbox, URLs or request bodies. |
| `env` | `NAME=<real value>` | Inside the sandbox: any process there can read and copy it. No host restriction applies. |

Both modes are written to `/run/instabox/secrets/env` (tmpfs, mode 0600, owned by the sandbox user) and loaded by `/etc/profile.d/zz-instabox-secrets.sh`. Login shells get them: SSH, `instabox exec` and the exec API. Processes that skip the profile (systemd units, cron, `bash -c` without `-l`) do not, and running processes keep their old environment until restarted. An env Secret reaches a sandbox only when the sandbox selects it in `envSecrets` (`"envSecrets": ["DATABASE_URL"]` on `POST /v1/machines` or `PATCH /v1/machines/{id}/secrets`); `"secrets": "all"` never includes env Secrets.

### HTTP and SDK callers
Use the HTTP API for explicit selections when an SDK does not expose them:
```json
{
  "name": "app",
  "templateId": "universal",
  "orgId": "org_...",
  "secrets": ["SERVICE_API_KEY"]
}
```
Send this to `POST /v1/machines`. After creation, use `PATCH /v1/machines/{id}/secrets` with a new `secrets` selection, `GET` on the same path for metadata and status, and `POST` on that path for an immediate refresh. Explicit `null` selections are rejected.

API keys with `machines:read` can read org Secret metadata and sandbox selections. `machines:write` can change selections and refresh delivery for authorized sandboxes. Creating, importing, changing or deleting org Secret values requires the org owner or admin: a signed-in session or the workspace's own `workspace:admin` API key. A personal org's key and narrower keys cannot manage values (`403 missing_scope`). Management reads never return values. Full endpoint schemas are in the [OpenAPI specification](https://api.instabox.sh/v1/openapi.json).

The SDK creation option `vault: false` disables only per-user Vault delivery; it does not change org Secret selections. Vault inspection and push APIs remain available. When an SDK does not expose Secret selection fields, use the Secret CLI or HTTP API.

### Existing Vault items
Vault and Org Secrets remain independent stores. Existing env values, file delivery and metadata selectors keep working; there is no automatic migration. A sandbox can use both stores, and explicitly selected Secrets take precedence for same-named environment variables. `--no-vault` affects only Vault; clearing Secret selections affects only Secrets. `instabox vault export NAME --out recovered.json` remains available for items retained by an earlier explicit migration. Its output contains the real value.

---

# Webhooks

https://instabox.sh/docs/webhooks.md

Signed POSTs when a sandbox is ready, pauses, stops, fails or is deleted.

Register an HTTPS endpoint for an org and InstaBox POSTs a signed JSON event to it when one of the org's sandboxes or snapshots changes state, so clients need not poll `GET /v1/machines/{id}`.

### Events
| Type | When |
|---|---|
| `sandbox.created` | the sandbox is accepted (state `creating`) |
| `sandbox.started` | it is `running` and ready for exec and SSH (after create, start, resume or wake) |
| `sandbox.stopped` | it is `stopped` |
| `sandbox.suspended` | it is paused (`suspended`): by you, when idle, or by a plan limit |
| `sandbox.error` | it is in `error` |
| `sandbox.deleted` | it is `deleted` |
| `snapshot.created`, `snapshot.failed`, `snapshot.deleted` | a snapshot is ready, failed to upload, or is deleted |
| `webhook.test` | only from a test send |

Each body is `{"id":"evt_…","type":"sandbox.suspended","createdAt":"…","orgId":"org_…","data":{"sandbox":{"id":"m_…","name":"worker-1","metadata":{}},"previousState":"suspending","state":"suspended","reason":"idle","operationId":"op_…"}}`. `reason` is what moved it: `user`, `idle`, `archive`, `wake`, `system` (observed by the server, such as a crash), and others.

### Create an endpoint
```sh
instabox webhooks create https://example.com/hook --event sandbox.started --event sandbox.error
instabox webhooks ls
instabox webhooks test wh_...
instabox webhooks deliveries wh_...
```
No `--event` subscribes to every type. `create` and `rotate` print the signing secret (`whsec_…`) once. The URL must be public `https`; redirects are not followed. The org's owner or admin manages endpoints, signed in or with an API key of that org: `machines:read` lists and reads deliveries, `machines:write` creates, updates, rotates, tests and retries, `machines:delete` deletes. With `INSTABOX_API_KEY`, `--org` defaults to the key's org. The dashboard's Webhooks page does the same, with a delivery log. Over HTTP:
```sh
curl -X POST https://api.instabox.sh/v1/orgs/$ORG/webhooks -H "Authorization: Bearer $INSTABOX_API_KEY" \
  -H 'Content-Type: application/json' -d '{"url":"https://example.com/hook","events":["sandbox.started","sandbox.error"]}'
```
`GET /v1/orgs` lists your orgs; an API key sees only its own. The routes are under `/v1/orgs/{id}/webhooks` in the [OpenAPI document](https://api.instabox.sh/v1/openapi.json).

### Verify the signature
Requests follow [Standard Webhooks](https://www.standardwebhooks.com/), so its libraries verify them. Headers: `webhook-id` (the event ID, the same on every retry: dedupe on it), `webhook-timestamp` (Unix seconds) and `webhook-signature`: `v1,` and the base64 HMAC-SHA256 of `<webhook-id>.<webhook-timestamp>.<raw body>`, keyed with the base64-decoded part of the secret after `whsec_`. After a rotation it lists two signatures for 24 hours; accept either, comparing in constant time. Reject timestamps more than 5 minutes off.
```js
import crypto from 'node:crypto';
const key = Buffer.from(secret.slice('whsec_'.length), 'base64');
const want = crypto.createHmac('sha256', key).update(`${id}.${timestamp}.${rawBody}`).digest();
const ok = header.split(' ').some((s) => {
  const got = Buffer.from(s.startsWith('v1,') ? s.slice(3) : '', 'base64');
  return got.length === want.length && crypto.timingSafeEqual(got, want); // constant time
});
```

### Delivery
Answer 2xx within 10 seconds of connecting: reply first, then do the work. Other answers and timeouts are retried after 5 s, 5 min, 30 min, 2 h, 5 h, 10 h and 10 h, then the delivery fails; A delivery still pending 3 days after its event fails as expired. `instabox webhooks retry` sends a finished one again. Events for one endpoint can arrive out of order: order by `createdAt`. An endpoint that fails every attempt for 5 days is disabled, and the workspace's owner and admins get an email; `instabox webhooks update ID --enable` turns it back on. Deliveries are kept 30 days.

---

# API keys and SDK

https://instabox.sh/docs/keys-sdk.md

Drive machines from code: TypeScript, HTTP, or the CLI with a key.

Code uses an **API key** (`ibk_...`): the TypeScript SDK, plain HTTP, the CLI and SSH all accept one. Signing in with GitHub or Google is for people, to use the dashboard and to create keys.

### 1. Create a key
On **API keys** in the dashboard sidebar, choose **Create Key**. **Full access** suits the SDK; **Restricted** picks scopes:

| Scope | Allows |
|---|---|
| `machines:read` | list and get machines, operations, metrics and usage |
| `machines:write` | create, start, stop, pause, resume, set auto-pause and labels, exec and SSH |
| `machines:delete` | delete machines |
| `images:read`, `images:write`, `images:delete` | list, save and delete snapshots |

Write and delete include read. The SDK and CLI look names up with `images:read`, so give it to keys that create machines. The secret is shown once; revoking a key also ends its SSH certificates. Keys cannot create keys.
```
export INSTABOX_API_KEY=ibk_...
export INSTABOX_API_URL=https://api.instabox.sh
```

> A key with `machines:write` can select org Secrets for a sandbox and execute code there. That code can send selected Secrets to their allowed hosts. For a fresh sandbox that should receive credentials from neither store, pass `"vault": false, "secrets": []` to the creation API.

### 2. TypeScript SDK
```
npm install @insforge/instabox-sdk
```
It reads `INSTABOX_API_KEY` and `INSTABOX_API_URL`, or takes `{ apiKey, apiUrl }` as options.
```
import { Sandbox } from '@insforge/instabox-sdk'

const sbx = await Sandbox.create('universal', {   // a template, a snapshot name, or a snapshot ID
  metadata: { task: 'review' },
})
const r = await sbx.commands.run('uname -a')         // throws CommandExitError on a non-zero exit
console.log(r.stdout)
await sbx.files.write('/data/home/notes.txt', 'hello')
console.log(await sbx.files.read('/data/home/notes.txt'))

await sbx.pause()                                   // pause; memory is kept
const again = await Sandbox.connect(sbx.sandboxId)   // resumes it
await Sandbox.list({ metadata: { task: 'review' } })
await again.kill()                                  // delete
```
Also: `setAutoSuspend`, `setMetadata`, `stop`, `getInfo`, `sshCredentials`, `getMetrics` and `getUsage`, and `sbx.desktop` to watch and drive the desktop ([Desktop](https://instabox.sh/docs/desktop.md)). To copy a machine, save a snapshot with `createSnapshot` and pass its ID to `Sandbox.create`. Full reference: [SDK reference](https://instabox.sh/docs/sdk.md).

### 3. HTTP
Send the key as `X-API-Key` (or `Authorization: Bearer`). Lifecycle calls return an **operation**: poll it until `succeeded` or `failed` before the next change to that machine. They need an `Idempotency-Key` header (without one: `400`); reuse a key only to retry the same request.
```
H="X-API-Key: $INSTABOX_API_KEY"
curl -s -H "$H" -H "Idempotency-Key: $(uuidgen)" -H 'Content-Type: application/json' \
  -d '{"name": "box", "templateId": "herdr"}' "$INSTABOX_API_URL/v1/machines"
curl -s -H "$H" "$INSTABOX_API_URL/v1/operations/op_...?wait=25s"  # long poll, until "state": "succeeded"
curl -s -H "$H" -H 'Content-Type: application/json' \
  -d '{"cmd": "uname -a", "timeoutSeconds": 60}' "$INSTABOX_API_URL/v1/machines/m_.../exec"
curl -s -H "$H" -H 'Content-Type: application/json' \
  -d '{"argv": ["printf", "%s|", "a b", "$X"]}' "$INSTABOX_API_URL/v1/machines/m_.../exec"  # no shell: prints a b|$X|
curl -s -X DELETE -H "$H" -H "Idempotency-Key: $(uuidgen)" "$INSTABOX_API_URL/v1/machines/m_..."
```
`POST /v1/machines` takes `{}` (agent-browser, named `box-` and 8 random hex digits); an unknown `templateId` is `400` listing the templates your plan can create from, and a body field the API lacks is `400 unknown_field` (`"template"`: did you mean `"templateId"`?).
`exec` returns `stdout`, `stderr` and `exitCode` once the command exits (at most 10 minutes). Send `cmd` (a shell string, run with `bash -lc`) or `argv` (a program and its arguments, run with no shell), not both. It takes no Idempotency-Key: a retry runs the command again. When a disk of the machine is at least 90% full, or the command failed with `No space left on device`, the result carries a `diskWarning` (`mount`, `usedPct`, `level`, `noSpace`, `message`) naming the full disk and the fix (`instabox resize <box> --disk <GiB>` grows `/data`, live on a running machine); `instabox exec` prints it on stderr. The [API reference](https://instabox.sh/docs/api.md) explains each endpoint an API key calls.

### 4. CLI and SSH with a key
With `INSTABOX_API_KEY` set, the CLI needs no login:
```
curl -fsSL https://api.instabox.sh/install.sh | sh
instabox create --name box --template herdr
instabox exec box -- uname -a
instabox exec --background box -- 'npm run build'   # detached job: prints its ID
instabox jobs logs box <job> -f                     # follow it; exits with its code
instabox ssh box
instabox rm --yes box
instabox run -- uname -a   # one-shot: create, run, delete
instabox run --push . -- ls   # upload this directory (git-ignored files skipped) first
```
Over plain HTTP, `POST /v1/machines/{id}/connections` with your public key (and an `Idempotency-Key`) returns the certificate and host CA.

---

# CI with GitHub Actions

https://instabox.sh/docs/ci.md

Run tests in a machine per job, or keep a machine as a self-hosted runner, and which to pick.

Run your tests in instabox machines from GitHub Actions. Pick a path:

- **A machine per job**, for a clean machine on each run, or to have an agent set CI up: a GitHub-hosted job creates a machine, runs the tests in it and deletes it.
- **A self-hosted runner**, if you're out of GitHub Actions minutes or want to move existing jobs over: a machine you keep runs GitHub's runner and takes the jobs itself, with `runs-on: [self-hosted, instabox]`.

Both use the commands you use by hand.

### 1. A key for CI
Create a key for CI alone, so you can revoke it without breaking anything else, and store it as a repository secret:

```sh
instabox keys create --name github-ci --expires-in-days 90
gh secret set INSTABOX_API_KEY   # paste the ibk_... secret printed above
```

The default scopes already fit CI: `machines:read`, `machines:write` and `machines:delete` create, use and delete machines, and `images:read` starts them from a snapshot. The key can't save or delete snapshots, so do that signed in on your own computer, as below.

### 2. A machine per job

#### Prepare a saved snapshot (one time)
Install your toolchain and dependencies once and save the machine as a snapshot, so each CI machine starts with them in place:

```sh
instabox create --name ci-prep
instabox exec ci-prep --timeout 600 -- 'sudo apt-get update && sudo apt-get install -y postgresql-client'
instabox exec ci-prep --timeout 600 -- 'docker pull postgres:16'
instabox snapshot save ci-prep --name ci-base
instabox rm --yes ci-prep
```

Docker images you pull are saved too, with no container needed. A snapshot name is used once: to update `ci-base`, `instabox snapshot rm --yes ci-base` and run the steps again. The free plan keeps 5 snapshots; Pro and Team, any number. See [Snapshots](https://instabox.sh/docs/snapshots.md).

#### The workflow
`instabox run` creates a machine (`--from ci-base`: from the snapshot), uploads the checkout, runs the command, prints its output and deletes the machine. It exits with the command's code, so the job fails when the tests fail.

```yaml
name: tests
on:
  pull_request:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    timeout-minutes: 30
    env:
      INSTABOX_API_KEY: ${{ secrets.INSTABOX_API_KEY }}
    steps:
      - uses: actions/checkout@v4
      - name: Install the instabox CLI
        run: |
          curl -fsSL https://api.instabox.sh/install.sh | INSTABOX_INSTALL_DIR="$HOME/.local/bin" sh
          echo "$HOME/.local/bin" >> "$GITHUB_PATH"
      - name: Run the tests
        run: instabox run --from ci-base --push . --timeout 10m -e CI=1 -- 'npm ci && npm test'
```

| Part | Why |
|---|---|
| `INSTABOX_API_KEY` | The CLI signs in with it; no `instabox login` step. |
| `--from ci-base` | Starts with the toolchain and dependencies in place. Leave it out to start from the default template. |
| `--push .` | Uploads the checkout, skipping files git ignores (`node_modules`, build output). The machine needs no GitHub access. |
| `--timeout 10m` | Kills the command after 10 minutes (the most) and exits 124. |
| `-e CI=1` | Sets environment variables for the command; pass test secrets the same way, `-e DATABASE_URL="$DATABASE_URL"`. |
| Deleting | `run` deletes the machine when the command ends, fails or the job is cancelled. If the runner dies, the server deletes it by itself 10 minutes after `--timeout` runs out (5 without `--push`). |

Pull requests from forks get no repository secrets, so on them the job has no key and fails; run it on `push` and same-repository pull requests only, or make it skip when `INSTABOX_API_KEY` is empty.

#### Copy the test report back, or run longer than 10 minutes
Create the machine yourself, run the tests, copy the report out, and always delete the machine:

```yaml
      - name: Create a machine
        id: box
        run: |
          set -o pipefail
          id=$(instabox create --snapshot ci-base --name ci-$GITHUB_RUN_ID-$GITHUB_RUN_ATTEMPT --delete-after 1h --json | jq -er .id)
          echo "id=$id" >> "$GITHUB_OUTPUT"
      - name: Run the tests
        run: |
          set +e
          instabox push ${{ steps.box.outputs.id }} . repo
          instabox exec ${{ steps.box.outputs.id }} --cwd repo --timeout 600 -- 'npm ci && npm test'
          code=$?
          instabox pull ${{ steps.box.outputs.id }} repo/junit.xml ./junit.xml || true
          exit $code
      - name: Delete the machine
        if: always() && steps.box.outputs.id != ''
        run: instabox rm --yes ${{ steps.box.outputs.id }}
```

- `set -o pipefail` and `jq -e` fail the step when `create` fails, so the delete step never runs on an empty ID. `set +e` and `exit $code` copy the report out, then fail the job with the tests' exit code.
- `--delete-after 1h` caps the machine's life (1m-24h; keep it above the job's `timeout-minutes`): if the runner dies before the last step, the server deletes it then, where a plain `create` would leave it paused, counting against your machine limit.
- A machine from `create` still pauses after 30 idle minutes, and a job that uses little CPU (one waiting on the network, say) counts as idle; on a paid plan, add `--auto-suspend 0` to `create`.
- For a suite longer than 10 minutes, start it as a background job and follow its log, which exits with the job's code: `job=$(instabox exec --background <id> --cwd repo --json -- 'npm ci && npm test' | jq -er .jobId)`, then `instabox jobs logs <id> "$job" -f`.

#### Many jobs at once: start limits
Each job starts one machine, and every create, start, resume and wake counts as a start.

| Plan | Starts per minute | Machines |
|---|---|---|
| Free | 3 | 1 in total, in any state |
| Pro | 10 | 500, 100 running at once |
| Team | 100 | 500 running at once |

- A start over the limit fails with `rate_limited` and starts nothing. A matrix of 30 jobs on Pro needs 3 minutes of starts, so cap it with `strategy.max-parallel: 10`. That caps the jobs running at once, so short jobs can still start more than 10 machines in a minute; `rate_limited` is retryable, so rerun the failed jobs.
- To fail at once when no host has room, add `--fail-fast`: `run` then exits 75; retry the job later.

All limits: [Limits](https://instabox.sh/docs/limits.md).

#### Cost
Runtime is billed by the second, only while a machine runs, and a deleted machine costs nothing more. A 4 vCPU / 8 GiB machine is $0.034 an hour, so a 5-minute run is about $0.003, and paid plans pay it only beyond their monthly credits. The free plan pays nothing. See [Pricing](https://instabox.sh/docs/pricing.md).

### 3. A self-hosted runner
One machine runs [GitHub's runner](https://docs.github.com/actions/hosting-your-own-runners) as a service, and your workflows send jobs to it with `runs-on: [self-hosted, instabox]`. The jobs get the machine's 4 vCPUs, 8 GB, Docker and whatever you installed, and the next job starts warm. Create it with a registration token (you need admin rights on the repository) and the setup file at https://instabox.sh/ci/github-runner.sh:

```sh
token=$(gh api -X POST repos/OWNER/REPO/actions/runners/registration-token --jq .token)
curl -fsSL https://instabox.sh/ci/github-runner.sh -o github-runner.sh
{ echo "RUNNER_URL=https://github.com/OWNER/REPO RUNNER_TOKEN=$token"; cat github-runner.sh; } \
  | instabox create --name gh-runner --setup-file -
```

For every repository of an organization, use `orgs/ORG/actions/runners/registration-token` and `RUNNER_URL=https://github.com/ORG`. `RUNNER_LABELS` (default `instabox`), `RUNNER_NAME` (default the machine's hostname), and `RUNNER_VERSION` with its `RUNNER_SHA256` (default: a tested release, checked against its SHA-256; the runner then updates itself) go on the same line. Then:

```yaml
jobs:
  test:
    runs-on: [self-hosted, instabox]
    steps:
      - uses: actions/checkout@v4
      - run: npm ci && npm test
```

- **Pausing:** a runner waiting for jobs counts as idle, and so does a job that uses little CPU (one waiting on the network, say), so a machine can pause in the middle of a job. On a paid plan, keep it running: add `--auto-suspend 0 --max-run-minutes -1` to `create`. On the free plan it pauses after 30 idle minutes, even during such a job, and pauses after 8 hours of running, after which nothing can wake it for about 10 minutes; a paused runner takes no jobs (a queued job waits for it), so wake it first from a GitHub-hosted job (`wake` resumes only a machine that paused itself; one you paused needs `instabox resume`):

```yaml
jobs:
  wake:
    runs-on: ubuntu-latest
    steps:
      - run: curl -fsSL https://api.instabox.sh/install.sh | INSTABOX_INSTALL_DIR="$HOME/.local/bin" sh && ~/.local/bin/instabox wake gh-runner
        env:
          INSTABOX_API_KEY: ${{ secrets.INSTABOX_API_KEY }}
  test:
    needs: wake
    runs-on: [self-hosted, instabox]
    # ...
```

- **Security:** a self-hosted runner runs whatever code the workflow checks out, and jobs share the machine. Don't attach one to a public repository whose fork pull requests run workflows without approval. The runner's credentials are in `~/actions-runner` (the setup file deletes its own copy, `/tmp/instabox-setup.sh`, which held the one-hour registration token): don't share the machine or snapshot it for others.
- **Removing it:** `instabox rm --yes gh-runner`, then delete the offline runner under **Settings → Actions → Runners**.

---

# SDK reference

https://instabox.sh/docs/sdk.md

Every class, method and option of @insforge/instabox-sdk.

Version 0.5.0 of `@insforge/instabox-sdk`. For a walk through the common calls, start with [Integrate with the SDK](https://instabox.sh/docs/integrate.md).

### Install and authenticate
```
npm install @insforge/instabox-sdk
export INSTABOX_API_KEY=ibk_...
# optional; the default is https://api.instabox.sh
export INSTABOX_API_URL=https://api.instabox.sh
```
Every static call (`create`, `connect`, `list`, `kill`, the snapshot calls and the metrics and usage calls) also takes the key and URL as options, which win over the environment. A `Sandbox` object keeps its connection, so its own methods take no key.
```
import { Sandbox } from '@insforge/instabox-sdk'

const sbx = await Sandbox.create('agent-browser', {
  apiKey: process.env.INSTABOX_API_KEY,
  apiUrl: 'https://api.instabox.sh',
})
```
With no key from either, the call throws `InstaboxAuthError` with code `missing_api_key` (status 0) before any request. The key is sent as the `X-API-Key` header.

These connection options (`ConnectionOptions`) apply to every static call:

| Option | Type | Default |
|---|---|---|
| `apiKey` | `string` | env `INSTABOX_API_KEY` |
| `apiUrl` | `string` | env `INSTABOX_API_URL`, else `https://api.instabox.sh` |
| `requestTimeoutMs` | `number` | 60 000 per HTTP request; a command gets its own timeout plus 30 000 |
| `operationTimeoutMs` | `number` | 600 000: the wait for create, pause, resume and kill |
| `fetch` | `typeof fetch` | the global `fetch` (Node 18+, Bun, Deno) |
| `pollIntervalMs` | `number` | 250: first delay of operation polling, grows 1.5x to 1 s |
| `retryDelayMs` | `number` | 250: first delay between retries |

Scopes a key needs:

| Scope | Allows |
|---|---|
| `machines:read` | `Sandbox.list`, `getInfo`, `isRunning`, `getMetrics`, `getUsage`, `Sandbox.usage` |
| `machines:write` | `create`, `connect` (resume), `pause`, `resume`, `stop`, `setAutoSuspend`, `setMetadata`, `commands`, `files`, `sshCredentials` |
| `machines:delete` | `kill` |
| `images:read` | Resolve private snapshot names, `listSnapshots`, `getSnapshot` |
| `images:write` | `createSnapshot` |
| `images:delete` | `deleteSnapshot` |

`:write` and `:delete` include `:read`. Creating from a snapshot name also needs `images:read`. A call outside the key's scopes throws `InstaboxAuthError` (`403 missing_scope`).

### Sandbox.create
```
Sandbox.create(opts?: SandboxOpts): Promise<Sandbox>
Sandbox.create(template: string, opts?: SandboxOpts): Promise<Sandbox>
```
`template` is a template ID (`universal`), a private snapshot name or a snapshot ID (`sn_...`). Template IDs take precedence over snapshot names. The default is `agent-browser` (`DEFAULT_TEMPLATE`), or `universal` (`FALLBACK_TEMPLATE`) on a server without it. It resolves once the machine runs; a snapshot that is still being saved is waited for, up to `operationTimeoutMs`.

`SandboxOpts` is the connection options plus:

| Option | Type | Default |
|---|---|---|
| `name` | `string` | `sbx-<random>`; lowercase letters, digits and `-` |
| `metadata` | `Record<string, string>` | none; labels to filter `Sandbox.list` on |
| `envs` | `Record<string, string>` | none; added to every `commands.run` of this object (client side) |
| `archiveMs` | `number` | none; stop and archive after this long |
| `autoSuspendMs` | `number` | 30 minutes; pause after this much idle time. A paid plan takes 5-30 minutes, rounded up to 5, 10, 15, 20, 25 or 30 (below 5 or above 30 is refused), `0` never. The free plan always pauses after 30 idle minutes; a server from 2026-10-25 refuses another value (403) instead of ignoring it |
| `vcpus` | `number` | the template's |
| `memMiB` | `number` | the template's |
| `diskGiB` | `number` | the size's; the disk (`/data`), in GiB, sent as the API's `persistentDiskGiB` |
| `vault` | `boolean` | `false` disables only personal Vault delivery; org Secret selections are independent |

Times are sent as whole seconds. On api.instabox.sh a sandbox is 4 vCPUs and 8 GiB unless `vcpus` and `memMiB` name another size of your plan (Pro: 2/4 and 8/16; Team: 2/4 up to 32/64; `GET /v1/orgs` lists each workspace's as `allowedSpecs`). Any other size is refused with `400 spec_not_allowed`, and so is a `diskGiB` other than the disk the size comes with: leave it out. A paid sandbox's disk grows later with `PATCH /v1/machines/{id}` (see [Disk sizes](https://instabox.sh/docs/limits.md)). In a REST body the field is `persistentDiskGiB`; `diskGiB` there is `400 unknown_field`. The free plan creates from agent-browser only (`403 template_not_allowed`); a sandbox from a snapshot is not limited.

### Connect, list and kill
```
Sandbox.connect(sandboxId: string, opts?: SandboxConnectOpts)
  : Promise<Sandbox>
Sandbox.list(opts?: SandboxListOpts): Promise<SandboxInfo[]>
Sandbox.kill(sandboxId: string, opts?: ConnectionOptions)
  : Promise<boolean>
```
- `connect` attaches to an existing machine and resumes it if it is paused or stopped. `resume: false` attaches without waking it. `envs` works as in `create`.
- `list` returns every page of your machines. `metadata` keeps those with every given key and value.
- `kill` deletes a machine and its disks. It returns `false` if the machine did not exist.

### Snapshot calls
```
Sandbox.listSnapshots(opts?: ConnectionOptions): Promise<Snapshot[]>
Sandbox.getSnapshot(snapshotId: string, opts?: ConnectionOptions)
  : Promise<Snapshot>
Sandbox.deleteSnapshot(snapshotId: string, opts?: ConnectionOptions)
  : Promise<boolean>
```
`listSnapshots` returns your private snapshots. `deleteSnapshot` returns `false` if the snapshot was already gone. Save one with `sbx.createSnapshot`.

To copy a sandbox, save a snapshot and create from it:
```
const snap = await sbx.createSnapshot({ name: 'my-setup' })
const copy = await Sandbox.create(snap.id, { vault: false })
```
A copy uses its creation request's selections, not the source sandbox's grants. Omitting `secrets` does not enroll the copy in Secrets. `vault: false` disables only Vault delivery. To explicitly select Secrets, use the CLI or HTTP API.

### The Sandbox object
| Member | Returns | What it does |
|---|---|---|
| `sandboxId` | `string` | The machine ID, `m_...` |
| `getInfo()` | `Promise<SandboxInfo>` | Fresh state from the server |
| `isRunning()` | `Promise<boolean>` | True if `state` is `running` |
| `pause()` | `Promise<void>` | Saves memory and suspends it |
| `resume()` | `Promise<void>` | Resumes a paused machine, or starts a stopped one |
| `stop()` | `Promise<void>` | Shuts it down; processes end, `/data` is kept |
| `setAutoSuspend(idleMs: number)` | `Promise<void>` | Idle pause; a paid plan takes 5-30 minutes, rounded up to a 5-minute step (below 5 or above 30 is refused), and `0` turns it off, the free plan keeps 30 minutes and refuses another value. Kept across pause and resume |
| `setMetadata(metadata: Record<string, string>)` | `Promise<void>` | Replaces the labels; `{}` clears them |
| `createSnapshot(opts: CreateSnapshotOpts)` | `Promise<Snapshot>` | Saves its disks as a private snapshot |
| `getMetrics(opts?: SandboxMetricsOpts)` | `Promise<SandboxMetrics[]>` | CPU and memory samples, oldest first |
| `getUsage(opts?: SandboxUsageOpts)` | `Promise<SandboxUsage>` | What it used over a window |
| `sshCredentials(publicKey: string, opts?: { ttlSeconds?: number })` | `Promise<SshCredentials>` | A short-lived SSH certificate for `publicKey` |
| `kill()` | `Promise<boolean>` | Deletes it and its disks; `false` if already gone |
| `commands` | `Commands` | Run shell commands |
| `files` | `Files` | Read and write files |
| `desktop` | `Desktop` | See and control the desktop |

Lifecycle calls (`create`, `connect`, `pause`, `resume`, `stop`, `kill`) wait for the server's operation to finish, up to `operationTimeoutMs`.

`getInfo()` returns a `SandboxInfo`: `sandboxId`, `templateId`, `snapshotId?`, `name`, `metadata`, `vault`, `startedAt`, `archiveAt?`, `autoSuspendMs?`, `state` and `machine` (the raw API object). `state` is one of:
```
creating  starting  running  stopping  stopped
suspending  suspended  resuming  deleting  deleted  error
```
A paused machine is `suspended`. The `vault` field describes personal Vault delivery. Vault inspection and push endpoints remain available independently of `GET /v1/machines/{id}/secrets`, which returns org Secret selections and delivery status. Use the [Secret CLI or HTTP API](https://instabox.sh/docs/secrets.md) to manage those selections.

`CreateSnapshotOpts`: `name` (required), `description`, and `rootOnly` to save only the root disk. From a running machine the snapshot comes back with `status: 'pending'` and turns `ready` once saved.

`SshCredentials`: `host`, `port`, `username` (the machine ID), `certificate` (save it as `<key>-cert.pub`), `knownHostsLine`, `expiresAt` and `connectionId`. The machine must be running. `ttlSeconds` is 1 to 86 400; the default is 1 hour. See [SSH](https://instabox.sh/docs/ssh.md).

### sbx.commands
```
run(cmd: string, opts?: CommandOptions & { background?: false })
  : Promise<CommandResult>
run(cmd: string, opts: CommandOptions & { background: true })
  : Promise<CommandHandle>
```
| Option | Type | Default |
|---|---|---|
| `cwd` | `string` | the server's: HOME, `/data/home` |
| `envs` | `Record<string, string>` | none; merged over the `envs` given to `Sandbox.create` |
| `timeoutMs` | `number` | the server's; sent as whole seconds, at most 600 000 |
| `stdin` | `string` | none; at most 1 MiB of UTF-8 (`MAX_STDIN_BYTES`) |
| `onStdout` | `(data: string) => unknown` | called once with the whole stdout when the command ends |
| `onStderr` | `(data: string) => unknown` | the same, for stderr |
| `background` | `boolean` | `false`; `true` starts it detached and returns at once |

The result (`CommandResult`) is `{ stdout, stderr, exitCode, timedOut, truncated, error? }`. Each output stream is cut at 1 MiB, and `truncated` says so. Output is not streamed.

A non-zero exit throws `CommandExitError`, which carries the same fields. A command that runs past `timeoutMs` throws it with `timedOut: true` and exit code 124.
```
import { CommandExitError } from '@insforge/instabox-sdk'

try {
  await sbx.commands.run('exit 3')
} catch (e) {
  if (e instanceof CommandExitError) console.log(e.exitCode, e.stderr)
}
```
With `background: true`, `run` returns a `CommandHandle`: `pid` (the shell, which leads the process group) and `kill()`, which sends SIGTERM to everything it started and returns `false` if all had exited.
```
const server = await sbx.commands.run('node server.js', {
  background: true,
})
await server.kill()
```
`exec(cmd, opts?)` takes `cwd`, `envs`, `timeoutMs` and `stdin` and returns the `CommandResult` without throwing on a non-zero exit. It is marked internal, so prefer `run`. Commands are never retried.

### sbx.files
```
read(path: string, opts?: { format?: 'text' }): Promise<string>
read(path: string, opts: { format: 'bytes' }): Promise<Uint8Array>
write(path: string, data: string | Uint8Array): Promise<WriteInfo>
list(path: string): Promise<EntryInfo[]>
remove(path: string): Promise<void>
exists(path: string): Promise<boolean>
```
- `read` returns UTF-8 text, or bytes with `{ format: 'bytes' }`.
- `write` creates parent directories and replaces the file atomically. It returns `{ path }`. Writing to a directory throws `is_a_directory`.
- `list` returns `{ name, path, type }` entries, `type` being `'file'` or `'dir'`. It is not recursive.
- `remove` deletes a file or a directory, recursively. A missing path is fine.

Files travel through the command channel as base64, so they need the same scope as commands. Each read or write is at most 10 MiB (`MAX_FILE_BYTES`). Relative paths start at HOME, `/data/home`, on the persistent disk.

### sbx.desktop
```
start(opts?: { width?: number; height?: number })
  : Promise<DesktopStatus>
status(): Promise<DesktopStatus>
screenshot(): Promise<Uint8Array>
click(x: number, y: number,
  opts?: { button?: MouseButton; double?: boolean }): Promise<void>
move(x: number, y: number): Promise<void>
drag(from: [number, number], to: [number, number]): Promise<void>
scroll(opts: { direction: ScrollDirection; amount?: number })
  : Promise<void>
type(text: string, opts?: { delayMs?: number }): Promise<void>
press(keys: string | string[]): Promise<void>
open(url: string): Promise<void>
cursorPosition(): Promise<{ x: number; y: number }>
streamUrl(opts?: { viewOnly?: boolean; ttlSeconds?: number })
  : Promise<DesktopStream>
revokeStreamUrls(): Promise<void>
```
- `start` resolves once the desktop runs and leaves a running one as it is. On a template without the desktop it installs it first, about half a minute, once. Screen: 800 to 2560 by 600 to 1600, default 1280 x 800.
- `status` returns `DesktopStatus`: `installed`, `running`, and `width` and `height` while running.
- `screenshot` returns a PNG of the whole screen.
- `click` uses the left button unless `button` is `'right'` or `'middle'`; `double` clicks twice. Coordinates are pixels from the top left.
- `drag` holds the left button. `scroll` turns the wheel at the pointer, `amount` notches (default 3), `direction` `'up'`, `'down'`, `'left'` or `'right'`.
- `type` types the text as is, quotes, newlines and Unicode included, into the focused window.
- `press` takes a key (`'Enter'`, `'a'`, `'F5'`) or a chord (`['ctrl', 'l']`).
- `open` opens an http or https URL in the desktop's browser.

Input and screenshots run commands in the machine, so a failing one throws `CommandExitError`. The desktop runs on X display `:1` (`DESKTOP_DISPLAY`).

**The stream link.** `streamUrl` returns `{ url, expiresAt }`: a page that shows the desktop full-screen, to open or put in an `<iframe>`. Anyone with the link can connect, no instabox account needed, until `expiresAt` (`ttlSeconds` 60 to 86 400, default 3 600). It is view-only unless `viewOnly: false`. Expiry stops new connections only; `revokeStreamUrls()` ends every link of the machine and disconnects open viewers within a few seconds. See [Desktop](https://instabox.sh/docs/desktop.md).

### Metrics and usage
```
sbx.getMetrics(opts?: SandboxMetricsOpts): Promise<SandboxMetrics[]>
Sandbox.getMetrics(sandboxId: string,
  opts?: SandboxMetricsOpts & ConnectionOptions)
  : Promise<SandboxMetrics[]>
sbx.getUsage(opts?: SandboxUsageOpts): Promise<SandboxUsage>
Sandbox.getUsage(sandboxId: string,
  opts?: SandboxUsageOpts & ConnectionOptions)
  : Promise<SandboxUsage>
Sandbox.usage(opts?: ConnectionOptions): Promise<Usage>
```
All of them need `machines:read`; `Sandbox.usage` also works with `images:read`.
```
// the last 15 minutes of CPU and memory
const samples = await sbx.getMetrics({
  since: new Date(Date.now() - 15 * 60_000),
})
// what it used since the start of October (UTC)
const usage = await Sandbox.getUsage(sbx.sandboxId, {
  from: new Date('2026-10-01T00:00:00Z'),
})
console.log(usage.runningSeconds, usage.vcpuSeconds)
```

**Metrics.** `getMetrics` returns one sample per 30 s, oldest first, measured on the host. `since` (a `Date`) is the start of the window: by default 5 minutes ago, at most 24 h back. There are samples only for the times in the window the machine ran, so the list is empty while it is not running. The last sample of a running machine is its host's latest report (at most about 30 s old, CPU and memory only), so a new machine shows its first sample within about 30 s. The CLI prints the same: `instabox metrics <id-or-name> [--json]`. Each `SandboxMetrics`:

| Field | Type | What |
|---|---|---|
| `timestamp` | `Date` | When the sample was taken |
| `cpuUsedPct` | `number` | CPU time over the machine's vCPUs, 0 to 100 |
| `cpuCount` | `number` | vCPUs |
| `memUsed` | `number` | Guest memory touched, in bytes |
| `memTotal` | `number` | Memory size, in bytes |
| `diskTotal` | `number` | Disk (`/data`) size, in bytes |

On the latest sample of a running machine, `diskUsed` is the bytes used on `/data`, read inside the machine (the last read, refreshed in the background at most once a minute and at most 10 minutes old). The REST route `GET /v1/machines/{id}/disk` and `instabox disk <box>` show `/data` and `/` (used, free, size, inodes) with a level (`ok` below 80%, `high` from 80%, `critical` from 90%, `full` at 100%) and a warning that says how to free or add space.

**Usage of a machine.** `getUsage` returns what a machine used between `from` and `to` (both `Date`s), for billing your own customers. The default range is the current UTC month: `from` is the start of the month, `to` is now, and `to` may be at most 366 days after `from`. A `SandboxUsage`:

| Field | Type | What |
|---|---|---|
| `from`, `to` | `Date` | The window |
| `runningSeconds` | `number` | Seconds running, not paused or stopped |
| `vcpuSeconds` | `number` | vCPUs times running seconds |
| `memGiBSeconds` | `number` | Memory GiB times running seconds |
| `diskGiBSeconds` | `number` | Disk (`/data`) size times the seconds it existed in the window, paused or stopped included |

A deleted machine's usage stays readable by its account, by ID. Running time is recorded from the deploy of 2026-10-14; earlier time is not counted.

**Usage of the account.** `Sandbox.usage()` returns your counts, stored bytes and limits (`GET /v1/usage`). Bytes are measured about hourly.
```
interface Usage {
  computedAt: string | null // when bytes were measured
  logicalBytes: number
  storedBytes: number
  exclusiveBytes: number // deprecated: always 0
  machines: number
  snapshots: number
  limits: UsageLimits // maxMachines, maxSnapshots, maxStoredGiB,
                      // machineSpec?, liveSnapshots?, vault?
  storage?: UsageStorage // storedBytes by machine
}
```
`storage` has `machines` (each with `id`, `name`, `state`, `sizeBytes`, `diskBytes`, `snapshots` and `snapshotBytes`), `deletedMachineSnapshots` and `deletedMachineSnapshotBytes`. `computedAt` is null and `storage` absent before your first measurement.

### Errors
| Class | When |
|---|---|
| `InstaboxError` | Base class of every error. Fields: `status`, `code`, `message`, `requestId`, `retryable`, `operationId` |
| `InstaboxAuthError` | 401 or 403: a bad or revoked key, or a missing scope. No key at all: `missing_api_key`, status 0 |
| `InstaboxQuotaError` | 429, such as `quota_exceeded` |
| `InstaboxTimeoutError` | A request or an operation did not finish in time |
| `CommandExitError` | A command exited non-zero. Also has `stdout`, `stderr`, `exitCode`, `timedOut`, `truncated`, `error` |

`status` is 0 for errors that did not come from an HTTP response. A failed operation (for example `no_capacity` while creating) throws `InstaboxError` with the operation's `code` and `operationId`.

| Code | Meaning |
|---|---|
| `missing_api_key` | No key in the options or the environment |
| `missing_scope` | The key lacks a scope the call needs (403; older servers: `insufficient_scope`) |
| `missing_key`, `malformed_key`, `invalid_key`, `expired_key`, `revoked_key` | The key was not sent, is not a key, does not exist, expired or was revoked (401) |
| `not_found` | No such machine or snapshot |
| `operation_conflict` | Another operation runs on the machine (409); `operationId` names it |
| `quota_exceeded` | An account limit was reached (429) |
| `spec_not_allowed` | A size your plan does not offer, a disk size at create, or growing a free sandbox's disks (400) |
| `template_not_allowed` | A template your plan does not offer: the free plan creates from agent-browser only (403) |
| `is_a_directory` | `files.write` to a directory |
| `request_timeout`, `operation_timeout` | A request or an operation took too long |
| `network_error` | The request did not reach the API |

Reads, and changes (which carry an `Idempotency-Key`), are retried up to 3 times with backoff on 502, 503, 504 and network errors.

### Types
| Type | What |
|---|---|
| `ConnectionOptions` | `apiKey`, `apiUrl` and the timeouts every static call takes |
| `SandboxOpts`, `SandboxConnectOpts`, `SandboxListOpts` | Options of `create`, `connect`, `list` |
| `SandboxInfo` | What `getInfo` and `list` return |
| `Machine`, `MachineSpec`, `MachineState` | The raw machine from the API, its size, its state |
| `CreateSnapshotOpts`, `Snapshot` | Snapshot options, a saved snapshot |
| `SandboxMetrics`, `SandboxMetricsOpts` | `getMetrics` samples and options |
| `SandboxUsage`, `SandboxUsageOpts` | `getUsage` result and options |
| `Usage`, `UsageLimits`, `UsageStorage`, `UsageMachineStorage` | What `Sandbox.usage` returns |
| `SshCredentials` | What `sshCredentials` returns |
| `CommandOptions`, `CommandResult`, `CommandHandle` | `commands.run` options and results |
| `EntryInfo`, `WriteInfo` | `files.list` entries, `files.write` result |
| `DesktopStatus`, `DesktopStream` | `desktop.status` and `desktop.streamUrl` results |
| `MouseButton`, `ScrollDirection` | `'left'`, `'right'`, `'middle'`; `'up'`, `'down'`, `'left'`, `'right'` |
| `Template`, `TemplateRef`, `Operation`, `ApiError` | API objects |

Constants: `DEFAULT_API_URL`, `DEFAULT_TEMPLATE`, `FALLBACK_TEMPLATE`, `MAX_FILE_BYTES` (10 MiB), `MAX_STDIN_BYTES` (1 MiB), `DESKTOP_DISPLAY`.

---

# CLI reference

https://instabox.sh/docs/cli.md

Every command. Add --help to any of them for the details.

### Auth
```
login [--provider github|google]   sign in with a device code
logout                             revoke and forget stored credentials
whoami                             show the signed-in user
```

### Machines
```
templates [--json]
ls [--meta K=V ...] [--json]          --meta: only machines with that metadata (AND)
create --name N [--template T | --snapshot S]
       [--auto-suspend 10m|0] [--delete-after 1h] [--meta K=V ...] [--no-wait] [--fail-fast] [--setup-file PATH|-] [--wait-setup] [--json]
                                      --fail-fast: when no host has room, fail at once and create nothing;
                                      with --fail-fast, create and run exit 75 when no host has room (retry later, or another size or template)
                                      --setup-file: run a script (at most 64 KB) once it runs;
                                      a failed script exits with its code and keeps the machine;
                                      get --json shows metadata.setupStatus, setupExitCode, setupLog
auto-suspend <id-or-name> <duration>|0   pause it once idle that long; 0 turns it off
get <id-or-name> [--json]
rename <id-or-name> <new-name>        in place, in any state: the ID, port URLs and SSH certificate stay;
                                      renames its Host block in ~/.ssh/config too
exec <id-or-name> [--cwd D] [--env K=V ...] [--timeout S] [--stdin] [--json] -- <cmd...>   run one command; exits with its code;
                                      one argument is a shell string ('a | b'), several run as that exact argv
                                      (--json: {stdout, stderr, exitCode, signal, timedOut, truncated, invalidUtf8, durationMs});
                                      exits 65 when the command exited 0 but its output was binary (copy files with pull or cp)
run [--template T | --from SNAPSHOT] [--name N] [--push DIR] [--cwd D] [-e K=V ...] [--timeout 60s] [--keep] [--fail-fast] [--setup-file PATH|-] [--json] -- <cmd...>
                                      one-shot: create a machine, run the command, delete the machine
                                      (also on error or Ctrl-C); exits with its code (124: timed out);
                                      run's own failures: 75 --fail-fast and no room, 125 API, network, create, upload or cleanup error, 130 interrupted;
                                      --push: upload DIR's unignored files into the working directory first;
                                      a killed CLI's machine is deleted by the server at its deleteAt, 5 minutes after --timeout
                                      (10 with --push); a failed cleanup delete is retried 5 times with backoff;
                                      --keep keeps it and prints its name to stderr (not when the create failed)
files <id-or-name> [PATH] [--json]   list a live directory or print a text file (as root)
push <id-or-name> LOCAL [REMOTE] [-p] [--all]   copy a file or directory in (default: HOME); a file streams up to 5 GiB;
                                      in a git repo, tracked files only (--all: untracked too); -p creates REMOTE's parents
pull <id-or-name> REMOTE [LOCAL]      copy a file or directory out (default: the current directory); a file streams, any size
cp [-r] [-p] SRC DST                  scp-style: cp ./x.tgz box:/data/home/x.tgz, cp box:/data/home/x.tgz .
start|stop|suspend|resume|rm <id-or-name> [--no-wait]   suspend: pause
restart <id-or-name> [--timeout 60s] [--json]   power-cycle (recover works too): stop, then start;
                                      disks kept; a guest not shut down by --timeout is killed
rm <id-or-name> --yes                 rm and the other rm commands ask y/N first; --yes (-y, --force) skips it, needed off a terminal
usage [--json]                        your machine and snapshot counts, and limits
```

### Snapshots
```
snapshot save <id-or-name> --name N [--description D] [--root-only]   --root-only: installed software, not home and workspace
snapshot ls [--json]
snapshot files <id-or-name> [PATH] [--json]   list a directory of its installed files or print a text file
snapshot rm <id-or-name> [--yes]
fork <id-or-name> [--name N] [--count N] [--keep-snapshot] [--json]
                                      snapshot + create --count (1-5) machines from it, then delete the snapshot
```

### SSH
```
ssh <id-or-name> [-- ssh args or command]
ssh-config <id-or-name>   print a ~/.ssh/config Host block
ssh-cert <id-or-name>     refresh the SSH certificate only
ssh-token <id-or-name> [--ttl 7d] [--mosh] [--json]   print a plain ssh (or mosh) command (no CLI or key needed)
ssh-token --revoke <id-or-name>              revoke the machine's ssh commands
mosh <id-or-name> [-- command]               like ssh, with mosh (needs mosh installed)
port-forward <id-or-name> [LOCAL:]REMOTE [...] [--address A]   forward local ports over SSH until Ctrl-C (forward works too)
```

### Public ports
```
port publish <id-or-name> <port> [--name NAME] [--json]
                                      give a port a public URL until you unpublish it
port ls [<id-or-name>]                list public ports of one or all machines
port unpublish <id-or-name> <port>    remove the URL and close its connections
port setup <id-or-name>               install the instabox-port command in the machine
```

### Orca
```
orca connect <id-or-name> [--scope runtime|mobile]   print a one-time Orca connection (JSON)
```

### Secrets
```
secrets set NAME [--host HOST] [--org ORG]    read a value from stdin or a hidden prompt
secrets import FILE [--host HOST] [--org ORG] atomic import; use - for stdin
secrets ls [--org ORG] [--json]               metadata only
secrets rm NAME [--org ORG] [--yes]
secrets show <id-or-name>                     selection and delivery status
secrets select <id-or-name> --secrets all|none|NAMES
secrets push <id-or-name>                     refresh delivery on a running machine
create ... [--secrets all|none|NAMES]
```
`secret` aliases `secrets`. Org commands default to your personal org (with `INSTABOX_API_KEY`, the key's org). Setting, importing and removing values require the org owner or admin: a signed-in session or a workspace's `workspace:admin` key in `INSTABOX_API_KEY`. `--host` can be repeated for a Secret used with several hosts; without it, every public HTTPS destination is allowed. Names in selection flags can be comma-separated or a JSON array. `--no-vault` disables only personal Vault delivery. To disable both stores on a fresh sandbox, also pass `--secrets none`.

### Webhooks
```
webhooks create URL [--event TYPE ...] [--description D] [--disabled] [--org ORG]   prints the secret once
webhooks ls | get ID | update ID [--url U] [--event T ...] [--enable|--disable] | rm ID
webhooks rotate ID | test ID | deliveries ID [--limit N] | retry ID DELIVERY | events
```
`webhook` aliases `webhooks`. Org commands default to your personal org (with `INSTABOX_API_KEY`, the key's org). See [Webhooks](https://instabox.sh/docs/webhooks.md) for the events and signature.

### Vault
Vault remains available for personal env and file delivery, with metadata selectors. Use `set`, `set-file`, `import`, `ls`, `rm`, `show` and `push`. Org Secrets is independent; `--no-vault` does not clear Secret selections. Export recovers items retained by an earlier explicit migration and contains real values; keep the output private.
```
vault set NAME                            read an env value from stdin or a hidden prompt
vault set-file PATH                       read file contents from stdin
vault import FILE                         import a .env file
vault ls [--json]
vault rm NAME [--yes]
vault show <id-or-name>                    inspect matching items and last delivery
vault push <id-or-name>                    refresh Vault delivery
vault export NAME --out recovered.json    create a new private file; never print the value
```
The CLI warns about a future Vault retirement, but these commands remain supported. Export is limited to retained migration items; regular reads return metadata only.

### API keys
```
keys create --name N [--scope S ...] [--expires-in-days N]   prints the secret once
keys ls [--json]
keys rm <key-id> [--yes]
```
With `INSTABOX_API_KEY=ibk_...` (and optionally `INSTABOX_API_URL`) set, every other command uses the key instead of a sign-in.

### Output
`--json` works on every command (each command's `-h` lists it); `-o json`, `--output json` and `--format json` are the same. `ssh`, `mosh` and `port-forward` are interactive and refuse it with the JSON error code `json_unsupported` (use `exec --json`). With JSON output a failure prints `{"error":{"code","message",...}}` on stdout instead of text on stderr and still exits non-zero (2 for usage errors, code `usage`); API errors keep the server's `code`, `status` and `requestId`. When stdout is not a terminal (a pipe or a file), the list and status commands print JSON without it: `ls`, `get`, `templates`, `usage`, `snapshot ls`, `port ls`, `keys ls`, `secrets ls`, `vault ls` and `workspace ls|get|members|invites`. `INSTABOX_NO_AUTO_JSON=1` or `--output table` keeps the table. Every other command (`exec`, `ssh`, `files`, `create`, ...) prints the same output piped or not.

### The CLI itself
```
version                   print the CLI version
update                    replace this CLI with the server's current build (self-update works too)
completion bash|zsh|fish|powershell   print a tab-completion script for commands, flags and machine names
```
`update` downloads the build `install.sh` installs, checks it against the server's SHA256SUMS and swaps it in place; it says "already up to date" when the CLI already is that build. To complete as you type, add `eval "$(instabox completion bash)"` to `~/.bashrc` or `eval "$(instabox completion zsh)"` to `~/.zshrc` (`instabox completion help` covers fish and PowerShell). Machine names come from your machine list, which never wakes a machine.

### Global flags
```
--server URL              API server (env INSTABOX_SERVER or INSTABOX_API_URL)
--ca-cert FILE            extra CA certificate for the server (env INSTABOX_CA_CERT)
--insecure-skip-verify    do not verify the server certificate (development only)
```

---

# Pricing

https://instabox.sh/docs/pricing.md

Plans, what each includes, and the unit prices of usage.

The numbers on the [pricing page](https://instabox.sh/pricing). All prices are in USD.

### Plans

**Free**: $0

- 1 machine, 4 vCPU / 8 GiB
- 20 GiB disk
- 5 snapshots
- 100 GiB egress / month

**Pro**: $20/month + usage

- $20 / month free credits
- Max 100 concurrent machines
- Up to 8 vCPU / 16 GiB
- 20 GiB disk, up to 200 GiB
- Unlimited snapshots
- 1 TiB egress / month
- Email support

**Builder**: $100/month + usage

- $100 / month free credits
- Max 200 concurrent machines
- Up to 16 vCPU / 32 GiB
- 20 GiB disk, up to 500 GiB
- Unlimited snapshots
- 5 TiB egress / month
- Email support

**Team**: $500/month + usage

- $500 / month free credits
- 500 concurrent machines
- Unlimited machines
- Custom machines CPU and RAM
- 20 GiB disk, up to 1 TiB
- Unlimited snapshots
- 50 TiB egress / month
- Priority email support & SLAs

**Enterprise**: Custom

- 99.9% SLA
- SSO / SAML and SCIM
- Audit logs
- Dedicated pool or BYOC
- HIPAA BAA
- Dedicated support

### Unit prices

Paid plans pay these for usage beyond their monthly credits. Runtime is metered by the second, only while a machine is running.

| Resource | Price | Unit |
|---|---|---|
| vCPU | $0.004 | per vCPU-hour |
| Memory | $0.00225 | per GiB-hour |
| Storage | $0.00011 | per GiB-hour |
| Egress | $0.02 | per GiB |

### Questions

**What do I pay for?** While a machine is running, you pay for the vCPUs and memory you gave it. Pause it, and you just pay for storage.

**How do credits work?** Usage comes out of your included credits first, then you pay as you go. Credits reset every month.

**Do you charge for network traffic?** Ingress is always free. Each plan includes egress every month (100 GiB on Free, 1 TiB on Pro, 5 TiB on Builder, 50 TiB on Team), then $0.02 per GiB.

---

# Limits

https://instabox.sh/docs/limits.md

What each plan allows, and the machine specs. Account and GET /v1/usage show yours.

| What | Default limit |
|---|---|
| Machines | Free: 1, in any state (paused and stopped ones count). Pro: 500, 100 running at once. Team: unlimited, 500 running at once |
| Machine size | 4 vCPUs and 8 GiB of memory by default, the only size on the free plan. Pro: 2/4, 4/8 or 8/16. Team: 2/4 up to 32 vCPUs / 64 GiB. `GET /v1/orgs` lists each workspace's as `allowedSpecs` |
| Snapshots | Free: 5. Pro and Team: unlimited |
| Storage | Free: 200 GB for your snapshots and machine files, counted hourly. Pro and Team: no cap; storage beyond the monthly credit is billed per GiB-hour ([Pricing](https://instabox.sh/docs/pricing.md)) |
| API keys | 20 active |
| `exec` | 32 requests at once across your sandboxes, shared by commands, file reads, desktop, port-forward and Secret refresh calls (more get a retryable `429 quota_exceeded`); 10 minutes per command |
| Idle pause | Free: 30 minutes, fixed. Paid plans: 5 to 30 minutes, or off |
| Labels | 32 per machine |
| Public ports | 16 per machine |

### Machine specs
Every template is Debian 13 (trixie), amd64, with systemd, on Linux 6.18.54 (`uname -r`: `6.18.54-instabox`) in a Firecracker microVM. A machine has 4 vCPUs and 8 GiB of memory by default (sizes above; `free -m` shows about 7.8 GiB) and a 20 GiB persistent ext4 disk at `/data` (`/dev/vdb`; home is `/data/home`). The ext4 root disk (`/`) depends on the template. Every template has git, curl, jq, Python 3.13 with `python3 -m venv` and pip, and passwordless `sudo` with apt for anything else.

| Template | OS, kernel | vCPU / RAM | Root disk | `/data` | Also preinstalled |
|---|---|---|---|---|---|
| `agent-browser` (the default) | Debian 13, 6.18.54 | 4 / 8 GiB | 16 GiB | 20 GiB | gh, Node.js 22 with npm, pnpm and Yarn, Bun, uv, Go, Rust, gcc and make, Docker with Compose, Claude Code, Codex, and the desktop (VNC, Xfce, Chromium) |
| `universal` | Debian 13, 6.18.54 | 4 / 8 GiB | 16 GiB | 20 GiB | `agent-browser`'s tools; the desktop installs on first use (about half a minute) |
| `t3` | Debian 13, 6.18.54 | 4 / 8 GiB | 16 GiB | 20 GiB | `universal`'s, plus the T3 Code server (port 3774) |
| `herdr` | Debian 13, 6.18.54 | 4 / 8 GiB | 8 GiB | 20 GiB | gh, Node.js 22 and npm, Claude Code, Codex, the desktop, and herdr (no Docker, uv, Go, Rust or C toolchain) |
| `orca` | Debian 13, 6.18.54 | 4 / 8 GiB | 8 GiB | 20 GiB | gh, Node.js 22 and npm, Claude Code, Codex, the desktop, and the Orca runtime (no Docker, uv, Go, Rust or C toolchain) |

The free plan creates from `agent-browser` only. `instabox templates` (`GET /v1/templates`) lists the templates you can create from. Check a machine with `uname -r`, `cat /etc/os-release`, `nproc`, `free -m` and `df -h / /data`.

- Over the machine or storage limit, new machines and snapshots are refused until you delete some. **Account** warns from 80% of your storage.
- A machine started from a snapshot has at least the storage of the machine it was saved from.
- `exec` returns the output when the command ends (`exec --stream` prints it as it comes). Run jobs longer than 10 minutes with `exec --background` or in tmux.
- `exec` returns when the command exits, even if it started a server in the background (`nohup ./server >server.log 2>&1 &`); the server keeps running, and its output from later than about a second after the exit is not returned. Redirect both stdout and stderr (`>log 2>&1`): a background process still writing to exec's output after that gets a broken pipe, so it may die or a server may drop requests.

### Disk sizes
A machine has one disk, `/data` (home is `/data/home`), 20 GiB by default. It comes with the machine's size: at create, leave `persistentDiskGiB` out (the TypeScript SDK's `diskGiB`, the Python SDK's `persistent_disk_gib`); any other disk size is `400 spec_not_allowed`. To change its size later (`df -h /data` full?): `instabox resize <machine> --disk 50` from the CLI (add `--restart` when it must stop the machine first: a shrink, or an image that can't grow online), `PATCH /v1/machines/{id}` with `{"persistentDiskGiB": 50}` for API and SDK alike, or **Resize disk** in the machine's Settings in the dashboard. The operating system and the template's software sit on a separate system disk the template sizes; it is not counted in the disk and only admins grow it (`rootDiskGiB` from anyone else is `400 spec_not_allowed`).

- The size is 1-1024 GiB; 0 or absent leaves the disk unchanged. More than 1024 is `400 bad_request`.
- **Grow** a running machine and it grows right away, no restart, processes keep running (machines from older images too). If it can't grow online (rare: the machine is unreachable or its host is older), it's `409 grow_needs_stop`: stop it and send the size again. A stopped machine grows at its next start.
- **Shrink** only a stopped machine (`409 operation_conflict` otherwise). Your data plus 10% (at least 1 GiB) must fit; else `409 disk_too_small`, the message names the smallest size that fits, and nothing changes.
- Paid plans only: a free machine's disk is fixed (`400 spec_not_allowed`, running or stopped). The disk may grow to at most 200 GiB on Pro, 500 GiB on Builder, 1024 GiB on Team and Enterprise, within your stored-data limit (`429 quota_exceeded`).
- The field is `persistentDiskGiB` in every REST body; `diskGiB` is only the TypeScript SDK's option name, and `POST /v1/machines` refuses it with `400 unknown_field`. PATCH ignores fields it does not know: `{"name": "web", "diskGiB": 200}` renames the machine and leaves its disk as it is.

---

# API overview

https://instabox.sh/docs/api.md

Authentication, operations, idempotency and errors: what every endpoint shares.

### Base URL
```
https://api.instabox.sh
```
Every request and response body is JSON. Times are RFC 3339, in UTC.

### Authentication
Send an [API key](https://instabox.sh/docs/keys-sdk.md) in the `X-API-Key` header (or as `Authorization: Bearer`). Create keys in the dashboard: **API keys** in the sidebar; a restricted key only reaches the endpoints its scopes allow.
```
curl https://api.instabox.sh/v1/machines -H "X-API-Key: $INSTABOX_API_KEY"
```

### Changes run as operations
Creating, starting, stopping, pausing, resuming and deleting a machine answer `202 Accepted` with an **operation** at once. Follow it with [Get an operation](https://instabox.sh/docs/api/operations.md): it ends `succeeded` or `failed`, and a machine runs one operation at a time.

### Idempotency
Endpoints that list `Idempotency-Key` under **Headers** need one: any unique string, such as a UUID. Retrying a completed request with the same key returns its response instead of acting twice; the same key on a different request is `409 idempotency_conflict`. Keys are kept for 7 days.

### Confirming deletes
[Delete a machine](https://instabox.sh/docs/api/machines.md#delete) and [Delete a snapshot](https://instabox.sh/docs/api/snapshots.md#delete) take an optional `X-Confirm-Delete` header: the ID or exact name of what you mean to delete. Any other value is `409 delete_confirmation_required` and nothing is deleted, so a mistyped ID cannot remove another machine; the same `Idempotency-Key` then works for the corrected request. Without the header the delete goes ahead. The CLI's `rm` and `snapshot rm` send it.

### Errors
Errors use the HTTP status and a JSON body whose `code` says what went wrong. `retryable` is true when the same request may succeed later; `retryAfterSeconds`, when present (`no_capacity`, `rate_limited`, `machine_cooldown`), is how many seconds to wait first; an error response also sends it as the `Retry-After` header, while a failed operation carries only the field, in its `error`.
```
{
  "error": {
    "code": "machine_not_running",
    "message": "machine is stopped; start it first",
    "requestId": "req_fbckiomplsq3fqin5dvsvzpnli",
    "retryable": false,
    "operationId": null
  }
}
```
| Status | Codes |
|---|---|
| 400 | `bad_request`, `unknown_field` (`POST /v1/machines` only: a body field it does not have; the message suggests the closest), `spec_not_allowed` (a size your plan does not offer, a disk size at create, or growing a free machine's disks; `GET /v1/orgs` lists each workspace's as `allowedSpecs`) |
| 401 | `missing_key`, `malformed_key`, `invalid_key`, `expired_key`, `revoked_key`, `session_expired` ([authentication errors](https://instabox.sh/docs/api.md#authentication-errors)), `unauthenticated` (a bad refresh token or ticket) |
| 403 | `permission_denied`, `missing_scope` (the key lacks the scope), `template_not_allowed` (the free plan creates from agent-browser only; a snapshot is not limited) |
| 404 | `not_found` |
| 409 | `operation_conflict` (another operation runs, which `operationId` names, or the change is not allowed now), `idempotency_conflict`, `machine_not_running`, `delete_confirmation_required` (`X-Confirm-Delete` names neither the ID nor the name) |
| 429 | `quota_exceeded` (a [limit](https://instabox.sh/docs/limits.md) was reached; the message says which) |
| 503 | `no_capacity` (with `retryAfterSeconds` and `Retry-After` when retryable), `host_unavailable` (usually retryable) |

`no_capacity` (no host has room right now, as a 503 or a failed operation) is retryable: wait `retryAfterSeconds` (60; the 503 also sends it as the `Retry-After` header), then retry with exponential backoff (for example every few minutes), or try another size or template. A create whose operation failed replays it for the same `Idempotency-Key`, so retry with a new key. With `--fail-fast` the CLI's `create` and `run` exit 75 on it (otherwise 1).

### Authentication errors
Each credential problem has its own `code` (`reason` repeats it), with `hint` saying how to fix it and `docs` linking here. All are HTTP 401. Older servers sent `unauthenticated`, `api_key_expired` or `api_key_revoked` instead; treat those as credential errors too.
| `code` | When |
|---|---|
| `missing_key` | No `Authorization` or `X-API-Key` header, or an empty `Bearer` token (an unset variable) |
| `malformed_key` | Not an API key (`ibk_` and 52 characters) or access token, or `Authorization` without `Bearer` |
| `invalid_key` | Well-formed, but no such key or access token |
| `expired_key` | The key or token expired |
| `revoked_key` | The key was revoked, or the session signed out |
| `session_expired` | The dashboard's session cookie is no longer valid |
```
curl https://api.instabox.sh/v1/machines -H 'Authorization: Bearer garbage'
{
  "error": {
    "code": "malformed_key",
    "reason": "malformed_key",
    "message": "malformed API key: expected an API key (\"ibk_...\") or an access token (\"iba_...\"); create an API key at …",
    "hint": "create an API key at https://dashboard.instabox.sh/dashboard/api-keys and send it as \"Authorization: Bearer <key>\" or \"X-API-Key: <key>\"",
    "docs": "https://instabox.sh/docs/api#authentication-errors",
    ...
  }
}
```
A key without the scope a route needs gets `403 missing_scope` (older servers: `insufficient_scope`) with the scopes the route accepts in `requiredScopes` (the message names them too, such as `this API key lacks the machines:delete scope this route needs`) and a `hint` to create a key with one.

### OpenAPI
The full machine-readable description, every public endpoint included, is at [https://api.instabox.sh/v1/openapi.json](https://api.instabox.sh/v1/openapi.json).

---

# Machines

https://instabox.sh/docs/api/machines.md

Create, list, change and delete machines.

A machine is a Linux VM of your own: its files under `/data` and the software you install stay across stops and restarts. A machine gets 4 vCPUs, 8 GB of memory and 20 GB of storage unless the create names another size of your plan (Pro: 2/4 and 8/16; Team: 2/4 up to 32/64; `GET /v1/orgs` lists each workspace's as `allowedSpecs`).

- `POST /v1/machines`: Create a machine
- `GET /v1/machines`: List machines
- `GET /v1/machines/{id}`: Get a machine
- `PATCH /v1/machines/{id}`: Update a machine
- `DELETE /v1/machines/{id}`: Delete a machine

## The machine object

**Properties**

- `id` (string): `m_` and 26 characters.
- `name` (string): Unique among your machines.
- `state` (string): `creating`, `starting`, `running`, `stopping`, `stopped`, `suspending`, `suspended` (paused), `resuming`, `deleting` or `error`.
- `operationId` (string | null): The operation in progress, if any.
- `template` (object): The template it started from: `id`, `version`, `digest`.
- `spec` (object): Its size: `vcpus`, `memMiB`, `persistentDiskGiB` (the disk, `/data`), and `rootDiskGiB` (the template-sized system disk).
- `runtime` (object): `ready` is true once it runs and passes its checks.
- `autoSuspendAfterSeconds` (integer | null): Idle time before it pauses (always 1800 on the free plan); null: off.
- `metadata` (object): Your labels.
- `createdAt` (string): When it was created.

## Create a machine

`POST /v1/machines`

Starts a machine from a template or one of your snapshots. Returns a `create` operation; the new machine is its `machineId`. A body field not listed here is refused with `400 unknown_field`, naming the field and the closest one listed (`"template"`: did you mean `"templateId"`?).

**Headers**

- `Idempotency-Key` (string, required): A unique string, such as a UUID; a retry with the same key is not applied twice (see the [API overview](https://instabox.sh/docs/api.md)).

**Body**

- `name` (string): 1-63 lowercase letters, digits and `-`, starting with a letter or digit. Absent: `box-` and 8 random hex digits, so `{}` is a valid body.
- `templateId` (string): A [template](https://instabox.sh/docs/api/account.md) with `creatable` true, such as `universal`, optionally pinned to a version as `universal@2026-10-15.4` (default: the version listed `latest`). Give this or `snapshotId`; with neither, `agent-browser`. An unknown or retired one is `400 bad_request`, and the message lists the templates your plan can create from; a version the template does not have lists its versions, newest first, with the `latest` (or `default`) one tagged.
- `templateVersion` (string): The template’s version (default: the one listed `latest`), the same as the `id@version` form above; both at once must agree. A version the template does not have is `400 bad_request` listing its versions.
- `snapshotId` (string): Start from this snapshot of yours instead.
- `vcpus` (integer): Leave it and `memMiB` out for the default size, 4 vCPUs and 8192 MiB. Else name both of another size of your plan: Pro 2/4096 or 8/16384, Team 2/4096 up to 32/65536 (`GET /v1/orgs` lists each workspace’s as `allowedSpecs`). Any other size, or any but the default on the free plan, is `400 spec_not_allowed`. A paid machine changes size later with `PATCH /v1/machines/{id}` while stopped.
- `memMiB` (integer): The memory in MiB of the size `vcpus` names.
- `guestUser` (string): The Linux user inside, which SSH, exec and the terminal log in as: up to 32 of `a-z`, `0-9`, `_` and `-`, starting with a letter or `_`. Reserved names (`root`, system users and groups) are `400 invalid_guest_user`. Default: `user` (with `snapshotId`: the user of that snapshot). Fixed at create; older templates always get `dev`.
- `autoSuspendAfterSeconds` (integer): Pause the machine once it has been idle this many seconds. A paid plan takes 300-1800, rounded up to 300, 600, 900, 1200, 1500 or 1800, and 0 turns idle pause off; below 300 or above 1800 is refused (400), nothing created. The free plan always pauses after 1800 seconds (30 minutes): another value is refused (403), nothing created. The reply shows the effective value.
- `metadata` (object): String labels, up to 32 keys. Filter by them when listing. Not for secrets.
- `orgId` (string): Target org; defaults to your personal org. A snapshot determines its own org.
- `vault` (boolean): False disables personal Vault delivery only. It does not change Secret selections.
- `secrets` ("all" | string[]): All current and future proxy Secrets, or explicit names ([] selects none). Env Secrets are never included. Omit both selection fields to keep Vault behavior without Secret enrollment. With envSecrets alone, proxy selection defaults to all.
- `envSecrets` (string[]): Explicit env Secret names ([] selects none). No all mode. Code inside the sandbox can read these values.
- `desiredState` ("running" | "stopped"): `stopped` stops it once it is set up. Default: `running`.
- `persistentDiskGiB` (integer): Leave it out: the disk (`/data`) comes with the size (20 GiB, or a snapshot’s when larger). Any size but that one is `400 spec_not_allowed`; grow the disk later with [Update a machine](https://instabox.sh/docs/api/machines.md#update). The SDKs’ `diskGiB` and `persistent_disk_gib` are this field; `diskGiB` in a REST body is `400 unknown_field`.
- `rootDiskGiB` (integer): Leave it out, like `persistentDiskGiB`.
- `failFast` (boolean): When no host has room right now, answer `503 no_capacity` at once and create nothing, instead of a `create` operation that then fails with `no_capacity`. Default: false.

**Request**

```bash
curl -X POST https://api.instabox.sh/v1/machines -H "X-API-Key: $INSTABOX_API_KEY" -H "Idempotency-Key: $(uuidgen)" -H 'Content-Type: application/json' \
  -d '{"name": "dev", "templateId": "universal"}'
```

**Response** (202 Accepted)

```json
{
  "id": "op_7xk2mq4tz5rbw3vn6pd2hs4jye",
  "machineId": "m_agqteugyy5px6hzeadbh4ldjo4",
  "type": "create",
  "state": "queued",
  "error": null,
  "createdAt": "2026-10-13T09:12:04Z",
  "updatedAt": "2026-10-13T09:12:04Z"
}
```

## List machines

`GET /v1/machines`

Your machines, a page at a time.

**Query parameters**

- `metadata` (string): `key:value`: only machines with that label. Repeat it to require several.
- `limit` (integer): Page size.
- `cursor` (string): The `nextCursor` of the previous page.

**Request**

```bash
curl "https://api.instabox.sh/v1/machines?metadata=task:review" -H "X-API-Key: $INSTABOX_API_KEY"
```

**Response** (200 OK)

```json
{
  "machines": [ { "id": "m_agqteugyy5px6hzeadbh4ldjo4", "name": "dev", "state": "running", … } ],
  "nextCursor": null
}
```

## Get a machine

`GET /v1/machines/{id}`

The machine, by ID or by name.

**Path parameters**

- `id` (string, required): The machine’s ID or its name.

**Request**

```bash
curl https://api.instabox.sh/v1/machines/dev -H "X-API-Key: $INSTABOX_API_KEY"
```

**Response** (200 OK)

```json
{
  "id": "m_agqteugyy5px6hzeadbh4ldjo4",
  "name": "dev",
  "state": "running",
  "desiredState": "running",
  "revision": 3,
  "operationId": null,
  "template": { "id": "universal", "version": "2026-10-13.10", "digest": "sha256:9f2c…" },
  "spec": { "vcpus": 4, "memMiB": 8192, "persistentDiskGiB": 20 },
  "storage": { "sizeGiB": 20, "mountPath": "/data", "persistent": true, "synced": true },
  "runtime": { "ready": true },
  "autoSuspendAfterSeconds": 1800,
  "metadata": { "task": "review" },
  "guestUser": "alice",
  "createdAt": "2026-10-13T09:12:04Z",
  "updatedAt": "2026-10-13T09:12:31Z"
}
```

## Update a machine

`PATCH /v1/machines/{id}`

Changes the idle pause or labels, in any state and at once, or resizes a stopped paid machine: its vCPUs and memory, or its disk (`/data`). Fields you leave out are unchanged.

**Path parameters**

- `id` (string, required): The machine's ID (`m_agqteugyy5px6hzeadbh4ldjo4`).

**Headers**

- `Idempotency-Key` (string, required): A unique string, such as a UUID; a retry with the same key is not applied twice (see the [API overview](https://instabox.sh/docs/api.md)).

**Body**

- `vcpus` (integer): New vCPUs, with `memMiB`: another of your plan’s sizes (`allowedSpecs` in `GET /v1/orgs`, e.g. Pro 2/4096, 4/8192, 8/16384). Alone it picks the one size with that many vCPUs. Only while the machine is stopped with no operation running (else `409 operation_conflict`); the new size applies at its next start, a fresh boot (files stay). Another size, or a free machine, is `400 spec_not_allowed`.
- `memMiB` (integer): New memory in MiB, with `vcpus` (see it); 0 or absent: unchanged.
- `persistentDiskGiB` (integer): New disk (`/data`) size in GiB, 1-1024; 0 or absent: unchanged. A running machine grows online, with no restart (if it can't, rarely, `409 grow_needs_stop`: stop it and send the size again); a stopped one is resized at its next start. Shrinking needs a stopped machine (else `409 operation_conflict`) whose data plus 10% (at least 1 GiB) fits (else `409 disk_too_small`, nothing changes). It may grow to the plan’s limit (Pro 200, Builder 500, Team and Enterprise 1024 GiB) and your stored-data limit (`429 quota_exceeded`). A free machine’s disk is fixed (`400 spec_not_allowed`). The field is not `diskGiB`: this endpoint ignores fields it does not know.
- `rootDiskGiB` (integer): Admins only: new system disk size in GiB (the template sizes it). From anyone else it is `400 spec_not_allowed`.
- `autoSuspendAfterSeconds` (integer): Pause it once idle this many seconds. A paid plan rounds it up to 300 to 1800 and 0 turns it off; the free plan keeps the fixed 30 minutes and refuses another value (403). The reply shows the effective value.
- `metadata` (object): Replaces the labels; `{}` clears them.

**Request**

```bash
curl -X PATCH https://api.instabox.sh/v1/machines/m_agqteugyy5px6hzeadbh4ldjo4 -H "X-API-Key: $INSTABOX_API_KEY" -H "Idempotency-Key: $(uuidgen)" -H 'Content-Type: application/json' \
  -d '{"autoSuspendAfterSeconds": 600}'
```

**Response** (200 OK)

```json
{
  "id": "m_agqteugyy5px6hzeadbh4ldjo4",
  "name": "dev",
  "state": "running",
  "desiredState": "running",
  "revision": 3,
  "operationId": null,
  "template": { "id": "universal", "version": "2026-10-13.10", "digest": "sha256:9f2c…" },
  "spec": { "vcpus": 4, "memMiB": 8192, "persistentDiskGiB": 20 },
  "storage": { "sizeGiB": 20, "mountPath": "/data", "persistent": true, "synced": true },
  "runtime": { "ready": true },
  "autoSuspendAfterSeconds": 1800,
  "metadata": { "task": "review" },
  "guestUser": "alice",
  "createdAt": "2026-10-13T09:12:04Z",
  "updatedAt": "2026-10-13T09:12:31Z"
}
```

## Delete a machine

`DELETE /v1/machines/{id}`

Deletes the machine and its files. Snapshots saved from it are kept.

**Path parameters**

- `id` (string, required): The machine's ID (`m_agqteugyy5px6hzeadbh4ldjo4`).

**Headers**

- `Idempotency-Key` (string, required): A unique string, such as a UUID; a retry with the same key is not applied twice (see the [API overview](https://instabox.sh/docs/api.md)).
- `X-Confirm-Delete` (string): Optional: the ID or exact name of what you are deleting. Any other value is `409 delete_confirmation_required` and nothing is deleted; without the header the delete goes ahead.

**Request**

```bash
curl -X DELETE https://api.instabox.sh/v1/machines/m_agqteugyy5px6hzeadbh4ldjo4 -H "X-API-Key: $INSTABOX_API_KEY" -H "Idempotency-Key: $(uuidgen)" -H "X-Confirm-Delete: m_agqteugyy5px6hzeadbh4ldjo4"
```

**Response** (202 Accepted)

```json
{
  "id": "op_7xk2mq4tz5rbw3vn6pd2hs4jye",
  "machineId": "m_agqteugyy5px6hzeadbh4ldjo4",
  "type": "delete",
  "state": "queued",
  "error": null,
  "createdAt": "2026-10-13T09:12:04Z",
  "updatedAt": "2026-10-13T09:12:04Z"
}
```

---

# Lifecycle

https://instabox.sh/docs/api/lifecycle.md

Start, stop, pause and resume machines.

Each of these answers `202 Accepted` with an [operation](https://instabox.sh/docs/api/operations.md) and needs an `Idempotency-Key`. A paused machine keeps its memory and running programs; a stopped one keeps only its files.

- `POST /v1/machines/{id}/start`: Start a machine
- `POST /v1/machines/{id}/stop`: Stop a machine
- `POST /v1/machines/{id}/suspend`: Pause a machine
- `POST /v1/machines/{id}/resume`: Resume a machine

## Start a machine

`POST /v1/machines/{id}/start`

Boots a stopped machine. On a paused one it resumes it, or boots fresh if its programs cannot be brought back.

**Path parameters**

- `id` (string, required): The machine's ID (`m_agqteugyy5px6hzeadbh4ldjo4`).

**Headers**

- `Idempotency-Key` (string, required): A unique string, such as a UUID; a retry with the same key is not applied twice (see the [API overview](https://instabox.sh/docs/api.md)).

**Request**

```bash
curl -X POST https://api.instabox.sh/v1/machines/m_agqteugyy5px6hzeadbh4ldjo4/start -H "X-API-Key: $INSTABOX_API_KEY" -H "Idempotency-Key: $(uuidgen)"
```

**Response** (202 Accepted)

```json
{
  "id": "op_7xk2mq4tz5rbw3vn6pd2hs4jye",
  "machineId": "m_agqteugyy5px6hzeadbh4ldjo4",
  "type": "start",
  "state": "queued",
  "error": null,
  "createdAt": "2026-10-13T09:12:04Z",
  "updatedAt": "2026-10-13T09:12:04Z"
}
```

## Stop a machine

`POST /v1/machines/{id}/stop`

Shuts a running machine down: programs end, files are kept. A paused machine cannot be stopped; resume or delete it.

**Path parameters**

- `id` (string, required): The machine's ID (`m_agqteugyy5px6hzeadbh4ldjo4`).

**Headers**

- `Idempotency-Key` (string, required): A unique string, such as a UUID; a retry with the same key is not applied twice (see the [API overview](https://instabox.sh/docs/api.md)).

**Body**

- `timeoutSeconds` (integer): Seconds to wait for a clean shutdown before forcing it off (0 to 600). Default: 60.

**Request**

```bash
curl -X POST https://api.instabox.sh/v1/machines/m_agqteugyy5px6hzeadbh4ldjo4/stop -H "X-API-Key: $INSTABOX_API_KEY" -H "Idempotency-Key: $(uuidgen)"
```

**Response** (202 Accepted)

```json
{
  "id": "op_7xk2mq4tz5rbw3vn6pd2hs4jye",
  "machineId": "m_agqteugyy5px6hzeadbh4ldjo4",
  "type": "stop",
  "state": "queued",
  "error": null,
  "createdAt": "2026-10-13T09:12:04Z",
  "updatedAt": "2026-10-13T09:12:04Z"
}
```

## Pause a machine

`POST /v1/machines/{id}/suspend`

Pauses a running machine, keeping its memory and running programs.

**Path parameters**

- `id` (string, required): The machine's ID (`m_agqteugyy5px6hzeadbh4ldjo4`).

**Headers**

- `Idempotency-Key` (string, required): A unique string, such as a UUID; a retry with the same key is not applied twice (see the [API overview](https://instabox.sh/docs/api.md)).

**Request**

```bash
curl -X POST https://api.instabox.sh/v1/machines/m_agqteugyy5px6hzeadbh4ldjo4/suspend -H "X-API-Key: $INSTABOX_API_KEY" -H "Idempotency-Key: $(uuidgen)"
```

**Response** (202 Accepted)

```json
{
  "id": "op_7xk2mq4tz5rbw3vn6pd2hs4jye",
  "machineId": "m_agqteugyy5px6hzeadbh4ldjo4",
  "type": "suspend",
  "state": "queued",
  "error": null,
  "createdAt": "2026-10-13T09:12:04Z",
  "updatedAt": "2026-10-13T09:12:04Z"
}
```

## Resume a machine

`POST /v1/machines/{id}/resume`

Continues a paused machine where it left off.

**Path parameters**

- `id` (string, required): The machine's ID (`m_agqteugyy5px6hzeadbh4ldjo4`).

**Headers**

- `Idempotency-Key` (string, required): A unique string, such as a UUID; a retry with the same key is not applied twice (see the [API overview](https://instabox.sh/docs/api.md)).

**Request**

```bash
curl -X POST https://api.instabox.sh/v1/machines/m_agqteugyy5px6hzeadbh4ldjo4/resume -H "X-API-Key: $INSTABOX_API_KEY" -H "Idempotency-Key: $(uuidgen)"
```

**Response** (202 Accepted)

```json
{
  "id": "op_7xk2mq4tz5rbw3vn6pd2hs4jye",
  "machineId": "m_agqteugyy5px6hzeadbh4ldjo4",
  "type": "resume",
  "state": "queued",
  "error": null,
  "createdAt": "2026-10-13T09:12:04Z",
  "updatedAt": "2026-10-13T09:12:04Z"
}
```

---

# Commands and files

https://instabox.sh/docs/api/commands.md

Run a command in a machine, and read, upload and download its files.

They need a running machine: one paused for being idle is woken first, any other gets `409 machine_not_running`. At most 32 requests per user run at once, across all your sandboxes. Commands, file reads and writes, desktop, port-forward and Secret refresh calls share this limit. A background command counts only while it starts. More get a retryable `429 quota_exceeded`.

- `POST /v1/machines/{id}/exec`: Run a command
- `GET /v1/machines/{id}/files`: Read a file or directory
- `PUT /v1/machines/{id}/files`: Upload a file
- `GET /v1/machines/{id}/files/content`: Download a file
- `POST /v1/machines/{id}/files/upload-url`: Get an upload URL

## Run a command

`POST /v1/machines/{id}/exec`

Runs a command as the machine’s user and returns its output when it exits: `cmd` is a shell string run with `bash -lc`; `argv` is a program and its arguments, run with no shell, so each argument arrives exactly as sent. Set exactly one of them. A non-zero exit code is still a `200` result. With `Accept: text/event-stream` the output is streamed as server-sent events while the command runs: `stdout` and `stderr` events (`{"data"}`), then one `exit` event with the result (empty output) or an `error` event. Run jobs longer than 10 minutes in the background. The call returns when the command exits, even if a process it started in the background keeps its stdout or stderr open; that process keeps running, output written later than about a second after the exit is not returned, and its later writes to that output fail with a broken pipe, so redirect a server’s stdout and stderr to a file (`nohup server >log 2>&1 &`). If the connection to the command is lost before it exits (the client disconnects, an API server restarts), the command and its process group are killed rather than left running; a restarting API server answers `503 host_unavailable` (`retryable`).

**Path parameters**

- `id` (string, required): The machine's ID (`m_agqteugyy5px6hzeadbh4ldjo4`).

**Body**

- `cmd` (string): The shell command, run with `bash -lc`. Set this or `argv`.
- `argv` (string[]): The program and its arguments, run with no shell: `$`, `*`, quotes and spaces reach the program as written. `["printf", "%s|", "a b", "$X"]` prints `a b|$X|`. Set this or `cmd`.
- `cwd` (string): Working directory. Default: home, `/data/home`.
- `envs` (object): Environment variables to set.
- `stdin` (string): Fed to the command, then end of file. At most 1 MiB.
- `timeoutSeconds` (integer): Kill the command after this long (exit code 124). Default 60, at most 600.

**Request**

```bash
curl -X POST https://api.instabox.sh/v1/machines/m_agqteugyy5px6hzeadbh4ldjo4/exec -H "X-API-Key: $INSTABOX_API_KEY" -H 'Content-Type: application/json' \
  -d '{"cmd": "echo hello"}'
```

**Response** (200 OK)

```json
{
  "stdout": "hello\n",
  "stderr": "",
  "exitCode": 0,
  "timedOut": false,
  "truncated": false
}
```

## Read a file or directory

`GET /v1/machines/{id}/files`

Lists a directory (up to 5000 entries) or returns a text file (up to 256 KiB), read live as root.

**Path parameters**

- `id` (string, required): The machine's ID (`m_agqteugyy5px6hzeadbh4ldjo4`).

**Query parameters**

- `path` (string): An absolute path. Default: `/`.

**Request**

```bash
curl "https://api.instabox.sh/v1/machines/m_agqteugyy5px6hzeadbh4ldjo4/files?path=/data/home" -H "X-API-Key: $INSTABOX_API_KEY"
```

**Response** (200 OK)

```json
{
  "path": "/data/home",
  "type": "dir",
  "size": 0,
  "mode": "drwxr-xr-x",
  "modTime": "2026-10-13T09:30:12Z",
  "entries": [
    { "name": "app", "type": "dir", "size": 0, "mode": "drwxr-xr-x", "modTime": "2026-10-13T09:28:40Z" },
    { "name": "notes.txt", "type": "file", "size": 5, "mode": "-rw-r--r--", "modTime": "2026-10-13T09:30:12Z" }
  ]
}
```

## Upload a file

`PUT /v1/machines/{id}/files`

Streams the raw request body into the file, as the machine’s user: any bytes, up to 5 GiB. The file appears only once every byte arrived; the answer has its SHA-256. A missing parent directory is `404 missing_parent` unless `parents=true`; one you cannot write is `403 permission_denied`; a directory is `409 not_a_file`. A transfer idle for 60 seconds is dropped. `201` for a new file, `200` for a replaced one.

**Path parameters**

- `id` (string, required): The machine's ID (`m_agqteugyy5px6hzeadbh4ldjo4`).

**Query parameters**

- `path` (string, required): An absolute path.
- `mode` (string): Octal permissions, e.g. `0755`. Default: an existing file’s, else `0644`.
- `parents` (boolean): Create missing parent directories.

**Request**

```bash
curl -X PUT "https://api.instabox.sh/v1/machines/m_agqteugyy5px6hzeadbh4ldjo4/files?path=/data/home/x.tgz" -H "X-API-Key: $INSTABOX_API_KEY" \
  --data-binary @x.tgz
```

**Response** (201 Created)

```json
{
  "path": "/data/home/x.tgz",
  "size": 52428800,
  "sha256": "3f0a…",
  "mode": "0644",
  "created": true
}
```

## Download a file

`GET /v1/machines/{id}/files/content`

Streams a file’s raw bytes, any size, as the machine’s user, with its exact `Content-Length`. Missing is `404 not_found`, a directory `409 not_a_file`, unreadable `403 permission_denied`.

**Path parameters**

- `id` (string, required): The machine's ID (`m_agqteugyy5px6hzeadbh4ldjo4`).

**Query parameters**

- `path` (string, required): An absolute path.

**Request**

```bash
curl "https://api.instabox.sh/v1/machines/m_agqteugyy5px6hzeadbh4ldjo4/files/content?path=/data/home/x.tgz" -H "X-API-Key: $INSTABOX_API_KEY" -o x.tgz
```

**Response** (200 OK)

```json
(the file’s bytes)
```

## Get an upload URL

`POST /v1/machines/{id}/files/upload-url`

A signed URL that takes `PUT` of one file’s bytes with no other credential, until it expires (default 15 minutes, at most 1 hour). It binds the path, `mode` and `parents`, and stops working if your API key is revoked. Same limits as uploading a file.

**Path parameters**

- `id` (string, required): The machine's ID (`m_agqteugyy5px6hzeadbh4ldjo4`).

**Body**

- `path` (string, required): An absolute path.
- `mode` (string): Octal permissions.
- `parents` (boolean): Create missing parent directories.
- `expiresInSeconds` (integer): Default 900, at most 3600.

**Request**

```bash
curl -X POST https://api.instabox.sh/v1/machines/m_agqteugyy5px6hzeadbh4ldjo4/files/upload-url -H "X-API-Key: $INSTABOX_API_KEY" -H 'Content-Type: application/json' \
  -d '{"path": "/data/home/big.bin"}'
curl -X PUT --upload-file big.bin "$URL"
```

**Response** (201 Created)

```json
{
  "url": "https://api.instabox.sh/v1/machines/m_agqteugyy5px6hzeadbh4ldjo4/files?path=%2Fdata%2Fhome%2Fbig.bin&token=…",
  "method": "PUT",
  "path": "/data/home/big.bin",
  "expiresAt": "2026-10-13T09:45:12Z",
  "maxBytes": 5368709120
}
```

---

# Snapshots

https://instabox.sh/docs/api/snapshots.md

Save a machine, then start new machines from it.

A snapshot holds a machine’s installed software and its files under `/data`, home included. It does not hold memory or running programs. Snapshots are private to you.

- `POST /v1/machines/{id}/snapshots`: Save a snapshot
- `GET /v1/snapshots`: List snapshots
- `GET /v1/snapshots/{id}`: Get a snapshot
- `GET /v1/snapshots/{id}/files`: Read a snapshot’s files
- `DELETE /v1/snapshots/{id}`: Delete a snapshot

## The snapshot object

**Properties**

- `id` (string): `sn_` and 26 characters.
- `name` (string): Unique among your snapshots.
- `status` (string): `ready` can be used. A snapshot of a running machine is `pending` until it is uploaded, then `ready` or `failed`.
- `sourceMachineId` (string): The machine it was saved from.
- `rootSizeBytes` (integer): Size of the saved system disk.
- `dataSizeBytes` (integer): Size of the saved storage disk (`/data`). Machines started from it get at least this much storage.
- `createdAt` (string): When it was saved.

## Save a snapshot

`POST /v1/machines/{id}/snapshots`

A stopped machine is saved at once (`201`). A running machine, where the server allows it, is saved while it runs: `202`, and the snapshot is `pending` until it is uploaded.

**Path parameters**

- `id` (string, required): The machine's ID (`m_agqteugyy5px6hzeadbh4ldjo4`).

**Headers**

- `Idempotency-Key` (string, required): A unique string, such as a UUID; a retry with the same key is not applied twice (see the [API overview](https://instabox.sh/docs/api.md)).

**Body**

- `name` (string, required): Lowercase letters, digits and `-`; unique among your snapshots.
- `description` (string): Shown with the snapshot.
- `rootOnly` (boolean): Save the installed software only: machines from it start with an empty home.

**Request**

```bash
curl -X POST https://api.instabox.sh/v1/machines/m_agqteugyy5px6hzeadbh4ldjo4/snapshots -H "X-API-Key: $INSTABOX_API_KEY" -H "Idempotency-Key: $(uuidgen)" -H 'Content-Type: application/json' \
  -d '{"name": "dev-base"}'
```

**Response** (201 Created)

```json
{
  "id": "sn_q4mz7tk2bx5rn3wd6vp2hj4sye",
  "name": "dev-base",
  "sourceMachineId": "m_agqteugyy5px6hzeadbh4ldjo4",
  "sourceSnapshotSeq": 7,
  "status": "ready",
  "template": { "id": "universal", "version": "2026-10-13.10", "digest": "sha256:9f2c…" },
  "rootSizeBytes": 17179869184,
  "dataSizeBytes": 21474836480,
  "createdAt": "2026-10-13T10:02:11Z"
}
```

## List snapshots

`GET /v1/snapshots`

Your snapshots, oldest first.

**Request**

```bash
curl https://api.instabox.sh/v1/snapshots -H "X-API-Key: $INSTABOX_API_KEY"
```

**Response** (200 OK)

```json
{ "snapshots": [ { "id": "sn_q4mz7tk2bx5rn3wd6vp2hj4sye", "name": "dev-base", "status": "ready", … } ] }
```

## Get a snapshot

`GET /v1/snapshots/{id}`

One of your snapshots.

**Path parameters**

- `id` (string, required): The snapshot’s ID.

**Request**

```bash
curl https://api.instabox.sh/v1/snapshots/sn_q4mz7tk2bx5rn3wd6vp2hj4sye -H "X-API-Key: $INSTABOX_API_KEY"
```

**Response** (200 OK)

```json
{
  "id": "sn_q4mz7tk2bx5rn3wd6vp2hj4sye",
  "name": "dev-base",
  "sourceMachineId": "m_agqteugyy5px6hzeadbh4ldjo4",
  "sourceSnapshotSeq": 7,
  "status": "ready",
  "template": { "id": "universal", "version": "2026-10-13.10", "digest": "sha256:9f2c…" },
  "rootSizeBytes": 17179869184,
  "dataSizeBytes": 21474836480,
  "createdAt": "2026-10-13T10:02:11Z"
}
```

## Read a snapshot’s files

`GET /v1/snapshots/{id}/files`

Lists a directory or returns a text file of the saved software, without starting a machine. Files under `/data` are not shown.

**Path parameters**

- `id` (string, required): The snapshot’s ID.

**Query parameters**

- `path` (string): An absolute path. Default: `/`.

**Request**

```bash
curl "https://api.instabox.sh/v1/snapshots/sn_q4mz7tk2bx5rn3wd6vp2hj4sye/files?path=/etc" -H "X-API-Key: $INSTABOX_API_KEY"
```

**Response** (200 OK)

```json
{
  "path": "/etc",
  "type": "dir",
  "size": 0,
  "mode": "drwxr-xr-x",
  "modTime": "2026-10-13T08:01:55Z",
  "entries": [
    { "name": "apt", "type": "dir", "size": 0, "mode": "drwxr-xr-x", "modTime": "2026-10-13T08:01:40Z" },
    { "name": "os-release", "type": "symlink", "size": 21, "mode": "lrwxrwxrwx", "modTime": "2026-10-13T08:01:12Z", "target": "../usr/lib/os-release" },
    …
  ]
}
```

## Delete a snapshot

`DELETE /v1/snapshots/{id}`

Machines created from it are not affected.

**Path parameters**

- `id` (string, required): The snapshot’s ID.

**Headers**

- `Idempotency-Key` (string, required): A unique string, such as a UUID; a retry with the same key is not applied twice (see the [API overview](https://instabox.sh/docs/api.md)).
- `X-Confirm-Delete` (string): Optional: the ID or exact name of what you are deleting. Any other value is `409 delete_confirmation_required` and nothing is deleted; without the header the delete goes ahead.

**Request**

```bash
curl -X DELETE https://api.instabox.sh/v1/snapshots/sn_q4mz7tk2bx5rn3wd6vp2hj4sye -H "X-API-Key: $INSTABOX_API_KEY" -H "Idempotency-Key: $(uuidgen)" -H "X-Confirm-Delete: sn_q4mz7tk2bx5rn3wd6vp2hj4sye"
```

**Response** (204 No Content)

No body.

---

# Operations

https://instabox.sh/docs/api/operations.md

Follow a change to a machine until it is done.

Creating, starting, stopping, pausing, resuming and deleting a machine each return an operation. Wait for it before the next change to that machine: a machine runs one operation at a time.

- `GET /v1/operations/{id}`: Get an operation

## The operation object

**Properties**

- `id` (string): `op_` and 26 characters.
- `machineId` (string): The machine it changes.
- `type` (string): `create`, `start`, `stop`, `suspend` (pause), `resume` or `delete`.
- `state` (string): `queued`, `running`, then `succeeded` or `failed`.
- `phase` (string): Progress, such as `booting` or `snapshotting`.
- `error` (object | null): Why it failed: an error `code` and `message`.
- `machine` (object): Once it succeeded: the machine as it is now.

## Get an operation

`GET /v1/operations/{id}`

With `wait`, the request waits until the operation is done or changes, so a loop of these needs no sleeping.

**Path parameters**

- `id` (string, required): The operation’s ID.

**Query parameters**

- `wait` (string): Wait up to this long for a change, such as `25s` (at most 30s).

**Request**

```bash
curl "https://api.instabox.sh/v1/operations/op_7xk2mq4tz5rbw3vn6pd2hs4jye?wait=25s" -H "X-API-Key: $INSTABOX_API_KEY"
```

**Response** (200 OK)

```json
{
  "id": "op_7xk2mq4tz5rbw3vn6pd2hs4jye",
  "machineId": "m_agqteugyy5px6hzeadbh4ldjo4",
  "type": "create",
  "state": "succeeded",
  "error": null,
  "createdAt": "2026-10-13T09:12:04Z",
  "updatedAt": "2026-10-13T09:12:04Z"
}
```

---

# SSH

https://instabox.sh/docs/api/ssh.md

Log in to a machine with ssh or mosh.

An SSH token is the simplest way in: one `ssh` command that works in any terminal, no key needed. A certificate suits clients that bring their own key.

- `POST /v1/machines/{id}/ssh-tokens`: Create an SSH token
- `GET /v1/machines/{id}/ssh-tokens`: List SSH tokens
- `DELETE /v1/machines/{id}/ssh-tokens/{tokenID}`: Revoke an SSH token
- `DELETE /v1/machines/{id}/ssh-tokens`: Revoke all SSH tokens
- `POST /v1/machines/{id}/connections`: Get an SSH certificate

## Create an SSH token

`POST /v1/machines/{id}/ssh-tokens`

Returns a ready-to-run `ssh` command. With an API key, the token is shown only in this response. It works until it expires or is revoked. It takes no `Idempotency-Key`: a retry makes another token.

**Path parameters**

- `id` (string, required): The machine's ID (`m_agqteugyy5px6hzeadbh4ldjo4`).

**Body**

- `name` (string): A name to recognize it by.
- `ttlSeconds` (integer): How long it works. Default 7 days, at most 30.
- `noExpiry` (boolean): A token that works until it is revoked, instead of ttlSeconds. Anyone holding it can get in.

**Request**

```bash
curl -X POST https://api.instabox.sh/v1/machines/m_agqteugyy5px6hzeadbh4ldjo4/ssh-tokens -H "X-API-Key: $INSTABOX_API_KEY" -H 'Content-Type: application/json' \
  -d '{"name": "laptop"}'
```

**Response** (201 Created)

```json
{
  "id": "cn_k3wq7xz2mb4tn5rd6vh2pj4sye",
  "name": "laptop",
  "machineId": "m_agqteugyy5px6hzeadbh4ldjo4",
  "host": "api.instabox.sh",
  "port": 2222,
  "token": "ibssh_r2kd7vq4mx5tz3nb6wp2hj4sye",
  "command": "ssh -p 2222 ibssh_r2kd7vq4mx5tz3nb6wp2hj4sye@api.instabox.sh",
  "expiresAt": "2026-10-20T10:31:07Z",
  "hostKeyFingerprint": "SHA256:Xp1v…"
}
```

## List SSH tokens

`GET /v1/machines/{id}/ssh-tokens`

The machine’s tokens, newest first. With an API key, without their secrets.

**Path parameters**

- `id` (string, required): The machine's ID (`m_agqteugyy5px6hzeadbh4ldjo4`).

**Request**

```bash
curl https://api.instabox.sh/v1/machines/m_agqteugyy5px6hzeadbh4ldjo4/ssh-tokens -H "X-API-Key: $INSTABOX_API_KEY"
```

**Response** (200 OK)

```json
{
  "tokens": [
    { "id": "cn_k3wq7xz2mb4tn5rd6vh2pj4sye", "name": "laptop", "createdAt": "2026-10-13T10:31:07Z", "expiresAt": "2026-10-20T10:31:07Z" }
  ]
}
```

## Revoke an SSH token

`DELETE /v1/machines/{id}/ssh-tokens/{tokenID}`

Ends one token and closes its connections.

**Path parameters**

- `id` (string, required): The machine's ID (`m_agqteugyy5px6hzeadbh4ldjo4`).
- `tokenID` (string, required): The token’s `id`.

**Request**

```bash
curl -X DELETE https://api.instabox.sh/v1/machines/m_agqteugyy5px6hzeadbh4ldjo4/ssh-tokens/cn_k3wq7xz2mb4tn5rd6vh2pj4sye -H "X-API-Key: $INSTABOX_API_KEY"
```

**Response** (204 No Content)

No body.

## Revoke all SSH tokens

`DELETE /v1/machines/{id}/ssh-tokens`

Ends every token of the machine and closes their connections.

**Path parameters**

- `id` (string, required): The machine's ID (`m_agqteugyy5px6hzeadbh4ldjo4`).

**Request**

```bash
curl -X DELETE https://api.instabox.sh/v1/machines/m_agqteugyy5px6hzeadbh4ldjo4/ssh-tokens -H "X-API-Key: $INSTABOX_API_KEY"
```

**Response** (200 OK)

```json
{ "revoked": 2 }
```

## Get an SSH certificate

`POST /v1/machines/{id}/connections`

Signs your public key for a short time. Log in as the machine’s ID through the returned host and port, trusting the returned host CA. The machine must be running, or paused for being idle (it is woken).

**Path parameters**

- `id` (string, required): The machine's ID (`m_agqteugyy5px6hzeadbh4ldjo4`).

**Headers**

- `Idempotency-Key` (string, required): A unique string, such as a UUID; a retry with the same key is not applied twice (see the [API overview](https://instabox.sh/docs/api.md)).

**Body**

- `publicKey` (string, required): Your public key, as in `authorized_keys`.
- `ttlSeconds` (integer): Default 1 hour, at most 24.

**Request**

```bash
curl -X POST https://api.instabox.sh/v1/machines/m_agqteugyy5px6hzeadbh4ldjo4/connections -H "X-API-Key: $INSTABOX_API_KEY" -H "Idempotency-Key: $(uuidgen)" -H 'Content-Type: application/json' \
  -d "{\"publicKey\": \"$(cat ~/.ssh/id_ed25519.pub)\"}"
```

**Response** (201 Created)

```json
{
  "id": "cn_t5mq2xk7bz4rn3wd6vp2hj4sye",
  "machineId": "m_agqteugyy5px6hzeadbh4ldjo4",
  "transport": "ssh",
  "host": "api.instabox.sh",
  "port": 2222,
  "username": "m_agqteugyy5px6hzeadbh4ldjo4",
  "certificate": "ssh-ed25519-cert-v01@openssh.com AAAA…",
  "expiresAt": "2026-10-13T11:31:07Z",
  "hostTrust": { "type": "ca", "publicKey": "ssh-ed25519 AAAA…", "principals": ["api.instabox.sh"] }
}
```

---

# Public ports

https://instabox.sh/docs/api/ports.md

Give a web server in a machine an HTTPS URL.

Anyone with a public URL can reach the whole service on that port, until you unpublish it. A visit wakes a machine paused for being idle and waits for it to run; a machine its owner paused or stopped returns 503 until it is resumed or started. At most 16 per machine.

- `POST /v1/machines/{id}/ports`: Publish a port
- `GET /v1/machines/{id}/ports`: List a machine’s ports
- `GET /v1/ports`: List all ports
- `DELETE /v1/machines/{id}/ports/{port}`: Unpublish a port

## The public port object

**Properties**

- `port` (integer): The port in the machine.
- `name` (string): Its display name.
- `url` (string): Its public HTTPS URL.
- `machineId` (string): The machine.

## Publish a port

`POST /v1/machines/{id}/ports`

Gives the port a public URL (`201`). Publishing it again keeps the URL, and renames it if you send a `name` (`200`). It does not start a server.

**Path parameters**

- `id` (string, required): The machine's ID (`m_agqteugyy5px6hzeadbh4ldjo4`).

**Body**

- `port` (integer, required): The port your server listens on.
- `name` (string): A display name. Default: `Port N`.

**Request**

```bash
curl -X POST https://api.instabox.sh/v1/machines/m_agqteugyy5px6hzeadbh4ldjo4/ports -H "X-API-Key: $INSTABOX_API_KEY" -H 'Content-Type: application/json' \
  -d '{"port": 3000, "name": "Web app"}'
```

**Response** (201 Created)

```json
{
  "id": "pv-k2rd7vq4mx5tz3nb6wp2hj4sye",
  "machineId": "m_agqteugyy5px6hzeadbh4ldjo4",
  "port": 3000,
  "name": "Web app",
  "url": "https://3000-agqteugyy5px6hzeadbh4ldjo4.instabox.tech",
  "createdAt": "2026-10-13T10:20:45Z"
}
```

## List a machine’s ports

`GET /v1/machines/{id}/ports`

The machine’s public ports.

**Path parameters**

- `id` (string, required): The machine's ID (`m_agqteugyy5px6hzeadbh4ldjo4`).

**Request**

```bash
curl https://api.instabox.sh/v1/machines/m_agqteugyy5px6hzeadbh4ldjo4/ports -H "X-API-Key: $INSTABOX_API_KEY"
```

**Response** (200 OK)

```json
{ "enabled": true, "ports": [ { "port": 3000, "name": "Web app", "url": "https://3000-agqteugyy5px6hzeadbh4ldjo4.instabox.tech", … } ] }
```

## List all ports

`GET /v1/ports`

The public ports of all your machines.

**Request**

```bash
curl https://api.instabox.sh/v1/ports -H "X-API-Key: $INSTABOX_API_KEY"
```

**Response** (200 OK)

```json
{ "enabled": true, "ports": [ … ] }
```

## Unpublish a port

`DELETE /v1/machines/{id}/ports/{port}`

Removes the URL and closes its open connections. The server in the machine keeps running.

**Path parameters**

- `id` (string, required): The machine's ID (`m_agqteugyy5px6hzeadbh4ldjo4`).
- `port` (integer, required): The port.

**Request**

```bash
curl -X DELETE https://api.instabox.sh/v1/machines/m_agqteugyy5px6hzeadbh4ldjo4/ports/3000 -H "X-API-Key: $INSTABOX_API_KEY"
```

**Response** (204 No Content)

No body.

---

# Secrets

https://instabox.sh/docs/api/secrets.md

Org credentials, sandbox selections and delivery status.

Org Secrets store encrypted values. Reads return metadata only. All members can list metadata and select credentials for authorized sandboxes. Creating, replacing, importing or deleting values requires the org owner or admin: a sign-in session or the workspace API key (workspace:admin). A personal org key and narrower keys cannot perform these writes (403 missing_scope). Read write payloads from a private JSON file. No Secret endpoint requires an Idempotency-Key.

- `GET /v1/orgs/{id}/secrets`: List Secret metadata
- `PUT /v1/orgs/{id}/secrets/{name}`: Create or replace a Secret
- `POST /v1/orgs/{id}/secrets/import`: Import Secrets atomically
- `DELETE /v1/orgs/{id}/secrets/{name}`: Delete a Secret
- `GET /v1/machines/{id}/secrets`: Inspect sandbox Secrets
- `PATCH /v1/machines/{id}/secrets`: Change sandbox selections
- `POST /v1/machines/{id}/secrets`: Refresh sandbox delivery

## The Secret object

**Properties**

- `id` (string): Stable across replacement. Deleting and recreating a name gives it a new ID.
- `orgId` (string): Owning org. Sandboxes can select only Secrets from their own org.
- `name` (string): Environment variable name, unique in the org.
- `delivery` (string): proxy or env.
- `hosts` (string[]): Allowed hosts for proxy credentials; empty for env.
- `size` (integer): Value size in bytes. The value is never returned.
- `version` (integer): Increases on replacement.
- `createdAt` (string): Creation time.
- `updatedAt` (string): Last replacement time.

## List Secret metadata

`GET /v1/orgs/{id}/secrets`

All org members. API keys require machines:read. Returns names, modes, hosts and versions, never values.

**Path parameters**

- `id` (string, required): The org ID. You must belong to this org.

**Request**

```bash
curl https://api.instabox.sh/v1/orgs/org_example/secrets -H "X-API-Key: $INSTABOX_API_KEY"
```

**Response** (200 OK)

```json
{"items":[{"id":"sec_example","orgId":"org_example","name":"SERVICE_API_KEY","delivery":"proxy","hosts":["api.example.com"],"size":24,"version":1,"createdAt":"2026-10-20T12:00:00Z","updatedAt":"2026-10-20T12:00:00Z"}]}
```

## Create or replace a Secret

`PUT /v1/orgs/{id}/secrets/{name}`

Owner/admin session or the workspace key (workspace:admin); not a personal org key. Send the value and delivery mode again on replacement. The ID stays stable. Changing delivery removes incompatible grants; switching to env never selects it for a sandbox implicitly. Reconciliation follows the save.

**Path parameters**

- `id` (string, required): The org ID. You must belong to this org.
- `name` (string, required): The Secret name, unique within the org.

**Body**

- `value` (string, required): Up to 64 KiB. Proxy values must fit in an HTTP header.
- `delivery` ("proxy" | "env", required): Explicit on every write. Proxy supplies a placeholder; env supplies the real value to explicitly selected sandboxes.
- `hosts` (string[]): Proxy requires 1–32 exact public hostnames, or "*" for every public HTTPS destination. Partial wildcards are not supported. Omit for env delivery.

**Request**

```bash
curl -X PUT https://api.instabox.sh/v1/orgs/org_example/secrets/SERVICE_API_KEY -H "X-API-Key: $INSTABOX_API_KEY" -H 'Content-Type: application/json' --data-binary @secret.json
```

**Response** (201 Created)

```json
{"id":"sec_example","orgId":"org_example","name":"SERVICE_API_KEY","delivery":"proxy","hosts":["api.example.com"],"size":24,"version":1,"createdAt":"2026-10-20T12:00:00Z","updatedAt":"2026-10-20T12:00:00Z"}
```

## Import Secrets atomically

`POST /v1/orgs/{id}/secrets/import`

Owner/admin session or the workspace key (workspace:admin); not a personal org key. All entries use the same explicit delivery mode and hosts. Validation or quota failure changes nothing. Names omitted from the batch remain unchanged. Import does not select env credentials for any sandbox. The CLI can parse a .env file into this request.

**Path parameters**

- `id` (string, required): The org ID. You must belong to this org.

**Body**

- `values` (object, required): Map of Secret names to string values.
- `delivery` ("proxy" | "env", required): Explicit on every write. Proxy supplies a placeholder; env supplies the real value to explicitly selected sandboxes.
- `hosts` (string[]): Proxy requires 1–32 exact public hostnames, or "*" for every public HTTPS destination. Partial wildcards are not supported. Omit for env delivery.

**Request**

```bash
curl -X POST https://api.instabox.sh/v1/orgs/org_example/secrets/import -H "X-API-Key: $INSTABOX_API_KEY" -H 'Content-Type: application/json' --data-binary @secrets-import.json
```

**Response** (200 OK)

```json
{"items":[{"id":"sec_example","orgId":"org_example","name":"SERVICE_API_KEY","delivery":"proxy","hosts":["api.example.com"],"size":24,"version":1,"createdAt":"2026-10-20T12:00:00Z","updatedAt":"2026-10-20T12:00:00Z"}]}
```

## Delete a Secret

`DELETE /v1/orgs/{id}/secrets/{name}`

Owner/admin session or the workspace key (workspace:admin); not a personal org key. Deletes explicit grants too. Proxy revocation completes after acknowledgement or lease expiry (at most 60 seconds). Already admitted requests can finish. Env values already copied into processes, files or snapshots remain.

**Path parameters**

- `id` (string, required): The org ID. You must belong to this org.
- `name` (string, required): The Secret name, unique within the org.

**Request**

```bash
curl -X DELETE https://api.instabox.sh/v1/orgs/org_example/secrets/SERVICE_API_KEY -H "X-API-Key: $INSTABOX_API_KEY"
```

**Response** (204 No Content)

No body.

## Inspect sandbox Secrets

`GET /v1/machines/{id}/secrets`

API keys require machines:read and sandbox access. Returns selections, metadata and independent proxy and guest delivery status. Applied means the managed configuration was installed; existing processes may still have older environment values.

**Path parameters**

- `id` (string, required): The machine's ID (`m_agqteugyy5px6hzeadbh4ldjo4`).

**Request**

```bash
curl https://api.instabox.sh/v1/machines/m_agqteugyy5px6hzeadbh4ldjo4/secrets -H "X-API-Key: $INSTABOX_API_KEY"
```

**Response** (200 OK)

```json
{"secrets":[],"envSecrets":[],"items":[],"version":1,"proxy":{"state":"pending","revision":2,"appliedRevision":1},"guest":{"state":"pending","revision":2,"appliedRevision":1,"items":[]}}
```

## Change sandbox selections

`PATCH /v1/machines/{id}/secrets`

API keys require machines:write and sandbox access. Each supplied field replaces that entire selection; omission keeps it unchanged. Null, unknown or wrong-delivery names reject the request. Selection changes do not disable Vault. Delivery updates in the background.

**Path parameters**

- `id` (string, required): The machine's ID (`m_agqteugyy5px6hzeadbh4ldjo4`).

**Body**

- `secrets` ("all" | string[]): All current and future proxy Secrets, or explicit names ([] selects none). Env Secrets are never included.
- `envSecrets` (string[]): Explicit env Secret names ([] selects none). No all mode. Code inside the sandbox can read these values.

**Request**

```bash
curl -X PATCH https://api.instabox.sh/v1/machines/m_agqteugyy5px6hzeadbh4ldjo4/secrets -H "X-API-Key: $INSTABOX_API_KEY" -H 'Content-Type: application/json' -d '{"secrets":[],"envSecrets":[]}'
```

**Response** (200 OK)

```json
{"secrets":[],"envSecrets":[],"items":[],"version":1,"proxy":{"state":"pending","revision":2,"appliedRevision":1},"guest":{"state":"pending","revision":2,"appliedRevision":1,"items":[]}}
```

## Refresh sandbox delivery

`POST /v1/machines/{id}/secrets`

API keys require machines:write and a running sandbox. Installs the selected environment and public CA and requests proxy reconciliation. Check both returned statuses. Applications must reload rotated env values; refresh cannot erase copies they already made.

**Path parameters**

- `id` (string, required): The machine's ID (`m_agqteugyy5px6hzeadbh4ldjo4`).

**Request**

```bash
curl -X POST https://api.instabox.sh/v1/machines/m_agqteugyy5px6hzeadbh4ldjo4/secrets -H "X-API-Key: $INSTABOX_API_KEY"
```

**Response** (200 OK)

```json
{"secrets":[],"envSecrets":[],"items":[],"version":1,"proxy":{"state":"pending","revision":2,"appliedRevision":1},"guest":{"state":"pending","revision":2,"appliedRevision":1,"items":[]}}
```

---

# Account

https://instabox.sh/docs/api/account.md

Templates, your usage and limits, and who a key belongs to.

Read-only facts about your account and what machines can start from.

- `GET /v1/templates`: List templates
- `GET /v1/usage`: Get usage and limits
- `GET /v1/me`: Get the current user

## List templates

`GET /v1/templates`

What a machine can start from, with the software each one has, one entry per version. `latest` marks the version a create naming the template without a `templateVersion` gets, and `default` the one a create naming no template gets. A template with `creatable` false (`hidden`) is listed only for the machines and snapshots already on it: a create naming it is refused.

**Request**

```bash
curl https://api.instabox.sh/v1/templates -H "X-API-Key: $INSTABOX_API_KEY"
```

**Response** (200 OK)

```json
{
  "templates": [
    {
      "id": "universal",
      "version": "2026-10-13.10",
      "description": "dev plus Docker, Python (uv), Go and Rust",
      "arch": "x86_64",
      "defaultSpec": { "vcpus": 4, "memMiB": 8192, "persistentDiskGiB": 20 },
      "creatable": true,
      "latest": true,
      …
    }
  ]
}
```

## Get usage and limits

`GET /v1/usage`

Your machine and snapshot counts, the data they store (measured about hourly) and your limits.

**Request**

```bash
curl https://api.instabox.sh/v1/usage -H "X-API-Key: $INSTABOX_API_KEY"
```

**Response** (200 OK)

```json
{
  "machines": 2,
  "snapshots": 1,
  "storedBytes": 6442450944,
  "computedAt": "2026-10-13T10:00:00Z",
  "limits": { "maxMachines": 5, "maxSnapshots": 10, "maxStoredGiB": 200, … },
  …
}
```

## Get the current user

`GET /v1/me`

Who the key belongs to. Any key may call it.

**Request**

```bash
curl https://api.instabox.sh/v1/me -H "X-API-Key: $INSTABOX_API_KEY"
```

**Response** (200 OK)

```json
{ "userId": 42, "login": "octocat", "admin": false, … }
```
