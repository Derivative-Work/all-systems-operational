"""M5c: the band's holds and performances (blender/perf.py has the body solver and why it runs at set time).

Each band member becomes their own copy of their library person (sets.BAND), posed holding their instrument, then
keyed on every frame of the build from timing/music_map.json:
- guitar (person 3): fretting hand on the neck, sliding to a new chord position on bar changes; strumming hand over
  the sound hole on an eighth-note down/up motion that crosses the strings on each strum onset of the guitar stem
  (hits "strums"), full strokes where there's an onset, small ghost strokes where there isn't, scaled by the bar's
  guitar energy.
- banjo (person 8): fretting hand as the guitar's; picking hand resting by the bridge, fingers flicking on 16ths
  and the wrist bouncing on eighths, driven by the guitar stem's energy (the banjo has no stem of its own).
- kick (person 12): seated on the stool, right foot on a pedal (blender/perf_props.py); on every kick hit
  (hits "kick", strength > 0.4) the footboard goes down and the beater swings into the batter head on the hit's
  frame; on the main kicks the heel lifts first. Hands clap on the backbeat. The kit's snare is gone (decisions 15).
- tambourine (person 17): the tambourine in the right hand at chest height; each percussion-stem hit (hits
  "tambourine", strength > 0.35) is a shake (wrist twist); hits on beats 2 and 4 slap the rim into the open left
  palm.
- singer (person 22, the lead): left hand on the mic stand; head and upper body follow the lead vocal envelope
  (lifting into loud lines, a nod on each sung syllable). The Mixamo rig has no jaw bone, so no jaw.
- everyone standing: a bob on the beat (half-time in the bridge) and a slow weight shift, legs re-solved so the
  feet stay planted; the four singers lean into their mics on each Hey! and with the gang-vocal (backing) envelope.
"""
import math

import bpy
import numpy as np
from mathutils import Euler, Matrix, Quaternion, Vector

import aso_props as PR
import coverage as C
import gb
import perf as PF
import perf_grips as G
import perf_props as PP
import sets as S

ALL_KICKS = [h for h in C.MM["hits"]["kick"] if h["strength"] > 0.4]
STRUMS = C.MM["hits"]["strums"]
GUITAR_E = C.MM["energy"]["guitar"]["norm"]
LEAD_ENV = np.array(C.MM["env_30fps"]["lead"])
BACK_ENV = np.array(C.MM["env_30fps"]["backing"])
EIGHTHS = np.sort(np.concatenate([C.BEATS, (C.BEATS[:-1] + C.BEATS[1:]) / 2]))
_CH = gb.rng("m5c_chords").integers(0, 3, len(C.BARS) + 2)       # chord shape per bar (fret position)
Y = Vector((0, 1, 0))


def env_at(arr, t):
    i = int(round(t * FPS_))
    return float(arr[min(max(i, 0), len(arr) - 1)])


FPS_ = 30


def tamb_hits():
    out = []
    bb = set(round(t, 2) for t in C.BACKBEAT)
    for h in C.TAMB:
        bib = int(h["bar_beat"].split(".")[1])
        slap = bib in (2, 4) and abs(h["off_ms"]) < 70 and h["strength"] > 0.6
        out.append((h["t"], h["strength"], slap))
    return out


TAMB_H = tamb_hits()


# ---------------------------------------------------------------- timing curves

def strum_crossings():
    """For every eighth of the grid, the time the strumming hand crosses the strings (the onset if one is within
    90 ms, else the grid) and the stroke size (1 with an onset, scaled by its strength; 0.3 a ghost)."""
    st = np.array([h["t"] for h in STRUMS])
    sw = np.array([h["strength"] for h in STRUMS])
    cross, amp = [], []
    for t in EIGHTHS:
        k = int(np.argmin(np.abs(st - t))) if len(st) else 0
        if len(st) and abs(st[k] - t) < 0.09:
            cross.append(st[k])
            amp.append(0.55 + 0.45 * sw[k])
        else:
            cross.append(t)
            amp.append(0.3)
    return np.array(cross), np.array(amp)


