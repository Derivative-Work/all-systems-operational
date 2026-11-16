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

    # M5c review 2 (decisions 19): necks 25 degrees up, the head turned 16 degrees toward the room so the lower bout
    # sits back by the right hip, the top tilted 12 degrees up toward the player (instruments.frame_matrix's tilt is
    # positive top-down: M5c2's +6/+10 tipped the tops away), the sound hole (pot centre) 10 cm over the hip joint
    FIT = {"guitar": dict(ang=25.0, yaw=16.0, tilt=-12.0, anchor="hole", x=-0.045, dz=0.10),
           "banjo": dict(ang=25.0, yaw=16.0, tilt=-12.0, anchor="pot", x=-0.06, dz=0.10)}

    def __init__(self, body, coll, kind, obs, name):
        self.body, self.kind = body, kind
        self.key = body.rig.data.name                 # the library person (rig data is shared by every copy)
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
    """A finger's three joints set to these flexions toward the palm, from the rest (straight) hand
    (perf.flex_matrix: the rig's flexion axes). The library's own finger poses bent about local X, which on this
    rig fans the fingers sideways, so they're replaced, not added to."""
    for k, ang in zip((1, 2, 3), (a, b, c)):
        body.basis[PF.bn(f"{side}Hand{finger}{k}")] = PF.flex_matrix(side, finger, ang)
    body.memo = {}


def thumb3(body, side, a, b, c):
    """The thumb's three joints set to these flexions (across toward the palm) from rest."""
    for k, ang in zip((1, 2, 3), (a, b, c)):
        body.basis[PF.bn(f"{side}HandThumb{k}")] = PF.flex_matrix(side, "Thumb", ang)
    body.memo = {}


def grip(body, side, curls, thumb):
    """Every finger and the thumb set from rest: curls = (a, b, c) for all four fingers, or a dict per finger."""
    for f in ("Index", "Middle", "Ring", "Pinky"):
        curl3(body, side, f, *(curls[f] if isinstance(curls, dict) else curls))
    thumb3(body, side, *thumb)


def set_curl(body, side, finger, base, s):
    """Reset a finger's three joints to the hold's base and curl them by s x (a, b, c)."""
    for k, ang in zip((1, 2, 3), base):
        nm = PF.bn(f"{side}Hand{finger}{k}")
        body.basis[nm] = PF.flex_matrix(side, finger, ang * s)
    body.memo = {}


def fit_finger(body, side, finger, base, plane_p, plane_n, dist, s_lo=0.3, s_hi=1.6, near=None):
    """Curl a finger (its three joints scaled together) until its tip is `dist` off a plane (the skin offset). The
    distance isn't monotonic in the curl (a curling tip can cross the plane and come back out), so the curl is
    scanned from straight to tight for the first crossing, then bisected there. Out of reach: the curl that comes
    nearest without going into the plane. Returns the scale and the tip's final distance."""
    def d_at(s):
        set_curl(body, side, finger, base, s)
        tip = body.tail(f"{side}Hand{finger}3")
        return (tip - plane_p).dot(plane_n)
    ss = list(np.linspace(s_lo, s_hi, 33))
    ds = [d_at(x) for x in ss]
    found = []
    for i in range(len(ss) - 1):
        if (ds[i] - dist) * (ds[i + 1] - dist) <= 0:
            lo, hi, dlo = ss[i], ss[i + 1], ds[i]
            for _ in range(16):
                m = (lo + hi) / 2
                dm = d_at(m)
                if (dlo - dist) * (dm - dist) <= 0:
                    hi = m
                else:
                    lo, dlo = m, dm
            s = (lo + hi) / 2
            d_at(s)
            miss = (body.tail(f"{side}Hand{finger}3") - near).length if near is not None else 0.0
            found.append((miss, s))
            if near is None:
                break
    if found:
        s = min(found)[1]
        return s, d_at(s)
    ok = [(abs(d - dist), x) for x, d in zip(ss, ds) if d >= dist]
    s = min(ok)[1] if ok else ss[int(np.argmax(ds))]
    return s, d_at(s)


# ---------------------------------------------------------------- fretting

