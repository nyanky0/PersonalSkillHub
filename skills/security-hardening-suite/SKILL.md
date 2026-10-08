---
name: security-hardening-suite
description: "Enterprise threat modeling, OWASP Top 10 defense, web pentesting, code security audit, and secret redaction."
version: 2.0.0
author: Hermes Agent & Antigravity
metadata:
  hermes:
    tags: [security, pentest, hardening, owasp, audit]
---

# Security Hardening Suite



## Sub-Module: security-and-hardening

# Security and Hardening

## Overview

安全优先的开发实践。将每个外部输入视为敌意的，每个密钥视为神圣的，每个授权检查视为强制的。安全不是一个阶段——它是每一行涉及用户数据、认证或外部系统的代码的约束�?
## When to Use

- 构建任何接受用户输入的功�?- 实现认证或授�?- 存储或传输敏感数�?- 与外�?API 或服务集�?- 添加文件上传、webhook 或回�?- 处理支付�?PII 数据

---

## Process: Threat Model First

没有威胁模型的控制是猜测。加固前，花5分钟像攻击者一样思考：

1. **映射信任边界�?* 不可信数据在哪里跨越进入系统？HTTP 请求、表单字段、文件上传、webhook、第三方 API、消息队列，以及 **LLM 输出**。每个边界都是攻击面�?
2. **命名资产�?* 什么值得窃取或破坏？凭据、PII、支付数据、管理员操作、资金转移�?
3. **对每个边界运�?STRIDE** �?快速视角，不是仪式�?
| 威胁 | 提问 | 典型缓解 |
|------|------|----------|
| **S**poofing（伪装） | 能有人冒充用�?服务吗？ | 认证、签名验�?|
| **T**ampering（篡改） | 数据能在传输或存储中被改变吗�?| 完整性检查、参数化查询、HTTPS |
| **R**epudiation（抵赖） | 行为能事后被否认吗？ | 安全事件审计日志 |
| **I**nformation disclosure（信息泄露） | 数据能泄露吗�?| 加密、字段白名单、通用错误 |
| **D**enial of service（拒绝服务） | 能被压垮吗？ | 速率限制、输入大小上限、超�?|
| **E**levation of privilege（权限提升） | 用户能获得不该有的权限吗�?| 授权检查、最小权�?|

4. **在用例旁边写滥用用例�?* 对每个功能问"我会如何误用它？"——然后让这成为你的第一个测试�?
如果你无法命名功能的信任边界，你还没准备好加固它。这�?OWASP **A04: Insecure Design** �?大多数违规始于设计，而非代码�?
**完成条件**：已输出威胁模型文档，包含信任边界图、资产清单、每个边界的 STRIDE 分析、至�?1 个滥用用例�?
---

## The Three-Tier Boundary System

### Always Do（无条件执行�?
- **验证所有外部输�?*在系统边界（API 路由、表单处理器�?- **参数化所有数据库查询** �?永远不要将用户输入拼接到 SQL
- **编码输出**防止 XSS（使用框架自动转义，不要绕过�?- **使用 HTTPS** 进行所有外部通信
- **哈希密码**使用 bcrypt/scrypt/argon2（永远不要存储明文）
- **设置安全�?*（CSP, HSTS, X-Frame-Options, X-Content-Type-Options�?- **使用 httpOnly, secure, sameSite cookies** 管理会话
- **运行 `npm audit`**（或等效工具）每次发布前

### Ask First（需要人类批准）

- 添加新认证流程或更改认证逻辑
- 存储新类别的敏感数据（PII、支付信息）
- 添加新的外部服务集成
- 更改 CORS 配置
- 添加文件上传处理�?- 修改速率限制或节�?- 授予提升权限或角�?
### Never Do（绝不做�?
- **永远不要提交密钥**到版本控制（API 密钥、密码、令牌）
- **永远不要记录敏感数据**（密码、令牌、完整信用卡号）
- **永远不要信任客户端验�?*作为安全边界
- **永远不要禁用安全�?*为了方便
- **永远不要使用 `eval()` �?`innerHTML`** 与用户提供的数据
- **永远不要存储会话**在客户端可访问的存储（localStorage 用于 auth 令牌�?- **永远不要暴露堆栈跟踪**或内部错误详情给用户

---

## OWASP Top 10 Prevention Patterns

### Injection（SQL, NoSQL, OS Command�?
```typescript
// BAD: SQL injection via string concatenation
const query = `SELECT * FROM users WHERE id = '${userId}'`;

// GOOD: Parameterized query
const user = await db.query('SELECT * FROM users WHERE id = $1', [userId]);

// GOOD: ORM with parameterized input
const user = await prisma.user.findUnique({ where: { id: userId } });
```

### Broken Authentication

```typescript
// Password hashing
import { hash, compare } from 'bcrypt';

const SALT_ROUNDS = 12;
const hashedPassword = await hash(plaintext, SALT_ROUNDS);
const isValid = await compare(plaintext, hashedPassword);

// Session management
app.use(session({
  secret: process.env.SESSION_SECRET,  // From environment, not code
  resave: false,
  saveUninitialized: false,
  cookie: {
    httpOnly: true,     // Not accessible via JavaScript
    secure: true,       // HTTPS only
    sameSite: 'lax',    // CSRF protection
    maxAge: 24 * 60 * 60 * 1000,  // 24 hours
  },
}));
```

### Cross-Site Scripting (XSS)

