# 04 — Power Automate flow rules

Session 3 Task B, **revised after a real export landed.**

# 0. OBSERVED — a real legacy export, Rank 1

`source-artifacts/flows/OOP[SaleSupportTeam]…updateKYC&SUIT_20260730090946.zip` — a genuine
export from the InnovestX tenant. This section is Rank 1 and **overrides everything below it.**

## 0.1 The package has five files, not two

```
manifest.json
Microsoft.Flow/flows/manifest.json                       <- a SECOND manifest
Microsoft.Flow/flows/<assetGUID>/definition.json
Microsoft.Flow/flows/<assetGUID>/apisMap.json            <- nothing predicted this
Microsoft.Flow/flows/<assetGUID>/connectionsMap.json     <- nothing predicted this
```

The existing skill's `template_skeleton` has only `manifest.json` + `definition.json`.
**Three files are missing from it.**

External research predicted `connections.json` and `flow.json`. **Both names are wrong.** The real
files are `apisMap.json` and `connectionsMap.json`, and there is no `flow.json`.

`Microsoft.Flow/flows/manifest.json` is tiny and lists the asset folders:

```json
{ "packageSchemaVersion": "1.0",
  "flowAssets": { "assetPaths": ["5dbb1e49-407c-4324-93ff-286a95d533d6"] } }
```

The two map files are flat connector→resource-GUID dictionaries:

```json
// apisMap.json          connector API name -> the apis resource GUID
{ "shared_sharepointonline": "bd833414-...", "shared_office365": "6dedcde4-..." }
// connectionsMap.json    connector API name -> the apis/connections resource GUID
{ "shared_sharepointonline": "a77de9db-...", "shared_office365": "e812a341-..." }
```

**This is almost certainly the "connection map" in `PackageFlowMissingConnectionMap`.** The error
names the artifact. A package without `connectionsMap.json` has no connection map to find.

## 0.2 Every connector needs TWO manifest resources, keyed by GUID

The skeleton used friendly keys (`conn_sharepoint`) and one resource per connector. Reality:

| Resource | `type` | `configurableBy` | `dependsOn` |
|---|---|---|---|
| the connector | `Microsoft.PowerApps/apis` | `System` | `[]` |
| **the connection** | `Microsoft.PowerApps/apis/connections` | **`User`** | `[the apis GUID]` |

Both keyed by **GUID**, not by a friendly name. The flow resource `dependsOn` lists all four.
`suggestedCreationType` is `Existing` on connector resources, `New` on the flow.

The `apis/connections` resource is the one whose `configurableBy: User` makes the import UI offer
a connection picker — and its `details.displayName` is **the exporting user's email address**.
The skeleton has no `apis/connections` resources at all.

## 0.3 Two different fields are both called `connectionName`

This is the trap, and it explains why the existing validator can be right while the skeleton is wrong.

| Location | Value in the real export | Meaning |
|---|---|---|
| `properties.connectionReferences.<key>` — the **key** | `shared_sharepointonline` | connector API name |
| `properties.connectionReferences.<key>.connectionName` | `3c98a7f6391549e89bb9a2996b0cc3db` and `shared-office365-75c8d61c-8bb4-4fdb-a8b2-2a0b2265796d` | **per-connection identifier, opaque** |
| `definition.actions.*.inputs.host.connectionName` | `shared_sharepointonline` | connector API name, matching the key above |

So: the existing validator's check (every `host.connectionName` must appear as a
`connectionReferences` key) is **correct**. What the skeleton gets wrong is the *value* of
`connectionReferences.<key>.connectionName` — it put the API name where an opaque per-connection ID
belongs. **Confirmed as a real defect.**

Note the two connections use **two different formats** — one bare 32-hex, one
`shared-<api>-<guid>`. There is no single pattern to generate, which is exactly why it must be
carried verbatim.

`connectionReferences` entries also carry `apiName` and
`isProcessSimpleApiReferenceConversionAlreadyDone`, neither present in the skeleton.

