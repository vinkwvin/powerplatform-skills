# HTML/CSS/JS → Power Apps: translation playbook

How to turn each front-end construct into the right control and Power Fx. The mapping table is the
quick lookup; the worked examples below show the patterns that aren't obvious, using markup shaped
like the real prototype pages (dashboard shell, editable asset table, upload zone, forms).

## Contents
1. Element / CSS → control mapping table
2. Layout: flex/grid → GroupContainer AutoLayout
3. Sidebar nav → Classic/Button
4. Cards → GroupContainer
5. Inputs, selects, radios, textareas
6. Tables → Gallery (read-only)
7. Editable tables (Add Row / delete) → collections
8. Status badges → Switch()
9. Upload drop zones → dashed GroupContainer
10. Icons: Material-Symbols → Icon.* enum
11. Interactions & forms → OnSelect / Patch / SubmitForm

---

## 1. Element / CSS → control mapping table

| HTML / CSS | Power Apps control | Notes |
|---|---|---|
| `<div>`/`<section>` with `flex`/`grid` | `GroupContainer@1.5.0` + `Variant: AutoLayout` | `flex-row`→Horizontal, `flex-col`→Vertical |
| `<div>` card (`bg-* rounded shadow`) | `GroupContainer@1.5.0` | white card → **omit** `DropShadow` |
| `<h1>…<h3>`, `<p>`, `<span>`, `<label>` | `Label@2.5.1` (bare) | size from token; caps labels → `Size: 9` |
| `<a>` / `<button>` (nav or action) | `Classic/Button@2.2.0` | active state = indigo fill + Semibold |
| `<input type=text/email>` | `Classic/TextInput@2.3.2` | `HintText` = placeholder |
| `<input type=number>` | `Classic/TextInput@2.3.2` | + `Format: =TextFormat.Number` |
| `<textarea>` | `Classic/TextInput@2.3.2` | + `Mode: =TextMode.MultiLine` |
| `<select>` | `Classic/DropDown@2.3.1` | needs `Items` **and** `Items.Value` |
| radio group | `Classic/Radio@2.3.0` | + `Layout`, `RadioSize`, `Items`+`Items.Value` |
| `<input type=checkbox>` | `Classic/CheckBox@2.1.0` | `Default`, `Text` |
| `<table>` (read-only) | `Gallery@2.15.0` (`Vertical`) | header row = separate Labels above |
| editable `<table>` + Add/delete JS | `Gallery` bound to a **collection** | `Collect`/`Remove`/`Patch` |
| status pill (`bg-status-* text-status-*`) | `Label` with `Fill`/`Color` via `Switch()` | see §8 |
| dashed upload zone (`border-dashed`) | `GroupContainer` `BorderStyle.Dashed` + Browse button | file picker is a placeholder |
| Material-Symbols `<span>` icon | `Classic/Icon@2.5.0` | map name → nearest `Icon.*` (§10) |
| avatar circle | `GroupContainer` (round via `RadiusX/Y`) + `Classic/Icon` `Icon.Person` | |
| CSS `gap` | `LayoutGap` on the container | |
| CSS `padding` | `PaddingTop/Right/Bottom/Left` | |

## 2. Layout: flex/grid → GroupContainer AutoLayout

Each layout `<div>` becomes a `GroupContainer` with `Variant: AutoLayout`. Direction and gap come
straight from the CSS.

```
<main class="ml-[260px] mt-16 p-container_padding flex flex-col gap-stack_lg">
```
→
```yaml
- ContentArea:
    Control: GroupContainer@1.5.0
    Variant: AutoLayout
    Properties:
      Height: =Parent.Height
      LayoutDirection: =LayoutDirection.Vertical    # flex-col
      LayoutGap: =24                                  # gap-stack_lg (24px)
      LayoutOverflowY: =LayoutOverflow.Scroll         # if content scrolls
      PaddingBottom: =32                              # p-container_padding (32px)
      PaddingLeft: =32
      PaddingRight: =32
      PaddingTop: =32
      Width: =Parent.Width - 208                      # ml-[260px] → sidebar 208 at 0.8
      X: =208
      Y: =0
```
A `grid grid-cols-2 gap-gutter` → a Horizontal AutoLayout container (or two, if it wraps), each child
card given `FillPortions: =1` and an explicit `Height`/`LayoutMinHeight`.

