"""M5c review (human interventions 15): grips on the rebuilt instruments, and hand poses with wrists in range.

Everything here works in the rig's armature space (blender/perf.py), with the instruments of blender/instruments.py
placed on their players by an instrument-to-armature matrix G (the hold) carried each frame by the lower spine
(rel = Spine now x Spine at the hold^-1), as the instrument object is parented to that bone.

- Fit: the instrument's top faces the room; its back is brought to 8 mm off the player's belly and hip (the torso's
  evaluated mesh, clothes included), the sound hole (guitar) or pot centre (banjo) at a set height over the hips.
- Strap: a flat strap from the end pin round the player's right side and across the back to the top of the left
  shoulder, then down the front of the chest to the heel's strap button, laid 6 mm off the torso's surface. The
  straight runs (across the back, down the chest) are keyed per frame between their two ends, so the strap stays
  attached to the instrument (lower spine) and the shoulder (upper spine) through the lean-ins.
- Fretting hand: the palm under the neck facing it, thumb side toward the nut, the fingers curled over the
  fretboard; the middle fingertip is put on the strings behind the chord's fret (the wrist moved until it lands),
  then each other fingertip is curled onto the fretboard plane (a skin offset of its radius) where it can reach.
- Strumming / picking hand: the forearm rests on the body's upper edge (guitar) or the armrest (banjo) with a
  sleeve's clearance, the hand continues along it (wrist near neutral, a small flexion that leads the strum), the
  pick fingers over the sound hole or by the bridge, the banjo's ring and little fingers planted on the head.
- Claps: palms meeting in front of the chest, fingers up and a little forward, forearms angled in; the hands are
  oriented from the forearm (perf.Body.hand_to) within the wrist limits, then moved apart or together so the palm
  surfaces touch at the clap.
"""
import math

import bpy
import numpy as np
from mathutils import Matrix, Quaternion, Vector

import contact as CT
import instruments as IN
import perf as PF

R_FORE = CT.R_FORE


def interp_half(outline, x):
    xs = [a for a, w in outline]
    ws = [w for a, w in outline]
    return float(np.interp(x, xs, ws))


def torso_cloud(obs):
    """Torso points (armature space, hold) from blender/contact.py's own-body obstacles."""
    pts = [o.verts for o in obs if o.kind == "own body" and not o.name.startswith(("LeftUpLeg", "RightUpLeg"))]
    return np.concatenate(pts) if pts else np.zeros((0, 3))


def front_y(cloud, x, z, r=0.025):
    sel = (np.abs(cloud[:, 0] - x) < r) & (np.abs(cloud[:, 2] - z) < r)
    return float(cloud[sel, 1].min()) if sel.any() else None


def back_y(cloud, x, z, r=0.025):
    sel = (np.abs(cloud[:, 0] - x) < r) & (np.abs(cloud[:, 2] - z) < r)
    return float(cloud[sel, 1].max()) if sel.any() else None


def side_x(cloud, y, z, sign, r=0.03):
    sel = (np.abs(cloud[:, 1] - y) < r) & (np.abs(cloud[:, 2] - z) < r)
    if not sel.any():
        return None
    return float(cloud[sel, 0].max()) if sign > 0 else float(cloud[sel, 0].min())


def top_z(cloud, x, y, r=0.03):
    sel = (np.abs(cloud[:, 0] - x) < r) & (np.abs(cloud[:, 1] - y) < r)
    return float(cloud[sel, 2].max()) if sel.any() else None


# ---------------------------------------------------------------- an instrument on its player

class Instr:
    """The instrument's frame on the player (hold), in armature space: P(local point), D(local direction)."""

    FIT = {"guitar": dict(ang=30.0, yaw=6.0, tilt=6.0, anchor="hole", x=-0.045, dz=0.18),
           "banjo": dict(ang=34.0, yaw=8.0, tilt=10.0, anchor="pot", x=-0.06, dz=0.18)}

    def __init__(self, body, coll, kind, obs, name):
        self.body, self.kind = body, kind
        self.obj, self.spec = (IN.acoustic_guitar if kind == "guitar" else IN.banjo)(name)
        f = self.FIT[kind]
        anchor = self.spec.points["hole" if f["anchor"] == "hole" else "pot"].copy()
        anchor.z = 0.0
        hips = body.head("Hips")
        G = IN.frame_matrix((0, 0, 0), f["ang"], f["yaw"], f["tilt"])
        tgt = Vector((f["x"], 0.0, hips.z + f["dz"]))
        G.translation = tgt - G.to_3x3() @ anchor
        self.cloud = torso_cloud(obs)
        core = self.cloud[np.abs(self.cloud[:, 0]) < 0.17]        # the trunk only (stray cloth at the hands out)
        # bring the back to 8 mm off the torso (move along the figure's Y only)
        shifts = []
        for p in IN.back_points(self.spec):
            q = G @ p
            yf = front_y(core, q.x, q.z)
            if yf is not None:
                shifts.append(q.y - (yf - 0.008))
        G.translation.y -= max(shifts) if shifts else 0.13
        self.G = G
        self.G3 = G.to_3x3()
        self.obj.matrix_basis = body.rig.matrix_basis @ G

    def P(self, v):
        return self.G @ Vector(v)

    def D(self, v):
        return (self.G3 @ Vector(v)).normalized()


