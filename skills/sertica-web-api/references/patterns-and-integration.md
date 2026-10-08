# SERTICA Web API — integration patterns

Everything below is read out of the captured OpenAPI spec (`assets/sertica-swagger.json.gz`,
2,743 paths / 3,340 operations / 1,104 schemas) plus one live reachability probe. Anything not
verifiable from the spec is marked **UNVERIFIED** — check it against the target environment.

## 1. Environment

| Item | Value |
|---|---|
| Base URL | `https://indobaruna-test.sertica.com/api` |
| Spec (source of truth) | `https://indobaruna-test.sertica.com/api/swagger/v1/swagger.json` |
| Swagger UI | `https://indobaruna-test.sertica.com/api/swagger/index.html` (JS-rendered — a plain HTTP fetch returns an empty shell) |
| Auth scheme | OpenAPI `Bearer` (http bearer, JWT) — every operation sets `security: [{Bearer: []}]` |
| Unauthenticated call | `GET /api/PurchaseOrders` → **401** (verified) |

## 2. Auth

```http
POST /api/Auth
Content-Type: application/json

{ "login": "svc.integration", "password": "...", "roleNo": null, "unitNo": null,
  "totpCode": null, "recoveryCode": null }
```

→ `200` `JwtToken`:

```json
{ "accessToken": "eyJhbGciOi...", "expiresIn": 3600 }
```

- Model `SerticaUser` = `{ login, password, roleNo, unitNo, totpCode, recoveryCode }`. Sending
  `username` instead of `login` yields **500 `ArgumentNullException (Parameter 'key')`**, not a 400 — verify your payload keys before blaming the credentials.
- `roleNo` and `unitNo` are optional but scope the whole session: the same credentials with another
  `unitNo` see another company/vessel data set. Pick the unit deliberately and cache a token per unit.
- `expiresIn` is seconds. Refresh before expiry, and retry once on `401` (token revocation is silent).
- TOTP-enabled accounts must pass `totpCode` (or `recoveryCode`) at login.

Supporting endpoints: `GET /Auth` (current user), `GET /Auth/units` (unit/unit-group tree the account
may access), `GET /Auth/userRights` (granted rights — useful to pre-flight an integration),
`GET /Auth/{login}/roles`, `POST /Auth/accessToken`, `GET /Auth/fileDownloadToken`,
`GET /Auth/officeSiteUrl`, `GET /Auth/integrations`, plus `/Auth/forgotPassword|resetPassword|changePassword|resetPin` and `/Auth/totp/{setup,confirm,disable,recoverycodes/generate}`.

## 3. Transport conventions

- `Content-Type: application/json` on every body. The spec offers `application/json`, `text/json`,
  `text/plain` for responses and `application/json-patch+json` for bodies; use plain JSON.
- Property names are **camelCase** (`purchaseOrderNo`, `deliveryDate`).
- Every model has `additionalProperties: false` — undocumented keys are rejected.
- **No schema declares `required`** (0 of 1,104), so field validation happens server-side and comes
  back as `400 ValidationResult`:

```json
{ "isValid": false,
  "errors":     [ { "text": "...", "fieldName": "..." } ],
  "brokenRules":[ { "type": "...", "index": 0, "objectGuid": "...", "field": "...", "field2": "...", "description": "..." } ],
  "subResults": { "positions[0]": { "isValid": false, "errors": [ ... ] } } }
```

  `subResults` is keyed by sub-object — always surface it, it is where nested position/line errors live.
- Enums travel as **strings**. Example `SearchOperator`:
  `Equals, LessThan, GreaterThan, Like, Range, In, Dynamic, StartsWith, EndsWith, IsNull, NotLike, Or, NotEquals, NotIn`.
- Dates are `string:date-time` in the models (e.g. `expireDate`, `issueDate`). Exact accepted format and
  time zone are **UNVERIFIED** — round-trip one write/read before relying on it.

## 4. Pagination

```http
GET /api/PurchaseOrders?page=1&pageSize=100
Authorization: Bearer <token>
```

→ bare JSON array (no `total`, no envelope, no count header — checked across all 3,340 operations).

- `page` defaults to `1` everywhere (627 operations expose it).
- `pageSize` defaults to **25** on 450 operations and **5** on 177 operations (e.g.
  `/PurchaseOrders/{no}/history`). Always pass it explicitly.
- Termination rule: keep requesting pages and stop on an empty array. A short page does *not* reliably
  mean the end. Maximum accepted `pageSize` is **UNVERIFIED**.

```php
// Laravel: drain a list endpoint
$page = 1; $all = [];
do {
    $rows = Http::withToken($token)
        ->get("{$base}/PurchaseOrders", ['page' => $page, 'pageSize' => 200])
        ->throw()->json();
    $all = array_merge($all, $rows);
    $page++;
} while (count($rows) === 200);
```

## 5. Search (the powerful path)

Three endpoints per module: `POST /{Module}/search`, `POST /{Module}/searchCount` (→ `int`),
`GET /{Module}/searchInfo` (what you may filter on). `POST /{Module}/searchIndex/{guid}` returns a
record's position inside a result set.

