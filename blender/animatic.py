"""M5: render every Blender shot of the animatic as a JPEG sequence at 960x540, 30 fps, Eevee, timed by
timing/shot_times.json (the M2 cues, approved, human interventions 9).

Adapted from Ever Present's blender/shots.py (9301de4): each shot = the M3 board's room, state and camera
(blender/board.py FRAMES, approved at the M3 gate, human interventions 8) + a camera move over the shot + the shot's
cued events, keyed on the cue frames:
- crowd claps on beats 2 and 4 of the beat grid (timing/timing_map.json; poses.key_claps), O03 from the drums' entry;
- O10: Switch flips ON and the ON AIR sign lights on the cue (texture swap, the sign's glow keyed);
- O12: the freeze: everyone frozen (poses.still) but the late clapper (94.39, 95.59 s; the third clap is the cut) and
  Switch, who sags and drops at the stop as ON AIR goes dark;
- O15: the green probe's LED dims on "song" and comes back on "(It wrote it anyway)";
- O16: one bulb goes out and the dark runs down every strand (sets.key_cascade) between the two cues;
- O17: mugs raised on chorus 2's four Hey!s (poses.key_mugs; decisions 9);
- O18: the whiteboard is the Remotion whiteboard as a movie texture (renders/m5/remotion/M5-O18-Whiteboard.mp4);
- O19: two parts, cross-faded in the edit (decisions 11): the treehouse door opens and the camera goes out onto the
  deck and up (O19a), then rises over the hilltop park's crest to the crowd (O19b);
- O21: the park frozen, Switch holding one beat (to 202.42 s), then dropping;
- O22: the park empty, one silhouette walking off down the path.
Usage: blender -b --factory-startup --python blender/animatic.py -- [--out renders/m5/frames_blender] [--only O10,O12]
       [--samples 8] [--frames 1,40] (test frames only) [--size 960x540]
"""
import argparse
import json
import math
import sys
import time
from pathlib import Path

import bpy
from mathutils import Vector

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import aso_kit as K  # noqa: E402
import board as BD  # noqa: E402
import gb  # noqa: E402
import poses  # noqa: E402
import sets as S  # noqa: E402

ROOT = gb.ROOT
FPS = 30
TS = json.loads((ROOT / "timing" / "shot_times.json").read_text())
SHOTS = TS["shots"]
TM = json.loads((ROOT / "timing" / "timing_map.json").read_text())
BEATS = list(zip(TM["beats"]["beats"], TM["beats"]["beat_in_bar"]))
BOARD = {f[0]: f for f in BD.FRAMES}         # id: (id, label, room, state, (loc, target, lens), exposure)
O19A = 175                                    # O19's split (frames): treehouse part, then the park part,
XF = 10                                       # overlapping by XF frames for the cross-fade (scripts/animatic.py)


def nframes(sid):
    if sid == "O19a":
        return O19A
    if sid == "O19b":
        return SHOTS["O19"]["end_frame"] - SHOTS["O19"]["start_frame"] - O19A + XF
    if sid == "O08c":
        return 72                              # 4 beats from the second echo (decisions 11)
    s = SHOTS[sid]
    return s["end_frame"] - s["start_frame"]


def f_of(sid, t):
    """Song time -> 1-based frame in the shot."""
    base = SHOTS[sid[:3]]["song_start"] + (O19A - XF) / FPS * (sid == "O19b")
    return int(round((t - base) * FPS)) + 1


def mark(sid, i):
    return SHOTS[sid]["marks"][i]["frame_in_shot"] + 1


def clap_frames(sid, n, after=None):
    """Frames of beats 2 and 4 inside the shot (claps), optionally only after song time `after`."""
    out = []
    for t, b in BEATS:
        if b in (2, 4) and (after is None or t >= after):
            f = f_of(sid, t)
            if 3 <= f <= n - 3:
                out.append(f)
    return out


# ---------------------------------------------------------------- keying helpers

def key_cam(cam, keys, n):
    """keys: [(fraction of the shot, loc, target, lens)], Bezier eased between."""
    prev = None
    for fr, loc, tgt, lens in keys:
        f = 1 + round(fr * (n - 1))
        cam.location = loc
        rot = gb.look_rot(loc, tgt)
        if prev is not None:
            rot.make_compatible(prev)
        prev = rot.copy()
        cam.rotation_euler = rot
        cam.data.lens = lens
        cam.keyframe_insert("location", frame=f)
        cam.keyframe_insert("rotation_euler", frame=f)
        cam.data.keyframe_insert("lens", frame=f)


