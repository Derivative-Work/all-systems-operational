"""M1b review sheet: the v1.3 bridge in O18 at the M7 look (blender/m1b_o18.py stills, graded) with the denial tags
composited from renders/m1b/remotion/M7-O18-DenialTags.mov, the whiteboard texture in full, the fact card and the
status pages' stamp.
Usage: .venv/bin/python -I scripts/m1b_sheet.py  -> review/m1b_o18.jpg
"""
import subprocess
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

TILE = (960, 540)
FONT = ImageFont.truetype("remotion/public/fonts/Inter-VF.ttf", 22) if Path("remotion/public/fonts/Inter-VF.ttf").exists() \
    else ImageFont.load_default()
# sub-shot, frame of O18 its still shows (the sub-shot's middle: coverage.py --still --at 0.5)
SUBS = [("O18a", 72, "O18a wide: 'Root cause' written in"), ("O18b", 216, "O18b board mid: the July fix circled; contributing factors"),
        ("O18c", 360, "O18c side wide: both denial tags, pinned to the board's quote line"),
        ("O18d", 468, "O18d board close: the full board; the panel sits lower here")]


def tagged(sub, f, tmp):
    bg = Image.open(f"renders/m1b/graded/{sub}.png").convert("RGBA")
    png = Path(tmp) / f"tags-{f}.png"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", "renders/m1b/remotion/M7-O18-DenialTags.mov", "-vf",
                    f"select=eq(n\\,{f})", "-vsync", "0", "-frames:v", "1", "-pix_fmt", "rgba", str(png)], check=True)
    bg.alpha_composite(Image.open(png).convert("RGBA"))
    return bg.convert("RGB")


def fit(im):
    im = im.convert("RGB")
    im.thumbnail(TILE)
    out = Image.new("RGB", TILE, (24, 24, 26))
    out.paste(im, ((TILE[0] - im.width) // 2, (TILE[1] - im.height) // 2))
    return out


with tempfile.TemporaryDirectory() as tmp:
    tiles = [(fit(tagged(s, f, tmp)), cap) for s, f, cap in SUBS]
stamp = Image.open("review/m1b/O02-StatusPage.png").crop((200, 300, 1160, 840))
tiles += [(fit(Image.open("review/m1b/board-full.png")), "the v1.3 whiteboard texture, full (2400x1500)"),
          (fit(Image.open("review/m1b/FactCard.png")), "fact card: the brief's text (rev 141), verbatim"),
          (fit(stamp), "status page rows: 'Last updated: Thu 11:15 a.m.' (O02, O23)")]
cols, cap_h = 2, 40
rows = (len(tiles) + cols - 1) // cols
sheet = Image.new("RGB", (cols * TILE[0] + (cols + 1) * 10, rows * (TILE[1] + cap_h) + (rows + 1) * 10), (24, 24, 26))
d = ImageDraw.Draw(sheet)
for i, (im, cap) in enumerate(tiles):
    x, y = 10 + (i % cols) * (TILE[0] + 10), 10 + (i // cols) * (TILE[1] + cap_h + 10)
    sheet.paste(im, (x, y))
    d.text((x + 4, y + TILE[1] + 8), cap, fill=(230, 230, 230), font=FONT)
sheet.save("review/m1b_o18.jpg", quality=88)
print("review/m1b_o18.jpg", sheet.size)
