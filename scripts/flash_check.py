"""Photosensitivity check (human interventions 32: "The "ON AIR" flicker is far too fast -- I don't want this to be an
epilepsy risk"): general and red flashes in a video, against WCAG 2.3.1's thresholds (after ITU-R BT.1702 and
Ofcom's guidance), approximated in the way automated checkers do. Not a certified test (PEAT or a Harding test is,
and the master should go through one); it finds what to fix.

- The video is read at 256x144. Per pixel, relative luminance Y (sRGB linearised, Rec. 709 weights) and a
  transition each time Y swings by at least 0.1 (10% of the maximum) against the last turning point, in the
  opposite direction from the last transition, with the darker side under 0.8.
- Concurrency (WCAG: "the combined area of flashes occurring concurrently"): in each 10-degree field (a third of the
  width by a third of the height of the screen, at the viewing distance the guidance assumes; fields every 4 px), a
  field transition happens when a quarter or more of its pixels made a transition the same way within the last
  three frames (0.1 s). Moving texture (branches crossing a bright sky) changes pixels both ways at once and
  doesn't add up; a light or a cut does.
- Two opposing field transitions are a flash; a frame fails where a field has had 7 or more (more than three
  flashes) in the last second.
- Red flashes: the same, on the saturated-red share (R / (R + G + B) >= 0.8, its change at least 20 points).
Writes every failing frame's time and area to --out (JSON) and prints the failing spans.
Usage: .venv/bin/python -I scripts/flash_check.py review/m7_cut_v2.mp4 [--out log/render_logs/m7_flash_check.json]
       [--from-s 0] [--to-s 0]
"""
import argparse
import json
import subprocess
from pathlib import Path

import numpy as np

