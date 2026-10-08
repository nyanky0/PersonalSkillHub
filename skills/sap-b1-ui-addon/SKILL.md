---
name: sap-b1-ui-addon
description: "SAP Business One UI API add-on skill (SAPbouiCOM, 212 objects)."
---

# SAP B1 — UI API (UI Add-On) Skill

Sumber: `REFUI.chm` — SAP B1 UI API Reference, 212 objek (namespace `SAPbouiCOM`).
UI API menangani **tampilan & interaksi** add-on di SAP B1 desktop (Windows client).

## Model objek inti

| Objek | Peran |
|-------|-------|
| `SboGuiApi` | Titik masuk: konek ke SAP B1 yang sedang berjalan, dapatkan `Application`. |
| `Application` | Root UI API: forms, menu, event, dsb. |
| `Form` | Sebuah form (window) add-on. Punya `Items`, `DataSources`, `Mode`. |
| `Item` | Elemen dalam form (button, edit text, combo, grid, dll.) — tipe via `Item.Type` (enum `BoFormItemTypes`). |
| `FormDataSources` | `DataSources.DBDataSource`, `.UserDataSource`, `.DataTable` — jembatan data form. |
| `Events` | Registrasi handler event (ItemEvent, FormEvent, AppEvent, MenuEvent). |
| `Menu` | Menu add-on. |
| `ChooseFromList` | Pencarian (CFL) — dialog pilih BP/item/dokumen. |

## Alur dasar add-on UI