def curl3(body, side, finger, a, b, c):
    body.rot(f"{side}Hand{finger}1", x=a)
    body.rot(f"{side}Hand{finger}2", x=b)
    body.rot(f"{side}Hand{finger}3", x=c)


def set_curl(body, side, finger, base, s):
    """Reset a finger's three joints to the hold's base and curl them by s x (a, b, c)."""
    for k, ang in zip((1, 2, 3), base):
        nm = PF.bn(f"{side}Hand{finger}{k}")
        body.basis[nm] = body.lib[nm] @ Matrix.Rotation(math.radians(ang * s), 4, "X")
    body.memo = {}


def fit_finger(body, side, finger, base, plane_p, plane_n, dist, s_lo=0.3, s_hi=1.6):
    """Curl a finger (its three joints scaled together) until its tip is `dist` off a plane (the skin offset);
    bisection on the curl scale. Returns the scale and the tip's final distance."""
    def d_at(s):
        set_curl(body, side, finger, base, s)
        tip = body.tail(f"{side}Hand{finger}3")
        return (tip - plane_p).dot(plane_n)
    lo, hi = s_lo, s_hi
    dlo, dhi = d_at(lo), d_at(hi)
    if (dlo - dist) * (dhi - dist) > 0:            # out of reach: the end that comes nearer, never into the plane
        s = lo if abs(dlo - dist) < abs(dhi - dist) else hi
        if d_at(s) < dist:
            s = lo if dlo > dhi else hi
        return s, d_at(s)
    for _ in range(18):
        m = (lo + hi) / 2
        dm = d_at(m)
        if (dlo - dist) * (dm - dist) <= 0:
            hi, dhi = m, dm
        else:
            lo, dlo = m, dm
    s = (lo + hi) / 2
    return s, d_at(s)


# ---------------------------------------------------------------- fretting

FRET_CURL = {"Index": (38, 62, 30), "Middle": (44, 68, 34), "Ring": (44, 68, 34), "Pinky": (40, 62, 30)}


class Fretting:
    """The fretting (left) hand: palm under the neck, thumb behind it, fingers curled onto the strings."""

    def __init__(self, body, ins, frets):
        self.body, self.ins = body, ins
        sp, N = ins.spec, ins.spec.neck
        self.frets = frets                   # the index finger's fret per chord shape
        self.y_l = Vector((0.24, 0.62, 0.75)).normalized()        # wrist to knuckles: up, toward the front, the nut
        n = Vector((0.0, 0.77, -0.64))
        self.n_l = (n - self.y_l * n.dot(self.y_l)).normalized()  # the palm faces the neck
        self.z_tip = N.board_top + 0.0012 + 0.0062                # pressing the string onto the fret, skin offset
        for f, c in FRET_CURL.items():
            curl3(body, "Left", f, *c)
        for k in (2, 3):
            body.rot(f"LeftHandThumb{k}", x=8)
        self.base = {f: FRET_CURL[f] for f in FRET_CURL}
        self.wrist = None
        self.ob = CT.mesh_obstacle("probe", "instrument", ins.obj, body)
        self.solve(Matrix.Identity(4), frets[0], first=True)
        # the other fingertips onto the fretboard (the strings' plane), where they reach
        T, Np, Nn = self.targets(Matrix.Identity(4), frets[0])
        self.fit = {}
        for f in ("Index", "Ring", "Pinky"):
            s, d = fit_finger(body, "Left", f, FRET_CURL[f], Np, Nn, 0.0062)
            self.fit[f] = s
        self.fit["Middle"] = 1.0

    def targets(self, rel, fret):
        ins, sp, N = self.ins, self.ins.spec, self.ins.spec.neck
        x = N.fret_x(fret + 1) + 0.3 * (N.fret_x(fret) - N.fret_x(fret + 1))
        y = sp.string_y(x, 2 if sp.n_strings == 6 else 1)
        T = rel @ ins.P((x, y, self.z_tip))
        Np = rel @ ins.P((x, 0, N.board_top + 0.0012))
        Nn = (rel.to_3x3() @ ins.D((0, 0, 1))).normalized()
        return T, Np, Nn

    FLEX, DEV = 20.0, -6.0          # the wrist a little flexed and toward the little finger, as fretting has

    def solve(self, rel, fret, first=False, iters=3):
        """The elbow hangs by the player's side (pole down, out and a little forward); the hand follows the forearm
        with a small bend, the palm turned to the neck by the forearm; the wrist moves until the middle fingertip
        is on its string."""
        body, ins = self.body, self.ins
        T, _, _ = self.targets(rel, fret)
        R3 = rel.to_3x3()
        y = (R3 @ ins.D(self.y_l)).normalized()
        n = (R3 @ ins.D(self.n_l)).normalized()
        w = T - y * 0.12 - n * 0.03 if self.wrist is None else rel @ self.wrist
        sh = body.head("LeftArm")
        pole = sh + Vector((0.25, -0.12, -0.45))
        for _ in range(8 if first else iters):
            body.two_bone("LeftArm", "LeftForeArm", w, pole)
            body.hand_follow("Left", n, self.FLEX, self.DEV)
            tip = body.tail("LeftHandMiddle3")
            w = w + (T - tip)
        body.two_bone("LeftArm", "LeftForeArm", w, pole)
        body.hand_follow("Left", n, self.FLEX, self.DEV)
        ob = getattr(self, "ob", None)
        if ob is not None:                       # a palm or finger in the neck: the hand out, away from it
            pushed = 0.0
            for _ in range(8):
                pen = arm_penetration_rel(body, "Left", ob, rel, ("palm", "finger"))
                if pen <= 0.003 or pushed > 0.015:      # at most 1.5 cm: the fingertips stay on the strings
                    break
                y_, n_, t_ = body.palm("Left")
                w = w - n_ * (pen + 0.002)
                pushed += pen + 0.002
                body.two_bone("LeftArm", "LeftForeArm", w, pole)
                body.hand_follow("Left", n, self.FLEX, self.DEV)
        if first:
            self.wrist = rel.inverted() @ w
        return w


