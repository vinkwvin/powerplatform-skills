# Follow-up prompt — the record only, when the artifact already came back

<!-- v1.0.0 -->

**When to use this.** You pasted `feedback-session.md`, got the corrected artifact back, and the
structured record never arrived — the files were long enough to eat the whole response. This asks
for the missing half and explicitly forbids re-sending the artifact.

**Where it goes:** the same chat, right after that reply.

**Where the answer goes:** `feedback/<skill>/<YYYY-MM-DD>-<short-topic>.md`.

---

## The prompt — copy from here down

The files came through. Do **not** output them again, or any part of them — I have them saved. I
need the written record instead, and re-sending code is what crowded it out last time.

Answer from what actually happened in this conversation. Where you cannot remember, write
`unknown` — a blank is more useful to me than a plausible reconstruction, and I would rather have
six honest answers than twelve confident ones. Be blunt: this is for fixing the skill, not for
reassuring me.

One YAML code block, nothing outside it.

```yaml
process:
  # Did you run the skill's validator script — scripts/validate_pa_yaml.py — in the sandbox
  # before giving me any file? Answer plainly. "No" is a completely acceptable answer and is
  # more useful to me than a yes I cannot check.
  validator_run: <yes | no | unknown>
  validator_run_when: <before every version | only when I complained | never | unknown>
  # If you did not run it, why not. Not available? Did not think to? Skill did not say to
  # clearly enough? The wording of the gate is something I can change.
  validator_skipped_because: <free text, or n/a>

  studio_rounds: <how many times I pasted into Studio before it was right>
  first_paste_outcome: <compiled clean | compiled with visual defects | rejected outright | unknown>
  # Verbatim if you have them — PA1001, PA2108, "invalid control", etc.
  studio_errors_reported: [<...>]

# For each item, say where the rule was. This distinction is the whole point of the exercise:
#   absent               — the skill never mentioned it. I add a rule.
#   present_but_wrong    — the skill said something, and it was wrong. I correct it.
#   present_and_ignored  — the skill said the right thing and you did not apply it. I move it,
#                          shorten it, or put it in the checklist.
# The third is the one that is uncomfortable to admit and the most valuable to me — it is the
# only category that improves the skill without making it longer, and a skill nobody finishes
# reading has no rules at all. If it applies, say so.
findings:
  - id: border_color_default_blue
    what: buttons with a border but no BorderColor got Studio's default blue
    rule_status: <absent | present_but_wrong | present_and_ignored | unknown>
    # The specific thing I need: in the version that went wrong, did those buttons have
    # BorderThickness set to =0, or was BorderThickness absent entirely?
    borderthickness_was: <"=0" | absent | mixed | unknown>
    rounds_to_fix: <n>

  - id: no_per_side_border
    what: BorderThickness draws all four sides; a single divider rule needed its own container
    rule_status: <absent | present_but_wrong | present_and_ignored | unknown>
    rounds_to_fix: <n>

  - id: border_clipped_by_equal_height_parent
    what: a 1px border on a child as tall as its parent was clipped by the parent edge
    rule_status: <absent | present_but_wrong | present_and_ignored | unknown>
    rounds_to_fix: <n>

  - id: parent_template_direct_child_only
    what: Parent.TemplateWidth/Height resolved only on the gallery's direct child
    rule_status: <absent | present_but_wrong | present_and_ignored | unknown>
    rounds_to_fix: <n>

  - id: parent_width_overflows_padded_parent
    what: bare =Parent.Width inside a padded parent overflowed it by the padding
    rule_status: <absent | present_but_wrong | present_and_ignored | unknown>
    rounds_to_fix: <n>

  - id: aligncontainer_required
    what: without AlignInContainer a fixed-size child stretched and ignored its Width
    rule_status: <absent | present_but_wrong | present_and_ignored | unknown>
    rounds_to_fix: <n>

  - id: container_height_vs_children
    what: containers shorter than their contents clipped or collapsed
    rule_status: <absent | present_but_wrong | present_and_ignored | unknown>
    rounds_to_fix: <n>

# Anything you corrected three or more times. These are worth more than everything above:
# a mistake repeated after correction means the rule is not where you look, whatever it says.
repeated_corrections:
  - what: <...>
    times: <n>
    why_it_kept_happening: <your honest read>

# Did Studio accept LayoutJustifyContent.SpaceBetween? I have no confirmation it works, and I
# am deliberately not adding it to the confirmed list until someone says it pasted.
unverified_now_confirmed:
  - member: LayoutJustifyContent.SpaceBetween
    studio_accepted: <yes | no | never tested | unknown>
  - member: <anything else you marked UNVERIFIED and later tested>
    studio_accepted: <yes | no | never tested | unknown>

# The one question that decides whether v3 is ground truth or just the latest draft.
final_state:
  v3_pasted_into_studio: <yes | no | unknown>
  v3_result: <clean | still has defects — list them | not yet pasted | unknown>

# Free text. What would have saved the most round trips if the skill had said it on page one?
# One thing, not five.
biggest_single_miss: <...>
```
