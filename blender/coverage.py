"""M5b: render the coverage plan (config/coverage.json): every Blender sub-shot as a JPEG sequence at 960x540, 30 fps,
Eevee, with camera, light, ambient and crowd motion cued to the music map (timing/music_map.json). Plan M5b,
decisions 12; the figure-library rebuild with real instrument performance is M5c, not here.

Each O-shot's room, state and cued events are built exactly as M5 did (blender/animatic.py shot(): claps, Switch, ON
AIR, the LED, the cascade, the mugs, the whiteboard movie, the door, the freezes, the walker). On top of that, per
build (skipped in the freezes O12 and O21, where the stream has stopped):
- Camera (one per sub-shot, keyed every frame): the preset's base and move (push, truck, M5's own keys, tracking the
  walker), eased; handheld drift (three sines per channel, seeded per sub-shot: gb.rng("m5b_cam_<id>"), main seed
  41); a small drop and nod on every main kick, scaled by the bar's drums energy; Eevee depth of field on the closes
  and mids, racking from a foreground head to the band one beat in where the preset says so.
- Light: practicals pulse with the main kicks; the window (or sky) light lifts on every Hey!; haze in the rooms (a
  low-density volume with a spot through each window: Eevee volumetrics); ON AIR flickers through the last beats
  before stop 1, the park lamp and Switch before stop 2; light breaks through on "Service has been restored" (O19);
  the cafe's string lights chase the lead vocal's syllables outward from the hub until O16's cascade kills them.
- Ambient: rain streaks run down the glass (the window shader's streak texture, keyed), the drizzle falls (looped),
  fog cards drift over the park's skyline, steam rises off the probes' mugs, the umbrella turns.
- People (first pass; M5c rebuilds the performances): every crowd member sways and bounces on half notes (seeded per
  person: gb.rng("m5b_crowd_<shot>")), surges toward the band through the choruses and settles in the verses, and
  hops on the Hey!s; each clapper gets their own copy of M5's clap keys, shifted by their own lag; the band bobs on
  the beat, the singers lean in to their mics on the Hey!s, the kick player's right leg lifts and strikes on the main
  kicks, the tambourine shakes on the percussion hits. Pose rules unchanged (blender/poses.py).
Usage: blender -b --factory-startup --python blender/coverage.py -- [--out renders/m5b/frames] [--only O09,O11]
       [--subs O09b,O11g] [--still] (one frame per sub-shot, its middle, PNG) [--samples 8] [--size 960x540]
"""
import argparse
import json
import math
import os
import sys
import time
from pathlib import Path

import bpy
import numpy as np
from mathutils import Euler, Matrix, Vector

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import animatic as A  # noqa: E402  (M5's builds and event keys)
import aso_kit as K  # noqa: E402
import gb  # noqa: E402
import poses  # noqa: E402
import sets as S  # noqa: E402

ROOT = gb.ROOT
FPS = 30
COV = json.loads((ROOT / "config" / "coverage.json").read_text())
# M1b: ASO_MUSIC_MAP picks another map in timing/ (coverage_m7.py: the v1.3 one); unset, M5c3's
MM = json.loads((ROOT / "timing" / os.environ.get("ASO_MUSIC_MAP", "music_map.json")).read_text())
TS = A.TS
SHOTS = A.SHOTS
BEATS = np.array(A.TM["beats"]["beats"])
BIB = np.array(A.TM["beats"]["beat_in_bar"])
KICKS = [h for h in MM["hits"]["kick"] if h["main"]]
TAMB = [h for h in MM["hits"]["tambourine"] if h["strength"] > 0.35]
LEAD_ON = MM["hits"]["lead_onsets"]
HEYS = [h["t"] for h in MM["heys"]]
BACKBEAT = [h["t"] for h in MM["hits"]["backbeat"]]
BARS = MM["bars"]
DRUMS_E = MM["energy"]["drums"]["norm"]
MIX_E = MM["energy"]["mix"]["norm"]
FREEZE = {"O12", "O21"}
# M7 (blender/coverage_m7.py, blender/look.py): f(build, room) run after the render settings, and f(sub, room, build
# exposure, camera preset) -> the view exposure. None keeps M5b-M5c3's.
SETTINGS = None
EXPOSURE = None
# M7b: f(camera, sub, build, f0, f1) run after each sub-shot's camera is keyed (M7's camera fixes: O04a follows the
# phone, O18e racks from the ringing phone; billboards face the camera). None keeps M5b-M5c3's cameras.
CAMERA_HOOK = None
NOHAZE = "--nohaze" in sys.argv
CHORUS = {"Stomp-clap": 0.7, "Chorus 1": 1.0, "Post-Chorus 1": 0.8, "Build 1": 1.0, "Chorus 2": 1.0,
          "Post-Chorus 2": 0.8, "Build 2": 0.6, "Final Chorus": 1.0}


# ---------------------------------------------------------------- time helpers

def build_base(b):
    """Song time of local frame 1 of a build."""
    return SHOTS[b[:3]]["song_start"] + (A.O19A - A.XF) / FPS * (b == "O19b")


def build_vstart(b):
    """Video frame of local frame 1."""
    if b == "O08c":
        return SHOTS["O08"]["start_frame"] + 115            # the cutaway's place in O08 (scripts/animatic.py O08_TREE)
    return SHOTS[b[:3]]["start_frame"] + (A.O19A - A.XF) * (b == "O19b")


def song_t(b, f):
    """Local frame (1-based) -> song time. O08c (the cutaway) runs on O08's clock from frame 115."""
    if b == "O08c":
        return SHOTS["O08"]["song_start"] + (115 + f - 1) / FPS
    return build_base(b) + (f - 1) / FPS


def beat_pos(t):
    """Fractional beat index on the grid."""
    i = int(np.clip(np.searchsorted(BEATS, t) - 1, 0, len(BEATS) - 2))
    return i + (t - BEATS[i]) / (BEATS[i + 1] - BEATS[i])


def bar_index(t):
    for k, b in enumerate(BARS):
        if b["start"] <= t < b["end"]:
            return k
    return len(BARS) - 1


def section(t):
    return BARS[bar_index(t)]["section"]


def chorus_amt(t):
    """0..1, eased over a bar at each section change: how much of a chorus we're in."""
    def raw(x):
        return CHORUS.get(section(x), 0.0)
    return float(np.mean([raw(t - d) for d in np.linspace(0, 2.4, 9)]))


def env_hits(t, times, tau=0.12, attack=0.033, weights=None):
    v = 0.0
    for k, h in enumerate(times):
        d = t - h
        if -attack <= d < 6 * tau:
            w = 1.0 if weights is None else weights[k]
            v += w * (min(1.0, (d + attack) / attack) if d < 0 else math.exp(-d / tau))
    return v


# ---------------------------------------------------------------- f-curve helpers (Blender 5 layered actions)

def _action(idb):
    ad = idb.animation_data or idb.animation_data_create()
    if ad.action is None:
        ad.action = bpy.data.actions.new(f"m5b_{idb.name}")
    return ad.action


