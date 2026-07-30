---
name: generating-powerapps-yaml
description: >-
  Generates pasteable Power Apps Canvas source YAML (.pa.yaml) that compiles in Studio on the
  first paste. Use whenever the user wants a canvas screen produced, extended, or fixed — from
  an HTML/CSS/Tailwind mockup, a Stitch or Figma export, a UI screenshot, a solution-spec.yaml,
  or a written description. Triggers: "make this a Power App", "generate pa.yaml", "Power Apps
  YAML", "convert my HTML to a canvas app", "port this screen to Power Apps", "add a screen",
  "paste code into Studio", or any Studio paste failure (PA1001, PA2108, "invalid control",
  "property not recognized"). Do NOT use for SharePoint lists or columns —
  use building-sharepoint-lists. Do NOT use for Power Automate flows or .zip packages — use
  building-powerautomate-flows. Do NOT use to gather requirements or write a solution-spec.yaml
  — use planning-powerplatform-solutions. Do NOT use for user or admin manuals — use
  writing-app-manuals. If a solution-spec.yaml exists, ask for it first and read its screens,
  variables and bindings sections.
---

# HTML, spec, or description → Power Apps Canvas pa.yaml

<!-- v1.0.0 -->

Every rule marked with a count below was measured across 17 screens that compiled in Studio.
Where a rule has a number attached, it is not a preference.

## Step 0 — Intake

Settle three things. If the user already said, state your assumption in one line and move on.

1. **Source** — files (read the markup *and* its linked CSS/`tailwind-config.js`/JS, because
   tokens and interactions live there), pasted HTML, a screenshot, or `solution-spec.yaml`.
   Given both HTML and an image, take exact values from the HTML and use the image only to check
   the HTML is not truncated.
2. **Scope** — layout and styling only, or also behaviour (`onclick` → `OnSelect`), or also data
   binding (tables → galleries and collections). Go as deep as the source supports.
3. **Output** — one file per screen is the default and matches how Studio pastes. Combine under
   one `Screens:` block only when asked.

## Workflow

1. **Read the source fully**, including linked token files. Re-read tokens every run; they drift.
2. **Map tokens to values** — hex → `RGBA(r, g, b, a)`, spacing → the measured sizing set. See
   `references/layout-sizing.md`.
3. **Build the control tree** from the DOM, top-down. See `references/patterns.md`.
4. **Choose control types from the catalog only.** Nine types exist. See
   `references/control-catalog.md`. Anything not in it gets `# UNVERIFIED` and a question — never
   a plausible guess.
5. **Translate the hard patterns** — tables → `Gallery`, editable tables → a collection, status
   badges → `Switch()`, upload zones → `GroupContainer` with `BorderStyle.Dashed`.
6. **Wire behaviour** — `href`/`onclick` → `OnSelect: =Navigate(Target)`. Anything whose target
   does not exist yet → `OnSelect: =Notify("…", NotificationType.Information)` so it compiles now.
7. **Emit the YAML** following the inline rules below.
8. **Validate.** See the gate below. Do not skip it.
9. **Deliver** the full file in one block, plus a separate one-control snippet for anything marked
   `UNVERIFIED` so the user can paste-test it alone before trusting it inside a full screen.
10. **Offer the capture step** — one line, once the work is confirmed working: the user can paste
    `prompts/feedback-session.md` to record what had to be corrected.

### Checklist

```
[ ] tokens re-read from source this run
[ ] every control type in the catalog, exact version string
[ ] properties alphabetised in every Properties block
[ ] block scalar on every value containing ': ', a newline, or ' #'
[ ] screen has Fill, LoadingSpinnerColor, OnVisible
[ ] no X or Y below the root container
[ ] Height + LayoutMinHeight on every container and gallery
[ ] Items AND Items.Value on every DropDown and Radio
[ ] validator run, exits clean
[ ] UNVERIFIED items listed, with a test snippet each
```

