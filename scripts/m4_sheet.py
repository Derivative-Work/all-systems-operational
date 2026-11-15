"""M4 contact sheet: every take of the given items, labelled with its id and the agent's keep/reject note.

New for this repository (layout after Ever Present's stills.py review_grid). Notes come from
config/m4_stills.json "review": {"<item>_s<seed>": "KEEP: ..." | "REJECT: ..." | "maybe: ..."}.
Usage: .venv/bin/python -I scripts/m4_sheet.py OUT.jpg ITEM [ITEM ...] [--cols 3] [--title "..."]
"""
import argparse
import json
import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("items", nargs="+")
    ap.add_argument("--cols", type=int, default=3)
    ap.add_argument("--cell", type=int, default=640)
    ap.add_argument("--title", default="")
    a = ap.parse_args()
    notes = json.load(open("config/m4_stills.json")).get("review", {})
    paths = [p for it in a.items for p in sorted(Path("assets/gen/stills", it).glob(f"{it}_s*.png"))]
    cw = a.cell
    ch = round(cw * 1088 / 1920)
    note_h, pad, top = 74, 10, 50
    rows = (len(paths) + a.cols - 1) // a.cols
    W = a.cols * (cw + pad) + pad
    H = top + rows * (ch + note_h + pad) + pad
    sheet = Image.new("RGB", (W, H), (16, 16, 18))
    d = ImageDraw.Draw(sheet)
    f, fb, ft = ImageFont.truetype(FONT, 15), ImageFont.truetype(BOLD, 17), ImageFont.truetype(BOLD, 22)
    d.text((pad, 14), a.title, fill=(255, 255, 255), font=ft)
    for k, p in enumerate(paths):
        x = pad + (k % a.cols) * (cw + pad)
        y = top + (k // a.cols) * (ch + note_h + pad)
        im = Image.open(p).convert("RGB")
        sheet.paste(im.resize((cw, ch), Image.LANCZOS), (x, y))
        note = notes.get(p.stem, "not reviewed")
        col = (120, 220, 120) if note.startswith("KEEP") else (255, 110, 100) if note.startswith("REJECT") \
            else (255, 210, 0)
        d.rectangle((x, y + ch, x + cw, y + ch + note_h), fill=(28, 28, 32))
        d.text((x + 6, y + ch + 4), p.stem, fill=col, font=fb)
        for i, line in enumerate(textwrap.wrap(note, 78)[:3]):
            d.text((x + 6, y + ch + 25 + i * 16), line, fill=(225, 225, 225), font=f)
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    sheet.save(a.out, quality=88)
    print(a.out, len(paths), "takes")


if __name__ == "__main__":
    main()
