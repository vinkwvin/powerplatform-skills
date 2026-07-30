---
name: powerapps-yaml
description: >-
  Convert an HTML/CSS/JS UI prototype (Tailwind or plain CSS) into pasteable Power Apps
  Canvas source YAML (pa.yaml) that actually compiles in Power Apps Studio. Use this whenever
  the user wants to turn a front-end mockup, prototype, static HTML page, design, or repo of
  HTML pages into Power Apps canvas screens — including phrasings like "make this a Power App",
  "generate pa.yaml", "Power Apps YAML", "convert my HTML to a canvas app", "port this screen
  to Power Apps", or "turn this Tailwind page into a canvas screen". It handles the parts that
  trip people up: control-type selection (bare Label/Gallery vs Classic/ controls), design-token
  → RGBA/size mapping, tables → galleries, editable tables → collections, status badges →
  Switch(), interactions/onclick → OnSelect, and the YAML-safety rules (block scalars) that
  decide whether the paste compiles. Also use when the user reports a pa.yaml compile or paste
  error in Power Apps Studio and needs it diagnosed and fixed.
---

# HTML/CSS/JS prototype → Power Apps Canvas pa.yaml

## What this does

You hand over a finished front-end prototype (HTML + Tailwind/CSS + a little JS) and get back
Power Apps **Canvas source YAML** (`pa.yaml`) that pastes into Power Apps Studio and compiles on
the first or second try. The hard part isn't the layout — it's that pa.yaml is picky in ways the
official schema doesn't tell you: some controls must be bare (`Label@2.5.1`), most must be
`Classic/…`, certain values must be block scalars or the paste silently breaks, and properties
have to be alphabetized. This skill encodes those empirically-verified rules so the output works
in *this* environment rather than just validating against a schema.

Think of the job as three passes over the prototype: **structure** (containers and layout),
**style** (tokens → exact colors and sizes), and **behavior** (interactions and data). Do all
three, then validate before delivering.

## Step 0 — Intake (do this first, it's quick)

Before writing any YAML, settle three things. If the user already told you, don't re-ask —
just state what you're assuming and move on.

1. **Input mode** — are you reading files (`index.html`, `pages/*.html`, `assets/tailwind-config.js`,
   `assets/app.css`) or working from HTML pasted into chat? If files, read the page **and** its
   linked CSS/token config and JS, because the tokens and interactions live there, not in the markup.
2. **Scope** — layout + styling only, or also wire up interactions (onclick → `OnSelect`), or also
   attempt data binding (tables → collections/galleries, form submit → `Patch`/`SubmitForm`)? When
   in doubt, go as deep as the source supports and leave a clearly-labeled `Notify(...)` placeholder
   wherever the real screen/flow/data source doesn't exist yet.
3. **Output shape** — one `pa.yaml` per screen (matches a repo of standalone pages and how Studio
   pastes one screen at a time), or several screens combined under one `Screens:` block. One-screen-
   per-page is the safe default; combine only when asked.

If any of these is genuinely ambiguous and the choice changes the output materially, ask. Otherwise
pick the sensible default, say so in one line, and proceed.

## Workflow

1. **Read the source fully.** Markup + linked CSS/`tailwind-config.js` + JS. Note the design tokens,
   the repeated shell (sidebar / top bar), and any JS that adds rows, toggles state, or navigates.
2. **Extract the tokens → a color/size lookup.** Pull `tailwind.config.theme.extend` (colors,
   spacing, fontSize) or `:root` CSS custom properties or inline hex. Convert to Power Apps values.
   See `references/token-mapping.md`. Re-read the token file every run — tokens drift.
3. **Build the control tree.** Walk the DOM top-down and decide, for each element, which Power Apps
   control it becomes. See the mapping table in `references/html-to-powerapps.md`.
4. **Pick control types correctly.** This is the #1 source of compile errors. `Label` and `Gallery`
   are **bare**; every other interactive control is **`Classic/…`** with an exact version. The full
   table with versions is in `references/yaml-conventions.md` — consult it, don't guess versions.
5. **Translate the hard patterns.** Tables → `Gallery`; editable tables (Add Row / delete JS) →
   a **collection** (`Collect`/`Remove`/`Patch`) bound to the gallery; status badges → `Switch()`
   on the status value; dashed upload zones → `GroupContainer` with `BorderStyle.Dashed`. Worked
   examples (from real pages) are in `references/html-to-powerapps.md`.
6. **Wire behavior.** `onclick="location='x'"` / `<a href>` → `OnSelect: =Navigate(TargetScreen)`.
   Submit → `SubmitForm`/`Patch`. Anything whose target isn't built yet → `OnSelect: =Notify("…",
   NotificationType.Information)` so it compiles now and gets swapped later.
7. **Emit the pa.yaml** following every convention: `Screens:` schema, `LoadingSpinnerColor` on each
   screen, **alphabetized** properties, block scalars for any value containing `: ` or `#`, explicit
   `Height` + `LayoutMinHeight` on cards/galleries so nothing collapses.
