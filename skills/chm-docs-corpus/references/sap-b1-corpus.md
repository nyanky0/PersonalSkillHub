# SAP B1 SDK 10.0 — CHM corpus (concrete instance)

Authoritative extraction + indexing recipe proven in a real session.

## Source CHM (protected Program Files location)
`C:\Program Files (x86)\SAP\SAP Business One SDK\Help\`
- `REFDB.chm` — Database Tables Reference (table names + fields). The most-used file.
- `REFDI.chm` — DI API Objects Reference (SAPbobsCOM, ~2,960 objects, 27k files)
- `REFUI.chm` — UI API Reference (SAPbouiCOM, ~212 objects, 1.8k files)
- `SDK_EN.chm`, `ScreenPainter.chm`, `JCO.zip`

## Extraction
Use 7-Zip with forward-slash Windows paths (NOT `hh -decompile`, NOT `/c/...` paths):
```bash
SEVENZ="C:/Program Files/7-Zip/7z.exe"
"$SEVENZ" x -y -o"C:/Users/<user>/.sap-b1-help/REFDB" "C:/Program Files (x86)/SAP/SAP Business One SDK/Help/REFDB.chm"
```
Move the tree to a stable dir with native `robocopy` (fast on 31k files).

## Stable locations (this machine)
- Corpus: `C:/Users/yudah/.sap-b1-help/{REFDB,REFDI,REFUI}`
- Index + helpers: `C:/Users/yudah/.sap-b1-skills/` (`build_index.py`, `search_sap.py`,
  `refdb_index.json`, `refdi_index.json`, `refui_index.json`)
- Search helper usage:
  - `python C:/Users/yudah/.sap-b1-skills/search_sap.py db <tabel|kata>`
  - `... di <objek>` / `... ui <objek>` / `... dbfields <tabel>`

## Document line source tables (REFDB↔REFDI cross-check, sampled)
oInvoices=13→OINV, oCreditNotes=14→ORIN, oDeliveryNotes=15→ODLN, oReturns=16→ORDN,
oOrders=17→ORDR, oPurchaseInvoices=18→OPCH, oPurchaseCreditNotes=19→ORPC,
oPurchaseDeliveryNotes=20→OPDN, oPurchaseReturns=21→ORPD, oPurchaseOrders=22→OPOR,
oQuotations=23→OQUT, oInventoryGenEntry=59→OIGN, oInventoryGenExit=60→OIGE,
oStockTransfer=67→OWTR, oInventoryTransferRequest=1250000001→OWTQ.
Core value notes: oChartOfAccounts=1, oBusinessPartners=2, oItems=4.

## Enum name gotchas (verify in HTML, not memory)
- DI object types enum: `SAPbobsCOM~Enumerations~BoObjectTypes_EN.html`.
- UI item types is **`BoFormItemTypes`** (it_COMBO_BOX, it_CHECK_BOX, it_OPTION_BUTTON...) —
  there is NO `BoItemTypes` in this SDK. Check `SAPbouiCOM~Enumerations~BoFormItemTypes_EN.html`.
- Event types: `BoEventTypes` (et_ITEM_PRESSED, et_COMBO_SELECT, et_MENU_CLICK, ...).