# ---------------------------------------------------------------- strumming and picking

def two_bone_over(body, side, wrist, contact, clear, elbow_guess, avoid=None):
    """Solve the arm to `wrist` choosing the elbow (round the shoulder-wrist axis) so the forearm passes `clear`
    over the point `contact` (resting on an edge), as near as it can; ties go to the elbow nearest elbow_guess."""
    S = body.head(f"{side}Arm")
    best = None
    u = (Vector(wrist) - S).normalized()
    ref = (Vector(elbow_guess) - S)
    ref = (ref - u * ref.dot(u)).normalized()
    v = u.cross(ref)
    for k in range(-24, 25):
        a = math.radians(k * 3.0)
        pole = S + (ref * math.cos(a) + v * math.sin(a)) * 0.5
        E = body.two_bone(f"{side}Arm", f"{side}ForeArm", wrist, pole)
        W = body.head(f"{side}Hand")
        d = seg_dist(contact, E, W)
        cost = (d - clear) ** 2 * (1.0 if d >= clear else 25.0) + 1e-4 * (a * a)
        if avoid is not None:
            ob, rel = avoid
            cost += 4.0 * arm_penetration_rel(body, side, ob, rel, ("forearm",))
        if best is None or cost < best[0]:
            best = (cost, pole, d)
    body.two_bone(f"{side}Arm", f"{side}ForeArm", wrist, best[1])
    return best[2]


def arm_penetration(body, side, ob, parts=("forearm", "palm", "finger")):
    """Deepest penetration (m) of one arm's spheres into an obstacle in the hold frame."""
    worst = 0.0
    for p, r, part in CT.arm_spheres(body, side):
        if part not in parts:
            continue
        loc, nrm, _, d = ob.bvh.find_nearest(Vector(p), r + 0.05)
        if loc is None:
            continue
        sd = d if (Vector(p) - loc).dot(nrm) >= 0 else -d
        worst = max(worst, r - sd)
    return worst


def arm_penetration_rel(body, side, ob, rel, parts=("forearm", "palm", "finger")):
    """As arm_penetration, the obstacle carried by rel (hold -> now)."""
    ri = rel.inverted()
    worst = 0.0
    for p, r, part in CT.arm_spheres(body, side):
        if part not in parts:
            continue
        q = ri @ Vector(p)
        loc, nrm, _, d = ob.bvh.find_nearest(q, r + 0.05)
        if loc is None:
            continue
        sd = d if (q - loc).dot(nrm) >= 0 else -d
        worst = max(worst, r - sd)
    return worst


def deepest_rel(body, side, ob, rel):
    """(penetration, sphere index, outward normal now) of the deepest sphere of an arm in an obstacle carried by
    rel; (0, None, None) when clear."""
    ri = rel.inverted()
    R3 = rel.to_3x3()
    best = (0.0, None, None)
    for i, (p, r, part) in enumerate(CT.arm_spheres(body, side)):
        q = ri @ Vector(p)
        loc, nrm, _, d = ob.bvh.find_nearest(q, r + 0.05)
        if loc is None:
            continue
        sd = d if (q - loc).dot(nrm) >= 0 else -d
        if r - sd > best[0]:
            best = (r - sd, i, (R3 @ nrm).normalized())
    return best


