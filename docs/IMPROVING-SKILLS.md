# Improving the skills

<!-- v1.0.0 -->

How a correction someone made in a Claude chat on Tuesday becomes a rule everyone benefits from.

The suite was built from **one** system. Every project after it hits something those artifacts never
contained. This document is the difference between a snapshot that slowly goes stale and a toolset
that gets better every time someone uses it.

## Contents
1. The loop in one page
2. Stage 1 — Capture
3. Stage 2 — File
4. Stage 3 — Triage
5. Stage 4 — Decide what to change
6. Stage 5 — Regression-proof it
7. Stage 6 — Release
8. Stage 7 — Measure
9. Anti-patterns

---

## 1. The loop in one page

```
   working chat                     repo                        release
   ────────────                     ────                        ───────
   build something
        │
        ├─ paste prompts/feedback-session.md      ← 2 minutes, at the END
        │        │
        │        └─→ corrected artifact + YAML record
        │                    │
        └────────────────────┴─→ feedback/<skill>/YYYY-MM-DD-topic.{md,ext}
                                      │
                                      ├─ scripts/triage_feedback.py  → ranked actions
                                      │
                                      ├─ validator gaps first
                                      ├─ rule_status decides the edit
                                      ├─ every confirmed fix → a new eval
                                      │
                                      └─→ version bump, CHANGELOG, re-zip
                                                  │
                                                  └─→ "re-install, here's what changed"
```

Two roles. **Anyone using a skill** does Stage 1 and 2 — two minutes, no judgement required.
**Whoever runs an intake round** does 3 through 7, in a fresh Claude Code session on this repo,
opening with *"Read PROJECT-BRIEF.md. We're on Session 11."*

### Stage 1 and 2 must work without this repository

Most people running these skills do not use GitHub and should never have to. The loop above is
what the *maintainer* sees; what a teammate sees is one zip in and one file out.

- **In** — `python3 scripts/build_starter_pack.py` builds the single attachment: five skill zips,
  the Thai handoff PDF, and the two prompts. See [`handoff/README.md`](../handoff/README.md).
- **Out** — they paste [`team-quick-feedback.md`](../prompts/team-quick-feedback.md), save what
  Claude writes, and send it back on Teams. The maintainer drops it into `feedback/<skill>/`.

There is also a lane that does not come back here at all. A project with a different palette or
type scale is a `HOUSE` difference, not a finding, and
[`project-style-override.md`](../prompts/project-style-override.md) settles it inside that one
chat. Routing style differences upstream is how a house convention gets mistaken for a platform
law — see the anti-pattern in §9.

Keep the two entry points honest: if filing requires a repo, a checkout, or a command line, the
people whose corrections are most worth having will not file.

## 2. Stage 1 — Capture

**When:** at the end of a chat where you used a skill to build something real. Before you close it.

**Why then and not later:** a long conversation gets compacted. What survives is a
recency-weighted summary that reconstructs plausibly rather than accurately. Ask on Friday about
Tuesday's chat and you get fiction with the texture of fact. We learned this the hard way — see
`prompts/harvest-buildchat.md`, which is the archaeology tool for a conversation where we left it
too long, and note how much of its output came back marked `recall: reconstructed`.

**How:** paste [`prompts/feedback-session.md`](../prompts/feedback-session.md). That is the whole
ask.

**What it collects, and why in that order:**

1. **The corrected artifact** — the file that finally worked. This is the valuable half. It is
   checkable against a validator and diffable against the first attempt, which makes it ground truth
   in exactly the way the original 17 screens are.
2. **A structured record** — what went wrong per element, how many rounds it took, whether the
   validator caught it or Studio did, and what the skill's rule status was.

A record without an artifact is still worth filing. It just cannot promote a rule on its own.

## 3. Stage 2 — File

```
feedback/<skill>/2026-08-14-approval-screen.md        the YAML record
feedback/<skill>/2026-08-14-approval-screen.pa.yaml   the corrected artifact
```

Same basename, dated, one folder per skill. That is it.

**Do not pre-filter.** Do not decide whether your finding is important, whether someone already
reported it, or whether it was your own fault. Intake is deliberately cheap and unfiltered; judging
is the intake round's job and it is much better at it with five reports than with one.

## 4. Stage 3 — Triage

`python3 scripts/triage_feedback.py` reads every record and produces a ranked action list.

Ranking, highest first:

| Priority | Signal | Why it ranks there |
|---|---|---|
| 1 | `caught_by: studio` | reached a real paste. The validator is the only thing between a teammate and a broken artifact, and it failed |
| 2 | same `element` in reports from **two different people** | independent corroboration beats one report claiming `times: 5` |
| 3 | `rule_status: present-and-ignored` | the rule exists and did not land. Fixable without adding length |
| 4 | `times >= 3` in one report | meets the "corrected 3+ times" bar the project already uses for inline rules |
| 5 | `rule_status: present-but-wrong` | actively misleading, but at least it was noticed |
| 6 | `rule_status: absent`, single report | real, and the easiest kind to over-act on |

