# 02 — Reconciliation: `yaml-conventions.md` vs the 17 shipped screens

Produced by Session 1. Compares `/source-artifacts/docs/yaml-conventions.md` (278 lines,
Rank 2) against `ledger/01-observed-conventions.md` (Rank 1, measured).

**On the second candidate doc.** `AccountClosure_Developer_Handbook.pdf` is also in
`/source-artifacts/docs/`. It was not reconciled here — it is a developer handbook for the
account-closure system, addressed to the builder, and the brief's ruling assigns that reader
to the planner skill rather than the YAML skill. If it turns out to contain its own YAML
conventions section, that is a separate reconciliation and a possible doc-vs-doc conflict.
**Flagged, not resolved.**

Per `source-artifacts/docs/PROVENANCE.md`, the copy at
`existing-skills/powerapps-yaml/references/yaml-conventions.md` is byte-identical and was
counted as one source, not two.

---

# 1. Confirmed — documented and obeyed

| Doc claim | Measured | Confidence |
|---|---|---|
| §1 Full `Screens:` schema, not a bare control list | 17/17 | `high` |
| §1 Screen names may contain spaces | e.g. `Sales - Create New Request` | `high` |
| §1 Every screen carries `LoadingSpinnerColor` | 17/17 | `high` |
| §1 **Properties sorted alphabetically inside every block** | **2,847/2,847, zero violations** | `high` |
| §1 Spaces only, no tabs | 0 tabs in 37,507 lines | `high` |
| §2 `Label` and `Gallery` bare; interactive controls `Classic/` | 2,830/2,830 controls | `high` |
| §2 Exact version strings for all listed types | all 9 types match the table exactly | `high` |
| §2 `Gallery@2.15.0` with `Variant: Vertical` | 36/36 | `high` |
| §2 `GroupContainer@1.5.0` + `Variant: AutoLayout` | 887/887 | `high` |
| §3 **`DropShadow.Light` never written** | 0 occurrences | `high` |
| §3 `DropShadow.None` on structural containers; omitted on elevated surfaces | 806/887 carry it, 81 omit | `high` |
| §4 DropDown and Radio need both `Items` and `Items.Value` | Radio 16/16, DropDown 1/1 | `low` (n=16 / n=1) |
| §4 Radio also carries `Layout`, `RadioSize`, `Default` | 16/16 each | `low` |
| §4 TextInput multi-line via `Mode: =TextMode.MultiLine` | 13 uses | `medium` |
| §4 GroupContainer supports `BorderStyle: =BorderStyle.Dashed` | 7 uses, only value observed | `low` |
| §5 `LayoutOverflowY: =LayoutOverflow.Scroll` on **two** levels per long page | exactly 2 per screen, 34 total, both at depth 2 | `high` |
| §5 Every card and gallery carries explicit `Height` **plus** `LayoutMinHeight` | 887/887 containers, 36/36 galleries — stronger than the doc claims | `high` |
| §6 Sidebar `Width: 208` | 17 uses, once per screen | `high` |
| §6 Body text `Size: 11`; section headers `Size: 12`; column headers `Size: 9` | 643 / 82 / 487 | `high` |
| §7 **Block scalar required where the value contains `: ` or `#`** | 119 block scalars, 0 unnecessary, reasons exactly as documented | `high` |
| §7 Multi-line formulas also use `\|` | 48 of 119 are multiline | `high` |
| §10 Gallery `TemplatePadding: =0` | 27 of 36 | `medium` |

---

# 2. Undocumented — consistent in the artifacts, absent from the doc

The recovered rules. Each holds across the artifacts and appears nowhere in the 278 lines.