def seg_dist(p, a, b):
    ab = b - a
    t = max(0.0, min(1.0, (p - a).dot(ab) / max(ab.length_squared, 1e-9)))
    return (p - (a + ab * t)).length


REST_CLEAR = 0.012        # the sleeve's axis this far beyond its radius over the edge: resting, with room to strum
PICK_CURL = {"Index": (55, 60, 35), "Middle": (60, 70, 40), "Ring": (62, 72, 40), "Pinky": (60, 70, 40)}


class Strumming:
    """The strumming (guitar) or picking (banjo) right hand: forearm resting on the edge or armrest."""

    def __init__(self, body, ins):
        self.body, self.ins = body, ins
        sp = ins.spec
        if ins.kind == "guitar":
            cands = []
            for xc in (-0.14, -0.10, -0.06, -0.02, 0.02):
                w = interp_half(sp.outline, xc)
                cands.append((Vector((xc, w, 0.0)), Vector((0, 0.42, 1.0)).normalized()))     # the top's edge
                cands.append((Vector((xc, w, -0.045)), Vector((0, 1.0, 0.0))))                # the side, higher up
            self.P0 = Vector((sp.points["hole"].x - 0.035, -0.004, sp.string_z(0.08) + 0.006))
            curls = PICK_CURL
            self.pick_finger = "Index"
        else:
            c = sp.points["pot"]
            cands = []
            for ang in (102, 116, 130, 144, 158, 172, 186):
                a = math.radians(ang)
                d = Vector((math.cos(a), math.sin(a), 0))
                cands.append((c + d * (sp.points["head_r"] + 0.008) + Vector((0, 0, 0.015)),
                              Vector((d.x * 0.3, d.y * 0.3, 1.0)).normalized()))               # on the armrest
            self.P0 = Vector((0.015, -0.006, sp.string_z(0.015) + 0.006))
            curls = {"Index": (50, 62, 35), "Middle": (55, 66, 35), "Ring": (30, 40, 20), "Pinky": (28, 38, 20)}
            self.pick_finger = "Middle"
        for f, cc in curls.items():
            curl3(body, "Right", f, *cc)
        body.rot("RightHandThumb2", x=10)
        body.rot("RightHandThumb3", x=12)
        self.curls = curls
        self.n_l = Vector((0, 0, -1))                 # the palm toward the top
        self.flex0 = 10.0 if ins.kind == "guitar" else 20.0
        self.dz = 0.0
        # where the forearm can rest: of the candidate points on the edge (or armrest), the one the forearm passes
        # nearest once the pick finger is on its point
        base = dict(body.basis)
        best = None
        ob = CT.mesh_obstacle("probe", "instrument", ins.obj, body)
        self.ob = ob
        for edge, out in cands:
            body.reset(base)
            self.edge_l, self.C_l = edge, edge + out * (R_FORE + REST_CLEAR)
            self.W_hold = None
            self.solve(Matrix.Identity(4), 0.0, self.flex0, first=True)
            d = seg_dist(ins.P(self.C_l), body.head("RightForeArm"), body.head("RightHand"))
            pen = arm_penetration(body, "Right", ob)
            cost = d + 10.0 * pen
            if best is None or cost < best[0]:
                best = (cost, edge, out, d, pen)
        self.rest_gap, self.rest_pen = best[3], best[4]
        body.reset(base)
        self.edge_l, self.C_l = best[1], best[1] + best[2] * (R_FORE + REST_CLEAR)
        self.W_hold = None
        self.solve(Matrix.Identity(4), 0.0, self.flex0, first=True)
        if ins.kind == "banjo":                       # ring and little fingers planted on the head
            for f in ("Ring", "Pinky"):
                fit_finger(body, "Right", f, curls[f], ins.P((0, 0, 0)), ins.D((0, 0, 1)), 0.0065, 0.2, 2.2)

    def solve(self, rel, h, flex, first=False):
        """first (the hold): search the elbow so the forearm rests over C, the pick finger on its point. Then each
        frame: the hold's wrist and elbow carried by the spine, the wrist moved by the stroke h across the strings
        and corrected so the pick finger is on its point, the elbow kept where the hold had it (stable, no search),
        the hand lifted off the top if any sphere is still in the body."""
        body, ins = self.body, self.ins
        R3 = rel.to_3x3()
        Y = (R3 @ ins.D((0, 1, 0))).normalized()
        Zt = (R3 @ ins.D((0, 0, 1))).normalized()
        C = rel @ ins.P(self.C_l)
        P = rel @ ins.P(self.P0) + Y * h
        n = (R3 @ ins.D(self.n_l)).normalized()
        av = (self.ob, rel) if getattr(self, "ob", None) is not None else None
        sh = body.head("RightArm")
        reach = (body.len[PF.bn("RightArm")] + body.len[PF.bn("RightForeArm")]) * 0.94   # never a straight arm

        def clamp(w):
            d = w - sh
            return sh + d.normalized() * min(d.length, reach)

        if first:
            W = P + (C - P).normalized() * 0.11 + Zt * 0.03
            for _ in range(12):
                W = clamp(W)
                two_bone_over(body, "Right", W, C, 0.0, W - (W - C).normalized() * 0.213, av)
                body.hand_follow("Right", n, flex, 0.0)
                tip = body.tail(f"RightHand{self.pick_finger}3")
                W = W + (P - tip) * 0.7                  # the pick finger onto its point (damped)
            W = clamp(W)
            two_bone_over(body, "Right", W, C, 0.0, W - (W - C).normalized() * 0.213, av)
            body.hand_follow("Right", n, flex, 0.0)
            self.E_hold = body.head("RightForeArm").copy()
        else:
            E = rel @ self.E_hold
            W = rel @ self.W_hold + Y * (h * 0.9)
            for _ in range(3):
                W = clamp(W)
                body.two_bone("RightArm", "RightForeArm", W, E)
                body.hand_follow("Right", n, flex, 0.0)
                tip = body.tail(f"RightHand{self.pick_finger}3")
                W = W + (P - tip) * 0.8
            W = clamp(W)
            body.two_bone("RightArm", "RightForeArm", W, E)
            body.hand_follow("Right", n, flex, 0.0)
        if av is not None:     # still into the body: the elbow up and the hand off the top, a little at a time
            Ecur = rel @ self.E_hold
            for _ in range(16):
                pen = arm_penetration_rel(body, "Right", self.ob, rel)
                if pen <= 0.002:
                    break
                Ecur = Ecur + Vector((0, 0, 1)) * (pen * 0.8 + 0.003)
                W = clamp(W + Zt * (pen * 0.6 + 0.002))
                body.two_bone("RightArm", "RightForeArm", W, Ecur)
                body.hand_follow("Right", n, flex, 0.0)
        if first:
            self.W_hold = rel.inverted() @ W
            self.E_hold = body.head("RightForeArm").copy()
        return W


