"""M5c performance sheet: each band member and three crowd members through one bar of chorus 1 (bar 30, 69.78-72.19 s,
O09's build), one frame per sixteenth, so the strums, the kick, the tambourine, the claps and the lean-ins can be
checked against the music map on stills (like Ever Present's blender/ep/motion_sheet.py).

Built as blender/coverage_m5c.py builds O09 (M5's room and events, then blender/perf_band.py and
blender/perf_crowd.py); for the sheet only, each performer is shown alone (everyone else hidden), lit from the
front by a soft fill, from a fixed three-quarter camera. Tiles: renders/m5c/perf_sheet/<who>_<k>.png and
renders/m5c/perf_sheet/sheet.json (what each tile shows and which hits fall on its frame); scripts/m5c_animatic.py
--perfsheet tiles them into review/m5c_performance_sheet.jpg.
Usage: blender -b --factory-startup --python blender/perf_sheet.py -- [--bar 30] [--out renders/m5c/perf_sheet]
       [--closeup]  (M5c review: M5c2's sheet, renders/m5c2/perf_sheet, adds the crowd clapper at 3x)
"""
import argparse
import json
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE / "ep"))
import coverage_m5c  # noqa: E402,F401  (patches coverage for M5c)
import coverage as C  # noqa: E402
import aso_kit as K  # noqa: E402
import gb  # noqa: E402
import perf as PF  # noqa: E402
import perf_band as PB  # noqa: E402
import perf_crowd as PC  # noqa: E402
import sets as S  # noqa: E402

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
ap = argparse.ArgumentParser()
ap.add_argument("--bar", type=int, default=30)
ap.add_argument("--build", default="O09")
ap.add_argument("--out", default="renders/m5c/perf_sheet")
ap.add_argument("--closeup", action="store_true", help="add the crowd clapper's hands at 3x (M5c review)")
a = ap.parse_args(argv)
out = C.ROOT / a.out
out.mkdir(parents=True, exist_ok=True)

