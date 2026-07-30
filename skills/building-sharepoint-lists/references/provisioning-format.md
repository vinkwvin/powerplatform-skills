# The provisioning workbook format

What `generate_workbook.py` emits, why it is shaped that way, and how a human uses it.

## Contents
1. Why a workbook at all
2. Why it is transposed
3. Row layout
4. Shading
5. The library case
6. Using it in the browser
7. The reverse direction

---

## 1. Why a workbook at all

`PLATFORM` constraint on this environment: no Power Platform CLI, no local execution. Lists get
created by a person clicking in a browser.

A workbook beats a prose spec for that job because it is:

- **checkable** — a column either has a type in row 3 or it does not
- **progress-tracking** — the person creating columns can work left to right and see where they got to
- **the same artifact twice** — the sheet used to create the columns is also the sheet used to paste
  seed data
- **round-trippable** — `xlsx_to_spec.py` reads it back, so the workbook and the spec cannot drift
  silently

The optional PnP script (`--script`) is for whoever *does* have PowerShell. It is generated from the
same spec, so the two cannot disagree.

## 2. Why it is transposed

Fields run **across the columns**, one sheet per list, with fixed metadata rows down the left.

The obvious layout — one row per field — breaks down at scale. The reference system's largest list
has 61 fields; as 61 rows with 7 columns you scroll vertically and lose the header. Transposed:

- a person entering seed data types **down** a column, which is how a form is filled
- the metadata rows stay visible with a single frozen pane
- adding a field appends a column instead of inserting a row into a formatted block
- the sheet reads in the same left-to-right order the form will

`HOUSE` — this is a format choice, and the format the reference team already used. A project that
prefers row-per-field should change `generate_workbook.py` once rather than hand-editing output.

## 3. Row layout

Fixed row numbers, so a human can rely on them and so `xlsx_to_spec.py` can find them by label.

| Row | Holds |
|---|---|
| 1 | **Section** — grouping label, written once per section |
| 2 | **FIELD NAME (EN)** — the column name. ASCII only |
| 3 | **Data type** — the SharePoint type to pick in the UI |
| 4 | **Label** — the localised display label, set after creating the column |
| 5 | **Description** — what the column is for |
| 6 | **Choices / Notes** — enumerated choices, join-key note, library note |
| 7 | **Populated by** — `user`, or `automation — do NOT put on a user form` |
| 8 | marker row |
| 9+ | blank, for seed or sample data |

Rows 2 and 4 being separate is the important part. `PLATFORM`: a non-ASCII or punctuated column
name survives creation and then breaks formulas, REST URLs, and exports — SharePoint stores it as
an escaped internal name like `_x0e01__x0e32_...`. Keep the name ASCII in row 2 and put the
localised text in row 4.

`xlsx_to_spec.py` locates rows by matching the left-column label, not by row number, so a workbook
with extra or reordered rows still parses.

## 4. Shading

| Colour | Means |
|---|---|
| grey-lavender, left column | metadata row headers |
| **orange** | `populated_by: automation`. Create the column, then remove it from the default form |
| **purple** | a key column — the join key, or a `Title` holding the natural key. Plain text on purpose. Do not convert to Lookup |

The purple shading exists because the text-key decision is the one most likely to be "corrected" by
someone who does not know why. The note in row 6 states the reason next to the column itself.

## 5. The library case

A list whose first field is type `file` is a **document library**. Its sheet is labelled `LIBRARY`.

`PLATFORM`: a library is created as a library — it cannot be converted from a list, and a list
cannot hold file uploads. So the order is:

1. Create the document library in the browser.
2. Add the metadata columns from the sheet, skipping the first (`file`) column, which is the file
   itself.

The PnP script does not create libraries; it emits a comment telling you to create it first, then
adds the columns.

## 6. Using it in the browser

1. Open the **How to use** sheet. Confirm the site URL is filled in.
2. Work through the list sheets **in order**. Sheet order follows spec order, and a list referenced
   by another comes first.
3. Per sheet: create the list (or library), then add columns left to right using row 3 for the type.
4. Set display labels from row 4 after the columns exist.
5. Remove every orange column from the default form.
6. Add any index named in row 6 **now** — `PLATFORM`: an index must be added before the list passes
   the list-view threshold (5,000 items by default), and adding one afterwards can fail. `Title` is
   indexed already.
7. Paste seed data from row 9 down, if there is any.

## 7. The reverse direction

`xlsx_to_spec.py` converts an existing workbook back into `lists[]`. Two uses:

- **Bootstrap** — a system that already exists and is documented in Excel becomes a spec without
  retyping it, so the other skills can consume it.
- **Round-trip check** — `xlsx → spec → xlsx` must preserve every field. The regression fixture in
  `evals/building-sharepoint-lists/fixtures/` does exactly this: 131 fields out, 131 back,
  identical.

**What it cannot recover:** `relations[]`. A workbook shows that two lists both have a `RequestID`
column; it does not say they are joined, or why. Joins are added by hand, and
`validate_lists.py` requires a `reason` on each — deliberately, because an unexplained relation is
the thing a later builder undoes.

Anything the extractor has to guess is emitted as a `TODO` comment in the header rather than
silently defaulted. Read those before feeding the output to another skill.
