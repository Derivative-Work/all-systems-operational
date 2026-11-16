"""M5c review (M5c2): the performance animatic after the review fixes (human interventions 15: the instruments on Ever
Present's neck, wrists in range, no clipping): review/m5c2_animatic.mp4, same cut and length as M5c.

scripts/m5c_animatic.py with M5c2's paths: the frames blender/coverage_m5c.py re-renders into renders/m5c2/frames/
(the builds with a band or crowd); segments in renders/m5c2/segments/. A segment none of whose sub-shots was
re-rendered (the Remotion and composite shots, O07, O22) is M5c's own segment, hard-linked from renders/m5c/segments/
(identical content, no re-encode). M5c's outputs are untouched.
Also: --share (h264 650 kb/s, AAC 128k), --sheet (the coverage contact sheet), --check (cuts vs the plan), and
--perfsheet (tiles blender/perf_sheet.py --closeup stills into review/m5c2_performance_sheet.jpg).
Usage: .venv/bin/python -I scripts/m5c2_animatic.py [--out review/m5c2_animatic.mp4]
       .venv/bin/python -I scripts/m5c2_animatic.py --share | --check | --perfsheet
"""
import argparse
import os
import json
import subprocess
import sys
from pathlib import Path

import cv2
import numpy as np

sys.path.insert(0, "scripts")
import m5b_animatic as M  # noqa: E402

A = M.A
M.COV = json.load(open("config/coverage_m5c.json"))
M.SUBS = M.COV["subs"]
M.FR = Path("renders/m5c2/frames")
A.SEG = Path("renders/m5c2/segments")
M5C_SEG = Path("renders/m5c/segments")
M.OUT = OUT = "review/m5c2_animatic.mp4"


def main_run(a):
    """M5b's main_run with M5c's file names."""
    A.SEG.mkdir(parents=True, exist_ok=True)
    only = set(filter(None, a.only.split(",")))
    keys, sources = [], {}
    for sid in A.order():
        seg = A.SEG / f"{sid}.mp4"
        subs = [x["id"] for x in M.subs_of(sid)]
        if not any((M.FR / x).is_dir() for x in subs) and (M5C_SEG / f"{sid}.mp4").exists():
            if not seg.exists():
                os.link(M5C_SEG / f"{sid}.mp4", seg)           # nothing re-rendered in it: M5c's segment as is
            keys.append(sid)
            sources[sid] = "M5c segment (unchanged)"
            print(f"{sid:5s} M5c segment, unchanged", flush=True)
            continue
        if (only and sid not in only) or (a.reuse and seg.exists() and sid not in only):
            keys.append(sid)
            continue
        how, n = M.build(sid)
        keys.append(sid)
        sources[sid] = how
        print(f"{sid:5s} {n:4d} f  {len(M.subs_of(sid))} shots  {how}", flush=True)
    if only and not a.reuse:
        return
    for name, comp, n in A.END:
        seg = A.SEG / f"end_{comp}.mp4"
        if not seg.exists() and (M5C_SEG / f"end_{comp}.mp4").exists():
            os.link(M5C_SEG / f"end_{comp}.mp4", seg)
        if not seg.exists():
            fr = A.read_video(A.REM / f"{comp}.mp4", n)
            A.write(A.label(fr, f"{name}  remotion"), seg)
        keys.append(f"end_{comp}")
    lst = A.SEG / "list_m5c2.txt"
    lst.write_text("".join(f"file '{(A.SEG / (k + '.mp4')).resolve()}'\n" for k in keys))
    joined = A.SEG / "joined_m5c2.mp4"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", str(joined)],
                   check=True)
    nframes = int(subprocess.run(["ffprobe", "-v", "error", "-count_frames", "-select_streams", "v:0", "-show_entries",
                                  "stream=nb_read_frames", "-of", "csv=p=0", str(joined)], capture_output=True,
                                 text=True).stdout.strip())
    dur = nframes / A.FPS
    lead = A.TS["lead_in_s"]
    af = f"adelay={int(round(lead * 1000))}:all=1,apad=whole_dur={dur:.3f},atrim=start=0:end={dur:.3f},asetpts=PTS-STARTPTS"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(joined), "-i", A.MASTER, "-filter_complex", f"[1:a]{af}[a]",
                    "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart",
                    a.out], check=True)
    json.dump(sources, open("renders/m5c2/m5c2_animatic_sources.json", "w"), indent=1)
    print(f"{a.out}: {nframes} frames, {dur:.3f} s")


def perfsheet(src="renders/m5c2/perf_sheet/sheet.json", out="review/m5c2_performance_sheet.jpg", tw=200):
    man = json.load(open(src))
    rows = []
    th = None
    for row in man["rows"]:
        tiles = []
        for t in row["tiles"]:
            im = cv2.imread(t["file"])
            th = th or int(im.shape[0] * tw / im.shape[1])
            im = cv2.resize(im, (tw, th), interpolation=cv2.INTER_AREA)
            bar = np.full((40, tw, 3), 24, np.uint8)
            cv2.putText(bar, f"{t['beat']} {t['t']:.2f}s f{t['frame']}", (3, 15), cv2.FONT_HERSHEY_SIMPLEX, 0.36,
                        (235, 235, 235), 1, cv2.LINE_AA)
            cv2.putText(bar, " ".join(t["hits"]) or "-", (3, 33), cv2.FONT_HERSHEY_SIMPLEX, 0.38, (90, 210, 255), 1,
                        cv2.LINE_AA)
            tiles.append(np.vstack([bar, im]))
        lab = np.full((tiles[0].shape[0], 130, 3), 24, np.uint8)
        for k, w in enumerate(row["who"].split("_")):
            cv2.putText(lab, w, (8, 40 + 26 * k), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (240, 240, 240), 1, cv2.LINE_AA)
        rows.append(np.hstack([lab] + tiles))
    head = np.full((34, rows[0].shape[1], 3), 24, np.uint8)
    cv2.putText(head, f"M5c2 performances (after the M5c review): bar {man['bar']} ({man['section']}), build {man['build']}, one frame per sixteenth; "
                      "hits on the frame from timing/music_map.json", (8, 23), cv2.FONT_HERSHEY_SIMPLEX, 0.6,
                (240, 240, 240), 1, cv2.LINE_AA)
    cv2.imwrite(out, np.vstack([head] + rows), [cv2.IMWRITE_JPEG_QUALITY, 88])
    print(out, len(rows), "rows")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=OUT)
    ap.add_argument("--only", default="")
    ap.add_argument("--reuse", action="store_true")
    ap.add_argument("--share", action="store_true")
    ap.add_argument("--sheet", action="store_true")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--perfsheet", nargs="?", const="renders/m5c2/perf_sheet/sheet.json")
    ap.add_argument("--perfsheet-out", default="review/m5c2_performance_sheet.jpg")
    a = ap.parse_args()
    if a.share:
        M.share(a)
    elif a.sheet:
        M.sheet(a, out="review/m5c2_coverage_sheet.jpg")
    elif a.check:
        M.check(a)
    elif a.perfsheet:
        perfsheet(a.perfsheet, a.perfsheet_out)
    else:
        main_run(a)


if __name__ == "__main__":
    main()
