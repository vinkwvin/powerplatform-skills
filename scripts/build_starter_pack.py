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
   หน้า 2 บอกทุกอย่างที่ต้องทำ ใช้เวลาอ่าน 2 นาที

2. อัปโหลด skill ทั้ง 5 อันในโฟลเดอร์ skills/
   claude.ai  ->  Settings  ->  Capabilities  ->  Skills  ->  Upload skill
   อัปโหลดทีละอัน ทำครั้งเดียวจบ

3. ก่อนปิดแชทที่ใช้ทำงานจริง วาง prompt ในไฟล์
   prompts/team-quick-feedback.md  แล้วส่งไฟล์ที่ได้กลับมาให้ N'Vin

โฟลเดอร์อื่น
------------
prompts/project-style-override.md   ใช้ตอนโปรเจกต์นี้ใช้สี/ขนาดคนละชุดกับที่ skill วัดมา
CHANGELOG.md                        ผมแก้อะไรไปบ้าง และรอบไหนต้องโหลดใหม่

ติดขัดตรงไหน ทักมาได้เลยครับ  — N'Vin
"""


def main():
    pdf = next((DIST / "handoff").glob("*.pdf"), None)
    items = [(DIST / f"{s}.zip", f"skills/{s}.zip") for s in SKILLS]
    items += [
        (ROOT / "prompts" / "team-quick-feedback.md", "prompts/team-quick-feedback.md"),
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