CROSS, CAMP = strum_crossings()


def strum_phase(t):
    """(e, amplitude): e is the eighth count, integer at each crossing (even: a down stroke)."""
    k = int(np.clip(np.searchsorted(CROSS, t) - 1, 0, len(CROSS) - 2))
    e = k + (t - CROSS[k]) / max(CROSS[k + 1] - CROSS[k], 1e-3)
    u = e - k
    a = CAMP[k] * (1 - u) + CAMP[k + 1] * u
    # the eighth index parity is the grid's: EIGHTHS[0] is a beat (down)
    return e, a


def hit_env(t, times, pre=0.09, tau=0.07):
    """0..1: rises over `pre` s into each hit (eased), decays after it."""
    v = 0.0
    for h in times:
        d = t - h
        if -pre <= d < 0:
            x = (d + pre) / pre
            v = max(v, x * x * (3 - 2 * x))
        elif 0 <= d < 6 * tau:
            v = max(v, math.exp(-d / tau))
    return v


def window(times, t0, t1):
    return [x for x in times if t0 - 1.0 <= x <= t1 + 1.0]


# ---------------------------------------------------------------- shared standing motion

class Standing:
    """The planted-feet idle under each standing band member: bob, weight shift, breathing, lean-ins."""

    def __init__(self, body, r, half):
        self.b = body
        self.ankles = {s: body.head(f"{s}Foot") for s in ("Left", "Right")}
        self.feet = {s: body.M(f"{s}Foot").to_3x3() for s in ("Left", "Right")}
        self.knee = {s: body.head(f"{s}Leg") for s in ("Left", "Right")}
        u = r.random(4)
        self.lag = 0.06 + 0.1 * u[0]
        self.bob = 0.008 + 0.009 * u[1]
        self.shift = 0.008 + 0.008 * u[2]
        self.ph = u[3] * 6.28
        self.half = half

    def pre(self, t, energy, lean=0.0, lean_spine=(0.55, 0.45)):
        """Hips and spine for time t (before the arms). lean: degrees forward (lean-in)."""
        b = self.b
        bp = C.beat_pos(t)
        ph = (bp - self.lag) / (2.0 if self.half else 1.0)
        dz = -self.bob * (0.4 + 0.6 * energy) * (0.5 + 0.5 * math.cos(2 * math.pi * ph))
        dx = self.shift * math.sin(2 * math.pi * bp / 8.0 + self.ph)        # over two bars
        b.move("Hips", (dx, 0, dz))
        b.rot("Spine", z=-dx / self.shift * 0.8 if self.shift else 0)
        b.rot("Spine1", x=0.6 * math.sin(2 * math.pi * t / 4.1 + self.ph) + lean * lean_spine[0])
        b.rot("Spine2", x=lean * lean_spine[1])
        b.rot("Head", x=1.2 * (0.5 + 0.5 * math.cos(2 * math.pi * ph)))

    def legs(self):
        b = self.b
        for s in ("Left", "Right"):
            pole = self.knee[s] + Vector((0, -0.5, 0.1))
            b.two_bone(f"{s}UpLeg", f"{s}Leg", self.ankles[s], pole)
            b.orient(f"{s}Foot", self.feet[s])


# ---------------------------------------------------------------- the instruments: holds

FRETS = {"guitar": (1, 2, 3), "banjo": (1, 2, 3)}     # the index finger's fret for each chord shape (_CH); open positions (M5c review 2)


PF.WRIST_LABEL.update({"guitar fretting": G.Fretting.LIM, "banjo fretting": G.Fretting.LIM,
                       "kick player clap": G.CLAP_LIM, "crowd clap": G.CLAP_LIM, "crowd clap (joining in)": G.CLAP_LIM,
                       "O12 late clapper": G.CLAP_LIM})


def guitarist(e, b, coll, rig, obs):
    """M5c review: the acoustic of blender/instruments.py (Ever Present's neck), on a strap, fretted and strummed by
    blender/perf_grips.py's hands."""
    body = PF.Body(rig)
    ins = G.Instr(body, coll, "guitar", obs, "guitar")
    fr = G.Fretting(body, ins, FRETS["guitar"])
    st = G.Strumming(body, ins)
    body.keep()
    PF.parent_to_bone(ins.obj, body, "Spine", coll)
    strap = G.Strap(body, coll, ins, "guitar")
    return body, dict(ins=ins, fret=fr, strum=st, strap=strap), ins.obj


