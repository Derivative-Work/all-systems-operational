"""M7e (human interventions 32: "Check for gray box geometry. The drum kit and banjo are showing hard corners on round
surfaces. The drum kit's rim is floating in air. The server is clearly gray box, as are the coffee mugs."): the
M3 grey-box props remodelled for the M7 look. Installed by blender/look.py when config/look_m7.json m7e.on, in place
of the M3/M5 builders (blender/aso_props.py, blender/perf_props.py, blender/poses.py), which are unchanged, so M3-M5c3
still reproduce.

- Every aso_props.B prop (M7e on): smooth shading with edges sharper than 46 degrees kept hard (the grey box shaded
  every face smooth, so boxes looked blown up and cylinders' end caps went dark), boxes with rounded edges, larger
  cylinders with more sides, tori as real tori.
- The kick drum: a turned shell with rounded bearing edges, the heads lapping over them, solid hoops round the heads
  (the grey box's were open tubes standing off the shell: "the rim floating in air"), eight lugs a side with tension
  rods and claws (T-handles on the batter side), spurs on brackets with rubber feet. The SESSION 503 head as before,
  set into the front hoop.
- The pedal: a base plate, heel hinge, footboard, two posts with bearings, the axle, a cam, a chain (stretched to the
  cam each frame), a spring, the beater shaft and a felt beater. The axle is higher (the grey box's footboard tip
  ran into it) and the heel 5 cm further back, so the player's shoe stops short of the posts and the beater
  ("the kick drummer's foot is clipping into the kick drum arm"); the footboard runs under the cam.
- Mugs: turned (a foot ring, the wall, a rolled lip, the inside, coffee) with a handle swept along a curve; the held
  diner mugs the same, at their size.
- The server rack: rounded body, a perforated front door in a frame (blender/look.py "rack_door"), a lock handle,
  hinges, a status strip, split side panels with recessed grips, vents, casters and levelling feet.
- Chairs: the bentwood (a turned seat, splayed legs, a leg ring, a bent back hoop), the shell chair (a moulded shell
  on four dowel legs: the grey box's flat back read as a black screen in the treehouse), the ladder-back (turned
  posts, finials, bowed slats, stretchers), the bar chair (a turned seat, a foot ring).
Seeds: none (no randomness).
"""
import math
import sys
from pathlib import Path

import bmesh
import bpy
from mathutils import Euler, Matrix, Vector

sys.path.insert(0, str(Path(__file__).resolve().parent / "ep"))
import gb  # noqa: E402

import aso_kit as K  # noqa: E402
import aso_props as PR  # noqa: E402
import perf_props as PP  # noqa: E402

SHARP = math.radians(46.0)
# the pedal: the axle raised, the footboard shortened (the grey box's footboard tip sat at its axle, under the posts)
AXLE = Vector((0.0, PP.BATTER_Y + 0.035, 0.168))
BEATER_L = 0.15
HEEL = Vector((0.0, -0.42, 0.03))     # 5 cm back: the shoe's toe went through the beater (kick_foot_check, O03c)
BOARD_L = 0.28                       # the footboard's toe under the cam


# ---------------------------------------------------------------- mesh helpers (on a builder's bmesh)

def frame(c=(0, 0, 0), axis=(0, 0, 1), spin=0.0):
    rot = Vector((0, 0, 1)).rotation_difference(Vector(axis).normalized()).to_matrix().to_4x4()
    return Matrix.Translation(Vector(c)) @ rot @ Matrix.Rotation(spin, 4, "Z")


def _faces(b, fs, role, normals=True):
    mi = b.i(role) if hasattr(b, "i") else b.mi(role)          # aso_props.B or instruments.IB
    for f in fs:
        f.material_index = mi
        f.smooth = True
    if normals:
        bmesh.ops.recalc_face_normals(b.bm, faces=fs)
    return fs


