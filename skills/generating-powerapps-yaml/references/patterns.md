# Translation patterns

HTML/CSS/JS → Power Apps controls. Carried forward from the retired `powerapps-yaml` playbook,
with values corrected against the 17 screens that compiled.

## Contents
1. Element → control mapping
2. flex/grid → AutoLayout
3. Sidebar nav
4. Cards
5. Inputs, selects, radios, textareas
6. Tables → Gallery
7. Editable tables → collections
8. Status badges → Switch()
9. Upload zones
10. Icons — and the mapping problem
11. Screen skeleton

---

## 1. Element → control mapping

| HTML / CSS | Control | Notes |
|---|---|---|
| `<div>`/`<section>` with `flex`/`grid` | `GroupContainer@1.5.0` + `Variant: AutoLayout` | `flex-row` → Horizontal, `flex-col` → Vertical |
| card `<div>` (`bg-white rounded shadow`) | `GroupContainer@1.5.0` | white card → **omit** `DropShadow` |
| `<h1>`–`<h3>`, `<p>`, `<span>`, `<label>` | `Label@2.5.1` bare | caps micro-labels → `Size: =9` |
| `<a>` / `<button>` | `Classic/Button@2.2.0` | active nav = indigo fill + `FontWeight.Semibold` |
| `<input type=text\|email>` | `Classic/TextInput@2.3.2` | `HintText` = placeholder |
| `<input type=number>` | `Classic/TextInput@2.3.2` | + `Format: =TextFormat.Number` |
| `<textarea>` | `Classic/TextInput@2.3.2` | + `Mode: =TextMode.MultiLine` |
| `<select>` | `Classic/DropDown@2.3.1` | `Items` **and** `Items.Value` |
| radio group | `Classic/Radio@2.3.0` | + `Layout`, `RadioSize: =18`, `Items`, `Items.Value` |
| `<input type=checkbox>` | `Classic/CheckBox@2.1.0` | `Default`, `Text` |
| `<table>` read-only | `Gallery@2.15.0` `Vertical` | header row = separate Labels above the gallery |
| editable `<table>` + Add/delete JS | `Gallery` bound to a collection | `Collect` / `Remove` / `Patch` |
| status pill | `Label` with `Fill`/`Color` via `Switch()` | §8 |
| dashed upload zone | `GroupContainer` + `BorderStyle: =BorderStyle.Dashed` | picker is a placeholder |
| Material-Symbols icon `<span>` | `Classic/Icon@2.5.0` | §10 — read it, the enum is small |
| avatar circle | `GroupContainer` with all four `Radius*` + `Classic/Icon` `Icon.Person` | |
| CSS `gap` | `LayoutGap` | |
| CSS `padding` | `PaddingTop/Right/Bottom/Left` | |
| CSS `width: calc(100% - 40px)` | `Width: =Parent.Width - 40` | the standard inset idiom |

## 2. flex/grid → AutoLayout

```yaml
- Content_Row:
    Control: GroupContainer@1.5.0
    Variant: AutoLayout
    Properties:
      DropShadow: =DropShadow.None
      FillPortions: =0
      Height: =86
      LayoutAlignItems: =LayoutAlignItems.Center     # align-items: center
      LayoutDirection: =LayoutDirection.Horizontal   # flex-row
      LayoutGap: =16                                 # gap-4
      LayoutMinHeight: =86
      PaddingLeft: =24
      PaddingRight: =24
      Width: =Parent.Width - 40
```

No `X`/`Y`. A horizontal row usually wants `LayoutAlignItems: =LayoutAlignItems.Center`, and any
fixed-height child inside it wants `AlignInContainer: =AlignInContainer.Center` so it does not
stretch.

## 3. Sidebar nav

**Nav items are always `Classic/Button@2.2.0`, never `Label`** — even when the mockup shows what
looks like plain text with an icon. It has to be clickable. If the destination screen does not
exist yet, still use a Button and set `OnSelect` to a `Notify(...)` placeholder. Do not invent a
`Navigate()` target.

Sidebar container: `Width: =208`, `LayoutDirection: =LayoutDirection.Vertical`,
`LayoutOverflowY: =LayoutOverflow.Scroll`, `Fill: =RGBA(255, 255, 255, 1)`.
Nav buttons: `Height: =34`, `Size: =11`, `Align: =Align.Left`.

Active item: `Fill: =RGBA(238, 242, 255, 1)`, indigo text, `FontWeight: =FontWeight.Semibold`.

## 4. Cards