**Then assign a tier before deciding anything** (see [`EVIDENCE-TIERS.md`](EVIDENCE-TIERS.md)):

- **`PLATFORM`** — Power Platform rejected it. Universal, urgent, applies to every project.
- **`HOUSE`** — it worked, it just did not match our conventions. May mean *this project differs*,
  in which case the fix is a config value, not a rule.
- **`EXAMPLE`** — a fact about that project. File it, change nothing.

The tier question is the one that stops the suite drifting into a house style dressed as platform
law. A `HOUSE` finding from a project with a different design system is not a bug in the skill.

## 5. Stage 4 — Decide what to change

`rule_status` maps to an action. This is the core of the method:

| `rule_status` | Fix | Watch out for |
|---|---|---|
| `absent` | add a rule | the tempting one. A skill that only grows becomes a skill nobody finishes reading, and an unread rule is worth nothing |
| `present-but-wrong` | correct it, and check the reference it came from | if a written doc was the source, that doc is now suspect everywhere |
| `present-and-ignored` | **move or rewrite it** — inline it, make it an instruction rather than advice, or shorten what surrounds it | the highest-value category, and the one a self-report avoids |

**On `present-and-ignored`.** A rule that is present, correct, and not followed is not an information
problem — it is a placement or wording problem. Adding a second rule saying the same thing louder
makes it worse. Options that work:

- move it from `references/` into the `SKILL.md` body
- rewrite advice as an instruction ("prefer X" → "use X. Never Y.")
- attach the count, so the reader knows it is measured rather than aesthetic
- attach the *failure*, so ignoring it has a visible cost
- delete something nearby, so it competes with less

**Validator gaps outrank rule changes.** If a defect reached Studio, add the check first. A rule
tells a model what to do; a validator stops the artifact regardless of whether the model read it.
The validator is the load-bearing part.

Also legitimate: **deleting a rule**. If a report shows a rule was correct-but-irrelevant, or its
`HOUSE` value does not generalise, take it out of the body and into a reference — or out entirely.

## 6. Stage 5 — Regression-proof it

**Every confirmed fix becomes an eval.** Add a case to `evals/<skill>/` using the corrected artifact
as the fixture, with the specific failure in `fail_if`.

Without this the loop leaks: a rule gets fixed, a later edit shortens the wrong paragraph, and the
same defect returns six months later looking novel. The eval is what makes the fix permanent.

Evals run in fresh **claude.ai** chats on Sonnet and Haiku — a different runtime from Claude Code,
and the one the team actually uses. A skill that only works on the strongest model has not been
tested where it will live.

## 7. Stage 6 — Release

1. Bump the `<!-- vX.Y.Z -->` line in the changed `SKILL.md`.
   - patch: wording, a reference edit · minor: a new rule or validator check · major: a workflow or
     output-format change
2. Add a `dist/CHANGELOG.md` line saying what changed and **whether a teammate needs to care**.
3. Re-zip into `dist/`.
4. **Tell the team to re-install.**

Step 4 is the one that gets skipped, and skipping it wastes the whole round. Skills on claude.ai are
per-account and **do not sync** — an improved skill sitting in `dist/` helps nobody. An intake round
is not finished when the skill is fixed; it is finished when the team is running the new one.

## 8. Stage 7 — Measure

Without a number you cannot tell improvement from churn. Two metrics, both already in the feedback
records:

**Rounds-to-clean** — `meta.rounds` from each report. How many times did the user send it back? Track
the median per skill. If it is not falling, the added rules are not helping.

**Validator catch rate** — the share of `fixes[]` entries with `caught_by: validator` versus
`caught_by: studio` or `me-eyeballing`. Rising is the goal: it means defects are being stopped in the
sandbox rather than in the browser.

`scripts/triage_feedback.py --metrics` prints both. Put them at the top of each intake round's
report. A round that adds nine rules and moves neither number did nine rules' worth of harm to
readability and nothing else.

## 9. Anti-patterns

**Only ever adding.** The most common failure. Length has a cost paid by every future reader, and a
Haiku-sized context spent on a rule that fires once a year is a rule that crowds out one that fires
weekly.

**Treating a HOUSE finding as PLATFORM.** Project B has a different type scale, so a warning fires,
so someone "fixes" the skill — and now Project A's screens warn. Change the config, not the rule.

**Filing a report and doing nothing visible.** A teammate who files twice and sees no response stops
filing, and you lose the input permanently. Every intake round reports what it did **and what it did
not act on, with the reason**.

**Fixing the rule and skipping the eval.** The fix survives until the next edit.

**Fixing the rule and skipping the re-install notice.** The fix never reaches anyone.

**Trusting the model's account over the artifact.** The record explains; the artifact proves. When
they disagree, the artifact wins — the same rule that governs the rest of this project.