def _find(idb, path, index):
    ad = idb.animation_data
    if not (ad and ad.action):
        return None
    for fc in A._fcurves(ad.action):
        if fc.data_path == path and fc.array_index == index:
            return fc
    return None


def _remove(idb, fc):
    act = idb.animation_data.action
    if hasattr(act, "fcurves") and len(getattr(act, "fcurves", [])) and fc in list(act.fcurves):
        act.fcurves.remove(fc)
        return
    for layer in act.layers:
        for strip in layer.strips:
            for cb in strip.channelbags:
                if fc in list(cb.fcurves):
                    cb.fcurves.remove(fc)
                    return


def base_series(idb, path, index, frames, default):
    fc = _find(idb, path, index)
    if fc is None:
        return np.full(len(frames), float(default))
    return np.array([fc.evaluate(f) for f in frames])


def key_series(idb, path, index, frames, values, interp="LINEAR"):
    """Replace one channel's keys with a value per frame."""
    fc = _find(idb, path, index)
    if fc is not None:
        _remove(idb, fc)
    act = _action(idb)
    fc = act.fcurve_ensure_for_datablock(idb, path, index=index)
    n = len(frames)
    fc.keyframe_points.add(n)
    co = np.empty(2 * n, np.float32)
    co[0::2] = frames
    co[1::2] = values
    fc.keyframe_points.foreach_set("co", co)
    fc.keyframe_points.foreach_set("interpolation", [bpy.types.Keyframe.bl_rna.properties["interpolation"].enum_items[interp].value] * n)
    fc.update()
    return fc


def key_prop(idb, path, frames, values, interp="LINEAR"):
    """For a custom property or a single float (index 0)."""
    return key_series(idb, path, 0, frames, values, interp)


def node_input(mat, node_type, name):
    for nd in mat.node_tree.nodes:
        if nd.type == node_type and name in nd.inputs:
            return nd, nd.inputs[name]
    return None, None


# ---------------------------------------------------------------- people

def instances(prefix=("crowd", "umbrella_holder")):
    return [o for o in bpy.data.objects if o.type == "EMPTY" and o.instance_type == "COLLECTION"
            and o.name.startswith(prefix)]


def own_clap_copy(e, lag, tag):
    """Give one clapper their own copy of the shared clap variant (rig + meshes), its keys shifted by `lag` frames."""
    src = e.instance_collection
    rig = next((o for o in src.objects if o.type == "ARMATURE"), None)
    if rig is None or not (rig.animation_data and rig.animation_data.action):
        return
    coll = bpy.data.collections.new(f"{src.name}_{tag}")
    poses._holding().children.link(coll)
    m = {o: o.copy() for o in src.objects}
    for o, c in m.items():
        coll.objects.link(c)
        if o.parent in m:
            c.parent = m[o.parent]
        for md in getattr(c, "modifiers", []):
            if md.type == "ARMATURE" and md.object in m:
                md.object = m[md.object]
    r2 = m[rig]
    act = rig.animation_data.action.copy()
    r2.animation_data.action = act
    for fc in A._fcurves(act):
        for kp in fc.keyframe_points:
            kp.co.x += lag
            kp.handle_left.x += lag
            kp.handle_right.x += lag
    coll["pose"] = src.get("pose", "clap")
    e.instance_collection = coll


def crowd_motion(b, n, room):
    """Sway and bounce on half notes, chorus surges, Hey! hops; per-person seeded lags and amounts."""
    r = gb.rng(f"m5b_crowd_{b}")
    frames = np.arange(1, n + 1)
    ts = np.array([song_t(b, f) for f in frames])
    bp = np.array([beat_pos(t) for t in ts])
    ch = np.array([chorus_amt(t) for t in ts])
    en = np.array([MIX_E[bar_index(t)] for t in ts])
    hey = np.array([env_hits(t, HEYS, tau=0.18) for t in ts])
    target = {"live": (0.0, 8.4), "cafe": (-0.4, 7.6), "park": (0.0, 6.0), "treehouse": (0.15, 4.75)}[room]
    people = instances()
    nclap = 0
    for k, e in enumerate(people):
        u = r.random(8)
        lag = (u[0] - 0.4) * 0.35                                # beats behind (+) or ahead of the grid
        amp_b = 0.018 + 0.03 * u[1]                              # bounce depth, m
        amp_s = math.radians(1.2 + 2.2 * u[2])                   # sway, side to side
        surge = 0.1 + 0.22 * u[3]                                # chorus surge toward the band, m
        hop = 0.02 + 0.05 * u[4]
        p0 = Vector(e.location)
        d = Vector((target[0] - p0.x, target[1] - p0.y, 0))
        d = d.normalized() if d.length > 0.3 else Vector((0, 0, 0))
        half = (bp - lag) / 2.0                                  # half notes
        drive = (0.45 + 0.55 * en) * (0.55 + 0.6 * ch)
        z = -amp_b * drive * (0.5 + 0.5 * np.cos(2 * np.pi * half)) + hop * hey * (0.4 + 0.6 * ch)
        sway = amp_s * drive * np.sin(np.pi * half + u[5] * 0.6)
        sv = surge * ch
        rz0 = e.rotation_euler.z
        for i, (vals) in enumerate((p0.x + d.x * sv, p0.y + d.y * sv, p0.z + z)):
            key_series(e, "location", i, frames, vals)
        key_series(e, "rotation_euler", 1, frames, sway)
        key_series(e, "rotation_euler", 0, frames, math.radians(1.5) * hey * u[6])
        if e.get("pose") == "clap" and e.instance_collection.name.startswith("pv_"):
            own_clap_copy(e, round((u[7] - 0.35) * 4.0), f"{b}_{k}")
            nclap += 1
    return f"crowd motion on {len(people)} people ({nclap} clappers with their own lag)"


def band_motion(b, n):
    band = S.OBJ.get("band")
    if not band:
        return "no band"
    frames = np.arange(1, n + 1)
    ts = np.array([song_t(b, f) for f in frames])
    bp = np.array([beat_pos(t) for t in ts])
    en = np.array([DRUMS_E[bar_index(t)] for t in ts])
    hey = np.array([env_hits(t, HEYS, tau=0.3, attack=0.13) for t in ts])
    half = b == "O18"                                            # the bridge is half-time
    for nm in list(bpy.data.objects.keys()):                     # mic stands stay put when a singer leans
        o = bpy.data.objects[nm]
        if nm.startswith("mic_") and o.parent is not None:
            mw = o.matrix_world.copy()
            o.parent = None
            o.matrix_world = mw
    r = gb.rng(f"m5b_band_{b}")
    for role, e in band.items():
        u = r.random(3)
        if role == "kick":                                       # the kit is parented to the player: the leg moves
            continue
        ph = (bp - 0.08 - 0.1 * u[0]) / (2.0 if half else 1.0)
        bob = (0.008 + 0.01 * u[1]) * (0.4 + 0.6 * en) * (0.5 + 0.5 * np.cos(2 * np.pi * ph))
        z0 = e.location.z
        key_series(e, "location", 2, frames, z0 - bob)
        lean = math.radians(7.0) * hey if role != "kick" else 0.0 * hey
        nod = math.radians(1.2) * (0.5 + 0.5 * np.cos(2 * np.pi * ph))
        key_series(e, "rotation_euler", 0, frames, e.rotation_euler.x + lean + nod)
    notes = ["band bob" + (" (half-time)" if half else "")]
    notes.append(kick_leg(b, n, band["kick"]))
    t = bpy.data.objects.get("tambourine")
    if t is not None:
        x0 = t.location.x
        sh = np.array([env_hits(tt, [h["t"] for h in TAMB], tau=0.05, attack=0.02) for tt in ts])
        key_series(t, "location", 0, frames, x0 + 0.012 * np.sin(np.arange(n) * 2.1) * np.clip(sh, 0, 1.2))
        notes.append("tambourine shakes")
    return ", ".join(notes)


