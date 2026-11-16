"""M5c review (human interventions 15: "it's clipping through the instruments"): a collision check for hands, fingers
and forearms against the instruments, the mic stands, the performer's own body and, when clapping, the other hand.

Run on every solved frame (blender/perf_band.py, blender/perf_crowd.py), alongside the pose rules in blender/perf.py.

- The arm is a set of spheres on the solved bones (armature space): six along the forearm from 40% of its length
  (radius 0.030 m, the sleeve; nearer the elbow the sleeve meets the torso's side wherever the arm hangs), twelve
  over the palm (from the wrist to each finger root; 0.016, the palm's half-thickness measured on the library hands:
  -0.016 to +0.020 m about the hand bone), and every finger and thumb joint and midpoint (0.0095 at the
  root to 0.006 at the tip, measured the same way).
- Obstacles are triangle meshes in a bone's hold frame (mathutils BVH trees): an instrument rides the bone it is
  parented to (the guitar and banjo the lower spine); a mic stand stands still; the performer's own body is split by
  each vertex's strongest bone weight (hips, spine, chest, upper legs; the clothes and the skin under them, evaluated
  in the hold pose with the clothes' masks off), each part riding its bone. Strings and frets are left out (fingers
  press on them; the fretboard under them is in).
- Signed distance: the nearest surface point and its normal; a sphere whose centre is less than its radius outside
  the surface clips by the difference. Clipping is counted at more than CLIP (4 mm) in.
- The two hands (claps, the tambourine's slap): every sphere pair; at a closed clap the palms should touch (gap
  about 0) and not pass into each other.
"""
import math

import bpy
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree

P = "mixamorig:"
CLIP = 0.004
SKIP_MATS = ("string", "fret", "chrome")      # material name fragments left out of instrument meshes

FINGERS = ("Index", "Middle", "Ring", "Pinky")
R_FORE, R_PALM = 0.030, 0.016
R_FING = (0.0095, 0.0085, 0.0072, 0.006)      # at the joints 1, 2, 3 and the tip


def bn(b):
    return b if b.startswith(P) else P + b


def arm_spheres(body, side):
    """[(point, radius, part)] for one arm in armature space, from the solved pose."""
    out = []
    fh, ft = body.head(f"{side}ForeArm"), body.tail(f"{side}ForeArm")
    for u in np.linspace(0.4, 0.95, 6):
        out.append((fh.lerp(ft, u), R_FORE, "forearm"))
    w = body.head(f"{side}Hand")
    for f in FINGERS:
        r1 = body.head(f"{side}Hand{f}1")
        for u in (0.3, 0.65, 1.0):
            out.append((w.lerp(r1, u), R_PALM if u < 1 else R_FING[0] + 0.002, "palm"))
        js = [body.head(f"{side}Hand{f}{k}") for k in (1, 2, 3)] + [body.tail(f"{side}Hand{f}3")]
        for k in range(3):
            out.append((js[k].lerp(js[k + 1], 0.5), (R_FING[k] + R_FING[k + 1]) / 2, "finger"))
            out.append((js[k + 1], R_FING[k + 1], "finger"))
    js = [body.head(f"{side}HandThumb{k}") for k in (1, 2, 3)] + [body.tail(f"{side}HandThumb3")]
    for k in range(3):
        out.append((js[k].lerp(js[k + 1], 0.5), 0.0105 - 0.0012 * k, "finger"))
        out.append((js[k + 1], 0.0095 - 0.0012 * k, "finger"))
    return out


class Obstacle:
    def __init__(self, name, kind, verts, polys, bone=None, body=None, thin=False):
        self.name, self.kind, self.bone = name, kind, bone
        self.thin = thin              # open or thin-walled (the tambourine's frame): unsigned distance, no inside
        self.verts = np.asarray(verts, float)
        self.bvh = BVHTree.FromPolygons([tuple(v) for v in self.verts], polys) if len(polys) else None
        self.lo = self.verts.min(0) - 0.06 if len(self.verts) else None
        self.hi = self.verts.max(0) + 0.06 if len(self.verts) else None
        self.hold_inv = body.M(bone).inverted() if bone is not None else None

    def to_hold(self, body):
        """Armature space now -> the obstacle's hold frame."""
        if self.bone is None:
            return None
        return np.array(body.M(self.bone) @ self.hold_inv).astype(float)


