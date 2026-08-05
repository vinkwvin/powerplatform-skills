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

## Round 2 — the comment headers ARE the feedback record

The files came back from `prompts/feedback-session.md` with no structured YAML record. The reason
is a defect in that prompt, not in the chat: it asked for **the artifact first and the record
second**, and two 1,400-line files consumed the whole response. Fixed in `feedback-session.md`
v1.2.0 — the record now comes first, with an instruction to stop rather than truncate it.

But the 78 lines of comment header on the two files are a correction log in prose. Mined, they
give seven findings, all of them the kind that costs a Studio round trip:

| # | Finding | `rule_status` |
|---|---|---|
| 1 | `BorderThickness > 0` with no `BorderColor` → Studio paints its default blue | absent |
| 2 | No per-side border; `BorderThickness` draws all four sides | absent |
| 3 | A border draws on the control's own bounds → clipped when child `Height` == parent `Height` | absent |
| 4 | `Parent.Template*` resolves only on a gallery's direct child | counted in `layout-sizing.md`, never stated as a constraint |
| 5 | Bare `=Parent.Width` overflows a padded parent by the padding | present, but framed as a style distribution rather than a failure |
| 6 | `AlignInContainer` or a fixed-size child stretches and ignores its `Width` | **`present-and-ignored`** — `patterns.md:76`, phrased as "wants" |
| 7 | Container `Height` >= sum(children) + gaps + padding | absent |

№6 is the category `docs/IMPROVING-SKILLS.md` calls the most valuable and the least likely to be
volunteered: the rule was correct, present, and buried in §2 of a reference file as a preference.
It is now a hard rule in `SKILL.md` and a checklist line. That fix makes the skill better without
making it longer, which is the only kind of fix that scales.

### The border rule, and where measurement corrected inference

№1 was checkable against the reference set, so it was measured rather than assumed. Across all
2,830 reference controls, **every control with `BorderThickness > 0` sets `BorderColor`, and every
control without `BorderColor` has thickness `=0` or absent. Zero exceptions.** That is now a
PLATFORM `ERROR`.

Independent confirmation: deleting the 10 `BorderColor` lines from ChopChop v3 reproduces v2's bug
and the validator names `Tab_FlightDeck` and `Tab_LiveTracking` — the exact two controls the v3
header blames. The rule derived from the reference set and the bug found in the field are the same
rule.

**An over-reach was caught and withdrawn.** The header says the offending buttons had *neither*
property, so a HOUSE warning was added for `Classic/Button` with no `BorderThickness` — 248 of 268
reference buttons set it explicitly. It fired on **20 of the reference screens' own buttons**,
which shipped and worked. So absence alone is not the cause, and a warning on known-good ground
truth is the precise thing that teaches people to ignore warnings. The check was removed and the
guidance demoted to prose in `SKILL.md`. Artifacts outrank inference; the hierarchy did its job.

The follow-up prompt asks the one question that would settle it: in the broken version, was
`BorderThickness` absent or `=0`?

## Open questions

Sent to the chat as `prompts/followup-record-only.md`:

1. **Was `validate_pa_yaml.py` ever run?** If a real session skipped the D2 gate, that is a bigger
   finding than all seven rules above, and the fix is the gate's wording rather than any rule.
2. **Did v3 actually paste clean?** Until answered, v3 is the latest draft, not ground truth.
3. **Did Studio accept `LayoutJustifyContent.SpaceBetween`?** Deliberately still unconfirmed.
4. **`BorderThickness` absent or `=0`** in the version that broke.
5. **Studio round-trip count and the verbatim PA error codes.**
6. **Anything corrected 3+ times** — a repeat after correction means the rule is not where the
   reader looks, whatever it says.
