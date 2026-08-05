# feedback/ — field reports from real use

Where a working session's lessons land so they can be folded back into the skills.

## Why this exists

The five skills are built from one project's artifacts. Every project after that one will hit
things those 17 screens never contained. Without an intake path, each teammate rediscovers the
same corrections privately and the skills never improve.

## Layout

```
feedback/
├── generating-powerapps-yaml/
│   └── 2026-08-14-approval-screen.md      ← the YAML record
│   └── 2026-08-14-approval-screen.pa.yaml ← the corrected artifact  ← more important
├── building-sharepoint-lists/
├── planning-powerplatform-solutions/
├── building-powerautomate-flows/
└── writing-app-manuals/
```

**Always both files.** The record says what went wrong; the artifact proves it. The artifact is
Rank 1 and mechanically checkable — the same standing as the original 17 screens. The record is
Rank 4 context that explains it.

A record with no artifact is still worth filing, but it cannot promote a rule on its own.

## How a teammate files one

1. At the end of the working chat — before closing it — paste `prompts/feedback-session.md`.
2. Save the corrected artifact and the YAML record into the right skill folder, dated.
3. That is all. No triage, no judgement about whether it matters. Intake is cheap; deciding is
   the reviewing session's job.

## Where this folder sits now

This is the repository's copy. **The team's copy is a shared folder** — SharePoint or Teams —
laid out the same way, because they have no checkout and no maintainer to send files to.

| | Here | The team |
|---|---|---|
| Where records land | `feedback/<skill>/` | `บันทึก/<skill>/` in the shared folder |
| Who reads them | whoever runs an intake session | whoever runs the improvement round — anyone |
| What they run | `scripts/triage_feedback.py`, then edit by hand | `prompts/improve-the-skill.md`, pasted with the zip attached |
| Proof the fix is safe | `evals/`, run deliberately | `scripts/self_check.py`, bundled in the zip and run by the chat |

Everything below still describes the method. It is now executed by
[`prompts/improve-the-skill.md`](../prompts/improve-the-skill.md) rather than by a person with a
clone — so if you change the method, change that prompt too, or the two will drift and the prompt
is the one that is actually running.

`2026-08-05-chopchop.md` is the worked example. Read it before writing a first record.

## What happens to it

An improvement round reads everything new here and:

- **Validator gaps first.** Any `caught_by: studio` entry is something the validator let through
  to a real paste. Those become validator checks before anything else is considered.
- **`rule_status` decides the fix.** `absent` → add a rule. `present-but-wrong` → correct it.
  `present-and-ignored` → the rule exists and failed to land, so move it inline, rewrite it as an
  instruction, or shorten what surrounds it. That third case makes skills *better without making
  them longer*, which is the only sustainable direction.
- **Corroboration across reports.** The same `element` appearing in reports from two different
  teammates on two different projects is stronger evidence than one report at `times: 5`.
- **Every confirmed fix becomes a probe.** A small file under the skill's `tests/probes/` that
  produces the error the new rule is meant to produce, with its counts recorded in
  `tests/expected.json`, so the failure cannot come back silently. In this repo it also becomes an
  eval under `evals/<skill>/`.
- **Version bump and changelog**, then a re-packaged `.zip`.

## The check that cannot be talked around

Before any change ships, `scripts/self_check.py` runs the validator over the 17 screens that
compiled in Studio. **If a new rule makes one of them warn, the rule is wrong.** Those screens
shipped; a plausible inference does not outrank them. This has already caught one reasonable-looking
rule that fired on 20 working buttons.

The numbers live in `tests/expected.json`. Changing one to make a failure go away is the same as
deleting the check, and the only thing stopping that is whoever is reading the round's output.

## The thing that will break this

Skills on claude.ai are per-account and do not sync (D5). An improved skill sitting in a shared
folder helps nobody until every teammate downloads and re-uploads it. So a round is not finished
when the skill is fixed — it is finished when the team has been told to re-install, with a
one-line changelog saying what changed and whether they should care.

The other thing that breaks it: filing a report and seeing nothing happen. Every round has to say
what it did **and what it did not act on, with the reason**. A teammate who files twice into
silence stops filing, and that input is gone permanently.