# ---------------------------------------------------------------- claps

CLAP_CURL = (4, 6, 4)
POLE_K = [0.4]


def clap_pose(body, k, c=None, open_gap=0.13, cross=8.0):
    """Both hands: k = 0 apart .. 1 palms together, in front of the chest, fingers up and a little forward,
    forearms angled in. The right hand turned `cross` degrees more forward than the left so the hands don't read
    as pressed together in prayer. Returns the palm gap measured on the spheres (blender/contact.py)."""
    shL, shR = body.head("LeftArm"), body.head("RightArm")
    mid = (shL + shR) / 2
    if c is None:
        c = mid + Vector((0, -0.30, -0.07))
    out = {}
    for it in range(6):
        for s, sg in (("Left", 1), ("Right", -1)):
            pitch = 54.0 - (cross / 2) * sg                      # fingers' elevation above horizontal
            y = Vector((0, -math.cos(math.radians(pitch)), math.sin(math.radians(pitch))))
            nrm = Vector((-sg, 0, 0))
            sep = out.get(s, 0.0)
            w = c + Vector((sg * (0.022 + (1 - k) * open_gap + sep), 0.035, -0.055))
            sh = body.head(f"{s}Arm")
            body.arm_to(s, w, y, nrm, flex0=-6.0, pole=sh + Vector((sg * 0.22, -0.2, -0.35)), pole_k=POLE_K[0])
        # at the clap close the remaining gap (or undo an overlap): palms touching; opening, never overlapping
        g = palm_gap(body)
        if (abs(g) < 0.0015) if k >= 0.9 else (g >= -0.0005):
            break
        out = {"Left": out.get("Left", 0.0) - g / 2, "Right": out.get("Right", 0.0) - g / 2}
    return palm_gap(body)


def clap_fingers(body):
    """Fingers together and nearly straight for a clap (the library's relaxed hands are spread)."""
    for s in ("Left", "Right"):
        for f in ("Index", "Middle", "Ring", "Pinky"):
            curl3(body, s, f, -6, -6, -3)


def palm_gap(body):
    a = CT.arm_spheres(body, "Left")
    b = CT.arm_spheres(body, "Right")
    best = 1e9
    for p, r, part in a:
        if part == "forearm":
            continue
        for q, s, pq in b:
            if pq == "forearm":
                continue
            best = min(best, (p - q).length - r - s)
    return best


# ---------------------------------------------------------------- the strap

