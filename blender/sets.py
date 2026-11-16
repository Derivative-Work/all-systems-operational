"""The four Session 503 rooms and the O07 void, grey-box (M3): blocking shapes plus the light that sets each mood.

Brief ("Look, cast and series callbacks"): a made-up listener-supported station's live session in four rooms; grey
Seattle daylight through big windows (or open sky) backlights every performer, so people are silhouettes: no faces,
no lip sync. Everything is procedural and deterministic (gb.rng named streams from config/seeds.json main=41).

Generic by design (brief, Guardrails): no station's name, logo, call letters or frequency but the impossible
"50.3 FM"; no set copied from reference photos; no real cafe or venue; no glass-walled room on a public plaza and no
blue stage light (the live room has separate tall windows in a panelled wall, warm practicals, and opaque rainy
panes with nothing modelled outside); the treehouse is a generic cedar room among evergreens, no campus details;
the park skyline is generic towers in fog, no Space Needle, no water, no boats, no fountain.

Coordinates: metres, Z up, floor at 0. Each room has its own frame (see each builder). People face +Y at rot_z 0
(aso_kit.person); the band faces the room's audience and the camera side, with the windows behind it.

build(room, state) resets the file and builds one room for one shot state. Rooms and state keys:
  live      onair "lit"|"unlit", switch "on"|"off", crowd "stand"|"cheer"|"push"|"stopped", clapper bool,
            host "console"|"switch", phone_near bool
  cafe      bulbs_t 0..1 (O16 cascade: 0 all lit; the hub bulb goes first and the dark runs out every strand),
            green_led 0..1 (O15), crowd "stand"|"mugs"
  treehouse night bool (O08 cutaway), band bool, door_open 0..1
  park      crowd "sing"|"empty", walker bool, switch "on"|"off"
  void      (O07: one server rack on a chroma-green plane)
"""
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE / "ep"))
sys.path.insert(0, str(HERE / "lib"))
import aso_kit as K  # noqa: E402
import aso_props as PR  # noqa: E402
import gb  # noqa: E402
import poses  # noqa: E402

ROOMS = K.LOOK["rooms"]
STATE = {}
OBJ = {}          # named handles for cameras and board checks
# M7 (blender/look.py, enabled by blender/coverage_m7.py): functions f(room, state) run after each room is built (the
# look pass: materials, set dressing, light), and a replacement for drizzle(). Empty and None for M3-M5c3.
POST_BUILD = []
DRIZZLE_HOOK = None

# The band, cast by person index from the library (adults, mixed; chosen once and reused in every room, brief: "Built
# once in Blender and reused in every room"). Host: 30. The crowd draws from everyone else.
BAND = {"guitar": 3, "banjo": 8, "kick": 12, "tamb": 17, "singer": 22}
HOST = 30
NOT_CROWD = set(BAND.values()) | {HOST}


# ---------------------------------------------------------------- shared pieces

def band(origin, rot=0.0, mics=True, spread=1.0, pose_override=None):
    """The five-piece (acoustic guitar, banjo, kick drum, tambourine, a backing singer; everyone sings into a mic,
    the gang vocals). Local frame: the band faces local -Y; origin is the kick drummer's front line.
    rot turns the whole band (radians)."""
    root = gb.empty("band_root", origin)
    root.rotation_euler.z = rot
    s = spread
    lay = {  # role: (local x, local y, pose, rot offset)
        "guitar": (-0.95 * s, 0.0, "stand", 0.12),
        "banjo": (0.95 * s, 0.0, "stand", -0.12),
        "kick": (0.0, 0.9, "seated_play", 0.0),
        "tamb": (-2.0 * s, 0.55, "raised_one", 0.3),
        "singer": (2.0 * s, 0.55, "stand", -0.3),
    }
    out = {}
    for role, (x, y, pose, dr) in lay.items():
        p = K.person(f"band_{role}", pose_override or pose if role != "kick" else pose, (x, y, 0), math.pi + dr,
                     who=BAND[role])
        p.parent = root
        out[role] = p
        if mics and role != "kick":
            PR.mic_stand(f"mic_{role}", p)
    PR.acoustic_guitar("guitar", out["guitar"])
    PR.banjo("banjo", out["banjo"])
    if (pose_override or "raised_one") == "raised_one":
        PR.tambourine("tambourine", out["tamb"])
    PR.stool("kick_stool", out["kick"])
    OBJ["kick"], OBJ["kick_head"] = PR.kick_drum("kick", out["kick"])
    PR.snare("snare", out["kick"])
    OBJ["band"] = out
    return out


def crowd(name, n, center, size, target, mix, rng_name, fixed=(), variant_people=(1, 2, 5, 6, 9, 11, 13, 14, 16, 19, 20, 23, 27, 29, 31, 34),
          aisle=0.0):
    """n standing people in a jittered grid over center +- size/2, facing target. mix: {pose: weight}; poses from
    poses.POSES become posed copies of a few people (variant_people) to keep the file small. fixed: extra
    (name, pose, (x, y), who) placed exactly (the O04 phone holder, O12's late clapper)."""
    r = gb.rng(rng_name)
    pool = [i for i in range(48) if i not in NOT_CROWD and i not in {f[3] for f in fixed}]
    cols = max(1, round(math.sqrt(n * size[0] / size[1])))
    rows = math.ceil(n / cols)
    names, weights = list(mix), [mix[k] for k in mix]
    tot = sum(weights)
    out = []
    keep_clear = [Vector((f[2][0], f[2][1])) for f in fixed]
    for k in range(rows * cols):
        u = r.random(6)                                   # drawn for every slot, so states stay comparable
        if k >= n:
            continue
        i, j = k % cols, k // cols
        x = center[0] - size[0] / 2 + (i + 0.5) * size[0] / cols + (u[0] - 0.5) * 0.45 * size[0] / cols
        y = center[1] - size[1] / 2 + (j + 0.5) * size[1] / rows + (u[1] - 0.5) * 0.45 * size[1] / rows
        if any((Vector((x, y)) - c).length < 0.6 for c in keep_clear) or abs(x - center[0]) < aisle:
            continue                                      # aisle: O09 sees the kick drum's head down the middle
        acc, pose = 0.0, names[-1]
        for nm, w in zip(names, weights):
            acc += w / tot
            if u[2] < acc:
                pose = nm
                break
        rz = K.facing((x, y), target) + (u[3] - 0.5) * 0.5
        if pose in poses.POSES:
            who = variant_people[int(u[4] * len(variant_people))]
            o = K.person(f"{name}{k}", pose, (x, y, 0), rz, coll=poses.variant(who, pose, float(u[5])))
        else:
            who = pool[int(u[4] * len(pool))]
            o = K.person(f"{name}{k}", pose, (x, y, 0), rz, who=who)
        out.append(o)
    for nm, pose, (x, y), who, *face in fixed:
        rz = K.facing((x, y), face[0] if face else target)
        if pose in poses.POSES:
            o = K.person(nm, pose, (x, y, 0), rz, coll=poses.variant(who, pose, 0.5))
        else:
            o = K.person(nm, pose, (x, y, 0), rz, who=who)
        OBJ[nm] = o
        out.append(o)
    return out