def lathe(b, prof, role, c=(0, 0, 0), axis=(0, 0, 1), segs=96, closed=False, spin=0.0):
    """A surface of revolution: prof [(r, z)] turned about the axis through c (r 0: a point on the axis)."""
    M = frame(c, axis, spin)
    bm = b.bm
    angs = [2 * math.pi * k / segs for k in range(segs)]
    rings = []
    for r, z in prof:
        if r < 1e-7:
            rings.append([bm.verts.new(M @ Vector((0, 0, z)))])
        else:
            rings.append([bm.verts.new(M @ Vector((r * math.cos(a), r * math.sin(a), z))) for a in angs])
    pairs = list(zip(rings[:-1], rings[1:])) + ([(rings[-1], rings[0])] if closed else [])
    fs = []
    for A, Bv in pairs:
        if len(A) == 1 and len(Bv) == 1:
            continue
        for i in range(segs):
            j = (i + 1) % segs
            if len(A) == 1:
                q = (A[0], Bv[j], Bv[i])
            elif len(Bv) == 1:
                q = (A[i], A[j], Bv[0])
            else:
                q = (A[i], A[j], Bv[j], Bv[i])
            fs.append(bm.faces.new(q))
    return _faces(b, fs, role)


def rrect(r0, r1, z0, z1, rad, n=3):
    """A closed (r, z) profile: a rectangle with rounded corners (n steps a corner), counterclockwise."""
    rad = min(rad, (r1 - r0) / 2 * 0.999, (z1 - z0) / 2 * 0.999)
    pts = []
    for cx, cz, a0 in ((r1 - rad, z0 + rad, -90), (r1 - rad, z1 - rad, 0), (r0 + rad, z1 - rad, 90), (r0 + rad, z0 + rad, 180)):
        for k in range(n + 1):
            a = math.radians(a0 + 90 * k / n)
            pts.append((cx + rad * math.cos(a), cz + rad * math.sin(a)))
    return pts


def rdisc(r1, z0, z1, rad, n=3):
    """An open (r, z) profile for a solid puck on the axis: flat ends, its outer edges rounded."""
    rad = min(rad, r1 * 0.999, (z1 - z0) / 2 * 0.999)
    pts = [(0.0, z0)]
    for cz, a0 in ((z0 + rad, -90), (z1 - rad, 0)):
        for k in range(n + 1):
            a = math.radians(a0 + 90 * k / n)
            pts.append((r1 - rad + rad * math.cos(a), cz + rad * math.sin(a)))
    pts.append((0.0, z1))
    return pts


def circle_prof(R, z, r, n=12):
    return [(R + r * math.cos(2 * math.pi * k / n), z + r * math.sin(2 * math.pi * k / n)) for k in range(n)]


def torus(b, c, R, r, role, axis=(0, 0, 1), segs=64, sides=12):
    return lathe(b, circle_prof(R, 0.0, r, sides), role, c, axis, segs, closed=True)


def catmull(pts, n=6, closed=False):
    P = [Vector(p) for p in pts]
    m = len(P)
    out = []
    rng = range(m) if closed else range(m - 1)
    for i in rng:
        p0 = P[(i - 1) % m] if closed or i > 0 else P[0]
        p1, p2 = P[i], P[(i + 1) % m]
        p3 = P[(i + 2) % m] if closed or i + 2 < m else P[-1]
        for k in range(n):
            t = k / n
            out.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t
                              + (-p0 + 3 * p1 - 3 * p2 + p3) * t ** 3))
    if not closed:
        out.append(P[-1])
    return out


def tube(b, pts, role, rad=0.004, rad2=None, sides=12, caps=True, closed=False, taper=None):
    """A tube along a polyline (parallel-transported frames), elliptical section (rad across the first normal,
    rad2 across the second); taper: (start scale, end scale)."""
    bm = b.bm
    rad2 = rad if rad2 is None else rad2
    P = [Vector(p) for p in pts]
    n = len(P)
    if closed:
        T = [(P[(i + 1) % n] - P[(i - 1) % n]).normalized() for i in range(n)]
    else:
        T = [(P[min(i + 1, n - 1)] - P[max(i - 1, 0)]).normalized() for i in range(n)]
    ref = Vector((0, 0, 1)) if abs(T[0].z) < 0.9 else Vector((1, 0, 0))
    N = (ref - T[0] * ref.dot(T[0])).normalized()
    rings = []
    for i in range(n):
        if i > 0:
            N = T[i - 1].rotation_difference(T[i]) @ N
            N = (N - T[i] * N.dot(T[i])).normalized()
        Bn = T[i].cross(N)
        s = 1.0 if taper is None else taper[0] + (taper[1] - taper[0]) * i / max(1, n - 1)
        rings.append([bm.verts.new(P[i] + N * (s * rad * math.cos(a)) + Bn * (s * rad2 * math.sin(a)))
                      for a in (2 * math.pi * k / sides for k in range(sides))])
    fs = []
    pairs = list(zip(rings[:-1], rings[1:])) + ([(rings[-1], rings[0])] if closed else [])
    for A, Bv in pairs:
        for k in range(sides):
            j = (k + 1) % sides
            fs.append(bm.faces.new((A[k], A[j], Bv[j], Bv[k])))
    if caps and not closed:
        fs.append(bm.faces.new(list(reversed(rings[0]))))
        fs.append(bm.faces.new(rings[-1]))
    return _faces(b, fs, role)