class Strap:
    """Four pieces: end pin round the right side to the back (rides the lower spine, with the instrument); a straight
    run across the back up to below the left shoulder blade (keyed per frame between its ends); over the left
    shoulder (rides the upper spine); a straight run down the chest to the heel's button (keyed per frame)."""

    OFF = 0.007

    def __init__(self, body, coll, ins, name):
        self.body, self.ins = body, ins
        cl = ins.cloud
        sp = ins.spec
        mb = body.rig.matrix_basis
        E0 = ins.P(sp.points["endpin"])
        H = ins.P(sp.points["heelpin"])
        o = self.OFF

        def fy(x, z):
            v = front_y(cl, x, z)
            return v if v is not None else -0.12

        def by(x, z):
            v = back_y(cl, x, z)
            return v if v is not None else 0.12

        z1 = E0.z + 0.03
        ym = (fy(-0.06, z1) + by(-0.06, z1)) / 2
        sx = side_x(cl, ym, z1, -1)
        sx = sx if sx is not None else -0.17
        low = [E0 + Vector((0.004, 0.012, 0)), Vector((sx - o - 0.01, (fy(-0.12, z1) + ym) / 2, z1)),
               Vector((sx - o, ym, z1 + 0.02)), Vector((-0.11, by(-0.11, z1 + 0.05) + o, z1 + 0.05)),
               Vector((-0.05, by(-0.05, z1 + 0.09) + o, z1 + 0.09))]
        Rb = low[-1]
        shx = 0.12
        zs = body.head("LeftArm").z
        yc = (fy(shx, zs - 0.06) + by(shx, zs - 0.06)) / 2
        zt = top_z(cl, shx, yc)
        zt = (zt if zt is not None else zs + 0.04) + o
        Sb = Vector((0.10, by(0.10, zs - 0.12) + o + 0.004, zs - 0.12))
        up = [Sb, Vector((shx, yc + 0.06, zt - 0.025)), Vector((shx, yc + 0.02, zt)), Vector((shx, yc - 0.025, zt - 0.006)),
              Vector((shx, yc - 0.055, zt - 0.035))]
        Sf = Vector((0.115, fy(0.115, zt - 0.10) - o, zt - 0.10))
        up.append(Sf)

        def nrm(pts, centre_y):
            out = []
            for p in pts:
                d = Vector((p.x, p.y - centre_y, 0.0))
                if p.z > zt - 0.04:
                    d = d * 0.3 + Vector((0, 0, 1))
                out.append(d.normalized() if d.length > 1e-6 else Vector((0, 0, 1)))
            return out

        self.low = IN.strap(f"{name}_strap_low", [mb @ p for p in low], normals=[mb.to_3x3() @ v for v in nrm(low, ym)])
        self.up = IN.strap(f"{name}_strap_up", [mb @ p for p in up], normals=[mb.to_3x3() @ v for v in nrm(up, yc)])
        PF.parent_to_bone(self.low, body, "Spine", coll)
        PF.parent_to_bone(self.up, body, "Spine2", coll)
        self.runs = []
        for nm, a, abone, b_, bbone, nv in (("back", Rb, "Spine", Sb, "Spine2", Vector((0, 1, 0))),
                                             ("front", Sf, "Spine2", H, "Spine", Vector((0, -1, 0)))):
            ob = IN.strap(f"{name}_strap_{nm}", [Vector((0, 0, 0)), Vector((0, 1, 0))], normals=[Vector((0, 0, 1))] * 2)
            PF.into_coll(ob, coll)
            ob.rotation_mode = "QUATERNION"
            self.runs.append(dict(obj=ob, a=a, abone=abone, b=b_, bbone=bbone, n=nv, hold={
                abone: body.M(abone).inverted(), bbone: body.M(bbone).inverted()}, keys=[]))
        self.H, self.Sf = H, Sf

    def add(self):
        body = self.body
        mb = body.rig.matrix_basis
        for r in self.runs:
            A = mb @ (body.M(r["abone"]) @ r["hold"][r["abone"]] @ r["a"])
            B = mb @ (body.M(r["bbone"]) @ r["hold"][r["bbone"]] @ r["b"])
            d = B - A
            yv = d.normalized()
            zv = (r["n"] - yv * r["n"].dot(yv)).normalized()
            xv = yv.cross(zv)
            R = Matrix((xv, yv, zv)).transposed()
            r["keys"].append((tuple(A), tuple(R.to_quaternion()), d.length))

    def write(self, frames, hold=False):
        import coverage as C
        for r in self.runs:
            ks = r["keys"][:1] * len(frames) if hold else r["keys"]
            ob = r["obj"]
            for i in range(3):
                C.key_series(ob, "location", i, frames, [k[0][i] for k in ks])
            qs = [k[1] for k in ks]
            for j in range(1, len(qs)):
                if np.dot(qs[j], qs[j - 1]) < 0:
                    qs[j] = tuple(-v for v in qs[j])
            for i in range(4):
                C.key_series(ob, "rotation_quaternion", i, frames, [q[i] for q in qs])
            C.key_series(ob, "scale", 1, frames, [k[2] for k in ks])


ARM_BONES = [f"{s}{b}" for s in ("Left", "Right") for b in ("Arm", "ForeArm", "Hand")]


