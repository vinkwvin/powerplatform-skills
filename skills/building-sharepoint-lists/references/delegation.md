# Delegation — why the joins are text

<!-- The single most consequential rule in this skill. The failure it prevents is silent. -->

## Contents
1. What delegation is
2. The Lookup problem
3. What stays delegable
4. Where the key lives
5. The exception: people
6. How to explain this to whoever inherits the app

---

## 1. What delegation is

`PLATFORM`

Power Apps does not run `Filter()` against a whole SharePoint list. It tries to translate the
expression into a server-side query. When it can, the server does the work and the app sees every
matching row — that is a *delegable* expression.

When it cannot translate, the app pulls the first N rows (500 by default, up to 2,000) and filters
them **in the client**. Everything past N is invisible.

The important part: **this is not an error.** The app does not crash, the gallery does not go red,
nothing appears in a log. It shows fewer rows and looks like it worked. In the maker studio you get
a blue-underline delegation warning at authoring time; at run time, on a list that has since grown
past the limit, you get nothing.

That is why this rule is stated in the SKILL.md body rather than in a reference nobody opens.

## 2. The Lookup problem

`PLATFORM`

A Lookup column stores a reference to an item in another list. Filtering on it — or on any of its
fields — is **not delegable** for SharePoint.

So a child list joined to its parent by Lookup produces a gallery that:

- works during development, when the list has 30 rows
- works at go-live, when it has 300
- quietly starts hiding data somewhere past 500
- is reported months later as "some requests are missing" with no other symptom

A text column holding the same key value is delegable. Same join, same query, no ceiling.

**Zero of the 131 columns in the reference system are Lookup.** That was deliberate.

## 3. What stays delegable

`PLATFORM`. For SharePoint specifically — the delegable set differs by connector.

| Delegable | Not delegable |
|---|---|
| `Filter(List, TextCol = "x")` | anything on a Lookup column |
| `Filter(List, StartsWith(TextCol, "x"))` | `in` operator |
| `Filter(List, NumCol > 5)` | `Search()` on many columns |
| `Sort` on a single indexed column | `CountRows` on a filtered set |
| `LookUp(List, TextCol = "x")` | most functions wrapped around the column |

Two habits that matter more than memorising the table:

- **Filter on a plain column, compared to a literal or a variable.** As soon as a function wraps
  the column, assume it breaks.
- **Test with more rows than the delegation limit.** A list with 40 rows cannot show you this bug.
  Seed 600 rows before believing a gallery.

## 4. Where the key lives

`PLATFORM` — `Title` exists on every SharePoint list and is indexed by default.

So put the natural key in `Title` and rename its display label, rather than adding a parallel key
column that then needs its own index.

```
New_Request.Title              = "REQ-1042"      the key, indexed for free
Request_Prechecks.RequestID    = "REQ-1042"      text, delegable
Request_Files.RequestID        = "REQ-1042"
```

`HOUSE` — the reference system did this three times: the request ID, a config key, and a citizen ID
used for a lookup that a flow filters on every run.

**A list can have at most 20 indexed columns, and an index must be added before the list grows
past the list-view threshold** — 5,000 items by default. Adding one afterwards can fail. Decide
indexes at provisioning time.

## 5. The exception: people

`PLATFORM`

`Person or Group` is the right type for a person, and this rule does **not** apply to it. Do not
generalise "avoid Lookup" into "avoid all complex types".

A person field turned into text loses the picker, the identity resolution, the email address, and
`User()` comparisons. Filtering on a person column has its own delegation caveats — compare on
`.Email` and test it — but that is a reason to test, not a reason to store a name as a string.

The reference system used `Person or Group` nine times and text for every list-to-list join.

## 6. How to explain this to whoever inherits the app

State the reason, not just the rule. A text column where a Lookup "should" be looks like a mistake
to the next developer, and they will fix it.

Put a note in the provisioning workbook next to the key column — `generate_workbook.py` does this
automatically — and one line in the handover doc:

> The child lists join to the header by a text `RequestID`, not a Lookup column. This is
> deliberate: Lookup columns are not delegable, so a gallery filtered on one silently truncates at
> 500 rows with no error. Do not convert these to Lookup.
