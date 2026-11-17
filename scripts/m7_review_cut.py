"""M7 review cut (human interventions 31: "assemble a cut with the frames you already have so I can examine the issues
unrelated to these"): the whole video at 960x540, 30 fps, from the M7 frames as they stand, for review, not the master.
The 1080p master assembly comes later, with 1080p Remotion renders.

The M5c3 assembly (scripts/m5c3_animatic.py -> m5c2 -> m5b -> animatic.py: the cut, the composites, the labels) with
M7's changes:
  frames     renders/m7/frames/<sub>/ (blender/coverage_m7.py), or the first pass in archive/renders/m7/frames_v1/<sub>/
             while a sub-shot is being re-rendered (production log 66); its label says so
  grade      every rendered frame through scripts/grade.py, at 960x540: the cafe warm, O22 home from "Remember
             Wednesday" (per frame, from O22's first mark), the rest grey; grain seeded by the video frame
  O22d       the generated clip (scripts/m7_inserts.py), home grade, in place of the Blender sub-shot
  O04        the phone's screen is rendered in Blender since M7b, so M5's pinned screen is not composited
  O18        M5's caption plus the v1.3 denial tags (renders/m1b/remotion/M7-O18-DenialTags.mov)
  O22        M5's lower third; no M5 home-movie filter (the grade does it)
  Remotion   M5's compositions re-rendered with the current code (renders/m7/remotion_review/, scripts/m5_remotion.sh
             with M5_REMOTION_OUT): the status stamp is v1.3's "Thu 11:15 a.m." (production log 53)
  end        renders/m7/remotion/M7-EndSequence.mp4 (scripts/m7_end.sh) in place of M5's O24 and cards
  audio      the post-filtered v1.3 master from 8.4 s to O24 (video frame 7439), then audio/credits/credits-m7-end.wav
Usage: .venv/bin/python -I scripts/m7_review_cut.py [--out review/m7_cut_v1.mp4]
       .venv/bin/python -I scripts/m7_review_cut.py --share [--share-end-s 18.3]   (h264 650 kb/s, AAC 128k, 960x540,
       from the start to O24 + share-end-s: the end card and "Next incident: TBD"; the cards after are as the preview)
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

import cv2
import numpy as np

sys.path.insert(0, "scripts")
import grade as G  # noqa: E402
import m5c2_animatic as M2  # noqa: E402  (sets the M5c coverage plan on m5b)
import m7_inserts as MI  # noqa: E402

M = M2.M
A = M2.A
W, H, FPS = A.W, A.H, A.FPS
FR = Path("renders/m7/frames")
FIRST = Path("archive/renders/m7/frames_v1")
A.SEG = Path("renders/m7/review_segments")
A.REM = Path("renders/m7/remotion_review")
END_MP4 = Path("renders/m7/remotion/M7-EndSequence.mp4")
TAGS = Path("renders/m1b/remotion/M7-O18-DenialTags.mov")
SONG = "audio/postfilter/all-systems-operational-master-deslopped.wav"       # v1.3, post-filtered (production log 52)
CREDITS = "audio/credits/credits-m7-end.wav"                                  # production log 62
O24_FRAME = A.SHOTS["O24"]["start_frame"]
LOOK_M7 = json.loads(Path("config/look_m7.json").read_text())
CLIP_SUBS = set(LOOK_M7["m7c"]["clip_subs"])
LOOK = {"live": "grey", "cafe": "cafe", "treehouse": "grey", "park": "grey", "void": "grey"}
HOME_FROM = A.SHOTS["O22"]["start_frame"] + A.mark("O22", 0)
OUT = "review/m7_cut_v1.mp4"
SOURCES = {}
PENDING = set()          # --pending: sub-shots whose frames on disk are still the first pass, fix queued


def frames_of(s, extra=0):
    """M5b's reader for M7: a sub-shot's frames (plus its dissolve pre-roll), resized and graded."""
    sid = s["id"]
    n = s["frames"] + extra
    if sid in CLIP_SUBS:
        fr, how = MI.o22d((W, H))
        SOURCES[sid] = how
        return fr
    files = sorted((FR / sid).glob("[0-9]*.jpg"))
    src = "M7 render"
    if len(files) != n:
        files = sorted((FIRST / sid).glob("[0-9]*.jpg"))
        src = "M7 first pass (being re-rendered)"
    if len(files) != n:
        raise SystemExit(f"{sid}: {len(files)} frames, {n} needed")
    if sid in PENDING:
        src = "M7 first pass (being re-rendered)"
    SOURCES[sid] = src
    v0 = s["start_frame"] - extra
    out = []
    for i, f in enumerate(files):
        im = cv2.resize(cv2.imread(str(f)), (W, H), interpolation=cv2.INTER_AREA)
        vf = v0 + i
        look = "home" if s["shot"] == "O22" and vf >= HOME_FROM else LOOK[s["room"]]
        out.append(G.grade(im, look, vf))
    return out


M.frames_of = frames_of


def label_subs(frames, shot, how):
    s0 = A.SHOTS[shot]["start_frame"] if shot in A.SHOTS else None
    for s in M.subs_of(shot):
        a, b = s["start_frame"] - s0, s["end_frame"] - s0
        cam = s.get("camera") or s["source"]
        first = "  [first pass]" if SOURCES.get(s["id"], "").startswith("M7 first pass") else ""
        A.label(frames[a:b], f"{s['id']}  {s['framing']}: {cam}{first}" if s["source"] == "blender" else f"{s['id']}  {how}")
    return frames


M.label_subs = label_subs
A.o04 = lambda n: (A.blender("O04", n), "blender motion (the phone's screen rendered in Blender, M7b)")
_segment = A.segment


def segment(sid, o07="server"):
    if sid == "O18":
        n = A.nfr(sid)
        fr = A.over(A.blender(sid, n), A.overlay("M5-Dramatization", n))
        fr = A.over(fr, A.read_video(TAGS, n, pix="bgra"))
        return fr, "blender motion (v1.3 board) + caption + denial tags"
    if sid == "O22":
        n = A.nfr(sid)
        return A.over(A.blender(sid, n), A.overlay("M5-O22-LT", n)), "blender motion (walk-off), O22d clip, graded + lower third"
    return _segment(sid, o07)


A.segment = segment


def encode_end(seg):
    """The end sequence at 960x540, encoded as A.write encodes, so the segments concatenate without re-encoding."""
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(END_MP4), "-vf", f"scale={W}:{H}:flags=area,fps={FPS}",
                    "-an", "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p",
                    "-video_track_timescale", "15360", str(seg)], check=True)


def main_run(a):
    A.SEG.mkdir(parents=True, exist_ok=True)
    keys, how_of = [], {}
    for sid in A.order():
        how, n = M.build(sid)
        keys.append(sid)
        how_of[sid] = how
        print(f"{sid:5s} {n:4d} f  {len(M.subs_of(sid))} shots  {how}", flush=True)
    seg = A.SEG / "end_M7.mp4"
    encode_end(seg)
    keys.append("end_M7")
    lst = A.SEG / "list.txt"
    lst.write_text("".join(f"file '{(A.SEG / (k + '.mp4')).resolve()}'\n" for k in keys))
    joined = A.SEG / "joined.mp4"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", str(joined)],
                   check=True)
    nframes = int(subprocess.run(["ffprobe", "-v", "error", "-count_frames", "-select_streams", "v:0", "-show_entries",
                                  "stream=nb_read_frames", "-of", "csv=p=0", str(joined)], capture_output=True,
                                 text=True).stdout.strip())
    dur, t24 = nframes / FPS, O24_FRAME / FPS
    lead = A.TS["lead_in_s"]
    af = (f"[1:a]aformat=sample_rates=48000:channel_layouts=stereo,adelay={int(round(lead * 1000))}:all=1,"
          f"apad=whole_dur={t24:.4f},atrim=start=0:end={t24:.4f},asetpts=PTS-STARTPTS[s];"
          f"[2:a]aformat=sample_rates=48000:channel_layouts=stereo,asetpts=PTS-STARTPTS[c];"
          f"[s][c]concat=n=2:v=0:a=1,apad=whole_dur={dur:.4f},atrim=end={dur:.4f}[a]")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(joined), "-i", SONG, "-i", CREDITS, "-filter_complex", af,
                    "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart",
                    a.out], check=True)
    json.dump({"shots": how_of, "subs": SOURCES}, open("renders/m7/review_cut_sources.json", "w"), indent=1)
    first = sorted(k for k, v in SOURCES.items() if v.startswith("M7 first pass"))
    print(f"{a.out}: {nframes} frames, {dur:.3f} s; first-pass frames in: {', '.join(first) or 'none'}")


def share(a):
    out = a.out.replace(".mp4", "_share.mp4")
    end = O24_FRAME / FPS + a.share_end_s
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", a.out, "-t", f"{end:.3f}", "-c:v", "libx264", "-preset", "slow",
                    "-b:v", "650k", "-maxrate", "900k", "-bufsize", "1800k", "-pix_fmt", "yuv420p", "-c:a", "aac",
                    "-b:a", "128k", "-movflags", "+faststart", out], check=True)
    print(out, f"0-{end:.1f} s,", round(Path(out).stat().st_size / 1e6, 1), "MB")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=OUT)
    ap.add_argument("--share", action="store_true")
    ap.add_argument("--share-end-s", type=float, default=18.3)
    ap.add_argument("--pending", default="", help="sub-shots to label first pass")
    a = ap.parse_args()
    PENDING.update(filter(None, a.pending.split(",")))
    if a.share:
        share(a)
    else:
        main_run(a)


if __name__ == "__main__":
    main()
