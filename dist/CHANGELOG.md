# Changelog

What changed in each skill, and whether you need to re-install.

**Skills on claude.ai are per-account and do not sync.** An improved skill sitting here helps
nobody until each teammate downloads it and re-uploads. Every entry says whether it is worth
your two minutes.

---

## generating-powerapps-yaml v1.1.0 — enum members are checked like control types

**Re-install: worth it if you generate screens.** One new check, no behaviour removed.

**What prompted it.** The first field use of the suite, on a project with nothing in common with
the one it was built from. The output was structurally clean — 191 controls, 5 control types, 9
levels deep, zero property names the reference set had never seen, `X`/`Y` on the root containers
only. But it used `LayoutJustifyContent.SpaceBetween`, which appears in none of the 17 reference
screens, and **nothing flagged it**. `SpaceBetween` happens to be real. The next guess might not
be, and an invented enum member fails only when Studio rejects the paste — the exact round trip
this suite exists to avoid.

The gap was that `Icon` had a confirmed-member list and no other enum did. Step 4 of the workflow
said "choose control *types* from the catalog only", which a reader correctly reads as not being
about enum members at all.

**Changed:**
- `assets/house-style.yaml` gains `enum_members:` — 14 enums with their measured members.
- `validate_pa_yaml.py` checks any `Enum.Member` in any property value against that list. Tier
  `HOUSE`, so it is a WARN: an unlisted member is *unconfirmed*, not *invalid*.
- `references/control-catalog.md` §5 documents all 14 enums with counts.
- `SKILL.md` step 4 now covers enum members explicitly.

**If you hit the warning:** paste-test that one control alone. If Studio accepts it, add the
member to `assets/house-style.yaml` and say so in your field report. That is how the confirmed
set grows — it is not meant to stay at 14 enums forever.

**New project with a different design system?** Nothing here changes: enum members are a platform
vocabulary, not a house style, so this list should converge across projects rather than diverge.

---

## v1.0.0 — first release

All five skills. Install all of them.

| Skill | Zip |
|---|---|
| `planning-powerplatform-solutions` | `planning-powerplatform-solutions.zip` |
| `generating-powerapps-yaml` | `generating-powerapps-yaml.zip` |
| `building-sharepoint-lists` | `building-sharepoint-lists.zip` |
| `building-powerautomate-flows` | `building-powerautomate-flows.zip` |
| `writing-app-manuals` | `writing-app-manuals.zip` |

**What they are built from** — artifacts that actually worked, not documentation:

- 17 Power Apps screens that compiled in Studio (2,830 controls, 2,847 property blocks)
- 10 SharePoint lists, 131 columns, in production
- one real Power Automate legacy export from our own tenant
- two manuals that shipped

**Notable findings baked in:**

- A legacy flow package has **five** files, not two. `apisMap.json` and `connectionsMap.json`
  are not in any documentation we could find, and `connectionsMap.json` appears to be what
  `PackageFlowMissingConnectionMap` is actually complaining about.
- Seven values prescribed in our written conventions doc appear **zero times** in seventeen
  shipped screens. The screens win; the doc is superseded.
- `X`/`Y` coordinates appear only on the outermost container — 0 of 2,813 nested controls.
- Lookup columns are absent from all 131 production columns, deliberately: they are not
  delegable, so a gallery filtered on one truncates silently at 500 rows with no error.

**How to install:** claude.ai → Settings → Capabilities → Skills → Upload skill.

---

## How to read future entries

Each entry says one of:

- **re-install** — a rule or validator changed; you will get worse output without it
- **re-install when convenient** — wording, references, or a new example
- **no action** — internal only

