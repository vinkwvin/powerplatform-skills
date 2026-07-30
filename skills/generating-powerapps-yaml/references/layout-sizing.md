# Layout and sizing

Measured across 17 screens that compiled in Studio.

## Contents
1. AutoLayout, not coordinates
2. The inset idiom
3. Containment
4. Scrolling
5. Nesting depth
6. Sizing values
7. Colour

---

## 1. AutoLayout, not coordinates

Every `GroupContainer@1.5.0` is `Variant: AutoLayout` — 887/887.

`X` and `Y` appear **17 times each**: once per screen, on the depth-1 root container, always
`=0`. Across the other 2,813 controls — 1,370 Labels, 268 Buttons, 36 Galleries, everything
else — neither appears once.

```yaml
- Screen_Root:
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
      X: =0          # only here
      Y: =0          # only here
```

Older written notes and the example files in the retired `html-to-yaml` skill position children
with `X`/`Y`. Those examples needed fixing before they compiled. Do not copy that shape.

Layout comes from: `LayoutDirection` · `LayoutGap` · `LayoutAlignItems` ·
`LayoutJustifyContent` · `FillPortions` · `AlignInContainer` · the `Padding*` family.

## 2. The inset idiom

To inset a child from its container, subtract from the parent width:

`=Parent.Width - N`, with N ∈ {8, 10, 12, 20, 24, 32, 40, 56, 80}

Roughly 1,591 of 2,291 `Width` values take this form. Distribution: `- 10` (475), `- 40` (337),
`- 56` (240), `- 8` (181), `- 24` (173), `- 20` (136), `- 32` (30), `- 80` (11), `- 12` (8).

Bare `=Parent.Width` appears 147 times, `=Parent.TemplateWidth` 36 (gallery templates).

This is how "give the control real padding so adjacent borders do not overlap" is expressed.

## 3. Containment

**Every container carries both `Height` and `LayoutMinHeight`** — 887/887. Same for galleries:
`Height` and `LayoutMinHeight` on 36/36.

`LayoutMinHeight` is the floor that stops a row collapsing to zero. Common values: `=62` (75),
`=34` (74), `=86` (72), `=700` (51, root containers), `=30` (41), `=40` (39).

`FillPortions` is `=0` on 1,665 of 2,204 uses — it is mostly *disabling* proportional sizing,
not driving it. `=1` (342) is the only common alternative; 5, 4, 3, 7, 6 appear rarely.
`FillPortions` occurs on `Label` (1,370) and `GroupContainer` (834) and **on no other type**.

Do not rely on `FillPortions` alone for multi-row blocks. Give the container an explicit
`Height` plus `LayoutMinHeight`.

## 4. Scrolling

`LayoutOverflowY` appears **34 times = exactly twice per screen**, always
`=LayoutOverflow.Scroll`, always on `GroupContainer`, always at **nesting depth 2**.

Two scroll containers per screen: the content region and the card inside it. One is not enough.

## 5. Nesting depth

| Depth | Controls |
|---|---|
| 1 | 17 (the root, one per screen) |
| 2 | 34 |
| 3 | 370 |
| 4 | 491 |
| 5 | 517 |
| 6 | **1,172** |
| 7 | 156 |
| 8 | 73 |

Max depth per file: 6 in five files, 7 in seven, 8 in five. The bulk of controls sit at depth 6.

A generator that flattens the tree to two or three levels will not resemble the working set.
Real screens nest: root → region → card → section → row → control.

## 6. Sizing values

### `Size` is a closed set of eleven values

| Value | Uses | Typical role |
|---|---|---|
| 11 | 643 | body text |
| 9 | 487 | column headers, captions |
| 10 | 264 | secondary body |
| 8 | 231 | smallest — the floor |
| 12 | 82 | section headers |
| 13 | 81 | |
| 16 | 17 | |
| 20 | 16 | |
| 15 | 4 | |
| 26 | 3 | largest — the ceiling |
| 22 | 1 | |

**Floor 8, ceiling 26.** Older written notes prescribe `Size: 32` for stat numerals and
`Size: 18` for form titles; neither value occurs in any screen. For a large numeral use 26, 22
or 20.

### `Height` is not disciplined

111 distinct values, range 10–1540. Most common: 18 (377), 34 (245), 32 (237), 14 (232),
22 (226), 38 (211), 20 (168). `=Parent.Height` 132, `=Parent.TemplateHeight` 36.

Measured anchors that differ from older notes: nav buttons are `=34` (not 35); top bar is `=60`
or `=62` (not 58); inputs are `=32` or `=30`.

### `TemplateSize`

Per gallery: `=40` (14), `=34` (8), `=52` (5), `=42` (4), `=48` (3), `=58` (1), `=54` (1).
`=51` does not occur.

### `Width`

Sidebar is `=208`, once per screen. Other fixed widths: 176 (204 uses), 90, 100, 240, 200, 220.

## 7. Colour

31 distinct `RGBA(...)` values, 4,391 uses. Nine cover 89%.

| Value | Uses | Apparent role |
|---|---|---|
| `RGBA(27, 27, 35, 1)` | 953 | body text |
| `RGBA(70, 69, 84, 1)` | 740 | secondary text |
| `RGBA(255, 255, 255, 1)` | 565 | surface |
| `RGBA(199, 196, 215, 1)` | 460 | border |
| `RGBA(59, 57, 194, 1)` | 334 | primary indigo |
| `RGBA(228, 225, 236, 1)` | 268 | pressed fill, neutral chip |
| `RGBA(234, 230, 242, 1)` | 233 | hover fill |
| `RGBA(245, 242, 254, 1)` | 189 | tinted surface |
| `RGBA(120, 118, 134, 1)` | 172 | tertiary text |

Status colours: `RGBA(0, 104, 121, 1)` (75) · `RGBA(186, 26, 26, 1)` (74, error) ·
`RGBA(170, 237, 255, 1)` (50) · `RGBA(60, 87, 1, 1)` (25) · `RGBA(204, 239, 140, 1)` (19).

`RGBA(56, 96, 178, 1)` occurs exactly 17 times and only as `LoadingSpinnerColor`. Treat it as
reserved.

Screen `Fill` is `RGBA(252, 248, 255, 1)`, 17 uses.

**The palette itself belongs in Project knowledge**, not in this skill. It is recorded here as
measurement, so a generated screen can be checked against what shipped. If a project supplies
its own tokens, use those and re-derive every value from the token file each run.
