---
name: powerautomate-flow
description: >-
  Generate a Power Automate cloud flow as an importable legacy package (.zip) from a
  flow spec, so it can be uploaded in the browser via My Flows → Import → Import Package
  (Legacy) with no CLI. Use this whenever the user wants to build, scaffold, or generate a
  Power Automate flow from a description, a diagram, a SharePoint schema, or a Power Apps
  screen — including phrasings like "make a flow that…", "generate the flow zip",
  "Power Automate package", "build this approval flow", "turn this workflow diagram into a
  flow", or "create the definition.json". Also use when the user reports that a flow package
  won't import (grey connection X, silent import failure, "flow schema doesn't match") and
  needs it diagnosed and fixed, or when they want a scope/action pasted via the classic
  designer's "My clipboard". This is the Power Automate counterpart to the powerapps-yaml
  skill: same generate-text → paste-into-browser loop, different target format.
---

# Flow spec → importable Power Automate legacy package (.zip)

## What this does

You describe a flow (trigger + steps, or a workflow diagram / SharePoint schema) and get back a
**legacy package .zip** that imports in the browser — no Power Platform CLI, no local scripts on
the corporate machine. The zip contains a `manifest.json` and a
`Microsoft.Flow/flows/<GUID>/definition.json`, where the definition is the Logic Apps Workflow
Definition Language (WDL) JSON that *is* the flow.

Power Automate has no clean human-editable "flow-as-YAML" like Power Apps' pa.yaml, and its code
view is **read-only** — so you cannot paste a whole flow's JSON into the designer. The two real
paste surfaces are (1) **Import Package (Legacy)** for a whole flow, and (2) the **classic
designer's "My clipboard"** for one action/scope. This skill targets both, zip first.

The single most important rule: **anchor on a real exported package, don't invent one.** AI-built
zips fail because the manifest plumbing, GUIDs, and connector `host` blocks are guessed. Regenerate
only the `definition.json` body against a real skeleton the user exported once, and let the
validator catch the rest.

## Step 0 — Intake (quick, do first)

Settle these before writing JSON. If the user already answered, state your assumption and move on.

1. **Skeleton available?** Has the user exported one real flow from the target environment
   (My Flows → ⋯ → Export → Package (.zip)) that uses the **same connectors** as the target flow?
   If yes, use its `manifest.json` verbatim and only regenerate `definition.json`. If no, tell them
   to export one first — it's the difference between a 1-try import and a debugging spiral. Use
   `assets/template_skeleton/` only as a last-resort generic fallback and flag that connections will
   likely need manual remap.
2. **Trigger type** — manual/instant (`Request`/`Button`), scheduled (`Recurrence`), or automated
   connector trigger (`OpenApiConnection`, e.g. "when a SharePoint item is created")? This decides
   the `triggers` block; see `references/wdl-schema.md`.
3. **Connectors used** — SharePoint, Office 365 Outlook/Users, Approvals, Dataverse, HTTP, etc. Each
   needs a `host` block and a connection reference. Pull known ones from
   `references/connector-recipes.md`; for anything not there, get the exact `host` from **Peek code**
   of a real action (never guess `operationId`/`apiId`).

If a choice is genuinely ambiguous and changes the output, ask one question. Otherwise pick the
sensible default, say so in a line, and proceed.

## Workflow

1. **Read the spec fully.** Trigger, ordered steps, branches/conditions, the data each step needs.
   If the input is a diagram or a SharePoint schema, list the actions in execution order first.
2. **Get the skeleton.** Read the user's exported `manifest.json`. Note the flow GUID (the folder
   name under `Microsoft.Flow/flows/`), the connection resource keys, and the `dependsOn` list. You
   will reuse all of this unchanged.
3. **Map each step to an action.** Decide type per step: connector call → `OpenApiConnection`;
   `Compose`/`Set variable`/`Initialize variable`; `If` → `If` (with `expression` + `actions`/`else`);
   `Apply to each` → `Foreach`; `Scope`; `HTTP`; `Terminate`. See `references/wdl-schema.md`.
4. **Name actions safely.** Keys use underscores for spaces (`Get_items`, `Send_an_email_V2`). Every
   expression reference must use that exact key: `outputs('Get_items')`, `body('Get_items')`,
   `items('Apply_to_each')`. A name typo orphans the reference — the #2 cause of failures.
5. **Chain with `runAfter`, not order.** Order comes from `runAfter`, not JSON position. First action
   in root (and first inside any Scope/If/Foreach) has `runAfter: {}`. Each later action:
   `runAfter: { "Previous_Action": ["Succeeded"] }`. Parallel branches share the same predecessor.
   This is the #1 cause of failures — get it right.
6. **Fill `host` blocks from recipes/Peek code.** Every connector action needs
   `host: { connectionName, operationId, apiId }` plus `authentication: "@parameters('$authentication')"`.
   Use `references/connector-recipes.md`; lift anything missing from a real Peek code block.
7. **Wire connection references.** Every `connectionName` used must appear in the definition's
   `properties.connectionReferences`, and the matching resource must already be in the skeleton's
   `manifest.json` `resources` + the flow's `dependsOn`. If the target flow uses a connector the
   skeleton doesn't, the user must export a skeleton that includes it — don't hand-add manifest
   resources unless you have a verified block for that connector.