def kick_leg(b, n, e):
    """A local copy of the kick player (library rig + its loop, copied) with the right leg keyed: the thigh lifts two
    frames before each main kick and strikes on it."""
    src = e.instance_collection
    coll = bpy.data.collections.new(f"kick_player_{b}")
    poses._holding().children.link(coll)
    m = {o: o.copy() for o in src.objects}
    for o, c in m.items():
        coll.objects.link(c)
        if o.parent in m:
            c.parent = m[o.parent]
        for md in getattr(c, "modifiers", []):
            if md.type == "ARMATURE" and md.object in m:
                md.object = m[md.object]
    rig = next(c for c in m.values() if c.type == "ARMATURE")
    if rig.animation_data and rig.animation_data.action:
        rig.animation_data.action = rig.animation_data.action.copy()
    e.instance_collection = coll
    P = poses.P
    kf = [round((h["t"] - song_t(b, 1)) * FPS) + 1 for h in KICKS]
    kf = [f for f in kf if 3 <= f <= n]
    for bone, up in (("RightUpLeg", 14.0), ("RightLeg", -6.0), ("RightFoot", -15.0)):
        pb = rig.pose.bones.get(P + bone)
        if pb is None:
            continue
        pb.rotation_mode = "QUATERNION"
        q0 = pb.rotation_quaternion.copy()
        q1 = q0 @ Euler((math.radians(up), 0, 0)).to_quaternion()
        pb.rotation_quaternion = q0
        pb.keyframe_insert("rotation_quaternion", frame=1)
        for f in kf:
            pb.rotation_quaternion = q0
            pb.keyframe_insert("rotation_quaternion", frame=f - 4)
            pb.rotation_quaternion = q1
            pb.keyframe_insert("rotation_quaternion", frame=f - 2)
            pb.rotation_quaternion = q0
            pb.keyframe_insert("rotation_quaternion", frame=f)
    return f"kick leg on {len(kf)} kicks"


# ---------------------------------------------------------------- light

def pulse_lights(b, n, room):
    frames = np.arange(1, n + 1)
    ts = np.array([song_t(b, f) for f in frames])
    kw = [h["strength"] * DRUMS_E[bar_index(h["t"])] for h in KICKS]
    kick = np.array([env_hits(t, [h["t"] for h in KICKS], tau=0.1, attack=0.02, weights=kw) for t in ts])
    hey = np.array([env_hits(t, HEYS, tau=0.22, attack=0.05) for t in ts])
    kick = np.clip(kick, 0, 1.2)
    hey = np.clip(hey, 0, 1.2)
    notes = []
    pract = [o for o in bpy.data.objects if o.type == "LIGHT" and (o.name.startswith(("bulb_light", "lamp_light"))
                                                                   or o.name.startswith(("strand_light", "hub_light")))]
    for o in pract:
        base = base_series(o.data, "energy", 0, frames, o.data.energy)
        key_series(o.data, "energy", 0, frames, base * (0.8 + 0.45 * kick))
    if pract:
        notes.append(f"{len(pract)} practicals pulse on the kick")
    for mname in [m.name for m in bpy.data.materials if m.name.startswith("m_practical")]:
        m = bpy.data.materials[mname]
        nd, inp = node_input(m, "BSDF_PRINCIPLED", "Emission Strength")
        if inp is not None and inp.default_value > 0:
            key_series(m.node_tree, f'nodes["{nd.name}"].inputs[{list(nd.inputs).index(inp)}].default_value', 0, frames,
                       inp.default_value * (0.8 + 0.45 * kick))
    wins = [o for o in bpy.data.objects if o.type == "LIGHT" and o.name.startswith("wl_")]
    for o in wins:
        base = base_series(o.data, "energy", 0, frames, o.data.energy)
        key_series(o.data, "energy", 0, frames, base * (1.0 + 0.55 * hey))
    sun = bpy.data.objects.get("overcast")
    if sun is not None:
        base = base_series(sun.data, "energy", 0, frames, sun.data.energy)
        key_series(sun.data, "energy", 0, frames, base * (1.0 + 0.4 * hey))
    if wins or sun:
        notes.append("window/sky light lifts on the Hey!s")
    return notes


def haze(room, density=0.02):
    """A low-density volume over the room and a spot through each window, so the window light shows as beams."""
    size = {"live": ((0, 5, 2.3), (14, 10, 4.6)), "cafe": ((0, 4.5, 1.8), (12, 9, 3.6)),
            "treehouse": ((0, 3, 1.8), (7, 6, 3.6))}.get(room)
    if size is None:
        return None
    m = bpy.data.materials.new("haze")
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    v = nt.nodes.new("ShaderNodeVolumePrincipled")
    v.inputs["Density"].default_value = density
    v.inputs["Color"].default_value = (0.9, 0.92, 0.95, 1)
    v.inputs["Anisotropy"].default_value = 0.55
    nt.links.new(v.outputs[0], out.inputs["Volume"])
    c, s = size
    o = gb.box("haze_volume", c, s, m)
    o.visible_shadow = False
    spots = 0
    for w in [o_ for o_ in bpy.data.objects if o_.type == "LIGHT" and o_.name.startswith("wl_")]:
        ld = bpy.data.lights.new(f"beam_{w.name}", "SPOT")
        ld.energy = {"live": 900, "cafe": 280, "treehouse": 450}[room]
        ld.spot_size = math.radians(38)
        ld.spot_blend = 0.6
        ld.shadow_soft_size = 0.4
        ld.color = gb.lin(K.PAL["daylight"])[:3]
        ld.specular_factor = 0.0
        ld.diffuse_factor = 0.15                                # beams in the haze, not a key on faces
        ld.volume_factor = 1.0
        so = gb.link(bpy.data.objects.new(f"beam_{w.name}", ld))
        n_ = w.matrix_world.to_3x3() @ Vector((0, 0, -1))       # the area light's shine direction
        so.location = w.location - n_ * 0.3 + Vector((0, 0, 0.6))
        so.rotation_euler = gb.look_rot(tuple(so.location), tuple(so.location + n_ * 5 + Vector((0, 0, -2.2))))
        spots += 1
    return f"haze volume {density} with {spots} window beams"


