#!/usr/bin/env python3
"""Render handoff/handoff.html to a print-ready PDF, and optionally to page images.

`handoff/handoff.html` is the single source. The prose lives there and nowhere else — a
separate markdown copy would disagree with it inside a week, which is the rule this suite
already applies to the manuals it generates.

Pages are fixed-height A4 sections with `overflow: hidden`, which buys exact layout control
and costs reflow: text that grows past the bottom is CLIPPED, silently. So `--images` exists,
and it is not optional after editing copy — it writes one PNG per page so the layout can be
eyeballed the same way a generated screen has to be.

Usage:
    python3 scripts/build_handoff.py
    python3 scripts/build_handoff.py --images        # also write page PNGs
    python3 scripts/build_handoff.py --images --shot-dir /tmp/pages
"""
import argparse
import glob
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "handoff" / "handoff.html"
OUT = ROOT / "dist" / "handoff" / "Power-Platform-Skill-Suite-Handoff-TH.pdf"

# A4 at 96dpi is 794x1123, which is what the paged PDF uses. The screenshot viewport is not
# the same thing: headless Chromium hands back fewer pixels of height than --window-size asks
# for, so a viewport set to the exact page height silently loses the last ~90px — the footer,
# the page number, and on the cover the signature. A review image that crops the bottom of
# every page while looking complete is worse than no review image. Overshoot, and let the
# spare show as body background.
PAGE_PX = (794, 1240)
SECTION_RE = re.compile(r'<section class="page.*?</section>', re.S)


def find_chrome():
    for pattern in ("/opt/pw-browsers/chromium-*/chrome-linux/chrome",
                    "/opt/pw-browsers/chromium/chrome-linux/chrome"):
        hits = sorted(glob.glob(pattern))
        if hits:
            return hits[-1]
    for name in ("chromium", "chromium-browser", "google-chrome"):
        found = shutil.which(name)
        if found:
            return found
    return None


def run(chrome, *args):
    subprocess.run([chrome, "--headless", "--disable-gpu", "--no-sandbox", *args],
                   check=True, capture_output=True)


# Measured in the browser, because only the browser knows where the text actually landed.
# Every page is a fixed-height box with overflow:hidden, so content that grows past the bottom
# is cut without any error — the page just quietly loses its last paragraph. Eyeballing page
# images catches that only if you happen to know what was supposed to be there.
OVERFLOW_PROBE = """
<script>
const out = [];
document.querySelectorAll('.page').forEach((p, i) => {
  const cs = getComputedStyle(p);
  const limit = p.getBoundingClientRect().bottom - parseFloat(cs.paddingBottom);
  let low = 0, who = '';
  p.querySelectorAll(':scope > *').forEach(el => {
    if (el.classList.contains('foot')) return;
    const b = el.getBoundingClientRect().bottom;
    if (b > low) { low = b; who = el.tagName.toLowerCase() + '.' + (el.className || '?'); }
  });
  out.push({page: i + 1, over: Math.round(low - limit), who: who});
});
document.title = JSON.stringify(out);
</script>
"""


def check_overflow(chrome, src):
    """Report any page whose content runs past its own bottom padding."""
    html = src.read_text(encoding="utf-8")
    with tempfile.TemporaryDirectory() as tmp:
        probe = pathlib.Path(tmp) / "probe.html"
        probe.write_text(html.replace("</body>", OVERFLOW_PROBE + "</body>"), encoding="utf-8")
        proc = subprocess.run(
            [chrome, "--headless", "--disable-gpu", "--no-sandbox",
             "--virtual-time-budget=3000", "--dump-dom", probe.as_uri()],
            capture_output=True, text=True)
    m = re.search(r"<title>(\[.*?\])</title>", proc.stdout, re.S)
    if not m:
        print("  (could not measure page overflow)")
        return []
    import json
    bad = [r for r in json.loads(m.group(1).replace("&quot;", '"')) if r["over"] > 0]
    for r in bad:
        print(f"  OVERFLOW  page {r['page']}: content runs {r['over']}px past the bottom "
              f"padding — last element {r['who']}")
    return bad


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--images", action="store_true", help="write one PNG per page for review")
    ap.add_argument("--shot-dir", default="/tmp/handoff-pages")
    args = ap.parse_args()

    chrome = find_chrome()
    if not chrome:
        print("No chromium found. Install one, or set it on PATH.", file=sys.stderr)
        return 1
    if not SRC.exists():
        print(f"Missing source: {SRC}", file=sys.stderr)
        return 1

    OUT.parent.mkdir(parents=True, exist_ok=True)
    run(chrome, "--no-pdf-header-footer", f"--print-to-pdf={OUT}", SRC.as_uri())
    print(f"wrote {OUT.relative_to(ROOT)}  ({OUT.stat().st_size // 1024} KB)")

    overflow = check_overflow(chrome, SRC)
    if overflow:
        print(f"\n{len(overflow)} page(s) are losing content. Move something to the next page "
              f"or cut it.\nThe PDF was still written — look at it, but do not ship it.")

    if not args.images:
        return 1 if overflow else 0

    # Screenshot each page on its own: split the document into one file per <section>,
    # keeping <head> so the styles come along. Chromium's --screenshot only ever captures
    # the first viewport, so rendering the whole document and cropping is not an option.
    html = SRC.read_text(encoding="utf-8")
    head = html.split("<body>", 1)[0] + "<body>"
    sections = SECTION_RE.findall(html)
    shot_dir = pathlib.Path(args.shot_dir)
    shot_dir.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory() as tmp:
        for i, section in enumerate(sections, 1):
            one = pathlib.Path(tmp) / f"p{i:02d}.html"
            one.write_text(f"{head}\n{section}\n</body></html>", encoding="utf-8")
            run(chrome, "--hide-scrollbars",
                f"--window-size={PAGE_PX[0]},{PAGE_PX[1]}",
                f"--screenshot={shot_dir / f'page-{i:02d}.png'}", one.as_uri())

    print(f"{len(sections)} page image(s) in {shot_dir}")
    print("Look at every one. Clipped text does not raise an error — it just disappears.")
    return 1 if overflow else 0


if __name__ == "__main__":
    sys.exit(main())
