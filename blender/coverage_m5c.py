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
       blender -b --factory-startup --python blender/coverage_m5c.py -- --checkonly [O09,O17]  (checks, no render)
       --log <path>: the check log (default log/render_logs/m5c_pose_check.log)
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
# M5c review 2 (human interventions 16; decisions 19): the guitarist recast from person 3 to person 33 and the banjo
# player from person 8 to person 36 (blender/cast_probe.py: the real-size guitar and banjo sit on them with the
# strumming arm down and the fretting hand round the neck). Swapped, not moved: 33 and 36 take the band's places and
# 3 and 8 take theirs (33 was O12's late clapper, 36 a treehouse meeting chair; crowd draws by index swap too).
import aso_kit as K  # noqa: E402
K.SWAP.update({3: 33, 33: 3, 8: 36, 36: 8})
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
        # M5c review: O12's crowd frozen in their solved M5c poses too (O11's seeds, as O21 uses O20's), not the
        # library poses; the late clapper claps with the solver's clap
        notes.append(PC.perform(b, n, room, seed_build=sb, freeze_t=t))
        if b == "O12":
            notes.append(PC.late_clapper(b, n, (C.A.mark("O12", 1), C.A.mark("O12", 2))))
    if b == "O22":
        notes.append(PC.walker(b, n))
    for nm in ("pmug0", "pmug1"):                 # the probes' mugs sat 1.8 cm above the table (M3), seen in O14b's close
        mg = bpy.data.objects.get(nm)
        if mg is not None:
            mg.location.z -= 0.018
            notes.append(f"{nm} set down on the table")
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
    if c2.get("reanchor") and c2.get("kind") != "band":
        # M5c review 2: an M5b close on a recast player (fixed in the room): the same direction and distance,
        # re-centred on the player's hand at the sub-shot's middle frame (plus a figure-frame offset)
        base = _cam_base(sub, c, b)
        role, bone, off = c2["reanchor"]
        e = S.OBJ["band"][role]
        bpy.context.scene.frame_set(int((sub["start_frame"] + sub["end_frame"]) / 2 - C.build_vstart(b) + 1))
        p = C.bone_world(e, bone) + e.matrix_world.to_3x3().normalized() @ Vector(off)
        d = p - Vector(base["tgt"])
        base["loc"], base["tgt"] = Vector(base["loc"]) + d, p
        if base.get("focus") is not None:
            base["focus"] = Vector(base["focus"]) + d
        return base
    if c2.get("kind") != "band":
        return _cam_base(sub, c, b)
    e = S.OBJ["band"][c2["role"]]
    bpy.context.view_layer.update()
    mw = e.matrix_world
    loc, tgt = mw @ Vector(c2["loc"]), mw @ Vector(c2["target"])
    if c2.get("anchor"):
        # M5c review 2: loc and target are offsets (figure frame) from a bone of the solved pose at the sub-shot's
        # middle frame, so the close follows the hand whoever plays (the recast players are taller)
        bpy.context.scene.frame_set(int((sub["start_frame"] + sub["end_frame"]) / 2 - C.build_vstart(b) + 1))
        p = C.bone_world(e, c2["anchor"])
        R = mw.to_3x3().normalized()
        loc, tgt = p + R @ Vector(c2["loc"]), p + R @ Vector(c2["target"])
    dof = c2.get("dof")
    focus = None
    if dof:
        fp = dof.get("focus", "target")
        focus = tgt.copy() if fp == "target" or c2.get("anchor") else mw @ Vector(fp)
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


def check_only(only=()):
    """Build every build's performances (no render) for the pose, wrist and contact checks."""
    import time
    order = ["O03", "O04", "O07", "O08", "O08c", "O09", "O10", "O11", "O12", "O14", "O15", "O16", "O17", "O18",
             "O19a", "O19b", "O20", "O21", "O22"]
    by = C.subs_by_build()
    for b in order:
        subs = by.get(b, [])
        if not subs or (only and b not in only):
            continue
        t0 = time.time()
        n = C.A.nframes(b)
        keys, expo, notes = C.A.shot(b, n)
        layers(b, n, subs[0]["room"], notes)
        print(f"check {b}: {n} frames, {time.time() - t0:.1f} s", flush=True)


if __name__ == "__main__":
    if "--log" in sys.argv:
        i = sys.argv.index("--log")
        LOG = C.ROOT / sys.argv[i + 1]
        del sys.argv[i:i + 2]
    if "--checkonly" in sys.argv:
        i = sys.argv.index("--checkonly")
        only = set(filter(None, (sys.argv[i + 1] if len(sys.argv) > i + 1 else "").split(",")))
        check_only(only)
        write_report()
        print(PF.report_text(), flush=True)
        sys.exit(0)
    if "--out" not in sys.argv:
        sys.argv += ["--out", "renders/m5c/frames"]
    C.main()
    write_report()
    print(PF.report_text(), flush=True)
