# System overview — section order

<!-- Read by scripts/render_overview.py. Changing the order here changes the document. -->

The overview is a **rendering of the spec**, never hand-written. Every section below is generated
from a spec section; if something belongs in the document, it belongs in the spec first.

Ordered so a reader who stops early still has the useful part. Most readers stop after §3.

| § | Section | From | Omit when |
|---|---|---|---|
| 1 | Summary | `meta`, `process` | never |
| 2 | Glossary | `glossary[]` | never — it is why readers disagree less |
| 3 | Who does what | `roles[]`, `process[]` | never |
| 4 | The process | `process[]` | never |
| 5 | Screens | `screens[]` | no screens defined |
| 6 | Data | `lists[]`, `relations[]` | no lists defined |
| 7 | Automation | `flows[]` | no flows defined |
| 8 | Open questions | `TODO` markers anywhere in the spec | nothing outstanding |
| 9 | How this was produced | `meta`, spec version, generation note | never |

## Why this order

**Glossary at §2, not in an appendix.** Its job is to stop two readers understanding the same
document differently, which it can only do if they read it before the rest. An appendix glossary
is a reference; a front glossary is a contract.

**Roles before process.** "Who does what" answers the question most readers actually opened the
document with. A process diagram means little until you know which box is yours.

**Data at §6, after screens.** Business readers stop before it and lose nothing; builders want it
and will scroll. Leading with schema loses the business reader on page one.

**Open questions before the colophon, not buried.** An unresolved decision that nobody reads is
an unresolved decision that surfaces in UAT. Numbered, so people can reply "answering Q3".

## Per-section content rules

**§1 Summary** — what the system is for, who uses it, how many stages, and its current status
(`draft` or `final`). Under 150 words. If it needs more, the scope is unclear.

**§2 Glossary** — every term, its `aka` list, one-sentence definition. Terms marked
`unresolved: true` are flagged inline, because a disputed term is more important than a settled
one.

**§3 Who does what** — one row per role: label, responsibilities, data visibility scope, and
which screens they reach. Generated from `roles[]` joined to `screens[].roles`.

**§4 The process** — stages in order, each with owner role, entry and exit condition. The exit
condition is the part people argue about, so it gets its own column.

**§5 Screens** — one row per screen: name, purpose, who sees it, which lists it reads and writes,
which flows it fires. This is `screens[]` rendered directly.

**§6 Data** — one block per list: purpose, kind (list or library), field count, and the field
table with type, who populates it, and choices. Relations rendered as a table **including the
reason** — the reason is what stops a later builder undoing the decision.

**§7 Automation** — one row per flow: name, purpose, trigger kind, what it touches, whether the
app waits for it. Flows called as children are marked as such.

**§8 Open questions** — numbered, each with the spec path it came from, so an answer can be
applied without hunting.

**§9 How this was produced** — spec version and status, and a note that the document is generated
from the spec and should not be edited by hand. Short, but it is what stops the two drifting.

## Format

`render_overview.py` emits **self-contained print-ready HTML**, not a PDF binary.

That is deliberate. The team's environment has no CLI and no local execution, so a PDF library is
not available where the document is actually produced. Every browser prints to PDF, so:

- the HTML is the artifact — one file, no assets, opens anywhere
- **Ctrl/Cmd + P → Save as PDF** produces the PDF, with page breaks and margins already set by
  `@page` CSS
- the same file can be sent as-is to a reader who does not want a PDF

If a headless browser happens to be available in the sandbox, the script converts as well and
says so. It never depends on it.
