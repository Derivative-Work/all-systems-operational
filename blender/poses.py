"""Poses the figure library lacks (brief, Rapid-response rendering plan: "a late clap loop, a mug raise, a crowd push
and a walk-off"), made at set-build time without rebuilding assets/figures/figures.blend.

How: a linked person's "stand" collection is copied into a new local collection (its rig as a local object, its
meshes as local objects sharing the library's mesh data and retargeted to the copied rig, as make_figures.live()
does), the stand loop is dropped, and the rig is re-aimed with blender/ep/figlib.py's aim(). The copy is excluded
from the view layer once posed and used through collection instances, like a library pose.

- clap:      both forearms in front of the chest, hands meeting (O12's late clapper; crowd claps). clap_loop()
             keys it open/closed for animation; the board uses the closed frame.
- mug_raise: right arm up and forward, a mug in the hand (O17). The mug is placed at the posed hand, not
             skinned: right for stills and for a held pose, it won't follow an animated arm.
- push:      the crush toward the mics: leaning in, head tilted forward, clapping at face height on bent elbows.
- reach:     the host's bent-elbow reach for Switch (O10).
  Rule for all of them (lead review): no arm straight from shoulder to wrist pointing forward or forward-and-up.
- fist:      one fist up, the other arm down (singalong punches; lead review: no open palms held high, which
             read as Ever Present's worship crowd).
- clap_open: mid-clap, hands apart (O12's late clapper, the one person still moving).
- walk-off:  the library's "walk" pose is used as is (its loop is the swing; blender/ep/gait.py bakes a
             planted-foot walk but imports Ever Present's final.py, so it isn't wired up at grey-box).
Limits: no finger re-curl beyond the stand pose's relaxed hands, no per-pose motion loop (the library's sway).
A rebuild through blender/ep/make_figures.py with these as figlib poses would add both, plus a grip on the mug.
"""
import math
import sys
from pathlib import Path

import bpy
from mathutils import Matrix, Vector

sys.path.insert(0, str(Path(__file__).resolve().parent / "ep"))
import figlib as F  # noqa: E402
import gb  # noqa: E402

import aso_kit as K  # noqa: E402

P = F.P


def _pose_clap(rig, u, closed=True):
    for s in (1, -1):
        F.arm(rig, s, (s * 0.28, -0.5, -0.82),
              (-s * 0.72, -0.66, 0.22) if closed else (-s * 0.1, -0.9, 0.35),
              (-s * 0.25, -0.95, 0.25) if closed else (-s * 0.1, -0.95, 0.3))
    F.aim(rig, "Head", (0, -0.2 + 0.1 * u, 1))


# Rule for every pose (lead review): no arm straight from shoulder to wrist pointing forward or forward-and-up; in
# hard silhouette that reads as a salute or a rifle. Raised hands go up on a bent elbow: upper arm out to the side at
# or below horizontal, forearm near vertical.

def _pose_mug(rig, u):
    """A toast: upper arm out to the side at shoulder height, forearm upright, the mug beside the head, fingers
    closed round it (lead review: hands gripping; elbow bent, never a straight arm)."""
    F.arm(rig, -1, (-0.82, -0.3, 0.05), (-0.08, -0.2, 1.0), (0.0, -0.1, 1))
    F.arm(rig, 1, (0.12, -0.03, -1), (0.05, -0.15, -1))
    F.curl_fingers(rig, 48, 25, sides=("Right",))
    F.aim(rig, "Head", (0, -0.05, 1))


def _pose_fist(rig, u):
    """One fist up (a singalong punch on the Hey!s): fingers fully curled, thumb over them; the other arm down."""
    s = 1 if u < 0.5 else -1                                # which arm
    side = "Left" if s > 0 else "Right"
    # elbow out and down below the shoulder, forearm upright: a fist pump beside the head. (With the upper arm level,
    # a fist hidden behind the next head left a straight sideways arm in silhouette, O20 r9.)
    # M5: the fist clears the head (human interventions 8: a fist beside the head read as a hand to the head): the
    # upper arm out to the side and a little up, the forearm upright, the elbow bent about 70 degrees.
    F.arm(rig, s, (s * 0.8, -0.2, 0.3), (s * 0.12, -0.12, 1.0), (0.0, -0.05, 1))
    F.arm(rig, -s, (-s * 0.12, -0.03, -1), (-s * 0.05, -0.15, -1))
    F.curl_fingers(rig, 80, 40, sides=(side,))
    F.aim(rig, "Head", (0, 0.1, 1))


def _pose_clap_open(rig, u):
    """Mid-clap, hands apart at chest height, elbows out (O12's late clapper): a silhouette no one else in the frozen
    crowd has, so the one person still clapping reads in a still. M5: lowered from face height (human interventions 8:
    hands near the head read as "confused")."""
    for sd in (1, -1):
        F.arm(rig, sd, (sd * 0.45, -0.35, -0.82), (-sd * 0.12, -0.9, 0.42), (sd * 0.1, -0.85, 0.5))
    F.curl_fingers(rig, 18, 10)                             # cupped, as in a clap; not a spread-fingered wave
    F.aim(rig, "Head", (0, -0.1, 1))


