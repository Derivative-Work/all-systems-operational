"""M4 clip review: a frame sheet (frames 1, 30, 60, 90, 121 per take, one row per take, with the agent's note) and a
low-res 2x2 preview mp4 of the takes side by side. Frame sheet adapted from Ever Present's scripts/clip_sheet.py
(6a9070b): fixed frames instead of quarters, notes from config/m4_clips.json 'review', and the preview video.
Usage: .venv/bin/python -I scripts/m4_clip_review.py O06 review/m4_fax_clips.jpg review/m4_fax_clips.mp4
"""
import json
import subprocess
import sys
import textwrap
from io import BytesIO
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

FONT = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)
FRAMES = (1, 30, 60, 90, 121)


def frame(p, n, w=400):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(p), "-vf", f"select=eq(n\\,{n - 1}),scale={w}:-2",
                          "-frames:v", "1", "-f", "image2pipe", "-vcodec", "png", "-"], capture_output=True, check=True).stdout
    return Image.open(BytesIO(raw)).convert("RGB")


def main(clip, jpg, mp4):
    notes = json.load(open("config/m4_clips.json")).get("review", {})
    takes = sorted(Path(f"assets/gen/clips/{clip}").glob("*.mp4"))
    rows = [(p, [frame(p, n) for n in FRAMES]) for p in takes]
    w, h = rows[0][1][0].size
    lh = 70
    im = Image.new("RGB", (len(FRAMES) * (w + 6) + 6, 30 + len(rows) * (h + lh + 30)), (16, 16, 18))
    dr = ImageDraw.Draw(im)
    dr.text((8, 6), f"{clip} clips: frames {', '.join(map(str, FRAMES))} of 121 (24 fps, 5 s)", font=FONT, fill=(220, 220, 220))
    for r, (p, fr) in enumerate(rows):
        y = 30 + r * (h + lh + 30)
        dr.text((8, y + 4), p.stem, font=FONT, fill=(255, 210, 0))
        for k, f in enumerate(fr):
            im.paste(f, (6 + k * (w + 6), y + 28))
        note = textwrap.fill(notes.get(p.stem, ""), 190)
        dr.multiline_text((8, y + 32 + h), note, font=FONT, fill=(230, 230, 230), spacing=3)
    im.save(jpg, quality=85)
    ins = sum((["-i", str(p)] for p in takes), [])
    lab = "".join(f"[{i}:v]scale=640:-2,drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf:"
                  f"text='{p.stem}':x=10:y=10:fontsize=22:fontcolor=yellow[v{i}];" for i, p in enumerate(takes))
    n = len(takes)
    stack = "".join(f"[v{i}]" for i in range(n)) + (f"xstack=inputs={n}:layout=0_0|w0_0|0_h0|w0_h0[out]" if n == 4
                                                      else f"hstack=inputs={n}[out]")
    subprocess.run(["ffmpeg", "-v", "error", "-y", *ins, "-filter_complex", lab + stack, "-map", "[out]", "-an",
                    "-c:v", "libx264", "-crf", "26", "-pix_fmt", "yuv420p", mp4], check=True)
    print(jpg, mp4)


if __name__ == "__main__":
    main(*sys.argv[1:4])