W, H, FPS = 256, 144, 30
FIELD = (H // 3, W // 3)            # a 10-degree field: a third of the height, a third of the width
STEP, DARK, RED, RED_STEP = 0.10, 0.80, 0.80, 0.20
LIMIT = 7                           # transitions in one second: more than three flashes


def lin(c):
    c = c.astype(np.float32) / 255.0
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


class Pixels:
    """Per pixel, alternating transitions; returns this frame's new transitions, + and -."""

    def __init__(self, step, dark=None):
        self.step, self.dark = step, dark
        self.ref = None
        self.sign = np.zeros((H, W), np.int8)

    def add(self, v):
        if self.ref is None:
            self.ref = v.copy()
            return np.zeros((H, W), bool), np.zeros((H, W), bool)
        d = v - self.ref
        s = np.sign(d).astype(np.int8)
        big = np.abs(d) >= self.step
        if self.dark is not None:
            big &= np.minimum(v, self.ref) < self.dark
        new = big & (s != self.sign)
        same = (s == self.sign) & (s != 0)       # further the same way as the last transition: follow the extreme
        self.ref = np.where(new | same, v, self.ref)
        self.sign = np.where(new, s, self.sign)
        return new & (s > 0), new & (s < 0)


def field_shares(mask):
    """The share of each 10-degree field (every 4 px) covered by the mask (box sums on an integral image)."""
    ii = np.pad(mask.astype(np.int32).cumsum(0).cumsum(1), ((1, 0), (1, 0)))
    fh, fw = FIELD
    s = ii[fh:, fw:] - ii[:-fh, fw:] - ii[fh:, :-fw] + ii[:-fh, :-fw]
    return s[::4, ::4] / (fh * fw)


class Fields:
    """Per field: transitions when a quarter of it changed the same way within the last 3 frames; their history."""

    def __init__(self, px):
        self.px = px
        self.win_p, self.win_n = [], []
        self.sign = None
        self.hist = None

    def add(self, v, f):
        p, n = self.px.add(v)
        self.win_p = (self.win_p + [p])[-3:]
        self.win_n = (self.win_n + [n])[-3:]
        sp = field_shares(np.logical_or.reduce(self.win_p))
        sn = field_shares(np.logical_or.reduce(self.win_n))
        if self.sign is None:
            self.sign = np.zeros(sp.shape, np.int8)
            self.hist = np.full((LIMIT,) + sp.shape, -10 ** 6, np.int32)
        ev = np.where(sp >= 0.25, 1, np.where(sn >= 0.25, -1, 0)).astype(np.int8)
        new = (ev != 0) & (ev != self.sign)
        self.sign = np.where(new, ev, self.sign)
        if new.any():
            self.hist[:-1][:, new] = self.hist[1:][:, new]
            self.hist[-1][new] = f
        flashing = (f - self.hist[0]) < FPS
        return float(flashing.mean()), int(flashing.sum()), float(max(sp.max(), sn.max()))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("video")
    ap.add_argument("--out", default="log/render_logs/m7_flash_check.json")
    ap.add_argument("--from-s", type=float, default=0.0)
    ap.add_argument("--to-s", type=float, default=0.0)
    a = ap.parse_args()
    cmd = ["ffmpeg", "-v", "error", "-ss", f"{a.from_s:.3f}", "-i", a.video]
    if a.to_s > 0:
        cmd += ["-t", f"{a.to_s - a.from_s:.3f}"]
    cmd += ["-vf", f"scale={W}:{H}:flags=area,fps={FPS}", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"]
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    gen, red = Fields(Pixels(STEP, DARK)), Fields(Pixels(RED_STEP))
    fails, peak = [], {"general": (0, 0), "red": (0, 0)}
    f = 0
    while True:
        buf = p.stdout.read(W * H * 3)
        if len(buf) < W * H * 3:
            break
        im = np.frombuffer(buf, np.uint8).reshape(H, W, 3)
        L = lin(im)
        Y = 0.2126 * L[..., 0] + 0.7152 * L[..., 1] + 0.0722 * L[..., 2]
        s = L.sum(-1) + 1e-6
        r = np.where(L[..., 0] / s >= RED, L[..., 0] / s, 0.0)
        for kind, c, v in (("general", gen, Y), ("red", red, r)):
            share, nf, _ = c.add(v, f)
            if nf > peak[kind][0]:
                peak[kind] = (nf, f)
            if nf:
                fails.append({"kind": kind, "frame": f, "t": round(a.from_s + f / FPS, 3), "field_share": round(share, 3)})
        f += 1
    p.wait()
    spans = []
    for x in sorted(fails, key=lambda x: (x["kind"], x["frame"])):
        if spans and spans[-1]["kind"] == x["kind"] and x["frame"] - spans[-1]["to_frame"] <= 1:
            spans[-1]["to_frame"], spans[-1]["to_t"] = x["frame"], x["t"]
            spans[-1]["max_share"] = max(spans[-1]["max_share"], x["field_share"])
        else:
            spans.append({"kind": x["kind"], "from_frame": x["frame"], "to_frame": x["frame"], "from_t": x["t"],
                          "to_t": x["t"], "max_share": x["field_share"]})
    out = {"generated_by": "scripts/flash_check.py", "video": a.video, "frames": f, "from_s": a.from_s,
           "rule": "fail: a 10-degree field with > 3 flashes (>= 7 alternating transitions, each over a quarter of it at once) "
                   "in the last second; field_share: the share of field positions failing",
           "peak": {k: {"fields": v[0], "t": round(a.from_s + v[1] / FPS, 3)} for k, v in peak.items()},
           "failing_spans": spans}
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    json.dump(out, open(a.out, "w"), indent=1)
    print(f"{a.video}: {f} frames; most failing fields: general {peak['general'][0]} at "
          f"{a.from_s + peak['general'][1] / FPS:.2f} s, red {peak['red'][0]} at {a.from_s + peak['red'][1] / FPS:.2f} s")
    for sp in spans:
        print(f"  FAIL {sp['kind']}: {sp['from_t']:.2f}-{sp['to_t']:.2f} s, up to {sp['max_share']:.0%} of the fields")
    if not spans:
        print("  no failing frames")


if __name__ == "__main__":
    main()
