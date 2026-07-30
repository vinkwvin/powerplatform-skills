# Legacy package structure (the .zip that imports)

The whole point: reproduce the exact structure Power Automate emits on export, so import accepts it.
**Anchor on a real export.** Regenerate only `definition.json`; reuse `manifest.json` unchanged
except the display name.

## Folder layout (exact — do not rename or re-nest)

```
<FlowName>_YYYYMMDD/
├── manifest.json
└── Microsoft.Flow/
    └── flows/
        └── <FLOW_GUID>/
            └── definition.json
```

- `<FLOW_GUID>` is one GUID used in **three places**: the folder name, the manifest resource key,
  and `definition.json` → `name` / `id`. They must be identical.
- Zip the **contents** of `<FlowName>_YYYYMMDD/` (so `manifest.json` is at the zip root), not the
  parent folder. On Windows: select `manifest.json` + `Microsoft.Flow`, right-click → Compress to
  ZIP. The validator's `--zip` does this correctly for you.

## manifest.json anatomy

```json
{
  "schema": "1.0",
  "details": {
    "displayName": "Account Closure - Notify Middle Team",
    "description": "",
    "createdTime": "2026-07-15T00:00:00.0000000Z",
    "packageTelemetryId": "<GUID>",
    "creator": "user@contoso.com",
    "sourceEnvironment": ""
  },
  "resources": {
    "<FLOW_GUID>": {
      "id": null,
      "name": "<FLOW_GUID>",
      "type": "Microsoft.Flow/flows",
      "suggestedCreationType": "New",
      "creationType": "Existing, New, Update",
      "details": { "displayName": "Account Closure - Notify Middle Team" },
      "configurableBy": "User",
      "hierarchy": "Root",
      "dependsOn": [
        "<CONNECTION_KEY_SHAREPOINT>",
        "<CONNECTION_KEY_OUTLOOK>"
      ]
    },
    "<CONNECTION_KEY_SHAREPOINT>": {
      "id": "/providers/Microsoft.PowerApps/apis/shared_sharepointonline",
      "name": "shared_sharepointonline",
      "type": "Microsoft.PowerApps/apis",
      "details": { "displayName": "SharePoint" },
      "configurableBy": "System",
      "hierarchy": "Child",
      "dependsOn": []
    },
    "<CONNECTION_KEY_OUTLOOK>": {
      "id": "/providers/Microsoft.PowerApps/apis/shared_office365",
      "name": "shared_office365",
      "type": "Microsoft.PowerApps/apis",
      "details": { "displayName": "Office 365 Outlook" },
      "configurableBy": "System",
      "hierarchy": "Child",
      "dependsOn": []
    }
  }
}
```

Notes:
- The connection resource **keys** (`<CONNECTION_KEY_*>`) are arbitrary strings in the real export
  (often GUIDs). Whatever they are, the flow resource's `dependsOn` must list them, and the
  connection resource `name`/`id` must point at the connector (`shared_sharepointonline`, etc.).
- `creationType` "Existing, New, Update" lets the importer offer "Create as new". Keep the export's
  value.
- The load-bearing invariant: **for every connector the flow uses, there is a connection resource
  here, it's in `dependsOn`, and its `name` matches the `connectionName` used in the definition.**

## definition.json anatomy

The flow object wraps the WDL definition under `properties.definition`, plus a
`connectionReferences` map.

```json
{
  "name": "<FLOW_GUID>",
  "id": "/providers/Microsoft.Flow/flows/<FLOW_GUID>",
  "type": "Microsoft.Flow/flows",
  "properties": {
    "apiId": "/providers/Microsoft.PowerApps/apis/shared_logicflows",
    "displayName": "Account Closure - Notify Middle Team",
    "definition": {
      "$schema": "https://schema.management.azure.com/providers/Microsoft.Logic/schemas/2016-06-01/workflowdefinition.json#",
      "contentVersion": "1.0.0.0",
      "parameters": {
        "$connections": { "defaultValue": {}, "type": "Object" },
        "$authentication": { "defaultValue": {}, "type": "SecureObject" }
      },
      "triggers": { "...": "see wdl-schema.md" },
      "actions": { "...": "see wdl-schema.md" }
    },
    "connectionReferences": {
      "shared_sharepointonline": {
        "connectionName": "shared_sharepointonline",
        "source": "Embedded",
        "id": "/providers/Microsoft.PowerApps/apis/shared_sharepointonline",
        "tier": "NotSpecified"
      },
      "shared_office365": {
        "connectionName": "shared_office365",
        "source": "Embedded",
        "id": "/providers/Microsoft.PowerApps/apis/shared_office365",
        "tier": "NotSpecified"
      }
    }
  }
}
```

The `connectionReferences` key **must equal** the `connectionName` used inside each action's
`host` block. That is the link the importer follows.

## The connection cross-check (memorize this chain)

A connection is wired correctly only if the same connector appears in **all four** places:

1. action `inputs.host.connectionName` — e.g. `shared_sharepointonline`
2. `properties.connectionReferences["shared_sharepointonline"]`
3. `manifest.json.resources[<key>]` with `name: "shared_sharepointonline"`
4. the flow resource's `dependsOn` includes `<key>`

Miss any one → grey X on import that never turns green. The validator checks 1↔2 (from the
definition) and, if given the manifest, 2↔3↔4.

## Why this beats a from-scratch AI zip

The manifest keys, `packageTelemetryId`, `creationType` flags, and connection resource shapes are
fiddly and environment-flavored. Regenerating them invites silent import failure. Exporting once and
reusing the manifest means the only thing that changes between flows is the `definition.json` body —
the part that's genuinely different and worth generating.
