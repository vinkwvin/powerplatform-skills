---
name: writing-app-manuals
description: >-
  Generates two Word manuals from one solution-spec.yaml — a full admin manual and a
  user-friendly manual for everyday users. Triggers: "write the manual", "user guide",
  "documentation for the app", "how-to guide", "admin guide", "training material", "hand this
  over to the users", "send the users a guide to check", or a request to document a Power
  Platform system for the people who will use it. Runs in DRAFT mode before the build — a manual
  the user reads and corrects is a cheap requirements test — and FINAL mode after, with
  screenshots and real troubleshooting. Do NOT use to generate Power Apps screens or .pa.yaml —
  use generating-powerapps-yaml. Do NOT use for SharePoint lists — use building-sharepoint-lists.
  Do NOT use for Power Automate flows — use building-powerautomate-flows. Do NOT use to gather
  requirements or write the system-overview for the BUILDER — use
  planning-powerplatform-solutions. If no solution-spec.yaml exists, ask for it first.
---

# solution-spec.yaml → admin manual + user manual

<!-- v1.0.0 -->

Reads `screens[]`, `roles[]`, `lists[]`, `flows[]`, `glossary[]`, `process[]`, `meta.status`.

Rules are tagged `PLATFORM` (a `.docx` or tooling fact) or `HOUSE` (convention, in
`assets/house-style.yaml`). See `docs/EVIDENCE-TIERS.md`.

## One source, two documents

The user manual is a **projection** of the admin manual, not a second document. Its two body
sections are the admin manual's user-facing sections, compressed; architecture, setup,
troubleshooting and appendices are dropped.

Generate one source and render twice. Never author two files that must be kept in sync by hand —
they diverge inside a week, and the one that is wrong is always the one someone is reading.

## Draft mode and final mode

`meta.status` decides which.

| | `draft` — before the build | `final` — after |
|---|---|---|
| Purpose | a requirements test disguised as documentation | documentation |
| Screenshots | numbered placeholder frames | pasted in by a human |
| Setup section | omitted | full |
| Troubleshooting | omitted | real observed failures only |
| Appendices | glossary only | all |
| Sent to | the user, to correct | the user, to use |

**Draft mode is the more valuable of the two.** A user reading "click here, then here" and saying
*"that's not how we do it"* has caught a spec error while it still costs a sentence. Asking the
same person to approve a spec gets a nod.

What is missing from a draft is exactly what a user cannot validate anyway — setup and
troubleshooting need a built system. What remains is what they can check: roles, screen
walkthroughs, glossary.

## Workflow

1. **Read the spec.** Confirm `meta.status`, and say which mode you are in.
2. **Check the glossary exists.** It becomes an appendix and is the reason two readers agree. If
   it is empty, say so — that is a gap in the spec, not something to invent here.
3. **Generate** — `python scripts/generate_manual.py <spec> -o <dir>`. Two `.docx`.
4. **Validate.** See the gate below.
5. **List the screenshot frames** the human must fill, by number, with what each should show.
6. **In final mode, ask for troubleshooting entries.** Do not invent them — see the rule.
7. **Hand over** with the placeholder count and what is still needed.

### Checklist

```
[ ] mode stated, and it matches meta.status
[ ] glossary present, or its absence reported
[ ] both documents generated from one source
[ ] every screen in the user manual has heading → screenshot frame → steps
[ ] screenshot frames numbered, each naming screen, state and what to highlight
[ ] troubleshooting entries are observed failures, or the section is absent
[ ] automation-written columns not presented as things a user fills in
[ ] validator run, exits clean
```

## Rules

**`HOUSE` — never invent a troubleshooting entry.** Every entry must be a failure someone
actually hit. A plausible-but-fictional problem sends a reader chasing something that does not
happen, and it makes the real entries look equally speculative. In final mode, ask the team for
them. In draft mode there are none, because nothing has failed yet.

**`PLATFORM` — screenshots cannot be generated.** Emit a numbered placeholder frame naming the
screen, the state to put it in, and what to highlight. A frame saying *"Figure 4 — Sales screen,
after entering a citizen ID, highlight the litigation result box"* gets filled correctly; one
saying *"screenshot here"* gets filled wrong or not at all.

**`HOUSE` — the user manual is per-screen: heading → screenshot frame → bullet steps.** No
architecture, no column tables, no schema. If a sentence needs a data model to understand, it
belongs in the admin manual.

**`HOUSE` — an automation-written column is never described as something the user fills in.**
`populated_by` decides this, and getting it wrong produces a support ticket per reader.

**`HOUSE` — write for the reader named in `roles[]`.** The admin manual addresses whoever runs the
system; the user manual addresses whoever uses it. Same system, different depth, different
vocabulary. Neither is a summary of the other.

**`HOUSE` — bilingual headings put the localised language first**, per `assets/house-style.yaml`.
Change it there, not per-document, so the two manuals cannot disagree.

**`PLATFORM` — `.docx` mechanics.** Built-in heading styles or the table of contents comes out
empty. Tables need a width on the table *and* on every cell. Never a literal `\n` — separate
paragraphs. See `references/docx-mechanics.md`.

## Validation gate

Run `python scripts/validate_manual.py <file>`. If it fails, fix and re-run. Do not present
output to the user until the validator exits clean.

## References — read the one you need

- `references/manual-outlines.md` — the section order of both documents, and which spec section
  fills each.
- `references/screenshot-frames.md` — how to write a frame someone can actually act on.
- `references/troubleshooting.md` — where entries come from, and why inventing them is worse
  than omitting the section.
- `references/docx-mechanics.md` — the `docx` gotchas that decide whether the file opens clean.
