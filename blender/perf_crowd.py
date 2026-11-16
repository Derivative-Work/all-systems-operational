"""M5c: the crowd's performances and the O22 walk-off (blender/perf.py has the body solver).

Every crowd member (instances named crowd*) gets their own copy of their person (library or blender/poses.py
variant), keyed per frame, seeded per person (gb.rng("m5c_crowd_<build>"), main seed 41):
- legs: a bounce on the half notes with each person's own lag, a sway over the bar, a lean and a few centimetres'
  surge toward the band through the choruses and builds (hips forward, feet planted), a small hop on the Hey!s for
  some; about a third stomp one foot on the main kicks on beats 1 and 3 in the choruses and the stomp-clap. Feet
  are re-solved every frame, so nothing slides.
- arms, by pose: clappers (clap, push) clap on the backbeat with their own lag of -1 to +3 frames, hands meeting at
  chest height; about half of the standing people join the claps through the choruses; fists pump on the Hey!s
  (and some on the chorus downbeats), elbow bent; mugs (cafe) go up in a toast on each Hey!, the elbow out and the
  mug in front of the shoulder, not at the head; phones stay in both hands.
The O22 walker: blender/ep/gait.py's planted-foot walk baked into the walker's own copy, at the speed that covers
M5's path in the shot; the instance stays put and only rides the ground's height.
"""
import math
import sys
import types

import bpy
import numpy as np
from mathutils import Matrix, Vector

import coverage as C
import gb
import perf as PF
import perf_band as PB
import perf_grips as G
import sets as S


def instances():
    return [o for o in bpy.data.objects if o.type == "EMPTY" and o.instance_type == "COLLECTION"
            and o.name.startswith("crowd")]


class Person:
    def __init__(self, e, b, k, r):
        self.e = e
        self.pose = e.get("pose", "stand")
        coll, rig = PF.own_copy(e, f"{e.name}_{b}")
        self.coll = coll
        self.body = body = PF.Body(rig)
        u = r.random(14)
        self.lag_b = (u[0] - 0.4) * 0.35                       # beats behind (+) or ahead of the grid
        self.lag_s = (-1 + 4 * u[1]) / 30.0                   # clap lag, -1..+3 frames
        self.amp_b = 0.012 + 0.022 * u[2]
        self.sway = 0.008 + 0.016 * u[3]
        self.surge = 0.025 + 0.035 * u[4]
        self.hop = (0.025 + 0.035 * u[5]) if u[6] < 0.45 else 0.0
        self.stomp = "Left" if u[7] < 0.17 else "Right" if u[7] < 0.34 else None
        self.joiner = self.pose == "stand" and u[8] < 0.45
        self.pumper = u[9] < 0.5
        self.ph = u[10] * 6.28
        self.lean = 2.0 + 3.0 * u[11]
        if self.pose == "phone":
            self.stomp = None
        self.ankles = {s: body.head(f"{s}Foot") for s in ("Left", "Right")}
        self.feet = {s: body.M(f"{s}Foot").to_3x3() for s in ("Left", "Right")}
        self.knee = {s: body.head(f"{s}Leg") for s in ("Left", "Right")}
        self.wr = {s: body.head(f"{s}Hand") for s in ("Left", "Right")}       # the hold's wrists
        self.sinv = body.M("Spine2").inverted()
        self.fist_side = None
        if self.pose == "fist":
            # the raised one: the higher wrist
            self.fist_side = max(("Left", "Right"), key=lambda s: self.wr[s].z)
        self.rec = PF.Rec(body, PF.CORE + PF.ARMS + PF.LEGS)
        import contact as CT
        body.reset()
        obs = CT.body_obstacles(coll, body)
        # M5c review: arms that hang at the sides turned out until they clear the body (hips, jackets); the mug
        # re-seated in the re-posed hand
        hang = {"stand": ("Left", "Right"), "clap": (), "push": (), "phone": (), "mug_raise": ("Left",),
                "fist": tuple(x for x in ("Left", "Right") if x != self.fist_side)}.get(self.pose, ())
        self.abduct = {sd: G.clear_hanging(body, sd, obs) for sd in hang}
        if self.pose == "mug_raise":
            G.mug_pose(body, 0.0)
            G.grip(body, "Right", (45, 60, 35), (25, 20, 10))             # round the mug's body
            seat_mug(coll, body)
        if self.pose == "phone":                    # the library's phone grip bent the fingers sideways (local X)
            for sd in ("Left", "Right"):
                G.grip(body, sd, (20, 30, 18), (15, 15, 10))
        if self.pose == "fist" and self.fist_side:
            G.fist_pose(body, self.fist_side, 0.0)
            G.grip(body, self.fist_side, (80, 95, 60), (20, 35, 35))     # a closed fist, the thumb across it
        if self.pose in ("clap", "push") or self.joiner:
            G.clap_fingers(body)
        body.keep()
        self.wr = {s: body.head(f"{s}Hand") for s in ("Left", "Right")}
        self.checker = CT.Checker(body, obs, PF.REPORT.setdefault("contact", {}), f"{b}:{e.name}")