def banjoist(e, b, coll, rig, obs):
    body = PF.Body(rig)
    ins = G.Instr(body, coll, "banjo", obs, "banjo")
    fr = G.Fretting(body, ins, FRETS["banjo"])
    st = G.Strumming(body, ins)
    body.keep()
    PF.parent_to_bone(ins.obj, body, "Spine", coll)
    strap = G.Strap(body, coll, ins, "banjo")
    return body, dict(ins=ins, fret=fr, strum=st, strap=strap), ins.obj


def tamb_player(e, b, coll, rig):
    """M5c review: the tambourine gripped at its frame with the wrist in line (blender/perf_grips.py)."""
    body = PF.Body(rig)
    tm = G.Tambourine(body, PP.tambourine)
    body.keep()
    PF.parent_to_bone(tm.obj, body, "RightHand", coll)
    return body, dict(tm=tm), tm.obj


def singer(e, b, coll, rig, mouth):
    body = PF.Body(rig)
    pole_y = mouth.y - 0.27
    grip = Vector((0.0, pole_y, mouth.z - 0.36))
    sg = G.StandGrip(body, grip)
    import contact as CT
    G.clear_hanging(body, "Right", CT.body_obstacles(coll, body))      # the free arm off the thigh
    body.keep()
    return body, dict(pole_y=pole_y, grip=grip, sg=sg)


def kick_player(e, b, coll, rig):
    """Seated on the stool, moved 0.17 m to their left so the right foot sits on the pedal at the drum's centre."""
    rig.location = (0.17, 0.0, 0.0)
    off = Vector((0.17, 0, 0))
    body = PF.Body(rig)
    hips = body.M("Hips")
    m = hips.copy()
    m.translation = Vector((0.0, 0.0, 0.62))
    body.set_M("Hips", m)
    ank = {"Right": PP.HEEL + Vector((0, 0.005, 0.085)) - off, "Left": Vector((0.36, -0.47, 0.085)) - off}
    toes = {"Right": None, "Left": Vector((0.37, -0.64, 0.03)) - off}
    for s in ("Left", "Right"):
        body.two_bone(f"{s}UpLeg", f"{s}Leg", ank[s], body.head(f"{s}UpLeg") + Vector((0, -1.0, 0.7)))
    body.aim("LeftFoot", toes["Left"] - body.head("LeftFoot"))
    body.aim("RightFoot", (PP.board_toe(PP.REST_TOE) - off + Vector((0, 0.075, 0.035))) - body.head("RightFoot"))
    G.clap_fingers(body)
    body.keep()
    return body, dict(off=off, ank=ank, toes=toes)


# ---------------------------------------------------------------- per-frame performances

def clap_amount(t, lag=0.0, times=None):
    """Hands together on each backbeat (plus lag, s), apart between: 1 at the clap."""
    times = C.BACKBEAT if times is None else times
    v = 0.0
    for h in times:
        d = t - (h + lag)
        if -0.16 <= d <= 0:
            x = (d + 0.16) / 0.16
            v = max(v, x * x)
        elif 0 < d < 0.2:
            v = max(v, 1 - d / 0.2)
    return v


def lean_amount(t):
    """Gang vocals: lean on the Hey!s (to 1) and with the backing envelope (to 0.35)."""
    h = C.env_hits(t, C.HEYS, tau=0.3, attack=0.13)
    return min(1.0, h) * 1.0 + 0.35 * max(0.0, (env_at(BACK_ENV, t) - 0.4) / 0.6)


LEAN_DEG = 7.5            # with the mic 9 cm off, the mouth travels ~6 cm


