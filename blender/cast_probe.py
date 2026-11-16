"""M5c review 2 (human interventions 16: "the guitar is comically large for that guitarist. Maybe use a different
player"): try library people on the real-size guitar and banjo (blender/instruments.py, unchanged) with the hold and
grips of blender/perf_grips.py, and measure how each sits: shoulder height, arm and hand lengths, where the body
hangs against the hips, the strumming arm's angles and rest, the fretting hand's wrap and reach at the first frets.
Optionally a front and a three-quarter still of each (test stills: archive/, never in the video).

Usage: blender -b --factory-startup --python blender/cast_probe.py -- --kind guitar --who 3,25,39 [--dz 0.10]
       [--stills archive/review/m5c3_cast] [--out log/render_logs/m5c3_cast_guitar.json]
"""
import argparse
import json
import math
import sys
from pathlib import Path

import bpy
from mathutils import Matrix, Vector

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE / "ep"))
import aso_kit as K  # noqa: E402
import arm_checks as AC  # noqa: E402
import contact as CT  # noqa: E402
import gb  # noqa: E402
import perf as PF  # noqa: E402
import perf_grips as G  # noqa: E402

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
ap = argparse.ArgumentParser()
ap.add_argument("--kind", default="guitar")
ap.add_argument("--who", default="3")
ap.add_argument("--dz", default="")
ap.add_argument("--ang", type=float, default=None)
ap.add_argument("--yaw", type=float, default=None)
ap.add_argument("--tilt", type=float, default=None)
ap.add_argument("--x", type=float, default=None)
ap.add_argument("--strum_dx", type=float, default=None)
ap.add_argument("--flex0", type=float, default=None)
ap.add_argument("--knuckle", default="")
ap.add_argument("--fret_flex", type=float, default=None)
ap.add_argument("--fret_y", default="")
ap.add_argument("--fret_target", default="")
ap.add_argument("--fret_n", default="")
ap.add_argument("--stills", default="")
ap.add_argument("--out", default="")
ap.add_argument("--palms", action="store_true")
a = ap.parse_args(argv)

K.reset()
K.load_people(["stand"])
sc = bpy.context.scene
results = []


def still(tag, e, loc_local, tgt_local):
    sc.render.engine = "BLENDER_EEVEE"
    sc.render.resolution_x, sc.render.resolution_y = 480, 640
    if sc.world is None:
        sc.world = bpy.data.worlds.new("w")
    sc.world.color = (0.32, 0.32, 0.34)
    cam = bpy.data.objects.get("probe_cam") or gb.link(bpy.data.objects.new("probe_cam", bpy.data.cameras.new("c")))
    sun = bpy.data.objects.get("probe_sun") or gb.link(bpy.data.objects.new("probe_sun", bpy.data.lights.new("s", "SUN")))
    sun.data.energy = 3.5
    bpy.context.view_layer.update()
    loc, tgt = e.matrix_world @ Vector(loc_local), e.matrix_world @ Vector(tgt_local)
    cam.location = loc
    cam.rotation_euler = (tgt - loc).to_track_quat("-Z", "Y").to_euler()
    cam.data.lens = 40
    sun.rotation_euler = cam.rotation_euler
    sc.camera = cam
    Path(a.stills).mkdir(parents=True, exist_ok=True)
    sc.render.filepath = str(Path(a.stills) / f"{tag}.png")
    bpy.ops.render.render(write_still=True)


