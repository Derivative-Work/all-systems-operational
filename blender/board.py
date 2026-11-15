"""M3 lighting board: one still per key Blender shot of All Systems Operational, each from its room and state, with a
named camera ("cam_<shot>"), from the grey-box sets in blender/sets.py.

The brief's M3 (docs/plan.md): "Four Blender sets (live room, coffee shop, treehouse with deck, hilltop park) with Ever
Present's people and band, the Sandbox Rhapsody probes ... and a lighting board"; gate: "Approve the rooms and the
screens". Every shot is backlit by grey daylight or sky; the textures are the Remotion stills in assets/gen/tex
(render them first: see the M3 grey-box entry in the production log; e.g.
`npx remotion still O09-KickDrumHead assets/gen/tex/kick_head.png --frame=0 --gl=swangle`).
Overlays the brief puts on top (lower thirds, buffering spinner, captions, the O04 phone UI) are Remotion layers
composited later, not in these stills.

Usage: blender -b --factory-startup --python blender/board.py -- --out review/m3/board [--only O03,O09] [--size 1280x720] [--samples 32]
Sheet: .venv/bin/python -I scripts/board_sheet.py review/m3/board review/m3_board.jpg 3
"""
import argparse
import sys
import time
from pathlib import Path

import bpy

sys.path.insert(0, str(Path(__file__).resolve().parent))
import aso_kit as K  # noqa: E402
import sets as S  # noqa: E402
import gb  # noqa: E402

FRAMES = [
    # id, label, room, state, camera (loc, target, lens), exposure offset
    ("O03", "live room: rain on the windows, band backlit, small crowd", "live",
     dict(onair="lit", switch="on", crowd="stand"), ((2.2, 0.5, 2.0), (-0.3, 8.5, 1.5), 24), 0.0),
    ("O04", "live room: over a shoulder, phone (placeholder screen)", "live",
     dict(onair="lit", crowd="stand", phone_near=True), ("over_shoulder", "phone_holder", 30), 0.0),
    ("O07", "void: a lone server rack on chroma green", "void", {}, ((3.2, -3.6, 1.7), (0.0, 0.4, 0.35), 35), 0.0),
    ("O08", "live room: the host's silhouette at the console", "live",
     dict(onair="lit", crowd="stand"), ((6.1, 1.0, 1.55), (3.4, 5.4, 1.25), 30), 0.0),
    ("O08c", "treehouse at night: silhouettes over laptops (cutaway)", "treehouse",
     dict(night=True, band=False), ((0.05, 0.25, 2.05), (0.0, 2.7, 0.75), 24), 0.0),
    ("O09", "live room wide: full band, SESSION 503 kick, crowd joins", "live",
     dict(onair="lit", crowd="cheer"), ((0.0, 2.2, 2.9), (0.0, 8.2, 1.0), 30), 0.0),
    ("O10", "live room: Switch by the door, wired to ON AIR (lit)", "live",
     dict(onair="lit", switch="on", host="switch", crowd="stand"), ((-4.7, 1.7, 1.6), (-7.0, 3.5, 1.95), 22), 0.0),
    ("O11", "live room: everybody crowds the mics", "live",
     dict(onair="lit", crowd="push"), ((0.6, 3.2, 1.55), (0.0, 8.4, 1.7), 30), 0.0),
    ("O12", "live room: hard stop, ON AIR dark, one late clapper", "live",
     dict(onair="unlit", switch="off", crowd="stopped", clapper=True), ((2.6, 0.6, 2.0), (-2.6, 6.0, 1.5), 20), 0.4),
    ("O12c", "live room: close on the late clapper, everyone else frozen", "live",
     dict(onair="unlit", switch="off", crowd="stopped", clapper=True), ((1.3, 0.8, 1.55), (-2.4, 4.8, 1.45), 22), 0.3),
    ("O14", "coffee shop: probes, table tent, Polaroid", "cafe",
     dict(crowd="stand"), ((3.9, 3.15, 1.02), (6.0, 2.98, 1.1), 32), 0.0),
    ("O15", "coffee shop: the green probe's LED dims", "cafe",
     dict(crowd="stand", green_led=0.0), ((4.1, 2.75, 0.92), (4.8, 2.8, 0.86), 50), 0.0),
    ("O16", "coffee shop: string lights, the dark runs down every strand", "cafe",
     dict(crowd="stand", bulbs_t=0.45), ((-1.2, 0.8, 1.5), (0.8, 5.5, 3.1), 20), 0.0),
    ("O17", "coffee shop: crowd raises mugs, steam on the windows", "cafe",
     dict(crowd="mugs", side_light=False), ((0.5, 1.2, 1.9), (-0.4, 8.0, 1.5), 26), -0.6),
    ("O18", "treehouse: the band before the whiteboard", "treehouse",
     dict(), ((0.25, 0.35, 1.75), (0.05, 6.0, 1.65), 28), -1.0),
    ("O19", "treehouse: door open onto the deck in the drizzle", "treehouse",
     dict(door_open=1.0), ((2.3, 1.62, 1.6), (6.0, 1.75, 1.1), 24), -0.6),
    ("O20", "hilltop park: singalong, one umbrella, Switch on the lamp post", "park",
     dict(crowd="sing"), ((1.0, -6.5, 1.6), (0.3, 6.0, 2.0), 28), 0.0),
    ("O22", "hilltop park: emptied, one silhouette walks off", "park",
     dict(crowd="empty", walker=True), ((0.0, -7.0, 1.7), (0.5, 12.0, 2.5), 28), 0.0),
]


