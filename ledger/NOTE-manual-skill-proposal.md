# NOTE — proposed fifth skill: app user manuals

Status: **proposal, not accepted.** Raised by Vin before Session 1 ran.
Not a session deliverable. Recorded so the finding survives to Session 2 Task D,
which is the last cheap moment to widen the spec schema.

## Reference artifacts measured

Two manuals from the 360 Degree Feedback Survey project, supplied by Vin.
Rank 1 for *document structure* (these shipped). Rank 1 for the troubleshooting
entries (real observed failures). They say nothing about Power Platform build rules.

| | user-friendly | full / admin |
|---|---|---|
| paragraphs | 116 | 418 |
| tables | 10 | 52 |
| images | 13 | 9 |
| words | ~607 | ~2,826 |
| H1 / H2 / H3 | 3 / 16 / 0 | 8 / 44 / 12 |
| TOC | none | `สารบัญ / Table of Contents` |
| numbering | `1.`–`9.` flat, per screen | decimal `1.1`, `3.0`, appendix `A`–`D` |
| heading language order | **English / Thai** | **Thai / English** |

### Full manual — H1 skeleton

1. บทนำ / Introduction — incl. access tiers, roles & responsibilities, who-reads-what, prerequisites
2. ภาพรวมระบบ / System Architecture — SharePoint lists, flows, screens, Power BI, data flow
3. การติดตั้งระบบครั้งแรก / Initial Setup (Admin) — starts with a setup checklist (`3.0`)
4. สำหรับผู้ให้คะแนนทุกคน / For Everyone
5. สำหรับทีม HR / For the HR Team
6. การแก้ปัญหาที่พบบ่อย / Troubleshooting — 8 entries
7. ภาคผนวก / Appendix A–D — Power Query M code, mapping tables, per-column calculation, glossary

### User-friendly manual — H1 skeleton

1. Introduction / บทนำ
2. Part A — For Everyone (Raters)
3. Part B — For the HR Team

## Finding 1 — the user manual is a projection of the full manual

Sections 4 and 5 of the full manual are Part A and Part B of the user manual,
compressed. Dropped entirely: architecture, admin setup, troubleshooting, appendix.

Consequence: generate **one** source and render two documents. Same logic as D1
(the spec is the product; the PDF is a rendering), applied one level up. Do not
author two documents that must be kept in sync by hand.

## Finding 2 — the full manual's tables are a rendering of the spec

Measured from the real document, not inferred:

| Table | Header | Spec section it renders |
|---|---|---|
| T15 (11r×3c) | `Screen \| หน้าที่ \| ใครเข้าถึงได้` | `screens[]` + purpose + role access |
| T14 (10r×3c) | `Flow \| ชนิด \| หน้าที่` | `flows[]` + type + purpose |
| T13 (8r×5c) | `List \| Column ที่ต้องใส่ค่าเอง \| Column ที่ถูก Automate` | `lists[].fields[]` + who populates each |
| T12 (7r×2c) | `List \| เก็บอะไร` | `lists[]` + purpose |
| T08 (5r×4c) | `ผู้ใช้ \| เห็นอะไรได้บ้าง` | roles — access tiers |
| T09 (6r×4c) | `บทบาท \| หน้าที่หลัก` | roles — responsibilities |
| T10 (4r×2c) | `ผู้อ่าน \| ส่วนที่ควรอ่าน` | roles — who reads what |
| T01 (4r×2c) | `เวอร์ชัน / Version` → `ฉบับร่าง 1.0 (Draft)` | `meta.version`, `meta.status` |

In the user-friendly manual, 9 of 10 "tables" are 1r×1c — single-cell frames
holding a screenshot plus caption (`Home / Summary screen`, `Begin Survey screen`).
Only the score-scale table carries data. So its per-screen shape is:
**heading → screenshot frame → bullet steps.**

## Spec fields this requires that no builder skill needs

Session 2 Task D must decide on these or the schema needs editing after four
skills already hard-code its key names.

- `screens[].purpose` — user-facing "what this screen is for". Builders need controls, not intent.
- `screens[].roles[]` — which role sees this screen. Drives the Part A / Part B split.
- `roles[]` — id, label, responsibilities, access tier, which manual sections apply.
- `flows[].purpose` and `flows[].type` — T14 has both; the flow builder needs neither.
- `lists[].purpose` — T12.
- `lists[].fields[].populated_by: user | automation` — T13. **Dual-use:** the SharePoint
  builder also wants this, since an automation-written column should not appear as a
  user-entry field. Strongest candidate of the set.
- `glossary[]` — Appendix D. **Already needed and already missing:** the planner skill's
  workflow runs "glossary first", and the brief's key list (`meta`, `process`, `screens[]`,
  `variables[]`, `lists[]`, `relations[]`, `flows[]`, `bindings[]`) has nowhere to put the
  result. Two independent consumers point at the same absent key.
- `meta.status: draft | final` — the reference full manual is stamped `ฉบับร่าง 1.0 (Draft)`.

## Finding 3 — two inputs Claude cannot generate

1. **Screenshots.** 13 and 9 images. Claude cannot capture a built Power App. The skill
   must emit numbered placeholder frames naming the screen, the state to put it in, and
   what to highlight — then a human pastes. Same class of constraint as paste-into-browser.
2. **Troubleshooting entries.** All 8 in the reference are specific observed failures
   (leading zeros dropped on SharePoint paste; Choice column rejecting a value; Power Query
   `#N/A`; Power BI not refreshing). These cannot be invented — same guardrail as the
   control catalog. They must come from a human or from a ledger of observed failures.
   In draft mode there are none, because nothing has failed yet.

## Open questions — Vin to decide

1. **Heading language order contradicts between the two references.** User-friendly leads
   English, full leads Thai. Deliberate or drift? Per D3 the TH↔EN convention belongs in
   Project knowledge, not inlined in a SKILL.md — but the skill needs a stated rule to follow.
2. **Content boundary with two existing documents.** Three artifacts would describe system
   structure: the planner's `system-overview.pdf` (pre-build), the existing
   `AccountClosure_Developer_Handbook.pdf`, and full-manual section 2 (post-build).
   The suite's organising rule is "mutually exclusive by artifact produced" — a `.docx` is a
   distinct artifact, so the taxonomy holds, but the *content* overlaps and needs explicit
   negative routes.
3. **Session placement.** Must come after the four builder skills exist and before packaging.
   Proposed: insert as Session 8, push lint-and-package to Session 9.
