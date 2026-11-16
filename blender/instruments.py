"""M5c review (human interventions 15): the acoustic guitar and the banjo rebuilt on Ever Present's guitar neck.

Provenance: the neck, fretboard, frets, nut, headstock and tuner construction below is adapted from Ever Present's
`guitar()` in blender/ep/stage_props.py (vendored unchanged from ../ever-present at commit 726343c, its production
log 96; relicensed MIT for this repository, human interventions 7): a set neck from the heel to the nut, 43 mm wide
at the nut and 56 mm at the heel, with a rounded back; a flat fretboard with frets at true spacing
(nut - scale * (1 - 2^(-n/12))); a bone nut; a generic headstock flared from the nut with long sides and a rounded
crown, tuner posts on the face, gear housings, shafts and keys out the sides; strings from the bridge to the nut.
That code isn't factored out of `guitar()` (the electric's body, pickups and strap are inline), so it's copied here
and generalised to any frame, scale, fret count, width and tuner layout; blender/ep/ stays as vendored.
Added here: the acoustic's body, sound hole, rosette, bridge and saddle, the back angle of the headstock, strings
over the nut to the posts, strap buttons; the banjo's pot, head, hoop, brackets, resonator, tailpiece, bridge,
armrest and fifth-string peg. No maker's outlines, logos or text.

Both are built in their own frame (metres): X along the strings from the bridge saddle (0) toward the headstock,
Y across, toward the bass side (up when played), Z out of the top. `place()` puts that frame in a player's figure
frame. Each returns (object, Spec) where Spec has the points the grips use.
"""
import math
from dataclasses import dataclass, field

import bmesh
import bpy
import numpy as np
from mathutils import Matrix, Vector

import aso_kit as K
import gb


# ---------------------------------------------------------------- materials (names matter: blender/contact.py
# leaves "string", "fret" and "chrome" out of the collision meshes)

def mats():
    P = K.PAL
    return {
        "top": gb.mat("inst_top_spruce", P.get("spruce", "#c9a36a"), 0.45),
        "sides": gb.mat("inst_sides_mahogany", "#5a2c16", 0.4),
        "binding": gb.mat("inst_binding", "#e8e0cc", 0.4),
        "hole": gb.mat("inst_soundhole", "#0b0807", 0.95),
        "neck": gb.mat("inst_neck", "#7a5230", 0.45),                    # Ever Present's guitar_neck
        "board": gb.mat("inst_board", "#24160d", 0.5),                   # Ever Present's guitar_board
        "bone": gb.mat("inst_bone_nut", "#e6e1d4", 0.55),                # Ever Present's drum_head (the nut)
        "fret": gb.mat("inst_fret", "#d6d8dc", 0.12, metal=1.0),
        "string": gb.mat("inst_string", "#d6d8dc", 0.2, metal=1.0),
        "chrome": gb.mat("inst_chrome", "#d6d8dc", 0.12, metal=1.0),     # Ever Present's prop_chrome
        "head": gb.mat("inst_banjo_head", P.get("banjo_head", "#e6dfcc"), 0.6),
        "rim": gb.mat("inst_banjo_rim", P.get("banjo_rim", "#5a3a22"), 0.4),
        "hoop": gb.mat("inst_hoop", "#b9bbbf", 0.2, metal=1.0),           # hoop, flange, armrest: solid for contacts
        "maple": gb.mat("inst_bridge_maple", "#d8b47c", 0.5),
        "strap": gb.mat("inst_strap", "#1b1512", 0.8),                   # Ever Present's guitar_strap
    }