def perform(b, n, freeze_t=None, seed_build=None):
    """Replace the band of the current build with performing copies. freeze_t: hold the pose at that song time on
    every frame (the hard stops). Returns notes and the per-role data (for the checks and the sheet)."""
    band = S.OBJ.get("band")
    if not band:
        return "no band", {}
    for nm in ("guitar", "banjo", "tambourine", "kick", "kick_head", "snare"):
        o = bpy.data.objects.get(nm)
        if o is not None:
            bpy.data.objects.remove(o)
    for role in band:
        o = bpy.data.objects.get(f"mic_{role}")
        if o is not None:
            bpy.data.objects.remove(o)
    r = gb.rng(f"m5c_band_{seed_build or b}")
    frames = np.arange(1, n + 1)
    ts = [C.song_t(b, f) for f in frames] if freeze_t is None else [freeze_t] * n
    half = b == "O18"
    roles = {}
    gb.into(None)
    for role, e in band.items():
        coll, rig = PF.own_copy(e, f"{role}_{b}")
        roles[role] = dict(e=e, coll=coll, rig=rig)
    # each performer's own body, for fitting the instruments and the contact check (blender/contact.py)
    import contact as CT
    for role in ("guitar", "banjo"):                  # (their torsos are the library's; the arms aren't in these)
        roles[role]["obs"] = CT.body_obstacles(roles[role]["coll"], PF.Body(roles[role]["rig"]))
    # holds
    gbody, ginfo, _ = guitarist(band["guitar"], b, roles["guitar"]["coll"], roles["guitar"]["rig"],
                                roles["guitar"]["obs"])
    bbody, binfo, _ = banjoist(band["banjo"], b, roles["banjo"]["coll"], roles["banjo"]["rig"],
                               roles["banjo"]["obs"])
    tbody, tinfo, tamb = tamb_player(band["tamb"], b, roles["tamb"]["coll"], roles["tamb"]["rig"])
    sbody0 = PF.Body(roles["singer"]["rig"])
    mouth_s = sbody0.head("Head") + Vector((0, -0.105, 0.065))
    sbody, sinfo = singer(band["singer"], b, roles["singer"]["coll"], roles["singer"]["rig"], mouth_s)
    kbody, kinfo = kick_player(band["kick"], b, roles["kick"]["coll"], roles["kick"]["rig"])
    S.OBJ["tambourine"] = tamb
    roles["guitar"]["info"], roles["banjo"]["info"] = ginfo, binfo
    # mics at each singer's mouth (figure space of their instance, parented to it; static)
    mics = {}
    for role, body in (("guitar", gbody), ("banjo", bbody), ("tamb", tbody), ("singer", sbody)):
        mouth = body.head("Head") + Vector((0, -0.105, 0.065))
        kw = {}
        if role == "singer":
            kw = dict(pole_y=sinfo["pole_y"])
        if role == "tamb":
            kw = dict(pole_x=0.24, pole_y=mouth.y - 0.45)
        o, top = PP.mic_stand_at(f"mic_{role}", mouth, parent=band[role], **kw)
        mics[role] = (mouth, o)
    mic_tip = {role: mouth + Vector((0, -0.09, -0.015)) for role, (mouth, o) in mics.items()}
    PF.REPORT.setdefault("mic", {})
    # the kit, on the kick player's instance (figure space)
    S.OBJ["kick"], S.OBJ["kick_head"] = PP.kick_drum("kick", band["kick"])
    _, board, beater = PP.pedal("kick_pedal", band["kick"])
    st = bpy.data.objects.get("kick_stool")
    if st is not None:
        st.location.x = 0.17
    for role in ("guitar", "banjo", "tamb", "singer", "kick"):
        roles[role]["body"] = {"guitar": gbody, "banjo": bbody, "tamb": tbody, "singer": sbody, "kick": kbody}[role]
    for bd in (gbody, bbody, tbody, sbody, kbody):
        gbody_spine_inv(bd)
    checkers = make_checkers(b, roles, mics)
    # per-frame
    t0, t1 = min(ts), max(ts)
    kicks = window([h["t"] for h in ALL_KICKS], t0, t1)
    mains = window([h["t"] for h in C.KICKS], t0, t1)
    tam = [h for h in TAMB_H if t0 - 1 <= h[0] <= t1 + 1]
    stand = {role: Standing(roles[role]["body"], r, half) for role in ("guitar", "banjo", "tamb", "singer")}
    recs = {role: PF.Rec(roles[role]["body"], PF.CORE + PF.ARMS + PF.LEGS + (
        ["RightHandIndex1", "RightHandMiddle1", "RightHandThumb1"] if role == "banjo" else []) + (
        [f"LeftHand{f}{k}" for f in ("Index", "Middle", "Ring", "Pinky") for k in (1, 2, 3)]
        if role in ("guitar", "banjo") else [])) for role in roles}
    board_v, beater_v = [], []
    PF.CHECK_ON[0] = True
    for i, t in enumerate(ts):
        if freeze_t is not None and i > 0:
            break
        bi = C.bar_index(t)
        ge = GUITAR_E[bi]
        en = C.DRUMS_E[bi]
        lean = lean_amount(t) * LEAN_DEG
        # chord position: slides over 0.12 s at each bar start
        bs = C.BARS[bi]["start"]
        wslide = min(1.0, max(0.0, (t - bs) / 0.12))
        prev_k, cur_k = _CH[max(bi - 1, 0)], _CH[bi]
        # guitar
        body = gbody
        body.reset()
        stand["guitar"].pre(t, en, lean)
        stand["guitar"].legs()
        rel = body.M("Spine") @ gbody_spine_inv(gbody)
        e8, a8 = strum_phase(t)
        A = a8 * (0.25 + 0.75 * min(1.0, ge / 0.7)) if ge > 0.05 else 0.05
        h = -A * math.sin(math.pi * e8) * 0.065
        ginfo["strum"].solve(rel, h, ginfo["strum"].flex0 - 8.0 * A * math.cos(math.pi * e8))   # the wrist leads the stroke
        fk = FRETS["guitar"][prev_k] * (1 - wslide) + FRETS["guitar"][cur_k] * wslide
        ginfo["fret"].solve(rel, fk)
        ginfo["strap"].add()
        recs["guitar"].add()
        # banjo
        body = bbody
        body.reset()
        stand["banjo"].pre(t, en, lean)
        stand["banjo"].legs()
        rel = body.M("Spine") @ gbody_spine_inv(bbody)
        drive = min(1.0, ge / 0.7) if ge > 0.05 else 0.0
        bp = C.beat_pos(t)
        bounce = 0.006 * drive * math.sin(2 * math.pi * bp * 2)
        binfo["strum"].solve(rel, bounce, binfo["strum"].flex0 + 4.0 * drive * math.sin(2 * math.pi * bp * 2))
        for f_, ph in (("Index", 0.0), ("Middle", 0.5)):
            body.flex("Right", f_, 1, 14 * drive * math.sin(2 * math.pi * (bp * 4 + ph)))
        body.flex("Right", "Thumb", 1, 8 * drive * math.sin(2 * math.pi * (bp * 4 + 0.75)))
        fk = FRETS["banjo"][prev_k] * (1 - wslide) + FRETS["banjo"][cur_k] * wslide
        binfo["fret"].solve(rel, fk)
        binfo["strap"].add()
        recs["banjo"].add()
        # tambourine
        body = tbody
        body.reset()
        stand["tamb"].pre(t, en, lean)
        stand["tamb"].legs()
        rel = body.M("Spine") @ gbody_spine_inv(tbody)
        shake, slap = 0.0, 0.0
        for th, sw_, sl in tam:
            v = hit_env(t, [th], pre=0.06, tau=0.06) * min(1.0, sw_)
            if sl:
                slap = max(slap, v)
            else:
                shake = max(shake, v)
        tinfo["tm"].solve(rel, shake, slap, t)
        recs["tamb"].add()
        # singer (lead)
        body = sbody
        body.reset()
        le = max(0.0, (env_at(LEAD_ENV, t) - 0.5) / 0.5)
        nod = hit_env(t, [x["t"] for x in C.LEAD_ON if t - 1 < x["t"] < t + 1], pre=0.05, tau=0.12)
        stand["singer"].pre(t, en, lean + 1.5 * le)
        b_ = body
        b_.rot("Neck", x=-3.0 * le)
        b_.rot("Head", x=-4.0 * le + 2.5 * nod)
        stand["singer"].legs()
        rel = body.M("Spine") @ gbody_spine_inv(sbody)
        sinfo["sg"].solve()                          # the hand stays on the stand (the stand doesn't move)
        recs["singer"].add()
        # kick
        body = kbody
        body.reset()
        kv = hit_env(t, kicks, pre=0.075, tau=0.05)
        heel = 0.0
        for hm in mains:
            d = t - hm
            if -0.2 <= d < -0.04:
                heel = max(heel, math.sin(0.5 * math.pi * (d + 0.2) / 0.16))
            elif -0.04 <= d < 0:
                heel = max(heel, -d / 0.04)
        body.rot("Spine1", x=2.0 * (0.5 + 0.5 * math.cos(2 * math.pi * C.beat_pos(t))) * en)
        body.rot("Head", x=1.5 * kv)
        toe = PP.REST_TOE + (PP.STRIKE_TOE - PP.REST_TOE) * kv
        ank = kinfo["ank"]["Right"] + Vector((0, 0, 0.03 * heel))
        body.two_bone("RightUpLeg", "RightLeg", ank, body.head("RightUpLeg") + Vector((0, -1.0, 0.7)))
        body.aim("RightFoot", (PP.board_toe(toe) - kinfo["off"] + Vector((0, 0.075, 0.035))) - body.head("RightFoot"))
        ck = clap_amount(t) * min(1.0, 0.3 + en)
        G.clap_pose(body, ck)
        recs["kick"].add()
        arm_checks(b, t, roles, ginfo, binfo, ck, FRETS["guitar"][prev_k] * (1 - wslide) + FRETS["guitar"][cur_k] * wslide,
                   FRETS["banjo"][prev_k] * (1 - wslide) + FRETS["banjo"][cur_k] * wslide)
        for role in ("guitar", "banjo", "tamb", "singer", "kick"):
            PF.check(roles[role]["body"], f"band_{role}", t, labels=LABELS[role])
            checkers[role].run(t, LABELS[role], clap_k=ck if role == "kick" else None,
                               other_ok=role != "kick")
        for role in ("guitar", "banjo", "tamb", "singer"):
            mo = roles[role]["body"].head("Head") + Vector((0, -0.105, 0.065))
            dm = (mo - mic_tip[role]).length
            k_ = f"{b}:band_{role}"
            if k_ not in PF.REPORT["mic"] or dm < PF.REPORT["mic"][k_][0]:
                PF.REPORT["mic"][k_] = (round(dm, 3), round(t, 2))
        for nm_ in ("RightLeg", "RightFoot", "RightToeBase", "LeftLeg", "LeftFoot", "LeftToeBase"):
            pt = kbody.rig.matrix_basis @ kbody.tail(nm_)
            if abs(pt.x) < PP.KICK_R + 0.02 and pt.z < PP.KICK_C.z + PP.KICK_R and pt.y < PP.BATTER_Y:
                PF._viol(f"{b}:band_kick", "leg_in_drum", t, f"{nm_} tail {tuple(round(v, 2) for v in pt)}")
        board_v.append(PP.board_rot(toe))
        beater_v.append(PP.beater_rot(PP.REST_BEATER + (PP.STRIKE_BEATER - PP.REST_BEATER) * kv))
    for info in (ginfo, binfo):
        info["strap"].write(frames, hold=freeze_t is not None)
    for role, rc in recs.items():
        if freeze_t is None:
            rc.write(frames)
        else:
            rc.hold(frames)
        PF.REG[roles[role]["rig"].name] = rc
        PF.apply_static(roles[role]["body"], PF.FINGERS)
    PF.CHECK_ON[0] = True
    if freeze_t is not None:
        board_v, beater_v = board_v[:1] * n, beater_v[:1] * n
    C.key_series(board, "rotation_euler", 0, frames, board_v)
    C.key_series(beater, "rotation_euler", 0, frames, beater_v)
    S.OBJ["perf_band"] = roles
    S.OBJ["mics"] = mics
    S.OBJ["beater"] = beater
    note = ("band holds and performances (strums on the guitar stem's onsets, banjo picking, kick pedal on "
            f"{len(kicks)} kicks, tambourine on {len(tam)} hits, lead from the vocal envelope, lean-ins on Hey!s)")
    if freeze_t is not None:
        note = f"band frozen at {freeze_t:.2f} s in their M5c holds"
    return note, roles