8. **Assemble the package folder** exactly:
   ```
   <FlowName>_YYYYMMDD/
   ├── manifest.json                                  (from skeleton, displayName updated)
   └── Microsoft.Flow/flows/<GUID>/definition.json    (regenerated)
   ```
   Keep the GUID identical across folder name, manifest resource key, and definition `id`/`name`.
9. **Validate.** Run `python3 scripts/validate_flow.py <package-folder>` (stdlib only, no install).
   Fix every ERROR, review WARNs. This catches broken `runAfter`, dangling references, missing
   `authentication`, connection mismatches, and JSON errors *before* upload.
10. **Build the zip and deliver.** `python3 scripts/validate_flow.py <folder> --zip <out.zip>` writes
    a correctly-structured zip. Tell the user to import via **My Flows → Import → Import Package
    (Legacy)**, then remap connections on the import screen (credentials never travel in the zip —
    that's expected, not an error). List any placeholders or guessed values you couldn't verify.

## Core rules cheat-sheet

The ones that decide whether the import works. Details in the references.

- **Anchor on a real export.** Reuse the user's `manifest.json`; regenerate only `definition.json`.
- **`runAfter` is the execution graph.** First action → `runAfter: {}`; each next →
  `runAfter: {"Prev":["Succeeded"]}`. Order in the file is irrelevant.
- **Action key = reference name.** Underscores for spaces; `outputs('Exact_Key')` must match the key.
- **Connector actions need** a `host` block **and** `"authentication": "@parameters('$authentication')"`.
- **Connection cross-check:** every `connectionName` → in `connectionReferences` → in manifest
  `resources` → in flow `dependsOn`. All four or the connection shows a grey X.
- **GUID identical** across folder name / manifest key / definition id.
- **Edit the extracted file, then re-zip.** Never edit `definition.json` inside the zip.
- **Don't invent `operationId`/`apiId`.** Recipe library or Peek code only.
- **Expressions:** `@{...}` when embedding in a string, `@...` when the whole value is the expression.
  Escape single quotes in strings as `''`.

## Reference files — read the one you need

- `references/package-structure.md` — the package contract: exact folder layout, `manifest.json`
  anatomy (resources, dependsOn, connection resources), `definition.json` wrapper
  (`properties.definition` + `connectionReferences`), and the GUID rules. **Read this before
  assembling the folder**, and when diagnosing a grey-X connection or silent import failure.
- `references/wdl-schema.md` — the definition language: `$schema`/`contentVersion`/`parameters`,
  the three trigger types, every common action shape (`Compose`, variables, `If`, `Foreach`,
  `Scope`, `OpenApiConnection`, `HTTP`, `Terminate`), `runAfter` patterns for series/parallel/branch,
  and expression syntax. **Read this while writing actions.**
- `references/connector-recipes.md` — ready `host` blocks + connection references for the common
  connectors (SharePoint, Office 365 Outlook/Users, Approvals, Dataverse, HTTP, Teams,
  Notifications) with their `apiId`/`operationId` and required parameters. **Read this in step 6.**
  If a connector or operation isn't listed, get it from Peek code — don't guess.
- `references/clipboard-paste.md` — the *other* paste path: the classic-designer "My clipboard"
  action/scope JSON format for inserting a block into an existing flow without a full import, plus
  the warning about the new-designer format. **Read this when the user wants a partial paste, not a
  whole flow.**

## Validating and building

`scripts/validate_flow.py` is a dependency-free checker + zip builder. Run it on every package:

```bash
python3 scripts/validate_flow.py path/to/<FlowName>_YYYYMMDD          # validate
python3 scripts/validate_flow.py path/to/<FlowName>_YYYYMMDD --zip out.zip   # validate + build zip
```

It reports ERRORs (will break the import — dangling `runAfter` target, reference to a non-existent
action, `connectionName` missing from `connectionReferences`, connector action missing
`authentication`, invalid JSON, GUID mismatch, wrong folder structure) and WARNs (action name with
spaces, connection in `connectionReferences` but not in manifest `dependsOn`, missing `$schema`).
Non-zero exit on any ERROR. It is a safety net, not the source of truth — the references are.

## Gotchas worth remembering

- **The zip refuses silently.** A broken package usually just won't import with no useful message.
  That's why the validator exists — never upload an unvalidated package.
- **Connections always remap on import.** The grey/green connection step is normal; credentials are
  never in the zip. A grey X that *won't* go green means a `connectionReferences`↔manifest mismatch —
  a real bug, check the cross-references.
- **New vs classic designer clipboard differ.** The simple hand-authorable clipboard JSON is the
  *classic* format; the new designer uses a huge `nodeData` node format and often rejects pasted
  classic JSON ("doesn't match the current flow schema"). For partial pastes, use the classic
  designer. See `references/clipboard-paste.md`.
- **Triggers can't be copy-pasted** — only whole-flow import brings a trigger. That's the zip's
  main advantage over the clipboard.
- **Peek code is your source of truth for `host` blocks.** When unsure of an `operationId`, open a
  real action in the designer → ⋯ → Peek code, and copy the `host` verbatim.
