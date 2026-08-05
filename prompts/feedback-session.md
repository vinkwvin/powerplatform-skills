# Paste-ready prompt — capture a working session for skill improvement

<!-- v1.3.0 -->

**Where this goes:** at the **end** of any claude.ai chat where you used one of the five skills to
build something real. Before you close it.

**Why then:** a long chat gets compacted, and what survives reconstructs plausibly rather than
accurately. Two minutes now beats an hour of archaeology later — compare
`prompts/harvest-buildchat.md`, the tool for a conversation we left too long, and how much of its
output came back marked `reconstructed`.

**Where the answer goes:** `feedback/<skill>/<YYYY-MM-DD>-<short-topic>.md`, with the corrected
artifact saved beside it under the same basename. See `docs/IMPROVING-SKILLS.md`.

**Do not pre-filter.** Do not decide whether your finding matters, whether someone already reported
it, or whether it was your own fault. Filing is cheap; judging is the intake round's job, and it is
better at it with five reports than with one.

---

## The prompt — copy from here down

We are done. Before I close this chat, write a feedback record so the skill that guided this work can
be improved. Be blunt — this is for fixing the skill, not for reassuring me. An honest account of
what you got wrong is the useful thing here.

### First: the record

**Write this before anything else, and do not output the artifact above it.** The record is short
and it is the part that gets lost — a long artifact emitted first eats the whole response and the
record silently never arrives. That has already happened once. If you can only deliver one of the
two, deliver this one.

YAML, one code block, nothing outside it.

```yaml
meta:
  skill: <which skill guided this>
  skill_version: <the version comment in its SKILL.md, if visible>
  house_style_id: <assets/house-style.yaml meta.style_id, if visible>
  model: <which model you are>
  what_we_built: <one line>
  rounds: <how many times I sent it back for corrections>
  reached_studio_broken: <true|false — did a broken version get as far as being pasted?>
  first_attempt_validated: <true|false — did your FIRST output pass the validator?>

# Verbatim error strings are the single most valuable thing in this file. Each one has become
# a static check — quote them exactly, including the Location, rather than paraphrasing.
studio_errors_verbatim:
  - "<exact text the platform showed, e.g. Name isn't valid. 'TemplateWidth' isn't recognized. Location: Check_Body.Width>"

fixes:
  - element: <the specific control, column, box, action or section — be specific>
    wrong: <what you produced>
    right: <what it had to become>
    i_said: <roughly what I told you, in my words>
    caught_by: validator | studio | me-eyeballing | you-self-corrected
    tier: platform | house | unclear
    rule_status: absent | present-but-wrong | present-and-ignored
    rule_quote: <if present-but-wrong or present-and-ignored, quote the SKILL.md line>
    times: <rounds this same thing took>

friction:
  - what: <something that slowed us down but was not a correctness bug>
    where: <which workflow step>

missing:
  - <something you needed to know, the skill did not say, and you guessed>

unverified_confirmed:
  - <anything you marked UNVERIFIED that Studio or SharePoint then ACCEPTED — this is how the
     catalog grows, so do not omit it>

worked_well:
  - <parts that visibly saved a round. Brief — this stops us deleting them by accident>
```

### On `rule_status` — get this one right

It decides what the fix to the skill actually is, and it is the field people fill in carelessly.

- **`absent`** — the skill never mentioned this. Fix: add a rule.
- **`present-but-wrong`** — the skill told you something and it was incorrect. Fix: correct it.
  Quote the line so it can be found.
- **`present-and-ignored`** — the rule was there, it was correct, and you did not follow it.
  **Say so.** This is the most valuable category and the one you will most want to avoid, because it
  reads as an admission. It is not a criticism of you: it means the rule is buried in a reference,
  ambiguously worded, phrased as advice where an instruction was needed, or crowded out by
  surrounding text. Fix: move or rewrite it.

If you skip that third category, the skill gets longer and no better. A rule nobody follows is worse
than no rule, because it takes up space and creates false confidence.

### On `tier`

- **`platform`** — Power Apps, SharePoint or the flow importer rejected it. Universal.
- **`house`** — it worked; it just did not match this organisation's conventions. May simply mean
  this project differs, in which case the fix is a config value, not a rule.
- **`unclear`** — say `unclear`. Do not guess. A misfiled tier turns one project's preference into
  everyone's law.

### Then: the artifact

Now output the **final working version** of what we built, in full — the version that worked after
all corrections, not your first attempt and not a summary of the differences.

If it is long, say so and stop after the record rather than truncating it. I would rather ask for
the artifact in a second message than lose the record to it — I can always request the files
again, but the account of what went wrong exists only in this conversation.

### Rules

1. **`caught_by: studio` matters most.** Anything that got past the validator to a real paste is a
   validator gap, and the validator is the only thing standing between a teammate and a broken
   artifact. Flag every one.
2. **Be specific about `element`.** "The layout was wrong" is unusable. "The status badge Label
   inside the gallery template" is actionable.
3. **Do not soften `wrong`.** Write what you actually produced, including the embarrassing ones.
4. **Report `first_attempt_validated: false` honestly.** It is the single most useful number in the
   file — it is how we tell whether the skills are getting better rather than just longer.
5. **Answer this even if every other field is empty: what would have saved the most round trips
   if the skill had said it on page one?** One field report's answer was that the validator's own
   success message overclaimed — it said "Safe to paste" when all it could prove was "this
   parses". No structured field would have surfaced that. Counting repeated corrections would have
   scored that project clean, because each fix held first time; the problem was one blind spot
   presenting three times, not one mistake repeated. If something felt structurally wrong rather
   than individually wrong, say so here.
6. **No summary paragraph.** The artifact and the YAML are the whole deliverable.
7. If a section is genuinely empty, return it empty. `friction: []` is a real answer, and padding it
   costs someone reading time later.
8. **Quote any value containing a colon-space.** This record is YAML, so the same rule the skill
   enforces applies to the report about it:

   ```yaml
   wrong: Control: Image@2.2.0        # BREAKS — colon-space starts a nested mapping
   wrong: "Control: Image@2.2.0"      # correct
   ```

   An unparsable record is two minutes of your time thrown away. `scripts/triage_feedback.py` will
   name the file and the reason rather than skipping it quietly, but it is cheaper to quote it now.
