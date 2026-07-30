# NOTE — external research on Power Automate packages and community skills

Status: **finding, not a session deliverable.** Read alongside
`ledger/NOTE-flow-groundtruth-gap.md` before Session 3 Task B and Session 8.

## How to rank this

Public documentation and community repositories. **This is not in the 1–4 hierarchy and
does not substitute for a real export.** It is useful for *format* — what fields exist,
what they look like — and useless for *behaviour* — whether a given package imports cleanly
into the SCB/InnovestX tenant. Grade anything sourced here `confidence: medium` for
structure and `confidence: low` for anything about import success.

Where it corroborates a defect already found in the existing skill, say so as external
corroboration, not as verification.

---

## Finding 1 — no community skill solves this problem

Every Power Automate skill or plugin found assumes live API access to a tenant.

| Project | Mechanism | Offline legacy `.zip`? |
|---|---|---|
| `microsoft/power-platform-skills` (official) | self-contained MCP engine at `server/mcp.mjs`; `az login` + MSAL | **No** — requires tenant network access |
| `aaronba/PowerAutomate-skills` | Dataverse Web API + Flow Management API | **No** — exports `workflow.json` + `metadata.yml`, never mentions `manifest.json` |
| FlowStudio MCP | MCP server, 30+ tools | **No** |
| `ktg0066/power-automate-claude-skill` | appears in search results; both URLs returned 404 | **Unverified — could not fetch** |

Microsoft's official plugin ships six skills — `setup`, `browse-flows`, `create-flow`,
`build-flow`, `debug-flow`, `manage-flows` — and `build-flow` does "autonomously generate a
complete flow from a description". But it does it *through the API*, against a live
environment.

**What this means for the project.** Vin's constraint — closed environment, no CLI, no local
execution, everything pasted or uploaded through a browser — is not covered by any existing
skill. There is nothing to copy for the packaging layer. `building-powerautomate-flows` is
filling a real gap rather than reinventing something; that also means no community
implementation exists to check our packaging against, which is exactly why a real export
matters so much.

## Finding 2 — real packages contain files the existing skeleton lacks

External sources consistently list four files:

```
manifest.json
Microsoft.Flow/flows/<GUID>/definition.json
connections.json      ← optional per sources
flow.json             ← optional per sources; flow state and summary metadata
```

The existing skill's `template_skeleton` has only the first two. Whether `connections.json`
and `flow.json` are required, ignored, or generated on import is **unknown and cannot be
settled from documentation.** A real export answers it in one look.

## Finding 3 — external corroboration of the `connectionName` defect

Documented format for a real export:

```json
"connectionName": "shared-service-12345"
"id": "/providers/Microsoft.PowerApps/apis/shared_service/connections/shared-service-12345"
```

Hyphen-delimited, carrying a per-connection identifier, and the `id` path includes a
`/connections/<name>` segment.

The existing skeleton has:

```json
"connectionName": "shared_sharepointonline"
"id": "/providers/Microsoft.PowerApps/apis/shared_sharepointonline"
```

Underscore-delimited, holding the *connector API name*, with no per-connection identifier
and no `/connections/` segment. So the defect recorded in
`ledger/NOTE-flow-groundtruth-gap.md` is independently corroborated. The exact correct value
still requires a real export — documentation gives the shape, not our tenant's values.

## Finding 4 — `splitOn` literal form

For array-returning triggers:

```json
"splitOn": "@triggerOutputs()?['body/value']"
```

Consistent with the brief's rule. The existing skeleton's `OnNewItems` trigger has no
`splitOn` at all, and its validator does not check for one.

## Finding 5 — a contradiction to flag, not resolve

The brief states: *never generate `operationMetadataId` or `metadata`.*

External sources say each action in a real definition **has** an `operationMetadataId`.

These are reconcilable — "present in exports but must never be fabricated" is a coherent
rule — but the reconciliation is a guess. Two readings with different consequences:

- **(a)** Omit the field entirely; Studio populates it on import.
- **(b)** The field is required; carry it verbatim from the template export.

Do not pick one. A real export plus one import attempt settles it. Record as
`UNVERIFIED` in Session 3, per the guardrail on unverified properties.

## Finding 6 — `PackageFlowMissingConnectionMap` is a real error string

Confirmed as a genuine Power Automate import error: a flow resource missing mapping for
specific connections. Documented context is flows originating in a solution that lack
connection references. So at least one entry in the existing skill's error taxonomy is real
rather than invented.

## Finding 7 — the reframe that matters most

Standard (legacy) package export and solution export differ fundamentally: **a legacy
package requires connections to be remapped manually during import.** Solutions use
environment variables and support ALM; legacy packages do not.

So part of the "grey-X connection" experience is **expected behaviour of the legacy path**,
not purely a defect. The import UI asks the user to pick connections. That changes what the
skill should promise: not "this package imports silently and works", but "this package
imports and then prompts you to map N connections, which is normal — here is what to pick".

A skill that treats the connection prompt as a failure will send people chasing a bug that
is not there. This distinction is worth stating prominently in the SKILL.md.

---

## Sources

- [Editing Power Automate Export Packages — edvaldo b. guimarães filho](https://edvaldoguimaraes.com.br/2025/10/03/editing-power-automate-export-packages/) (503 at fetch time; surfaced in search results)
- [Exporting Power Automate Flows: Standard Packages vs. Solutions — edvaldo b. guimarães filho](https://edvaldoguimaraes.com.br/2025/10/03/exporting-power-automate-flows-standard-packages-vs-solutions/)
- [Understanding the Power Automate definition — wyattdave, DEV Community](https://dev.to/wyattdave/understanding-the-power-automate-definition-42po)
- [microsoft/power-platform-skills — power-automate plugin](https://github.com/microsoft/power-platform-skills/tree/main/plugins/power-automate)
- [aaronba/PowerAutomate-skills](https://github.com/aaronba/PowerAutomate-skills)
- [Export a solution — Microsoft Learn](https://learn.microsoft.com/en-us/power-automate/export-flow-solution)
- [Export and import flows — Microsoft Learn training](https://learn.microsoft.com/en-us/training/modules/administer-flows/2-flow-export-import)
- [Import Flow Fails: Connection Mapping Selections Don't Save — Power Platform Community](https://community.powerplatform.com/forums/thread/details/?threadid=82714e72-3a84-f011-b4cc-7c1e52151eee)
