"""M5b: the coverage animatic, 960x540, 30 fps, cut to the post-filtered master: review/m5b_animatic.mp4 (plan M5b).

Same structure, length and end order as M5 (scripts/animatic.py, production log 15; 8,699 frames, 289.97 s): every
O-shot is still exactly its timing/shot_times.json frame count, and M5's composites are reused unchanged (Remotion
overlays, O04's pinned phone screen, O06's clip, O08's inserts, O19's dissolve, O22's grade, the end sequence). What
changes: each Blender shot is the concatenation of its sub-shots (config/coverage.json, rendered by
blender/coverage.py into renders/m5b/frames/<sub-shot>/), and the review label names the sub-shot and its angle.
M5's outputs are untouched (renders/m5/, review/m5_*).
Also writes a share copy (--share: h264 650 kb/s, AAC 128k) and the coverage contact sheet (--sheet: one frame per
sub-shot, its middle, with its id).
Usage: .venv/bin/python -I scripts/m5b_animatic.py [--out review/m5b_animatic.mp4] [--only O09,O11] [--reuse]
       .venv/bin/python -I scripts/m5b_animatic.py --share      (after the main run)
       .venv/bin/python -I scripts/m5b_animatic.py --sheet      (after the main run)
       .venv/bin/python -I scripts/m5b_animatic.py --check      (cuts in the output vs coverage.json)
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

import cv2
import numpy as np

sys.path.insert(0, "scripts")
import animatic as A  # noqa: E402  (M5's assembly: readers, composites, segment())

W, H, FPS = A.W, A.H, A.FPS
COV = json.load(open("config/coverage.json"))
SUBS = COV["subs"]
FR = Path("renders/m5b/frames")
A.SEG = Path("renders/m5b/segments")
OUT = "review/m5b_animatic.mp4"


def subs_of(shot):
    return [s for s in SUBS if s["shot"] == shot]


def frames_of(s, extra=0):
    d = FR / s["id"]
    files = sorted(d.glob("[0-9]*.jpg"))
    n = s["frames"] + extra
    if len(files) != n:
        raise SystemExit(f"{s['id']}: {len(files)} frames rendered, {n} needed (blender/coverage.py)")
    return [cv2.resize(cv2.imread(str(f)), (W, H), interpolation=cv2.INTER_AREA) for f in files]


def blender(sid, n):
    """Replaces M5's reader: a build's frames = its sub-shots in order (placeholders where M5 drops in an insert)."""
    if sid == "O08c":
        out = frames_of(next(s for s in SUBS if s["id"] == "O08c"))
    elif sid == "O19a":
        out = frames_of(next(s for s in SUBS if s["id"] == "O19a"))
    elif sid == "O19b":
        out = []
        for s in subs_of("O19")[1:]:
            out += frames_of(s, s.get("xfade_in", 0))
    else:
        out = []
        for s in subs_of(sid):
            if s["source"] == "blender" and s.get("build") == sid:
                out += frames_of(s)
            else:                                                 # an insert M5 composites over this range
                out += [np.zeros((H, W, 3), np.uint8)] * s["frames"]
    if len(out) != n:
        raise SystemExit(f"{sid}: {len(out)} frames from the sub-shots, {n} expected")
    return out


A.blender = blender


def label_subs(frames, shot, how):
    s0 = A.SHOTS[shot]["start_frame"] if shot in A.SHOTS else None
    for s in subs_of(shot):
        a, b = s["start_frame"] - s0, s["end_frame"] - s0
        cam = s.get("camera") or s["source"]
        A.label(frames[a:b], f"{s['id']}  {s['framing']}: {cam}" if s["source"] == "blender" else f"{s['id']}  {how}")
    return frames


def build(sid):
    fr, how = A.segment(sid, "server")
    n = A.nfr(sid)
    assert len(fr) == n, (sid, len(fr), n)
    A.write(label_subs(fr, sid, how), A.SEG / f"{sid}.mp4")
    return how, n


def main_run(a):
    A.SEG.mkdir(parents=True, exist_ok=True)
    only = set(filter(None, a.only.split(",")))
    keys, sources = [], {}
    for sid in A.order():
        seg = A.SEG / f"{sid}.mp4"
        if (only and sid not in only) or (a.reuse and seg.exists() and sid not in only):
            keys.append(sid)
            continue
        how, n = build(sid)
        keys.append(sid)
        sources[sid] = how
        print(f"{sid:5s} {n:4d} f  {len(subs_of(sid))} shots  {how}", flush=True)
    if only and not a.reuse:
        return
    for name, comp, n in A.END:
        seg = A.SEG / f"end_{comp}.mp4"
        if not (a.reuse and seg.exists()):
            fr = A.read_video(A.REM / f"{comp}.mp4", n)
            A.write(A.label(fr, f"{name}  remotion"), seg)
        keys.append(f"end_{comp}")
    lst = A.SEG / "list_m5b.txt"
    lst.write_text("".join(f"file '{(A.SEG / (k + '.mp4')).resolve()}'\n" for k in keys))
    joined = A.SEG / "joined_m5b.mp4"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", str(joined)], check=True)
    nframes = int(subprocess.run(["ffprobe", "-v", "error", "-count_frames", "-select_streams", "v:0", "-show_entries",
                                  "stream=nb_read_frames", "-of", "csv=p=0", str(joined)], capture_output=True, text=True).stdout.strip())
    dur = nframes / FPS
    lead = A.TS["lead_in_s"]
    af = f"adelay={int(round(lead * 1000))}:all=1,apad=whole_dur={dur:.3f},atrim=start=0:end={dur:.3f},asetpts=PTS-STARTPTS"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(joined), "-i", A.MASTER, "-filter_complex", f"[1:a]{af}[a]",
                    "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart",
                    a.out], check=True)
    json.dump(sources, open("renders/m5b/m5b_animatic_sources.json", "w"), indent=1)
    print(f"{a.out}: {nframes} frames, {dur:.3f} s")


def share(a):
    out = a.out.replace(".mp4", "_share.mp4")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", a.out, "-c:v", "libx264", "-preset", "slow", "-b:v", "650k",
                    "-maxrate", "900k", "-bufsize", "1800k", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "128k",
                    "-movflags", "+faststart", out], check=True)
    print(out, round(Path(out).stat().st_size / 1e6, 1), "MB")


def sheet(a, out="review/m5b_coverage_sheet.jpg", cols=10, tw=320):
    th = tw * 9 // 16
    want = {s["id"]: (s["start_frame"] + s["end_frame"]) // 2 for s in SUBS}
    cap = cv2.VideoCapture(a.out)
    tiles = []
    for s in SUBS:
        cap.set(cv2.CAP_PROP_POS_FRAMES, want[s["id"]])
        ok, f = cap.read()
        im = cv2.resize(f, (tw, th), interpolation=cv2.INTER_AREA)
        bar = np.full((22, tw, 3), 24, np.uint8)
        t = f"{s['id']}  {s['seconds']:.1f} s  {s['framing']}"
        cv2.putText(bar, t, (5, 16), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (240, 240, 240), 1, cv2.LINE_AA)
        tiles.append(np.vstack([bar, im]))
    while len(tiles) % cols:
        tiles.append(np.full_like(tiles[0], 24))
    rows = [np.hstack(tiles[i:i + cols]) for i in range(0, len(tiles), cols)]
    cv2.imwrite(out, np.vstack(rows), [cv2.IMWRITE_JPEG_QUALITY, 88])
    print(out, len(SUBS), "tiles")


def check(a):
    """Every planned cut vs the output: the review label changes exactly there (label strip differs), and the picture
    changes there (the largest frame difference within +-2 frames of the cut)."""
    cap = cv2.VideoCapture(a.out)
    prev, diffs, strips = None, [], []
    while True:
        ok, f = cap.read()
        if not ok:
            break
        g = cv2.cvtColor(cv2.resize(f, (240, 135)), cv2.COLOR_BGR2GRAY).astype(np.float32)
        diffs.append(0.0 if prev is None else float(np.abs(g - prev).mean()))
        strips.append(cv2.cvtColor(f[4:24, 300:660], cv2.COLOR_BGR2GRAY).astype(np.float32))
        prev = g
    n = len(diffs)
    bad = []
    rows = []
    for s in SUBS[1:]:
        c = s["start_frame"]
        lab = float(np.abs(strips[c] - strips[c - 1]).mean())
        win = range(max(1, c - 2), min(n, c + 3))
        pk = max(win, key=lambda k: diffs[k])
        rows.append((s["id"], c, pk - c, round(diffs[c], 1), round(lab, 1)))
        if pk != c and s.get("xfade_in") is None:
            bad.append((s["id"], c, pk))
    print(f"{a.out}: {n} frames; {len(SUBS) - 1} planned cuts")
    for r in rows:
        print("  %-11s frame %5d  peak at %+d  diff %5.1f  label change %5.1f" % r)
    print("cuts whose biggest picture change is not on the planned frame:", bad or "none")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=OUT)
    ap.add_argument("--only", default="")
    ap.add_argument("--reuse", action="store_true")
    ap.add_argument("--share", action="store_true")
    ap.add_argument("--sheet", action="store_true")
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    if a.share:
        share(a)
    elif a.sheet:
        sheet(a)
    elif a.check:
        check(a)
    else:
        main_run(a)


if __name__ == "__main__":
    main()