def window(name, x0, x1, z0, z1, y, facing="-Y", rain=1.0, steam=0.0, strength=3.0, light=600.0, seed=0.0,
           mullion=True, frame_role="trim", side=False, see=0.0):
    """A window opening's pane (rain-on-glass shader), its frame and mullions, and an area light just inside it,
    shining into the room. For side walls (side=True) x0..x1 are the y-extent and y is the wall's x."""
    w, h = x1 - x0, z1 - z0
    c = (x0 + x1) / 2
    zc = (z0 + z1) / 2
    mat = K.window_mat(f"win_{name}", strength=strength, rain=rain, steam=steam, seed=seed, see=see)
    fr = K.mat(frame_role, 0.6)
    if not side:
        sgn = -1 if facing == "-Y" else 1
        gb.plane(f"pane_{name}", (c, y, zc), (w, h), mat, facing=facing)
        for dz in (z0, z1):
            gb.box(f"wf_{name}_{dz:.1f}", (c, y + sgn * 0.04, dz), (w + 0.1, 0.1, 0.08), fr)
        for dx in (x0, x1):
            gb.box(f"wfv_{name}_{dx:.1f}", (dx, y + sgn * 0.04, zc), (0.08, 0.1, h), fr)
        if mullion:
            gb.box(f"wm_{name}", (c, y + sgn * 0.03, z0 + h * 0.62), (w, 0.05, 0.05), fr)
            gb.box(f"wmv_{name}", (c, y + sgn * 0.03, zc), (0.05, 0.05, h), fr)
        if light:
            K.area(f"wl_{name}", (c, y + sgn * 0.12, zc), (c, y + sgn * 5, zc - 0.6), light, w, K.PAL["daylight"], size_y=h)
    else:
        sgn = -1 if facing == "-X" else 1
        gb.plane(f"pane_{name}", (y, c, zc), (w, h), mat, facing=facing)
        for dz in (z0, z1):
            gb.box(f"wf_{name}_{dz:.1f}", (y + sgn * 0.04, c, dz), (0.1, w + 0.1, 0.08), fr)
        for dx in (x0, x1):
            gb.box(f"wfv_{name}_{dx:.1f}", (y + sgn * 0.04, dx, zc), (0.1, 0.08, h), fr)
        if mullion:
            gb.box(f"wm_{name}", (y + sgn * 0.03, c, z0 + h * 0.62), (0.05, w, 0.05), fr)
        if light:
            K.area(f"wl_{name}", (y + sgn * 0.12, c, zc), (y + sgn * 5, c, zc - 0.6), light, h, K.PAL["daylight"], size_y=w)
    return mat


def wall_with_openings(name, axis, at, span, height, openings, m, thick=0.2):
    """A wall along X (axis "x": at = y) or along Y (axis "y": at = x) from span[0] to span[1], with rectangular
    openings [(a0, a1, z0, z1)], built from boxes."""
    a0, a1 = span
    cuts = sorted(openings)
    pieces = []
    cur = a0
    for o0, o1, z0, z1 in cuts:
        if o0 > cur:
            pieces.append((cur, o0, 0, height))
        pieces.append((o0, o1, 0, z0))
        pieces.append((o0, o1, z1, height))
        cur = o1
    if cur < a1:
        pieces.append((cur, a1, 0, height))
    for k, (p0, p1, z0, z1) in enumerate(pieces):
        if p1 - p0 < 1e-3 or z1 - z0 < 1e-3:
            continue
        c, w = (p0 + p1) / 2, p1 - p0
        if axis == "x":
            gb.box(f"{name}{k}", (c, at, (z0 + z1) / 2), (w, thick, z1 - z0), m)
        else:
            gb.box(f"{name}{k}", (at, c, (z0 + z1) / 2), (thick, w, z1 - z0), m)


def drizzle(name, lo, hi, n, rng_name, length=(0.16, 0.3), alpha=0.35, emit=0.6):
    """Drizzle: n thin streaks (4 mm wide) scattered through the box lo..hi, tilted a few degrees by the wind;
    one merged mesh, seeded. Cheaper than particles and identical every render."""
    if DRIZZLE_HOOK is not None:
        return DRIZZLE_HOOK(name, lo, hi, n, rng_name, length, alpha, emit)
    r = gb.rng(rng_name)
    m = gb.mat(f"{name}_mat", "#eef1f3", 0.2, emit=emit, alpha=alpha)
    b = gb.Builder([m])
    for _ in range(n):
        p = [lo[i] + (hi[i] - lo[i]) * r.random() for i in range(3)]
        L = length[0] + (length[1] - length[0]) * r.random()
        b.box(p, (0.004, 0.004, L), rot=(0.12, 0.05, 0))
    o = gb.mesh_obj(name, b.to_mesh(name))
    o.visible_shadow = False
    return o


def finish(fill_hex, fill):
    K.world(fill_hex, fill)
    poses.finish()
    bpy.context.view_layer.update()


# ---------------------------------------------------------------- 1. the live room (O03-O13)

LIVE = {"door_y": (2.3, 3.3), "switch": (3.85, 1.25), "sign": (2.8, 2.72), "band": (0.0, 7.7), "host": (4.9, 2.6),
        "station": (6.9, 3.05)}


