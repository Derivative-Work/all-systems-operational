"""M7b look board (production log 37+; human interventions 18-19): the changed hero frames beside their M7a versions,
the treehouse and O04 screens sheet, and the motion test.

  --grade      renders/m7b/raw/<id>.png and renders/m7b/raw_late/O04a.png (blender/coverage_m7.py --still, 1920x1080,
               16-bit) -> renders/m7b/<id>.png (scripts/grade.py: grey, cafe); the M7a references rendered for this
               pass (renders/m7b/m7a_ref/raw, production log 36) -> renders/m7b/m7a_ref/<id>.png the same way
  --board      review/m7b_look_board.jpg: one row per hero, M7a left (renders/m7a/<id>.png, or the reference above),
               M7b right, labelled with what changed
  --screens    review/m7b_screens.jpg: every M7b screen texture (O04's phone; the treehouse's six, night and day) at a
               readable beat, and the screens as rendered: crops of O04a at 1080p and 960 wide, O08c and O18e
  --motion     review/m7b_motion_test.mp4 from renders/m7b/frames_motion/<id>/*.jpg (graded), each segment with the
               master's audio at its own song time; h264 at 650 kb/s, AAC 128k
Usage: .venv/bin/python -I scripts/m7b_board.py --grade | --board | --screens | --motion
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
import m7a_board as MA  # noqa: E402

RAW, OUT, REF = ROOT / "renders/m7b/raw", ROOT / "renders/m7b", ROOT / "renders/m7b/m7a_ref"
TEX = ROOT / "assets/gen/tex/m7b"
FPS = 30
LOOK = {"live": "grey", "cafe": "cafe", "treehouse": "grey", "park": "grey"}
HEROES = [  # id, what changed in M7b
    ("O03b", "rain on glass: beads appear, grow and merge; runners slide in jerks and leave trails (moving: see the motion test)"),
    ("O03c", "kick close: +1/3 stop (the SESSION 503 head, the shell's lacquer)"),
    ("O04a", "the phone: the chat as a texture on the Blender phone, big type, a closer camera over the shoulder (M7b at 90% of the shot: the question arrives at 50%)"),
    ("O08c", "night cutaway: the invented incident-night screens, the screens as the light, a dim cool fill on the set only; no daylight shafts at night"),
    ("O09f", "banjo close: +1/3 stop"),
    ("O09j", "guitar close: +1/3 stop"),
    ("O14c", "steam as rising, curling wisps; the band-only Polaroid; drops on the steamed glass"),
    ("O14d", "the band-only Polaroid (Wed 11/11)"),
    ("O17b", "drops and drip trails on the steamed windows; steam on half the table mugs; haze drift"),
    ("O17j", "tambourine close: +1/3 stop"),
    ("O18a", "treehouse lift: set-only fills (light linking), the cedar and roof read, silhouettes kept; the fourth laptop on the call"),
    ("O18e", "treehouse insert: no -0.5 offset, the lift, the dashboard in focus then the rack to the whiteboard; the ringing phone"),
]


def room_of(sid):
    return MA.SUBS[sid]["room"]


def raw_path(sid):
    return (OUT / "raw_late" / f"{sid}.png") if sid == "O04a" else RAW / f"{sid}.png"


def do_grade():
    for sid, _ in HEROES:
        lk = LOOK[room_of(sid)]
        src = raw_path(sid)
        im = cv2.imread(str(src), cv2.IMREAD_UNCHANGED)
        cv2.imwrite(str(OUT / f"{sid}.png"), G.grade(im[:, :, :3], lk, MA.frames_of(sid)[1]))
        print(f"{sid}: {lk} ({src.relative_to(ROOT)})")
    if (RAW / "O04a.png").exists():
        im = cv2.imread(str(RAW / "O04a.png"), cv2.IMREAD_UNCHANGED)
        cv2.imwrite(str(OUT / "O04a_mid.png"), G.grade(im[:, :, :3], "grey", MA.frames_of("O04a")[1]))
    for p in sorted((REF / "raw").glob("*.png")):
        sid = p.stem
        im = cv2.imread(str(p), cv2.IMREAD_UNCHANGED)
        cv2.imwrite(str(REF / f"{sid}.png"), G.grade(im[:, :, :3], LOOK[room_of(sid)], MA.frames_of(sid)[1]))
        print(f"M7a reference {sid}")


def m7a_frame(sid):
    for p in (ROOT / f"renders/m7a/{sid}.png", REF / f"{sid}.png"):
        if p.exists():
            return cv2.imread(str(p)), str(p.relative_to(ROOT))
    raise FileNotFoundError(sid)


def save(img, out, limit=7.8e6):
    q = 88
    while True:
        cv2.imwrite(str(ROOT / out), img, [cv2.IMWRITE_JPEG_QUALITY, q])
        if (ROOT / out).stat().st_size < limit or q <= 60:
            break
        q -= 4
    print(f"{out}: {img.shape[1]}x{img.shape[0]}, q{q}, {(ROOT / out).stat().st_size / 1e6:.1f} MB")


def board(out="review/m7b_look_board.jpg", tw=960):
    th = tw * 9 // 16
    W = 2 * tw + 10
    rows = [MA.bar(W, "M7b look board. Left: M7a (approved as the base, human interventions 18). Right: M7b. Eevee 1920x1080, "
                      "graded.", 40, 0.62),
            MA.bar(W, "Same sub-shot, frame, camera and performance in each pair, except O04a (M7b's camera; M7b shown at 90% "
                      "of the shot, M7a at its middle).", 30, 0.5, (170, 170, 170))]
    for sid, what in HEROES:
        mid, vf = MA.frames_of(sid)
        a, src = m7a_frame(sid)
        b = cv2.imread(str(OUT / f"{sid}.png"))
        cam = MA.SUBS[sid]["camera"]
        rows += [MA.bar(W, f"{sid}  |  {room_of(sid)}  |  frame {mid} (video {vf})  |  camera {cam}", 32, 0.6),
                 MA.bar(W, f"M7b: {what}", 28, 0.5, (120, 220, 255)),
                 np.hstack([MA.bar(tw, "M7a  (" + src + ")", 24, 0.45, (170, 170, 170)), np.full((24, 10, 3), 24, np.uint8),
                            MA.bar(tw, f"M7b  ({LOOK[room_of(sid)]} grade)", 24, 0.45, (120, 220, 255))]),
                 np.hstack([cv2.resize(a, (tw, th), interpolation=cv2.INTER_AREA), np.full((th, 10, 3), 24, np.uint8),
                            cv2.resize(b, (tw, th), interpolation=cv2.INTER_AREA)]),
                 np.full((14, W, 3), 24, np.uint8)]
    save(np.vstack(rows), out)


def tex_frame(comp, i):
    d = TEX / comp / "frames"
    files = sorted(d.glob("*.*"))
    return cv2.imread(str(files[min(i, len(files) - 1)]))


def fit(im, w=None, h=None):
    if w and h:
        s = min(w / im.shape[1], h / im.shape[0])
    else:
        s = (w / im.shape[1]) if w else (h / im.shape[0])
    return cv2.resize(im, (int(im.shape[1] * s), int(im.shape[0] * s)), interpolation=cv2.INTER_AREA)


def pad_to(im, w, h, bg=24):
    out = np.full((h, w, 3), bg, np.uint8)
    out[:im.shape[0], :im.shape[1]] = im[:h, :w]
    return out


def screens(out="review/m7b_screens.jpg"):
    W = 1930
    rows = [MA.bar(W, "M7b screens. Remotion textures (remotion/src/components/TreehouseScreens.tsx, PhoneChat.tsx "
                      "PhoneChatBig), mapped onto the Blender screens. All invented; generic UIs in the video's palette.", 40, 0.55)]
    # O04: the texture before and after the Hey!, then the render crops
    o04 = [fit(tex_frame("M7-O04-PhoneScreen", i), h=560) for i in (40, 100, 130)]
    lbl = ["O04 texture, frame 40 (before 'inbox')", "frame 100 (question in)", "frame 130 (+1 on the Hey!)"]
    tiles = [np.vstack([MA.bar(o.shape[1], t, 24, 0.4), o]) for o, t in zip(o04, lbl)]
    late = cv2.imread(str(OUT / "O04a.png"))
    g = cv2.cvtColor(late, cv2.COLOR_BGR2GRAY)
    ys, xs = np.where(g > np.percentile(g, 99.0))          # the screen is the brightest thing in frame
    cy, cx = int(np.median(ys)), int(np.median(xs))
    y0, x0 = max(0, cy - 230), max(0, cx - 300)
    crop = late[y0:y0 + 460, x0:x0 + 600]
    small = cv2.resize(late, (960, 540), interpolation=cv2.INTER_AREA)
    crop_s = small[y0 // 2:y0 // 2 + 230, x0 // 2:x0 // 2 + 300]
    tiles.append(np.vstack([MA.bar(600, "O04a M7b at 1080p, 1:1 crop", 24, 0.4), crop]))
    tiles.append(np.vstack([MA.bar(300, "the same, 960 wide, 1:1", 24, 0.4), crop_s]))
    hmax = max(t.shape[0] for t in tiles)
    row = np.hstack([pad_to(t, t.shape[1] + 10, hmax) for t in tiles])
    rows += [MA.bar(W, "O04: one message and the +1 count in big type, above the holder's thumb", 30, 0.55, (120, 220, 255)),
             pad_to(row, W, hmax)]
    # the treehouse textures, night (O08c) and day (O18e's middle)
    for v, fr, note in (("night", 35, "O08c's night (72 frames; the hero's frame)"), ("day", 539, "O18's day (576 frames; O18e's frame)")):
        tiles = []
        for comp, kind in (("TwoFactor", "phone"), ("AlertCall", "phone"), ("Dashboard", "lap"), ("Terminal", "lap"),
                           ("Agent", "lap"), ("VideoCall", "lap")):
            im = tex_frame(f"M7-Tree-{comp}-{v}", fr)
            im = fit(im, h=400) if kind == "phone" else fit(im, w=420)
            tiles.append(np.vstack([MA.bar(im.shape[1], comp, 24, 0.45), im]))
        hmax = max(t.shape[0] for t in tiles)
        row = np.hstack([pad_to(t, t.shape[1] + 8, hmax) for t in tiles])
        rows += [MA.bar(W, f"Treehouse textures, {note}", 30, 0.55, (120, 220, 255)), pad_to(fit(row, w=W) if row.shape[1] > W else row, W, hmax)]
    # as rendered
    for sid in ("O08c", "O18e"):
        im = cv2.imread(str(OUT / f"{sid}.png"))
        rows += [MA.bar(W, f"{sid} as rendered (M7b, 1920x1080 graded, shown at 960 wide)", 30, 0.55, (120, 220, 255)),
                 pad_to(cv2.resize(im, (960, 540), interpolation=cv2.INTER_AREA), W, 540)]
    save(np.vstack(rows), out)


MOTION = [("O03b", 0, 120), ("O03a", 20, 110), ("O14c", 0, 120), ("O18a", 0, 90)]   # sub, first, last local index


def motion(out="review/m7b_motion_test.mp4"):
    """Grade each motion-test frame and encode; each segment carries the master's audio from its own song time."""
    segs = []
    tmp = OUT / "frames_motion" / "graded"
    tmp.mkdir(parents=True, exist_ok=True)
    k = 0
    for sid, a, b in MOTION:
        s = MA.SUBS[sid]
        files = sorted((OUT / "frames_motion" / sid).glob("*.jpg"))[a:b]
        lk = LOOK[s["room"]]
        v0 = MA.vstart(s["build"])
        for f in files:
            vf = v0 + int(f.stem) - 1
            cv2.imwrite(str(tmp / f"{k:05d}.png"), G.grade(cv2.imread(str(f)), lk, vf))
            k += 1
        segs.append((sid, (v0 + int(files[0].stem) - 1) / FPS, len(files) / FPS))
    filt = "".join(f"[1:a]atrim=start={t0:.4f}:duration={d:.4f},asetpts=PTS-STARTPTS[a{i}];" for i, (_, t0, d) in enumerate(segs))
    filt += "".join(f"[a{i}]" for i in range(len(segs))) + f"concat=n={len(segs)}:v=0:a=1[aout]"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-framerate", str(FPS), "-i", str(tmp / "%05d.png"),
                    "-i", str(ROOT / "review/m5c3_animatic.mp4"), "-filter_complex", filt, "-map", "0:v", "-map", "[aout]",
                    "-c:v", "libx264", "-b:v", "650k", "-maxrate", "900k", "-bufsize", "1300k", "-pix_fmt", "yuv420p",
                    "-c:a", "aac", "-b:a", "128k", "-shortest", "-movflags", "+faststart", str(ROOT / out)], check=True)
    print(f"{out}: {k} frames, {k / FPS:.2f} s, segments {[(s, round(t, 2), round(d, 2)) for s, t, d in segs]}, "
          f"{(ROOT / out).stat().st_size / 1e6:.2f} MB")


def main():
    ap = argparse.ArgumentParser()
    for k in ("grade", "board", "screens", "motion"):
        ap.add_argument(f"--{k}", action="store_true")
    a = ap.parse_args()
    if a.grade:
        do_grade()
    if a.board:
        board()
    if a.screens:
        screens()
    if a.motion:
        motion()


if __name__ == "__main__":
    main()
