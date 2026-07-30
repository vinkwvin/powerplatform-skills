# 05 — SharePoint list rules

Session 3 Task C. Measured from `AccountClosure_SharePoint_Database.xlsx` (10 list sheets plus
`Power_Automate`, `Variables_Bindings`, `Screen_Data_Matrix`, `App_Field_Coverage`) and
`AccountClosure_SharePoint_List_Setup.xlsx` (12 sheets, the provisioning form).

Rank 1 for *schema design*. These lists were designed and documented alongside 17 screens that
compiled; whether every column was provisioned exactly as specified is not verified here.

## Contents
1. The ten lists
2. Field-type distribution
3. Cross-list references — the delegation rule
4. Naming conventions
5. The audit-trail pattern
6. Title repurposing
7. The document library
8. User-populated vs automation-populated
9. Corrections to the brief

---

## 1. The ten lists

| # | List | Fields | Role |
|---|---|---|---|
| 1 | `New_Request` | **61** | the request header — one row per closure request |
| 2 | `Request_Accounts` | 14 | one row per account in the closure inventory |
| 3 | `Request_Tasks` | 9 | per-team settlement tasks |
| 4 | `Request_Prechecks` | 13 | one row per checking department (DA / Middle / ProductOp EQ) |
| 5 | `Request_Files` | 6 | **document library**, not a list |
| 6 | `Request_DocChecklist` | 7 | required-document checklist, varies by `IsAlive` |
| 7 | `Approval_Logs` | 7 | append-only audit trail |
| 8 | `Role_Mapping` | 5 | employee → system role → visibility scope |
| 9 | `System_Config` | 4 | key/value configuration |
| 10 | `Litigation_Register` | 5 | citizen-ID → litigation status cache |

**131 fields total.** One header list plus five child lists keyed to it, plus three reference
lists and one audit log.

`New_Request` is sectioned in the provisioning workbook: Customer Info (11), Account Details (17),
Closure Decision (8), Transfer Info (7), Balances (4), Tracking & Workflow (14).

## 2. Field-type distribution

| Type | Count | Share |
|---|---|---|
| Single line of text | 51 | 39% |
| Choice | 27 | 21% |
| Yes/No (Boolean) | 21 | 16% |
| Person or Group | 9 | 7% |
| Date and Time | 8 | 6% |
| Multiple lines of text | 8 | 6% |
| Currency | 5 | 4% |
| Number | 1 | <1% |
| File | 1 | <1% |

**Nine types. `Lookup` is not among them — zero Lookup columns across 131 fields.**

`Number` is used exactly once (`RejectCount`). Counts and money are otherwise `Currency`.

## 3. Cross-list references — the delegation rule

**Every cross-list reference is a `Single line of text` column named `RequestID`.** It appears in
all five child lists and in `Approval_Logs` — nine of ten lists have either `RequestID` or a
`Title` that holds the key.

```
New_Request.Title            = "INVX888-1999"      ← the key lives in Title
Request_Accounts.RequestID   = "INVX888-1999"      ← text, not Lookup
Request_Tasks.RequestID      = "INVX888-1999"
Request_Prechecks.RequestID  = "INVX888-1999"
Request_Files.RequestID      = "INVX888-1999"
Request_DocChecklist.RequestID = "INVX888-1999"
Approval_Logs.RequestID      = "INVX888-1999"
```

**Why text and not Lookup.** A Lookup column is not delegable in Power Apps — filtering a gallery
on one pushes the work to the client, so it silently truncates at the delegation limit and the
gallery shows an incomplete list with no error. A text column supports delegable `Filter(...)` and
`StartsWith(...)`. `App_Field_Coverage` records this directly for the dashboard search:
*"(UI only — delegable StartsWith filter on New_Request)"*.

**The exception that the brief's phrasing would blur.** "Text over lookup" applies to
**list-to-list references only**. People are `Person or Group` (9 uses) — not text. Do not
generalise the rule into "avoid all complex column types."

## 4. Naming conventions

