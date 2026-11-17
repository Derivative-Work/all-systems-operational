"""M7 check (human interventions 32: "particularly at "the agents that we hired", it's reading as shaky hands rather than
handheld"): how much each sub-shot's picture shakes, measured on the rendered frames.

For each sub-shot folder, the global shift between consecutive frames (phase correlation on 480x270 greyscale, with a
Hann window) gives the camera's path in pixels at 1920 wide. The path is split into a smooth part (a centred moving
average over --win frames, about 0.4 s: the drift and the planned move) and the rest (shake: what changes faster than
that). Reported per sub-shot: the shake's RMS and peak (px at 1920 wide), its RMS frame-to-frame velocity (px per
frame), and the smooth part's speed, sorted by shake. Moving subjects add to the measure; the closes on hands and
instruments read high for that reason, so read the numbers alongside the frames.
Usage: .venv/bin/python -I scripts/motion_check.py [--frames renders/m7/frames] [--subs O14b,O14c] [--win 13]
       [--out log/render_logs/m7_motion_check.json]
"""
import argparse
import json
from pathlib import Path

import cv2
import numpy as np

SCALE = 4.0  # 480 px analysed, reported at 1920


def path_of(files):
    win = None
    prev = None
    pts = [(0.0, 0.0)]
    resp = []
    for f in files:
        im = cv2.imread(str(f), cv2.IMREAD_GRAYSCALE)
        im = cv2.resize(im, (480, 270), interpolation=cv2.INTER_AREA).astype(np.float32)
        if win is None:
            win = cv2.createHanningWindow((480, 270), cv2.CV_32F)
        if prev is not None:
            (dx, dy), r = cv2.phaseCorrelate(prev, im, win)
            x, y = pts[-1]
            pts.append((x + dx * SCALE, y + dy * SCALE))
            resp.append(r)
        prev = im
    return np.array(pts), float(np.median(resp)) if resp else 0.0


def smooth(p, win):
    k = np.ones(win) / win
    pad = win // 2
    q = np.pad(p, ((pad, pad), (0, 0)), mode="edge")
    return np.stack([np.convolve(q[:, i], k, mode="valid") for i in range(2)], 1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--frames", default="renders/m7/frames")
    ap.add_argument("--subs", default="")
    ap.add_argument("--win", type=int, default=13)
    ap.add_argument("--out", default="log/render_logs/m7_motion_check.json")
    a = ap.parse_args()
    want = set(filter(None, a.subs.split(",")))
    rows = []
    for d in sorted(Path(a.frames).iterdir()):
        if not d.is_dir() or (want and d.name not in want):
            continue
        files = sorted(d.glob("[0-9]*.jpg"))
        if len(files) < a.win + 2:
            continue
        p, conf = path_of(files)
        s = smooth(p, a.win)
        sh = p - s
        v = np.diff(sh, axis=0)
        rows.append({"sub": d.name, "frames": len(files), "shake_rms_px": round(float(np.sqrt((sh ** 2).sum(1).mean())), 2),
                     "shake_peak_px": round(float(np.sqrt((sh ** 2).sum(1)).max()), 2),
                     "shake_vel_rms_px": round(float(np.sqrt((v ** 2).sum(1).mean())), 2),
                     "smooth_speed_px": round(float(np.sqrt((np.diff(s, axis=0) ** 2).sum(1)).mean()), 2),
                     "confidence": round(conf, 3)})
        print(json.dumps(rows[-1]), flush=True)
    rows.sort(key=lambda r: -r["shake_rms_px"])
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    json.dump({"generated_by": "scripts/motion_check.py", "win": a.win, "subs": rows}, open(a.out, "w"), indent=1)
    print("most shake:")
    for r in rows[:15]:
        print(f"  {r['sub']:6s} rms {r['shake_rms_px']:6.2f}  peak {r['shake_peak_px']:6.2f}  vel {r['shake_vel_rms_px']:5.2f}"
              f"  drift {r['smooth_speed_px']:5.2f} px/f  conf {r['confidence']:.2f}")


if __name__ == "__main__":
    main()
