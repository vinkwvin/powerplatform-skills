# Troubleshooting entries

Where they come from, and why inventing them is worse than leaving the section out.

## The rule

**Every entry is a failure someone actually hit.** No exceptions.

All eight entries in the shipped reference manual were real: leading zeros dropped on a SharePoint
paste, a Choice column rejecting a value, Power Query returning `#N/A`, a report not refreshing.
Specific, ugly, and each one cost somebody an afternoon.

## Why not invent plausible ones

Three reasons, and the third is the one that matters:

1. **It sends readers hunting problems they do not have.** A reader with a real problem searches
   this section, finds a fictional entry that half-matches, and follows a fix for a different
   fault.
2. **It cannot be kept accurate.** A real entry is corrected when the fix changes. A fictional one
   has nobody who knows it is stale.
3. **It devalues the real entries.** A section that is visibly padded gets skimmed, and the eight
   entries that would have saved an afternoon get skimmed with it. One invented entry costs more
   than the eight real ones earn.

The same logic as the control catalog: an invented-but-plausible item is worse than an admitted
gap, because it is indistinguishable from a verified one until it fails.

## Where entries come from

**In final mode, ask.** "What went wrong while you were building this, and what fixed it?" Ask the
people who built it, not the spec.

**From the feedback ledger.** `feedback/` accumulates field reports with `wrong`, `right` and
`caught_by`. A `caught_by: studio` entry is by definition a real failure that reached a user, and
it converts into a troubleshooting entry directly.

**From the build chat.** If the system was built with Claude, `prompts/feedback-session.md` at the
end of that chat captures exactly this.

## Shape of an entry

```yaml
- symptom: "Leading zeros disappear from account numbers after pasting into SharePoint"
  cause: "The column is a Number type, or Excel reformatted the value before the paste"
  fix: "Set the column to Single line of text, and paste from a text editor rather than Excel"
```

- **Symptom in the reader's words.** They search for what they see, not for the cause. "The status
  doesn't update" beats "the flow's condition evaluates false".
- **One cause.** If there are three, that is three entries.
- **A fix someone can perform.** Not "check the configuration".

## When the section is empty

Say so, plainly, and say why:

> No problems have been recorded yet. Entries are added here as real failures occur — this section
> is deliberately empty rather than filled with problems nobody has actually had.

That sentence is doing real work. It tells the reader the absence is a decision, not an oversight,
and it invites them to report the first one.