def safe_dips(ts, t0, t1, r, cfg):
    """M7e: a brightness per frame (1 lit, cfg dim at the bottom of a dip) for a flicker from t0 to t1 that stays
    under the photosensitive-seizure limit: at most one dip each min_gap_s (so under 3 a second), each dip_s long,
    easing in and out over ease_s, the gaps closing toward t1."""
    dips, t = [], t0 + r.uniform(0.05, cfg["min_gap_s"])
    while t < t1:
        p = (t - t0) / max(t1 - t0, 1e-3)
        d = r.uniform(*cfg["dip_s"])
        dips.append((t, min(t + d, t1)))
        t += d + cfg["min_gap_s"] * (1.0 + (1.0 - p) * r.uniform(0.3, 1.2))
    lvl = np.ones(len(ts))
    e = cfg["ease_s"]
    for i, tt in enumerate(ts):
        for a, z in dips:
            if a - e <= tt <= z + e:
                w = min(1.0, (tt - (a - e)) / e, ((z + e) - tt) / e)
                lvl[i] = min(lvl[i], 1.0 - (1.0 - cfg["dim"]) * w)
    return lvl, dips


def _emit_input(m):
    for nd in m.node_tree.nodes:
        if nd.type == "EMISSION":
            return nd, nd.inputs["Strength"]
    return node_input(m, "BSDF_PRINCIPLED", "Emission Strength")


def onair_flicker(b, n, t0, t1):
    """ON AIR (the live room) flickers from song time t0 to t1 (the last beats before stop 1)."""
    lit = S.OBJ.get("onair")
    if lit is None:
        return None
    if ONAIR_SAFE is not None:                   # M7e: slow dips in brightness, not a per-frame blink
        frames = np.arange(1, n + 1)
        ts = np.array([song_t(b, f) for f in frames])
        lvl, dips = safe_dips(ts, t0, t1, gb.rng(f"m7e_onair_{b}"), ONAIR_SAFE)
        m = lit.active_material
        nd, inp = _emit_input(m)
        if inp is not None:
            key_series(m.node_tree, f'nodes["{nd.name}"].inputs[{list(nd.inputs).index(inp)}].default_value', 0, frames,
                       inp.default_value * lvl)
        g = bpy.data.objects.get("onair_glow")
        if g:
            key_series(g.data, "energy", 0, frames, g.data.energy * lvl)
        lit.hide_render = False
        return f"ON AIR dims {len(dips)} times {t0:.2f}-{t1:.2f} s (M7e, at most one dip each {ONAIR_SAFE['min_gap_s']} s)"
    unlit = A.twin(lit, "onair_unlit", "lit", 0.15)
    r = gb.rng(f"m5b_onair_{b}")
    frames = np.arange(1, n + 1)
    ts = np.array([song_t(b, f) for f in frames])
    on = np.ones(n)
    for i, t in enumerate(ts):
        if t0 <= t < t1:
            p = 0.25 + 0.45 * (t - t0) / max(t1 - t0, 1e-3)
            on[i] = 0.0 if r.random() < p else 1.0
    lit.hide_render = False
    key_series(lit, "hide_render", 0, frames, 1 - on, "CONSTANT")
    key_series(unlit, "hide_render", 0, frames, on, "CONSTANT")
    g = bpy.data.objects.get("onair_glow")
    if g:
        key_series(g.data, "energy", 0, frames, g.data.energy * on, "CONSTANT")
    return f"ON AIR flickers {t0:.2f}-{t1:.2f} s"


def lamp_flicker(b, n, t0, t1):
    """Before stop 2: the park lamp flickers and Switch strains (jitters on his box)."""
    r = gb.rng(f"m5b_lamp_{b}")
    frames = np.arange(1, n + 1)
    ts = np.array([song_t(b, f) for f in frames])
    m = bpy.data.materials.get("lamp_glow")
    notes = []
    if m:
        nd, inp = node_input(m, "BSDF_PRINCIPLED", "Emission Strength")
        if inp is not None:
            v = np.full(n, inp.default_value)
            if ONAIR_SAFE is not None:           # M7e: slow dips, not a per-frame blink
                lvl, _ = safe_dips(ts, t0, t1, gb.rng(f"m7e_lamp_{b}"), ONAIR_SAFE)
                v = v * lvl
            for i, t in enumerate(ts):
                if ONAIR_SAFE is None and t0 <= t < t1 and r.random() < 0.25 + 0.4 * (t - t0) / (t1 - t0):
                    v[i] = 0.2
            key_series(m.node_tree, f'nodes["{nd.name}"].inputs[{list(nd.inputs).index(inp)}].default_value', 0, frames,
                       v, "CONSTANT")
            notes.append("lamp flickers")
    sw = S.OBJ.get("switch")
    if sw is not None:
        x0, z0 = sw.location.x, sw.location.z
        if ONAIR_SAFE is None:
            jit = np.array([(0.004 * math.sin(i * 2.7) if t0 <= t < t1 else 0.0) for i, t in enumerate(ts)])
        else:                                    # M7e: a tremble at 5 Hz, not a jump every frame (13 Hz)
            jit = np.array([(0.003 * math.sin(2 * math.pi * 5.0 * (t - t0)) if t0 <= t < t1 else 0.0) for t in ts])
        key_series(sw, "location", 0, frames, x0 + jit)
        key_series(sw, "location", 2, frames, z0 - np.array([0.01 * min(1, max(0, (t - t0) / (t1 - t0))) for t in ts]))
        notes.append("Switch strains")
    return ", ".join(notes) + f" {t0:.2f}-{t1:.2f} s"


def breakthrough(b, n):
    """'Service has been restored' (170.57 and 175.39 s): light breaks through the door (O19a) and the sky (O19b)."""
    frames = np.arange(1, n + 1)
    ts = np.array([song_t(b, f) for f in frames])
    lines = [170.57, 175.388]
    ramp = np.array([sum(min(1.0, max(0.0, (t - l) / 1.2)) * (0.6 if k else 1.0) for k, l in enumerate(lines)) for t in ts])
    if b == "O19a":
        dl = bpy.data.objects.get("door_light")
        if dl:
            key_series(dl.data, "energy", 0, frames, dl.data.energy * (0.4 + 2.2 * ramp))
        return "door light breaks through"
    sun = bpy.data.objects.get("overcast")
    if sun:
        base = base_series(sun.data, "energy", 0, frames, sun.data.energy)
        key_series(sun.data, "energy", 0, frames, base * (0.7 + 0.5 * np.clip(ramp, 0, 1.6)))
    return "sky brightens on the restored lines"


