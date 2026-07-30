# Power Platform Skill Suite

Five Claude Agent Skills that take a Power Platform delivery team from **requirement → agreed
design → working Power Apps + SharePoint + Power Automate**, using short prompts and Pro-plan
token budgets.

<!-- v1.0.0 -->

## The problem this solves

We build in a closed environment: **no Power Platform CLI, no local execution.** Everything Claude
produces gets copy-pasted or uploaded into a browser. So a generated artifact has to be correct on
the first paste — there is no cheap retry loop, and a failed paste costs a real round trip through
Studio.

Generic AI help does not survive that constraint. Ask any model for Power Apps YAML and it will
produce something plausible: a control type that does not exist, a property the platform rejects, a
value that breaks the YAML parse. It looks right and it does not compile.

These skills exist to close that gap. Every rule in them was measured against artifacts that
**actually worked** — 17 screens that compiled in Studio, 131 SharePoint columns in production, a
real flow export from our own tenant. Where a rule has a number attached, it is not an opinion.

## The five skills

Mutually exclusive by the artifact they produce, so a request routes to exactly one.

| Skill | Produces | Reads |
|---|---|---|
| `planning-powerplatform-solutions` | `solution-spec.yaml`, HTML mockup, `system-overview.pdf` | a requirements interview |
| `generating-powerapps-yaml` | `*.pa.yaml` | spec `screens[]`, `variables[]`, `bindings[]` |
| `building-sharepoint-lists` | provisioning `.xlsx` + column script | spec `lists[]`, `relations[]` |
| `building-powerautomate-flows` | legacy import `.zip` | spec `flows[]` |
| `writing-app-manuals` | admin `.docx` + user-friendly `.docx` | spec `screens[]`, `roles[]`, `glossary[]` |

**The spec is the product.** The planner emits one machine-readable `solution-spec.yaml`; every
builder reads only its own section; the PDF and the manuals are *renderings* of it. A PDF is lossy,
expensive to re-read, and cannot be validated — so it is never the source of truth.

## Status

| Session | Deliverable | State |
|---|---|---|
| 1 | Measure the working artifacts → `ledger/01`, `ledger/02` | done |
| 2 | Build-chat harvest → `ledger/07`, `ledger/08` | raw captured |
| 3 | Skill audit, flow rules, list rules → `ledger/03`–`05` | done |
| 4 | The spec contract → `spec/` | done |
| 5 | `generating-powerapps-yaml` | done |
| 6 | `building-sharepoint-lists` | done |
| 7 | `planning-powerplatform-solutions` | not started |
| 8 | `building-powerautomate-flows` | not started |
| 9 | `writing-app-manuals` | not started |
| 10 | Lint and package → `dist/*.zip` | not started |
| 11 | **Feedback intake — recurring** | process defined |

## Install (Pro plan, ~2 minutes)

1. Download the `.zip` for the skill you want from `dist/`.
2. In claude.ai: **Settings → Capabilities → Skills → Upload skill**.
3. Upload the zip. Done.

**Skills are per-account and do not sync.** Every teammate installs their own copy, and when a
skill is improved everyone re-downloads. `dist/CHANGELOG.md` says what changed and whether you need
to bother.

## Use

**One stage per chat.** Start a fresh conversation for each skill. Not a style preference — a
budget one: a planning interview plus three builders in one thread burns context on material the
later stages do not need, and the quality drops before the tokens run out.

A normal project:

```
chat 1   planning-powerplatform-solutions   →  solution-spec.yaml + mockup + PDF
chat 2   building-sharepoint-lists          →  provisioning workbook
chat 3   generating-powerapps-yaml          →  the screens
chat 4   building-powerautomate-flows       →  the flow packages
chat 5   writing-app-manuals (draft)        →  send to the user to validate
  ... build, then ...
chat 6   writing-app-manuals (final)        →  with screenshots and real troubleshooting
```

Carry `solution-spec.yaml` between chats. You do not need to re-explain the system.

You do not have to name the skill — the descriptions are written to trigger on how people actually
ask ("make this a Power App", "why is my gallery only showing 500 rows"). If a skill does not fire,
that is a bug worth reporting.

## What makes a rule a rule

Two ideas do most of the work here. Read them before changing anything.

### Ground-truth hierarchy — [`PROJECT-BRIEF.md`](PROJECT-BRIEF.md)

When sources disagree, higher rank wins:

1. **Artifacts that worked** — files in `source-artifacts/`. These compiled or imported.
2. **Written convention docs** and existing skills — distilled when the lesson was fresh.
3. **Human recall** — strong on frequent problems, weak on detail.
4. **Anything recovered from an old chat** — `confidence: low` until an artifact confirms it.

The point of the ranking is that a plausible claim never outranks a file that shipped. When a
document and an artifact disagree, the artifact wins and the document gets corrected.

### Evidence tiers — [`docs/EVIDENCE-TIERS.md`](docs/EVIDENCE-TIERS.md)

Every rule is one of three things, and they behave differently:

