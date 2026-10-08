# SAP ⇄ SERTICA integration baseline (Indobaruna / IBT)

Source: `D:\Metrodata\IBT\SAP-SERTICA-API-Payload-Summary.pdf` (offline copy: `assets/SAP-SERTICA-API-Payload-Summary.pdf`) — "SAP-SERTICA API Payload Summary,
Development baseline", updated 13 September 2026 (credentials omitted). Every path, model and field
below was re-checked against the captured OpenAPI spec (`assets/sertica-swagger.json.gz`); the
**Verification status** notes come from the PDF and say what was actually executed live.

Instance: `https://indobaruna-test.sertica.com` (test). Target app: the IBT Laravel/React/Inertia
project's `Settings → SAP Config` push.

## 0. Path-name corrections vs the PDF

The PDF writes paths in short form. The spec's real keys (use these — casing of the key placeholder
matters when you build the URL from a variable, and some models have a differently named key):

| PDF shorthand | Actual spec path | Model |
|---|---|---|
| `GET /api/ItemGroups/<parentGroupNo>` (check parent) | `GET /api/ItemGroups/{itemGroupNo}` | `Item.ItemGroup` |
| `POST /api/ItemGroups` | same | `Item.ItemGroup` |
| `GET /api/Items/<itemNo>` | same | `Item.Item` |
| `PUT /api/Items/<itemNo>` | same | `Item.Item` |
| `GET /api/Items/<itemNo>/ItemGroups` | same | verify relationship |
| `GET /api/Items/<itemNo>/warehouses` | same | verify warehouse assignment |
| `POST /api/Items/<itemNo>/adjuststock` | same | `Stock.StockAdjustment` |
| `GET /api/ItemGroupSelection/<groupNo>` | `GET /api/ItemGroupSelection/{itemGroupNo}` | `ItemGroupSelectionTree.ItemGroupSelection` |
| `PUT /api/ItemGroupSelectionTree` | same (body = **array**) | `ItemGroupSelectionTree.ItemGroupSelection` |
| `GET /api/JobHistories/<jobHistoryGuid>` | `GET /api/JobHistories/{jobhistoryGuid}` (lowercase `h`) | `JobHistory.JobHistory` |
| `GET /api/JobHistories/<guid>/items` | `GET /api/JobHistories/{jobhistoryGuid}/items` | `JobHistory.JobHistoryItem` |
| `POST /api/ItemWarehouseHistories/search` | same | `Logihold…Search.SearchDefinition` |

## 1. Authentication: one token per unit context

```http
POST /api/Auth
Content-Type: application/json

{ "login": "<integration-user>", "password": "<secret>", "roleNo": "<authorized-role>", "unitNo": "Master Unit" }
```

- Response: `{ "accessToken": "<jwt>", "expiresIn": <seconds> }` → send `Authorization: Bearer <accessToken>`.
- `roleNo` — authorized SERTICA role (e.g. `Admin` during development).
- `unitNo` — the **authentication context**: `Master Unit`, `KPG0`, `IHB0`, …
- **A token does not change unit context later.** Changing `unitNo` in a request field does not
  re-scope the session — obtain a **separate token per unit** you integrate with.

| Token context | Used for |
|---|---|
| `Master Unit` | create/update master item groups, items, and item-group membership |
| Vessel (`KPG0`, `IHB0`, …) | distribute groups, verify visibility, assign warehouse/location, adjust stock, read consumption |

`password` is stored securely — never in source code, config committed to git, or logs.

## 2. Flow A — create master group + item (master token)

Sequence: `check/create group → check/create item → assign group → distribute → verify`.

### A. Group (create only when missing)

```http
GET  /api/ItemGroups/{itemGroupNo}      # 404 ⇒ create
POST /api/ItemGroups
Authorization: Bearer <masterToken>

{ "dataOwner": "MasterUnit", "itemGroupNo": "<SAP group code>", "name": "<SAP group name>",
  "text": "Synchronized from SAP", "parentItemGroupNo": "<approved parent>", "unitNo": "Master Unit" }
```

### B. Item (master unit)

```http
GET  /api/Items/{itemNo}                # 404 ⇒ create
POST /api/Items
Authorization: Bearer <masterToken>

{ "dataOwner": "MasterUnit", "itemNo": "<SAP material number>", "name": "<SAP material description>",
  "measureUnitNo": "PCS", "itemTypeNo": "SPARE", "currencyNo": "IDR", "unitNo": "Master Unit",
  "inactive": false, "critical": false, "certificate": false,
  "trackExpiry": false, "trackedItem": false, "disallowManualStockAdjustment": false }
```

