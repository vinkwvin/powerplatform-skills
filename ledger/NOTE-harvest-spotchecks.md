# NOTE — spot checks run against the harvest on arrival

Three checks run immediately when `ledger/07-buildchat-raw.md` landed, because they were
cheap and one of them looked like a live defect. **Session 2 folds these into
`ledger/08-buildchat-verified.md`; they are not a substitute for its full pass.**

## 1. CONFIRMED, with a correction — the matrix regression persisted on Head of Sales

Harvest, twice: *"Show the assets/money matrix only on Sales and Middle, never on Head of
Sales or C&AM"* (`times: 2`, `recall: direct`) and *"a subagent re-added the matrix to Head
of Sales that had been explicitly removed"* (`times: 1`).

`grep -il matrix` across the 17 screens:

```
02_Sales_InitialContact.pa.yaml     ← expected
03_Sales_Documents.pa.yaml          ← expected
06_Middle_PrecheckWallet.pa.yaml    ← expected
07_Middle_VerifyDocs.pa.yaml        ← expected
08_HeadOfSales_Approval.pa.yaml     ← should not be here
```

C&AM (`09`, `10`) is clean. Head of Sales is not. `08_HeadOfSales_Approval.pa.yaml:18`:

```
ClearCollect(colMatrix, {Acct: "Cash Account", Pick: ""}, … {Acct: "Offshore ACC", Pick: ""});
```

**But `colMatrix` is referenced exactly once in that file — this line.** No gallery binds
`Items: =colMatrix`. So the removal was *partial*: the visible control went, the
initialization stayed. Orphaned dead code, not a user-visible defect.

Verdict: the harvest entry is `confirmed` — the re-add happened and cleanup was incomplete.
The artifact refines it. Worth fixing in the prototype independently of this project.

## 2. NOT SETTLED by grep — the unit-holder scope rule

Harvest: *"Put the mutual-fund unit-holder decision only on Middle screens; keep it off
Sales"* (`times: 2`, `corrected`, `evidence: none`, `recall: reconstructed`).

`grep -il "unitholder|unit holder|mutual"` matches **all nine** request screens (`02`–`10`),
Sales included. That looks like a contradiction but is not evidence of one: the rule concerns
the unit-holder *decision control*, while "Mutual Fund ACC" also appears as a plain row label
in every account matrix and collection. Grep cannot separate the two.

Left `unverifiable-by-grep`. Session 2 must inspect the control context, not the string.
**Do not record this as contradicted on the strength of the grep** — that is exactly the
false-promotion failure the verdict taxonomy exists to prevent.

## 3. A second workbook exists and is not in the repo

Harvest cites `evidence: Account-Closure_SharePoint_Database.xlsx` and references
*"the Excel Power_Automate sheet"*. The workbook in `/source-artifacts/sharepoint/` is
`AccountClosure_SharePoint_List_Setup.xlsx` — a different file. Its sheets:

```
① Setup guide (25r)   1. New_Request (66r×11c)      2. Request_Accounts (19r)
3. Request_Tasks      4. Request_Prechecks          5. Request_Files
6. Request_DocChecklist  7. Approval_Logs           8. Role_Mapping
9. System_Config      10. Litigation_Register
```

**No `Power_Automate` sheet.** So the seven designed flows are documented in a workbook the
repo does not have. Uploading it would give Session 3 Task B *designed* flow specs to work
from — still not a real export, so it does not lift the `confidence: low` grading in
`ledger/NOTE-flow-groundtruth-gap.md`, but it beats reading a synthetic template.

Also noted: **ten lists, not six**, and `New_Request` is 66 rows — the brief calls its
regression fixture "the 38-field `New_Request` list". Rows are not fields (headers and
section breaks inflate the count), but Session 3 Task C should establish the real field count
rather than carrying 38 forward unchecked.
