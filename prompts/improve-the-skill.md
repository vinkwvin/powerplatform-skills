# แชทปรับปรุง skill — ทีมดูแลกันเอง

<!-- v1.0.0 -->

## เมื่อไหร่ถึงใช้อันนี้

เมื่อมีบันทึกจากการทำงานจริงสะสมไว้พอสมควร (แนะนำ 3–5 อัน หรือเมื่อเจอเรื่องที่ Studio ปฏิเสธ
ซึ่งเรื่องแบบนั้นไม่ต้องรอ) รอบหนึ่งใช้เวลาประมาณ 30–45 นาที

## ต้องเตรียมอะไร

| ลำดับ | สิ่งที่ต้องมี | เอามาจากไหน |
|---|---|---|
| 1 | ไฟล์ `.zip` ของ skill เวอร์ชันล่าสุด | โฟลเดอร์กลางของทีม |
| 2 | บันทึกจากแชททำงานจริง 1 อันขึ้นไป | ที่เก็บไว้จาก `team-quick-feedback.md` |
| 3 | แชทใหม่ที่ว่างเปล่า | อย่าใช้แชทเดิมที่ทำงาน — บริบทเก่าจะทำให้ตัดสินใจเพี้ยน |

## ขั้นตอน

1. เปิดแชทใหม่
2. แนบไฟล์ `.zip` ของ skill
3. แนบหรือวางบันทึกทั้งหมดที่มี
4. วาง prompt ข้างล่างนี้
5. ตอบคำถามที่มันถาม แล้วรอผลลัพธ์
6. โหลด `.zip` ใหม่ที่ได้ → อัปโหลดที่ Settings → Capabilities → Skills → Upload skill
7. วางไฟล์ใหม่ลงโฟลเดอร์กลาง แล้วแจ้งทีมพร้อมบรรทัด CHANGELOG ที่ได้มา

---

## The prompt — คัดลอกตั้งแต่บรรทัดล่างนี้ลงไป

You are maintaining a Claude Skill. I have attached the skill as a `.zip` and one or more field
records from real working sessions.

This skill has no central maintainer. You are it, for this round. The person running this chat
knows Power Platform but did not build the skill, so state your reasoning as you go rather than
only your conclusions.

Work through the seven steps below **in order**. Do not skip ahead to editing.

### Step 1 — Baseline. Change nothing yet.

1. Unpack the zip and list its structure.
2. Report: the skill name, the version in the `<!-- vX.Y.Z -->` comment, and the line count of
   `SKILL.md`.
3. Run `python3 scripts/self_check.py` and paste the output.

If the self-check fails before you have touched anything, stop and say so. The zip is damaged or
incomplete, and no change made on top of it can be trusted.

**Do not read the files under `tests/`.** There are megabytes of them. They exist to be checked
by the script, not read by you, and reading them will spend context you need for the edit.

### Step 2 — Triage. Rank the findings before deciding anything.

Extract every finding from the records into one table, then sort by this order — highest first:

| Rank | Signal | Why it ranks there |
|---|---|---|
| 1 | `caught_by: studio` | it reached a real paste. The validator is the only thing between a teammate and a broken artifact, and it failed |
| 2 | the same `element` in records from **two different people** | independent corroboration beats one report claiming it happened five times |
| 3 | `rule_status: present-and-ignored` | the rule exists and did not land. Fixable without adding length |
| 4 | `times >= 3` in one record | corrected three or more times in a single session |
| 5 | `rule_status: present-but-wrong` | actively misleading, but at least somebody noticed |
| 6 | `rule_status: absent`, single record | real, and the easiest kind to over-act on |

Then assign each finding a tier, and **say which** — this is the decision that keeps the skill
usable on projects it was not built from:

- **`platform`** — Power Apps, SharePoint or the flow importer rejected it. Universal. Applies to
  every project, forever.
- **`house`** — it worked. It just did not match this team's conventions. This may simply mean the
  project differs, in which case the fix is a config value and not a rule.
- **`example`** — a fact about that one project. Record it, change nothing.

If a record says `unclear`, decide it here and explain how you decided. Do not carry `unclear`
into Step 3.

### Step 3 — Decide the action for each finding.

`rule_status` determines the fix. This is the part people get wrong:

| `rule_status` | Action | The trap |
|---|---|---|
| `absent` | add a rule | the tempting one. A skill that only grows becomes a skill nobody finishes reading, and an unread rule is worth nothing |
| `present-but-wrong` | correct it, and check the reference file it came from | if a reference explained it wrongly, that reference is now suspect everywhere else too |
| `present-and-ignored` | **move or rewrite it. Do not add a second rule saying the same thing louder** | the highest-value category, and the one that feels least like progress |

For `present-and-ignored`, pick from these and say which you chose:

- move it out of `references/` and into the `SKILL.md` body
- rewrite advice as an instruction — "prefer X" becomes "use X. Never Y."
- attach the measured count, so a reader knows it is evidence and not taste
- attach the failure, so ignoring it has a visible cost
- delete something next to it, so it competes with less

A `house` finding does **not** get a rule. It gets a value in `assets/house-style.yaml`.

### Step 4 — A check beats a rule. Write the check first.

If any finding has `caught_by: studio`, ask whether a static check could have caught it before the
paste. If yes, add the check to `scripts/validate_*.py` **before** you touch any rule text.

A rule tells the model what to do and depends on it reading and following the rule. A check stops
the artifact regardless. When you can have either, take the check.