def push(loc, tgt, k):
    """A point k of the way from loc toward tgt."""
    a, b = Vector(loc), Vector(tgt)
    return tuple(a + (b - a) * k)


def key_vis(o, frames_on):
    """Show o only on [(from, to)] ranges (hide_render keyed, constant)."""
    o.hide_render = True
    o.keyframe_insert("hide_render", frame=1)
    for a, b in frames_on:
        o.hide_render = False
        o.keyframe_insert("hide_render", frame=a)
        o.hide_render = True
        o.keyframe_insert("hide_render", frame=b)
    constant(o)


def constant(o):
    ad = o.animation_data
    if ad and ad.action:
        for fc in _fcurves(ad.action):
            for kp in fc.keyframe_points:
                kp.interpolation = "CONSTANT"


def _fcurves(action):
    if hasattr(action, "fcurves") and len(getattr(action, "fcurves", [])):
        return list(action.fcurves)
    out = []                                   # Blender 5 layered actions
    for layer in getattr(action, "layers", []):
        for strip in layer.strips:
            for cb in strip.channelbags:
                out += list(cb.fcurves)
    return out


def twin(o, tex, mode, strength):
    """A copy of a texture plane showing another texture (Switch on/off, ON AIR lit/unlit)."""
    t = o.copy()
    t.data = o.data.copy()
    t.data.materials.clear()
    t.data.materials.append(K.image_mat(f"tex_{o.name}_{tex}", tex, mode, strength))
    for c in o.users_collection:
        c.objects.link(t)
    return t


def switch_drop(sw_on, sw_off, sag_from, drop_at, n):
    """Switch sags (sinks and leans) from sag_from, then the paddle drops to OFF at drop_at (the Remotion rig's
    'sagging' motion, as keys on the planes)."""
    for o in (sw_on, sw_off):
        z0, r0 = o.location.z, o.rotation_euler.copy()
        axis = 0 if abs(o.rotation_euler.x) < 1e-3 and abs(o.rotation_euler.y) > 1e-3 else 1
        o.keyframe_insert("location", frame=1)
        o.keyframe_insert("location", frame=sag_from)
        o.keyframe_insert("rotation_euler", frame=sag_from)
        h = o.dimensions.z or o.dimensions.y
        o.location.z = z0 - 0.08 * h
        o.rotation_euler[1] = r0[1] + math.radians(5)
        o.keyframe_insert("location", frame=drop_at)
        o.keyframe_insert("rotation_euler", frame=drop_at)
        o.location.z = z0 - 0.14 * h
        o.rotation_euler[1] = r0[1] + math.radians(9)
        o.keyframe_insert("location", frame=drop_at + 6)
        o.keyframe_insert("rotation_euler", frame=drop_at + 6)
    key_vis(sw_on, [(1, drop_at)])
    key_vis(sw_off, [(drop_at, n + 1)])


def onair_pair(st_lit_from, n, lit_until=None):
    """ON AIR lit on [st_lit_from, lit_until), unlit otherwise; the glow light keyed with it."""
    lit = S.OBJ["onair"]
    unlit = twin(lit, "onair_unlit", "lit", 0.15)
    rng = [(st_lit_from, (lit_until or n + 1))]
    key_vis(lit, rng)
    key_vis(unlit, [(1, st_lit_from), ((lit_until or n + 1), n + 1)] if st_lit_from > 1 else [((lit_until or n + 1), n + 1)])
    g = bpy.data.objects.get("onair_glow")
    if g:
        e = g.data.energy
        for f, v in ((1, 0.0 if st_lit_from > 1 else e), (st_lit_from, e), ((lit_until or n + 1), 0.0)):
            g.data.energy = v
            g.data.keyframe_insert("energy", frame=f)
        for fc in _fcurves(g.data.animation_data.action):
            for kp in fc.keyframe_points:
                kp.interpolation = "CONSTANT"


def variants(pose):
    return [c for c in bpy.data.collections if c.name.startswith("pv_") and c.get("pose") == pose]


def all_claps(sid, n, after=None):
    fr = clap_frames(sid, n, after)
    for c in variants("clap"):
        poses.key_claps(c, fr)
    return len(fr)


def freeze_people():
    """Patch K.person so every library person in this build is a frozen copy (the hard stops)."""
    orig = K.person

    def frozen(name, pose, loc, rot_z=0.0, u=0.0, who=None, coll=None):
        if coll is None:
            coll = poses.still(K.pick(pose, u, who))
        return orig(name, pose, loc, rot_z, u, who, coll)
    K.person = frozen
    return orig


# ---------------------------------------------------------------- shots

