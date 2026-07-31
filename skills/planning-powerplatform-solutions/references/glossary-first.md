# Glossary first

Why the glossary is built before scoping, data, or screens — and the one question that does most
of the work.

## Contents
1. The failure this prevents
2. The disambiguating question
3. When the answer is "no, they're different"
4. What goes in an entry
5. Where the glossary ends up
6. Running it across departments

---

## 1. The failure this prevents

Two departments describe their work. One calls it a *case*. The other calls it a *request*. Both
descriptions are accurate, both people are competent, and nobody in the room notices anything
wrong — because in each department the word is unambiguous.

Left alone, that produces:

- two lists, `Cases` and `Requests`, holding the same rows
- two screens showing the same data with different labels
- a flow that updates one and not the other
- a report where the totals do not reconcile, discovered in UAT
- a migration to merge them, six months later, with live data in both

The cost is asymmetric, and that asymmetry is the whole argument:

| Mistake | Caught | Cost |
|---|---|---|
| **Two names treated as two things** | UAT, or later | duplicate schema, duplicate screens, data migration |
| **Two things treated as one name** | the first review — someone says "that's not what I meant" | a rename |

So when uncertain, **ask**. And when still uncertain after asking, prefer recording them as
possibly-the-same with an `unresolved` marker over silently splitting them.

This is why the glossary goes first rather than being written up at the end. A term settled in
minute five shapes the data model. The same term settled in hour three means redoing it.

## 2. The disambiguating question

Ask it directly, by name, with both terms in the sentence:

> **"Is a *case* the same thing as a *request*?"**

Not "what do you mean by case?" — that produces a definition of *case*, in isolation, which is
exactly what you already have. The question has to put the two terms in contact.

Follow-ups that resolve it quickly when the first answer is fuzzy:

- **"If I closed the request, would the case be closed too?"** — lifecycle test. Shared lifecycle
  is strong evidence of one thing.
- **"Can one exist without the other?"** — if a case can exist with no request, they are two
  things with a relationship.
- **"Who creates each one, and when?"** — same creator at the same moment is usually one thing.
- **"Would you ever have two cases for one request?"** — establishes cardinality, which you need
  for `relations[]` anyway.
- **"Show me where each one lives today."** — two names for one spreadsheet column settles it
  instantly.

That last one is the strongest. Existing artifacts beat recollection, in an interview exactly as
everywhere else in this project.

## 3. When the answer is "no, they're different"

Good — record both, and record **what distinguishes them**, because that distinction is a field
in the data model.

```yaml
- term: Case
  aka: [ticket]
  definition: >-
    A customer-reported problem. Opened by support, may span multiple requests.
  distinct_from:
    term: Request
    difference: >-
      A Case is the customer's problem; a Request is one action taken to resolve it.
      One Case can have several Requests. Closing the last Request does not close the Case.
```

`distinct_from` is not decoration. It is the sentence you will paste into the overview when
somebody asks the same question in three months, and it usually implies a relation:
one `Case` to many `Request`s.

## 4. What goes in an entry

```yaml
glossary:
  - term: Pre-check
    term_th: การตรวจสอบก่อนอนุมัติ        # localised label, if the project is bilingual
    aka: [precheck, pre check, initial review]
    definition: >-
      One sentence. What it is, in the user's words, not the system's.
    owner_role: middle_team               # who decides what this means, when it is disputed
    unresolved: false                     # true = two departments still disagree
```

Rules for the definition:

- **One sentence.** If it needs a paragraph, the term is hiding two concepts — split it.
- **In the user's words.** "The review three departments do before approval", not "a row in
  `Request_Prechecks` with `Result` not equal to `Pending`". The second is a schema note, and it
  will be wrong the moment the schema changes.
- **`aka` collects every spelling you actually heard**, including the ones you think are typos.
  `precheck`, `pre-check`, `pre check` all appear in real documents and all need to resolve to
  one entry.
- **`owner_role`** matters when a term is disputed. Someone has to be the tiebreak, and naming
  them now avoids a meeting later.

## 5. Where the glossary ends up

One source, four consumers:

| Consumer | Uses it as |
|---|---|
| the spec | the vocabulary every other section is written in |
| the system overview | its glossary section |
| `writing-app-manuals` | the manual's appendix, in both languages |
| the next person | the answer to "wait, what's a pre-check?" |

Because it is in the spec, it stays consistent with everything generated from the spec. A
glossary maintained separately drifts within one project.

## 6. Running it across departments

If the interview spans departments — and a workflow app usually does — the glossary is where the
seams show.

1. **Collect terms per department first**, without reconciling. Let each group use its own words.
2. **Then reconcile in one pass**, out loud, with the disambiguating question for every near-miss.
3. **Record disagreements as `unresolved: true`** rather than picking a winner in the room. A term
   two departments genuinely use differently is a design decision, not a vocabulary problem — it
   usually means the process forks there, and it belongs in Open Questions.
4. **Watch for the reverse case:** one department using one word for two things. A `status` that
   means "workflow stage" to operations and "account state" to finance is two fields, and
   catching it here saves an awkward column later.

A practical tell: if two people can look at the same screen mockup and describe what it shows
using different nouns, the glossary is not finished.