def seat_mug(coll, body):
    """The mug (parented to the right hand bone by blender/poses.py) re-seated in the re-posed hand: upright, in the
    curled fingers on the palm side, its handle toward the palm."""
    mug = next((o for o in coll.objects if "mug" in o.name and o.parent_type == "BONE"), None)
    if mug is None:
        return
    hb = PF.bn("RightHand")
    y, n, t = body.palm("Right")
    centre = (body.head("RightHand") + body.head("RightHandMiddle2")) / 2 + n * 0.055
    hx = -Vector((n.x, n.y, 0)).normalized()                      # the handle toward the palm
    R = Matrix((hx, Vector((0, 0, 1)).cross(hx), Vector((0, 0, 1)))).transposed()
    want = Matrix.Translation(centre) @ R.to_4x4()
    pm = body.M(hb) @ Matrix.Translation((0, body.len[hb], 0))
    mug.matrix_parent_inverse = Matrix.Identity(4)
    mug.matrix_basis = pm.inverted() @ want


def toast(t, heys):
    """0..1: the mug goes up over 0.25 s before each Hey!, holds 0.45 s, comes down over 0.35 s."""
    v = 0.0
    for h in heys:
        d = t - h
        if -0.25 <= d < 0:
            x = (d + 0.25) / 0.25
            v = max(v, x * x * (3 - 2 * x))
        elif 0 <= d < 0.45:
            v = 1.0
        elif 0.45 <= d < 0.8:
            x = 1 - (d - 0.45) / 0.35
            v = max(v, x * x * (3 - 2 * x))
    return v


def stomp_lift(t, times):
    v = 0.0
    for h in times:
        d = t - h
        if -0.24 <= d < -0.06:
            v = max(v, math.sin(0.5 * math.pi * (d + 0.24) / 0.18))
        elif -0.06 <= d < 0:
            v = max(v, -d / 0.06)
    return v


def solve(p, t, ch, en, hey, kick13, room):
    body = p.body
    body.reset()
    bp = C.beat_pos(t)
    half = (bp - p.lag_b) / 2.0
    drive = (0.45 + 0.55 * en) * (0.55 + 0.6 * ch)
    dz = -p.amp_b * drive * (0.5 + 0.5 * math.cos(2 * math.pi * half))
    dx = p.sway * drive * math.sin(math.pi * half + p.ph)
    dy = -p.surge * ch
    hop = p.hop * hey * (0.4 + 0.6 * ch)
    lift = {"Left": 0.0, "Right": 0.0}
    if p.stomp and ch > 0.3:
        lift[p.stomp] = 0.075 * stomp_lift(t, kick13) * ch
    body.move("Hips", (dx, dy, dz + hop - 0.25 * max(lift.values())))
    body.rot("Spine", z=-dx / max(p.sway, 1e-3) * 1.2)
    body.rot("Spine1", x=p.lean * ch + 0.5 * math.sin(2 * math.pi * t / 4.3 + p.ph) + 2.0 * hey)
    body.rot("Head", x=1.5 * (0.5 + 0.5 * math.cos(2 * math.pi * (bp - p.lag_b))), z=1.0 * math.sin(math.pi * half + p.ph))
    for s in ("Left", "Right"):
        a = p.ankles[s] + Vector((0, 0, hop * 0.85 + lift[s]))
        body.two_bone(f"{s}UpLeg", f"{s}Leg", a, p.knee[s] + Vector((0, -0.5, 0.1)))
        body.orient(f"{s}Foot", p.feet[s])
    rel = body.M("Spine2") @ p.sinv
    if p.pose in ("clap", "push") or (p.joiner and ch > 0.05):
        k = PB.clap_amount(t, p.lag_s)
        w_join = 1.0 if p.pose in ("clap", "push") else min(1.0, ch * 1.4)
        if w_join >= 0.999:
            G.clap_pose(body, k)
        else:                                  # joining in: the hands come up from the waist into the clap
            mid = (body.head("LeftArm") + body.head("RightArm")) / 2
            G.clap_pose(body, k * w_join, c=mid + Vector((0, -0.25 + 0.08 * (1 - w_join), -0.07 - 0.22 * (1 - w_join))))
    elif p.pose == "fist" and p.fist_side:
        k = max(hey, (p.pumper * ch) * PB.hit_env(t, [x for x in C.BEATS if abs(x - t) < 1.5], pre=0.12, tau=0.25) * 0.8)
        G.fist_pose(body, p.fist_side, min(1.0, k))
    elif p.pose == "mug_raise":
        G.mug_pose(body, toast(t, C.HEYS) if room == "cafe" else 0.0)
    for s_ in ("Left", "Right"):
        body.limit_wrist(s_)
    p.rec.add()
    labels, ck = labels_of(p, ch)
    PF.check(body, p.e.name, t, PF.rig_offset(body), labels=labels)
    p.checker.run(t, labels, clap_k=ck(t) if ck else None, other_ok=ck is None)
    if ck and ck(t) >= 0.97 and PF.CHECK_ON[0]:
        import arm_checks as AC
        AC.clap_facing(body, labels["Left"], f"{PF.BUILD[0]}:{p.e.name}", t)


