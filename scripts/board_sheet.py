"""Contact sheet of the M3 lighting board: every still in the board directory, in shot order, labelled with the shot ID
and its label (from blender/board.py's FRAMES, parsed as text so this runs without Blender). Adapted from Ever
Present's scripts/board_sheet.py (shot IDs O01-O24 plus suffixes, e.g. O08c).
Usage: .venv/bin/python -I scripts/board_sheet.py review/m3/board review/m3_board.jpg [cols=3]
"""
import re
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

src, out = Path(sys.argv[1]), Path(sys.argv[2])
cols = int(sys.argv[3]) if len(sys.argv) > 3 else 3
board = Path(__file__).resolve().parents[1] / "blender" / "board.py"
labels = dict(re.findall(r'\("(O\d\d[a-z]?)", "([^"]+)"', board.read_text()))
ids = [i for i in labels if (src / f"{i}.png").exists()]
tw, th, pad, cap = 640, 360, 8, 30
rows = -(-len(ids) // cols)
sheet = Image.new("RGB", (cols * (tw + pad) + pad, rows * (th + cap + pad) + pad), (18, 18, 20))
d = ImageDraw.Draw(sheet)
font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 15)
bold = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 17)
for k, sid in enumerate(ids):
    x, y = pad + (k % cols) * (tw + pad), pad + (k // cols) * (th + cap + pad)
    sheet.paste(Image.open(src / f"{sid}.png").convert("RGB").resize((tw, th), Image.LANCZOS), (x, y + cap))
    d.text((x + 2, y + 6), sid, font=bold, fill=(255, 255, 255))
    d.text((x + 62, y + 7), labels[sid], font=font, fill=(190, 190, 190))
sheet.save(out, quality=90)
print(out, len(ids), "stills")