```yaml
- Stat_Card:
    Control: GroupContainer@1.5.0
    Variant: AutoLayout
    Properties:
      Fill: =RGBA(255, 255, 255, 1)
      Height: =102
      LayoutDirection: =LayoutDirection.Vertical
      LayoutGap: =8
      LayoutMinHeight: =102
      PaddingBottom: =16
      PaddingLeft: =16
      PaddingRight: =16
      PaddingTop: =16
      RadiusBottomLeft: =12
      RadiusBottomRight: =12
      RadiusTopLeft: =12
      RadiusTopRight: =12
```

`DropShadow` is omitted here on purpose — the default elevation on a white surface is already
right. On flat structural containers write `DropShadow: =DropShadow.None`.

## 5. Inputs, selects, radios, textareas

```yaml
- Filter_Input:
    Control: Classic/TextInput@2.3.2
    Properties:
      BorderColor: =RGBA(199, 196, 215, 1)
      BorderThickness: =1
      Default: =""
      Fill: =RGBA(255, 255, 255, 1)
      FocusedBorderColor: =RGBA(59, 57, 194, 1)
      FocusedBorderThickness: =1
      Height: =32
      HintText: ="Filter by Customer Name..."
      HoverBorderColor: =RGBA(120, 118, 134, 1)
      HoverFill: =RGBA(247, 246, 252, 1)
      Size: =11
      Width: =Parent.Width - 24
```

Textarea: add `Mode: =TextMode.MultiLine` and a taller `Height`.
Numeric: add `Format: =TextFormat.Number`.

```yaml
- Reason_Picker:
    Control: Classic/DropDown@2.3.1
    Properties:
      Items: |
        =["เจ้าของบัญชีเสียชีวิต", "ลูกค้าไม่ประสงค์ใช้บริการ", "อื่นๆ"]
      Items.Value: =Value          # omitting this renders an empty dropdown, silently
```

Conditional reveal: do **not** bind `Visible` directly to `DropDown.Selected.Value` — it does not
re-evaluate reliably on paste. Write a context variable in `OnChange` and bind `Visible` to that.

```yaml
      OnChange: |
        =UpdateContext({varReasonOther: Self.Selected.Value = "อื่นๆ"})
```

## 6. Tables → Gallery

Header labels sit above the gallery; the template holds one row referencing `ThisItem.*`. Header
and template column widths must match exactly or cells drift.

```yaml
- Requests_Gallery:
    Control: Gallery@2.15.0
    Variant: Vertical
    Properties:
      Height: =210
      Items: =colRequests
      LayoutMinHeight: =210
      TemplatePadding: =0
      TemplateSize: =40
      Width: =Parent.Width - 40
    Children:
      - Cell_RequestId:
          Control: Label@2.5.1
          Properties:
            Color: =RGBA(27, 27, 35, 1)
            FillPortions: =0
            Height: =Parent.TemplateHeight
            Size: =11
            Text: =ThisItem.RequestId
            VerticalAlign: =VerticalAlign.Middle
            Width: =176
```

## 7. Editable tables → collections

Seed the collection in the screen's `OnVisible`, guarded so re-entry does not wipe edits:

```yaml
      OnVisible: |
        =If(IsEmpty(colMatrix), ClearCollect(colMatrix,
          {Acct: "Cash Account", Pick: ""},
          {Acct: "Credit Balance", Pick: ""}))
```

Add row → `Collect(colMatrix, {Acct: "", Pick: ""})`.
Delete row → `Remove(colMatrix, ThisItem)`.
Edit a cell → `Patch(colMatrix, ThisItem, {Pick: Self.Selected.Value})`.

**Do not bake live SharePoint datasource bindings into pasted YAML** — they error on paste
because the datasource is not yet added to the app. Ship paste-safe collections plus a short
wiring note telling the user which collection maps to which list.

## 8. Status badges → Switch()

A pill is a `Label` whose `Fill` and `Color` come from `Switch()` on the status. Both need block
scalars — they are multi-line and contain commas.

```yaml
- Cell_Status:
    Control: Label@2.5.1
    Properties:
      Align: =Align.Center
      Color: |
        =Switch(ThisItem.Status,
          "Pending Risk", RGBA(0, 104, 121, 1),
          "Completed", RGBA(60, 87, 1, 1),
          "Rejected", RGBA(186, 26, 26, 1),
          RGBA(70, 69, 84, 1))
      Fill: |
        =Switch(ThisItem.Status,
          "Pending Risk", RGBA(170, 237, 255, 1),
          "Completed", RGBA(204, 239, 140, 1),
          "Rejected", RGBA(255, 224, 221, 1),
          RGBA(228, 225, 236, 1))
      FillPortions: =0
      Height: =22
      Size: =9
      Text: =ThisItem.Status
      VerticalAlign: =VerticalAlign.Middle
      Width: =140
```

