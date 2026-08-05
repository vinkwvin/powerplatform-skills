# handoff/ — what the team receives

<!-- v2.0.0 -->

The team does not use GitHub, and **there is no maintainer.** Everything has to reach them as one
attachment, and everything they need to change has to be changeable from that attachment alone.
This folder is that boundary.

## The source

`handoff.html` is the document. The prose lives there and nowhere else — no markdown twin, because
two files saying the same thing disagree within a week and the one being read is always the wrong
one. Same rule this suite applies to the manuals it generates.

Thai, because the audience reads Thai. English is kept only where the words are literal: skill
names, file names, UI paths, and anything typed or clicked.

Sixteen pages, numbered sections, a contents page, and a running head naming the section on every
page. It is written to be found in, not read through.

## Rebuilding

```bash
python3 scripts/build_handoff.py --images     # PDF + one PNG per page + overflow check
python3 scripts/build_starter_pack.py         # the single zip to send
```

Pages are fixed-height A4 sections with `overflow: hidden`. That buys exact layout control and
costs reflow: **text that grows past the bottom is clipped silently.** Nothing errors, and a
review image of a clipped page looks complete.

So the builder measures it. After writing the PDF it loads the document in the browser, compares
each page's lowest element against that page's bottom padding, and reports any page losing
content — then exits non-zero. It has already caught two overflows that a page-by-page visual
review missed. Do not silence it; move something to the next page or cut it.

## What goes in the zip

| | |
|---|---|
| `READ-ME-FIRST.txt` | three steps, in Thai, for someone who has just downloaded a zip |
| `Power-Platform-Skill-Suite-Handoff-TH.pdf` | the handoff, 16 pages |
| `skills/*.zip` | the five skills, upload-ready, each carrying its own regression harness |
| `prompts/team-quick-feedback.md` | step 1 — paste at the END of a working chat |
| `prompts/improve-the-skill.md` | step 2 — the improvement round |
| `prompts/project-style-override.md` | for a project with a different design system |
| `CHANGELOG.md` | what changed, and whether a re-download is worth two minutes |

## The loop, with no maintainer and no repository

| Step | Who | When | What |
|---|---|---|---|
| 1 | anyone | end of a real working chat, 2 min | paste `team-quick-feedback.md`, save the record to the shared folder |
| 2 | any one person | after 3–5 records, 30–45 min | paste `improve-the-skill.md` with the zip attached, get a new zip back |
| 3 | the version owner | after step 2 is tested | publish to the shared folder and tell the team whether to re-download |

There is a fourth path that never enters this loop: a project with a different palette or type
scale is a `HOUSE` difference, not a finding, and `project-style-override.md` settles it inside
that one chat. Routing style differences into the improvement round is how a house convention gets
promoted to a fake platform law.

### Why the improvement round can be trusted

Step 2 is a model editing its own instructions with nobody reviewing the diff. Two things make
that safe enough to hand over:

**The evidence travels in the zip.** `package_skills.py` copies the 17 reference screens, the
ChopChop field output, and the probe fixtures into `tests/` at package time, and
`scripts/self_check.py` checks them against recorded baselines in `tests/expected.json`. A rule
that fires on the reference screens fails the check, because those screens compiled in Studio and
shipped. Packaging runs the self-check inside the extracted zip, cut off from this repository — if
the ground truth does not travel, packaging fails.

**The methodology is in the prompt.** Triage order, `rule_status` → action, check-before-rule, the
200-line cap, the evidence bar, and seven rules that cannot be broken. `improve-the-skill.md` is
the intake round from `docs/IMPROVING-SKILLS.md` rewritten as something a chat can execute.

Neither replaces judgement. Both make the common failure — adding a plausible rule nobody
measured — cost something.