8. **Validate.** Run `python3 scripts/validate_pa_yaml.py <file>` (stdlib only, no install). Fix
   every ERROR and review WARNs. This catches the exact mistakes that waste round-trips in Studio.
9. **Deliver.** Write the `.pa.yaml` file (files mode) or print it in a single fenced block for
   pasting. If you left placeholders or made a judgment call (an icon that had no exact Power Apps
   equivalent, a data source that isn't wired), list them briefly so the user knows what to finish.

## Core rules cheat-sheet

These are the ones that decide whether the paste works. Details and the rest are in the references.

- **Control types:** `Label@2.5.1` and `Gallery@2.15.0` are **bare**. `Classic/Button@2.2.0`,
  `Classic/TextInput@2.3.2`, `Classic/DropDown@2.3.1`, `Classic/Icon@2.5.0`, `Classic/Radio@2.3.0`
  need the **`Classic/` prefix** (bare modern versions reject `Color`/`Fill`/`Size`). Containers:
  `GroupContainer@1.5.0` with `Variant: AutoLayout`.
- **Every screen** carries `Properties: LoadingSpinnerColor: =RGBA(56, 96, 178, 1)`.
- **Alphabetize** the keys inside every `Properties:` block.
- **Block scalars** (`|`) for any value containing `: ` (colon-space) or `#` — otherwise YAML
  mis-parses it and the paste breaks:
  ```yaml
  Text: |
    ="Status: Pending Verification"
  ```
- **DropDown and Radio** need **both** `Items: =[...]` **and** `Items.Value: =Value`.
- **DropShadow:** `=DropShadow.None` on flat/structural containers; **omit entirely** on elevated
  white cards (the default elevation is already right — never write `DropShadow.Light`).
- **Placeholders:** use `Notify(...)` for buttons whose target screen/flow/data isn't built yet.
- **Spaces, not tabs**, for indentation.

## Reference files — read the one you need

- `references/yaml-conventions.md` — the environment contract: exact control types + versions,
  schema shape, sizing (~0.8 scale), layout/scroll rules, YAML safety, a copy-paste **screen
  skeleton**, and the `Gallery` structure. **Read this before writing YAML** if you're unsure of a
  version string or property name.
- `references/html-to-powerapps.md` — the translation playbook: a full element/CSS → control
  mapping table, plus worked before/after examples for the tricky cases (table → gallery, editable
  table → collection, status badge → `Switch`, dashed upload zone, icons, interactions, forms).
  **Read this when translating structure and behavior.**
- `references/token-mapping.md` — turning design tokens into exact Power Apps values: where tokens
  live, hex → `RGBA()` conversion, the ~0.8 layout scale, and a ready lookup for a Material-Design-3
  Tailwind theme (with the note to re-derive from the actual config each run). **Read this in the
  style pass.**

## Validating

`scripts/validate_pa_yaml.py` is a dependency-free linter for the conventions above. Run it on
every file before delivering:

```bash
python3 scripts/validate_pa_yaml.py path/to/Screen.pa.yaml
```

It reports ERRORs (things that will break the paste — wrong bare/Classic choice, missing
`Items.Value`, un-escaped `: `/`#`, tabs) and WARNs (things that usually should be fixed —
non-alphabetized properties, `DropShadow.Light`, a Radio missing `Layout`/`RadioSize`, a screen
missing `LoadingSpinnerColor`, an off-book control version). Exit code is non-zero if any ERROR is
found, so it can gate a commit. It is a safety net, not the source of truth — the conventions files
are.

## Gotchas worth remembering

- The official Microsoft `pa.schema.yaml` is **necessary but not sufficient**. Schema-valid YAML
  still fails to paste if the control versions/prefixes don't match this environment. Trust the
  version strings in `references/yaml-conventions.md`.
- Don't rely on `FillPortions` alone for multi-row auto-layout blocks — give tall columns an explicit
  `Height` plus `LayoutMinHeight`/`LayoutMinWidth` or rows collapse to nothing.
- Long/scrollable pages need `LayoutOverflowY: =LayoutOverflow.Scroll` on **both** the content
  container **and** the inner form card, not just one.
- Material-Symbols icon names (`dashboard`, `cloud_upload`, `expand_more`, …) have **no** 1:1 Power
  Apps equivalent. Map to the nearest `Icon.*` enum (table in `html-to-powerapps.md`) and flag any
  you had to approximate.
- Keep table header row and gallery template on matching column widths or the cells won't line up.
