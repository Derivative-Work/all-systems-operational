"""The vertical cut, A stacked (human interventions 46: "Yes make A stacked"), 1080x1920 for YouTube Shorts:
  section   "We are aware" through chorus 1, the build and hard stop 1 ("without fai—") to "We'll be right back" and
            "We're seeing renewed errors", then four bars of the cafe as the band comes back in (human interventions 48:
            "so the 'renewed errors' has time to be visible"), through "The agents that we hired to read the mail for us
            (Hey!)": the master's frames 1492 (O08's cut) to 3395 (config/vertical_status.json), 63.43 s, ending just
            before the pickup "Are (waiting in the lobby)" at 113.21 s, the sound faded over its last 0.3 s
  top       the made-up status page at phone width (Remotion Vertical-Status), the narrator on screen the whole time; its
            rows follow the song (human interventions 47; config/vertical_status.json): Investigating one by one on "We are
            aware ... everything", "Early signs of stabilization" on the line, the mail back on "open up the mail",
            "Renewed errors" on "We're seeing renewed errors"; the banner stays green. From O13's second card (the video's
            own status page, master frames 3089-3113) the picture holds "We'll be right back." rather than show the page
            twice, until the cafe (O14, 3114)
  middle    the master's picture, 16:9, full width (1080x608), with its own lower thirds, viewer count and spinner
  below     the lyric as sung (lyrics/as_sung_lines_video.srt), the echoes and Hey!s on their own line in coral
  tag       "AI-GENERATED SATIRE" (the credits slide's eyebrow) for the whole cut: the Short has no bookend, which is
            where the video's own disclosure is
  clear     the strips YouTube Shorts covers: the top 140 px, the bottom 330, and the buttons down the right (x > 950)
            beside the captions
Parts: npx remotion render Vertical-Status renders/vertical/parts/status --sequence --image-format=png --scale=1.5
       --gl=swangle --concurrency=8 (1080x558, one per frame of the cut)
Usage: .venv/bin/python -I scripts/vertical_short.py [--out renders/vertical/all-systems-operational-short-A.mp4]
       [--still <clip frame> <png>] (one frame, for checking the layout)
"""
import argparse
import json
import re
import subprocess
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

MASTER = "renders/m7/master/all-systems-operational-master.mp4"
SRT = "lyrics/as_sung_lines_video.srt"
PARTS = Path("renders/vertical/parts")
FPS = 30
SPAN = json.loads(Path("config/vertical_status.json").read_text())
START, END = SPAN["start_frame"], SPAN["end_frame"]
HOLD, CAFE = 3088, 3114          # O13's card's last frame (29 frames from 3060), held over its status card; O14
FADE_S = 0.3
VW, VH = 1080, 1920
BG = (14, 17, 19)
WHITE = (255, 253, 248)          # remotion/src/theme.ts white
CORAL = (226, 100, 62)           # coral
TAG_Y, PANEL_Y, PANEL_H, PIC_Y, CAP_Y = 140, 186, 558, 766, 1400
CAP_CX, CAP_W = 505, 860         # captions centred left of the Shorts buttons


def font(sz, w="ExtraBold"):
    f = ImageFont.truetype("remotion/public/fonts/WorkSans-VF.ttf", sz)
    f.set_variation_by_name(w)
    return f


def srt_cues():
    out = []
    for block in Path(SRT).read_text().strip().split("\n\n"):
        ln = block.strip().splitlines()
        a, b = [sum(float(x) * m for x, m in zip(t.replace(",", ".").split(":"), (3600, 60, 1))) for t in ln[1].split(" --> ")]
        out.append((a, b, " ".join(ln[2:])))
    return out


def wrap(d, text, F, width):
    lines, cur = [], ""
    for w in text.split():
        t = f"{cur} {w}".strip()
        if d.textlength(t, font=F) <= width or not cur:
            cur = t
        else:
            lines.append(cur)
            cur = w
    return lines + [cur]


