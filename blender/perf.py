"""M5c: instrument holds and stem-driven performances, added at set time (no figure-library rebuild).

Why at set time (decisions 15): every person in assets/figures/figures.blend is a full Mixamo rig with deforming
meshes, so a local copy of any library person (its rig, its meshes sharing the library's mesh data, as
blender/poses.py and M5b's clapper copies already do) can be posed and keyed per frame here. A rebuild through
blender/ep/make_figures.py would only re-bake the same rigs with other loops; grips and per-song timing need the
music map at set time anyway.

How (all in the rig's armature space, which is the figure frame: -Y forward, +X the person's left, metres):
- Body: forward kinematics from the bones' rest matrices and a basis per bone, and two-bone IK (law of cosines with
  a pole) for arms and legs, solved analytically per frame, as blender/ep/gait.py does for the walk. No constraints
  and no depsgraph evaluation, so it's fast and works on instanced copies.
- Each performer: a local copy of their library person (the library's sway loop dropped), a static hold pose solved
  once (hands on the instrument), then per-frame offsets from timing/music_map.json, keyed as quaternions on every
  frame. Feet stay planted (legs re-solved every frame), so bounces, sways and lean-ins never slide a foot.
- Instruments are parented to bones (guitar and banjo to the lower spine, the tambourine to the right hand, mugs and
  phones already ride their hands); mic stands stand on the floor at each singer's mouth height.
Seeds: config/seeds.json main 41 through gb.rng("m5c_band_<build>"), gb.rng("m5c_crowd_<build>").
"""
import math
import sys
from pathlib import Path

import bpy
import numpy as np
from mathutils import Euler, Matrix, Quaternion, Vector

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE / "ep"))
import aso_kit as K  # noqa: E402
import gb  # noqa: E402
import poses  # noqa: E402

P = "mixamorig:"
FPS = 30


def bn(b):
    return b if b.startswith(P) else P + b


# ---------------------------------------------------------------- the body: FK and two-bone IK

