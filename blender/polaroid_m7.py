"""M7: the photo in the cafe's Polaroid (O14; brief: "a Polaroid of the band in this same room, lit warm, captioned
'Wed 11/11'"). Rendered, not generated: the M7 cafe (blender/look.py) at O17's first Hey! (mugs up), the band and the
crowd's backs from behind the crowd, the windows a warmer late-afternoon grey and the string lights up, square.
Then scripts/grade.py --look instant, and Remotion's O14-Polaroid frames it with the "Wed 11/11" caption
(remotion/src/components/Textures.tsx, photo prop): assets/gen/tex/polaroid_m7.png, which blender/look.py puts on the
wall when it exists. M3's placeholder (assets/gen/tex/polaroid.png) is untouched.
Usage: blender -b --factory-startup --python blender/polaroid_m7.py -- [--out remotion/public/gen/polaroid_photo_m7_raw.png]
       [--size 1080] [--samples 64]
"""
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE / "ep"))
argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
sys.argv = sys.argv[:sys.argv.index("--")] if "--" in sys.argv else sys.argv     # coverage_m7 parses its own options

import bpy  # noqa: E402
import coverage_m7 as CM7  # noqa: E402
import gb  # noqa: E402
import look as LK  # noqa: E402

C = CM7.C
A = C.A
K = C.K


def opt(name, default):
    return type(default)(argv[argv.index(name) + 1]) if name in argv else default


def main():
    out = C.ROOT / opt("--out", "remotion/public/gen/polaroid_photo_m7_raw.png")
    size = opt("--size", 1080)
    b = "O17"
    n = A.nframes(b)
    keys, expo, notes = A.shot(b, n)
    C.layers(b, n, "cafe", notes)
    K.render_settings((size, size), 64, 0.0)
    LK.SAMPLES[0] = opt("--samples", 64)
    C.SETTINGS(b, "cafe")
    sc = bpy.context.scene
    sc.render.fps = C.FPS
    # Wed 11/11, lit warm: the windows a warmer, lower late-afternoon grey; the string lights up
    for m in bpy.data.materials:
        if not m.get("window"):
            continue
        nt = m.node_tree
        em = next(nd for nd in nt.nodes if nd.type == "EMISSION")
        em.inputs["Strength"].default_value *= 0.75
        src = em.inputs["Color"].links[0].from_socket
        mx = nt.nodes.new("ShaderNodeMix")
        mx.data_type, mx.blend_type = "RGBA", "MULTIPLY"
        mx.inputs[0].default_value = 1.0
        nt.links.new(src, mx.inputs[6])
        mx.inputs[7].default_value = gb.lin("#ffd9a8")
        nt.links.new(mx.outputs[2], em.inputs["Color"])
    for o in bpy.data.objects:
        if o.type == "LIGHT" and o.name.startswith(("strand_light", "hub_light")):
            o.data.energy *= 2.5
        if o.type == "LIGHT" and o.name.startswith("wl_"):
            o.data.color = gb.lin("#ffe2bd")[:3]
    bm = bpy.data.materials.get("string_bulb")
    for nd in bm.node_tree.nodes:
        if nd.type == "MATH" and nd.operation == "MULTIPLY":
            nd.inputs[1].default_value *= 1.4
    gb.into(None)
    cam = gb.camera("cam_polaroid", (0.45, 3.7, 1.95), (-0.45, 7.7, 1.3), 27)
    cam.data.clip_end = 100.0
    cam.data.dof.use_dof = True
    cam.data.dof.aperture_fstop = 4.0
    cam.data.dof.focus_distance = 3.9
    sc.camera = cam
    sc.frame_set(A.mark("O17", 0) + 2)
    sc.view_settings.exposure = LK.exposure({}, "cafe", 0.0, {}) + 0.5
    sc.render.image_settings.file_format = "PNG"
    sc.render.filepath = str(out)
    out.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.render.render(write_still=True)
    print(f"polaroid photo: {out}", flush=True)


main()