`SearchDefinition`:

```json
{
  "distinct": true,
  "criteria": [
    { "field": "orderDate", "operator": "Range", "values": ["2025-01-01", "2025-03-31"] },
    { "field": "companyNo", "operator": "In",    "values": ["1001", "1002"] },
    { "field": "description", "operator": "Like", "values": ["%pump%"] }
  ],
  "sorting":  [ { "field": "orderDate", "direction": "Descending" } ],
  "columns":  ["purchaseOrderNo", "orderDate", "totalCost"],
  "contains": ["positions"],
  "subObjectsToInclude": ["positions"],
  "unitFilter": ["NO001"],
  "forDeviceRequest": null
}
```

- `criteria[]` = `{ field, operator, values[], valuesMatching }`; `operator` from the enum above.
  Use `Range`/`In` for multi-value, `Dynamic` only where the module documents it.
- `sorting[]` = `{ field, direction }`; `contains`/`subObjectsToInclude` pull nested collections into
  the response where the module supports it (`searchInfo.supportsContains` says whether it does);
  `columns` narrows the projection; `unitFilter` restricts to units.
- **Line/position collections are separate modules, not nested arrays**: `POST /PurchaseOrderPositions/search`,
  `POST /RequisitionPositions/search`, `GET /ImInvoices/{invoiceNo}/positions[/{positionNo}]`,
  `GET /Carriers/{carrierNo}/positions`. The header model (`PurchaseOrders`) carries totals only —
  sync header and positions as two calls and match on the position keys returned there.
- Discovery flow: `GET /{Module}/searchInfo` → `SearchInfo { supportsContains, fields[] }`, each field
  `{ field, dataType, operators[], enumType, isCustomProperty }`. `dataType` comes from
  `SearchDataType` (`String, Int, Decimal, Enum, DateTime, Guid, Bool, Duration, Unkonwn[sic]`).
  Cache this per module — it is the only authoritative list of filterable fields, and it includes
  customer-defined custom properties (`isCustomProperty: true`).
- Typical use: full re-read of a module after a change window (search by `Range` on the modification
  date) instead of paging through everything.

## 6. Detail, create, update, delete

| Operation | Call | Result |
|---|---|---|
| Read one | `GET /{Module}/{key}` | object, `404` when absent |
| Create | `POST /{Module}` (body = module model) | `201` + created object |
| Update | `PUT /{Module}/{key}` (body = full model) | `200` + updated object |
| Delete | `DELETE /{Module}/{key}` | `204` |
| Force delete | `DELETE /{Module}/{key}/force` | `204` (leaves dangling references — avoid in integrations) |
| Copy | `GET /{Module}/{key}/copy` | new record based on existing |
| History | `GET /{Module}/{key}/history` | audit rows (needs the `*_HistoryMode` right) |

Path keys are module-specific: `documentNo`, `jobNo`, `itemNo`, `componentNo`, `unitNo`,
`purchaseOrderNo`, `invoiceNo`, `requisitionNo`, `shipmentNo`, `vesselReportNo`, `templateNo`,
`formNo`, `addressNo`, `userNo`, `webhookNo`, `taskNo`, `resourceNo`, or `guid`/`{...}Guid`.

Upsert pattern for master-data sync (idempotent): `GET` by business key → `PUT` when found, `POST` when
`404`. Several modules also carry `externalReference`, `externalReference2..4` and
`forceAutogenerateDocumentNo` query flags — use them to keep your system's id on the record instead of
creating duplicates.

## 7. Documents, files, photos

File traffic is `multipart/form-data` with a **single binary part named `File`** (51 operations):

```bash
# replace the file of an existing document
curl -X POST "$BASE/Documents/DOC-1001/file" \
  -H "Authorization: Bearer $TOKEN" \
  -F "File=@./manual.pdf"

# upload into a job history data entry / certificate renewal, etc.
curl -X POST "$BASE/Certificates/CERT-77/renew" -H "Authorization: Bearer $TOKEN" -F "File=@./cert.pdf"
```

Download: `GET /{Module}/{key}/file` (add `contentDisposition`, `filename` to steer the browser),
`GET /{Module}/{key}/pdf` for the rendered report, `GET /{Module}/{key}/documents` for the attachment
list. Signed/short-lived links come from `GET /Auth/fileDownloadToken`.

Edit-in-place workflow for controlled documents: `PUT /Documents/{documentNo}/checkout` →
download `GET .../file` → edit → `POST /Documents/{documentNo}/checkin` with the `File` part
(varargs `checkinWithoutVersion`, `revisionRemark`, `version`). `POST /Documents/zipArchive`
(SearchDefinition body) packages a search result set.

## 8. Automation surfaces

- **Webhooks** (`/Webhooks`): CRUD + `POST /Webhooks/{no}/execute` (fire from API, right
  `Webhooks_ExecuteFromAPI:Function`), `POST /Webhooks/validate`, `POST /Webhooks/tree`,
  `GET /Webhooks/{no}/responses` (+`/count`), `GET /Webhooks/{no}/webhooklogs/search`,
  `GET /Webhooks/{no}/webhookschedules`, `GET /Webhooks/{no}/webhookapis/{guid}`. This is the
  supported push channel — prefer it over polling when SERTICA must notify your app.
  `WebhookLogStatus` enum: `Error, Resolved, InSync`.