**Corrected value.** The retired playbook gave `RGBA(255, 218, 214, 1)` for the rejected
background. That value occurs **zero** times in the 17 screens; the shipped value is
`RGBA(255, 224, 221, 1)` (10 uses). Measured badge palette:

| Status | Fill | Color |
|---|---|---|
| Pending | `RGBA(170, 237, 255, 1)` (50) | `RGBA(0, 104, 121, 1)` (75) |
| Completed | `RGBA(204, 239, 140, 1)` (19) | `RGBA(60, 87, 1, 1)` (25) |
| Rejected | `RGBA(255, 224, 221, 1)` (10) | `RGBA(186, 26, 26, 1)` (74) |
| Neutral | `RGBA(228, 225, 236, 1)` (268) | `RGBA(70, 69, 84, 1)` (740) |

## 9. Upload zones

`GroupContainer` with `BorderStyle: =BorderStyle.Dashed`, `BorderThickness: =1`, a
`Classic/Icon` using `Icon.Publish`, an instruction `Label`, and a `Classic/Button` whose
`OnSelect` is a `Notify(...)` placeholder — a real file picker needs an `AddMediaButton`, which
is **not in the confirmed catalog**. Mark it `# UNVERIFIED` if the user needs true upload.

## 10. Icons — and the mapping problem

**The confirmed enum has six members:** `Icon.Document`, `Icon.View`, `Icon.Person`,
`Icon.Clock`, `Icon.Publish`, `Icon.Trash`.

The retired playbook mapped Material-Symbols names onto `Icon.Home`, `Icon.Table`, `Icon.Money`
and `Icon.Shop`. **None of those four appears in any of the 17 screens.** They may well exist in
Power Apps — the `Icon.*` enum is large — but they are not confirmed here, and this skill's rule
is that unconfirmed means labelled.

So: map to one of the six where the meaning survives; otherwise use the closest of the six, say
which ones you approximated, and mark any member outside the six `# UNVERIFIED`.

| Material-Symbols | Use |
|---|---|
| `description`, `article`, `folder` | `Icon.Document` |
| `visibility`, `search`, `preview` | `Icon.View` |
| `person`, `account_circle`, `group` | `Icon.Person` |
| `schedule`, `history`, `pending` | `Icon.Clock` |
| `cloud_upload`, `upload_file`, `attach_file` | `Icon.Publish` |
| `delete`, `remove`, `close` | `Icon.Trash` |
| `dashboard`, `home`, `payments`, `account_tree` | no confirmed member — approximate and flag |

## 11. Screen skeleton

Derived from `01_Dashboard.pa.yaml`, which compiled. Older written notes carry a skeleton that
positions children with `X`/`Y` — do not use it.

```yaml
Screens:
  Dashboard:
    Properties:
      Fill: =RGBA(252, 248, 255, 1)
      LoadingSpinnerColor: =RGBA(56, 96, 178, 1)
      OnVisible: |
        =If(IsBlank(gblRequestID), Set(gblRequestID, ""));
        If(IsEmpty(colRequests), ClearCollect(colRequests, {RequestId: "", Customer: ""}))
    Children:
      - Dashboard_Root:
          Control: GroupContainer@1.5.0
          Variant: AutoLayout
          Properties:
            DropShadow: =DropShadow.None
            Height: =Parent.Height
            LayoutAlignItems: =LayoutAlignItems.Start
            LayoutDirection: =LayoutDirection.Horizontal
            LayoutGap: =0
            LayoutMinHeight: =700
            LayoutMinWidth: =1000
            Width: =Parent.Width
            X: =0
            Y: =0
          Children:
            - Dashboard_Sidebar:
                Control: GroupContainer@1.5.0
                Variant: AutoLayout
                Properties:
                  DropShadow: =DropShadow.None
                  Fill: =RGBA(255, 255, 255, 1)
                  FillPortions: =0
                  Height: =Parent.Height
                  LayoutDirection: =LayoutDirection.Vertical
                  LayoutGap: =4
                  LayoutMinHeight: =700
                  LayoutMinWidth: =208
                  LayoutOverflowY: =LayoutOverflow.Scroll
                  PaddingBottom: =16
                  PaddingLeft: =16
                  PaddingRight: =16
                  PaddingTop: =16
                  Width: =208
                Children:
                  - Dashboard_Logo:
                      Control: Label@2.5.1
                      Properties:
                        Color: =RGBA(59, 57, 194, 1)
                        FillPortions: =0
                        FontWeight: =FontWeight.Bold
                        Height: =38
                        Size: =13
                        Text: ="Account Closure"
                        VerticalAlign: =VerticalAlign.Middle
                        Width: =176
```
