"""Props the Ever Present kit lacks, modelled procedurally for the Session 503 band and rooms (M3 grey-box).

Instruments (brief: "acoustic guitar, banjo, kick drum, tambourine"; Ever Present's guitar is a cherry-burst solid
body with a pickguard, i.e. electric, so the acoustic is new too): each is fitted to a library pose and parented to
the person's instance empty, in the library's figure frame (-Y forward, +X the player's left, metres; hands
measured on people 0, 1, 4 and 7: stand hands hang at x +-0.2, z 0.75; raised_one's left hand at (0.31, -0.2, 1.8);
seated_play hips at z 0.5-0.6, hands at y -0.45, z 0.75). The kick drum's front head is the Remotion texture
(O09-KickDrumHead, SESSION 503). No brands, logos or text on anything else: laptops, mugs, chargers and
instruments are blank.

Room props: mic stands, stools, mismatched chairs, cafe tables, mugs, a server rack, laptops, a conference phone,
a charger tangle, evergreens, a lamp post with a weatherproof outlet box, an umbrella.
"""
import math
import sys
from pathlib import Path

import bmesh
import bpy
from mathutils import Matrix, Vector

sys.path.insert(0, str(Path(__file__).resolve().parent / "ep"))
import gb  # noqa: E402

import aso_kit as K  # noqa: E402


class B(gb.Builder):
    """gb.Builder with oriented cylinders and tori, by palette role."""

    def __init__(self, roles, rough=None):
        self.roles = list(roles)
        super().__init__([K.mat(r, rough) if isinstance(r, str) else r for r in roles])

    def i(self, role):
        return role if isinstance(role, int) else self.roles.index(role)

    def cyl(self, c, r, h, role, axis=(0, 0, 1), r2=None, segs=20, caps=True):
        res = bmesh.ops.create_cone(self.bm, cap_ends=caps, segments=segs, radius1=r, radius2=r if r2 is None else r2,
                                    depth=h)
        rot = Vector((0, 0, 1)).rotation_difference(Vector(axis).normalized()).to_matrix().to_4x4()
        self._tag(res["verts"], self.i(role), Matrix.Translation(c) @ rot)

    def rod(self, a, b, r, role, segs=8):
        a, b = Vector(a), Vector(b)
        self.cyl((a + b) / 2, r, (b - a).length, role, axis=b - a, segs=segs)

    def bx(self, c, size, role, rot=(0, 0, 0)):
        self.box(c, size, self.i(role), rot)

    def torus(self, c, R, r, role, axis=(0, 0, 1), segs=24):
        # a ring of short rods approximates the torus
        pts = [Vector((R * math.cos(2 * math.pi * k / segs), R * math.sin(2 * math.pi * k / segs), 0)) for k in range(segs)]
        rot = Vector((0, 0, 1)).rotation_difference(Vector(axis).normalized()).to_matrix()
        for k in range(segs):
            self.rod(Vector(c) + rot @ pts[k], Vector(c) + rot @ pts[(k + 1) % segs], r, role, segs=6)

    def obj(self, name, parent=None, loc=(0, 0, 0), rot_z=0.0):
        return gb.mesh_obj(name, self.to_mesh(name), loc, rot_z, parent)


def _outline_guitar(n=40, lower=0.19, upper=0.145, waist=0.12, L=0.48):
    """Half-widths along the body's length (0 = tail) for a figure-eight acoustic outline."""
    pts = []
    for k in range(n + 1):
        t = k / n
        w = (lower * math.sin(math.pi * min(1, t / 0.58)) if t < 0.58 else 0) + \
            (upper * math.sin(math.pi * (t - 0.5) / 0.5) if t > 0.5 else 0)
        w = max(w, waist if 0.45 < t < 0.62 else 0.0, 0.02)
        pts.append((t * L, w))
    return pts