def rod(b, a, c, r, role, sides=16, taper=None):
    return tube(b, [a, c], role, r, sides=sides, taper=taper)


def bbox(b, c, size, role, bevel=0.004, rot=(0, 0, 0), axes=None, segs=3):
    """A box with rounded edges (bevel clamped to a fifth of its smallest side), rotated by Euler rot or onto the
    given axes (three unit vectors: the box's x, y, z)."""
    bm = b.bm
    r = bmesh.ops.create_cube(bm, size=1.0)
    verts = r["verts"]
    R = Matrix(axes).transposed().to_4x4() if axes is not None else Euler(rot).to_matrix().to_4x4()
    S = Matrix.Diagonal((size[0], size[1], size[2], 1.0))
    bmesh.ops.transform(bm, matrix=Matrix.Translation(Vector(c)) @ R @ S, verts=verts)
    faces = list({f for v in verts for f in v.link_faces})
    mi = b.i(role)
    for f in faces:
        f.material_index = mi
        f.smooth = True
    bv = min(bevel, 0.2 * min(size))
    if bv > 1e-5:
        edges = list({e for v in verts for e in v.link_edges})
        res = bmesh.ops.bevel(bm, geom=edges, offset=bv, segments=segs, profile=0.5, affect="EDGES", clamp_overlap=True)
        for f in res["faces"]:
            f.material_index = mi
            f.smooth = True
    return verts


def finish(o, angle=SHARP):
    """Smooth shading, edges sharper than `angle` kept hard."""
    me = o.data
    me.shade_smooth()
    me.set_sharp_from_angle(angle=angle)
    return o


# ---------------------------------------------------------------- the kick drum (figure frame, as perf_props)

