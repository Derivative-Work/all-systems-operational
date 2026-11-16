"""M5c review: tile blender/instrument_sheet.py's stills into review/m5c_instruments.jpg (the rebuilt acoustic guitar
and banjo alone and on their players, their hands, and the other hands: tambourine, mic stand, the claps).
Usage: .venv/bin/python -I scripts/instrument_sheet.py [renders/m5c2/instruments/sheet.json] [review/m5c_instruments.jpg]
"""
import json
import sys

import cv2
import numpy as np

src = sys.argv[1] if len(sys.argv) > 1 else "renders/m5c2/instruments/sheet.json"
out = sys.argv[2] if len(sys.argv) > 2 else "review/m5c_instruments.jpg"
man = json.load(open(src))
tw = 420
groups = [("guitar", [t for t in man["tiles"] if t["tag"].startswith("guitar")]),
          ("banjo", [t for t in man["tiles"] if t["tag"].startswith("banjo")]),
          ("other hands", [t for t in man["tiles"] if not t["tag"].startswith(("guitar", "banjo"))])]
cols = max(len(g) for _, g in groups)
rows = []
for name, tiles in groups:
    if not tiles:
        continue
    ims = []
    for t in tiles:
        im = cv2.imread(t["file"])
        im = cv2.resize(im, (tw, tw * im.shape[0] // im.shape[1]), interpolation=cv2.INTER_AREA)
        bar = np.full((26, tw, 3), 24, np.uint8)
        cv2.putText(bar, t["label"], (6, 18), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (240, 240, 240), 1, cv2.LINE_AA)
        ims.append(np.vstack([bar, im]))
    while len(ims) < cols:
        ims.append(np.full_like(ims[0], 24))
    rows.append(np.hstack(ims))
head = np.full((40, rows[0].shape[1], 3), 24, np.uint8)
title = sys.argv[3] if len(sys.argv) > 3 else ("M5c review: the acoustic guitar and banjo on Ever Present's neck "
                                                "(blender/instruments.py), their grips, and the other hands")
cv2.putText(head, f"{title}; O09, frame {man['frame']} ({man['t']:.2f} s)"
                  + (f", the clap at frame {man['clap_frame']}" if "clap_frame" in man else ""),
            (10, 27), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (240, 240, 240), 1, cv2.LINE_AA)
cv2.imwrite(out, np.vstack([head] + rows), [cv2.IMWRITE_JPEG_QUALITY, 88])
print(out, sum(len(g) for _, g in groups), "tiles")
