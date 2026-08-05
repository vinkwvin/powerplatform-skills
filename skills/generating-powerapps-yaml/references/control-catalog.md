# Control catalog

> **Tiers.** `PLATFORM` = a Power Apps fact; violating it makes Studio fail. `HOUSE` = this
> organisation's convention, held in `assets/house-style.yaml` and editable per project.
> `EXAMPLE` = illustration from one real system, never a rule. See `docs/EVIDENCE-TIERS.md`.
>
> Counts below are from 17 screens that compiled: 2,830 controls, 2,847 `Properties` blocks.
> A count proves *this team always did it*, not *it must always be done* — which is exactly
> why the two are labelled differently.

A type not listed here is not *confirmed here*. The Power Apps control set is larger than this
list — `Rectangle`, `Image`, `Toggle`, `Slider` and others exist. They are absent because no
screen in the reference set used them, not because they are forbidden. Mark anything outside the
list `# UNVERIFIED`, paste-test it alone, and add it to `assets/house-style.yaml` once Studio
accepts it. That is how the confirmed set grows.

## Contents
1. The nine types
2. Property sets that every instance carries
3. Optional properties, by type
4. Icon enum
5. Every other enum
6. What is deliberately absent

---

## 1. The nine confirmed types

`PLATFORM` on bare-vs-`Classic/`. `HOUSE` on the version pins and on which types are confirmed.

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

`HOUSE` — a house baseline, so a generated control matches the rest of the codebase. Absence never breaks a paste; it just produces something that looks unlike everything around it.

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

`EXAMPLE` — what one system used, as a guide to what is available and normal.

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

`HOUSE` — the confirmed subset, not the whole enum.

Six members observed, and no others:

`Icon.Document` (22) · `Icon.View` (22) · `Icon.Person` (17) · `Icon.Clock` (8) ·
`Icon.Publish` (7) · `Icon.Trash` (1)

Material-Symbols names (`dashboard`, `cloud_upload`, `expand_more`) have no equivalent. Map to
the nearest member above and say which ones you approximated. `Icon.Error` is **not** confirmed
despite appearing in older written notes — it occurs in zero screens.

## 5. Every other enum

`HOUSE` — the members observed across the 17 screens. Held in `assets/house-style.yaml` under
`enum_members`, and checked by the validator exactly like `Icon`.

| Enum | Members observed | Uses |
|---|---|---|
| `VerticalAlign` | `.Middle` (1369) · `.Top` (1) | 1370 |
| `LayoutDirection` | `.Vertical` (439) · `.Horizontal` (412) | 851 |
| `FontWeight` | `.Semibold` (505) · `.Normal` (179) · `.Bold` (37) | 721 |
| `LayoutAlignItems` | `.Center` (310) · `.Start` (66) · `.Stretch` (20) | 396 |
| `Align` | `.Left` (201) · `.Center` (169) · `.Right` (24) | 394 |
| `LayoutJustifyContent` | `.Center` (89) · `.End` (34) · `.Start` (33) | 156 |
| `AlignInContainer` | `.Center` (30) · `.Start` (16) | 46 |
| `LayoutOverflow` | `.Scroll` (34) | 34 |
| `Layout` | `.Horizontal` (11) · `.Vertical` (5) | 16 |
| `TextMode` | `.MultiLine` (13) | 13 |
| `NotificationType` | `.Information` (4) · `.Success` (3) | 7 |
| `BorderStyle` | `.Dashed` (7) | 7 |
| `TextFormat` | `.Number` (4) | 4 |
| `DropShadow` | `.None` (806) | 806 |

**Read this table the same way as the control list.** Every one of these enums is larger than
what shipped here. `LayoutJustifyContent.SpaceBetween` is a real member and appears in zero of
the 17 screens — an unlisted member is *unconfirmed*, not *invalid*.

The reason to flag it anyway: a member that genuinely does not exist looks identical to one that
does, and nothing reveals the difference until Studio rejects the paste. In an environment with
no CLI, that round trip is the expensive thing this suite exists to avoid. So an unlisted member
gets `# UNVERIFIED`, a one-control test snippet, and a line in `house-style.yaml` once it works.

`DropShadow.Light` is the counter-example, and the reason the check is worth having: plausible,
frequently generated, and it does not exist. It is a hard `ERROR`, not a warning.

## 6. What is deliberately absent

- **No tenth control type.** `Rectangle`, `Image`, `Slider`, `DatePicker`, `Toggle`, `Timer`,
  `HtmlText` do not appear in any of the 17 screens. They may work; none is confirmed. Mark
  `# UNVERIFIED` and offer a one-control test snippet.
- **`Classic/Label` and `Classic/Gallery` are wrong** — both are bare.
- **`DropShadow.Light` does not exist.** Zero occurrences.
- **No `X`/`Y` below the root.** Not an omission, a prohibition.