_SPINV = {}


def arm_checks(b, t, roles, ginfo, binfo, ck, fk_g, fk_b):
    """M5c review 2: the strumming/picking arms, the fretting hands and the kick player's claps
    (blender/arm_checks.py), on this frame's solved poses."""
    import arm_checks as AC
    if not PF.CHECK_ON[0]:
        return
    for role, info, fk, ls, lf in (("guitar", ginfo, fk_g, "guitar strumming", "guitar fretting"),
                                   ("banjo", binfo, fk_b, "banjo picking", "banjo fretting")):
        body = roles[role]["body"]
        ins = info["ins"]
        Gm = body.M("Spine") @ gbody_spine_inv(body) @ ins.G
        key = f"{b}:band_{role}"
        AC.strum_arm(body, "Right", Gm, ins.spec, ls, key, t)
        AC.fret_wrap(body, "Left", Gm, ins.spec, fk, lf, key, t)
    if ck is not None and ck >= 0.97:
        AC.clap_facing(roles["kick"]["body"], "kick player clap", f"{b}:band_kick", t)

LABELS = {"guitar": {"Left": "guitar fretting", "Right": "guitar strumming"},
          "banjo": {"Left": "banjo fretting", "Right": "banjo picking"},
          "tamb": {"Left": "tambourine slap hand", "Right": "tambourine hand"},
          "singer": {"Left": "lead on the mic stand", "Right": "lead free hand"},
          "kick": {"Left": "kick player clap", "Right": "kick player clap"}}