def kick_drum(name, parent, head_tex="kick_head"):
    b = PR.B(["kick_shell", "kick_hoop", "chrome", "drum_head", "rubber"])
    c, R, D = PP.KICK_C, PP.KICK_R, PP.KICK_D
    h = D / 2
    Y = (0, 1, 0)                       # the lathe's z runs along +Y (toward the player); its angle 0 is +X
    S = 160
    # shell: rounded bearing edges, 8 mm walls
    lathe(b, [(R - 0.008, -h + 0.002), (R - 0.0045, -h), (R - 0.0015, -h + 0.0006), (R, -h + 0.003), (R, h - 0.003),
              (R - 0.0015, h - 0.0006), (R - 0.0045, h), (R - 0.008, h - 0.002)], "kick_shell", c, Y, S, closed=True)
    # heads, lapping over the bearing edges (the front one behind the printed head)
    for s in (1, -1):
        lathe(b, [(0.0, s * (h + 0.0015)), (R - 0.004, s * (h + 0.0015)), (R + 0.0005, s * (h - 0.0002)),
                  (R + 0.0013, s * (h - 0.004)), (R + 0.0013, s * (h - 0.012))], "drum_head", c, Y, S)
    # hoops: solid, round the heads' collars, standing 1.4 cm proud of each head
    hr0, hr1 = R + 0.0035, R + 0.0165
    for s in (1, -1):
        z0, z1 = sorted((s * (h - 0.010), s * (h + 0.0155)))
        lathe(b, rrect(hr0, hr1, z0, z1, 0.0035), "kick_hoop", c, Y, S, closed=True)
    # lugs, tension rods and claws: eight a side, off the vertical
    for k in range(8):
        a = 2 * math.pi * (k + 0.5) / 8
        rad = Vector((math.cos(a), 0, -math.sin(a)))            # the lathe's angle a in figure space
        tan = Vector((0, 1, 0)).cross(rad)
        for s in (1, -1):
            ay = Vector((0, s, 0))
            lug_c = c + rad * (R + 0.010) + ay * (h - 0.052)
            bbox(b, lug_c, (0.016, 0.044, 0.020), "chrome", 0.006, axes=(tan, ay, rad))
            rr = R + 0.0205
            p0 = c + rad * rr + ay * (h - 0.030)
            p1 = c + rad * rr + ay * (h + 0.019)
            rod(b, p0, p1, 0.0028, "chrome", 12)
            # the claw: along the hoop's outside, hooked over its outer edge
            bbox(b, c + rad * (hr1 + 0.0032) + ay * (h + 0.003), (0.013, 0.026, 0.0065), "chrome", 0.0025, axes=(tan, ay, rad))
            bbox(b, c + rad * (hr1 - 0.002) + ay * (h + 0.0168), (0.013, 0.0042, 0.014), "chrome", 0.0015, axes=(tan, ay, rad))
            if s == 1:                                              # batter side: T-handles
                tip = c + rad * rr + ay * (h + 0.026)
                rod(b, p1, tip, 0.0032, "chrome", 12)
                rod(b, tip - tan * 0.017, tip + tan * 0.017, 0.0034, "chrome", 12)
            else:                                                   # front: square heads
                bbox(b, c + rad * rr + ay * -(h + 0.022), (0.009, 0.007, 0.009), "chrome", 0.0015, axes=(tan, ay, rad))
    # spurs: brackets on the lower sides of the front half, legs splayed forward to rubber feet
    for a in (math.radians(32), math.radians(148)):
        rad = Vector((math.cos(a), 0, -math.sin(a)))
        tan = Vector((0, 1, 0)).cross(rad)
        mount = c + rad * (R + 0.012) + Vector((0, -0.075, 0))
        bbox(b, mount, (0.034, 0.052, 0.026), "chrome", 0.006, axes=(tan, Vector((0, 1, 0)), rad))
        foot = Vector((math.copysign(0.415, rad.x), c.y - 0.17, 0.028))
        top = mount + rad * 0.012
        rod(b, top, foot, 0.0072, "chrome", 16)
        lathe(b, rdisc(0.0135, 0.0, 0.032, 0.006), "rubber", (foot.x, foot.y, 0.0), (0, 0, 1), 24)
    o = finish(b.obj(name, parent))
    head = gb.plane(f"{name}_head", tuple(c + Vector((0, -h - 0.0032, 0))), (2 * R, 2 * R),
                    K.image_mat(f"{name}_headmat", head_tex, "lit", 0.35, 0.6), parent=parent, facing="-Y")
    return o, head