def _plate(b, outline, depth, role, frame):
    """A slab from a symmetric outline [(along, half-width)], frame = (origin, along axis, across axis, thickness axis)."""
    o, ax, cx, tx = (Vector(v) for v in frame)
    ring = [(a, w) for a, w in outline] + [(a, -w) for a, w in reversed(outline)]
    bot = [b.bm.verts.new(o + ax * a + cx * w - tx * depth / 2) for a, w in ring]
    top = [b.bm.verts.new(o + ax * a + cx * w + tx * depth / 2) for a, w in ring]
    fs = [b.bm.faces.new(list(reversed(bot))), b.bm.faces.new(top)]
    n = len(ring)
    for k in range(n):
        fs.append(b.bm.faces.new((bot[k], bot[(k + 1) % n], top[(k + 1) % n], top[k])))
    for f in fs:
        f.material_index = b.i(role)


# ---------------------------------------------------------------- instruments (figure frame, parented to a person)

def acoustic_guitar(name, parent):
    """Dreadnought held across the body of a standing player: body at the right hip, neck rising to the left."""
    b = B(["spruce", "rosewood", "cable"])
    ang = math.radians(28)                     # neck rises toward the player's left (+X)
    ax = Vector((math.cos(ang), 0, math.sin(ang)))
    tail = Vector((-0.30, -0.19, 0.86))
    _plate(b, _outline_guitar(), 0.10, "spruce", (tail, ax, Vector((-math.sin(ang), 0, math.cos(ang))), (0, 1, 0)))
    b.cyl(tail + ax * 0.31 + Vector((0, -0.051, 0)), 0.045, 0.004, "cable", axis=(0, 1, 0))     # sound hole
    nb, ne = tail + ax * 0.47, tail + ax * 0.98
    b.rod(nb, ne, 0.025, "rosewood")
    b.bx(tail + ax * 1.05, (0.07, 0.03, 0.16), "rosewood", rot=(0, -(math.pi / 2 - ang), 0))
    b.rod((-0.12, 0.0, 1.38), tail + Vector((0, 0.02, 0.02)), 0.012, "cable")   # strap over the shoulder
    o = b.obj(name, parent)
    return o


def banjo(name, parent):
    """Open-back banjo: a round pot with a pale head at the right hip, long thin neck to the left."""
    b = B(["banjo_head", "banjo_rim", "metal", "cable"])
    ang = math.radians(32)
    ax = Vector((math.cos(ang), 0, math.sin(ang)))
    c = Vector((-0.12, -0.2, 0.98))
    b.cyl(c, 0.14, 0.06, "banjo_rim", axis=(0, 1, 0), segs=28)
    b.cyl(c + Vector((0, -0.031, 0)), 0.135, 0.004, "banjo_head", axis=(0, 1, 0), segs=28)
    b.rod(c + ax * 0.12, c + ax * 0.78, 0.02, "banjo_rim")
    b.bx(c + ax * 0.84, (0.05, 0.03, 0.14), "banjo_rim", rot=(0, -(math.pi / 2 - ang), 0))
    b.rod((-0.1, 0.0, 1.38), c + Vector((0, 0.03, 0.05)), 0.012, "cable")
    return b.obj(name, parent)


def tambourine(name, parent, hand=(0.31, -0.2, 1.8)):
    """Held up in raised_one's left hand: a frame ring with jingles, no head (a stomp-clap band's)."""
    b = B(["tamb", "metal"])
    c = Vector(hand) + Vector((0.02, -0.04, 0.1))
    axis = (0.2, -1, 0.3)
    b.cyl(c, 0.125, 0.045, "tamb", axis=axis, segs=28, caps=False)
    b.cyl(c, 0.105, 0.046, "tamb", axis=axis, segs=28, caps=False)
    rot = Vector((0, 0, 1)).rotation_difference(Vector(axis).normalized()).to_matrix()
    for k in range(5):
        a = 2 * math.pi * k / 5 + 0.3
        b.cyl(c + rot @ Vector((0.115 * math.cos(a), 0.115 * math.sin(a), 0)), 0.024, 0.01, "metal", axis=axis)
    return b.obj(name, parent)


