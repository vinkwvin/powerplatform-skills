# Confirmed Control Catalog (Power Apps Canvas .pa.yaml)

This is the accumulated ground truth for this project, built from actual Power Apps Studio
"View code" exports and real paste tests — not from guessing at what "should" work by analogy
with web/HTML controls. Treat everything here as the baseline. Anything not listed here is
UNVERIFIED by definition, even if it seems like an obvious counterpart to something that is listed.

Every entry below is tagged with its evidence source:
- **[Studio-tested]** — explicitly confirmed by pasting into Studio and reading back errors/exports
- **[Project file]** — observed working in the user's actual shipped `.pa.yaml` files (see
  `assets/examples/`), which is strong but slightly weaker evidence than a fresh isolated test,
  since project files might contain unnoticed cosmetic errors.

## Control types

| Control | Type string | Evidence | Notes |
|---|---|---|---|
| Label | `Label@2.5.1` | Studio-tested | No prefix. |
| Button | `Classic/Button@2.2.0` | Studio-tested | Has `Classic/` prefix. **All sidebar/nav items must use this**, never Label, even if the mockup shows plain text — nav items need to be clickable/navigable. |
| Free-position container | `GroupContainer@1.5.0` with `Variant: ManualLayout` | Studio-tested | |
| Rectangle / color bar | `Rectangle@2.3.0` | Studio-tested (pastes clean) | Rounded corners (`Radius...`) NOT verified — don't assume it supports them. |
| Image | `Image@2.2.3` | Studio-tested (pastes clean) | Only `Image/X/Y/Width/Height` verified. Other properties unverified. |
| Icon (recolorable) | `Classic/Icon@2.5.0` | Studio-tested | Must use this, not plain `Icon` (current version 0.0.7 does NOT support `Color`). |
| Text input | `Classic/TextInput@2.3.2` | Project file (`example-form-fields.yaml`) | Seen with `BorderColor`, `BorderThickness`, `Color`, `Default`, `HintText`, `Radius*`, `Size`, plus the universal X/Y/Width/Height. |
| Dropdown | `Classic/DropDown@2.3.1` | Project file (`example-form-fields.yaml`) | Seen with `BorderColor`, `BorderThickness`, `ChevronBackground`, `Color`, `Items` (array literal, e.g. `=["option1","option2"]`), `Items.Value`, `Size`. |
| Radio button | `Classic/Radio@2.3.0` | Studio-tested (earlier session) | `Items` accepts array literal syntax: `=["option1", "option2"]`. |

Not yet attempted / no evidence either way: Timer, Slider, DatePicker, Toggle, ComboBox, Gallery,
DataTable, PDF viewer, Camera, Barcode. Do not assume the same property names carry over — propose
a small isolated test snippet before using any of these in a full file.

## Properties confirmed per control

- **Every control tried so far**: `X`, `Y`, `Width`, `Height`, `Fill`, `Visible`
- **Label**: `Text`, `Color`, `Font` (e.g. `=Font.'Segoe UI'`), `Size`, `Align` (e.g. `=Align.Center`), `FontWeight` (e.g. `=FontWeight.Bold`) — `FontWeight` confirmed on Label only, not verified on Button.
- **Classic/Button**: `Text`, `Color`, `Fill`, `BorderColor`, `BorderStyle` (enum, e.g. `=BorderStyle.None`), `BorderThickness`, `FocusedBorderThickness`, `Disabled(Color|BorderColor|Fill)`, `Hover(Color|BorderColor|Fill)`, `Pressed(Color|BorderColor|Fill)`, `Radius(TopLeft|TopRight|BottomLeft|BottomRight)`, `OnSelect`
- **GroupContainer**: `Fill`, `Width`, `Height`, `Visible`, `Radius(TopLeft|TopRight|BottomLeft|BottomRight)`
- **Classic/Icon**: `Icon` (enum, e.g. `=Icon.CheckBadge`), `Color`, `BorderColor`, `Disabled(Color|BorderColor|Fill)`, `Hover(Color|BorderColor|Fill)`, `Pressed(Color|BorderColor|Fill)`, `FocusedBorderThickness`
- **Classic/TextInput**: `BorderColor`, `BorderThickness`, `Color`, `Default`, `HintText`, `Radius(TopLeft|TopRight|BottomLeft|BottomRight)`, `Size`
- **Classic/DropDown**: `BorderColor`, `BorderThickness`, `ChevronBackground`, `Color`, `Items` (array literal), `Items.Value`, `Size`
- **Classic/Radio**: `Items` (array literal)

