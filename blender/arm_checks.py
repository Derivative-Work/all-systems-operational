"""M5c review 2 (human interventions 16): numeric checks for the strumming and picking arms, the fretting hands and the
claps, on every solved frame, alongside blender/perf.py's pose rules and blender/contact.py's collisions.

The palm normal here comes from the bones alone (the hand's axis and the index-to-little-finger line, by the
chirality of a right and a left hand), not from perf.Body.hand_axes, so the same checks score M5c2's poses (whose
hand_axes had the back of the hand as the palm) and M5c3's. Verified on the mesh by blender/palm_test.py.

- Strumming / picking arm (guitar, banjo): the upper arm's angle below horizontal (at least UPPER_MIN), the forearm's
  angle below horizontal (the hand not above the elbow: at least FORE_MIN), and the rest: the nearest the first half
  of the forearm comes to the body's upper edge (guitar: the bass-side edge of the top over the lower bout) or the
  armrest (banjo), measured to the sleeve's surface (at most REST_MAX).
- Fretting hand: the palm faces the neck (its normal within 60 degrees of the direction from the palm to the neck's
  axis), the palm within PALM_MAX of the neck's surface, the thumb behind the neck or over its top edge, the finger
  roots (knuckles) below the treble edge and the index, middle and ring fingertips on the fretboard side.
- Claps: on the closed frames, each palm faces the other hand (its normal within 60 degrees of the direction to the
  other palm's centre).
"""
import math

import numpy as np
from mathutils import Vector

P = "mixamorig:"
UPPER_MIN = 45.0
FORE_MIN = 0.0
REST_MAX = 0.025
PALM_MAX = 0.035
FACING = 0.5                    # cos 60 degrees
R_FORE = 0.030

REPORT = {}
DEBUG = [False]


def bn(b):
    return b if b.startswith(P) else P + b


def palm_frame(body, side):
    """(y, n, t, centre): finger direction, true palm normal, thumb side and the palm's surface centre."""
    h = body.head(f"{side}Hand")
    y = (body.tail(f"{side}Hand") - h).normalized()
    t = body.head(f"{side}HandIndex1") - body.head(f"{side}HandPinky1")
    t = (t - y * t.dot(y)).normalized()
    n = y.cross(t) if side == "Left" else t.cross(y)
    c = (h + body.head(f"{side}HandMiddle1")) / 2 + n * 0.018
    return y, n, t, c


def _stat(label):
    return REPORT.setdefault(label, {})


def _acc(label, key, v, at, mode="min"):
    S = _stat(label)
    cur = S.get(key)
    if cur is None or (v < cur[0] if mode == "min" else v > cur[0]):
        S[key] = (round(v, 4), at)


def _count(label, key, bad):
    S = _stat(label)
    n, b = S.get(key, (0, 0))
    S[key] = (n + 1, b + int(bool(bad)))


def seg_dist(p, a, b):
    ab = b - a
    t = max(0.0, min(1.0, (p - a).dot(ab) / max(ab.length_squared, 1e-9)))
    return (p - (a + ab * t)).length


def rest_points(spec):
    """The rest line in the instrument's frame: the guitar's bass-side top edge over the lower bout (from the tail to
    the waist), or the banjo's armrest (bass-tail side of the hoop)."""
    if spec.kind == "guitar":
        tail = spec.points["tail"]
        return [Vector((x, float(np.interp(x, [a for a, w in spec.outline], [w for a, w in spec.outline])), 0.0))
                for x in np.linspace(tail + 0.04, tail + 0.27, 24)]
    c, r = spec.points["pot"], spec.points["head_r"]
    return [c + Vector((math.cos(a), math.sin(a), 0)) * (r + 0.008) + Vector((0, 0, 0.015))
            for a in np.radians(np.linspace(95, 190, 20))]


def strum_arm(body, side, G, spec, label, key, t):
    """G: the instrument's frame now (instrument -> armature)."""
    up, fore = body.arm_angles(side)
    at = f"{key} {t:.2f}s"
    _acc(label, "upper arm below horizontal, min (deg)", up, at)
    _acc(label, "forearm below horizontal, min (deg)", fore, at)
    _count(label, f"upper arm under {UPPER_MIN:.0f} deg below horizontal", up < UPPER_MIN)
    _count(label, "hand above the elbow", fore < FORE_MIN)
    E, W = body.head(f"{side}ForeArm"), body.head(f"{side}Hand")
    mid = E.lerp(W, 0.5)
    d = min(seg_dist(G @ p, E, mid) for p in rest_points(spec)) - R_FORE
    _acc(label, "forearm (first half) to the rest edge, max (m)", d, at, "max")
    _count(label, f"forearm more than {REST_MAX * 100:.1f} cm off the rest edge", d > REST_MAX)