**Create rule:** always `GET` before `POST`. If the business key already exists, compare ownership and
`PUT` the update instead of creating a duplicate.

### C. Assign the group to the item

`GET /api/Items/{itemNo}` → **merge** into the latest item document → `PUT /api/Items/{itemNo}`:

```json
"itemGroups": [ { "itemNo": "<itemNo>", "itemName": "<item name>", "itemGroupNo": "<groupNo>",
  "itemGroupName": "<group name>", "itemGroupUnitNo": "Master Unit", "itemGroupUnitName": "Office",
  "guidForReferencedObject": "<group.guid>", "unitGuid": "<group.unitGuid>", "deleted": false } ]
```

Verify with `GET /api/Items/{itemNo}/ItemGroups`.
Item-group element model = the inline `itemGroups` item of `Item.Item` (13 fields; the 9 above are all real).

### D. Distribute the group to one vessel

```http
GET /api/ItemGroupSelection/{itemGroupNo}          Authorization: Bearer <targetVesselToken>
PUT /api/ItemGroupSelectionTree                    Authorization: Bearer <targetVesselToken>
```

Body is an **array**:

```json
[ { "dataOwner": "Unit", "itemGroupGuid": "<selection.itemGroupGuid>", "hasChildren": false,
    "name": "<group name>", "itemGroupText": "<group text>", "itemGroupNo": "<groupNo>",
    "parentVisibleKey": "<parentGroupNo>", "unitNo": "Master Unit", "selected": true,
    "selectedUnitNo": "<target vessel code>", "hasParent": true } ]
```

`dataOwner` enum is `Unit | MasterUnit`; read the current row first (`ItemGroupSelection/{itemGroupNo}`)
so you send back the same `itemGroupGuid`/`unitNo` values you were given.

### E. Assign vessel warehouse/location

`GET /api/Items/{itemNo}` (vessel token) → merge → `PUT /api/Items/{itemNo}`:

```json
"warehouses": [ { "warehouseNo": "E01", "warehouseName": "Engine Room", "locationNo": "001.001",
  "locationName": "BIN 01", "standardWarehouse": true, "stock": 0, "maximumStock": 0, "minimumStock": 0,
  "itemNo": "<itemNo>", "itemName": "<item name>", "unitNo": "KPG0", "itemUnitNo": "Master Unit",
  "measureUnitNo": "PCS" } ]
```

Verify with `GET /api/Items/{itemNo}/warehouses`.
Warehouse element = inline `warehouses` item of `Item.Item` (32 fields: `standardWarehouse` boolean,
`stock`/`minimumStock`/`maximumStock` numbers, `location`/`locationNo`/`locationName`, `itemUnitNo`,
`unitNo`, …). Note `PUT /Items/{itemNo}` replaces the whole document — **always read-merge-write**, never
send a partial body you assembled from scratch.

## 3. Flow B — goods receipt / increase SERTICA stock

Authenticate as the **receiving vessel**. Resolve and verify the item warehouse/location before posting.

```http
POST /api/Items/{itemNo}/adjuststock      Authorization: Bearer <receivingVesselToken>
Content-Type: application/json
```

Delta receipt (goods receipt) vs absolute balance (physical/stocktake reconciliation):

```json
{ "warehouseNo": "E01", "itemLocationNo": "001.001", "quantity": 5,
  "description": "SAP_GR:<unique-reference>", "stockAdjustmentType": "WriteUpStock",
  "fromSerticaApp": false, "sourceSystem": "SAP" }
```
```json
{ "warehouseNo": "E01", "itemLocationNo": "001.001", "quantity": 5,
  "description": "SAP_STOCKTAKE:<unique-reference>", "stockAdjustmentType": "Stocktake",
  "fromSerticaApp": false, "sourceSystem": "SAP" }
```

| Field | Rule |
|---|---|
| `warehouseNo` | receiving vessel warehouse |
| `itemLocationNo` | omit only when the warehouse assignment has no location |
| `quantity` | receipt **delta** for `WriteUpStock`; **target balance** for `Stocktake` |
| `description` | unique SAP correlation reference — audit trail + echo suppression |
| `stockAdjustmentType` | `WriteUpStock` for receipt delta; `Stocktake` for absolute reconciliation |
| `fromSerticaApp` | `false` for SAP-originated posts |
| `sourceSystem` | `"SAP"` |