def _pose_push(rig, u):
    """The crush toward the mics (O11): leaning in, head tilted forward toward the mics, clapping at chest height on
    bent elbows (upper arms down, forearms forward and a little up, hands meeting in front of the chest). No arm
    reaches out: extended arms read as a salute or a rifle in silhouette (lead review). M5: lowered from face height
    (human interventions 8: hands at the head read as "confused")."""
    F.aim(rig, "Spine", (0, -0.2, 1))
    F.aim(rig, "Spine1", (0, -0.32, 1))
    for s in (1, -1):
        F.arm(rig, s, (s * 0.3, -0.25, -0.92), (-s * 0.6, -0.72, 0.36), (-s * 0.3, -0.92, 0.25))
    F.curl_fingers(rig, 15, 8)
    F.aim(rig, "Neck", (0, -0.25, 1))
    F.aim(rig, "Head", (0, -0.35 + 0.15 * u, 1))


def _pose_reach(rig, u):
    """The host reaching for Switch (O10): reaching sideways to the left on a bent elbow, the hand at chest height;
    the other arm down."""
    F.arm(rig, 1, (0.8, -0.25, -0.45), (0.75, -0.45, 0.45), (0.6, -0.6, 0.3))
    F.arm(rig, -1, (-0.12, -0.03, -1), (-0.05, -0.15, -1))
    F.aim(rig, "Head", (0, -0.3, 1))


def _pose_mug_low(rig, u):
    """M5: the mug held low between toasts: upper arm down at the side, forearm forward and up, the hand still
    upright so the mug (parented to the hand) stays level; the toast (_pose_mug) is keyed on the Hey!s."""
    F.arm(rig, -1, (-0.2, -0.12, -1), (-0.05, -0.75, 0.66), (0.0, -0.1, 1))


POSES = {"clap": _pose_clap, "clap_open": _pose_clap_open, "mug_raise": _pose_mug, "push": _pose_push,
         "fist": _pose_fist, "reach": _pose_reach}
_HOLD = None


def _holding():
    global _HOLD
    if _HOLD is None or _HOLD.name not in bpy.data.collections:
        _HOLD = gb.collection("pose_variants")
    return _HOLD


def variant(who, pose, u=0.5):
    """A local collection "pv_<who>_<pose>": library person `who` re-posed. Cached per build."""
    name = f"pv_{who:02d}_{pose}"
    if name in bpy.data.collections:
        return bpy.data.collections[name]
    src = K.pick("stand", who=who)
    coll = bpy.data.collections.new(name)
    _holding().children.link(coll)
    m = {o: o.copy() for o in src.objects}
    for o, c in m.items():
        coll.objects.link(c)
        if o.parent in m:
            c.parent = m[o.parent]
        for md in getattr(c, "modifiers", []):
            if md.type == "ARMATURE" and md.object in m:
                md.object = m[md.object]
    rig = next(c for c in m.values() if c.type == "ARMATURE")
    rig.name = f"{name}_rig"
    if rig.animation_data:
        rig.animation_data.action = None
    bpy.context.view_layer.update()
    POSES[pose](rig, u)
    if pose == "mug_raise":
        _mug(coll, rig, u)
    coll["pose"] = pose
    bpy.context.view_layer.update()
    return coll


def _mug(coll, rig, u):
    """A mug in the raised (right) hand, inside the curled fingers: centred between the hand bone's tail and the
    middle finger's second joint, upright, handle toward the thumb side."""
    mw = rig.matrix_world
    a = mw @ rig.pose.bones[P + "RightHand"].tail
    b = mw @ rig.pose.bones[P + "RightHandMiddle2"].head
    roles = ("mug", "mug2", "mug3")
    me = _mug_mesh(roles[int(u * 3) % 3])
    o = bpy.data.objects.new(f"{coll.name}_mug", me)
    o.location = (a + b) / 2 + Vector((0.0, -0.045, -0.02))
    o.rotation_euler.z = 1.4
    coll.objects.link(o)
    # M5: parented to the hand bone, keeping its place, so it follows a keyed arm (key_mugs)
    bpy.context.view_layer.update()
    mw_ = o.matrix_world.copy()
    o.parent, o.parent_type, o.parent_bone = rig, "BONE", P + "RightHand"
    bpy.context.view_layer.update()
    o.matrix_world = mw_


_MUGS = {}


def _mug_mesh(role):
    if role in _MUGS:
        return _MUGS[role]
    b = gb.Builder([K.mat(role, 0.35)])
    import bmesh
    # a big diner mug (8 x 12 cm), larger than the table mugs so it reads in silhouette against the steamed glass
    r = bmesh.ops.create_cone(b.bm, cap_ends=True, segments=18, radius1=0.05, radius2=0.054, depth=0.12)
    b._tag(r["verts"], 0, Matrix.Translation((0, 0, 0)))
    b.capsule((0.05, 0, 0.04), (0.085, 0, 0.03), 0.012)
    b.capsule((0.085, 0, 0.03), (0.085, 0, -0.03), 0.012)
    b.capsule((0.085, 0, -0.03), (0.05, 0, -0.04), 0.012)
    _MUGS[role] = b.to_mesh(f"mug_{role}")
    return _MUGS[role]