b = a.build
n = C.A.nframes(b)
keys, expo, notes = C.A.shot(b, n)
room = "live"
PF.BUILD[0] = b
notes.append(PB.perform(b, n)[0])
notes.append(PC.perform(b, n, room))
print("; ".join(notes), flush=True)
K.render_settings((400, 500), 16, 0.0)
sc = bpy.context.scene
sc.render.fps = 30
bar = C.BARS[a.bar]
beats = [t for t in C.BEATS if bar["start"] - 0.01 <= t < bar["end"] + 0.3][:5]
eighths = [beats[k // 4] + (beats[k // 4 + 1] - beats[k // 4]) * (k % 4) / 4 for k in range(16)]   # sixteenths
base = C.song_t(b, 1)
fr = [int(round((t - base) * 30)) + 1 for t in eighths]

band = S.OBJ["band"]
people = {f"band_{r}": band[r] for r in ("guitar", "banjo", "kick", "tamb", "singer")}
crowd = PC.instances()


def pick(pose, cond=lambda e: True):
    c = [e for e in crowd if e.get("pose") == pose and cond(e)]
    return c[0] if c else None


for nm, e in (("crowd_clap", pick("clap")), ("crowd_fist", pick("fist")), ("crowd_stand", pick("stand"))):
    if e is not None:
        people[nm] = e
if a.closeup and "crowd_clap" in people:          # M5c review: the clapper's hands at 3x, so wrists can be judged
    people["crowd_clap_3x"] = people["crowd_clap"]
allp = [o for o in bpy.data.objects if o.type == "EMPTY" and o.instance_type == "COLLECTION"]
gb.into(None)
K.world("#8a8f94", 0.6)
for o in bpy.data.objects:
    if o.type == "LIGHT":
        o.data.energy *= 0.5


def near(t, times, tol=1.1 / 30):
    return any(abs(t - x) <= tol for x in times)


kick_t = [h["t"] for h in PB.ALL_KICKS]
tamb_t = [h[0] for h in PB.TAMB_H]
strum_t = [h["t"] for h in PB.STRUMS]
manifest = {"bar": a.bar, "section": bar["section"], "build": b, "times": eighths, "frames": fr, "rows": []}
for nm, e in people.items():
    for o in allp:
        o.hide_render = o is not e
    mw = e.matrix_world
    fwd = (mw.to_3x3() @ Vector((0, -1, 0))).normalized()
    left = (mw.to_3x3() @ Vector((1, 0, 0))).normalized()
    p = mw.translation
    if nm == "band_kick":                       # the pedal side: right leg, footboard, beater, batter head
        loc = p + fwd * 0.3 - left * 1.15 + Vector((0, 0, 0.6))
        tgt = p + fwd * 0.6 + Vector((0, 0, 0.28))
        lens = 40
    else:                                       # head to hips, whatever the person's height
        sc.frame_set(fr[0])
        hz = C.bone_world(e, "Head").z
        tgt = p + fwd * 0.2 + Vector((0, 0, hz - p.z - 0.38))
        loc = tgt + fwd * 2.3 - left * 0.7 + Vector((0, 0, 0.12))
        lens = 70
        if nm.endswith("_3x"):                  # the same camera, three times the focal length, on the hands
            tgt = p + fwd * 0.3 + Vector((0, 0, hz - p.z - 0.33))
            loc = tgt + fwd * 2.3 - left * 0.7 + Vector((0, 0, 0.12))
            lens = 210
    cam = gb.camera(f"sheet_{nm}", tuple(loc), tuple(tgt), lens)
    cam.data.clip_start = 0.05
    lt = K.area(f"sheet_fill_{nm}", tuple(loc + Vector((0, 0, 0.8)) + left * 0.6), tuple(tgt), 260, 2.0, "#ffffff")
    sc.camera = cam
    sc.view_settings.exposure = K.LOOK["exposure"] + 0.3
    row = {"who": nm, "tiles": []}
    for k, (t, f) in enumerate(zip(eighths, fr)):
        sc.frame_set(f)
        path = out / f"{nm}_{k}.png"
        sc.render.filepath = str(path)
        bpy.ops.render.render(write_still=True)
        hits = []
        if near(t, kick_t):
            hits.append("kick")
        if near(t, tamb_t):
            hits.append("tamb")
        if near(t, strum_t):
            hits.append("strum")
        if near(t, C.BACKBEAT):
            hits.append("clap")
        if near(t, C.HEYS, 0.12):
            hits.append("Hey!")
        rp = path.relative_to(C.ROOT) if path.is_relative_to(C.ROOT) else path
        row["tiles"].append({"file": str(rp), "t": round(t, 3), "frame": f,
                             "beat": f"{a.bar}.{1 + k // 4}{['', 'e', '&', 'a'][k % 4]}", "hits": hits})
    lt.hide_render = True
    manifest["rows"].append(row)
    print("sheet", nm, flush=True)


# ---- timing, by frame, over the whole build: do the hits land on the music map's frames?
def frame_of(t):
    return int(round((t - base) * 30)) + 1


beater = S.OBJ["beater"]
fc = next(f for f in C.A._fcurves(beater.animation_data.action) if f.data_path == "rotation_euler")
off = []
for t in [h["t"] for h in PB.ALL_KICKS]:
    f = frame_of(t)
    if 6 <= f <= n - 6:
        vals = {g: fc.evaluate(g) for g in range(f - 4, f + 5)}
        off.append(max(vals, key=vals.get) - f)            # the beater is most forward (largest X) at the strike
gb_ = S.OBJ["perf_band"]["guitar"]
rec = PF.REG[gb_["rig"].name]
perp0 = gb_["info"]["ins"].D((0, 1, 0))          # across the strings (M5c review: the rebuilt guitar's frame)
hy = []
for f in range(1, n + 1):
    body = PF.rec_pose(rec, f - 1)
    rel = body.M("Spine") @ PB.gbody_spine_inv(body)
    perp = rel.to_3x3() @ perp0
    hy.append(body.tail("RightHand").dot(perp) - body.head("Spine").dot(perp))
import numpy as np
hy = np.array(hy)
mid = (hy.max() + hy.min()) / 2
cross = [i + 1 for i in range(1, n) if (hy[i - 1] - mid) * (hy[i] - mid) <= 0]
soff = []
for h in PB.STRUMS:
    f = frame_of(h["t"])
    if 3 <= f <= n - 3 and cross:
        c = min(cross, key=lambda x: abs(x - f))
        soff.append(c - f)
tb = S.OBJ["tambourine"]
trig = tb.parent
trec = PF.REG[trig.name]
tz = []
for f in range(1, n + 1):
    body = PF.rec_pose(trec, f - 1)
    tz.append(body.tail("RightHand").z)
tz = np.array(tz)
toff = []
for th, sw, slap in PB.TAMB_H:
    f = frame_of(th)
    if slap and 6 <= f <= n - 6:
        toff.append(int(np.argmin(tz[f - 5:f + 6])) - 5)


def summ(xs):
    xs = np.array(xs)
    return {"n": int(len(xs)), "on_frame": int((xs == 0).sum()), "within_1": int((np.abs(xs) <= 1).sum()),
            "median": float(np.median(xs)) if len(xs) else None, "worst": int(np.abs(xs).max()) if len(xs) else None}


manifest["timing"] = {"build": b, "beater_most_forward_vs_kick_frame": summ(off),
                      "strum_hand_crossing_vs_strum_onset_frame": summ(soff),
                      "tambourine_lowest_vs_slap_frame": summ(toff)}
print("TIMING", json.dumps(manifest["timing"]), flush=True)
(out / "sheet.json").write_text(json.dumps(manifest, indent=1))
print("wrote", out / "sheet.json")
