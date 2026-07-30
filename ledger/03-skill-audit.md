# 03 — Skill audit: `powerapps-yaml` vs `html-to-yaml`

Session 3 Task A. Both skills compete for the same trigger and must merge into
`generating-powerapps-yaml` (D4). This file decides what survives. **No merging yet.**

Every conflict is settled against `ledger/01` (measured) and `ledger/02` §3 (Vin's rulings) —
not by preference.

## Contents
1. What each skill is
2. Coverage comparison
3. Unique content worth keeping — `powerapps-yaml`
4. Unique content worth keeping — `html-to-yaml`
5. Conflicts, with winners
6. What neither skill has
7. Recommended merge shape

---

## 1. What each skill is

| | `powerapps-yaml` | `html-to-yaml` |
|---|---|---|
| SKILL.md | 145 lines | 146 lines |
| Input | HTML/CSS/JS prototype, files or pasted | HTML/CSS mockup **or screenshot image** |
| References | `yaml-conventions.md` (278), `html-to-powerapps.md` (363), `token-mapping.md` (106) | `confirmed-controls.md` (111), `schema-v3.pa.yaml` (583) |
| Assets | — | 3 example `.pa.yaml` (3,234 lines) |
| Validator | **`validate_pa_yaml.py`, 313 lines** | **none** |
| Organising idea | encode the environment contract, then validate | only emit what is confirmed, label the rest honestly |
| Shape | Intake → 9-step workflow → cheat-sheet → references → validating → gotchas | Why → read catalog → understand source → write → hand off → interpret feedback → maintain catalog |

The two are not redundant. `powerapps-yaml` is a **generator**; `html-to-yaml` is a **discipline
and feedback protocol**. That is why the merge is worth doing rather than picking one.

## 2. Coverage comparison

| Concern | `powerapps-yaml` | `html-to-yaml` |
|---|---|---|
| Control types + exact versions | yes, full table | yes, catalog |
| Design token → RGBA/size | yes, dedicated reference | partial (hover colours only) |
| HTML element → control mapping | yes, full playbook | prose only |
| Table → Gallery | yes, worked example | via examples |
| Editable table → collection | yes | no |
| Status badge → `Switch()` | yes | no |
| Alphabetical property order | **yes** | **no mention** |
| Block scalars | yes, with rule | partial — bans flow style, does not state the `: `/`#` rule |
| Screen `LoadingSpinnerColor` | **yes** | **no** |
| AutoLayout containers | yes | **no — teaches `X`/`Y`** |
| CONFIRMED / UNVERIFIED labelling | no | **yes, central** |
| Studio error classification | no | **yes, blocking vs non-blocking** |
| Isolated paste-test snippets | no | **yes** |
| Screenshot input | no | **yes** |
| Feedback → update the catalog | no | **yes** |
| Validator | **yes** | no |

## 3. Unique to `powerapps-yaml` — keep

- **Step 0 Intake** (input mode / scope / output shape), with "if the user already told you, don't re-ask" — good token discipline for a Pro-plan reader.
- **Token extraction pass**, including "re-read the token file every run — tokens drift."
- **`html-to-powerapps.md`** — the element→control mapping table and worked examples for editable table → collection and badge → `Switch()`. Nothing in the other skill replaces this.
- **The validator.** D2 requires one; only this skill has it.
- **One-screen-per-file default**, matching how Studio pastes.
- **`Notify(...)` placeholder convention** for unbuilt targets, so a screen compiles before its navigation exists.

## 4. Unique to `html-to-yaml` — keep

These are the reason not to simply discard it.

- **`# CONFIRMED` / `# UNVERIFIED — guessing from <reasoning>` inline tagging.** This *is* the brief's hard guardrail ("never invent a control type… mark it `UNVERIFIED` and ask") already implemented. Highest-value item in either skill.
- **Blocking vs non-blocking error classification** — `PA1001`/`PA2108` block the whole paste; `PA2105`/`PA2106` are version warnings Studio auto-substitutes. Prevents both panic and complacency. Straight into `references/error-taxonomy.md`.
- **Isolated test-snippet protocol** — when a control is unconfirmed, ship the full file *plus* a one-control snippet to paste-test alone. Correct response to a browser-only, no-cheap-retry environment.
- **Screenshot as a first-class input**, with "prefer HTML for exact values, the image to check the HTML wasn't cut off."
- **Full-file paste requirement** — Studio needs the whole screen, so never fragment the deliverable.
- **Flow-style YAML ban** — commas inside `RGBA(...)` break flow style. Measured: all 2,847 blocks are block style.
- **"Every formula value starts with `=`"** — stated explicitly here, only implied in the other.
- **Sidebar/nav items are always `Classic/Button@2.2.0`, never `Label`**, even when the mockup looks like text — because it must be clickable.
- **The catalog-maintenance loop** ("don't let confirmed-vs-unverified knowledge live only in chat history"). This is D7 arrived at independently, before the brief formalised it. Strong corroboration that the feedback loop belongs in the suite.

## 5. Conflicts, with winners

| # | Conflict | Winner | Evidence |
|---|---|---|---|
| K1 | **Positioning: `X`/`Y` vs AutoLayout.** `html-to-yaml` Step 2 skeleton uses `X:`/`Y:`, and Step 0 tells the reader to follow the examples' "X/Y coordinates". `powerapps-yaml` uses AutoLayout containers. | **`powerapps-yaml`** | `ledger/01` §6: `X`/`Y` on 17 root containers only; **0 of 1,370 Labels, 0 of 268 Buttons, 0 of 36 Galleries**. 887/887 containers are `AutoLayout`. Vin ruled explicitly. |
| K2 | **Screen properties.** `html-to-yaml` skeleton has `Fill` only. `powerapps-yaml` requires `LoadingSpinnerColor`. | **`powerapps-yaml`**, but **both are incomplete** | 17/17 screens carry `Fill` + `LoadingSpinnerColor` + `OnVisible`. Neither skill mentions `OnVisible`. |
| K3 | **Alphabetical ordering.** Required by one, unmentioned by the other. | **`powerapps-yaml`** | 2,847/2,847 blocks sorted, zero violations |
| K4 | **Validation.** Validator vs "hand off and let the user test in Studio". | **`powerapps-yaml`** | D2 makes a validator mandatory. The other skill's loop costs a Studio round-trip per error — the exact cost this project exists to remove |
| K5 | **Block scalars.** `powerapps-yaml` states the `: `/`#` rule. `html-to-yaml` only bans flow style. | **`powerapps-yaml`**, keep the other's ban as an addition | 119 block scalars, all necessary: colon-space 69, colon-space+multiline 46, multiline 2, ` #` 2 |
| K6 | **Which reference is authoritative on properties.** `yaml-conventions.md` vs `confirmed-controls.md`. | **Merge into one `control-catalog.md`, rebuilt from `ledger/01` §2–3** | Both are Rank 2 and both are now known to be incomplete — `yaml-conventions.md` omits `Classic/CheckBox` (110 uses) and has 11 contradictions |
| K7 | **Example fidelity.** `html-to-yaml` points at `assets/examples/*.yaml` as patterns to follow. | **Do not carry them forward as patterns** | Per Vin, they compiled only after fixing. They become `error-taxonomy.md` input, not templates. The 17 clean screens are the templates |
| K8 | **Naming convention.** `html-to-yaml` references screen names from a different project (`1-Cases`, `2.1-FlagSN/HNW/UHNWChecklist`). | **Drop** | Project-specific, and the suite is general-purpose |

**No conflict was resolved in `html-to-yaml`'s favour.** Its value is entirely additive — it contributes
protocol, not conventions. That is a clean split and makes the merge low-risk.

## 6. What neither skill has

Gaps the merged skill must close. All are `high` confidence from `ledger/01`.

- **`OnVisible` is mandatory on every screen**, and it seeds all globals and collections with `If(IsBlank(…), Set(…))` / `If(IsEmpty(…), ClearCollect(…))` guards (17/17).
- **`Classic/CheckBox@2.1.0` exists** — 110 uses, absent from both skills' catalogs.
- **The fixed property sets** — every Label carries 6 properties, every Button 14, every container `Height` + `LayoutMinHeight` (see `ledger/01` §3).
- **`X`/`Y` are forbidden below the root** — needs stating as a prohibition, not just an omission, because `html-to-yaml` actively taught the opposite.
- **The `=Parent.Width - N` inset idiom** (~1,591 uses) — neither skill mentions it, and it is how insets are actually done.
- **Interactive-state values** — `FocusedBorderThickness` 1 or 2 and never 0; hover/pressed are light tints; hover keeps the text colour.
- **`Size` is a closed set of 11 values**, floor 8 ceiling 26.
- **Variable naming convention** — `gbl*` globals, `col*` collections, `var*` context variables. Visible in the `Variables_Bindings` sheet and in all 17 screens.
- **Nesting runs 6–8 deep**; a generator that flattens will not match the working set.

## 7. Recommended merge shape

`powerapps-yaml` is the skeleton. `html-to-yaml` is grafted on as the honesty-and-feedback layer.
Conventions come from `ledger/01`, not from either skill's reference files.

```
skills/generating-powerapps-yaml/
├── SKILL.md                       # powerapps-yaml's Intake + workflow, plus the
│                                  # CONFIRMED/UNVERIFIED rule and the isolated-snippet
│                                  # protocol from html-to-yaml
├── references/
│   ├── control-catalog.md         # rebuilt from ledger/01 §2-3. Supersedes both
│   │                              # yaml-conventions.md §2 and confirmed-controls.md
│   ├── layout-sizing.md           # ledger/01 §5-6. AutoLayout only; X/Y prohibited
│   │                              # below root; the closed Size set; the inset idiom
│   ├── patterns.md                # html-to-powerapps.md, minus its X/Y examples
│   └── error-taxonomy.md          # html-to-yaml's blocking/non-blocking table, plus
│                                  # failure modes diffed out of the three example files
└── scripts/
    └── validate_pa_yaml.py        # extended per ledger/01 — see below
```

**Validator additions** beyond the brief's minimum, each backed by a measured count:

- `X`/`Y` present on any control below depth 1 → **ERROR** (0 of 2,813 non-root controls)
- screen missing `OnVisible` or `Fill` → **ERROR** (17/17)
- `Size` outside {8,9,10,11,12,13,15,16,20,22,26} → **WARN**
- `FocusedBorderThickness: =0` on an interactive control → **WARN** (never observed)
- `Classic/CheckBox@2.1.0` added to the accepted catalog
- `GroupContainer` missing `LayoutMinHeight` → **WARN** (887/887 have it)
- flow-style mapping in a `Properties` block → **ERROR**
- a block scalar with no forcing character → **WARN** (0 of 119 were decorative)