def hand(coll, side="Left"):
    """A posed variant's hand position (the hand bone's tail) in figure space, for props held in it."""
    rig = next(o for o in coll.objects if o.type == "ARMATURE")
    return tuple(rig.matrix_world @ rig.pose.bones[P + f"{side}Hand"].tail)


def finish():
    """Exclude the posed copies from the view layer (they render only through instances)."""
    if _HOLD is not None and _HOLD.name in bpy.data.collections:
        lc = bpy.context.view_layer.layer_collection.children.get(_HOLD.name)
        if lc:
            lc.exclude = True


def clap_loop(coll, period=20, start=1, lag=0, cycles=24):
    """Key a clap on a variant: closed on each beat (every `period` frames, `lag` frames late), open between.
    For animation (O12's late clapper); stills don't need it."""
    rig = next(o for o in coll.objects if o.type == "ARMATURE")
    bones = [P + f"{s}{b}" for s in ("Left", "Right") for b in ("Arm", "ForeArm", "Hand")]
    shots = {}
    for closed in (True, False):
        _pose_clap(rig, 0.5, closed)
        shots[closed] = {b: rig.pose.bones[b].rotation_quaternion.copy() for b in bones}
    for k in range(cycles):
        for closed, f in ((True, start + lag + k * period), (False, start + lag + k * period + period // 2)):
            for b in bones:
                pb = rig.pose.bones[b]
                pb.rotation_mode = "QUATERNION"
                pb.rotation_quaternion = shots[closed][b]
                pb.keyframe_insert("rotation_quaternion", frame=f)


# ---------------------------------------------------------------- M5: animation (blender/animatic.py)

_ARM_BONES = [P + f"{s}{b}" for s in ("Left", "Right") for b in ("Arm", "ForeArm", "Hand")]


def _snap(rig, bones):
    for b in bones:
        rig.pose.bones[b].rotation_mode = "QUATERNION"
    return {b: rig.pose.bones[b].rotation_quaternion.copy() for b in bones}


def _key(rig, shot, frame, bones):
    for b in bones:
        pb = rig.pose.bones[b]
        pb.rotation_quaternion = shot[b]
        pb.keyframe_insert("rotation_quaternion", frame=frame)


def key_claps(coll, frames, open_frames=5, wide=False):
    """Key a clap on a posed variant: hands meet on each frame in `frames` (the beat grid), open `open_frames` before
    and after. Every instance of the variant claps together (they share its rig). Chest height (_pose_clap).
    wide: open to _pose_clap_open (hands well apart, elbows out), so one clapper reads in a frozen crowd (O12)."""
    rig = next(o for o in coll.objects if o.type == "ARMATURE")
    shots = {}
    for closed in (True, False):
        if wide and not closed:
            _pose_clap_open(rig, 0.5)
        else:
            _pose_clap(rig, 0.5, closed)
        shots[closed] = _snap(rig, _ARM_BONES)
    _key(rig, shots[False], 1, _ARM_BONES)
    for f in frames:
        _key(rig, shots[False], f - open_frames, _ARM_BONES)
        _key(rig, shots[True], f, _ARM_BONES)
        _key(rig, shots[False], f + open_frames, _ARM_BONES)


def key_mugs(coll, frames, up=18, ease=6):
    """Key a mug_raise variant: held low, raised on each frame in `frames` (the Hey!s; reaching the top on the frame),
    held `up` frames, then lowered."""
    rig = next(o for o in coll.objects if o.type == "ARMATURE")
    bones = [P + f"Right{b}" for b in ("Arm", "ForeArm", "Hand")]
    _pose_mug_low(rig, 0.5)
    low = _snap(rig, bones)
    _pose_mug(rig, 0.5)
    high = _snap(rig, bones)
    _key(rig, low, 1, bones)
    for f in frames:
        _key(rig, low, f - ease, bones)
        _key(rig, high, f, bones)
        _key(rig, high, f + up, bones)
        _key(rig, low, f + up + 2 * ease, bones)


def still(src):
    """A frozen copy of any linked library person collection (its rig's motion loop dropped, the pose kept): the hard
    stops' freezes (O12, O21), where only the late clapper and Switch move."""
    name = f"st_{src.name}"
    if name in bpy.data.collections:
        return bpy.data.collections[name]
    coll = bpy.data.collections.new(name)
    _holding().children.link(coll)
    m = {o: o.copy() for o in src.objects}
    for o, c in m.items():
        coll.objects.link(c)
        if o.parent in m:
            c.parent = m[o.parent]
        for md in getattr(c, "modifiers", []):
            if md.type == "ARMATURE" and md.object in m:
                md.object = m[md.object]
    for c in m.values():
        if c.type == "ARMATURE" and c.animation_data:
            c.animation_data.action = None
    coll["pose"] = src.get("pose", src.name)
    return coll
