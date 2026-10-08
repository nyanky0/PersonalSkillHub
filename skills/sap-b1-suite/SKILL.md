---
name: sap-b1-suite
description: "Master SAP Business One SDK & Integration Suite."
version: 2.0.0
author: Hermes Agent & Antigravity
metadata:
  hermes:
    tags: [sap-b1, di-api, service-layer, hana, sql, addon, fdd, csharp]
---

# SAP Business One Enterprise Master Suite

Arsitektur pengembangan dan integrasi SAP Business One komprehensif:



## Sub-Module: sap-b1

# SAP Business One — SDK Skill Pack

Komponen skill untuk pengembangan add-on dan query pada SAP Business One (SAP B1) SDK 10.0.
Paket ini terdiri dari tiga modul skill yang saling melengkapi:

| Modul | Nama skill | Sumber | Dipakai untuk |
|-------|-----------|--------|----------------|
| Database & Query | `sap-b1-db` | `REFDB.chm` (Database Tables Reference) | Menulis query SQL (SQL Server / HANA), lookup tabel & field, konvensi penamaan tabel |
| DI API | `sap-b1-di-api` | `REFDI.chm` (Objects Reference, 2.960 objek) | Add-on sisi server / data: Company, Documents, Recordset, CompanyService, SBObob, UserTables |
| UI API | `sap-b1-ui-addon` | `REFUI.chm` (UI API, 212 objek) | Add-on UI: form, item, event, DataSources, menu, Choose From List |
| Service Layer API | `sap-b1-sl-api` | `Service Layer API Reference.html` (OData REST, 499 service/entity) | Integrasi REST/HTTP: auth Login, CRUD entity, query $filter/$expand/$select, batch, action `*Service_*` |
| **FDD Author (Master/Orkestrator)** | `sap-b1-fdd-author` | Template FDD PT Soltius Indonesia | Membuat Functional Design Documentation dari source code; memanggil 5 sub-skill dokumentasi |
| UDT/UDF Schema Extractor | `sap-b1-udt-udf-schema-extractor` | — | Ekstrak skema UDT/UDF/UDO → tabel data dictionary |
| Business Logic Translator | `sap-b1-business-logic-translator` | — | Ubah C#/algoritma → narasi Business Process non-teknis |
| Validation & Trigger Analyzer | `sap-b1-validation-trigger-analyzer` | — | Kumpulkan validasi & trigger → section "Validasi Dokumen" |
| Integration Mapper | `sap-b1-integration-mapper` | — | Map payload Service Layer/OData → tabel spesifikasi integrasi |
| Visual Logic Mapper | `sap-b1-visual-logic-mapper` | — | Render alur/arsitektur → diagram Mermaid flowchart (developer preview) |
| **Corporate Flowchart Architect** | `corporate-flowchart-architect` | Standar Soltius Draw.io XML | Diagram alur proses bisnis resmi Soltius (#4F88BB, 1..N integer, XML Draw.io & PNG) |

## Cara memilih modul

1. **Menulis query / laporan / data extraction dari database B1** → gunakan `sap-b1-db`.
2. **Membuat logika add-on (CRUD objek bisnis, dokumen, integrasi)** → gunakan `sap-b1-di-api`.
3. **Membuat/tampilan form, menangani event UI, menu, CFL** → gunakan `sap-b1-ui-addon`.
4. **Integrasi REST/HTTP (Python/Node/Java, aplikasi eksternal)** → gunakan `sap-b1-sl-api`.
5. **Campuran (form + data + query / REST + query)** → muat modul sesuai kebutuhan (mis. `sap-b1-sl-api` + `sap-b1-db` untuk cek tabel padanan entity).

## SAP Master Logic (satu panggilan, semua skill)

**Prinsip:** apa pun tugas SAP B1 yang diminta, muat `sap-b1` (umbrella) dulu, lalu panggil kombinasi skill di bawah sesuai konteks — tanpa perlu diminta per-skill oleh user. Routing otomatis:

| Konteks tugas | Skill yang dimuat |
|---|---|
| "Buat FDD / FDD dari source code" | `sap-b1-fdd-author` (master) + **5 sub-skill dokumentasi** sekaligus |
| Query/laporan/data extraction | `sap-b1-db` |
| Add-on logika (CRUD objek/dokumen) | `sap-b1-di-api` |
| Form/UI/event/menu | `sap-b1-ui-addon` |
| Integrasi REST/HTTP eksternal | `sap-b1-sl-api` |
| Dokumentasi proses bisnis | `sap-b1-business-logic-translator` |
| Diagram alur resmi Soltius / FDD | `corporate-flowchart-architect` (Draw.io XML) / `sap-b1-visual-logic-mapper` (Mermaid) |
| Skema UDT/UDF/UDO | `sap-b1-udt-udf-schema-extractor` |
| Validasi & trigger | `sap-b1-validation-trigger-analyzer` |
| Pemetaan endpoint/payload | `sap-b1-integration-mapper` |

**Alur FDD lengkap (contoh "buat FDD dari source code"):**
1. Muat `sap-b1-fdd-author` (template PT Soltius + quality gates)
2. Scan source → tentukan tipe add-on (C# UI API / Laravel+SL / SQL script)
3. `corporate-flowchart-architect` → Draw.io XML & High-res PNG Business Process resmi (#4F88BB, 1..N integer, zero-hallucination)
4. `sap-b1-business-logic-translator` → narasi + PIC + Journal entry (1:1 parity dengan diagram)
5. `sap-b1-udt-udf-schema-extractor` → tabel struktur data (UDT/UDF/UDO)
6. `sap-b1-validation-trigger-analyzer` → validasi sistem
7. `sap-b1-integration-mapper` → integrasi dokumen/payload
8. Susun ke template FDD (Cover → DAFTAR ISI → Pendahuluan → Proses → Struktur Data → UI → Approval) dan simpan `FDD - {Nama Add-on} v1.0.md`

## Infrastructure bersama (dipakai seluruh modul)

- **Corpus bantuan lengkap (hasil ekstrak CHM/HTML):** `C:/Users/yudah/.sap-b1-help/`
  - `REFDB/` — 2.844 halaman tabel (1 file per tabel, dikelompokkan per modul)
  - `REFDI/` — 27.196 file (2.960 objek DI API, format `SAPbobsCOM~<Objek>.html`)
  - `REFUI/` — 1.808 file (212 objek UI API, format `SAPbouiCOM~<Objek>.html`)
  - `REFSL/` — 499 file Service Layer (OData REST, entity + `*Service`, contoh JSON)
- **Index + search helper:** `C:/Users/yudah/.sap-b1-skills/`
  - `refdb_index.json`, `refdi_index.json`, `refui_index.json`, `refsl_index.json`
  - `search_sap.py` — antarmuka pencarian:

```bash
python C:/Users/yudah/.sap-b1-skills/search_sap.py db <tabel|kata>     # cari tabel DB
python C:/Users/yudah/.sap-b1-skills/search_sap.py di <objek|kata>     # cari objek DI API
python C:/Users/yudah/.sap-b1-skills/search_sap.py ui <objek|kata>     # cari objek UI API
python C:/Users/yudah/.sap-b1-skills/search_sap.py dbfields <tabel>    # dump semua field sebuah tabel
python C:/Users/yudah/.sap-b1-skills/search_sap.py sl <service|entity> # cari Service Layer (REST)
python C:/Users/yudah/.sap-b1-skills/search_sap.py sleps <service>     # daftar endpoint Service Layer
```

Contoh:
```bash
python C:/Users/yudah/.sap-b1-skills/search_sap.py db oitm        # -> Items master
python C:/Users/yudah/.sap-b1-skills/search_sap.py dbfields oinv   # -> semua field OINV
python C:/Users/yudah/.sap-b1-skills/search_sap.py di documents    # -> objek Documents
python C:/Users/yudah/.sap-b1-skills/search_sap.py ui application  # -> objek Application
python C:/Users/yudah/.sap-b1-skills/search_sap.py sl orders       # -> entity Orders + endpoint
python C:/Users/yudah/.sap-b1-skills/search_sap.py sleps invoices  # -> semua endpoint Invoices
```

Bila index belum ada, bangun ulang dengan:
```bash
python C:/Users/yudah/.sap-b1-skills/build_index.py                     # db/di/ui
python C:/Users/yudah/.sap-b1-skills/build_sl_corpus.py "<SL_Reference.html>"  # service layer
```

## Aturan umum

- **Wajib Cantumkan Object Key & ObjType**: Pada setiap perancangan, query, integrasi, SP_TransactionNotification, DI/UI API event, atau dokumentasi FDD yang berhubungan dengan object SAP, **SELALU include dan gunakan pemetaan resmi Table, Primary Key, dan Object Type** dari tabel master.
- **Selalu cek tabel ke DB sebelum menulis query**: gunakan `search_sap.py db <tabel>` — jangan menebak nama field.
- **Nama objek DI/UI case-sensitive** dalam kode; ikuti persis ejaan di corpus.
- Dokumen sumber asli (CHM) tetap ada di `C:\Program Files (x86)\SAP\SAP Business One SDK\Help\` — buka bila butuh penjelasan mendalam yang tidak ada di corpus.
- Jangan pernah menyertakan kredensial/koneksi string asli ke database dalam output; gunakan placeholder.
- Bila query/SQL perlu disesuaikan SQL Server vs HANA, selalu tanyakan platform target atau sediakan dua varian.

## Master Reference: SAP Business One Object Types, Primary Keys & Object Keys (ObjType Mapping)

> [!IMPORTANT]
> **Mandatory Rule: SAP Object Key & ObjType Resolution**
> KETIKA ada tugas, analisis, kodingan, query SQL, implementasi add-on, SP_TransactionNotification / SP_PostTransactionNotice, event DI API / UI API, endpoint Service Layer, atau dokumen FDD yang menyentuh **Object Key** atau **Object Type (`ObjType`)**, AI Agent dan Developer **WAJIB MENG-INCLUDE-KAN DAN MENGACU PADA TABEL MASTER OBJECT TYPE & PRIMARY KEY DI BAWAH INI**.
> Sumber acuan resmi: [`tables.json`](./tables.json) (upstream: `https://github.com/AxionCompany/sapb1-datatypes-tables`).
> **DILARANG** mengasumsikan atau menebak nama primary key / object type (misal: menebak `DocEntry` padahal `CardCode` / `ItemCode` / `AbsEntry` / `TransId` / `Code` / `AbsId` / `Num`, dll).

### Panduan Operasional Integrasi Berdasarkan Object Key & ObjType

1. **`SP_TransactionNotification` & `SP_PostTransactionNotice` (SQL Server / HANA)**:
   - Parameter `@object_type` (`NVARCHAR(30)`) berisi integer string dari **Object Type** (contoh: `'22'` untuk Purchase Order, `'17'` untuk Sales Order, `'2'` untuk Business Partner, `'234000031'` untuk Return Request).
   - Parameter `@list_of_cols_val_tab_del` berisi nilai dari kolom **Primary Key** tabel terkait (contoh: `DocEntry` pada `OPOR`/`ORDR`/`ORRR`, `CardCode` pada `OCRD`, `ItemCode` pada `OITM`, `TransId` pada `OJDT`).
   - Validasi query wajib mencocokkan `@object_type` dan meng-join tabel header menggunakan kolom Primary Key yang presisi:
     ```sql
     -- Contoh Validasi SP_TransactionNotification untuk Purchase Order (ObjType = 22, PK = DocEntry)
     IF @object_type = '22' AND @transaction_type IN ('A', 'U')
     BEGIN
         IF EXISTS (
             SELECT 1 FROM OPOR T0
             WHERE T0.DocEntry = CAST(@list_of_cols_val_tab_del AS INT)
               AND ISNULL(T0.U_SOL_UID, '') = ''
         )
         BEGIN
             SET @error = 22001
             SET @error_message = N'PO Validation: U_SOL_UID wajib diisi sebelum posting!'
         END
     END
     ```

2. **Dokumen Cross-Reference (`BaseType`, `BaseEntry`, `TargetType`)**:
   - Kolom `BaseType` dan `TargetType` pada baris dokumen (`INV1`, `RDR1`, `POR1`, `DLN1`, `PDN1`, `WTR1`, dll.) menyimpan integer **Object Type** dokumen asal/tujuan.
   - Kolom `BaseEntry` menyimpan nilai **Primary Key (`DocEntry`)** dari dokumen asal.
   - Contoh SQL Join:
     ```sql
     -- Menghubungkan A/R Invoice (OINV, ObjType 13) ke Delivery (ODLN, ObjType 15)
     SELECT T0.DocNum AS InvoiceNum, T1.LineNum, T2.DocNum AS DeliveryNum
     FROM OINV T0
     INNER JOIN INV1 T1 ON T0.DocEntry = T1.DocEntry
     INNER JOIN ODLN T2 ON T1.BaseEntry = T2.DocEntry AND T1.BaseType = 15
     ```

3. **DI API (C# / .NET - `SAPbobsCOM`)**:
   - Konstanta enum `BoObjectTypes` memetakan langsung ke **Object Type**:
     - `oOrders = 17` (`ORDR`, PK: `DocEntry`)
     - `oPurchaseOrders = 22` (`OPOR`, PK: `DocEntry`)
     - `oInvoices = 13` (`OINV`, PK: `DocEntry`)
     - `oBusinessPartners = 2` (`OCRD`, PK: `CardCode`)
     - `oItems = 4` (`OITM`, PK: `ItemCode`)
     - `oInventoryGenEntry = 59` (`OIGN`, PK: `DocEntry`)
     - `oInventoryGenExit = 60` (`OIGE`, PK: `DocEntry`)
     - `oStockTransfer = 67` (`OWTR`, PK: `DocEntry`)
     - `oInventoryTransferRequest = 1250000001` (`OWTQ`, PK: `DocEntry`)
     - `oReturnRequest = 234000031` (`ORRR`, PK: `DocEntry`)
     - `oGoodsReturnRequest = 234000032` (`OPRR`, PK: `DocEntry`)
   - Pemanggilan `oCompany.GetBusinessObject(BoObjectTypes)` dan `GetByKey(key)` wajib menggunakan tipe data kolom Primary Key.

4. **UI API (`SAPbouiCOM`) & Add-On Events**:
   - Pada event `FormDataEvent` (`et_FORM_DATA_ADD`, `et_FORM_DATA_UPDATE`, dll.), properti `BusinessObjectInfo.Type` berisi string **Object Type**.
   - Properti `BusinessObjectInfo.ObjectKey` mengembalikan XML yang membungkus nilai **Primary Key** dokumen:
     ```xml
     <DocumentParams><DocEntry>12345</DocEntry></DocumentParams>
     ```

5. **Service Layer (REST / OData v2)**:
   - Akses entity tunggal via endpoint Service Layer menggunakan format `/<EntityName>(<PrimaryKey>)`:
     - `GET /b1s/v2/Orders(123)` (Table: `ORDR`, ObjType: `17`, PK: `DocEntry`)
     - `GET /b1s/v2/PurchaseOrders(456)` (Table: `OPOR`, ObjType: `22`, PK: `DocEntry`)
     - `GET /b1s/v2/BusinessPartners('C20000')` (Table: `OCRD`, ObjType: `2`, PK: `CardCode`)
     - `GET /b1s/v2/Items('ITEM-001')` (Table: `OITM`, ObjType: `4`, PK: `ItemCode`)

6. **Dokumentasi FDD & Arsitektur Soltius**:
   - Setiap kali menyusun dokumen FDD (Functional Design Document), terutama pada bab **Data Structure**, **Document Validation**, dan **Integration Specifications**, analis/developer WAJIB mencantumkan rincian `Table`, `Table Description`, `Primary Key`, dan `Object Type` secara eksplisit.

### Master Mapping Table (328 SAP Business One Objects)

| Table | Table description | Primary Key | Object Type |
|---|---|---|---|
| `OACT` | G/L Accounts | `AcctCode` | 1 |
| `OCRD` | Business Partner | `CardCode` | 2 |
| `ODSC` | Bank Codes | `AbsEntry` | 3 |
| `OITM` | Items | `ItemCode` | 4 |
| `OVTG` | Tax Definition | `Code` | 5 |
| `OPLN` | Price Lists | `ListNum` | 6 |
| `OSPP` | Special Prices | `CardCode, ItemCode` | 7 |
| `OITG` | Item Properties | `ItmsTypCod` | 8 |
| `ORTM` | Rate Differences | `LineNum, IsSysCurr` | 9 |
| `OCRG` | Card Groups | `GroupCode` | 10 |
| `OCPR` | Contact Persons | `CntctCode` | 11 |
| `OUSR` | Users | `USERID` | 12 |
| `OINV` | A/R Invoice | `DocEntry` | 13 |
| `ORIN` | A/R Credit Memo | `DocEntry` | 14 |
| `ODLN` | Delivery | `DocEntry` | 15 |
| `ORDN` | Returns | `DocEntry` | 16 |
| `ORDR` | Sales Order | `DocEntry` | 17 |
| `OPCH` | A/P Invoice | `DocEntry` | 18 |
| `ORPC` | A/P Credit Memo | `DocEntry` | 19 |
| `OPDN` | Goods Receipt PO | `DocEntry` | 20 |
| `ORPD` | Goods Return | `DocEntry` | 21 |
| `OPOR` | Purchase Order | `DocEntry` | 22 |
| `OQUT` | Sales Quotation | `DocEntry` | 23 |
| `ORCT` | Incoming Payment | `DocEntry` | 24 |
| `ODPS` | Deposit | `DeposId` | 25 |
| `OMTH` | Reconciliation History | `MthAcctCod, IsInternal, MatchNum` | 26 |
| `OCHH` | Check Register | `CheckKey` | 27 |
| `OBTF` | Journal Voucher Entry | `BatchNum, TransId` | 28 |
| `OBTD` | Journal Vouchers List | `BatchNum` | 29 |
| `OJDT` | Journal Entry | `TransId` | 30 |
| `OITW` | Items – Warehouse | `ItemCode, WhsCode` | 31 |
| `OADP` | Print Preferences | `PrintId` | 32 |
| `OCLG` | Activities | `ClgCode` | 33 |
| `ORCR` | Recurring Postings | `RcurCode, Instance` | 34 |
| `ONNM` | Document Numbering | `ObjectCode, DocSubType` | 35 |
| `OCRC` | Credit Cards | `CreditCard` | 36 |
| `OCRN` | Currency Codes | `CurrCode` | 37 |
| `OIDX` | CPI Codes | `IdexCode` | 38 |
| `OADM` | Administration | `Code` | 39 |
| `OCTG` | Payment Terms | `GroupNum` | 40 |
| `OPRF` | Preferences | `FormNumber, UserSign` | 41 |
| `OBNK` | External Bank Statement Received | `AcctCode, Sequence` | 42 |
| `OMRC` | Manufacturers | `FirmCode` | 43 |
| `OCQG` | Card Properties | `GroupCode` | 44 |
| `OTRC` | Journal Entry Codes | `TrnsCode` | 45 |
| `OVPM` | Outgoing Payments | `DocEntry` | 46 |
| `OSRL` | Serial Numbers | `ItemCode, SerialNum` | 47 |
| `OALC` | Loading Expenses | `AlcCode` | 48 |
| `OSHP` | Delivery Types | `TrnspCode` | 49 |
| `OLGT` | Length Units | `UnitCode` | 50 |
| `OWGT` | Weight Units | `UnitCode` | 51 |
| `OITB` | Item Groups | `ItmsGrpCod` | 52 |
| `OSLP` | Sales Employee | `SlpCode` | 53 |
| `OFLT` | Report – Selection Criteria | `FormNum, UserSign, FilterName` | 54 |
| `OTRT` | Posting Templates | `TrtCode` | 55 |
| `OARG` | Customs Groups | `CstGrpCode` | 56 |
| `OCHO` | Checks for Payment | `CheckKey` | 57 |
| `OINM` | Whse Journal | `TransNum, Instance` | 58 |
| `OIGN` | Goods Receipt | `DocEntry` | 59 |
| `OIGE` | Goods Issue | `DocEntry` | 60 |
| `OPRC` | Cost Center | `PrcCode` | 61 |
| `OOCR` | Cost Rate | `OcrCode` | 62 |
| `OPRJ` | Project Codes | `PrjCode` | 63 |
| `OWHS` | Warehouses | `WhsCode` | 64 |
| `OCOG` | Commission Groups | `GroupCode` | 65 |
| `OITT` | Product Tree | `Code` | 66 |
| `OWTR` | Inventory Transfer | `DocEntry` | 67 |
| `OWKO` | Production Instructions | `OrderNum` | 68 |
| `OIPF` | Landed Costs | `DocEntry` | 69 |
| `OCRP` | Payment Methods | `CrTypeCode` | 70 |
| `OCDT` | Credit Card Payment | `Code` | 71 |
| `OCRH` | Credit Card Management | `AbsId, Instance` | 72 |
| `OSCN` | Customer/Vendor Cat. No. | `ItemCode, CardCode, Substitute` | 73 |
| `OCRV` | Credit Payments | `AbsId, PayId, Instance` | 74 |
| `ORTT` | CPI and FC Rates | `RateDate, Currency` | 75 |
| `ODPT` | Postdated Deposit | `DeposId` | 76 |
| `OBGT` | Budget | `AbsId` | 77 |
| `OBGD` | Budget Cost Assess. Mthd | `BgdCode` | 78 |
| `ORCN` | Retail Chains | `ChainCode` | 79 |
| `OALT` | Alerts Template | `Code` | 80 |
| `OALR` | Alerts | `Code` | 81 |
| `OAIB` | Received Alerts | `AlertCode, UserSign` | 82 |
| `OAOB` | Message Sent | `AlertCode, UserSign` | 83 |
| `OCLS` | Activity Subjects | `Code` | 84 |
| `OSPG` | Special Prices for Groups | `CardCode, ObjType, ObjKey` | 85 |
| `SPRG` | Application Start | `LineNum, UserCode` | 86 |
| `OMLS` | Distribution List | `Code` | 87 |
| `OENT` | Shipping Types | `DocEntry` | 88 |
| `OSAL` | Outgoing | `DocEntry` | 89 |
| `OTRA` | Transition | `DocEntry` | 90 |
| `OBGS` | Budget Scenario | `AbsId` | 91 |
| `OIRT` | Interest Prices | `Numerator` | 92 |
| `OUDG` | User Defaults | `Code` | 93 |
| `OSRI` | Serial Numbers for Items | `ItemCode, SysSerial` | 94 |
| `OFRT` | Financial Report Templates | `AbsId` | 95 |
| `OFRC` | Financial Report Categories | `TemplateId, CatId` | 96 |
| `OOPR` | Opportunity | `OpprId` | 97 |
| `OOIN` | Interest | `Num` | 98 |
| `OOIR` | Interest Level | `Num` | 99 |
| `OOSR` | Information Source | `Num` | 100 |
| `OOST` | Opportunity Stage | `Num` | 101 |
| `OOFR` | Defect Cause | `Num` | 102 |
| `OCLT` | Activity Types | `Code` | 103 |
| `OCLO` | Meetings Location | `Code` | 104 |
| `OISR` | Service Calls | `RequestNum` | 105 |
| `OIBT` | Batch No. for Item | `ItemCode, BatchNum, WhsCode` | 106 |
| `OALI` | Alternative Items 2 | `OrigItem, AltItem` | 107 |
| `OPRT` | Partners | `PrtId` | 108 |
| `OCMT` | Competitors | `CompetId` | 109 |
| `OUVV` | User Validations | `IndexID, LineNum` | 110 |
| `OFPR` | Posting Period | `AbsEntry` | 111 |
| `ODRF` | Drafts | `DocEntry` | 112 |
| `OSRD` | Batches and Serial Numbers | `ItemCode, DocType, DocEntry, DocLineNum` | 113 |
| `OUDC` | User Display Cat. | `CodeID` | 114 |
| `OPVL` | Lender – Pelecard | `Code` | 115 |
| `ODDT` | Withholding Tax Deduction Hierarchy | `Numerator` | 116 |
| `ODDG` | Withholding Tax Deduction Groups | `Numerator` | 117 |
| `OUBR` | Branches | `Code` | 118 |
| `OUDP` | Departments | `Code` | 119 |
| `OWST` | Confirmation Level | `WstCode` | 120 |
| `OWTM` | Approval Templates | `WtmCode` | 121 |
| `OWDD` | Docs. for Confirmation | `WddCode` | 122 |
| `OCHD` | Checks for Payment Drafts | `CheckKey` | 123 |
| `CINF` | Company Info | `Version` | 124 |
| `OEXD` | Freight Setup | `ExpnsCode` | 125 |
| `OSTA` | Sales Tax Authorities | `Code, Type` | 126 |
| `OSTT` | Sales Tax Authorities Type | `AbsId` | 127 |
| `OSTC` | Sales Tax Codes | `Code` | 128 |
| `OCRY` | Countries | `Code` | 129 |
| `OCST` | States | `Country, Code` | 130 |
| `OADF` | Address Formats | `Code` | 131 |
| `OCIN` | A/R Correction Invoice | `DocEntry` | 132 |
| `OCDC` | Cash Discount | `Code` | 133 |
| `OQCN` | Query Catagories | `CategoryId` | 134 |
| `OIND` | Triangular Deal | `Code` | 135 |
| `ODMW` | Data Migration | `Code` | 136 |
| `OCSTN` | Workstation ID | `Code` | 137 |
| `OIDC` | Indicator | `Code` | 138 |
| `OGSP` | Goods Shipment | `Code` | 139 |
| `OPDF` | Payment Draft | `DocEntry` | 140 |
| `OQWZ` | Query Wizard | `Code` | 141 |
| `OASG` | Account Segmentation | `AbsId` | 142 |
| `OASC` | Account Segmentation Categories | `SegmentId, Code` | 143 |
| `OLCT` | Location | `Code` | 144 |
| `OTNN` | 1099 Forms | `FormCode` | 145 |
| `OCYC` | Cycle | `Code` | 146 |
| `OPYM` | Payment Methods for Payment Wizard | `PayMethCod` | 147 |
| `OTOB` | 1099 Opening Balance | `VendCode, Form1099, Box1099` | 148 |
| `ORIT` | Dunning Interest Rate | `Code` | 149 |
| `OBPP` | BP Priorities | `PrioCode` | 150 |
| `ODUN` | Dunning Letters | `LineNum` | 151 |
| `CUFD` | User Fields – Description | `TableID, FieldID` | 152 |
| `OUTB` | User Tables | `TableName` | 153 |
| `OCUMI` | My Menu Items | `UserSign , Id_` | 154 |
| `OPYD` | Payment Run | `Code` | 155 |
| `OPKL` | Pick List | `AbsEntry` | 156 |
| `OPWZ` | Payment Wizard | `IdNumber` | 157 |
| `OPEX` | Payment Results Table | `AbsEntry` | 158 |
| `OPYB` | Payment Block | `AbsEntry` | 159 |
| `OUQR` | Queries | `IntrnalKey, Qcategory` | 160 |
| `OCBI` | Central Bank Ind. | `Indicator` | 161 |
| `OMRV` | Inventory Revaluation | `DocEntry` | 162 |
| `OCPI` | A/P Correction Invoice | `DocEntry` | 163 |
| `OCPV` | A/P Correction Invoice Reversal | `DocEntry` | 164 |
| `OCSI` | A/R Correction Invoice | `DocEntry` | 165 |
| `OCSV` | A/R Correction Invoice Reversal | `DocEntry` | 166 |
| `OSCS` | Service Call Statuses | `statusID` | 167 |
| `OSCT` | Service Call Types | `callTypeID` | 168 |
| `OSCP` | Service Call Problem Types | `prblmTypID` | 169 |
| `OCTT` | Contract Template | `TmpltName` | 170 |
| `OHEM` | Employees | `empID` | 171 |
| `OHTY` | Employee Types | `typeID` | 172 |
| `OHST` | Employee Status | `statusID` | 173 |
| `OHTR` | Termination Reason | `reasonID` | 174 |
| `OHED` | Education Types | `edType` | 175 |
| `OINS` | Customer Equipment Card | `insID` | 176 |
| `OAGP` | Agent Name | `AgentCode` | 177 |
| `OWHT` | Withholding Tax | `WTCode` | 178 |
| `ORFL` | Already Displayed 347, 349 and WTax Reports | `DocEntry, ReportType, DocType, LineNum, TaxCode, OrdinalNum` | 179 |
| `OVTR` | Tax Report | `AbsEntry` | 180 |
| `OBOE` | Bill of Exchange for Payment | `BoeKey` | 181 |
| `OBOT` | Bill Of Exchang Transaction | `AbsEntry` | 182 |
| `OFRM` | File Format | `AbsEntry` | 183 |
| `OPID` | Period Indicator | `Indicator` | 184 |
| `ODOR` | Doubtful Debts | `AbsEntry` | 185 |
| `OHLD` | Holiday Table | `HldCode` | 186 |
| `OCRB` | BP – Bank Account | `Country, BankCode, Account, CardCode` | 187 |
| `OSST` | Service Call Solution Statuses | `Number` | 188 |
| `OSLT` | Service Call Solutions | `SltCode` | 189 |
| `OCTR` | Service Contracts | `ContractID` | 190 |
| `OSCL` | Service Calls | `callID` | 191 |
| `OSCO` | Service Call Origins | `originID` | 192 |
| `OUKD` | User Key Description | `TableName, KeyId` | 193 |
| `OQUE` | Queue | `queueID` | 194 |
| `OIWZ` | Inflation Wizard | `AbsEntry` | 195 |
| `ODUT` | Dunning Terms | `TermCode` | 196 |
| `ODWZ` | Dunning Wizard | `WizardId` | 197 |
| `OFCT` | Sales Forecast | `AbsID` | 198 |
| `OMSN` | MRP Scenarios | `AbsEntry` | 199 |
| `OTER` | Territories | `territryID` | 200 |
| `OOND` | Industries | `IndCode` | 201 |
| `OWOR` | Production Order | `DocEntry` | 202 |
| `ODPI` | A/R Down Payment | `DocEntry` | 203 |
| `ODPO` | A/P Down Payment | `DocEntry` | 204 |
| `OPKG` | Package Types | `PkgCode` | 205 |
| `OUDO` | User-Defined Object | `Code` | 206 |
| `ODOW` | Data Ownership – Objects | `Object, SubObject` | 207 |
| `ODOX` | Data Ownership – Exceptions | `QueryId, Object, SubObject` | 208 |
| — | — | — | 209 |
| `OHPS` | Employee Position | `posID` | 210 |
| `OHTM` | Employee Teams | `teamID` | 211 |
| `OORL` | Relationships | `OrlCode` | 212 |
| `ORCM` | Recommendation Data | `DocEntry` | 213 |
| `OUPT` | User Autorization Tree | `AbsId` | 214 |
| `OPDT` | Predefined Text | `AbsEntry` | 215 |
| `OBOX` | Box Definition | `BoxCode, ReportType, BosCode` | 216 |
| `OCLA` | Activity Status | `statusID` | 217 |
| `OCHF` | 312 | `ObjName` | 218 |
| `OCSHS` | User-Defined Values | `IndexID` | 219 |
| `OACP` | Periods Category | `AbsEntry` | 220 |
| `OATC` | Attachments | `AbsEntry` | 221 |
| `OGFL` | Grid Filter | `FormID, GridID, UserCode` | 222 |
| `OLNG` | User Language Table | `Code` | 223 |
| `OMLT` | Multi-Language Translation | `TranEntry` | 224 |
| `OAPA3` | — | — | 225 |
| `OAPA4` | — | — | 226 |
| `OAPA5` | — | — | 227 |
| `SDIS` | Dynamic Interface (Strings) | `FormId, ItemId, ColumnId, Language` | 229 |
| `OSVR` | Saved Reconciliations | `acctCode` | 230 |
| `DSC1` | House Bank Accounts | `AbsEntry` | 231 |
| `RDOC` | Document | `DocCode` | 232 |
| `ODGP` | Document Generation Parameter Sets | `AbsEntry` | 233 |
| `OMHD` | #740 | `AlertCode` | 234 |
| `OACG` | Account Category | `AbsId` | 238 |
| `OBCA` | Bank Charges Allocation Codes | `Code` | 239 |
| `OCFT` | Cash Flow Transactions – Rows | `CFTId` | 241 |
| `OCFW` | Cash Flow Line Item | `CFWId` | 242 |
| `OBPL` | Business Place | `BPLId` | 247 |
| `OJPE` | Local Era Calendar | `Code` | 250 |
| `ODIM` | Cost Accounting Dimension | `DimCode` | 251 |
| `OSCD` | Service Code Table | `AbsEntry` | 254 |
| `OSGP` | Service Group for Brazil | `AbsEntry` | 255 |
| `OMGP` | Material Group | `AbsEntry` | 256 |
| `ONCM` | NCM Code | `AbsEntry` | 257 |
| `OCFP` | CFOP for Nota Fiscal | `ID` | 258 |
| `OTSC` | CST Code for Nota Fiscal | `ID` | 259 |
| `OUSG` | Usage of Nota Fiscal | `ID` | 260 |
| `OCDP` | Closing Date Procedure | `ClsDateNum` | 261 |
| `ONFN` | Nota Fiscal Numbering | `ObjectCode, DocSubType` | 263 |
| `ONFT` | Nota Fiscal Tax Category (Brazil) | `AbsId` | 264 |
| `OCNT` | Counties | `AbsId` | 265 |
| `OTCD` | Tax Code Determination | `AbsId` | 266 |
| `ODTY` | BoE Document Type | `AbsEntry` | 267 |
| `OPTF` | BoE Portfolio | `AbsEntry` | 268 |
| `OIST` | BoE Instruction | `AbsEntry` | 269 |
| `OTPS` | Tax Parameter | `AbsId` | 271 |
| `OTFC` | Tax Type Combination | `AbsId` | 275 |
| `OFML` | Tax Formula Master Table | `AbsId` | 276 |
| `OCNA` | CNAE Code | `AbsId` | 278 |
| `OTSI` | Sales Tax Invoice | `DocEntry` | 280 |
| `OTPI` | Purchase Tax Invoice | `DocEntry` | 281 |
| `OCCD` | Cargo Customs Declaration Numbers | `CCDNum` | 283 |
| `ORSC` | Resources | `ResCode` | 290 |
| `ORSG` | Resource Properties | `ResTypCod` | 291 |
| `ORSB` | ResGrpCod | `ResGrpCod` | 292 |
| — | RecordSet | — | 300 |
| — | Bridge | — | 305 |
| `OITR` | Internal Reconciliation | `ReconNum` | 321 |
| `OPOS` | POS Master Data | `EquipNo` | 541 |
| `ODRF` | Stock Transfer Draft | `DocEntry` | 1179 |
| `OMSG` | Messaging Service Settings | `USERID` | 10000105 |
| `OBTN` | Batch Numbers Master Data | `AbsEntry` | 10000044 |
| `OSRN` | Serial Numbers Master Data | `AbsEntry` | 10000045 |
| `OIVK` | IVL Vs OINM Keys | `TransSeq` | 10000062 |
| `OIQR` | Inventory Posting | `DocEntry` | 10000071 |
| `OFYM` | Financial Year Master | `AbsId` | 10000073 |
| `OSEC` | Sections | `AbsId` | 10000074 |
| `OCSN` | Certificate Series | `AbsId` | 10000075 |
| `ONOA` | Nature of Assessee | `AbsId` | 10000077 |
| `RTYP` | Document Type List | `CODE` | 10000196 |
| `OUGP` | UoM Group | `UgpEntry` | 10000197 |
| `OUOM` | UoM Master Data | `UomEntry` | 10000199 |
| `OBFC` | Bin Field Configuration | `AbsEntry` | 10000203 |
| `OBAT` | Bin Location Attribute | `AbsEntry` | 10000204 |
| `OBSL` | Warehouse Sublevel | `AbsEntry` | 10000205 |
| `OBIN` | Bin Location | `AbsEntry` | 10000206 |
| `ODNF` | DNF Code | `AbsEntry` | 140000041 |
| `OUGR` | Authorization Group | `GroupId` | 231000000 |
| `OEGP` | E-Mail Group | `EmlGrpCode` | 234000004 |
| `OGPC` | Government Payment Code | `AbsId` | 243000001 |
| `OIQI` | Inventory Opening Balance | `DocEntry` | 310000001 |
| `OBTW` | Batch Attributes in Location | `AbsEntry` | 310000008 |
| `OLLF` | Legal List Format | `AbsEntry` | 410000005 |
| `OHET` | Object: HR Employee Transfer | `TransferID` | 480000001 |
| `OTCX` | Tax Code Determination | `DocEntry` | 540000005 |
| `OPQT` | Purchase Quotation | `DocEntry` | 540000006 |
| `ORCP` | Recurring Transaction Template | `AbsEntry` | 540000040 |
| `OCCT` | Cost Center Type | `CctCode` | 540000042 |
| `OACR` | Accrual Type | `Code` | 540000048 |
| `ONFM` | Nota Fiscal Model | `AbsEntry` | 540000056 |
| `OBFI` | Brazil Fuel Indexer | `ID` | 540000067 |
| `OBBI` | Brazil Beverage Indexer | `ID` | 540000068 |
| `OCPT` | Cockpit Main Table | `AbsEntry` | 1210000000 |
| `OWTQ` | Inventory Transfer Request | `DocEntry` | 1250000001 |
| `OOAT` | Blanket Agreement | `AbsID` | 1250000025 |
| `OKPI` | Key Performance Indicator Package | `AbsEntry` | 1320000000 |
| `OTGG` | Target Group | `TargetCode` | 1320000002 |
| `OCPN` | Campaign | `CpnNo` | 1320000012 |
| `OROC` | Retorno Operation Codes | `AbsEntry` | 1320000028 |
| `OPSC` | Product Source Code | `Code` | 1320000039 |
| `ODTP` | Fixed Assets Depreciation Types | `Code` | 1470000000 |
| `OADT` | Fixed Assets Account Determination | `Code` | 1470000002 |
| `ODPA` | Fixed Asset Depreciation Areas | `Code` | 1470000003 |
| `ODPP` | Depreciation Type Pools | `Code` | 1470000004 |
| `OACS` | Asset Classes | `Code` | 1470000032 |
| `OAGS` | Asset Groups | `Code` | 1470000046 |
| `ODMC` | G/L Account Determination Criteria – Inventory | `DmcId` | 1470000048 |
| `OACQ` | Capitalization | `DocEntry` | 1470000049 |
| `OGAR` | G/L Account Advanced Rules | `AbsEntry` | 1470000057 |
| `OACD` | Credit Memo | `DocEntry` | 1470000060 |
| `OBCD` | Bar Code Master Data | `BcdEntry` | 1470000062 |
| `OINC` | Inventory Counting | `DocEntry` | 1470000065 |
| `OEDG` | Discount Groups | `AbsEntry` | 1470000077 |
| `OCCS` | Cycle Count Determination | `WhsCode` | 1470000092 |
| `OPRQ` | Purchase Request | `DocEntry` | 1470000113 |
| `OWLS` | Workflow – Task Details | `TaskID` | 1620000000 |
| `ORRR` | Return Request | `DocEntry` | 234000031 |
| `OPRR` | Goods Return Request | `DocEntry` | 234000032 |



## Referensi cepat "otak" skill

Dokumen ringkas seluruh paket (konvensi tabel, SQL vs HANA, DI API, UI API) ada di
`references/otak-skills.md` — baca file ini bila butuh ikhtisar cepat sebelum
membuka modul spesifik.

---

## Sub-Module: sap-b1-concepts

# SAP Business One — Functional Concepts

Consultant/business-user level knowledge: what SAP B1 IS, its modules, how business processes flow through it, and how the UI is organized. For code-level work use `sap-b1-addon-dev` (DI/UI API, C#) and `sap-b1-web-integration` (Service Layer, Laravel). For HANA queries use `sap-hana-cli`.

## What SAP B1 Is

- ERP for **small & mid-sized businesses (SMB)** — SAP's entry-level ERP (vs S/4HANA for enterprises)
- **All-in-one**: finance, sales, purchasing, inventory, production, CRM, service, HR, reporting in one system
- Two deployment options: **on-premise** (SQL Server or HANA) and **cloud** (SAP Business One Cloud)
- Key differentiator vs S/4HANA: faster implementation, simpler licensing, designed for SMB scale (10-500 users)
- Localization: strong country-specific versions (tax, e-invoicing, banking formats) — critical in Indonesia (e-Faktur, PPh, etc.)

## Database Platform: HANA vs SQL Server

SAP B1 support dua database backend. Pilihan platform mempengaruhi performance, deployment options, dan integration methods:

### Comparison

| Aspect | SAP HANA | Microsoft SQL Server |
|--------|----------|----------------------|
| Architecture | In-memory, column-store | Disk-based, row-store |
| Performance | Cepat analytics/query massal | Cukup transaksi harian |
| Cloud | HANA Cloud (Service Layer only) | N/A (on-prem only) |
| Cost | Lebih mahal (in-memory hardware) | Lebih murah, familiar |
| DI API support | On-prem only | On-prem only |
| UI API support | On-prem only | On-prem only |
| Service Layer | Yes (port 50000/50001) | Yes (port 50000/50001) |
| Analytics | HANA views, dashboards, cockpit | Standard B1 reports |
| SQL dialect | HANA SQL (LIMIT, \|\|, CURRENT_DATE) | T-SQL (TOP, +, GETDATE()) |

### When to choose HANA
- Client butuh analytics cepat / real-time dashboard
- Volume data besar (>500GB)
- Rencana migrasi ke cloud (HANA Cloud)
- Butuh HANA-specific features (prediction, text search)

### When to choose SQL Server
- Budget terbatas
- Tim familiar SQL Server / T-SQL
- Volume data sedang (SMB scale)
- Tidak butuh advanced analytics
- On-prem deployment only

### Integration impact (functional consultant level)
- **HANA Cloud**: DI API & UI API tidak bisa connect. Service Layer (REST/OData) satu-satunya integration method. Add-on development harus dirancang sebagai web integration, bukan client add-on.
- **HANA on-prem**: DI API, UI API, Service Layer semua bisa. Add-on development normal. UDT/UDF/UDO proses sama.
- **SQL Server on-prem**: DI API, UI API, Service Layer semua bisa. Add-on development normal.

## UI & Navigation (Fiori-style Cockpit)

Modern B1 uses a **Fiori-style cockpit** (HTML5-based) — flat, clean, tile-based home screen, NOT the old heavy WinForms-style UI. Key elements:

- **Cockpit/tiles**: role-based home screen with app tiles (Sales, Purchasing, Inventory, Finance...). Users personalize tiles per role.
- **Main menu**: module groups — Business Partners, Sales, Purchasing, Inventory, Production, MRP, Service, Financials, Reports, Administration.
- **Master data vs Documents vs Reports**: three core screen types:
  - *Master Data* — static records (Business Partners, Items, Price Lists, G/L Accounts)
  - *Documents* — transactional (Sales Order, Delivery, A/R Invoice, Purchase Order, Goods Receipt PO)
  - *Reports* — queryable outputs (financial statements, inventory status, aging)
- **Personalization**: user can customize cockpit, table columns, document layouts (Print Layout designer / Crystal Reports), and default values per user.
- **Keyboard/UX**: search box (global quick search), drag-and-drop columns, table filters, saved queries.
- Add-on UI (UI API) renders as additional forms/menus inside this same cockpit.

## Core Modules & Business Processes

### 1. Sales (Order-to-Cash)
Master data: Customers (Business Partners). Process flow:
```
Customer → Sales Opportunity (optional, CRM) → Sales Quotation → Sales Order
→ Delivery (goods out) → A/R Invoice → Incoming Payment → Cash
```
- **Pick & Pack** — warehouse pick list + pack for delivery, with availability checking
- **Document Generation Wizard** — mass-create documents (e.g. many Sales Orders → Deliveries)
- CRM: opportunities, activities, campaigns, pipeline stages
- Documents update inventory + G/L automatically (posting)

### 2. Purchasing (Procure-to-Pay)
Master data: Vendors (Business Partners), Items.
```
Requisition → Purchase Quotation → Purchase Order → Goods Receipt PO (goods in)
→ A/P Invoice → Outgoing Payment → Cash
```
- Purchase Request (internal need) → RFQ → PO workflow
- Landed costs, special procurement scenarios (drop-ship, subcontracting)
- Goods Receipt PO can be posted with or without invoice (accrual options)

### 3. Inventory & Warehouses
Master data: Items + Item Groups, Warehouses, Units of Measure (UoM), Bin Locations, Serial/Batch tracking.
- **Valuation methods**: Moving Average, FIFO, Standard Price (per item) — affects COGS & stock value
- **Serial numbers** (unique per unit) & **batches** (lot-based, e.g. expiry date)
- **Bin locations** — warehouse zones/racks for pick path optimization
- Item master: per-warehouse stock, price lists, purchasing/sales data, BOM component flag
- Inventory transactions: Goods Receipt, Goods Issue, Transfer, Inventory Count (cycle/physical), Revaluation

### 4. Pricing
- **Price Lists** — multiple lists (retail, wholesale, promo), base list + price list groups (customer/vendor assignment)
- **Special prices** — per Business Partner, period-valid, quantity-based
- **Discounts** — line-level, document-level, group discounts, cash discounts (payment terms)
- Price update: automatic (periodic price list updates, price wizard), manual, currency-based
- Price Lists define selling & purchasing prices; exchange rates for foreign currency docs

### 5. Production & MRP (light manufacturing)
- **BOM (Bill of Materials)** — component → parent item structure
- **Resources** — machines/work centers with capacity
- **Production Orders** — issue materials (Goods Issue), production receipt (finished goods in)
- **MRP** — Material Requirements Planning: net requirement calc from sales orders, forecasts, inventory, BOM explosion → generates purchase/production recommendations
- Designed for light manufacturing (SMB), not full S/4HANA PP

### 6. Service (after-sales)
- Service Calls (tickets), Customer Equipment Cards (installed base), Contracts (warranty/SLA)
- Link to inventory (spare parts), sales (chargeable calls), technicians
- Service process: call logged → assign technician → parts used → resolution → invoice if chargeable

### 7. Finance & Accounting
- **Chart of Accounts (COA)** — G/L accounts structure (balance sheet + P&L)
- **Automatic journal entries** — documents post to G/L automatically (goods receipt → inventory + GR/IR, invoice → expense + AP, etc.)
- **Manual journal entries / Journal Voucher** — direct postings
- **Financial setup**: document numbering, posting periods, tax definitions, exchange rates, default accounts (inventory, revenue, expense, tax)
- **Posting Templates + Recurring Postings** — recurring entries (rent, depreciation, subscriptions)
- **Internal reconciliation** — match G/L account items & Business Partner open transactions (incoming vs outgoing payments)
- **Banking**: Payment Wizard (propose payments for open invoices), bank statements, checks, credit cards, external reconciliation
- **Fixed Assets** — asset master, capitalization, depreciation (straight-line, declining balance), retirement, reports
- **Cost Accounting** — cost centers, profit centers, allocation rules, multi-dimensional reporting
- **Financial reports**: Trial Balance, Balance Sheet, P&L, Cash Flow, Aging (AR/AP), Journal, General Ledger

### 8. Implementation & Administration (consultant tools)
- **Project methodology**: implementation activities (discover → setup → test → go-live), implementation tools
- **Company creation**: new company wizard, key settings (currency, fiscal year, posting periods)
- **Authorizations**: user setup, user groups, general authorizations, data ownership (per user/group restrictions)
- **Document numbering**: number ranges per document, series assignment (per user/group), automatic vs manual numbering
- **Customization tools**: 
  - UDF (User-Defined Fields) — add fields to existing tables/forms
  - UDT (User-Defined Tables) — new tables
  - UDO (User-Defined Objects) — full objects with header+lines+form
  - UDV (User-Defined Values) — value lists for UDFs
  - Query Manager — save/reuse SQL queries
  - Alerts — predefined + custom alerts (condition-based notifications)
  - **Approval Process** — workflow: define approval templates, conditions (amount threshold, document type), approver levels
  - Print Layout Designer / Crystal Reports for document layouts
- **HANA analytics**: dashboards/cockpits from HANA views (user-defined dashboards)

## Document Lifecycle & Posting Logic (core concept)

- Documents follow **status lifecycle**: Draft → Open → Closed (e.g. Sales Order → Delivery → Invoice → Payment)
- **Copy-to**: documents copy from predecessor (quotation → order → delivery → invoice) carrying lines, prices, quantities
- **Posting**: each logistics document posts automatic journal entries; inventory updates happen at goods movement (Delivery / Goods Receipt), NOT at order
- **Document numbering**: series per document type; per-user series assignment
- **Base document linking**: target docs reference base docs (e.g. invoice references delivery references order) — enables drill-down, partial deliveries, returns
- **Returns/Credit Memos**: reverse flows (Sales Return, A/R Credit Memo, Purchase Return, A/P Credit Memo)
- **Draft documents**: save incomplete docs as Draft, continue later
- **Warehouse & BP integration**: every document touches inventory (if item-based) and BP balance (AR/AP)

## Posting Logic — Journal Entries per Document (perpetual inventory)

Every logistics document posts automatic journal entries. Exact accounts depend on G/L account determination (per item group, per warehouse, per BP). Default structure (moving average valuation):

### Sales documents
| Document | Debit | Credit | Notes |
|---|---|---|---|
| **Delivery** (goods out) | COGS (Expense) | Inventory | qty × item cost; updates moving average |
| **A/R Invoice based on Delivery** | A/R (BP account) | Revenue | **NO inventory posting** — already posted at delivery |
| **A/R Invoice (direct, no delivery)** | A/R | Revenue | also posts COGS/Inventory if goods not yet delivered |
| **Return based on Delivery** | Inventory | COGS | cost taken from the return doc, updates moving avg |
| **A/R Credit Memo** | Revenue | A/R | reverses invoice; inventory if goods returned |

### Purchasing documents
| Document | Debit | Credit | Notes |
|---|---|---|---|
| **Goods Receipt PO** (goods in) | Inventory | **Allocation account** (GR/IR) | allocation = temporary, cleared later by A/P Invoice |
| **Goods Receipt PO with Freight** | Inventory + Freight | Allocation | freight capitalized into stock value |
| **A/P Invoice based on GRPO** | Allocation (clearing) | Vendor (A/P) | allocation account debited same amount it was credited — clears to zero |
| **A/P Invoice (direct)** | Expense/Inventory | Vendor | no allocation involved |
| **Goods Return** | Allocation | Inventory | reverses GRPO |
| **A/P Credit Memo** | Vendor | Allocation/Expense | reverses invoice |
| **A/P Invoice w/ price difference vs GRPO** | Allocation + Inventory (adj) | Vendor | price change updates inventory + moving average |

### Inventory transactions
| Document | Debit | Credit |
|---|---|---|
| **Goods Receipt** (manual, non-PO) | Inventory | Allocation/Expense (per settings) |
| **Goods Issue** (manual) | Expense/COGS | Inventory |
| **Inventory Transfer** | Inventory (to wh) | Inventory (from wh) — no P&L effect |
| **Opening quantities / initial posting** | Inventory | Opening balance / clearing |
| **Landed Costs** | Inventory | Allocation/Vendor | appends cost to item value |

### Key rules
1. **GR/IR allocation account** — central to purchase accrual: GRPO credits allocation, A/P invoice debits it. Balance = goods received but not yet invoiced. Monthly closing = accrual for uninvoiced GRPOs.
2. **Delivery, not invoice, moves inventory** (perpetual system). Invoice on top of delivery only books revenue/AR.
3. **Price difference GRPO vs invoice** — hits inventory (and moving average), NOT expense, in perpetual system.
4. **Purchase Accounts Posting System** (localization option) — adds P&L purchase account dimension: purchase expense debited directly at GRPO for period analysis; works alongside perpetual inventory; involves GRPO, goods returns, A/P invoices/corrections, credit memos, landed costs. Not linked to valuation basis.

## Approval Process (functional detail)

Purpose: control document release via multi-level workflow, standard in B1 (no add-on needed).

### Setup flow
1. **Administration → Approval Process → Approval Templates** — define per document type (Purchase Order, A/R Invoice, Goods Receipt PO, etc.)
2. Template settings: name, document type, **conditions** (e.g. total > 50M, specific BP group, specific warehouse, branch), validity period
3. **Stages/levels**: each level has one or more approvers (user or user group), order matters
4. Optional: escalation / replacement approver per level, "approve all levels by same person" option, termination conditions

### Runtime flow
1. User adds document (e.g. PO 100M) → document goes to **Pending status** (approval request created, doc locked from further changes)
2. Approvers see task in **Approval Status** report / cockpit notifications; can **Approve, Reject, or Return for revision** with comments
3. All approvers at level approve → next level → final approval → document **released** (status Open, can proceed: GRPO, etc.)
4. Any rejection → document cancelled/rejected; return → user edits and resubmits

### Gotchas
- Conditions evaluated on **document values at save time** — if doc changes before approval, re-evaluation needed
- **Data ownership** affects who sees approval tasks (BP group restrictions)
- Approval templates are per document type — no cross-document workflow chaining
- Rejected docs keep their number (series gap) — audit trail visible
- Add-ons (UI API) can hook approval events for custom notifications
- Approval does NOT block automatic postings of predecessor docs — e.g. GRPO approved but its A/P invoice can be in different approval flow

## Business Logic Gotchas (functional level)

1. **Inventory valuation affects COGS** — valuation method choice (Moving Average vs FIFO vs Standard) changes P&L. Set BEFORE stock movement; hard to change later.
2. **Document postings are automatic** — no separate "post" button for logistics docs; posting happens on add/update. Finance sees entries instantly.
3. **Series & numbering** — assign series to users/groups early; gaps in numbering = deleted docs (audit red flag).
4. **Exchange rate timing** — rates are date-based; revaluation needed for multi-currency.
5. **Approval process is document-type based** — conditions evaluate on document values (total, BP, branch). Draft → approval chain → release.
6. **Data ownership vs authorizations** — two separate permission layers: *what* you can do (authorizations) vs *whose* data you see (data ownership).
7. **MRP explosion** — MRP output only as good as master data (BOM accuracy, lead times, safety stock, forecast).
8. **Cost accounting dimensions** — profit/cost centers assigned at document level (line or header) drive allocation reports.
9. **Fixed asset capitalization** — depreciation starts per configured rule (mid-period, pro-rata); manual vs automatic posting.
10. **Document Generation Wizard & Pick/Pack** — automation tools for high-volume flows; availability check before delivery.

## Learning Path (official SAP courses)

- **TB1000 Managing Logistics in SAP Business One** (11h) — navigation, purchasing, sales, inventory, pricing, production/MRP, service
- **TB1100 Handling Accounting in SAP Business One** (5h40m) — accounting basics, financial setup, financial process, banking, controlling reports, fixed assets, cost accounting
- **TB1200 Implementing SAP Business One** (3h20m) — implementation tools, system setup & administration, customization tools
- **C_TB120 certification** — "SAP Certified - SAP Business One" (implementation track)
- All available free on learning.sap.com (search "SAP Business One")

## Posting & Approval References (official)

- SAP Help Portal → SAP Business One 10.0 → "How to Set Up and Manage a Perpetual Inventory System in SAP Business One" — full journal entry structures per document (Moving Average / Standard / FIFO sections), revaluation, inventory audit reports, FIFO layers, purchase accounts posting
- SAP Learning (free, learning.sap.com): TB1000/TB1100/TB1200 + C_TB120 certification
- Approval process: SAP Help → Administration → Approval Process (templates, conditions, stages)

## Verification Checklist
- [ ] Module covered: Sales, Purchasing, Inventory, Pricing, Production/MRP, Service, Finance, Admin/Implementation
- [ ] Document flows show copy-from relationships (order → delivery → invoice)
- [ ] Posting logic explained (auto journal entries, inventory at goods movement)
- [ ] UI: cockpit/tiles, master data vs documents vs reports distinction
- [ ] Customization: UDF/UDT/UDO/UDV, queries, alerts, approval process

---

## Sub-Module: sap-b1-db

# SAP B1 — Database & Query Skill

Sumber: `REFDB.chm` — Database Tables Reference (SAP B1 SDK 10.0), 2.844 tabel.
SAP B1 berjalan di atas **Microsoft SQL Server** atau **SAP HANA** — sintaks kedua platform harus dikuasai.

## Alur kerja (WAJIB)

1. **Cek nama tabel/field** sebelum menulis query — jangan pernah menebak:

```bash
python C:/Users/yudah/.sap-b1-skills/search_sap.py db <tabel>        # info tabel
python C:/Users/yudah/.sap-b1-skills/search_sap.py dbfields <tabel>  # semua field + tipe
```

2. **Cek pemetaan dokumen→tabel** di bagian bawah bila query melibatkan dokumen penjualan/pembelian.
3. Tulis query, sesuaikan sintaks SQL Server **atau** HANA (lihat tabel perbedaan di bawah).
4. Verifikasi nama field dari hasil `dbfields` sebelum menyelesaikan.

## Konvensi penamaan tabel

| Prefix | Arti | Contoh |
|--------|------|--------|
| `O...` | Master data / header dokumen | `OCRD` (Business Partners), `OITM` (Items), `OINV` (A/R Invoice header) |
| `R...` | Baris (lines) dokumen | `RDR1` (Sales Order lines), `INV1` (Invoice lines), `RCT1` (Incoming Payments lines) |
| `N...` | Penomoran dokumen | `NNM1` (Document Numbering) |
| `A...` | Log / archive | `AADM` (Administration log) |
| `U_...` | User-Defined Table | `U_MYTABLE` (buatan user) |
| `@...` | User-Defined Table via DI (named query) | `@U_MYTABLE` dalam SQL |

### Aturan penting

- **`DocEntry`** = kunci internal (identity) dokumen; **`DocNum`** = nomor dokumen tampilan (bisa beda karena numbering series).
- **`CardCode`** = kode Business Partner; **`ItemCode`** = kode item.
- **`LineNum`** = nomor baris dokumen (0-based di tabel `R...`).
- Field User-Defined (UDF) pada tabel standar berprefix `U_` (mis. `OITM.U_MyField`).
- Tabel header dokumen: `DocEntry`, `DocNum`, `CardCode`, `CardName`, `DocDate`, `DocDueDate`, `DocTotal`, `DocCurrency`, `DocStatus`, `CANCELED`, `DocType`, `Series`.
- Tabel baris dokumen: `DocEntry` (link ke header), `LineNum`, `ItemCode`, `Dscription`, `Quantity`, `Price`, `LineTotal`, `WarehouseCode`, `OcrCode` (profit center), `TaxCode`, `UoMCode`.
- **Master Object Type & Primary Key**: Untuk mapping lengkap 326 tabel, ObjType, dan Primary Key resmi (dipakai pada SP_TransactionNotification, BaseType/TargetType, DI API BoObjectTypes, UI API ObjectKey, Service Layer), rujuk ke bagian **Master Reference: SAP Business One Object Types, Primary Keys & Object Keys**.
- **Quantity di SAP B1 disimpan dengan tanda**: dokumen penjualan positif, dokumen pembelian/retur negatif (untuk perhitungan stok).

## Katalog tabel inti

### Master data
| Tabel | Isi |
|-------|-----|
| `OADM` | Administration — setting perusahaan (satu baris) |
| `OCRD` | Business Partners (customer + vendor + prospek, dibedakan `CardType` C/V/L) |
| `OITM` | Items master (termasuk `ItemType`: 4=item, 1=service, 2=labour) |
| `OITW` | Item per warehouse (stok) |
| `OITL` | Bin / serial / batch per warehouse |
| `OWHS` | Warehouses |
| `OACT` | Chart of Accounts |
| `OCPR` | Cost Centers (profit centers) |
| `OTAX` | Tax codes |
| `OUOM` / `OUOMG` | Unit of Measure / groups |
| `OCTG` | Item groups |
| `OCST` | Item cost categories |
| `OPRC` | Price lists |
| `OITM`+`ITM1` | Item price list rows (`ITM1`) |
| `ONPM` | Numbering series (per doc type) |
| `OUSR` | Users |
| `OHEM` | Employees |
| `OBPL` | Branches |
| `OCRY` | Countries |
| `OSTT` | Territories |
| `OCLT` | Local currencies |

### Dokumen penjualan
| Dokumen | Header | Baris |
|---------|--------|-------|
| Quotation | `OQUT` | `QUT1` |
| Sales Order | `ORDR` | `RDR1` |
| Delivery | `ODLN` | `DLN1` |
| A/R Invoice | `OINV` | `INV1` |
| A/R Credit Memo | `ORIN` | `RIN1` |
| A/R Reserve Invoice | `OINV` (Reserve) | `INV1` |
| Returns | `ORDN` | `RDN1` |
| Draft | `ODRF` | `DRF1` |

### Dokumen pembelian
| Dokumen | Header | Baris |
|---------|--------|-------|
| Purchase Quotation | `OQUT` (P) | `QUT1` |
| Purchase Order | `OPOR` | `POR1` |
| Goods Receipt PO | `OPDN` | `PDN1` |
| A/P Invoice | `OPCH` | `PCH1` |
| A/P Credit Memo | `ORPC` | `RPC1` |
| A/P Return | `ORPD` | `RPD1` |
| Landed Cost | `OIDC` | `IDC1` |

### Inventory & produksi
| Tabel | Isi |
|-------|-----|
| `OIGN` / `OIGE` | Inventory Gen Entry / Exit (header) |
| `IGN1` / `IGE1` | Barisnya |
| `OWTR` / `WTR1` | Inventory Transfer |
| `OWTQ` / `WTQ1` | Inventory Transfer Request |
| `OWOR` / `WOR1` | Production Orders |
| `OITR` | Inventory counting |
| `OSRN` | Serial numbers |
| `OBTN` | Batches |

### Keuangan
| Tabel | Isi |
|-------|-----|
| `OJDT` | Journal Entry (header) |
| `JDT1` | Journal Entry lines |
| `OACT` | Chart of Accounts |
| `OVPM` / `VPM1` | Vendor Payments |
| `ORCT` / `RCT1` | Incoming Payments (customer) |
| `OINV` (A/R) + `OINV`… | Invoice / Credit Memo |
| `OBTF` | Bank transfers |
| `OCHH` | Checks for Payment |
| `OAPR` | A/P advances |
| `ORIT` | Incoming payments batches |
| `OADB` | Budget distribution |
| `OBT` | Budget |

### Lainnya
| Tabel | Isi |
|-------|-----|
| `OALR` | Alerts |
| `OATC` / `ATC1` | Attachments |
| `OATL` | Approval templates |
| `OUBR` | User branches |
| `OUSG` | User groups |
| `OQUT`/`ODRF` … | Documents draft / quotation |
| `OCRD` + `CRD1` | BP addresses (`CRD1`) |
| `OCPR` + `OCPC` | Cost centers / categories |
| `OPRJ` | Projects |
| `OITM` + `ITL1` | Item bin locations |

> Daftar lengkap: `python C:/Users/yudah/.sap-b1-skills/search_sap.py db <kata_kunci>` (mis. `db "sales order"`, `db tax`).

## Sintaks: SQL Server vs SAP HANA

SAP B1 query biasanya ditulis untuk **salah satu** platform. Selalu tanyakan target, atau tawarkan dua varian.

| Operasi | SQL Server | SAP HANA |
|---------|-----------|----------|
| Ambil N baris pertama | `SELECT TOP 10 ...` | `SELECT ... LIMIT 10` (atau `TOP 10`) |
| Gabung string | `A + B` atau `CONCAT(A,B)` | `A \|\| B` atau `CONCAT(A,B)` |
| Tanggal hari ini | `GETDATE()` | `CURRENT_DATE` / `NOW()` |
| Cast tanggal | `CAST(x AS DATE)` | `TO_DATE(x,'YYYY-MM-DD')` |
| Tambah hari | `DATEADD(day, 5, d)` | `ADD_DAYS(d, 5)` |
| Bulan dari tanggal | `MONTH(d)` | `MONTH(d)` (sama) |
| Year | `YEAR(d)` | `YEAR(d)` (sama) |
| Panjang string | `LEN(s)` | `LENGTH(s)` / `LEN(s)` |
| Substring | `SUBSTRING(s, start, len)` | `SUBSTRING(s, start, len)` (sama) |
| Cari posisi | `CHARINDEX(sub, s)` | `LOCATE(sub, s)` |
| Null jika kosong | `ISNULL(x, 0)` | `IFNULL(x, 0)` / `COALESCE` |
| Case | `CASE WHEN ... THEN ... END` | sama |
| Tabel sementara | `#temp` | Session-local table (prefer subquery/CTE) |
| Konkatenasi grup | `STRING_AGG` (2017+) | `STRING_AGG` (HANA 2.0 SPS03+) |
| Pembulatan | `ROUND(x, 2)` | `ROUND(x, 2)` (sama) |
| Unicode string | `N'...'` | `'...'` (UTF-8 native) |
| Komentar | `--` / `/* */` | sama |

### Tips khusus SAP B1

- **Field tanggal** disimpan sebagai datetime — bandingkan dengan `CAST(GETDATE() AS DATE)` di SQL Server, atau gunakan rentang `>= '2026-01-01' AND < '2026-02-01'` untuk portabilitas.
- **Jangan gunakan `SELECT *`** pada tabel besar (OINV, RDR1, JDT1) — selalu filter kolom.
- **Nomor dokumen**: join header dan baris via `DocEntry`, filter `CANCELED = 'N'` bila hanya butuh dokumen aktif.
- **DocType**: `'I'` = item document, `'S'` = service document — memengaruhi isi tabel baris.
- **UserTables** (U_): di SQL Server dipanggil `U_NAMA`; di HANA `"@U_NAMA"` untuk named query, atau `U_NAMA` untuk view. Selalu cek via DI API `UserTablesMD` bila ragu.
- **Query Manager**: query yang disimpan user ada di tabel `OQMN` (Query Manager).
- Untuk laporan Crystal Reports, gunakan koneksi langsung ke DB B1; jangan pakai `ONP` view kecuali diperlukan.

## Pola query umum

### 1. Open sales orders (stok belum dikirim)
```sql
SELECT RDR1.DocEntry, RDR1.LineNum, RDR1.ItemCode, OITM.ItemName,
       RDR1.Quantity - RDR1.PackedQty AS OpenQty, RDR1.Price
FROM RDR1
INNER JOIN ORDR ON RDR1.DocEntry = ORDR.DocEntry
INNER JOIN OITM ON RDR1.ItemCode = OITM.ItemCode
WHERE ORDR.DocStatus = 'O' AND ORDR.CANCELED = 'N'
  AND RDR1.Quantity - RDR1.PackedQty > 0
ORDER BY ORDR.DocNum
```

### 2. Stok per item per warehouse
```sql
SELECT T0.ItemCode, T0.ItemName, T1.WhsCode, T1.OnHand
FROM OITM T0
INNER JOIN OITW T1 ON T0.ItemCode = T1.ItemCode
WHERE T0.ItemType = 4
```

### 3. Penjualan per customer bulan ini (SQL Server)
```sql
SELECT T0.CardCode, T0.CardName, SUM(T1.LineTotal) AS Sales
FROM OINV T0
INNER JOIN INV1 T1 ON T0.DocEntry = T1.DocEntry
WHERE T0.DocDate >= DATEADD(month, DATEDIFF(month, 0, GETDATE()), 0)
  AND T0.CANCELED = 'N' AND T0.DocStatus = 'C'
GROUP BY T0.CardCode, T0.CardName
ORDER BY Sales DESC
```

### 4. Versi HANA dari pola 3
```sql
SELECT T0.CardCode, T0.CardName, SUM(T1.LineTotal) AS Sales
FROM OINV T0
INNER JOIN INV1 T1 ON T0.DocEntry = T1.DocEntry
WHERE T0.DocDate >= ADD_DAYS(LAST_DAY(ADD_MONTHS(CURRENT_DATE, -1)), 1)
  AND T0.CANCELED = 'N' AND T0.DocStatus = 'C'
GROUP BY T0.CardCode, T0.CardName
ORDER BY Sales DESC
```

### 5. Saldo piutang customer (umur piutang sederhana)
```sql
SELECT T0.CardCode, T0.CardName,
       SUM(CASE WHEN T0.DocDate < DATEADD(day, -30, GETDATE()) THEN T0.DocTotal ELSE 0 END) AS Over30
FROM OINV T0
WHERE T0.CANCELED = 'N' AND T0.DocStatus = 'O'
GROUP BY T0.CardCode, T0.CardName
```

## Pitfalls

- `PackedQty` di tabel baris dokumen = quantity yang sudah dipenuhi — untuk open quantity selalu kurangi.
- Field `Price` vs `PriceAfterVAT`: gunakan `Price` untuk harga tanpa pajak, `TotalSumSy`/`DocTotalSy` untuk total dalam mata uang sistem.
- Kolom `DocTotal` dalam mata uang dokumen; `DocTotalSy` dalam mata uang sistem — perhatikan perbedaannya.
- Jangan lupa filter `CANCELED`; dokumen yang dibatalkan tetap ada di tabel.
- `Quantity` bisa negatif (retur/pembelian) — sesuaikan logika stok.
- Di HANA, nama tabel case-sensitive — SAP B1 menggunakan huruf besar.

---

## Sub-Module: sap-b1-di-api

# SAP B1 — DI API Add-On Skill

Sumber: `REFDI.chm` — SAP B1 DI API 10.0 Objects Reference (10.00.330), 2.960 objek.
Library: `SAPbobsCOM` (COM / Interop), dipakai dari .NET, VB6, atau melalui wrapper.

## Model objek inti

| Objek | Peran |
|-------|-------|
| `Company` | Objek utama. SATU-SATUNYA objek yang dibuat langsung (`oCompany = New SAPbobsCOM.Company`). Semua objek lain dibuat lewat Company. |
| `Company.GetBusinessObject(oXXX)` | Membuat objek bisnis dari enum `BoObjectTypes`. |
| `Documents` | Objek dokumen marketing/inventory (penjualan, pembelian). Header + `Lines`. |
| `BusinessPartners` | Business partner (customer/vendor). |
| `Items` | Item master. |
| `Recordset` | Akses data mentah; method `DoQuery` menjalankan SQL apa pun. |
| `SBObob` | Akses data cepat; hasil berupa `Recordset`. |
| `CompanyService` | Data administrasi: `AdminInfo` (OADM), `CompanyInfo` (CINF), dll. |
| `UserTablesMD`, `UserFieldsMD` | Definisi User-Defined Table & User-Defined Field. |
| `QueryManager` | Menjalankan query tersimpan (Query Manager). |

## Alur koneksi (Company)

```csharp
using SAPbobsCOM;

Company oCompany = new Company();
oCompany.Server = "server_name";
oCompany.CompanyDB = "SBO_DB";
oCompany.UserName = "manager";
oCompany.Password = "****";
oCompany.DbServerType = BoDataServerTypes.dst_MSSQL2019; // atau dst_HANADB
oCompany.UseTrusted = true;
int ret = oCompany.Connect();
if (ret == 0) {
    // sukses
} else {
    string msg = "", code = "";
    oCompany.GetLastError(out code, out msg);
    Console.WriteLine("Error {0}: {1}", code, msg);
}
```

Perhatikan: parameter koneksi server/db tergantung platform — tambahkan `dst_MSSQL2019`/`dst_HANADB`. Jangan pernah hardcode password asli; gunakan config/environment variable.

## Membuat & memanipulasi objek bisnis

```csharp
// Baca Business Partner berdasarkan kode
BusinessPartners oBP = (BusinessPartners)oCompany.GetBusinessObject(BoObjectTypes.oBusinessPartners);
int ret = oBP.GetByKey("1000000");
if (ret == 0) {
    Console.WriteLine(oBP.CardName);
}

// Buat Item baru
Items oItem = (Items)oCompany.GetBusinessObject(BoObjectTypes.oItems);
// tambahkan properti... lalu simpan
int res = oItem.Add();
```

## Dokumen (Documents) & tabel sumbernya

Objek `Documents` mewakili banyak tipe dokumen, dipilih via enum `BoObjectTypes`:

| Enum | Dokumen | Tabel header |
|------|---------|--------------|
| `oInvoices` (13) | A/R Invoice | `OINV` |
| `oCreditNotes` (14) | A/R Credit Memo | `ORIN` |
| `oDeliveryNotes` (15) | Delivery | `ODLN` |
| `oReturns` (16) | Returns | `ORDN` |
| `oOrders` (17) | Sales Order | `ORDR` |
| `oPurchaseInvoices` (18) | A/P Invoice | `OPCH` |
| `oPurchaseCreditNotes` (19) | A/P Credit Memo | `ORPC` |
| `oPurchaseDeliveryNotes` (20) | Goods Receipt PO | `OPDN` |
| `oPurchaseReturns` (21) | A/P Return | `ORPD` |
| `oPurchaseOrders` (22) | Purchase Order | `OPOR` |
| `oQuotations` (23) | Quotation | `OQUT` |
| `oInventoryGenEntry` (59) | Inventory Gen Entry | `OIGN` |
| `oInventoryGenExit` (60) | Inventory Gen Exit | `OIGE` |
| `oStockTransfer` (67) | Inventory Transfer | `OWTR` |
| `oInventoryTransferRequest` (1250000001) | Transfer Request | `OWTQ` |

> Lengkap: `python C:/Users/yudah/.sap-b1-skills/search_sap.py di documents` dan baca halaman `SAPbobsCOM~Documents.html` di corpus untuk daftar lengkap pemetaan tabel.

### Contoh membuat dokumen (C#)

```csharp
Documents oDoc = (Documents)oCompany.GetBusinessObject(BoObjectTypes.oSalesOrders);
oDoc.CardCode = "C001";
oDoc.DocDate = DateTime.Today;
oDoc.Lines.ItemCode = "A001";
oDoc.Lines.Quantity = 10;
oDoc.Lines.Price = 100;
oDoc.Lines.Add();
// header properties setelah Lines, atau set sebelum Add
int res = oDoc.Add();
```

Aturan penting: set properti **header** dulu, lalu properti **baris** (`Lines`), tapi untuk kolom yang bergantung antar baris urutkan dengan benar. Setelah `Add()`, `DocEntry` terisi.

### Membaca kembali & Update

```csharp
int ret = oDoc.GetByKey(docEntry);
// ubah properti...
oDoc.Update();
// hapus
oDoc.Remove();
```

## Recordset (query SQL langsung)

```csharp
Recordset oRS = (Recordset)oCompany.GetBusinessObject(BoObjectTypes.oRecordset);
oRS.DoQuery("SELECT CardCode, CardName FROM OCRD WHERE CardType='C'");
while (!oRS.EoF) {
    Console.WriteLine(oRS.Fields.Item("CardCode").Value + " - " + oRS.Fields.Item("CardName").Value);
    oRS.MoveNext();
}
```

`Recordset` juga dipakai untuk **query dinamis dan user tables**. Method utama: `DoQuery`, `Fields`, `MoveFirst/MoveNext`, `EoF/BoF`, `GetAsXML`.

## Foreach user-defined table

```csharp
// Tabel user U_TESTTABLE
oRS.DoQuery("SELECT * FROM U_TESTTABLE");
while (!oRS.EoF) { ... oRS.MoveNext(); }
```

Untuk tabel yang dibuat lewat `UserTablesMD`, nama di SQL adalah `U_<Name>`.

## CompanyService & SBObob

```csharp
CompanyService oService = oCompany.GetCompanyService();
AdminInfo oAdmin = oService.GetAdminInfo();      // OADM
CompanyInfo oInfo = oService.GetCompanyInfo();   // CINF

SBObob oBob = (SBObob)oCompany.GetBusinessObject(BoObjectTypes.oBObob);
Recordset oRS2 = oBob.GetBusinessPartnerBalance("C001", DateTime.Today);
```

## Enumerasi penting (BoObjectTypes inti)

| Enum | Nilai | Objek |
|------|-------|-------|
| `oChartOfAccounts` | 1 | Chart of Accounts |
| `oBusinessPartners` | 2 | Business Partners |
| `oItems` | 4 | Items |
| `oInvoices` | 13 | Documents (sales invoice) |
| `oDeliveryNotes` | 15 | Documents (delivery) |
| `oPurchaseInvoices` | 18 | Documents (purchase invoice) |
| `oPurchaseOrders` | 22 | Documents (purchase order) |
| `oQuotations` | 23 | Documents (quotation) |
| `oInventoryTransferRequest` | 1250000001 | StockTransfer request |

## Untuk .NET / VB6 tips

- Reference COM `SAP Business One DI API` (`SAPbobsCOM.dll`).
- Selalu cek nilai return method: `0` = sukses, selain itu ambil `GetLastError(out code, out msg)`.
- Setelah `Add()` jangan panggil `Update()` tanpa di-load ulang — gunakan `GetByKey` dulu bila perlu mengubah.
- Gunakan `using (oCompany) { ... }` atau pastikan release COM object untuk hindari leak.
- Untuk integrasi massal, lakukan di dalam transaksi (`oCompany.StartTransaction()` / `oCompany.EndTransaction(BoTxToCommit.tot_Commit)`) lalu `oCompany.CommitTransaction()`.

## Menelusuri objek apa pun

```bash
python C:/Users/yudah/.sap-b1-skills/search_sap.py di <objek>
# contoh: di "reserve invoices", di "buyer", di "packages"
python C:/Users/yudah/.sap-b1-skills/search_sap.py di <objek>
```

Baca halaman lengkap objek di `C:/Users/yudah/.sap-b1-help/REFDI/SAPbobsCOM~<Objek>.html` untuk properti/method detail.

## Pitfalls

- `oBusinessPartners`, `oItems`, dll. disebutkan dengan awalan `o` kecil — konsisten dengan enum.
- Banyak objek DI punya properti `UserFields` (untuk UDF) dan metode `GetByKey`/`Add`/`Update`/`Remove`.
- Objek `Documents` header vs `Lines`: pastikan `oDoc.Lines.Add()` dipanggil sehabis men-set baris terakhir.
- Jangan buat `Company` berulang-ulang; buat sekali lalu reuse.
- **UDF: `UserFieldsMD.Name` = alias, TANPA prefix `U_`.** SAP menambah `U_`
  sendiri; menulis `Name = "U_SOL_X"` menghasilkan kolom/field SL dobel
  (`U_U_SOL_X`) → Service Layer balas `Property U_SOL_... is invalid`. Nama UDF
  cukup `SOL_X` (deskripsi jangan diberi prefix template seperti `IBT:`).
  **Sebaliknya saat query/merujuk `U_` tetap wajib** (nama kolom fisik & field
  SL): `T0."U_SOL_X"`, `$[OPOR.U_SOL_X]`, array `FindColumns` UDO, `itemId` FMS,
  payload Service Layer. Kurang `U_` → `Invalid column name`.
- **`LinkedTable` hanya untuk UDT.** Diisi tabel sistem (mis. `"OITM"`) pada UDF
  di tabel user-defined → `UserFieldsMD.Add()` gagal `This related table doesn't
  exist` dan blok setup setelahnya tidak jalan.
- **UDF wajib dibuat lewat DI (`UserFieldsMD.Add`) atau Service Layer (`POST /UserFieldsMD`) — JANGAN `INSERT` ke `CUFD` lewat SQL.** Baris `CUFD` hasil SQL tidak pernah dimuat Service Layer: field muncul di SAP client tetapi setiap payload dibalas `Property 'U_SOL_x' of 'Item' is invalid`. Kalau `CUFD` sudah terisi lewat SQL, paksa refresh metadata **per tabel** (lihat skill `sap-b1-sl-api`, pitfalls) — tidak perlu restart SAP.
- Batas panjang nyata: `CUFD.AliasID` 100 char, `CUFD.Descr` 160 char (bukan 8/18).
- Saat membandingkan nilai field, gunakan properti enum, bukan hardcode numerik yang bisa berubah antar versi (kecuali untuk nilai yang kita tahu stabil, mis. di atas).

---

## Sub-Module: sap-b1-sl-api

# SAP B1 — Service Layer API (REST / OData)

Sumber: `Service Layer API Reference.html` (SAP B1 10.0) — diambil dari server
lokal `https://nyankyo:50000/Service%20Layer%20API%20Reference.html`, diekstrak
menjadi corpus yang bisa dicari.

Service Layer = **API REST berbasis OData v2/v4** untuk SAP Business One.
Posisinya di stack SDK: DI API = in-process (.NET add-on), Service Layer =
HTTP/REST (integrasi eksternal, Python/Node/Java, apa pun yang bisa kirim HTTP).

## Alur kerja (WAJIB)

1. **Cek service/entity dulu sebelum menulis request** — jangan menebak nama endpoint:

```bash
python C:/Users/yudah/.sap-b1-skills/search_sap.py sl <service|entity>   # info + endpoint
python C:/Users/yudah/.sap-b1-skills/search_sap.py sleps <service>       # daftar endpoint lengkap
```

Contoh:
```bash
python C:/Users/yudah/.sap-b1-skills/search_sap.py sl items        # -> Items (GET/POST/PATCH/DELETE)
python C:/Users/yudah/.sap-b1-skills/search_sap.py sl login        # -> contoh auth Login
python C:/Users/yudah/.sap-b1-skills/search_sap.py sleps Orders    # -> endpoint Orders + Close/Cancel/Reopen
```

2. Bila butuh detail field/struktur JSON, buka file corpus langsung:
   `C:/Users/yudah/.sap-b1-help/REFSL/<ServiceName>.txt` (berisi contoh request JSON).
3. Bila butuh mapping ke tabel database → gunakan `sap-b1-db` (`search_sap.py db`).
   Bila butuh objek DI API padanan → gunakan `sap-b1-di-api` (`search_sap.py di`).

## Dasar Service Layer

### Base URL & auth

```
Base URL  : https://<server>:50000/b1s/v2/
Login     : POST https://<server>:50000/b1s/v2/Login
```

Login (langkah pertama WAJIB — tanpa login semua request gagal):
```json
POST https://localhost:50000/b1s/v2/Login
{
  "CompanyDB": "SBODEMOUS",
  "UserName":  "manager",
  "Password":  "1234"
}
```
- Response berisi **session ID** + dua cookie: `B1SESSION` dan `ROUTEID`.
- Request berikutnya **wajib** menyertakan cookie/header `B1SESSION`.
  `ROUTEID` opsional (session stickiness / load balancing).
- `Language` opsional di body login (default `ln_English` = 3; lihat enum
  `BoSuppLangs` / DI API `BoLanguages`).

Contoh header request berikutnya:
```
Content-Type: application/json
B1SESSION: <session-id-dari-login>
Cookie: B1SESSION=<session-id>
```

### CRUD standar (entity collection)

Pola endpoint untuk semua entity (Items, Orders, Invoices, BusinessPartners, ...):

| Operasi | Method & URL | Keterangan |
|---------|-------------|------------|
| Baca satu | `GET /b1s/v2/Orders(123)` | by primary key |
| Baca list | `GET /b1s/v2/Orders` | + query options |
| Buat | `POST /b1s/v2/Orders` | body = JSON object |
| Update | `PATCH /b1s/v2/Orders(123)` | body = field yang diubah saja |
| Hapus | `DELETE /b1s/v2/Orders(123)` | |
| Aksi dokumen | `POST /b1s/v2/Orders(123)/Close` | Close/Cancel/Reopen/... |

### Service actions/functions (bukan CRUD)

Service yang diakhiri `Service` diekspos sebagai endpoint action:
```
POST https://localhost:50000/b1s/v2/<ServiceName>_<ActionName>
```
Contoh: `ActivitiesService_GetActivityList`, `AccountsService_CreateOpenBalance`,
`BusinessPartnersService_CreateOpenBalance`, `ApprovalRequestsService_GetApprovalRequestList`.
Cek daftarnya: `search_sap.py sleps <ServiceName>`.

### Query options OData

| Option | Contoh | Fungsi |
|--------|--------|--------|
| `$select` | `$select=CardCode,CardName` | pilih kolom saja |
| `$filter` | `$filter=CardType eq 'C'` | filter (eq, ne, gt, ge, lt, le, and, or, not, startswith, substringof, contains) |
| `$orderby` | `$orderby=CardCode desc` | urutan |
| `$top` / `$skip` | `$top=10&$skip=20` | pagination |
| `$expand` | `$expand=BusinessPartnerGroups` | ikutkan navigasi/lines |
| `$count` | `$count=true` | hitung total |
| `$search` | `$search=apple` | full-text search |

Contoh:
```
GET https://localhost:50000/b1s/v2/Orders?$select=DocEntry,DocNum,CardCode&$filter=DocStatus eq 'O'&$orderby=DocNum desc&$top=50
```

### Batch request

Beberapa operasi dalam satu HTTP request: `POST /b1s/v2/$batch` dengan
`Content-Type: multipart/mixed` (format OData batch).

## Mapping: Service Layer ↔ DB ↔ DI API

Service Layer entity → tabel DB → objek DI API (kunci integrasi antar skill):

| Entity SL | Tabel DB | Objek DI API |
|-----------|----------|--------------|
| `BusinessPartners` | `OCRD` (+`CRD1`) | `BusinessPartners` |
| `Items` | `OITM` (+`ITM1`, `OITW`) | `Items` |
| `Orders` | `ORDR`/`RDR1` | `Documents` (oDocumentType=17) |
| `Invoices` | `OINV`/`INV1` | `Documents` (oDocumentType=13) |
| `PurchaseOrders` | `OPOR`/`POR1` | `Documents` (oDocumentType=22) |
| `PurchaseInvoices` | `OPCH`/`PCH1` | `Documents` (oDocumentType=18) |
| `JournalEntries` | `OJDT`/`JDT1` | `JournalEntries` |
| `Drafts` | `ODRF`/`DRF1` | `Drafts` |
| `Warehouses` | `OWHS` | `Warehouses` |
| `ChartOfAccounts` | `OACT` | `ChartOfAccounts` |
| `Users` | `OUSR` | `Users` |
| `UserTablesMD` | `U_...` (user tables) | `UserTablesMD` |
| `Attachments2` | `OATC`/`ATC1` | `Attachments` |

> Cek mapping lain via `search_sap.py sl <entity>` lalu `search_sap.py db <tabel>`.

## Pitfalls

- **Wajib login dulu** — semua request tanpa `B1SESSION` dianggap bad request.
- **Case-sensitive**: nama entity persis seperti di reference (`BusinessPartners`, bukan `businesspartners`).
- **PATCH hanya kirim field yang berubah** — mengirim object penuh bisa memicu validasi berlebih / konflik.
- **Tanggal format ISO**: `"2016-08-30"` (date), `"2016-08-30T12:00:00"` (datetime).
- **Pagination default** dibatasi (biasanya 20 baris per halaman) — selalu pakai `$top`/`$skip` untuk data besar.
- **Dokumen punya status**: `Close`/`Cancel`/`Reopen` adalah action POST, bukan PATCH status.
- **Header opsional yang sering dibutuhkan**: `Prefer: return=representation` (minta object hasil), `B1S-CaseInsensitive: true` (filter case-insensitive), `B1S-Metadata: minimal` (kecilkan payload).
- **Entity ItemGroups**: key-nya `Number` (`ItmsGrpCod`), BUKAN `Code` → `POST /ItemGroups` dengan `Code` gagal `Property 'Code' of 'ItemGroups' is invalid`.
- **Nomor item group di-generate SAP** (running number). Jadi **jangan kirim `Number`** saat POST — nilainya diabaikan dan nomor di SAP tidak akan sama dengan body. Kirim `{GroupName}` saja, lalu **tarik balik** nomornya: `GET /ItemGroups?$select=Number,GroupName` (bisa `$filter=GroupName eq '...'` bila hanya butuh satu). Pola ini berlaku umum: entity ber-`Number` (item group, profit center, dll) tidak pernah punya nomor yang bisa ditebak sisi klien.
- **UDF ADA di `CUFD` tapi SL bilang invalid**: `Property 'U_SOL_xxx' of 'Item' is invalid` padahal baris `CUFD` ada → UDF dibuat **via SQL langsung** (INSERT ke `CUFD`), bukan via DI API/SL, sehingga SL tidak memuat metadata-nya. UDF buatan `POST /UserFieldsMD` langsung dikenali. **Jangan bikin UDF via SQL.** Kalau `CUFD` sudah terisi via SQL: paksa refresh **per tabel** tanpa restart SAP — (1) `POST UserFieldsMD {Name:'ZZREFRESH',Type:'db_Alpha',Size:8,Description:'temp',TableName:'OITM'}` lalu (2) `DELETE UserFieldsMD(FieldID=<dari balikan>,TableName='<nama tabel FISIK dari balikan, mis. AITM>')`. Refresh per tabel, bukan global (setelah `OITM` di-refresh, `OCRD` masih invalid sampai di-refresh sendiri).
- **Validasi nama UDF jangan pakai `$select`/`$filter`**: SL **mengabaikan diam-diam** properti tidak dikenal di `$select`/`$filter` (balas 200 seolah ada) → tidak bisa dipakai mendeteksi field hilang. Satu-satunya bukti: `PATCH`/`POST` nyata dengan nilai yang valid/unik; balasan `Property 'X' of 'Y' is invalid` = field tidak ada, sedangkan balasan soal tipe/nilai/bisnis (`'' is not a valid value…`, `Specify an active branch…`) = field ADA.
- **DELETE `UserFieldsMD` butuh kunci `FieldID` + `TableName` FISIK** (`UserFieldsMD(FieldID=15,TableName='AITM')`); kunci `Name` gagal `invalid entity key 'Name'`. Nama fisik = prefix `A` (`OITM`→`AITM`, `@SOL_PNUM_D`→`@ASOL_PNUM_D`), ambil saja dari balikan `POST /UserFieldsMD`.
- Jangan sertakan kredensial asli dalam output; gunakan placeholder.

## Referensi & rebuild corpus

- Corpus SL: `C:/Users/yudah/.sap-b1-help/REFSL/` (499 file service).
- Index: `C:/Users/yudah/.sap-b1-skills/refsl_index.json`.
- Rebuild dari HTML sumber:
  ```bash
  python C:/Users/yudah/.sap-b1-skills/build_sl_corpus.py "<Service Layer API Reference.html>"
  ```
- Referensi ringkas gabungan seluruh paket ada di umbrella `sap-b1/references/otak-skills.md`
  dan `C:/Users/yudah/OneDrive/Desktop/SAP_B1_Otak_Skills.md` (sudah termasuk modul Service Layer).

---

## Sub-Module: sap-hana-cli

# SAP HANA Developer CLI (hana-cli)

## SAP B1 Context: HANA vs SQL Server

SAP Business One (B1) support dua database backend. hana-cli relevan untuk HANA backend B1:

| Aspect | HANA (hana-cli target) | SQL Server (NOT hana-cli) |
|--------|------------------------|---------------------------|
| DB engine | SAP HANA (in-memory, column-store) | MS SQL Server (disk-based, row-store) |
| B1 DI API port | 30015 (single) / 39015 (multi-tenant) | 30000 (license server) / 1433 (DB) |
| B1 Service Layer | :50000 / :50001 (identical API) | :50000 / :50001 (identical API) |
| SQL dialect | HANA SQL (`LIMIT`, `\|\|`, `CURRENT_DATE`, `SUBSTRING`) | T-SQL (`TOP`, `+`, `GETDATE()`, `LEFT()`/`RIGHT()`) |
| B1 Cloud | HANA Cloud → Service Layer ONLY | N/A (on-prem only) |
| DI API bitness | 64-bit only | 64-bit + 86-bit |
| Metadata tables | `CUFD`, `OUTB`, `OUDO` (same names, HANA schema) | `CUFD`, `OUTB`, `OUDO` (same names, DB schema) |
| UDT/UDF/UDO | Identical DI API code | Identical DI API code |

> **hana-cli tidak bisa connect ke B1 SQL Server backend.** hana-cli = HANA only. Untuk SQL Server, gunakan SQL Server tools (`sqlcmd`, SSMS, mssql-cli).
> **B1 HANA Cloud**: DI API & UI API tidak bisa connect. Service Layer (REST/OData) satu-satunya integration method. hana-cli bisa connect ke HANA Cloud via service key (`connectViaServiceKey`).
> **B1 10.0 HANA DI API path**: `C:\Program Files\SAP\SAP Business One DI API\DI API 100\` (64-bit, NOT Program Files (x86)).

### hana-cli for B1 HANA — Common Use Cases

```bash
# Connect to B1 HANA database
hana-cli connect -n "hanahost:30015" -u SYSTEM -p PASSWORD --save

# Inspect B1 metadata tables (same names in HANA & SQL)
hana-cli inspectTable -s SAPB1 -t CUFD -o cds    # UDF metadata
hana-cli inspectTable -s SAPB1 -t OUTB -o cds    # UDT metadata
hana-cli inspectTable -s SAPB1 -t OUDO -o cds    # UDO metadata

# Query B1 user tables (prefixed with @ in B1)
hana-cli querySimple -q "SELECT * FROM \"SAPB1\".\"@MY_UDT\" LIMIT 10" -o json

# List all B1 tables in HANA schema
hana-cli tables -s SAPB1

# Convert B1 HANA table to CDS for CAP/CDS development
hana-cli inspectTable -s SAPB1 -t ORDR -o cds
```

### B1 HANA SQL Differences (vs T-SQL)

| Operation | HANA SQL | T-SQL (SQL Server) |
|-----------|----------|---------------------|
| Limit rows | `SELECT * FROM T LIMIT 10` | `SELECT TOP 10 * FROM T` |
| String concat | `'a' \|\| 'b'` | `'a' + 'b'` |
| Current date | `CURRENT_DATE` | `GETDATE()` |
| Substring | `SUBSTRING(s, 1, 3)` | `LEFT(s, 3)` or `SUBSTRING(s, 1, 3)` |
| No LEFT/RIGHT | Use `SUBSTRING()` | `LEFT()` / `RIGHT()` |
| Cross apply | Not supported | `CROSS APPLY` / `OUTER APPLY` |
| Schema | `"SCHEMA"."TABLE"` (quoted) | `DB.SCHEMA.TABLE` |

## Related Skills

- **sap-b1-addon-dev**: SAP B1 add-on development (DI API, UI API, Service Layer, UDO, C#) — includes HANA vs SQL Server connection details
- **sap-b1-concepts**: SAP B1 functional concepts — includes database platform comparison (HANA vs SQL Server)
- **sap-b1-web-integration**: SAP B1 web integration with Service Layer — includes HANA vs SQL Server Service Layer comparison
- **sap-cap-capire**: Use for CAP database development, HDI container management, and CDS syntax comparison
- **sap-btp-cloud-platform**: Use for HANA Cloud operations, BTP integration, and cloud instance management
- **sap-abap-cds**: Use for comparing CDS syntax between CAP and ABAP or understanding HANA CDS features
- **sap-datasphere**: Use when working with SAP Datasphere integration or data warehousing scenarios
- **sap-dependency-security**: Use for secure dependency upgrades, exact MCP server pins, npm package hardening, lockfile linting, and cooldown policy when projects include hana-cli dependencies

A developer-centric command-line interface for SAP HANA database development, particularly useful in non-SAP tooling environments like VS Code.

**Repository**: [https://github.com/SAP-samples/hana-developer-cli-tool-example](https://github.com/SAP-samples/hana-developer-cli-tool-example)
**npm Package**: [https://www.npmjs.com/package/hana-cli](https://www.npmjs.com/package/hana-cli)
**Current Version**: 3.202405.1 (April 2024)
**Node.js Requirement**: ≥20.19.0

---

## Table of Contents
- [Quick Start](#quick-start)
- [Core Command Categories](#core-command-categories)
- [Output Formats](#output-formats)
- [Connection Configuration](#connection-configuration)
- [Common Workflows](#common-workflows)
- [Bundled Resources](#bundled-resources)

## Quick Start

### Installation

```bash
# Install globally via npm (recommended)
npm install -g hana-cli

# Verify installation
hana-cli version
```

### First Connection

```bash
# Interactive connection setup
hana-cli connect

# Or specify connection directly
hana-cli connect -n "hostname:port" -u DBUSER -p PASSWORD --save

# Using service key (HANA Cloud)
hana-cli connectViaServiceKey
```

---

## MCP Integration (AI-Driven Database Operations)

### Overview
The hana-mcp-server integration enables natural language database operations through Claude's Model Context Protocol. Use conversational queries alongside traditional CLI commands for a complete development workflow.

### Setup

The bundled MCP config pins `hana-mcp-server@0.3.1`. Use **sap-dependency-security** before changing this pin because the server receives HANA tenant connection environment variables.

#### 1. Environment Variables
Required configuration (add to ~/.zshrc, ~/.bashrc, or project .env):
```bash
export HANA_HOST="your-hana-host.hanacloud.ondemand.com"
export HANA_PORT="443"
export HANA_USER="DBADMIN"
export HANA_PASSWORD="your-password"
export HANA_ENCRYPT="true"  # Optional, defaults to true
export HANA_DATABASE=""     # Optional, for MDC tenant
export HANA_CONNECTION_TYPE="single-container"  # Optional
```

#### 2. Connection Types
- **single-container** (default): Standard HANA databases
- **mdc-system**: Multi-tenant system database
- **mdc-tenant**: Specific tenant in multi-tenant environment

### When to Use: CLI vs MCP

| Scenario | Recommended Tool | Why |
|----------|------------------|-----|
| Exploratory queries, ad-hoc analysis | **MCP** | Natural language, no syntax needed |
| Automation scripts, CI/CD pipelines | **CLI** | Scriptable, consistent output |
| Learning database structure | **MCP** | Conversational discovery |
| Generating CDS/EDMX/OpenAPI output | **CLI** | Supports 17+ formats |
| Complex multi-step workflows | **CLI** | Fine-grained control |
| Quick data sampling and inspection | **MCP** | Faster for one-off queries |

### Example Natural Language Queries

#### Schema & Table Discovery
- "Show me all schemas in this HANA database"
- "List all tables in the SYSTEM schema"
- "What tables exist in the MY_APP schema?"
- "Show me all views in the PUBLIC schema"

#### Table Structure & Metadata
- "Describe the structure of the USERS table"
- "What columns does the ORDERS table have?"
- "Show me the data types for MY_TABLE"
- "What is the primary key of the CUSTOMERS table?"

#### Data Sampling & Inspection
- "Sample 5 rows from the PRODUCTS table"
- "Show me the first 10 records from SALES_DATA"
- "Get sample data from ORDER_ITEMS table"
- "Display a few rows from MY_TABLE"

#### Query Execution
- "How many rows are in the CUSTOMERS table?"
- "Show me distinct values in the STATUS column of ORDERS"
- "What is the maximum value in the PRICE column of PRODUCTS?"
- "Find all records in USERS where country is 'USA'"

#### System Performance & Monitoring
- "Check the HANA database status"
- "Show me system performance metrics"
- "What is the current database version?"

### MCP Tools Available
The hana-mcp-server provides these MCP tools:
- `list_schemas`: Enumerate all schemas
- `list_tables`: Show tables in a schema
- `describe_table`: Get table structure and metadata
- `query`: Execute SQL queries from natural language
- `sample_data`: Retrieve sample rows
- `system_info`: Database status and performance

### Example: MCP + CLI Workflow
```bash
# 1. Use MCP to explore (natural language)
"Show me all tables in the PRODUCTS schema"

# 2. Use MCP to understand structure
"Describe the PRODUCTS.INVENTORY table"

# 3. Use CLI for format conversion (precise output)
hana-cli inspectTable -t INVENTORY -s PRODUCTS -o cds

# 4. Use CLI for HDI operations
hana-cli createContainer -c MY_CONTAINER
```

---

## Core Command Categories

### Database Object Inspection

| Command | Aliases | Purpose |
|---------|---------|---------|
| `inspectTable` | `it`, `table` | Inspect table structure |
| `inspectView` | - | Inspect view definition |
| `inspectProcedure` | - | Inspect stored procedure |
| `inspectFunction` | - | Inspect function definition |
| `tables` | - | List all tables in schema |
| `views` | - | List all views in schema |
| `procedures` | - | List stored procedures |
| `functions` | - | List functions |

### Query Execution

| Command | Aliases | Purpose |
|---------|---------|---------|
| `querySimple` | `qs` | Execute SQL query |
| `callProcedure` | `cp` | Execute stored procedure |
| `hdbsql` | - | Direct SQL execution |

### HDI Container Management

| Command | Aliases | Purpose |
|---------|---------|---------|
| `containers` | `cont` | List HDI containers |
| `createContainer` | - | Create new container |
| `dropContainer` | - | Remove container |
| `activateHDI` | - | Enable HDI service |
| `adminHDI` | - | Administer HDI privileges |

### Cloud & BTP Operations

| Command | Aliases | Purpose |
|---------|---------|---------|
| `hanaCloudInstances` | - | List HANA Cloud instances |
| `hanaCloudStart` | - | Start cloud instance |
| `hanaCloudStop` | - | Stop cloud instance |
| `btp` | - | Configure BTP CLI |
| `btpInfo` | - | Display BTP target info |

---

## Output Formats

The `--output` / `-o` option supports 17+ formats:

| Format | Use Case |
|--------|----------|
| `tbl` | Human-readable table (default) |
| `json` | JSON data |
| `yaml` | YAML format |
| `csv` | CSV export |
| `excel` | Excel file |
| `cds` | CAP CDS definitions |
| `hdbcds` | HANA CDS format |
| `hdbtable` | HDB Table definitions |
| `sql` | SQL DDL statements |
| `edmx` | OData EDMX metadata |
| `openapi` | OpenAPI/Swagger spec |
| `graphql` | GraphQL schema |

---

## Connection Configuration

Connection credentials are searched in priority order:

1. `default-env-admin.json` (with `--admin` flag)
2. `.cdsrc-private.json` (via `cds bind`)
3. `.env` file with VCAP_SERVICES
4. File specified via `--conn` parameter
5. `default-env.json` in current/parent directories
6. `~/.hana-cli/default.json`

For connection templates, see `templates/default-env.json`.

---

## Common Workflows

### Inspect and Convert Table to CDS

```bash
# Inspect table structure
hana-cli inspectTable -s MYSCHEMA -t MYTABLE

# Convert to CDS format
hana-cli inspectTable -s MYSCHEMA -t MYTABLE -o cds
```

### Mass Convert Schema Objects

```bash
# Convert all objects in schema to CDS
hana-cli massConvert -s MYSCHEMA
```

### Execute Query with Export

```bash
# Run query and export to JSON
hana-cli querySimple -q "SELECT * FROM MYTABLE" -o json

# Export to Excel file
hana-cli querySimple -q "SELECT * FROM MYTABLE" -o excel -f ./output -n report
```

### Manage HDI Containers

```bash
# List all containers
hana-cli containers

# Create new container
hana-cli createContainer -c MY_CONTAINER -g MY_GROUP

# Create container users
hana-cli createContainerUsers -c MY_CONTAINER
```

---

## UI Commands

Many commands have browser-based UI alternatives (suffix `UI`):

- `tablesUI` - Browse tables visually
- `containersUI` - Manage containers in browser
- `massConvertUI` - Visual mass conversion
- `querySimpleUI` - Query builder interface
- `systemInfoUI` - System dashboard

---

## Key Features

- **Multi-database support**: HANA, PostgreSQL, SQLite backends
- **Format conversion**: 17+ output formats including CDS, EDMX, OpenAPI
- **HDI management**: Full container lifecycle management
- **Cloud integration**: SAP BTP CLI and HANA Cloud support
- **Interactive prompts**: Missing parameters prompted automatically
- **Service key auth**: Secure cloud authentication

---

## Detailed References

For comprehensive documentation:

- **All 91 Commands**: See `references/command-reference.md`
- **Connection & Security**: See `references/connection-security.md`
- **HDI Management**: See `references/hdi-management.md`
- **Output Formats**: See `references/output-formats.md`
- **Cloud Operations**: See `references/cloud-operations.md`
- **Database Inspection**: See `references/db-inspection.md`
- **Mass Operations**: See `references/mass-operations.md`
- **System Administration**: See `references/system-admin.md`
- **Web UI Interface**: See `references/web-ui.md`
- **Troubleshooting Guide**: See `references/troubleshooting.md`
- **Development Environment**: See `references/development-environment.md`
- **ABAP Programming Patterns**: See `references/abap-programming.md`

---

## Troubleshooting

### Connection Issues

```bash
# Check current connection status
hana-cli status

# Test with explicit credentials
hana-cli connect -n "host:443" -u USER -p PASS --encrypt true

# Use SSL trust store
hana-cli connect --trustStore /path/to/certificate.pem
```

### Permission Errors

```bash
# Diagnose privilege errors
hana-cli privilegeError

# View current user info
hana-cli inspectUser
```

### Version Compatibility

- **Node.js**: Requires ≥20.19.0
- **@sap/cds**: Uses 9.4.4
- **@sap/cds-dk**: Requires ≥8.9 for cds bind

---

## Bundled Resources

### Reference Documentation
- `references/command-reference.md` - Complete command reference with all options
- `references/abap-programming.md` - ABAP-specific programming patterns
- `references/development-environment.md` - Development setup and environment guidance
- `references/connection-security.md` - Secure connection and credential handling
- `references/troubleshooting.md` - Common errors and recovery steps

### Templates
- `templates/default-env.json` - Local connection template for CAP-style bindings
- `templates/cdsrc-private.json` - CAP private configuration template

## Resources

- **GitHub**: [https://github.com/SAP-samples/hana-developer-cli-tool-example](https://github.com/SAP-samples/hana-developer-cli-tool-example)
- **Intro Video**: [https://youtu.be/dvVQfi9Qgog](https://youtu.be/dvVQfi9Qgog)
- **Cloud Shells Demo**: [https://youtu.be/L7QyVLvAIIQ](https://youtu.be/L7QyVLvAIIQ)
- **SAP HANA Cloud**: [https://help.sap.com/docs/hana-cloud](https://help.sap.com/docs/hana-cloud)
- **SAP CAP**: [https://cap.cloud.sap/docs/](https://cap.cloud.sap/docs/)

---

*Last Updated: 2025-11-26 | Version: 1.1.0*

---

## Sub-Module: sap-b1-customization-objects

# SAP B1 — Objek Kustomisasi (UDT / UDF / UDO / FMS)

Dipakai saat menulis/memperbaiki script setup kustomisasi (`UserTablesMD`, `UserFieldsMD`, `UserObjectsMD`,
`FormattedSearches`, `Menus`) atau saat aplikasi eksternal mengeluh UDF-nya "tidak ada".

## Urutan pembuatan (satu arah, tidak bisa dibolak-balik)

1. UDT — `UserTablesMD`, `TableName = "@SOL_X"` → tabel SQL `@SOL_X`.
2. UDF di UDT — `UserFieldsMD.TableName = "@SOL_X"`, object type `oUserFields`.
3. UDF di tabel sistem — `OITM`, `OPOR`, `OPRQ`, `OPQT`, `POR1`, `PRQ1`, … (nama tabel header ≠ nama tabel baris).
4. UDO — `UserObjectsMD`; baru bisa setelah tabel/UDT yang dipakainya ada.
5. FMS + menu — `oFormattedSearches`, `oMenus`; terakhir, karena menunjuk UDF/UDO yang sudah jadi.

## Aturan yang mahal kalau dilanggar

- **Simpan nama UDF tanpa prefix `U_`.** `CUFD.AliasID` = nama polos; SAP menambah `U_` pada nama kolom DB, dan
  Service Layer menerima key `U_<AliasID>`. Menulis `Name = "U_SOL_X"` → alias `U_SOL_X`, kolom `U_U_SOL_X`, dan
  aplikasi yang mengirim `U_SOL_X` ditolak `Property 'U_SOL_X' is invalid` walaupun UDF "kelihatan sudah dibuat".
- **Batas panjang sebenarnya: `CUFD.AliasID` 100 karakter, `CUFD.Descr` 160 karakter.** Angka 8/18 karakter
yang beredar di forum/UI tidak berlaku di DB — alias 20+ karakter terbukti tersimpan. Tetap tulis nama sependek
yang tetap jelas, dan pastikan alias **sama persis** dengan key yang dikirim aplikasi.
- **Deskripsi UDF polos, tanpa prefix template domain** (`"Nomor dokumen web"`, bukan `"IBT: Nomor dokumen web"`).
Konteks domain sudah terbaca dari nama UDT/UDO-nya; prefix berulang mengotori daftar field di UI SAP.
- **Waspadai UDF dobel** — `U_SOL_X` hidup berdampingan dengan `SOL_X` di tabel yang sama, akibat run lama yang
masih memakai prefix `U_`. Dua-duanya tampak valid, tapi aplikasi hanya cocok dengan yang tanpa `U_`. Cek duplikat
sebelum menuduh kode aplikasi (query + cara bersihkan ada di `references/verifikasi-dan-diagnosa.md`).
- **Jangan isi `LinkedTable` dengan tabel sistem.** `UserFieldsMD.LinkedTable` mengisi `CUFD.RTable` dan hanya
  menerima user table/UDT; diisi `"OITM"` → `Add()` gagal `This related table doesn't exist`. Biarkan kosong;
  validasi referensi item/BP di kode aplikasi atau lewat FMS.
- **Pakai helper yang sudah ada di solution** (`Utils.CreateUDT`, `Utils.CreateUDF`, `Utils.CreateUDO`,
  `Utils.CreateFMS` — mis. `AddOn/Bank Integration/Utils.cs`): sudah cek-exist dulu sehingga idempotent.
  Jangan bikin wrapper `UserFieldsMD` sendiri — penamaan & urutan field jadi beda dari solution lain.
- **Setup bersifat fail-fast.** Satu `Add()` yang gagal menghentikan seluruh blok berikutnya (UDO/FMS/menu tidak
  pernah jadi), tapi gejalanya cuma baris status — jangan simpulkan sukses dari ketiadaan popup error; cek DB.
- **Kalau file `.cs` itu sudah dijalankan user dan gagal di satu baris: perbaiki baris itu saja.** Rename/refactor
  blok lain membuat user menjalankan versi lama sementara DB berubah (field dobel/salah nama sulit ditarik).

## Verifikasi (wajib setelah tiap run)

Baca metadata langsung dari DB `<CompanyDB>` via `sqlcmd -S <server> -E` (Windows auth) — `CUFD` = UDF,
`OUTB` = UDT, `OUDO` = UDO. Query lengkap, peta gejala → sebab, dan cara mencocokkan dengan payload aplikasi ada di
`references/verifikasi-dan-diagnosa.md`.

## Pitfalls

- `oCompany.GetBusinessObject(BoObjectTypes.oUserFields)` untuk UDF, `oUserTablesMD` untuk UDT — jangan tertukar.
- Field UDF terpisah per tabel: field header dokumen (`OPOR`) tidak otomatis ada di baris (`POR1`) — cek `TableID`
  di `CUFD` sebelum menyimpulkan payload ditolak karena data.
- UDO yang gagal daftar sering tidak melempar error ke pemanggil: verifikasi tabel `OUDO`, bukan hanya status bar.

---

## Sub-Module: sap-b1-config-automation

# SAP B1 Config Automation (Setup Toolkit)

## When to Use
- Automate database/config setup saat implementasi SAP B1: UDF/UDT/UDO massal dari template Excel.
- Scope lanjutan: G/L Account Determination, document numbering/series, master data import, approval template.
- Idempotent batch config yang bisa dijalankan ulang (skip existing).

## Why this class exists
Config DB saat implementasi = repetitif + rawan human-error → ideal di-automasi. Value bukan di "bikin field" tapi di **import + validasi** (duplicate check, referensi master data). Kebanyakan partner masih klik manual → toolkit = differentiation + billing reusable per project.

## Core pattern: Excel template → typed definitions → idempotent DI API create

### 1. Dual-mode exe (hemat testing drastis)
```csharp
bool standalone = args.Length == 0;
company = standalone ? ConnectStandalone() : ConnectViaB1(args[0]);

// UI add-on mode: SAP B1 client launch add-on dgn args[0] = connection string
private static Company ConnectViaB1(string connString)
{
    var oGui = new SAPbouiCOM.SboGuiApi();
    oGui.Connect(connString);
    return (Company)oGui.GetApplication().Company.GetDICompany();
}

// Standalone mode: test tanpa register di client B1 (config.json)
// Company.Connect() dgn Server/CompanyDB/User/Pass/DbServerType
```
- `DbServerType`: parse int dari config.json ke enum `BoDataServerTypes`. **SQL = `0`, HANA = `3`** (bukan 1/2 — comment kode yang bilang `1=MSSQL,2=HANA` itu bohong/salah). Verifikasi: `dst_MSSQL=0, dst_HANADB=3`.
- Standalone = buka exe langsung, test template+logic, baru register add-on kalau udah mateng.

### 2. WinForms-in-B1 > native UI API form (untuk form config)
- Native UI API form (FormType + FormXMLData + item events) = stabil tapi verbose, XML gede, versi-sensitive.
- **Plain WinForms dialog** yang di-`Application.Run` di dalam process add-on = jendela terpisah di client B1. Stabil lintas versi, cukup layout code, tanpa Form Design Tool / .srf.
- `ponytail:` native UI API form → tambah kalo butuh integrasi cockpit (matrix item events, CFL).
- Flow form: browse `.xlsx` → Load (preview grid + count) → Confirm → Run → summary log OK/SKIP/FAIL + kode error.

### 3. Baca template Excel pakai NPOI
- NPOI free, gak butuh Excel terpasang: `IWorkbook wb = new XSSFWorkbook(fs)`; cek sheet by name.
- Header UDF: `Table | FieldName | Description | Type | Size | Mandatory` — Type `A/N/D/T/B/M` (Alphanumeric/Numeric/Date/Time/Boolean/Memo).
- Header UDT: `TableName | Description | Type | CreateForm` — Type `R`(regular)/`D`(document), CreateForm `Y` = sekalian UDO + default form + menu.
- Baris blank (Table kosong) di-skip + warning.
- **Generate template Excel dev-side pakai openpyxl (Python)** — gaya/border/kolom jauh lebih gampang daripada NPOI. Copy hasil `.xlsx` ke folder `Templates\`.

### 4. Idempotent create via tabel metadata (safe no-op)
```sql
-- UDF exists — USE THIS (version-agnostic, works 9.x AND 10.0):
-- UDF is just column U_<Name> on base table. No metadata table dependency.
SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_NAME='{table}' AND COLUMN_NAME='U_{fieldName}'
-- UDF exists — 9.x LEGACY ONLY: UDF2 table. B1 10.0 SQL has NO UDF2
-- (throws 'Invalid object name dbo.UDF2'). 10.0 metadata tables: XRUDF/OUTB/OUDO.
-- UDF2.AliasID stores field name WITHOUT U_ prefix!
SELECT COUNT(*) FROM UDF2 WHERE TableID='{table}' AND AliasID='{nameTanpaU_}'
-- UDT exists (oUserTablesMD; OUTB.TableName tanpa prefix U_):
SELECT COUNT(*) FROM OUTB WHERE TableName='{nameTanpaU_}'
-- UDO exists (oUserObjectsMD; UDO.Code = nama tabel U_...):
SELECT COUNT(*) FROM OUDO WHERE Code='{table}'
```
- UDO setup: `CanCreateDefaultForm=tYES`, `MenuItem=tYES`, `MenuItemFatherUID="43520"`.
- `Marshal.ReleaseComObject` wajib tiap `BoObjectTypes` object — bocor COM bikin add-on lambat.

### 5. Multi-sheet Excel reader (support both template styles)
- Legacy template: single sheet `"UDF"` (all UDF rows in one sheet).
- IBT-style template: two sheets `"UDF_Header"` + `"UDF_Line"` (header-level vs line-level UDFs).
- Reader must try `"UDF"` first; if absent, fall back to `"UDF_Header"` + `"UDF_Line"`.
- `"UDF_Line"` is optional — not all templates have line-level UDFs.
- Both sheet formats use same column layout: `Table | FieldName | Description | Type | Size | Mandatory`.

### 6. Per-item try/catch + log display (prevent silent abort)
- Wrap each `AddUdf()`/`AddUdt()` call in try/catch inside `RunAll()`. DI API property setters can throw COM exceptions (not just return error codes). Without per-item catch, one bad field aborts the entire batch — remaining UDFs never get created.
- Expose `GetLogDump()` method on ConfigService → MainForm calls it after RunAll. Without this, user only sees "OK: X FAILED: Y" with zero detail on which field failed and why.
- Wrap `RunConfig()` in MainForm with top-level try/catch → show `_svc.GetLogDump()` even on fatal exception.

## Login & troubleshooting standalone DI

- **Login failed for user 'X' (SQL) ≠ -132.** If standalone exe dies instantly with a MessageBox "Login failed <code>: <msg>", the code IS reaching the DB — it's a SQL auth problem, NOT missing SDK/COM. Root cause found in the field: `UserName` in config.json must be a **SQL Server login**, and the B1 demo user `manager` typically has **no SQL login at all** (B1 client connects through its own server-tools mechanism). Test first:
  ```powershell
  sqlcmd -S localhost -U manager -P 'P@ssw0rd' -d SBOTEST -Q "SELECT 1"
  # Login failed for user 'manager' → switch config to sa (or create a SQL login)
  sqlcmd -S localhost -E -Q "SELECT name, is_disabled FROM sys.server_principals WHERE name='sa'"
  ```
  Don't assume `manager` works just because it's the B1 superuser in OUSR. `sa` with the same password is the common fix on dev boxes.
- **Standalone smoke test (no B1 client needed):** launch exe, check MainWindowTitle, kill:
  ```powershell
  $p = Start-Process -FilePath 'C:\...\ConfigToolkit.exe' -WorkingDirectory 'C:\...'
  Start-Sleep -Seconds 8
  Get-Process -Name ConfigToolkit | Select MainWindowTitle
  Stop-Process -Name ConfigToolkit -Force
  ```
  Window title visible = COM connect + login succeeded. No window = startup throw (see MessageBox cases below).
- Error **-132 "Error during SBO user authentication"** = password **user SAP B1** (OUSR) salah — BUKAN SQL login, BUKAN DbServerType, BUKAN server address. DI standalone pakai user/password SAP internal (hash di OUSR), beda dari credential SQL. Fix: reset password user di client B1 (atau via DI UserObject kalau udah konek). Jangan brute common password — login gagal -132 akan muncul berulang dan bisa lock user (FailedLog).
  **Verify independently via Service Layer (proven 2026-09):** a DI API -132 can be cross-checked WITHOUT touching the add-on — POST the same credentials to `http://<host>:50001/b1s/v2/Login` `{"CompanyDB":..., "UserName":..., "Password":...}`. `HTTP 400` + body `{"error":{"code":"206","message":"Invalid login credential"}}` = the SAP user password is definitively wrong (not the code, not the connection). HTTP 401 = wrong session/auth mechanism; HTTP 000 = SL down. If `manager`/`P@ssw0rd` fails on BOTH DI and SL, the password is wrong, period — don't keep "fixing" the code. NB: WSL curl to the host's SL port often gives 000 (WSL2 NAT) — probe from the Windows side with `Invoke-RestMethod` in powershell.exe instead; SL listener check: `Get-NetTCPConnection -State Listen -LocalPort 50001`. Also remember: the **same credentials live in the web app's `.env`** (`SAP_B1_USERNAME`/`SAP_B1_PASSWORD`) — a bad SAP password breaks the Laravel/React → Service Layer integration too, not just the standalone exe. Fix the password once, update config.json + .env together.
- Cek user valid dari WSL: SQL Windows-auth ke company DB, `SELECT USER_CODE, SuperUser, Locked FROM OUSR WHERE USER_CODE='manager'` — kolom status itu `Locked`, **bukan** `ACTIVE` (OUSR gak punya kolom ACTIVE; `ACTIVE` = kolom di tabel lain, query error "Invalid column name" kalau dipakai).
- Server untuk SQL client: `Server=localhost` (default instance, port 1433). Jangan `localhost:30015` (itu HANA port). Set up yang awalnya dijual/diingat sebagai HANA → cek dulu DB type beneran (port listen: 1433=SQL vs 30015/39015=HANA) sebelum debug panjang.
- **Jangan tulis config.json dari PowerShell `ConvertTo-Json`** — output-nya BOM + spasi aneh, dan `DataContractJsonSerializer` (ConfigJson.Load) gagal deserialize dengan "Encountered unexpected character" → exe crash startup dengan pesan membingungkan. Tulis config dari WSL pakai `json.dump` Python (no BOM) atau manual. Kalau exe tiba-tiba crash deserialize, cek dulu config.json yang ke-tulis tool test.
- MessageBox class `#32770` berjudul "Startup error: ..." = exe launch tapi connect gagal (modal error), BUKAN form utama. Detail cara enum window + baca teks dialog dari WSL: skill `wsl-windows-admin`.

## Pitfall arsitektur
- **DI API & UI add-on tidak bisa ke HANA Cloud** — cuma on-prem SQL/HANA. Target cloud → rancang sejak awal ke Service Layer (REST), jangan bangun DI API dulu.
- SQL = row-based, murah, familiar. HANA = in-memory column, cepat analitik, cloud jadi standar (harus Service Layer).
- Tabel metadata bisa dikit beda antar versi B1 (9.x vs 10.0) — verifikasi `UDF2`/`OUTB`/`OUDO` di versi target.

## HANA vs SQL Server — DI API Connection Differences

| Property | HANA | SQL Server |
|----------|------|------------|
| `DbServerType` | `dst_HANADB` (enum value 3) | `dst_MSSQL` (enum value 0) |
| Server port | 30015 (single-tenant) / 39015 (multi-tenant) | 30000 (B1 license server) |
| DB direct port | 30015 / 39015 | 1433 (SQL Server, not used by DI API) |
| License server | `host:30000` | `host:30000` |
| DI API bitness | 64-bit only | 64-bit + 86-bit |
| SQL syntax (Recordset) | HANA SQL: `LIMIT`, `\|\|`, `CURRENT_DATE`, `SUBSTRING` | T-SQL: `TOP`, `+`, `GETDATE()`, `LEFT()`/`RIGHT()` |
| Cloud support | HANA Cloud → Service Layer ONLY | N/A |

### HANA-specific pitfalls
- **HANA DI API = 64-bit only.** UI add-on (B1 client) = 86-bit. Dual-build x64+x86.
- **HANA port 30015 ≠ 30000.** 30000 = license server. 30015 = HANA DB. Salah port = connection refused.
- **HANA multi-tenant** → port 39015, bukan 30015. Cek konfigurasi SLD.
- **HANA Cloud** → DI API & UI API TIDAK bisa. Service Layer (REST) satu-satunya cara.
- **HANA SQL di Recordset.DoQuery**: `SELECT * FROM ORDR LIMIT 10` (bukan `TOP 10`). String concat `||` (bukan `+`). Date `CURRENT_DATE` (bukan `GETDATE()`).
- **HANA metadata tables**: `CUFD`, `OUTB`, `OUDO` — nama sama, tapi di HANA schema namespace. Query tetap sama nama tabel.
- **config.json `DbServerType`**: parse int. SQL=0, HANA=3. Bukan 1/2.

## Scaffold project
```
ConfigToolkit/
├── ConfigToolkit.sln                # .NET Framework 4.8
├── build.bat                        # msbuild x64+x86 dual + stage deploy\ConfigToolkit-{x64,x86}/
├── Templates/                       # UDF_Template.xlsx, UDT_Template.xlsx (openpyxl)
└── ConfigToolkit/
    ├── Program.cs                   # dual-mode dispatch
    ├── ConfigToolkit.csproj         # SAPbobsCOM/SAPbouiCOM COMReference (EmbedInteropTypes) + NPOI PackageReference 2.5.6
    ├── addon_manifest.xml
    ├── config.json                  # standalone login
    ├── Core/    ConfigJson.cs ConfigLog.cs
    ├── Models/  UdfDefinition.cs UdtDefinition.cs
    ├── Services/ConfigService.cs ExcelTemplateReader.cs
    ├── Forms/   MainForm.cs
    └── Utils/   Ui.cs
```
- COM refs pakai `<COMReference>` TypeLib GUID (B1 10.0: SAPbobsCOM `{FC8030BE-F5D2-4B8E-8F92-44228FE30100}`, SAPbouiCOM `{6048236A-956D-498D-A6F1-9C81C13AB6E8}`, `EmbedInteropTypes=True`) — di-resolve MSBuild dari 64-bit TypeLib reg; runtime bitness harus match reg.
- NPOI via `<PackageReference Include="NPOI" Version="2.5.6" />`; deploy butuh 4 NPOI dll + `BouncyCastle.Crypto.dll` + `ICSharpCode.SharpZipLib.dll`.
- Build: VS MSBuild `/t:Rebuild /restore` — **wajib `/restore`** (tanpa itu `CS0246: NPOI not found`), **prefer VS 2019 MSBuild** (VS 2022 restore bisa poison `obj\project.assets.json` di csproj lama ber-COMReference → gagal CS0246 terus). build.bat: `for /d` loop discover MSBuild (cmd gak expand wildcard tengah path), `EnableDelayedExpansion` + `!OUT!` buat staging deploy. Detail lengkap: skill `wsl-windows-admin` section "cmd.exe batch + MSBuild pitfalls".
- Compile cuma bisa di Visual Studio Windows (butuh SDK + MSBuild); WSL gak ada csc/mono — jangan klaim "udah compile".
- **`.sln` platform MUST match csproj PlatformTarget (proven 2026-09 on ConfigToolkit).** A csproj that only defines `x64`/`x86` configs (mandatory for COM-reference add-ons — bitness must match the skill's scaffolding) + a `.sln` that maps `Debug|Any CPU` → VS F5 fails with **"Unable to start debugging"** because the build config can't resolve. Fix: replace `Any CPU` with `x64` in BOTH `GlobalSection(SolutionConfigurationPlatforms)` AND `GlobalSection(ProjectConfigurationPlatforms)` (the per-project `.Debug|Any CPU.ActiveCfg` / `.Build.0` lines). Verify with `MSBuild.exe ConfigToolkit.sln -t:Build -p:Configuration=Debug -p:Platform=x64` before claiming fixed. Write the `.sln` via write_file with tabs — a `patch`-mode edit of a `.sln` mangles the indentation.
- **Source fix ≠ binary fix.** Editing `ConfigService.cs`/reader refactors the SOURCE but leaves the compiled exe stale until MSBuild re-runs. Before telling the user "fixed", compare `stat -c '%y'` of the source vs the deployed exe — if exe mtime predates source, the running binary still has the old bugs. Reported as "fix ada di source, binary belum" — separah itu. Rebuild in VS Windows is the only way to make the fix live; WSL can't compile .NET Framework + SAP COM refs.

## Related
- `sap-b1-addon-dev` (user-owned): API pola UDF/UDT/UDO (`references/udo-udt-udf.md`), project structure & registration (`references/addon-structure.md`).

## ⚠️ "Still can't run" → root cause is often a MISSING COM SDK, not the code (proven 2026-09)
When the exe, after all source fixes, still fails to launch (or dies at `new Company()` with `0x80040154 / Class not registered`, or a MessageBox `#32770` "Startup error"), stop debugging the C# — check whether the DI/UI API **COM SDK** is even installed. SAP ships two different SDKs:
- **DI API + UI API (COM)** → installs `SAPbobsCOM.dll` / `SAPbouiCOM.dll`: what `new Company()` and any UI API need.
- **Service Layer SDK (`.NET` REST wrapper)** → installs ONLY `SAPBusinessOneSDK.dll` (a Service-Layer client, NOT COM). Does NOT provide `Company`/`SAPbobsCOM`/`SAPbouiCOM`, does NOT register the COM CLSIDs. A COM add-on exe cannot use it.

Check which you actually have (WSL):
```bash
find "/mnt/c/Program Files (x86)/SAP" -iname "SAPbobsCOM.dll" -o -iname "SAPbouiCOM.dll"
```
Only `SAPBusinessOneSDK.dll` present ⇒ **COM SDK not installed** — no amount of code fix helps; the binary cannot run here. Fix = install the full DI/UI API SDK component, OR re-architect to Service Layer (`sap-b1-web-integration`), which needs only `SAPBusinessOneSDK.dll`/plain REST and is the only path for HANA Cloud anyway. (COM CLSID reg check: HKCR\CLSID for the csproj GUIDs above.)

> **BEFORE blaming the SDK (2026-09 follow-up):** a full server install lives at `C:\Program Files (x86)\SAP\SAP Business One Server\B1_SHR\Client.x64\` with the client at `C:\Program Files\SAP\SAP Business One\SAP Business One.exe` — SDK paths are NOT the same as 9.x. Order of checks when exe dies instantly: (1) `sqlcmd` login test with the config creds (SQL auth fail = most common), (2) `sqlcmd -E` to list sys.databases (CompanyDB typo), (3) only then suspect COM/typelib. The exe in this project ran fine once the SQL login was fixed — SDK was never the problem.

---

## Sub-Module: sap-b1-addon-dev

# SAP Business One Add-On Development

## ⚠️ VERSION GOTCHA (B1 10.0 vs 9.x) — READ FIRST
Enum/property names CHANGED in B1 10.0 DI API. If code written for 9.x won't compile (CS0117/CS1061), use these 10.0 names:
- `BoObjectTypes.oUserFields` (not `oUserDefinedFields`), `oUserTables` (not `oUserTablesMD`), `oUserObjectsMD` (same)
- `BoFieldTypes.db_Alpha/db_Numeric/db_Date/db_Memo/db_Float` (no Time/Boolean enum → map T→Date, B→Alpha)
- `BoUTBTableType.bott_NoObject/bott_Document/bott_MasterData` (not `utbOther/utbDocument`)
- `BoUDOObjType.boud_MasterData/boud_Document` (not `ou_BusinessObject`)
- `UserObjectsMD` menu props: `MenuCaption` (string), `FatherMenuID` (Int32 — numeric, NOT string), `MenuItem` (no `MenuItemString/MenuItemType/MenuItemFatherUID`, no `BoMenuType`)
- `Recordset.EoF` (capital F, not `Eof`)
Verify live metadata: PowerShell reflection on `obj\Debug\Interop.SAPbobsCOM.dll`
(or `C:\Program Files\SAP\SAP Business One DI API\DI API 100\`).
SAP B1 10.0 SDK path: `C:\Program Files\SAP\SAP Business One DI API\DI API 100\` (NOT Program Files (x86)).


## When to Use
- Building B1 add-ons in C#/VB.NET
- Connecting to B1 via DI API or Service Layer
- Creating User Defined Objects/Tables/Fields
- Customizing forms with UI API
- Handling B1 events
- Registering/deploying add-ons

## References
- `references/di-api.md` — DI API connection, CRUD, query
- `references/ui-api.md` — UI API forms, events, menus
- `references/service-layer.md` — REST/OData API, Laravel integration
- `references/udo-udt-udf.md` — Custom objects/tables/fields
- `references/addon-structure.md` — Project layout, deployment

## HANA vs SQL Server — Quick Reference

| Aspect | HANA on-prem | SQL Server on-prem | HANA Cloud |
|--------|-------------|---------------------|------------|
| DI API | Yes (64-bit only) | Yes (64-bit + 86-bit) | NO |
| UI API | Yes (x86 client) | Yes (x86 client) | NO |
| Service Layer | Yes (:50000/:50001) | Yes (:50000/:50001) | Yes (only option) |
| DB port | 30015 (single) / 39015 (multi) | 30000 (license) / 1433 (DB) | N/A |
| `DbServerType` | `dst_HANADB` (3) | `dst_MSSQL` (0) | N/A |
| SQL dialect | HANA SQL (`LIMIT`, `\|\|`, `CURRENT_DATE`) | T-SQL (`TOP`, `+`, `GETDATE()`) | N/A |
| UDT/UDF/UDO | Identical code | Identical code | Service Layer only |
| Add-on type | Client add-on + web | Client add-on + web | Web only |

> **HANA Cloud = Service Layer ONLY.** DI API & UI API tidak bisa connect ke cloud. Rancang dari awal ke Service Layer.
> **HANA DI API = 64-bit only.** UI add-on = x86 (B1 client 32-bit). Dual-build kalau butuh standalone + add-on.
> **Build wajib MSBuild VS** (COM interop). `dotnet build` fail. Set `Copy Local=False`, `Embed Interop Types=False`.

## Quick Start

### DI API Connection — HANA
```csharp
using SAPbobsCOM;
Company oCompany = new Company();
oCompany.Server = "hanahost:30015";              // HANA DB port (30015 single, 39015 multi-tenant)
oCompany.CompanyDB = "SBODEMOUS";
oCompany.UserName = "manager";
oCompany.Password = "manager";
oCompany.DbServerType = BoDataServerTypes.dst_HANADB;  // enum value 3
oCompany.LicenseServer = "hanahost:30000";     // license server (SLD)
int ret = oCompany.Connect(); // 0 = success
```

### DI API Connection — SQL Server
```csharp
using SAPbobsCOM;
Company oCompany = new Company();
oCompany.Server = "sqlhost:30000";              // B1 license server port (NOT 1433)
oCompany.CompanyDB = "SBODEMOUS";
oCompany.UserName = "manager";
oCompany.Password = "manager";
oCompany.DbServerType = BoDataServerTypes.dst_MSSQL;  // enum value 0 (dst_MSSQL2019 also valid)
oCompany.LicenseServer = "sqlhost:30000";
int ret = oCompany.Connect();
```

### UI API Connection (same for HANA & SQL)
```csharp
using SAPbouiCOM;
SboGuiApi oGui = new SboGuiApi();
oGui.Connect(args[0].ToString());
Application oApp = oGui.GetApplication();
Company oCompany = (Company)oApp.Company.GetDICompany(); // uses whatever DB B1 client is connected to
```

### Service Layer Login (same for HANA & SQL)
```csharp
POST https://server:50000/b1s/v1/Login
Body: {"CompanyDB":"SBODEMOUS","UserName":"manager","Password":"manager"}
Response: Set-Cookie: B1SESSION=<session_id>
```

> Service Layer API identik untuk HANA maupun SQL Server. Beda cuma performance (HANA faster).

---

## Sub-Module: sap-b1-addon-integration

# SAP B1 Add-On Integration & Debugging

Companion to `sap-b1-addon-dev` (user-owned, covers DI/UI API basics). This skill captures
integration/debugging lessons learned hands-on with the ConfigToolkit project and the Soltius
reference template. Load when: add-on "can't run" in the client, UDF/UDT/UDO creation from Excel,
DI API login errors, or web→SAP Service Layer credential problems.

## Debug from Visual Studio → Attach to Process
The only reliable way to debug a UI add-on. "Start" (F5) will never work because the exe needs
the client's connection string arg.

1. Build **Debug** config (Release has no PDB → breakpoints won't bind).
2. Stage exe + PDB + `.b1s` + dependencies into a dedicated `deploy\<Name>-debug\` folder.
3. Register the Debug exe in Add-On Administration (remove the old entry first), Type = **UI Add-On**, Status = Active.
4. Close SAP fully → reopen → login company (the add-on auto-launches).
5. VS → Debug → **Attach to Process** (Ctrl+Alt+P) → find `<AddOn>.exe` (tick "Show processes from all users").
6. Breakpoints hit on menu-click event handlers.

Attach to the add-on process, NOT the SAP client process. If the add-on process isn't listed, it
didn't launch → re-check registration + `.b1s`.

## Project Context (ConfigToolkit)
Path: `C:\Users\muham\Desktop\SAPB1_ConfigToolkit` (WSL: `/mnt/c/Users/muham/Desktop/SAPB1_ConfigToolkit`)
- C# WinForms add-on: batch UDF/UDT/UDO from Excel template via DI API
- Standalone mode (no args, config.json) + UI add-on mode (inside B1 client)
- Solution platform: `x64` ONLY (SAP B1 COM refs require bitness-specific; no Any CPU → sln must
  map Debug/Release → x64, else VS F5 "unable to start debugging")
- Templates: `Templates/IBT_UDF_Mapping_Template.xlsx` (sheets UDF_Header/UDF_Line for IBT web sync)

## Quick Rules
- UI add-on inside client MUST use keep-alive pattern (Application.Run() no form; menu event opens dialog)
- UDF existence check: `CUFD` table (canonical), NOT INFORMATION_SCHEMA
- `UserFieldsMD.Name` = WITHOUT `U_` prefix (SAP auto-prepends)
- DI API login fails with `-132` = SAP user/password wrong, NOT SQL auth — SQL `sa` never valid B1 login
- Verify creds against Service Layer `/b1s/v2/Login` to isolate: HTTP 400 code 206 = bad password
- `.b1s` file = VSI registration marker; `addon_manifest.xml` `B1VERSION` must match client (10.0)

## References
- `references/soltius-addon-pattern.md` — keep-alive UI add-on pattern, menu, events, .b1s, manifest
- `references/udf-metadata.md` — CUFD vs UDF2 vs XRUDF vs INFORMATION_SCHEMA, U_ prefix rules
- `references/credentials-debug.md` — DI -132 vs Service Layer invalid credential, SAP vs SQL auth

---

## Sub-Module: sap-b1-addon-runtime

# SAP B1 — Add-on Runtime & Koneksi

Menjalankan dan men-debug add-on SAP B1 dari Visual Studio: bitness, connection string, attach UI API
vs DI API, dan setup deploy. Untuk referensi objek API (form, event, dokumen, UDT/UDF) pakai
`sap-b1-ui-addon` / `sap-b1-di-api`. Skill ini soal **kenapa add-on tidak nyambung / tidak jalan**.

## Urutan diagnosa (jangan lompat ke kode dulu)

1. **Bandingkan bitness client vs add-on.** Client SAP B1 10.0 (FP 2311+) 64-bit, dan COM library-nya
   (`SAPbouiCOM`, `SAPbobsCOM`) hanya jalan di host process 64-bit. Set `PlatformTarget = x64`.
   Pastikan dengan membaca PE header — jangan menebak dari nama folder (`C:\Program Files\SAP\...`
   vs `... (x86)`; instalasi SAP menaruh komponen 32-bit dan 64-bit berdampingan).
2. **Cek registrasi COM TypeLib** memakai GUID dari `<COMReference>` di `.csproj`. Kalau UI API hanya
   punya subkey `win64`, add-on 32-bit mustahil connect. DI API biasanya punya `win32` + `win64`.
3. **Cek company/server yang sedang login di client** dari
   `%LOCALAPPDATA%\SAP\SAP Business One\-REGISTRY-*-LogIN-*.binary` (base64 → UTF-16LE).
4. **Decode connection string** add-on (hex → UTF-16LE) dari `<StartArguments>`.
5. Perbaiki, rebuild, ulangi.

Probe siap jalan: `references/connection-troubleshooting.md`.

## Aturan yang menentukan

- **x64 wajib.** Gejala salah bitness menyamar jadi error koneksi: `SboGuiApi.Connect()` gagal dengan
  "Could not find SBO that match the connection string" walau client sudah terbuka dan sudah login ke
  company yang benar. Cek bitness dulu sebelum berburu masalah connection string.
- **Jangan turunkan platform target ke `x86` "supaya jalan"** — pada client 10.0 itu justru penyebabnya.
- **Connection string bukan penanda company.** `0030002C0030002C00530041005000420044005F00440061007400650076002C0050004C006F006D0056004900490056`
  decode jadi `0,0,SAPBD_Datev,PLomVIIV` — template dev generik SAP ("attach ke client mana pun yang
  sedang jalan"). Nama company di dalamnya tidak berarti string itu terikat ke company tersebut.
- **Runtime add-on menerima connection string dari SAP B1, bukan dari kode:**
  `Environment.GetCommandLineArgs().GetValue(1)`. Untuk debug dari VS, isi `<Project>.csproj.user` →
  `<StartArguments>` (Project Properties → Debug → Command Line Arguments). Menjalankan dari VS tanpa
  argumen → `Connect("")` gagal. Daftarkan lewat Add-On Manager kalau ingin SAP B1 yang menyuplai string.
- **Kalau tujuannya cuma men-deploy kustomisasi** (UDT/UDF/UDO/menu/FMS), lepas ketergantungan UI API:
  pakai koneksi DI API mandiri (`Company.Server` / `CompanyDB` / `UserName` / `Password` /
  `DbServerType` + `Connect()`), dan guard setiap `oSBOApplication.StatusBar...` dengan
  `if (oSBOApplication != null)`. Hasilnya bisa dijalankan dari VS tanpa membuka client.
- **Append blok deploy ke proyek add-on yang sudah ada: sisakan method deploy-nya saja.** Jangan
  ikut-sertakan `public static class Utils` atau helper sejenis — nested class men-shadow `Utils` milik
  host project, dan semua panggilan `Utils.*` jadi error "no definition / no overload".
- **Setelah menyunting file `.cs` hasil salin-tempel, verifikasi keseimbangan `{`/`}` per-method.**
  Penyisipan kurung otomatis bisa mendarat di posisi salah (mis. sebelum penutup `catch`, bukan
  sesudahnya) walau jumlah totalnya seimbang — cek juga urutan penutup `if` / `catch` / method.

## Verifikasi sebelum bilang "beres"

- Add-on benar-benar run dan connect pada platform target yang dipilih.
- Saat mengklaim perbaikan bitness/koneksi, sebutkan buktinya (hasil cek PE header / registrasi COM /
  company yang login) — bukan hanya "harusnya jalan".

---

## Sub-Module: sap-b1-addons

# SAP B1 Add-Ons (SOLTIUS Scheduler + Web API)

User's SAP B1 project at /mnt/d/Scheduller. Two .NET 8 add-ons:
- "SOLTIUS - Scheduler Add-On" — WinForms UI add-on; saves profiles (AllConfigurations.xml, active in DefaultConfig.xml), POSTs active profile XML to Web API.
- "SOLTIUS - Web API Add-On" — ASP.NET Core (Kestrel, default port 5006); receives profile XML, saves Configuration/Config.xml, provisions staging DB tables.

## Sync flow

1. Scheduler `ProfileSyncService.SyncActiveProfile` → POST XML to `{WebApiUrl}/api/ProfileSync` (Content-Type application/xml).
2. Web API `ProfileSyncController` → `ConfigurationService.ConfigureAsync(xml)`:
   - SaveConfigAsync: overwrite Configuration/Config.xml (ContentRootPath/Configuration/Config.xml — project root when run via dotnet run)
   - GetDatabaseConfig: parse ExternalDatabase (DBType, Server, Port, DatabaseName, User, Pass)
   - Factory picks initializer (MySQL or SQL Server) → OpenAsync → CREATE TABLE IF NOT EXISTS sales_order_header + sales_order_detail (Dapper).
3. Success → 200. Any exception → controller catch → **500 "Database staging tidak dapat diakses: {ex.Message}"** (was 502 before 2026-08 fix; 502 semantics were wrong).

## Config.xml shape (payload built by `BuildExternalDatabaseXml`)

- XML root `<Configuration>`; since 2026-08 carries `<Environment>` child (from `AppConfig.Environment`: Production/Development/Testing set by radio buttons in FormCreate/ManageProfile) before `<ExternalDatabase>`. Empty/legacy profile → `Unknown`. Web API stores raw XML, so tag lands verbatim in Config.xml; `GetDatabaseConfig` ignores unknown elements — adding tags is safe, no API-side change needed.
- `<ExternalDatabase>` holds ExternalDBType/Server/Port/Name/User/Pass. `AppConfig.Environment` already existed in the model but was NOT serialized into the sync payload until 2026-08 — if a tag seems missing, check the builder, not the model.

## Key facts / pitfalls

- **502 from /api/ProfileSync does NOT mean Web API is down.** Was the controller's own catch for staging DB failure; since 2026-08 fix it returns **500** (correct semantics) with body `{"message":"Database staging tidak dapat diakses: {ex.Message}"}`. Server is alive (scheduler would get connection-refused/timeout otherwise).
- **Config invalid → 400 INVALID_CONFIG** (since 2026-08): `ConfigurationService.GetDatabaseConfig` throws `ApiConfigInvalidException` (missing/invalid ExternalDatabase) → `GlobalExceptionMiddleware` maps to 400. `ApiNotConfiguredException` (no Config.xml) → 503 NOT_CONFIGURED. `StatusService` caches DB-probe result for 10s TTL — after editing Config.xml, wait ~12s before re-probing /api/Status or you read stale cache.
- **Scheduler error text now includes API body** (since 2026-08): `TryPostProfileSync` reads response body → error shows `HTTP 500 ... Detail: {"message":...}`, not just the status phrase.
- **Scheduler hides the real error.** `TryPostProfileSync` shows only `HTTP {code} {phrase}` ("HTTP 502 Bad Gateway"). The API response body has the actual exception message. To see it: curl the endpoint manually, or patch scheduler to read response body.
- **Port 40000 on user machine = SAP Business One Tomcat** (`C:\Program Files\SAP\SAP Business One SetupFiles\tomcat\bin\tomcat10.exe`), NOT MySQL. Profile pointing MySQL → MUMARI:40000 fails every time.
- **No MySQL exists on this machine** (no service, no mysqld, no Docker). Only SQL Server: MSSQLSERVER running on port 1433. MySQL profile values are wrong unless a remote MySQL is intended.
- **"sa" user is SQL Server convention.** MySQL default is root. Seeing user "sa" with DBType MySQL is a red flag.
- **Initializers never CREATE DATABASE** — only tables (IF NOT EXISTS). The target DB must already exist or connection fails (login failed / cannot open database).
- **Verified working profile (2026-08)**: SQLServer → MUMARI:1433, DB `SBODemoAU123` (exists on MSSQLSERVER), user `sa` / password `P@ssw0rd`. The sa password is **P@ssw0rd (zero)** — `P@ssword` fails login (user misremembers it as P@ssword; verify with sqlcmd before trusting).
- **Kestrel port pitfall**: launchSettings.json profile "http" binds 5006 ONLY under `dotnet run`/VS. Running the exe directly binds the Kestrel default **5000** → scheduler POST to 5006 gets connection-refused. Fix: `"Urls": "http://localhost:5006"` in appsettings.json (already applied to source + bin/Debug copy). When the API is up but unreachable, check the listening port, not just the process.
- Failed sends queue to `PendingProfileSync.xml` (scheduler bin/Debug) and auto-retry on next sync. Since 2026-08: **dedup** (identical WebApiUrl+XML not enqueued twice) + **7-day expiry** (items older than 7 days dropped in `FlushPendingSyncs`). Old wrong-config payloads keep failing until profile fixed — queue self-cleans once a send succeeds or expires. To reset manually, write an empty `<PendingProfileSyncs .../>` root (stale payloads otherwise retry for up to 7 days).
- Config.xml copies exist in multiple places: project root `/mnt/d/Scheduller/Configuration/Config.xml` (live when run from project), `SOLTIUS - Web API Add-On/bin/Debug/net8.0/Configuration/Config.xml` (build artifact, can be stale). Check ContentRootPath of the running process before trusting a copy.

## Debug sequence

1. Confirm API alive — probe from the WINDOWS side: `powershell.exe -NoProfile -Command "curl.exe -s -m 5 -o NUL -w \"%{http_code}\" http://localhost:5006/api/Status"` (WSL2 curl to a Windows listener often returns 000 even when the API is up — NAT/forwarding; 200 here = up).
2. Reproduce sync manually with curl to see real body:
   `curl -X POST -H "Content-Type: application/xml" --data-binary @payload.xml http://localhost:5006/api/ProfileSync`
3. Check DB port reachable + who owns it (see skill wsl-windows-admin, Port/process discovery).
4. Fix profile in Manage Profile (type/server/port/db/user/pass) → Update → resync. Pending queue flushes on next sync.
5. End-to-end verify (start API exe → POST payload → assert staging tables exist): run scripts/verify-profile-sync.sh.

## Sales Order path (API → staging DB)

- Endpoint: `POST /api/SalesOrder` (JSON body, `SalesOrderHeader` + `DocumentLines`). Controller → `SalesOrderService` (validates CardCode + DocumentLines) → `SalesOrderRepository.InsertSalesOrderAsync`.
- **Staging table schema is defined by the initializers (source of truth), NOT by the repository.** Columns actually created (both MySQL + SQL Server initializers): header `cardcode, cardname, docdate, docduedate, taxdate, remarks, process_status, retrycount, created_at, updated_at, processed_at, errormessage`; detail `id, header_id, linenum, itemcode, itemname, warehouse, quantity, price, process_status, ...`.
- **MySQL-only SQL in the repository breaks on SQL Server (and vice-versa).** Found bug (2026-08): repo INSERT used `status` (table has `process_status`), `itemdescription`/`warehousecode` (table has `itemname`/`warehouse`), `NOW()` (SQL Server needs `GETDATE()`), `SELECT LAST_INSERT_ID()` (SQL Server needs `SELECT CAST(SCOPE_IDENTITY() AS BIGINT)` for Dapper `ExecuteScalarAsync<long>`), and skipped NOT NULL `linenum` (must be set per line: `++lineNum` in loop). Every POST → 500. Repository now SQL Server-only with a guard: `if (config.DBType != DatabaseType.SqlServer) throw NotSupportedException(...)`.
- When reviewing repos against initializers, diff the INSERT column list against INFORMATION_SCHEMA.COLUMNS, not against memory:
  `sqlcmd -S MUMARI,1433 -U sa -P P@ssw0rd -d SBODemoAU123 -Q "SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME='sales_order_header' ORDER BY ORDINAL_POSITION" -W`

## Scheduler sync path (staging → SAP, since 2026-08)

- **`btnSync_Click` no longer posts hardcoded mock data.** It reads real pending orders via `DatabaseService.LoadPendingSalesOrders()` (header JOIN detail WHERE process_status=0, grouped by header), then `SapSyncService.ExecuteSalesOrderSync(PendingSalesOrder)` creates a multi-line SAP order, then `UpdateSalesOrderStatus(headerId, 1|2, errMsg)` flips staging rows.
- **process_status contract**: 0 = pending, 1 = success, 2 = failed. `UpdateSalesOrderStatus` sets `retrycount = CASE WHEN @Status=1 THEN 0 ELSE retrycount+1 END` (reset on success, increment on failure). Tables have NO docentry column — SAP DocEntry lives only in TBL_SYNC_HISTORY log.
- **Headless runner**: `Services/SalesOrderSyncRunner.cs` (`RunPendingSync(config, isDryRun)`) — same engine without WinForms deps; used by FormSync `manualStaging()` and CLI `-PROFILE:name` mode (`automaticSync()`). FormSync's old `manualStaging()`/`automaticSync()` were no-ops (all code commented, showed fake "Sync Finished") — now real.
- `SyncHandler.cs` was 100% dead code (every method commented) → **deleted** 2026-08. Don't resurrect it.
- Non-SDK csproj (Scheduler) has explicit `<Compile Include>` list — **new .cs files must be registered there or build fails CS0246**. (Web API csproj is SDK-style, auto-includes.)

## Build (from WSL)

- **SDK-install pitfall (2026-09):** a machine can have `C:\Program Files (x86)\SAP\SAP Business One SDK\` present but with only `Lib\SAPBusinessOneSDK.dll` (the Service Layer .NET SDK) and NO `SAPbobsCOM.dll` / `SAPbouiCOM.dll` (the DI/UI API COM components). Symptom: `new Company()` → `80040154 Class not registered` at runtime, and the COMReference won't resolve at build. Distinguishing check before blaming code: `find "C:\Program Files (x86)\SAP" -iname "SAPbobsCOM*" -o -iname "SAPbouiCOM*"` (the SDK folder may appear full elsewhere; count real .dll files under `Lib`). Missing COM DLLs → install the full DI API + UI API SDK components, or pivot the tool to Service Layer (HTTP `https://<host>:50000/b1s/v1` — needs a running SL endpoint, not COM registration). The standalone exe ALSO won't run until it's rebuilt AFTER the source fix; source fixes alone don't update `bin/` artifacts.

- **`dotnet build`/`dotnet msbuild` FAILS on this solution**: `error MSB4803: The task "ResolveComReference" is not supported on the .NET Core version of MSBuild` (Shared Library references SAPbobsCOM COM interop). Must use the .NET Framework MSBuild: `"C:\Program Files\Microsoft Visual Studio\2022\Community\MSBuild\Current\Bin\MSBuild.exe"`.
- **bin/Debug gets file-locked** when the Scheduler exe is running and/or VS 2022 has the project open (MSB3027 "file locked by ... devenv"). Build to a separate OutDir to avoid touching bin: `/p:OutDir=D:\Scheduller\build_verify\`, then run/verify from that copy. `bin/Debug/net8.0/*.dll` can stay stale — don't trust its timestamps as build proof.
- Web API csproj references the Scheduler project (which references Shared Library), so building the API builds all three.

## Verify end-to-end (ad-hoc)

- Profile sync: `scripts/verify-profile-sync.sh` (build → start API → POST /api/ProfileSync → assert staging tables).
- SalesOrder insert: `scripts/verify-sales-order.sh` (POST valid → 200; POST empty CardCode → 400; assert rows + linenum via sqlcmd; cleanup with `DELETE FROM sales_order_detail; DELETE FROM sales_order_header; DBCC CHECKIDENT(...RESEED,0)`).
- Probe API from Windows side: `powershell.exe -NoProfile -Command "curl.exe ..."` — WSL2 curl to Windows listener often returns 000 (NAT), not proof the API is down.
- Remember to kill the verify API instance afterward (`Get-Process 'SOLTIUS - Web API Add-On' | Stop-Process -Force`) — it holds port 5006.
- **Unit-test a class from the WinForms project without a test suite**: drop a console `.csproj` (`<Project Sdk="Microsoft.NET.Sdk">`, `TargetFramework net48`, `ProjectReference` to the Scheduler csproj) + `harness.cs` in a temp dir, `MSBuild /t:Restore` then `/t:Build`, run the exe via `powershell.exe -Command "& 'D:\...\harness.exe'"`. Used 2026-08 to verify `AccessPasswordStore` AES round-trip + Base64 fallback (5 checks, HARNESS_OK). Works for any class in the Scheduler assembly.
- **Simpler harness variant (2026-08)**: Scheduler targets net8.0 (not net48), so a plain `dotnet.exe run --project ...` harness works with `<ProjectReference>` to the Scheduler csproj — no MSBuild/powershell dance. Reference the built exe directly via `<Reference Include="SOLTIUS - Scheduler Add-On"><HintPath>D:\Scheduller\SOLTIUS - Scheduler Add-On\bin\Debug\SOLTIUS - Scheduler Add-On.exe</HintPath></Reference>` (exe is a valid assembly reference), `TargetFramework net8.0`, `Nullable disable`, `ImplicitUsings disable`. Verify `BuildExternalDatabaseXml` output with `XDocument.Parse` + element assertions. Run via `dotnet.exe run --project "C:\...\verify.csproj"`, exit code 0 = pass.
- **WSL path vs Windows path in powershell -Command**: pass Windows paths (`D:\\...`) inside the powershell command string, not `/mnt/d/...` — MSBuild errors MSB1001/MSB1009 on mixed/Linux paths. Also `$_` inside a double-quoted `powershell.exe -Command "..."` from bash gets eaten → use single quotes for the PS command or escape `$_`; `-RedirectStandardOutput` on Start-Process hangs the WSL powershell (skip it).
- **WSL /tmp is invisible to Windows MSBuild**: harness/verify scripts placed in `/tmp/...` cannot be built by `powershell.exe MSBuild` (Windows-side). Write the harness under `/tmp/hermes-verify-*` to follow the system pattern, COPY it to `/mnt/d/...` before building, run, then clean up. **2026-08 simplification**: create the temp dir directly under `/mnt/c/Users/<user>/AppData/Local/Temp/hermes-verify-$$` (Windows-native path, no copy step), translate to Windows path via `sed 's|/mnt/c/|C:/|; s|/|\\|g'`, run `dotnet.exe run --project` with it, then `rm -rf /mnt/c/Users/<user>/AppData/Local/Temp/hermes-verify-*`.
- **WinForms harness csproj needs `<UseWindowsForms>true</UseWindowsForms>`** (SDK-style) or `System.Windows.Forms` fails with CS0234. Keep `LangVersion 7.3` — the Scheduler project is `LangVersion 7.0`, so NO `string?` nullable annotations in harness or project code (compile error).

## Codebase pitfalls (found in review 2026-08)

- **`ISalesOrderService` had a nested duplicate interface** (outer empty, methods only on inner) — compiles but DI of the outer interface can't call methods, so the controller bypassed the service (dead code). Flatten to one interface.
- **SapSyncService NRE**: `config.SAPServerType.ToUpper()` / `config.SAPLicenseServer.Replace(...)` crash when those profile fields are empty. Guard with `(config.X ?? "")`.
- **Double profile-sync trigger**: profile change fired `ProfileSyncService.SyncActiveProfile` inside `FormChooseCF.button1_Click` AND `SendActiveConfigurationToWebAsync` in `FormMain.configurationToolStripMenuItem_Click` → two POSTs. Keep only the FormMain one (fire after dialog OK, not inside the dialog handler).
- **Scheduler `GetDatabaseService` hardcoded a SQL Server connection string** regardless of `ExternalDBType` (breaks MySQL profiles silently). Guard on ExternalDBType, append `,{port}` when set, add `TrustServerCertificate=True`. Since 2026-08 the shared builder lives in `ConfigService.BuildStagingConnectionString(config)` (returns null for non-SQLServer) — use it instead of hand-building.
- **Login/Setup password was Base64, not encrypted** (`FormPassword.cs`/`FormLogin.cs`, Security/AccessConfig.xml). Since 2026-08: `UI/AccessPasswordStore.cs` wraps shared-library AES `Encryption` class; `Decrypt()` falls back to legacy Base64, `IsLegacyFormat()` detects old entries, and `FormPassword_Load` auto-migrates old Base64 → AES on open. Verified working sa password `P@ssw0rd`; the app login password was `P@ssw0rd` too.
- **`ConfigurationController` was a duplicate of `ProfileSyncController`** (same ConfigureAsync, different error handling) → deleted 2026-08. `/api/Configuration` now 404; only `/api/ProfileSync` exists.

Full architecture + session diagnosis: references/profile-sync-architecture.md
Sales Order repository bug diagnosis + fixed SQL: references/sales-order-repository.md
2026-08 bug-fix round (502 root cause, repo SQL fix, dead-code cleanup, AES password, sync engine): references/2026-08-bugfix-round.md
Scheduler service feature (dual-mode exe, Windows Service, setting form real-time vs interval + install via sc.exe): references/scheduler-service-feature.md

---

## Sub-Module: sap-b1-business-logic-translator

# SAP B1 Business Logic to Narrative Translator

## Overview

**Core principle:** Answer *"what does the business do, in what order, and when does it stop?"* — never dump operators, class names, or DB columns into the audience's face. Code lives in the margin (footnote), the narrative lives in the body.

Audience: business analysts, finance, non-technical approvers. They must walk away able to describe the flow in plain language and predict what the system will or will not do.

## Translation Rules

1. **Verb-first prose.** Each step opens with an action a person would understand: *"System mengecek tanggal… jika kosong, proses dihentikan"* — not *"if (docDate == null) return;"*.
2. **One code branch → one numbered narrative step.** `if/else`, `switch`, early `return`, exceptions each become their own branch step with a visible condition.
3. **Preserve decision points.** Do not flatten conditions. Label them "**Cek:**" so the reader sees the gate.
4. **Terminology bridge first.** On first use, gloss the SAP/technical term: *"stok minimum (Minimum Safety Stock)"*.
5. **Keep numbers & thresholds exact.** A depreciation rate, an allocation percentage, a tolerance — keep verbatim, never round or paraphrase the figure.
6. **Mark side effects.** Database writes, postings, emails, Service Layer syncs, and document status changes are called out as outcomes: *"Setelah lolos, dokumen di-**post** dan nomor seri diterbitkan."*
7. **Code preserves in footnote** — put original snippet or `class:method` reference under each step so a developer can trace back.

## Narrative Template

```
## [Nama Proses] — Alur Bisnis

**Tujuan:** <one line, outcome not mechanism>
**Pemicu (Trigger):** <event that starts it>

### Langkah
1. **Mulai.** <what fires>
2. **Cek:** <condition>. → Jika *ya*: <next>; Jika *tidak*: <next/berhenti>.
   - *Jika ya* → 3
   - *Jika tidak* → <langkah/berhenti, error>
3. **Proses core.** <calculation or transformation, with exact formula if any>
4. **Simpan / Kirim.** <database write, post, sync, email>
5. **Selesai.** <final state>

### Ringkasan aturan
| Kondisi | Hasil |
|---|---|
| <input state> | <what happens> |
```

## Worked Micro-Example

**Source (C# UI API):**
```csharp
private void Item_Event(string FormUID, ref ItemEvent pVal) {
  if (pVal.EventType != BoEventTypes.et_FORM_LOAD) return;
  if (LoadFrom.Freeze != null) LoadFrom.Freeze = false;
}
```

**Narrative:**
```
## Akses Form — Alur Bisnis
**Tujuan:** Memastikan form termuat dan dapat diisi oleh user.
**Pemicu:** User membuka form dokumen (mis. Order Pembelian).

1. **Mulai.** Sistem memuat form dari header.
2. **Cek:** Apakah ini peristiwa *muat form*? → Jika ya lanjut ke langkah 3; jika bukan (mis. klik/ubah kolom) sistem mengabaikannya.
3. **Aktifkan input.** Setelah form terbuka, field *LoadFrom* dibuka kuncinya agar user dapat memilih referensi dokumen asal.
4. **Selesai.** Form siap digunakan.
```

## When Translating Backend Algorithms (non-UI)

For pure backend (asset depreciation, cost allocation, GRPO matching):
- State **inputs** first (what data the process consumes).
- State **formula / allocation key** verbatim, with a plain-language reading.
- State **output** (journal entries, posting, generated transactions).
- Follow the same numbered-step template; there is no "form" trigger — trigger is a schedule, a status change, or an API call.

## Output contracts

- Narrative only ever references SAP objects via their business name plus a bracketed gloss, e.g. *"Order Pembelian (Purchase Order)"*.
- Never put `if/!=/&&`, C# keywords, form UIDs, or direct column names in the body text.
- Every step chains to the next with explicit "→".
- End with the summary rules table.

## Common mistakes

- Dumping source code as the deliverable (truncate → footnote only).
- Flattening branches into one sentence (kills readability of gates).
- Rounding/approximating business numbers.
- Dropping the "Selama terjadi error, apa yang terjadi?" story.
- Translating events like `et_DATA_ADD` without explaining *what user action* triggers them.

## Quick reference

| Source element | Narrative treatment |
|---|---|
| `EventType` switch | "Saat {user action} terjadi" → numbered branch |
| early `return` | "Jika kondisinya tidak terpenuhi, proses berhenti (dokumen tidak diproses)" |
| `Freeze = false` | "kolom {X} dibuka untuk diisi" |
| formula | exact equation + one-line plain reading |
| DB write / post / sync | "tersimpan / ter-*post* / tersinkronkan ke SAP" |
| exception block | "Bila terjadi galat, sistem menampilkan pesan dan membatalkan langkah" |

---

## Sub-Module: sap-b1-web-integration

# SAP B1 Web Integration Skill

Build web applications that integrate with SAP Business One — not add-ons (see `sap-b1-addon-dev`), but external systems that push/pull data via Service Layer or DI API.

## When to Use

Trigger on: "SAP B1 web integration", "web app connect to SAP B1", "batch push to SAP B1", "staging database SAP", "approval workflow SAP B1", "Laravel SAP B1 integration", or any request to build a web frontend that sends transactions to SAP B1.

Not for: SAP B1 add-on development (use `sap-b1-addon-dev`), SAP HANA queries (use `sap-hana-cli`), or SAP B1 functional configuration questions.

**User asks "buatkan prompt berdasarkan PRD":** use
`templates/build-prompt.md` — ready-to-paste build prompt (Laravel + auth +
user/roles + SAP B1 approval engine + stage controller page, non-AI-slop UI,
bahasa Indonesia). Fill the `<...>` placeholders (db name, modules, thresholds)
from the PRD before handing over.

## Architecture Pattern: Staging DB + Batch Processing

```
Web App (Laravel) → Staging DB (Cloud MySQL) → Scheduler → SAP B1
```

**Why staging DB?**
- Decouples web from SAP B1 (SAP B1 down → web still works)
- Allows approval workflow before pushing to SAP B1
- Provides audit trail and retry mechanism
- Handles network instability gracefully

**Key tables:**
- `staging_transactions` — all transactions with status tracking
- `approval_flow` — multi-level approval records
- `approval_templates` — configurable approval rules per module

See [references/architecture.md](references/architecture.md) for full schema and data flow.

## Batch Processing Pattern

```php
Every N minutes (Laravel scheduler + queue):
  1. Ping SAP B1 (timeout 5s) — offline → log 'unreachable', skip batch
  2. If success → SELECT 100 pending/approved transactions (with lines)
  3. Group by module, dispatch per-transaction job to queue
  4. Per-row sequential: success → COMMIT + status 'success'
     fail → log SL error + status 'failed' — NO batch rollback
```

**IMPORTANT (PRD V2 / actual repo):** sequential per-row processing, NOT all-or-nothing.
Each transaction commits independently; a failure must NOT roll back already-succeeded
rows in the same batch. Each job handles login, push, and its own status update.
Old all-or-nothing batch is superseded.

**Configuration:**
- Batch size: 10-100 (safe range, >300 causes performance issues)
- Schedule: 5 minutes (configurable) or queue-driven
- Concurrency: Single scheduler instance; worker pool via Redis queue
- Healthcheck before batch: `checkSapServiceLayer()` / `pingSapSl()`

See [references/batch-processing.md](references/batch-processing.md) for scheduler implementation details.

## Approval System

Multi-level, configurable approval workflow:

- **Unlimited levels** — not fixed to 2-3
- **Approver types** — User, Role, Department, or Custom condition
- **Timeout** — auto-escalate if no response within configured hours
- **Delegation** — approver can delegate to another user
- **Conditions** — amount threshold, department, custom rules

See [references/approval-system.md](references/approval-system.md) for schema and flow.

## SAP B1 Integration Methods

### Service Layer (Recommended for Web Apps)
- REST/OData API, HTTP-based
- Cross-platform, no client installation
- Default port: `https://localhost:50000/b1s/v2/` (actual deployments often use `:50001` + `b1s/v1` — check the running config)
- Session-based auth (login → cookie → requests)
- **Session caching is MANDATORY**: Service Layer limits concurrent sessions. Store `B1SESSION`/`ROUTEID` cookies in Redis with 25-min TTL (SL timeout is 30 min). Login flow: check Redis first → reuse if valid → else login and persist cookies. Do NOT login per request.
- Auto-reauth on session expiry (HTTP 401, error code 301, "Invalid session", "already timeout") — but retry exactly ONCE; see pitfalls.

See [references/service-layer-session.md](references/service-layer-session.md) for the full session-management pattern, the 301 infinite-recurse bug, and Http::fake testing pitfalls.

## Real-World Reference Implementation

IBT (Indobaruna Bulk Transport) procurement app — full procure-to-pay flow
(RL → PQ/PQC → PO → GRPO, inventory transfers) on Laravel + Inertia + SL,
with module↔ObjectType↔SL-entity mapping table and vessel bulk PR upload:
[references/ibt-procurement-app.md](references/ibt-procurement-app.md).
Includes the fast technique for recovering business flow from an unfamiliar
Laravel codebase (routes grep → services list → engine transition matrices →
migration comments).

Approval engine internals (state machine, approval_stages filter axes,
delegation/SLA, async queue sync path, access control incl. role_authorizations
max_approval_amount & branch isolation): [references/ibt-approval-engine.md](references/ibt-approval-engine.md).

### HANA vs SQL Server — Service Layer

Service Layer API identik untuk HANA maupun SQL Server. Endpoint, OData query, session management = sama. Beda cuma backend performance:

| Aspect | HANA | SQL Server |
|--------|------|------------|
| API endpoints | Identical (`/b1s/v1/`) | Identical |
| Port | 50000 (HTTP) / 50001 (HTTPS) | 50000 (HTTP) / 50001 (HTTPS) |
| Performance | Faster (in-memory) | Slower (disk-based) |
| Cloud | HANA Cloud → Service Layer ONLY | N/A |

> **HANA Cloud = Service Layer only.** DI API & UI API tidak bisa. Kalau target = cloud, rancang arsitektur dari awal ke Service Layer. Jangan bangun DI API dulu lalu migrasi.
> Port bisa beda per deployment — verifikasi konfigurasi actual. Beberapa pakai `:50001/b1s/v1/`.

### DI API (Higher Performance)
- Windows COM object, direct database access
- Requires SAP B1 client installed on Windows
- Faster but platform-dependent
- Good for: Windows services, batch jobs on same server

> **COM SDK may NOT be installed even when a "SAP SDK" exists (proven 2026-09).** SAP ships two SDKs; the `.NET` Service-Layer wrapper `SAPBusinessOneSDK.dll` (in `C:\Program Files (x86)\SAP\...\SAP Business One SDK\Lib\`) is often the only one installed. It is NOT the COM DI/UI API — it does NOT provide `SAPbobsCOM`/`SAPbouiCOM`/`Company`, and the COM exe dies with `0x80040154 Class not registered`. Verify with `find "/mnt/c/Program Files (x86)/SAP" -iname "SAPbobsCOM.dll"` — if only `SAPBusinessOneSDK.dll` is present, the COM dispatch add-on can't run there. For a web integration this doesn't matter (you use Service Layer over HTTP); it only blocks a COM add-on exe. This is a strong argument to architect the web→SAP path on Service Layer from the start.

### Mock (For Local Development)
- Build mock service that returns realistic responses
- Test all flows without SAP B1 installed
- Replace with real integration later

See [references/sap-b1-api.md](references/sap-b1-api.md) for API details and limitations.

## Local Development Setup

1. **Phase 1: Mock API** — Build all modules, approval, dashboard with mock responses
2. **Phase 2: Local SAP B1** — Install SAP B1 on Windows, test real integration
3. **Phase 3: Cloud** — Deploy to cloud, VPN to SAP B1 server

**WSL + Windows setup:**
- Laravel runs in WSL
- SAP B1 Service Layer runs on Windows
- Communication via HTTP (Service Layer URL)
- Docker stack: when the WSL distro lacks a `docker` CLI, call `docker.exe`/`docker-compose.exe`
  from the Windows Docker Desktop install dir (see local-setup.md "Running the Stack").
  Containers: `sap_app` (port 8080), `sap_mysql`, `sap_redis`, `sap_worker`.

See [references/local-setup.md](references/local-setup.md) for detailed setup guide.

## SAP B1 API Limitations

| Parameter | Limitation | Recommendation |
|-----------|------------|----------------|
| Batch size | >300 records slow | Keep at 100 per batch |
| Timeout | 30 seconds default | Set to 60 seconds |
| Page size | 20 records default | Use $top parameter |
| Rate limit | No strict limit | Avoid concurrent calls |
| Log files | Accumulate over time | Regular cleanup |

## Huawei Cloud Infrastructure (Production)

| Service | Purpose | Specification |
|---------|---------|---------------|
| ECS | Web + Scheduler | 2 vCPU, 4GB RAM each |
| RDS MySQL | Staging DB | MySQL 8.0, 2 vCPU, 4GB RAM |
| Redis | Cache & Queue | 2GB memory |
| OBS | File storage | Attachments, exports |
| VPN | SAP B1 connection | Site-to-site VPN |

Estimated cost: ~$165-270/month

## Pitfalls

1. **Batch rollback complexity** — Prefer sequential per-row commit (PRD V2) over all-or-nothing. User explicitly chose sequential: failures must not roll back already-successful rows.
2. **Concurrency** — Always use row-level locking (SELECT ... FOR UPDATE) + Redis lock. Only ONE scheduler instance.
3. **SAP B1 downtime** — Website must work when SAP B1 is offline. Staging DB is the buffer.
4. **Approval timeout** — Must have escalation mechanism. Approver might be offline/away.
5. **Permanent staging DB** — Data stored forever for audit. Need indexing strategy for performance.
6. **Service Layer session limits** — Never login per request. Cache B1SESSION/ROUTEID in Redis, TTL 25 min. Reuse across requests AND queue workers. Connection Limit Exceeded errors come from ignoring this.
7. **301 = session expired — retry exactly once** — SL returns error code 301 (sometimes HTTP 200 body!) on expired session. Auto-reauth + retry is fine, but if the guard flag is reset before retrying, a persistent 301 causes infinite recursion → PHP "Premature end of process" / stack overflow. Keep the reauth guard set through the retry; clear only after a non-session response.
8. **Http::fake() empty = silent success** — `Http::fake()` with no args makes EVERY request return 200 empty. Login "succeeds" with no cookies, POST returns empty body → `success=true` but `doc_entry=null` → TypeError when `markAsSynced(int $docEntry)` gets null. Always fake explicit Login + endpoint responses in tests.
9. **"Not configured" ≠ empty config service** — SapServiceLayer/ping reads `system_configs` DB table (dynamic), NOT `config('services.sap')`. To simulate unconfigured in tests, `SystemConfig::setValue('sap_sl_base_url', '')` — truncating the table makes getValue fall back to .env/config with a REAL URL.
10. **SLD re-login restriction** — Don't call Logout before re-Login; rapid Logout+Login pairs get rejected with "Fail to NONE-SSO login from SLD". Use backoff between attempts (1s, 2s, 3s).
11. **cURL error 28 ≠ SL down — check the stored base URL first** — `system_configs` can hold a STALE SAP IP (host moved networks / Wi-Fi changed). Symptom: timeout from WSL, from the Docker container, AND from Windows host ping — unreachable from every side = wrong IP, not network. Diagnose: `powershell Get-NetIPAddress -AddressFamily IPv4` lists CURRENT host IPs; if the stored URL doesn't match, update `SystemConfig::setValue('sap_sl_base_url', 'http://<current-ip>:50001')`. Firewall variant (Windows localhost reachable but WSL/container timeout) → add `New-NetFirewallRule` inbound allow for the port — see `wsl-windows-admin`.
12. **Redis session keys invisible via `Redis` facade** — Laravel's redis CACHE store uses the `cache` connection (REDIS_CACHE_DB=1 default), while the `Redis` facade uses `default` (DB 0). `Redis::keys('*sap_sl*')` returns empty even when sessions persist → looks like a bug. Verify with `Redis::connection('cache')->keys('*sap_sl*')` or `redis-cli -n 1 keys`; TTL ≈ 1500s proves the 25-min TTL works.

## Code Review Patterns

When reviewing a Laravel↔SAP B1 Service Layer integration, check for these
recurring issues. Full patterns, code examples, and fix recipes:
[references/code-review-patterns.md](references/code-review-patterns.md).

Critical checklist:
1. **No rand() fallback** for DocEntry/DocNum — return null if missing
2. **OData $filter escape** — single quotes in ALL user input (search, cardCode, itemCode)
3. **DRY payload building** — Job/Reconciler must call `buildDocumentPayload()`, not rebuild
4. **Binary endpoints** — separate method for PDF/Crystal Report, not JSON `request()`
5. **Webhook idempotency** — event_hash + unique constraint
6. **Session login lock** — `Cache::lock()` to prevent concurrent logins
7. **Job $tries=1** — document creation is NOT idempotent, no auto-retry
8. **Offline mode** — don't set `$created=true` when SAP unreachable

When the web portal needs UDFs created in SAP B1, see
[references/udf-mapping-template.md](references/udf-mapping-template.md)
for the full 18-field UDF spec (12 header + 6 line), DocObjectCode mapping,
master data checklist, gap analysis, and Excel template generation for
ConfigToolkit import.

## Related Skills

- `sap-b1-addon-dev` — SAP B1 add-on development (C#, DI API, UI API, UDO)
- `sap-hana-cli` — SAP HANA database queries
- `laravel` — Laravel best practices
- `sql` — Database design and optimization

---

## Sub-Module: sap-b1-fdd

# SAP B1 Functional Design Documentation (FDD) Standard

Skill ini adalah standar acuan tunggal (**single source of truth**) untuk menyusun dokumen **Functional Design Documentation (FDD)** add-on dan integrasi sistem berbasis SAP Business One, mengikuti standar baku dokumen konsultan **PT Soltius Indonesia** (termasuk referensi resmi *FDD - GRPO Service v1.2*).

Dokumen FDD berfungsi sebagai kontrak fungsional dan teknis antara konsultan implementor/developer dengan pihak client sebelum tahap pengkodean dimulai.

---

## 1. Anatomi dan Struktur Dokumen (Bab 1 s/d Bab 5)

Setiap FDD wajib memiliki struktur 5 bab standar berikut:

```
COVER PAGE (Page 1)
  ├── Banner SAP Business One (cover_image1.png - Center)
  ├── Logo Soltius (soltius_logo.png - Right Aligned)
  ├── Judul FDD (Hitam)
  ├── Nama Add-on / Modul Integrasi & Version (Hitam)
  ├── "DEVELOPED BY PT SOLTIUS INDONESIA"
  ├── "FOR"
  ├── Logo Client (misal: Logo IBT - Center)
  ├── Nama PT Client & Tahun
  └── Tabel Disclaimer & Confidentiality Statement (Page 1)

DAFTAR ISI (Page 2)
  └── TOC Otomatis (Heading 1, 2, 3)

BAB 1 — PENDAHULUAN
  ├── 1.1 Latar Belakang (Kondisi bisnis, gap SAP standard, urgensi solusi)
  ├── 1.2 Tujuan Development (List kata kerja: Mempermudah, Mengotomatisasi)
  ├── 1.3 Ruang Lingkup (Scope of Works positif & batasan negatif eksplisit)
  └── [Kotak Catatan Khusus jika diperlukan]

BAB 2 — PENJELASAN PROSES DEVELOPMENT
  ├── 2.1 Business Process (Skenario proses operasional)
  │     ├── Flowchart Swimlane Soltius (Aktor di kiri, Judul proses di atas tanpa nomor gambar)
  │     └── Keterangan Proses Bernomor (PIC, input, output, jurnal D/C)
  ├── 2.2 Arsitektur Sistem & Urutan Development (Scrum/Sprint atau Sync Hub)
  └── [Kotak Catatan Khusus di bawah subbab proses spesifik]

BAB 3 — DESIGN STRUKTUR DATA & UDF
  ├── 3.1 User-Defined Tables (UDT) / Database Schema Web
  ├── 3.2 User-Defined Fields (UDF) SAP B1 (Standar 7 kolom)
  ├── 3.3 User-Defined Objects (UDO) & Service Layer Endpoints
  ├── 3.4 Validasi Sistem & Format Error Code
  └── [Kotak Catatan Khusus Validasi]

BAB 4 — DESIGN USER INTERFACE
  ├── Subbab per Form / Modul
  ├── Sketsa Wireframe UI Anti-Slop (Prinsip /design-taste-frontend, tanpa tabrakan teks)
  └── Penjelasan Elemen Form, Grid, Action Button, & Role Access (Price Masking)

BAB 5 — APPROVAL
  └── Lembar Tanda Tangan Resmi (Salinan format persis FDD GRPO Service)
```

---

## 2. Standar Halaman Cover & Margin (Referensi GRPO Service)

### A. Format Halaman 1 (Cover Page)
1. **Banner SAP Business One**: Gambar `cover_image1.png` diletakkan di bagian paling atas (lebar penuh ~6.0 inch, center).
2. **Logo Soltius di Bawah Gambar SAP**: Gambar `soltius_logo.png` diletakkan tepat di bawah banner SAP (lebar ~1.32 inch, **rata kanan / right-aligned**).
3. **Tipografi Judul Hitam**:
   - Seluruh teks cover menggunakan warna **hitam murni** (`RGBColor(0, 0, 0)`), **bukan biru**.
   - Teks:
     ```
     FUNCTIONAL DESIGN DOCUMENTATION
     (FDD)
     <NAMA ADD-ON / INTEGRASI HURUF BESAR>
     VERSION <X.Y>
     DEVELOPED BY
     PT SOLTIUS INDONESIA
     FOR
     [Logo Client]
     PT <NAMA CLIENT>
     <TAHUN>
     ```
4. **Logo Client**: Diletakkan di atas nama PT Client dengan proporsi proporsional (tinggi ~0.8–1.0 inch, center).
5. **Disclaimer di Halaman 1**:
   - Tabel Disclaimer diletakkan di **bawah tahun pada Halaman 1** (tidak dipisah ke halaman tersendiri).
6. **Page 1 Isolasi**: Atur `section.different_first_page_header_footer = True`. Halaman 1 **tidak boleh memiliki header dan footer**.

### B. Margin Dokumen
- **Top Margin**: `1.0 inch` (72 pt)
- **Bottom Margin**: `1.0 inch` (72 pt)
- **Left Margin**: `1.25 inch` (90 pt)
- **Right Margin**: `1.25 inch` (90 pt)
- **Header Distance**: `0.5 inch` (36 pt)
- **Footer Distance**: `0.5 inch` (36 pt)

---

## 3. Standar Flowchart Swimlane Soltius

Flowchart FDD digambar secara programatik dengan layout **horizontal swimlane**:
1. **Aktor / Siapa yang Memproses di Sisi Kiri**:
   - Lane Atas: `USER (Kapal / Dept / Purchasing)`
   - Lane Bawah: `SYSTEM (Web Suite & SAP Business One)`
2. **Judul Proses di Atas (HANYA Nama Proses)**:
   - Header bar di atas flowchart hanya memuat nama proses transaksi (contoh: `ALUR PROSES PENGADAAN BARANG & JASA (END-TO-END WORKFLOW)`).
   - **DILARANG** menyertakan teks `(Gambar 2.x)` di dalam gambar flowchart, karena caption `Gambar 2.x. Nama Proses` sudah dicetak di bawah gambar pada dokumen Word.
3. **Simbol Formal Standar**:
   - Terminator (Oval): Start / End (warna netral lembut `#F1F5F9`).
   - Process (Rectangle): Proses komputasi / eksekusi sistem (`#FFFFFF`).
   - Data / Document I/O (Parallelogram): Penginputan form atau penerbitan dokumen (`#FFFFFF`).
   - Decision (Diamond): Titik keputusan dengan cabang berlabel jelas: "Ya" / "Tidak".
4. **Badge Sistem Pojok Kanan Atas**: Kotak kecil penanda sistem `SAP` atau `ADD-ON`.
5. **Warna Garis Konsisten**: Outline seluruh shape dan panah menggunakan **1 warna konsisten: Hitam (`#000000`)**. Panah bersifat **edge-to-edge** (orthogonal vertikal dan horizontal).

---

## 4. Standar UI Wireframe & Anti-Slop (Skill /design-taste-frontend)

1. **Tata Letak Bersih & Tanpa Tabrakan (Zero Collision)**:
   - Hindari menggambar modal pop-up yang menimpa teks tabel di latar belakang tanpa jarak yang jelas.
   - Gunakan layout berbasis HTML/CSS yang dirender headless via Edge (`--headless=new`) atau skrip vektor Matplotlib resolusi tinggi (180 DPI) monokrom hitam-putih murni (`#FFFFFF` background, garis `#1A202C`, aksen `#F7FAFC` / `#EDF2F7`).
2. **Aturan Bersih Wireframe Mockup**:
   - **Bebas Logo**: Tidak menyertakan logo perusahaan, emblem sistem, atau device frames (browser bar / laptop frame).
   - **Header Bar Minimalis**: Header hanya memuat **judul halaman murni** (contoh: *Requisition List*, *Purchase Quotation*, *Goods Receipt PO*, *Packing List GRPO IN*, *Packing List OUT*), tanpa embel-embel kalimat pendukung sistem.
   - **Daftar 19 Modul Mockup Standar FDD Add-On**:
     1. Halaman Login & Cabang
     2. Halaman Dashboard & Overview KPI
     3. Halaman Requisition List (RL)
     4. Halaman Katalog Master Suku Cadang
     5. Form Purchase Quotation (PQ)
     6. Form Price Quotation Comparison (PQC)
     7. Form Purchase Order (PO)
     8. Form Goods Receipt PO (GRPO)
     9. Form Packing List (GRPO IN)
     10. Form Packing List (OUT)
     11. Form Goods Return (GRE)
     12. Form Approval Center & Antrean
     13. Form Master Data & Sinkronisasi SAP
     14. Form Pelaporan & Audit Trail Siklus Dokumen
     15. Form Konfigurasi Sistem & Settings
     16. Form Pipeline Tahapan Approval (Approval Stages)
     17. Form Delegasi Wewenang Approval
     18. Form Manajemen Pengguna & Matriks Hak Akses
     19. Form Penomoran Dokumen Otomatis (Document Numbering Series)
3. **Standar Penyisipan ke Dokumen Word (FDD Point 3 / Bab UI)**:
   - Gunakan paragraph style standar Soltius: `SOL-Level 1` (Judul Bab), `SOL-Level 2` (Sub-bab), `SOL-Par1` (Deskripsi naratif), `SOL-List` (Rincian bernomor elemen form), dan `SOL-Free` (Gambar & Caption).
   - Gambar diposisikan Center dengan lebar proporsional A4 (`width = Inches(6.2)`).
   - Format Caption Gambar wajib Center, teks berformat **italic**, dan **warna hitam murni** (`RGBColor(0, 0, 0)`, bukan abu-abu):
     `p.add_run("Gambar 3.x. ")` (*Bold Italic Hitam*) diikuti `p.add_run("<Judul Halaman>")` (*Regular Italic Hitam*).
4. **Navbar & Price Masking**:
   - Topbar navigasi memuat **Active Branch Badge** yang permanen dan menonjol (`Cabang: Kantor Pusat Jakarta (BPL 1)`).
   - Panel komparasi menampilkan perbandingan side-by-side:
     - Tampilan Role Purchasing/SI: Seluruh harga satuan, diskon, PPN, dan grand total terbuka.
     - Tampilan Role Non-Purchasing: Nilai finansial disamarkan secara otomatis (`🔒 [ DILINDUNGI / MASKED ]`).

---

## 5. Standar Lembar Approval (Bab 5 — Format Resmi GRPO Service)

Format persis salinan acuan resmi *FDD - GRPO Service v1.2*:

```python
# PT SOLTIUS INDONESIA
SIGNED FOR PT SOLTIUS INDONESIA
Tabel 3 Kolom: NAME | DATE | SIGNED
- JANUAR FEBIYANTO (Quality Assurance)
- BAGUS PURPRADIGDO (Project Manager)
- YUDA HERNAWAN (Technical Consultant)

# CLIENT
SIGNED FOR  PT INDOBARUNA BULK TRANSPORT
Tabel 3 Kolom: NAME | DATE | SIGNED
- EDDY IRAWAN (Project Manager)
- RIDHO HERMAWAN (IT Team)
```

---

## Sub-Module: soltius-fdd-flowchart

# Soltius FDD Flowchart Style (Soltius v2 Standard)

> [!NOTE]
> Standar master FDD dan flowchart Soltius terpadu kini dikonsolidasi di skill [`sap-b1-fdd`](../sap-b1-fdd/SKILL.md). Gunakan panduan berikut untuk detail spesifik perenderan programatik Matplotlib.

## When to use
When generating flowcharts for SAP B1 add-on Functional Design Documents (FDD) that must match Soltius reference style (e.g. *FDD - GRPO Service v1.2*).

## Reference Documents
- `D:\SOLTIUS\FDD\FDD\Baru\OneDrive_2_03-09-2026\FDD - GRPO Service v1.2.docx`
- `D:\Metrodata\dokumen fdd\FDD - GRPO Service v1.2.docx`

## Visual Pattern (Soltius v2 Standard)

### 1. Shape & Simbol Formal
- **Start / End**: Oval / Stadium (`#F2F4F7`, border hitam 1.2 pt).
- **Process**: Rectangle (`#FFFFFF` / `#F0F4F8`, border hitam 1.2 pt).
- **Data / Document I/O**: Parallelogram / Jajaran Genjang (`#FFFFFF` / `#F4F6F9`, border hitam 1.2 pt).
- **Decision**: Diamond / Belah Ketupat (`#FFFFFF` / `#FFFDF0`, border hitam 1.2 pt). Label cabang "Ya" / "Tidak" pada panah.

### 2. Badge Sistem di Pojok Kanan Atas Shape
- Setiap shape proses/data/decision wajib memuat tag badge sistem di pojok kanan atas:
  - `SAP`: Untuk proses ERP / Service Layer / DI API.
  - `ADD-ON` / `WEB APP`: Untuk proses add-on / web interface.

### 3. Skema Warna & Panah
- Outline seluruh shape dan panah menggunakan **1 warna konsisten: Hitam (`#000000`)**.
- Layout orthogonal (vertikal dan horizontal saja).
- Panah harus **edge-to-edge** (menghubungkan tepi shape ke tepi shape tanpa memotong shape atau teks).

### 4. Penomoran & Keterangan Proses
- Setiap node diberi nomor lingkaran atau urutan (`1`, `2`, `3`...).
- Di bawah gambar flowchart dalam FDD, sertakan daftar **Keterangan proses:** bernomor yang memuat aktor (PIC), input dokumen, output, dan jurnal akuntansi jika relevan.

### 5. Font Matplotlib (CRITICAL)
- Font WAJIB menggunakan **`DejaVu Sans`** (default Matplotlib).
- DILARANG menggunakan `calibri.ttf` Windows karena merupakan variable font (`fvar`) yang dapat merusak ukuran teks menjadi mikroskopis.

---