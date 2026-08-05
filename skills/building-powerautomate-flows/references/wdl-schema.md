# Workflow Definition Language (WDL) — the flow body

> **Provenance and tier.** Salvaged from the retired `powerautomate-flow` skill. Workflow
> Definition Language is publicly documented and stable, so this is `PLATFORM` and checkable
> without a tenant — but it was written before any real export existed here. Where it disagrees
> with `references/package-structure.md`, **that file wins**: it was read out of a real export.
>
> Known corrections already applied elsewhere: `operationMetadataId` does **not** appear in a real
> export (never generate it), and `splitOn` applies only to array-returning triggers.


This is what goes in `properties.definition`. Power Automate is Logic Apps under the hood, same
schema. Everything here is inside `definition`.

## Contents
- Top-level shape
- Triggers (3 types)
- Actions (the common ones)
- `runAfter` patterns — series, parallel, branch, error handling
- Control actions — If, Foreach, Scope, Until, Switch
- Expression syntax

## Top-level shape

```json
{
  "$schema": "https://schema.management.azure.com/providers/Microsoft.Logic/schemas/2016-06-01/workflowdefinition.json#",
  "contentVersion": "1.0.0.0",
  "parameters": {
    "$connections": { "defaultValue": {}, "type": "Object" },
    "$authentication": { "defaultValue": {}, "type": "SecureObject" }
  },
  "triggers": { "<TriggerName>": { ... } },
  "actions": { "<ActionName>": { ... }, "<ActionName2>": { ... } }
}
```

`triggers` and `actions` are **objects keyed by name**, not arrays. The key is the name; underscores
stand in for spaces. Execution order is set by `runAfter`, never by position.

## Triggers (pick one)

### Manual / instant (button, or called from a Power App)
```json
"manual": {
  "type": "Request",
  "kind": "Button",
  "inputs": { "schema": { "type": "object", "properties": {}, "required": [] } }
}
```
Add input fields under `properties` if the flow takes parameters.

### Scheduled (recurrence)
```json
"Recurrence": {
  "type": "Recurrence",
  "recurrence": { "frequency": "Day", "interval": 1, "timeZone": "SE Asia Standard Time" }
}
```
`frequency`: Second|Minute|Hour|Day|Week|Month.

### Automated (connector trigger — e.g. SharePoint item created)
```json
"When_an_item_is_created": {
  "type": "OpenApiConnection",
  "inputs": {
    "host": {
      "connectionName": "shared_sharepointonline",
      "operationId": "OnNewItems",
      "apiId": "/providers/Microsoft.PowerApps/apis/shared_sharepointonline"
    },
    "parameters": {
      "dataset": "https://contoso.sharepoint.com/sites/AccountClosure",
      "table": "<LIST_GUID>"
    },
    "authentication": "@parameters('$authentication')"
  },
  "recurrence": { "frequency": "Minute", "interval": 5 }
}
```
Get the exact `operationId` from Peek code of the real trigger — don't guess. Common ones are in
`connector-recipes.md`.

## Actions — common shapes

All action objects live under `actions`. Each has `type`, `inputs` (or control-specific keys), and
`runAfter`.

### Compose
```json
"Compose": { "type": "Compose", "inputs": "@triggerBody()", "runAfter": {} }
```

### Initialize / Set variable
```json
"Initialize_variable": {
  "type": "InitializeVariable",
  "inputs": { "variables": [ { "name": "Counter", "type": "integer", "value": 0 } ] },
  "runAfter": {}
},
"Set_variable": {
  "type": "SetVariable",
  "inputs": { "name": "Counter", "value": "@add(variables('Counter'), 1)" },
  "runAfter": { "Initialize_variable": ["Succeeded"] }
}
```
Variable types: string, integer, float, boolean, array, object. `InitializeVariable` actions must
sit at **root level** (not inside a Foreach/Scope) — Power Automate enforces this.

