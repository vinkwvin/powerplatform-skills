# Paste-ready prompt — capture a working session for skill improvement

<!-- v1.0.0 -->

**Where this goes:** at the **end** of any claude.ai chat where a teammate used one of the five
skills to build something real. While it is still fresh — before the chat is closed or compacted.

**Who runs it:** the teammate who did the work. Not Vin, not later. The point is that memory is
intact, which is exactly what `prompts/harvest-buildchat.md` had to work without.

**Where the answer goes:** `feedback/<skill>/<yyyy-mm-dd>-<short-topic>.md`, plus the corrected
artifact alongside it. See `feedback/README.md`.

**The most important part is not the prompt.** It is the **corrected artifact** — the file that
finally worked after fixing. That is ground truth and mechanically checkable. The prose below is
context for it.

---

## The prompt — copy from here down

We are done. Before I close this chat, I need you to write a feedback record so the skill that
guided this work can be improved. Be blunt — this is for fixing the skill, not for reassuring me.

### First, the artifact

Output the **final working version** of what we built, in full, in one code block. The version
that actually worked after all corrections — not your first attempt, not a summary of the
differences. If it is too long for one block, say so and output it in labelled parts.

### Then, the record

YAML, one code block, no prose outside it.

```yaml
meta:
  skill: <which skill guided this — e.g. generating-powerapps-yaml>
  skill_version: <the version comment in its SKILL.md, if you can see it>
  what_we_built: <one line>
  rounds: <how many times I sent it back for corrections>
  reached_studio_broken: <true|false — did a broken version get as far as being pasted?>

fixes:
  - element: <the specific control, box, section, field, or action — be specific>
    wrong: <what you produced>
    right: <what it had to become>
    i_said: <roughly what I told you, in my words>
    caught_by: validator | studio | me-eyeballing | you-self-corrected
    rule_status: absent | present-but-wrong | present-and-ignored
    rule_quote: <if present-but-wrong or present-and-ignored, quote the SKILL.md line>
    times: <how many rounds this same thing took>

friction:
  - what: <something that slowed us down that was not a correctness bug>
    where: <which part of the workflow>

missing:
  - <something you needed to know and the skill did not tell you, so you guessed>

worked_well:
  - <parts of the skill that visibly saved a round — brief, so we do not delete them by accident>
```

### On `rule_status` — get this one right

It decides what the fix to the skill actually is, and it is the field people fill in carelessly.

- **`absent`** — the skill never mentioned this. Fix: add a rule.
- **`present-but-wrong`** — the skill told you something and it was incorrect. Fix: correct the
  rule. Quote it so we can find it.
- **`present-and-ignored`** — the rule was there, correct, and you did not follow it. **Say so.**
  This is the most valuable category and the one you will be most tempted to avoid. It means the
  rule is buried, ambiguous, in a reference file when it should be inline, or phrased as advice
  when it needed to be an instruction. Fix: move or rewrite it. If you skip this category the
  skill gets longer and no better.

### Rules

1. **`caught_by: studio` matters most.** Anything that got past the validator to a real paste is
   a validator gap, and the validator is the only thing standing between a teammate and a broken
   paste. Flag every one.
2. **Be specific about `element`.** "The layout was wrong" is unusable. "The status badge Label
   inside the gallery template" is actionable.
3. **Do not soften `wrong`.** Write what you actually produced.
4. **No summary paragraph.** The artifact and the YAML are the whole deliverable.
5. If a section is genuinely empty, return it empty. `friction: []` is a real answer.