FRET_CURL = {"Index": (38, 62, 30), "Middle": (44, 68, 34), "Ring": (44, 68, 34), "Pinky": (40, 62, 30)}
KNUCKLE = [0.010, 0.030]
FRET_FLEX = [40.0]
FRET_TARGET = ["tip"]
FRET_THUMB = [-20.0, 30.0, 20.0]   # the fretting thumb: its root turned -20 about local Y, flexed 30, then 20 and 12
#                                   (behind the neck, the tip over its bass edge; searched for no contact at frets 1-3)
FRET_Y = [0.30, 0.42, 0.86]     # wrist to knuckles (instrument frame): toward the nut, up, out past the board's face
FRET_N = [0.0, 0.90, -0.44]     # the palm: up at the neck's underside, a little back
DEBUG = [False, {}]
FRET_ELBOW_MIN = 32.0       # the fretting arm's upper arm at least this far below horizontal (no raised elbow)


class Fretting:
    """The fretting (left) hand round the neck, M5c review 2 (human interventions 16: "The left hands ... are not
    wrapping the neck"): the palm (the side verified on the mesh, blender/palm_test.py) under the neck facing its
    back and treble side, the thumb behind the neck, the knuckles just below the treble edge and a little in front
    of the fretboard, the fingers rising past the edge and curling down onto the strings. The middle finger's
    knuckle is put at its place for the chord (the index finger's fret plus one), the elbow chosen so the hand
    continues the forearm with a small flexion (perf.Body.arm_to), hanging toward the player's side; then each
    finger is curled until its tip is on the strings."""

    # fretting wrists flex further than the general limit (perf.WRIST: 25): 30-45 degrees is usual at the first
    # frets; decisions 19
    LIM = {"flex": FRET_FLEX[0], "ext": 25.0, "uln": 20.0, "rad": 10.0}

    def __init__(self, body, ins, frets):
        self.body, self.ins = body, ins
        sp, N = ins.spec, ins.spec.neck
        self.frets = frets                   # the index finger's fret per chord shape
        # wrist to knuckles: up past the treble edge, out toward the fretboard's face, a little toward the nut; the
        # palm up and back, toward the neck's back and treble side
        self.y_l = Vector(FRET_Y).normalized()
        n = Vector(FRET_N)
        self.n_l = (n - self.y_l * n.dot(self.y_l)).normalized()
        self.z_tip = N.board_top + 0.0012 + 0.0062                # pressing the string onto the fret, skin offset
        for f, c in FRET_CURL.items():
            curl3(body, "Left", f, *c)
        thumb3(body, "Left", FRET_THUMB[1], FRET_THUMB[2], FRET_THUMB[2] * 0.6)
        b1 = PF.bn("LeftHandThumb1")
        body.basis[b1] = Matrix.Rotation(math.radians(FRET_THUMB[0]), 4, "Y") @ body.basis[b1]
        body.memo = {}
        self.base = {f: FRET_CURL[f] for f in FRET_CURL}
        self.ob = CT.mesh_obstacle("probe", "instrument", ins.obj, body)
        from mathutils.kdtree import KDTree
        cl = ins.cloud
        self.kd = KDTree(len(cl))
        for i, p in enumerate(cl):
            self.kd.insert(Vector(p), i)
        self.kd.balance()
        # a hold per chord position (the index finger's fret): the elbow searched for it, then every fingertip
        # flexed onto its string; per frame the elbow and the finger flexions are interpolated between them as the
        # hand slides (M5c review 2: one elbow for all positions put the palm in the neck on the slides)
        base = dict(body.basis)
        self.holds = {}
        for fr_ in sorted(set(frets)):
            key = ("fret", ins.key, ins.kind, fr_, tuple(sorted(ins.FIT[ins.kind].items())))
            if key not in _HOLD_CACHE:
                body.reset(base)
                _, E, W, info = self.search(fr_)
                self.E_hold, self.W_hold = E, W
                self.fit = {f: 1.0 for f in FRET_CURL}
                self.solve(Matrix.Identity(4), fr_, first=True)
                T, Np, Nn = self.targets(Matrix.Identity(4), fr_)
                fit = {}
                for f in ("Index", "Middle", "Ring", "Pinky"):
                    fit[f], _ = fit_finger(body, "Left", f, FRET_CURL[f], Np, Nn, 0.0062, 0.2, 1.8,
                                           near=self.finger_target(f, fr_))
                _HOLD_CACHE[key] = (E, W, fit, info)
            self.holds[fr_] = _HOLD_CACHE[key]
        body.reset(base)
        self.E_hold, self.W_hold, self.fit, self.hold_info = self.holds[frets[0]]
        self.solve(Matrix.Identity(4), frets[0], first=True)

    def hold_at(self, fret):
        """The hold for a (sliding, fractional) chord position: elbow and finger flexions interpolated."""
        ks = sorted(self.holds)
        fret = min(max(fret, ks[0]), ks[-1])
        lo = max(k for k in ks if k <= fret)
        hi = min(k for k in ks if k >= fret)
        w = 0.0 if hi == lo else (fret - lo) / (hi - lo)
        (E0, W0, F0, _), (E1, W1, F1, _) = self.holds[lo], self.holds[hi]
        return E0.lerp(E1, w), W0.lerp(W1, w), {f: F0[f] * (1 - w) + F1[f] * w for f in F0}

    def anchor(self, rel, fret):
        """The point the hand is placed by: the middle fingertip on its string (FRET_TARGET "tip") or the middle
        knuckle under the treble edge ("knuckle")."""
        return self.targets(rel, fret)[0] if FRET_TARGET[0] == "tip" else self.knuckle(rel, fret)

    def knuckle(self, rel, fret):
        """Where the middle finger's knuckle goes: between frets fret+1 and fret+2, KNUCKLE[0] below the treble
        edge and KNUCKLE[1] in front of the fretboard's face (the fingers arch over the strings)."""
        ins, N = self.ins, self.ins.spec.neck
        x = N.fret_x(fret + 2) + 0.55 * (N.fret_x(fret + 1) - N.fret_x(fret + 2))
        return rel @ ins.P((x, -(N.half(x) + KNUCKLE[0]), N.board_top + KNUCKLE[1]))

    # each finger's string and fret offset (from the index finger's fret) in a generic open-position shape
    SHAPE = {"Index": (1, 0), "Middle": (3, 1), "Ring": (4, 2), "Pinky": (2, 2)}

    def finger_target(self, f, fret, rel=None):
        """Where finger f presses (instrument string index from the treble side, fret behind which it presses)."""
        ins, sp, N = self.ins, self.ins.spec, self.ins.spec.neck
        si, df = self.SHAPE[f]
        si = min(si, sp.n_strings - 1)
        fr = fret + df
        x = N.fret_x(fr) + 0.3 * (N.fret_x(fr - 1) - N.fret_x(fr))
        p = ins.P((x, sp.string_y(x, si), self.z_tip))
        return p if rel is None else rel @ p

    def targets(self, rel, fret):
        ins, sp, N = self.ins, self.ins.spec, self.ins.spec.neck
        x = N.fret_x(fret + 1) + 0.3 * (N.fret_x(fret) - N.fret_x(fret + 1))
        y = sp.string_y(x, 2 if sp.n_strings == 6 else 1)
        T = rel @ ins.P((x, y, self.z_tip))
        Np = rel @ ins.P((x, 0, N.board_top + 0.0012))
        Nn = (rel.to_3x3() @ ins.D((0, 0, 1))).normalized()
        return T, Np, Nn

    def place(self, E, K_, y, n, W=None, iters=5):
        """The arm through elbow E, the middle knuckle on K_, the hand bent toward y (palm toward n) within the
        fretting wrist limits. Returns (W, knuckle miss)."""
        body = self.body
        L2 = body.len[PF.bn("LeftForeArm")]
        W = E + (K_ - E).normalized() * L2 if W is None else E + (W - E).normalized() * L2
        pt = (lambda: body.tail("LeftHandMiddle3")) if FRET_TARGET[0] == "tip" else \
            (lambda: body.head("LeftHandMiddle1"))
        for _ in range(iters):
            body.two_bone("LeftArm", "LeftForeArm", W, E)
            body.hand_to("Left", y, n, self.LIM)
            off = pt() - body.head("LeftHand")
            W = E + ((K_ - off) - E).normalized() * L2
        body.two_bone("LeftArm", "LeftForeArm", W, E)
        body.hand_to("Left", y, n, self.LIM)
        return W, (pt() - K_).length

    def search(self, fret):
        """The hold's elbow: on the sphere round the shoulder, the one from which the hand (within the wrist
        limits) crosses the neck with its palm to it, the knuckle on its place, the elbow below the neck and out of
        the torso."""
        body, ins = self.body, self.ins
        S = body.head("LeftArm")
        L1 = body.len[PF.bn("LeftArm")]
        L2 = body.len[PF.bn("LeftForeArm")]
        K_ = self.anchor(Matrix.Identity(4), fret)
        y = ins.D(self.y_l)
        n = ins.D(self.n_l)
        Xn = ins.D((1, 0, 0))
        N = ins.spec.neck
        x = N.fret_x(fret + 1)
        axis = ins.P((x, 0, N.board_top - (N.board_t + N.shaft_t) / 2))
        base = dict(body.basis)
        best = None
        for th in range(4, 86, 3):
            for ph in range(0, 360, 6):
                c, s_ = math.cos(math.radians(th)), math.sin(math.radians(th))
                E = S + Vector((c * math.cos(math.radians(ph)), c * math.sin(math.radians(ph)), -s_)) * L1
                if E.x < S.x - 0.04 or E.y > S.y + 0.08:      # not across the chest, not behind the back
                    continue
                if not (L2 - 0.03 < (K_ - E).length < L2 + 0.13):
                    continue
                body.reset(base)
                W, miss = self.place(E, K_, y, n, iters=4)
                yh, nh, th_ = body.palm("Left")
                pc = body.palm_point("Left")
                face = nh.dot((axis - pc).normalized())
                along = abs(yh.dot(Xn))
                pen = arm_penetration(body, "Left", self.ob, ("forearm", "palm"))
                _, _, d_el = self.kd.find(E)
                cost = (miss / 0.005) ** 2 + (max(0.0, along - 0.45) / 0.08) ** 2 + (max(0.0, 0.75 - face) / 0.1) ** 2
                cost += (pen / 0.003) ** 2 + (((0.05 - d_el) / 0.01) ** 2 if d_el < 0.05 else 0.0)
                cost += ((th - 50) / 30.0) ** 2 + (((FRET_ELBOW_MIN - th) / 4.0) ** 2 if th < FRET_ELBOW_MIN else 0.0)
                if DEBUG[0]:
                    k_ = th
                    if k_ not in DEBUG[1] or cost < DEBUG[1][k_][0]:
                        DEBUG[1][k_] = (round(cost, 1), ph, round(miss, 3), round(along, 2), round(face, 2), round(pen, 3),
                                        tuple(round(v, 2) for v in yh))
                if best is None or cost < best[0]:
                    best = (cost, E.copy(), W.copy(), dict(miss=round(miss, 4), along=round(along, 2),
                                                           face=round(face, 2), pen=round(pen, 4), th=th, ph=ph,
                                                           elbow_torso=round(d_el, 3), cost=round(cost, 2)))
        body.reset(base)
        if best is None:
            raise RuntimeError("fretting: no elbow reaches the neck")
        return best

    def solve(self, rel, fret, first=False, iters=3):
        """Each frame: the hold's elbow carried by the spine, the knuckle on its place for the (sliding) chord
        position, the hand bent toward the hold's direction across the neck; pushed out of the neck if a palm or
        finger sphere is in it (at most 1.5 cm)."""
        body, ins = self.body, self.ins
        if first:
            E_l, W_l, fit = self.E_hold, self.W_hold, self.fit
        else:
            E_l, W_l, fit = self.hold_at(fret)
        for f, sc in fit.items():
            set_curl(body, "Left", f, FRET_CURL[f], sc)
        K_ = self.anchor(rel, fret)
        R3 = rel.to_3x3()
        y = (R3 @ ins.D(self.y_l)).normalized()
        n = (R3 @ ins.D(self.n_l)).normalized()
        E = rel @ E_l
        W, _ = self.place(E, K_, y, n, None if first else rel @ W_l, iters=8 if first else iters)
        ob = getattr(self, "ob", None)
        if ob is not None:
            pushed = 0.0
            for _ in range(8):
                pen = arm_penetration_rel(body, "Left", ob, rel, ("palm",))     # fingers press on the board
                if pen <= 0.003 or pushed > 0.015:
                    break
                _, n_, _ = body.palm("Left")
                W = W - n_ * (pen + 0.002)
                pushed += pen + 0.002
                body.two_bone("LeftArm", "LeftForeArm", W, E)
                body.hand_to("Left", y, n, self.LIM)
        return W


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