```typescript
// BAD: Rendering user input as HTML
element.innerHTML = userInput;

// GOOD: Use framework auto-escaping (React does this by default)
return <div>{userInput}</div>;

// If you MUST render HTML, sanitize first
import DOMPurify from 'dompurify';
const clean = DOMPurify.sanitize(userInput);
```

### Broken Access Control

```typescript
// Always check authorization, not just authentication
app.patch('/api/tasks/:id', authenticate, async (req, res) => {
  const task = await taskService.findById(req.params.id);

  // Check that the authenticated user owns this resource
  if (task.ownerId !== req.user.id) {
    return res.status(403).json({
      error: { code: 'FORBIDDEN', message: 'Not authorized to modify this task' }
    });
  }

  // Proceed with update
  const updated = await taskService.update(req.params.id, req.body);
  return res.json(updated);
});
```

### Security Misconfiguration

```typescript
// Security headers (use helmet for Express)
import helmet from 'helmet';
app.use(helmet());

// Content Security Policy
app.use(helmet.contentSecurityPolicy({
  directives: {
    defaultSrc: ["'self'"],
    scriptSrc: ["'self'"],
    styleSrc: ["'self'", "'unsafe-inline'"],  // Tighten if possible
    imgSrc: ["'self'", 'data:', 'https:'],
    connectSrc: ["'self'"],
  },
}));

// CORS �?restrict to known origins
app.use(cors({
  origin: process.env.ALLOWED_ORIGINS?.split(',') || 'http://localhost:3000',
  credentials: true,
}));
```

### Sensitive Data Exposure

```typescript
// Never return sensitive fields in API responses
function sanitizeUser(user: UserRecord): PublicUser {
  const { passwordHash, resetToken, ...publicFields } = user;
  return publicFields;
}

// Use environment variables for secrets
const API_KEY = process.env.STRIPE_API_KEY;
if (!API_KEY) throw new Error('STRIPE_API_KEY not configured');
```

### Server-Side Request Forgery (SSRF)

任何时候服务器获取用户影响�?URL �?webhook�?�?URL 导入"、图片代理、链接预�?�?攻击者可以将它指向内部服务（云元数据、`localhost`、私�?IP）�?
```typescript
// BAD: fetch whatever the user gives you
await fetch(req.body.webhookUrl);

// GOOD: allowlist scheme + host, reject if ANY resolved IP is private, forbid redirects
import { lookup } from 'node:dns/promises';
import ipaddr from 'ipaddr.js';

const ALLOWED_HOSTS = new Set(['hooks.example.com']);

async function assertSafeUrl(raw: string): Promise<URL> {
  const url = new URL(raw);
  if (url.protocol !== 'https:') throw new Error('https only');
  if (!ALLOWED_HOSTS.has(url.hostname)) throw new Error('host not allowed');
  // Resolve ALL records; a single private/reserved address fails the check.
  const addrs = await lookup(url.hostname, { all: true });
  if (addrs.some((a) => ipaddr.parse(a.address).range() !== 'unicast')) {
    throw new Error('private/reserved IP');
  }
  return url;
}

await fetch(await assertSafeUrl(req.body.webhookUrl), { redirect: 'error' });
```

`range() !== 'unicast'` 检查覆盖环回、链路本�?`169.254.169.254`（云元数据，#1 SSRF 目标）、私有和唯一本地范围�?IPv4 �?IPv6�?
**注意 �?这仍�?TOCTOU 缺口�?* `fetch` 在检查后再次解析 DNS，所以使用短 TTL 记录的攻击者可以在验证和连接之间重绑定到内�?IP。对于高风险面，解析一次并连接到固�?IP，或在前端放置过滤代理�?
---

## Input Validation Patterns

### Schema Validation at Boundaries

```typescript
import { z } from 'zod';

const CreateTaskSchema = z.object({
  title: z.string().min(1).max(200).trim(),
  description: z.string().max(2000).optional(),
  priority: z.enum(['low', 'medium', 'high']).default('medium'),
  dueDate: z.string().datetime().optional(),
});

// Validate at the route handler
app.post('/api/tasks', async (req, res) => {
  const result = CreateTaskSchema.safeParse(req.body);
  if (!result.success) {
    return res.status(422).json({
      error: {
        code: 'VALIDATION_ERROR',
        message: 'Invalid input',
        details: result.error.flatten(),
      },
    });
  }
  // result.data is now typed and validated
  const task = await taskService.create(result.data);
  return res.status(201).json(task);
});
```

### File Upload Safety

```typescript
// Restrict file types and sizes
const ALLOWED_TYPES = ['image/jpeg', 'image/png', 'image/webp'];
const MAX_SIZE = 5 * 1024 * 1024; // 5MB

function validateUpload(file: UploadedFile) {
  if (!ALLOWED_TYPES.includes(file.mimetype)) {
    throw new ValidationError('File type not allowed');
  }
  if (file.size > MAX_SIZE) {
    throw new ValidationError('File too large (max 5MB)');
  }
  // Don't trust the file extension �?check magic bytes if critical
}
```

---

## Triaging npm audit Results

不是所有审计发现都需要立即行动。使用这个决策树�?
```
npm audit reports a vulnerability
├── Severity: critical or high
�?  ├── Is the vulnerable code reachable in your app?
�?  �?  ├── YES --> Fix immediately (update, patch, or replace the dependency)
�?  �?  └── NO (dev-only dep, unused code path) --> Fix soon, but not a blocker
�?  └── Is a fix available?
�?      ├── YES --> Update to the patched version
�?      └── NO --> Check for workarounds, consider replacing the dependency, or add to allowlist with a review date
├── Severity: moderate
�?  ├── Reachable in production? --> Fix in the next release cycle
�?  └── Dev-only? --> Fix when convenient, track in backlog
└── Severity: low
    └── Track and fix during regular dependency updates
```