class IB(gb.Builder):
    """gb.Builder with oriented cylinders, rods, boxes in any orientation and prisms from 2D outlines."""

    def __init__(self, M):
        self.keys = list(M)
        super().__init__([M[k] for k in self.keys])

    def mi(self, k):
        return self.keys.index(k)

    def cyl(self, c, r, h, k, axis=(0, 0, 1), r2=None, caps=True, segs=20):
        res = bmesh.ops.create_cone(self.bm, cap_ends=caps, segments=segs, radius1=r, radius2=r if r2 is None else r2,
                                    depth=h)
        rot = Vector((0, 0, 1)).rotation_difference(Vector(axis).normalized()).to_matrix().to_4x4()
        self._tag(res["verts"], self.mi(k), Matrix.Translation(Vector(c)) @ rot)

    def rod(self, a, b, r, k, segs=8):
        a, b = Vector(a), Vector(b)
        self.cyl((a + b) / 2, r, (b - a).length, k, axis=b - a, segs=segs)

    def obox(self, c, size, k, R=None):
        """A box of `size` along the columns of R (3x3; identity: the instrument's own X, Y, Z)."""
        r = bmesh.ops.create_cube(self.bm, size=1.0)
        q = (R if R is not None else Matrix.Identity(3)).to_quaternion()
        self._tag(r["verts"], self.mi(k), Matrix.LocRotScale(Vector(c), q, Vector(size)))

    def prism(self, outline, z0, z1, k, frame=None):
        """outline [(a, b)] in the frame's first two axes, from z0 to z1 along its third. frame = (origin, A, B, N)."""
        o, A, Bv, N = (Vector(v) for v in (frame or ((0, 0, 0), (1, 0, 0), (0, 1, 0), (0, 0, 1))))
        bot = [self.bm.verts.new(o + A * a + Bv * b + N * z0) for a, b in outline]
        top = [self.bm.verts.new(o + A * a + Bv * b + N * z1) for a, b in outline]
        fs = [self.bm.faces.new(list(reversed(bot))), self.bm.faces.new(top)]
        n = len(outline)
        for i in range(n):
            fs.append(self.bm.faces.new([bot[i], bot[(i + 1) % n], top[(i + 1) % n], top[i]]))
        for f in fs:
            f.material_index = self.mi(k)
            f.smooth = False
        bmesh.ops.recalc_face_normals(self.bm, faces=fs)

    def ring(self, c, r0, r1, z0, z1, k, segs=48, a0=0.0, a1=2 * math.pi):
        """An annulus (or an arc of one) in the XY plane from z0 to z1."""
        closed = abs(a1 - a0 - 2 * math.pi) < 1e-6
        m = segs if closed else segs + 1
        angs = [a0 + (a1 - a0) * i / segs for i in range(m)]
        c = Vector(c)
        V = []
        for r in (r0, r1):
            for z in (z0, z1):
                V.append([self.bm.verts.new(c + Vector((r * math.cos(a), r * math.sin(a), z))) for a in angs])
        fs = []
        ib, it, ob, ot = V
        rng = range(m) if closed else range(m - 1)
        for i in rng:
            j = (i + 1) % m
            for a, b in ((it, ot), (ob, ib), (ot, ob), (ib, it)):
                fs.append(self.bm.faces.new([a[i], a[j], b[j], b[i]]))
        if not closed:
            for i in (0, m - 1):
                fs.append(self.bm.faces.new([ib[i], it[i], ot[i], ob[i]]))
        for f in fs:
            f.material_index = self.mi(k)
        bmesh.ops.recalc_face_normals(self.bm, faces=fs)


def _catmull(pts, n=6):
    """Smooth a polyline (list of (a, b)) with a Catmull-Rom spline, n samples per span."""
    P = [pts[0]] + list(pts) + [pts[-1]]
    out = []
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = (np.array(P[k]) for k in (i - 1, i, i + 1, i + 2))
        for s in range(n):
            t = s / n
            out.append(tuple(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t
                                    + (-p0 + 3 * p1 - 3 * p2 + p3) * t ** 3)))
    out.append(tuple(pts[-1]))
    return out


# ---------------------------------------------------------------- the neck (after Ever Present's guitar())

@dataclass
class Neck:
    scale: float                  # bridge saddle (X=0) to nut
    frets: int
    heel: float                   # X where the neck leaves the body
    board_end: float              # X where the fretboard ends over the body (< heel when it overhangs)
    half_nut: float               # half-widths of the neck at the nut and at the heel
    half_heel: float
    board_top: float              # Z of the fretboard's top face
    board_t: float = 0.006        # fretboard thickness (Ever Present: 6 mm)
    shaft_t: float = 0.018        # neck depth below the fretboard, plus the rounded back's 4 mm
    head_tilt: float = 12.0       # headstock back angle (degrees; Ever Present's is flat)
    head: dict = field(default_factory=dict)

    @property
    def nut(self):
        return self.scale

    def fret_x(self, n):
        """Ever Present's true spacing: nut - scale * (1 - 2^(-n/12)), i.e. scale * 2^(-n/12) from the saddle."""
        return self.scale * 2 ** (-n / 12)

    def half(self, x):
        return self.half_heel - (self.half_heel - self.half_nut) * (x - self.heel) / (self.nut - self.heel)