| Tier | Means | Validator | Overridable |
|---|---|---|---|
| `PLATFORM` | a Power Platform fact. Violating it makes the platform fail | `ERROR` | never |
| `HOUSE` | a convention we adopted. Sound, not mandatory | `WARN` | yes — edit `assets/house-style.yaml` |
| `EXAMPLE` | illustration from a real system | not enforced | n/a |

**This is the part that keeps the suite usable on a project that is not the one it was built from.**
A measured count like "1,370 of 1,370 Labels carry these six properties" proves *this team always
did it* — not *it must always be done*. Both statements are useful; only one is a law.

So the palette, the type scale, the naming conventions and the layout defaults live in an editable
config inside each skill. A new project with a different design system **edits one YAML file**. It
does not edit validator code, and it does not learn to ignore warnings.

```bash
# check platform rules only, ignoring every house convention
python3 scripts/validate_pa_yaml.py --platform-only Screen.pa.yaml

# check against a different project's conventions
python3 scripts/validate_pa_yaml.py --style ../our-style.yaml Screen.pa.yaml
```

## Every generator validates before it hands anything over

Each skill ships a Python validator and a blocking gate in its `SKILL.md`:

> Run `python scripts/validate_*.py <file>`. If it fails, fix and re-run. Do not present output to
> the user until the validator exits clean.

Validation happens in the Claude sandbox, **before** the paste — which is the whole point in an
environment where a failed paste is expensive.

Every validator is tested in both directions, and the tests are the receipts:

| Validator | Real artifacts | Deliberately broken |
|---|---|---|
| `validate_pa_yaml.py` | 17 screens: 0 errors, 0 warnings | 6 defects → 7 errors, each naming the control path |
| `validate_lists.py` | the spec: clean | 7 defects → 7 errors, each naming the offending key |
| `validate_spec.py` | the schema example: clean | 8 defects → 8 errors |
| `generate_workbook.py` + `xlsx_to_spec.py` | 131 fields round-trip losslessly | — |

## Improving the skills — this is the important part

The suite was built from **one** system. Every project after it will hit something those artifacts
never contained. Without a way to feed that back, each teammate rediscovers the same corrections
privately and the skills never get better.

So there is a loop, and it takes about two minutes of your time per project.

**When you finish real work with a skill**, before you close that chat, paste
[`prompts/feedback-session.md`](prompts/feedback-session.md) into it. It asks Claude for two things:

1. **The file that finally worked** — this is the valuable half. It is checkable, exactly like the
   original 17 screens.
2. **What went wrong, element by element** — and crucially, *why the skill did not prevent it*:
   - the skill never mentioned it → **add a rule**
   - the skill said something wrong → **fix the rule**
   - the skill said the right thing and Claude ignored it → **the rule is buried or badly worded**

That third category is the one that matters most and the one a model will avoid admitting, so the
prompt asks for it directly. It is also the only category that makes a skill better *without making
it longer* — and a skill nobody finishes reading has no rules at all.

Full process, including how findings are triaged and released:
[`docs/IMPROVING-SKILLS.md`](docs/IMPROVING-SKILLS.md).

```bash
python3 scripts/triage_feedback.py        # ranked action list from everything filed
```

## Repository map

```
PROJECT-BRIEF.md          the governing document: decisions, guardrails, session map
README.md                 you are here
docs/
  EVIDENCE-TIERS.md       PLATFORM vs HOUSE vs EXAMPLE — read before changing a rule
  IMPROVING-SKILLS.md     the feedback loop, end to end
spec/
  solution-spec.schema.yaml   the contract; also a filled worked example
  validate_spec.py
skills/<name>/
  SKILL.md                under 200 lines. Platform rules inline, everything else a pointer
  assets/house-style.yaml the overridable conventions
  references/*.md         one level deep, TOC on anything over 100 lines
  scripts/*.py            validators and generators
prompts/
  feedback-session.md     paste at the END of a working chat
  harvest-buildchat.md    one-off: recover rules from a long past conversation
evals/<skill>/            three per skill, with real artifacts as regression fixtures
feedback/<skill>/         field reports land here
ledger/                   how every rule was derived, with counts and confidence
source-artifacts/         the ground truth. Do not edit; these are what worked
dist/                     upload-ready zips + CHANGELOG
```

`ledger/00-INDEX.md` is the index. Read it before any deep dive — it says which file holds what,
which session wrote it, and what is still unverified.

## For anyone reading this from outside the team

The specific rules here encode one organisation's Power Platform environment, and the palette and
naming conventions are ours. Two things may still be useful to you:

- **The methodology.** Measure what worked, grade every rule by what fails when you break it, put
  the overridable parts in a config, validate before delivery, and close the loop with field
  reports. None of that is Power Platform specific.
- **The platform findings.** `ledger/04-flow-rules.md` §0 documents a real Power Automate legacy
  export package in more detail than we could find published anywhere — including two files
  (`apisMap.json`, `connectionsMap.json`) that the community documentation we surveyed does not
  mention, and which appear to be what `PackageFlowMissingConnectionMap` is actually complaining
  about.

`source-artifacts/` contains material from a real internal system, including a colleague's email
address inside the flow export. Treat this repository accordingly.
