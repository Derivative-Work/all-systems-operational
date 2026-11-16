"""M1b: where O18's two denial tags pin (brief rev 141: "an on-screen tag pins to that whiteboard line").

Builds O18 exactly as the M7 render does (blender/coverage_m7.py, which imports it without running its __main__),
but in place of rendering, projects one point of the whiteboard through each sub-shot's camera on every frame: the
left end of the board's denial line ("not related to cyber or AI / agents"), at mid-height. Its place on the board
texture comes from the v1.3 board (review/m1b/board-full.png, 2400x1500: the line's ink spans x 239-1314,
y 848-929). A ray cast from the camera says whether something (a head, a mic) stands in front of it.
Writes timing/o18_pins.json: per frame of O18 (from the shot's first frame), the pin in 1920x1080 pixels, or null when
it is outside the frame; outAt, the cut to O18e, where the tags go; and bottoms, the panel's distance from the frame's
bottom edge from a frame on: the lower thirds' 110 px, then 56 px in O18d's board close, where 110 would cover the
board's last line ("Full report: Nov 20").
Usage: blender -b --factory-startup --python blender/o18_pins.py -- --subs O18c,O18d --size 1920x1080
       --out <scratch dir> --log log/render_logs/m1b_o18_pins_pose_check.log
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE / "ep"))

import bpy  # noqa: E402
from bpy_extras.object_utils import world_to_camera_view  # noqa: E402

import coverage_m7 as M7  # noqa: E402

C = M7.C
TEX = (2400, 1500)
PIN_PX = (225, 888)          # just left of the opening quote, at the line's mid-height
SIZE = (1920, 1080)
SHOTS = json.loads((C.ROOT / "timing" / "shot_times.json").read_text())["shots"]
O18_START = SHOTS["O18"]["start_frame"]
SUBS = {s["id"]: s for s in C.COV["subs"]}
OUT_AT = SUBS["O18e"]["start_frame"] - O18_START
track, hidden, cams = {}, [], {}


def board_point():
    wb = C.S.OBJ["whiteboard"]
    me = wb.data
    uv = me.uv_layers.active.data
    at = {}
    for li, lp in enumerate(me.loops):
        at[tuple(round(c, 3) for c in uv[li].uv)] = wb.matrix_world @ me.vertices[lp.vertex_index].co
    u, v = PIN_PX[0] / TEX[0], 1 - PIN_PX[1] / TEX[1]
    p00, p10, p01 = at[(0.0, 0.0)], at[(1.0, 0.0)], at[(0.0, 1.0)]
    return p00 + (p10 - p00) * u + (p01 - p00) * v


def project(animation=False, write_still=False, **_):
    sc = bpy.context.scene
    cam = sc.camera
    p = board_point()
    v0 = C.build_vstart("O18")
    for f in range(sc.frame_start, sc.frame_end + 1):
        sc.frame_set(f)
        dg = bpy.context.evaluated_depsgraph_get()
        co = world_to_camera_view(sc, cam, p)
        k = f + v0 - 1 - O18_START
        inside = co.z > 0 and 0 <= co.x <= 1 and 0 <= co.y <= 1
        track[str(k)] = [round(co.x * SIZE[0], 1), round((1 - co.y) * SIZE[1], 1)] if inside else None
        o = cam.matrix_world.translation
        d = p - o
        hit, loc, _n, _i, obj, _m = sc.ray_cast(dg, o, d.normalized(), distance=d.length - 0.01)
        if inside and hit and obj and obj.name != "whiteboard":
            hidden.append([k, obj.name])
        cams[str(k)] = cam.name


class _Ops:
    def __getattr__(self, name):
        if name == "render":
            return type("R", (), {"render": staticmethod(project)})
        return getattr(bpy.ops, name)


class _Bpy:
    ops = _Ops()

    def __getattr__(self, name):
        return getattr(bpy, name)


C.bpy = _Bpy()
C.main()
out = {
    "_doc": "blender/o18_pins.py (production log): the whiteboard's denial line (board texture px "
            f"{list(PIN_PX)} of {list(TEX)}) projected through O18c's and O18d's cameras, per frame of O18 from the "
            "shot's first frame; pixels in 1920x1080; null outside the frame. hidden: frames where something stands "
            "between the camera and the pin. outAt: the cut to O18e, where the tags go. bottoms: the panel's distance "
            "from the bottom edge from that frame on (56 px in O18d, clear of the board's last line).",
    "outAt": OUT_AT,
    "bottoms": {"0": 110, str(SUBS["O18d"]["start_frame"] - O18_START): 56},
    "track": track,
    "hidden": hidden,
}
(C.ROOT / "timing" / "o18_pins.json").write_text(json.dumps(out, indent=1) + "\n")
ks = sorted(int(k) for k in track)
print(f"O18 pins: frames {ks[0]}-{ks[-1]}, {sum(v is None for v in track.values())} outside the frame, "
      f"{len(hidden)} hidden; outAt {OUT_AT}", flush=True)
for k in (ks[0], 297, 342, 431, 432, 503):
    if str(k) in track:
        print(f"  frame {k}: {track[str(k)]} ({cams[str(k)]})", flush=True)
