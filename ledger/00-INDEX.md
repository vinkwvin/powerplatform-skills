# 00 — Ledger index

One row per ledger file. Created by Session 1; every later session appends its own row.

Read this first in any session. Never re-derive what a ledger file already records.

| File | Holds | Written by | Consumed by | Status |
|---|---|---|---|---|
| `00-INDEX.md` | this table | S1 | all | live |
| `01-observed-conventions.md` | measured conventions from the 17 shipped screens, graded `high`/`medium`/`low` | S1 | S4 (schema), S5 (Power Apps YAML) | **done** |
| `02-reconciliation.md` | `yaml-conventions.md` vs the artifacts: 23 confirmed, 24 undocumented, 11 contradicted | S1 | S4, S5, and every build session | **done — §3 RESOLVED: conflicts → artifacts win; doc-only rules stand; AutoLayout over X/Y** |
| `03-skill-audit.md` | `powerapps-yaml` vs `html-to-yaml`: coverage, unique content, 8 conflicts with winners | S3 | S5 | **done** — no conflict resolved in `html-to-yaml`'s favour; its value is additive protocol |
| `04-flow-rules.md` | Power Automate package structure and invariants | S3 | S8 | **done — nothing in it is Rank 1.** Six flows are *designed* (`medium`); packaging is *asserted* (`low`) or *researched* (`medium` on format only). No invariant is observed |
| `05-list-rules.md` | 10 lists / 131 fields: types, naming, the text-not-Lookup delegation rule, audit-trail pattern, Title repurposing | S3 | S6, S9 | **done** |
| `06-vin-notes.md` | Vin's verdicts on the build-chat harvest | Vin | S2 | template only — awaiting Vin |
| `07-buildchat-raw.md` | the build chat's own account of corrections and recurring mistakes, verbatim | Vin | S2 | **done** — Rank 4, unverified |
| `08-buildchat-verified.md` | per-entry verdicts on `07` after checking against the artifacts; the "corrected 3+ times" list | S2 | S5–S9 | pending |

## Spec contract — Session 4

| File | Holds | Consumed by |
|---|---|---|
| `spec/solution-spec.schema.yaml` | the contract, and simultaneously a filled worked example. 10 top-level keys: `meta` `process` `roles` `glossary` `lists` `relations` `screens` `variables` `flows` `bindings`. Validates clean | all five skills; each reads only its own sections |
| `spec/validate_spec.py` | structure + referential integrity. Non-zero exit, every message naming the offending key path | every skill, as its D2 gate on spec input |

Derived from the formats that already existed rather than invented — `AccountClosure_SharePoint_Database.xlsx` sheets 11–14 map one-to-one onto `flows[]`, `variables[]`, `screens[]` reads/writes, and `bindings[]`.

Two rules the validator enforces that are easy to lose later:
- `relations[].kind: lookup` is **rejected outright**, with the delegation reason in the message
- `trigger.kind: sharepoint_item` **requires** `splits_on`; any other trigger kind warns if it sets one

## Notes — findings recorded outside the numbered sequence

Not session deliverables. Each was produced when the finding appeared, so it would survive to
the session that needs it.

| File | Holds | Read before |
|---|---|---|
| `NOTE-flow-groundtruth-gap.md` | evidence that the existing flow skill's template is hand-authored, its validator passes its own skeleton, and what one throwaway export would settle | S3 Task B, S8 |
| `NOTE-flow-external-research.md` | public docs and community repos on legacy packages; no community skill covers offline `.zip` generation | S3 Task B, S8 |
| `NOTE-manual-skill-proposal.md` | measured structure of the two 360 reference manuals, and the spec fields a manual needs that no builder does | S4, S9 |
| `NOTE-harvest-spotchecks.md` | three checks run when `07` arrived, incl. the confirmed matrix leftover at `08_HeadOfSales_Approval.pa.yaml:18` | S2 |

## Scripts

| Script | Does | Written by |
|---|---|---|
| `scripts/harvest_yaml.py` | measures control types, property sets, alphabetical ordering, sizing values, block scalars and their forcing characters, nesting depth, `LayoutOverflowY`, and RGBA usage across a folder of `*.pa.yaml` | S1 |

## Corrections to PROJECT-BRIEF discovered by Session 3

- **`New_Request` has 61 fields, not 38.** The brief's Session 6 fixture description is wrong.
- **10 lists, not 6** — and `Request_Files` is a document library, not a list.
- **Six flows, not seven.** Flow 6 is a child flow called by four parents.
- **`splitOn` applies to exactly one of the six flows** — only Flow 4 has a SharePoint trigger. State the rule with its condition, or a reader will hunt for `splitOn` on a Power Apps trigger.

## Skills built

| Skill | Session | Validator tested | Notes |
|---|---|---|---|
| `generating-powerapps-yaml` | 5 | 17 real screens clean; 6 injected defects caught | merges the two retired YAML skills |
| `building-sharepoint-lists` | 6 | clean spec passes; 7 injected defects caught; 131-field round trip lossless | ships `xlsx_to_spec.py` for existing systems |
| `planning-powerplatform-solutions` | 7 | renders the real spec to a 9-section overview, HTML + PDF | writes the spec the other four read |

## Standing cautions

- **`source-artifacts/docs/yaml-conventions.md` exists twice**, byte-identical, the second copy
  inside `existing-skills/powerapps-yaml/references/`. One source, not two. See
  `source-artifacts/docs/PROVENANCE.md`.
- **`AccountClosure_Developer_Handbook.pdf` has not been reconciled.** If it contains its own
  YAML conventions, that is a doc-vs-doc conflict nobody has looked at.
- **`html-to-yaml`'s three example `.yaml` files are not clean ground truth** — per Vin they
  compiled only after fixing. They are S5's error-taxonomy input, and must not be treated as
  evidence of what pastes first try.
- **`AccountClosure_SharePoint_Database.xlsx` sheets 12-14 are `solution-spec.yaml` in spreadsheet
  form.** `Variables_Bindings` (17 rows) is `variables[]`; `Screen_Data_Matrix` (18 rows) is
  `bindings[]` per screen; `App_Field_Coverage` (409 rows) is `bindings[]` per field. Session 4
  should derive from these rather than invent.
- **`ledger/01` has no independent human cross-check.** The recall half of `06` was reassigned
  to empirical measurement, so `01`'s confidence grades are the only vote on how elements are
  built.
