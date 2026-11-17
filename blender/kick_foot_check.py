"""M7e check (human interventions 32: "The kick drummer's foot is clipping into the kick drum arm"): the kick player's
right foot against the pedal (base and posts, footboard, beater, chain) on every frame of the sub-shots built, and
a still of the pedal from beside it at the frame where the foot comes closest.

Builds each sub-shot exactly as blender/coverage_m7.py does; after its camera is keyed, for every frame (--step): the
evaluated body mesh of the kick player's own copy (the vertices weighted to the right foot and toes), in world space,
against each pedal part's evaluated mesh: triangle overlaps (an intersection: clipping) and the nearest distance.
One JSON line per sub-shot to --report; with --pedal-still, a PNG per build from a camera beside the pedal at the
closest frame (into --out).
Usage: blender -b --factory-startup --python blender/kick_foot_check.py -- --subs O03c,O14b --still --at first
       --size 320x180 --out <scratch> --log <scratch>/pose.log --report <scratch>/kick_foot.jsonl [--pedal-still]
       [--step 1]
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


REPORT = Path(_opt("--report", "log/render_logs/m7e_kick_foot.jsonl"))
STEP = int(_opt("--step", "1"))
PEDAL_STILL = "--pedal-still" in sys.argv
if PEDAL_STILL:
    sys.argv.remove("--pedal-still")
OUT = Path(sys.argv[sys.argv.index("--out") + 1]) if "--out" in sys.argv else Path(".")

import bpy  # noqa: E402
from mathutils import Matrix, Vector  # noqa: E402
from mathutils.bvhtree import BVHTree  # noqa: E402

import coverage_m7 as M7  # noqa: E402

C = M7.C
_orig = C.CAMERA_HOOK
PARTS = ("kick_pedal_base", "kick_pedal_board", "kick_pedal_beater", "kick_pedal_chain")
DONE = set()


def tris_of(me, mw, vmask=None):
    vs = [mw @ v.co for v in me.vertices]
    me.calc_loop_triangles()
    tris = [tuple(t.vertices) for t in me.loop_triangles if vmask is None or any(vmask[i] for i in t.vertices)]
    return vs, tris


def foot_mask(ob):
    names = [g.name for g in ob.vertex_groups]
    want = {i for i, n in enumerate(names) if n.endswith(("RightFoot", "RightToeBase", "RightToe_End"))}
    return [any(g.group in want and g.weight > 0.1 for g in v.groups) for v in ob.data.vertices]


def instances(dg, inst, obs):
    """The evaluated instances of the instancer's meshes, with their real world matrices."""
    out = {}
    for oi in dg.object_instances:
        if oi.is_instance and oi.parent is not None and oi.parent.original == inst and oi.object.original in obs:
            out[oi.object.original.name] = (oi.object, oi.matrix_world.copy())
    return out


def hook(cam, sub, b, f0, f1):
    if _orig:
        _orig(cam, sub, b, f0, f1)
    inst = bpy.data.objects.get("band_kick")
    if inst is None or inst.instance_collection is None:
        return
    parts = [o for o in (bpy.data.objects.get(n) for n in PARTS) if o is not None]     # the grey box had no chain
    feet = {}
    for o in inst.instance_collection.all_objects:
        if o.type == "MESH":
            m = foot_mask(o)
            if sum(m) >= 20:
                feet[o] = m
    if not feet or len(parts) < 3:
        print(f"KICKFOOT {sub['id']}: no kick player or pedal ({list(feet)}, {[p.name for p in parts]})", flush=True)
        return
    print(f"KICKFOOT {sub['id']}: foot meshes {[(o.name, sum(m)) for o, m in feet.items()]}", flush=True)
    sc = bpy.context.scene
    rec = {"sub": sub["id"], "build": b, "frames": 0, "clip_frames": {}, "min_d": {}, "closest_f": None, "closest_d": 9.0}
    for f in range(f0, f1, STEP):
        sc.frame_set(f)
        dg = bpy.context.evaluated_depsgraph_get()
        ins = instances(dg, inst, set(feet))
        fv, ft = [], []
        for o, m in feet.items():
            if o.name not in ins:
                continue
            ev, mw = ins[o.name]
            me = ev.to_mesh()
            vs, tr = tris_of(me, mw, m)
            ft += [tuple(i + len(fv) for i in t) for t in tr]
            fv += vs
            ev.to_mesh_clear()
        if not ft:
            print(f"KICKFOOT {sub['id']}: no instances of the foot meshes at frame {f}", flush=True)
            return
        fb = BVHTree.FromPolygons(fv, ft, all_triangles=True)
        idx = sorted({i for t in ft for i in t})
        for p in parts:
            ev = p.evaluated_get(dg)
            me = ev.to_mesh()
            pv, pt = tris_of(me, ev.matrix_world)
            ev.to_mesh_clear()
            pb = BVHTree.FromPolygons(pv, pt, all_triangles=True)
            if fb.overlap(pb):
                rec["clip_frames"][p.name] = rec["clip_frames"].get(p.name, 0) + 1
            d = min((pb.find_nearest(fv[i])[3] for i in idx[::2]), default=9.0)
            rec["min_d"][p.name] = round(min(rec["min_d"].get(p.name, 9.0), d), 4)
            if d < rec["closest_d"]:
                rec["closest_d"], rec["closest_f"] = round(d, 4), f
        rec["frames"] += 1
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    with REPORT.open("a") as fh:
        fh.write(json.dumps(rec) + "\n")
    print(f"KICKFOOT {sub['id']}: {rec['frames']} frames; clipping frames {rec['clip_frames']}; nearest {rec['min_d']}; "
          f"closest {rec['closest_d']} m at frame {rec['closest_f']}", flush=True)
    if PEDAL_STILL and b not in DONE and rec["closest_f"] is not None:
        DONE.add(b)
        sc.frame_set(rec["closest_f"])
        mw = inst.matrix_world                     # figure space: the pedal runs from y -0.47 (heel) to -0.73
        loc = mw @ Vector((-0.62, -0.42, 0.24))
        tgt = mw @ Vector((0.0, -0.62, 0.11))
        cd = bpy.data.cameras.new("pedal_cam")
        cd.lens, cd.clip_start = 35, 0.02
        pc = bpy.data.objects.new("pedal_cam", cd)
        sc.collection.objects.link(pc)
        pc.location = loc
        pc.rotation_euler = (tgt - loc).to_track_quat("-Z", "Y").to_euler()
        old = sc.camera
        sc.camera = pc
        fp = sc.render.filepath
        sc.render.filepath = str(OUT / f"pedal_{b}_{rec['closest_f']}.png")
        bpy.ops.render.render(write_still=True)
        for k in (0.25, 0.5, 0.75):                       # and three more through the sub-shot
            fk = int(f0 + k * (f1 - f0))
            sc.frame_set(fk)
            sc.render.filepath = str(OUT / f"pedal_{b}_{fk}.png")
            bpy.ops.render.render(write_still=True)
        sc.render.filepath = fp
        sc.camera = old
        bpy.data.objects.remove(pc)


C.CAMERA_HOOK = hook
if __name__ == "__main__":
    C.main()
