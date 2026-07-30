---
name: html-to-yaml
description: >-
  Converts HTML/CSS mockups (e.g. from Google Stitch AI) or screenshot images of a UI design into
  Power Apps Canvas source code (.pa.yaml, Source Code schema v3.0) that can be pasted directly
  into a blank screen in Power Apps Studio via "Paste code". Use whenever the user shares an HTML
  mockup, a UI screenshot, or a Figma/Stitch export and wants it turned into a Power Apps screen,
  or asks to "convert this to pa.yaml", "make this a Power Apps screen", "turn this design into
  code I can paste into Power Apps", or similar, even without the exact term ".pa.yaml". Also use
  to fix/debug a .pa.yaml that failed to paste in Studio (PA1001/PA2108-style errors), to add a
  new screen to an existing app, or to extend a screen generated this way before. Encodes a
  catalog of which Power Apps control types/properties are actually confirmed to work vs. guessed
  — the main source of paste failures — so consult it before writing any .pa.yaml.
---

# HTML/Image → Power Apps Canvas YAML

## Why this skill exists

Power Apps Canvas's `.pa.yaml` format looks like ordinary YAML, but its schema is narrow,
version-pinned, and full of naming quirks that aren't derivable from first principles or from
general web-dev intuition (e.g. `Label` has no prefix but `Classic/Button` does; `Icon` and
`Classic/Icon` are different controls with different capabilities). Guessing at unconfirmed
control types or properties is the single biggest cause of paste failures in Studio. The fix is
discipline, not cleverness: only use what's confirmed, label everything else honestly, and let
the user test small pieces before committing to a full file.

## Step 0 — Read the confirmed control catalog first

Before writing a single line of `.pa.yaml`, read `references/confirmed-controls.md` in full. It
contains the control-type table, per-control confirmed properties, YAML gotchas (block-style vs
flow-style, full-file paste requirement, nesting rules, name-collision behavior), the project's
already-extracted hover colors, and the list of CSS effects with no Power Fx equivalent. This file
gets updated over time as more things get tested — always re-read it fresh rather than relying on
what you remember from earlier in the conversation, since the user may have added new confirmed
entries after a Studio test.

If `references/schema-v3.pa.yaml` is present, it's the official JSON-Schema definition for the
`.pa.yaml` file format itself (structure, not which controls/properties exist). Check it when
you're unsure about structural rules — e.g. what's a valid control name, how `Children` nesting
must be shaped, what top-level keys are legal — but note it validates *structure* only; it cannot
tell you whether `Classic/Button` supports a `Radius` property. Property-level truth only comes
from `confirmed-controls.md` and from what the user reports back from real Studio tests.

`assets/examples/` contains real, working `.pa.yaml` screens from this project (a sidebar +
navigation screen, a multi-section form with text inputs and dropdowns, and a checklist/card
screen). When building something structurally similar — another sidebar, another form, another
card grid — open the closest matching example and follow its actual patterns (naming conventions,
how sections are grouped, how X/Y coordinates are laid out) rather than inventing a new pattern
from scratch.

## Step 1 — Understand the source material

- If given an HTML file: read it and mentally decompose it into the controls it will need
  (Label, Button, GroupContainer, Rectangle, Image, Icon, TextInput, DropDown, Radio, etc.),
  extracting real values for text, colors, sizes, and positions rather than approximating.
- If given a screenshot/image only (no HTML): treat it as the visual ground truth for layout,
  spacing, and colors, and cross-check any HTML provided against it — mockup images sometimes
  differ slightly from the HTML that was exported alongside them.
- If given both, prefer the HTML for exact values (hex colors, Tailwind classes, pixel sizes) and
  the image to double check that the HTML wasn't cut off or doesn't match visually.
- Pull hover-state colors from the HTML's Tailwind config directly rather than eyeballing them
  from the screenshot — screenshots don't show hover states at all in most cases.