| Convention | Evidence |
|---|---|
| Lists: `PascalCase` with `_` between words — `New_Request`, `Request_DocChecklist` | 10/10 |
| Child lists prefixed `Request_` | 5/5 child lists |
| Fields: `PascalCase`, no spaces, no underscores — `CustomerName`, `AccruedInterestPosted` | 131/131 |
| Booleans read as a statement or an action: `IsAlive`, `IsLocked`, `IsExempt`, `IsActiveUser`, `CloseTFEXAccount`, `HasNoAssets` | 21/21 |
| An account-number field pairs with its boolean: `CloseTFEXAccount` + `TFEXAccountNumber` | 6 pairs |
| `<Thing>Other` holds the free-text escape for a Choice: `ClosureReason` + `ClosureReasonOther` | 1 pair, and `CloseScope` + `CloseScopeAccounts` follows the shape |
| Thai display name is carried **beside** the English field name, never inside it | 131/131 — the workbook has a `ชื่อไทย (TH)` row |

That last one is the load-bearing convention for Session 9: the bilingual layer lives in the
provisioning workbook as a parallel row, so a manual generator can render Thai labels without any
Thai appearing in a column name.

## 5. The audit-trail pattern

A `<Verb>By` / `<Verb>At` pair, `Person or Group` + `Date and Time`, appears in **seven of ten
lists**:

| List | Pair |
|---|---|
| `Request_Accounts` | `EditedBy` / `EditedAt` |
| `Request_Tasks` | `DoneBy` / `DoneAt` |
| `Request_Prechecks` | `CheckedBy` / `CheckedAt` |
| `Request_Files` | `UploadedBy` / `UploadedAt` |
| `Request_DocChecklist` | `CheckedBy` / `CheckedAt` |
| `Approval_Logs` | `ActionTakenBy` / `ActionDate` |
| `New_Request` | `CurrentAssignee` (+ `Approval_Logs` for history) |

`confidence: high`. Any generated child list should carry the pair by default.

## 6. Title repurposing

`Title` is not decorative — it holds the natural key, and the workbook annotates the override:

- `New_Request.Title` → the RequestID
- `System_Config.Title (→ ConfigKey)` → the config key
- `Litigation_Register.Title (=CitizenID)` → the citizen ID, described as **indexed**

Deliberate: SharePoint indexes `Title` by default, so putting the lookup key there makes the
delegable filter fast without adding an index. Flow 2 depends on it — *"Title eq CitizenID (indexed)"*.

## 7. The document library

`Request_Files` is a **document library**, not a list: its first column is `Name (file)` of type
`File`. It still carries `RequestID` as text, plus `Department`, `FileKind`, `UploadedBy`,
`UploadedAt`.

**Provisioning differs** — a library is created as a library, and its metadata columns are added
afterwards. `generate_workbook.py` must treat a `File`-typed first column as the signal, or it will
emit a list that cannot hold uploads.

## 8. User-populated vs automation-populated

The `List_Setup` workbook carries this split explicitly — its sheets have a *"Column ที่ต้องใส่ค่าเอง"*
(enter manually) versus *"Column ที่ถูก Automate"* (automated) distinction. This is the field
`lists[].fields[].populated_by: user | automation` reserved in Session 4.

Evidence from the flow designs: `RequestStatus`, `CurrentStage`, `CurrentAssignee`, `IdentityCISVerified`,
`RejectCount` and the whole of `Approval_Logs` are written by flows, never typed. `TotalBalance`,
`AccruedInterestPosted` and `NetBalanceFinal` are entered by the checking departments.

Consequence for Session 6: an automation-written column must not surface as a user-entry field in
the provisioning UX, and Session 9's manual renders the same split as a table.

## 9. Corrections to the brief

- **`New_Request` has 61 fields, not 38.** The brief calls its regression fixture "the 38-field `New_Request` list". Session 6's fixture is 61 fields in 6 sections.
- **There are 10 lists, not 6.** The 360-project manual described 6; this system has 10.
- **`Request_Files` is a library, not a list**, so "ten lists" is nine lists plus one library.

## 10. Two sheets that are really spec, not schema

Flagged for Session 4 — these are `solution-spec.yaml` in spreadsheet form, already built by hand:

- **`12. Variables_Bindings`** (17 rows) — `variables[]` with `Kind` (Global `Set` / Collection `ClearCollect` / Context `UpdateContext`), who sets it, and what it drives. It also documents the naming convention: **`gbl*` globals, `col*` collections, `var*` context variables.**
- **`13. Screen_Data_Matrix`** (18 rows) — per screen: lists read, lists written, flows fired. This is `bindings[]` at screen granularity.
- **`14. App_Field_Coverage`** (409 rows) — control → control type → what it shows → database column → input/display. This is `bindings[]` at **field** granularity, and it is the single most valuable input Session 4 has.