def pedal(name, parent):
    """As perf_props.pedal: (base, footboard pivot, beater pivot), the pivots rotating about X (+ lifts the toe /
    swings the beater toward the player); the chain follows the footboard's toe to the cam."""
    b = PR.B(["chrome", "metal", "rubber"])
    HEEL = PP.HEEL
    ax = AXLE
    y_front = PP.BATTER_Y + 0.012
    bbox(b, (0, (HEEL.y - 0.02 + y_front) / 2, 0.003), (0.105, abs(y_front - HEEL.y) + 0.04, 0.006), "metal", 0.002)
    bbox(b, (0, HEEL.y + 0.012, 0.016), (0.074, 0.03, 0.022), "metal", 0.004)                      # heel hinge
    for s in (-1, 1):
        x = s * 0.062
        bbox(b, (x, ax.y, 0.012), (0.03, 0.05, 0.016), "metal", 0.004)                              # post feet
        rod(b, (x, ax.y, 0.018), (x, ax.y, ax.z + 0.006), 0.0085, "metal", 16)                      # posts
        lathe(b, rdisc(0.015, -0.011, 0.011, 0.004), "metal", (x, ax.y, ax.z), (1, 0, 0), 24)  # bearings
    rod(b, (-0.075, ax.y, ax.z), (0.075, ax.y, ax.z), 0.0048, "chrome", 12)                         # axle
    lathe(b, rdisc(0.021, -0.006, 0.006, 0.002), "chrome", (0.034, ax.y, ax.z), (1, 0, 0), 32) # cam
    # the spring outside the left post, its rocker on the axle
    pts = [(0.078 + 0.0075 * math.cos(t), ax.y + 0.0075 * math.sin(t), 0.035 + 0.075 * t / (2 * math.pi * 12))
           for t in (2 * math.pi * 12 * k / 240 for k in range(241))]
    tube(b, pts, "chrome", 0.0011, sides=6)
    rod(b, (0.078, ax.y, 0.112), (0.078, ax.y, ax.z - 0.004), 0.002, "chrome", 8)
    bbox(b, (0.078, ax.y, ax.z), (0.008, 0.03, 0.012), "chrome", 0.002)
    # the hoop clamp under the batter hoop
    bbox(b, (0, PP.BATTER_Y + 0.004, 0.004), (0.06, 0.03, 0.008), "metal", 0.002)
    base = finish(b.obj(f"{name}_base", parent))
    # footboard (pivot at the heel)
    fb = gb.empty(f"{name}_board_pivot", tuple(HEEL), parent)
    bb = PR.B(["metal", "rubber"])
    bbox(bb, (0, -BOARD_L / 2, 0.006), (0.085, BOARD_L, 0.011), "metal", 0.003)
    bbox(bb, (0, -BOARD_L + 0.008, 0.014), (0.07, 0.012, 0.007), "metal", 0.002)                 # toe stop
    for k in range(5):                                                                              # grip ribs
        bbox(bb, (0, -0.04 - 0.035 * k, 0.0125), (0.06, 0.006, 0.002), "rubber", 0.0008)
    board = finish(bb.obj(f"{name}_board", fb))
    fb.rotation_euler.x = PP.board_rot(PP.REST_TOE)
    # the chain: from the footboard's toe up to the cam, stretched each frame
    cb = PR.B(["chrome"])
    bbox(cb, (0, 0.5, 0), (0.011, 1.0, 0.003), "chrome", 0.0008)
    chain = finish(cb.obj(f"{name}_chain", fb))
    chain.location = (0.034, -BOARD_L + 0.012, 0.014)
    tgt = gb.empty(f"{name}_chain_top", (0.034, ax.y, ax.z - 0.021), parent)
    con = chain.constraints.new("STRETCH_TO")
    con.target, con.volume, con.keep_axis, con.rest_length = tgt, "NO_VOLUME", "PLANE_X", 1.0
    # beater (pivot at the axle): shaft and felt
    bp = gb.empty(f"{name}_beater_pivot", tuple(ax), parent)
    be = PR.B(["chrome", "felt", "metal"])
    rod(be, (0, 0, 0), (0, 0, BEATER_L + 0.01), 0.0042, "chrome", 12)
    lathe(be, rdisc(0.009, -0.012, 0.012, 0.003), "metal", (0, 0, 0.02), (0, 0, 1), 16)         # weight
    lathe(be, rdisc(0.031, -0.011, 0.0262, 0.009, 4), "felt", (0, 0, BEATER_L), (0, -1, 0), 40)      # felt: its face meets the head
    lathe(be, rdisc(0.012, -0.019, -0.009, 0.003), "metal", (0, 0, BEATER_L), (0, -1, 0), 20)       # hub
    beater = finish(be.obj(f"{name}_beater", bp))
    bp.rotation_euler.x = PP.beater_rot(PP.REST_BEATER)
    return base, fb, bp


# ---------------------------------------------------------------- mugs

def _mug(b, role, rb, rt, h, z0=0.0, wall=0.0042, coffee=0.74):
    """A turned mug (foot ring, wall, rolled lip, inside), the coffee in it, and its handle toward +X."""
    w = wall
    prof = [(0.0, z0 + 0.004), (rb - 0.010, z0 + 0.004), (rb - 0.007, z0 + 0.0), (rb - 0.0025, z0 + 0.0),
            (rb - 0.0004, z0 + 0.002), (rb, z0 + 0.006), (rt, z0 + h - 0.004), (rt + 0.0002, z0 + h - 0.0018),
            (rt - 0.0008, z0 + h - 0.0003), (rt - w * 0.5, z0 + h), (rt - w + 0.0008, z0 + h - 0.0005),
            (rt - w, z0 + h - 0.0025), (rb - w * 1.25, z0 + 0.014), (rb - w * 1.6, z0 + 0.0105),
            (rb - w * 2.4, z0 + 0.0092), (0.0, z0 + 0.009)]
    lathe(b, prof, role, (0, 0, 0), (0, 0, 1), 72)
    zc = z0 + h * coffee
    ri = (rb - w * 1.25) + (rt - w - (rb - w * 1.25)) * (zc - z0 - 0.014) / (h - 0.0025 - 0.014)
    lathe(b, [(0.0, zc), (ri + 0.0004, zc)], "coffee", (0, 0, 0), (0, 0, 1), 72)
    k = h / 0.098
    path = [(rt - 0.003, 0, z0 + 0.084 * k), (rt + 0.014 * k, 0, z0 + 0.087 * k), (rt + 0.026 * k, 0, z0 + 0.077 * k),
            (rt + 0.030 * k, 0, z0 + 0.057 * k), (rt + 0.025 * k, 0, z0 + 0.036 * k), (rt + 0.012 * k, 0, z0 + 0.026 * k),
            (rb - 0.003, 0, z0 + 0.024 * k)]
    tube(b, catmull(path, 6), role, 0.0040 * k, 0.0062 * k, sides=14, caps=True)