## 3. Sidebar nav → Classic/Button

Nav `<a>` items are **buttons, not labels** — they need hover/press/active fills. Active tab
(`bg-primary-container/10 text-primary font-bold`) vs inactive (`text-on-surface-variant`):

```yaml
- NavDashboard:                     # ACTIVE
    Control: Classic/Button@2.2.0
    Properties:
      Align: =Align.Left
      Color: =RGBA(59, 57, 194, 1)          # text-primary
      Fill: =RGBA(238, 242, 255, 1)         # primary-container tint
      FontWeight: =FontWeight.Semibold
      Height: =35
      HoverFill: =RGBA(234, 230, 242, 1)
      OnSelect: =Notify("Dashboard", NotificationType.Information)
      Size: =11
      Text: ="Dashboard"
      Width: =176
- NavSales:                          # INACTIVE
    Control: Classic/Button@2.2.0
    Properties:
      Align: =Align.Left
      Color: =RGBA(70, 69, 84, 1)           # text-on-surface-variant
      Fill: =RGBA(255, 255, 255, 1)
      Height: =35
      HoverFill: =RGBA(234, 230, 242, 1)
      OnSelect: =Navigate('Sales - Check DA')
      Size: =11
      Text: ="Sales"
      Width: =176
```
If the nav item has an icon + text, either place a `Classic/Icon` beside a `Label` inside a small
Horizontal container, or keep it a single button and drop the icon (note the omission).

## 4. Cards → GroupContainer

```
<div class="bg-surface rounded-lg p-stack_lg flex flex-col gap-stack_sm shadow-[...] border ...">
  <h3 class="font-label-caps ... uppercase">PENDING TASKS</h3>
  <span class="text-[48px] font-bold text-error">5</span>
</div>
```
→ white/surface card = **omit `DropShadow`** (default elevation matches the subtle
`shadow-[0_2px_4px_rgba(0,0,0,0.05)]`); label-caps → `Size: 9`; big number → `Size: 32`, colored
from the token (`text-error` → `RGBA(186, 26, 26, 1)`). Give the card an explicit `Height` +
`LayoutMinHeight`.

## 5. Inputs, selects, radios, textareas

```yaml
# <input type="text" placeholder="Filter by Customer Name...">
- FilterName:
    Control: Classic/TextInput@2.3.2
    Properties:
      BorderColor: =RGBA(119, 117, 134, 1)
      Height: =32
      HintText: ="Filter by Customer Name..."
      Width: =360

# <textarea rows="4" placeholder="Enter ledger verification steps...">
- AuditRemarks:
    Control: Classic/TextInput@2.3.2
    Properties:
      Height: =96
      HintText: ="Enter ledger verification steps, discrepancy notes..."
      Mode: =TextMode.MultiLine
      Width: =Parent.Width - 48

# <select> ... <option>All Statuses</option> ...
- StatusFilter:
    Control: Classic/DropDown@2.3.1
    Properties:
      Height: =32
      Items: |
        =["All Statuses", "Pending Risk", "Completed", "Pending Operation", "Rejected", "Pending Middle"]
      Items.Value: =Value                 # REQUIRED companion
      Width: =256

# radio group Yes/No
- ConfirmRadio:
    Control: Classic/Radio@2.3.0
    Properties:
      Default: ="Yes"
      Items: =["Yes", "No"]
      Items.Value: =Value
      Layout: =Layout.Horizontal
      RadioSize: =30
```
`<input type=number>` is the same as text plus `Format: =TextFormat.Number`.

## 6. Tables → Gallery (read-only)

See the full Gallery skeleton in `yaml-conventions.md` §10. Process:
1. `<thead>` → a row of `Label`s **above** the gallery (not inside it), or the gallery's own header
   band. Keep column X/Width identical to the template.
2. `<tbody>` rows → the gallery **template** (one row of controls). Repeated `<tr>`s in the HTML are
   just sample data — represent them as gallery `Items`, not as duplicated controls.
3. Each `<td>` → a `Label`/control with `Text: =ThisItem.<Field>` and the column's `X`/`Width`.
4. Row action `<button>` (e.g. "View") → `Classic/Button` in the template, `OnSelect` referencing
   `ThisItem`.

