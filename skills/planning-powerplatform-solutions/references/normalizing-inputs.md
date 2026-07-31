# Normalizing what they arrive with

Turn a flowchart, ER diagram, process document, or existing spreadsheet into spec sections
*before* asking a single question. Reading first is the difference between an interview that
feels informed and one that feels like a form.

## Contents
1. The order of operations
2. A flowchart or process diagram
3. An ER diagram or data model
4. An existing spreadsheet
5. A process document or SOP
6. A screenshot or whiteboard photo
7. Nothing at all
8. When two inputs disagree

---

## 1. The order of operations

1. **Read everything.** All of it, before the first question.
2. **Extract nouns → glossary candidates.** Every distinct noun is a term until proven otherwise.
3. **Extract verbs → process stages and flows.**
4. **Extract actors → roles.**
5. **Draft what you can into the spec**, marking every inference `TODO — confirm`.
6. **Then interview**, using the draft as the agenda: *"I read this as five stages, here they
   are — what did I get wrong?"*

That last move matters more than it looks. Correcting a wrong draft is faster and more accurate
than answering an open question, and it shows you did the reading.

## 2. A flowchart or process diagram

| In the diagram | Becomes |
|---|---|
| a swimlane | a `roles[]` entry |
| a box in a lane | a `process[]` stage, `owner_role` = the lane |
| an arrow label | the exit condition of the stage it leaves |
| a diamond | a decision → usually a `choice` field plus a branch in a flow |
| a loop back | a rejection or return path — confirm it explicitly, it is often drawn but not described |
| a parallel split | stages that run at once → a gate flow that waits for all branches |
| a terminator | the first `entry` and the last `exit` |

**What flowcharts systematically leave out**, so ask:

- what happens on rejection at each stage — arrows usually only show forward
- who can see what, as opposed to who acts
- what data each box reads and writes
- timing: is anything on a schedule rather than an event

## 3. An ER diagram or data model

| In the diagram | Becomes |
|---|---|
| an entity | a `lists[]` entry |
| an attribute | a field, with its type |
| PK | a candidate for `Title` as the natural key |
| FK | a `relations[]` entry — **as a text key, never a Lookup** |
| a crow's foot | cardinality, which decides which side holds the key |
| a many-to-many | a junction list, which the diagram may not have drawn |

**Translate the FK deliberately and say so out loud.** An ER diagram implies a foreign-key
constraint; SharePoint has no such thing, and the delegable expression of that relationship is a
text column. Record the reason in `relations[].reason` at the moment you make the change, because
the person reading the ER diagram later will otherwise think the spec is wrong.

## 4. An existing spreadsheet

The best input there is. A spreadsheet in daily use records what people actually capture, which is
usually narrower and stranger than what they say they need.

`building-sharepoint-lists/scripts/xlsx_to_spec.py` extracts columns and types directly. Then
read the **data**, not just the headers:

- a column that is empty in 90% of rows is optional, or dead
- a column with six distinct values is a `choice`, whatever its header says
- a text column holding `Y`/`N`/blank is a `bool` that needs a third state
- two columns that are never both filled are one field plus a discriminator
- a column called `Notes` doing three jobs is three fields waiting to be split
- leading zeros, dates stored as text, and merged cells all indicate what the real constraints are

Ask about anything strange rather than normalizing it silently. Odd data usually encodes a real
business rule nobody remembered to mention.

## 5. A process document or SOP

Written procedures describe the **happy path in the present tense** and skip exceptions. Extract
the stages, then ask specifically:

- "what happens when this step fails?"
- "who does this when the named person is away?"
- "is this still what actually happens?" — SOPs age badly, and people follow the current practice
  rather than the document

## 6. A screenshot or whiteboard photo

Treat as visual ground truth for **layout and grouping**, not for values. Field labels in a
screenshot are reliable; the data in them is usually dummy. Cross-check against any HTML or
spreadsheet you were given, and prefer those for exact strings.

A screenshot of an existing system is also a scope trap: everything visible reads as required.
Ask which parts are actually used.

## 7. Nothing at all

They describe it verbally. Fine — but a process with no artifact anywhere is a warning worth
naming gently: it usually means the process is less settled than it sounds, and different people
will describe it differently.

Two moves that help:

- **Ask for one real example, end to end.** "Walk me through the last one you did." A concrete
  instance surfaces the exceptions that a general description smooths over.
- **Ask two people separately** if you can. Where their accounts diverge is where the spec needs
  a decision rather than a description.

## 8. When two inputs disagree

Common, and informative. The flowchart says four stages; the spreadsheet has six status values.

**Do not reconcile silently.** The mismatch is usually a real finding: a stage that was added and
never documented, or two statuses that mean the same thing.

Rank the sources the same way the rest of this project does — **an artifact in current use beats a
document about it.** A spreadsheet with live data outranks an SOP written two years ago, which
outranks a recollection.

Then say what you found: *"the diagram shows four stages, but the spreadsheet has six statuses —
are these two extra ones stages, or sub-states of one?"* That question is usually worth the whole
rest of the interview.
