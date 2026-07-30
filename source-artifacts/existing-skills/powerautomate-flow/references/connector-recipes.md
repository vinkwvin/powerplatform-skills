# Connector recipes — verified host blocks

The `host` block is where AI guesses and guesses wrong. Retrieve from here; for anything not listed,
**open the real action in the designer → ⋯ → Peek code and copy the `host` verbatim.** Never invent
an `operationId` or `apiId`.

Each recipe gives: the `connectionName` (also the `connectionReferences` key and manifest resource
`name`), the `apiId`, the common `operationId`s, and required parameter keys. Combine with the action
shape from `wdl-schema.md`.

> Operation IDs drift as connectors version. Treat this list as a strong default and confirm against
> Peek code when a paste/import rejects an operation.

## SharePoint — `shared_sharepointonline`
`apiId`: `/providers/Microsoft.PowerApps/apis/shared_sharepointonline`

| Purpose | operationId | key parameters |
|---|---|---|
| When an item is created | `OnNewItems` | `dataset` (site URL), `table` (list GUID) |
| When an item is created or modified | `OnUpdatedItems` | `dataset`, `table` |
| Get items | `GetItems` | `dataset`, `table`, optional `$filter`, `$top` |
| Get item (by ID) | `GetItem` | `dataset`, `table`, `id` |
| Create item | `PostItem` | `dataset`, `table`, then `item/<FieldInternalName>` |
| Update item | `PatchItem` | `dataset`, `table`, `id`, `item/<FieldInternalName>` |
| Delete item | `DeleteItem` | `dataset`, `table`, `id` |

`table` is the **list GUID** (or internal name). Field keys use the **internal** name and are
case-sensitive (e.g. `item/Title`, `item/AccountStatus`).

```json
"Update_item": {
  "type": "OpenApiConnection",
  "inputs": {
    "host": { "connectionName": "shared_sharepointonline", "operationId": "PatchItem",
              "apiId": "/providers/Microsoft.PowerApps/apis/shared_sharepointonline" },
    "parameters": {
      "dataset": "https://contoso.sharepoint.com/sites/AccountClosure",
      "table": "<New_Request LIST GUID>",
      "id": "@triggerBody()?['ID']",
      "item/AccountStatus": "Pending Middle check docs"
    },
    "authentication": "@parameters('$authentication')"
  },
  "runAfter": {}
}
```

## Office 365 Outlook — `shared_office365`
`apiId`: `/providers/Microsoft.PowerApps/apis/shared_office365`

| Purpose | operationId | key parameters |
|---|---|---|
| Send an email (V2) | `SendEmailV2` | `emailMessage/To`, `emailMessage/Subject`, `emailMessage/Body` |
| Send email with options | `SendEmailWithOptions` | `optionsEmailSubject`, `options`, `To` |
| Get emails (V3) | `GetEmailsV3` | `folderPath`, `top` |

## Office 365 Users — `shared_office365users`
`apiId`: `/providers/Microsoft.PowerApps/apis/shared_office365users`

| Purpose | operationId |
|---|---|
| Get my profile (V2) | `MyProfile_V2` |
| Get user profile (V2) | `UserProfile_V2` |
| Get manager (V2) | `Manager_V2` |

## Approvals — `shared_approvals`
`apiId`: `/providers/Microsoft.PowerApps/apis/shared_approvals`

| Purpose | operationId | notes |
|---|---|---|
| Start and wait for an approval | `StartAndWaitForAnApproval` | `approvalType` (e.g. `Basic`, `BasicAwaitAll`), `title`, `assignedTo`, `details` |
| Create an approval | `CreateAnApproval` | pair with "Wait for an approval" |

```json
"Start_and_wait_for_an_approval": {
  "type": "OpenApiConnection",
  "inputs": {
    "host": { "connectionName": "shared_approvals", "operationId": "StartAndWaitForAnApproval",
              "apiId": "/providers/Microsoft.PowerApps/apis/shared_approvals" },
    "parameters": {
      "approvalType": "Basic",
      "WorkflowApprovalCreationInput/title": "Approve account closure @{triggerBody()?['RequestId']}",
      "WorkflowApprovalCreationInput/assignedTo": "head-of-sales@contoso.com",
      "WorkflowApprovalCreationInput/details": "Please review."
    },
    "authentication": "@parameters('$authentication')"
  },
  "runAfter": {}
}
```

## Microsoft Dataverse — `shared_commondataserviceforapps`
`apiId`: `/providers/Microsoft.PowerApps/apis/shared_commondataserviceforapps`

| Purpose | operationId | key parameters |
|---|---|---|
| List rows | `ListRecords` | `entityName` (plural logical), `$filter`, `$select` |
| Get a row by ID | `GetItem` | `entityName`, `recordId` |
| Add a row | `CreateRecord` | `entityName`, then `item/<attr>` |
| Update a row | `UpdateRecord` | `entityName`, `recordId`, `item/<attr>` |
| Delete a row | `DeleteRecord` | `entityName`, `recordId` |

## Teams — `shared_teams`
`apiId`: `/providers/Microsoft.PowerApps/apis/shared_teams`

| Purpose | operationId |
|---|---|
| Post message in a chat or channel | `PostMessageToConversation` |
| Post adaptive card in a channel | `PostCardToConversation` |

## Notifications (mobile) — `shared_flowpush`
`apiId`: `/providers/Microsoft.PowerApps/apis/shared_flowpush`

| Purpose | operationId |
|---|---|
| Send me a mobile notification | `SendPushNotificationV2` |

## HTTP — no connector
`Http` action type, no `host`/`authentication`/connection reference. Premium.

## Data Operations — no connector
`Compose`, `Select` (`type: "Select"`), `Join`, `Filter array` (`type: "Query"`),
`Create CSV table`/`Create HTML table` (`type: "Table"`), `Parse JSON` (`type: "ParseJson"`). None
need a `host` or connection reference — they're in-engine.

## Checklist when adding a connector to a flow
1. Confirm the skeleton's `manifest.json` already has that connection resource + it's in `dependsOn`.
   If not, the user must export a skeleton that uses this connector.
2. Add the entry to `properties.connectionReferences` (key = `connectionName`).
3. Use the `host` block from the table above (or Peek code).
4. Include `"authentication": "@parameters('$authentication')"`.
5. Run the validator — it re-checks all four cross-reference points.
