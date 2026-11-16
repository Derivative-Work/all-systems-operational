"""M5c review: close-up check stills of the rebuilt acoustic guitar and banjo (blender/instruments.py), alone and on
their players, after Ever Present's guitar check (../ever-present/review/m7/rerender/guitarcheck.py: front, head,
side). Built as blender/coverage_m5c.py builds O09 (the live room, then the band's holds and performances), at one
frame of bar 30 (chorus 1, the performance sheet's bar); each player alone in frame (everyone else hidden), lit from
the front for inspection.
Views per instrument: front alone (the player hidden), side alone, headstock, front on the player, the fretting
hand, the strumming / picking hand, the strap from behind. Also a crowd clapper at the clap, close.
Usage: blender -b --factory-startup --python blender/instrument_sheet.py -- [--out renders/m5c2/instruments]
       [--frame 452] [--size 900x900]
"""
import argparse
import json
import sys
from pathlib import Path

import bpy
from mathutils import Vector

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE / "ep"))
import coverage_m5c  # noqa: E402,F401  (patches coverage for M5c)
import coverage as C  # noqa: E402
import aso_kit as K  # noqa: E402
import gb  # noqa: E402
import perf as PF  # noqa: E402
import perf_band as PB  # noqa: E402
import perf_crowd as PC  # noqa: E402
import sets as S  # noqa: E402

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
ap = argparse.ArgumentParser()
ap.add_argument("--out", default="renders/m5c2/instruments")
ap.add_argument("--frame", type=int, default=452)
ap.add_argument("--size", default="900x900")
ap.add_argument("--n", type=int, default=0, help="frames to solve (0: up to --frame + 2)")
ap.add_argument("--only", default="")
ap.add_argument("--palms", action="store_true", help="test only: paint the palm sides (blender/palm_test.py)")
a = ap.parse_args(argv)
out = C.ROOT / a.out
out.mkdir(parents=True, exist_ok=True)
b = "O09"
n = a.n or a.frame + 2
keys, expo, notes = C.A.shot(b, n)
PF.BUILD[0] = b
note, roles = PB.perform(b, n)
notes.append(note)
notes.append(PC.perform(b, n, "live"))
print("; ".join(notes), flush=True)
W, H = (int(v) for v in a.size.split("x"))
K.render_settings((W, H), 32, 0.0)
sc = bpy.context.scene
gb.into(None)
K.world("#8a8f94", 0.6)
for o in bpy.data.objects:
    if o.type == "LIGHT":
        o.data.energy *= 0.5
sc.frame_set(a.frame)
band = S.OBJ["band"]
if a.palms:
    import palm_test
    for e in list(band.values()) + PC.instances():
        palm_test.paint_palms(e.instance_collection)
allp = [o for o in bpy.data.objects if o.type == "EMPTY" and o.instance_type == "COLLECTION"]
man = {"frame": a.frame, "t": C.song_t(b, a.frame), "tiles": []}


def solo(e):
    for o in allp:
        o.hide_render = o is not e


def shoot(tag, e, loc_f, tgt_f, lens, hide_person=False, label=""):
    """Camera and target in the performer's figure frame (armature points through the rig's basis)."""
    mw = e.matrix_world
    loc, tgt = mw @ Vector(loc_f), mw @ Vector(tgt_f)
    cam = gb.camera(f"chk_{tag}", tuple(loc), tuple(tgt), lens)
    cam.data.clip_start = 0.02
    lt = K.area(f"chk_fill_{tag}", tuple(loc + Vector((0, 0, 0.6))), tuple(tgt), 120, 1.5, "#ffffff")
    sc.camera = cam
    sc.view_settings.exposure = K.LOOK["exposure"] + 0.4
    hidden = []
    if hide_person:
        coll = e.instance_collection
        for o in coll.objects:
            if o.type == "MESH" and not o.name.startswith(("guitar", "banjo")) and not o.hide_render:
                o.hide_render = True
                hidden.append(o)
    p = out / f"{tag}.png"
    sc.render.filepath = str(p)
    bpy.ops.render.render(write_still=True)
    for o in hidden:
        o.hide_render = False
    lt.hide_render = True
    man["tiles"].append({"file": str(p.relative_to(C.ROOT)), "tag": tag, "label": label or tag})
    print("still", tag, flush=True)