def mesh_obstacle(name, kind, o, body, bone=None, mat=None, thin=False):
    """An object's mesh (built in figure space; its matrix_basis taken as figure space) in the rig's armature
    space, riding `bone` (None: static)."""
    me = o.data
    keep = set(i for i, m in enumerate(me.materials) if m is None or not any(s in m.name for s in SKIP_MATS))
    M = np.array((body.rig.matrix_basis.inverted() @ (o.matrix_basis if mat is None else mat)))
    co = np.empty(len(me.vertices) * 3)
    me.vertices.foreach_get("co", co)
    co = co.reshape(-1, 3) @ M[:3, :3].T + M[:3, 3]
    polys = [tuple(p.vertices) for p in me.polygons if p.material_index in keep]
    used = sorted({i for p in polys for i in p})
    remap = {v: k for k, v in enumerate(used)}
    return Obstacle(name, kind, co[used], [tuple(remap[i] for i in p) for p in polys], bone, body, thin)


BODY_PARTS = {"Hips": "Hips", "Spine": "Spine", "Spine1": "Spine1", "Spine2": "Spine2", "LeftShoulder": "Spine2",
              "RightShoulder": "Spine2", "Neck": "Spine2", "LeftUpLeg": "LeftUpLeg", "RightUpLeg": "RightUpLeg"}


def body_obstacles(coll, body):
    """The performer's own torso and thighs, from the evaluated meshes in the hold pose (body.base set on the rig for
    the evaluation, the clothes' masks off so the skin under them counts too), split by strongest bone weight."""
    rig = body.rig
    saved = {pb.name: pb.matrix_basis.copy() for pb in rig.pose.bones}
    act = rig.animation_data.action if rig.animation_data else None
    if act is not None:
        rig.animation_data.action = None
    for pb in rig.pose.bones:
        if pb.name in body.base:
            pb.matrix_basis = body.base[pb.name]
    masks = []
    for o in coll.objects:
        for md in getattr(o, "modifiers", []):
            if md.type == "MASK" and md.show_viewport:
                md.show_viewport = False
                masks.append(md)
    sc = bpy.context.scene.collection
    linked = coll.name not in sc.children
    if linked:
        sc.children.link(coll)
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    parts = {}
    for o in coll.objects:
        if o.type != "MESH" or o.hide_render or o.parent is not rig and not any(
                md.type == "ARMATURE" for md in o.modifiers):
            continue
        gi = {g.index: g.name[len(P):] for g in o.vertex_groups if g.name.startswith(P)}
        if not gi:
            continue
        ev = o.evaluated_get(dg)
        me = ev.to_mesh()
        if len(me.vertices) != len(o.data.vertices):
            ev.to_mesh_clear()
            continue
        co = np.empty(len(me.vertices) * 3)
        me.vertices.foreach_get("co", co)
        M = np.array(rig.matrix_world.inverted() @ o.matrix_world)
        co = co.reshape(-1, 3) @ M[:3, :3].T + M[:3, 3]
        polys = [tuple(p.vertices) for p in me.polygons]
        ev.to_mesh_clear()
        dom = []
        for v in o.data.vertices:
            gg = [g for g in v.groups if g.group in gi]
            dom.append(BODY_PARTS.get(gi[max(gg, key=lambda g: g.weight).group]) if gg else None)
        for part in set(BODY_PARTS.values()):
            ps = [p for p in polys if all(dom[i] == part for i in p)]
            if not ps:
                continue
            used = sorted({i for p in ps for i in p})
            remap = {v: k for k, v in enumerate(used)}
            parts.setdefault(part, []).append((co[used], [tuple(remap[i] for i in p) for p in ps], o.name))
    if linked:
        sc.children.unlink(coll)
    for md in masks:
        md.show_viewport = True
    for pb in rig.pose.bones:
        pb.matrix_basis = saved[pb.name]
    if act is not None:
        rig.animation_data.action = act
    out = []
    for part, lst in parts.items():
        for co, ps, nm in lst:
            out.append(Obstacle(f"{part}:{nm}", "own body", co, ps, bn(part), body))
    return out