def cam_from_board(sid):
    _, _, room, st, (loc, tgt, lens), expo = BOARD[sid]
    if loc == "over_shoulder":
        loc, tgt = BD.over_shoulder(S.OBJ[tgt])
    return loc, tgt, lens


def shot(sid, n):
    """Build the shot's room and keys; returns (camera keys, exposure, bloom, notes)."""
    notes = []
    # O12 uses the board's close camera O12c (same state): from O12's wide the late clapper was too small to read
    base = {"O19a": "O19", "O19b": "O20", "O21": "O20", "O08c": "O08c", "O12": "O12c"}.get(sid, sid)
    _, _, room, st, _, expo = BOARD[base]
    st = dict(st)
    orig = None
    if sid == "O12":
        orig = freeze_people()
        st.update(clapper_at=(-0.26, 4.5), clapper_face=(3.44, 6.06))   # side-on to O12c's camera, the chest-height clap against a window
    if sid == "O21":
        orig = freeze_people()
        st["switch"] = "on"
    if sid == "O10":
        st.update(onair="lit", switch="on")
    if sid == "O19a":
        st["door_open"] = 0.01          # > 0 so the set adds the doorway light; the hinge is keyed below
    if sid == "O22":
        st = dict(crowd="empty", walker=True)
    try:
        S.build(room, st)
    finally:
        if orig:
            K.person = orig
    loc, tgt, lens = cam_from_board(base)
    keys = [(0, loc, tgt, lens), (1, push(loc, tgt, 0.06), tgt, lens)]

    if sid == "O03":
        keys = [(0, loc, tgt, lens), (1, (1.5, 2.0, 1.9), tgt, lens)]
        notes.append(f"claps on 2 and 4 from the drums' entry ({all_claps(sid, n, TM['events']['drums_in'])})")
    elif sid == "O04":
        # aim between the phone and the band, and ease toward the phone (the phone must stay whole in frame for its
        # screen to be pinned: scripts/animatic.py)
        e = S.OBJ["phone_holder"]
        ph = K.local_to_world(e, e.instance_collection["phone"])
        t0 = tuple(Vector(tgt).lerp(ph, 0.45))
        keys = [(0, loc, t0, lens), (1, push(loc, tuple(ph), 0.12), tuple(Vector(tgt).lerp(ph, 0.55)), lens)]
    elif sid == "O07":
        keys = [(0, loc, tgt, lens), (1, (2.5, -4.0, 1.6), tgt, lens * 1.08)]
    elif sid == "O08":
        keys = [(0, loc, tgt, lens), (1, (5.75, 1.45, 1.5), tgt, lens)]
    elif sid == "O08c":
        keys = [(0, loc, tgt, lens), (1, (0.05, 0.6, 1.95), tgt, lens)]
    elif sid == "O09":
        keys = [(0, loc, tgt, lens), (1, (0.0, 3.3, 2.6), tgt, lens)]
        notes.append(f"claps ({all_claps(sid, n)})")
    elif sid == "O10":
        at = mark("O10", 0)
        sw_on = S.OBJ["switch"]
        sw_off = twin(sw_on, "switch_off", "flat", 1.0)
        key_vis(sw_off, [(1, at)])
        key_vis(sw_on, [(at, n + 1)])
        onair_pair(at, n)
        keys = [(0, loc, tgt, lens), (1, push(loc, tgt, 0.1), tgt, lens)]
        notes.append(f"Switch ON and ON AIR lit at frame {at}")
    elif sid == "O11":
        keys = [(0, loc, tgt, lens), (1, (0.45, 3.9, 1.55), tgt, lens)]
        notes.append(f"claps ({all_claps(sid, n)})")
    elif sid == "O12":
        sw_on = S.OBJ["switch"]
        sw_on.data.materials.clear()
        sw_on.data.materials.append(K.image_mat("tex_switch_on12", "switch_on", "flat", 1.0))
        sw_off = twin(sw_on, "switch_off", "flat", 1.0)
        switch_drop(sw_on, sw_off, 1, 4, n)
        # the board's O12 state is unlit; light it for the first frames so the sign goes dark on the stop
        lit = twin(S.OBJ["onair"], "onair_lit", "glow", 2.2)
        key_vis(lit, [(1, 4)])
        S.OBJ["onair"].hide_render = False
        key_vis(S.OBJ["onair"], [(4, n + 1)])
        clapper = S.OBJ["late_clapper"].instance_collection
        cf = [mark("O12", 1), mark("O12", 2)]
        poses.key_claps(clapper, cf, open_frames=7, wide=True)
        keys = [(0, loc, tgt, lens), (1, loc, tgt, lens)]
        notes.append(f"frozen; late clapper closes on frames {cf}; Switch drops and ON AIR dark at frame 4")
    elif sid == "O14":
        keys = [(0, loc, tgt, lens), (1, (3.98, 3.14, 1.02), tgt, lens)]
    elif sid == "O15":
        g = S.OBJ["probes"][0]
        d0, d1 = mark("O15", 0), mark("O15", 1)
        for f, v in ((1, 1.0), (d0, 1.0), (d0 + 8, 0.04), (d1, 0.04), (d1 + 5, 1.0)):
            g["led"] = v
            g.keyframe_insert('["led"]', frame=f)
        keys = [(0, loc, tgt, lens), (1, push(loc, tgt, 0.08), tgt, lens)]
        notes.append(f"LED dims frames {d0}-{d0 + 8}, back at {d1}-{d1 + 5}")
    elif sid == "O16":
        a, b = mark("O16", 0), mark("O16", 1)
        S.key_cascade(a, b - a)
        hub = bpy.data.objects.get("hub_light")
        for o in bpy.data.objects:
            if o.name.startswith("strand_light") or o.name == "hub_light":
                s_ = o.name[len("strand_light"):] if o.name != "hub_light" else None
                mine = [x for x in S.OBJ["bulbs"] if s_ is not None and x.name.startswith(f"bulb_{s_}_")]
                f0 = a + int(min((x["dist"] for x in mine), default=0) * (b - a))
                f1 = a + int(max((x["dist"] for x in mine), default=0) * (b - a))
                e = o.data.energy
                o.data.energy = e
                o.data.keyframe_insert("energy", frame=max(1, f0 - 1))
                o.data.energy = 0.0
                o.data.keyframe_insert("energy", frame=max(f0, f1))
        keys = [(0, loc, tgt, lens), (1, loc, (0.6, 5.5, 2.7), lens)]
        notes.append(f"bulb cascade frames {a}-{b}")
    elif sid == "O17":
        heys = [mark("O17", i) for i in range(4)]
        for c in variants("mug_raise"):
            poses.key_mugs(c, heys)
        keys = [(0, loc, tgt, lens), (1, (0.35, 2.1, 1.85), tgt, lens)]
        notes.append(f"mugs up on {heys}; claps ({all_claps(sid, n)})")
    elif sid == "O18":
        wb = S.OBJ["whiteboard"]
        node = next(nd for nd in wb.active_material.node_tree.nodes if nd.type == "TEX_IMAGE")
        mov = bpy.data.images.load(str(ROOT / "renders/m5/remotion/M5-O18-Whiteboard.mp4"))
        mov.source = "MOVIE"
        node.image = mov
        node.image_user.frame_duration = n
        node.image_user.frame_start = 1
        node.image_user.frame_offset = 0
        node.image_user.use_auto_refresh = True
        keys = [(0, loc, tgt, lens), (1, (0.2, 1.25, 1.72), tgt, lens)]
        notes.append("whiteboard: Remotion movie texture")
    elif sid == "O19a":
        hinge = bpy.data.objects["door_hinge"]
        hinge.rotation_euler.z = 0.0
        hinge.keyframe_insert("rotation_euler", frame=1)
        hinge.rotation_euler.z = math.radians(100)
        hinge.keyframe_insert("rotation_euler", frame=40)
        keys = [(0, loc, tgt, lens), (0.25, loc, tgt, lens), (0.65, (3.95, 1.64, 1.75), (9.0, 1.8, 1.6), lens),
                (1, (5.6, 1.7, 3.4), (12.0, 2.2, 5.5), lens)]
        notes.append("door opens frames 1-40; camera out onto the deck and up")
    elif sid == "O19b":
        from sets import hill_z
        z0 = hill_z(0, -16) + 1.0
        keys = [(0, (0.0, -16.0, z0), (0.3, 6.0, 0.5), 28), (1, (0.4, -8.5, 4.2), (0.3, 6.0, 1.4), 28)]
        notes.append(f"camera rises over the crest; claps ({all_claps('O19b', n, SHOTS['O19']['song_start'] + (O19A - XF) / FPS)})")
    elif sid == "O20":
        keys = [(0, loc, tgt, lens), (1, (1.0, -6.1, 1.62), tgt, lens)]      # a short push: the lamp post (Switch) stays in frame
        notes.append(f"claps ({all_claps(sid, n)})")
    elif sid == "O21":
        sw_on = S.OBJ["switch"]
        sw_off = twin(sw_on, "switch_off", "flat", 1.0)
        drop = mark("O21", 1)
        switch_drop(sw_on, sw_off, 1, drop, n)
        end = (1.0, -6.1, 1.62)                       # O20's last camera
        keys = [(0, end, tgt, lens), (1, end, tgt, lens)]
        notes.append(f"frozen; Switch holds to frame {drop}, then drops")
    elif sid == "O22":
        w = S.OBJ["walker"]
        from sets import hill_z
        # along the gravel path (a flat plank at z 0.01-0.02 over the crest, sets.park), then over its far end and
        # down the slope out of sight; on the plank the walker stays on it (the hill drops ~0.5 m below its end)
        p0, p1 = Vector((1.0, -3.0)), Vector((3.2, 12.0))
        w.rotation_euler.z = K.facing(tuple(p0), tuple(p1)) + math.pi
        for k in range(0, 31):
            f = 1 + round(k / 30 * (n - 1))
            p = p0.lerp(p1, k / 30)
            w.location = (p.x, p.y, 0.02 if p.y < 8.3 else hill_z(p.x, p.y))
            w.keyframe_insert("location", frame=f)
        for fc in _fcurves(w.animation_data.action):
            for kp in fc.keyframe_points:
                kp.interpolation = "LINEAR"
        keys = [(0, loc, tgt, lens), (1, (0.0, -7.6, 1.75), tgt, lens)]
        notes.append("walker 15.2 m up the path and over the crest")
    return keys, expo, notes


