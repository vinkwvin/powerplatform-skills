# NOTE — Power Automate has no ground truth

## RESOLVED — an export landed. See `ledger/04-flow-rules.md` §0.

The gap this file describes is closed. Kept because its diagnosis was largely correct and the
comparison is instructive:

- **Confirmed:** the `template_skeleton` is hand-authored, and its
  `connectionReferences.<key>.connectionName` does hold the connector API name where an opaque
  per-connection identifier belongs.
- **Confirmed:** the skeleton's `OnNewItems` trigger is missing `splitOn`; a real export of an
  array-returning trigger carries it.
- **Understated:** the skeleton is missing **three whole files**, not just some field values.
- **Wrong in the other direction:** this file relayed the research claim that
  `operationMetadataId` belongs in a real definition. It does not appear at all.

Status: **finding, not a session deliverable.** Recorded before Session 1 ran.

## The fact that starts this

Vin has never built a Power Automate flow. No `.zip` has ever been exported, and none has
ever been imported. So `/source-artifacts/flows/` has no Rank 1 occupant, and cannot get
one without ten minutes of browser work.

That matters more than a missing folder, because the existing `powerautomate-flow` skill
reads as though it were artifact-backed and is not.

## Evidence — the template is hand-authored

`assets/template_skeleton/` in the existing skill is synthetic. From the files themselves:

| Field | Value found | What a real export has |
|---|---|---|
| `details.packageTelemetryId` | `00000000-0000-0000-0000-000000000000` | a genuine GUID |
| `details.creator` | `REPLACE@contoso.com` | the exporting user |
| flow resource id | `11111111-2222-3333-4444-555555555555` | a real flow GUID |
| `details.createdTime` | `2026-07-15T00:00:00.0000000Z` | a precise timestamp, not midnight |
| trigger `dataset` | `https://contoso.sharepoint.com/sites/REPLACE` | a real site URL |
| `details.sourceEnvironment` | `""` | the source environment |

**The one that matters most:** `properties.connectionReferences` sets
`connectionName: "shared_sharepointonline"` — the *connector API name*. In a real legacy
export that field carries a per-connection identifier, not the API name. So the skill's own
template violates the rule the brief states most prominently: *`connectionReferences` is
never hand-authored; carry it verbatim from a real export.* The template is hand-authored
`connectionReferences`.

**Second:** the trigger is `OnNewItems`, which returns an array, and it has no `splitOn`.
The brief calls `splitOn` mandatory on array-returning triggers, with the failure being
"fires once per batch". Neither the template nor the validator honors it.

## Evidence — the validator cannot catch either problem

Run against the skill's own skeleton:

```
$ python3 validate_flow.py template_skeleton
0 error(s), 0 warning(s).
OK. Build the zip with --zip <out.zip>, then import via My Flows → Import → Import Package (Legacy).
$ echo $?
0
```

It passes clean. What it actually checks is internal self-consistency — "every
`connectionName` used in an action's `host` block is declared in
`properties.connectionReferences`" — which the skeleton satisfies by construction. Grepping
the source shows **no `splitOn` check exists at all**.

So the validator enforces the template's own conventions and will always pass anything built
from the template. It cannot detect the grey-X import failure it was written to prevent,
because detecting that requires ground truth it does not have.

None of this means the skill is worthless. It means its packaging layer is unverified and is
currently presented as verified.

## What unblocks it — ~10 minutes, no CLI

1. Power Automate → **Create** → **Automated cloud flow** → trigger **"When an item is
   created"** (SharePoint), pointed at any list, including a throwaway → add one action,
   **"Send an email (V2)"** → Save.
2. **My Flows** → the flow → **⋯** → **Export** → **Package (.zip)**. That is the legacy format.
3. Upload to `/source-artifacts/flows/`.

One export settles: the real `connectionName` format, real `packageTelemetryId` and
`sourceEnvironment`, the true manifest resource shape, whether a real export of an
array-returning trigger carries `splitOn`, and whether Studio emits `operationMetadataId`
or `metadata` at all — the brief says never to generate them, and a real export shows what
is actually there.

**Then the test that matters:** re-import the unmodified zip. If it imports clean, the
package structure is confirmed. Then regenerate only `definition.json`, re-import, and the
exact loop the skill is built around has been observed working rather than assumed.

A second flow using **Approvals** is worth three more minutes — account closure is
approval-heavy and that connector has a distinctive connection shape.

## Consequences for the session map

**Session 3 Task B.** The task promises "every invariant, each paired with the failure it
prevents." With no real export, every invariant is an assertion drawn from a synthetic
template and every failure is hypothesized. Task B still runs, but `ledger/04` must be
written as *"what the existing skill asserts, unverified"* — `confidence: low` throughout,
source recorded as the skill's own template, failures marked hypothesized. Nothing in it may
read as artifact-backed. This is still useful: Session 8 needs to know what is being claimed.

**Session 8.** Three-way split rather than an upgrade:

- **Salvage** — `wdl-schema.md` (219 lines), `connector-recipes.md` (132). Workflow Definition
  Language is publicly documented and stable; checkable without a tenant.
- **Rebuild against a real export** — `package-structure.md` (144), `manifest.json`,
  `connectionReferences`, GUID handling. The invention is concentrated here.
- **Keep but mark untested** — `clipboard-paste.md` (52), the classic-designer fallback.

The validator must gain a `splitOn` check on array-returning triggers and a check that
`connectionName` is not the connector API name.

**Gate:** if `/source-artifacts/flows/` is still empty when Session 8 opens, stop and say so.

## The asymmetry worth carrying

The two validators in this suite are not equally trustworthy, and the skills should say so.
Seventeen screens that compiled in Studio back the Power Apps validator. Zero observed
imports back the flow validator.