class Body:
    def __init__(self, rig):
        self.rig = rig
        bones = rig.data.bones
        self.rest = {b.name: b.matrix_local.copy() for b in bones}
        self.rinv = {k: v.inverted() for k, v in self.rest.items()}
        self.par = {b.name: (b.parent.name if b.parent else None) for b in bones}
        self.len = {b.name: b.length for b in bones}
        self.lib = {pb.name: pb.matrix_basis.copy() for pb in rig.pose.bones}     # the library pose
        self.base = dict(self.lib)
        self.basis = dict(self.lib)
        self.memo = {}

    # pose
    def reset(self, to=None):
        self.basis = dict(to if to is not None else self.base)
        self.memo = {}

    def keep(self):
        """The current pose becomes the base (the hold) that every frame starts from."""
        self.base = dict(self.basis)

    def M(self, b):
        b = bn(b)
        m = self.memo.get(b)
        if m is None:
            p = self.par[b]
            m = (self.rest[b] if p is None else self.M(p) @ self.rinv[p] @ self.rest[b]) @ self.basis[b]
            self.memo[b] = m
        return m

    def head(self, b):
        return self.M(b).translation.copy()

    def tail(self, b):
        b = bn(b)
        return self.M(b) @ Vector((0, self.len[b], 0))

    def mid(self, b):
        return (self.head(b) + self.tail(b)) / 2

    def set_M(self, b, Mdes):
        b = bn(b)
        p = self.par[b]
        par = self.rest[b] if p is None else self.M(p) @ self.rinv[p] @ self.rest[b]
        self.basis[b] = par.inverted() @ Mdes
        self.memo = {}

    def rot(self, b, x=0.0, y=0.0, z=0.0):
        """A local rotation (degrees) on top of the bone's current basis (X bends a Mixamo bone forward)."""
        b = bn(b)
        self.basis[b] = self.basis[b] @ Euler((math.radians(x), math.radians(y), math.radians(z))).to_matrix().to_4x4()
        self.memo = {}

    def turn(self, b, q, about=None):
        """Rotate bone b (and its children) by armature-space rotation q about its head (or `about`)."""
        M0 = self.M(b)
        c = M0.translation if about is None else Vector(about)
        R = q.to_matrix().to_4x4()
        self.set_M(b, Matrix.Translation(c) @ R @ Matrix.Translation(-c) @ M0)

    def move(self, b, d):
        M0 = self.M(b)
        self.set_M(b, Matrix.Translation(Vector(d)) @ M0)

    def aim(self, b, d):
        """Turn b (minimal rotation) so its head-to-tail axis points along d."""
        M0 = self.M(b)
        y0 = M0.col[1].xyz.normalized()
        q = y0.rotation_difference(Vector(d).normalized())
        m = (q.to_matrix() @ M0.to_3x3()).to_4x4()
        m.translation = M0.translation
        self.set_M(b, m)

    def orient(self, b, R3):
        """Set bone b's armature-space orientation (3x3), keeping its head where it is."""
        M0 = self.M(b)
        m = R3.to_4x4()
        m.translation = M0.translation
        self.set_M(b, m)

    def two_bone(self, b1, b2, target, pole):
        """Solve b1-b2 so b2's tail reaches target (clamped to the reach), the middle joint toward pole."""
        b1, b2 = bn(b1), bn(b2)
        S = self.head(b1)
        L1, L2 = self.len[b1], self.len[b2]
        d = Vector(target) - S
        dl = min(max(d.length, abs(L1 - L2) + 1e-3), L1 + L2 - 1e-4)
        u = d.normalized()
        a = (L1 * L1 - L2 * L2 + dl * dl) / (2 * dl)
        h = math.sqrt(max(L1 * L1 - a * a, 0.0))
        n = Vector(pole) - S
        n = n - u * n.dot(u)
        n = n.normalized() if n.length > 1e-6 else Vector((0, -1, 0))
        Kn = S + u * a + n * h
        self.aim(b1, Kn - S)
        self.aim(b2, S + u * dl - self.head(b2))
        return Kn

    def curl(self, side, deg, thumb=None, fingers=("Index", "Middle", "Ring", "Pinky")):
        for f in fingers:
            for k in (1, 2, 3):
                self.rot(f"{side}Hand{f}{k}", x=deg)
        if thumb is not None:
            for k in (2, 3):
                self.rot(f"{side}HandThumb{k}", x=thumb)


class Rec:
    """Collects the keyed bones' bases per frame and writes them as quaternion (and Hips location) F-curves."""

    def __init__(self, body, bones, loc=("Hips",)):
        self.body = body
        self.bones = [bn(b) for b in bones if bn(b) in body.rest]
        self.loc = [bn(b) for b in loc]
        self.q = {b: [] for b in self.bones}
        self.l = {b: [] for b in self.loc}

    def add(self):
        for b in self.bones:
            q = self.body.basis[b].to_quaternion()
            if self.q[b] and np.dot(self.q[b][-1], q) < 0:
                q = -q
            self.q[b].append(tuple(q))
        for b in self.loc:
            self.l[b].append(tuple(self.body.basis[b].translation))

    def write(self, frames):
        import coverage as C
        rig = self.body.rig
        if rig.animation_data:
            rig.animation_data.action = None
        for b in self.bones:
            rig.pose.bones[b].rotation_mode = "QUATERNION"
            arr = np.array(self.q[b])
            for i in range(4):
                C.key_series(rig, f'pose.bones["{b}"].rotation_quaternion', i, frames, arr[:, i])
        for b in self.loc:
            arr = np.array(self.l[b])
            for i in range(3):
                C.key_series(rig, f'pose.bones["{b}"].location', i, frames, arr[:, i])

    def hold(self, frames):
        """Freezes: the first collected pose on every frame."""
        for b in self.bones:
            self.q[b] = [self.q[b][0]] * len(frames)
        for b in self.loc:
            self.l[b] = [self.l[b][0]] * len(frames)
        self.write(frames)


