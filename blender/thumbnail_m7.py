"""Thumbnail stills of the cafe's string lights, lit so the web reads (human interventions 43: "You might need to make
new renders with more light for the wire to be visible"). blender/coverage_m7.py's O16 build and O16a camera,
unchanged, then for each requested frame and variant: the strands thickened (a displace along their normals) and a
soft fill from below the camera toward the hub, so the wires show against the ceiling. Thumbnail only: the video's
frames are not touched.
Usage: blender -b --factory-startup --python blender/thumbnail_m7.py -- --out <dir> --still --subs O16a
       --size 3840x2160 --log <dir>/pose.log --web-frames 21,22,24 --web-variants "ev=1.5,bulb=0.35,prac=4/wirecol=#9a948c"
       -> <dir>/O16a_f<frame>_v<k>.png, one per variant (plus coverage's own still, <dir>/O16a.png)
       --web-variants, "/" between variants, each "key=value,...": fill (W, a soft disk below the camera aimed at the
       hub), wire (metres added to the strands' 4 mm radius; default 0.006), ev (stops added to the exposure), bulb
       (the bulbs' emission times this), prac (the strands' and hub's point lights times this), wirecol (the strands'
       colour; default the cable's #141416)
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))


def _opt(name, default=None):
    if name in sys.argv:
        i = sys.argv.index(name)
        v = sys.argv[i + 1]
        del sys.argv[i:i + 2]
        return v
    return default


FRAMES = [int(x) for x in _opt("--web-frames", "22").split(",")]
VARIANTS = [dict(kv.split("=") for kv in v.split(",") if kv) for v in _opt("--web-variants", "wire=0.006").split("/")]

import bpy  # noqa: E402
from mathutils import Vector  # noqa: E402

import coverage_m7 as M7  # noqa: E402  (its __main__ block doesn't run on import)
import sets as SETS  # noqa: E402
import gb  # noqa: E402

C = M7.C
_exposure = C.EXPOSURE


def web_stills(s, e):
    sc = bpy.context.scene
    out = C.ROOT / C_ARGS["out"]
    wires = bpy.data.objects["string_wires"]
    cable = wires.data.materials[0]
    disp = wires.modifiers.new("thumb_thicker", "DISPLACE")
    disp.direction, disp.mid_level = "NORMAL", 0.0
    mul = next(n for n in bpy.data.materials["string_bulb"].node_tree.nodes if n.type == "MATH")
    bulb0 = mul.inputs[1].default_value
    pracs = [(o, o.data.energy) for o in bpy.data.objects if o.type == "LIGHT" and
             (o.name.startswith("strand_light") or o.name == "hub_light")]
    cam = sc.camera.matrix_world.translation.copy()
    hub = Vector(SETS.CAFE["hub"])
    ld = bpy.data.lights.new("thumb_fill", "AREA")
    ld.shape, ld.size, ld.color = "DISK", 3.0, (1.0, 0.9, 0.78)
    lo = bpy.data.objects.new("thumb_fill", ld)
    sc.collection.objects.link(lo)
    lo.location = cam - Vector((0, 0, 0.4))
    lo.rotation_euler = (hub - lo.location).to_track_quat("-Z", "Y").to_euler()
    for f in FRAMES:
        sc.frame_set(f)
        for k, v in enumerate(VARIANTS):
            fill = float(v.get("fill", 0))
            ld.energy, lo.hide_render = fill, fill <= 0
            disp.strength = float(v.get("wire", 0.006))
            sc.view_settings.exposure = e + float(v.get("ev", 0))
            mul.inputs[1].default_value = bulb0 * float(v.get("bulb", 1))
            for o, en in pracs:
                o.data.energy = en * float(v.get("prac", 1))
            if v.get("wirecol"):
                m = cable.copy()
                m.name = f"thumb_cable_{k}"
                for n in m.node_tree.nodes:
                    if n.type == "BSDF_PRINCIPLED":
                        n.inputs["Base Color"].default_value = gb.lin(v["wirecol"])
                wires.data.materials[0] = m
            else:
                wires.data.materials[0] = cable
            sc.render.image_settings.file_format = "PNG"
            sc.render.filepath = str(out / f"{s['id']}_f{f}_v{k}.png")
            bpy.ops.render.render(write_still=True)
            print(f"THUMB {s['id']} frame {f} v{k} {v} -> {sc.render.filepath}", flush=True)
    bpy.data.objects.remove(lo)
    wires.modifiers.remove(disp)
    wires.data.materials[0] = cable
    mul.inputs[1].default_value = bulb0
    for o, en in pracs:
        o.data.energy = en
    sc.view_settings.exposure = e


def exposure(s, room, expo, c_):
    e = _exposure(s, room, expo, c_)
    if s["id"] == "O16a":
        web_stills(s, e)
    return e


C.EXPOSURE = exposure

if __name__ == "__main__":
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    C_ARGS = {"out": argv[argv.index("--out") + 1]}
    (C.ROOT / C_ARGS["out"]).mkdir(parents=True, exist_ok=True)
    C.main()
    M7.CM.write_report()
