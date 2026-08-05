# 09 — Field report 01: ChopChop

The first use of a packaged skill on a real project that is **not** the one the suite was built
from. This is the evidence the whole D7 loop was designed to collect, and the first test of the
claim that a suite measured from one system generalises to another.

- **Skill:** `generating-powerapps-yaml` v1.0.0
- **Project:** ChopChop — helicopter logistics UI. Unrelated domain, unrelated design language.
- **Artifacts:** two screens, `LiveTracking.pa.yaml` and `FlightDeck.pa.yaml`, at v3.
- **Rank:** 1 for *structure* (measured directly). **Not Rank 1 for paste success** — see the
  open question at the bottom.
- **Fixtures:** `evals/generating-powerapps-yaml/fixtures/`, eval `04-field-output-chopchop.json`.

## How the files were obtained

Copied verbatim out of the session transcript, not re-typed. This matters: a hand-transcription
slip would have shown up as a defect in the output and been recorded here as one.

## Measured

| | LiveTracking | FlightDeck | Total |
|---|---|---|---|
| controls | — | — | **191** |
| control types | — | — | 5, all in the confirmed nine |
| max nesting depth | — | — | 9 |
| `X` / `Y` | 1 / 1 | 1 / 1 | 4, all at depth 1 |
| `LayoutOverflowY` | 2 | 2 | matches `scroll_containers_per_screen: 2` |
| screen properties | 3 | 3 | `Fill`, `LoadingSpinnerColor`, `OnVisible` |

Diffed against the 17 reference screens:

| | count |
|---|---|
| property names never seen in the reference set | **0** of 41 |
| `Icon.*` members never seen | **0** |
| control types never seen | **0** |
| other enum members never seen | **1** — `LayoutJustifyContent.SpaceBetween`, 11 uses |

## Validator result

Clean: `0 error(s) [PLATFORM], 0 warning(s) [HOUSE]` at v1.0.0.

A clean pass proves nothing on its own, so five mutations were injected into the ChopChop files
themselves and every one was caught: `Classic/` on a bare control; an unknown control type; a
wrong version string (`Gallery@2.14.0`); an `X` at depth 5; and a colon-space value with its
block scalar removed. The last one fails at YAML parse, which is the failure mode that costs a
Studio round trip.

## What worked, and which tier proved it

**The HOUSE/EXAMPLE split held under the only test that matters.** ChopChop uses an entirely
foreign palette and produced **zero** colour warnings, because `palette.enforce: false` and colour
is EXAMPLE tier. Had the palette been baked into the validator as the counts alone would have
justified, this project would have opened with dozens of warnings that were all wrong, and the
next thing the user learns is to ignore warnings. That is the failure mode `docs/EVIDENCE-TIERS.md`
was written to prevent, and it did not happen.

Meanwhile the rules that *are* platform facts transferred with nothing lost: bare-vs-`Classic/`,
alphabetisation, block scalars, `Height` + `LayoutMinHeight`, AutoLayout over coordinates.

**Two protocols fired unprompted**, with no user in the loop asking for them:

- A helicopter glyph does not exist in the confirmed six-icon set. The output used
  `Icon: =Icon.Publish  # UNVERIFIED approximation` and said so, rather than inventing
  `Icon.Helicopter`.
- An unconfirmed `Timer` control was delivered **commented out, as an isolated snippet at the end
  of the file**, instead of inlined into the screen where it would have taken the whole paste
  down with it.

## The one gap — and it is a real one

`LayoutJustifyContent.SpaceBetween` appears in zero of the 17 reference screens and **nothing
flagged it**.

`SpaceBetween` is in fact valid. That is not the point. The point is that the skill had no way to
tell the difference between a member that exists and one that does not, and `DropShadow.Light` —
already a hard `ERROR` in this validator — is proof that plausible-but-nonexistent members get
generated in practice.

Diagnosis, in the vocabulary of `docs/IMPROVING-SKILLS.md`:

| | |
|---|---|
| `caught_by` | this review — **not** the validator, and not the user |
| `tier` | HOUSE |
| `rule_status` | **`absent`** |

`absent`, not `present-and-ignored`: `Icon` had a confirmed-member list and no other enum did, and
workflow step 4 said "choose control **types** from the catalog only" — which a careful reader
correctly understands as saying nothing about enum members.

### Fixed in v1.1.0

- `assets/house-style.yaml` gains `enum_members:` — 14 enums, measured members, counts recorded.
- `validate_pa_yaml.py` checks every `Enum.Member` against it. WARN, not ERROR: an unlisted
  member is *unconfirmed*, not *invalid*, and the message says so and asks for a one-control
  paste test.
- `references/control-catalog.md` §5 documents all 14 with counts.
- `SKILL.md` step 4 extends the catalog rule to enum members explicitly.

Regression: the 17 reference screens stay at 0 errors / 0 warnings; ChopChop now reports the 11
`SpaceBetween` warnings and nothing else.

**Do not silence those 11 by adding `SpaceBetween` to the list.** It goes in when someone confirms
Studio accepted it, and then eval `04` moves to a 0-warning expectation. Adding it now would
convert a real open question into a fabricated confirmation.

## Open question — the honest limit of this report

**Whether these files paste cleanly into Studio at v3 is unconfirmed.** Everything above is
structural: measured from the files, verified by mutation. Nobody has reported the paste result.

The file headers say v3 was a "border + brand CI pass" fixing cases where "Studio drew its default
blue", which means at least two Studio round trips already happened — so `rounds > 1`, and there
is correction history in that chat which this report does not have. The next action is
`prompts/feedback-session.md` pasted at the end of that conversation; it will produce the
`first_attempt_validated` and `rounds` fields that are missing here, and may well surface
corrections that never reached me.