def build_neck(B, N, strings_nut, string_z_nut):
    """Neck, fretboard, frets, nut and headstock in the instrument frame. strings_nut: the strings' Y at the nut
    (for their run on to the tuner posts)."""
    zt, zb = N.board_top, N.board_top - N.board_t
    shaft = [(N.heel, -N.half(N.heel)), (N.nut, -N.half(N.nut)), (N.nut, N.half(N.nut)), (N.heel, N.half(N.heel))]
    B.prism([(a, b * 0.96) for a, b in shaft], zb - N.shaft_t + 0.004, zb, "neck")                 # the shaft
    B.prism([(a, b * 0.82) for a, b in shaft], zb - N.shaft_t, zb - N.shaft_t + 0.004, "neck")     # rounded back
    board = [(N.board_end, -N.half(N.board_end)), (N.nut, -N.half(N.nut)), (N.nut, N.half(N.nut)),
             (N.board_end, N.half(N.board_end))]
    B.prism(board, zb, zt, "board")                                                                 # fretboard
    for n in range(1, N.frets + 1):
        x = N.fret_x(n)
        B.obox((x, 0, zt + 0.0006), (0.0016, 2 * N.half(x) - 0.002, 0.0015), "fret")
    B.obox((N.nut + 0.0025, 0, zt + 0.0012), (0.005, 2 * N.half(N.nut), zt - zb + 0.0035), "bone")  # the nut
    # headstock, flared from the nut (Ever Present's outline), tilted back about the nut's base
    H = dict(flare=0.06, side=0.11, hw=0.0435, crown=0.018, posts=3, p0=0.07, dp=0.042, pb=0.026, hb=0.044,
             thick=0.016)
    H.update(N.head)
    a = math.radians(N.head_tilt)
    o = Vector((N.nut + 0.005, 0, zb))
    U, W, Nn = Vector((math.cos(a), 0, -math.sin(a))), Vector((0, 1, 0)), Vector((math.sin(a), 0, math.cos(a)))
    t = np.linspace(0, 1, 9)
    hn = N.half(N.nut)
    flare = [(H["flare"] * u, hn + (H["hw"] - 0.002 - hn) * math.sin(u * math.pi / 2)) for u in t]
    tip = [(H["flare"] + H["side"] * u, H["hw"] - 0.002 + 0.002 * math.sin(u * math.pi)) for u in t[1:]]
    L = H["flare"] + H["side"]
    crown = [(L + H["crown"] * math.sin(u * math.pi), (H["hw"] - 0.002) * math.cos(u * math.pi)) for u in t[1:-1]]
    side = flare + tip
    out = side + crown + [(p, -q) for p, q in reversed(side)]
    B.prism(out, -H["thick"], 0.0, "neck", (o, U, W, Nn))
    # a short volute behind the nut, so the tilted head reads as one piece with the neck
    B.prism([(-0.006, -hn * 0.8), (0.03, -hn * 0.8), (0.03, hn * 0.8), (-0.006, hn * 0.8)],
            -N.shaft_t - 0.002, -0.004, "neck", (o, U, W, Nn))

    def fr(u, w, n):
        return o + U * u + W * w + Nn * n

    R = Matrix((U, W, Nn)).transposed()           # box axes: along the head, across, out of its face
    posts = []
    for i in range(H["posts"]):
        for sg in (-1, 1):
            u = H["p0"] + H["dp"] * i
            B.cyl(fr(u, sg * H["pb"], 0.006), 0.004, 0.014, "chrome", axis=Nn, segs=8)            # string posts
            B.cyl(fr(u, sg * H["pb"], 0.0005), 0.0065, 0.002, "chrome", axis=Nn, segs=10)         # bushings
            B.cyl(fr(u, sg * H["hb"], -0.008), 0.007, 0.012, "chrome", axis=W, segs=8)             # gear housings
            B.rod(fr(u, sg * (H["hb"] + 0.006), -0.008), fr(u, sg * (H["hb"] + 0.022), -0.008), 0.002, "chrome", 6)
            B.obox(fr(u, sg * (H["hb"] + 0.028), -0.008), (0.005, 0.012, 0.014), "chrome", R)       # keys
            posts.append(fr(u, sg * H["pb"], 0.009))
    # strings over the nut to the posts (each to the nearest post on its side, low strings to the nearer ones)
    left = sorted([p for p in posts if p.y > 0], key=lambda p: p.x)
    right = sorted([p for p in posts if p.y < 0], key=lambda p: p.x)
    ys = sorted(strings_nut)
    lo = [y for y in ys if y < 0]
    hi = [y for y in ys if y >= 0]
    for grp, pp in ((sorted(lo, reverse=True), right), (sorted(hi), left)):
        for y, p in zip(grp, pp):
            B.rod((N.nut, y, string_z_nut), p, 0.0005, "string", segs=4)
    return posts