def blend_arms(body, a, b, w, sides=("Left", "Right")):
    """Per-bone slerp of the arms' bases between two poses (dicts of bases), then the wrists brought in range."""
    for s in sides:
        for nm in ("Arm", "ForeArm", "Hand"):
            k = PF.bn(f"{s}{nm}")
            qa, qb = a[k].to_quaternion(), b[k].to_quaternion()
            m = qa.slerp(qb, w).to_matrix().to_4x4()
            m.translation = a[k].translation
            body.basis[k] = m
    body.memo = {}
    for s in sides:
        body.limit_wrist(s)


# ---------------------------------------------------------------- fist pump (elbow down)

def fist_pose(body, side, k):
    """An elbow-down pump: the upper arm out and a little forward, below horizontal; the forearm up (k = 1) or
    forward and up at about 50 degrees (k = 0); the fist in line with the forearm, palm in, at or below the top of
    the head, never above it, never pointing forward."""
    sg = 1 if side == "Left" else -1
    sh = body.head(f"{side}Arm")
    L1 = body.len[PF.bn(f"{side}Arm")]
    L2 = body.len[PF.bn(f"{side}ForeArm")]
    e_up = sh + Vector((sg * 0.74, -0.40, -0.55)).normalized() * L1
    e_dn = sh + Vector((sg * 0.55, -0.45, -0.70)).normalized() * L1
    f_up = Vector((-sg * 0.12, -0.22, 0.97)).normalized()
    f_dn = Vector((-sg * 0.15, -0.62, 0.77)).normalized()
    E = e_dn.lerp(e_up, k)
    f = f_dn.lerp(f_up, k).normalized()
    W = E + f * L2
    top = body.tail("Head").z
    if W.z > top - 0.15:                               # the fist (about 8 cm above the wrist) under the head's top
        W.z = top - 0.15
    body.two_bone(f"{side}Arm", f"{side}ForeArm", W, E)
    body.hand_follow(side, Vector((-sg, 0.0, 0.0)), 0.0, 0.0)


# ---------------------------------------------------------------- the mug toast (cafe)

def mug_pose(body, k):
    """Right hand: low (k = 0), the forearm forward and a little up, the mug at the belly; the toast (k = 1), the
    elbow out and forward below the shoulder, the forearm up and in, the mug in front of the shoulder. The palm
    faces in (knuckles upright, so the mug stands), a little radial bend keeps it level."""
    sh = body.head("RightArm")
    L1 = body.len[PF.bn("RightArm")]
    L2 = body.len[PF.bn("RightForeArm")]
    e_lo = sh + Vector((-0.12, -0.18, -0.97)).normalized() * L1
    e_hi = sh + Vector((-0.60, -0.55, -0.58)).normalized() * L1
    f_lo = Vector((0.12, -0.92, 0.36)).normalized()
    f_hi = Vector((0.30, -0.55, 0.78)).normalized()
    E = e_lo.lerp(e_hi, k)
    f = f_lo.lerp(f_hi, k).normalized()
    body.two_bone("RightArm", "RightForeArm", E + f * L2, E)
    body.hand_follow("Right", Vector((1.0, 0.0, 0.0)), 0.0, 10.0 * k)


# ---------------------------------------------------------------- arms hanging at the sides

def clear_hanging(body, side, obstacles, margin=0.012, max_deg=16.0):
    """Turn a hanging arm out from the body (about the figure's forward axis at the shoulder) in 2-degree steps
    until its forearm and hand spheres clear the performer's own body by `margin` (the library's stand arms sink
    into hips and jackets). Returns the degrees used."""
    sg = 1 if side == "Left" else -1
    own = [o for o in obstacles if o.kind == "own body"]
    deg = 0.0
    while deg <= max_deg:
        worst = 0.0
        for p, r, part in CT.arm_spheres(body, side):
            for ob in own:
                M = ob.to_hold(body)
                q = Vector(p) if M is None else Matrix(M.tolist()).inverted() @ Vector(p)
                if not all(ob.lo[i] < q[i] < ob.hi[i] for i in range(3)):
                    continue
                loc, nrm, _, d = ob.bvh.find_nearest(q, r + margin + 0.02)
                if loc is None:
                    continue
                sd = d if (q - loc).dot(nrm) >= 0 else -d
                worst = max(worst, r + margin - sd)
        if worst <= 0:
            break
        body.turn(f"{side}Arm", Quaternion(Vector((0, -1, 0)), math.radians(2.0 * sg)))
        deg += 2.0
    return deg


# ---------------------------------------------------------------- tambourine and mic stand

def palm_centre(body, side):
    y, n, t = body.palm(side)
    return (body.head(f"{side}Hand") + body.head(f"{side}HandMiddle1")) / 2 + n * 0.018


