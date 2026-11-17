"""M7 check: is anything right at the lens? (production log 66: O08a's camera started inside the live room's floor-lamp
shade, a wipe nobody caught from M5 to M7.) Builds each sub-shot exactly as blender/coverage_m7.py does, then, after
its camera is keyed, casts a grid of rays (5 across, 3 down) from the camera through the frame on every frame
(--step) and records the nearest hit per ray. A sub-shot is flagged when any ray hits something nearer than --near.
Writes one JSON line per sub-shot to --report: frames checked, frames with a near hit, the most rays near in any one
frame (out of 15), the nearest distance and its frame, the objects hit near, and the camera's clip start (anything
nearer than that isn't drawn, which is why a near object can slide out of the picture as the camera moves).
Renders only a tiny still per sub-shot (the coverage machinery renders after the hook); pass --out to a scratch folder.
Usage: blender -b --factory-startup --python blender/camera_clearance.py -- --only O20,O22 --still --at first
       --size 320x180 --out <scratch> --log <scratch>/pose.log --report log/render_logs/m7_camera_clearance.jsonl
       [--step 1] [--near 0.25] [--ignore rain,drop]
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))


def _opt(name, default=None):
    if name in sys.argv:
        i = sys.argv.index(name)
        v = sys.argv[i + 1]
        del sys.argv[i:i + 2]
        return v
    return default


REPORT = Path(_opt("--report", "log/render_logs/m7_camera_clearance.jsonl"))
STEP = int(_opt("--step", "1"))
NEAR = float(_opt("--near", "0.25"))
IGNORE = [s for s in _opt("--ignore", "").split(",") if s]

import bpy  # noqa: E402
import coverage_m7 as M7  # noqa: E402  (its __main__ doesn't run)

C = M7.C
_orig = C.CAMERA_HOOK
GRID = [(u, v) for v in (0.1, 0.5, 0.9) for u in (0.05, 0.275, 0.5, 0.725, 0.95)]


def hook(cam, sub, b, f0, f1):
    if _orig:
        _orig(cam, sub, b, f0, f1)
    sc = bpy.context.scene
    rec = {"sub": sub["id"], "build": b, "camera": sub.get("camera"), "frames": 0, "near_frames": 0, "max_rays": 0,
           "min_d": None, "min_f": None, "objects": {}, "clip_start": round(cam.data.clip_start, 4)}
    for f in range(f0, f1, STEP):
        sc.frame_set(f)
        dg = bpy.context.evaluated_depsgraph_get()
        mw = cam.matrix_world
        o = mw.translation.copy()
        tr, br, bl, tl = [mw @ v for v in cam.data.view_frame(scene=sc)]
        n_near = 0
        for u, v in GRID:
            p = tl.lerp(tr, u).lerp(bl.lerp(br, u), v)
            d_ = (p - o).normalized()
            org = o
            for _ in range(4):                      # step past ignored objects
                ok, loc, _n, _i, obj, _m = sc.ray_cast(dg, org, d_)
                if not ok or not any(k in obj.name for k in IGNORE):
                    break
                org = loc + d_ * 1e-4
            if not ok:
                continue
            dist = (loc - o).length
            if rec["min_d"] is None or dist < rec["min_d"]:
                rec["min_d"], rec["min_f"] = round(dist, 4), f - f0 + 1
            if dist < NEAR:
                n_near += 1
                rec["objects"][obj.name] = min(rec["objects"].get(obj.name, 9.0), round(dist, 4))
        rec["frames"] += 1
        rec["near_frames"] += n_near > 0
        rec["max_rays"] = max(rec["max_rays"], n_near)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    with REPORT.open("a") as fh:
        fh.write(json.dumps(rec) + "\n")
    print(f"CLEARANCE {sub['id']}: {rec['near_frames']}/{rec['frames']} frames near (<{NEAR} m), max {rec['max_rays']}/15 "
          f"rays, min {rec['min_d']} m at frame {rec['min_f']}, {rec['objects']}", flush=True)


C.CAMERA_HOOK = hook
if __name__ == "__main__":
    C.main()
