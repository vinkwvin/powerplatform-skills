# 01 — Observed conventions

Produced by Session 1. Every number here is measured by `scripts/harvest_yaml.py` over
`/source-artifacts/yaml/` — 17 files, 17 screens, 2,830 controls, 2,847 `Properties` blocks.
Nothing is inferred.

**Confidence scale:** `high` = holds across all 17 files with no exception ·
`medium` = holds in most, with counted exceptions · `low` = varies.

## Contents

1. Schema shape
2. Control catalog
3. Mandatory property sets
4. Property ordering
5. Sizing
6. Layout and positioning
7. Interactive state styling
8. Block scalars
9. Colour
10. Measured but not resolvable here

---

## 1. Schema shape

| Rule | Evidence | Confidence |
|---|---|---|
| Top-level key is `Screens:`, one screen per file | 17/17 files, 17 screens | `high` |
| Screen carries exactly three properties: `Fill`, `LoadingSpinnerColor`, `OnVisible` | 17/17 screens, no screen has a fourth | `high` |
| `LoadingSpinnerColor` is always `=RGBA(56, 96, 178, 1)` | 17/17 screens; that value appears 17 times total | `high` |
| Screen `OnVisible` initializes global state with `If(IsBlank(...), Set(...))` / `If(IsEmpty(...), ClearCollect(...))` guards | 17/17 screens | `high` |
| Nesting: `Screens:` → screen → `Properties:`/`Children:` → `- Name:` with `Control:`, optional `Variant:`, `Properties:`, optional `Children:` | 2,830 controls | `high` |
| Spaces only, no tab in leading whitespace | 0 tabs across 37,507 lines | `high` |
| No duplicate keys within a `Properties` block | 0 found | `high` |

## 2. Control catalog

Nine control types, exact version strings, nothing else. This is the complete confirmed set.

| Control | Count | Files | Variant | Confidence |
|---|---|---|---|---|
| `Label@2.5.1` | 1,370 | 17/17 | — | `high` |
| `GroupContainer@1.5.0` | 887 | 17/17 | `AutoLayout` on 887/887 | `high` |
| `Classic/Button@2.2.0` | 268 | 17/17 | — | `high` |
| `Classic/CheckBox@2.1.0` | 110 | 12/17 | — | `medium` |
| `Classic/Icon@2.5.0` | 77 | 17/17 | — | `high` |
| `Classic/TextInput@2.3.2` | 65 | 13/17 | — | `medium` |
| `Gallery@2.15.0` | 36 | 17/17 | `Vertical` on 36/36 | `high` |
| `Classic/Radio@2.3.0` | 16 | 8/17 | — | `low` |
| `Classic/DropDown@2.3.1` | **1** | 1/17 | — | `low` |

`Label` and `Gallery` are bare; every interactive control is `Classic/`; `GroupContainer` is bare.
Confirmed, no exception in 2,830 controls — `high`.

`Icon` values in use: `Icon.Document` (22), `Icon.View` (22), `Icon.Person` (17),
`Icon.Clock` (8), `Icon.Publish` (7), `Icon.Trash` (1). Six enum members total.

## 3. Mandatory property sets

Properties present on **every single instance** of a control type. Absence is never observed,
so these read as required rather than conventional.

| Control | Always present | Count |
|---|---|---|
| `Label@2.5.1` | `Color`, `FillPortions`, `Height`, `Size`, `Text`, `VerticalAlign` | 1,370/1,370 each |
| `Classic/Button@2.2.0` | `Align`, `Color`, `Fill`, `FocusedBorderThickness`, `FontWeight`, `Height`, `HoverColor`, `HoverFill`, `OnSelect`, `PressedColor`, `PressedFill`, `Size`, `Text`, `Width` | 268/268 each |
| `GroupContainer@1.5.0` | `Height`, `LayoutMinHeight` | 887/887 each |
| `Gallery@2.15.0` | `Height`, `Items`, `LayoutMinHeight`, `TemplatePadding`, `TemplateSize`, `Width` | 36/36 each |
| `Classic/Icon@2.5.0` | `Color`, `Height`, `Icon`, `Width` | 77/77 each |
| `Classic/TextInput@2.3.2` | `BorderColor`, `BorderThickness`, `Default`, `Fill`, `FocusedBorderColor`, `FocusedBorderThickness`, `Height`, `HintText`, `HoverBorderColor`, `HoverFill`, `Size`, `Width` | 65/65 each |
| `Classic/Radio@2.3.0` | `Default`, `FocusedBorderColor`, `FocusedBorderThickness`, `Height`, `Items`, `Items.Value`, `Layout`, `RadioSize`, `Size`, `Width` | 16/16 each |