- **Scheduled tasks** (`/ScheduledTasks`, right `TSTask:*`): `POST /ScheduledTasks/{taskNo}/RunNowTask`,
  `/activatetask`, `/deactivatetask`, `/queueItems`.
- **Master Data Management** (`/MasterDataManagement*`, `/MDMUnit`, `/MasterUnit`): master-data sync and
  distribution across units.
- **VRS API** (`/VrsApiConfigurations`, `/VrsApiScripts`): vessel-report scripting exposed over the API.

## 9. Errors, rights, licenses

| Code | Meaning | Handling |
|---|---|---|
| 400 | `ValidationResult` (also used for business-rule failures) | show `errors[]`, `brokenRules[]`, `subResults{}` |
| 401 | missing/expired token | re-login, retry once |
| 403 | caller lacks the operation's user right (`User must have one of these User Rights` + table) | the required right is in the endpoint catalogs' `Rights` column |
| 404 | record not found (detail endpoints) | treat as "create" in upserts |
| 500 | unhandled server error, "See Sertica logs" | not retryable blindly; log correlation data |

- 3,028 of 3,340 operations document their required right; 688 distinct `Key:Right` values exist.
  Most common: `AnalyticsMain:View`, `JobApp:Function`, `PurchaseOrder:View`, `Form:View`,
  `SparePart:View`, `ImInvoice_Update:Update`, `ChangeRequest:View`, `ProcurementRequisition:View`,
  `Job:View`, `OrbOperation:View`, `Component:View`, `VesselReport:View`, `ManagementSystem:View`,
  `Certificate:View`, `Options:View`.
- The spec's own header warns: *"some endpoints are restricted by license or user rights and may not be
  available in your environment"* — endpoint sets can differ per tenant/license. Enumerate against the
  target environment, don't assume the captured catalog is complete there.
- Pre-flight before rollout: `GET /Auth/userRights` for the integration account and compare with the
  `Rights` column of every endpoint the integration uses.

## 10. Minimal client (Laravel / PHP)

```php
final class SerticaClient
{
    public function __construct(
        private string $base,
        private string $login,
        private string $password,
        private ?string $unitNo = null,
    ) {}

    private function token(): string
    {
        return Cache::remember("sertica.token.{$this->unitNo}", now()->addMinutes(45), function () {
            $res = Http::acceptJson()->post("{$this->base}/Auth", [
                'login' => $this->login, 'password' => $this->password, 'unitNo' => $this->unitNo,
            ]);
            if (! $res->successful()) {
                throw new RuntimeException('SERTICA login failed: '.$res->status().' '.$res->body());
            }
            return $res->json('accessToken');           // JwtToken { accessToken, expiresIn }
        });
    }

    public function get(string $path, array $query = [])
    {
        $res = Http::withToken($this->token())->acceptJson()->get($this->base.$path, $query);
        if ($res->status() === 401) { Cache::forget("sertica.token.{$this->unitNo}");
            $res = Http::withToken($this->token())->acceptJson()->get($this->base.$path, $query); }
        if ($res->status() === 400) { throw new SerticaValidationException($res->json());
        }
        return $res->throw()->json();
    }

    /** Walk every page of a list endpoint. */
    public function all(string $path, int $pageSize = 200): array
    {
        $page = 1; $rows = []; $chunk = [];
        do { $chunk = $this->get($path, ['page' => $page++, 'pageSize' => $pageSize]);
             $rows = array_merge($rows, $chunk); } while (count($chunk) === $pageSize);
        return $rows;
    }

    /** Ranked/sorted read via SearchDefinition. */
    public function search(string $path, array $definition, int $pageSize = 200): array
    {
        $page = 1; $rows = []; $chunk = [];
        do { $chunk = Http::withToken($this->token())->acceptJson()
                ->post($this->base.$path.'/search?page='.$page++.'&pageSize='.$pageSize, $definition)
                ->throw()->json();
             $rows = array_merge($rows, $chunk); } while (count($chunk) === $pageSize);
        return $rows;
    }
}
```

Front-end / Node equivalent is plain `fetch` with `Authorization: Bearer`; the whole API is JSON in,
JSON out, so no SDK is required.

## 11. Go-live checklist

1. `POST /Auth` with the real service account, with and without `unitNo` — confirm the unit scoping you expect.
2. `GET /Auth/userRights` → diff against the `Rights` column of each endpoint you call.
3. Probe every list endpoint with `pageSize=500` and confirm the server honours it, otherwise lower it.
4. Round-trip one date field (`issueDate`, `orderDate`) and confirm format/time zone.
5. Trigger one `400` on purpose and log the full `ValidationResult`, including `subResults`.
6. Confirm the tenant exposes every module you depend on (license gaps remove whole tags).
7. Re-capture the spec (`python scripts/sertica_api.py refresh && python scripts/build_references.py`) after
   every SERTICA upgrade and diff the results.
