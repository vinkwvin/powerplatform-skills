# Error taxonomy

What Studio tells you, what it means, and what actually causes it.

## Contents
1. Blocking vs non-blocking
2. Failure modes and their fixes
3. When the user reports a Studio result
4. The isolated-snippet protocol

---

## 1. Blocking vs non-blocking

Classify every message before reacting. Treating a version warning as urgent wastes a round;
dismissing a blocking error wastes the whole paste.

| Code | Blocking? | Meaning |
|---|---|---|
| `PA1001` | **yes** — whole paste rejected | the source could not be parsed or a control type is invalid |
| `PA2108` | **yes** | property is not recognised on that control |
| `PA2105` | no | control version not found; Studio substitutes the nearest |
| `PA2106` | no | property version warning; Studio substitutes |

A non-blocking version warning means the screen pasted. Check the result visually rather than
rewriting the file.

**Provenance note.** These four codes come from the retired `html-to-yaml` skill, written when
the lesson was fresh. They are Rank 2 — not measured from the 17 screens, which contain no error
records. Treat the blocking/non-blocking split as reliable and the exact code numbers as worth
confirming if a message does not match.

## 2. Failure modes and their fixes

Ordered by how often the cause appears in real work.

### The value contained `: ` and was not a block scalar
**Symptom:** the paste fails, or a property silently holds the wrong value. YAML reads
colon-space as the start of a nested mapping.
**Fix:** wrap in `|`.

```yaml
# breaks
Text: ="Status: Pending Verification"
# works
Text: |
  ="Status: Pending Verification"
```

Same for a value containing ` #` (starts a YAML comment) and for any multi-line formula —
`Switch(...)`, `If(...)`, `Table(...)` spanning lines.

### Wrong bare-vs-Classic choice
**Symptom:** `PA1001`, or the control pastes but rejects `Color`/`Fill`/`Size` with `PA2108`.
**Cause:** a bare interactive control resolves to the modern variant, which has a different
property set.
**Fix:** `Classic/` on everything interactive; bare on `Label`, `Gallery`, `GroupContainer`.

### An invented control type or property
**Symptom:** `PA1001` or `PA2108`.
**Cause:** something plausible that does not exist. This is the top cause of paste failure and
the reason this skill keeps a closed catalog.
**Fix:** use the catalog. If the design needs something outside it, mark `# UNVERIFIED` and ship
a test snippet.

### `Items` without `Items.Value`
**Symptom:** no error — the dropdown or radio renders empty.
**Cause:** a silent failure, which makes it worse than a loud one.
**Fix:** both properties, always.

### Properties not alphabetised
**Symptom:** usually pastes, sometimes misbehaves.
**Cause:** all 2,847 real blocks are sorted; unsorted output is outside the tested envelope.
**Fix:** sort case-insensitively.

### `X`/`Y` on a nested control
**Symptom:** the control lands in the wrong place, or the layout collapses, because AutoLayout
is positioning its siblings and this one is fighting it.
**Fix:** delete `X`/`Y` below the root and express the offset with `Padding*`, `LayoutGap`, or
`Width: =Parent.Width - N`.

### Rows collapse to zero height
**Symptom:** a card or gallery renders as a sliver.
**Cause:** `FillPortions` alone, with no `LayoutMinHeight`.
**Fix:** explicit `Height` **and** `LayoutMinHeight` on the container and the gallery.

### `DropShadow.Light`
**Symptom:** `PA2108`.
**Cause:** the value does not exist. Zero occurrences in 17 screens.
**Fix:** `DropShadow.None`, or omit `DropShadow` on elevated white cards.

### A tab in leading whitespace
**Symptom:** the paste fails outright.
**Fix:** spaces only.

### Flow-style mapping in `Properties`
**Symptom:** parse failure.
**Cause:** `{X: =0, Fill: =RGBA(1, 2, 3, 1)}` — the commas inside `RGBA(...)` break flow-style
parsing.
**Fix:** block style throughout.

### A `Navigate()` target that does not exist
**Symptom:** compile error naming an unknown screen.
**Fix:** `OnSelect: =Notify("…", NotificationType.Information)` until the target screen exists,
then swap it.

### Header and gallery template widths disagree
**Symptom:** columns do not line up.
**Fix:** identical fixed `Width` or matching `FillPortions` on the header labels and the template
cells.

## 3. When the user reports a Studio result

1. **Classify the message** — blocking or not, per the table above.
2. **If they send a screenshot**, compare it against the source point by point: position, colour,
   size, font, border, corner radius. Name the specific remaining differences. Do not say "looks
   close".
3. **Fix only what broke.** A targeted one-property change beats regenerating the file.
4. **If a Studio test confirms something new** — a control or property that was `UNVERIFIED` now
   works — that is a real finding. Record it via `prompts/feedback-session.md` so it reaches the
   catalog instead of dying in the chat.

## 4. The isolated-snippet protocol

Studio needs a full-file paste, so the main deliverable is never fragmented. But when a screen
depends on something outside the catalog:

1. Mark it `# UNVERIFIED — guessing from <reasoning>` in the full file.
2. **Also** emit a separate block containing just that one control inside a minimal screen,
   labelled "test this one first".
3. Say plainly in your reply which items are unverified.

One paste to test one uncertainty is cheap. Discovering the uncertainty inside a 3,000-line
screen is not.