def fret_wrap(body, side, G, spec, fret, label, key, t):
    """The fretting hand round the neck at `fret` (the index finger's fret)."""
    N = spec.neck
    y, n, tt, c = palm_frame(body, side)
    G3 = G.to_3x3()
    Xi, Yi, Zi = (G3 @ Vector((1, 0, 0))).normalized(), (G3 @ Vector((0, 1, 0))).normalized(), \
        (G3 @ Vector((0, 0, 1))).normalized()
    # the neck's axis (centre of its section), and the palm's nearest point on it
    zc = N.board_top - (N.board_t + N.shaft_t) / 2
    a0, a1 = G @ Vector((N.fret_x(fret + 4), 0, zc)), G @ Vector((N.nut + 0.01, 0, zc))
    ab = a1 - a0
    u = max(0.0, min(1.0, (c - a0).dot(ab) / ab.length_squared))
    ax = a0 + ab * u
    xl = N.fret_x(fret + 4) + (N.nut + 0.01 - N.fret_x(fret + 4)) * u
    half = N.half(xl)
    to = ax - c
    face = n.dot(to.normalized())
    rad = max(half, (N.board_t + N.shaft_t) / 2)
    gap = to.length - rad
    at = f"{key} {t:.2f}s"
    _count(label, "palm not facing the neck (more than 60 deg off)", face < FACING)
    _acc(label, "palm facing the neck, min (cos)", face, at)
    _count(label, f"palm more than {PALM_MAX * 100:.1f} cm off the neck", gap > PALM_MAX)
    _acc(label, "palm to the neck's surface, max (m)", gap, at, "max")
    th = body.tail(f"{side}HandThumb3")
    rel = th - ax
    behind = rel.dot(Zi) < -((N.board_t + N.shaft_t) / 2 + 0.004) or rel.dot(Yi) > half     # past the back, or over the top
    _count(label, "thumb neither behind the neck nor over its top", not behind)
    kn = body.head(f"{side}HandMiddle1") - ax
    _count(label, "knuckles not below the treble edge", kn.dot(Yi) > -half * 0.5)
    on = 0
    for f in ("Index", "Middle", "Ring"):
        tip = body.tail(f"{side}Hand{f}3") - ax
        ok = tip.dot(Zi) > (N.board_top - zc) - 0.004 and abs(tip.dot(Yi)) < half + 0.004
        on += int(ok)
        if DEBUG[0]:
            print("TIP", f, round(tip.dot(Xi), 3), round(tip.dot(Yi), 3), round(tip.dot(Zi), 3), "half", round(half, 3),
                  "board", round(N.board_top - zc, 3), ok)
    if DEBUG[0]:
        print("THUMB", round(rel.dot(Xi), 3), round(rel.dot(Yi), 3), round(rel.dot(Zi), 3), "palm gap", round(gap, 3))
    _count(label, "index, middle or ring tip off the fretboard", on < 3)


def clap_facing(body, label, key, t):
    yl, nl, tl, cl = palm_frame(body, "Left")
    yr, nr, tr, cr = palm_frame(body, "Right")
    d = cr - cl
    if d.length < 1e-6:
        return
    d.normalize()
    fl, fr = nl.dot(d), nr.dot(-d)
    at = f"{key} {t:.2f}s"
    _count(label, "closed clap with a palm not facing the other hand", min(fl, fr) < FACING)
    _acc(label, "closed clap, palm facing the other hand, min (cos)", min(fl, fr), at)
    S = _stat(label)
    S.setdefault("_facing", []).append(min(fl, fr))


def report_lines():
    if not REPORT:
        return []
    lines = ["arm and hand checks (blender/arm_checks.py; counts are hand-frames failing / checked):"]
    for lab in sorted(REPORT):
        for k, v in sorted(REPORT[lab].items()):
            if k.startswith("_"):
                continue
            if isinstance(v[1], str):
                lines.append(f"  {lab}: {k} {v[0]} ({v[1]})")
            else:
                lines.append(f"  {lab}: {k}: {v[1]} of {v[0]}")
        f = REPORT[lab].get("_facing")
        if f:
            lines.append(f"  {lab}: closed claps, palm facing (cos, min/median): {min(f):.2f} / {float(np.median(f)):.2f}")
    return lines