## 0.4 `splitOn` — confirmed, exactly as stated

Real trigger `When_an_item_is_created_or_modified`, `operationId: GetOnUpdatedItems`:

```json
"splitOn": "@triggerOutputs()?['body/value']"
```

One occurrence in the file, on the one array-returning trigger. The rule and its literal form are
now **observed**, not hypothesized. The trigger also carries `evaluatedRecurrence` alongside
`recurrence` — absent from the skeleton.

## 0.5 `operationMetadataId` — the brief was right, the research was wrong

**Zero occurrences across the entire definition.** Not on the trigger, not on any of the ~12
actions at any nesting level.

`ledger/NOTE-flow-external-research.md` Finding 5 reported that external sources say every action
has one, and flagged the brief's "never generate `operationMetadataId`" as a contradiction to
resolve. **It is resolved in the brief's favour.** Real exports do not carry it. Delete the
UNVERIFIED mark and keep the rule.

## 0.6 `metadata` — one occurrence, and it is tenant-specific

`"metadata"` appears exactly once, at `definition.metadata`, and holds environment junk:

```json
{ "workflowEntityId": null, "provisioningMethod": "FromDefinition",
  "creator": { "id": "<user GUID>", "type": "User", "tenantId": "<tenant GUID>" },
  "clientLastModifiedTime": "...", "modifiedSources": "Portal", ... }
```

So the rule needs splitting: **never generate per-action `metadata`** (it does not exist), and
**never author `definition.metadata`** — carry it from the template or omit it, because it embeds
a real user GUID and tenant GUID.

## 0.7 The flow GUID is not the asset GUID

| Where | GUID |
|---|---|
| package folder + manifest resource key | `5dbb1e49-407c-4324-93ff-286a95d533d6` |
| `definition.json` `name` and `id` | `0db6fe46-eecb-48d4-9dca-e700d82e6a1f` |

**Two different GUIDs.** The skeleton reuses one value for both. Whether the mismatch is required
or merely tolerated is unknown, but copying the skeleton's single-GUID shape is not what a real
export looks like.

## 0.8 Other fields the skeleton lacks

`properties.flowFailureAlertSubscribed` · `properties.isManaged` · `definition.outputs: {}` ·
`manifest.details.creator: "N/A"` (not an email) · `details.iconUri` on every connector resource ·
a real `packageTelemetryId` GUID.

## 0.9 Privacy — the skill must warn about this

A real export embeds, in plain text: the exporting user's **email address**
(`pimchanok.n@innovestx.co.th`, in two `apis/connections` resources) and their **user GUID and
tenant GUID** (`definition.metadata.creator`).

Template-anchoring means shipping those values inside every generated package. The skill must say
so plainly, so nobody publishes a package externally without checking. This file records the email
because the artifact is already committed to the repo; treat the repo accordingly.

## 0.10 What this changes for Session 8

- The generator must emit **five files**, and `apisMap.json` / `connectionsMap.json` are not optional.
- `manifest.json` resources must be **GUID-keyed**, with a paired `apis` + `apis/connections` resource per connector.
- Only `definition.json`'s `triggers`/`actions` are safely regenerable. `connectionReferences`, `definition.metadata`, both manifests, and both map files are **carry-verbatim**.
- The validator gains: all five files present · every connector in `apisMap` also in `connectionsMap` · every map value resolving to a manifest resource of the right `type` · `connectionReferences.<k>.connectionName` **not equal** to `<k>` · `operationMetadataId` absent · `splitOn` present on `sharepoint_item` triggers · `runAfter` cycle detection.

---

# The rest of this file predates the export

Everything below was written when no export existed. Section 0 supersedes it wherever they
disagree. Retained because the *designed flows* in §1 are still the only description of what the
account-closure flows should do.

## Read this before using anything below

Read `ledger/NOTE-flow-groundtruth-gap.md` and `ledger/NOTE-flow-external-research.md` too —
both now carry corrections.

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
