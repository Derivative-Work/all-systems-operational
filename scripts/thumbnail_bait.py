"""Louder thumbnail options (human interventions 41: "Give me more clickbait-adjacent thumbnail options"), beside
scripts/thumbnail.py's calm banner: big outlined type, a red arrow or ring, punchier colour, a face where the video has
one (the Little Switch, the probe). Every line is a lyric or a fact the video states; nothing ties AI to the cause; no
real logo, screenshot or face (METADATA: those stay in the bookend).
  E  "EVERYTHING IS FINE": the Switch straining on the lamppost box (O20i), the made-up status banner small
  F  "THE CHATBOT LOST ITS INBOX": the probe at the cafe, its "connector unavailable" sign ringed (O15a)
  G  "EVERY LIGHT IS GREEN": the server on the chroma green (O07a), ringed
  H  "503 / PLEASE STAY ON THE LINE": the ON AIR sign (O11g)
  I  "THE STATUS PAGE" vs "THE SERVERS": the made-up banner beside the treehouse dashboard, its 83% ringed (O18e)
Frames: the M7e render (renders/m7/frames/<sub>/), or 4K stills for the tight crops: blender -b --factory-startup
--python blender/coverage_m7.py -- --out <scratch> --still --at 0.2 --subs O20i,O15a --size 3840x2160, saved as
review/thumbnail/frames/O20i_4k_020.png and O15a_4k_020.png (git-ignored; log/render_logs/thumbnail_bait_stills.log).
Usage: .venv/bin/python -I scripts/thumbnail_bait.py [--stills review/thumbnail/frames] [--only E,F] [--out review/thumbnail]
       -> thumbnail_<X>_<name>.jpg (1280x720) and thumbnail_options_bait.jpg
"""
import argparse
import math
import os
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, "scripts")
import grade as G  # noqa: E402

W, H = 1280, 720
GREEN = (47, 158, 104, 255)                     # remotion/src/theme.ts ok
RED = (232, 44, 44, 255)
YELLOW = (255, 214, 10, 255)
WHITE = (255, 255, 255, 255)
INK = (8, 8, 10, 255)


def font(sz, w="Black"):
    f = ImageFont.truetype("remotion/public/fonts/WorkSans-VF.ttf", sz)
    f.set_variation_by_name(w)
    return f


def frame(sub, k, stills=None):
    """Frame k of a sub-shot: a 4K still from --stills if there is one, else the render."""
    if stills:
        for p in sorted(Path(stills).rglob(f"*{sub}*")):
            if p.suffix.lower() in (".png", ".jpg"):
                return cv2.imread(str(p), cv2.IMREAD_UNCHANGED)[:, :, :3]
    fs = sorted(Path("renders/m7/frames", sub).glob("*.jpg"))
    return cv2.imread(str(fs[k]))


def plate(im, crop, look, gain=1.0, sat=1.0, contrast=0.0):
    """Crop (x0, y0, width as fractions; 16:9), grade as the edit does, then brighten, saturate and add contrast for a
    small picture."""
    hh, ww = im.shape[:2]
    x0, y0, cw = crop
    cw = int(cw * ww)
    ch = cw * 9 // 16
    X, Y = int(x0 * ww), int(y0 * hh)
    im = im[Y:Y + ch, X:X + cw]
    if im.dtype == np.uint16:
        im = (im / 257).astype(np.uint8)
    im = cv2.resize(im, (1920, 1080), interpolation=cv2.INTER_AREA if cw >= 1920 else cv2.INTER_CUBIC)
    im = G.grade(im, look, 600)
    f = im.astype(np.float32) / 255.0
    if gain != 1.0:
        f = f ** (1 / gain)
    if contrast:
        f = f + contrast * (f - 0.5) * (1 - np.abs(2 * f - 1))      # an S-curve about mid grey
    hsv = cv2.cvtColor(np.clip(f, 0, 1), cv2.COLOR_BGR2HSV)
    hsv[..., 1] = np.clip(hsv[..., 1] * sat, 0, 1)
    f = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
    im = (np.clip(f, 0, 1) * 255).astype(np.uint8)
    im = cv2.resize(im, (W, H), interpolation=cv2.INTER_AREA)
    return Image.fromarray(im[..., ::-1]).convert("RGBA")