1. Buat proyek add-on (C# / VB.NET) dengan referensi `SAPbouiCOM`.
2. Connect ke aplikasi yang berjalan:

```csharp
SboGuiApi oGui = new SboGuiApi();
oGui.Connect("0030002C0030002C0030002C0030002C0030002C0030002C0030002C0030002C");
Application oApp = oGui.GetApplication(-1);
```

`Connect` menerima connection string yang disediakan SAP B1 (Add-On Manager). Jangan hardcode selain placeholder.

3. Buat form dari XML (`FormCreationParams`), tambahkan ke `oApp.Forms`.
4. Daftarkan handler event di `oApp.RegisterEvent(...)` atau via `Events` manager.
5. Isi data via `DataSources` atau langsung ke item.

## Membuat form dari XML (pola umum)

```csharp
FormCreationParams oParams = oApp.CreateObject(BoCreatableObjectType.cot_FormCreationParams);
oParams.XmlData = "<Form ...>...</Form>"; // atau load dari file
oParams.UniqueID = "my_form_1";
Form oForm = oApp.Forms.AddForm(oParams);
```

Form XML biasanya dibuat dengan **Screen Painter** (file `.xml`) dan di-embed sebagai resource. Elemen kunci: `<form>`, `<items>`, `<item>`, `<datasources>`, `<mode>`.

## Item penting & tipe

| Item Type (`BoFormItemTypes`) | Elemen UI |
|---------------------------|-----------|
| `it_EDIT` | EditText (input satu baris) |
| `it_BUTTON` | Button (tombol) |
| `it_COMBO_BOX` | ComboBox (dropdown) |
| `it_GRID` | Grid (tabel data) |
| `it_MATRIX` | Matrix (grid dokumen) |
| `it_STATIC` | Static text (label) |
| `it_FOLDER` | Folder/tab |
| `it_PICTURE` | Picture (gambar) |
| `it_LINKED_BUTTON` | Linked button |
| `it_CHECK_BOX` | Checkbox |
| `it_OPTION_BUTTON` | Option button (radio) |
| `it_EXTEDIT` | Extended edit (memo/richtext) |
| `it_ACTIVE_X` | ActiveX control |
| `it_WEB_BROWSER` | Web browser control |
| `it_RECTANGLE` | Rectangle (dekorasi) |
| `it_BUTTON_COMBO` | Button + Combo |
| `it_PANE_COMBO_BOX` | Pane combo box |

Akses item: `oForm.Items.Item("item_uid")`. Ambil kontrol spesifik via `oForm.Items.Item("x").Specific` (mis. `EditText`, `Button`).

## Event (BoEventTypes — inti)

Event di-handle lewat `Application` events manager. Event umum:

| Event | Kapan terjadi |
|-------|---------------|
| `et_ITEM_PRESSED` | Tombol/item diklik |
| `et_CLICK` | Klik pada item |
| `et_COMBO_SELECT` | Pilihan combo berubah |
| `et_VALIDATE` | Validasi input |
| `et_GOT_FOCUS` / `et_LOST_FOCUS` | Fokus masuk/keluar |
| `et_FORM_LOAD` | Form selesai dimuat |
| `et_FORM_ACTIVATE` / `et_FORM_DEACTIVATE` | Form aktif/nonaktif |
| `et_FORM_CLOSE` | Form ditutup |
| `et_FORM_DATA_LOAD` | Data form dimuat |
| `et_FORM_DATA_ADD` / `et_FORM_DATA_UPDATE` / `et_FORM_DATA_DELETE` | CRUD data form |
| `et_CHOOSE_FROM_LIST` | CFL dipilih/dibatalkan |
| `et_KEY_DOWN` | Tombol keyboard ditekan |
| `et_DOUBLE_CLICK` | Double click |
| `et_DATASOURCE_LOAD` | DataSource dimuat |

Daftar lengkap: `python C:/Users/yudah/.sap-b1-skills/search_sap.py ui event` atau baca `SAPbouiCOM~Enumerations~BoEventTypes_EN.html` di corpus.

### Contoh handler (C#)

```csharp
void OnItemEvent(string FormUID, ref ItemEvent pVal, out bool BubbleEvent)
{
    BubbleEvent = true;
    if (pVal.BeforeAction && pVal.EventType == BoEventTypes.et_ITEM_PRESSED)
    {
        if (pVal.ItemUID == "btnSave")
        {
            // simpan
        }
    }
}
```

## DataSources

```csharp
// DBDataSource: tampilkan data dari tabel/query ke grid
DBDataSource oDBDS = oForm.DataSources.DBDataSources.Add("OCRD");
oDBDS.Query("SELECT CardCode, CardName FROM OCRD WHERE CardType='C'");
// DataTable: data non-DB
DataTable oDT = oForm.DataSources.DataTables.Add("dt1");
// UserDataSource: variabel form (bind item)
UserDataSource oUDS = oForm.DataSources.UserDataSources.Add("udsVar", BoDataType.dt_SHORT_TEXT);
oUDS.Value = "test";
```

Grid diisi via `DataTable`; combo diisi via `ValidValues.Add(...)`.

## Menu add-on

```csharp
MenuItem oItem = oApp.Menus.Item("1280").SubMenus.Add("my_menu", "Menu Saya",
    BoMenuType.mt_STRING, 1, true, false);
oApp.RegisterEvent(50000, "my_menu", BoEventTypes.et_MENU_CLICK); // dll.
```

Event menu ditangani via `MenuEvent` (`pVal.MenuUID`).

## Choose From List (CFL)

```csharp
ChooseFromList oCFL = oForm.ChooseFromLists.Add("cfl_bp", BoCFLType.cft_Regular);
oCFL.SetConditions(new Condition()); // filter
// event et_CHOOSE_FROM_LIST -> pVal.SelectedObjects -> ambil SelectedObject
```

## Best practices

- **Selalu cek `pVal.BeforeAction`** untuk membedakan before/after.
- **`BubbleEvent`** harus di-set (`true` = lanjut ke SAP, `false` = blokir).
- Jangan akses item sebelum form selesai load — gunakan `et_FORM_LOAD`.
- Gunakan **Screen Painter** untuk desain form, lalu embed XML sebagai resource.
- Tutup form dengan `oForm.Close()`; pastikan unsubscribe event bila perlu.
- Mode form: `BoFormMode.fm_ADD_MODE` / `fm_UPDATE_MODE` / `fm_OK_MODE` — cek via `pVal.FormMode`.
- Untuk performa grid besar, set `AutoResizeColumns` dan matikan redraw saat mengisi (`oForm.Freeze(true)` ... `Freeze(false)`).

## Menelusuri objek UI apa pun

```bash
python C:/Users/yudah/.sap-b1-skills/search_sap.py ui <objek>
# contoh: ui "grid", ui "datatable", ui "menuevent", ui "form"
```

Baca halaman lengkap di `C:/Users/yudah/.sap-b1-help/REFUI/SAPbouiCOM~<Objek>.html`.

## Pitfalls

- Nama item di XML harus **unik** dalam satu form.
- `Item.Type` read-only — tipe ditentukan saat form XML dibuat.
- `DataTable` perlu `Columns.Add` sebelum mengisi nilai.
- Event handler yang di-register untuk semua form (`et_FORM_ACTIVATE`) bisa mahal — batasi scope.
- CFL `SelectedObjects` hanya valid dalam event `et_CHOOSE_FROM_LIST`; ambil sebelum `BubbleEvent=false`.
- COM interop: release object untuk hindari kebocoran memori di add-on yang berjalan lama.
