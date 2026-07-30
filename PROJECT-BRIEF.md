# PROJECT BRIEF — Power Platform Skill Suite

<!-- Paste this as the first message of a new Claude Code session on the `powerplatform-skills` repo. -->
<!-- v2.1 -->

## Read this first — what to do with this message

This is a **project brief, not a task list to execute in one go.** Do the following, in order:

1. Save this message verbatim as `PROJECT-BRIEF.md` in the repo root. Commit it. From now on, any new session starts with *"Read PROJECT-BRIEF.md. We're on Session N"* instead of re-pasting this.
2. Run the **Preflight** below and report the inventory.
3. Ask me which session we're running. **Do only that session.** Stop at its stop-gate and wait.

If I've already told you the session number, skip step 3 and go.

---

## Preflight — run before anything else

Report a short inventory table. Do not start work until I confirm.

| Check | What to report |
|---|---|
| `PROJECT-BRIEF.md` exists in repo? | yes/no — if no, create and commit it now |
| `/source-artifacts/yaml/` | count of `.pa.yaml` files |
| `/source-artifacts/flows/` | count of `.zip` files |
| `/source-artifacts/sharepoint/` | count of `.xlsx` files |
| `/source-artifacts/docs/` | filenames present |
| `/source-artifacts/existing-skills/` | skill folder names found |
| `/ledger/` | files present, or empty |
| `/spec/` | files present, or empty |
| `python3 -c "import yaml, openpyxl"` | works / fails |

**If a directory needed for the requested session is empty, stop and tell me exactly which files to upload.** I upload binaries by hand through the GitHub web editor — you can't fetch them. Never proceed on an empty input directory and never fabricate substitute content.

---

## Mission

Build four Agent Skills so a Power Platform delivery team can go from **requirement → agreed design → working Power Apps + SharePoint + Power Automate** with short prompts, on Pro-plan token budgets.

The team works in a closed SCB/InnovestX environment: no Power Platform CLI, no local execution. Everything Claude produces gets **copy-pasted or uploaded into a browser**. So generated artifacts must be correct on the first paste — there is no cheap retry loop.

Final suite — four skills, mutually exclusive by artifact produced:

| # | Skill (gerund form) | Produces | Reads |
|---|---|---|---|
| 1 | `generating-powerapps-yaml` | `*.pa.yaml` | spec `screens[]`, `variables[]`, `bindings[]` |
| 2 | `building-sharepoint-lists` | provisioning `.xlsx` + column script | spec `lists[]`, `relations[]` |
| 3 | `planning-powerplatform-solutions` | `solution-spec.yaml`, HTML mockup, `system-overview.pdf` | requirements interview |
| 4 | `building-powerautomate-flows` | legacy import `.zip` | spec `flows[]` |

---

## Five locked decisions — do not relitigate

**D1. The spec is the product; the PDF is a rendering.** The planner emits one machine-readable `solution-spec.yaml`. The PDF is generated *from* it. Every builder skill reads only its own section. Rationale: a PDF is lossy, expensive to re-read, and unvalidatable.

**D2. Validation happens in the Claude sandbox, before the paste.** Every generator skill ships a Python validator in `scripts/` and a blocking gate in SKILL.md, worded exactly:

> Run `python scripts/validate_*.py <file>`. If it fails, fix and re-run. Do not present output to the user until the validator exits clean.

**D3. Conventions live in a claude.ai Project; procedures live in Skills.** Design tokens, TH↔EN glossary, site URLs, naming standards go in Project knowledge. Skills reference them and ask if absent. Never inline them into a SKILL.md.

**D4. Merge overlapping skills.** `powerapps-yaml` and `html-to-yaml` currently compete for the same trigger. They become one. Every description carries explicit negative routes ("Do NOT use for… use X instead").

**D5. Distribution is per-account `.zip`.** Custom skills on claude.ai are private per account and don't sync from Claude Code. You produce zips in `/dist/`; a human downloads and uploads them.

---

## Ground truth hierarchy — the most important rule in this brief

When sources disagree, higher rank wins. Always.

| Rank | Source | Standing |
|---|---|---|
| **1** | Files in `/source-artifacts/` | **Ground truth.** These compiled in Studio or imported cleanly. They are what actually worked. |
| **2** | `/source-artifacts/docs/`, existing SKILL.md files | Distilled rules, written when the lesson was fresh |
| **3** | `ledger/06-vin-notes.md` (my recall) | Strong on frequently-hit problems, weak on detail |
| **4** | Anything recovered from the old Claude Code chat | **`confidence: low` until an artifact confirms it** |

