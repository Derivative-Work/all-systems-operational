"""M5: contact sheet of the animatic, one frame per shot (plus the end-sequence cards), each labelled with its ID, the
video time and the frame's source. The frame is a telling one where the shot has a cued event (after Switch flips, on
a late clap, with the LED dimmed, a mug up), else the shot's middle.
Usage: .venv/bin/python -I scripts/m5_sheet.py review/m5_animatic.mp4 review/m5_animatic_sheet.jpg
"""
import json
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont

TS = json.load(open("timing/shot_times.json"))
SHOTS = TS["shots"]
SRC = json.load(open("renders/m5/m5_animatic_sources.json"))
# frame in the shot to show (else the middle)
PICK = {"O01": 240, "O02": 180, "O04": 130, "O08": 60, "O10": 50, "O12": 19, "O13": 40, "O15": 100, "O16": 60,
        "O17": 130, "O18": 470, "O19": 120, "O21": 30, "O22": 400}
COLS, TW, THH, LAB = 5, 384, 216, 34


def frame_at(video, n):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", video, "-vf", f"select=eq(n\\,{n})", "-frames:v", "1", "-f", "rawvideo",
                          "-pix_fmt", "rgb24", "-"], capture_output=True, check=True).stdout
    return Image.fromarray(np.frombuffer(raw, np.uint8).reshape(540, 960, 3))


def main():
    video, out = sys.argv[1], sys.argv[2]
    items = []
    for sid in sorted([k for k in SHOTS if k != "O24"], key=lambda k: SHOTS[k]["start_frame"]):
        s = SHOTS[sid]
        k = PICK.get(sid, (s["end_frame"] - s["start_frame"]) // 2)
        items.append((sid, s["start_frame"] + k, SRC.get(sid, "")))
    f0 = SHOTS["O24"]["start_frame"]
    for name, comp, n in (("O24 end card", "M5-O24-EndCard", 180), ("O24 final card", "M5-O24-FinalCard", 90),
                          ("fact card", "M5-FactCard", 450), ("disclosure card", "M5-DisclosureCard", 540)):
        items.append((name, f0 + n // 2, "remotion"))
        f0 += n
    rows = (len(items) + COLS - 1) // COLS
    sheet = Image.new("RGB", (COLS * TW, rows * (THH + LAB)), "#151515")
    d = ImageDraw.Draw(sheet)
    try:
        fb = ImageFont.truetype("DejaVuSans-Bold.ttf", 15)
        fs = ImageFont.truetype("DejaVuSans.ttf", 10)
    except OSError:
        fb = fs = ImageFont.load_default()
    for i, (sid, fr, src) in enumerate(items):
        x, y = (i % COLS) * TW, (i // COLS) * (THH + LAB)
        sheet.paste(frame_at(video, fr).resize((TW, THH), Image.LANCZOS), (x, y + LAB))
        d.text((x + 6, y + 2), f"{sid}  {fr / 30:.2f} s", fill="#fff", font=fb)
        d.text((x + 6, y + 20), src[:70], fill="#bbb", font=fs)
    sheet.save(out, quality=88)
    print(out, len(items), "frames")


if __name__ == "__main__":
    main()