only = set(filter(None, a.only.split(",")))
for role in ("guitar", "banjo"):
    if only and role not in only:
        continue
    e = band[role]
    solo(e)
    info = roles[role]
    body = PF.rec_pose(PF.REG[info["rig"].name], a.frame - 1)
    mb = info["rig"].matrix_basis
    obj = bpy.data.objects[role]
    # the instrument's frame now (it rides the lower spine): through its evaluated world matrix
    bpy.context.view_layer.update()
    from perf_band import gbody_spine_inv
    rel = body.M("Spine") @ gbody_spine_inv(body)
    I = roles[role]["info"]["ins"]

    def P(v):
        return mb @ (rel @ I.P(v))

    def D(v):
        return (mb.to_3x3() @ rel.to_3x3() @ I.D(v)).normalized()

    sp = I.spec
    N = sp.neck
    mid = P(((N.nut + (sp.points["hole"].x if role == "guitar" else sp.points["pot"].x)) / 2, 0, 0))
    ctr = P((sp.points["hole"].x if role == "guitar" else sp.points["pot"].x, 0, 0))
    out_ = D((0, 0, 1))
    up_ = D((0, 1, 0))
    shoot(f"{role}_front_alone", e, mid + out_ * 1.6 + up_ * 0.1, mid, 35, True, f"{role}: front, alone")
    shoot(f"{role}_side_alone", e, ctr + D((-1, 0, 0)) * 1.1 + out_ * 0.35 + Vector((0, 0, 0.25)), ctr + D((1, 0, 0)) * 0.2,
          35, True, f"{role}: from the tail, alone")
    hs = P((N.nut + 0.09, 0, 0))
    shoot(f"{role}_headstock", e, hs + out_ * 0.45 + up_ * 0.05 + D((1, 0, 0)) * 0.05, hs, 50, False,
          f"{role}: headstock")
    shoot(f"{role}_on_player", e, Vector((0.35, -2.3, 1.25)), Vector((0.05, -0.1, 1.05)), 50, False,
          f"{role}: on the player")
    fh = mb @ body.tail("LeftHand")
    shoot(f"{role}_fret_hand", e, fh + out_ * 0.42 + up_ * 0.12 + Vector((0.08, 0, 0.04)), fh, 50, False,
          f"{role}: fretting hand")
    shoot(f"{role}_fret_hand_under", e, fh + out_ * 0.3 - up_ * 0.25 + Vector((0.1, 0, -0.05)), fh, 50, False,
          f"{role}: fretting hand from below")
    shoot(f"{role}_fret_hand_along", e, fh + D((1, 0, 0)) * 0.4 + out_ * 0.06 + up_ * 0.03, fh, 45, False,
          f"{role}: fretting hand, along the neck")
    ph = mb @ body.tail("RightHand")
    shoot(f"{role}_pick_hand", e, ph + out_ * 0.45 + up_ * 0.25 + D((-1, 0, 0)) * 0.12, ph, 50, False,
          f"{role}: {'strumming' if role == 'guitar' else 'picking'} hand")
    shoot(f"{role}_pick_hand_side", e, ph + D((-1, 0, 0)) * 0.45 + up_ * 0.1 + out_ * 0.15, ph, 50, False,
          f"{role}: forearm on the {'edge' if role == 'guitar' else 'armrest'}")
    shoot(f"{role}_strap_back", e, Vector((-0.6, 1.9, 1.5)), Vector((0.0, 0.0, 1.15)), 45, False,
          f"{role}: strap from behind")
# the other hands: tambourine, the lead's grip on the stand, the kick player's and a crowd clapper's clap
if not only or "others" in only:
    import perf_grips as G
    for role in ("tamb", "singer", "kick"):
        e = band[role]
        solo(e)
        body = PF.rec_pose(PF.REG[roles[role]["rig"].name], a.frame - 1)
        mb = roles[role]["rig"].matrix_basis
        ch = mb @ ((body.tail("LeftHand") + body.tail("RightHand")) / 2)
        if role == "singer":
            ch = mb @ body.tail("LeftHand")
        shoot(f"{role}_hands_front", e, ch + Vector((0.12, -0.55, 0.12)), ch, 50, False, f"{role}: hands, front")
        shoot(f"{role}_hands_side", e, ch + Vector((0.55, -0.15, 0.08)), ch, 50, False, f"{role}: hands, from the left")
        shoot(f"{role}_hands_top", e, ch + Vector((-0.1, -0.25, 0.5)), ch, 50, False, f"{role}: hands, from above")
    clapper = next((x for x in PC.instances() if x.get("pose") == "clap"), None)
    if clapper is not None:
        rig = next(o for o in clapper.instance_collection.objects if o.type == "ARMATURE")
        rec = PF.REG[rig.name]
        # the frame nearest the clap (both hands closest) within a beat of --frame
        best = None
        for f in range(max(1, a.frame - 15), min(n, a.frame + 15) + 1):
            body = PF.rec_pose(rec, f - 1)
            g = G.palm_gap(body)
            if best is None or g < best[0]:
                best = (g, f)
        sc.frame_set(best[1])
        body = PF.rec_pose(rec, best[1] - 1)
        solo(clapper)
        mb = rig.matrix_basis
        ch = mb @ ((body.tail("LeftHand") + body.tail("RightHand")) / 2)
        man["clap_frame"] = best[1]
        shoot("crowd_clap_front", clapper, ch + Vector((0.1, -0.5, 0.1)), ch, 50, False, "crowd clapper at the clap, front")
        shoot("crowd_clap_side", clapper, ch + Vector((0.5, -0.12, 0.06)), ch, 50, False, "crowd clapper at the clap, side")
        shoot("crowd_clap_body", clapper, ch + Vector((0.3, -1.6, 0.1)), ch + Vector((0, 0, -0.1)), 50, False,
              "crowd clapper at the clap")
(out / "sheet.json").write_text(json.dumps(man, indent=1))
print("wrote", out / "sheet.json")
