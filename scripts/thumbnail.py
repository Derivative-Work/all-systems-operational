"""The YouTube thumbnail (METADATA: not the real screenshot or the creator's photo): a frame of the live room (O03a, the
M7e render, graded grey), darkened toward the top, with the made-up status page's banner ("All systems operational",
its green, a check) and its stale stamp ("Last updated: Thu 11:15 a.m."). Work Sans (OFL, remotion/public/fonts).
Usage: .venv/bin/python -I scripts/thumbnail.py [--frame 101] [--out review/thumbnail/thumbnail.jpg]  (1280x720)
"""
import argparse
import os
import sys

import cv2
from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, "scripts")
import grade as G  # noqa: E402

GREEN = (47, 158, 104, 255)                     # remotion/src/theme.ts ok


def font(sz, w):
    f = ImageFont.truetype("remotion/public/fonts/WorkSans-VF.ttf", sz)
    f.set_variation_by_name(w)
    return f


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--frame", type=int, default=101)
    ap.add_argument("--out", default="review/thumbnail/thumbnail.jpg")
    a = ap.parse_args()
    d0 = "renders/m7/frames/O03a"
    src = os.path.join(d0, sorted(os.listdir(d0))[a.frame - 1])
    im = cv2.resize(G.grade(cv2.imread(src), "grey", 600), (1280, 720), interpolation=cv2.INTER_AREA)
    pil = Image.fromarray(im[..., ::-1]).convert("RGBA")
    grad = Image.new("L", (1280, 720), 0)
    gd = ImageDraw.Draw(grad)
    for y in range(320):
        gd.line([(0, y), (1280, y)], fill=int(150 * (1 - y / 320) ** 1.5))
    pil = Image.composite(Image.new("RGBA", (1280, 720), (8, 10, 12, 255)), pil, grad)
    F1, F2 = font(64, "Bold"), font(30, "Medium")
    text = "All systems operational"
    tw = ImageDraw.Draw(pil).textlength(text, font=F1)
    x0, y0, h = 56, 52, 112
    w = int(tw + 170)
    shadow = Image.new("RGBA", (1280, 720), (0, 0, 0, 0))
    ImageDraw.Draw(shadow).rounded_rectangle([x0 + 4, y0 + 10, x0 + w + 4, y0 + h + 10], 22, fill=(0, 0, 0, 140))
    pil = Image.alpha_composite(pil, shadow.filter(ImageFilter.GaussianBlur(10)))
    d = ImageDraw.Draw(pil)
    d.rounded_rectangle([x0, y0, x0 + w, y0 + h], 22, fill=GREEN)
    cx, cy, r = x0 + 82, y0 + h // 2, 30
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(255, 255, 255, 255), width=6)
    d.line([(cx - 14, cy + 1), (cx - 4, cy + 12), (cx + 15, cy - 11)], fill=(255, 255, 255, 255), width=7, joint="curve")
    d.text((x0 + 126, cy), text, font=F1, fill=(255, 255, 255, 255), anchor="lm")
    d.text((x0 + 6, y0 + h + 22), "Last updated: Thu 11:15 a.m.", font=F2, fill=(236, 234, 230, 235), anchor="la")
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    pil.convert("RGB").save(a.out, quality=92)
    print(a.out, src)


if __name__ == "__main__":
    main()
