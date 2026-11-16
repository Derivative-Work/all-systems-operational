"""M7c: the park's view transform as a lookup table, so scripts/m7c_plate.py --compose can map the generated far plate
through its inverse and the plate reads in the render as it was generated (production log 44+).

A ramp of scene-linear grey values (2^-12 .. 2^4) as a float image, saved through the scene's colour management as
blender/aso_kit.render_settings and blender/look.exposure set it for the park's wides: AgX, config/aso_look.json's look,
exposure = config/aso_look.json exposure + config/look_m7.json rooms.park.exposure (the wides' camera offset is 0).
Out: assets/gen/tex/m7c/agx_lut.png (16-bit RGB, one row) and agx_lut.json (the linear values and the settings).
Usage: blender -b --factory-startup --python blender/m7c_agx_lut.py
"""
import json
import sys
from pathlib import Path

import bpy

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "ep"))
import gb  # noqa: E402

LOOK = json.loads((gb.ROOT / "config" / "aso_look.json").read_text())
L7 = json.loads((gb.ROOT / "config" / "look_m7.json").read_text())
OUT = gb.ROOT / "assets" / "gen" / "tex" / "m7c"
OUT.mkdir(parents=True, exist_ok=True)
sc = bpy.context.scene
sc.view_settings.view_transform = "AgX"
sc.view_settings.look = LOOK["agx_look"]
expo = LOOK["exposure"] + L7["rooms"]["park"]["exposure"]
sc.view_settings.exposure = expo
sc.view_settings.gamma = 1.0
N = 2048
vals = [2.0 ** (-12 + 16 * i / (N - 1)) for i in range(N)]
img = bpy.data.images.new("agx_lut", N, 1, float_buffer=True, alpha=False)
px = []
for v in vals:
    px += [v, v, v, 1.0]
img.pixels.foreach_set(px)
st = sc.render.image_settings
st.file_format, st.color_depth, st.color_mode = "PNG", "16", "RGB"
img.save_render(str(OUT / "agx_lut.png"), scene=sc)
(OUT / "agx_lut.json").write_text(json.dumps({
    "_doc": "blender/m7c_agx_lut.py: agx_lut.png's pixel i is linear[i] (grey) through the view transform below",
    "view_transform": "AgX", "look": LOOK["agx_look"], "exposure": expo, "display": sc.display_settings.display_device,
    "blender": bpy.app.version_string, "linear": vals}) + "\n")
print(f"AgX LUT: {N} values, exposure {expo}, look {LOOK['agx_look']} -> {OUT / 'agx_lut.png'}")
