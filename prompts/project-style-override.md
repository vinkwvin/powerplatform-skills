# โปรเจกต์นี้ใช้ดีไซน์คนละชุด — ทำยังไงไม่ต้องแก้ skill

<!-- v1.0.0 -->

**อาการ.** validator เตือนขึ้นมาเป็นสิบบรรทัด ทั้งที่งานก็ถูกแล้ว — สีไม่ตรง ขนาดฟอนต์ไม่ตรง
ระยะห่างไม่ตรง เพราะโปรเจกต์นี้ใช้ design system คนละชุดกับที่ skill ถูกวัดมา

**สิ่งที่ห้ามทำ.** อย่าแก้ `validate_*.py` และอย่าปล่อยให้ตัวเองชินกับการมองข้าม warning
วันที่ warning กลายเป็นสิ่งที่ทุกคนข้าม คือวันที่ validator หมดประโยชน์ และมันคือของชิ้นเดียว
ที่กั้นระหว่างเพื่อนร่วมทีมกับไฟล์ที่พังตอน paste

**สิ่งที่ควรทำ.** กฎในชุดนี้แบ่งเป็นสองชั้น และมันตั้งใจออกแบบมาให้เจอสถานการณ์นี้พอดี:

| ชั้น | แปลว่า | validator | แก้ได้ไหม |
|---|---|---|---|
| `PLATFORM` | Power Apps / SharePoint จะปฏิเสธจริง ๆ | `ERROR` | ไม่ได้ ไม่ว่าโปรเจกต์ไหน |
| `HOUSE` | ธรรมเนียมที่ทีมเราตกลงกันเอง ใช้ได้ผลดี แต่ไม่ใช่กฎของแพลตฟอร์ม | `WARN` | ได้ — นี่คือจุดที่ตั้งใจให้แก้ |

สีทั้งชุด ขนาดฟอนต์ ระยะ inset และ prefix ของตัวแปร เป็น `HOUSE` ทั้งหมด
เปลี่ยนได้โดยไม่ต้องแตะโค้ดสักบรรทัด

---

## วิธีที่ 1 — บอกตอนเริ่มแชท (ใช้อันนี้เป็นหลัก)

ไม่ต้องแก้ไฟล์ ไม่ต้องลง skill ใหม่ ไม่ต้องแตะอะไรเลย วางตอน **เริ่ม** แชท พร้อมกับ token ของโปรเจกต์

### The prompt — คัดลอกตั้งแต่บรรทัดล่างนี้ลงไป

This project uses a different design system from the one this skill was measured against. Before we
start, set up a project style override so the validator checks this project's conventions instead of
the defaults.

Here are this project's tokens:

```
<paste your palette, type scale, spacing scale, and naming conventions here —
 hex values are fine, I do not need them converted first>
```

Do this:

1. Copy `assets/house-style.yaml` from the skill to a working file called `our-style.yaml`.
2. Replace only the `HOUSE` values my tokens actually cover — the palette, the font-size set, the
   inset values, the variable prefixes. Convert hex to `RGBA(r, g, b, a)` for me.
3. Set `enforce: false` on any section my tokens do not speak to, rather than inventing values for
   it. An invented convention is worse than an absent one.
4. Bump `meta.style_id` to something naming this project, so a later field report can say which
   style it ran against.
5. From here on, validate with `--style our-style.yaml` instead of the default, and say so each
   time you run it.
6. Show me `our-style.yaml` once, at the end. I want to save it and re-upload it on the next chat
   for this project so we do not do this twice.

Two rules while you do that:

- **Do not change any `PLATFORM` rule and do not edit the validator.** If something in this project
  seems to require it, stop and tell me — that is a finding to send back, not a local edit.
- If a warning survives the override, do not silence it. Tell me what it is. It may be the one
  warning that was right.

---

## วิธีที่ 2 — ไม่มี token ครบ แค่อยากดูว่ามีอะไรพังจริง ๆ ไหม

บางทีก็แค่อยากรู้ว่า "เรื่องที่เตือนมานี่ มีอันไหนที่ Studio จะปฏิเสธจริงบ้าง" วางบรรทัดเดียว:

> Validate with `--platform-only` and show me both runs side by side — what the platform will
> actually reject, and what is only our house convention. I want to see the difference.

ทุก validator รับ flag นี้ อะไรที่หายไปตอนใส่ `--platform-only` คือเรื่องสไตล์ ไม่ใช่เรื่องพัง

---

## วิธีที่ 3 — จะแก้ค่าเริ่มต้นถาวร (นาน ๆ ครั้ง และควรบอก N'Vin)

ถ้าเป็นเรื่องที่ **ทั้งทีมควรได้เหมือนกัน** ไม่ใช่แค่โปรเจกต์เดียว — เช่น Studio รับ enum member
ตัวใหม่ที่เมื่อก่อนขึ้น warning — อันนั้นไม่ใช่ style override แต่เป็น **catalog ที่โตขึ้น**
ส่งกลับมาให้ N'Vin ผ่าน [`team-quick-feedback.md`](team-quick-feedback.md) แล้วมันจะไปอยู่ใน zip
รอบหน้าที่ทุกคนได้ใช้

จะแก้ zip ของตัวเองให้ถาวรก็ทำได้ — อัปโหลด zip ของ skill เข้าแชทใหม่แล้วสั่ง:

> Open this skill zip, edit only `assets/house-style.yaml` with the changes below, leave every other
> file byte-for-byte unchanged, re-zip it with the same folder structure, and give it back to me to
> download. Then confirm which files you touched.

แล้วเอาไปอัปโหลดทับที่ **Settings → Capabilities → Skills**

**แต่รู้ไว้ว่านี่คือการแยกสำเนาของตัวเองออกจากของทีม** รอบหน้าที่ N'Vin ปล่อย zip ใหม่ การแก้ของคุณจะหายไป
ถ้ามันคุ้มที่จะแก้ มันก็คุ้มที่จะส่งกลับมา — แล้วจะได้ไม่ต้องแก้ซ้ำอีก
