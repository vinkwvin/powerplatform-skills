# Control catalog

Measured across 17 screens that compiled in Studio: 2,830 controls, 17 screens.
Counts are the evidence. A type not listed here is not confirmed — mark it `# UNVERIFIED`
and ask.

## Contents
1. The nine types
2. Property sets that every instance carries
3. Optional properties, by type
4. Icon enum
5. What is deliberately absent

---

## 1. The nine types

| Control | Uses | Files | Variant | Bare or Classic |
|---|---|---|---|---|
| `Label@2.5.1` | 1,370 | 17/17 | — | **bare** |
| `GroupContainer@1.5.0` | 887 | 17/17 | `AutoLayout` (887/887) | **bare** |
| `Classic/Button@2.2.0` | 268 | 17/17 | — | Classic |
| `Classic/CheckBox@2.1.0` | 110 | 12/17 | — | Classic |
| `Classic/Icon@2.5.0` | 77 | 17/17 | — | Classic |
| `Classic/TextInput@2.3.2` | 65 | 13/17 | — | Classic |
| `Gallery@2.15.0` | 36 | 17/17 | `Vertical` (36/36) | **bare** |
| `Classic/Radio@2.3.0` | 16 | 8/17 | — | Classic |
| `Classic/DropDown@2.3.1` | **1** | 1/17 | — | Classic |

**Rule of thumb:** `Label`, `Gallery` and `GroupContainer` are bare. Everything interactive
takes `Classic/`. A bare interactive control resolves to the modern variant, which rejects
`Color`, `Fill` and `Size`.

`Classic/DropDown` has a sample size of one. Treat DropDown-specific detail as `low`
confidence and verify against Studio if the screen depends on it.

## 2. Property sets that every instance carries

Present on **every** instance. Absence was never observed, so treat them as required.

### `Label@2.5.1` — six properties, 1,370/1,370 each
`Color` · `FillPortions` · `Height` · `Size` · `Text` · `VerticalAlign`

`VerticalAlign` is `=VerticalAlign.Middle` on 1,369 of 1,370 (one `.Top`).
`Width` is present on 1,164 of 1,370 — the one member of the set that is genuinely optional.

### `Classic/Button@2.2.0` — fourteen properties, 268/268 each
`Align` · `Color` · `Fill` · `FocusedBorderThickness` · `FontWeight` · `Height` ·
`HoverColor` · `HoverFill` · `OnSelect` · `PressedColor` · `PressedFill` · `Size` ·
`Text` · `Width`

### `GroupContainer@1.5.0` — 887/887 each
`Height` · `LayoutMinHeight`

Plus `Variant: AutoLayout` on 887/887.

### `Gallery@2.15.0` — 36/36 each
`Height` · `Items` · `LayoutMinHeight` · `TemplatePadding` · `TemplateSize` · `Width`

### `Classic/Icon@2.5.0` — 77/77 each
`Color` · `Height` · `Icon` · `Width`

### `Classic/TextInput@2.3.2` — 65/65 each
`BorderColor` · `BorderThickness` · `Default` · `Fill` · `FocusedBorderColor` ·
`FocusedBorderThickness` · `Height` · `HintText` · `HoverBorderColor` · `HoverFill` ·
`Size` · `Width`

### `Classic/Radio@2.3.0` — 16/16 each
`Default` · `FocusedBorderColor` · `FocusedBorderThickness` · `Height` · `Items` ·
`Items.Value` · `Layout` · `RadioSize` · `Size` · `Width`

### Screen — 17/17 each
`Fill` · `LoadingSpinnerColor` · `OnVisible`. Never a fourth.

## 3. Optional properties, by type

| Control | Optional | Uses |
|---|---|---|
| `Label` | `FontWeight` | 453 |
| | `BorderColor`, `BorderThickness`, `Fill`, `PaddingLeft`, `PaddingRight` | 160 each, 14/17 files |
| | `Align` | 126 |
| `Classic/Button` | `BorderThickness` | 248 |
| | `BorderColor` | 61 |
| `GroupContainer` | `LayoutDirection` | 851 |
| | `FillPortions` | 834 |
| | `DropShadow` | 806 — 81 containers omit it deliberately |
| | `LayoutGap` | 697 |
| | `Width` | 554 |
| | `PaddingLeft`, `PaddingRight` | 450 each |
| | `LayoutAlignItems` | 396 |
| | `RadiusTopLeft`, `RadiusTopRight`, `RadiusBottomLeft`, `RadiusBottomRight` | 349 each |
| | `Fill` | 331 |
| | `PaddingTop`, `PaddingBottom` | 302 each |
| | `BorderColor`, `BorderThickness` | 169 each |
| | `LayoutJustifyContent` | 156 |
| | `LayoutMinWidth` | 94 |
| | `AlignInContainer` | 46 |
| | `LayoutOverflowY` | 34 |
| | `X`, `Y` | **17 each — root container only** |
| | `BorderStyle` | 7, only `=BorderStyle.Dashed` |
| | `Visible` | 2 |
| `Classic/CheckBox` | `Height` | 93 |
| | `Default` | 18 |
| | `OnCheck` | 17 |
| | `OnUncheck` | 12 |
| `Classic/TextInput` | `Mode` | 13, only `=TextMode.MultiLine` |
| | `Visible` | 9 |
| | `Format` | 4 |
| | `OnChange` | 1 |
| `Gallery` | `Visible` | 14 |
| | `BorderColor`, `BorderThickness`, `Fill` | 8 each |
| `Classic/Radio` | `OnChange` | 5 |
| `Classic/Icon` | `OnSelect` | 1 |

### Interactive-state values

| Property | Observed values |
|---|---|
| `FocusedBorderThickness` | `=1` (289 controls), `=2` (61 buttons). **Never 0.** |
| `BorderThickness` | `=0` or `=1` on buttons; `=1` elsewhere; `=2` on 7 containers |
| `HoverFill` | a light tint — `RGBA(234, 230, 242, 1)` on 233 of 268 buttons |
| `PressedFill` | a slightly darker tint — `RGBA(228, 225, 236, 1)` on 238 |
| `HoverColor` | usually unchanged body text — `RGBA(27, 27, 35, 1)` on 217 |
| `RadioSize` | `=18` (13), `=16` (3) |
| `TemplatePadding` | `=0` (27), `=6` (7), `=4` (2) |
| `AlignInContainer` | `.Center` (30), `.Start` (16) |

Hover and pressed states lighten the *fill* and leave the text colour alone. A dark hover fill
or a thick focus ring departs from all 17 screens.

## 4. Icon enum

Six members observed, and no others:

`Icon.Document` (22) · `Icon.View` (22) · `Icon.Person` (17) · `Icon.Clock` (8) ·
`Icon.Publish` (7) · `Icon.Trash` (1)

Material-Symbols names (`dashboard`, `cloud_upload`, `expand_more`) have no equivalent. Map to
the nearest member above and say which ones you approximated. `Icon.Error` is **not** confirmed
despite appearing in older written notes — it occurs in zero screens.

## 5. What is deliberately absent

- **No tenth control type.** `Rectangle`, `Image`, `Slider`, `DatePicker`, `Toggle`, `Timer`,
  `HtmlText` do not appear in any of the 17 screens. They may work; none is confirmed. Mark
  `# UNVERIFIED` and offer a one-control test snippet.
- **`Classic/Label` and `Classic/Gallery` are wrong** — both are bare.
- **`DropShadow.Light` does not exist.** Zero occurrences.
- **No `X`/`Y` below the root.** Not an omission, a prohibition.