def place_palm(body, side, target, n_des, pole, flex=0.0, dev=0.0, iters=6):
    """Move the wrist until the palm's centre (its surface) is on `target`, the hand following the forearm."""
    y, n, t = body.palm(side)
    w = body.head(f"{side}Hand") + (Vector(target) - palm_centre(body, side))
    for _ in range(iters):
        body.two_bone(f"{side}Arm", f"{side}ForeArm", w, pole)
        body.hand_follow(side, n_des, flex, dev)
        w = w + (Vector(target) - palm_centre(body, side))
    body.two_bone(f"{side}Arm", f"{side}ForeArm", w, pole)
    body.hand_follow(side, n_des, flex, dev)
    return w


class Tambourine:
    """Right hand: the frame gripped at its edge, the forearm forward, up and in, the hand in line with it; the
    disc stands out from the palm, facing forward. Left hand: open, behind the disc (between it and the chest), palm
    to its back face 5 cm off; a slap brings the disc back onto the palm (the right arm moves), a shake turns the
    forearm."""

    def __init__(self, body, make_tamb):
        self.body = body
        sh = body.head("RightArm")
        L1, L2 = body.len[PF.bn("RightArm")], body.len[PF.bn("RightForeArm")]
        E = sh + Vector((-0.30, -0.55, -0.78)).normalized() * L1
        f = Vector((0.35, -0.85, 0.40)).normalized()
        self.E, self.W0 = E, E + f * L2
        self.n_r = Vector((0.8, 0.0, 0.6))
        body.two_bone("RightArm", "RightForeArm", self.W0, E)
        body.hand_follow("Right", self.n_r, 0.0, 0.0)
        curl3(body, "Right", "Index", 55, 70, 40)
        for fg in ("Middle", "Ring", "Pinky"):
            curl3(body, "Right", fg, 62, 75, 40)
        body.rot("RightHandThumb2", x=20)
        # the frame's band lies in the palm, the fingers round its edge: the disc's centre is out from the palm
        # (along its normal), its face along the fingers
        y, n, t = body.palm("Right")
        g = (body.head("RightHand") + body.head("RightHandMiddle1")) / 2 + n * 0.018
        self.centre = g + n * 0.116
        X, Yv, Z = n, y, t
        self.N = y                                               # the disc's front face; the left palm waits there
        self.obj = make_tamb("tambourine")
        R = Matrix((X, Yv, Z)).transposed()
        self.obj.matrix_basis = body.rig.matrix_basis @ (Matrix.Translation(self.centre) @ R.to_4x4())
        # the left palm, 5 cm off the disc's face, facing it
        shl = body.head("LeftArm")
        self.poleL = shl + Vector((0.3, 0.0, -0.4))
        down = Vector((0, 0, -1)) - self.N * (-self.N.z)
        # behind the disc (between it and the chest), palm to its back face: the left arm never crosses the ring
        self.QL = self.centre - self.N * (0.0235 + 0.05) + down.normalized() * 0.03
        curl3(body, "Left", "Index", 6, 8, 4)
        for fg in ("Middle", "Ring", "Pinky"):
            curl3(body, "Left", fg, 8, 10, 5)
        place_palm(body, "Left", self.QL, self.N, self.poleL, 0.0, 0.0, iters=8)
        self.WL = body.head("LeftHand").copy()

    def solve(self, rel, shake, slap, t):
        body = self.body
        R3 = rel.to_3x3()
        W = rel @ (self.W0 - self.N * (0.05 * slap) + Vector((0, 0, -0.012)) * shake)      # the disc onto the palm
        body.two_bone("RightArm", "RightForeArm", W, rel @ self.E)
        body.hand_follow("Right", R3 @ self.n_r, 0.0, 0.0)
        if shake > 0:
            fa = PF.bn("RightForeArm")
            body.basis[fa] = body.basis[fa] @ Matrix.Rotation(math.radians(18 * shake * math.sin(t * 60)), 4, "Y")
            body.memo = {}
        place_palm(body, "Left", rel @ (self.QL + self.N * (0.012 * slap)), R3 @ self.N, rel @ self.poleL, 0.0, 0.0,
                   iters=2)


class StandGrip:
    """The lead's left hand round the mic stand's pole, below the boom: palm to the pole, fingers curled round."""

    def __init__(self, body, grip):
        self.body, self.grip = body, Vector(grip)
        sh = body.head("LeftArm")
        self.pole = sh + Vector((0.28, 0.0, -0.4))
        self.n = Vector((-1.0, 0.25, 0.0)).normalized()
        for fg in ("Index", "Middle", "Ring", "Pinky"):
            curl3(body, "Left", fg, 55, 70, 40)
        body.rot("LeftHandThumb2", x=25)
        self.target = self.grip - self.n * (0.011 + 0.004)
        place_palm(body, "Left", self.target, self.n, self.pole, 10.0, 0.0, iters=8)

    def solve(self):
        place_palm(self.body, "Left", self.target, self.n, self.pole, 10.0, 0.0, iters=2)