def live_room(st):
    """Studio live room, 14 x 10 x 4.6 m. X across (-7..7), Y from the front wall (0) to the window wall (10).
    Five tall rainy windows (1.7 x 3.6 m, separate openings in a panelled wall) behind the band; a door in the left
    wall (x -7) near the front with the ON AIR sign over it and Little Switch beside it, conduit between; the host's
    console at the front right; the 50.3 FM sign on the left wall; acoustic panels, ceiling clouds, rugs."""
    W, D, H = ROOMS["live"]["size"]
    R = ROOMS["live"]
    floor, wall, ceil = K.mat("floor_wood", 0.55), K.mat("wall", 0.9), K.mat("ceiling", 0.9)
    gb.box("floor", (0, D / 2, -0.05), (W, D, 0.1), floor)
    gb.box("ceiling", (0, D / 2, H + 0.05), (W, D, 0.1), ceil)
    gb.box("wall_front", (0, -0.1, H / 2), (W, 0.2, H), wall)
    gb.box("wall_right", (W / 2 + 0.1, D / 2, H / 2), (0.2, D, H), wall)
    d0, d1 = LIVE["door_y"]
    wall_with_openings("wall_left", "y", -W / 2 - 0.1, (0, D), H, [(d0, d1, 0, 2.2)], wall)
    xs = [-5.2, -2.6, 0.0, 2.6, 5.2]
    wall_with_openings("wall_back", "x", D + 0.1, (-W / 2, W / 2), H, [(x - 0.85, x + 0.85, 0.55, 4.15) for x in xs], wall)
    for k, x in enumerate(xs):
        window(f"live{k}", x - 0.85, x + 0.85, 0.55, 4.15, D, "-Y", rain=1.0, strength=R["window_strength"],
               light=R["window_light"], seed=k * 3.1)
    # door, closed, with its frame
    gb.box("door", (-W / 2 - 0.05, (d0 + d1) / 2, 1.1), (0.06, d1 - d0 - 0.04, 2.18), K.mat("door", 0.6))
    gb.box("door_frame_top", (-W / 2 + 0.02, (d0 + d1) / 2, 2.25), (0.06, d1 - d0 + 0.16, 0.1), K.mat("trim"))
    for y in (d0 - 0.05, d1 + 0.05):
        gb.box(f"door_frame{y:.1f}", (-W / 2 + 0.02, y, 1.12), (0.06, 0.1, 2.25), K.mat("trim"))
    # ON AIR sign over the door: a housing with the Remotion face (lit or unlit), facing into the room (+X)
    sy, sz = LIVE["sign"]
    gb.box("onair_box", (-W / 2 + 0.08, sy, sz), (0.12, 0.86, 0.38), K.mat("console", 0.4))
    lit = st.get("onair", "lit") == "lit"
    OBJ["onair"] = K.tex_plane("onair_face", "onair_lit" if lit else "onair_unlit", (-W / 2 + 0.145, sy, sz), 0.32,
                               facing="+X", mode="glow" if lit else "lit", strength=2.2 if lit else 0.15)
    if lit:
        K.point("onair_glow", (-W / 2 + 0.6, sy, sz), 25, "#ff3a2a", radius=0.3, shadow=False)
    # Little Switch: a flat textured plane on the wall by the door (never restyled), wired by conduit to the sign
    swy, swz = LIVE["switch"]
    OBJ["switch"] = K.tex_plane("switch", "switch_on" if st.get("switch", "on") == "on" else "switch_off",
                                (-W / 2 + 0.012, swy, swz), 0.44, facing="+X", mode="flat", strength=1.0)
    cm = K.mat("conduit", 0.4, metal=0.6)
    xw = -W / 2 + 0.03
    gb.box("sw_backbox", (xw - 0.01, swy, swz + 0.24), (0.04, 0.09, 0.09), cm)
    gb.cyl("conduit_up", (xw, swy, (swz + 0.28 + sz) / 2), 0.012, sz - swz - 0.28, cm, n=8)
    gb.cyl("conduit_over", (xw, (swy + sy + 0.43) / 2, sz), 0.012, swy - sy - 0.43, cm, n=8, axis="Y")
    gb.box("conduit_elbow", (xw, swy, sz), (0.05, 0.05, 0.05), cm)
    # station sign (50.3 FM), on the left wall past the door
    OBJ["station"] = K.tex_plane("station_sign", "station_sign", (-W / 2 + 0.03, LIVE["station"][0], LIVE["station"][1]),
                                 0.8, facing="+X", mode="lit", strength=0.5)
    # acoustic panels: fabric slabs on the side walls, clouds overhead
    pm = [K.mat("panel", 0.95), K.mat("panel2", 0.95)]
    k = 0
    for sx in (-1, 1):
        for y in (1.2, 4.6, 5.9, 8.3, 9.3) if sx < 0 else (1.2, 2.5, 3.8, 5.1, 6.4, 7.7, 9.0):
            for z in (1.3, 2.6):
                if sx < 0 and abs(y - LIVE["station"][0]) < 1.2 and z > 2:
                    continue
                gb.box(f"panel{k}", (sx * (W / 2 - 0.05), y, z), (0.1, 1.1, 1.1), pm[k % 2])
                k += 1
    for i, (x, y) in enumerate(((-3.5, 3), (3.5, 3), (-3.5, 6.5), (3.5, 6.5), (0, 4.7))):
        gb.box(f"cloud{i}", (x, y, H - 0.45), (2.6, 1.4, 0.1), pm[i % 2])
    # rugs
    for i, (c, s, rz, role) in enumerate((((0, 7.9), (6.0, 3.0), 0.0, "rug1"), ((-1.8, 4.6), (4.0, 3.0), 0.08, "rug2"),
                                          ((2.4, 5.0), (3.4, 2.6), -0.06, "rug3"))):
        gb.box(f"rug{i}", (c[0], c[1], 0.006 + 0.002 * i), (s[0], s[1], 0.01), K.mat(role, 0.95), rot_z=rz)
    # host's console: a desk with a sloped mixer facing the band, the host behind it (silhouette)
    hx, hy = LIVE["host"]
    to_band = K.facing((hx, hy), (LIVE["band"][0], LIVE["band"][1]))
    dvec = Vector((-math.sin(to_band), math.cos(to_band), 0))
    dc = Vector((hx, hy, 0)) + dvec * 0.62
    cmat = K.mat("console", 0.5)
    gb.box("console_desk", (dc.x, dc.y, 0.38), (1.8, 0.75, 0.76), cmat, rot_z=to_band)
    mixer = gb.box("console_mixer", (dc.x, dc.y, 0.83), (1.4, 0.5, 0.08), K.mat("metal", 0.4), rot_z=to_band)
    mixer.rotation_euler.x = -0.18
    for i, dx in enumerate((-0.7, 0.7)):
        p = dc + Vector((math.cos(to_band), math.sin(to_band), 0)) * dx + dvec * 0.15
        gb.box(f"console_monitor{i}", (p.x, p.y, 1.0), (0.2, 0.2, 0.3), cmat, rot_z=to_band)
    host_at = st.get("host", "console")
    if host_at == "console":
        OBJ["host"] = K.person("host", "seated_play", (hx, hy, 0), to_band, who=HOST)
        PR.stool("host_stool", OBJ["host"])
    else:  # O10: the host at the switch, back to the camera, reaching across to it with the raised (left) hand
        hp = (-W / 2 + 0.5, swy + 0.5, 0)
        OBJ["host"] = K.person("host", "reach", hp, K.facing(hp[:2], (-W / 2, hp[1])),
                               coll=poses.variant(HOST, "reach"))  # back to camera, bent-elbow reach
    # practicals: a floor lamp front right, three bare bulbs on drops over the crowd (warm, dim)
    pr = R["practicals"]
    gb.cyl("lamp_stand", (6.1, 0.8, 0.8), 0.02, 1.6, K.mat("metal"), n=8)
    gb.cyl("lamp_shade", (6.1, 0.8, 1.65), 0.22, 0.3, K.mat("practical", 0.5, emit=1.5), n=16)
    K.point("lamp_light", (6.1, 0.8, 1.55), pr * 0.5, K.PAL["practical"], radius=0.15)
    # (the bulbs hang between the band and the windows: in front of the band they lit faces, board d1)
    for i, x in enumerate((-3.9, -1.3, 1.3, 3.9)):
        gb.cyl(f"drop{i}", (x, 9.3, H - 0.8), 0.004, 1.6, K.mat("cable"), n=6)
        gb.cyl(f"bulb{i}", (x, 9.3, H - 1.64), 0.04, 0.09, K.mat("practical", 0.3, emit=12.0), n=10)
        K.point(f"bulb_light{i}", (x, 9.3, H - 1.7), pr, K.PAL["practical"], radius=0.04)
    # the band, in front of the windows, facing the room
    band(LIVE["band"] + (0,), 0.0)
    # the crowd: ~20 standing, facing the band
    target = (0.0, 8.6)
    mode = st.get("crowd", "stand")
    # singalong gestures only: claps, fists, the push; never the library's open palms held high (lead review: those
    # read as Ever Present's worship crowd)
    mix = {"stand": {"stand": 6, "clap": 1, "phone": 1},
           "cheer": {"stand": 2, "clap": 3, "fist": 2},
           "push": {"push": 5, "clap": 2, "fist": 1},
           "stopped": {"stand": 1}}[mode]
    # the crush: packed close to the band's mics (front line y 7.1), shoulders overlapping
    center, size = ((0.0, 6.25), (5.8, 1.7)) if mode == "push" else ((-0.2, 4.7), (7.6, 3.0))
    fixed = []
    if st.get("phone_near"):
        fixed.append(("phone_holder", "phone", (1.3, 3.25), 40))
    if st.get("clapper"):
        # the crowd's back edge, nearest the camera, turned a little off the band so O12c's camera sees both hands
        # M5: clapper_at / clapper_face (optional) move them for the animatic's O12, side-on against a window
        fixed.append(("late_clapper", "clap_open", st.get("clapper_at", (-0.5, 3.0)), 33, st.get("clapper_face", (-2.3, 5.2))))
    crowd("crowd", 20, center, size, target, mix, "live_crowd", fixed, aisle=0.5 if mode == "cheer" else 0.0)
    finish("#b9bdc0", R["fill"])