def apply_static(body, bones):
    """Bones not keyed but changed in the hold (finger curls): set on the rig directly."""
    rig = body.rig
    for b in bones:
        b = bn(b)
        pb = rig.pose.bones.get(b)
        if pb is not None:
            pb.rotation_mode = "QUATERNION"
            pb.matrix_basis = body.basis[b]


FINGERS = [f"{s}Hand{f}{k}" for s in ("Left", "Right") for f in ("Index", "Middle", "Ring", "Pinky", "Thumb")
           for k in (1, 2, 3)]
CORE = ["Hips", "Spine", "Spine1", "Spine2", "Neck", "Head", "LeftShoulder", "RightShoulder"]
ARMS = [f"{s}{b}" for s in ("Left", "Right") for b in ("Arm", "ForeArm", "Hand")]
LEGS = [f"{s}{b}" for s in ("Left", "Right") for b in ("UpLeg", "Leg", "Foot", "ToeBase")]


# ---------------------------------------------------------------- local copies

_PERF = None


def holder():
    return poses._holding()          # reset with each build (sets.build)


def own_copy(e, tag):
    """Give instance e its own copy of its collection (rig + meshes sharing mesh data + attached props), the rig's
    motion loop dropped. Returns (collection, rig)."""
    src = e.instance_collection
    coll = bpy.data.collections.new(f"perf_{tag}")
    holder().children.link(coll)
    m = {o: o.copy() for o in src.objects}
    for o, c in m.items():
        coll.objects.link(c)
        if o.parent in m:
            c.parent = m[o.parent]
        for md in getattr(c, "modifiers", []):
            if md.type == "ARMATURE" and md.object in m:
                md.object = m[md.object]
    rig = next(c for c in m.values() if c.type == "ARMATURE")
    rig.name = f"perf_{tag}_rig"
    if rig.animation_data:
        rig.animation_data.action = None
    for k in src.keys():
        coll[k] = src[k]
    e.instance_collection = coll
    return coll, rig


def into_coll(o, coll):
    for c in list(o.users_collection):
        c.objects.unlink(o)
    coll.objects.link(o)
    return o


def parent_to_bone(o, body, bone, coll):
    """Parent o (built in figure space, identity transform) to a bone of body's rig, keeping it where it is in the
    hold pose. Bone parents sit at the bone's tail."""
    bone = bn(bone)
    rig = body.rig
    into_coll(o, coll)
    pm = rig.matrix_basis @ body.M(bone) @ Matrix.Translation((0, body.len[bone], 0))
    w = o.matrix_basis.copy()
    o.parent, o.parent_type, o.parent_bone = rig, "BONE", bone
    o.matrix_parent_inverse = Matrix.Identity(4)
    o.matrix_basis = pm.inverted() @ w
    return o


def body_points(coll, body, zlo, zhi, xr=None):
    """Most-forward (min y) point of the person's meshes in a height band (for clearances), hold pose, figure
    space. Uses the library mesh data in the rest-deformed state through the evaluated copy."""
    sc = bpy.context.scene.collection
    sc.children.link(coll)                                   # evaluated only while linked to the view layer
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    ys = []
    for o in coll.objects:
        if o.type != "MESH" or o.hide_render:
            continue
        ev = o.evaluated_get(dg)
        me = ev.to_mesh()
        co = np.empty(len(me.vertices) * 3)
        me.vertices.foreach_get("co", co)
        co = co.reshape(-1, 3) @ np.array(o.matrix_world)[:3, :3].T + np.array(o.matrix_world)[:3, 3]
        ev.to_mesh_clear()
        sel = (co[:, 2] > zlo) & (co[:, 2] < zhi)
        if xr is not None:
            sel &= (co[:, 0] > xr[0]) & (co[:, 0] < xr[1])
        if sel.any():
            ys.append(co[sel, 1].min())
    sc.children.unlink(coll)
    return min(ys) if ys else None


# ---------------------------------------------------------------- pose rules, checked on every solved frame