- Note: previously-generated screens in this app are named things like `1-Cases`,
  `2.1-FlagSN/HNW/UHNWChecklist`, `2.5-CustomizeDocument`, `3-CustomizeDocumentForm`,
  `4-AllYourDocuments`. If this new screen should link to/from an existing one, match the naming
  convention and check `assets/examples/example-sidebar-cases.yaml` for how `Navigate()` calls
  reference other screens by name.

## Step 2 — Write the .pa.yaml

Structure is mandatory and non-negotiable — always the full wrapper, never a bare control:

```yaml
Screens:
  <ScreenName matching what Studio should show>:
    Properties:
      Fill: =RGBA(r, g, b, a)
    Children:
      - <ControlName>:
          Control: <ControlType>@<version>
          Variant: <if applicable>
          Properties:
            X: =...
            Y: =...
          Children:              # only if this control has nested children
            - <ChildControlName>:
                Control: ...
```

Rules while writing:

1. **Tag every control and every property you're not 100% sure of.** Add an inline comment:
   `# CONFIRMED` (backed by `confirmed-controls.md` or a project example) or
   `# UNVERIFIED — guessing from <reasoning>` (not yet backed by evidence). Never present a guess
   as if it were confirmed — if you don't know, say so instead of quietly picking something
   plausible.
2. **Sidebar/nav items are always `Classic/Button@2.2.0`**, never `Label`, even when the mockup
   shows what looks like plain text with an icon — the real control needs to be clickable. If the
   destination screen doesn't exist yet, still use Button, and set `OnSelect` to a placeholder
   with a comment noting it isn't wired up yet (don't skip `OnSelect` silently and don't invent a
   `Navigate()` target that doesn't exist).
3. **Only use confirmed control types/properties in the main file.** If the mockup needs
   something not in `confirmed-controls.md` (e.g. a Slider, a DatePicker, rounded Rectangle
   corners), do two things: mark it `# UNVERIFIED` in the full file, AND separately propose a
   small isolated YAML snippet (just that one control) that the user can paste-test on its own
   before it's trusted inside a bigger screen.
4. **Block-style YAML only** for Properties — never flow-style (`{X: =0, Fill: =RGBA(...)}`),
   since the commas inside `RGBA(...)` break flow-style parsing.
5. **Real nesting = real `Children:` keys.** If a control must live inside a container, nest it in
   the YAML directly; don't rely on visual placement.
6. Every formula value starts with `=`.
7. When effects have no confirmed Power Fx equivalent (see the list in
   `confirmed-controls.md`), say so plainly in your response and propose the closest practical
   substitute — don't silently drop the requirement or fake it with an unconfirmed property.

## Step 3 — Hand off for testing

Send the user the complete file. Since Studio requires a full-file paste, don't split the main
deliverable into fragments — but do include any small isolated test snippets from step 2's rule 3
as separate blocks, clearly labeled as "test this one first."

## Step 4 — Interpret feedback

When the user reports back a Studio result (error text, warning text, or a screenshot):

- **Classify every message as blocking or non-blocking first**, per the Error vs warning table in
  `confirmed-controls.md` (e.g. `PA1001`/`PA2108` = blocks the whole paste; `PA2105`/`PA2106` =
  non-blocking version warning, Studio auto-substitutes). Don't treat a non-blocking warning as
  something that needs an urgent fix, and don't dismiss a real blocking error.
- **If they send a screenshot of the actual result**, compare it point-by-point against the
  original mockup — position, color, size, font, borders, corner radius — before declaring
  anything "matches now." Call out specific remaining differences rather than a vague "looks
  close."
- Fix only what's actually broken. Don't rewrite the whole file if a targeted fix (one control,
  one property) resolves the reported issue.
- If a new control/property gets confirmed as a result of this round (Studio accepted it, or the
  screenshot shows it rendered correctly), that's worth recording — see below.

## Keeping the catalog honest over time

This skill is only as good as `references/confirmed-controls.md` staying accurate. Whenever a
Studio test confirms or disconfirms something new during a conversation, update that file (adding
a row to the relevant table, moving something from "unverified" to "confirmed," or correcting a
wrong assumption) so the next conversion in this project benefits from it too. Don't let
confirmed-vs-unverified knowledge live only in chat history where it'll be lost.