# ---------------------------------------------------------------- 2. the coffee shop (O14-O17)

CAFE = {"probe_table": (4.85, 3.0), "hub": (0.4, 4.6, 3.42), "band": (-0.4, 7.4)}


def cafe(st):
    """Coffee shop, 12 x 9 x 3.6 m: the station's "on the road" session. X across (-6..6), Y from the street-side
    front (0) to the back windows (9). Three steamed windows behind the band (back wall), two on the right wall with
    the Polaroid on the pier between them, the probes' table in front of that pier. Counter, shelf and mugs along
    the left wall; mismatched chairs; string lights radiating from one hub bulb to hooks round the walls."""
    W, D, H = ROOMS["cafe"]["size"]
    R = ROOMS["cafe"]
    wall, floor = K.mat("cafe_wall", 0.9), K.mat("cafe_floor", 0.6)
    gb.box("floor", (0, D / 2, -0.05), (W, D, 0.1), floor)
    gb.box("ceiling", (0, D / 2, H + 0.05), (W, D, 0.1), K.mat("wall_dark", 0.9))
    gb.box("wall_front", (0, -0.1, H / 2), (W, 0.2, H), wall)
    gb.box("wall_left", (-W / 2 - 0.1, D / 2, H / 2), (0.2, D, H), wall)
    bx = [-3.7, 0.0, 3.7]
    wall_with_openings("wall_back", "x", D + 0.1, (-W / 2, W / 2), H, [(x - 1.3, x + 1.3, 0.8, 3.1) for x in bx], wall)
    for k, x in enumerate(bx):
        window(f"cafe{k}", x - 1.3, x + 1.3, 0.8, 3.1, D, "-Y", rain=0.6, steam=0.75, strength=R["window_strength"],
               light=R["window_light"], seed=k * 2.3)
    ry = [(0.9, 2.3), (3.7, 5.1)]
    wall_with_openings("wall_right", "y", W / 2 + 0.1, (0, D), H, [(a, b, 0.8, 2.9) for a, b in ry], wall)
    for k, (a, b) in enumerate(ry):
        window(f"cafer{k}", a, b, 0.8, 2.9, W / 2, "-X", rain=0.6, steam=0.75, strength=R["window_strength"],
               light=R["window_light"] * 0.7 if STATE.get("side_light", True) else 0.0, seed=5 + k, side=True)
    # the Polaroid on the right-wall pier, the probes' table in front of it
    OBJ["polaroid"] = K.tex_plane("polaroid", "polaroid", (W / 2 - 0.012, 3.0, 1.38), 0.3, facing="-X", mode="lit",
                                  strength=0.6)
    tx, ty = CAFE["probe_table"]
    PR.cafe_table("probe_table", (tx, ty, 0))
    top = 0.758
    tent = K.tex_plane("table_tent", "table_tent", (tx - 0.02, ty, top + 0.052), 0.105, facing="-X", mode="lit", strength=0.45)
    tent.rotation_euler.y = 0.22
    back = gb.plane("table_tent_back", (tx + 0.025, ty, top + 0.052), (0.153, 0.105), K.mat("paper", 0.9), facing="+X")
    back.rotation_euler.y = -0.22
    OBJ["tent"] = tent
    import sr_kit as SR
    sc = 1.7
    pz = top + SR.PROBE_R * sc + 0.035
    g = SR.probe("anthropic", (tx - 0.05, ty - 0.2, pz), led_role="standby", led=st.get("green_led", 1.0), scale=sc)
    a = SR.probe("openai", (tx - 0.05, ty + 0.21, pz), led_role="amber", led=1.0, scale=sc)
    g.rotation_euler.z = -math.pi / 2 - 0.35          # lenses toward the room (-X), a little toward each other
    a.rotation_euler.z = -math.pi / 2 + 0.35
    for k, o in enumerate((g, a)):                     # a felt coaster each, so the folded arms clear the table
        gb.cyl(f"coaster{k}", (o.location.x, o.location.y, top + 0.012), 0.06, 0.024, K.mat("panel", 0.9), n=20)
    OBJ["probes"] = (g, a)
    PR.mug("pmug0", (tx - 0.12, ty - 0.37, top + 0.018), "mug", 0.8)
    PR.mug("pmug1", (tx - 0.1, ty + 0.38, top + 0.018), "mug2", -1.2)
    SR.refresh()
    # other tables, mismatched chairs, mugs on every surface
    r = gb.rng("cafe_furniture")
    roles = ["chair_a", "chair_b", "chair_c", "chair_d"]
    mroles = ["mug", "mug2", "mug3"]
    tables = [(-3.6, 2.0), (-0.8, 1.6), (2.0, 1.4), (-2.4, 3.6), (1.6, 3.4), (4.8, 6.0), (-4.6, 5.8)]
    for i, (x, y) in enumerate(tables):
        sq = r.random() < 0.4
        PR.cafe_table(f"table{i}", (x, y, 0), r=0.36 if not sq else 0.34, square=sq)
        for j in range(int(2 + 3 * r.random())):
            a_ = r.random() * 6.28
            PR.mug(f"mug_t{i}_{j}", (x + 0.2 * math.cos(a_), y + 0.2 * math.sin(a_), 0.758), mroles[int(r.random() * 3)],
                   r.random() * 6.28)
        for j in range(int(2 + 2 * r.random())):
            a_ = r.random() * 6.28
            PR.chair(f"chair{i}_{j}", (x + 0.62 * math.cos(a_), y + 0.62 * math.sin(a_), 0), a_ + math.pi / 2,
                     roles[int(r.random() * 4)], int(r.random() * 4))
    for j, (a_, sty) in enumerate(((-0.4, 2),)):               # the probes' table: one empty chair (camera side clear)
        PR.chair(f"pchair{j}", (tx + 0.62 * math.cos(a_), ty + 0.62 * math.sin(a_), 0), a_ + math.pi / 2, roles[j], sty)
    # counter, shelf, espresso machine block (blank), mugs along both
    gb.box("counter", (-W / 2 + 0.55, 3.6, 0.52), (0.9, 4.4, 1.04), K.mat("counter", 0.5))
    gb.box("counter_top", (-W / 2 + 0.55, 3.6, 1.06), (1.0, 4.5, 0.05), K.mat("table", 0.4))
    gb.box("espresso", (-W / 2 + 0.45, 2.4, 1.3), (0.6, 0.5, 0.45), K.mat("metal", 0.25, metal=0.8))
    gb.box("pastry_case", (-W / 2 + 0.6, 4.6, 1.25), (0.7, 1.2, 0.35), K.mat("glass", 0.05, alpha=0.3) if "glass" in K.PAL
           else gb.mat("pastry_glass", "#e8eef0", 0.05, alpha=0.25))
    gb.box("shelf", (-W / 2 + 0.12, 3.6, 2.1), (0.25, 3.6, 0.04), K.mat("table", 0.5))
    for j in range(16):
        PR.mug(f"mug_shelf{j}", (-W / 2 + 0.12, 2.0 + 0.21 * j, 2.12), mroles[j % 3], 1.57)
    for j in range(7):
        PR.mug(f"mug_counter{j}", (-W / 2 + 0.85, 3.0 + 0.32 * j, 1.085), mroles[(j + 1) % 3], r.random() * 6.28)
    for k, x in enumerate(bx):                                 # mugs on the window sills
        gb.box(f"sill{k}", (x, D - 0.08, 0.78), (2.7, 0.22, 0.04), K.mat("trim", 0.6))
        for j in range(3):
            PR.mug(f"mug_sill{k}_{j}", (x - 0.9 + 0.8 * j + 0.2 * r.random(), D - 0.1, 0.8), mroles[(j + k) % 3], r.random() * 6.28)
    # string lights: the dependency web
    string_lights(st.get("bulbs_t", 0.0), R["bulbs"])
    # band on a rug in front of the back windows; the crowd between the tables and the band
    gb.box("band_rug", (CAFE["band"][0], CAFE["band"][1] + 0.3, 0.006), (5.4, 2.2, 0.01), K.mat("rug1", 0.95))
    band(CAFE["band"] + (0,), 0.0, spread=0.9)
    mode = st.get("crowd", "stand")
    mix = {"stand": {"stand": 5, "clap": 1, "mug_raise": 2}, "mugs": {"mug_raise": 5, "clap": 3, "stand": 1}}[mode]
    crowd("crowd", 16, (-0.3, 5.3), (7.0, 1.6), (CAFE["band"][0], CAFE["band"][1] + 1), mix, "cafe_crowd")
    finish("#c9c2b6", R["fill"])