REG = {}                  # rig name -> Rec (cameras aim at the solved pose: coverage.bone_world is patched)
CHECK_ON = [True]
REPORT = {"frames": 0, "people": set(), "viol": {}, "min_hand_head": {}, "straight_fwd": {}, "builds": {}}
BUILD = [""]
STRAIGHT_DEG = 25.0       # an arm this close to straight ...
FWD = 0.5                 # ... pointing this much forward (-Y), not down (z > -0.3): the salute/rifle read
HAND_HEAD = 0.20          # a hand closer than this to the head's centre: "hand at the head"


def rig_offset(body):
    return body.rig.matrix_basis.copy()


def check(body, who, t, off=None):
    """The pose rules (blender/poses.py top) on this frame's solved pose, in the figure frame:
    - no arm straight (elbow under STRAIGHT_DEG) pointing forward or forward-and-up;
    - no hand within HAND_HEAD of the head's centre;
    - no hand above the top of the head (no open palms held high; both up is the worship pose)."""
    if not CHECK_ON[0]:
        return
    R = REPORT
    R["frames"] += 1
    key = f"{BUILD[0]}:{who}"
    R["people"].add(key)
    hd = body.mid("Head")
    top = body.tail("Head")
    up = 0
    for s in ("Left", "Right"):
        sh, el, wr = body.head(f"{s}Arm"), body.head(f"{s}ForeArm"), body.head(f"{s}Hand")
        hand = body.tail(f"{s}Hand")
        a = math.degrees((el - sh).angle(wr - el, 0.0))
        d = (wr - sh).normalized()
        if a < STRAIGHT_DEG and -d.y > FWD and d.z > -0.3:
            _viol(key, "straight_fwd", t, f"{s} elbow {a:.0f} deg, dir {tuple(round(x, 2) for x in d)}")
        dh = (hand - hd).length
        m = R["min_hand_head"].get(key)
        if m is None or dh < m[0]:
            R["min_hand_head"][key] = (dh, t, s)
        if dh < HAND_HEAD:
            _viol(key, "hand_at_head", t, f"{s} hand {dh:.2f} m from the head")
        if hand.z > top.z:
            up += 1
            _viol(key, "hand_overhead", t, f"{s} hand {hand.z - top.z:.2f} m above the head")
    if up == 2:
        _viol(key, "both_overhead", t, "both hands above the head")


def _viol(key, kind, t, msg):
    v = REPORT["viol"].setdefault(key, {}).setdefault(kind, [0, None, None])
    v[0] += 1
    if v[1] is None:
        v[1], v[2] = round(t, 2), msg


def report_text():
    R = REPORT
    lines = [f"pose check: {R['frames']} solved frames, {len(R['people'])} figures (build:instance)"]
    nv = sum(len(v) for v in R["viol"].values())
    lines.append(f"violations: {nv} figure/rule pairs" if nv else "violations: none")
    for key, kinds in sorted(R["viol"].items()):
        for kind, (cnt, t, msg) in kinds.items():
            lines.append(f"  {key}: {kind} on {cnt} frames (first {t} s: {msg})")
    close = sorted(R["min_hand_head"].items(), key=lambda kv: kv[1][0])[:8]
    lines.append("closest hands to a head: " + "; ".join(f"{k} {v[0]:.2f} m ({v[2]}, {v[1]:.2f} s)" for k, v in close))
    for k, v in R["builds"].items():
        lines.append(f"  {k}: {v}")
    return "\n".join(lines)


def rec_pose(rec, i):
    """Put rec's body in the pose it recorded at index i (for cameras aiming at a hand)."""
    body = rec.body
    body.reset()
    for b in rec.bones:
        q = Quaternion(rec.q[b][min(i, len(rec.q[b]) - 1)])
        m = q.to_matrix().to_4x4()
        if b in rec.loc:
            m.translation = Vector(rec.l[b][min(i, len(rec.l[b]) - 1)])
        body.basis[b] = m
    body.memo = {}
    return body