REST_CLEAR = 0.006        # the sleeve this far over the edge or armrest: resting on it, with room to strum
PICK_CURL = {"Index": (35, 50, 25), "Middle": (65, 85, 45), "Ring": (68, 88, 45), "Pinky": (66, 85, 45)}
UPPER_PREF = 62.0         # the upper arm's preferred angle below horizontal (at least arm_checks.UPPER_MIN)
STRUM_DX = {"guitar": 0.06, "banjo": 0.05}   # the pick point along the strings: guitar from the sound hole's centre, banjo from the bridge (+ toward the neck)
PICK_Z = [0.016]           # the index fingertip over the strings: the pick held in it reaches them
FLEX0 = {"guitar": 25.0, "banjo": 15.0}   # the hold's wrist bend (+ flexion, toward the palm; - extension, the hand off the top)
_HOLD_CACHE = {}          # (person, instrument, fit) -> the hold's elbow and wrist: the same in every build


class Strumming:
    """The strumming (guitar) or picking (banjo) right arm, M5c review 2 (human interventions 16: "the strumming
    arms are all angled out the wrong way -- they should be resting downwards rather than coming from the top"):
    the upper arm hangs down from the shoulder (at least 45 degrees below horizontal, about 62 preferred), the
    forearm rests on the body's bass-side edge over the lower bout (guitar) or the armrest (banjo) near the elbow
    and comes down across the top to the pick point by the sound hole or the bridge, the hand along the forearm
    with a small flexion. The hold is searched over elbow positions on the sphere round the shoulder; each frame the
    elbow stays where the hold put it (riding the lower spine) and the forearm turns about it to strum, the wrist
    leading the stroke."""

    def __init__(self, body, ins):
        import arm_checks as AC
        self.body, self.ins = body, ins
        sp = ins.spec
        if ins.kind == "guitar":
            self.P0 = Vector((sp.points["hole"].x + STRUM_DX["guitar"], -0.004, sp.string_z(0.30) + PICK_Z[0]))
            curls = PICK_CURL
            self.pick_finger = "Index"
            out = Vector((0, 0.42, 1.0)).normalized()
            self.rest_l = [(p, out) for p in AC.rest_points(sp)]
        else:
            c = sp.points["pot"]
            self.P0 = Vector((STRUM_DX["banjo"], -0.006, sp.string_z(0.015) + 0.006))
            curls = {"Index": (50, 62, 35), "Middle": (55, 66, 35), "Ring": (30, 40, 20), "Pinky": (28, 38, 20)}
            self.pick_finger = "Middle"
            self.rest_l = []
            for p in AC.rest_points(sp):
                d = (p - c)
                d.z = 0
                d.normalize()
                self.rest_l.append((p, Vector((d.x * 0.3, d.y * 0.3, 1.0)).normalized()))
        for f, cc in curls.items():
            curl3(body, "Right", f, *cc)
        thumb3(body, "Right", 20, 15, 10)              # the thumb on the index's side, holding the pick
        self.curls = curls
        self.n_l = Vector((0, 0, -1))                 # the palm toward the top
        self.flex0 = FLEX0[ins.kind]
        self.ob = CT.mesh_obstacle("probe", "instrument", ins.obj, body)
        from mathutils.kdtree import KDTree
        cl = ins.cloud
        self.kd = KDTree(len(cl))
        for i, p in enumerate(cl):
            self.kd.insert(Vector(p), i)
        self.kd.balance()
        key = (ins.key, ins.kind, tuple(sorted(ins.FIT[ins.kind].items())))
        base = dict(body.basis)
        if key in _HOLD_CACHE:
            self.E_hold, self.W_hold, self.hold_info = _HOLD_CACHE[key]
        else:
            self.search()
            _HOLD_CACHE[key] = (self.E_hold, self.W_hold, self.hold_info)
        body.reset(base)
        self.place(self.E_hold, ins.P(self.P0), self.flex0, self.W_hold, iters=6)
        if ins.kind == "banjo":                       # ring and little fingers planted on the head
            for f in ("Ring", "Pinky"):
                fit_finger(body, "Right", f, curls[f], ins.P((0, 0, 0)), ins.D((0, 0, 1)), 0.0065, 0.2, 2.2)

    # ---- the arm through a given elbow, the pick finger on its point
    def place(self, E, P, flex, W=None, iters=5, n=None):
        body = self.body
        L2 = body.len[PF.bn("RightForeArm")]
        n = (self.ins.D(self.n_l) if n is None else n)
        W = E + (P - E).normalized() * L2 if W is None else E + (W - E).normalized() * L2
        res = 1.0
        for _ in range(iters):
            body.two_bone("RightArm", "RightForeArm", W, E)
            body.hand_follow("Right", n, flex, 0.0)
            tip = body.tail(f"RightHand{self.pick_finger}3")
            res = (tip - P).length
            off = tip - body.head("RightHand")
            W = E + ((P - off) - E).normalized() * L2
        body.two_bone("RightArm", "RightForeArm", W, E)
        body.hand_follow("Right", n, flex, 0.0)
        res = (body.tail(f"RightHand{self.pick_finger}3") - P).length
        return W, res

    def rest_gap(self, E, W, rel=None):
        """The first half of the forearm to the rest edge, from the sleeve's surface (+ over, - into it)."""
        mid = E.lerp(W, 0.5)
        best = 1e9
        for p, out in self.rest_l:
            q = self.ins.P(p) if rel is None else rel @ self.ins.P(p)
            best = min(best, seg_dist(q, E, mid) - R_FORE)
        return best

    def outside(self, E, margin=0.0):
        """The elbow over the rest edge (beyond the bass-side outline, guitar; beyond the armrest's radius, banjo)
        or in front of the top, never behind the body or under it."""
        ins = self.ins
        q = ins.G.inverted() @ E
        if q.z > 0.025:
            return True
        if ins.kind == "guitar":
            ol = ins.spec.outline
            w = float(np.interp(q.x, [a for a, _ in ol], [w_ for _, w_ in ol]))
            return q.y > w + margin and q.z > -0.01           # over the edge, level with the top or in front of it
        c = ins.spec.points["pot"]
        d = Vector((q.x - c.x, q.y - c.y))
        r = ins.spec.points["head_r"]
        return q.y > c.y and ((d.length > r + 0.02 + margin and q.z > -0.01) or (d.length > r + 0.05 and q.z > -0.07))

    def search(self):
        body, ins = self.body, self.ins
        S = body.head("RightArm")
        L1 = body.len[PF.bn("RightArm")]
        L2 = body.len[PF.bn("RightForeArm")]
        P = ins.P(self.P0)
        best = None
        n_ok = 0
        base = dict(body.basis)
        for th in range(46, 88, 2):
            for ph in range(0, 360, 5):
                c, s_ = math.cos(math.radians(th)), math.sin(math.radians(th))
                E = S + Vector((c * math.cos(math.radians(ph)), c * math.sin(math.radians(ph)), -s_)) * L1
                dEP = (P - E).length
                if not (L2 + 0.02 < dEP < L2 + 0.17):
                    continue
                if E.y > S.y + 0.06 or E.x > S.x + 0.10:          # not behind the back, not across the chest
                    continue
                if not self.outside(E):                           # over the edge or in front, never behind
                    continue
                body.reset(base)
                W, res = self.place(E, P, self.flex0, iters=4)
                g = self.rest_gap(E, W)
                pen = arm_penetration(body, "Right", self.ob)
                _, _, d_el = self.kd.find(E)
                up, fore = body.arm_angles("Right")
                cost = (res / 0.006) ** 2 + ((g - REST_CLEAR) / 0.01) ** 2 * (1.0 if g >= REST_CLEAR else 6.0)
                cost += (pen / 0.003) ** 2 + ((th - UPPER_PREF) / 18.0) ** 2
                cost += ((5.0 - fore) / 5.0) ** 2 if fore < 5.0 else 0.0
                cost += ((0.045 - d_el) / 0.01) ** 2 if d_el < 0.045 else 0.0          # the elbow outside the torso
                if best is None or cost < best[0]:
                    best = (cost, E.copy(), W.copy(), dict(res=round(res, 4), rest_gap=round(g, 4), pen=round(pen, 4),
                                                           upper=round(up, 1), fore=round(fore, 1), th=th, ph=ph,
                                                           elbow_torso=round(d_el, 3), cost=round(cost, 2),
                                                           dEP=round(dEP, 3), hand=round((body.tail(
                                                               f"RightHand{self.pick_finger}3") - body.head(
                                                               "RightHand")).length, 3), n_ok=0,
                                                           pen_parts={pt: round(arm_penetration(body, "Right", self.ob, (pt,)), 4)
                                                                      for pt in ("forearm", "palm", "finger")}))
                n_ok += 1
        body.reset(base)
        if best is None:
            raise RuntimeError("strumming: no elbow reaches the pick point")
        best[3]["n_ok"] = n_ok
        self.E_hold, self.W_hold, self.hold_info = best[1], best[2], best[3]

    def solve(self, rel, h, flex, first=False):
        """Each frame: the hold's elbow carried by the spine; the pick point moved by the stroke h across the
        strings; the forearm turns about the elbow to put the pick finger on it, the wrist bent by flex; the hand
        lifted off the top a little at a time if any sphere is still in the body."""
        body, ins = self.body, self.ins
        R3 = rel.to_3x3()
        Y = (R3 @ ins.D((0, 1, 0))).normalized()
        Zt = (R3 @ ins.D((0, 0, 1))).normalized()
        E = rel @ self.E_hold
        P = rel @ ins.P(self.P0) + Y * h
        n = (R3 @ ins.D(self.n_l)).normalized()
        W, _ = self.place(E, P, flex, rel @ self.W_hold, iters=3, n=n)
        for _ in range(12):
            pen = arm_penetration_rel(body, "Right", self.ob, rel)
            if pen <= 0.002:
                break
            W = W + Zt * (pen * 0.6 + 0.002)
            body.two_bone("RightArm", "RightForeArm", W, E)
            body.hand_follow("Right", n, flex, 0.0)
        return W