def strings(B, xs, ys0, ys1, z0, z1, r=0.0006):
    for y0, y1 in zip(ys0, ys1):
        B.rod((xs[0], y0, z0), (xs[1], y1, z1), r, "string", segs=4)


@dataclass
class Spec:
    kind: str
    neck: Neck
    string_y: callable            # (x, i) -> Y of string i at X
    string_z: callable            # x -> Z of the strings
    n_strings: int
    points: dict
    depth: float                  # body (or pot) depth behind the top
    outline: list                 # body outline [(x, half-width)] (guitar) or [] (banjo)


# ---------------------------------------------------------------- the acoustic guitar (dreadnought-ish)

G_SCALE = 0.648                   # Ever Present's scale
G_BODY_L, G_DEPTH = 0.51, 0.10


def _guitar_outline():
    """Half-widths along the body from the tail (0) to the neck end (0.51): lower bout 395 mm, waist 270, upper bout
    290, a rounded tail and fairly square shoulders (dreadnought-ish, no maker's outline)."""
    cp = [(0.0, 0.0), (0.004, 0.045), (0.015, 0.088), (0.035, 0.128), (0.07, 0.168), (0.12, 0.192), (0.17, 0.1975),
          (0.22, 0.19), (0.27, 0.163), (0.31, 0.139), (0.335, 0.135), (0.36, 0.138), (0.40, 0.146), (0.44, 0.145),
          (0.47, 0.134), (0.495, 0.11), (0.505, 0.08), (0.509, 0.045), (0.51, 0.0)]
    return _catmull(cp, 5)