def labels_of(p, ch):
    """Pose labels per hand for the wrist and contact checks, and the clap amount function when clapping."""
    if p.pose in ("clap", "push") or (p.joiner and ch > 0.05):
        lab = "crowd clap" if p.pose in ("clap", "push") else "crowd clap (joining in)"
        return {"Left": lab, "Right": lab}, (lambda t: PB.clap_amount(t, p.lag_s))
    if p.pose == "fist" and p.fist_side:
        o = "Right" if p.fist_side == "Left" else "Left"
        return {p.fist_side: "crowd fist", o: "crowd fist, other arm"}, None
    if p.pose == "mug_raise":
        return {"Right": "crowd mug", "Left": "crowd mug, other arm"}, None
    return {"Left": f"crowd {p.pose}", "Right": f"crowd {p.pose}"}, None


def perform(b, n, room, seed_build=None, freeze_t=None):
    sb = seed_build or b
    r = gb.rng(f"m5c_crowd_{sb}")
    people = [Person(e, b, k, r) for k, e in enumerate(instances())]
    if not people:
        return "no crowd"
    frames = np.arange(1, n + 1)
    ts = [C.song_t(b, f) for f in frames] if freeze_t is None else [freeze_t] * n
    t0, t1 = min(ts), max(ts)
    k13 = [h["t"] for h in C.KICKS if t0 - 1 <= h["t"] <= t1 + 1 and h["bar_beat"].split(".")[1] in ("1", "3")]
    heys_s = [h + 0.06 for h in C.HEYS]
    cache = {}
    PF.CHECK_ON[0] = True
    for i, t in enumerate(ts):
        if freeze_t is not None and i > 0:
            break
        ch = C.chorus_amt(t)
        en = C.MIX_E[C.bar_index(t)]
        hey = C.env_hits(t, heys_s, tau=0.16, attack=0.1)
        for p in people:
            solve(p, t, ch, en, min(1.0, hey), k13, room)
    PF.CHECK_ON[0] = True
    for p in people:
        if freeze_t is None:
            p.rec.write(frames)
        else:
            p.rec.hold(frames)
        PF.REG[p.body.rig.name] = p.rec
        PF.apply_static(p.body, PF.FINGERS)
    kinds = {}
    for p in people:
        kinds[p.pose] = kinds.get(p.pose, 0) + 1
    st = sum(1 for p in people if p.stomp)
    jo = sum(1 for p in people if p.joiner)
    if freeze_t is not None:
        return f"crowd frozen at {freeze_t:.2f} s in their M5c poses ({len(people)} people, seeds of {sb})"
    return (f"crowd performances on {len(people)} people ({', '.join(f'{v} {k}' for k, v in sorted(kinds.items()))}; "
            f"{st} stompers, {jo} join the chorus claps)")


# ---------------------------------------------------------------- O12: the late clapper

