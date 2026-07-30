# 06 — Vin's notes

<!-- Awaiting Vin. Verdicts only — see scope note. -->

**Status:** template. Rank 3 once filled.

## What this file is now, and what it stopped being

Originally: Vin's unaided recall, written before seeing the build-chat harvest, so agreement
between the two would be real corroboration.

Two things changed that, both deliberately:

1. **Vin read `ledger/07-buildchat-raw.md` first.** Independence for anything the harvest
   covered is gone — restating it would make Session 2 count one source twice.
2. **Vin reassigned the recall half to empirical harvesting.** Rather than trying to remember
   how each element was set up, Session 1 reads the 17 `.pa.yaml` files and measures it.
   That is a better instrument for this question: the artifacts are Rank 1 and memory is
   Rank 3.

So this file is now **verdicts only**. The cost is accepted and worth naming: there is no
longer an independent human source to cross-check `ledger/01` against. Everything about
how elements are built now rests on the artifacts alone. Session 1's confidence grades carry
more weight than originally planned, because nothing else votes.

---

# Verdicts on the harvest

Human verification of machine claims. Session 2 Task C reads this.

Go through `ledger/07-buildchat-raw.md` entry by entry. One verdict each:

| Verdict | Meaning |
|---|---|
| `confirms` | Yes, that happened, roughly that often |
| `confirms-understated` | Happened, but more often or worse than stated |
| `denies` | Not what happened |
| `never-happened` | Reconstructed out of nothing |
| `adds-detail` | True, and here is what it left out — especially the *why* |

## Priority — the three that matter

These are `recall: reconstructed` with `evidence: none`: the weakest combination in the
harvest, sitting in its most valuable list. All three are general layout rules that apply to
every future project, which is why they are worth your time.

1. **Container height must fully contain its children** so content never leaks past the box
   edge. `times: 3` — high enough that if you confirm it and the artifacts confirm it, it
   goes inline in `generating-powerapps-yaml`.
2. **Every control inset from its container with real padding** so adjacent borders never
   overlap. `times: 2`.
3. **Minimal, light hover/focus styling** — not thick borders or heavy dark fills. `times: 2`.

## Out of scope — do not spend time on these

Excluded because the skills are general-purpose and these are facts about one project. They
stay in `ledger/07` as a record; Session 2 marks them `out-of-scope` and no skill inherits them.

- The mutual-fund unit-holder decision belonging only on Middle screens
- The assets/money matrix appearing only on Sales and Middle
- Both delivery-mechanism entries (the git bundle, the sandbox 403 on push)
- Pushing only to `vinkwvin/INVX-Account-Closure`

This also settles the open question in `ledger/NOTE-harvest-spotchecks.md`: the unit-holder
scope rule no longer needs verifying, because it is not a candidate rule. The matrix leftover
at `08_HeadOfSales_Approval.pa.yaml:18` is still worth fixing in the prototype, but as a
project task, not a skill input.

## Worth a verdict if you have the patience

- The five `abandoned` entries. All `times: 1`, four with `evidence: none`. The *reasoning*
  is what stops a future skill re-proposing them, and reasoning is the first thing compaction
  eats. Two look generally useful rather than project-specific:
  - `Visible` bound directly to `DropDown.Selected.Value` did not re-evaluate on paste;
    moved to `OnChange` writing a context variable
  - live SharePoint datasource bindings error on paste; ship paste-safe collections plus a
    separate wiring map
- `FillPortions` on a non-`Label`/`GroupContainer` control being rejected — `times: 2`,
  cites `validate_pa_yaml.py`. Session 1 can check this mechanically against the 17 screens.

## Verdicts

<!-- rule (short) | verdict | correction or detail -->