### Supply-Chain Hygiene

`npm audit` 捕获已知 CVE；它不会捕获恶意�?typosquatted 包。还要：

- **提交 lockfile** 并在 CI 中使�?`npm ci`（不�?`npm install`）�?可重现构建，无静默版本漂�?- **添加新依赖前审查** �?维护、下载量，以及它们是否真正值得
- **警惕 `postinstall` 脚本** 在不熟悉的包�?�?它们在安装时运行任意代码
- **注意 typosquats** �?`cross-env` vs `crossenv`，`react-dom` vs `reactdom`

---

## Rate Limiting

```typescript
import rateLimit from 'express-rate-limit';

// General API rate limit
app.use('/api/', rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 100,                   // 100 requests per window
  standardHeaders: true,
  legacyHeaders: false,
}));

// Stricter limit for auth endpoints
app.use('/api/auth/', rateLimit({
  windowMs: 15 * 60 * 1000,
  max: 10,  // 10 attempts per 15 minutes
}));
```

---

## Secrets Management

```
.env files:
  ├── .env.example  �?Committed (template with placeholder values)
  ├── .env          �?NOT committed (contains real secrets)
  └── .env.local    �?NOT committed (local overrides)

.gitignore must include:
  .env
  .env.local
  .env.*.local
  *.pem
  *.key
```

**提交前总是检查：**
```bash
# Check for accidentally staged secrets
git diff --cached | grep -i "password\|secret\|api_key\|token"
```

**如果密钥被提交，轮换它�?* 删除行或重写历史不够 �?假设它在到达远程的那一刻就被泄露了。先撤销并重新颁发密钥，然后从历史中清除�?
---

## Securing AI / LLM Features