def bulb_chase(b, n):
    """String lights chase the lead vocal: each sung syllable sends a bright pulse out from the hub along every strand
    (0.9 s to the hooks); O16's cascade (M5 keys) still puts each bulb out on its frame."""
    bulbs = S.OBJ.get("bulbs") or []
    if not bulbs:
        return None
    frames = np.arange(1, n + 1)
    ts = np.array([song_t(b, f) for f in frames])
    on_t = np.array([h["t"] for h in LEAD_ON])
    on_w = np.array([h["strength"] for h in LEAD_ON])
    sel = (on_t > ts[0] - 1.0) & (on_t < ts[-1])
    on_t, on_w = on_t[sel], on_w[sel]
    for o in bulbs:
        d = o["dist"]
        base = base_series(o, '["on"]', 0, frames, o["on"])
        arr = on_t + 0.9 * d                                     # when each pulse reaches this bulb
        v = np.zeros(n)
        for t_a, w in zip(arr, on_w):
            v += w * np.exp(-((ts - t_a) / 0.09) ** 2)
        key_series(o, '["on"]', 0, frames, base * (0.62 + 0.55 * np.clip(v, 0, 1.0)))
    return f"{len(bulbs)} bulbs chase {len(on_t)} sung syllables"


# ---------------------------------------------------------------- ambient

def rain_flow(n, speed=0.5):
    k = 0
    for m in bpy.data.materials:
        if not m.get("window"):
            continue
        for nd in m.node_tree.nodes:
            if nd.type == "MAPPING":
                loc = nd.inputs["Location"]
                path = f'nodes["{nd.name}"].inputs[{list(nd.inputs).index(loc)}].default_value'
                z0 = loc.default_value[2]
                key_series(m.node_tree, path, 2, [1, n + 1], [z0, z0 + speed * n / FPS])
                k += 1
    return f"rain runs on {k} panes"


def drizzle_fall(n, v=3.2):
    k = 0
    for o in [o for o in bpy.data.objects if o.name.startswith("drizzle") and o.type == "MESH"]:
        h = o.dimensions.z
        top = o.copy()
        top.location.z += h
        for c in o.users_collection:
            c.objects.link(top)
        per = h / v * FPS
        for x in (o, top):
            z0 = x.location.z
            fc = key_series(x, "location", 2, [1, 1 + per], [z0, z0 - h])
            fc.modifiers.new("CYCLES")
        k += 1
    return f"drizzle falls ({k} volumes, looped)" if k else None


def steam(n):
    out = []
    for nm in ("pmug0", "pmug1"):
        mg = bpy.data.objects.get(nm)
        if mg is None:
            continue
        m = bpy.data.materials.new(f"steam_{nm}")
        m.use_nodes = True
        nt = m.node_tree
        nt.nodes.clear()
        N, L = nt.nodes.new, nt.links.new
        o_ = N("ShaderNodeOutputMaterial")
        tc = N("ShaderNodeTexCoord")
        mp = N("ShaderNodeMapping")
        mp.inputs["Scale"].default_value = (5.0, 5.0, 2.2)
        L(tc.outputs["Generated"], mp.inputs["Vector"])
        nz = N("ShaderNodeTexNoise")
        nz.inputs["Scale"].default_value = 3.0
        nz.inputs["Detail"].default_value = 3.0
        L(mp.outputs[0], nz.inputs["Vector"])
        sep = N("ShaderNodeSeparateXYZ")
        L(tc.outputs["Generated"], sep.inputs[0])
        fade = N("ShaderNodeMath"); fade.operation = "SINE"          # 0 at the bottom and top, 1 midway
        mul0 = N("ShaderNodeMath"); mul0.operation = "MULTIPLY"; mul0.inputs[1].default_value = math.pi
        L(sep.outputs["Z"], mul0.inputs[0]); L(mul0.outputs[0], fade.inputs[0])
        fx = N("ShaderNodeMath"); fx.operation = "SINE"
        mulx = N("ShaderNodeMath"); mulx.operation = "MULTIPLY"; mulx.inputs[1].default_value = math.pi
        L(sep.outputs["X"], mulx.inputs[0]); L(mulx.outputs[0], fx.inputs[0])
        ramp = N("ShaderNodeMapRange")
        ramp.inputs["From Min"].default_value, ramp.inputs["From Max"].default_value = 0.5, 0.75
        L(nz.outputs["Fac"], ramp.inputs["Value"])
        a1 = N("ShaderNodeMath"); a1.operation = "MULTIPLY"
        a2 = N("ShaderNodeMath"); a2.operation = "MULTIPLY"
        a3 = N("ShaderNodeMath"); a3.operation = "MULTIPLY"; a3.inputs[1].default_value = 0.35
        L(ramp.outputs[0], a1.inputs[0]); L(fade.outputs[0], a1.inputs[1])
        L(a1.outputs[0], a2.inputs[0]); L(fx.outputs[0], a2.inputs[1])
        L(a2.outputs[0], a3.inputs[0])
        em = N("ShaderNodeEmission"); em.inputs["Color"].default_value = (0.95, 0.94, 0.92, 1); em.inputs["Strength"].default_value = 0.7
        tr = N("ShaderNodeBsdfTransparent")
        mix = N("ShaderNodeMixShader")
        L(a3.outputs[0], mix.inputs[0]); L(tr.outputs[0], mix.inputs[1]); L(em.outputs[0], mix.inputs[2])
        L(mix.outputs[0], o_.inputs["Surface"])
        m.surface_render_method = "BLENDED"
        p = mg.matrix_world.translation
        for k_ in range(2):
            pl = gb.plane(f"steam_{nm}_{k_}", (p.x, p.y, p.z + 0.2), (0.1, 0.24), m, facing="-Y")
            pl.rotation_euler.z += k_ * math.pi / 2
            pl.visible_shadow = False
        loc = mp.inputs["Location"]
        key_series(nt, f'nodes["{mp.name}"].inputs[{list(mp.inputs).index(loc)}].default_value', 2, [1, n + 1],
                   [0.0, -0.9 * n / FPS])
        out.append(nm)
    return f"steam on {', '.join(out)}" if out else None


def umbrella_turn(b, n):
    u = bpy.data.objects.get("umbrella")
    h = S.OBJ.get("umbrella_holder")
    if u is None or h is None:
        return None
    hand = Vector(poses.hand(h.instance_collection, "Right"))
    piv = gb.empty("umbrella_pivot", tuple(hand))
    piv.parent = h
    u.parent = piv
    u.location = tuple(-hand)
    frames = np.arange(1, n + 1)
    ts = np.array([song_t(b, f) for f in frames])
    key_series(piv, "rotation_euler", 2, frames, 0.5 * np.sin(2 * np.pi * ts / 7.0) + 0.15 * ts)
    key_series(piv, "rotation_euler", 1, frames, math.radians(3) * np.sin(2 * np.pi * ts / 3.1))
    return "umbrella turns"