def over_shoulder(e):
    """O04: a camera over a phone holder's right shoulder, looking down past the phone toward the band. The phone's
    screen centre is the library collection's "phone" property (figure space)."""
    from mathutils import Vector
    import math
    ph = K.local_to_world(e, e.instance_collection["phone"])
    rz = e.rotation_euler.z - math.pi              # the person's facing, person() convention
    f = Vector((-math.sin(rz), math.cos(rz), 0))
    right = Vector((f.y, -f.x, 0))
    loc = ph - f * 0.6 + right * 0.3 + Vector((0, 0, 0.4))
    tgt = ph + f * 0.8 + Vector((0, 0, -0.05))
    return tuple(loc), tuple(tgt)


def main():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="review/m3/board")
    ap.add_argument("--only", default="")
    ap.add_argument("--size", default="1280x720")
    ap.add_argument("--samples", type=int, default=32)
    ap.add_argument("--save", default="", help="also save each built shot as <dir>/<shot>.blend (for inspection)")
    a = ap.parse_args(argv)
    out = gb.ROOT / a.out
    out.mkdir(parents=True, exist_ok=True)
    size = tuple(int(v) for v in a.size.split("x"))
    only = set(filter(None, a.only.split(",")))
    for sid, label, room, st, (loc, tgt, lens), expo in FRAMES:
        if only and sid not in only:
            continue
        t0 = time.time()
        S.build(room, st)
        K.render_settings(size, a.samples, expo)
        gb.into(None)
        if loc == "over_shoulder":
            loc, tgt = over_shoulder(S.OBJ[tgt])
        cam = gb.camera(f"cam_{sid}", loc, tgt, lens)
        cam.data.clip_end = 3000.0                   # the park skyline is 450 m off
        if room == "cafe" or sid == "O10":
            K.bloom()
        bpy.context.scene.camera = cam
        bpy.context.scene.frame_set(1)
        bpy.context.scene.render.filepath = str(out / f"{sid}.png")
        tb = time.time()
        bpy.ops.render.render(write_still=True)
        if a.save:
            Path(a.save).mkdir(parents=True, exist_ok=True)
            bpy.ops.wm.save_as_mainfile(filepath=str(Path(a.save).resolve() / f"{sid}.blend"))
        print(f"BOARD {sid} {label}: build {tb - t0:.1f} s, render {time.time() - tb:.1f} s, "
              f"{len(bpy.data.objects)} objects", flush=True)


if __name__ == "__main__":
    main()
