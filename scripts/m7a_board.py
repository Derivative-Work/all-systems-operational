"""M7a look board (plan M7; production log 30+): hero frames per set at the final look, each beside the M5c3 grey-box
frame of the same sub-shot and frame, for the human's approval before the full M7 render.

  --grade      renders/m7a/raw/<id>.png (blender/coverage_m7.py --still, 1920x1080, 16-bit) -> renders/m7a/<id>.png
               (scripts/grade.py: grey, cafe, or home for O22 from "Remember Wednesday")
  --board      review/m7a_look_board.jpg: one row per hero, the M5c3 frame left, the M7a frame right, labelled with the
               shot, its frame (local and video), the set and the camera. M5c3's frames are its Blender renders
               (renders/m5c3/frames, or M5c2's / M5c's where M5c3 linked them); O22d's is extracted from
               review/m5c3_animatic.mp4, so M5c3's own home-movie grade shows (with its lower third and label).
  --cycles     review/m7a_cycles_vs_eevee.jpg from renders/m7a/raw/<id>.png and renders/m7a/cycles/<id>.png, graded
               alike, with seconds per frame from the logs.
  --motion     review/m7a_motion_test.mp4: the live-room motion test (renders/m7a/frames_motion/<id>/*.jpg, graded) with the
               master's audio at the same song time; h264 at 650 kb/s, AAC 128k.
Usage: .venv/bin/python -I scripts/m7a_board.py --grade | --board | --cycles [spf json] | --motion
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
import grade as G  # noqa: E402

TS = json.loads((ROOT / "timing/shot_times.json").read_text())
COV = json.loads((ROOT / "config/coverage_m5c.json").read_text())
SUBS = {s["id"]: s for s in COV["subs"]}
O19A, XF, FPS = 175, 10, 30
HEROES = [  # id, set, what it shows
    ("O03a", "live room", "wide: rain-streaked windows, daylight shafts in the haze, band and crowd in silhouette"),
    ("O03b", "live room", "rain on glass, close"),
    ("O09j", "live room", "performer close: the guitar, rim-lit"),
    ("O10a", "live room", "Switch by the door, wired to the ON AIR sign"),
    ("O14c", "coffee shop", "the probes' table, the table tent, the Polaroid"),
    ("O14d", "coffee shop", "the warm Polaroid, Wed 11/11 (a Blender render of the band here)"),
    ("O17b", "coffee shop", "wide singalong: string lights, steamed windows, mugs up"),
    ("O18a", "treehouse", "wide: the band before the whiteboard, rain on the glass"),
    ("O18e", "treehouse", "the conference phone and the chargers"),
    ("O19a", "treehouse", "the door onto the deck: moss on the railings, drizzle, the conifers"),
    ("O20a", "hilltop park", "wide: the crowd, the band, conifers and the skyline in fog"),
    ("O20c", "hilltop park", "the one umbrella"),
    ("O22d", "hilltop park", "the skyline in fog, home-movie grade (from Remember Wednesday)"),
]
LOOK_OF = {"live room": "grey", "coffee shop": "cafe", "treehouse": "grey", "hilltop park": "grey"}
RAW, OUT = ROOT / "renders/m7a/raw", ROOT / "renders/m7a"


def vstart(b):
    if b == "O08c":
        return TS["shots"]["O08"]["start_frame"] + 115
    return TS["shots"][b[:3]]["start_frame"] + (O19A - XF) * (b == "O19b")


def frames_of(sid):
    s = SUBS[sid]
    v0 = vstart(s["build"])
    f0 = s["start_frame"] - v0 + 1 - s.get("xfade_in", 0)
    f1 = s["end_frame"] - v0 + 1
    mid = (f0 + f1) // 2
    return mid, v0 + mid - 1


def look_of(sid, room):
    if sid.startswith("O22"):
        cue = TS["shots"]["O22"]["start_frame"] + TS["shots"]["O22"]["marks"][0]["frame_in_shot"]
        return "home" if frames_of(sid)[1] >= cue else "grey"
    return LOOK_OF[room]


def do_grade():
    for sid, room, _ in HEROES:
        src = RAW / f"{sid}.png"
        if not src.exists():
            print(f"{sid}: no raw render")
            continue
        im = cv2.imread(str(src), cv2.IMREAD_UNCHANGED)
        lk = look_of(sid, room)
        cv2.imwrite(str(OUT / f"{sid}.png"), G.grade(im[:, :, :3], lk, frames_of(sid)[1]))
        print(f"{sid}: {lk}")


def greybox(sid):
    mid, vf = frames_of(sid)
    if sid.startswith("O22"):
        out = subprocess.run(["ffmpeg", "-v", "error", "-i", str(ROOT / "review/m5c3_animatic.mp4"), "-vf",
                              f"select=eq(n\\,{vf})", "-frames:v", "1", "-f", "rawvideo", "-pix_fmt", "bgr24", "-"],
                             capture_output=True, check=True).stdout
        return np.frombuffer(out, np.uint8).reshape(540, 960, 3), f"review/m5c3_animatic.mp4 frame {vf} (graded)"
    for d in ("m5c3", "m5c2", "m5c"):
        p = ROOT / f"renders/{d}/frames/{sid}/{mid:04d}.jpg"
        if p.exists():
            return cv2.imread(str(p)), f"renders/{d}/frames/{sid}/{mid:04d}.jpg"
    raise FileNotFoundError(sid)


def bar(w, text, h=34, scale=0.62, color=(235, 235, 235), bg=24):
    b = np.full((h, w, 3), bg, np.uint8)
    cv2.putText(b, text, (10, int(h * 0.7)), cv2.FONT_HERSHEY_SIMPLEX, scale, color, 1, cv2.LINE_AA)
    return b


def board(out="review/m7a_look_board.jpg", tw=960):
    th = tw * 9 // 16
    rows = [bar(2 * tw + 10, "M7a look board. Left: the M5c3 grey box (approved as a base). Right: the M7a look, "
                "Eevee 1920x1080, graded.", 40, 0.62),
            bar(2 * tw + 10, "Same sub-shot, frame, camera and performance in each pair.", 30, 0.55, (170, 170, 170))]
    for sid, room, what in HEROES:
        mid, vf = frames_of(sid)
        gbx, src = greybox(sid)
        new = cv2.imread(str(OUT / f"{sid}.png"))
        a = cv2.resize(gbx, (tw, th), interpolation=cv2.INTER_AREA)
        b = cv2.resize(new, (tw, th), interpolation=cv2.INTER_AREA)
        cam = SUBS[sid]["camera"]
        head = bar(2 * tw + 10, f"{sid}  |  {room}  |  frame {mid} of the build (video frame {vf}, "
                                f"{vf / FPS:.2f} s)  |  camera {cam}  |  {what}", 34, 0.6)
        sub = np.hstack([bar(tw, "M5c3 grey box  (" + src + ")", 26, 0.45, (170, 170, 170)),
                         np.full((26, 10, 3), 24, np.uint8),
                         bar(tw, f"M7a look  ({look_of(sid, room)} grade)", 26, 0.45, (120, 220, 255))])
        rows += [head, sub, np.hstack([a, np.full((th, 10, 3), 24, np.uint8), b]), np.full((14, 2 * tw + 10, 3), 24, np.uint8)]
    img = np.vstack(rows)
    q = 88
    while True:
        cv2.imwrite(out, img, [cv2.IMWRITE_JPEG_QUALITY, q])
        if Path(out).stat().st_size < 7.8e6 or q <= 60:
            break
        q -= 4
    print(f"{out}: {img.shape[1]}x{img.shape[0]}, q{q}, {Path(out).stat().st_size / 1e6:.1f} MB")


def cycles(spf, out="review/m7a_cycles_vs_eevee.jpg", tw=960):
    spf = json.loads(Path(spf).read_text()) if spf else {}
    th = tw * 9 // 16
    rows = [bar(2 * tw + 10, "Eevee (left, the main path) vs Cycles (right), same scene, camera and frame, graded alike "
                             "(scripts/grade.py). Seconds per frame on the RTX 5090 at 1920x1080.", 40, 0.6)]
    for p in sorted((OUT / "cycles").glob("*.png")):
        sid = p.stem
        room = next(r for s, r, _ in HEROES if s == sid)
        lk = look_of(sid, room)
        e = G.grade(cv2.imread(str(RAW / f"{sid}.png"), cv2.IMREAD_UNCHANGED)[:, :, :3], lk, frames_of(sid)[1])
        c = G.grade(cv2.imread(str(p), cv2.IMREAD_UNCHANGED)[:, :, :3], lk, frames_of(sid)[1])
        cv2.imwrite(str(OUT / "cycles" / f"{sid}_graded.jpg"), c, [cv2.IMWRITE_JPEG_QUALITY, 92])
        s = spf.get(sid, {})
        rows += [bar(2 * tw + 10, f"{sid}  |  {room}  |  frame {frames_of(sid)[0]}", 32, 0.6),
                 np.hstack([bar(tw, f"Eevee  {s.get('eevee', '?')} s/frame", 26, 0.5, (120, 220, 255)),
                            np.full((26, 10, 3), 24, np.uint8),
                            bar(tw, f"Cycles  {s.get('cycles', '?')} s/frame", 26, 0.5, (120, 255, 160))]),
                 np.hstack([cv2.resize(e, (tw, th), interpolation=cv2.INTER_AREA), np.full((th, 10, 3), 24, np.uint8),
                            cv2.resize(c, (tw, th), interpolation=cv2.INTER_AREA)]),
                 np.full((14, 2 * tw + 10, 3), 24, np.uint8)]
    cv2.imwrite(out, np.vstack(rows), [cv2.IMWRITE_JPEG_QUALITY, 90])
    print(f"{out}: {Path(out).stat().st_size / 1e6:.1f} MB")


def motion(subs=("O03a", "O03b"), out="review/m7a_motion_test.mp4"):
    """Grade each motion-test frame (grey) and encode with the master's audio from the same song time."""
    tmp = OUT / "frames_motion" / "graded"
    tmp.mkdir(parents=True, exist_ok=True)
    k = 0
    v0 = None
    for sid in subs:
        d = OUT / "frames_motion" / sid
        files = sorted(d.glob("*.jpg"))
        s = SUBS[sid]
        v0 = s["start_frame"] if v0 is None else v0
        for f in files:
            im = cv2.imread(str(f))
            fr = s["start_frame"] + int(f.stem) - (s["start_frame"] - vstart(s["build"]) + 1)
            cv2.imwrite(str(tmp / f"{k:05d}.png"), G.grade(im, "grey", fr))
            k += 1
    t0 = v0 / FPS
    dur = k / FPS
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-framerate", str(FPS), "-i", str(tmp / "%05d.png"),
                    "-ss", f"{t0:.4f}", "-t", f"{dur:.4f}", "-i", str(ROOT / "review/m5c3_animatic.mp4"),
                    "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-b:v", "650k", "-maxrate", "900k",
                    "-bufsize", "1300k", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "128k", "-shortest",
                    "-movflags", "+faststart", str(ROOT / out)], check=True)
    print(f"{out}: {k} frames, {dur:.2f} s from video frame {v0} ({t0:.2f} s), "
          f"{(ROOT / out).stat().st_size / 1e6:.2f} MB")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--grade", action="store_true")
    ap.add_argument("--board", action="store_true")
    ap.add_argument("--cycles", nargs="?", const="")
    ap.add_argument("--motion", action="store_true")
    a = ap.parse_args()
    if a.grade:
        do_grade()
    if a.board:
        board()
    if a.cycles is not None:
        cycles(a.cycles)
    if a.motion:
        motion()


if __name__ == "__main__":
    main()