def late_clapper(b, n, close_frames, open_frames=7):
    """M5c review: O12's late clapper (the one person still moving after the stop) on their own copy, clapping with
    the solver's clap (blender/perf_grips.py; wrists in range) instead of blender/poses.py's keyed clap_loop: hands
    together on each frame in close_frames, wide open between (M5b's timing)."""
    e = S.OBJ.get("late_clapper")
    if e is None:
        return None
    import contact as CT
    coll, rig = PF.own_copy(e, f"late_clapper_{b}")
    body = PF.Body(rig)
    G.clap_fingers(body)
    body.keep()
    obs = CT.body_obstacles(coll, body)
    chk = CT.Checker(body, obs, PF.REPORT.setdefault("contact", {}), f"{b}:late_clapper")
    rec = PF.Rec(body, PF.CORE + PF.ARMS)
    lab = {"Left": "O12 late clapper", "Right": "O12 late clapper"}
    for f in range(1, n + 1):
        k = 0.0
        for c in close_frames:
            k = max(k, 1.0 - abs(f - c) / open_frames)
        k = k * k * (3 - 2 * k)
        body.reset()
        G.clap_pose(body, k, open_gap=0.2)
        rec.add()
        PF.check(body, "late_clapper", f / 30.0, labels=lab)
        chk.run(f / 30.0, lab, clap_k=k)
        if k >= 0.97:
            import arm_checks as AC
            AC.clap_facing(body, lab["Left"], f"{b}:late_clapper", f / 30.0)
    rec.write(np.arange(1, n + 1))
    PF.REG[rig.name] = rec
    PF.apply_static(body, PF.FINGERS)
    return f"late clapper: solver claps closing on frames {list(close_frames)}"


# ---------------------------------------------------------------- O22: the walk-off

def walker(b, n):
    """Planted-foot walk (blender/ep/gait.py) on the walker's own copy along M5's path."""
    w = S.OBJ.get("walker")
    if w is None:
        return None
    sys.modules.setdefault("final", types.SimpleNamespace(_fc_of=C.A._fcurves))   # gait's only use of final.py
    import gait
    from sets import hill_z
    p0, p1 = Vector((1.0, -3.0)), Vector((3.2, 12.0))
    L = (p1 - p0).length
    T = (n - 1) / C.FPS
    speed = L / T
    coll, rig = PF.own_copy(w, f"walker_{b}")
    if w.animation_data:
        w.animation_data_clear()
    d = (p1 - p0).normalized()
    w.rotation_euler.z = math.atan2(d.y, d.x) - math.pi / 2 + math.pi
    cadence = 1.45
    gait.bake(rig, n, speed=speed, cadence=cadence, phase=0.0, lift=0.07, stance=0.62, arm_deg=10.0, fps=C.FPS)
    frames = np.arange(1, n + 1)
    pos = [p0 + d * speed * (f - 1) / C.FPS for f in frames]
    zs = [0.02 if p.y < 8.3 else hill_z(p.x, p.y) for p in pos]
    C.key_series(w, "location", 0, frames, [p0.x] * n)
    C.key_series(w, "location", 1, frames, [p0.y] * n)
    C.key_series(w, "location", 2, frames, zs)
    S.OBJ["walker_path"] = (p0, d, speed, zs)

    def walker_pos(f):
        f = int(min(max(f, 1), n))
        p = p0 + d * speed * (f - 1) / C.FPS
        return Vector((p.x, p.y, zs[f - 1]))
    C.walker_pos = walker_pos
    return (f"walker: planted-foot gait (blender/ep/gait.py), {speed:.2f} m/s, {cadence} steps/s, "
            f"{speed / cadence:.2f} m steps, {L:.1f} m")


def foot_slide(b, n):
    """Check the walker's feet in world space: during each stance (foot within 1 cm of its lowest), how far it moves
    per frame. Evaluates the copy by linking it to the scene for the check, then unlinks it."""
    w = S.OBJ.get("walker")
    if w is None:
        return None
    coll = w.instance_collection
    rig = next(o for o in coll.objects if o.type == "ARMATURE")
    sc = bpy.context.scene
    sc.collection.children.link(coll)
    pts = {"Left": [], "Right": []}
    for f in range(1, n + 1):
        sc.frame_set(f)
        bpy.context.view_layer.update()
        for s in pts:
            pb = rig.pose.bones[PF.P + f"{s}ToeBase"]
            pts[s].append(w.matrix_world @ (rig.matrix_world @ pb.head))
    sc.collection.children.unlink(coll)
    out = {}
    for s, ps in pts.items():
        z = np.array([p.z for p in ps])
        lo = float(min(p.z for p in ps if p.y < 8.0))          # the plank (beyond it the hill drops away)
        moves = []
        for i in range(1, len(ps)):
            if z[i] < lo + 0.01 and z[i - 1] < lo + 0.01 and ps[i].y < 8.0:      # on the plank
                dv = ps[i] - ps[i - 1]
                moves.append(math.hypot(dv.x, dv.y))
        out[s] = (len(moves), float(np.max(moves)) if moves else 0.0, float(np.mean(moves)) if moves else 0.0)
    return out
