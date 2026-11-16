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


def flex_matrix(side, finger, deg):
    """The local rotation that flexes a finger joint by deg toward the palm (Body.hand_axes has how it was measured):
    fingers about Z (- on the left hand, + on the right), the thumb about -X."""
    if finger == "Thumb":
        return Matrix.Rotation(math.radians(-deg), 4, "X")
    return Matrix.Rotation(math.radians(-deg if side == "Left" else deg), 4, "Z")


# Wrist limits (degrees) for every hand pose (M5c review): flexion and extension within 25, ulnar deviation 15,
# radial 10 (a hand aligned with the forearm, a small bend); the forearm turns (pronation/supination) at most
# TWIST_MAX either way from the rig's rest, so the palm's facing comes from the forearm, not a twisted wrist.
WRIST = {"flex": 25.0, "ext": 25.0, "uln": 15.0, "rad": 10.0}
WRIST_LABEL = {}          # pose label -> its own limits (M5c review 2: the fretting hands, decisions 19)
TWIST_MAX = 175.0


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
        self.memo_static = {}

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

    def flex(self, side, finger, k, deg):
        """Flex one finger joint (k = 1, 2, 3) by deg toward the palm (negative: extend), on top of its basis."""
        b = bn(f"{side}Hand{finger}{k}")
        self.basis[b] = self.basis[b] @ flex_matrix(side, finger, deg)
        self.memo = {}

    def curl(self, side, deg, thumb=None, fingers=("Index", "Middle", "Ring", "Pinky")):
        for f in fingers:
            for k in (1, 2, 3):
                self.flex(side, f, k, deg)
        if thumb is not None:
            for k in (2, 3):
                self.flex(side, "Thumb", k, thumb)

    # ---- wrists (M5c review, human interventions 15: "people look like they have broken wrists")
    # The neutral wrist is the rig's rest relation of hand to forearm (the mesh undeformed there, within ~6 degrees of
    # straight). The palm normal and the thumb side come from the rest finger roots, so they hold on every rig.

    def hand_axes(self, side):
        """(rel, n_loc, t_loc): the hand's rest orientation in the forearm's frame, and the palm normal (out of the
        palm) and the thumb-side axis in the hand bone's own frame."""
        k = ("axes", side)
        v = self.memo_static.get(k)
        if v is not None:
            return v
        Rh = self.rest[bn(f"{side}Hand")].to_3x3()
        Rf = self.rest[bn(f"{side}ForeArm")].to_3x3()
        y = Rh.col[1].normalized()
        t = self.rest[bn(f"{side}HandIndex1")].translation - self.rest[bn(f"{side}HandPinky1")].translation
        t = (t - y * t.dot(y)).normalized()
        # The palm side, verified on the mesh (M5c review 2, human interventions 16: "the backs of the hands
        # clapping"): with the fingers pointing up and the palm toward the viewer, a right hand's thumb is on the
        # viewer's right, so the palm normal is t x y for the right hand and y x t for the left. The opposite sign
        # (M5c2's) is the back of the hand: a test render with the faces on its side painted (blender/palm_test.py,
        # archive/review/m5c3_palm_test/) shows the fingernails on them, and at rest they face away from the thighs.
        # Finger flexion (toward this palm) is a rotation about the finger bones' local Z, negative on the left
        # hand and positive on the right; the thumb flexes about its local -X. Measured on the deformed mesh
        # (fingertip vertices of a library person, blender/palm_test.py): local +X, which M5c and M5c2 used as the
        # curl, swings the fingers sideways (0.74-0.79 of the tip's motion across the hand).
        n = y.cross(t) if side == "Left" else t.cross(y)
        Rhi = Rh.inverted()
        v = (Rf.inverted() @ Rh, (Rhi @ n).normalized(), (Rhi @ t).normalized())
        self.memo_static[k] = v
        return v

    def neutral(self, side):
        """The hand's neutral frame on the current forearm: (y0, n0, t0) in armature space."""
        rel, nl, tl = self.hand_axes(side)
        R = self.M(f"{side}ForeArm").to_3x3() @ rel
        return R.col[1].normalized(), (R @ nl).normalized(), (R @ tl).normalized(), R

    def palm(self, side):
        """(y, n, t) of the hand as posed: finger direction, palm normal, thumb side."""
        _, nl, tl = self.hand_axes(side)
        R = self.M(f"{side}Hand").to_3x3()
        return R.col[1].normalized(), (R @ nl).normalized(), (R @ tl).normalized()

    def wrist_angles(self, side):
        """(flexion, deviation, roll) in degrees: + flexion bends the fingers toward the palm (- is extension),
        + deviation toward the thumb (radial; - ulnar), roll the hand's twist about its own axis at the wrist."""
        y0, n0, t0, R0 = self.neutral(side)
        y, n, t = self.palm(side)
        f = math.degrees(math.atan2(y.dot(n0), y.dot(y0)))
        d = math.degrees(math.atan2(y.dot(t0), y.dot(y0)))
        q = (R0.inverted() @ self.M(f"{side}Hand").to_3x3()).to_quaternion()
        r = math.degrees(2 * math.atan2(q.y, q.w))
        r = (r + 180) % 360 - 180
        return f, d, r

    def forearm_twist(self, side):
        q = self.basis[bn(f"{side}ForeArm")].to_quaternion()
        r = math.degrees(2 * math.atan2(q.y, q.w))
        return (r + 180) % 360 - 180

    def hand_to(self, side, y_des, n_des=None, lim=None, twist_max=None):
        """Orient the hand: the forearm turns about its own axis (pronation/supination, up to twist_max from rest) so
        the palm faces n_des as nearly as it can, then the hand starts aligned with the forearm (neutral wrist) and
        bends toward y_des by at most the wrist limits. Returns the (flexion, deviation) used."""
        lim = WRIST if lim is None else lim
        tmax = TWIST_MAX if twist_max is None else twist_max
        fa = bn(f"{side}ForeArm")
        a = self.M(fa).col[1].xyz.normalized()
        y_des = Vector(y_des).normalized()
        if n_des is not None:
            # start from the forearm without twist (the swing alone), so the result depends on the pose, not on
            # what the forearm carried from the previous solve
            m = self.basis[fa]
            q = m.to_quaternion()
            qt = Quaternion((q.w, 0.0, q.y, 0.0))
            if qt.magnitude > 1e-9:
                qt.normalize()
                sw = (q @ qt.inverted()).to_matrix().to_4x4()
                sw.translation = m.translation
                self.basis[fa] = sw
                self.memo = {}
            _, n0, _, _ = self.neutral(side)
            nd = Vector(n_des)
            # the palm normal we want, as seen once the hand bends toward y_des: project both onto the plane
            # across the forearm and take the signed angle about it
            p0 = n0 - a * n0.dot(a)
            p1 = nd - a * nd.dot(a)
            if p0.length > 1e-6 and p1.length > 1e-6:
                ang = math.degrees(p0.angle(p1))
                if p0.cross(p1).dot(a) < 0:
                    ang = -ang
                cur = self.forearm_twist(side)
                new = max(-tmax, min(tmax, cur + ang))
                self.basis[fa] = self.basis[fa] @ Matrix.Rotation(math.radians(new - cur), 4, "Y")
                self.memo = {}
        y0, n0, t0, R0 = self.neutral(side)
        f = math.degrees(math.atan2(y_des.dot(n0), y_des.dot(y0)))
        d = math.degrees(math.atan2(y_des.dot(t0), y_des.dot(y0)))
        f = max(-lim["ext"], min(lim["flex"], f))
        d = max(-lim["uln"], min(lim["rad"], d))
        y = (y0 + n0 * math.tan(math.radians(f)) + t0 * math.tan(math.radians(d))).normalized()
        R = y0.rotation_difference(y).to_matrix() @ R0
        self.orient(f"{side}Hand", R)
        return f, d

    def hand_follow(self, side, n_des=None, flex=0.0, dev=0.0, lim=None):
        """The hand continues along the forearm (neutral wrist), the palm turned toward n_des by the forearm's twist,
        then bent by flex (+ toward the palm) and dev (+ toward the thumb), clamped to the wrist limits."""
        lim = WRIST if lim is None else lim
        a = self.M(f"{side}ForeArm").col[1].xyz.normalized()
        if n_des is not None:
            self.hand_to(side, a, n_des, lim)
        y0, n0, t0, R0 = self.neutral(side)
        f = max(-lim["ext"], min(lim["flex"], flex))
        d = max(-lim["uln"], min(lim["rad"], dev))
        y = (y0 + n0 * math.tan(math.radians(f)) + t0 * math.tan(math.radians(d))).normalized()
        self.orient(f"{side}Hand", y0.rotation_difference(y).to_matrix() @ R0)
        return f, d

    def arm_to(self, side, wrist, y_des, n_des=None, flex0=0.0, pole=None, pole_k=0.0, lim=None):
        """Two-bone arm to `wrist`, the elbow put where the forearm would leave the wrist bent by flex0 toward the
        palm (so the hand needs little bend), optionally pulled toward `pole` by pole_k; then hand_to."""
        y_des = Vector(y_des).normalized()
        a = y_des
        if n_des is not None and flex0:
            n = Vector(n_des)
            n = (n - y_des * n.dot(y_des)).normalized()
            fr = math.radians(flex0)
            a = (y_des * math.cos(fr) - n * math.sin(fr)).normalized()
        L = self.len[bn(f"{side}ForeArm")]
        E = Vector(wrist) - a * L
        if pole is not None and pole_k:
            E = E.lerp(Vector(pole), pole_k)
        self.two_bone(f"{side}Arm", f"{side}ForeArm", wrist, E)
        return self.hand_to(side, y_des, n_des, lim)

    def palm_point(self, side, off=0.018):
        """The palm's surface centre (between the wrist and the middle finger's root, `off` out of the palm)."""
        _, n, _ = self.palm(side)
        return (self.head(f"{side}Hand") + self.head(f"{side}HandMiddle1")) / 2 + n * off

    def arm_angles(self, side):
        """(upper arm below horizontal, forearm below horizontal) in degrees: + is downward from the shoulder or
        the elbow. A forearm that rises from the elbow to the wrist is negative."""
        sh, el, wr = self.head(f"{side}Arm"), self.head(f"{side}ForeArm"), self.head(f"{side}Hand")
        u, f = (el - sh).normalized(), (wr - el).normalized()
        return math.degrees(math.asin(max(-1.0, min(1.0, -u.z)))), math.degrees(math.asin(max(-1.0, min(1.0, -f.z))))

    def limit_wrist(self, side, lim=None):
        """Bring an already posed hand within the wrist limits (its palm facing as near as it was)."""
        y, n, _ = self.palm(side)
        f, d, r = self.wrist_angles(side)
        lim = WRIST if lim is None else lim
        if -lim["ext"] - 0.5 <= f <= lim["flex"] + 0.5 and -lim["uln"] - 0.5 <= d <= lim["rad"] + 0.5 and abs(r) < 10:
            return False
        self.hand_to(side, y, n, lim)
        return True


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
REPORT = {"frames": 0, "people": set(), "viol": {}, "min_hand_head": {}, "straight_fwd": {}, "builds": {}, "wrist": {}}
BUILD = [""]
STRAIGHT_DEG = 25.0       # an arm this close to straight ...
FWD = 0.5                 # ... pointing this much forward (-Y), not down (z > -0.3): the salute/rifle read
HAND_HEAD = 0.20          # a hand closer than this to the head's centre: "hand at the head"


