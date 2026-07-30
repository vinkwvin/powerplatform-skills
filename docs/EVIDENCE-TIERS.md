# Evidence tiers — how a rule earns its place in a skill

<!-- v1.0.0 -->

Read this before adding, changing, or removing any rule in any skill.

## The problem this solves

Every rule in this suite was measured against one system. "1,370 of 1,370 Labels carry these six
properties" is a real number, and it is a number about **one team building one app**.

Treat that as universal law and the skills become a straitjacket: the next project has a different
palette, a different type scale, a different layout, and the skill fights it. Treat it as mere
preference and the skills lose the thing that makes them worth having — the rules that actually
decide whether a paste compiles.

So every rule carries a tier. Three tiers, and they behave differently.

## The three tiers

### `PLATFORM` — a fact about Power Platform

True regardless of project, team, tenant, or design system. Violating it produces a failure the
platform itself generates.

- Interactive controls need the `Classic/` prefix; `Label`, `Gallery`, `GroupContainer` are bare
- A value containing `: ` must be a block scalar, or YAML mis-parses it
- `Classic/DropDown` and `Classic/Radio` need both `Items` and `Items.Value`
- `DropShadow.Light` does not exist
- A tab in leading whitespace breaks the paste
- Lookup columns are not delegable in Power Apps
- A legacy flow package needs `apisMap.json` and `connectionsMap.json`
- A `sharepoint_item` trigger returns an array, so it needs `splitOn`

**In a skill:** stated inline, as an instruction. **In a validator:** `ERROR`.
**Overridable:** never. A project that wants to violate a PLATFORM rule wants a different platform.

### `HOUSE` — this organisation's default

A convention the team adopted and applied consistently. Sound, worth defaulting to, and **not a
platform requirement**. A different project may legitimately choose otherwise — but should choose
once and then be consistent.

- Properties sorted alphabetically inside every `Properties` block
- `Size` drawn from a closed set, floor 8, ceiling 26
- The 31-colour palette, and `RGBA(56, 96, 178, 1)` reserved for `LoadingSpinnerColor`
- Two `LayoutOverflowY` scroll containers per screen, at depth 2
- Every `Label` carrying the same six properties
- `gbl*` / `col*` / `var*` variable prefixes
- List names `PascalCase_With_Underscores`, field names `PascalCase`
- The `<Verb>By` / `<Verb>At` audit pair on child lists
- Thai display text as a sibling `*_th` field, never inside a name

**In a skill:** stated with its count and its tier, so a reader knows it is a default rather than
a law. **In a validator:** `WARN`, and the numbers live in an editable config, not in the code.
**Overridable:** yes, per project, deliberately and in one place.

### `EXAMPLE` — illustration from a real system

Concrete material that makes a rule legible. Never a rule itself.

- `New_Request`, `Request_Prechecks`, `RequestID`, `gblRequestID`
- Account closure stages, the six designed flows, Thai field labels
- The specific screens `02_Sales_InitialContact.pa.yaml` and so on

**In a skill:** clearly marked as an example, and never the only way something is shown.
**In a validator:** never enforced.
**Overridable:** meaningless — it is data, not a rule.

## How to tell them apart

Ask: **what generates the failure if this is violated?**

| Answer | Tier |
|---|---|
| Power Apps Studio, SharePoint, or the flow importer | `PLATFORM` |
| A human reviewer, or inconsistency with the rest of the codebase | `HOUSE` |
| Nothing — it is just what this project happened to contain | `EXAMPLE` |

Second test, for the hard cases: **would this rule survive a project with a completely different
visual design and different business domain?**

- "Interactive controls need `Classic/`" — survives. `PLATFORM`.
- "`Size` ceiling is 26" — does not survive a project with a large-display design. `HOUSE`.
- "`RequestID` joins the child lists" — does not survive at all. `EXAMPLE`.

## The trap that produced this document

A measured count feels like proof, and it is — of the wrong proposition. `1,370/1,370` proves
*this team always did it*, not *it must always be done*. The count is real evidence for the
existence of a convention and no evidence at all about its necessity.

Two rules from the same measurement, one in each tier:

| Measurement | Tier | Why |
|---|---|---|
| 0 of 2,813 nested controls declare `X`/`Y` | **HOUSE** | AutoLayout was a design decision. Coordinate positioning is legal Power Apps; it just fights AutoLayout when mixed. Strong default, not law |
| 119 of 119 block scalars had a forcing character | **PLATFORM** on the requirement, **HOUSE** on the restraint | *Requiring* `|` when the value contains `: ` is YAML. *Never* using `|` otherwise is a tidiness convention |

Splitting a single measurement across tiers like this is normal. Do it rather than rounding the
whole finding to one tier.

## Applying this

1. **Every rule in a `references/` file is prefixed with its tier.**
2. **Inline rules in `SKILL.md` are PLATFORM-first.** A HOUSE rule goes inline only if violating
   it costs real rework; otherwise it lives in a reference.
3. **HOUSE numbers live in `assets/house-style.yaml`** inside the skill, not in validator code, so
   a new project edits one file.
4. **Validators exit non-zero on PLATFORM only.** HOUSE deviations warn. A team that has changed
   its palette should not have a red validator.
5. **When a field report arrives** (see `docs/IMPROVING-SKILLS.md`), assign the finding a tier
   before deciding what to change. A PLATFORM discovery is urgent and universal. A HOUSE
   discovery may just mean this project differs — and the fix may be a config value, not a rule.
