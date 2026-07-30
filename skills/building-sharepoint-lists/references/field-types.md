# Field types

The spec type vocabulary, what each maps to in SharePoint, and what it costs.

## Contents
1. The mapping
2. Choosing between similar types
3. Types deliberately excluded
4. Distribution in the reference system

---

## 1. The mapping

`PLATFORM` — these are SharePoint column types.

| spec `type` | SharePoint column | PnP `-Type` | Notes |
|---|---|---|---|
| `text` | Single line of text | `Text` | 255 chars. The default for keys and short values |
| `multiline` | Multiple lines of text | `Note` | Plain or rich. Not delegable for filtering |
| `choice` | Choice | `Choice` | Rejects any value not in the list — enumerate them all |
| `bool` | Yes/No (Boolean) | `Boolean` | Has no null: it is Yes or No, never blank |
| `number` | Number | `Number` | For counts and quantities |
| `currency` | Currency | `Currency` | Has a locale. Prefer over `number` for money |
| `datetime` | Date and Time | `DateTime` | Stored UTC, displayed in site locale |
| `person` | Person or Group | `User` | Keeps the picker, resolution and email |
| `file` | (the file itself) | — | Only valid as the first field of a `library` |

## 2. Choosing between similar types

### `text` vs `multiline`
`text` caps at 255 characters and **is** delegable. `multiline` has no practical cap and is **not**
delegable for filtering. So: anything you might filter or sort on is `text`, even if it is longish.
Remarks, opinions, and reasons are `multiline`.

### `choice` vs `text`
`choice` gives a controlled vocabulary and a dropdown for free. Its cost: it **rejects** any value
not in the list. A flow or an import writing an unexpected value fails — often with a message that
does not name the column.

Two consequences:

- Enumerate every value before provisioning, including the ones only a flow writes.
- If free text is genuinely possible, add an explicit companion column rather than enabling
  "Can add values manually" — an ad-hoc value entered once becomes an undocumented member of the
  vocabulary forever.

```yaml
- name: ClosureReason
  type: choice
  choices: [Deceased, NoLongerTrading, Other]
  other_field: ClosureReasonOther     # ← the escape, explicit
- name: ClosureReasonOther
  type: text
  populated_by: user
```

### `number` vs `currency`
`currency` carries a locale and formats consistently in the app, the list view, and an export.
Use `number` for counts. A money column typed as `number` will eventually be exported without its
decimals.

### `bool` and the missing third state
`bool` cannot be blank. So "not answered yet" is not representable — if you need it, use a `choice`
of Yes / No / Pending. This is the most common modelling mistake in an approval workflow: a
`bool` `Approved` cannot distinguish "rejected" from "nobody has looked".

### `person` vs `text`
Always `person` for a person. See `references/delegation.md` §5.

### `datetime` and the date-only case
There is no date-only type; use `datetime` and set the column's display format to Date Only. The
stored value is still UTC, so a date entered at 00:00 local can display as the previous day in
another timezone. For a pure business date that must never shift, some teams store `text` in
`YYYY-MM-DD` — a legitimate trade, but decide once and record it in `house-style.yaml`.

## 3. Types deliberately excluded

| Type | Why not |
|---|---|
| **Lookup** | not delegable. See `references/delegation.md`. Use `text` for the key |
| **Managed Metadata** | needs a term store, extra permissions, and is not delegable |
| **Calculated** | recomputed server-side, cannot be patched, and cannot be filtered delegably |
| **Hyperlink** | two values in one column; awkward in Power Apps. Use `text` for the URL |
| **Attachments** | still available on a list, but a `library` gives real metadata per file |

None of these is forbidden by SharePoint. They are excluded here because each has a delegation or
tooling cost that shows up late. If a project needs one, add it to this table with the reason
rather than using it silently.

## 4. Distribution in the reference system

`EXAMPLE` — one system, 10 lists, 131 fields. Shown to give a sense of proportion, not as a target.

| Type | Count | Share |
|---|---|---|
| `text` | 51 | 39% |
| `choice` | 27 | 21% |
| `bool` | 21 | 16% |
| `person` | 9 | 7% |
| `datetime` | 8 | 6% |
| `multiline` | 8 | 6% |
| `currency` | 5 | 4% |
| `number` | 1 | <1% |
| `file` | 1 | <1% |

Text and choice together cover 60%. If a design is reaching for exotic types often, that is usually
a sign the model wants another list rather than another column type.