Derive `Items` from the columns: `Request ID, Customer Name, Date, Status, Reject Count, Action` →
`colRequests` records `{RequestId, CustomerName, RequestDate, Status, RejectCount}`.

## 7. Editable tables (Add Row / delete) → collections

When the JS builds rows dynamically (an `addRowBtn` that appends a `<tr>`, delete buttons that remove
the row), that's a **collection** in Power Apps — not static controls.

Source shape (from the asset-entry page):
```js
addRowBtn.onclick = () => tbody.appendChild(newRow);   // Add Row
deleteBtn.onclick = () => this.closest('tr').remove(); // Remove row
// each row: <select> coin  +  <input type=number> balance  +  delete
```
→
```yaml
# On the screen: seed one empty row when the screen opens
Screens:
  Sales - Customer Asset Entry:
    Properties:
      LoadingSpinnerColor: =RGBA(56, 96, 178, 1)
      OnVisible: =ClearCollect(colAssets, {Coin: "", Balance: 0})
    Children:
      - AddRowButton:
          Control: Classic/Button@2.2.0
          Properties:
            OnSelect: =Collect(colAssets, {Coin: "", Balance: 0})   # Add Row
            Text: ="Add Row"
      - AssetGallery:
          Control: Gallery@2.15.0
          Variant: Vertical
          Properties:
            Height: =260
            Items: =colAssets
            LayoutMinHeight: =260
            TemplateSize: =60
          Children:
            - RowCoin:
                Control: Classic/DropDown@2.3.1
                Properties:
                  Default: =ThisItem.Coin
                  Items: =["Bitcoin (BTC)", "Ethereum (ETH)", "Tether (USDT)"]
                  Items.Value: =Value
                  Width: =280
                  X: =0
            - RowBalance:
                Control: Classic/TextInput@2.3.2
                Properties:
                  Default: =Text(ThisItem.Balance)
                  Format: =TextFormat.Number
                  HintText: ="0.00000000"
                  Width: =420
                  X: =290
            - RowDelete:
                Control: Classic/Icon@2.5.0
                Properties:
                  Color: =RGBA(70, 69, 84, 1)
                  Icon: =Icon.Trash
                  OnSelect: =Remove(colAssets, ThisItem)              # delete row
                  Width: =24
                  X: =720
```
Writing edits back to a record is out of scope for a static prototype; if the user wants persistence,
use `Patch(DataSource, Defaults(...), {...})` on submit — otherwise leave `Notify(...)`.

## 8. Status badges → Switch()

A pill whose background/text come from `bg-status-*-bg` / `text-status-*-text` tokens becomes a
`Label` with `Fill` and `Color` set by a `Switch()` on the status value. Because the formula spans
lines, it **must** be a block scalar. Status token colors (from the MD3 theme):

| Status | bg → Fill | text → Color |
|---|---|---|
| Pending (any) | `RGBA(170, 237, 255, 1)` | `RGBA(0, 104, 121, 1)` |
| Completed | `RGBA(204, 239, 140, 1)` | `RGBA(60, 87, 1, 1)` |
| Rejected | `RGBA(255, 218, 214, 1)` | `RGBA(186, 26, 26, 1)` |

```yaml
- StatusBadge:
    Control: Label@2.5.1
    Properties:
      Align: =Align.Center
      Color: |
        =Switch(true,
          StartsWith(ThisItem.Status, "Pending"), RGBA(0, 104, 121, 1),
          ThisItem.Status = "Completed", RGBA(60, 87, 1, 1),
          ThisItem.Status = "Rejected", RGBA(186, 26, 26, 1),
          RGBA(70, 69, 84, 1))
      Fill: |
        =Switch(true,
          StartsWith(ThisItem.Status, "Pending"), RGBA(170, 237, 255, 1),
          ThisItem.Status = "Completed", RGBA(204, 239, 140, 1),
          ThisItem.Status = "Rejected", RGBA(255, 218, 214, 1),
          RGBA(228, 225, 236, 1))
      Text: =ThisItem.Status
```

## 9. Upload drop zones → dashed GroupContainer

