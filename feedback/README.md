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

## What happens to it

A recurring intake session (Session 11) reads everything new here and:

- **Validator gaps first.** Any `caught_by: studio` entry is something the validator let through
  to a real paste. Those become validator checks before anything else is considered.
- **`rule_status` decides the fix.** `absent` → add a rule. `present-but-wrong` → correct it.
  `present-and-ignored` → the rule exists and failed to land, so move it inline, rewrite it as an
  instruction, or shorten what surrounds it. That third case makes skills *better without making
  them longer*, which is the only sustainable direction.
- **Corroboration across reports.** The same `element` appearing in reports from two different
  teammates on two different projects is stronger evidence than one report at `times: 5`.
- **Every confirmed fix becomes an eval.** Added to `evals/<skill>/` using the corrected artifact
  as the fixture, so the failure cannot come back silently.
- **Version bump and changelog**, then a re-packaged `.zip` in `/dist/`.

## The thing that will break this

Skills on claude.ai are per-account and do not sync (D5). An improved skill sitting in `/dist/`
helps nobody until every teammate downloads and re-uploads it. So an intake round is not finished
when the skill is fixed — it is finished when the team is told to re-install, with a one-line
changelog saying what changed and why they should care.

Keep `dist/CHANGELOG.md` current for exactly this reason.