def string_lights(t, strength):
    """Strands from one hub bulb (near the ceiling's centre) to hooks round the walls, each sagging; a bulb every
    ~0.45 m. Every bulb is its own object with an "on" property (aso_kit.bulb_mat). t in 0..1: bulbs whose distance
    from the hub (as a fraction of the longest strand) is below t are out (O16: one bulb goes out and the dark runs
    down every strand). key_cascade() keys it over frames for animation."""
    W, D, H = ROOMS["cafe"]["size"]
    hub = Vector(CAFE["hub"])
    hooks = [(-W / 2 + 0.1, y, 3.05) for y in (1.0, 3.0, 5.0, 7.0)] + [(W / 2 - 0.1, y, 3.05) for y in (0.5, 2.6, 6.2, 8.2)] + \
            [(x, D - 0.1, 3.15) for x in (-5.0, -1.9, 1.9, 5.0)] + [(x, 0.1, 3.05) for x in (-3.5, 0.0, 3.5)]
    bm = K.bulb_mat(strength=strength)
    cab = K.mat("cable", 0.6)
    me = None
    longest = max((Vector(h) - hub).length for h in hooks)
    bulbs = []
    wires = gb.Builder([cab])
    for s, h in enumerate(hooks):
        h = Vector(h)
        L = (h - hub).length
        n = max(3, int(L / 0.45))
        pts = []
        for k in range(n + 1):
            u = k / n
            p = hub.lerp(h, u)
            p.z -= 0.32 * math.sin(math.pi * u) * min(1.0, L / 5)
            pts.append(p)
        for a, b in zip(pts, pts[1:]):
            wires.capsule(a, b, 0.004)
        for k, p in enumerate(pts[1:-1], start=1):
            if me is None:
                bb = gb.Builder([bm])
                bb.ball((0, 0, 0), 0.032, scale=(1, 1, 1.3))
                me = bb.to_mesh("bulb")
            o = gb.mesh_obj(f"bulb_{s}_{k}", me, tuple(p - Vector((0, 0, 0.05))))
            o["dist"] = (k / n) * L / longest
            bulbs.append(o)
    hb = gb.mesh_obj("bulb_hub", me, tuple(hub - Vector((0, 0, 0.05))))
    hb["dist"] = 0.0
    bulbs.append(hb)
    gb.mesh_obj("string_wires", wires.to_mesh("string_wires"))
    on_frac = []
    for o in bulbs:
        o["on"] = 1.0 if (t <= 0 or o["dist"] > t) else 0.0
        o.visible_shadow = False
        on_frac.append(o["on"])
    OBJ["bulbs"] = bulbs
    # their light: one soft warm point per strand midpoint and the hub, scaled by the strand's lit share
    for s, h in enumerate(hooks):
        mine = [o for o in bulbs if o.name.startswith(f"bulb_{s}_")]
        lit = sum(o["on"] for o in mine) / max(1, len(mine))
        mid = hub.lerp(Vector(h), 0.55) - Vector((0, 0, 0.35))
        if lit > 0:
            K.point(f"strand_light{s}", tuple(mid), 5 * lit, K.PAL["bulb"], radius=0.5, shadow=False)   # practicals,
            # not a key: at 22 W they lit the crowd and the drummer's face from the front (lead review, O17)
    if hb["on"]:
        K.point("hub_light", tuple(hub - Vector((0, 0, 0.2))), 3, K.PAL["bulb"], radius=0.2, shadow=False)


def key_cascade(start, frames):
    """Key the O16 cascade: from frame `start`, the dark reaches every bulb at its distance share of `frames`."""
    for o in OBJ.get("bulbs", []):
        f = start + int(o["dist"] * frames)
        o["on"] = 1.0
        o.keyframe_insert('["on"]', frame=f - 1)
        o["on"] = 0.0
        o.keyframe_insert('["on"]', frame=f)


# ---------------------------------------------------------------- 3. the treehouse meeting room (O18, O08 cutaway, O19)

TREE = {"band_y": 4.75, "door": (1.2, 2.1), "table": (0.0, 2.45)}


