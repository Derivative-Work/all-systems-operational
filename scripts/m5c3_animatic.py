"""M5c review 2 (M5c3): the performance animatic after the second round of M5c notes (human interventions 16: the
strumming arms down, the guitarist and banjo player recast, the fretting hands round the necks, palms meeting in the
claps, the disclosure at the end only): review/m5c3_animatic.mp4, same cut and length as M5c2.

scripts/m5c2_animatic.py with M5c3's paths: the frames blender/coverage_m5c.py re-renders into renders/m5c3/frames/,
segments in renders/m5c3/segments/. A segment none of whose sub-shots was re-rendered is M5c2's own (hard-linked from
renders/m5c2/segments/, itself M5c's where M5c2 linked it). O17 has no disclosure panel (decisions 18; it is
re-rendered anyway). The end sequence: the disclosure card is renders/m5c3/remotion/M5-DisclosureCard.mp4 (the
"between 2014 and 2017" wording); the other end cards are M5c2's segments.
Also: --share (h264 650 kb/s, AAC 128k), --sheet (the coverage contact sheet), --check (cuts vs the plan), and
--perfsheet (tiles blender/perf_sheet.py --closeup --hands stills into review/m5c3_performance_sheet.jpg).
Usage: .venv/bin/python -I scripts/m5c3_animatic.py [--out review/m5c3_animatic.mp4]
       .venv/bin/python -I scripts/m5c3_animatic.py --share | --sheet | --check | --perfsheet
"""
import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

import cv2
import numpy as np

sys.path.insert(0, "scripts")
import m5c2_animatic as M2  # noqa: E402

M = M2.M
A = M2.A
M.FR = Path("renders/m5c3/frames")
A.SEG = Path("renders/m5c3/segments")
PREV_SEG = Path("renders/m5c2/segments")
REM3 = Path("renders/m5c3/remotion")
M.OUT = OUT = "review/m5c3_animatic.mp4"


def main_run(a):
    A.SEG.mkdir(parents=True, exist_ok=True)
    keys, sources = [], {}
    for sid in A.order():
        seg = A.SEG / f"{sid}.mp4"
        subs = [x["id"] for x in M.subs_of(sid)]
        if not any((M.FR / x).is_dir() for x in subs) and (PREV_SEG / f"{sid}.mp4").exists():
            if not seg.exists():
                os.link(PREV_SEG / f"{sid}.mp4", seg)           # nothing re-rendered in it: M5c2's segment as is
            keys.append(sid)
            sources[sid] = "M5c2 segment (unchanged)"
            print(f"{sid:5s} M5c2 segment, unchanged", flush=True)
            continue
        if a.reuse and seg.exists():
            keys.append(sid)
            continue
        how, n = M.build(sid)
        keys.append(sid)
        sources[sid] = how
        print(f"{sid:5s} {n:4d} f  {len(M.subs_of(sid))} shots  {how}", flush=True)
    for name, comp, n in A.END:
        seg = A.SEG / f"end_{comp}.mp4"
        if comp == "M5-DisclosureCard":
            if not (a.reuse and seg.exists()):
                fr = A.read_video(REM3 / f"{comp}.mp4", n)
                A.write(A.label(fr, f"{name}  remotion"), seg)
            sources[f"end_{comp}"] = "M5c3 disclosure card (renders/m5c3/remotion)"
        elif not seg.exists():
            os.link(PREV_SEG / f"end_{comp}.mp4", seg)
        keys.append(f"end_{comp}")
    lst = A.SEG / "list_m5c3.txt"
    lst.write_text("".join(f"file '{(A.SEG / (k + '.mp4')).resolve()}'\n" for k in keys))
    joined = A.SEG / "joined_m5c3.mp4"
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
    json.dump(sources, open("renders/m5c3/m5c3_animatic_sources.json", "w"), indent=1)
    print(f"{a.out}: {nframes} frames, {dur:.3f} s")


def perfsheet(src, out, tw=200):
    """M5c2's tiling, with M5c3's header."""
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
    cv2.putText(head, f"M5c3 performances (after the second M5c review): bar {man['bar']} ({man['section']}), build "
                      f"{man['build']}, one frame per sixteenth; hits on the frame from timing/music_map.json; guitar "
                      "person 33, banjo person 36", (8, 23), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (240, 240, 240), 1, cv2.LINE_AA)
    cv2.imwrite(out, np.vstack([head] + rows), [cv2.IMWRITE_JPEG_QUALITY, 88])
    print(out, len(rows), "rows")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=OUT)
    ap.add_argument("--reuse", action="store_true")
    ap.add_argument("--share", action="store_true")
    ap.add_argument("--sheet", action="store_true")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--perfsheet", nargs="?", const="renders/m5c3/perf_sheet/sheet.json")
    ap.add_argument("--perfsheet-out", default="review/m5c3_performance_sheet.jpg")
    a = ap.parse_args()
    if a.share:
        M.share(a)
    elif a.sheet:
        M.sheet(a, out="review/m5c3_coverage_sheet.jpg")
    elif a.check:
        M.check(a)
    elif a.perfsheet:
        perfsheet(a.perfsheet, a.perfsheet_out)
    else:
        main_run(a)


if __name__ == "__main__":
    main()
