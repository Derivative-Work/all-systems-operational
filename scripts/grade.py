"""M7 grade: one display-referred grade for the rendered frames, applied after Blender (AgX, config/aso_look.json) as a
reproducible, logged step (plan M7; the M7a look board, production log 30+). Same for every set but the cafe's
warmth and O22's home movie (brief, O22: "From 'Remember Wednesday' on, the picture takes soft film grain and a warm
grade, like a home movie; everything before stays in grey daylight").

Looks:
  grey     live room, treehouse, park: Seattle grey daylight: a little desaturated, cool slate in the shadows, a soft
           shoulder, blacks lifted just off zero, a light vignette;
  cafe     the same, warmer in the mids and shadows (string lights, wood, brick) and a touch more saturated, the
           windows' highlights left grey daylight;
  home     O22 from "Remember Wednesday": warm and faded (lifted, low-contrast blacks), softer, a halation glow round
           the highlights, a stronger vignette and soft film grain (seeded: config/seeds.json main + the frame number);
  instant  the cafe Polaroid's photo (blender/polaroid_m7.py): warm, faded, a cyan cast in the shadows, soft.
Input: 8- or 16-bit PNG/JPEG (BGR, as OpenCV reads it). Output: 8-bit.
Usage: .venv/bin/python -I scripts/grade.py --look grey in.png out.png [--frame N]
       .venv/bin/python -I scripts/grade.py --look grey --dir in_dir out_dir   (every PNG/JPG; frame = file number)
"""
import argparse
import json
from pathlib import Path

import cv2
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SEEDS = json.loads((ROOT / "config" / "seeds.json").read_text())

LOOKS = {
    "grey": dict(wb=(1.0, 1.0, 1.0), sat=0.84, curve=0.18, lift=0.016, shadow=(-0.006, 0.0, 0.012),
                 high=(0.004, 0.0, -0.004), mid=(0.0, 0.0, 0.0), vignette=0.22, soft=0.0, halation=0.0, grain=0.0),
    "cafe": dict(wb=(1.0, 1.0, 1.0), sat=0.92, curve=0.16, lift=0.018, shadow=(0.012, 0.004, -0.006),
                 high=(-0.004, 0.0, 0.008), mid=(0.035, 0.012, -0.03), vignette=0.25, soft=0.0, halation=0.0, grain=0.0),
    "home": dict(wb=(1.13, 1.0, 0.8), sat=0.74, curve=-0.05, lift=0.07, shadow=(0.018, 0.006, -0.012),
                 high=(0.02, 0.006, -0.03), mid=(0.0, 0.0, 0.0), vignette=0.38, soft=0.9, halation=0.22, grain=0.02),
    "instant": dict(wb=(1.12, 1.02, 0.84), sat=0.8, curve=0.05, lift=0.08, shadow=(-0.01, 0.012, 0.02),
                    high=(0.03, 0.01, -0.03), mid=(0.0, 0.0, 0.0), vignette=0.3, soft=0.8, halation=0.15, grain=0.012),
}


def grade(img, look, frame=0):
    """img: uint8 or uint16 BGR -> uint8 BGR."""
    L = LOOKS[look]
    x = img.astype(np.float32) / (65535.0 if img.dtype == np.uint16 else 255.0)
    x = x[:, :, ::-1]                                                        # RGB
    h, w = x.shape[:2]
    if L["soft"]:
        k = max(1, int(round(L["soft"] * h / 1080)))
        x = cv2.GaussianBlur(x, (0, 0), k * 0.6)
    if L["halation"]:
        hi = np.clip((x - 0.7) / 0.3, 0, 1)
        glow = cv2.GaussianBlur(hi, (0, 0), h / 60)
        x = x + L["halation"] * glow * np.array([1.0, 0.75, 0.55], np.float32)
    x = x * np.array(L["wb"], np.float32)
    y = x @ np.array([0.2126, 0.7152, 0.0722], np.float32)
    x = y[..., None] + L["sat"] * (x - y[..., None])
    x = np.clip(x, 0, 1)
    s = x * x * (3 - 2 * x)                                                  # soft S (curve > 0) or flatter (< 0)
    x = x + L["curve"] * (s - x)
    y = (x @ np.array([0.2126, 0.7152, 0.0722], np.float32))[..., None]
    x = x + np.array(L["shadow"], np.float32) * (1 - y) ** 2 + np.array(L["high"], np.float32) * y ** 2 \
        + np.array(L["mid"], np.float32) * 4 * y * (1 - y)
    x = L["lift"] + (1 - L["lift"]) * x
    if L["vignette"]:
        yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
        r2 = ((xx - w / 2) / (w / 2)) ** 2 * 0.6 + ((yy - h / 2) / (h / 2)) ** 2 * 0.4
        x = x * (1 - L["vignette"] * np.clip(r2, 0, 1.5) ** 1.5)[..., None]
    if L["grain"]:
        rng = np.random.default_rng([SEEDS["main"], int(frame)])
        g = rng.normal(0, 1, (h, w)).astype(np.float32)
        g = cv2.GaussianBlur(g, (0, 0), 0.7 * h / 1080 + 0.3)
        g /= g.std() + 1e-6
        y = (x @ np.array([0.2126, 0.7152, 0.0722], np.float32))[..., None]
        x = x + L["grain"] * g[..., None] * (0.35 + 0.65 * np.sqrt(np.clip(y, 0, 1)) * (1 - 0.5 * y))
    x = np.clip(x, 0, 1)[:, :, ::-1]
    return (x * 255 + 0.5).astype(np.uint8)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--look", required=True, choices=sorted(LOOKS))
    ap.add_argument("--frame", type=int, default=0)
    ap.add_argument("--dir", action="store_true")
    ap.add_argument("src")
    ap.add_argument("dst")
    a = ap.parse_args()
    if a.dir:
        Path(a.dst).mkdir(parents=True, exist_ok=True)
        files = sorted(p for p in Path(a.src).iterdir() if p.suffix.lower() in (".png", ".jpg"))
        for p in files:
            im = cv2.imread(str(p), cv2.IMREAD_UNCHANGED)
            fr = int(p.stem) if p.stem.isdigit() else 0
            cv2.imwrite(str(Path(a.dst) / (p.stem + ".png")), grade(im[:, :, :3], a.look, fr))
        print(f"{a.dst}: {len(files)} frames graded ({a.look})")
    else:
        im = cv2.imread(a.src, cv2.IMREAD_UNCHANGED)
        cv2.imwrite(a.dst, grade(im[:, :, :3], a.look, a.frame))
        print(f"{a.dst}: graded ({a.look}, frame {a.frame})")


if __name__ == "__main__":
    main()
