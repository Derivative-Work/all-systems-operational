"""(Adapted from Ever Present's scripts/contact_sheet.py.) Tile PNG/JPG stills into one labelled contact sheet.

Usage: .venv/bin/python -I scripts/contact_sheet.py OUT.jpg IMG [IMG ...] [--cols 8] [--cell 420]
Transparent images are shown over a grey checkerboard so their alpha is visible.
"""
import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


def checker(size, sq=16):
    im = Image.new("RGB", size, (150, 150, 150))
    d = ImageDraw.Draw(im)
    for y in range(0, size[1], sq):
        for x in range(0, size[0], sq):
            if (x // sq + y // sq) % 2:
                d.rectangle([x, y, x + sq - 1, y + sq - 1], fill=(115, 115, 115))
    return im


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("images", nargs="+")
    ap.add_argument("--cols", type=int, default=8)
    ap.add_argument("--cell", type=int, default=420)
    a = ap.parse_args()
    cell, label_h, pad = a.cell, 34, 10
    rows = (len(a.images) + a.cols - 1) // a.cols
    sheet = Image.new("RGB", (a.cols * (cell + pad) + pad, rows * (cell + label_h + pad) + pad), (24, 24, 26))
    draw = ImageDraw.Draw(sheet)
    try:
        font = ImageFont.truetype("DejaVuSans.ttf", 18)
    except OSError:
        font = ImageFont.load_default()
    for i, p in enumerate(a.images):
        im = Image.open(p)
        im.thumbnail((cell, cell), Image.LANCZOS)
        if im.mode in ("RGBA", "LA", "P"):
            im = im.convert("RGBA")
            bg = checker(im.size)
            bg.paste(im, (0, 0), im)
            im = bg
        else:
            im = im.convert("RGB")
        r, c = divmod(i, a.cols)
        x0 = pad + c * (cell + pad)
        y0 = pad + r * (cell + label_h + pad)
        sheet.paste(im, (x0 + (cell - im.width) // 2, y0 + (cell - im.height) // 2))
        draw.text((x0 + 4, y0 + cell + 6), Path(p).stem, fill=(225, 225, 225), font=font)
    sheet.save(a.out, quality=90)
    print(a.out, sheet.size)


if __name__ == "__main__":
    main()