def acoustic_guitar(name):
    M = mats()
    B = IB(M)
    x14 = G_SCALE * 2 ** (-14 / 12)                  # the body joins at the 14th fret
    tail = x14 - G_BODY_L
    half_out = _guitar_outline()
    ring = [(tail + a, w) for a, w in half_out] + [(tail + a, -w) for a, w in reversed(half_out[1:-1])]
    B.prism(ring, -G_DEPTH, -0.003, "sides")                                     # back and sides
    B.prism(ring, -0.003, 0.0, "top")                                            # spruce top
    big = [(tail + a, w + 0.0025 * (w > 0.005)) for a, w in half_out]
    big = [(a, w) for a, w in big] + [(a, -w) for a, w in reversed(big[1:-1])]
    big[0] = (big[0][0] - 0.0025, 0.0)
    B.prism(big, -0.004, -0.0008, "binding")                                     # binding at the top's edge
    B.prism(big, -G_DEPTH, -G_DEPTH + 0.003, "binding")
    hole_x, hole_r = x14 - 0.150, 0.050
    B.cyl((hole_x, 0, 0.0004), 0.061, 0.0008, "binding", segs=48)                # rosette
    B.cyl((hole_x, 0, 0.0006), 0.056, 0.0008, "top", segs=48)
    B.cyl((hole_x, 0, 0.0009), 0.053, 0.0008, "binding", segs=48)
    B.cyl((hole_x, 0, 0.0011), hole_r, 0.0008, "hole", segs=48)                  # sound hole
    B.cyl((hole_x, 0, -0.05), hole_r - 0.001, 0.09, "hole", segs=48)                  # the dark inside
    # bridge and saddle (the saddle's crown at X = 0), bridge pins behind it
    B.obox((-0.006, 0, 0.0045), (0.028, 0.155, 0.009), "board")
    for s in (-1, 1):
        B.obox((-0.004, s * 0.072, 0.0035), (0.024, 0.02, 0.007), "board")     # the wings, lower
    B.obox((0.0, 0, 0.0105), (0.003, 0.074, 0.005), "bone")
    ys_saddle = [(i - 2.5) * 0.0105 for i in range(6)]
    ys_nut = [(i - 2.5) * 0.0072 for i in range(6)]
    for y in ys_saddle:
        B.cyl((-0.013, y, 0.0095), 0.0028, 0.002, "bone", segs=8)
    # neck: heel at the body's edge, the fretboard on to just past the 20th fret over the top
    N = Neck(scale=G_SCALE, frets=20, heel=x14, board_end=G_SCALE * 2 ** (-20 / 12) - 0.008, half_nut=0.0215,
             half_heel=0.028, board_top=0.006, head_tilt=12.0)
    z_sad, z_nut = 0.0128, N.board_top + 0.0024
    build_neck(B, N, ys_nut, z_nut)
    heel = [(x14 - 0.004, 0.0), (x14 - 0.004, -G_DEPTH + 0.002), (x14 + 0.016, -G_DEPTH + 0.004),
            (x14 + 0.05, -0.024), (x14 + 0.05, 0.0)]
    B.prism([(a, b) for a, b in heel], -0.024, 0.024, "neck", ((0, 0, 0), (1, 0, 0), (0, 0, 1), (0, 1, 0)))
    strings(B, (0.0, N.nut), ys_saddle, ys_nut, z_sad, z_nut)
    for y in ys_saddle:                                                          # saddle to the pins
        B.rod((0.0, y, z_sad), (-0.013, y, 0.0105), 0.0006, "string", segs=4)
    endpin = Vector((tail - 0.006, 0, -G_DEPTH / 2))
    B.cyl(endpin, 0.006, 0.012, "chrome", axis=(1, 0, 0), segs=10)
    heelpin = Vector((x14 + 0.03, 0, -0.058))
    B.cyl(heelpin, 0.005, 0.01, "chrome", axis=(0, 0, 1), segs=10)
    o = gb.mesh_obj(name, B.to_mesh(name))
    md = o.modifiers.new("edges", "EDGE_SPLIT")
    md.split_angle = math.radians(35)

    def sy(x, i):
        u = x / N.nut
        return ys_saddle[i] * (1 - u) + ys_nut[i] * u

    def sz(x):
        return z_sad + (z_nut - z_sad) * x / N.nut

    pts = {"hole": Vector((hole_x, 0, 0)), "hole_r": hole_r, "tail": tail, "endpin": endpin, "heelpin": heelpin,
           "x14": x14}
    return o, Spec("guitar", N, sy, sz, 6, pts, G_DEPTH, [(tail + a, w) for a, w in half_out])


# ---------------------------------------------------------------- the banjo (five-string, resonator)

J_SCALE = 0.670
HEAD_R = 0.1397                   # 11" head
POT_C = 0.062                     # the head's centre, from the bridge toward the neck


