"""The YouTube thumbnail (METADATA: not the real screenshot or the creator's photo): a frame of the live room (O03a, the
M7e render, graded grey), darkened toward the top, with the made-up status page's banner ("All systems operational",
its green, a check) and its stale stamp ("Last updated: Thu 11:15 a.m."). Work Sans (OFL, remotion/public/fonts).
The stamp sits on a dark backing (human interventions 38). Options from other frames: pass the frame's path, its
--look (scripts/grade.py), --gain and --banner top|bottom.
Usage: .venv/bin/python -I scripts/thumbnail.py [frame.png] [--frame 101] [--look grey] [--gain 1.0] [--banner top]
       [--crop x0,y0,x1,y1] [--out review/thumbnail/thumbnail.jpg]  (1280x720)
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
    ap.add_argument("src", nargs="?", default=None, help="a frame (PNG or JPEG); default O03a's --frame from the render")
    ap.add_argument("--frame", type=int, default=101)
    ap.add_argument("--look", default="grey")
    ap.add_argument("--gain", type=float, default=1.0, help="brighten the graded frame (thumbnails read small)")
    ap.add_argument("--banner", default="top", choices=("top", "bottom"))
    ap.add_argument("--crop", default="", help="x0,y0,x1,y1 as fractions of the frame (kept 16:9 by its width)")
    ap.add_argument("--out", default="review/thumbnail/thumbnail.jpg")
    a = ap.parse_args()
    if a.src is None:
        d0 = "renders/m7/frames/O03a"
        a.src = os.path.join(d0, sorted(os.listdir(d0))[a.frame - 1])
    im = cv2.imread(a.src, cv2.IMREAD_UNCHANGED)[:, :, :3]
    if a.crop:
        x0, y0, x1, _ = (float(v) for v in a.crop.split(","))
        hh, ww = im.shape[:2]
        cw = int((x1 - x0) * ww)
        ch = cw * 9 // 16
        X, Y = int(x0 * ww), int(y0 * hh)
        im = im[Y:Y + ch, X:X + cw]
    im = G.grade(im, a.look, 600)
    if a.gain != 1.0:
        im = (255 * ((im / 255.0) ** (1 / a.gain))).clip(0, 255).astype("uint8")
    im = cv2.resize(im, (1280, 720), interpolation=cv2.INTER_AREA)
    pil = Image.fromarray(im[..., ::-1]).convert("RGBA")
    top = a.banner == "top"
    grad = Image.new("L", (1280, 720), 0)
    gd = ImageDraw.Draw(grad)
    for k in range(320):                        # darkened toward the banner's edge of the frame
        gd.line([(0, k if top else 719 - k), (1280, k if top else 719 - k)], fill=int(150 * (1 - k / 320) ** 1.5))
    pil = Image.composite(Image.new("RGBA", (1280, 720), (8, 10, 12, 255)), pil, grad)
    F1, F2 = font(64, "Bold"), font(32, "SemiBold")
    text, stamp = "All systems operational", "Last updated: Thu 11:15 a.m."
    dd = ImageDraw.Draw(pil)
    tw, sw = dd.textlength(text, font=F1), dd.textlength(stamp, font=F2)
    x0, h, sh = 56, 112, 52
    w = int(tw + 170)
    y0 = 52 if top else 720 - 52 - h - 14 - sh
    ys = y0 + h + 14
    shadow = Image.new("RGBA", (1280, 720), (0, 0, 0, 0))
    ImageDraw.Draw(shadow).rounded_rectangle([x0 + 4, y0 + 10, x0 + w + 4, y0 + h + 10], 22, fill=(0, 0, 0, 140))
    pil = Image.alpha_composite(pil, shadow.filter(ImageFilter.GaussianBlur(10)))
    # the stamp on a dark backing (human interventions 38: "the contrast on the "last updated" is not great")
    back = Image.new("RGBA", (1280, 720), (0, 0, 0, 0))
    ImageDraw.Draw(back).rounded_rectangle([x0, ys, x0 + int(sw) + 36, ys + sh], 14, fill=(14, 16, 18, 215))
    pil = Image.alpha_composite(pil, back)
    d = ImageDraw.Draw(pil)
    d.rounded_rectangle([x0, y0, x0 + w, y0 + h], 22, fill=GREEN)
    cx, cy, r = x0 + 82, y0 + h // 2, 30
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(255, 255, 255, 255), width=6)
    d.line([(cx - 14, cy + 1), (cx - 4, cy + 12), (cx + 15, cy - 11)], fill=(255, 255, 255, 255), width=7, joint="curve")
    d.text((x0 + 126, cy), text, font=F1, fill=(255, 255, 255, 255), anchor="lm")
    d.text((x0 + 18, ys + sh // 2), stamp, font=F2, fill=(246, 244, 240, 255), anchor="lm")
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    pil.convert("RGB").save(a.out, quality=92)
    print(a.out, a.src)


if __name__ == "__main__":
    main()