# ---------------------------------------------------------------- claps

CLAP_CURL = (4, 6, 4)
CLAP_ITERS = [16]
CLAP_FWD = [0.30]           # the clap's centre in front of the shoulders
CLAP_PITCH = [40.0]          # the fingers' elevation at the clap (degrees; M5c2 54)
CLAP_LIM = {**PF.WRIST, "ext": 40.0}   # clapping wrists extend up to 40 (decisions 20): the palms meet, not just the fingertips
POLE_K = [0.5]


def clap_pose(body, k, c=None, open_gap=0.13, cross=8.0):
    """Both hands: k = 0 apart .. 1 palms together, in front of the chest, fingers up and a little forward,
    forearms angled in. The right hand turned `cross` degrees more forward than the left so the hands don't read
    as pressed together in prayer. Returns the palm gap measured on the spheres (blender/contact.py)."""
    shL, shR = body.head("LeftArm"), body.head("RightArm")
    mid = (shL + shR) / 2
    if c is None:
        c = mid + Vector((0, -CLAP_FWD[0], -0.07))
    out = {}
    for it in range(CLAP_ITERS[0]):
        for s, sg in (("Left", 1), ("Right", -1)):
            pitch = CLAP_PITCH[0] - (cross / 2) * sg              # fingers' elevation above horizontal
            y = Vector((0, -math.cos(math.radians(pitch)), math.sin(math.radians(pitch))))
            nrm = Vector((-sg, 0, 0))
            sep = out.get(s, 0.0)
            w = c + Vector((sg * (0.022 + (1 - k) * open_gap + sep), 0.035, -0.055))
            sh = body.head(f"{s}Arm")
            body.arm_to(s, w, y, nrm, flex0=-6.0, pole=sh + Vector((sg * 0.22, -0.2, -0.35)), pole_k=POLE_K[0],
                        lim=CLAP_LIM)
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
            curl3(body, s, f, -4, -4, -2)
        thumb3(body, s, 0, 4, 4)


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

    POLE_L = Vector((0.4, -0.15, -0.3))      # the left elbow's pole, from the left shoulder: out and forward, off the chest

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
        thumb3(body, "Right", 10, 20, 10)
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
        self.poleL = shl + self.POLE_L
        down = Vector((0, 0, -1)) - self.N * (-self.N.z)
        # behind the disc (between it and the chest), palm to its back face: the left arm never crosses the ring
        self.QL = self.centre - self.N * (0.0235 + 0.05) + down.normalized() * 0.03
        curl3(body, "Left", "Index", 6, 8, 4)
        for fg in ("Middle", "Ring", "Pinky"):
            curl3(body, "Left", fg, 8, 10, 5)
        thumb3(body, "Left", 0, 0, 0)
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
        thumb3(body, "Left", 15, 25, 15)
        self.target = self.grip - self.n * (0.011 + 0.004)
        place_palm(body, "Left", self.target, self.n, self.pole, 10.0, 0.0, iters=8)

    def solve(self):
        place_palm(self.body, "Left", self.target, self.n, self.pole, 10.0, 0.0, iters=2)
