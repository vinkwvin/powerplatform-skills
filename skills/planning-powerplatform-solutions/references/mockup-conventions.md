# The HTML mockup

What it is for, what it must not become, and how it hands off.

## Contents
1. What it is for
2. What it must not become
3. Structure that survives the handoff
4. Design tokens
5. What to show per screen
6. Handing off

---

## 1. What it is for

The mockup is a **question asked in a form people can answer**. A user shown a screen says
"the approver needs to see the balance here" in five seconds. The same user shown
`screens[].purpose` in YAML says "looks fine" and means nothing by it.

Two jobs, in order:

1. **Validate the spec** — surface a missing field or a wrong role while it costs a sentence.
2. **Feed `generating-powerapps-yaml`** — it converts HTML into `.pa.yaml`, so a mockup built to
   convert cleanly saves a whole round later.

## 2. What it must not become

**Not a prototype.** No routing between pages, no state, no form validation, no fake login. Every
hour spent making it behave is an hour spent on something thrown away — and worse, a mockup that
behaves invites feedback on behaviour rather than on structure, which is not what you need yet.

**Not a design deliverable.** It uses the project's existing tokens. If there are none, ask —
inventing a visual language here means someone has to live with it.

**Not exhaustive.** Two or three representative screens beat twelve. Show the shapes that differ:
a form, a list, an approval, a dashboard. Ten screens that are the same shape teach the reader
nothing new and cost real time.

## 3. Structure that survives the handoff

`generating-powerapps-yaml` maps HTML to controls (see its `references/patterns.md`). A mockup
that uses these shapes converts almost mechanically; one that uses exotic CSS converts badly.

| Use | Because |
|---|---|
| `flex` / `grid` containers | become `GroupContainer` + `AutoLayout` directly |
| semantic `<h1>`–`<h3>`, `<p>`, `<label>` | become `Label` with a size from the type scale |
| real `<button>` and `<a>` | become `Classic/Button` — a clickable `<div>` does not |
| `<table>` for tabular data | becomes a `Gallery` with a header row |
| `<input>`, `<select>`, `<textarea>` | map to their `Classic/` control one-to-one |
| CSS `gap` and `padding` | become `LayoutGap` and `Padding*` |
| `width: calc(100% - 40px)` | becomes `Width: =Parent.Width - 40`, the standard inset |

Avoid: absolute positioning, CSS grid areas, transforms, pseudo-element content, and anything
whose visual result cannot be expressed as a nested box with padding. Power Apps has no equivalent
and the converter will have to approximate.

**Name things the way the spec does.** A `<section id="request-header">` that matches
`screens[].id` makes the mapping obvious. Ad-hoc names mean the converter guesses.

## 4. Design tokens

Per D3, tokens live in **Project knowledge**, not in this skill. Read them from wherever the
project keeps them — `tailwind.config.js`, `:root` custom properties, a token file — and re-read
them every run, because they drift.

If there are none and the mockup needs them: **ask**. Do not pick a palette. A palette chosen in a
mockup becomes the app's palette by default, and nobody revisits it.

When the project has no visual language yet and the user genuinely wants you to proceed, say what
you are doing: use a neutral greyscale plus one accent, and mark it explicitly as placeholder in
both the mockup and the handoff note.

## 5. What to show per screen

Enough to answer "is this the right screen for this person", and no more:

- the fields they fill in or read, with real-looking sample values
- the actions available to them
- what is read-only versus editable — a genuine source of misunderstanding
- what they cannot see, if that is a decision worth confirming
- the empty state, if it is meaningfully different

**Use plausible sample data, never `lorem ipsum`.** A realistic value is itself a question: if the
sample shows a 13-digit ID and the real one has 10, someone says so immediately. Placeholder text
gets skipped over.

## 6. Handing off

Deliver the mockup with three things stated plainly:

1. **Which spec screens it covers**, by `screens[].id`, and which it does not.
2. **Which parts are placeholder** — tokens you had to invent, sample data, any control that has
   no confirmed Power Apps equivalent.
3. **The next step:** `generating-powerapps-yaml`, in a fresh chat, with the spec and the mockup.

Say what the mockup is *not* as clearly as what it is. A user who thinks the app is nearly built
because the mockup looks finished is a problem you created, and it costs more to undo than the
sentence would have cost to write.
