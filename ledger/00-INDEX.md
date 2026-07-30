# 00 — Ledger index

One row per ledger file. Created by Session 1; every later session appends its own row.

Read this first in any session. Never re-derive what a ledger file already records.

| File | Holds | Written by | Consumed by | Status |
|---|---|---|---|---|
| `00-INDEX.md` | this table | S1 | all | live |
| `01-observed-conventions.md` | measured conventions from the 17 shipped screens, graded `high`/`medium`/`low` | S1 | S4 (schema), S5 (Power Apps YAML) | **done** |
| `02-reconciliation.md` | `yaml-conventions.md` vs the artifacts: confirmed / undocumented / contradicted | S1 | S4, S5, and every build session | **done — §3 awaiting Vin's rulings** |
| `03-skill-audit.md` | `powerapps-yaml` vs `html-to-yaml`: coverage, unique content, conflicts with a recommended winner | S3 | S5 | pending |
| `04-flow-rules.md` | Power Automate package structure and invariants | S3 | S8 | pending — **see `NOTE-flow-groundtruth-gap.md`; will be `confidence: low` throughout unless a real export lands first** |
| `05-list-rules.md` | SharePoint field types, naming, cross-list references, user-vs-automation columns | S3 | S6, S9 | pending |
| `06-vin-notes.md` | Vin's verdicts on the build-chat harvest | Vin | S2 | template only — awaiting Vin |
| `07-buildchat-raw.md` | the build chat's own account of corrections and recurring mistakes, verbatim | Vin | S2 | **done** — Rank 4, unverified |
| `08-buildchat-verified.md` | per-entry verdicts on `07` after checking against the artifacts; the "corrected 3+ times" list | S2 | S5–S9 | pending |

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

## Standing cautions

- **`source-artifacts/docs/yaml-conventions.md` exists twice**, byte-identical, the second copy
  inside `existing-skills/powerapps-yaml/references/`. One source, not two. See
  `source-artifacts/docs/PROVENANCE.md`.
- **`AccountClosure_Developer_Handbook.pdf` has not been reconciled.** If it contains its own
  YAML conventions, that is a doc-vs-doc conflict nobody has looked at.
- **`html-to-yaml`'s three example `.yaml` files are not clean ground truth** — per Vin they
  compiled only after fixing. They are S5's error-taxonomy input, and must not be treated as
  evidence of what pastes first try.
- **`ledger/01` has no independent human cross-check.** The recall half of `06` was reassigned
  to empirical measurement, so `01`'s confidence grades are the only vote on how elements are
  built.