def treehouse(st):
    """A generic cedar treehouse meeting room among evergreens, 7 x 6 m, walls 2.6 m to a gable roof (ridge along Y,
    3.7 m) with two rainy skylights. X across (-3.5..3.5), Y from the front wall (0) to the back wall (6). The
    whiteboard on the back wall behind the band, flanked by windows; side windows onto the trees; a door in the right
    wall onto a deck with mossy railings. Conference table with a speakerphone, laptops and a tangle of chargers.
    Floor at z 0; the forest floor is 9 m below."""
    W, D, H = ROOMS["treehouse"]["size"]
    R = ROOMS["treehouse"]
    night = st.get("night", False)
    WH = 2.6
    ced, ced2 = K.mat("cedar", 0.75), K.mat("cedar_dark", 0.8)
    gb.box("floor", (0, D / 2, -0.06), (W, D, 0.12), ced2)
    # walls with openings
    wall_with_openings("wall_back", "x", D + 0.08, (-W / 2, W / 2), WH,
                       [(-3.15, -2.0, 0.8, 2.3), (2.0, 3.15, 0.8, 2.3)], ced, thick=0.16)
    wall_with_openings("wall_front", "x", -0.08, (-W / 2, W / 2), WH, [(-2.4, -1.0, 0.9, 2.2), (1.0, 2.4, 0.9, 2.2)], ced, thick=0.16)
    wall_with_openings("wall_left", "y", -W / 2 - 0.08, (0, D), WH, [(1.0, 2.6, 0.9, 2.3), (3.6, 5.2, 0.9, 2.3)], ced, thick=0.16)
    d0, d1 = TREE["door"]
    wall_with_openings("wall_right", "y", W / 2 + 0.08, (0, D), WH, [(d0, d1, 0.0, 2.1), (3.6, 5.2, 0.9, 2.3)], ced, thick=0.16)
    # plank lines: thin dark battens so the walls read as boards
    bat = gb.Builder([ced2])
    for z in [0.3 + 0.32 * k for k in range(8)]:
        bat.box((0, D - 0.005, z), (W, 0.012, 0.012))
        bat.box((-W / 2 + 0.005, D / 2, z), (0.012, D, 0.012))
    gb.mesh_obj("battens", bat.to_mesh("battens"))
    # gable roof, ridge along Y at x 0; gable-end triangles; two skylights with rain
    ridge = 3.7
    ang = math.atan2(ridge - WH, W / 2)
    sl = math.hypot(W / 2, ridge - WH)
    for s in (-1, 1):
        o = gb.box(f"roof{s}", (s * W / 4, D / 2, (WH + ridge) / 2), (sl + 0.3, D + 0.6, 0.1), ced2)
        o.rotation_euler.y = -s * ang
    tri = gb.Builder([ced])
    for y in (-0.08, D + 0.08):
        bmv = [tri.bm.verts.new(v) for v in ((-W / 2, y, WH), (W / 2, y, WH), (0, y, ridge))]
        f = tri.bm.faces.new(bmv)
    gb.mesh_obj("gables", tri.to_mesh("gables"))
    for i, x in enumerate((-1.6, 1.6)):
        s_ = 1 if x > 0 else -1
        zr = WH + (ridge - WH) * (1 - abs(x) / (W / 2)) - 0.075
        sky = gb.plane(f"skylight{i}", (x, 5.25, zr), (1.0, 1.2),         # behind the band: a rim, not a key
                       K.window_mat(f"skylight{i}", strength=0.4 if night else 0.9, rain=1.4, seed=11 + i),
                       facing="-Z")
        sky.rotation_euler.y = -s_ * ang
        # (no light under the skylights: as a rim from above-behind it washed the floor and table, and the bounce lit
        # every face, board r2 diagnostic; the back windows alone keep the band in silhouette)
    for i, x in enumerate((-2.2, 0.0, 2.2)):
        gb.box(f"beam{i}", (x, D / 2, WH + 0.05 + (ridge - WH) * (1 - abs(x) / (W / 2)) * 0.0), (0.12, D, 0.16), ced2)
    # windows: real glass with rain, the evergreens behind (sky world bright grey, or night)
    wstr = 0.35 if night else R["window_strength"]
    wl = 0.0 if night else R["window_light"]
    for k, (a, b) in enumerate(((-3.15, -2.0), (2.0, 3.15))):
        window(f"tb{k}", a, b, 0.8, 2.3, D, "-Y", rain=1.0, strength=wstr, light=wl, seed=k, frame_role="cedar_dark", see=0.85)
    for k, (a, b) in enumerate(((-2.4, -1.0), (1.0, 2.4))):
        window(f"tf{k}", a, b, 0.9, 2.2, 0.0, "+Y", rain=1.0, strength=wstr * 0.8, light=0.0, seed=4 + k, frame_role="cedar_dark", see=0.85)
    for k, (a, b) in enumerate(((1.0, 2.6), (3.6, 5.2))):     # side windows beside the band light no one (faces)
        window(f"tl{k}", a, b, 0.9, 2.3, -W / 2, "+X", rain=1.0, strength=wstr, light=0.0, seed=7 + k, side=True,
               frame_role="cedar_dark", see=0.85)
    window("tr0", 3.6, 5.2, 0.9, 2.3, W / 2, "-X", rain=1.0, strength=wstr, light=0.0, seed=9, side=True,
           frame_role="cedar_dark", see=0.85)
    # the door onto the deck (hinged at d1, opening outward)
    hinge = gb.empty("door_hinge", (W / 2 + 0.08, d1, 0))
    gb.box("tdoor", (0, -(d1 - d0) / 2, 1.05), (0.05, d1 - d0 - 0.02, 2.08), K.mat("door", 0.6), parent=hinge)
    hinge.rotation_euler.z = st.get("door_open", 0.0) * math.radians(100)     # swings out onto the deck
    if st.get("door_open", 0.0) > 0 and not night:
        K.area("door_light", (W / 2 + 0.2, (d0 + d1) / 2, 1.1), (0, (d0 + d1) / 2, 0.8), R["window_light"] * 0.4, 0.9,
               K.PAL["daylight"], size_y=2.1)
    # the whiteboard (Remotion texture) behind the band
    wb = K.tex_plane("whiteboard", "whiteboard_full", (0, D - 0.02, 1.86), 1.36, facing="-Y", mode="lit",
                     strength=2.4 if not night else 0.05)       # bright behind the band: part of its backlight
    OBJ["whiteboard"] = wb
    w_ = wb.dimensions.x
    gb.box("wb_frame", (0, D - 0.005, 1.86), (w_ + 0.06, 0.02, 1.42), K.mat("whiteboard_frame", 0.4))
    gb.box("wb_tray", (0, D - 0.06, 1.16), (w_ * 0.6, 0.08, 0.03), K.mat("whiteboard_frame", 0.4))
    # conference table, chairs, speakerphone, laptops, chargers
    tx, ty = TREE["table"]
    gb.box("ctable", (tx, ty, 0.73), (2.6, 1.1, 0.05), K.mat("cedar_dark", 0.5))
    for sx in (-1, 1):
        gb.box(f"ctable_leg{sx}", (tx + sx * 1.0, ty, 0.36), (0.08, 0.8, 0.72), K.mat("metal"))
    PR.conference_phone("speakerphone", (tx, ty + 0.1, 0.755))
    PR.charger_tangle("chargers", (tx + 0.55, ty + 0.12, 0.755), gb.rng("chargers"), n=8, spread=0.4)
    scr = gb.mat("laptop_screen", "#dfe6ee", 0.4, emit=2.6 if night else 0.15)
    seats = [(-0.85, ty - 0.95), (0.05, ty - 1.0), (0.95, ty - 0.9)]
    for i, (x, y) in enumerate(seats):
        PR.laptop(f"laptop{i}", (x, ty - 0.3, 0.755), 0.0, scr, open_deg=108)
        PR.chair(f"tchair{i}", (x, y + 0.05, 0), math.pi, ["chair_d", "chair_b", "chair_d"][i], 1)
        if night:
            K.point(f"laptop_glow{i}", (x, ty - 0.45, 0.95), 0.7, "#e6eef8", radius=0.12)
    for i, x in enumerate((-0.9, 0.9)):
        PR.chair(f"tchair_far{i}", (x, ty + 0.85, 0), 0.0, "chair_d", 1)
    # people: three at the table's near side, hunched over the laptops (O08 cutaway) or watching the band
    who = (36, 41, 45)
    for i, (x, y) in enumerate(seats):
        if night or st.get("band", True):
            K.person(f"meeting{i}", "seated_phone" if night else "seated_phone", (x, y + 0.08, 0), 0.0 + (i - 1) * 0.08,
                     who=who[i])
    if st.get("band", True) and not night:
        band((0.15, TREE["band_y"], 0), 0.0, spread=0.78)
    # deck, railings with moss
    deck_and_forest(st)
    # interior practical: a warm pendant over the table
    gb.cyl("pendant", (tx, ty, 2.45), 0.2, 0.18, K.mat("practical", 0.4, emit=3.0 if night else 0.0), r2=0.06, n=16)
    if night:                                   # off by day: it front-lit the band's faces (board d3, d4)
        K.point("pendant_light", (tx, ty, 2.3), 18, K.PAL["practical"], radius=0.2)
    if night:
        K.world("#14171b", 0.25)
        poses.finish()
        bpy.context.view_layer.update()
    else:
        # The sky seen through the glass is an emissive dome kept out of the light probes; the world itself is near
        # black. (Eevee lit the room with the full world strength: the camera-ray world trick only works in Cycles,
        # and a brighter world lit the band's faces, lead review.)
        sky_dome((0, 3, 0), 45.0, "#d4d8da", 2.2)
        K.world("#cfd3d5", 0.03)          # bright through the glass, dim as light: band in silhouette
        poses.finish()
        bpy.context.view_layer.update()


