"""The 1080p master (human interventions 37: "an upload-ready version"): scripts/m7_review_cut.py's assembly at full size
for the upload. The same cut, frames, grade, inserts, overlays, end sequence and audio as the review cut, except:
  size       1920x1080: the M7 frames as rendered (no resize), graded at full size (scripts/grade.py scales its blur,
             halation and grain with the height)
  Remotion   the M5 compositions at full size (M5_REMOTION_SCALE=1 M5_REMOTION_OUT=renders/m7/remotion_master
             scripts/m5_remotion.sh ...); the end sequence and the O18 denial tags are 1080p already
  labels     none (the review cut's sub-shot labels are for review only)
  video      h264 High, CRF 14, preset slow, yuv420p, per segment, joined without re-encoding
  audio      AAC-LC 384 kb/s, 48 kHz stereo (YouTube's recommendation for stereo)
Usage: .venv/bin/python -I scripts/m7_master.py [--out renders/m7/master/all-systems-operational-master.mp4] [--remux]
"""
import argparse
import subprocess
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, "scripts")
import m7_review_cut as R  # noqa: E402

A, M = R.A, R.M
W, H = 1920, 1080
OUT = "renders/m7/master/all-systems-operational-master.mp4"


def setup():
    R.W, R.H = W, H
    A.W, A.H = W, H
    M.W, M.H = W, H
    d = list(A.read_video.__defaults__)            # (n, pix, size, fill): the size default was bound at 960x540
    d[2] = (W, H)
    A.read_video.__defaults__ = tuple(d)
    A.REM = Path("renders/m7/remotion_master")
    A.SEG = Path("renders/m7/master_segments")
    A.label = lambda frames, text: frames
    A.write = write
    R.AUDIO = ["-c:a", "aac", "-b:a", "384k", "-ar", "48000"]
    R.SOURCES_JSON = "renders/m7/master_sources.json"


def write(frames, path):
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{W}x{H}", "-r",
                          str(A.FPS), "-i", "-", "-c:v", "libx264", "-profile:v", "high", "-preset", "slow", "-crf", "14",
                          "-pix_fmt", "yuv420p", "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709",
                          "-video_track_timescale", "15360", str(path)], stdin=subprocess.PIPE)
    for f in frames:
        if f.shape[:2] != (H, W):
            raise SystemExit(f"{path}: a {f.shape[1]}x{f.shape[0]} frame in the 1080p master")
        p.stdin.write(np.ascontiguousarray(f).tobytes())
    p.stdin.close()
    if p.wait():
        raise SystemExit(f"{path}: ffmpeg failed")


def encode_end(seg):
    """The end sequence (1080p already), re-encoded as the segments are, so they join without re-encoding."""
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(R.END_MP4), "-vf", f"scale={W}:{H}:flags=lanczos,fps={A.FPS}",
                    "-an", "-c:v", "libx264", "-profile:v", "high", "-preset", "slow", "-crf", "14", "-pix_fmt", "yuv420p",
                    "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709",
                    "-video_track_timescale", "15360", str(seg)], check=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=OUT)
    ap.add_argument("--remux", action="store_true", help="only the audio again, on the joined picture already built")
    a = ap.parse_args()
    setup()
    R.encode_end = encode_end
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    if a.remux:
        n, d = R.mux(A.SEG / "joined.mp4", a.out)
        print(f"{a.out}: {n} frames, {d:.3f} s (remuxed)")
        return
    R.main_run(argparse.Namespace(out=a.out, share=False, share_end_s=18.3, pending=""))


if __name__ == "__main__":
    main()
