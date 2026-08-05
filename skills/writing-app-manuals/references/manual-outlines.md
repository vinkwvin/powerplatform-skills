# Manual outlines

Section order for both documents, and which spec section fills each.

> **Tiers.** Structure is `HOUSE`, derived from two manuals that shipped (418 paragraphs / 52
> tables, and 116 / 10). The `.docx` mechanics are `PLATFORM`. See `docs/EVIDENCE-TIERS.md`.

## Contents
1. Admin manual
2. User manual
3. Why the user manual is a projection
4. Draft vs final

---

## 1. Admin manual

Decimal numbering — a reference document people return to and cite.

| § | Section | From | Omit when |
|---|---|---|---|
| 1 | Introduction | `meta`, `roles[]`, `process[]` | never |
| 2 | System architecture | `lists[]`, `flows[]`, `screens[]` | never |
| 3 | Setting the system up | `lists[]`, `flows[]` | `status: draft` |
| 4 | Using the system | `screens[]`, `bindings[]` | never |
| 5 | Troubleshooting | human-supplied observed failures | draft, or none recorded |
| 6 | Glossary | `glossary[]` | never |

§1 carries three things people actually look up: who does what, who reads which manual, and what
each role can see.

§2 includes a **which-columns-are-filled-in-by-hand** table, split by `populated_by`. It is the
most-consulted table in an admin manual and the cheapest to get wrong.

## 2. User manual

Flat numbering, one number per screen — a document people read once.

| § | Section | From |
|---|---|---|
| 1 | Introduction | `meta`, `roles[]`, `process[]` |
| 2 | Using the app | `screens[]` filtered to user-facing roles |
| 3 | Glossary | `glossary[]` |

**Per screen, exactly three things: heading → screenshot frame → bullet steps.** In the shipped
reference, 9 of the user manual's 10 tables were 1×1 screenshot frames; only the score scale was
a real data table. That is the shape.

No architecture, no column tables, no schema. If a sentence needs a data model to understand, it
belongs in the admin manual.

## 3. Why the user manual is a projection

Its body sections *are* the admin manual's user-facing sections, compressed. Architecture, setup,
troubleshooting and appendices are dropped.

So: generate one source, render twice. Two hand-maintained files diverge inside a week, and the
one that is wrong is always the one somebody is reading.

Two differences beyond dropping sections:

- the user manual omits "what the screen shows you", keeping only what the reader **does**
- it filters `screens[]` to roles whose `manual_sections` include `user`

## 4. Draft vs final

`meta.status` decides. What is absent from a draft is exactly what a user could not validate
anyway — setup and troubleshooting need a built system. What remains is what they can check:
roles, screen walkthroughs, glossary.

That is why a draft is not a degraded manual. It is the validatable subset, and it is the cheapest
requirements test available.