for who in [int(x) for x in a.who.split(",")]:
    for dz in ([float(x) for x in a.dz.split(",")] if a.dz else [G.Instr.FIT[a.kind]["dz"]]):
        gb.into(None)
        for o in list(bpy.data.objects):
            if o.name.startswith(("guitar", "banjo", "probe")) and o.type == "MESH":
                bpy.data.objects.remove(o)
        G.Instr.FIT[a.kind]["dz"] = dz
        if a.fret_flex is not None:
            G.Fretting.LIM["flex"] = a.fret_flex
        if a.fret_target:
            G.FRET_TARGET[0] = a.fret_target
        if a.fret_y:
            G.FRET_Y[:] = [float(v) for v in a.fret_y.split(",")]
        if a.fret_n:
            G.FRET_N[:] = [float(v) for v in a.fret_n.split(",")]
        if a.knuckle:
            G.KNUCKLE[:] = [float(v) for v in a.knuckle.split(",")]
        if a.flex0 is not None:
            G.FLEX0[a.kind] = a.flex0
        if a.strum_dx is not None:
            G.STRUM_DX[a.kind] = a.strum_dx
        for k_ in ("ang", "yaw", "tilt", "x"):
            if getattr(a, k_) is not None:
                G.Instr.FIT[a.kind][k_] = getattr(a, k_)
        e = K.person(f"cand_{who}_{dz}", "stand", (0, 0, 0), math.pi, who=who)
        coll, rig = PF.own_copy(e, f"cand_{who}_{int(dz * 1000)}")
        body = PF.Body(rig)
        obs = CT.body_obstacles(coll, body)
        ins = G.Instr(body, coll, a.kind, obs, a.kind)
        try:
            fr = G.Fretting(body, ins, (1, 2, 3))
            st = G.Strumming(body, ins)
        except RuntimeError as ex:
            print("CASTFAIL", who, dz, ex)
            for o in list(coll.objects):
                bpy.data.objects.remove(o)
            bpy.data.collections.remove(coll)
            bpy.data.objects.remove(e)
            continue
        body.keep()
        PF.apply_static(body, PF.FINGERS)
        for b_ in PF.CORE + PF.ARMS + PF.LEGS:
            pb = rig.pose.bones.get(PF.bn(b_))
            if pb is not None:
                pb.rotation_mode = "QUATERNION"
                pb.matrix_basis = body.basis[PF.bn(b_)]
        PF.parent_to_bone(ins.obj, body, "Spine", coll)
        AC.REPORT.clear()
        AC.strum_arm(body, "Right", ins.G, ins.spec, "strum", str(who), 0.0)
        AC.fret_wrap(body, "Left", ins.G, ins.spec, 1, "fret", str(who), 0.0)
        reach = {}
        for f in (1, 2, 3, 5):
            body.reset()
            fr.solve(Matrix.Identity(4), f, first=True)
            w = body.head("LeftHand")
            sh = body.head("LeftArm")
            L = body.len[PF.bn("LeftArm")] + body.len[PF.bn("LeftForeArm")]
            tip = body.tail("LeftHandMiddle3")
            T, _, _ = fr.targets(Matrix.Identity(4), f)
            reach[f] = dict(wrist_reach=round((w - sh).length / L, 3), tip_miss_mm=round((tip - T).length * 1000, 1),
                            wrist=[round(x, 1) for x in body.wrist_angles("Left")])
        body.reset()
        sp = ins.spec
        centre = ins.P(Vector((sp.points["tail"] + 0.255, 0, -sp.depth / 2))) if a.kind == "guitar" else \
            ins.P(sp.points["pot"])
        hips = body.head("Hips")
        top = body.tail("Head")
        import arm_checks as AC_
        rp = [ins.P(p) for p in AC_.rest_points(ins.spec)]
        S_ = body.head("RightArm")
        P_ = ins.P(st.P0)
        geo = dict(S=[round(v, 3) for v in S_], P=[round(v, 3) for v in P_],
                   rest_first=[round(v, 3) for v in rp[0]], rest_mid=[round(v, 3) for v in rp[len(rp) // 2]],
                   rest_last=[round(v, 3) for v in rp[-1]],
                   S_to_rest_min=round(min((q - S_).length for q in rp), 3),
                   P_to_rest=[round((q - P_).length, 3) for q in rp[::4]])
        r = dict(who=who, dz=dz, fit=dict(G.Instr.FIT[a.kind]),
                 shoulder=round(body.head("RightArm").z, 3), head_top=round(top.z, 3), hips=round(hips.z, 3),
                 upper_arm=round(body.len[PF.bn("RightArm")], 3), forearm=round(body.len[PF.bn("RightForeArm")], 3),
                 hand=round((body.tail("RightHandMiddle3") - body.head("RightHand")).length, 3),
                 body_centre_z=round(centre.z, 3), body_centre_above_hips=round(centre.z - hips.z, 3),
                 body_centre_height_frac=round(centre.z / top.z, 3),
                 strum_hold=st.hold_info, fret_hold=fr.hold_info,
                 geo=geo, checks={k: v for k, v in AC.REPORT.items()}, fret_reach=reach)
        results.append(r)
        print("CAST", json.dumps(r))
        if a.stills:
            sc.collection.children.link(coll) if coll.name not in sc.collection.children else None
            e.hide_render = True
            if a.palms:
                import palm_test
                palm_test.paint_palms(coll)
            f_ = G.Instr.FIT[a.kind]
            tag = f"{a.kind}_p{who:02d}_dz{int(dz * 100):02d}_a{f_['ang']:.0f}_y{f_['yaw']:.0f}_t{f_['tilt']:.0f}"
            still(tag + "_front", e, (0.15, -2.4, 1.15), (0.0, 0.0, 1.05))
            still(tag + "_threequarter", e, (-1.2, -1.6, 1.4), (0.0, 0.0, 1.1))
            body.reset()
            fh = rig.matrix_basis @ body.head("LeftHandMiddle1")
            rh = rig.matrix_basis @ body.head("RightHand")
            re_ = rig.matrix_basis @ body.head("RightForeArm")
            nk = ins.D((1, 0, 0))
            still(tag + "_fret_front", e, tuple(fh + Vector((-0.05, -0.38, 0.06))), tuple(fh))
            still(tag + "_fret_below", e, tuple(fh + Vector((0.08, -0.22, -0.30))), tuple(fh))
            still(tag + "_fret_alongneck", e, tuple(fh + nk * 0.40 + Vector((0, -0.08, 0.04))), tuple(fh))
            still(tag + "_strum_side", e, tuple(re_ + Vector((-0.70, -0.25, 0.05))), tuple((re_ + rh) / 2))
            still(tag + "_strum_above", e, tuple(re_ + Vector((-0.25, -0.45, 0.45))), tuple((re_ + rh) / 2))
            sc.collection.children.unlink(coll)
        for o in list(coll.objects):
            bpy.data.objects.remove(o)
        bpy.data.collections.remove(coll)
        bpy.data.objects.remove(e)
if a.out:
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    Path(a.out).write_text(json.dumps(results, indent=1))