| # | Rule | Evidence | Confidence |
|---|---|---|---|
| U1 | **Screen `OnVisible` is mandatory** and initializes all global state with `If(IsBlank(…), Set(…))` / `If(IsEmpty(…), ClearCollect(…))` guards. The doc's own §9 skeleton omits `OnVisible` entirely. | 17/17 screens | `high` |
| U2 | **Screen `Fill` is mandatory.** The doc shows it in the skeleton but never states it as a rule. | 17/17 screens | `high` |
| U3 | **A screen has exactly three properties** — `Fill`, `LoadingSpinnerColor`, `OnVisible`. Never a fourth. | 17/17 | `high` |
| U4 | **`Classic/CheckBox@2.1.0` is a confirmed control type.** It is missing from the doc's §2 control table altogether. | 110 uses, 12/17 files | `medium` |
| U5 | **`X`/`Y` appear only on the depth-1 root container.** No `Label`, `Button`, `Gallery`, `Icon`, `TextInput`, `Radio` or `CheckBox` declares either. | X 17, Y 17, all on root `GroupContainer`; 0 elsewhere across 2,830 controls | `high` |
| U6 | **Every `Label` carries a fixed six-property set**: `Color`, `FillPortions`, `Height`, `Size`, `Text`, `VerticalAlign`. | 1,370/1,370 each | `high` |
| U7 | **Every `Label` carries `FillPortions`** — the doc mentions `FillPortions` only as a GroupContainer per-child sizing property. | 1,370/1,370 | `high` |
| U8 | **`FillPortions` appears on `Label` and `GroupContainer` only** — never on any other control type. | 2,204/2,204 uses | `high` |
| U9 | **`Label` `VerticalAlign` is `.Middle`.** | 1,369/1,370 (one `.Top`) | `high` |
| U10 | **Every `Classic/Button` carries all 14 properties**, including four the doc's §4 button list omits: `FocusedBorderThickness`, `HoverColor`, `PressedColor`, plus `Height` and `Width`. | 268/268 each | `high` |
| U11 | **`FocusedBorderThickness` is never 0** — always `=1`, occasionally `=2`. A focus ring is always present, just thin. | Button 1 (207) / 2 (61); TextInput 1 (65); Radio 1 (16) | `high` |
| U12 | **Hover and pressed states are light tints of the surface, not dark fills, and the text colour does not change.** `HoverFill` `RGBA(234,230,242,1)`, `PressedFill` `RGBA(228,225,236,1)`, `HoverColor` stays `RGBA(27,27,35,1)`. | 233 / 238 / 217 of 268 buttons | `high` |
| U13 | **The width inset idiom `=Parent.Width - N`** is the standard way to inset a child from its container. N ∈ {8, 10, 12, 20, 24, 32, 40, 56, 80}. | ~1,591 of 2,291 `Width` uses | `high` |
| U14 | **`Size` is a closed set of 11 values**, floor 8, ceiling 26. Not a free numeric field. | 1,829 uses | `high` |
| U15 | **`FillPortions` is `=0` by default** — the overwhelming majority, with `=1` the only common alternative. | 1,665 of 2,204 are `=0`; 342 are `=1` | `high` |
| U16 | **`LayoutOverflowY` sits at nesting depth 2 specifically**, and only on `GroupContainer`. The doc says "content container and inner form card" without pinning the depth. | 34/34 at depth 2 | `high` |
| U17 | **Nesting runs 6–8 levels deep**, with the bulk of controls at depth 6. The doc gives no depth guidance, and a generator that flattens will not match. | d6 holds 1,172 of 2,830 controls | `high` |
| U18 | **`RGBA(56,96,178,1)` is reserved for `LoadingSpinnerColor`** and appears nowhere else. | 17 uses, all on that property | `high` |
| U19 | **`BorderThickness` is only ever 0, 1 or 2.** | Button 0/1; Label 1; TextInput 1; Gallery 1; GroupContainer 1/2 | `high` |
| U20 | **The palette is 31 colours**, with 9 covering 89% of uses. | 4,391 uses | `high` |
| U21 | **`Icon` uses six enum members**: `Icon.Document`, `Icon.View`, `Icon.Person`, `Icon.Clock`, `Icon.Publish`, `Icon.Trash`. | 77 uses | `medium` |
| U22 | **Block scalars are never used decoratively.** Every one of the 119 has a genuine forcing character. A generator may emit `\|` only when required. | 0 of 119 unnecessary | `high` |
| U23 | **Only six properties ever take a block scalar**: `OnSelect`, `OnVisible`, `OnCheck`, `Text`, `OnUncheck`, `OnChange`. | 119 uses | `high` |
| U24 | **Every `GroupContainer` carries both `Height` and `LayoutMinHeight`** — universal, not limited to cards and galleries as §5 implies. | 887/887 | `high` |

---

# 3. Contradicted — RESOLVED by Vin

**Vin's ruling, applied to every row below:**

> *"For each topic that conflicts with the reality, you must stick with how the reality is. For one that only contains in the rule just stick with the rule."*
> *"Use auto layout rule instead."*

Two standing rules follow, and they govern Sessions 4–9:

- **Conflict → the artifacts win.** Every C-row where a measured count contradicts the doc resolves to the measured value. §6 of `yaml-conventions.md` is superseded by `ledger/01` §5 and must not be quoted as a source of numbers.
- **Doc-only → the doc stands.** A rule in the doc that the artifacts neither confirm nor contradict is kept as written, at the doc's own confidence. It is not promoted to `high` by surviving — absence of counter-evidence is not evidence.
- **C9 is resolved explicitly in favour of AutoLayout.** No generated screen positions children with `X`/`Y`. `X`/`Y` appear only on the depth-1 root container.

