"""M5c review 2 (human interventions 16: "All of the clapping has the backs of the hands clapping, not the palms"):
find the palm side of the library hands on the mesh, not from the solver's notion of it, and paint it for test
renders (archive/ only; never in the video).

- paint_palms(coll): on a performer's copy, the body mesh's faces whose vertices all belong (strongest weight) to a
  hand or finger bone and whose rest normal points to the palm side (perf.Body.hand_axes' n, at rest) get a bright
  magenta material, the opposite side green. The mesh data is copied first (the library's is shared).
- Run as a script: one library person at rest with the arms out from the sides, each hand from both sides of the
  palm normal: the fingers straight, bent +40 degrees per joint about local X (M5c/M5c2's "curl"), and flexed 40
  degrees per joint by perf.flex_matrix (local Z; the thumb -X 30). The magenta side must be the one without
  fingernails, and the flexed fingers must fold toward it.

Usage: blender -b --factory-startup --python blender/palm_test.py -- --who 33 --out archive/review/m5c3_palm_test
"""
import argparse
import math
import sys
from pathlib import Path

import bpy
from mathutils import Euler, Matrix, Quaternion, Vector

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE / "ep"))

P = "mixamorig:"


def rest_palm(rig, side):
    """(n, y, t) of a hand at rest, armature space: the palm normal by the hand's chirality (as perf.py)."""
    B = rig.data.bones
    y = B[P + side + "Hand"].matrix_local.to_3x3().col[1].normalized()
    t = B[P + side + "HandIndex1"].head_local - B[P + side + "HandPinky1"].head_local
    t = (t - y * t.dot(y)).normalized()
    n = y.cross(t) if side == "Left" else t.cross(y)
    return n, y, t


def _emit(name, col):
    m = bpy.data.materials.get(name)
    if m is None:
        m = bpy.data.materials.new(name)
        m.use_nodes = True
        b = m.node_tree.nodes["Principled BSDF"]
        b.inputs["Base Color"].default_value = col
        b.inputs["Emission Color"].default_value = col
        b.inputs["Emission Strength"].default_value = 1.2
    return m


def paint_palms(coll, back=True):
    rig = next(o for o in coll.objects if o.type == "ARMATURE")
    body = max((o for o in coll.objects if o.type == "MESH"), key=lambda o: len(o.data.vertices))
    body.data = body.data.copy()
    me = body.data
    me.materials.append(_emit("TEST_palm_magenta", (1.0, 0.0, 1.0, 1.0)))
    im = len(me.materials) - 1
    ig = None
    if back:
        me.materials.append(_emit("TEST_back_green", (0.0, 0.9, 0.2, 1.0)))
        ig = len(me.materials) - 1
    gi = {g.index: g.name for g in body.vertex_groups}
    dom = {}
    for v in me.vertices:
        gs = [g for g in v.groups if gi.get(g.group, "").startswith(P)]
        if gs:
            dom[v.index] = gi[max(gs, key=lambda g: g.weight).group]
    M3 = (rig.matrix_world.inverted() @ body.matrix_world).to_3x3()
    for side in ("Left", "Right"):
        n, _, _ = rest_palm(rig, side)
        for f in me.polygons:
            if all(dom.get(i, "").startswith(P + side + "Hand") for i in f.vertices):
                d = (M3 @ f.normal).normalized().dot(n)
                if d > 0.35:
                    f.material_index = im
                elif d < -0.35 and ig is not None:
                    f.material_index = ig
    return body


def main():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    ap = argparse.ArgumentParser()
    ap.add_argument("--who", type=int, default=33)
    ap.add_argument("--out", default="archive/review/m5c3_palm_test")
    a = ap.parse_args(argv)
    lib = HERE.parent / "assets" / "figures" / "figures.blend"
    with bpy.data.libraries.load(str(lib), link=False) as (src, dst):
        dst.collections = [f"fig_{a.who:02d}_stand"]
    c = dst.collections[0]
    bpy.context.scene.collection.children.link(c)
    rig = next(o for o in c.all_objects if o.type == "ARMATURE")
    if rig.animation_data:
        rig.animation_data.action = None
    for pb in rig.pose.bones:
        pb.rotation_mode = "QUATERNION"
        pb.matrix_basis = Matrix.Identity(4)
    paint_palms(c)
    sc = bpy.context.scene
    sc.render.engine = "BLENDER_EEVEE"
    sc.render.resolution_x = sc.render.resolution_y = 420
    sc.world = bpy.data.worlds.new("w")
    sc.world.color = (0.35, 0.35, 0.38)
    sun = bpy.data.objects.new("sun", bpy.data.lights.new("sun", "SUN"))
    sc.collection.objects.link(sun)
    sun.data.energy = 3
    cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam"))
    sc.collection.objects.link(cam)
    sc.camera = cam
    cam.data.lens = 60
    # the arms out from the sides (about the figure's forward axis), so a camera fits on the palm side
    for side, sg in (("Left", 1), ("Right", -1)):
        pb = rig.pose.bones[P + side + "Arm"]
        bone = rig.data.bones[P + side + "Arm"]
        q = Quaternion(Vector((0, -1, 0)), math.radians(55 * sg))
        R = bone.matrix_local.to_3x3().inverted() @ q.to_matrix() @ bone.matrix_local.to_3x3()
        pb.rotation_quaternion = R.to_quaternion()
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    B = rig.data.bones

    def shoot(side, sign, tag):
        bpy.context.view_layer.update()
        pb = rig.pose.bones[P + side + "Hand"]
        n, y, t = rest_palm(rig, side)
        R = rig.matrix_world.to_3x3() @ pb.matrix.to_3x3() @ B[P + side + "Hand"].matrix_local.to_3x3().inverted()
        nw, yw = (R @ n).normalized(), (R @ y).normalized()
        ctr = (rig.matrix_world @ pb.matrix).translation + yw * 0.08
        loc = ctr + nw * sign * 0.45
        cam.location = loc
        fwd = (ctr - loc).normalized()
        q = fwd.to_track_quat("-Z", "Y")
        up = q @ Vector((0, 1, 0))
        yu = (yw - fwd * yw.dot(fwd)).normalized()
        ang = math.atan2(up.cross(yu).dot(fwd), up.dot(yu))
        cam.rotation_euler = (q @ Quaternion(Vector((0, 0, 1)), ang)).to_euler()
        sun.rotation_euler = cam.rotation_euler
        sc.render.filepath = str(out / f"p{a.who:02d}_{side}_{'palmside' if sign > 0 else 'backside'}_{tag}.png")
        bpy.ops.render.render(write_still=True)

    import perf as PF
    for tag, deg in (("straight", 0), ("xcurl40", 40), ("flex40", 40)):
        for side in ("Left", "Right"):
            for f in ("Index", "Middle", "Ring", "Pinky"):
                for k in (1, 2, 3):
                    rig.pose.bones[P + f"{side}Hand{f}{k}"].matrix_basis = \
                        PF.flex_matrix(side, f, deg) if tag == "flex40" else \
                        Euler((math.radians(deg), 0, 0)).to_matrix().to_4x4()
            for k in (2, 3):
                rig.pose.bones[P + f"{side}HandThumb{k}"].matrix_basis = \
                    PF.flex_matrix(side, "Thumb", 30 if tag == "flex40" else 0)
        for side in ("Left", "Right"):
            for sign in (1, -1):
                shoot(side, sign, tag)


if __name__ == "__main__":
    main()