All `high` except Radio (`low`, n=16 in 8 files) and TextInput (`medium`, 13/17 files).

`Label` `Width` is present 1,164/1,370 — the one member of the Label set that is optional.
`Confidence: medium`.

`Classic/DropDown@2.3.1` has 17 properties on its single instance, including both `Items` and
`Items.Value`. **n=1 — `low` confidence on anything DropDown-specific.**

`Items` + `Items.Value` together: 16/16 Radio, 1/1 DropDown. The rule holds wherever observed,
but the sample is one control type at n=16 and another at n=1.

## 4. Property ordering

| Rule | Evidence | Confidence |
|---|---|---|
| Properties are sorted alphabetically (case-insensitive) within every `Properties` block | **2,847/2,847 blocks, zero violations** | `high` |

The single strongest signal in the artifact set.

## 5. Sizing

| Rule | Evidence | Confidence |
|---|---|---|
| `Size` draws from a closed set of 11 values: 11 (643), 9 (487), 10 (264), 8 (231), 12 (82), 13 (81), 16 (17), 20 (16), 15 (4), 26 (3), 22 (1) | 1,829 uses | `high` |
| `Size` floor is **8**, ceiling **26** | 1,829 uses | `high` |
| `FillPortions` draws from 7 values, overwhelmingly `=0` | 2,204 uses: 0 (1,665), 1 (342), 5 (54), 3 (46), 4 (45), 7 (38), 6 (14) | `high` |
| `TemplateSize` varies per gallery | 36 uses, 7 values: 40 (14), 34 (8), 52 (5), 42 (4), 48 (3), 58 (1), 54 (1) | `medium` |
| `Height` is undisciplined — 111 distinct values, range 10–1540 | 2,813 uses; top: 18 (377), 34 (245), 32 (237), 14 (232), 22 (226), 38 (211), 20 (168) | `low` |
| Sidebar `Width: =208`, exactly once per screen | 17 uses | `high` |

## 6. Layout and positioning

| Rule | Evidence | Confidence |
|---|---|---|
| **`X`/`Y` appear only on the depth-1 root container, and nowhere else** | `GroupContainer` X 17, Y 17 (once per screen); **no other control type declares X or Y at all** | `high` |
| Positioning is done by AutoLayout, not coordinates | 887/887 containers are `Variant: AutoLayout` | `high` |
| Width inset idiom `=Parent.Width - N` | ~1,591 of 2,291 `Width` uses; N ∈ {10 (475), 40 (337), 56 (240), 8 (181), 24 (173), 20 (136), 32 (30), 12 (8), 80 (11)} | `high` |
| Every container carries **both** `Height` and `LayoutMinHeight` | 887/887 | `high` |
| Every gallery carries both `Height` and `LayoutMinHeight` | 36/36 | `high` |
| `LayoutOverflowY` is always `=LayoutOverflow.Scroll`, always on `GroupContainer`, always at **nesting depth 2**, exactly **twice per screen** | 34 uses = 2 × 17 | `high` |
| Nesting runs 6–8 levels deep | max depth: 6 in 5 files, 7 in 7 files, 8 in 5 files; controls by depth: d1 17, d2 34, d3 370, d4 491, d5 517, d6 1,172, d7 156, d8 73 | `high` |
| `BorderStyle` appears only as `=BorderStyle.Dashed` | 7 uses, 6/17 files | `low` |
| `VerticalAlign` on Label is `.Middle` | 1,369/1,370; one `.Top` | `high` |