def obj_hold_matrix(o, body):
    """An object's figure-space matrix in the hold pose (bone parents resolved on the solved hold)."""
    if o.parent is not None and o.parent_type == "BONE":
        rig = o.parent
        pb = PF.bn(o.parent_bone)
        return rig.matrix_basis @ body.M(pb) @ Matrix.Translation((0, body.len[pb], 0)) @ \
            o.matrix_parent_inverse @ o.matrix_basis
    return o.matrix_basis.copy()


def make_checkers(b, roles, mics):
    """Collision checkers (blender/contact.py) per band member: their instrument, their mic stand, their own body."""
    import contact as CT
    R = PF.REPORT.setdefault("contact", {})
    out = {}
    inst = {"guitar": ("guitar", "Spine", None), "banjo": ("banjo", "Spine", None),
            "tamb": ("tambourine", "RightHand", "Right"), "kick": ("kick", None, None)}
    for role, d in roles.items():
        body = d["body"]
        body.reset()
        obs = list(d["obs"]) if "obs" in d else CT.body_obstacles(d["coll"], body)
        skip = {}
        if role in inst:
            nm, bone, holder = inst[role]
            o = bpy.data.objects.get(nm)
            if o is not None:
                ob = CT.mesh_obstacle(nm, "instrument", o, body, PF.bn(bone) if bone else None,
                                      mat=obj_hold_matrix(o, body), thin=role == "tamb")
                obs.append(ob)
                if holder:
                    skip[holder] = {nm}
        if role in mics:
            o = mics[role][1]
            obs.append(CT.mesh_obstacle(o.name, "mic stand", o, body))
            if role == "singer":
                skip["Left"] = {o.name}
        out[role] = CT.Checker(body, obs, R, f"{b}:band_{role}", skip=skip)
    return out


def gbody_spine_inv(body):
    """The hold pose's Spine matrix, inverted: hand targets ride the lower spine (where the instrument hangs)."""
    k = id(body)
    if k not in _SPINV:
        body.reset()
        _SPINV[k] = body.M("Spine").inverted()
    return _SPINV[k]
