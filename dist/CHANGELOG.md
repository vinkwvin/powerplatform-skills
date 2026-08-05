# Changelog

What changed in each skill, and whether you need to re-install.

**Skills on claude.ai are per-account and do not sync.** An improved skill sitting here helps
nobody until each teammate downloads it and re-uploads. Every entry says whether it is worth
your two minutes.

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