def kick_drum(name, parent, head_tex="kick_head", r=0.28, depth=0.42):
    """A standalone 22-inch kick on its spurs with a pedal, in front of a seated player; the front (resonant) head
    shows the Remotion texture, facing the figure's front (-Y), i.e. the audience."""
    b = B(["kick_shell", "kick_hoop", "metal"])
    c = Vector((0, -0.95, r + 0.02))
    b.cyl(c, r, depth, "kick_shell", axis=(0, 1, 0), segs=40)
    for dy in (-depth / 2, depth / 2):
        b.cyl(c + Vector((0, dy, 0)), r + 0.012, 0.03, "kick_hoop", axis=(0, 1, 0), segs=40, caps=False)
    for s in (-1, 1):
        b.rod(c + Vector((s * r * 0.8, -0.1, -r * 0.5)), c + Vector((s * (r + 0.12), -0.2, -r - 0.02)), 0.008, "metal")
    b.bx((0, -0.95 + depth / 2 + 0.12, 0.05), (0.09, 0.22, 0.04), "metal", rot=(0.3, 0, 0))     # pedal
    b.rod((0, -0.95 + depth / 2 + 0.04, 0.05), (0, -0.95 + depth / 2 + 0.02, r), 0.008, "metal")  # beater
    o = b.obj(name, parent)
    head = gb.plane(f"{name}_head", tuple(c + Vector((0, -depth / 2 - 0.016, 0))), (2 * r, 2 * r),
                    K.image_mat(f"{name}_headmat", head_tex, "lit", 0.35, 0.6), parent=parent, facing="-Y")
    return o, head


def stool(name, parent, h=0.5):
    b = B(["console", "metal"])
    b.cyl((0, 0.02, h - 0.03), 0.17, 0.06, "console", segs=20)
    for k in range(3):
        a = 2 * math.pi * k / 3
        b.rod((0, 0.02, h - 0.05), (0.2 * math.cos(a), 0.02 + 0.2 * math.sin(a), 0.0), 0.012, "metal")
    return b.obj(name, parent)


def snare(name, parent):
    b = B(["kick_shell", "metal", "banjo_head"])
    hd = "banjo_head"
    c = Vector((0.28, -0.42, 0.62))
    b.cyl(c, 0.17, 0.13, "kick_shell", segs=28)
    b.cyl(c + Vector((0, 0, 0.066)), 0.17, 0.004, hd, segs=28)
    for k in range(3):
        a = 2 * math.pi * k / 3
        b.rod(c - Vector((0, 0, 0.07)), c + Vector((0.22 * math.cos(a), 0.22 * math.sin(a), -0.62)), 0.008, "metal")
    return b.obj(name, parent)


def mic_stand(name, parent, mouth=1.55, reach=0.42):
    """Straight stand with a short boom ending at the singer's mouth (figure frame: in front of the face)."""
    b = B(["metal", "cable"])
    base = Vector((0.0, -reach - 0.15, 0))
    b.cyl(base + Vector((0, 0, 0.01)), 0.14, 0.02, "metal", segs=16)
    top = base + Vector((0, 0, mouth - 0.12))
    b.rod(base, top, 0.011, "metal")
    tip = Vector((0, -0.17, mouth - 0.04))
    b.rod(top, tip, 0.008, "metal")
    b.cyl(tip + Vector((0, 0.035, 0.01)), 0.022, 0.13, "cable", axis=(0, 1, 0.35), segs=12)
    return b.obj(name, parent)


# ---------------------------------------------------------------- furniture and room props (world space)