def shade(pil, side, depth=0.55, strength=190):
    """Darken toward one edge (top, bottom, left, right) so the type reads."""
    g = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(g)
    n = int((H if side in ("top", "bottom") else W) * depth)
    for k in range(n):
        v = int(strength * (1 - k / n) ** 1.6)
        if side == "top":
            d.line([(0, k), (W, k)], fill=v)
        elif side == "bottom":
            d.line([(0, H - 1 - k), (W, H - 1 - k)], fill=v)
        elif side == "left":
            d.line([(k, 0), (k, H)], fill=v)
        else:
            d.line([(W - 1 - k, 0), (W - 1 - k, H)], fill=v)
    return Image.composite(Image.new("RGBA", (W, H), (6, 6, 8, 255)), pil, g)


def words(pil, xy, lines, size, anchor="la", stroke=11, gap=0.92, shadow=True):
    """Lines of heavy type, each [(text, colour), ...], outlined in black with a soft drop shadow."""
    F = font(size)
    x, y = xy
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d, ds = ImageDraw.Draw(lay), ImageDraw.Draw(sh)
    for ln in lines:
        total = sum(d.textlength(t, font=F) for t, _ in ln)
        cx = x - total if anchor[0] == "r" else x - total / 2 if anchor[0] == "m" else x
        for t, c in ln:
            ds.text((cx + 6, y + 9), t, font=F, fill=(0, 0, 0, 200), stroke_width=stroke, stroke_fill=(0, 0, 0, 200))
            d.text((cx, y), t, font=F, fill=c, stroke_width=stroke, stroke_fill=INK)
            cx += d.textlength(t, font=F)
        y += int(size * gap)
    if shadow:
        pil = Image.alpha_composite(pil, sh.filter(ImageFilter.GaussianBlur(8)))
    return Image.alpha_composite(pil, lay)


def arrow(pil, p0, p1, width=34, head=78, colour=RED, bend=0.18):
    """A fat curved arrow from p0 to p1 (head at p1), outlined white, with a shadow."""
    (x0, y0), (x1, y1) = p0, p1
    mx, my = (x0 + x1) / 2, (y0 + y1) / 2
    nx, ny = -(y1 - y0), x1 - x0
    cx, cy = mx + nx * bend, my + ny * bend
    pts = []
    for i in range(41):
        t = i / 40
        pts.append(((1 - t) ** 2 * x0 + 2 * (1 - t) * t * cx + t * t * x1, (1 - t) ** 2 * y0 + 2 * (1 - t) * t * cy + t * t * y1))
    # stop the shaft short of the head
    ax, ay = pts[-1]
    bx, by = pts[-6]
    ang = math.atan2(ay - by, ax - bx)
    base = (ax - head * 0.8 * math.cos(ang), ay - head * 0.8 * math.sin(ang))
    shaft = [p for p in pts if math.hypot(p[0] - ax, p[1] - ay) > head * 0.7]
    tip = [(ax, ay), (base[0] + head * 0.62 * math.cos(ang + math.pi / 2), base[1] + head * 0.62 * math.sin(ang + math.pi / 2)),
           (base[0] + head * 0.62 * math.cos(ang - math.pi / 2), base[1] + head * 0.62 * math.sin(ang - math.pi / 2))]
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    for img, off, col, grow in ((sh, (6, 9), (0, 0, 0, 170), 10), (lay, (0, 0), WHITE, 10), (lay, (0, 0), colour, 0)):
        d = ImageDraw.Draw(img)
        s = [(px + off[0], py + off[1]) for px, py in shaft]
        d.line(s, fill=col, width=width + grow, joint="curve")
        r = (width + grow) / 2
        d.ellipse([s[0][0] - r, s[0][1] - r, s[0][0] + r, s[0][1] + r], fill=col)
        t = [(px + off[0], py + off[1]) for px, py in tip]
        if grow:
            c = (sum(p[0] for p in t) / 3, sum(p[1] for p in t) / 3)
            t = [(c[0] + (p[0] - c[0]) * 1.22, c[1] + (p[1] - c[1]) * 1.22) for p in t]
        d.polygon(t, fill=col)
    pil = Image.alpha_composite(pil, sh.filter(ImageFilter.GaussianBlur(6)))
    return Image.alpha_composite(pil, lay)


