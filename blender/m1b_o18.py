"""M1b: O18 at the M7 look with the v1.3 whiteboard, for review before the full M7 render.

blender/coverage_m7.py (imported, its __main__ not run), with one change after each O18 build: the whiteboard shows
the v1.3 board sequence (scripts/m1b_remotion.sh: assets/gen/tex/m1b/M7-O18-Whiteboard/frames, 1800x1125) instead of
M5's movie, mapped the way blender/look.py maps the M7b screens (build frame 1 shows file 000). The full M7 render
takes the same texture once blender/look.py carries this swap.
Usage: blender -b --factory-startup --python blender/m1b_o18.py -- --out renders/m1b/raw --still --at 0.5
       --subs O18c,O18d --size 1920x1080 --log log/render_logs/m1b_o18_pose_check.log   (coverage.py's options)
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE / "ep"))

import bpy  # noqa: E402

import coverage_m7 as M7  # noqa: E402

C = M7.C
BOARD = C.ROOT / "assets/gen/tex/m1b/M7-O18-Whiteboard/frames"
_layers = C.layers


def _layers_m1b(b, n, room, notes):
    _layers(b, n, room, notes)
    if b != "O18":
        return
    files = sorted(BOARD.glob("*.jpeg"))
    if not files:
        raise FileNotFoundError(f"{BOARD}: run scripts/m1b_remotion.sh first")
    wb = C.S.OBJ["whiteboard"]
    node = next(nd for nd in wb.active_material.node_tree.nodes if nd.type == "TEX_IMAGE")
    img = bpy.data.images.load(str(files[0]), check_existing=True)
    img.source = "SEQUENCE"
    node.image = img
    iu = node.image_user
    iu.frame_duration, iu.frame_start, iu.frame_offset = len(files), 1, -1
    iu.use_auto_refresh, iu.use_cyclic = True, False
    notes.append(f"M1b: the v1.3 whiteboard ({len(files)} frames, {img.size[0]}x{img.size[1]})")


C.layers = _layers_m1b

if __name__ == "__main__":
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    if "--out" in argv:
        (C.ROOT / argv[argv.index("--out") + 1]).mkdir(parents=True, exist_ok=True)
    C.main()
    M7.CM.write_report()