The most useful thing in a record is `studio_errors_verbatim`. Every verbatim error string
collected so far has become a check. Read those first.

### Step 5 — Make the change, then prove it.

What you may edit, and what you may not:

| Path | May edit | Notes |
|---|---|---|
| `SKILL.md` | yes | **hard cap 200 lines.** If your change adds lines, name what you are removing |
| `assets/house-style.yaml` | yes | every project-specific convention belongs here, not in `SKILL.md` |
| `references/*.md` | yes | detail that not every run needs |
| `scripts/validate_*.py` | yes — to add or correct a check | never to silence a warning |
| `scripts/self_check.py` | no | it is the referee |
| `tests/reference/*` | **no, never** | these compiled in Studio. They are the evidence |
| `tests/expected.json` | only deliberately | see below |

Then run `python3 scripts/self_check.py` again and paste the output.

**If a rule you added fires on the reference screens, the rule is wrong.** Those screens compiled
and shipped. This has happened before: a warning was added for buttons with no `BorderThickness`,
and it fired on 20 reference buttons that worked fine. The reason turned out to be that all 20
shared the brand-blue fill, and Studio's default border is blue, so it was invisible. The
inference was reasonable and the evidence still beat it. A validator that warns on known-good
output is how people learn to ignore warnings.

**Add a probe for anything new.** Put a small file in `tests/probes/` that produces the error your
new rule is meant to produce, add its expected counts to `tests/expected.json`, and show me it
fails without your change and passes with it. A rule with no probe survives until the next edit
and then quietly stops working.

Changing a number in `tests/expected.json` is allowed when behaviour changed on purpose. It is
never allowed to make a failure go away. If you change one, say exactly why in the same message.

### Step 6 — Version and changelog.

Bump the `<!-- vX.Y.Z -->` comment in `SKILL.md`:

- **patch** — wording, a reference edit
- **minor** — a new rule or a new validator check
- **major** — the workflow or the output format changed

Write a `CHANGELOG.md` entry containing all four of these:

1. **Re-install: yes / no** — and be honest. A teammate who re-downloads for nothing stops
   re-downloading.
2. What changed, and the evidence for it. Quote the verbatim error or the count.
3. The before and after `self_check.py` numbers.
4. **What you did NOT act on, and why.** This matters as much as the rest. Somebody filed those
   findings; if nothing visible happens to a report, that person stops filing, and their input is
   lost for good.

### Step 7 — Rebuild and hand back.

Rebuild the `.zip` with the same folder structure — `SKILL.md` at the root inside a single folder
named for the skill — and give it to me to download.

Then list, in one short table: every file you changed, and one line saying what changed in it.

If you cannot produce a `.zip` for download in this chat, say so and instead output every changed
file **complete**, each in its own code block, with its exact path. I will rebuild the zip myself.

### Rules you may not break

These exist because there is nobody to catch it if you get one wrong.

1. **Every rule needs evidence.** A count from the reference corpus, or a verbatim error string
   from the platform. "This is good practice" and "this is usually recommended" are not evidence.
   If you have no evidence, write the rule as a question for the team instead of a rule.
2. **`platform` means the platform refused it.** Not "it looked wrong". Not "it is inconsistent".
   Mislabelling a house preference as a platform law is how a toolset stops working on the next
   project.
3. **Never silence a warning by editing the validator.** If the warning is wrong, the rule behind
   it is wrong, or the project's conventions differ — the first is a fix, the second is a
   `house-style.yaml` value. Neither is a deleted check.
4. **`SKILL.md` stays under 200 lines.** Length is paid by every future reader. If you cannot find
   something to remove, the addition probably is not worth its space.
5. **Never ship with `self_check.py` failing.**
6. **Never delete a rule that carries a measured count** unless a field record actually
   contradicts it. Somebody counted that.
7. **Say when you are unsure.** An honest "I could not tell whether this is platform or house" is
   worth more than a confident wrong tier. Leave it for the next round and say so in the
   changelog.

Start with Step 1.

---

## หลังจากได้ไฟล์ใหม่มาแล้ว

1. **ทดสอบก่อนแจก** — อัปโหลด skill ใหม่ แล้วลองสร้างงานจริงสัก 1 ชิ้น ถ้าออกมาแย่ลง ให้กลับไปใช้
   เวอร์ชันเดิม โฟลเดอร์กลางควรเก็บเวอร์ชันย้อนหลังไว้อย่างน้อย 3 อัน
2. **วางลงโฟลเดอร์กลาง** ตั้งชื่อไฟล์ให้มีเวอร์ชัน เช่น `generating-powerapps-yaml-v1.4.0.zip`
3. **แจ้งทีม** พร้อมบรรทัดจาก CHANGELOG โดยเฉพาะบรรทัด re-install — ถ้าไม่บอก จะไม่มีใครโหลด
   และงานทั้งรอบนี้จะไม่ถึงใครเลย
4. **เก็บบันทึกที่ใช้ไปแล้ว** ย้ายไปโฟลเดอร์ `ใช้แล้ว/` จะได้ไม่หยิบมาทำซ้ำรอบหน้า

## ถ้าเวอร์ชันใหม่แย่กว่าเดิม

กลับไปใช้เวอร์ชันก่อนหน้าจากโฟลเดอร์กลาง แล้วบันทึกไว้ว่ารอบนั้นเปลี่ยนอะไรและอาการเป็นอย่างไร
การถอยกลับไม่ใช่ความล้มเหลว — มันคือเหตุผลที่เราเก็บเวอร์ชันเก่าไว้ตั้งแต่แรก
