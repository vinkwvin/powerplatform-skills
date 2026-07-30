# PROJECT BRIEF — Power Platform Skill Suite

<!-- Paste this as the first message of a new Claude Code session on the `powerplatform-skills` repo. -->
<!-- v3.0 -->

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
| `/source-artifacts/manuals/` | count of `.docx` files |
| `/ledger/` | files present, or empty |
| `/spec/` | files present, or empty |
| `/prompts/` | files present, or empty |
| `python3 -c "import yaml, openpyxl, docx"` | works / fails |

**If a directory needed for the requested session is empty, stop and tell me exactly which files to upload.** I upload binaries by hand through the GitHub web editor — you can't fetch them. Never proceed on an empty input directory and never fabricate substitute content.

---

## Mission

Build four Agent Skills so a Power Platform delivery team can go from **requirement → agreed design → working Power Apps + SharePoint + Power Automate** with short prompts, on Pro-plan token budgets.

The team works in a closed SCB/InnovestX environment: no Power Platform CLI, no local execution. Everything Claude produces gets **copy-pasted or uploaded into a browser**. So generated artifacts must be correct on the first paste — there is no cheap retry loop.

Final suite — five skills, mutually exclusive by artifact produced:

| # | Skill (gerund form) | Produces | Reads |
|---|---|---|---|
| 1 | `generating-powerapps-yaml` | `*.pa.yaml` | spec `screens[]`, `variables[]`, `bindings[]` |
| 2 | `building-sharepoint-lists` | provisioning `.xlsx` + column script | spec `lists[]`, `relations[]` |
| 3 | `planning-powerplatform-solutions` | `solution-spec.yaml`, HTML mockup, `system-overview.pdf` | requirements interview |
| 4 | `building-powerautomate-flows` | legacy import `.zip` | spec `flows[]` |
| 5 | `writing-app-manuals` | full admin `.docx` + user-friendly `.docx` | spec `screens[]`, `roles[]`, `lists[]`, `flows[]`, `glossary[]` |

---

## Six locked decisions — do not relitigate

**D1. The spec is the product; the PDF is a rendering.** The planner emits one machine-readable `solution-spec.yaml`. The PDF is generated *from* it. Every builder skill reads only its own section. Rationale: a PDF is lossy, expensive to re-read, and unvalidatable.

**D2. Validation happens in the Claude sandbox, before the paste.** Every generator skill ships a Python validator in `scripts/` and a blocking gate in SKILL.md, worded exactly:

> Run `python scripts/validate_*.py <file>`. If it fails, fix and re-run. Do not present output to the user until the validator exits clean.

**D3. Conventions live in a claude.ai Project; procedures live in Skills.** Design tokens, TH↔EN glossary, site URLs, naming standards go in Project knowledge. Skills reference them and ask if absent. Never inline them into a SKILL.md.

**D4. Merge overlapping skills.** `powerapps-yaml` and `html-to-yaml` currently compete for the same trigger. They become one. Every description carries explicit negative routes ("Do NOT use for… use X instead").

**D5. Distribution is per-account `.zip`.** Custom skills on claude.ai are private per account and don't sync from Claude Code. You produce zips in `/dist/`; a human downloads and uploads them.

**D6. One manual source, two renderings — and it ships twice.** The user-friendly manual is a *projection* of the full admin manual, not a second document. Measured against the 360 reference pair: Part A and Part B of the user manual are sections 4 and 5 of the full manual, compressed, with architecture, admin setup, troubleshooting, and appendix dropped. Generate one source; render two `.docx`. Never author two files that must be hand-synced.

The manual also ships at two points in the project, from the same source:

- **Draft** — after the developer handbook, before the build. Sent to the user to answer *"does this describe your problem?"* It is a requirements test wearing documentation's clothes: a user answering "that's not how we do it" catches a spec error while it is still cheap, and reacting to concrete steps is far easier than approving an abstraction. Setup, troubleshooting, screenshots and appendices A–C are absent because they cannot exist yet — which is fine, because those are exactly the sections a user cannot validate. What remains (roles, screen walkthroughs, glossary) is precisely the validatable subset.
- **Final** — after the build, with screenshots pasted in and troubleshooting populated from what actually broke.

