# 04 — Power Automate flow rules

Session 3 Task B.

## Read this before using anything below

**No flow has ever been built, exported, or imported.** `/source-artifacts/flows/` holds no
export. Read `ledger/NOTE-flow-groundtruth-gap.md` and `ledger/NOTE-flow-external-research.md`
first.

Three source classes are mixed here and graded separately. Do not flatten them.

| Class | Source | Grade |
|---|---|---|
| **Designed** | `AccountClosure_SharePoint_Database.xlsx` → `11. Power_Automate` — six flows specified step by step against real lists | `medium` for *what the flows should do*; says nothing about packaging |
| **Asserted** | the existing skill's `SKILL.md`, references, and hand-authored `template_skeleton` | `low` — never validated against an import |
| **Researched** | public documentation and community repos | `medium` for format, `low` for import behaviour |

**Nothing here is Rank 1.** Every "failure it prevents" below is *hypothesized*, not observed.
That is the honest state, and it is why Session 8 is gated.

---

## 1. Designed flows — the only solid part of this file

Six flows, not seven. From the workbook, `confidence: medium`.

| Flow | Trigger | Steps | Lists touched |
|---|---|---|---|
| **1 — Submit & Dispatch** | Power Apps trigger (V2) | 11 | System_Config, New_Request, Request_Accounts, Request_Prechecks, Request_DocChecklist, Approval_Logs |
| **2 — Litigation Check** | Power Apps trigger | 5 | Litigation_Register, New_Request |
| **3 — Stage Decision** | Power Apps trigger | 7 | Role_Mapping, New_Request, Approval_Logs |
| **4 — Parallel Pre-check Gate** | **SharePoint — when an item is created or modified** | 6 | Request_Prechecks, New_Request, Approval_Logs |
| **5 — Close-out** | Power Apps trigger | 5 | Request_Tasks, New_Request, Approval_Logs |
| **6 — Notify / CC** | **child flow**, called by 1, 3, 4, 5 | 3 | System_Config, Role_Mapping |

### Patterns worth carrying into the skill

- **One shared notification child flow.** Flow 6 is called by four parents rather than duplicating mail logic. Recipients resolve from `System_Config` (`CC_<team>` keys) plus active `Role_Mapping` members.
- **Request/response flows.** 1, 2 and 5 end in `Respond to Power Apps`. Flow 1 returns the RequestID, which the app stores in `gblRequestID`. These are synchronous — the app waits.
- **Single-writer counter.** Flow 1 steps 2–4: `Get item` seed from `System_Config` → `Compose` → `Update item` seed+1, annotated *"single writer = no collision"*. The ID generator is deliberately funnelled through one flow.
- **Guard-then-act.** Flow 3 step 2 rejects a Reject/Return with an empty remark. Flow 5 step 3 fails close-out if open tasks remain, responding with an error the app displays. Guards live in the flow, not only in the UI.
- **Fan-in gate.** Flow 4 triggers on any precheck row change, re-reads all three rows for that request, and only advances when `count(Result ≠ Pending) = 3`. Three parallel departments, one gate.
- **Audit on every transition.** Every state-changing flow writes to `Approval_Logs`.

### The scoping fact that matters for `splitOn`

**Only Flow 4 has a SharePoint trigger.** The other five are Power Apps triggers or a child
trigger, and none of those return arrays. So `splitOn` — the brief's second-most-prominent flow
rule — applies to **exactly one of six flows** in this system.

That does not make the rule less true. It means the skill should state *when* it applies rather
than as a blanket, or a reader will hunt for `splitOn` on a Power Apps trigger and conclude
something is wrong.

Documented form: `"splitOn": "@triggerOutputs()?['body/value']"`.

## 2. Package structure — asserted and researched, not verified

| File | Status |
|---|---|
| `manifest.json` | present in both the skeleton and every external description |
| `Microsoft.Flow/flows/<GUID>/definition.json` | same |
| `connections.json` | **described externally, absent from the skeleton.** Required or not — unknown |
| `flow.json` | **described externally as flow state/summary, absent from the skeleton.** Unknown |

**Two files may be missing from everything this project has produced so far.** Neither can be
settled from documentation.

## 3. Invariants, each with the failure it is *believed* to prevent

`H` = hypothesized. `E` = externally corroborated. Nothing is `O` (observed) — that requires an import.

| Invariant | Believed failure if violated | Grade |
|---|---|---|
| `connectionReferences` carried verbatim from a real export, never hand-authored | `PackageFlowMissingConnectionMap`; grey-X connection at import | **E** — the error string is real; the documented `connectionName` format (`shared-service-12345`, with a `/connections/<name>` path segment) does not match the skeleton's `shared_sharepointonline` |
| `splitOn` on array-returning triggers | flow fires once per batch instead of once per item | **E** on form, **H** on consequence. Applies to Flow 4 only |
| Never generate `operationMetadataId` or `metadata` | import rejection or silent corruption | **CONTRADICTED — do not act on this yet.** External sources say every action in a real definition *has* an `operationMetadataId`. "Present in exports but never fabricated" reconciles it, but that is a guess. Mark `UNVERIFIED` |
| No cycles in `runAfter` | flow will not save or run | **H** — plausible and cheap to check; the validator must detect cycles |
| Execution order comes from `runAfter`, not key order | actions run in an unintended order | **E** |
| Every action referencing a connector declares its `connectionName` in `connectionReferences` | broken reference at import | **the one thing the existing validator does check** |
| `$connections` and `$authentication` declared in `definition.parameters` | authentication failure at run time | **E** |

## 4. What the existing validator does and does not do

`validate_flow.py`, 271 lines. Verified by running it.

**Does:** cross-checks every `connectionName` used in an action `host` block against
`properties.connectionReferences`; warns when a `connectionReferences` entry has no matching
manifest resource + `dependsOn`; walks nested operations.

**Does not:** check `splitOn` at all; check that `connectionName` is a per-connection identifier
rather than a connector API name; detect `runAfter` cycles; look for `connections.json` or
`flow.json`.

**And it passes its own skeleton clean** — `0 error(s), 0 warning(s)`, exit 0 — because it checks
self-consistency with conventions the skeleton defines. It cannot fail the template it ships with.

## 5. The reframe Session 8 must state prominently

A legacy package **requires connections to be remapped manually at import**; solutions use
environment variables and avoid this. So the connection-mapping prompt is **expected behaviour of
the legacy path, not a defect.**

A skill that presents the prompt as a failure sends teammates chasing a bug that does not exist.
Distinguish clearly:

- *"Import asks you to pick connections"* → normal. Pick them.
- *"Import shows a grey X you cannot resolve, or `PackageFlowMissingConnectionMap`"* → real failure.

## 6. What one throwaway export settles

Listed so the value is concrete: the real `connectionName` format · real `packageTelemetryId` and
`sourceEnvironment` · whether `connections.json` and `flow.json` exist and are required · whether a
real export of an array trigger carries `splitOn` · whether `operationMetadataId` appears, and
whether an import survives without it · the true manifest resource shape.

**Then:** re-import the unmodified zip. Clean import confirms the structure. Regenerate only
`definition.json`, re-import, and the loop the skill is built around has been observed rather than
assumed.
