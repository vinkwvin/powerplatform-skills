# Interview guide

The question set, in passes. Each pass fills specific spec sections, so you always know why you
are asking and when to stop.

Domain-agnostic: nothing here assumes what the app is for.

## Contents
1. How to run it
2. Pass 0 — frame
3. Pass 1 — glossary
4. Pass 2 — the process
5. Pass 3 — the data
6. Pass 4 — the screens
7. Pass 5 — the automation
8. Pass 6 — the wiring
9. Questions not to ask
10. When to stop

---

## 1. How to run it

**One pass at a time.** Ask the pass, draft that section of the spec, show it, correct it, move
on. Six short exchanges beat one long questionnaire — people answer concrete follow-ups far
better than abstract openers.

**Skip what the input already answered.** If they arrived with a flowchart, Pass 2 is mostly
confirmation. Asking anyway signals you did not read it.

**Draft in front of them.** Showing `RequestStatus: [Draft, Submitted, Approved]` gets a
correction in seconds. Asking "what statuses do you need?" gets a pause and an incomplete list.

**Never ask two questions in one sentence.** You will get one answer and not know which.

## 2. Pass 0 — frame → `meta`

Four questions, then move on. This pass should take two minutes.

- **What is this replacing?** A spreadsheet, a paper form, email, or nothing. The answer predicts
  most of the data model, and "nothing" is a warning sign — a process with no current artifact is
  usually not as settled as people think.
- **Who asked for it, and what happens if it does not get built?** Establishes whether there is a
  real deadline and a real owner.
- **Roughly how many records per month?** One number, and it decides whether delegation matters
  (`references/delegation.md` in the SharePoint skill). Under a few hundred, most things work;
  over a few thousand, design choices start mattering.
- **One language or two?** Sets `meta.languages` and whether every label needs a `*_th` sibling.

## 3. Pass 1 — glossary → `glossary`

**Before anything else.** See `references/glossary-first.md` for the method and the
disambiguating question.

- **"Walk me through it in your own words."** Write down every noun. Those are your candidate
  terms.
- For each near-duplicate: **"Is a *X* the same thing as a *Y*?"**
- **"Is there a word your team uses that another team would not understand?"**
- **"Is there a word both teams use that might mean different things?"** — the reverse case, and
  the one people forget.

Confirm the glossary out loud before Pass 2. Everything after this is written in its vocabulary.

## 4. Pass 2 — the process → `process`, `roles`

- **"Who touches this, in order?"** → the stages, and the role that owns each.
- **"What has to be true before it moves to the next person?"** → exit criteria, and usually a
  validation rule in a flow.
- **"What happens when it goes wrong — rejected, returned, cancelled?"** People describe the
  happy path unprompted and the unhappy path only when asked. The unhappy path is where most of
  the complexity lives.
- **"Can two people work on it at once, or is it strictly one at a time?"** → parallel stages,
  which change the flow design substantially.
- **"Who can see everything? Who can see only their own?"** → `roles[].visibility_scope`.
- **"Who is the tiebreak when two departments disagree?"** → useful in the glossary too.

## 5. Pass 3 — the data → `lists`, `relations`

Start from an artifact if one exists. A real spreadsheet answers this pass faster than any
question, and `xlsx_to_spec.py` extracts it directly.

- **"What is one row?"** Ask per list. If the answer needs "and", it is two lists.
- **"What do you need to record about it?"** → fields. Then, per field: **"who types this?"** →
  `populated_by`. If nobody types it, it is `automation`.
- **"Which of these must be filled in before submitting?"** → `required`.
- **"For this one, is it free text or a fixed list?"** → `text` vs `choice`. If fixed:
  **"list them all for me"** — a Choice column rejects anything not enumerated.
- **"Is there ever an 'other, please specify'?"** → the `other_field` escape.
- **"How do these two connect?"** → `relations`. Always a text key, and record the reason.
- **"Does anything need a file attached?"** → a document library, not a list.
- **"Who last touched this row, and when — do you need to know?"** Almost always yes → the
  `<Verb>By` / `<Verb>At` pair.

## 6. Pass 4 — the screens → `screens`, `roles`

- **"What does each person see when they open the app?"** One screen per role per stage is the
  usual starting shape.
- **"What can they do on that screen?"** → the actions, which become buttons and flows.
- **"What should they not be able to see?"** → `screens[].roles`, and sometimes a filter.
- **"Is there a screen where someone just watches?"** → a dashboard or tracking screen. Easy to
  forget and always asked for later.
- **"Where do they land after they finish?"** → navigation.

## 7. Pass 5 — the automation → `flows`

- **"What should happen automatically when X?"** → the trigger.
- **"Who needs to be told, and when?"** → notification flows. If more than two flows send mail,
  make one child flow they all call rather than duplicating the logic.
- **"Does the app wait for the answer, or carry on?"** → `request_response` vs `automated`. It
  changes the trigger kind and whether the flow ends in a response.
- **"Is there anything that must not happen twice?"** → a guard, and possibly a single-writer
  pattern for anything generating a sequence number.
- **"What runs on a schedule rather than an event?"** → recurrence triggers, easy to miss because
  nobody thinks of them as part of the process.

For each flow, record the trigger kind. A `sharepoint_item` trigger needs `splits_on`; the others
do not.

## 8. Pass 6 — the wiring → `variables`, `bindings`

Mostly derived rather than asked. Work from `screens[]` and `lists[]`:

- every control that shows or captures a value → a `bindings[]` row
- every value carried between screens → a `gbl*` global
- every list loaded into a gallery → a `col*` collection
- every show/hide toggle → a `var*` context variable

Ask only where it is genuinely ambiguous: **"when they set this on screen A, does screen B need
to know?"** → global, versus screen-local.

## 9. Questions not to ask

- **"What are your requirements?"** — produces a wish list, not a spec.
- **"Do you want it to be user-friendly?"** — no information content.
- **"Should we use SharePoint or Dataverse?"** — an implementation question dressed as a
  requirement, and not theirs to answer.
- **Anything the artifacts already answer.** Read first.
- **Anything you can derive.** Deriving `bindings[]` and showing it beats asking about it.
- **"Is there anything else?"** at the end — invites scope creep at the worst moment. Ask
  instead: **"is there anything in what I've written that's wrong?"**

## 10. When to stop

**When `validate_spec.py` exits clean and the glossary is confirmed.**

That is the whole rule. The validator checks that every binding resolves, every screen has a
role, every relation states a reason, every field says who populates it — which is a decent
proxy for "specified enough to build".

Anything still open at that point becomes a `TODO` in the spec and a line in the overview's Open
Questions. That is a better outcome than a longer interview: an open question in writing gets
answered by the right person later, while an interview answer given under pressure to finish gets
recorded as fact.