`meta.status: draft | final` drives the difference. The 360 reference is itself stamped `ฉบับร่าง 1.0 (Draft)`.

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

### Two clarifications on rank

**The build-chat harvest (Session 2) is Rank 4 on arrival and is meant to be promoted.** It is not an exception to the rule above — it is a disciplined use of it. It collects *behavioural* observations (what Vin corrected, what the model kept getting wrong), not factual claims about Power Apps, and every entry arrives carrying a named artifact to check it against. An entry the artifacts confirm becomes Rank 1-backed. An entry they contradict is deleted. An entry citing `evidence: none` stays Rank 4 forever and never goes inline in a skill.

This matters because the brief already relies on an evidence class it has no source for: *"only rules marked `high` confidence **or corrected 3+ times**, inline."* Nothing else in the project produces a correction count. The harvest is where that number comes from.

**`/source-artifacts/manuals/` is Rank 1 for document structure only.** The two 360 manuals shipped, so their section order, numbering, table shapes, and screenshot conventions are ground truth. Their troubleshooting entries are Rank 1 observed failures. They say **nothing** about Power Platform build rules — do not mine them for control types or column behaviour.

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

Ten sessions. What changed from v2.1 and why:

- **Session 2 is new** — the build-chat harvest. It sits second because its output feeds every later session, and because it must be produced *independently* of `ledger/01` for the two to corroborate each other rather than echo.
- **The old Session 2 split in two** (now 3 and 4). Five tasks in one session was the heaviest load in the map, and Task D — the spec schema, which four skills hard-code — was last in line and first to be lost to a budget overrun.
- **v2.1 had no Session 3.** The map jumped from 2 to "Sessions 4–7". Now numbered continuously.
- **Nothing created `ledger/00-INDEX.md`**, though Sessions 5–9 are each required to open by reading it. Session 1 now creates it; every later session appends.
- **Session 9 is new** — `writing-app-manuals`.
- **Session 8 (flows) is gated on ground truth that does not exist yet.** See the session for what unblocks it.

| # | Session | Produces |
|---|---|---|
| 1 | Harvest the working artifacts | `ledger/00-INDEX.md`, `01`, `02`, `scripts/harvest_yaml.py` |
| 2 | Build-chat harvest + corroboration | `ledger/07-buildchat-raw.md`, `08-buildchat-verified.md` |
| 3 | Written-doc audit + domain ledgers | `ledger/03`, `04`, `05` |
| 4 | Spec contract | `spec/solution-spec.schema.yaml`, `spec/validate_spec.py` |
| 5 | `generating-powerapps-yaml` | skill + evals |
| 6 | `building-sharepoint-lists` | skill + evals |
| 7 | `planning-powerplatform-solutions` | skill + evals |
| 8 | `building-powerautomate-flows` | skill + evals |
| 9 | `writing-app-manuals` | skill + evals |
| 10 | Lint and package | `/dist/*.zip` ×5, `README.md` |

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

Also create `ledger/00-INDEX.md`: one line per ledger file — what it holds, which session wrote it, which sessions consume it. Every later session appends its own row.

Note there are now **two** candidate Rank 2 docs in `/source-artifacts/docs/`: `yaml-conventions.md` and `AccountClosure_Developer_Handbook.pdf`. Reconcile against both. Where they disagree with each other, that is a section 3 item too. Read `source-artifacts/docs/PROVENANCE.md` first — a byte-identical copy of `yaml-conventions.md` also sits inside `existing-skills/powerapps-yaml/references/`, and two copies of one document are one source, not two that agree.

**Stop gate:** commit, then show me sections 2 and 3 only.

### Session 2 — Build-chat harvest + corroboration

The one session with a human step in the middle. Purpose: recover the corrections and recurring mistakes from the chat that built the Account Closure prototype, then verify each against the 17 screens before any of it is allowed near a skill.