Rank 4 is low for a specific reason: that session ran to millions of tokens and has auto-compacted many times. What survives is a recency-weighted summary, and it reconstructs plausibly rather than accurately. **Do not suggest mining it as a primary source.** It is a last-resort gap-filler for the *why* behind a rule and for approaches we abandoned.

---

## Hard guardrails

- **Never invent a Power Apps control type or property.** If unverified against `/source-artifacts/`, mark it `UNVERIFIED` and ask. Invented-but-plausible YAML is the exact failure mode this project exists to eliminate.
- **Never write a rule the ledger doesn't support.** If a skill needs something the ledger lacks, stop and ask.
- **Commit after every meaningful step.** Cloud session VMs are reclaimed on inactivity — uncommitted work is gone.
- **Never resolve a contradiction between sources silently.** Flag it and let me decide.
- **Target reader of every skill:** a teammate on Pro running Sonnet or Haiku. Assume competence, not context. Instructions Opus infers, Haiku needs stated.
- Forward slashes in all paths. No time-sensitive statements in skills.

---

## Session map

One session per conversation. Fresh session each time. Each starts by reading the ledger, never by re-deriving.

### Session 1 — Harvest the working artifacts

Read `/source-artifacts/yaml/` (screens that compiled successfully in Studio).

Write and run `scripts/harvest_yaml.py`, reporting empirically:

- every control type used, with count, and which properties appear on each
- whether properties are alphabetically sorted within each `Properties` block (count violations)
- every distinct `Height`, `Width`, `Size`, `FillPortions`, `TemplateSize` value
- every property using a `|` block scalar, and which characters forced it
- container nesting depth; where `LayoutOverflowY` appears
- every `RGBA(...)` value, deduplicated, with counts

Write `ledger/01-observed-conventions.md` as **rule | evidence (file:count) | confidence**, where confidence is `high` (holds across all files), `medium` (most), `low` (varies).

Then read `/source-artifacts/docs/PowerApps_YAML_Conventions.md` and write `ledger/02-reconciliation.md`:

1. **Confirmed** — documented and obeyed
2. **Undocumented** — consistent pattern in artifacts that the doc never states *(the recovered rules — the point of this session)*
3. **Contradicted** — doc and artifacts disagree. Flag each; do not resolve.

**Stop gate:** commit, then show me sections 2 and 3 only.

### Session 2 — Written docs + spec contract

- **A.** Audit `powerapps-yaml` vs `html-to-yaml` → `ledger/03-skill-audit.md`: coverage of each, unique content, every conflict with a recommended winner and reasoning from artifacts. Don't merge yet.
- **B.** Read `/source-artifacts/flows/` and `validate_flow.py` → `ledger/04-flow-rules.md`: package structure and every invariant, each paired with the failure it prevents.
- **C.** Read `/source-artifacts/sharepoint/` → `ledger/05-list-rules.md`: field types, naming, cross-list reference modelling.
- **D.** Draft `spec/solution-spec.schema.yaml` — commented YAML, keys `meta`, `process`, `screens[]`, `variables[]`, `lists[]`, `relations[]`, `flows[]`, `bindings[]`, where `bindings[]` maps `screen.control → variable → list.field`. Derive fields from what the ledger shows builders actually need, not from imagination. One real filled example per section.
- **E.** Write `spec/validate_spec.py` — required keys present; every binding references a real screen/variable/list; no orphan variables; no duplicate field names in a list. Non-zero exit, messages naming the offending key. Test against the example.

**Stop gate:** commit, then show me the schema and the Task A conflict list.

### Sessions 4–7 — Build one skill per session

Order: **Power Apps YAML → SharePoint lists → planning → Power Automate flows.** Planning comes third deliberately: the spec schema is discovered by building its consumers, not by imagining its producer.

Every skill follows this shape:

```
skills/<name>/
├── SKILL.md              # under 200 lines
├── references/           # TOC at top of any file over 100 lines
└── scripts/              # validators and generators
```

`SKILL.md` must contain:

- **description**: what it does + explicit trigger phrases + explicit negative routes to sibling skills + "if no `solution-spec.yaml` exists, ask for it first." Third person. Deliberately pushy about triggering — Claude under-triggers skills by default.
- a numbered workflow with a copyable checklist
- **only** rules marked `high` confidence or corrected 3+ times, inline. Everything else is a one-level-deep pointer to `references/`.
- the D2 validation gate, verbatim
- a `<!-- v1.0.0 -->` version line

Each session must also:

1. Open by reading `ledger/00-INDEX.md`, `ledger/02-reconciliation.md`, and this skill's domain ledger file. Ignore `confidence: low` items unless an artifact confirms them.
2. Write three evals in `evals/<skill>/` — JSON with `query`, input files, `expected_behavior` bullets — reusing real artifacts as regression fixtures.
3. Test the validator against a real `/source-artifacts/` file (must pass) and a deliberately corrupted copy (must fail with a message naming the specific problem).
4. Commit, then verify frontmatter parses and report SKILL.md line count.

Domain specifics:

- **`generating-powerapps-yaml`** — merge the two existing skills per `ledger/03`. References: `control-catalog.md`, `layout-sizing.md`, `patterns.md`, `error-taxonomy.md`. Validator checks at minimum: `yaml.safe_load` parses; control types match the confirmed catalog (bare `Label`/`Gallery`, `Classic/` on interactive); alphabetical properties; block scalars where values contain `: ` or `#`; `Classic/DropDown` and `Classic/Radio` have both `Items` and `Items.Value`; no `DropShadow.Light`; screen has `LoadingSpinnerColor`.
- **`building-sharepoint-lists`** — text fields over lookup fields for cross-list references, with the delegation/performance reason stated. `generate_workbook.py` (spec → xlsx) and `validate_lists.py`. Regression fixture: reproduce the 38-field `New_Request` list.
- **`planning-powerplatform-solutions`** — merges what I originally split into "methodology planner" and "system overview PDF"; one workflow, one output set. Interview → normalize any dumped flowchart/ER → **glossary first** (apparent cross-department conflicts are usually one system under two names — always ask "is this the same as X?") → HTML mockup using canonical design tokens → emit spec → validate → render PDF using the section order in `assets/pdf-outline.md`.
- **`building-powerautomate-flows`** — upgrade the existing skill rather than rewriting. Prominent in SKILL.md, not references: `connectionReferences` is never hand-authored (carry verbatim from a real export; failure = `PackageFlowMissingConnectionMap` / grey-X import); `splitOn` mandatory on array-returning triggers (failure = fires once per batch); never generate `operationMetadataId` or `metadata`; `runAfter` cycle detection in the validator. Keep template-anchoring — a real export is the structural anchor, only `definition.json` is regenerated. Add the classic-designer "My clipboard" fallback path.

### Session 8 — Lint and package

1. Lint every SKILL.md: description specific and covers what + when; body under 500 lines (target under 200); references one level deep; TOC on references over 100 lines; no time-sensitive content; consistent terminology (one term per concept — no mixing field/column/box); forward slashes; concrete examples.
2. Print the four descriptions side by side; identify any request matching two; sharpen negative routes until mutually exclusive.
3. Strip anything Claude already knows — no explaining what Power Apps, YAML, or a SharePoint list is. Report lines removed per skill.
4. Package each as an upload-ready `.zip` with `SKILL.md` at the folder root, written to `/dist/`. Verify by unzipping to temp and confirming frontmatter parses: `name` ≤64 chars, lowercase/numbers/hyphens only, no reserved words; `description` non-empty, ≤1024 chars.
5. Write `README.md`: what each skill does, the one-stage-per-chat rule, install steps for a Pro-plan teammate.

**Stop gate:** report the four zip paths and any checklist item you couldn't satisfy.

---

## Human tasks — not yours

Listed so you know where these inputs come from and don't try to do them:

- Uploading binaries to `/source-artifacts/` (GitHub web editor)
- `ledger/06-vin-notes.md` — my unassisted recall of the most frequent failures. Lands before Sessions 4–7.
- `ledger/07-recovered-*.md` — optional, surgical answers pulled from the old chat. `confidence: low` by default.
- Downloading `/dist/*.zip` and uploading to claude.ai → Settings → Skills
- Running the evals in fresh **claude.ai** chats on Sonnet and Haiku — a different runtime from Claude Code, and the one the team actually uses

---

## Right now

Run Preflight. Report the inventory. Then ask which session — or start Session 1 if I've already said so.
