# Legacy package structure

Every field below was read out of a real export from a live tenant. Tier `PLATFORM` throughout —
this is what the platform produces, not a convention.

## Contents
1. The five files
2. manifest.json
3. Microsoft.Flow/flows/manifest.json
4. apisMap.json and connectionsMap.json
5. definition.json
6. The two `connectionName` fields
7. What is safe to regenerate
8. Privacy

---

## 1. The five files

```
manifest.json
Microsoft.Flow/flows/manifest.json
Microsoft.Flow/flows/<assetGUID>/definition.json
Microsoft.Flow/flows/<assetGUID>/apisMap.json
Microsoft.Flow/flows/<assetGUID>/connectionsMap.json
```

A legacy package holds **one flow**. Multiple flows means multiple packages, or a solution export
— which is a different format with different rules.

Documentation elsewhere describes `connections.json` and `flow.json`. **Neither exists.** Those
names appear in community write-ups and are wrong; the real extra files are the two map files.

## 2. `manifest.json`

```json
{
  "schema": "1.0",
  "details": {
    "displayName": "...",
    "description": "",
    "createdTime": "2026-07-30T09:09:46.3195044Z",
    "packageTelemetryId": "<GUID>",
    "creator": "N/A",
    "sourceEnvironment": ""
  },
  "resources": { "<GUID>": { ... } }
}
```

`creator` was the literal string `"N/A"`, not an email. `sourceEnvironment` was empty. Both are
carried, not authored.

**`resources` is keyed by GUID**, not by friendly names. Three kinds:

| `type` | `configurableBy` | `suggestedCreationType` | `dependsOn` |
|---|---|---|---|
| `Microsoft.Flow/flows` | `User` | `New` | every connector and connection GUID |
| `Microsoft.PowerApps/apis` | `System` | `Existing` | `[]` |
| `Microsoft.PowerApps/apis/connections` | **`User`** | `Existing` | `[the apis GUID]` |

**Every connector needs both an `apis` resource and an `apis/connections` resource.** The
connections resource is the one marked `configurableBy: User`, and it is what makes the import UI
offer a connection picker. A package with only `apis` resources has nothing for the import to map.

The `apis` resource carries `"id": "/providers/Microsoft.PowerApps/apis/shared_sharepointonline"`
and `"name": "shared_sharepointonline"`. The `apis/connections` resource carries **no** `id` or
`name` — its `details.displayName` is the exporting user's email address.

The flow resource has **no** `id` and no `name` field.

## 3. `Microsoft.Flow/flows/manifest.json`

Small, and easy to forget:

```json
{ "packageSchemaVersion": "1.0",
  "flowAssets": { "assetPaths": ["<assetGUID>"] } }
```

## 4. `apisMap.json` and `connectionsMap.json`

Flat dictionaries, connector API name → resource GUID:

```json
// apisMap.json          -> the Microsoft.PowerApps/apis resource
{ "shared_sharepointonline": "bd833414-...", "shared_office365": "6dedcde4-..." }

// connectionsMap.json   -> the Microsoft.PowerApps/apis/connections resource
{ "shared_sharepointonline": "a77de9db-...", "shared_office365": "e812a341-..." }
```

Same keys in both. Every value must resolve to a resource in `manifest.json`, of the matching type.

**`connectionsMap.json` is almost certainly the "connection map" in
`PackageFlowMissingConnectionMap`.** The error names the artifact. Omit it and there is no map.

## 5. `definition.json`

```
name                                       a flow GUID
id                                         /providers/Microsoft.Flow/flows/<that GUID>
type                                       Microsoft.Flow/flows
properties
  apiId                                    /providers/Microsoft.PowerApps/apis/shared_logicflows
  displayName
  definition
    metadata                               tenant-specific; carry verbatim
    $schema                                .../2016-06-01/workflowdefinition.json#
    contentVersion                         1.0.0.0
    parameters                             $authentication (SecureObject), $connections (Object)
    triggers                               exactly one
    actions
    outputs                                {}
  connectionReferences
  flowFailureAlertSubscribed
  isManaged
```

**The flow GUID in `definition.json` is NOT the package asset GUID.** In the observed export the
folder was `5dbb1e49-…` and `properties`-level `name`/`id` were `0db6fe46-…`. Two different values.
Reusing one for both is not what a real export looks like.

`definition.metadata` holds `workflowEntityId`, `provisioningMethod`, `clientLastModifiedTime`,
`modifiedSources`, and a `creator` object with the user's GUID and the tenant GUID. **Carry it or
omit it — never author it.**

## 6. The two `connectionName` fields

The trap, and the reason a hand-built package fails:

| Location | Observed value | What it is |
|---|---|---|
| `connectionReferences` **key** | `shared_sharepointonline` | connector API name |
| `connectionReferences.<key>.connectionName` | `3c98a7f6391549e89bb9a2996b0cc3db` **and** `shared-office365-75c8d61c-8bb4-4fdb-a8b2-2a0b2265796d` | an **opaque per-connection id** |
| `actions.*.inputs.host.connectionName` | `shared_sharepointonline` | the API name again, matching the key |

Two connections in **one file** used two different formats. There is no pattern to generate — one
was a bare 32-hex string, the other `shared-<api>-<guid>`.

That is the whole argument for template anchoring. A validator can check that
`connectionReferences.<key>.connectionName` is not simply the key, and that is the best a
validator can do; the correct value has to come from a real export of the target tenant.

Each entry also carries `apiName`, `source: "Embedded"`, `tier: "NotSpecified"`, and
`isProcessSimpleApiReferenceConversionAlreadyDone: false`.

## 7. What is safe to regenerate

| Regenerate | Carry verbatim |
|---|---|
| `definition.triggers` | `connectionReferences` |
| `definition.actions` | `definition.metadata` |
| `displayName` (both manifests) | both manifests' resources and GUIDs |
| | `apisMap.json`, `connectionsMap.json` |
| | `packageTelemetryId`, `createdTime`, `creator` |

**If the flow needs a connector the template does not have, stop.** That connector's connection
identifiers do not exist in the template and cannot be invented. Ask for an export from a flow
that uses it.

## 8. Privacy

A real export contains, in plain text:

- the exporting user's **email address**, in each `apis/connections` resource `displayName`
- their **user GUID** and the **tenant GUID**, in `definition.metadata.creator`

Template anchoring means every generated package carries these. Say so before anyone sends a
package outside the organisation.
