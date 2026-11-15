"""M5c props that move with the performances (blender/perf.py). New file: blender/aso_props.py (M3's static props,
used by M5 and M5b) is unchanged; its shapes are reused where they fit (the guitar and banjo bodies).

All in the figure frame (-Y forward, +X the player's left, metres, floor z 0), as aso_props.
- kick_drum: the 22" kick of aso_props without its fixed pedal and beater; the SESSION 503 head as before.
- pedal: a heel plate and a footboard hinged at the heel, and the beater on its axle by the batter head; the
  footboard and the beater are separate objects on pivots, keyed per kick (blender/perf.py).
- mic_stand_at: a stand whose mic sits a few centimetres in front of a given mouth point (each singer's own height).
- tambourine: a frame ring with jingles, built round its own centre (parented to the player's hand).
"""
import math
import sys
from pathlib import Path

import bpy
from mathutils import Matrix, Vector

sys.path.insert(0, str(Path(__file__).resolve().parent / "ep"))
import gb  # noqa: E402

import aso_kit as K  # noqa: E402
import aso_props as PR  # noqa: E402

KICK_C = Vector((0.0, -0.95, 0.30))       # shell centre (aso_props: r 0.28, depth 0.42, centre z r + 0.02)
KICK_R, KICK_D = 0.28, 0.42
BATTER_Y = KICK_C.y + KICK_D / 2          # -0.74: the batter head, toward the player
AXLE = Vector((0.0, BATTER_Y + 0.035, 0.115))   # the beater's axle, just behind the batter hoop
BEATER_L = 0.2
HEEL = Vector((0.0, -0.47, 0.03))         # the footboard's hinge at the heel plate
BOARD_L = 0.25
REST_TOE, STRIKE_TOE = 17.0, 4.0           # footboard angle above level (degrees)
REST_BEATER, STRIKE_BEATER = 30.0, -3.0    # beater angle from vertical, + toward the player


def kick_drum(name, parent, head_tex="kick_head"):
    b = PR.B(["kick_shell", "kick_hoop", "metal"])
    c, r, depth = KICK_C, KICK_R, KICK_D
    b.cyl(c, r, depth, "kick_shell", axis=(0, 1, 0), segs=40)
    for dy in (-depth / 2, depth / 2):
        b.cyl(c + Vector((0, dy, 0)), r + 0.012, 0.03, "kick_hoop", axis=(0, 1, 0), segs=40, caps=False)
    for s in (-1, 1):
        b.rod(c + Vector((s * r * 0.8, -0.1, -r * 0.5)), c + Vector((s * (r + 0.12), -0.2, -r - 0.02)), 0.008, "metal")
    o = b.obj(name, parent)
    head = gb.plane(f"{name}_head", tuple(c + Vector((0, -depth / 2 - 0.016, 0))), (2 * r, 2 * r),
                    K.image_mat(f"{name}_headmat", head_tex, "lit", 0.35, 0.6), parent=parent, facing="-Y")
    return o, head


def pedal(name, parent):
    """Returns (base, footboard pivot, beater pivot). Pivots rotate about X: + lifts the toe / swings the beater
    toward the player."""
    b = PR.B(["metal", "kick_hoop"])
    b.bx((0, HEEL.y + 0.02, 0.012), (0.09, 0.07, 0.024), "metal")                     # heel plate
    b.bx((0, (HEEL.y + AXLE.y) / 2 - 0.02, 0.008), (0.05, abs(AXLE.y - HEEL.y) + 0.02, 0.012), "metal")   # base rail
    for s in (-1, 1):                                                                    # axle posts
        b.rod((s * 0.05, AXLE.y, 0.0), (s * 0.05, AXLE.y, AXLE.z + 0.02), 0.007, "metal")
    b.rod((-0.055, AXLE.y, AXLE.z), (0.055, AXLE.y, AXLE.z), 0.008, "metal")              # axle
    base = b.obj(f"{name}_base", parent)
    fb = gb.empty(f"{name}_board_pivot", tuple(HEEL), parent)
    bb = PR.B(["metal"])
    bb.bx((0, -BOARD_L / 2, 0.006), (0.085, BOARD_L, 0.012), "metal")
    board = bb.obj(f"{name}_board", fb)
    fb.rotation_euler.x = board_rot(REST_TOE)                # toe (-Y) up
    bp = gb.empty(f"{name}_beater_pivot", tuple(AXLE), parent)
    be = PR.B(["metal", "kick_hoop"])
    be.rod((0, 0, 0), (0, 0, BEATER_L), 0.006, "metal")
    be.ball((0, 0, BEATER_L), 0.03, 1, scale=(1.0, 0.8, 1.0))
    beater = be.obj(f"{name}_beater", bp)
    bp.rotation_euler.x = beater_rot(REST_BEATER)            # top toward +Y (the player)
    return base, fb, bp


def board_rot(toe_deg):
    """The footboard pivot's X rotation for a toe angle above level (about +X, -angle lifts the -Y end)."""
    return -math.radians(toe_deg)


def beater_rot(deg):
    """The beater pivot's X rotation for an angle from vertical, + toward the player (+Y)."""
    return -math.radians(deg)


def board_toe(angle_deg):
    """The footboard's toe end (figure space) at a given angle."""
    a = math.radians(angle_deg)
    return HEEL + Vector((0, -BOARD_L * math.cos(a), BOARD_L * math.sin(a) + 0.012))


def mic_stand_at(name, mouth, gap=0.09, pole_y=None, pole_x=0.0, parent=None):
    """A mic stand on the floor (figure space): pole straight up at (pole_x, pole_y), a boom to a mic whose grille is
    `gap` in front of the mouth, aimed at it."""
    b = PR.B(["metal", "cable"])
    mouth = Vector(mouth)
    tip = mouth + Vector((0, -gap, -0.015))
    py = mouth.y - 0.42 if pole_y is None else pole_y
    base = Vector((pole_x, py, 0))
    top = Vector((pole_x, py, mouth.z - 0.16))
    b.cyl(base + Vector((0, 0, 0.01)), 0.14, 0.02, "metal", segs=16)
    b.rod(base, top, 0.011, "metal")
    body_end = tip + (tip - top).normalized() * -0.16
    b.rod(top, body_end, 0.008, "metal")
    b.cyl((tip + body_end) / 2, 0.02, (tip - body_end).length, "cable", axis=tip - body_end, segs=12)
    b.ball(tip, 0.024, 1)
    return b.obj(name, parent), top


def tambourine(name):
    """Round its own centre, the disc in the XZ plane (normal -Y): a frame ring with five pairs of jingles."""
    b = PR.B(["tamb", "metal"])
    axis = (0, -1, 0)
    b.cyl((0, 0, 0), 0.125, 0.045, "tamb", axis=axis, segs=28, caps=False)
    b.cyl((0, 0, 0), 0.105, 0.046, "tamb", axis=axis, segs=28, caps=False)
    for k in range(5):
        a = 2 * math.pi * k / 5 + 0.3
        b.cyl((0.115 * math.cos(a), 0, 0.115 * math.sin(a)), 0.024, 0.012, "metal", axis=axis)
    return b.obj(name)
