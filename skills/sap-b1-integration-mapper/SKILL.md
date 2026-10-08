---
name: sap-b1-integration-mapper
description: "Use when documenting SAP Business One (SAP B1) integration — Service Layer / OData endpoints, HTTPS calls, B1SESSION/ROUTEID session handling, payl..."
---

# SAP B1 Endpoint & Integration Mapper

## Overview

**Core principle:** Every integration endpoint becomes one auditable row that links *trigger → request payload → response contract → error/recovery*, so a developer or business analyst can reproduce the call without guessing field names.

Works for Service Layer (`/b1s/v2`), OData, and custom endpoints. Combined with UDF payloads (`U_SOL_*` fields) as the mapping spec for the add-on docs.

## Mapping Template — One Row Set per Endpoint

```markdown
## Endpoint: POST /b1s/v2/PurchaseOrders  (Purchase Orders)

| Aspek | Nilai |
|---|---|
| Method / Path | POST /b1s/v2/PurchaseOrders |
| Sumber panggil (Trigger) | Approval final → Auto-post (SAP_B1_AUTO_POST) |
| Fungsi kode | `SapB1Service::createDocument` / `buildDocumentPayload($transaction)` |
| Auth / Session | B1SESSION + ROUTEID (TTL 25 menit, Redis) |
| Auth Ulang | HTTP 401 → re-login exponential backoff |

### Request Payload — Field Map
| Field (JSON) | Sumber / Sumber Data | Tipe | Wajib? |
|---|---|---|---|
| CardCode | `transactions.vendor_code` | string | Ya |
| DocDate | `transactions.doc_date` | date | Ya |
| U_SOL_WebTxId | `transactions.id` | int | Opt (UDF_ON) |
| DocumentLines[].ItemCode | `transaction_items.item_code` | string | Ya |

### Response Contract
| Kode | Makna | Aksi sistem |
|---|---|---|
| 201 | Created (DocEntry) | Simpan `sap_doc_entry`, status → SYNCED |
| 400 | Payload invalid | Log + retry manual |
| 401 | Session expired | Re-login, retry |
| 500 | Server/service error | Monitor `sap-sync` |

### Reversal / Update
- **Update** dokumen: PUT `/b1s/v2/PurchaseOrders({DocEntry})`
- **Cancel**: POST `PurchaseOrders('Cancel'=key)` / `CancelDocument`
- **Retry**: bulk-retry dari SAP Sync Monitor `/sap-sync`.
```

## Steps

1. **Locate integration code**: `SapB1Service`, `buildDocumentPayload`, `routes/api.php`, C# OData calls, `.env` `SAP_B1_*`.
2. **Capture the trigger** that initiates the call (button, approval, cron).
3. **Document auth/session handling** (token, TTL, refresh strategy).
4. **Build field-by-field request map** — every JSON property traced to its source attribute or literal.
5. **Record the response contract** — status codes, success fields (DocEntry, DocNum), error body, and what the app does next.
6. **Include lifecycle ops** — update/cancel/retry/undo, plus toggle-dependence (`SAP_ENABLE_CUSTOM_UDF` for `U_SOL_*`).
7. **Flag PII/credentials** — never write real passwords, tokens, or connection strings into the output; reference `.env` keys only.

## Rules

1. **Field fidelity:** property name must match JSON exactly (`DocumentLines` not `lines`); source attribute matches the model column.
2. **Optionality:** mark `Wajib?` per mode — a field required in UDF mode may be optional in standard mode. Tie to the toggle.
3. **Always pair request with response** — never ship a payload map without the response/error contract.
4. **Trace where each value comes from**: model, session, literal default, or computed (hash like `U_SOL_QRVerifyHash`).
5. **Provider-neutral naming** where providers exist (e.g. exchange rate, series retrieval as service actions).

## Quick reference

| Deliverable | Shape |
|---|---|
| Request map | table: JSON field → source → type → required? |
| Response contract | table: code → meaning → app action |
| Session handling | bullet: token, TTL, refresh/backoff |
| Lifecycle | bullets: update / cancel / retry / undo |

## Common mistakes

- Documenting payload without the response/error contract.
- Writing `lines` shorthand instead of exact JSON key.
- Leaking credentials/connection strings into the spec.
- Marking fields required without checking the UDF toggle.
- Ignoring session (401) recovery — the app's backoff is part of the contract.