```
<div class="border-2 border-dashed border-outline-variant rounded-xl p-8 flex flex-col items-center">
  <span class="material-symbols-outlined">cloud_upload</span>
  <p>Drag and drop files here or</p>
  <button>Browse Files</button>
</div>
```
→ a `GroupContainer` with a dashed border containing an upload icon, a label, and a Browse button.
Canvas file input needs an attachment/`AddMediaButton` control to truly pick files; for a prototype,
a `Classic/Button` with a `Notify` placeholder is fine — flag it.

```yaml
- UploadZone:
    Control: GroupContainer@1.5.0
    Variant: AutoLayout
    Properties:
      BorderColor: =RGBA(199, 196, 215, 1)
      BorderStyle: =BorderStyle.Dashed
      BorderThickness: =2
      Fill: =RGBA(245, 242, 254, 1)
      Height: =160
      LayoutAlignItems: =LayoutAlignItems.Center
      LayoutDirection: =LayoutDirection.Vertical
      LayoutGap: =16
      LayoutMinHeight: =160
    Children:
      - UploadIcon:
          Control: Classic/Icon@2.5.0
          Properties:
            Color: =RGBA(59, 57, 194, 1)
            Icon: =Icon.Publish            # cloud_upload → nearest
            Height: =32
            Width: =32
      - UploadHint:
          Control: Label@2.5.1
          Properties:
            Text: ="Drag and drop files here or"
      - BrowseButton:
          Control: Classic/Button@2.2.0
          Properties:
            Fill: =RGBA(85, 85, 219, 1)
            Color: =RGBA(255, 255, 255, 1)
            OnSelect: =Notify("File picker not wired yet", NotificationType.Information)
            Text: ="Browse Files"
```

## 10. Icons: Material-Symbols → Icon.* enum

There is no 1:1 mapping. Use the nearest built-in `Icon.*`; if nothing fits, drop the icon and note
it. Common ones seen in these prototypes:

| Material-Symbols | Power Apps `Icon.*` |
|---|---|
| `dashboard` | `Icon.Home` or `Icon.Table` |
| `point_of_sale` | `Icon.Money` |
| `account_balance_wallet` | `Icon.Money` |
| `account_tree` | `Icon.Shop` (approx) |
| `manage_accounts` | `Icon.Person` |
| `settings` | `Icon.Settings` |
| `handshake` | `Icon.People` (approx) |
| `account_balance` | `Icon.Money` |
| `analytics` | `Icon.Trending` |
| `search` / `person_search` | `Icon.Search` |
| `filter_list` | `Icon.Filter` |
| `add` | `Icon.Add` |
| `delete` | `Icon.Trash` |
| `content_copy` | `Icon.Copy` |
| `cloud_upload` / `upload_file` | `Icon.Publish` |
| `expand_more` | `Icon.ChevronDown` |
| `arrow_back` | `Icon.Back` |
| `person` | `Icon.Person` |
| `check_circle` | `Icon.CheckBadge` or `Icon.Check` |
| `gavel` | `Icon.DetailList` (approx) |

Verify each against the `Icon.*` enum in Studio; approximations are fine for a prototype but should
be flagged so the user can refine them.

## 11. Interactions & forms → OnSelect / Patch / SubmitForm

- `<a href="pages/x.html">` or `onclick="window.location.href='x'"` → `OnSelect: =Navigate('Screen
  Name')`. If that screen isn't built yet, `OnSelect: =Notify("Go to X", NotificationType.Information)`.
- Cancel / Back → `OnSelect: =Navigate(Dashboard)` (or `Back()`).
- Submit that persists data → `OnSelect: =Patch(DataSource, Defaults(DataSource), {Field: Ctrl.Text,
  …}); Navigate(Dashboard)` — or `SubmitForm(FormName)` if you modeled it as a form. For a prototype
  with no data source, `OnSelect: =Notify("Submitted", NotificationType.Success); Navigate(Dashboard)`.
- Search button filtering a gallery → set the gallery `Items` to a `Filter(...)`/`Search(...)` over
  the collection using the input's `.Text`, rather than an `OnSelect` handler.
- Any handler whose real behavior depends on a flow/connector/data source that doesn't exist yet →
  `Notify(...)` placeholder, and list it in the delivery notes.