class Checker:
    """One performer's obstacles and running tallies (stored in REPORT["contact"], keyed by the pose label)."""

    def __init__(self, body, obstacles, report, key, hands_pair=True, skip=None):
        self.body, self.obs, self.R, self.key = body, obstacles, report, key
        self.hands_pair = hands_pair
        self.skip = skip or {}                 # side -> obstacle names that side holds (no check)

    def run(self, t, labels, clap_k=None, other_ok=False):
        body = self.body
        sph = {s: arm_spheres(body, s) for s in ("Left", "Right")}
        for s, lst in sph.items():
            lab = labels.get(s)
            if not lab:
                continue
            pts = np.array([tuple(p) for p, r, part in lst])
            rad = np.array([r for p, r, part in lst])
            parts = [part for p, r, part in lst]
            per = {}
            for ob in self.obs:
                if ob.bvh is None or ob.name in self.skip.get(s, ()):
                    continue
                M = ob.to_hold(body)
                q = pts
                if M is not None:                                           # now -> the hold frame
                    Mi = np.linalg.inv(M)
                    q = pts @ Mi[:3, :3].T + Mi[:3, 3]
                near = np.all((q > ob.lo) & (q < ob.hi), axis=1)
                worst, wpart = 0.0, None
                for i in np.nonzero(near)[0]:
                    loc, nrm, _, d = ob.bvh.find_nearest(Vector(q[i]), rad[i] + 0.03)
                    if loc is None:
                        continue
                    sd = d if ob.thin or (Vector(q[i]) - loc).dot(nrm) >= 0 else -d
                    pen = rad[i] - sd
                    if pen > worst:
                        worst, wpart = pen, parts[i]
                if ob.kind not in per or worst > per[ob.kind][0]:
                    per[ob.kind] = (worst, wpart, ob.name)
            for kind, (worst, wpart, nm) in per.items():
                self._tally(lab, kind, worst, wpart, t, nm)
        if self.hands_pair and labels.get("Left") and labels.get("Right"):
            a = np.array([tuple(p) for p, r, part in sph["Left"]])
            b = np.array([tuple(p) for p, r, part in sph["Right"]])
            ra = np.array([r for p, r, part in sph["Left"]])
            rb = np.array([r for p, r, part in sph["Right"]])
            d = np.linalg.norm(a[:, None, :] - b[None, :, :], axis=2) - ra[:, None] - rb[None, :]
            gap = float(d.min())
            lab = labels["Left"] if labels["Left"] == labels["Right"] else f"{labels['Left']} / {labels['Right']}"
            if not other_ok:
                self._tally(lab, "other hand", -gap, None, t, "other hand")
            if clap_k is not None and clap_k >= 0.97:
                G = self.R.setdefault("_gaps", {}).setdefault(lab, [])
                G.append(gap)

    def _tally(self, lab, kind, pen, part, t, name):
        T = self.R.setdefault(lab, {}).setdefault(kind, {"n": 0, "clip": 0, "max": 0.0, "at": ""})
        T["n"] += 1
        if pen > CLIP:
            T["clip"] += 1
        if pen > T["max"]:
            T["max"] = round(pen, 4)
            T["at"] = f"{self.key} {t:.2f}s {part or ''} {name}".strip()


def report_lines(R):
    lines = [f"contacts (hand, finger and forearm spheres vs meshes; clipping = more than {CLIP * 1000:.0f} mm in; "
             "per pose label and obstacle: hand-frames checked, hand-frames clipping, deepest):"]
    for lab in sorted(k for k in R if not k.startswith("_")):
        for kind, T in sorted(R[lab].items()):
            lines.append(f"  {lab} vs {kind}: {T['n']} hand-frames, clipping on {T['clip']}, deepest "
                         f"{T['max'] * 1000:.1f} mm ({T['at']})")
    for lab, gs in sorted(R.get("_gaps", {}).items()):
        g = np.array(gs) * 1000
        lines.append(f"  closed claps, {lab}: {len(g)} frames, palm gap min {g.min():.1f} mm, median "
                     f"{np.median(g):.1f}, max {g.max():.1f} (0 = touching; negative = into each other)")
    return lines