def mug(name, loc, role="mug", rot_z=0.0, parent=None):
    b = PR.B([role, "coffee"])
    _mug(b, role, 0.040, 0.0435, 0.098)
    return finish(b.obj(name, parent, loc, rot_z))


_HELD = {}


def held_mug_mesh(role):
    """poses._mug_mesh's big diner mug (8 x 12 cm, centred on its origin, handle toward +X), turned."""
    if role in _HELD:
        return _HELD[role]
    b = gb.Builder([K.mat(role, 0.35), K.mat("coffee", 0.1)])
    b.roles = [role, "coffee"]
    b.i = lambda r: b.roles.index(r)
    _mug(b, role, 0.050, 0.054, 0.12, z0=-0.06, wall=0.005)
    me = b.to_mesh(f"mug_{role}_m7e")
    me.shade_smooth()
    me.set_sharp_from_angle(angle=SHARP)
    _HELD[role] = me
    return me


# ---------------------------------------------------------------- the server rack

def server_rack(name, loc, rot=(0, 0, 0)):
    """A 42U rack, 0.6 x 1.0 x 2.0 m, closed, as aso_props.server_rack (front at -Y): blank, no brand."""
    b = PR.B(["rack", "rack_face", "metal", "rack_door", "rubber", "chrome",
              gb.mat("rack_led", "#5fe39a", 0.4, emit=6.0), gb.mat("rack_led_amber", "#ffb347", 0.4, emit=4.0)])
    W, Dp, H = 0.6, 1.0, 2.0
    bbox(b, (0, 0, H / 2 + 0.04), (W, Dp, H - 0.08), "rack", 0.012)                               # body
    bbox(b, (0, 0, 0.055), (W - 0.03, Dp - 0.03, 0.05), "rack_face", 0.006)                       # plinth
    bbox(b, (0, 0, H - 0.01), (W - 0.01, Dp - 0.01, 0.03), "rack", 0.008)                        # roof
    for sx in (-1, 1):                                                                             # roof vents
        for k in range(7):
            bbox(b, (sx * 0.14, -0.3 + 0.1 * k, H + 0.0045), (0.16, 0.012, 0.004), "rack_face", 0.0015)
    bbox(b, (0, 0.33, H + 0.0045), (0.34, 0.07, 0.004), "rubber", 0.0015)                         # cable brush
    # front: the perforated door in its frame, the lock handle, hinges, a status strip
    y = -Dp / 2
    bbox(b, (0, y - 0.006, H / 2 + 0.04), (W - 0.05, 0.012, H - 0.15), "rack_door", 0.003)
    for sx in (-1, 1):
        bbox(b, (sx * (W / 2 - 0.042), y - 0.013, H / 2 + 0.04), (0.042, 0.012, H - 0.13), "rack", 0.004)
    for z in (0.135, H - 0.06):
        bbox(b, (0, y - 0.013, z), (W - 0.05, 0.012, 0.06), "rack", 0.004)
    bbox(b, (W / 2 - 0.042, y - 0.024, 1.02), (0.026, 0.012, 0.16), "metal", 0.004)               # lock body
    bbox(b, (W / 2 - 0.042, y - 0.034, 0.99), (0.016, 0.012, 0.11), "chrome", 0.004)              # lever
    for z in (0.32, 1.02, 1.72):
        lathe(b, rdisc(0.008, -0.03, 0.03, 0.003), "chrome", (-W / 2 + 0.004, y - 0.008, z), (0, 0, 1), 16)
    bbox(b, (0, y - 0.0205, H - 0.06), (0.24, 0.004, 0.026), "rack_face", 0.0015)                 # status strip
    for k in range(6):
        bbox(b, (-0.09 + 0.036 * k, y - 0.0232, H - 0.06), (0.008, 0.002, 0.006), 6 if k != 4 else 7, 0.001)
    # sides: two panels each, a recessed grip on each panel
    for sx in (-1, 1):
        x = sx * W / 2
        bbox(b, (x + sx * 0.0005, 0, H / 2 + 0.04), (0.003, 0.006, H - 0.2), "rack_face", 0.001)
        for zc in (0.55, 1.45):
            bbox(b, (x + sx * 0.0015, 0.0, zc), (0.004, 0.14, 0.035), "rack_face", 0.0015)
            bbox(b, (x + sx * 0.003, 0.0, zc - 0.006), (0.004, 0.12, 0.012), "chrome", 0.0015)
    # casters (swivel plate, fork, wheel) and levelling feet
    for sx in (-1, 1):
        for sy in (-1, 1):
            cx, cy = sx * 0.21, sy * 0.4
            bbox(b, (cx, cy, 0.024), (0.07, 0.07, 0.008), "metal", 0.002)
            for fx in (-1, 1):
                bbox(b, (cx + fx * 0.02, cy + 0.012, 0.0), (0.005, 0.03, 0.05), "metal", 0.0015)
            lathe(b, rdisc(0.034, -0.012, 0.012, 0.006), "rubber", (cx, cy + 0.018, -0.018), (1, 0, 0), 32)
            fx_, fy_ = sx * 0.25, sy * 0.46
            rod(b, (fx_, fy_, 0.03), (fx_, fy_, -0.02), 0.006, "chrome", 12)
            lathe(b, rdisc(0.018, -0.034, -0.02, 0.004), "rubber", (fx_, fy_, 0), (0, 0, 1), 24)
    o = finish(b.obj(name, None, loc))
    o.rotation_euler = rot
    return o


