# Screenshot frames

Claude cannot capture a running app. This is how to ask for the picture so it comes back right.

## The frame

Every frame carries three fields, and all three earn their place:

```
[ Figure 4 — paste screenshot here ]
Screen:    Sales - Initial Contact
State:     after entering a 13-digit citizen ID, litigation check returned Clean
Highlight: the green litigation result box
```

- **Screen** — which screen. Obvious, and still the field most often left implicit.
- **State** — what has to be true before the shot is taken. A blank form and a filled one are
  different pictures, and the useful one is almost never blank.
- **Highlight** — what the reader should look at. Without it you get a full-window screenshot with
  the relevant control 4 pixels wide.

A frame saying "screenshot here" gets filled wrong, or not at all.

## Rules

**Number them, sequentially, across the whole document.** "Figure 7" is something a person can
work through a list of. "the screenshot on page 12" is not.

**One frame per screen in the user manual**, immediately after the heading and before the steps.
That is the shape of the shipped reference and it is the shape readers expect.

**State what is in the picture, in the caption or the steps.** A screenshot that has to be read
carefully to be understood is doing the text's job badly.

**Ask for real data, not real customer data.** Realistic sample values, plausible names, correctly
formatted IDs — but nothing from production. A manual circulates further than anyone plans.

**Say how many frames there are** when handing over. "11 frames to fill" is a task someone can
schedule; "add screenshots where needed" is not.

## What to capture, per screen type

| Screen | State worth capturing |
|---|---|
| a form | partly filled, with one validation message visible |
| a list or dashboard | populated, several rows, one row highlighted |
| an approval | the decision buttons visible, with a real request loaded |
| a confirmation | the success state, since it is what the user is meant to look for |
| an error path | worth one frame in the admin manual if the recovery is non-obvious |

An empty state is worth capturing only when it is meaningfully different — a first-run screen, or
one where "nothing here" is a legitimate and confusing result.
