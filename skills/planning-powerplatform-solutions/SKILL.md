---
name: planning-powerplatform-solutions
description: >-
  Runs a requirements interview and produces solution-spec.yaml, an HTML mockup, and a
  system-overview document for a Power Platform solution. This is the FIRST skill on any new
  project — the other four read the spec it writes. Triggers: "we need an app for...", "help me
  scope this", "plan this system", "gather requirements", "design the solution", "turn this
  process into an app", "here's our flowchart/ER diagram/process doc", "write the spec", "system
  overview", "what should we build". Also use when a project has no solution-spec.yaml yet, or
  when an existing spec must be revised. Do NOT use to generate Power Apps screens or .pa.yaml —
  use generating-powerapps-yaml. Do NOT use to create SharePoint lists or columns — use
  building-sharepoint-lists. Do NOT use to build Power Automate flows or .zip packages — use
  building-powerautomate-flows. Do NOT use to write the end-user or admin manual — use
  writing-app-manuals. Produces the plan; the four builder skills produce the artifacts.
---

# Requirements interview → solution-spec.yaml + mockup + overview

<!-- v1.0.0 -->

The only skill that **writes** the spec. Everything downstream reads it, so a field left vague
here becomes four skills guessing differently.

Rules are tagged `PLATFORM` (a Power Platform fact) or `HOUSE` (convention, in
`assets/house-style.yaml`). See `docs/EVIDENCE-TIERS.md`.

## The stopping rule

An interview with no end condition is the main way this skill fails. There is an objective one:

> **The interview is over when `validate_spec.py` exits clean and the user has confirmed the
> glossary.** Not before, and — more importantly — **not after.**

Once the spec validates, stop asking. Anything still unknown becomes a `TODO` in the spec and a
line in the overview's Open Questions, which is more useful than a longer interview.

## Workflow

1. **Take in whatever they have.** A flowchart, an ER diagram, a process document, an existing
   spreadsheet, a screenshot of a whiteboard, or nothing. Normalize it before asking anything —
   see `references/normalizing-inputs.md`. If they have a workbook that already documents lists,
   `building-sharepoint-lists/scripts/xlsx_to_spec.py` extracts it rather than retyping.
2. **Build the glossary first.** Before scoping, before data, before screens. This is the step
   that pays for itself — see `references/glossary-first.md` and the rule below.
3. **Interview in passes**, each producing spec sections. `references/interview-guide.md` has the
   question set. Do not ask everything at once; a pass at a time, and skip what the input already
   answered.
4. **Draft the spec** as you go, not at the end. Show it. A user correcting YAML they can read is
   faster than a user answering an abstract question.
5. **Validate** — the gate below.
6. **Build the HTML mockup** from `screens[]` using the project's design tokens. See
   `references/mockup-conventions.md`.
7. **Render the overview** — `python scripts/render_overview.py <spec> -o overview.html`. It
   emits a print-ready HTML the user saves as PDF from the browser. Section order is fixed by
   `assets/pdf-outline.md`.
8. **Hand off.** Name the next skill for each remaining artifact, and say the spec travels
   between chats so nothing has to be re-explained.

### Checklist

```
[ ] glossary built and confirmed BEFORE anything else
[ ] every term with two names resolved, or recorded as genuinely two things
[ ] roles[] defined — every screen has at least one
[ ] process[] stages, each with an owner role
[ ] lists[] with populated_by on every field
[ ] relations[] with a stated reason on each
[ ] screens[] with purpose and roles
[ ] flows[] with trigger kind; splits_on where the trigger is sharepoint_item
[ ] variables[] and bindings[] connecting screens to fields
[ ] validator exits clean
[ ] open questions listed rather than guessed
```

## Rules

**`HOUSE` — glossary first, and ask the disambiguating question explicitly.** When two
departments describe what might be the same thing, **ask "is this the same as X?"** rather than
recording both. Most apparent cross-department conflicts are one system under two names, and the
cost is asymmetric: two names for one thing produces duplicate lists, duplicate screens, and a
migration later; one name for two things is caught in the first review. When genuinely unsure,
record both and mark the pair `unresolved` — never silently merge or silently split.

**`HOUSE` — write the spec in front of them.** Show the YAML as it fills in. Users correct a
concrete `RequestStatus: [Draft, Submitted, Approved]` far more reliably than they answer "what
statuses do you need?"

**`HOUSE` — the spec is the product; the overview is a rendering.** Never hand-write the overview
document. If something belongs in it, it belongs in the spec first. A hand-edited PDF and a spec
disagree within a week.

**`PLATFORM` — every list-to-list reference is a text key, never a Lookup.** Lookup columns are
not delegable, so a gallery filtered on one truncates silently. Set `relations[].kind: text_key`
and state the reason in the spec — the reason is what stops a later builder "fixing" it.

**`PLATFORM` — a `sharepoint_item` trigger needs `splits_on`.** Any other trigger kind does not.
State the condition, not a blanket rule.

**`HOUSE` — every field needs `populated_by: user | automation`.** It decides whether a column
appears on a form, and the manual renders the same split. If the user does not know yet, ask who
types it; if nobody types it, it is automation.

**`HOUSE` — record what you did not learn.** A spec with three honest `TODO`s beats a spec with
three confident inventions. Everything unresolved goes in the overview's Open Questions.

**Ask before assuming a design system.** Tokens, palette, and the TH↔EN glossary live in Project
knowledge. If they are absent and the mockup needs them, ask rather than picking.

## Validation gate

Run `python scripts/validate_spec.py <file>`. If it fails, fix and re-run. Do not present output
to the user until the validator exits clean.

## References — read the one you need

- `references/glossary-first.md` — why it goes first, the disambiguating question, and what to do
  when two departments disagree.
- `references/interview-guide.md` — the question set, in passes, each mapped to spec sections.
  Domain-agnostic.
- `references/normalizing-inputs.md` — turning a flowchart, ER diagram, process doc or existing
  spreadsheet into spec sections before asking anything.
- `references/mockup-conventions.md` — the HTML mockup: what it is for, what it must not become,
  and how it hands off to `generating-powerapps-yaml`.

## What this skill hands off

| Artifact | Next skill |
|---|---|
| `lists[]`, `relations[]` | `building-sharepoint-lists` |
| `screens[]`, `variables[]`, `bindings[]` | `generating-powerapps-yaml` |
| `flows[]` | `building-powerautomate-flows` |
| `screens[]`, `roles[]`, `glossary[]` | `writing-app-manuals` |

Say this out loud at handoff, and tell the user to carry `solution-spec.yaml` into each new chat.
One stage per chat — see the README.