def caption_layer(text):
    """The lyric: the line in white, wrapped; an ending (echo) or (Hey!) on its own line in coral."""
    m = re.match(r"^(.*?)\s*\(([^)]*)\)\s*$", text)
    main, echo = (m.group(1), m.group(2)) if m and m.group(1) else (text, "")
    lay = Image.new("RGBA", (VW, 260), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    Fe = font(54, "Bold")
    for sz in (70, 66, 62, 58):                                 # two lines at most, clear of the Shorts title
        F = font(sz)
        lines = wrap(d, main, F, CAP_W)
        if len(lines) <= 2:
            break
    y = 0
    for ln in lines:
        d.text((CAP_CX, y), ln, font=F, fill=WHITE, anchor="ma")
        y += int(sz * 1.09)
    if echo:
        d.text((CAP_CX, y + 6), f"({echo})", font=Fe, fill=CORAL, anchor="ma")
    return lay


def base():
    v = Image.new("RGB", (VW, VH), BG)
    d = ImageDraw.Draw(v)
    F = font(30, "SemiBold")
    x = 48
    for ch in "AI-GENERATED SATIRE":
        d.text((x, TAG_Y), ch, font=F, fill=CORAL)
        x += d.textlength(ch, font=F) + 4                      # letterspaced, as the credits slide's eyebrow
    return v


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="renders/vertical/all-systems-operational-short-A.mp4")
    ap.add_argument("--still", nargs=2)
    a = ap.parse_args()
    status = sorted((PARTS / "status").glob("*.png"))
    if len(status) != END - START:
        raise SystemExit(f"{PARTS / 'status'}: {len(status)} frames, not {END - START}")
    canvas = np.asarray(base()).copy()
    t0 = START / FPS
    # the lines that start in the cut (the one before ends 0.2 s in: its last word, unsung here)
    cues = [(s - t0, e - t0, caption_layer(t)) for s, e, t in srt_cues() if s >= t0 and s < END / FPS]
    n = END - START

    def frame(k, pic):
        f = canvas.copy()
        f[PANEL_Y:PANEL_Y + PANEL_H] = np.asarray(Image.open(status[k]).convert("RGB"))
        f[PIC_Y:PIC_Y + 608] = cv2.resize(pic, (VW, 608), interpolation=cv2.INTER_AREA)
        t = k / FPS
        im = Image.fromarray(f)
        for s, e, lay in cues:
            if s <= t < e:
                fade = min(1.0, (t - s) * FPS / 3)                # in over 3 frames
                if fade < 1:
                    lay = lay.copy()
                    lay.putalpha(lay.split()[3].point(lambda v: int(v * fade)))
                im.paste(lay, (0, CAP_Y), lay)
        return np.asarray(im)

    rd = subprocess.Popen(["ffmpeg", "-v", "error", "-ss", f"{t0:.6f}", "-i", MASTER, "-frames:v", str(n), "-f", "rawvideo",
                           "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
    if a.still:
        want = int(a.still[0])
        for k in range(want + 1):
            pic = np.frombuffer(rd.stdout.read(1920 * 1080 * 3), np.uint8).reshape(1080, 1920, 3)
        rd.kill()
        Image.fromarray(frame(want, pic)).save(a.still[1])
        print(a.still[1])
        return
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    dur = n / FPS
    wr = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{VW}x{VH}", "-r", str(FPS),
                           "-i", "-", "-ss", f"{t0:.6f}", "-t", f"{dur:.6f}", "-i", MASTER, "-map", "0:v", "-map", "1:a",
                           "-af", f"afade=t=in:d=0.02,afade=t=out:st={dur - FADE_S:.3f}:d={FADE_S}",
                           "-c:v", "libx264", "-profile:v", "high", "-preset", "slow", "-crf", "16", "-pix_fmt", "yuv420p",
                           "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709",
                           "-c:a", "aac", "-b:a", "384k", "-ar", "48000", "-movflags", "+faststart", "-shortest", a.out],
                          stdin=subprocess.PIPE)
    held = None
    for k in range(n):
        raw = rd.stdout.read(1920 * 1080 * 3)
        pic = np.frombuffer(raw, np.uint8).reshape(1080, 1920, 3)
        if START + k == HOLD:
            held = pic
        if HOLD < START + k < CAFE and held is not None:
            pic = held
        wr.stdin.write(frame(k, pic).tobytes())
    wr.stdin.close()
    rd.wait()
    if wr.wait():
        raise SystemExit("ffmpeg failed")
    print(f"{a.out}: {n} frames, {dur:.3f} s")


if __name__ == "__main__":
    main()
