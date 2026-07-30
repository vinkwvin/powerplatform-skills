# Power Apps Canvas YAML — environment conventions

The build contract for pasteable `pa.yaml` in this environment. Apply all of it by default.
These conventions are **empirically verified against Power Apps Studio**, which matters because the
official `pa.schema.yaml` alone is insufficient — schema-valid YAML still fails to paste if the
control prefixes/versions are wrong.

## Contents
1. File format & schema shape
2. Control types (versions + bare-vs-Classic) — the #1 error source
3. Drop shadow
4. Classic control quirks
5. Layout & scrolling
6. Sizing (~0.8 scale)
7. YAML safety (block scalars)
8. Behavior placeholders
9. Screen skeleton (copy-paste starting point)
10. Gallery structure (for tables/lists)

---

## 1. File format & schema shape

- Use the full **`Screens:`** source-code schema, not a bare control list.
- Screen name may be **descriptive with spaces** (e.g. `Sales - Create New Request:`).
- Every screen carries `Properties:` with `LoadingSpinnerColor: =RGBA(56, 96, 178, 1)`, then `Children:`.
- **Properties are sorted alphabetically** inside every `Properties:` block.
- Indent with **spaces only** — a tab anywhere in leading whitespace breaks the paste.

Nesting: `Screens:` → screen name → `Properties:` / `Children:` → each child is `- ControlName:` with
`Control:`, optional `Variant:`, `Properties:`, and (for containers/galleries) nested `Children:`.

## 2. Control types (this is the part that causes most errors)

| Purpose | Use this | NOT this |
|---|---|---|
| Text | `Label@2.5.1` | ~~`Classic/Label`~~ (rejected) |
| List / table | `Gallery@2.15.0` (`Variant: Vertical`) | ~~`Classic/Gallery`~~ (rejected) |
| Button | `Classic/Button@2.2.0` | bare `Button` (→ modern, rejects `Color`/`Fill`/`Size`) |
| Text box | `Classic/TextInput@2.3.2` | bare `TextInput` (→ modern) |
| Dropdown | `Classic/DropDown@2.3.1` | bare `DropDown` (→ modern) |
| Icon | `Classic/Icon@2.5.0` | bare `Icon` (→ modern) |
| Radio | `Classic/Radio@2.3.0` | bare `Radio` (→ modern) |
| Container | `GroupContainer@1.5.0` + `Variant: AutoLayout` | — |

**Rule of thumb: `Label` and `Gallery` are bare; everything else interactive is `Classic/…`.**
Use these exact version strings — off-book versions may still paste but aren't guaranteed here, so
the validator warns on any version not in this table.

## 3. Drop shadow

- `DropShadow: =DropShadow.None` on all **flat / structural / transparent** containers (page root,
  sidebar, top bar, table rows, cells, badges, field rows).
- **Omit `DropShadow` entirely** on elevated white surfaces (stat cards, form card, recent-requests
  panel) — the default already gives the right light shadow. **Never write `DropShadow.Light`.**

## 4. Classic control quirks

- **DropDown** and **Radio** need **both** `Items: =[...]` **and** `Items.Value: =Value`. Missing the
  `.Value` companion is a silent failure.
- **Radio**: also `Layout: =Layout.Horizontal`, `RadioSize: =30`, and a `Default: ="Yes"`. To nudge a
  tall radio into a row, use its own `Height` + `PaddingTop`, or `AlignInContainer: =AlignInContainer.Start`.
- **TextInput**: `Default` (the value), `HintText` (placeholder), `BorderColor`, `BorderThickness`,
  `Fill`, `Color`, `Size`. Multi-line (from `<textarea>`): `Mode: =TextMode.MultiLine`. Numeric (from
  `<input type=number>`): `Format: =TextFormat.Number`.
- **Button**: `Text`, `Fill`, `Color`, `Size`, `FontWeight`, `Align`, `HoverFill`, `PressedFill`,
  `BorderThickness`, `OnSelect`. An active nav item = indigo fill `RGBA(238,242,255,1)` + indigo text
  + `FontWeight: =FontWeight.Semibold`.
