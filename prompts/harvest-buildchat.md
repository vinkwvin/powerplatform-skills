# Paste-ready prompt — harvest the Account Closure build chat

<!-- v1.0.0 -->

**Where this goes:** the Claude Code conversation that built the INVX Account Closure
prototype — the one that produced `pages/*.html`, `tools/page-generator/`, and the 17
`.pa.yaml` screens.

**Where the answer goes:** save the YAML block it returns verbatim as
`ledger/07-buildchat-raw.md`. Do not clean it up, do not delete entries you disagree with.
Session 2 verifies it against the 17 artifacts and decides what survives.

**Why the constraints are worded so hard:** that chat has compacted many times, so it
reconstructs plausibly rather than accurately. Everything below is designed to make it
easier for it to admit uncertainty than to fabricate. Do not soften them.

---

## The prompt — copy from here down

I need you to report on **your own behaviour in this conversation** — not to re-derive
Power Apps or Power Automate rules.

Context: you built the INVX Account Closure prototype in this chat. I am now building
reusable Agent Skills from what that work taught us, so the next person does not
rediscover the same corrections. What I need from you is the record of what went wrong
and what I had to keep telling you.

### Output

Six lists, as YAML, in one code block. No preamble, no closing summary, no prose outside
the block.

1. `standing_instructions` — rules I gave you that applied for the rest of the chat.
2. `corrections` — things I corrected **more than once**. This is the list I care about
   most: if I corrected the same thing three times, it is a rule, and it belongs in a skill.
3. `recurring_mistakes` — errors you made repeatedly, including ones you caught yourself
   before I said anything.
4. `abandoned` — approaches we tried and dropped, with the reason. I need the reasoning so
   a future skill does not re-propose them.
5. `flow_attempts` — any Power Automate work in this chat at all. Did we build, export, or
   import a flow? If yes: what happened, what failed, and whether an export `.zip` exists
   anywhere. If no such work happened, return `flow_attempts: []`. That empty answer is
   genuinely useful to me — do not pad it.
6. `sharepoint_gotchas` — anything about list or column setup that bit us: type choices,
   naming, cross-list references, values a column rejected.

### Required fields on every entry

- `rule` — one sentence, imperative.
- `times` — integer. Distinct occasions this came up. Estimate if you must and say so.
- `source` — exactly one of:
  - `explicit` — I stated it in words
  - `corrected` — I rejected your output and you changed it
  - `inferred` — you concluded it yourself and I never confirmed it
- `evidence` — the file, screen, or artifact that demonstrates it
  (`07_Middle_VerifyDocs.pa.yaml`, `pages/sales-screen-1.html`, …). If no artifact
  demonstrates it, write `none`. **Do not invent a filename.**
- `recall` — `direct` if you actually remember the exchange; `reconstructed` if you are
  inferring it from what the code currently looks like.

### Hard constraints

1. **Do not read the `.pa.yaml` files and report their contents as rules you learned.**
   Those files are being analyzed separately and empirically. If you restate what is in
   them, you will look like independent confirmation when you are only an echo — and a
   wrong rule will get promoted on the strength of agreeing with itself. Report only what
   happened *between you and me*.
2. **Mark reconstruction honestly.** This conversation has been compacted many times.
   Anything you are reconstructing rather than remembering must say `recall: reconstructed`.
   A short honest list is worth far more to me than a long confident one. I discard what I
   cannot verify, so an admitted gap costs you nothing and a confident fabrication costs me
   real time.
3. **No tutorials.** I do not need explanations of what a Gallery or a connector is.
4. Order every list by `times`, descending.
5. If you do not remember enough to fill a list, return it empty. Empty is a valid answer.

Output the YAML block and stop.