`Stock.StockAdjustmentType` enum = `WriteUpStock | WriteDownStock | Stocktake` (8 fields on the model).

**Verification status (from the source doc):** `Stocktake` was directly tested and read back successfully.
`WriteUpStock` is exposed by the schema but the direct request **still needs a dedicated development test
before production**.

## 4. Flow C — consumption, option A: job consumption (SERTICA → SAP)

Vessel token → search finalized job executions → read job → read item lines → post SAP issue.

```http
POST /api/JobHistories/search?page=1&pageSize=100
Authorization: Bearer <vesselToken>
Content-Type: application/json

{ "distinct": true,
  "columns": ["guid","jobNo","liveJobNo","status","linkDate","unitNo","updateDate","createDate"],
  "criteria": [ {"field":"unitNo","operator":"Equals","values":["KPG0"]},
                {"field":"status","operator":"Equals","values":["Final"]} ] }

GET /api/JobHistories/{jobhistoryGuid}
GET /api/JobHistories/{jobhistoryGuid}/items
```

Fields required for SAP consumption:

| Field | Use |
|---|---|
| `status` (on `JobHistory`) | process `Final` executions only |
| `quantityFromOwnStock` (on `JobHistoryItem`, number) | inventory quantity consumed from vessel stock |
| `itemNo` | SAP material mapping |
| `warehouseNo` / `itemLocationNo` | SAP plant / storage-location mapping |
| `jobHistoryGuid` + item-line `guid` | durable deduplication + SAP external reference |

**Deduplication key:** `SERTICA_JOB:<unitNo>:<jobHistoryGuid>:<jobHistoryItemGuid>`.
Do **not** also post its `WarehouseHistory` row as a second SAP goods issue.

## 5. Flow D — consumption, option B: warehouse history (SERTICA → SAP)

Includes job use, manual adjustments, initialization, receipts and other stock movements →
**classification is mandatory**.

```http
POST /api/ItemWarehouseHistories/search?page=1&pageSize=100
Authorization: Bearer <vesselToken>
Content-Type: application/json

{ "distinct": true,
  "columns": ["guid","itemNo","warehouseNo","locationNo","quantity","historyType","historyDate",
              "stockQuantityAfterTransaction","description","updateUserNo","unitNo"],
  "criteria": [ {"field":"unitNo","operator":"Equals","values":["KPG0"]},
                {"field":"historyDate","operator":"GreaterThan","values":["<checkpoint-date-time>"]} ] }
```

`ItemWarehouseHistory.historyType` enum (23 fields on the model):
`Default | Init | WriteUpStock | WriteDownStock | Requisition | JobHistory | PriceUpdate | ResetStock | StatusStock | StatusCount`.

| Warehouse event | SAP handling |
|---|---|
| `JobHistory` | exclude if option A is active — same job consumption |
| `Init` | do not post as consumption |
| approved manual negative adjustment | post as consumption / inventory difference with approved type-reason mapping |
| positive adjustment / return | not consumption — separate receipt or return flow if in scope |
| transfer / reversal / correction | map explicitly; **never classify from the quantity sign alone** |
| `description` = `SAP_GR` / `SAP_SYNC` | suppress the outbound echo of an SAP-originated stock update |

**Deduplication key:** `SERTICA_STOCK:<unitNo>:<warehouseHistoryGuid>`.
Process every page and keep a **per-vessel checkpoint with overlap** (re-read a small window before the
last seen timestamp, then dedupe by key).

**Production check (from the source doc):** the warehouse-history search shape is verified; manual
`WriteDownStock` consumption, date-filter syntax, timezone behaviour and reversal handling still require
end-to-end validation.

## 6. Open items / unverified

1. `WriteUpStock` receipt post — schema-valid, not yet exercised live.
2. Timezone and exact format of `historyDate` / `linkDate` filters (the spec documents no format).
3. Max `pageSize` accepted by the search endpoints (defaults: 25, or 5 on some paths — always send it).
4. Rights needed per endpoint on the production unit (see the **Rights** column of
   `endpoints-06-items-inventory.md` / `endpoints-04-jobs-maintenance.md`); a token without them gets 403.
5. Error contract on a rejected `adjuststock` (`400 ValidationResult.brokenRules`) — capture once for the
   IBT mapping table.