def banjo(name):
    M = mats()
    B = IB(M)
    c = Vector((POT_C, 0, 0))
    # pot: head, tension hoop, wooden rim, flange, resonator, brackets
    B.cyl(c + Vector((0, 0, -0.001)), HEAD_R, 0.002, "head", segs=56)
    B.ring(c, HEAD_R - 0.002, HEAD_R + 0.006, -0.002, 0.007, "hoop", segs=56)                 # tension hoop
    B.ring(c, HEAD_R - 0.012, HEAD_R + 0.008, -0.068, -0.002, "rim", segs=56)                 # rim
    B.ring(c, HEAD_R + 0.006, 0.172, -0.034, -0.029, "hoop", segs=56)                         # flange
    B.ring(c, 0.163, 0.172, -0.078, -0.029, "rim", segs=56)                                   # resonator sides
    B.cyl(c + Vector((0, 0, -0.076)), 0.165, 0.005, "rim", segs=56)                           # resonator back (shallow)
    nb = 24
    for k in range(nb):
        a = 2 * math.pi * (k + 0.5) / nb
        d = Vector((math.cos(a), math.sin(a), 0))
        B.rod(c + d * (HEAD_R + 0.008) + Vector((0, 0, 0.004)), c + d * (HEAD_R + 0.016) + Vector((0, 0, -0.03)),
              0.0022, "chrome", segs=6)                                                          # hooks and nuts
        B.cyl(c + d * (HEAD_R + 0.016) + Vector((0, 0, -0.026)), 0.0035, 0.008, "chrome", segs=6)
    # armrest over the hoop on the tail side, toward the bass side (where the picking forearm lies)
    B.ring(c, HEAD_R + 0.0, HEAD_R + 0.016, 0.009, 0.015, "hoop", segs=24,
           a0=math.radians(100), a1=math.radians(178))
    for ang in (100, 178):
        a = math.radians(ang)
        d = Vector((math.cos(a), math.sin(a), 0))
        B.rod(c + d * (HEAD_R + 0.008) + Vector((0, 0, 0.01)), c + d * (HEAD_R + 0.02) + Vector((0, 0, -0.028)),
              0.003, "hoop", segs=6)
    # tailpiece: from the hoop at the tail toward the bridge, raised over the head
    t0, t1 = c.x - HEAD_R - 0.004, -0.04
    tp = [(t0, -0.017), (t1, -0.012), (t1, 0.012), (t0, 0.017)]
    B.prism(tp, 0.008, 0.011, "hoop")
    B.obox((t0 - 0.004, 0, -0.012), (0.008, 0.03, 0.04), "hoop")
    # bridge (maple, 16 mm) with its ebony cap
    bridge_h = 0.016
    B.prism([(-0.004, -0.038), (0.004, -0.038), (0.004, 0.038), (-0.004, 0.038)], 0.0, bridge_h - 0.002, "maple")
    B.prism([(-0.002, -0.036), (0.002, -0.036), (0.002, 0.036), (-0.002, 0.036)], bridge_h - 0.002, bridge_h, "board")
    # neck: narrow (32 mm at the nut, 41 at the heel), heel at the rim, the fretboard ending just past the 22nd fret
    heel_x = c.x + HEAD_R + 0.008
    N = Neck(scale=J_SCALE, frets=22, heel=heel_x, board_end=J_SCALE * 2 ** (-22 / 12) - 0.008, half_nut=0.016,
             half_heel=0.0205, board_top=0.0125, head_tilt=10.0,
             head=dict(flare=0.05, side=0.085, hw=0.040, crown=0.016, posts=2, p0=0.06, dp=0.046, pb=0.022,
                       hb=0.04, thick=0.016))
    z_br, z_nut = bridge_h + 0.0008, N.board_top + 0.0024
    # four long strings (4th, 3rd, 2nd, 1st from the bass side) and the short 5th beside the 4th
    ys_br = [0.0345 - 0.0115 * i for i in range(5)]            # at the bridge: 5th, 4th, 3rd, 2nd, 1st
    ys_nut = [0.0105 - 0.007 * i for i in range(4)]            # 4th..1st at the nut
    build_neck(B, N, ys_nut, z_nut)
    x5 = N.fret_x(5)
    # the neck runs on under the fretboard to the heel; the fretboard overhangs the head
    B.prism([(N.board_end, -N.half(N.board_end)), (heel_x, -N.half(heel_x)), (heel_x, N.half(heel_x)),
             (N.board_end, N.half(N.board_end))], 0.004, N.board_top - N.board_t, "neck")
    heel = [(heel_x - 0.003, N.board_top - N.board_t), (heel_x - 0.003, -0.072), (heel_x + 0.012, -0.072),
            (heel_x + 0.05, -0.02), (heel_x + 0.05, N.board_top - N.board_t)]
    B.prism(heel, -0.0185, 0.0185, "neck", ((0, 0, 0), (1, 0, 0), (0, 0, 1), (0, 1, 0)))
    # fifth-string peg on the bass side of the neck at the 5th fret, and the spike the string runs over
    hx = N.half(x5)
    B.cyl((x5 - 0.012, hx + 0.006, N.board_top - 0.012), 0.0055, 0.012, "chrome", axis=(0, 1, 0), segs=10)
    B.rod((x5 - 0.012, hx + 0.012, N.board_top - 0.012), (x5 - 0.012, hx + 0.02, N.board_top - 0.012), 0.002,
          "chrome", 6)
    B.obox((x5 - 0.012, hx + 0.026, N.board_top - 0.012), (0.012, 0.01, 0.006), "bone")
    spike = Vector((x5 - 0.004, 0.0175, N.board_top + 0.0015))
    B.cyl(spike, 0.0012, 0.003, "chrome", segs=6)
    for i, y in enumerate(ys_br):
        x_end = x5 - 0.004 if i == 0 else N.nut
        y_end = 0.0175 if i == 0 else ys_nut[i - 1]
        B.rod((0.0, y, z_br), (x_end, y_end, z_br + (z_nut - z_br) * x_end / N.nut), 0.0005, "string", segs=4)
        B.rod((0.0, y, z_br), (t1, y * 0.5, 0.0115), 0.0005, "string", segs=4)                 # to the tailpiece
    o = gb.mesh_obj(name, B.to_mesh(name))
    md = o.modifiers.new("edges", "EDGE_SPLIT")
    md.split_angle = math.radians(35)

    def sy(x, i):
        """i: 0..3 the long strings 4th..1st."""
        u = x / N.nut
        return ys_br[i + 1] * (1 - u) + ys_nut[i] * u

    def sz(x):
        return z_br + (z_nut - z_br) * x / N.nut

    pts = {"pot": c, "head_r": HEAD_R, "x5": x5, "armrest": (100, 178), "heelpin": Vector((heel_x + 0.03, 0, -0.06)),
           "endpin": Vector((c.x - 0.172, 0, -0.05)), "tail_x": t0}
    return o, Spec("banjo", N, sy, sz, 4, pts, 0.078, [])