- **GroupContainer** supports `BorderColor`, `BorderThickness`, `BorderStyle: =BorderStyle.Dashed`
  (used for upload drop zones), and the AutoLayout properties below.
- **Icon** (`Classic/Icon`): `Icon: =Icon.Person`. Only the built-in `Icon.*` enum exists — verified
  in use: `Icon.Person`, `Icon.Error`, `Icon.Publish`. Map arbitrary Material-Symbols names to the
  nearest enum (see `html-to-powerapps.md`).

### AutoLayout properties on `GroupContainer` (`Variant: AutoLayout`)
- `LayoutDirection: =LayoutDirection.Horizontal | .Vertical`
- `LayoutGap: =16` (spacing between children — maps from CSS `gap`)
- `LayoutJustifyContent`, `LayoutAlignItems: =LayoutAlignItems.Center`
- `LayoutOverflowY: =LayoutOverflow.Scroll` for scrollable regions
- Per-child sizing: `LayoutMinHeight`, `LayoutMinWidth`, `FillPortions`, `AlignInContainer`

## 5. Layout & scrolling

- Long pages: set `LayoutOverflowY: =LayoutOverflow.Scroll` on **both** the content container **and**
  the inner form card.
- Auto-layout multi-row blocks: give the wrapping container an explicit **`Height`** and give tall
  columns **`LayoutMinHeight`** (and `LayoutMinWidth` where needed) — don't rely on `FillPortions`
  alone or rows collapse to zero height.
- Horizontal rows: `LayoutAlignItems: =LayoutAlignItems.Center`; give inputs/buttons a fixed `Height`
  + `AlignInContainer: =AlignInContainer.Center` so they don't stretch to fill.
- Every card and gallery must carry an explicit `Height` plus `LayoutMinHeight` so nothing collapses.
- Table columns: keep the header row and the gallery template on matching widths (fixed `Width` or
  matching `FillPortions`) so cells line up.

## 6. Sizing (~0.8 of the original mockup, tuned for a large monitor)

Design tokens usually carry the source dimensions; scale layout dimensions by ~0.8 (e.g. a
`260px` sidebar → `Width: 208`). Concrete targets:

- Sidebar `Width: 208`; nav buttons `Height: 35`, `Size: 11`.
- Top bar `Height: 58`; body text `Size: 11`; section headers `Size: 12`; column headers `Size: 9`;
  big stat numbers `Size: 32`; form title `Size: 18`.
- Inputs `Height: 28–32`; footer buttons `Height: 38`; gallery `TemplateSize: 51`.
- Font floor ≈ 9 so nothing becomes unreadable.

(Font sizes aren't a strict ×0.8 of the token px — they're tuned. Layout dimensions scale; text sizes
follow the targets above.)

## 7. YAML safety (block scalars)

Any property value containing **`: ` (colon-space)** or **`#`** must be a block scalar (`|`),
otherwise YAML mis-reads it (a colon-space looks like a nested mapping; a `#` starts a comment) and
the paste breaks:

```yaml
Text: |
  ="Ineligible: Ongoing litigation prevents account closure."
```

Multi-line formulas (`Table(...)`, `Switch(...)`, `If(...)` spanning lines) also use `|`:

```yaml
Fill: |
  =Switch(ThisItem.Status,
    "Pending Risk", RGBA(170, 237, 255, 1),
    "Completed", RGBA(204, 239, 140, 1),
    "Rejected", RGBA(255, 218, 214, 1),
    RGBA(228, 225, 236, 1))
```

## 8. Behavior placeholders

Use `=Notify("…", NotificationType.Information)` (or `.Success`) for buttons whose target
screen/flow/data source isn't built yet — this avoids unknown-screen/unknown-name compile errors.
Swap for `Navigate(...)` / `Patch(...)` / `SubmitForm(...)` once the target exists.

## 9. Screen skeleton (copy-paste starting point)

