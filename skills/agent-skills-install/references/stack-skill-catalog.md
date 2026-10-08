# Ecosystem skill catalog for this user's integration stack

Curated from a real `npx skills find` session. The user builds Laravel+Inertia.js
websites fronting a C#/.NET desktop app + Huawei Cloud integration hub that pushes
data to SAP B1 Service Layer. Prefer these known-good packages (all 1K-21K installs,
official/established repos) when the user needs a skill for any of the domains.

Syntax: `npx skills add "<owner/repo>@<skill>" -g -y` (one per invocation).

## Laravel / Inertia.js (website)
| Skill | repo | installs | note |
|---|---|---|---|
| laravel-specialist | jeffallan/claude-skills | 21.2K | general Laravel patterns |
| laravel-inertia-react | asyrafhussin/agent-skills | 1.5K | **Laravel+Inertia+React specifics** — most on-target for this user |
| laravel-best-practices | laravel/boost (official) | 1.2K | official Laravel guidance |
| laravel-security / -patterns / -tdd | affaan-m/ecc | 7-9K each | optional security/testing |

## C# / .NET (desktop app)
| Skill | repo | installs |
|---|---|---|
| dotnet-best-practices | github/awesome-copilot | 14.6K |
| dotnet-backend-patterns | wshobson/agents | 17.2K |
| dotnet-design-pattern-review / dotnet-upgrade | github/awesome-copilot | 10-11K |
| dotnet-core-expert | jeffallan/claude-skills | 4K |

## Huawei Cloud (cloud hosts for desktop app + SAP B1)
| Skill | installs | note |
|---|---|---|
| huawei-cloud-find-skills | 4.8K | umbrella/gateway, official huaweicloud repo |
| huawei-cloud-iam-query | 4.7K | IAM / credential / API-key management |
| huawei-cloud-obs-upload | 4.7K | object-storage upload |
| huawei-cloud-network-query | 4.7K | VPC/security-group between VMs |
| huawei-cloud-* (billing, terraform, computing, storage) | 4.7K | siblings in same repo |

Note: the huaweicloud repo has a few SKILL.md files that fail YAML parse (e.g.
`edge/cdn/huawei-cloud-cdn-dns-resolution-diagnosis`). The CLI prints "Skipped —
YAML parse error" and moves on; those specific skills just won't install. Pick other
huawei-cloud-* skills instead.

## API gateway / integration hub (auth for external LAN users)
| Skill | repo | installs | note |
|---|---|---|---|
| api-gateway | maton-ai/api-gateway-skill | 1.3K | API key / gateway config for the integration hub |
| openapi-spec-generation | wshobson/agents | 14.5K | generate the hub's OpenAPI spec |
| openapi-to-application-code | github/awesome-copilot | 9.3K | scaffold client/server from spec; use to build the C#→SL SAP B1 client |

For SAP B1 Service Layer itself, DO NOT install ecosystem SAP skills — the user's
custom pack (`sap-b1`, `sap-b1-sl-api`, `sap-b1-db`, ...) already covers it and is
more complete. Same for `find-skills` / `ui-ux-pro-max` etc. already installed.