def sky_dome(center, r, hexcol, strength):
    """A big emissive cylinder round a set: the sky seen past the trees, bright to the camera but hidden from the
    light probes, so it doesn't light the interior."""
    m = gb.mat("sky_dome", hexcol, 1.0, emit=strength)
    o = gb.cyl("sky_dome", (center[0], center[1], center[2]), r, 120.0, m, n=48)
    for k in ("hide_probe_volume", "hide_probe_sphere", "hide_probe_plane"):
        if hasattr(o, k):
            setattr(o, k, True)
    o.visible_shadow = False
    return o


def deck_and_forest(st):
    W, D, H = ROOMS["treehouse"]["size"]
    ced2 = K.mat("cedar_dark", 0.8)
    moss = K.mat("moss", 0.95)
    x0, x1, y0, y1 = W / 2 + 0.1, W / 2 + 3.4, -0.4, 4.2
    gb.box("deck", ((x0 + x1) / 2, (y0 + y1) / 2, -0.06), (x1 - x0, y1 - y0, 0.12), ced2)
    rail = gb.Builder([ced2, moss])
    r = gb.rng("moss")
    for (a, b) in (((x1, y0), (x1, y1)), ((x0, y0), (x1, y0)), ((x0, y1), (x1, y1))):
        a, b = Vector((a[0], a[1], 0)), Vector((b[0], b[1], 0))
        n = int((b - a).length / 1.1) + 1
        for k in range(n + 1):
            p = a.lerp(b, k / n)
            rail.box((p.x, p.y, 0.5), (0.09, 0.09, 1.0))
        mid = (a + b) / 2
        d = b - a
        rail.box((mid.x, mid.y, 1.02), (abs(d.x) + 0.1, abs(d.y) + 0.1, 0.07))
        rail.box((mid.x, mid.y, 0.5), (abs(d.x) + 0.05, abs(d.y) + 0.05, 0.04))
        for k in range(int((b - a).length / 0.18)):                      # moss clumps along the top rail
            p = a.lerp(b, r.random())
            rail.ball((p.x + 0.03 * (r.random() - 0.5), p.y + 0.03 * (r.random() - 0.5), 1.06), 0.03 + 0.03 * r.random(), 1,
                      scale=(1.6, 1.6, 0.6))
    gb.mesh_obj("railings", rail.to_mesh("railings"))
    # supporting posts down to the forest floor
    for x, y in ((x0, y0), (x1, y0), (x1, y1), (-W / 2, 0), (-W / 2, D), (W / 2, D)):
        gb.box(f"stilt{x:.1f}_{y:.1f}", (x, y, -4.6), (0.25, 0.25, 9.0), ced2)
    # the forest: evergreens all round (fog-faded), the floor 9 m down
    night = st.get("night", False)
    fogc = "#1a1d21" if night else "#cfd3d5"
    ev = K.fog_mat("evergreen_fog", K.PAL["evergreen"], fogc, dist=22.0, emit_fog=0.3 if night else 1.0)
    tr = K.fog_mat("trunk_fog", K.PAL["trunk"], fogc, dist=22.0, emit_fog=0.3 if night else 1.0)
    trees = PR.B([ev, tr])
    trees.roles = ["evergreen", "trunk"]
    r = gb.rng("treehouse_trees")
    for k in range(70):
        a = r.random() * 2 * math.pi
        d = 6.5 + 30 * r.random() ** 1.3
        x, y = d * math.cos(a), 3 + d * math.sin(a)
        if -4.5 < x < 7.5 and -1.5 < y < 7.5:
            continue
        h = 24 + 14 * r.random()
        PR.evergreen(trees, (x, y, -9.0), h, 2.6 + 1.5 * r.random())
    trees.obj("forest")
    gb.box("forest_floor", (0, 3, -9.05), (120, 120, 0.1), K.fog_mat("forest_floor", "#2a2a22", fogc, dist=22.0))
    if not night:
        drizzle("drizzle_deck", (W / 2 + 0.3, -3.0, -1.0), (W / 2 + 9.0, 7.5, 3.6), 1800, "deck_drizzle", alpha=0.3)


# ---------------------------------------------------------------- 4. the hilltop park (O19 end - O22)

PARK = {"band": (0.0, 5.8), "lamp": (2.7, -2.6), "crowd": (0.0, 2.0)}


def hill_z(x, y):
    r2 = x * x + y * y
    return -32.0 * (1.0 - math.exp(-r2 / 3600.0))