A minimal valid screen with the shell + one card. Alphabetized properties, bare `Label`,
`Classic/` button, `GroupContainer` shells, `LoadingSpinnerColor` present.

```yaml
Screens:
  Dashboard:
    Properties:
      Fill: =RGBA(252, 248, 255, 1)
      LoadingSpinnerColor: =RGBA(56, 96, 178, 1)
    Children:
      - Sidebar:
          Control: GroupContainer@1.5.0
          Variant: AutoLayout
          Properties:
            DropShadow: =DropShadow.None
            Fill: =RGBA(255, 255, 255, 1)
            Height: =Parent.Height
            LayoutDirection: =LayoutDirection.Vertical
            LayoutGap: =8
            PaddingBottom: =24
            PaddingLeft: =16
            PaddingRight: =16
            PaddingTop: =24
            Width: =208
            X: =0
            Y: =0
          Children:
            - NavDashboard:
                Control: Classic/Button@2.2.0
                Properties:
                  Align: =Align.Left
                  Fill: =RGBA(238, 242, 255, 1)
                  FontWeight: =FontWeight.Semibold
                  Height: =35
                  OnSelect: =Notify("Dashboard", NotificationType.Information)
                  Size: =11
                  Text: ="Dashboard"
                  Width: =176
                  X: =16
                  Y: =64
      - ContentArea:
          Control: GroupContainer@1.5.0
          Variant: AutoLayout
          Properties:
            DropShadow: =DropShadow.None
            Height: =Parent.Height
            LayoutDirection: =LayoutDirection.Vertical
            LayoutGap: =24
            LayoutOverflowY: =LayoutOverflow.Scroll
            PaddingBottom: =32
            PaddingLeft: =32
            PaddingRight: =32
            PaddingTop: =32
            Width: =Parent.Width - 208
            X: =208
            Y: =0
          Children:
            - PendingCard:
                Control: GroupContainer@1.5.0
                Variant: AutoLayout
                Properties:
                  Fill: =RGBA(255, 255, 255, 1)
                  Height: =110
                  LayoutDirection: =LayoutDirection.Vertical
                  LayoutGap: =8
                  LayoutMinHeight: =110
                  PaddingBottom: =24
                  PaddingLeft: =24
                  PaddingRight: =24
                  PaddingTop: =24
                Children:
                  - PendingLabel:
                      Control: Label@2.5.1
                      Properties:
                        Color: =RGBA(70, 69, 84, 1)
                        Size: =9
                        Text: ="PENDING TASKS"
                  - PendingValue:
                      Control: Label@2.5.1
                      Properties:
                        Color: =RGBA(186, 26, 26, 1)
                        Size: =32
                        Text: ="5"
```

## 10. Gallery structure (tables / lists)

Tables become a `Gallery@2.15.0` (`Variant: Vertical`). The header row is separate Labels above the
gallery; the gallery template holds one row of controls referencing `ThisItem.*`. Keep header and
template column widths identical.

```yaml
- RequestsGallery:
    Control: Gallery@2.15.0
    Variant: Vertical
    Properties:
      Height: =320
      Items: =colRequests            # a collection, or a data source
      LayoutMinHeight: =320
      TemplatePadding: =0
      TemplateSize: =51
      Width: =900
      X: =32
      Y: =120
    Children:
      - CellRequestId:
          Control: Label@2.5.1
          Properties:
            Size: =11
            Text: =ThisItem.RequestId
            Width: =160
            X: =0
      - CellStatusBadge:
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
                "Rejected", RGBA(255, 218, 214, 1),
                RGBA(228, 225, 236, 1))
            Text: =ThisItem.Status
            Width: =140
            X: =520
      - CellViewButton:
          Control: Classic/Button@2.2.0
          Properties:
            Fill: =RGBA(255, 255, 255, 1)
            OnSelect: =Notify("View " & ThisItem.RequestId, NotificationType.Information)
            Text: ="View"
            Width: =80
            X: =820
```