# ---------------------------------------------------------------- chairs

def chair(name, loc, rot_z, role, style=0):
    """As aso_props.chair: 0 bentwood, 1 a mid-century shell, 2 a ladder-back, 3 a stool-height bar chair. The back
    is at local +Y."""
    b = PR.B([role, "metal", "rubber"])
    h = 0.46 if style != 3 else 0.72
    if style == 1:
        _shell(b, role, h)
        for sx in (-1, 1):
            for sy in (-1, 1):
                rod(b, (sx * 0.13, sy * 0.11, h - 0.025), (sx * 0.2, sy * 0.19, 0.012), 0.011, "metal", 14, taper=(1.0, 0.75))
                lathe(b, rdisc(0.0105, 0.0, 0.014, 0.004), "rubber", (sx * 0.2, sy * 0.19, 0), (0, 0, 1), 16)
        for sy in (-1, 1):                                                                         # the base's rails
            rod(b, (-0.17, sy * 0.15, 0.2), (0.17, sy * 0.15, 0.2), 0.006, "metal", 10)
        bbox(b, (0, 0, h - 0.03), (0.3, 0.26, 0.012), "metal", 0.003)                              # the shock mount plate
    else:
        if style == 2:
            bbox(b, (0, 0, h - 0.0175), (0.42, 0.4, 0.035), role, 0.008)
        else:
            lathe(b, rdisc(0.205 if style == 0 else 0.19, -0.02, 0.016, 0.009), role, (0, 0, h - 0.016), (0, 0, 1), 64)
        foot = 0.2 if style == 0 else (0.19 if style == 2 else 0.22)
        top = 0.15 if style != 2 else 0.18
        for sx in (-1, 1):
            for sy in (-1, 1):
                rod(b, (sx * top, sy * top, h - 0.03), (sx * foot, sy * foot, 0.0), 0.016 if style != 2 else 0.017, role,
                    16, taper=(1.0, 0.72))
        if style in (0, 3):                                                                        # the leg ring
            zr = 0.2 if style == 0 else 0.28
            R = (foot + (top - foot) * zr / (h - 0.03)) * math.sqrt(2.0)          # the legs run on the diagonals
            torus(b, (0, 0, zr), R, 0.008 if style == 0 else 0.011, role if style == 0 else "metal", segs=64, sides=10)
        if style == 0:                                                                             # the bent back
            pts = [(-0.15, 0.15, h - 0.02), (-0.165, 0.17, h + 0.12), (-0.175, 0.195, h + 0.3), (-0.13, 0.2, h + 0.42),
                   (0.0, 0.205, h + 0.45), (0.13, 0.2, h + 0.42), (0.175, 0.195, h + 0.3), (0.165, 0.17, h + 0.12),
                   (0.15, 0.15, h - 0.02)]
            tube(b, catmull(pts, 8), role, 0.012, 0.014, sides=14)
            ip = [(-0.1, 0.18, h + 0.02), (-0.12, 0.19, h + 0.2), (-0.07, 0.195, h + 0.3), (0.0, 0.197, h + 0.31),
                  (0.07, 0.195, h + 0.3), (0.12, 0.19, h + 0.2), (0.1, 0.18, h + 0.02)]
            tube(b, catmull(ip, 8), role, 0.009, 0.011, sides=12)
        if style == 2:                                                                             # the ladder back
            for sx in (-1, 1):
                rod(b, (sx * 0.18, 0.18, h), (sx * 0.185, 0.2, h + 0.5), 0.016, role, 16)
                b.ball((sx * 0.185, 0.2, h + 0.515), 0.022, b.i(role))
            for k, z in enumerate((0.2, 0.32, 0.44)):
                pts = [(-0.175, 0.19 + 0.02 * z, h + z), (0.0, 0.215 + 0.02 * z, h + z), (0.175, 0.19 + 0.02 * z, h + z)]
                tube(b, catmull(pts, 8), role, 0.022, 0.008, sides=12)
            for sy in (-1, 1):
                rod(b, (-0.17, sy * 0.17, 0.16), (0.17, sy * 0.17, 0.16), 0.009, role, 12)
            for sx in (-1, 1):
                rod(b, (sx * 0.17, -0.17, 0.12), (sx * 0.17, 0.17, 0.12), 0.009, role, 12)
    return finish(b.obj(name, None, loc, rot_z))