def chair(name, loc, rot_z, role, style=0):
    """Mismatched chairs: 0 bentwood, 1 a mid-century shell, 2 a ladder-back, 3 a stool-height bar chair."""
    b = B([role, "metal"])
    h = 0.46 if style != 3 else 0.72
    if style == 1:
        b.bx((0, 0, h), (0.46, 0.44, 0.05), role)
        b.bx((0, 0.21, h + 0.24), (0.46, 0.05, 0.42), role, rot=(-0.15, 0, 0))
        for sx in (-1, 1):
            for sy in (-1, 1):
                b.rod((sx * 0.18, sy * 0.17, h), (sx * 0.22, sy * 0.21, 0), 0.01, "metal")
    else:
        b.cyl((0, 0, h), 0.22 if style != 2 else 0.2, 0.04, role, segs=20) if style != 2 else \
            b.bx((0, 0, h), (0.42, 0.42, 0.04), role)
        for sx in (-1, 1):
            for sy in (-1, 1):
                b.rod((sx * 0.15, sy * 0.15, h), (sx * 0.19, sy * 0.19, 0), 0.015, role)
        if style == 0:
            b.torus((0, 0.17, h + 0.42), 0.18, 0.012, role, axis=(0, 1, 0), segs=16)
            for sx in (-1, 1):
                b.rod((sx * 0.15, 0.17, h), (sx * 0.15, 0.17, h + 0.3), 0.012, role)
        elif style == 2:
            for sx in (-1, 1):
                b.rod((sx * 0.19, 0.19, h), (sx * 0.19, 0.19, h + 0.5), 0.015, role)
            for z in (0.2, 0.32, 0.44):
                b.bx((0, 0.19, h + z), (0.38, 0.02, 0.05), role)
    return b.obj(name, None, loc, rot_z)


def cafe_table(name, loc, r=0.38, h=0.74, square=False):
    b = B(["table", "metal"])
    if square:
        b.bx((0, 0, h), (2 * r, 2 * r, 0.035), "table")
    else:
        b.cyl((0, 0, h), r, 0.035, "table", segs=28)
    b.rod((0, 0, h), (0, 0, 0.03), 0.03, "metal")
    b.cyl((0, 0, 0.015), 0.22, 0.03, "metal", segs=16)
    return b.obj(name, None, loc)


def mug(name, loc, role="mug", rot_z=0.0, parent=None):
    b = B([role])
    b.cyl((0, 0, 0.05), 0.042, 0.1, role, r2=0.045, segs=18)
    b.torus((0.052, 0, 0.055), 0.022, 0.006, role, axis=(0, 1, 0), segs=10)
    return b.obj(name, parent, loc, rot_z)


def server_rack(name, loc, rot=(0, 0, 0)):
    """A 42U rack, 0.6 x 1.0 x 2.0 m, closed: dark body, perforated front (slots), a few status LEDs. Blank."""
    b = B(["rack", "rack_face", "metal", gb.mat("rack_led", "#5fe39a", 0.4, emit=6.0)])
    b.bx((0, 0, 1.0), (0.6, 1.0, 2.0), "rack")
    for k in range(20):
        b.bx((0, -0.505, 0.12 + k * 0.088), (0.52, 0.01, 0.06), "rack_face")
        if k % 3 == 1:
            b.bx((0.22, -0.512, 0.12 + k * 0.088), (0.012, 0.004, 0.012), 3)
    b.bx((0.2, -0.53, 1.0), (0.03, 0.04, 0.3), "metal")                                  # handle
    for sx in (-1, 1):
        for sy in (-1, 1):
            b.cyl((sx * 0.24, sy * 0.42, -0.03), 0.03, 0.06, "metal", segs=10)            # casters
    o = b.obj(name, None, loc)
    o.rotation_euler = rot
    return o


def laptop(name, loc, rot_z, screen_mat=None, open_deg=105):
    """Blank lid (no logo); optional emissive screen facing the user (local -Y side faces the user at +Y?):
    the user sits at local +Y... here the user is at local -Y, the screen faces -Y."""
    b = B(["laptop", "cable"] + ([screen_mat] if screen_mat else []))
    b.bx((0, 0, 0.008), (0.32, 0.22, 0.016), "laptop")
    a = math.radians(open_deg - 90)
    hinge = Vector((0, 0.11, 0.016))
    up = Vector((0, math.sin(a), math.cos(a)))
    b.bx(tuple(hinge + up * 0.105 + Vector((0, 0.005, 0))), (0.32, 0.008, 0.21), "laptop", rot=(-a, 0, 0))
    if screen_mat:
        b.box(tuple(hinge + up * 0.105 + Vector((0, -0.0, 0)) - Vector((0, math.cos(a), -math.sin(a))) * 0.005),
              (0.29, 0.002, 0.18), 2, rot=(-a, 0, 0))
    return b.obj(name, None, loc, rot_z)