def fog_cards(n):
    """Three wide fog cards between the hill and the skyline, drifting sideways (park)."""
    m = bpy.data.materials.new("fog_card")
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    N, L = nt.nodes.new, nt.links.new
    o_ = N("ShaderNodeOutputMaterial")
    tc = N("ShaderNodeTexCoord")
    mp = N("ShaderNodeMapping"); mp.inputs["Scale"].default_value = (3.0, 1.0, 1.0)
    L(tc.outputs["Generated"], mp.inputs["Vector"])
    nz = N("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 2.5; nz.inputs["Detail"].default_value = 2.0
    L(mp.outputs[0], nz.inputs["Vector"])
    sep = N("ShaderNodeSeparateXYZ"); L(tc.outputs["Generated"], sep.inputs[0])
    sn = N("ShaderNodeMath"); sn.operation = "SINE"
    mul = N("ShaderNodeMath"); mul.operation = "MULTIPLY"; mul.inputs[1].default_value = math.pi
    L(sep.outputs["Y"], mul.inputs[0]); L(mul.outputs[0], sn.inputs[0])
    rr = N("ShaderNodeMapRange"); rr.inputs["From Min"].default_value, rr.inputs["From Max"].default_value = 0.4, 0.75
    L(nz.outputs["Fac"], rr.inputs["Value"])
    a = N("ShaderNodeMath"); a.operation = "MULTIPLY"; L(rr.outputs[0], a.inputs[0]); L(sn.outputs[0], a.inputs[1])
    a2 = N("ShaderNodeMath"); a2.operation = "MULTIPLY"; a2.inputs[1].default_value = 0.45; L(a.outputs[0], a2.inputs[0])
    em = N("ShaderNodeEmission"); em.inputs["Color"].default_value = gb.lin(K.PAL["fog"]); em.inputs["Strength"].default_value = 1.0
    tr = N("ShaderNodeBsdfTransparent"); mix = N("ShaderNodeMixShader")
    L(a2.outputs[0], mix.inputs[0]); L(tr.outputs[0], mix.inputs[1]); L(em.outputs[0], mix.inputs[2])
    L(mix.outputs[0], o_.inputs["Surface"])
    m.surface_render_method = "BLENDED"
    for k, (y, w, z, h) in enumerate(((70, 260, -10, 40), (150, 420, -18, 60), (260, 600, -25, 80))):
        pl = gb.plane(f"fog_card{k}", (0, y, z), (w, h), m, facing="-Y")
        pl.visible_shadow = False
    loc = mp.inputs["Location"]
    key_series(nt, f'nodes["{mp.name}"].inputs[{list(mp.inputs).index(loc)}].default_value', 0, [1, n + 1],
               [0.0, 0.05 * n / FPS])
    return "fog cards drift"


# ---------------------------------------------------------------- cameras

def find_person(c):
    pose, near = c["pose"], Vector(c["near"] + [0])
    cands = [e for e in instances(("crowd",)) if pose == "any" or e.get("pose") == pose]
    if not cands:
        cands = instances(("crowd",))
    return min(cands, key=lambda e: (Vector(e.location) - near).length)


def _blocked(loc, tgt, me, others, r=0.32):
    """Does any other person (a 0.32 m cylinder up to 1.9 m) stand on the line from the camera to its target, or on
    the camera?"""
    a, b = Vector((loc[0], loc[1])), Vector((tgt[0], tgt[1]))
    for o in others:
        if o is me:
            continue
        q = Vector((o.matrix_world.translation.x, o.matrix_world.translation.y))
        ab = b - a
        u = 0.0 if ab.length < 1e-6 else max(0.0, min(1.0, (q - a).dot(ab) / ab.length_squared))
        if (a + ab * u - q).length < r and min(loc[2], tgt[2]) < 1.9:
            return True
    return False


def person_cam(c, e, sgn):
    p, f, r = person_frame(e)
    side = abs(c.get("side", 0.85))
    focus = None
    if c["part"] == "hands":
        h = (bone_world(e, "LeftHand") + bone_world(e, "RightHand")) / 2
        loc = h + r * side * sgn - f * 0.3 + Vector((0, 0, 0.04))
        tgt = h
    elif c["part"] == "mug":
        h = bone_world(e, "RightHand")
        loc = h + r * 0.8 * sgn - f * 0.9 + Vector((0, 0, -0.15))
        tgt = h + f * 0.2
    else:                                                        # the back of the head, a third of the frame
        hd = bone_world(e, "Head")
        loc = hd - f * 1.05 + r * 0.3 * sgn + Vector((0, 0, 0.12))
        tgt = Vector(c.get("aim") or c["dof"].get("rack_to") or (0, 8, 1.4))
        focus = hd + Vector((0, 0, 0.08))
        tgt = loc + (tgt - loc).normalized() * 3.0
    return loc, tgt, focus


def pick_person(c):
    """The crowd member nearest c["near"] in the pose, with a clear line from the camera to their hands, mug or head
    (either side); falls back to the nearest."""
    pose, near = c["pose"], Vector(c["near"] + [0])
    crowd = instances(("crowd",))
    others = [o for o in bpy.data.objects if o.type == "EMPTY" and o.instance_type == "COLLECTION"]
    cands = [e for e in crowd if pose == "any" or e.get("pose") == pose] or crowd
    cands.sort(key=lambda e: (Vector(e.location) - near).length)
    pref = 1 if c.get("side", 0.85) >= 0 else -1
    for e in cands[:8]:
        for sgn in (pref, -pref):
            loc, tgt, focus = person_cam(c, e, sgn)
            mid = tgt if c["part"] != "back" else focus
            if not _blocked(loc, mid, e, others):
                return e, loc, tgt, focus
    e = cands[0]
    loc, tgt, focus = person_cam(c, e, pref)
    return e, loc, tgt, focus


def person_frame(e):
    """(position, forward, right) of an instance in world space: the library faces -Y in figure space."""
    mw = e.matrix_world
    fwd = (mw.to_3x3() @ Vector((0, -1, 0))).normalized()
    fwd.z = 0
    fwd.normalize()
    right = Vector((fwd.y, -fwd.x, 0))
    return mw.translation.copy(), fwd, right


def bone_world(e, bone):
    """A bone's head (world) for a library or posed person instance at the current frame."""
    rig = next(o for o in e.instance_collection.objects if o.type == "ARMATURE")
    bpy.context.view_layer.update()
    pb = rig.pose.bones[poses.P + bone]
    return e.matrix_world @ (rig.matrix_world @ pb.tail if bone.endswith("Hand") else rig.matrix_world @ pb.head)


def cam_base(sub, c, b):
    """(loc, target, lens, focus point or None, fstop, rack point or None) for frame u in 0..1 -> callable."""
    over = sub.get("cam_override") or {}
    c = {**c, **over}
    lens = c.get("lens", 35)
    dof = c.get("dof")
    focus_pt, rack_pt = None, None
    if "board" in c:
        loc, tgt, lens = A.cam_from_board(c["board"])
    elif c.get("kind") == "person":
        sc_ = bpy.context.scene
        at = (sub["start_frame"] + 2) if c["part"] == "mug" else (sub["start_frame"] + sub["end_frame"]) / 2
        sc_.frame_set(int(at - build_vstart(b) + 1))                # the mug: on its Hey!, raised
        e, loc, tgt, focus_pt = pick_person(c)
        if focus_pt is None:
            focus_pt = tgt
        loc, tgt = tuple(loc), tuple(tgt)
        sub["_person"] = e.name
    elif c.get("kind") == "walker":
        loc, tgt = (0, 0, 0), (0, 1, 0)
    elif "m5" in c:
        loc, tgt = (0, 0, 0), (0, 1, 0)
    else:
        loc, tgt = tuple(c["loc"]), tuple(c["target"])
        to = bpy.data.objects.get(c.get("target_obj", ""))
        if to is not None:
            bpy.context.scene.frame_set(int((sub["start_frame"] + sub["end_frame"]) / 2 - build_vstart(b) + 1))
            bb = [to.matrix_world @ Vector(v) for v in to.bound_box]
            tgt = tuple(sum(bb, Vector()) / 8)
    if dof:
        if focus_pt is None:
            fp = dof.get("focus", "target")
            focus_pt = Vector(tgt) if fp in ("target", "person") else Vector(fp)
        if dof.get("rack_to"):
            rack_pt = Vector(dof["rack_to"])
    return dict(loc=Vector(loc), tgt=Vector(tgt), lens=lens, focus=focus_pt, fstop=(dof or {}).get("fstop"),
                rack=rack_pt, kind=c.get("kind"), part=c.get("part"), framing=c.get("framing", "mid"))


def ease(u):
    return u * u * (3 - 2 * u)


def walker_pos(f):
    w = S.OBJ["walker"]
    return Vector([_find(w, "location", i).evaluate(f) for i in range(3)])


HANDHELD = None          # M7e: the handheld drift's settings (blender/look.py sets them from config/look_m7.json)
ONAIR_SAFE = None       # M7e: the ON AIR sign's and the park lamp's flicker, dips at most ~2.4 a second


def make_camera(sub, b, f0, f1, m5_keys, n):
    """Key one camera for local frames f0..f1-1 (inclusive of a pre-roll for dissolves)."""
    room_cams = COV["cameras"][sub["room"]]
    c = room_cams[sub["camera"]]
    base = cam_base(sub, c, b)
    mv = sub.get("move") or {"type": "hold"}
    cam = gb.camera(f"cam_{sub['id']}", tuple(base["loc"]), tuple(base["tgt"]), base["lens"])
    cam.data.clip_end = 3000.0
    cam.data.clip_start = 0.03
    frames = list(range(f0, f1))
    m5 = None
    if mv["type"] == "m5" or "m5" in c:
        tmp = gb.camera("tmp_m5", m5_keys[0][1], m5_keys[0][2], m5_keys[0][3])
        A.key_cam(tmp, m5_keys, n)
        m5 = {}
        for f in frames:
            bpy.context.scene.frame_set(f)
            m5[f] = (tmp.matrix_world.copy(), tmp.data.lens)
        bpy.data.objects.remove(tmp)
    r = gb.rng(f"m5b_cam_{sub['id']}")
    amp_p = {"wide": 0.014, "mid": 0.011, "close": 0.006}[base["framing"] if base["framing"] in ("wide", "mid", "close") else "mid"]
    amp_r = math.radians({"wide": 0.22, "mid": 0.32, "close": 0.45}.get(base["framing"], 0.3))
    if mv["type"] == "hold" or sub["id"].startswith("O04"):
        amp_p, amp_r = 0.0, 0.0                                 # freezes; O04's phone is pinned in the edit
    sines = [(r.uniform(0.12, 0.75), r.uniform(0, 2 * math.pi), r.uniform(0.4, 1.0)) for _ in range(18)]
    hh = HANDHELD
    if hh is not None:
        # M7e (config/look_m7.json m7e.handheld): the same draws, slower; rotation as a share of the lens's field
        lo, hi = hh["freq"]
        sines = [(lo + (fr - 0.12) / 0.63 * (hi - lo), ph, a) for fr, ph, a in sines]
        fk = base["framing"] if base["framing"] in ("wide", "mid", "close") else "mid"
        if amp_p or amp_r:
            fov = math.degrees(2 * math.atan(18.0 / base["lens"]))
            amp_p, amp_r = hh["amp_pos"][fk], math.radians(hh["amp_rot_frac"][fk] * fov)

    def drift(t, ch):
        s = 0.0
        for k in range(3):
            fr, ph, a = sines[ch * 3 + k]
            s += a * math.sin(2 * math.pi * fr * t + ph)
        return s / 1.6

    kick_t = [h["t"] for h in KICKS]
    kick_w = [DRUMS_E[bar_index(h["t"])] * h["strength"] for h in KICKS]
    speed = mv.get("speed", 1.0)
    rack_at = sub["start_t"] + 0.6 if base["rack"] is not None else None
    L, R, LENS, FD = [], [], [], []
    prev = None
    for f in frames:
        u = (f - f0) / max(1, f1 - f0 - 1)
        t = song_t(b, f)
        if m5 is not None:
            mw, lens = m5[f]
            loc = mw.translation.copy()
            rot = mw.to_euler()
            tgt = loc + mw.to_3x3() @ Vector((0, 0, -10))
        else:
            loc, tgt, lens = base["loc"].copy(), base["tgt"].copy(), base["lens"]
            if base["kind"] == "walker":
                wp = walker_pos(f)
                ahead = (walker_pos(min(f + 30, n)) - wp)
                ahead.z = 0
                d = ahead.normalized() if ahead.length > 1e-3 else Vector((0.13, 0.99, 0))
                side = Vector((d.y, -d.x, 0))
                if base["part"] == "feet":
                    loc = wp - d * 1.5 + side * 0.9 + Vector((0, 0, 0.35))
                    tgt = wp + d * 0.2 + Vector((0, 0, 0.15))
                    base["focus"] = None
                    focus_d = (tgt - loc).length
                else:
                    loc = wp - d * 3.2 + side * 0.4 + Vector((0, 0, 1.75))
                    tgt = wp + d * 2.0 + Vector((0, 0, 1.35))
            elif mv["type"] == "push":
                loc = loc.lerp(tgt, mv["k"] * speed * ease(u))
            elif mv["type"] == "truck":
                d = Vector(mv["d"]) * ease(u)
                loc, tgt = loc + d, tgt + d
            rot = gb.look_rot(tuple(loc), tuple(tgt))
        # handheld drift and the kick bump
        if hh is None:
            bump = env_hits(t, kick_t, tau=0.07, attack=0.02, weights=kick_w) if mv["type"] != "hold" else 0.0
            kb = {"wide": 1.0, "mid": 0.8, "close": 0.5}.get(base["framing"], 0.8)
        else:
            kb = hh["kick_bump"].get(base["framing"], 0.0)
            bump = env_hits(t, kick_t, tau=hh["bump_tau"], attack=hh["bump_attack"], weights=kick_w) \
                if mv["type"] != "hold" and kb > 0 else 0.0
        bump = min(bump, 1.2)
        loc = loc + Vector((drift(t, 0), drift(t, 1), drift(t, 2))) * amp_p + Vector((0, 0, -0.007 * kb * bump))
        e = Euler((rot.x + drift(t, 3) * amp_r - math.radians(0.18) * kb * bump, rot.y + drift(t, 4) * amp_r * 0.5,
                   rot.z + drift(t, 5) * amp_r))
        if prev is not None:
            e.make_compatible(prev)
        prev = e.copy()
        L.append(tuple(loc))
        R.append(tuple(e))
        LENS.append(lens)
        if base["fstop"]:
            fp = base["focus"]
            if base["kind"] == "walker":
                fp = walker_pos(f) + Vector((0, 0, 0.3 if base["part"] == "feet" else 1.4))
            d0 = (fp - loc).length if fp is not None else (tgt - loc).length
            if base["rack"] is not None and rack_at is not None:
                d1 = (base["rack"] - loc).length
                w = min(1.0, max(0.0, (t - rack_at) / 0.4))
                d0 = d0 + (d1 - d0) * ease(w)
            FD.append(d0)
    for i in range(3):
        key_series(cam, "location", i, frames, [v[i] for v in L])
        key_series(cam, "rotation_euler", i, frames, [v[i] for v in R])
    key_series(cam.data, "lens", 0, frames, LENS)
    if FD:
        cam.data.dof.use_dof = True
        cam.data.dof.aperture_fstop = base["fstop"]
        key_series(cam.data, "dof.focus_distance", 0, frames, FD)
    if CAMERA_HOOK is not None:
        CAMERA_HOOK(cam, sub, b, f0, f1)
    return cam


# ---------------------------------------------------------------- per build

def layers(b, n, room, notes):
    if b in FREEZE:
        notes.append("freeze: no M5b motion")
        return
    t0, t1 = song_t(b, 1), song_t(b, n)
    if room in ("live", "cafe", "park") and b not in ("O08c",):
        notes.append(crowd_motion(b, n, room))
    if room != "void" and b not in ("O08c",):
        notes.append(band_motion(b, n))
    if room != "void":
        notes += pulse_lights(b, n, room)
        h = haze(room, {"live": 0.022, "cafe": 0.007, "treehouse": 0.015}.get(room, 0.0)) if room != "park" and not NOHAZE else None
        if h:
            notes.append(h)
        notes.append(rain_flow(n))
        d = drizzle_fall(n)
        if d:
            notes.append(d)
    if room == "cafe":
        notes.append(bulb_chase(b, n))
        notes.append(steam(n))
    if room == "park":
        notes.append(fog_cards(n))
        u = umbrella_turn(b, n)
        if u:
            notes.append(u)
    if b == "O11":
        notes.append(onair_flicker(b, n, A.TM["beats"]["beats"][list(zip(A.TM["beats"]["bar"], A.TM["beats"]["beat_in_bar"])).index((39, 3))], 93.8))
    if b == "O20":
        notes.append(lamp_flicker(b, n, 199.41, 201.8))
    if b in ("O19a", "O19b"):
        notes.append(breakthrough(b, n))
    if b == "O22":                                               # Switch stays OFF after stop 2's drop (O21)
        sw = S.OBJ.get("switch")
        if sw is not None:
            off = A.twin(sw, "switch_off", "flat", 1.0)
            sw.hide_render = True
            notes.append("Switch OFF (after O21's drop)")


def subs_by_build():
    out = {}
    for s in COV["subs"]:
        if s["source"] == "blender":
            out.setdefault(s["build"], []).append(s)
    return out


def local_range(s, b):
    v0 = build_vstart(b)
    f0 = s["start_frame"] - v0 + 1 - s.get("xfade_in", 0)
    f1 = s["end_frame"] - v0 + 1
    return f0, f1


def main():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="renders/m5b/frames")
    ap.add_argument("--only", default="", help="builds")
    ap.add_argument("--subs", default="", help="sub-shots")
    ap.add_argument("--size", default="960x540")
    ap.add_argument("--samples", type=int, default=8)
    ap.add_argument("--still", action="store_true", help="one PNG per sub-shot (its middle frame)")
    ap.add_argument("--nohaze", action="store_true", help="test: no haze volume or beams")
    ap.add_argument("--at", default="mid", help="with --still: mid | first | last | a fraction")
    a = ap.parse_args(argv)
    size = tuple(int(v) for v in a.size.split("x"))
    only = set(filter(None, a.only.split(",")))
    want = set(filter(None, a.subs.split(",")))
    order = ["O03", "O04", "O07", "O08", "O08c", "O09", "O10", "O11", "O12", "O14", "O15", "O16", "O17", "O18",
             "O19a", "O19b", "O20", "O21", "O22"]
    by = subs_by_build()
    for b in order:
        subs = [s for s in by.get(b, []) if not want or s["id"] in want]
        if (only and b not in only) or not subs:
            continue
        t0 = time.time()
        n = A.nframes(b)
        keys, expo, notes = A.shot(b, n)
        room = subs[0]["room"]
        layers(b, n, room, notes)
        K.render_settings(size, a.samples, expo)
        sc = bpy.context.scene
        sc.render.fps = FPS
        sc.eevee.volumetric_tile_size = "8"
        sc.eevee.volumetric_samples = 32
        if b in ("O10", "O14", "O15", "O16", "O17"):           # as M5
            K.bloom()
        if SETTINGS is not None:
            SETTINGS(b, room)
        gb.into(None)
        tb = time.time()
        print(f"M5b build {b}: {n} frames, {time.time() - t0:.1f} s; " + "; ".join(x for x in notes if x), flush=True)
        for s in subs:
            f0, f1 = local_range(s, b)
            ts0 = time.time()
            cam = make_camera(s, b, f0, f1, keys, n)
            sc.camera = cam
            c_ = {**COV["cameras"][s["room"]][s["camera"]], **(s.get("cam_override") or {})}
            # the cafe's crowd and band are lit more from the front than the other rooms': its people angles go darker
            extra = -0.9 if room == "cafe" and (c_.get("expo") or c_.get("kind")) else 0.0
            sc.view_settings.exposure = K.LOOK["exposure"] + expo + c_.get("expo", 0.0) + extra
            if EXPOSURE is not None:
                sc.view_settings.exposure = EXPOSURE(s, room, expo, c_)
            out = ROOT / a.out / s["id"]
            if not a.still:
                out.mkdir(parents=True, exist_ok=True)
            if a.still:
                fr = {"mid": (f0 + f1) // 2, "first": f0, "last": f1 - 1}.get(a.at)
                if fr is None:
                    fr = int(f0 + float(a.at) * (f1 - f0 - 1))
                sc.frame_set(fr)
                sc.render.image_settings.file_format = "PNG"
                sc.render.filepath = str(ROOT / a.out / f"{s['id']}.png")
                bpy.ops.render.render(write_still=True)
            else:
                sc.frame_start, sc.frame_end = f0, f1 - 1
                sc.render.image_settings.file_format = "JPEG"
                sc.render.image_settings.quality = 92
                sc.render.filepath = str(out) + "/"
                bpy.ops.render.render(animation=True)
            print(f"M5b {s['id']}: frames {f0}-{f1 - 1} ({f1 - f0}), {s['camera']}"
                  f"{' on ' + s['_person'] if s.get('_person') else ''}, {time.time() - ts0:.1f} s", flush=True)
        print(f"M5b build {b} done in {time.time() - t0:.1f} s", flush=True)


if __name__ == "__main__":
    main()