def _shell(b, role, h, nu=26, nv=30, t=0.007):
    """A moulded shell: seat and back in one curved sheet, the sides turned up, solidified."""
    prof = [(-0.215, h - 0.012), (-0.2, h + 0.006), (-0.15, h + 0.004), (-0.04, h - 0.01), (0.07, h - 0.004),
            (0.15, h + 0.03), (0.19, h + 0.12), (0.205, h + 0.25), (0.2, h + 0.37)]
    width = [0.4, 0.42, 0.43, 0.44, 0.44, 0.44, 0.46, 0.47, 0.44]
    P = catmull([(0.0, y, z) for y, z in prof], 4)
    Wd = []
    for i in range(len(P)):
        u = i / (len(P) - 1) * (len(width) - 1)
        k = min(int(u), len(width) - 2)
        Wd.append(width[k] + (width[k + 1] - width[k]) * (u - k))
    m = len(P)
    bm = b.bm
    rows = []
    for i, p in enumerate(P):
        s = i / (m - 1)
        endr = min(1.0, min(s, 1 - s) / 0.06)
        w = Wd[i] * (0.86 + 0.14 * math.sin(endr * math.pi / 2))
        back = max(0.0, (s - 0.45) / 0.55)
        row = []
        for j in range(nu + 1):
            u = -1 + 2 * j / nu
            curl = abs(u) ** 3
            row.append(bm.verts.new((u * w / 2, p.y - 0.045 * back * u * u, p.z + 0.045 * curl * (1 - back))))
        rows.append(row)
    fs = []
    for i in range(m - 1):
        for j in range(nu):
            fs.append(bm.faces.new((rows[i][j], rows[i][j + 1], rows[i + 1][j + 1], rows[i + 1][j])))
    _faces(b, fs, role)
    res = bmesh.ops.solidify(bm, geom=fs, thickness=t)
    for g in res["geom"]:
        if isinstance(g, bmesh.types.BMFace):
            g.material_index = b.i(role)
            g.smooth = True


# ---------------------------------------------------------------- install

def install():
    """Swap the builders (blender/look.py enable, when config m7e.on)."""
    import instruments as IN
    import poses as PO
    PR.B.M7E = True
    IN.IB.M7E = True
    PP.kick_drum = kick_drum
    PP.pedal = pedal
    PP.AXLE, PP.BEATER_L, PP.BOARD_L, PP.HEEL = AXLE, BEATER_L, BOARD_L, HEEL     # perf_band places the foot by these
    PR.mug = mug
    PR.server_rack = server_rack
    PR.chair = chair
    PO._mug_mesh = held_mug_mesh
    return "M7e props: kick drum and pedal, mugs, server rack, chairs remodelled; props smooth-shaded with hard edges"
