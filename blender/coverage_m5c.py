"""M5c: render the coverage plan with the performances (plan M5c; decisions 15): blender/coverage.py (M5b) unchanged,
run with
- config/coverage_m5c.json (scripts/coverage_m5c.py: M5b's plan, same cuts, nine repeated closes swapped);
- the band and crowd motion replaced by blender/perf_band.py and blender/perf_crowd.py (holds, grips and
  stem-driven performances on each person's own rig copy), the freezes holding the performers' poses at the stop
  (seeded as the shot before, so O20j's last frame and O21 match), the O22 walker on a planted-foot gait;
- band-relative camera presets ("kind": "band": loc and target in a band member's figure frame);
- cameras that aim at a person's hands read the solved pose (perf.REG), not the rig's rest state;
- the pose rules checked on every solved frame: log/render_logs/m5c_pose_check.log (and the walker's feet).
Seeds: as M5b, plus gb.rng("m5c_band_<build>"), gb.rng("m5c_crowd_<build>"), gb.rng("m5c_chords").
Usage: blender -b --factory-startup --python blender/coverage_m5c.py -- [--out renders/m5c/frames] [--only O09]
       [--subs O09d,O20d] [--still] [--at mid]
"""
import json
import sys
from pathlib import Path

import bpy
from mathutils import Vector

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE / "ep"))
import coverage as C  # noqa: E402
import gb  # noqa: E402
import perf as PF  # noqa: E402
import perf_band as PB  # noqa: E402
import perf_crowd as PC  # noqa: E402
import sets as S  # noqa: E402

C.COV = json.loads((C.ROOT / "config" / "coverage_m5c.json").read_text())
FREEZE_AT = {"O12": ("O11", 93.80 - 1 / 30), "O21": ("O20", 201.80 - 1 / 30)}
LOG = C.ROOT / "log" / "render_logs" / "m5c_pose_check.log"


def band_motion(b, n):
    PF.BUILD[0] = b
    note, _ = PB.perform(b, n)
    return note


def crowd_motion(b, n, room):
    PF.BUILD[0] = b
    return PC.perform(b, n, room)


C.band_motion = band_motion
C.crowd_motion = crowd_motion

_layers = C.layers


def layers(b, n, room, notes):
    PF.BUILD[0] = b
    if b in FREEZE_AT:
        sb, t = FREEZE_AT[b]
        note, _ = PB.perform(b, n, freeze_t=t, seed_build=sb)
        notes.append(note)
        if b == "O21":
            notes.append(PC.perform(b, n, room, seed_build=sb, freeze_t=t))
    if b == "O22":
        notes.append(PC.walker(b, n))
    _layers(b, n, room, notes)
    if b == "O22":
        fs = PC.foot_slide(b, n)
        PF.REPORT["builds"]["O22 walker feet on the plank (stance frames, max and mean slide per frame, m)"] = \
            {k: (v[0], round(v[1], 4), round(v[2], 4)) for k, v in fs.items()}
        notes.append(f"walker feet: {fs}")
    write_report()


C.layers = layers

_bone_world = C.bone_world


def bone_world(e, bone):
    rig = next(o for o in e.instance_collection.objects if o.type == "ARMATURE")
    rec = PF.REG.get(rig.name)
    if rec is None:
        return _bone_world(e, bone)
    f = bpy.context.scene.frame_current
    body = PF.rec_pose(rec, f - 1)
    p = body.tail(bone) if bone.endswith("Hand") else body.head(bone)
    bpy.context.view_layer.update()
    return e.matrix_world @ (rig.matrix_basis @ p)


C.bone_world = bone_world

_cam_base = C.cam_base


def cam_base(sub, c, b):
    over = sub.get("cam_override") or {}
    c2 = {**c, **over}
    if c2.get("kind") != "band":
        return _cam_base(sub, c, b)
    e = S.OBJ["band"][c2["role"]]
    bpy.context.view_layer.update()
    mw = e.matrix_world
    loc, tgt = mw @ Vector(c2["loc"]), mw @ Vector(c2["target"])
    dof = c2.get("dof")
    focus = None
    if dof:
        fp = dof.get("focus", "target")
        focus = tgt.copy() if fp == "target" else mw @ Vector(fp)
    return dict(loc=loc, tgt=tgt, lens=c2.get("lens", 50), focus=focus, fstop=(dof or {}).get("fstop"), rack=None,
                kind="band", part=None, framing=c2.get("framing", "close"))


C.cam_base = cam_base


def write_report():
    LOG.parent.mkdir(parents=True, exist_ok=True)
    txt = PF.report_text()
    mic = PF.REPORT.get("mic", {})
    if mic:
        txt += "\nclosest mouth to mic grille per build and singer (m, s): " + "; ".join(
            f"{k} {v[0]}" for k, v in sorted(mic.items()))
    LOG.write_text(txt + "\n")


if __name__ == "__main__":
    if "--out" not in sys.argv:
        sys.argv += ["--out", "renders/m5c/frames"]
    C.main()
    write_report()
    print(PF.report_text(), flush=True)