def rig_offset(body):
    return body.rig.matrix_basis.copy()


def wrist_stat(body, side, label, key, t):
    """Wrist angles of one hand on this frame, kept per pose label: max flexion, extension, ulnar and radial
    deviation and roll, and the frames beyond the limits (WRIST, 2 degrees' slack)."""
    f, d, r = body.wrist_angles(side)
    W = REPORT["wrist"].setdefault(label, {"n": 0, "flex": (0.0, ""), "ext": (0.0, ""), "uln": (0.0, ""),
                                           "rad": (0.0, ""), "roll": (0.0, ""), "over": 0})
    W["n"] += 1
    at = f"{key} {side} {t:.2f}s"
    for k_, v in (("flex", f), ("ext", -f), ("rad", d), ("uln", -d), ("roll", abs(r))):
        if v > W[k_][0]:
            W[k_] = (round(v, 1), at)
    L = WRIST_LABEL.get(label, WRIST)
    if f > L["flex"] + 2 or -f > L["ext"] + 2 or d > L["rad"] + 2 or -d > L["uln"] + 2:
        W["over"] += 1


def check(body, who, t, off=None, labels=None):
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
        if labels and labels.get(s):
            wrist_stat(body, s, labels[s], key, t)
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
    if R["wrist"]:
        lines.append(f"wrists (degrees; limits flexion {WRIST['flex']:.0f}, extension {WRIST['ext']:.0f}, ulnar "
                     f"{WRIST['uln']:.0f}, radial {WRIST['rad']:.0f}"
                     + "".join(f"; {k}: flexion {v['flex']:.0f}, ulnar {v['uln']:.0f}" for k, v in WRIST_LABEL.items())
                     + "; 'over' = hand-frames beyond its limit by > 2):")
        for lab, W in sorted(R["wrist"].items()):
            lines.append(f"  {lab}: {W['n']} hand-frames, max flexion {W['flex'][0]} ({W['flex'][1]}), extension "
                         f"{W['ext'][0]} ({W['ext'][1]}), ulnar {W['uln'][0]}, radial {W['rad'][0]}, roll "
                         f"{W['roll'][0]}; over {W['over']}")
    if R.get("contact"):
        import contact
        lines += contact.report_lines(R["contact"])
    import arm_checks
    lines += arm_checks.report_lines()
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
