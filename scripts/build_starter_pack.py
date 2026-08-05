#!/usr/bin/env python3
"""Assemble the one file N'Vin sends the team.

The team does not use GitHub, so everything they need has to arrive as a single attachment:
the five skill zips, the handoff PDF, the two prompts they will paste, and the changelog that
tells them whether a re-download is worth their two minutes.

Run after scripts/package_skills.py and scripts/build_handoff.py.

    python3 scripts/build_starter_pack.py
"""
import pathlib
import sys
import zipfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
DIST = ROOT / "dist"
OUT = DIST / "handoff" / "team-starter-pack.zip"

SKILLS = ["planning-powerplatform-solutions", "generating-powerapps-yaml",
          "building-sharepoint-lists", "building-powerautomate-flows", "writing-app-manuals"]

# Read once, in Thai, by someone who just downloaded a zip and does not know what to open.
READ_ME_FIRST = """\
Power Platform Skill Suite — เริ่มตรงนี้
=======================================

1. เปิดไฟล์ PDF ก่อน  ->  Power-Platform-Skill-Suite-Handoff-TH.pdf
   16 หน้า มีสารบัญอยู่หน้า 2 ถ้ามีเวลาแค่ 2 นาที อ่านกล่อง "ถ้ามีเวลาแค่ 2 นาที" หน้า 2

2. อัปโหลด skill ทั้ง 5 อันในโฟลเดอร์ skills/
   claude.ai  ->  Settings  ->  Capabilities  ->  Skills  ->  Upload skill
   อัปโหลดทีละอัน ทำครั้งเดียวจบ

3. ตั้งโฟลเดอร์กลางของทีม ตามโครงสร้างในหน้า 10 ของ PDF
   แล้วตกลงกันว่าใครเป็นผู้ดูแลเวอร์ชัน (ต้องมี 1 คน)


ทีมดูแล skill เหล่านี้เองทั้งหมด ไม่มีคนกลางคอยแก้ให้
--------------------------------------------------
วงจรมี 2 ขั้นตอน อธิบายไว้ในส่วนที่ 7 ของ PDF

  ขั้นที่ 1  ทุกคน · 2 นาที · ทุกครั้งที่ทำงานจริงเสร็จ
            วาง prompt จาก prompts/team-quick-feedback.md ท้ายแชท
            แล้วเซฟไฟล์ที่ได้ลงโฟลเดอร์กลาง

  ขั้นที่ 2  ใครก็ได้ 1 คน · 30-45 นาที · เมื่อสะสมบันทึกได้ 3-5 อัน
            เปิดแชทใหม่ แนบ .zip ของ skill กับบันทึกทั้งหมด
            แล้ววาง prompt จาก prompts/improve-the-skill.md
            จะได้ .zip เวอร์ชันใหม่กลับมา


ไฟล์อื่นในโฟลเดอร์นี้
--------------------
prompts/project-style-override.md   ใช้ตอนโปรเจกต์นั้นใช้สี/ขนาดคนละชุดกับที่ skill วัดมา
CHANGELOG.md                        ประวัติการแก้ไข ต่อท้ายทุกครั้งที่ปล่อยเวอร์ชันใหม่
"""


def main():
    pdf = next((DIST / "handoff").glob("*.pdf"), None)
    items = [(DIST / f"{s}.zip", f"skills/{s}.zip") for s in SKILLS]
    items += [
        (ROOT / "prompts" / "team-quick-feedback.md", "prompts/team-quick-feedback.md"),
        (ROOT / "prompts" / "improve-the-skill.md", "prompts/improve-the-skill.md"),
        (ROOT / "prompts" / "project-style-override.md", "prompts/project-style-override.md"),
        (DIST / "CHANGELOG.md", "CHANGELOG.md"),
    ]
    if pdf:
        items.append((pdf, pdf.name))

    missing = [str(src.relative_to(ROOT)) for src, _ in items if not src.exists()]
    if missing:
        print("Missing — run package_skills.py and build_handoff.py first:", file=sys.stderr)
        for m in missing:
            print(f"  {m}", file=sys.stderr)
        return 1

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("READ-ME-FIRST.txt", READ_ME_FIRST)
        for src, arc in items:
            z.write(src, arc)

    with zipfile.ZipFile(OUT) as z:
        bad = z.testzip()
        if bad:
            print(f"corrupt entry: {bad}", file=sys.stderr)
            return 1
        names = z.namelist()

    print(f"wrote {OUT.relative_to(ROOT)}  ({OUT.stat().st_size // 1024} KB, "
          f"{len(names)} entries)")
    for n in sorted(names):
        print(f"  {n}")
    print("\nSend this one file. Nothing else is needed, and no GitHub access is involved.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
