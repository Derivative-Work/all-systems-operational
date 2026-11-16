"""M7b, Part B (production log 39-40; human interventions 18-19): the park as it stands, and the concept stills.

  --frames     review/m7b_park_frames.jpg: the middle frame of every park sub-shot (O19b-O22g) from
               review/m5c3_animatic.mp4 (the approved grey box, with its overlays), then the M7a renders of the park
               (O20a, O20c, O22d from renders/m7a; O19b from renders/m7b/m7a_ref, production log 36)
  --concepts   review/m7b_park_concepts.jpg: the kept concept stills and far-plate candidates
               (assets/gen/stills/m7b_park, config/m7b_park_concepts.json "review"), labelled, beside the current O20a and
               O19b (M7a), with the rejected takes small at the bottom
Usage: .venv/bin/python -I scripts/m7b_park_sheet.py --frames | --concepts
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

import cv2
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import m7a_board as MA  # noqa: E402

COV = json.loads((ROOT / "config/coverage_m5c.json").read_text())
CFG = json.loads((ROOT / "config/m7b_park_concepts.json").read_text())
STILLS = ROOT / "assets/gen/stills/m7b_park"


def label(im, text, scale=0.55):
    im = im.copy()
    h = int(30 * scale / 0.55)
    cv2.rectangle(im, (0, 0), (im.shape[1], h), (20, 20, 20), -1)
    cv2.putText(im, text, (8, int(h * 0.72)), cv2.FONT_HERSHEY_SIMPLEX, scale, (235, 235, 235), 1, cv2.LINE_AA)
    return im


def grid(tiles, cols, gap=8, bg=24):
    th, tw = tiles[0].shape[:2]
    while len(tiles) % cols:
        tiles.append(np.full((th, tw, 3), bg, np.uint8))
    rows = []
    for k in range(0, len(tiles), cols):
        r = []
        for t in tiles[k:k + cols]:
            r += [t, np.full((th, gap, 3), bg, np.uint8)]
        rows += [np.hstack(r[:-1]), np.full((gap, (tw + gap) * cols - gap, 3), bg, np.uint8)]
    return np.vstack(rows[:-1])


def frames(out="review/m7b_park_frames.jpg"):
    subs = [s for s in COV["subs"] if s.get("room") == "park" and s.get("source") == "blender"]
    sel = "+".join(f"eq(n\\,{(s['start_frame'] + s['end_frame']) // 2})" for s in subs)
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(ROOT / "review/m5c3_animatic.mp4"), "-vf", f"select={sel}",
                          "-vsync", "0", "-f", "rawvideo", "-pix_fmt", "bgr24", "-"], capture_output=True, check=True).stdout
    ims = np.frombuffer(raw, np.uint8).reshape(-1, 540, 960, 3)
    tiles = [label(cv2.resize(im, (480, 270), interpolation=cv2.INTER_AREA),
                   f"{s['id']} {s['camera']} (M5c3 grey box)", 0.45) for im, s in zip(ims, subs)]
    m7a = [("O20a", ROOT / "renders/m7a/O20a.png"), ("O19b", ROOT / "renders/m7b/m7a_ref/O19b.png"),
           ("O20c", ROOT / "renders/m7a/O20c.png"), ("O22d", ROOT / "renders/m7a/O22d.png")]
    tiles += [label(cv2.resize(cv2.imread(str(p)), (480, 270), interpolation=cv2.INTER_AREA), f"{sid} M7a look", 0.45)
              for sid, p in m7a]
    head = np.full((44, 4 * 480 + 24, 3), 24, np.uint8)
    cv2.putText(head, "The park now: the middle frame of every park sub-shot (M5c3 animatic), then the M7a look (last row).",
                (8, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (235, 235, 235), 1, cv2.LINE_AA)
    img = np.vstack([head, grid(tiles, 4)])
    cv2.imwrite(str(ROOT / out), img, [cv2.IMWRITE_JPEG_QUALITY, 86])
    print(f"{out}: {img.shape[1]}x{img.shape[0]}, {(ROOT / out).stat().st_size / 1e6:.1f} MB")


def concepts(out="review/m7b_park_concepts.jpg"):
    rv = CFG["review"]
    W = 1930
    tw, th = 954, 537
    head = np.full((44, W, 3), 24, np.uint8)
    cv2.putText(head, "M7b park concepts (FLUX.2 [dev], reference only, not footage) beside the park as it stands (M7a).",
                (8, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (235, 235, 235), 1, cv2.LINE_AA)
    cur = [label(cv2.resize(cv2.imread(str(ROOT / "renders/m7a/O20a.png")), (tw, th), interpolation=cv2.INTER_AREA),
                 "NOW: O20a, the wide from behind the crowd (M7a)"),
           label(cv2.resize(cv2.imread(str(ROOT / "renders/m7b/m7a_ref/O19b.png")), (tw, th), interpolation=cv2.INTER_AREA),
                 "NOW: O19b, rising over the crest (M7a code)")]
    kept = [(k, v) for k, v in rv.items() if not k.startswith("_") and v.get("keep")]
    rej = [(k, v) for k, v in rv.items() if not k.startswith("_") and not v.get("keep")]
    tiles = []
    for k, v in kept:
        item = k.rsplit("_s", 1)[0]
        im = cv2.imread(str(STILLS / item / f"{k}.png"))
        im = cv2.resize(im, (tw, int(tw * im.shape[0] / im.shape[1])), interpolation=cv2.INTER_AREA)[:th]
        im = np.vstack([im, np.full((th - im.shape[0], tw, 3), 24, np.uint8)]) if im.shape[0] < th else im
        tiles.append(label(im, f"{v['label']}  [{k}]"))
    def padw(g):
        return np.hstack([g, np.full((g.shape[0], W - g.shape[1], 3), 24, np.uint8)]) if g.shape[1] < W else g
    rows = [head, padw(grid(cur, 2)), np.full((12, W, 3), 24, np.uint8)]
    note = np.full((34, W, 3), 24, np.uint8)
    cv2.putText(note, "Concept stills (the direction for the rebuilt hill) and far-plate candidates (the generated backdrop "
                "behind the Blender set).", (8, 24), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (120, 220, 255), 1, cv2.LINE_AA)
    rows += [note, padw(grid(tiles, 2))]
    if rej:
        sm = []
        for k, v in rej:
            item = k.rsplit("_s", 1)[0]
            im = cv2.imread(str(STILLS / item / f"{k}.png"))
            sm.append(label(cv2.resize(im, (472, 266), interpolation=cv2.INTER_AREA), f"{k}: {v['why']}", 0.36))
        note2 = np.full((34, W, 3), 24, np.uint8)
        cv2.putText(note2, "Takes not on the sheet: rejected (a constraint) or not kept (weaker); logged in config/m7b_park_concepts.json review and log/prompts/m7b_park.md.",
                    (8, 24), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (140, 140, 255), 1, cv2.LINE_AA)
        g = grid(sm, 4)
        rows += [np.full((12, W, 3), 24, np.uint8), note2, padw(g)]
    img = np.vstack(rows)
    q = 88
    while True:
        cv2.imwrite(str(ROOT / out), img, [cv2.IMWRITE_JPEG_QUALITY, q])
        if (ROOT / out).stat().st_size < 7.8e6 or q <= 60:
            break
        q -= 4
    print(f"{out}: {img.shape[1]}x{img.shape[0]}, q{q}, {(ROOT / out).stat().st_size / 1e6:.1f} MB")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--frames", action="store_true")
    ap.add_argument("--concepts", action="store_true")
    a = ap.parse_args()
    if a.frames:
        frames()
    if a.concepts:
        concepts()


if __name__ == "__main__":
    main()