| # | Resolution |
|---|---|
| C1 | `RadioSize: =18` (13 uses); `=16` acceptable (3). **Never 30.** |
| C2 | `TemplateSize` per gallery from the measured set — 40, 34, 52, 42, 48, 58, 54. **Never 51.** |
| C3 | `Size` ceiling is **26**. Large numerals use 26, 22 or 20. **`Size: 32` is not a legal value.** |
| C4 | No `Size: 18`. Use 16 or 20. |
| C5 | Nav buttons `Height: =34`. **Never 35.** |
| C6 | Top bar `Height: =60` or `=62`. **Never 58.** |
| C7 | `Size` floor is **8**, not 9. |
| C8 | `Icon` enum set is the six measured members: `Document`, `View`, `Person`, `Clock`, `Publish`, `Trash`. **`Icon.Error` is not confirmed** — treat as `UNVERIFIED` if needed. |
| C9 | **AutoLayout only.** `X`/`Y` on the depth-1 root container and nowhere else. The doc's §9 skeleton and §10 gallery example must be rewritten from a real screen before either is quoted again. |
| C10 | The Button property set is the measured 14, not the doc's 10. |
| C11 | `FillPortions` defaults to `=0`; `=1` is the only common alternative. Not a primary layout tool. |

**Consequence for Session 5.** `yaml-conventions.md` §6 and its two copy-paste examples (§9 skeleton, §10 gallery) are the least trustworthy parts of the doc and the most likely to be copied verbatim. The merged skill must carry a skeleton derived from a real screen, not from the doc.

---

# 3-original. Contradicted — as measured (retained for the record)

**Six of these are the same class of failure: a specific numeric value the doc prescribes that
appears zero times in seventeen shipped screens.** Not rare — absent.

Per the brief, these are flagged and not resolved. Vin decides each.

| # | Doc says | Artifacts show | Note |
|---|---|---|---|
| **C1** | §4 Radio `RadioSize: =30` | **0 occurrences.** Actual: `=18` (13), `=16` (3) | The doc's value is not merely uncommon — no shipped radio uses it |
| **C2** | §6 and §10 gallery `TemplateSize: 51` | **0 occurrences.** Actual: 40 (14), 34 (8), 52 (5), 42 (4), 48 (3), 58 (1), 54 (1) | 51 sits between two values that are used; looks like a stale target |
| **C3** | §6 big stat numbers `Size: 32`, and the §9 skeleton uses `Size: =32` | **0 occurrences.** `Size` ceiling across all 1,829 uses is **26** (3 uses) | The doc's own copy-paste skeleton contains a value no screen uses |
| **C4** | §6 form title `Size: 18` | **0 occurrences** | Nearest used values: 16 (17), 20 (16) |
| **C5** | §6 nav buttons `Height: 35`, and the §9 skeleton uses `Height: =35` | **0 occurrences.** Nearest: `=34` (245) | Off by one from the actual convention |
| **C6** | §6 top bar `Height: 58` | **0 occurrences.** Nearest: `=60` (18), `=62` (75) | |
| **C7** | §6 "Font floor ≈ 9 so nothing becomes unreadable" | Floor is **8**, used **231 times** | The floor was breached deliberately and at scale, not by accident |
| **C8** | §4 Icon "verified in use: `Icon.Person`, `Icon.Error`, `Icon.Publish`" | `Icon.Error` **0 occurrences.** And four members in use are unlisted: `Icon.Document` (22), `Icon.View` (22), `Icon.Clock` (8), `Icon.Trash` (1) | The doc's "verified" list is both incomplete and contains an entry no artifact supports |
| **C9** | §9 skeleton and §10 gallery example position children with `X`/`Y` (`X: =16`, `Y: =64`, `X: =520`, `X: =820`) | **No control except the depth-1 root declares `X` or `Y`.** 0 of 1,370 Labels, 0 of 268 Buttons, 0 of 36 Galleries | **The most consequential contradiction.** The doc's two copy-paste starting points teach coordinate positioning; every shipped screen uses AutoLayout exclusively. Anyone starting from the skeleton produces something structurally unlike the working set |
| **C10** | §4 button property list: `Text`, `Fill`, `Color`, `Size`, `FontWeight`, `Align`, `HoverFill`, `PressedFill`, `BorderThickness`, `OnSelect` | Every button also carries `FocusedBorderThickness`, `HoverColor`, `PressedColor`, `Height`, `Width` — 268/268 | Listed under Contradicted rather than Undocumented because the doc presents its list as complete |
| **C11** | §5 "don't rely on `FillPortions` alone or rows collapse to zero height" | Consistent with the artifacts, but `FillPortions: =0` on 1,665 of 2,204 uses means the property is mostly *disabling* proportional sizing rather than driving it | Not a hard contradiction — a difference in emphasis. Flagged because a reader of the doc would expect `FillPortions` to be a primary layout tool |

## The pattern in C1–C7

Seven prescribed numbers, seven zero-occurrence results, all in §6 "Sizing" and §4. The most
economical explanation is that §6 records the *intended* ~0.8 scale targets while the shipped
screens record what was actually tuned afterwards — the doc was written from the plan, the
screens from the work. If that is right, the artifacts win on every one and §6 should be
rewritten from measurement.

**That is a hypothesis, not a resolution.** The alternative is that §6 describes a newer
standard the screens predate, which would invert the ranking — and only Vin can tell which.
