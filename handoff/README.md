# handoff/ — what the team receives

<!-- v1.0.0 -->

The team does not use GitHub. Everything in this repository has to reach them as one attachment
on Teams, and everything they send back has to arrive the same way. This folder is that boundary.

## The source

**`handoff.html` is the document.** The prose lives there and nowhere else. There is deliberately
no markdown twin — two files saying the same thing disagree inside a week, and the one someone is
reading is always the wrong one. That is the rule this suite already applies to the manuals it
generates, and it applies here too.

It is written in Thai, because the audience reads Thai. English is kept only where the words are
literal: skill names, file names, UI paths, and anything that gets typed or clicked.

## Rebuilding

```bash
python3 scripts/build_handoff.py --images     # PDF + one PNG per page
python3 scripts/build_starter_pack.py         # the single zip to send
```

**Use `--images` every time you edit the copy, and look at all eleven.** Pages are fixed-height
A4 sections with `overflow: hidden`, which buys exact layout control and costs reflow: text that
grows past the bottom is clipped silently. Nothing errors. The page just quietly loses its last
paragraph.

That failure has already happened once here, in the review tool rather than the document — the
screenshot viewport returned ~90px less than it was asked for, so every review image cropped its
own footer while looking complete. `PAGE_PX` in `build_handoff.py` now overshoots deliberately.
The lesson is the one on page 8 of the handoff itself: a clean run is not a correct render, and
the only way to know is to look.

## What goes in the zip

| | |
|---|---|
| `READ-ME-FIRST.txt` | three steps, in Thai, for someone who just downloaded a zip |
| `Power-Platform-Skill-Suite-Handoff-TH.pdf` | the handoff, 11 pages |
| `skills/*.zip` | the five skills, upload-ready |
| `prompts/team-quick-feedback.md` | paste at the END of a working chat — this is the whole ask |
| `prompts/project-style-override.md` | for a project with a different design system |
| `CHANGELOG.md` | what changed, and whether a re-download is worth two minutes |

## The loop, without a repository

Three lanes, described in full on page 9 of the PDF:

1. **Anyone, two minutes, every project** — paste `team-quick-feedback.md` at the end of the chat,
   send the record back on Teams. Files land in `feedback/<skill>/` here.
2. **Anyone, immediately** — a different palette or type scale is a `HOUSE` matter, so it is
   settled per project with `project-style-override.md`. Nothing to install, nothing to wait for.
3. **Maintainer, roughly monthly** — `scripts/triage_feedback.py`, fix, bump, re-zip, and say
   plainly which findings were *not* acted on and why.

Lane 1 versus lane 2 is the `PLATFORM`/`HOUSE` split with the theory removed: *did the platform
refuse it, or did it work and simply not match us?* The first is everyone's problem. The second is
this project's preference.

Lane 3 is the one that decides whether lanes 1 and 2 keep happening. A teammate who files twice
and sees nothing change stops filing, and that input is gone for good.
