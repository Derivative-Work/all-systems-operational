"""M7: generated clips that replace a Blender sub-shot in the M7 assembly (config/look_m7.json m7c.clip_subs; not
rendered by blender/coverage_m7.py), slotted as scripts/animatic.py slots O06's clip into its shot: the take read by
time (24 -> 30 fps, no interpolation, from its first frame), scaled to cover and centre-cropped, trimmed to the
sub-shot's length; then graded as the shot round it (scripts/grade.py).

O22d (brief: "fog drifting over the skyline"; human interventions 19 and 22): the picked LTX-2.3 take of the far plate
(config/m7c_plate.json o22d.pick, from scripts/m7c_plate.py --o22d), 1280x704 upscaled with Lanczos to cover the frame
(1920x1080: 1964x1080, centre-cropped), the home-movie grade (O22d comes after "Remember Wednesday"), grain seeded per
video frame (config/seeds.json main + the frame), as every graded M7 frame.
Usage (a check): .venv/bin/python -I scripts/m7_inserts.py O22d out_dir [--size 960x540]   (writes graded PNGs)
"""
import json
import subprocess
import sys
from pathlib import Path

import cv2
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import grade as G  # noqa: E402

FPS = 30
SUBS = {s["id"]: s for s in json.loads((ROOT / "config/coverage_m5c.json").read_text())["subs"]}
PLATE = json.loads((ROOT / "config/m7c_plate.json").read_text())


def read_clip(path, size):
    w, h = size
    vf = f"scale={w}:{h}:force_original_aspect_ratio=increase:flags=lanczos,crop={w}:{h}"
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-vf", vf, "-f", "rawvideo", "-pix_fmt", "bgr24", "-"],
                         check=True, capture_output=True).stdout
    return list(np.frombuffer(raw, np.uint8).reshape(-1, h, w, 3).copy())


def o22d(size=(1920, 1080), graded=True, pick=None):
    """(frames, description): O22d's frames for the M7 assembly, graded home unless graded=False."""
    s = SUBS["O22d"]
    n = s["frames"]
    take = pick or PLATE["o22d"]["pick"]
    src = read_clip(ROOT / "assets/gen/clips/O22d" / f"{take}.mp4", size)
    fps_in = PLATE["o22d"]["fps"]
    out = [src[min(len(src) - 1, int(round(i / FPS * fps_in)))] for i in range(n)]
    if graded:
        out = [G.grade(f, "home", s["start_frame"] + i) for i, f in enumerate(out)]
    return out, f"clip {take} (LTX-2.3 of the far plate), {fps_in} -> {FPS} fps by time, Lanczos to {size[0]}x{size[1]}, home grade"


INSERTS = {"O22d": o22d}


def main():
    sid, out = sys.argv[1], Path(sys.argv[2])
    size = (1920, 1080)
    if "--size" in sys.argv:
        size = tuple(int(v) for v in sys.argv[sys.argv.index("--size") + 1].split("x"))
    out.mkdir(parents=True, exist_ok=True)
    frames, how = INSERTS[sid](size)
    for i, f in enumerate(frames):
        cv2.imwrite(str(out / f"{i + 1:04d}.png"), f)
    print(f"{sid}: {len(frames)} frames, {how} -> {out}")


if __name__ == "__main__":
    main()
