# Classic-designer "My clipboard" paste (partial, no import)

> **UNTESTED.** The classic designer's "My clipboard" path has never been exercised by this team,
> and nothing in `source-artifacts/` confirms it. It is kept because it is the only route that
> avoids building a package at all, which makes it worth trying for a single action or scope.
>
> If you use it, report what happened via `prompts/feedback-session.md` — confirming or killing
> this page is a genuinely useful contribution.


Use this when the user wants to drop **one action or a scope** into an **existing** flow without a
full package import. It's faster than the zip for edits, but it can't bring a trigger and it's
session-bound.

## How the user pastes it
1. In the flow, toggle the **New designer OFF** (top-right). The classic designer's clipboard
   accepts this simple format; the new designer often rejects it with *"The action you're trying to
   copy and paste doesn't match the current flow schema."*
2. Add a new step → **My clipboard** tab → the generated action appears as a card → click to insert.
3. For a block of actions, wrap them in a **Scope** and paste the scope once.

## The clipboard JSON format (hand-authorable)

```json
{
  "id": "<any GUID>",
  "brandColor": "#8C6CFF",
  "connectionReferences": {},
  "connectorDisplayName": "Data Operations",
  "icon": "https://connectoricons-prod.azureedge.net/releases/v1.0.1633/1.0.1633/dataoperationnew/icon.png",
  "isTrigger": false,
  "operationName": "Compose",
  "operationDefinition": {
    "type": "Compose",
    "inputs": "hello",
    "runAfter": {}
  }
}
```

- `operationDefinition` is the same action shape as in `wdl-schema.md` (`type`/`inputs`/`runAfter`).
- `operationName` is the action's display name.
- For a connector action, `operationDefinition.inputs` carries the `host` block, and you list the
  connector under `connectionReferences` here too — but the pasted action will still need its
  connection re-selected in the target flow.
- `runAfter` is usually left `{}`; the designer re-chains it when you drop it into position.

## What survives and what doesn't
- **Survives:** action type, static inputs, structure of a scope's children.
- **Often lost/broken:** dynamic-content expressions referencing steps that don't exist in the
  target flow, and connection selections (you re-pick the connection).
- **Never:** triggers (not copyable at all).

## When to prefer the zip instead
- You need the trigger too → zip.
- You're building the whole flow from a spec → zip.
- The target uses the new designer only and won't switch → zip (the new designer's `nodeData`
  clipboard format is too verbose to hand-author reliably).

Use the clipboard for surgical edits to an existing flow; use the package for whole flows.