- **A.** I paste `prompts/harvest-buildchat.md` into the build chat and save its reply verbatim as `ledger/07-buildchat-raw.md`. This happens before the session opens — see Human tasks.
- **B.** Read `ledger/07-buildchat-raw.md`. For every entry, check its `evidence` field against the named artifact in `/source-artifacts/`. Write `ledger/08-buildchat-verified.md` with one of four verdicts per entry:
  - **`confirmed`** — the artifact demonstrates the rule. Promote to Rank 1-backed; eligible to go inline in a skill.
  - **`contradicted`** — the artifact shows the opposite. Delete the entry and record that it was wrong; a false rule that was believed is worth knowing about.
  - **`unverifiable`** — `evidence: none`, or the cited file does not exist. Stays Rank 4, `confidence: low`, never inline. Reference material at most.
  - **`out-of-scope`** — a real observation about something outside the five skills.
- **C.** Cross-check against `ledger/06-vin-notes.md`. The two were written independently, so agreement between them is real signal. Where Vin's recall and the chat's recall disagree, flag it — do not resolve.
- **D.** Produce the correction counts. Any rule with `source: corrected` and `times >= 3` that is also `confirmed` satisfies the "corrected 3+ times" bar and goes inline in its skill. List them explicitly; Sessions 5–9 read this list.
- **E.** Report what the harvest claimed but could not be checked, with counts. A silent drop here reads as "nothing was lost".

**Stop gate:** commit, then show me the `confirmed` list, the `contradicted` list, and any Vin-vs-chat disagreement from Task C.

### Session 3 — Written-doc audit + domain ledgers

- **A.** Audit `powerapps-yaml` vs `html-to-yaml` → `ledger/03-skill-audit.md`: coverage of each, unique content, every conflict with a recommended winner and reasoning from artifacts. Don't merge yet.
- **B.** Read `/source-artifacts/flows/` and `validate_flow.py` → `ledger/04-flow-rules.md`: package structure and every invariant, each paired with the failure it prevents.

  **Read `ledger/NOTE-flow-groundtruth-gap.md` before starting.** No flow has ever been built or imported, so `/source-artifacts/flows/` may still be empty and the existing skill's `template_skeleton` is hand-authored — synthetic GUIDs, `contoso.com`, and `connectionReferences` whose `connectionName` holds the connector API name rather than a real per-connection identifier. Its validator passes that skeleton clean, because it only checks self-consistency with its own conventions.

  If no real export is present, Task B still runs, but `ledger/04` is written as **"what the existing skill asserts, unverified"** — `confidence: low` throughout, source recorded as the skill's own template, and every "failure it prevents" marked as hypothesized rather than observed. Nothing in it may read as artifact-backed. If a real export *is* present, verify each invariant against it and grade accordingly.
- **C.** Read `/source-artifacts/sharepoint/` → `ledger/05-list-rules.md`: field types, naming, cross-list reference modelling. Include which columns are user-populated and which are written by automation — Session 6 and Session 9 both need that split.

**Stop gate:** commit, then show me the Task A conflict list and Task B's confidence grading.

### Session 4 — Spec contract

Read `ledger/00-INDEX.md` and every ledger file first. The schema is derived from what the ledgers show consumers actually need — not from imagination.

- **A.** Draft `spec/solution-spec.schema.yaml` — commented YAML. Keys: `meta`, `process`, `screens[]`, `variables[]`, `lists[]`, `relations[]`, `flows[]`, `bindings[]`, `roles[]`, `glossary[]`, where `bindings[]` maps `screen.control → variable → list.field`. One real filled example per section, taken from the account-closure artifacts rather than invented.

  **Five consumers, not four.** `ledger/NOTE-manual-skill-proposal.md` measured which fields the manual needs that no builder does, from the real 360 document. Carry all of them:

  | Field | Renders | Consumer |
  |---|---|---|
  | `screens[].purpose` | full manual T15 `หน้าที่` | manual only |
  | `screens[].roles[]` | T15 `ใครเข้าถึงได้`; drives the Part A / Part B split | manual only |
  | `roles[]` — id, label, responsibilities, access tier, applicable sections | T08, T09, T10 | manual only |
  | `flows[].purpose`, `flows[].type` | T14 | manual only |
  | `lists[].purpose` | T12 | manual only |
  | `lists[].fields[].populated_by: user \| automation` | T13 | **manual + SharePoint builder** — an automation-written column must not surface as a user-entry field |
  | `glossary[]` | Appendix D | **manual + planner** — the planner's workflow already runs "glossary first" and v2.1 had nowhere to put the result |
  | `meta.status: draft \| final` | version table; gates draft vs final rendering | manual only |

