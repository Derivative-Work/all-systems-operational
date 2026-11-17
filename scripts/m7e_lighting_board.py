"""M7e options board (human interventions 32: "Give me some other options for lighting levels for the people so I can
make a call on that"): the same frames at each people-fill level (blender/look.py people_fill), graded as the edit
grades them (scripts/grade.py), one row per shot, one column per level.
Stills come from: ASO_FILL=<w> blender -b --factory-startup --python blender/coverage_m7.py -- --out <dir>/w<w> --still
--at mid --subs <subs> --size 1600x900 --log <dir>/w<w>/pose.log, one run per level.
Usage: .venv/bin/python -I scripts/m7e_lighting_board.py <dir> --levels 0,120,350,900 --subs O03a,O09c,O17b,O18a,O20a
       --names "silhouettes (as approved),a hint,a soft wash,lit" [--out review/m7/lighting_options.jpg]
"""
import argparse
import json
import sys
from pathlib import Path

import cv2
import numpy as np

sys.path.insert(0, "scripts")
import grade as G  # noqa: E402

LOOK = {"live": "grey", "cafe": "cafe", "treehouse": "grey", "park": "grey", "void": "grey"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("dir")
    ap.add_argument("--levels", default="0,120,350,900")
    ap.add_argument("--subs", default="O03a,O09c,O17b,O18a,O20a")
    ap.add_argument("--names", default="")
    ap.add_argument("--cell", type=int, default=640)
    ap.add_argument("--out", default="review/m7/lighting_options.jpg")
    a = ap.parse_args()
    levels = a.levels.split(",")
    names = a.names.split(",") if a.names else [f"{w} W" for w in levels]
    subs = a.subs.split(",")
    plan = {s["id"]: s for s in json.load(open("config/coverage_m5c.json"))["subs"]}
    cw, ch = a.cell, a.cell * 9 // 16
    head, side = 70, 150
    board = np.full((head + ch * len(subs) + 8 * len(subs), side + (cw + 8) * len(levels), 3), 24, np.uint8)
    font = cv2.FONT_HERSHEY_SIMPLEX
    for j, (w, nm) in enumerate(zip(levels, names)):
        x = side + j * (cw + 8)
        cv2.putText(board, nm, (x + 6, 30), font, 0.8, (235, 235, 235), 2, cv2.LINE_AA)
        cv2.putText(board, f"fill {w} W a spot", (x + 6, 58), font, 0.6, (170, 170, 170), 1, cv2.LINE_AA)
    for i, sid in enumerate(subs):
        y = head + i * (ch + 8)
        s = plan[sid]
        cv2.putText(board, sid, (10, y + 30), font, 0.8, (235, 235, 235), 2, cv2.LINE_AA)
        cv2.putText(board, s["room"], (10, y + 58), font, 0.6, (170, 170, 170), 1, cv2.LINE_AA)
        for j, w in enumerate(levels):
            p = Path(a.dir) / f"w{w}" / f"{sid}.png"
            im = cv2.imread(str(p), cv2.IMREAD_UNCHANGED)
            if im is None:
                continue
            if im.dtype == np.uint16:
                im = (im / 257).astype(np.uint8)
            im = cv2.resize(im[..., :3], (cw, ch), interpolation=cv2.INTER_AREA)
            im = G.grade(im, LOOK[s["room"]], s["start_frame"])
            x = side + j * (cw + 8)
            board[y:y + ch, x:x + cw] = im
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(a.out, board, [cv2.IMWRITE_JPEG_QUALITY, 88])
    print(a.out, board.shape)


if __name__ == "__main__":
    main()