# ---------------------------------------------------------------- placing an instrument on a player

def frame_matrix(origin, neck_ang, yaw=0.0, tilt=0.0):
    """Instrument frame -> figure frame: the neck rising neck_ang degrees toward the player's left (+X), turned
    yaw degrees so the head comes forward (-Y), and the top tilted up by tilt degrees (toward the player's eyes)."""
    a = math.radians(neck_ang)
    X = Vector((math.cos(a), 0, math.sin(a)))
    Y = Vector((-math.sin(a), 0, math.cos(a)))
    Z = X.cross(Y)                                                 # (0, -1, 0): out of the top, to the front
    R = Matrix((X, Y, Z)).transposed()
    R = Matrix.Rotation(math.radians(-yaw), 3, "Z") @ R            # the head comes forward
    R = Matrix.Rotation(math.radians(tilt), 3, R.col[0]) @ R       # the top turns up a little
    m = R.to_4x4()
    m.translation = Vector(origin)
    return m


def back_points(spec, n=40):
    """Points on the back of the body or pot, instrument frame (for fitting it against the player)."""
    if spec.kind == "guitar":
        pts = []
        for a, w in spec.outline[::2]:
            for u in np.linspace(-0.9, 0.9, 7):
                pts.append(Vector((a, w * u, -spec.depth)))
        return pts
    c = spec.points["pot"]
    return [c + Vector((0.16 * r * math.cos(t), 0.16 * r * math.sin(t), -spec.depth))
            for r in (0.0, 0.5, 0.9) for t in np.linspace(0, 2 * math.pi, 12, endpoint=False)]


def strap(name, path, width=0.045, thick=0.004, normals=None):
    """A flat strap along a polyline of figure-space points (normals: the body's outward direction at each point,
    so the strap lies flat on it)."""
    M = mats()
    B = IB({"strap": M["strap"]})
    path = [Vector(p) for p in path]
    left, right = [], []
    for i, p in enumerate(path):
        d = (path[min(i + 1, len(path) - 1)] - path[max(i - 1, 0)]).normalized()
        nrm = Vector(normals[i]) if normals else Vector((0, -1, 0))
        w = d.cross(nrm).normalized() * (width / 2)
        nn = nrm.normalized() * (thick / 2)
        left.append((p + w + nn, p + w - nn))
        right.append((p - w + nn, p - w - nn))
    bm = B.bm
    V = [[bm.verts.new(v) for v in (l[0], l[1], r[1], r[0])] for l, r in zip(left, right)]
    fs = [bm.faces.new(V[0][::-1]), bm.faces.new(V[-1])]
    for a, b in zip(V, V[1:]):
        for k in range(4):
            fs.append(bm.faces.new([a[k], a[(k + 1) % 4], b[(k + 1) % 4], b[k]]))
    for f in fs:
        f.material_index = 0
    bmesh.ops.recalc_face_normals(bm, faces=fs)
    return gb.mesh_obj(name, B.to_mesh(name))
