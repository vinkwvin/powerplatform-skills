---
name: building-sharepoint-lists
description: >-
  Generates a SharePoint provisioning workbook (.xlsx) and column-creation script from a
  solution-spec.yaml lists section, so lists and libraries can be created in the browser with no
  CLI. Use whenever SharePoint data structure is being built, changed, or reviewed — triggers:
  "create the SharePoint lists", "make the list schema", "provisioning workbook", "column
  script", "what columns do I need", "add a field to the list", "why is my gallery only showing
  500 rows", "delegation warning", or modelling data for a Power Platform app. Do NOT use for
  Power Apps screens or .pa.yaml — use generating-powerapps-yaml. Do NOT use for Power Automate
  flows or .zip packages — use building-powerautomate-flows. Do NOT use to gather requirements
  or write the spec itself — use planning-powerplatform-solutions. Do NOT use for user or admin
  manuals — use writing-app-manuals. If no solution-spec.yaml exists, ask for it first; if the
  user is describing a whole system rather than its data, route them to
  planning-powerplatform-solutions first.
---

# solution-spec.yaml → SharePoint provisioning workbook

<!-- v1.0.0 -->

Reads `lists[]` and `relations[]`. Ignores every other section.

Rules below are tagged `PLATFORM` (a SharePoint or Power Apps fact, never overridable) or
`HOUSE` (this organisation's convention, in `assets/house-style.yaml`, editable per project).
See `docs/EVIDENCE-TIERS.md`.

## Step 0 — Intake

1. **Spec or description?** With a spec, read `lists[]` and `relations[]` and generate. Without
   one, and the user is describing data for one list, capture it into spec shape first so the
   output is reproducible. If they are describing a whole system, route to the planner.
2. **New site or existing?** An existing site means some lists exist — ask which, and generate
   only the delta. Never emit a create-script for a list that already holds data.
3. **Who populates each column?** Every field needs `populated_by: user | automation`. If the
   spec omits it, ask. This single field drives the provisioning UX, the manual, and whether a
   column appears in a form at all.

## Workflow

1. **Read `lists[]` and `relations[]`.**
2. **Check the joins.** Every list-to-list reference must be a text key, not a Lookup. See
   `references/delegation.md` for why, and say the reason out loud when you generate it — a
   builder who does not know the reason will "fix" it later.
3. **Resolve each field to a SharePoint column type** using the table in
   `references/field-types.md`.
4. **Identify libraries.** A list whose first field is type `file` is a document *library* and is
   provisioned differently. See `references/provisioning-format.md`.
5. **Generate the workbook** — `python scripts/generate_workbook.py <spec> -o <out.xlsx>`.
6. **Generate the column script** if asked — the same script with `--script`.
7. **Validate.** See the gate below.
8. **Report** the list count, field count per list, the join column, and anything you had to
   assume.
9. **Offer the capture step** once the lists are built and working: the user can paste
   `prompts/feedback-session.md` to record what had to be corrected.

### Checklist

```
[ ] every field has an explicit populated_by
[ ] no Lookup column anywhere; list-to-list joins are text
[ ] people fields are Person or Group, not text
[ ] every child list carries the join column
[ ] libraries identified by a first field of type file
[ ] choice fields have their choices enumerated
[ ] a choice with a free-text escape names its other_field
[ ] validator run, exits clean
[ ] assumptions listed
```

## Rules

**`PLATFORM` — Lookup columns are not delegable.** Filtering a gallery on a Lookup pushes the
work to the client: it truncates silently at the delegation limit and shows an incomplete list
with **no error at all**. Join lists with a text key instead. This is the single most consequential
rule in this skill, and the failure it prevents is invisible.

**`PLATFORM` — the text-key rule is for list-to-list references only.** People are
`Person or Group`. Do not generalise "avoid Lookup" into "avoid all complex column types" — a
person field turned into text loses the picker, the resolution, and the email.

**`PLATFORM` — `Title` always exists and is indexed by default.** Putting the natural key in
`Title` makes the join filter fast without adding an index. Rename its display label rather than
adding a parallel key column.

**`PLATFORM` — a document library is not a list.** Create it as a library, then add metadata
columns. A list cannot hold file uploads.

**`PLATFORM` — a Choice column rejects any value not in its list.** Enumerate every choice, and
if free text is possible, add an explicit `other_field` alongside rather than relying on
"Can add values manually".

**`HOUSE` — naming.** Lists `PascalCase_With_Underscores`; fields `PascalCase`, no spaces, no
underscores. Booleans read as a statement or an action (`IsActive`, `HasNoAssets`, `CloseAccount`).
A boolean that gates an optional value pairs with it (`CloseTFEXAccount` + `TFEXAccountNumber`).

**`HOUSE` — every child list carries a `<Verb>By` + `<Verb>At` pair** — `Person or Group` plus
`Date and Time` — so every row records who last acted and when. Cheap to add up front, painful to
retrofit.

**`HOUSE` — display language is a sibling column, never part of a name.** Keep the field name
ASCII and put the localised label in the workbook's own label row. A non-ASCII column name
survives creation and then breaks formulas, URLs, and exports.

**`HOUSE` — `populated_by: automation` columns are omitted from user-entry forms.** A user typing
into a column a flow overwrites is a support ticket waiting to happen.

## Validation gate

Run `python scripts/validate_lists.py <file>`. If it fails, fix and re-run. Do not present output
to the user until the validator exits clean.

## References — read the one you need

- `references/field-types.md` — the spec type vocabulary mapped to SharePoint column types, with
  what each is for and what it costs.
- `references/delegation.md` — why Lookup is banned, what delegation actually limits, and how to
  keep a filter delegable. Read before designing any join.
- `references/provisioning-format.md` — the workbook layout, why it is transposed, the library
  case, and how a human uses the output in the browser.

## Conventions this skill does not carry

Site URLs, tenant names, the TH↔EN glossary, and retention or permission policy live in Project
knowledge. If a site URL or a glossary is missing and the output depends on it, ask.