def ring(pil, box, width=12, colour=RED):
    """A hand-drawn-looking ring: two loose ellipse passes, outlined white."""
    x0, y0, x1, y1 = box
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    cx, cy, rx, ry = (x0 + x1) / 2, (y0 + y1) / 2, (x1 - x0) / 2, (y1 - y0) / 2
    for w, col in ((width + 8, WHITE), (width, colour)):
        for k, (s, e, j) in enumerate(((-100, 255, 1.0), (240, 300, 1.07))):
            pts = [(cx + rx * j * math.cos(math.radians(a)) * (1 + 0.03 * math.sin(a / 23)),
                    cy + ry * j * math.sin(math.radians(a))) for a in range(s, e + 1, 3)]
            d.line(pts, fill=col, width=w, joint="curve")
    return Image.alpha_composite(pil, lay)


def banner(pil, xy, scale=1.0):
    """The made-up status page's banner (scripts/thumbnail.py), at a scale."""
    x0, y0 = xy
    F1 = font(int(64 * scale), "Bold")
    text = "All systems operational"
    d = ImageDraw.Draw(pil)
    tw = d.textlength(text, font=F1)
    h = int(112 * scale)
    w = int(tw + 170 * scale)
    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(shadow).rounded_rectangle([x0 + 4, y0 + 10, x0 + w + 4, y0 + h + 10], int(22 * scale), fill=(0, 0, 0, 150))
    pil = Image.alpha_composite(pil, shadow.filter(ImageFilter.GaussianBlur(10)))
    d = ImageDraw.Draw(pil)
    d.rounded_rectangle([x0, y0, x0 + w, y0 + h], int(22 * scale), fill=GREEN)
    cx, cy, r = x0 + int(82 * scale), y0 + h // 2, int(30 * scale)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=WHITE, width=max(3, int(6 * scale)))
    d.line([(cx - 14 * scale, cy + 1 * scale), (cx - 4 * scale, cy + 12 * scale), (cx + 15 * scale, cy - 11 * scale)],
           fill=WHITE, width=max(3, int(7 * scale)), joint="curve")
    d.text((x0 + int(126 * scale), cy), text, font=F1, fill=WHITE, anchor="lm")
    return pil


def sticker(pil, centre, text, size, angle=-8, fill=RED, ink=WHITE, pad=(26, 10)):
    """A tilted label, like a sticker slapped on."""
    F = font(size)
    d0 = ImageDraw.Draw(Image.new("RGBA", (10, 10)))
    tw = d0.textlength(text, font=F)
    bw, bh = int(tw + 2 * pad[0]), int(size * 1.08 + 2 * pad[1])
    tile = Image.new("RGBA", (bw + 40, bh + 40), (0, 0, 0, 0))
    d = ImageDraw.Draw(tile)
    d.rounded_rectangle([20, 20, 20 + bw, 20 + bh], 14, fill=fill, outline=WHITE, width=6)
    d.text((20 + bw / 2, 20 + bh / 2 + size * 0.04), text, font=F, fill=ink, anchor="mm")
    tile = tile.rotate(angle, resample=Image.BICUBIC, expand=True)
    sh = Image.new("RGBA", tile.size, (0, 0, 0, 0))
    sh.paste((0, 0, 0, 170), mask=tile.split()[3])
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    x, y = int(centre[0] - tile.width / 2), int(centre[1] - tile.height / 2)
    lay.paste(sh.filter(ImageFilter.GaussianBlur(7)), (x + 6, y + 9), sh)
    pil = Image.alpha_composite(pil, lay)
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    lay.paste(tile, (x, y), tile)
    return Image.alpha_composite(pil, lay)


# ---------------------------------------------------------------- the options

def opt_E(st):
    p = plate(frame("O20i", 7, st), (0.165, 0.53, 0.44), "grey", gain=1.35, sat=1.25, contrast=0.35)
    p = shade(p, "left", 0.62, 215)
    p = words(p, (52, 150), [[("EVERYTHING", WHITE)], [("IS ", WHITE), ("FINE.", YELLOW)]], 118)
    p = banner(p, (52, 470), 0.62)
    return p


