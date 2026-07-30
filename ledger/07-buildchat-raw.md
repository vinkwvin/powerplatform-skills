# 07 — Build-chat harvest, raw

**Source:** the Claude Code conversation that built the INVX Account Closure prototype,
answering `prompts/harvest-buildchat.md`. Supplied by Vin.

**Rank 4 on arrival.** `confidence: low` throughout until Session 2 checks each entry
against `/source-artifacts/`. Nothing here goes inline in a skill on its own authority.

**Verbatim. Do not edit.** Session 2 writes its verdicts to `ledger/08-buildchat-verified.md`
and leaves this file alone. Entries Vin disagrees with stay here — a claim that turned out
to be wrong is itself worth recording.

---

```yaml
standing_instructions:
  - rule: "Emit every screen as first-try-pasteable Power Apps Source Code YAML, nothing that needs hand-fixing in Studio."
    times: 6
    source: explicit
    evidence: none
    recall: reconstructed
  - rule: "After each change round, regenerate all screens, run the validator, and hand back a downloadable zip."
    times: 6
    source: explicit
    evidence: pa-final.cjs
    recall: reconstructed
  - rule: "Keep the whole UI bilingual Thai + English."
    times: 5
    source: explicit
    evidence: none
    recall: reconstructed
  - rule: "Keep the prototype, the pa.yaml app, the database schema, and the handbook all describing one consistent design."
    times: 3
    source: explicit
    evidence: Account-Closure_Developer_Handbook.pdf
    recall: direct
  - rule: "Deliver as files the user pushes themselves; do not rely on this sandbox reaching GitHub."
    times: 3
    source: inferred
    evidence: push_round17.sh
    recall: direct
  - rule: "Push only to the user's own repo vinkwvin/INVX-Account-Closure, not the original ykunakorn repo."
    times: 2
    source: explicit
    evidence: push_round17.sh
    recall: direct

corrections:
  - rule: "Compute each container's height to fully contain its children so content never leaks past the box edge."
    times: 3
    source: corrected
    evidence: none
    recall: reconstructed
  - rule: "Inset every control from its container with real padding so adjacent borders never overlap."
    times: 2
    source: corrected
    evidence: none
    recall: reconstructed
  - rule: "Use minimal, light hover/focus styling, not thick borders or heavy dark fills."
    times: 2
    source: corrected
    evidence: none
    recall: reconstructed
  - rule: "Only use control properties Studio actually accepts; when a paste throws PA2108, remove the offending property, don't argue."
    times: 2
    source: corrected
    evidence: validate_pa_yaml.py
    recall: reconstructed
  - rule: "Put the mutual-fund unit-holder decision only on Middle screens; keep it off Sales."
    times: 2
    source: corrected
    evidence: none
    recall: reconstructed
  - rule: "Show the assets/money matrix only on Sales and Middle, never on Head of Sales or C&AM."
    times: 2
    source: corrected
    evidence: none
    recall: direct

recurring_mistakes:
  - rule: "Verify the delivery mechanism itself before handing it over — the push path broke three times running (bundle cloned to an empty tree, hardcoded a filename the browser had renamed, ran `git bundle verify` outside a repo)."
    times: 3
    source: corrected
    evidence: push_round17.sh
    recall: direct
  - rule: "Never set FillPortions on a non-Label/GroupContainer control; the validator rejects it and I had to wrap the control instead."
    times: 2
    source: inferred
    evidence: validate_pa_yaml.py
    recall: direct
  - rule: "When delegating to a subagent, expect scope creep and re-check its output — it re-added the matrix to Head of Sales that had been explicitly removed."
    times: 1
    source: inferred
    evidence: none
    recall: direct
  - rule: "Escape quotes in generated Power Fx correctly; I shipped a JS syntax error from nesting single quotes inside a single-quoted string and caught it only at generation."
    times: 1
    source: inferred
    evidence: none
    recall: direct
  - rule: "When told to build, build — don't stall with a batch of clarifying questions the user then rejects."
    times: 1
    source: corrected
    evidence: none
    recall: direct

abandoned:
  - rule: "Don't ship a git bundle as the delivery vehicle; cloning a branch-only bundle leaves an empty checkout — switched to a zip + fresh-repo script."
    times: 1
    source: inferred
    evidence: push_round17.sh
    recall: direct
  - rule: "Don't attempt the push from inside the sandbox; org egress policy returns a 403 that must not be retried — hand the user files instead."
    times: 1
    source: inferred
    evidence: none
    recall: direct
  - rule: "Don't drive a conditional reveal by binding Visible directly to DropDown.Selected.Value; it didn't re-evaluate on paste, so it moved to OnChange writing a context variable."
    times: 1
    source: inferred
    evidence: none
    recall: reconstructed
  - rule: "Don't string-splice the external Dashboard YAML; regenerate the Dashboard through the generator so its sidebar links aren't stale."
    times: 1
    source: inferred
    evidence: 01_Dashboard.pa.yaml
    recall: direct
  - rule: "Don't bake live SharePoint datasource bindings into the pasted YAML; they error on paste, so ship paste-safe collections plus a separate wiring map."
    times: 1
    source: inferred
    evidence: none
    recall: direct

flow_attempts:
  - rule: "Seven Power Automate flows were only designed and documented (schema, the Excel Power_Automate sheet, handbook §9); none was built, exported, or imported, and no flow .zip exists anywhere."
    times: 1
    source: inferred
    evidence: Account-Closure_SharePoint_Database.xlsx
    recall: direct

sharepoint_gotchas: []
```
