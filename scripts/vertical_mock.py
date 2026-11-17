"""Mockups for a vertical cut (human interventions 45: "Suggest options for a vertical cut"), 1080x1920, three moments
of the first chorus and hard stop 1 in two shapes:
  stacked      the made-up status page (O02's frame, every row green) on top, the 16:9 picture under it, the lyric big
  9:16 window  a window of the shot itself, moved to the action (here cropped from the 1080p frame and scaled up, so
               soft: the framing, not the sharpness; a real cut renders the window at 1080x1920)
with the strip YouTube Shorts covers (title and channel at the bottom, the buttons down the right) shaded.
Usage: .venv/bin/python -I scripts/vertical_mock.py <work dir> -> <work dir>/stacked_<t>.jpg, window_<t>.jpg and
       review/vertical/vertical_options.jpg (frames from the 40 master, archive/renders/m7/master/)
"""
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, "scripts")
import grade as G  # noqa: E402

S = Path(sys.argv[1])
VW, VH = 1080, 1920
BG = (11, 12, 14)
M = "archive/renders/m7/master/all-systems-operational-master_40.mp4"


def font(sz, w="Black"):
    f = ImageFont.truetype("remotion/public/fonts/WorkSans-VF.ttf", sz)
    f.set_variation_by_name(w)
    return f


def master(t):
    p = S / f"f_{t}.png"
    if not p.exists():
        import subprocess
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(t), "-i", M, "-frames:v", "1", str(p)], check=True)
    return Image.open(p).convert("RGB")


def raw(sub, k, t):
    im = cv2.imread(str(sorted(Path("renders/m7/frames", sub).glob("*.jpg"))[k]))
    im = G.grade(im, "grey", int(t * 30))
    return Image.fromarray(im[..., ::-1])


def caption(pil, y, lines, size=86):
    d = ImageDraw.Draw(pil)
    F = font(size)
    for ln in lines:
        d.text((VW // 2 - 40, y), ln, font=F, fill=(255, 255, 255), anchor="ma", stroke_width=9, stroke_fill=(0, 0, 0))
        y += int(size * 1.05)


def safe(pil):
    """Shorts' own UI, for reference: the title and channel strip at the bottom, the buttons down the right."""
    lay = Image.new("RGBA", pil.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    d.rectangle([0, VH - 360, VW, VH], fill=(255, 255, 255, 34))
    d.rectangle([VW - 130, VH - 1000, VW, VH - 360], fill=(255, 255, 255, 34))
    d.text((24, VH - 330), "Shorts UI", font=font(34, "SemiBold"), fill=(255, 255, 255, 140))
    return Image.alpha_composite(pil.convert("RGBA"), lay).convert("RGB")


STATUS = master(9.5).crop((170, 60, 1750, 640))           # the made-up status page: banner and the first rows


def stacked(t, lines):
    v = Image.new("RGB", (VW, VH), BG)
    st = STATUS.resize((VW, int(STATUS.height * VW / STATUS.width)), Image.LANCZOS)
    v.paste(st, (0, 150))
    pic = master(t).resize((VW, 608), Image.LANCZOS)
    v.paste(pic, (0, 150 + st.height + 40))
    caption(v, 150 + st.height + 40 + 608 + 50, lines)
    return safe(v)


def window(img, cx, lines, cap_y=1180):
    x0 = int(min(max(cx - 304, 0), 1920 - 608))
    v = img.crop((x0, 0, x0 + 608, 1080)).resize((VW, VH), Image.LANCZOS)
    caption(v, cap_y, lines)
    return safe(v)


moments = [
    ("chorus, wide", 61.5, ("O09a", 29), 840, ["ALL SYSTEMS", "OPERATIONAL"]),
    ("chorus, mid", 66.0, ("O09c", 38), 330, ["EVERY LIGHT", "IS GREEN"]),
    ("hard stop", 100.6, None, 960, ["WITHOUT FAI—"]),
]
cols = []
for name, t, rawk, cx, lines in moments:
    a = stacked(t, lines)
    b = window(raw(*rawk, t) if rawk else master(t), cx, lines)
    cols.append((name, a, b))
    a.save(S / f"stacked_{t}.jpg", quality=88)
    b.save(S / f"window_{t}.jpg", quality=88)
cw, ch = 300, 533
board = Image.new("RGB", (len(cols) * 2 * (cw + 16) + 16, ch + 110), (30, 30, 32))
d = ImageDraw.Draw(board)
for i, (name, a, b) in enumerate(cols):
    for j, (lab, im) in enumerate((("stacked", a), ("9:16 window", b))):
        x = 16 + (i * 2 + j) * (cw + 16)
        board.paste(im.resize((cw, ch), Image.LANCZOS), (x, 60))
        d.text((x, 18), f"{lab} · {name}", font=font(20, "SemiBold"), fill=(235, 235, 235))
Path("review/vertical").mkdir(parents=True, exist_ok=True)
board.save("review/vertical/vertical_options.jpg", quality=88)
print("review/vertical/vertical_options.jpg")