如果你的应用调用 LLM �?聊天机器人、摘要器、代理、RAG �?它继承了新的攻击面。映射到 [OWASP Top 10 for LLM Applications (2025)](https://genai.owasp.org/llm-top-10/)�?
- **将所有模型输出视为不可信输入 (LLM05: Improper Output Handling)�?* 永远不要�?LLM 输出直接传入 `eval`、SQL、shell、`innerHTML` 或文件路径。像验证原始用户输入一样验证和编码它�?
- **假设提示可以被劫�?(LLM01: Prompt Injection)�?* 上下文窗口中的不可信文本 �?用户消息、获取的网页、PDF �?可以携带指令。系统提示不是安全边界；在代码中强制执行权限，而非在提示中�?
- **保持密钥和其他用户数据不在提示中 (LLM02 / LLM07)�?* 上下文中的任何内容都可以被回显。不要把 API 密钥、跨租户数据或完整系统提示放在模型可以重复的地方�?
- **约束工具和代理权�?(LLM06: Excessive Agency)�?* 将工具范围限定为最小，对破坏性或不可逆操作要求确认，并验证每个工具参数�?
- **绑定消费 (LLM10: Unbounded Consumption)�?* 上限令牌、请求速率和循�?递归深度，使精心设计的输入不会产生高昂费用或挂起系统�?
- **隔离检索数�?(LLM08: Vector and Embedding Weaknesses)�?* �?RAG 中，将向量存储视为信任边界：按租户分区嵌入，使一个用户无法检索另一个用户的数据，并在索引前验证文档，使中毒内容无法引导答案�?
```typescript
// BAD: trusting model output as a command or as markup
const sql = await llm.generate(`Write SQL for: ${userQuestion}`);
await db.query(sql);                                   // arbitrary query execution
container.innerHTML = await llm.reply(userMessage);   // stored XSS, via the model

// GOOD: model output is data �?parse defensively, then validate, then encode
let intent;
try {
  intent = CommandSchema.parse(JSON.parse(await llm.replyJson(userMessage)));
} catch {
  throw new ValidationError('unexpected model output'); // JSON.parse or schema failed
}
await runAllowlistedAction(intent.action, intent.params);
container.textContent = await llm.reply(userMessage);
```

---

## Security Review Checklist

```markdown
### Authentication
- [ ] Passwords hashed with bcrypt/scrypt/argon2 (salt rounds �?12)
- [ ] Session tokens are httpOnly, secure, sameSite
- [ ] Login has rate limiting
- [ ] Password reset tokens expire

### Authorization
- [ ] Every endpoint checks user permissions
- [ ] Users can only access their own resources
- [ ] Admin actions require admin role verification

### Input
- [ ] All user input validated at the boundary
- [ ] SQL queries are parameterized
- [ ] HTML output is encoded/escaped
- [ ] Server-side URL fetches are allowlisted (no SSRF to internal services)

### Data
- [ ] No secrets in code or version control
- [ ] Sensitive fields excluded from API responses
- [ ] PII encrypted at rest (if applicable)

### Infrastructure
- [ ] Security headers configured (CSP, HSTS, etc.)
- [ ] CORS restricted to known origins
- [ ] Dependencies audited for vulnerabilities
- [ ] Error messages don't expose internals

### Supply Chain
- [ ] Lockfile committed; CI installs with `npm ci`
- [ ] New dependencies reviewed (maintenance, downloads, postinstall scripts)

### AI / LLM (if used)
- [ ] Model output treated as untrusted (no eval/SQL/innerHTML/shell)
- [ ] Secrets and other users' data kept out of prompts
- [ ] Tool/agent permissions scoped; destructive actions require confirmation
```

---

## Common Rationalizations

| 借口 | 现实 |
|------|------|
| "这是内部工具，安全不重要" | 内部工具会被攻破。攻击者针对最弱环节�?|
| "我们稍后添加安全" | 安全改造比内置�?0倍。现在就添加�?|
| "没人会尝试利用这�? | 自动化扫描器会发现它。隐晦安全不是安全�?|
| "框架处理安全" | 框架提供工具，不是保证。你仍需要正确使用它们�?|
| "这只是原�? | 原型变成生产。从第一天开始的安全习惯�?|
| "威胁建模在这里过�? | 5分钟�?我会如何攻击这个�?防止设计缺陷，没有控制能修补�?|
| "这只�?LLM 输出，只是文�? | 那个"文本"可以�?SQL 语句、脚本标签或 shell 命令。像任何不可信输入一样对待它�?|

---

## Red Flags

- 用户输入直接传递到数据库查询、shell 命令�?HTML 渲染
- 源代码或提交历史中的密钥
- 没有认证或授权检查的 API 端点
- 缺失 CORS 配置或通配�?(`*`) �?- 认证端点没有速率限制
- 堆栈跟踪或内部错误暴露给用户
- 已知严重漏洞的依�?- 服务器获取用户提供的 URL 没有白名单（SSRF�?- LLM/模型输出传入查询、DOM、shell �?`eval`
- 密钥、PII 或完整系统提示放�?LLM 上下文窗口中

---

## Verification

实现安全相关代码后：

- [ ] `npm audit` 显示无严重或高漏�?- [ ] 源代码或 git 历史中无密钥
- [ ] 所有用户输入在系统边界验证
- [ ] 每个受保护端点检查认证和授权
- [ ] 响应中存在安全头（用浏览�?DevTools 检查）
- [ ] 错误响应不暴露内部详�?- [ ] 认证端点有速率限制
- [ ] 服务器端 URL 获取针对白名单验证（�?SSRF�?- [ ] LLM/模型输出在使用前验证和编码（如有 AI 功能�?
---

## See Also

- `debugging-and-error-recovery` �?错误处理与安全输�?- `ci-cd-and-automation` �?CI/CD 安全�?- `skill-vetter` �?技能安全审�?

---

## Sub-Module: web-pentest

# Web Application Penetration Testing

A phased pentesting workflow for running web applications. Adapted from
Shannon's pipeline (Keygraph, AGPL — concepts only, no code borrowed).
Built around three rules:

1. No exploit, no report — every finding requires reproducible evidence.
2. Bounded scope — every active request goes against a target the operator
   pre-declared. Off-scope hosts are refused.
3. Bypass exhaustion before false-positive dismissal — a "blocked" payload
   is not a clean bill of health until you've tried the bypass set.

---

## ⚠️ Hard Guardrails — Read Before Every Engagement

Violating any of these invalidates the engagement and may be illegal.

1. **Authorization gate.** Before the first active scan in a session, you
   MUST confirm with the user, in writing, that they own or have written
   authorization to test the target. Record the acknowledgement in
   `engagement/authorization.md` (see template). No acknowledgement → no
   active scanning. Reading public pages with `curl` is fine; sending
   payloads is not.

2. **Scope allowlist.** Maintain `engagement/scope.txt` — one hostname or
   CIDR per line. Every `nmap`, `curl`, `whatweb`, browser navigation, or
   payload-bearing request MUST be against an entry in scope. If a target
   redirects you off-scope (3xx to a different host, a link in HTML),
   STOP and confirm with the user before following.

3. **No production systems without paper.** If the user hasn't told you
   "yes, prod is in scope and I have written sign-off," assume not. Default
   targets are staging, local docker, dedicated test instances.

4. **Cloud metadata is off by default.** Do not probe `169.254.169.254`,
   `metadata.google.internal`, `100.100.100.200`, `[fd00:ec2::254]`, or
   equivalent unless the engagement explicitly includes SSRF-to-metadata
   as a goal AND the target is one you control. The agent's browser tool
   can reach these from inside your own infrastructure — don't.

5. **Destructive payloads need approval.** SQLi payloads that DROP/DELETE,
   filesystem-write SSTI, command injection with `rm`/`shutdown`/`mkfs`,
   anything that mutates beyond a single test row → ASK FIRST. The
   `approval.py` system catches some; don't rely on it alone.

6. **Aux-client leakage risk (Hermes-specific).** This skill produces
   sessions full of SQLi/XSS/RCE payloads, captured credentials, JWT
   tokens. Hermes' compression and title-generation paths replay history
   through the auxiliary client (often the main model). Anything sensitive
   you write to the conversation can leave the box on the next compress.
   Mitigation:
   - Redact captured tokens/credentials to the LAST 6 CHARS before logging
     them in any message. Full values go to `engagement/evidence/` files,
     never into chat history.
   - If the engagement is sensitive, set `auxiliary.title_generation.enabled: false`
     in `~/.hermes/config.yaml` for the session.

7. **Rate limit yourself.** Default 200ms between active requests against
   any single host. The recon-scan.sh script enforces this. Don't bypass
   it without operator approval.

8. **Authority of the report.** This skill produces a security
   assessment, not a "PASS." Even a clean run is "no exploitable issues
   FOUND in scope X within time T using methods Y" — not "the application
   is secure." Mirror that language in the report.

---

## Phase 0: Engagement Setup

Before any scanning happens, create the engagement directory and
authorization acknowledgement.

```bash
ENGAGEMENT=engagement-$(date +%Y%m%d-%H%M%S)
mkdir -p "$ENGAGEMENT"/{evidence,findings,reports}
cd "$ENGAGEMENT"
```

1. **Ask the user (verbatim):**
   > "Confirm: (a) the target URL is [X], (b) you own this application
   > or have written authorization to test it, and (c) the engagement
   > may run for up to [N] hours starting now. Reply 'authorized' to
   > proceed."

2. **Wait for explicit `authorized` response.** Any other answer means STOP.

3. **Record authorization** to `engagement/authorization.md` using the
   template in `templates/authorization.md`. Include:
   - Target URL(s) and IP(s)
   - Authorization basis (ownership / written authz from $name)
   - Engagement window
   - Out-of-scope items (production, third-party services, etc.)
   - Operator name (the user driving this session)

4. **Build scope.txt:**
   ```
   localhost
   127.0.0.1
   staging.example.com
   192.168.1.0/24    # internal lab only, with operator OK
   ```

5. **Read** `references/scope-enforcement.md` before issuing the first
   active request — that doc has the host-extraction rules you apply
   to every command/URL before it goes out.

---

## Phase 1: Pre-Recon (Code Analysis, optional)

Skip if no source access (black-box engagement).

If you have read access to the application source:

1. **Map the architecture** — framework, routing, middleware stack
2. **Inventory sinks** — every `execute(`, `os.system(`, `eval(`,
   template render, file read/write, redirect target
3. **Map auth** — session cookie vs JWT, OAuth flows, password reset,
   privileged endpoints
4. **Identify trust boundaries** — what's authenticated, what's not,
   what comes from `request.*`
5. **Backward taint** from each sink to a request source. Early-terminate
   when proper sanitization is found (parameterized queries, allowlists,
   `shlex.quote`, well-known escapers).

Output: `evidence/pre-recon.md` — architecture map, sink inventory,
suspected vulnerable code paths.

This is OFFLINE work. No traffic to the target.

---

## Phase 2: Recon (Live, Read-Only)

Maps the attack surface. All requests are GETs of public pages, no
payloads yet. Still scope-bounded.

1. **Verify scope.** Resolve every target hostname → IP. Confirm IPs are
   in scope (avoids the "DNS points somewhere unexpected" trap).

2. **Network surface** (only if scope permits port scanning):
   ```bash
   nmap -sT -T3 --top-ports 100 -oN evidence/nmap.txt $TARGET
   ```
   Use `-T3` (default), not `-T4/-T5`. Stealthier and avoids tripping
   IDS/IPS in shared environments.

3. **Tech fingerprint:**
   ```bash
   whatweb -v $TARGET_URL > evidence/whatweb.txt
   curl -sIk $TARGET_URL > evidence/headers.txt
   ```

4. **Endpoint discovery:**
   - Crawl the app with the browser tool (`browser_navigate`,
     `browser_get_images`, follow links).
   - Inspect `robots.txt`, `sitemap.xml`, `.well-known/*`.
   - Use the developer tools network panel via browser tool to capture
     XHR/fetch calls.

5. **Auth surface:** Identify login, registration, password reset,
   session cookie names, token formats. Do NOT send credentials yet —
   just observe.

6. **Correlate with pre-recon** (if you have source). For each
   `evidence/pre-recon.md` finding, mark whether the live surface
   confirms it's reachable.

Output: `evidence/recon.md` — endpoints, technologies, auth model,
input vectors.

---

## Phase 3: Vulnerability Analysis

One delegate_task per vulnerability class. Each agent reads
`evidence/recon.md` (+ `evidence/pre-recon.md` if present), produces
`findings/<class>-queue.json` using `templates/exploitation-queue.json`.

Use `delegate_task` with these focused subagents (parallel where possible):

| Class | Goal | Reference |
|-------|------|-----------|
| `injection` | SQLi, command, path traversal, SSTI, LFI/RFI, deserialization | `references/vuln-taxonomy.md` (slot types) |
| `xss` | Reflected, stored, DOM-based | `references/vuln-taxonomy.md` (render contexts) |
| `auth` | Login bypass, JWT confusion, session fixation, OAuth flaws | `references/exploitation-techniques.md` |
| `authz` | IDOR, vertical/horizontal escalation, business logic | `references/exploitation-techniques.md` |
| `ssrf` | Internal reachability, metadata, protocol smuggling | Skip metadata unless explicitly authorized |
| `infra` | Misconfig, info disclosure, default creds, exposed admin | `references/exploitation-techniques.md` |

Each queue entry has: id, vuln class, source (file:line if known),
endpoint, parameter, slot type, suspected defense, verdict
(`identified` / `partial` / `confirmed` / `critical`), witness payload,
confidence (0-1), notes.

The analysis phase doesn't send malicious payloads yet — it stages them.
The exploitation phase actually fires them.

---

## Phase 4: Exploitation (Proof-Based, Conditional)

Only run a sub-agent per class where the analysis queue has actionable
entries (`identified` or `partial`).

For each candidate:

1. **Pre-send check** — host in scope? auth gate satisfied? payload
   approved if destructive?
2. **Send the witness payload** — minimal proof. SQLi: `' AND 1=1--`
   then `' AND 1=2--`. XSS: a benign marker like
   `<svg/onload=console.log("HERMES-PENTEST-XSS")>`. Never `alert(1)` in
   stored XSS — it'll fire for other users in shared environments.
3. **Verify the witness fires** — for blind injection, use a sleep
   probe (`SLEEP(5)`) and time the response. For SSRF, use a
   tester-controlled callback host you own (NOT a public service like
   webhook.site for sensitive engagements — exfil paths).
4. **Promote level:**
   - **L1 Identified** — pattern matched, no behavior change
   - **L2 Partial** — sink reached, but defense in place
   - **L3 Confirmed** — payload changed app behavior in observable way
   - **L4 Critical** — data extracted, code executed, access escalated
5. **Bypass exhaustion before classifying as FP.** For each candidate
   that blocks: try at least the bypass set in
   `references/bypass-techniques.md` for that class. Only after the set
   is exhausted may you write `verdict: false_positive`.
6. **Record evidence** for every L3/L4:
   - Full request (method, URL, headers, body)
   - Response (status, headers, relevant body excerpt)
   - Reproducer command (curl one-liner)
   - Impact statement

Output: `findings/exploitation-evidence.md`

**Redact in evidence files:**
- Any captured credentials/tokens → last 6 chars only in chat;
  full value to `findings/secrets-vault.md` (gitignored).
- Other users' PII → redact.
- Your test credentials → fine to keep.

---

## Phase 5: Reporting

Generate the final report using `templates/pentest-report.md`. Sections:

1. Executive summary
2. Engagement scope (from `engagement/scope.txt`)
3. Authorization (from `engagement/authorization.md`)
4. Findings (L3/L4 only — proof-required). Per finding:
   - Title, severity (CVSS 3.1), CWE
   - Affected endpoint(s)
   - Proof (request + response excerpt)
   - Reproduction steps
   - Impact
   - Remediation
5. Not-exploited candidates (L1/L2 with notes on what blocked them)
6. Out-of-scope observations
7. Methodology / tools used
8. Limitations and what was NOT tested

**Severity policy:** CVSS only for L3/L4. L1/L2 are "candidates pending
verification" — don't assign CVSS to unverified findings.

---

## When to Stop

- The user revokes authorization.
- A candidate finding clearly impacts production data and you don't have
  approval for destructive testing — STOP and ask.
- The target starts returning 503/429 storms — back off, reconvene with
  the operator.
- You discover something *outside* the contracted scope (e.g. an exposed
  customer database while testing an unrelated endpoint). STOP, document,
  report to the operator. Do not pivot without explicit approval — that
  pivot is what makes pentesting illegal.

---

## What This Skill Does NOT Cover

- Network-layer pentesting beyond port scanning (no Metasploit,
  Cobalt Strike, AD attacks, network protocol fuzzing).
- Reverse engineering / binary analysis (see issue #383).
- Source-only static analysis (see issue #382).
- Active social engineering / phishing.
- Anything against systems the operator hasn't pre-authorized.

If the engagement needs any of these, escalate to a professional
pentester. This skill complements professional pentesting; it does
not replace it.

---

## Further Reading

- `references/scope-enforcement.md` — how to bound every active request
- `references/vuln-taxonomy.md` — slot types, render contexts, OWASP map
- `references/exploitation-techniques.md` — per-class payload patterns
- `references/bypass-techniques.md` — common WAF/filter bypasses
- `templates/authorization.md` — engagement authorization template
- `templates/pentest-report.md` — final report template
- `templates/exploitation-queue.json` — per-class finding queue schema
- `scripts/recon-scan.sh` — rate-limited nmap+whatweb+headers wrapper

---

## Sub-Module: security-audit

# Security Audit

You are a security auditor. Your job is to find **exploitable vulnerabilities with real impact**.

## Platform terminology

This skill is agent-neutral. In the methodology:

- **Task tool** means the coding agent's delegation or sub-agent mechanism.
- **`research` agent** means a delegated agent optimized for focused codebase exploration and factual verification.
- **`general` agent** means a delegated agent that can investigate broadly and spawn focused research agents.
- **`subagent_type`** means the equivalent delegated-agent role supported by the current platform.

Use the platform's equivalent capabilities while preserving the specified roles, parallelism, prompts, and independence boundaries.

## Setup

Before starting, establish two paths:
- **Target**: the codebase to audit (from the user's request or the current working directory)
- **Output directory**: where all audit artifacts go. Ask the user if not specified, or default to `~/security-audit-skill/<repo-name>/run-<N>` where `<N>` is the next unused integer (check what exists with `ls`). Create it if it doesn't exist. This ensures multiple runs against the same repo produce separate results.

All files written during the audit go in the output directory:
- `architecture.md` — Phase 1 output, fed into Phase 2 agent prompts
- `REPORT.md` — human-readable report (Phase 4)
- `FINDINGS-DETAIL.md` — detailed data flows for MEDIUM+ findings (Phase 4)
- `findings.json` — machine-readable structured output (Phase 5)

Subagents (Phases 1, 2, 3, 6) do NOT write files — they return results to you via the Task tool. You are responsible for writing all files to the output directory.

### Coverage and prior runs

Each audit run explores different code paths depending on which agents find what and where they dig. No single run finds everything. Testing shows the best single run finds roughly half the total vulnerabilities across multiple runs.

**If prior runs exist** for the same repo (check `~/security-audit-skill/<repo-name>/`), read their `findings.json` files before starting Phase 2. Use them to:
1. **Skip known findings** — don't waste agents re-discovering the same status bypass. Mention prior findings in the report but focus hunting effort on new ground.
2. **Target gaps** — if prior runs focused heavily on injection and auth, weight this run toward business logic, creative attacks, and the wildcard agent. If prior runs missed public endpoints, focus there.
3. **Resolve disagreements** — if prior runs gave conflicting verdicts on the same finding, validate it definitively.

Include a brief summary of prior runs in the architecture summary so Phase 2 agents know what's already been found.

**If no prior runs exist**, note in the report that coverage improves with additional runs and recommend the user run the audit again to catch findings this run may have missed.

## Core Principles

### Only report what you can exploit

Every finding must have a concrete attack scenario: who is the attacker, what do they do, and what do they get? "An attacker could theoretically..." is not a finding. "Send this request, get this result" is.

### Confirm dynamically when you can

This is a source-first audit, but a claim you can execute beats one you can only argue. Where the target is locally buildable — a parser, a library, a CLI, a native component — build and run it: reproduce the crash, run the payload, diff the two parsers on the same bytes. Better still, **extract the suspect code into a minimal standalone harness** and test the hypothesis in isolation — fuzz the one function, feed it the crafted input, watch what it does. Where confirmation needs infrastructure you don't have — a proxy chain, a live cache, production auth — you cannot confirm from source alone: mark it "requires deployment testing" and do not report it as confirmed. Dynamic evidence is what resolves the memory-safety and request-framing classes that static reading leaves ambiguous.

### Determine the baseline dynamically

In Phase 1, identify what this application is and what comparable applications exist. Use those comparables to calibrate -- not to dismiss findings, but to focus effort. If the comparable has the same pattern and it's been exploited there, that's a STRONGER finding, not a weaker one. If the comparable has the same pattern and nobody's ever exploited it in 20 years, you should understand why before reporting it.

Do NOT hardcode a specific comparable. A CMS gets compared to other CMSes. An API gateway gets compared to other API gateways. A novel application may have no meaningful comparable.

### Defense-in-depth gaps are not vulnerabilities

If Layer A prevents the attack, the absence of Layer B is a hardening note, not a finding. Report it separately if you want, but do not inflate its severity.

### Severity requires impact

Severity is the combination of **likelihood** (how easy to exploit, what access is needed) and **impact** (what damage is achieved). Use both axes:

- **CRITICAL**: Unauthenticated RCE, full database dump, admin account takeover without credentials
- **HIGH**: Authenticated RCE, SQL injection with data exfiltration, stored XSS that fires for all users, auth bypass. Also: any finding where the RBAC/permission model is *completely* defeated for an action — e.g., a user can perform an action that the system explicitly gates behind a higher role, and the action has real consequences (publishing content, deleting resources, modifying other users' data).
- **MEDIUM**: Targeted XSS requiring specific conditions, CSRF with meaningful state change, information disclosure of secrets/credentials. Also: business logic bypasses with real but limited consequences — e.g., the action is possible but requires authentication, or the impact is confined to the attacker's own data, or the bypass requires uncommon conditions.
- **LOW**: Information disclosure of non-secret data, DoS requiring sustained effort
- **INFORMATIONAL**: A confirmed but minimal-impact observation with no standalone exploit — useful mainly as a building block for another finding. Pure defense-in-depth gaps belong in hardening notes, not here.

The key distinction between HIGH and MEDIUM for business logic findings: **does the finding defeat an explicit security boundary?** Defeating one — acting past a role the system explicitly enforces — is HIGH; a data inconsistency, a finding that requires privileged access to exploit, or one with limited blast radius is MEDIUM.

If you cannot describe the concrete damage an attacker achieves, the severity is probably lower than you think.

The principles are enforced operationally by the **validation rules in [HUNTING.md](HUNTING.md)** — the canonical bar every hunter applies before reporting a finding, and that Phase 3 re-applies adversarially. The domain companion files add domain-specific checks on top of that bar; they do not replace it.

Stack-specific: for Laravel targets (incl. React + Inertia.js frontends), load companion skills `laravel-security-audit` (failure patterns incl. Inertia over-shared props, dead 2FA, webhook optional HMAC) and `laravel-security-hardening` (verified fix patterns) — they carry the Laravel/Inertia checklists this hub doesn't duplicate.

## Workflow overview

Follow all six phases in order:

1. **Recon** — Run Phase 1 from [RECONNAISSANCE.md](RECONNAISSANCE.md) to map the application's architecture, trust boundaries, and input surfaces.
2. **Hunt** — Use [HUNTING.md](HUNTING.md) for Phase 2 orchestration, methodology, and validation rules; select scopes from [ATTACK-CLASSES.md](ATTACK-CLASSES.md), which routes native, AI/LLM, HTTP-protocol/auth, and client-side targets to specialized companion files ([MEMORY-SAFETY-AND-BINARY.md](MEMORY-SAFETY-AND-BINARY.md), [AI-AND-LLM.md](AI-AND-LLM.md), [WEB-PROTOCOL-AND-AUTH.md](WEB-PROTOCOL-AND-AUTH.md), [CLIENT-SIDE.md](CLIENT-SIDE.md)).
3. **Validate** — Use Phase 3 in [VALIDATION-AND-REPORTING.md](VALIDATION-AND-REPORTING.md) to consolidate duplicates and independently try to disprove every finding.
4. **Report** — Use Phase 4 in [VALIDATION-AND-REPORTING.md](VALIDATION-AND-REPORTING.md) to write `REPORT.md` and `FINDINGS-DETAIL.md`.
5. **Structured output** — Use Phase 5 in [VALIDATION-AND-REPORTING.md](VALIDATION-AND-REPORTING.md), `report-schema.json`, and `validate-findings.cjs` to write and validate `findings.json`.
6. **Independent verification** — Use Phase 6 in [VALIDATION-AND-REPORTING.md](VALIDATION-AND-REPORTING.md) to verify every factual claim and reconcile all outputs.

## Anti-Patterns to Avoid

These are the mistakes that make security audits useless:

1. **Listing everything that deviates from OWASP as a finding.** OWASP is a checklist, not a bug list. Every real application makes tradeoffs.
2. **Rating defense-in-depth gaps as HIGH/CRITICAL.** "Missing validateIdentifier where the query builder already quotes identifiers" is not HIGH severity.
3. **Ignoring the deployment model.** Rate limiting at the CDN layer is a valid architecture. Not every app needs application-level rate limiting.
4. **Treating designed behavior as a bug.** Understand the trust model before auditing. If the design says admins are fully trusted, admin-does-admin-things is not a finding.
5. **Padding the report with LOW findings to look thorough.** Ten LOWs don't make a useful report. Three MEDIUMs do.
6. **"Potential" findings without proof.** Either you can exploit it or you can't. If you need the word "potentially" or "theoretically", you haven't done enough research.
7. **Ignoring what the codebase does well.** If auth is solid, say so. It builds trust in the findings you DO report and helps the team prioritize.
8. **Constructing exploits from incorrect parser/runtime assumptions.** The most convincing false positives come from reasoning "the parser/runtime will interpret this as..." without verifying. If your exploit depends on parser or runtime behavior, cite the spec or test it. Don't assume.
9. **Skipping business logic and creative attacks.** The standard vulnerability classes (SQLi, XSS, SSRF) are what every scanner checks. The value of a manual audit is finding the things scanners can't: logic errors, state machine violations, chained attacks, implicit trust assumptions.
10. **Giving up too easily.** "The codebase uses parameterized queries so there's no SQL injection" is a lazy conclusion. Check EVERY use of sql.raw(). Check dynamic identifiers. Check search/FTS. Check if there's a code path that bypasses the query builder. Push.

---

## Sub-Module: secret-redaction

# Secret Redaction from Hermes Session DB

A secret typed into chat persists in `~/.hermes/state.db` (messages table, FTS indexes, WAL). Redaction is possible but has a self-reference trap.

## Core pitfall (read first)
Every tool call you make is itself stored in the DB (in `messages.tool_calls`), and your reasoning in `messages.reasoning` / `messages.reasoning_content`. If your cleanup command contains the secret literal, you write NEW copies while deleting old ones — an endless loop. Fix: build the pattern at runtime so the literal never appears in any command:

```python
pw = ''.join(map(chr,[77,117,109,97]))  # char codes, literal never in command
```

## Procedure
1. Never repeat the secret in replies or commands. Refer to it as "the string".
2. Run `scripts/redact_secret.py CODES` where CODES = comma-separated decimal char codes of the secret (e.g. `77,117,109`). The script does the full sweep.
3. Manual equivalent (if script unavailable):
   - `UPDATE messages SET content=replace(content,?,'[REDACTED]'), tool_calls=replace(tool_calls,?,'[REDACTED]') WHERE ... LIKE ?` — sweep BOTH columns, plus check `reasoning` and `reasoning_content` (they store chain-of-thought; they leak too).
   - Generic sweep: iterate ALL tables × ALL text columns via `sqlite_master` + `PRAGMA table_info`, not just tables you remember.
4. Rebuild FTS — plain UPDATE does NOT fix external-content FTS5 tables:
   ```sql
   DELETE FROM messages_fts;
   INSERT INTO messages_fts(messages_fts) VALUES('rebuild');
   INSERT INTO messages_fts_trigram(messages_fts_trigram) VALUES('rebuild');
   ```
   If `messages_fts_trigram` points at a missing/dangling content table (`..._src`), DROP and recreate it with `content='messages', content_rowid='id', tokenize='trigram'`.
5. `PRAGMA wal_checkpoint(TRUNCATE)` then `VACUUM` — without these, old bytes survive in the WAL and in freed pages of the main file.
6. Verify by counting raw bytes in the files, not just SQL rows:
   ```python
   open('state.db','rb').read().count(pw.encode())
   ```
   Must be 0 for both `state.db` and `state.db-wal`.

## Why repeats appeared
Each verification command (`strings ... | grep <literal>`) re-persisted the literal into tool_calls. Verify with runtime-built pattern only, e.g. `data.count(pw.encode())` in Python.

## Caveats
- The on-screen CLI render of the live session still shows the string until the session closes; only the persisted DB can be cleaned.
- After redaction, advise the user to rotate the secret anyway — you cannot prove zero copies (backups, other DBs like mnemosyne, gateway logs).
- Check sibling stores if relevant: `~/.hermes/mnemosyne/data/**/*.db`, gateway logs.

## Policy
Never accept or type user passwords — even when offered. If a sudo-requiring task comes up, hand the user the command to run themselves, or set up a passwordless sudoers rule for that specific command.

---