## 7. Interactive state styling

| Rule | Evidence | Confidence |
|---|---|---|
| `FocusedBorderThickness` is **never 0** — always 1, occasionally 2 | Button: 1 (207), 2 (61). TextInput 1 (65). Radio 1 (16). DropDown 1 (1) | `high` |
| `HoverFill` is a *light tint*, not a dark fill | Button: `RGBA(234,230,242,1)` (233), `RGBA(48,46,175,1)` (20), `RGBA(255,240,238,1)` (10), `RGBA(238,242,255,1)` (5) | `high` |
| `PressedFill` is a slightly darker tint of the same hue | Button: `RGBA(228,225,236,1)` (238), `RGBA(40,38,150,1)` (20), `RGBA(255,224,221,1)` (10) | `high` |
| `HoverColor` usually keeps the dark body text colour — only the fill changes | Button: `RGBA(27,27,35,1)` (217) of 268 | `high` |
| `BorderThickness` is 0 or 1 on buttons, 1 elsewhere | Button: 0 (187), 1 (61); TextInput 1 (65); Label 1 (160); Gallery 1 (8); GroupContainer 1 (162), 2 (7) | `high` |
| `DropShadow` is `=DropShadow.None` where present; **`DropShadow.Light` never appears** | 806/887 containers carry it; 81 omit it entirely; 0 occurrences of `.Light` | `high` |

## 8. Block scalars

| Rule | Evidence | Confidence |
|---|---|---|
| `\|` is used **only** where the value genuinely requires it — never as a style choice | 119 block scalars, **0 with no forcing character** | `high` |
| Forcing reasons: `: ` colon-space (69), colon-space + multiline (46), multiline alone (2), ` #` (2) | 119 total | `high` |
| Only six properties ever use `\|` | `OnSelect` (52), `OnVisible` (17), `OnCheck` (17), `Text` (14), `OnUncheck` (12), `OnChange` (7) | `high` |

**Measurement caveat.** `harvest_yaml.py` also reports "trailing whitespace" as a forcing reason
on every block scalar. That is an artifact: YAML block scalars retain a trailing newline by
construction, so the check always fires. It was excluded from the counts above. The three
real forcing conditions are colon-space, embedded newline, and ` #`.

## 9. Colour

31 distinct `RGBA(...)` values, 4,391 uses. Concentrated: the top 9 account for 3,914.

| Value | Uses | Apparent role |
|---|---|---|
| `RGBA(27,27,35,1)` | 953 | body text / on-surface |
| `RGBA(70,69,84,1)` | 740 | secondary text |
| `RGBA(255,255,255,1)` | 565 | surface |
| `RGBA(199,196,215,1)` | 460 | border / outline |
| `RGBA(59,57,194,1)` | 334 | primary (indigo) |
| `RGBA(228,225,236,1)` | 268 | pressed fill / neutral chip |
| `RGBA(234,230,242,1)` | 233 | hover fill |
| `RGBA(245,242,254,1)` | 189 | tinted surface |
| `RGBA(120,118,134,1)` | 172 | tertiary text |

`RGBA(56,96,178,1)` appears exactly 17 times — the per-screen `LoadingSpinnerColor` and nothing
else. `high` confidence that it is reserved for that property.

Per D3, the palette itself belongs in Project knowledge, not inlined in a SKILL.md. Recorded
here as measurement.

## 10. Measured but not resolvable here

- **"Container height must fully contain its children"** (a `times: 3` claim in
  `ledger/07-buildchat-raw.md`) cannot be verified by static measurement — it needs a layout
  engine. What *is* measurable is the mechanism used instead: 887/887 containers are
  `AutoLayout` and 887/887 carry `LayoutMinHeight` alongside `Height`. That is consistent with
  the rule being satisfied structurally rather than by arithmetic.
- **`FillPortions` restricted to `Label`/`GroupContainer`** (a `times: 2` claim in the harvest):
  `FillPortions` appears 1,370 times on `Label` and 834 on `GroupContainer` — and **on no other
  control type**. Confirmed at 2,204/2,204. `high`.