def park(st):
    """A hilltop park in drizzle: the crowd on the crest, the band facing them (backs to the far view), evergreens
    round the sides, a generic city skyline 450 m off in fog (boxes only, no landmark tower, nothing between it and
    the hill but fog: no water). A lamp post with a weatherproof outlet box; Little Switch on the box (O20). One
    umbrella in the crowd. Y runs from the camera side (-) toward the skyline (+)."""
    R = ROOMS["park"]
    fogd = R["fog_dist"]
    fogc = K.PAL["fog"]
    # ground: a polar grid round the crest
    import bmesh
    bm = bmesh.new()
    rings = [0.0] + [1.0 * (1.12 ** k) for k in range(60)]
    seg = 72
    verts = []
    for i, rr in enumerate(rings):
        row = []
        for j in range(seg if rr > 0 else 1):
            a = 2 * math.pi * j / seg
            x, y = rr * math.cos(a), rr * math.sin(a)
            row.append(bm.verts.new((x, y, hill_z(x, y))))
        verts.append(row)
    for j in range(seg):
        bm.faces.new((verts[0][0], verts[1][j], verts[1][(j + 1) % seg]))
    for i in range(1, len(verts) - 1):
        for j in range(seg):
            bm.faces.new((verts[i][j], verts[i + 1][j], verts[i + 1][(j + 1) % seg], verts[i][(j + 1) % seg]))
    me = bpy.data.meshes.new("ground")
    bm.to_mesh(me)
    bm.free()
    me.materials.append(K.fog_mat("grass", K.PAL["grass"], fogc, dist=fogd))
    gb.mesh_obj("ground", me)
    # a gravel path across the crest
    gb.box("path", (0.8, 0.5, 0.01), (2.0, 16.0, 0.02), K.fog_mat("path", K.PAL["path"], fogc, dist=fogd)).rotation_euler.z = 0.25
    # skyline: generic towers, deep in fog
    sky = PR.B([K.fog_mat("skyline", "#5a6066", fogc, dist=520.0)])
    sky.roles = ["sky"]
    r = gb.rng("skyline")
    for k in range(46):
        x = -260 + 520 * (k + r.random()) / 46
        y = 430 + 60 * r.random()
        h = 25 + 95 * r.random() ** 1.6
        w = 14 + 22 * r.random()
        sky.bx((x, y, -32 + h / 2), (w, 14 + 16 * r.random(), h), "sky")
    sky.obj("skyline")
    # evergreens on the slopes, both sides of the view; a few nearer ones framing
    ev = K.fog_mat("evergreen_p", K.PAL["evergreen"], fogc, dist=fogd)
    tr = K.fog_mat("trunk_p", K.PAL["trunk"], fogc, dist=fogd)
    trees = PR.B([ev, tr])
    trees.roles = ["evergreen", "trunk"]
    r = gb.rng("park_trees")
    for k in range(140):
        a = r.random() * 2 * math.pi
        d = 13 + 110 * r.random() ** 1.5
        x, y = d * math.cos(a), d * math.sin(a)
        if y > 8 and abs(x) < 0.55 * y:                  # keep the view to the skyline open
            continue
        if y < -6 and abs(x) < 6:                        # and the camera side clear
            continue
        h = 14 + 16 * r.random()
        PR.evergreen(trees, (x, y, hill_z(x, y) - 0.3), h, 2.4 + 1.6 * r.random())
    trees.obj("park_trees")
    # lamp post with the outlet box and Switch
    lx, ly = PARK["lamp"]
    post, sw = PR.lamp_post("lamp_post", (lx, ly, hill_z(lx, ly)), "switch_on" if st.get("switch", "on") == "on" else "switch_off")
    OBJ["switch"] = sw
    # people
    mode = st.get("crowd", "sing")
    if mode == "sing":
        band(PARK["band"] + (0,), 0.0, spread=1.0)
        fixed = [("umbrella_holder", "fist", (1.9, 1.3), 25)]          # a closed hand round the umbrella's shaft
        crowd("crowd", 24, PARK["crowd"], (9.0, 3.6), (0.0, 7.5), {"stand": 3, "clap": 3, "fist": 2},
              "park_crowd", fixed)
        PR.umbrella("umbrella", OBJ["umbrella_holder"], hand=poses.hand(OBJ["umbrella_holder"].instance_collection,
                                                                         "Right"))
    if st.get("walker"):
        OBJ["walker"] = K.person("walker", "walk", (1.6, 4.5, hill_z(1.6, 4.5)), -0.08, who=10)
    # drizzle round the crowd and camera
    drizzle("drizzle", (-12, -10, 0), (12, 14, 7), 4500, "park_drizzle", alpha=0.32, emit=0.5)
    # light: an overcast sky behind the band (backlight), soft
    K.world(K.PAL["sky_top"], R["sky"], light=R["sky_light"])
    # the sun from behind the band, high and soft (overcast): the crowd's backs and the band's faces fall into shade
    K.sun("overcast", (math.radians(-55), 0, math.radians(180)), R["sun"], "#eef0f2", angle=40)
    poses.finish()
    bpy.context.view_layer.update()


# ---------------------------------------------------------------- O07: the void

def void(st):
    """A lone server rack lying on its side on an empty chroma-key green plane (studio void): a floor and a curved
    cyclorama in flat green, two soft studio lights. [background failed to load] is a Remotion caption."""
    R = ROOMS["void"]
    g = K.mat("chroma", 0.9, emit=R["chroma_emit"])
    gb.box("chroma_floor", (0, 0, -0.05), (160, 160, 0.1), g)
    import bmesh
    bm = bmesh.new()
    rr, cy, n = 4.0, 6.0, 16
    prev = None
    for k in range(n + 1):
        a = (math.pi / 2) * k / n
        y, z = cy + rr * math.sin(a), rr - rr * math.cos(a)
        row = (bm.verts.new((-80, y, z)), bm.verts.new((80, y, z)))
        if prev:
            bm.faces.new((prev[0], prev[1], row[1], row[0]))
        prev = row
    top = (bm.verts.new((-80, cy + rr, 40)), bm.verts.new((80, cy + rr, 40)))
    bm.faces.new((prev[0], prev[1], top[1], top[0]))
    me = bpy.data.meshes.new("cyc")
    bm.to_mesh(me)
    bm.free()
    me.materials.append(g)
    gb.mesh_obj("cyclorama", me)
    OBJ["rack"] = PR.server_rack("rack", (-0.9, 0.4, 0.31), (0, math.radians(90), math.radians(18)))
    K.area("key", (2.5, -3.0, 4.5), (0, 0.5, 0.3), 1800, 3.0, "#f4f1ea")
    K.area("top", (0, 1.0, 6.0), (0, 1.0, 0), 900, 5.0, "#f4f4f4")
    K.world(K.PAL["chroma"], 0.25)          # beyond the cyclorama's edges the void stays green
    bpy.context.view_layer.update()


BUILDERS = {"live": live_room, "cafe": cafe, "treehouse": treehouse, "park": park, "void": void}


def build(room, st=None):
    st = dict(st or {})
    K.reset()
    poses._HOLD = None
    poses._MUGS.clear()
    STATE.clear(); STATE.update(st)
    OBJ.clear()
    if room != "void":
        K.load_people()
    BUILDERS[room](st)
    for h in POST_BUILD:
        h(room, st)
    return OBJ
