# จบงานแล้ว วางอันนี้ก่อนปิดแชท — the 2-minute version

<!-- v1.0.0 -->

**สำหรับทีม.** วางบล็อกข้างล่างนี้ที่ **ท้ายแชท** ที่เพิ่งใช้ skill ทำงานจริงเสร็จ — ก่อนปิดแชท
แล้วเซฟไฟล์ที่ได้ส่งกลับมาให้ N'Vin ทาง Teams จบ ไม่ต้องแก้อะไร ไม่ต้องตัดสินใจอะไร

**ทำไมต้องท้ายแชท ไม่ใช่ทีหลัง.** แชทยาว ๆ จะถูกย่อความ (compact) และสิ่งที่เหลือรอดคือสรุปที่
*ฟังดูสมเหตุสมผล* มากกว่าที่ *ถูกต้อง* ถามวันศุกร์ถึงแชทวันอังคาร จะได้เรื่องแต่งที่มีผิวสัมผัสของข้อเท็จจริง

**อย่ากรองก่อน.** อย่าตัดสินใจเองว่าเรื่องที่เจอสำคัญพอไหม มีคนรายงานไปแล้วหรือยัง หรือเป็นความผิดตัวเอง
หรือเปล่า การส่งมาถูกมาก การตัดสินใจเป็นงานของรอบ intake และรอบ intake ทำได้ดีกว่ามากเมื่อมีห้ารายงาน
มากกว่ามีอันเดียว

**อันนี้เป็นเวอร์ชันสั้น.** เวอร์ชันเต็มอยู่ที่ [`feedback-session.md`](feedback-session.md) ซึ่งเก็บ
ละเอียดกว่าแต่ยาวกว่ามาก — ใช้ตอนที่งานเจอปัญหาหนัก ๆ หรือตอนที่คุณเป็นคนทำรอบ intake เอง
วันธรรมดา ๆ ใช้อันนี้พอ

---

## The prompt — คัดลอกตั้งแต่บรรทัดล่างนี้ลงไป

We are done. Before I close this chat, write a short feedback record so the skill that guided this
work can be improved. Be blunt — this is for fixing the skill, not for reassuring me. An honest
account of what you got wrong is the useful thing here.

Output **one YAML code block and nothing else**. No summary paragraph, and do not re-print the
artifact — I already have it.

```yaml
meta:
  skill: <which skill guided this>
  skill_version: <the version comment in its SKILL.md, if you can see it>
  what_we_built: <one line>
  rounds: <how many times I sent it back for corrections>
  first_attempt_validated: <true|false — did your FIRST output pass the validator?>

# Exact text the platform showed — Power Apps Studio, SharePoint, or the flow importer.
# Copy it character for character, including the Location. Do not paraphrase.
# This is the most valuable field in the file: every verbatim error so far has become a
# static check, which is one round trip nobody has to make again.
studio_errors_verbatim: []

fixes:
  - element: <the exact control, column, or action. "the layout was wrong" is unusable>
    wrong: <what you produced>
    right: <what it had to become>
    caught_by: validator | studio | me-eyeballing | you-self-corrected
    tier: platform | house | unclear
    rule_status: absent | present-but-wrong | present-and-ignored
    rule_quote: <if present-but-wrong or present-and-ignored, quote the SKILL.md line>
    times: <rounds this same thing took>

biggest_miss: |
  <Free text, and answer it even if fixes is empty. What would have saved the most round trips
  if the skill had said it on page one? If something felt structurally wrong rather than
  individually wrong, this is where it goes — no structured field will catch that.>
```

Three things decide whether this record is useful:

1. **`tier`** — `platform` means Studio or SharePoint *refused* it; that is universal and everyone
   needs the fix. `house` means it worked and simply did not match this team's conventions; that may
   just mean this project differs, and the fix is a config value rather than a rule. If you are not
   sure, write `unclear`. Do not guess — a misfiled tier turns one project's preference into
   everyone's law.

2. **`rule_status`** — this decides what the fix actually is.
   - `absent` — the skill never mentioned it. Add a rule.
   - `present-but-wrong` — the skill said something and it was incorrect. Correct it.
   - `present-and-ignored` — the rule was there, it was correct, and you did not follow it.
     **Say so.** It is the most valuable line you can write and the one you will most want to
     avoid, because it reads as an admission. It is not: it means the rule is buried in a
     reference, worded as advice where an instruction was needed, or crowded out by the text
     around it. Skip this category and the skill only ever gets longer, never better.

3. **Quote any value containing a colon-space**, because this record is YAML too:

   ```yaml
   wrong: Control: Image@2.2.0        # BREAKS — colon-space starts a nested mapping
   wrong: "Control: Image@2.2.0"      # correct
   ```

If a section is genuinely empty, return it empty. `fixes: []` is a real answer and padding it costs
someone reading time later.