## Rules that decide whether the paste works

**Control types — nine, and no others.** `Label@2.5.1`, `GroupContainer@1.5.0`,
`Classic/Button@2.2.0`, `Classic/CheckBox@2.1.0`, `Classic/Icon@2.5.0`,
`Classic/TextInput@2.3.2`, `Gallery@2.15.0`, `Classic/Radio@2.3.0`,
`Classic/DropDown@2.3.1`. `Label`, `Gallery` and `GroupContainer` are **bare**; everything
interactive takes `Classic/`. Use these exact versions. (2,830 controls, no exceptions.)

**Alphabetise properties** inside every `Properties` block, case-insensitively.
(2,847 of 2,847 blocks, zero violations — the strongest signal in the artifact set.)

**Block scalars.** Any value containing `: `, a newline, or ` #` must use `|`. A colon-space
reads as a nested mapping and the paste breaks. Never use `|` when it is not required.
(119 block scalars, every one necessary, none decorative.)

```yaml
Text: |
  ="Status: Pending Verification"
```

**Position with AutoLayout, never coordinates.** `X` and `Y` appear only on the depth-1 root
container. (0 of 2,813 nested controls declare either. `GroupContainer` is always
`Variant: AutoLayout`, 887/887.) Inset children with `Width: =Parent.Width - N`.

**Every screen carries exactly three properties** — `Fill`, `LoadingSpinnerColor`
(`=RGBA(56, 96, 178, 1)`), and `OnVisible`. `OnVisible` seeds every global and collection with
`If(IsBlank(gbl…), Set(…))` / `If(IsEmpty(col…), ClearCollect(…))` guards. (17/17 screens.)

**`Height` *and* `LayoutMinHeight` on every container and gallery**, or rows collapse to zero
height. (887/887 containers, 36/36 galleries.)

**`Classic/DropDown` and `Classic/Radio` need both `Items` and `Items.Value`.** Omitting
`Items.Value` is a silent failure.

**Never write `DropShadow.Light`** — it does not exist. Use `DropShadow.None` on flat and
structural containers; omit `DropShadow` entirely on elevated white cards.

**Spaces only.** A tab anywhere in leading whitespace breaks the paste.

**Variable naming:** `gbl*` globals (`Set`), `col*` collections (`ClearCollect`), `var*` context
variables (`UpdateContext`).

**Mark anything unconfirmed.** Add `# UNVERIFIED — guessing from <reasoning>` inline and say so
in your reply. An invented-but-plausible control type or property is the single biggest cause of
paste failure, and it is the failure this skill exists to prevent. If you do not know, say so.

## Validation gate

Run `python scripts/validate_pa_yaml.py <file>`. If it fails, fix and re-run. Do not present
output to the user until the validator exits clean.

The validator is a safety net, not the source of truth. It catches wrong control types,
unsorted properties, missing block scalars, `X`/`Y` below the root, missing screen properties,
a missing `Items.Value`, `DropShadow.Light`, tabs, flow-style mappings, and sizes outside the
measured set. All 17 reference screens pass it with zero warnings.

## References — read the one you need

- `references/control-catalog.md` — the nine types, their exact version strings, and the
  property set every instance of each one carries. Read before writing any control.
- `references/layout-sizing.md` — AutoLayout, the closed `Size` set, the `=Parent.Width - N`
  inset idiom, scroll containers, nesting depth, and the measured colour palette.
- `references/patterns.md` — HTML element → control mapping, and worked cases: table → gallery,
  editable table → collection, badge → `Switch()`, upload zone, icons, forms.
- `references/error-taxonomy.md` — Studio error codes, which block the paste and which do not,
  and the failure modes seen in real files.

## Conventions this skill does not carry

Design tokens, the TH↔EN glossary, site URLs and naming standards live in Project knowledge,
not here. If a token set or glossary is missing and the output depends on it, ask.
