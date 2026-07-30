# 06 — Vin's notes

<!-- PART 1 awaiting Vin. PART 2 awaiting Vin. -->

**Status:** template. Rank 3 once filled.

**This file changed shape after `ledger/07-buildchat-raw.md` arrived.** It was originally
meant to be unaided recall, written *before* seeing the harvest, so that agreement between
the two would be real corroboration. That ordering is gone — Vin has read the harvest. Left
as-is, this file would restate it and Session 2 would count one source twice.

So it splits in two, and only Part 2 is still independent.

---

# Part 1 — Verdicts on the harvest

Not independent evidence. This is **human verification of machine claims**, which is a
different and in some ways stronger evidence class: it settles entries no artifact can reach.
Session 2 Task C reads this.

Go through `ledger/07-buildchat-raw.md` entry by entry. For each, one verdict:

| Verdict | Meaning |
|---|---|
| `confirms` | Yes, that happened, and roughly that often |
| `confirms-understated` | Happened, but more often / worse than it says |
| `denies` | That is not what happened |
| `never-happened` | Reconstructed out of nothing |
| `adds-detail` | True, and here is the part it left out — especially the *why* |

Priority order — spend effort here first:

1. **The four `corrections` entries marked `recall: reconstructed` with `evidence: none`.**
   Weakest possible combination, and the corrections list is the most valuable one in the
   harvest. These four: container height containing children; control inset/padding;
   light hover-focus styling; mutual-fund unit-holder decision on Middle only. If you
   confirm a `times: 3` entry that the artifacts also confirm, it goes inline in a skill.
2. **`sharepoint_gotchas: []`.** The harvest returned nothing. Ten lists exist and a
   66-row `New_Request` sheet. Did genuinely nothing bite, or did it forget? Part 2 §B is
   where the answer goes.
3. **The abandoned entries.** All five are `times: 1`, and four cite `evidence: none`. The
   *reasoning* is what stops a future skill re-proposing them, and reasoning is exactly what
   compaction eats first.

Entries you can skip: the two delivery-mechanism ones (git bundle, sandbox 403). Real events,
outside all five skills — Session 2 marks them `out-of-scope`.

## Verdicts

<!-- rule (short) | verdict | correction or detail -->

---

# Part 2 — What the harvest did not mention

**Still fully independent.** The harvest never raised any of the below, so your recall here
is uncontaminated and Session 2 can treat agreement with the artifacts as real signal.
This is now the more valuable half of the file.

## A. Power Apps / Studio

Failures the harvest missed entirely. It said nothing about: control-type selection
(bare vs `Classic/`), property ordering, block scalars, RGBA or design tokens, sizing scale,
gallery structure, `LoadingSpinnerColor`, `DropShadow`, or any specific Studio error code
except `PA2108`. If any of those cost you time, here is where it counts for the most.

## B. SharePoint lists

The harvest returned `sharepoint_gotchas: []`. Ten lists in the workbook. Column types,
naming, cross-list references, values a column rejected, the leading-zero problem, choice
columns, anything about `New_Request` specifically.

## C. Manuals

Out of scope for the harvest — it only knew the account-closure build. What made the 360
manuals work or not work for their readers. What you would do differently. Whether the
two-manual split is fixed or negotiable. **And the open question:** heading language order —
the user-friendly manual leads English, the full manual leads Thai. Deliberate, or drift?

## D. Power Automate

The harvest says seven flows were designed and documented, none built. Anything you know or
suspect about flows goes here, marked as expectation rather than experience.

## E. Anything else

Including suspicions. Mark them as suspicions and they will be graded as such, not discarded.