Important caveat: Studio's "View code" only shows properties that differ from their default value.
If a property isn't in an export, that does NOT prove the control lacks that property — it may
just never have been changed from default. Don't over-conclude from absence.

## Confirmed patterns and gotchas

- **Formulas always start with `=`**, e.g. `=RGBA(0,0,0,1)`, `="some text"`.
- **Use block-style YAML for Properties, never flow-style** (`{X: =0, Fill: =RGBA(...)}`).
  Flow-style breaks because the commas inside `RGBA(...)` get parsed as YAML separators.
  Always write:
  ```yaml
  Properties:
    X: =0
    Fill: =RGBA(10, 20, 30, 1)
  ```
- **Full-file paste only.** You must paste the entire `Screens: -> <screen name> -> Children:`
  structure. Pasting a single bare control snippet is not supported (that shortcut was retired).
- **True nesting requires literal nested `Children:` keys in the YAML.** Dragging one control
  on top of another in the Studio canvas, or in the Tree view, does NOT create real parent-child
  nesting — it just looks that way visually. If a control needs to be inside a container, write it
  nested in the YAML.
- **Name collisions auto-rename silently.** If a screen or control name in your paste already
  exists in the target file, Studio appends `_1`, `_2`, etc. without erroring — so don't assume
  a paste with a name collision failed just because the name changed.
- **Screen scrolling**: works in Responsive layout mode when `Screen.Height` (in the Properties
  block) is set larger than the visible viewport, e.g. `Height: =2232`.
- **Global theme colors**: prefer setting reusable colors once in `App.OnStart`
  (e.g. `Set(varThemeHover, ColorValue("#007FFA"))`) rather than repeating hex/RGBA literals
  across many controls.

## Confirmed hover colors (pulled directly from this project's Tailwind config, not guessed)

| Element | Tailwind class | Hex | Power Fx |
|---|---|---|---|
| Inactive sidebar nav button, hover | `hover:bg-surface-container-high` | `#e6e8f3` | `HoverFill: =RGBA(230, 232, 243, 1)` |
| Document selection card, hover background | `hover:bg-primary/5` | `#005ab6` @ 5% | `HoverFill: =RGBA(0, 90, 182, 0.05)` |
| Document selection card, hover border | `hover:border-primary` | `#005ab6` | `HoverBorderColor: =RGBA(0, 90, 182, 1)` |
| "Customize Document" button, hover | `hover:bg-primary/5` | `#005ab6` @ 5% | `HoverFill: =RGBA(0, 90, 182, 0.05)` |

These are specific to this app's existing HTML mockups. If a new mockup uses different Tailwind
colors, extract the hex directly from that file's Tailwind config / CSS — don't reuse this table
blindly and don't guess.

## Confirmed unachievable — say so plainly, don't fake it

There is no verified Power Fx equivalent for these CSS behaviors. When a mockup relies on one of
these, tell the user directly that pixel-perfect parity isn't possible and suggest the closest
practical alternative (e.g. a thin Rectangle standing in for a one-sided border) rather than
quietly dropping the requirement or inventing a fake property to paper over it.

- `group-hover` (child Label changing color when a parent Button/container is hovered) — Label and
  Button are separate controls that don't share hover state directly. A workaround exists via
  checking `Button.Value`/mouse-position formulas but it's substantially more complex; flag it as
  "possible but not yet confirmed" rather than doing it silently.
- `shadow-xl` (box shadow on hover or otherwise)
- `backdrop-blur`
- CSS transitions / animations
- One-sided borders (e.g. `border-left` only) — approximate with a thin Rectangle instead.
- Whether non-`Font.'Segoe UI'` fonts actually render on the user's machine — unverified either way.

## Error vs warning behavior when pasting

- **Errors** (e.g. `PA2108` unknown property, `PA1001` invalid schema) — **block the entire paste**.
  Nothing from that paste gets applied.
- **Warnings** (e.g. `PA2105`/`PA2106`, usually about an out-of-date or newer-than-current control
  version) — **do not block**. Studio silently substitutes the current version instead.

When the user reports back an error/warning message, sort it into one of these two buckets before
deciding what to fix — don't treat a warning as if it were fatal, and don't wave away a real error.