def o07t(size, samples):
    """The O07 alternate's server: the void's rack alone on a transparent film, from eye level a few metres off, to be
    laid on the fog-tower plate's lawn (scripts/animatic.py). One still."""
    S.build("void", {})
    for nm in ("chroma_floor", "cyclorama"):
        bpy.data.objects[nm].hide_render = True
    K.world("#c9ccce", 0.6)
    K.render_settings((1280, 720), max(samples, 32), 0.0)
    sc = bpy.context.scene
    sc.render.film_transparent = True
    gb.into(None)
    cam = gb.camera("cam_O07t", (0.6, -5.2, 0.75), (-0.2, 0.4, 0.3), 50)
    sc.camera = cam
    sc.render.image_settings.file_format = "PNG"
    sc.render.image_settings.color_mode = "RGBA"
    sc.render.filepath = str(ROOT / "renders/m5/O07t.png")
    bpy.ops.render.render(write_still=True)
    print("M5 O07t: server cut-out", flush=True)


def main():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="renders/m5/frames_blender")
    ap.add_argument("--only", default="")
    ap.add_argument("--size", default="960x540")
    ap.add_argument("--samples", type=int, default=8)
    ap.add_argument("--frames", default="", help="test: render only these frames (1-based) as PNG")
    a = ap.parse_args(argv)
    size = tuple(int(v) for v in a.size.split("x"))
    order = ["O03", "O04", "O07", "O08", "O08c", "O09", "O10", "O11", "O12", "O14", "O15", "O16", "O17", "O18",
             "O19a", "O19b", "O20", "O21", "O22"]
    only = [s for s in filter(None, a.only.split(","))]
    for sid in (only or order):
        t0 = time.time()
        if sid == "O07t":
            o07t(size, a.samples)
            continue
        n = nframes(sid)
        keys, expo, notes = shot(sid, n)
        K.render_settings(size, a.samples, expo)
        sc = bpy.context.scene
        sc.render.fps = FPS
        sc.frame_start, sc.frame_end = 1, n
        gb.into(None)
        cam = gb.camera(f"cam_{sid}", keys[0][1], keys[0][2], keys[0][3])
        cam.data.clip_end = 3000.0
        key_cam(cam, keys, n)
        if sid in ("O10", "O14", "O15", "O16", "O17"):
            K.bloom()
        sc.camera = cam
        if hasattr(S, "sr") or True:
            try:
                import sr_kit as SR
                SR.refresh()
            except Exception:
                pass
        out = ROOT / a.out / sid
        out.mkdir(parents=True, exist_ok=True)
        tb = time.time()
        if a.frames:
            sc.render.image_settings.file_format = "PNG"
            for f in [int(x) for x in a.frames.split(",")]:
                sc.frame_set(min(f, n))
                sc.render.filepath = str(out / f"test_{f:04d}.png")
                bpy.ops.render.render(write_still=True)
        else:
            sc.render.image_settings.file_format = "JPEG"
            sc.render.image_settings.quality = 92
            sc.render.filepath = str(out) + "/"
            bpy.ops.render.render(animation=True)
        print(f"M5 {sid}: {n} frames, build {tb - t0:.1f} s, render {time.time() - tb:.1f} s; " + "; ".join(notes), flush=True)


if __name__ == "__main__":
    main()
