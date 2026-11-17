"""Louder thumbnail options (human interventions 41: "Give me more clickbait-adjacent thumbnail options"), beside
scripts/thumbnail.py's calm banner: big outlined type, a red arrow or ring, punchier colour, a face where the video has
one (the Little Switch, the probe). Every line is a lyric or a fact the video states; nothing ties AI to the cause; no
real logo, screenshot or face (METADATA: those stay in the bookend).
  E  "EVERYTHING IS FINE": the Switch straining on the lamppost box (O20i), the made-up status banner small
  F  "THE CHATBOT LOST ITS INBOX": the probe at the cafe, its "connector unavailable" sign ringed (O15a)
  G  "EVERY LIGHT IS GREEN": the server on the chroma green (O07a), ringed
  H  "503 / PLEASE STAY ON THE LINE": the ON AIR sign (O11g)
  I  "THE STATUS PAGE" vs "THE SERVERS": the made-up banner beside the treehouse dashboard, its 83% ringed (O18e)
Human interventions 42, "the web of lights or dashboards" (board: --only J,K,L,M,N,P,Q --board thumbnail_options_web.jpg):
  J  "EVERYTHING IS WIRED TO EVERYTHING": the cafe's string lights with only the hub bulb out, ringed (O16a frame 22)
  K  "AND EVERYTHING IS GONE.": the dark running out from the hub, the type in the hole (O16a frame 24)
  L  the made-up "All systems operational" banner across the web lit (frame 21) and out (frame 32)
  M  "WIRED TO EVERYTHING": the web beside the night dashboard
Human interventions 43 ("more light for the wire to be visible ... use just the screens"): J-M from the string lights
rendered again with more light (blender/thumbnail_m7.py); the treehouse's screens flat, close together (O is skipped:
it reads as a shot number):
  N  "SOME USERS MAY BE EXPERIENCING": the dashboard beside the terminal, the alert ringing in front, the pool ringed
  P  the made-up "All systems operational" banner over the dashboard, its red gateway pool ringed
  Q  "WE ARE AWARE.": the dashboard, terminal, ringing alert and timed-out sign-in in a pile
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


# human interventions 42: "Try options that have the web of lights or dashboards". The cafe's string lights (O16a: the
# hub bulb goes out on frame 22, the dark runs down the strands from 23, all out by 28) and the treehouse dashboard at
# night (O08c, on "Some users may / be experiencing"). 4K stills at those frames (git-ignored, review/thumbnail/frames/
# O16a_4k_f<N>.png, O08c_4k_f36.png; log/render_logs/thumbnail_web_stills.log), else the 1080p render. Human
# interventions 43 ("more light for the wire to be visible"): the string lights again by blender/thumbnail_m7.py, the
# strands thicker, exposure +2.5 stops with the bulbs at 0.18 and their point lights at 6x (O16a_lit_4k_f<N>.png;
# log/render_logs/thumbnail_web_lit.log).

def at(sub, k, stills, tag=""):
    """Frame k (1-based, as the render numbers them) of a sub-shot: the 4K still if there is one, else the render."""
    p = Path(stills or "review/thumbnail/frames", f"{sub}{tag}_4k_f{k}.png")
    if p.exists():
        return cv2.imread(str(p), cv2.IMREAD_UNCHANGED)[:, :, :3]
    return cv2.imread(str(Path("renders/m7/frames", sub, f"{k:04d}.jpg")))


def opt_J(st):
    """The one bulb out: the hub dark, every strand still lit."""
    p = plate(at("O16a", 22, st, LIT), WEB_CROP, "cafe", gain=1.15, sat=1.25, contrast=0.3)
    p = shade(p, "bottom", 0.42, 235)
    p = ring(p, HUB_RING)
    p = words(p, (W // 2, 498), [[("EVERYTHING IS WIRED", WHITE)], [("TO ", WHITE), ("EVERYTHING", YELLOW)]], 92,
              anchor="ma")
    return p


def opt_K(st):
    """The dark running down the strands from the hub, the type in the hole it leaves."""
    p = plate(at("O16a", 24, st, LIT), WEB_CROP, "cafe", gain=1.15, sat=1.25, contrast=0.3)
    p = words(p, (W // 2, 214), [[("AND EVERYTHING", WHITE)], [("IS ", WHITE), ("GONE.", YELLOW)]], 118, anchor="ma")
    return p


def opt_L(st):
    """The web lit on the left, out on the right, the made-up status banner across the seam."""
    lit = plate(at("O16a", 21, st, LIT), WEB_CROP, "cafe", gain=1.15, sat=1.25, contrast=0.3)
    out = plate(at("O16a", 32, st, LIT), WEB_CROP, "cafe", gain=0.75, sat=1.1, contrast=0.3)     # the power off
    mask = Image.new("L", (W, H), 0)
    ImageDraw.Draw(mask).polygon([(700, 0), (W, 0), (W, H), (580, H)], fill=255)
    p = Image.composite(out, lit, mask)
    ImageDraw.Draw(p).line([(700, 0), (580, H)], fill=WHITE, width=10)
    p = banner(p, (130, 300), 1.0)
    return p


# human interventions 43: "...or put computers and phones closer together or use just the screens without them". The
# treehouse's screens as Remotion renders them for the Blender textures (remotion/src/components/TreehouseScreens.tsx),
# flat at twice their size: npx remotion still M7-Tree-<Screen>-night <png> --frame=<f> --scale=<2 laptop, 1 phone>
# (Dashboard 66, Terminal 60, AlertCall 20, TwoFactor 40), in review/thumbnail/frames/screens/ (git-ignored); set
# close together in a bezel, with a little perspective and their own glow, over the treehouse at night out of focus.
SCREENS = Path("review/thumbnail/frames/screens")


def device(name, kind):
    """A screen in a dark bezel with rounded corners (RGBA) and the bezel's width."""
    img = Image.open(SCREENS / f"{name}.png").convert("RGBA")
    w, h = img.size
    b, r = (int(0.03 * w), int(0.028 * w)) if kind == "laptop" else (int(0.045 * w), int(0.14 * w))
    dev = Image.new("RGBA", (w + 2 * b, h + 2 * b), (0, 0, 0, 0))
    ImageDraw.Draw(dev).rounded_rectangle([0, 0, w + 2 * b - 1, h + 2 * b - 1], r, fill=(12, 13, 15, 255),
                                          outline=(64, 66, 72, 255), width=max(3, b // 7))
    m = Image.new("L", (w, h), 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, w - 1, h - 1], max(6, r - b), fill=255)
    dev.paste(img, (b, b), m)
    return dev, b


def place(pil, name, kind, quad, glow=0.45):
    """A screen warped onto quad (top left, top right, bottom right, bottom left) with a drop shadow and a glow; returns
    the picture and a function from the screen's own pixels to the thumbnail's."""
    dev, b = device(name, kind)
    side = max(math.dist(quad[0], quad[1]), math.dist(quad[3], quad[2]))
    s = min(1.0, 1.4 * side / dev.width)
    dev = dev.resize((int(dev.width * s), int(dev.height * s)), Image.LANCZOS)
    w, h = dev.size
    M = cv2.getPerspectiveTransform(np.float32([[0, 0], [w, 0], [w, h], [0, h]]), np.float32(quad))
    a = cv2.warpPerspective(np.array(dev), M, (W, H), flags=cv2.INTER_CUBIC, borderValue=(0, 0, 0, 0))
    lay = Image.fromarray(a, "RGBA")
    alpha = lay.split()[3]
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sh.paste((0, 0, 0, 200), (10, 18), alpha)
    pil = Image.alpha_composite(pil, sh.filter(ImageFilter.GaussianBlur(14)))
    if glow:
        g = lay.convert("RGB").filter(ImageFilter.GaussianBlur(46))
        base = np.asarray(pil.convert("RGB"), np.float32)
        add = np.asarray(g, np.float32) * glow
        pil = Image.fromarray(np.clip(255 - (255 - base) * (255 - add) / 255, 0, 255).astype(np.uint8)).convert("RGBA")
    pil = Image.alpha_composite(pil, lay)

    def to(x, y):
        p = M @ np.array([(x + b) * s, (y + b) * s, 1.0])
        return p[0] / p[2], p[1] / p[2]
    return pil, to


def night_room(st, blur=18, dark=0.45):
    """The treehouse at night (O08c), out of focus and dimmed, as a backdrop."""
    p = plate(at("O08c", 36, st), (0.25, 0.1, 0.75), "grey", gain=1.2, sat=1.2)
    p = p.filter(ImageFilter.GaussianBlur(blur))
    return Image.blend(Image.new("RGBA", (W, H), (4, 5, 7, 255)), p, dark)


def box_of(to, x0, y0, x1, y1, pad=14):
    pts = [to(x0, y0), to(x1, y0), to(x1, y1), to(x0, y1)]
    return (min(p[0] for p in pts) - pad, min(p[1] for p in pts) - pad, max(p[0] for p in pts) + pad,
            max(p[1] for p in pts) + pad)


def opt_M(st):
    """Split: the string lights on the left, the dashboard (flat) on the right."""
    left = plate(at("O16a", 21, st, LIT), WEB_CROP, "cafe", gain=1.0, sat=1.2, contrast=0.25)
    right = night_room(st)
    right, to = place(right, "Dashboard-night", "laptop", [(632, 214), (1262, 198), (1268, 612), (604, 636)], glow=0.4)
    mask = Image.new("L", (W, H), 0)
    ImageDraw.Draw(mask).polygon([(640, 0), (W, 0), (W, H), (560, H)], fill=255)
    p = Image.composite(right, left, mask)
    ImageDraw.Draw(p).line([(640, 0), (560, H)], fill=WHITE, width=10)
    p = words(p, (36, 30), [[("WIRED TO", WHITE)], [("EVERYTHING", YELLOW)]], 84, stroke=9)
    return p


def opt_N(st):
    """The dashboard and the terminal side by side, the alert ringing in front: "SOME USERS MAY BE EXPERIENCING"."""
    p = night_room(st)
    p, _ = place(p, "Terminal-night", "laptop", [(26, 250), (520, 232), (530, 560), (20, 580)], glow=0.3)
    p, to = place(p, "Dashboard-night", "laptop", [(400, 214), (1150, 238), (1140, 700), (392, 712)])
    p, _ = place(p, "AlertCall-night", "phone", [(1048, 300), (1262, 318), (1236, 776), (1016, 760)], glow=0.25)
    p = ring(p, box_of(to, 120, 800, 1700, 1360, pad=8))
    p = words(p, (W // 2, 14), [[("SOME USERS MAY", WHITE)], [("BE ", WHITE), ("EXPERIENCING", YELLOW)]], 92,
              anchor="ma")
    return p


def opt_P(st):
    """The dashboard close, nearly full frame, under the made-up "All systems operational" banner."""
    p = night_room(st)
    p, to = place(p, "Dashboard-night", "laptop", [(70, 150), (1230, 120), (1250, 860), (52, 880)], glow=0.35)
    p = banner(p, (130, 28), 1.0)
    p = ring(p, box_of(to, 120, 800, 1700, 1360, pad=8))
    return p


def opt_Q(st):
    """Laptops and phones in a pile, all failing at once: "WE ARE AWARE."."""
    p = night_room(st)
    p, _ = place(p, "Terminal-night", "laptop", [(560, 40), (1250, 80), (1236, 500), (548, 470)], glow=0.25)
    p, to = place(p, "Dashboard-night", "laptop", [(250, 250), (930, 228), (944, 660), (240, 700)])
    p, _ = place(p, "TwoFactor-night", "phone", [(36, 280), (240, 260), (282, 700), (64, 726)], glow=0.25)
    p, _ = place(p, "AlertCall-night", "phone", [(960, 330), (1160, 350), (1130, 790), (920, 774)], glow=0.25)
    p = words(p, (40, 22), [[("WE ARE ", WHITE), ("AWARE.", YELLOW)]], 120)
    return p


WEB_CROP = (0.0, 0.0, 1.0)
HUB_RING = (560, 240, 720, 380)
LIT = "_lit"

OPTIONS = {"E": ("everything_is_fine", opt_E), "F": ("chatbot_inbox", opt_F), "G": ("every_light_green", opt_G),
           "H": ("503_on_air", opt_H), "I": ("status_vs_servers", opt_I), "J": ("wired_to_everything", opt_J),
           "K": ("everything_is_gone", opt_K), "L": ("lights_out_operational", opt_L),
           "M": ("lights_vs_dashboard", opt_M), "N": ("screens_some_users", opt_N),
           "P": ("screens_dashboard_operational", opt_P), "Q": ("screens_we_are_aware", opt_Q)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stills", default="review/thumbnail/frames", help="4K stills, found by sub-shot name")
    ap.add_argument("--only", default="")
    ap.add_argument("--out", default="review/thumbnail")
    ap.add_argument("--board", default="thumbnail_options_bait.jpg")
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
    out = os.path.join(a.out, a.board)
    board.save(out, quality=88)
    print(out)


if __name__ == "__main__":
    main()