### Connector call (OpenApiConnection) — the general shape
```json
"Send_an_email_V2": {
  "type": "OpenApiConnection",
  "inputs": {
    "host": {
      "connectionName": "shared_office365",
      "operationId": "SendEmailV2",
      "apiId": "/providers/Microsoft.PowerApps/apis/shared_office365"
    },
    "parameters": {
      "emailMessage/To": "middle-team@contoso.com",
      "emailMessage/Subject": "Account closure pending your check",
      "emailMessage/Body": "<p>Request @{triggerBody()?['RequestId']} is ready.</p>"
    },
    "authentication": "@parameters('$authentication')"
  },
  "runAfter": { "Compose": ["Succeeded"] }
}
```
Parameter keys with `/` (like `emailMessage/To`) are how nested connector inputs are flattened —
keep them exactly as Peek code shows.

### HTTP (premium)
```json
"HTTP": {
  "type": "Http",
  "inputs": { "method": "POST", "uri": "https://...", "headers": {}, "body": {} },
  "runAfter": {}
}
```

### Terminate
```json
"Terminate": {
  "type": "Terminate",
  "inputs": { "runStatus": "Succeeded" },
  "runAfter": { "Send_an_email_V2": ["Succeeded"] }
}
```

## runAfter — the execution graph

Order is **only** what `runAfter` says. Position in the JSON is cosmetic.

- **First action** (root, or first child of a Scope/If/Foreach): `"runAfter": {}`.
- **Series:** each action names its predecessor with the statuses it accepts:
  `"runAfter": { "Previous_Action": ["Succeeded"] }`.
- **Parallel branches:** two actions share the *same* predecessor — both have
  `"runAfter": { "Same_Predecessor": ["Succeeded"] }`. They then run in parallel.
- **Run-after-failure (error handling / "configure run after"):** accept other statuses:
  `"runAfter": { "Risky_Action": ["Failed", "TimedOut"] }`. Valid statuses:
  `Succeeded`, `Failed`, `Skipped`, `TimedOut`.

Every name in a `runAfter` must be a real action key at the **same nesting level**. A dangling
target is a top failure mode — the validator flags it.

## Control actions

### If (Condition)
```json
"Condition": {
  "type": "If",
  "expression": {
    "and": [ { "equals": [ "@triggerBody()?['Status']", "Approved" ] } ]
  },
  "actions": {
    "If_true_action": { "type": "Compose", "inputs": "approved", "runAfter": {} }
  },
  "else": {
    "actions": {
      "If_false_action": { "type": "Compose", "inputs": "rejected", "runAfter": {} }
    }
  },
  "runAfter": { "Compose": ["Succeeded"] }
}
```
Nested actions have their own `runAfter` scope — the first child is `{}`.

### Foreach (Apply to each)
```json
"Apply_to_each": {
  "type": "Foreach",
  "foreach": "@body('Get_items')?['value']",
  "actions": {
    "Inside_loop": { "type": "Compose", "inputs": "@items('Apply_to_each')", "runAfter": {} }
  },
  "runAfter": { "Get_items": ["Succeeded"] }
}
```
Reference the current item with `items('Apply_to_each')` — the arg is the loop's own name.

### Scope
```json
"Scope": {
  "type": "Scope",
  "actions": {
    "Step_1": { "type": "Compose", "inputs": "a", "runAfter": {} },
    "Step_2": { "type": "Compose", "inputs": "b", "runAfter": { "Step_1": ["Succeeded"] } }
  },
  "runAfter": {}
}
```
Scopes group actions (and are the unit the classic clipboard copies).

### Until / Switch
`Until` = `{ "type": "Until", "expression": "...", "limit": {...}, "actions": {...} }`.
`Switch` = `{ "type": "Switch", "expression": "@...", "cases": { "Case": { "case": "x", "actions": {...} } }, "default": { "actions": {...} } }`.

## Expression syntax

- Whole value is an expression: `"inputs": "@triggerBody()"`.
- Expression embedded in a string: `"@{...}"` — e.g. `"Request @{triggerBody()?['Id']} ready"`.
- Common functions: `triggerBody()`, `body('Action')`, `outputs('Action')`, `items('Loop')`,
  `variables('Name')`, `concat()`, `if()`, `equals()`, `add()`, `formatDateTime(utcNow(),'yyyy-MM-dd')`.
- Safe property access with `?[...]`: `triggerBody()?['Title']` won't throw if missing.
- **Escape single quotes** inside expression strings by doubling: `'it''s'`.
- Reference names in `body(...)`, `outputs(...)`, `items(...)` must exactly match the action **key**
  (underscores included). This is the same integrity the validator enforces.