def opt_F(st):
    p = plate(frame("O15a", 32, st), (0.0, 0.0, 1.0), "cafe", gain=1.25, sat=1.2, contrast=0.3)
    p = shade(p, "top", 0.5, 220)
    p = words(p, (W // 2, 26), [[("THE CHATBOT", WHITE)], [("LOST ITS ", WHITE), ("INBOX", YELLOW)]], 104, anchor="ma")
    p = ring(p, (14, 352, 432, 650))
    p = arrow(p, (150, 214), (205, 338), width=26, head=60, bend=0.3)
    return p


def opt_G(st):
    p = plate(frame("O07a", 21, st), (0.07, 0.2, 0.86), "grey", gain=1.1, sat=1.55, contrast=0.2)
    p = shade(p, "bottom", 0.42, 120)
    p = ring(p, (330, 80, 1050, 455))
    p = words(p, (W // 2, 470), [[("EVERY LIGHT", WHITE)], [("IS ", WHITE), ("GREEN", (120, 255, 140, 255))]], 118, anchor="ma")
    p = sticker(p, (1130, 90), "IT'S FINE", 46, angle=8)
    return p


def opt_H(st):
    p = plate(frame("O11g", 9, st), (0.0, 0.08, 0.86), "grey", gain=1.1, sat=1.3, contrast=0.2)
    p = shade(p, "bottom", 0.5, 230)
    p = words(p, (W - 30, -22), [[("503", WHITE)]], 200, anchor="ra", stroke=13)
    p = words(p, (W // 2, 520), [[("PLEASE STAY", WHITE)], [("ON THE LINE", YELLOW)]], 92, anchor="ma")
    return p


def opt_I(st):
    left = Image.new("RGBA", (W, H), (16, 18, 20, 255))
    right = plate(cv2.imread("review/thumbnail/frames/O18e_000.png"), (0.30, 0.30, 0.52), "grey", gain=1.45, sat=1.35,
                  contrast=0.3)
    p = left.copy()
    mask = Image.new("L", (W, H), 0)
    ImageDraw.Draw(mask).polygon([(600, 0), (W, 0), (W, H), (520, H)], fill=255)
    p = Image.composite(right, p, mask)
    d = ImageDraw.Draw(p)
    d.line([(600, 0), (520, H)], fill=WHITE, width=10)
    p = banner(p, (34, 300), 0.5)
    p = words(p, (40, 70), [[("THE STATUS", WHITE)], [("PAGE", WHITE)]], 84, stroke=9)
    p = words(p, (W - 40, 70), [[("THE", WHITE)], [("SERVERS", YELLOW)]], 84, anchor="ra", stroke=9)
    p = ring(p, (690, 360, 1150, 640))
    p = sticker(p, (560, 560), "VS", 70, angle=-10, fill=INK, ink=WHITE)
    return p


OPTIONS = {"E": ("everything_is_fine", opt_E), "F": ("chatbot_inbox", opt_F), "G": ("every_light_green", opt_G),
           "H": ("503_on_air", opt_H), "I": ("status_vs_servers", opt_I)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stills", default="review/thumbnail/frames", help="4K stills, found by sub-shot name")
    ap.add_argument("--only", default="")
    ap.add_argument("--out", default="review/thumbnail")
    a = ap.parse_args()
    keys = a.only.split(",") if a.only else list(OPTIONS)
    made = []
    for k in keys:
        name, fn = OPTIONS[k]
        path = os.path.join(a.out, f"thumbnail_{k}_{name}.jpg")
        fn(a.stills).convert("RGB").save(path, quality=92)
        made.append((k, name, path))
        print(path)
    # the board: each at full size and at the size YouTube shows in a feed (360 wide)
    cell, small = 640, 240
    board = Image.new("RGB", (cell + small + 36, len(made) * (cell * 9 // 16 + 18) + 18), (24, 24, 26))
    d = ImageDraw.Draw(board)
    for i, (k, name, path) in enumerate(made):
        im = Image.open(path)
        y = 18 + i * (cell * 9 // 16 + 18)
        board.paste(im.resize((cell, cell * 9 // 16), Image.LANCZOS), (12, y))
        board.paste(im.resize((small, small * 9 // 16), Image.LANCZOS), (cell + 24, y))
        d.text((cell + 24, y + small * 9 // 16 + 10), f"{k}  {name}", font=font(18, "SemiBold"), fill=(230, 230, 230))
    out = os.path.join(a.out, "thumbnail_options_bait.jpg")
    board.save(out, quality=88)
    print(out)


if __name__ == "__main__":
    main()