- **B.** Write `spec/validate_spec.py` — required keys present; every binding references a real screen/variable/list; no orphan variables; no duplicate field names in a list; every `screens[].roles[]` entry names a real `roles[]` id; every `lists[].fields[].populated_by` is one of the two allowed values. Non-zero exit, messages naming the offending key. Test against the example.

**Stop gate:** commit, then show me the schema and the validator's output on both the example and a deliberately broken copy.

### Sessions 5–9 — Build one skill per session

Order: **Power Apps YAML → SharePoint lists → planning → Power Automate flows → manuals.** Planning comes third deliberately: the spec schema is proven by building its consumers, not by imagining its producer. Manuals come last because it is the only skill with no Power Platform ground truth of its own, and it depends on `screens[].purpose`, `roles[]`, and `glossary[]` having survived contact with four other consumers.

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

1. Open by reading `ledger/00-INDEX.md`, `ledger/02-reconciliation.md`, `ledger/08-buildchat-verified.md`, and this skill's domain ledger file. Ignore `confidence: low` items unless an artifact confirms them. From `ledger/08`, the `confirmed` + `times >= 3` list goes inline; everything else is `references/` at most.
2. Write three evals in `evals/<skill>/` — JSON with `query`, input files, `expected_behavior` bullets — reusing real artifacts as regression fixtures.
3. Test the validator against a real `/source-artifacts/` file (must pass) and a deliberately corrupted copy (must fail with a message naming the specific problem).
4. Commit, then verify frontmatter parses and report SKILL.md line count.

Domain specifics:

- **`generating-powerapps-yaml`** — merge the two existing skills per `ledger/03`. References: `control-catalog.md`, `layout-sizing.md`, `patterns.md`, `error-taxonomy.md`. Validator checks at minimum: `yaml.safe_load` parses; control types match the confirmed catalog (bare `Label`/`Gallery`, `Classic/` on interactive); alphabetical properties; block scalars where values contain `: ` or `#`; `Classic/DropDown` and `Classic/Radio` have both `Items` and `Items.Value`; no `DropShadow.Light`; screen has `LoadingSpinnerColor`.
- **`building-sharepoint-lists`** — text fields over lookup fields for cross-list references, with the delegation/performance reason stated. `generate_workbook.py` (spec → xlsx) and `validate_lists.py`. Regression fixture: reproduce the 38-field `New_Request` list.
- **`planning-powerplatform-solutions`** — merges what I originally split into "methodology planner" and "system overview PDF"; one workflow, one output set. Interview → normalize any dumped flowchart/ER → **glossary first** (apparent cross-department conflicts are usually one system under two names — always ask "is this the same as X?") → HTML mockup using canonical design tokens → emit spec → validate → render PDF using the section order in `assets/pdf-outline.md`.
- **`building-powerautomate-flows`** — **not an upgrade and not a rewrite.** The existing skill splits three ways, and the split is the point:
  - **Salvage** — `wdl-schema.md` (219 lines) and `connector-recipes.md` (132). Workflow Definition Language is publicly documented and stable, so these claims are checkable without a tenant.
  - **Rebuild against a real export** — `package-structure.md`, `manifest.json`, `connectionReferences`, GUID handling. This is where the invention is concentrated.
  - **Unverifiable until someone tries it** — `clipboard-paste.md`, the classic-designer fallback. Keep it, mark it untested.

  Prominent in SKILL.md, not references: `connectionReferences` is never hand-authored (carry verbatim from a real export; failure = `PackageFlowMissingConnectionMap` / grey-X import); `splitOn` mandatory on array-returning triggers (failure = fires once per batch); never generate `operationMetadataId` or `metadata`; `runAfter` cycle detection in the validator. Keep template-anchoring — but the anchor must be a **real** export, which v2.1 assumed existed and did not.

  The validator must gain what the existing one lacks: a `splitOn` check on array-returning triggers, and a check that `connectionName` does not equal the connector API name. Also state plainly in the skill that this validator is weaker than the Power Apps one, and why — 17 compiling screens back that one; this one is backed by however many clean imports have actually been observed.

  **Gate:** if `/source-artifacts/flows/` still holds no real export when this session opens, stop and say so. Do not build a skill whose central claim is "carry this verbatim from a real export" with no real export in the repo.

  Read `ledger/NOTE-flow-external-research.md` too. Three things from it belong in the skill:
  - **No community skill covers this use case.** Every one found (including Microsoft's official plugin) works through a live API against a tenant. Nothing generates an offline legacy `.zip` for browser upload, so there is no reference implementation to check the packaging against.
  - **Real packages may contain `connections.json` and `flow.json`**, which the existing skeleton lacks entirely. Whether they are required is unknown from documentation.
  - **The connection prompt on import is expected legacy behaviour, not a failure.** A legacy package requires connections to be remapped manually at import; solutions do not. A skill that treats the prompt as a bug sends people chasing something that is not there. State this prominently.

- **`writing-app-manuals`** — reads `/source-artifacts/manuals/` for structure and `ledger/NOTE-manual-skill-proposal.md` for the measured mapping. References: `full-manual-outline.md`, `user-manual-outline.md`, `screenshot-frames.md`, `bilingual-headings.md`.

  One source, two renderings, per D6. `generate_manual.py` (spec + `meta.status` → both `.docx`) and `validate_manual.py`. Build with `docx` (npm) — see the `docx` skill's gotchas; dual widths on every table, `ShadingType.CLEAR` never `SOLID`, built-in `HeadingLevel.*` or the TOC comes out empty.

  Structure taken from the reference pair, not invented. Full manual: 8 H1 sections in the order Introduction → System Architecture → Initial Setup (Admin) → For Everyone → For the HR Team → Troubleshooting → Appendix, decimal numbering, a setup checklist at `3.0`, appendices for code / mapping / calculation / glossary. User manual: 3 H1 sections, flat per-screen numbering, and per screen exactly **heading → screenshot frame → bullet steps** (9 of its 10 tables are 1×1 screenshot frames).

  Two inputs the skill cannot generate, and must therefore *request* rather than fabricate:
  - **Screenshots.** Emit numbered placeholder frames naming the screen, the state to put it in, and what to highlight. The human pastes. Same class of constraint as paste-into-browser.
  - **Troubleshooting entries.** All 8 in the reference are specific observed failures — leading zeros dropped on a SharePoint paste, a Choice column rejecting a value, Power Query `#N/A`, Power BI not refreshing. These cannot be invented; same guardrail as the control catalog. They come from a human or from a ledger of observed failures, and in draft mode there are none.

### Session 10 — Lint and package

1. Lint every SKILL.md: description specific and covers what + when; body under 500 lines (target under 200); references one level deep; TOC on references over 100 lines; no time-sensitive content; consistent terminology (one term per concept — no mixing field/column/box); forward slashes; concrete examples.
2. Print the five descriptions side by side; identify any request matching two; sharpen negative routes until mutually exclusive. Two known collision zones: (a) `generating-powerapps-yaml` vs `planning-powerplatform-solutions` both accept an HTML mockup; (b) `writing-app-manuals` draft mode vs the planner, since both are consumed by a user validating requirements. The third — three documents describing system structure — is resolved by audience, per Vin's ruling: builder → planner, admin → full manual, normal user → user manual. Write the negative routes on the reader, not the subject.
3. Strip anything Claude already knows — no explaining what Power Apps, YAML, or a SharePoint list is. Report lines removed per skill.
4. Package each as an upload-ready `.zip` with `SKILL.md` at the folder root, written to `/dist/`. Verify by unzipping to temp and confirming frontmatter parses: `name` ≤64 chars, lowercase/numbers/hyphens only, no reserved words; `description` non-empty, ≤1024 chars.
5. Write `README.md`: what each skill does, the one-stage-per-chat rule, install steps for a Pro-plan teammate.

**Stop gate:** report the five zip paths and any checklist item you couldn't satisfy.

---

## Human tasks — not yours

Listed so you know where these inputs come from and don't try to do them:

- Uploading binaries to `/source-artifacts/` (GitHub web editor)
- **`ledger/06-vin-notes.md`** — my unassisted recall of the most frequent failures. **Write this before Session 1's stop gate.** Reading `ledger/01` first contaminates it, and its entire value is being an independent Rank 3 source that can corroborate or contradict Rank 1.
- **`ledger/07-buildchat-raw.md`** — paste `prompts/harvest-buildchat.md` into the Account Closure build chat and save the reply verbatim. Do not tidy it, do not delete entries I disagree with; Session 2 decides what survives. **Do this before Session 2 opens, and ideally before Session 1's stop gate** so it stays independent of `ledger/01` for the same reason `06` does.
- **Exporting one real Power Automate flow** — build a throwaway flow in the browser (SharePoint "When an item is created" → "Send an email (V2)"), then My Flows → ⋯ → Export → Package (.zip), and upload to `/source-artifacts/flows/`. Roughly ten minutes, and it is the only thing that unblocks Session 8. Then re-import the unmodified zip: if that succeeds, the package structure is confirmed.
- **Pasting screenshots** into the generated manual, using the numbered frames Session 9's skill emits
- **Supplying troubleshooting entries** — real observed failures only; the manual skill is forbidden from inventing them
- Downloading `/dist/*.zip` and uploading to claude.ai → Settings → Skills
- Running the evals in fresh **claude.ai** chats on Sonnet and Haiku — a different runtime from Claude Code, and the one the team actually uses

---

## Right now

Run Preflight. Report the inventory. Then ask which session — or start Session 1 if I've already said so.

### Already done — do not redo

Setup work completed before Session 1. Verify it is still present; do not recreate it.

- `PROJECT-BRIEF.md` at v3.0, committed
- Repo scaffold and `.gitignore`
- `/source-artifacts/yaml/` — 17 `.pa.yaml`, all verified to parse under `yaml.safe_load`, no tabs in leading whitespace, each a single-screen `Screens:` document
- `/source-artifacts/docs/` — `yaml-conventions.md`, `AccountClosure_Developer_Handbook.pdf`, `PROVENANCE.md`
- `/source-artifacts/sharepoint/` — `AccountClosure_SharePoint_List_Setup.xlsx`
- `/source-artifacts/existing-skills/` — all three skill folders, copied from the installed skills
- `/source-artifacts/manuals/` — both 360 reference `.docx`
- `/prompts/harvest-buildchat.md` — the Session 2 paste-ready prompt
- `ledger/NOTE-flow-groundtruth-gap.md`, `ledger/NOTE-manual-skill-proposal.md`

Still missing, and known: `/source-artifacts/flows/` (no flow has ever been built — gates Session 8), `ledger/06-vin-notes.md`, `ledger/07-buildchat-raw.md`.

### Answered — Vin's rulings

1. **Heading language order was drift, not design.** Standardise on **Thai first, English second** for both manuals: `1. บทนำ / Introduction`. Reasons — the readers are Thai staff, the Thai is the operative text, and the more carefully built of the two references already does it this way. Reversible; per D3 the TH↔EN convention itself lives in Project knowledge, and this is only the ordering rule the skill follows.

2. **The three system-structure documents split by reader, not by subject.** They may cover the same system; each is written for a different person at a different depth.

   | Document | Reader |
   |---|---|
   | `system-overview.pdf` (planner) | the **builder** who builds the app |
   | full manual (`.docx`) | the **admin user** who runs it |
   | user-friendly manual (`.docx`) | the **normal user** who uses it |

   Session 10's negative routes are written on audience: *"describing the system to the person building it → planner. To the person administering it → full manual. To the person using it → user manual."*

   One residual overlap Vin did not address: `AccountClosure_Developer_Handbook.pdf` also targets the builder, the same reader as `system-overview.pdf`. Ask before Session 7 whether the planner's PDF is meant to replace the handbook or sit beside it.

3. **`html-to-yaml`'s three example `.yaml` files worked, but with "common problems like misformatting and code errors."** They compiled *after* fixing. So they are **not** clean Rank 1 and must not go into `/source-artifacts/yaml/` — a file that needed repair cannot be evidence of what pastes first try.

   They are more valuable elsewhere. Session 5 uses them as the primary input to `references/error-taxonomy.md`: 3,234 lines demonstrating the failure modes the skill exists to prevent. Diffing them against the 17 clean screens shows what "misformatted" concretely means. Promotion in usefulness, not a demotion.