def conference_phone(name, loc):
    """The three-legged star speakerphone every meeting room has: generic, no brand."""
    b = B(["phone_body", "metal"])
    for k in range(3):
        a = 2 * math.pi * k / 3 + math.pi / 2
        b.bx((0.11 * math.cos(a), 0.11 * math.sin(a), 0.018), (0.2, 0.09, 0.03), "phone_body", rot=(0, 0, a))
    b.cyl((0, 0, 0.04), 0.07, 0.04, "phone_body", segs=20)
    b.cyl((0, 0, 0.062), 0.03, 0.004, "metal", segs=16)
    return b.obj(name, None, loc)


def charger_tangle(name, loc, rng, n=7, spread=0.45):
    """A tangle of chargers: bricks and cables looping across the table, seeded."""
    b = B(["cable", "brick"])
    for k in range(n):
        p0 = Vector((rng.uniform(-spread, spread), rng.uniform(-spread * 0.5, spread * 0.5), 0.012))
        pts = [p0]
        for j in range(6):
            pts.append(pts[-1] + Vector((rng.uniform(-0.14, 0.14), rng.uniform(-0.1, 0.1), 0.0)))
        for a, c in zip(pts, pts[1:]):
            b.rod(a, c, 0.004, "cable", segs=5)
        if k % 2 == 0:
            b.bx(tuple(pts[-1] + Vector((0, 0, 0.012))), (0.06, 0.05, 0.025), "brick", rot=(0, 0, rng.uniform(0, 3)))
    return b.obj(name, None, loc)


def evergreen(b, base, h, r, role="evergreen", trunk="trunk", tiers=5):
    """A conifer from stacked cones into builder b (role names must be in b.roles)."""
    b.cyl(Vector(base) + Vector((0, 0, h * 0.08)), r * 0.08, h * 0.16, trunk, segs=6)
    for k in range(tiers):
        t = k / tiers
        z = h * (0.12 + 0.8 * t)
        rr = r * (1.0 - 0.75 * t)
        b.cyl(Vector(base) + Vector((0, 0, z + h * 0.13)), rr, h * 0.3, role, r2=0.0, segs=9)


def lamp_post(name, loc, switch_tex=None, lit=True):
    """A park lamp post with a weatherproof outlet box at hand height on its camera side (-Y), where Little Switch
    sits as a flat plane (O20). Returns (post, switch plane or None)."""
    b = B(["lamp_post", "outlet_box", gb.mat("lamp_glow", "#fff1d8", 0.3, emit=6.0 if lit else 0.0)])
    b.cyl((0, 0, 0.15), 0.12, 0.3, "lamp_post", segs=12)
    b.rod((0, 0, 0.3), (0, 0, 3.6), 0.055, "lamp_post")
    b.cyl((0, 0, 3.75), 0.16, 0.3, 2, r2=0.13, segs=12)
    b.cyl((0, 0, 3.95), 0.2, 0.1, "lamp_post", r2=0.05, segs=12)
    b.bx((0, -0.11, 1.1), (0.3, 0.11, 0.42), "outlet_box")                       # the weatherproof box
    b.bx((0, -0.16, 1.33), (0.31, 0.08, 0.025), "outlet_box", rot=(0.5, 0, 0))    # its hinged cover, propped open
    post = b.obj(name, None, loc)
    sw = None
    if switch_tex:
        sw = K.tex_plane(f"{name}_switch", switch_tex, (loc[0], loc[1] - 0.172, loc[2] + 1.1), 0.36, mode="flat",
                         strength=1.0)
    return post, sw


def umbrella(name, parent, hand=(0.31, -0.2, 1.8)):
    """An open umbrella held up in raised_one's hand (figure frame): the only one in the park (O20)."""
    b = B(["umbrella", "metal"])
    hnd = Vector(hand)
    top = hnd + Vector((-0.05, 0.05, 0.55))
    b.rod(hnd + Vector((0, 0, -0.08)), top + Vector((0, 0, 0.05)), 0.01, "metal")
    b.cyl(top - Vector((0, 0, 0.08)), 0.52, 0.22, "umbrella", r2=0.03, segs=8)
    return b.obj(name, parent)
