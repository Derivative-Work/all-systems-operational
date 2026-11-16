"""M7: the final look over the M5c3 cut. blender/coverage_m5c.py (the M5c3 performances, cameras, cut and checks,
unchanged) with blender/look.py enabled: materials, set dressing, light, haze, render settings (plan M7; the M7a look
board, production log 30+). The grade is applied afterwards to the frames (scripts/grade.py).
Seeds: as M5c, plus gb.rng("m7_*") in blender/look.py; Cycles' seed is config/seeds.json main.
Usage: blender -b --factory-startup --python blender/coverage_m7.py -- --out renders/m7a/raw --still --subs O03a,O09j
       --size 1920x1080 [--engine eevee|cycles] [--samples N] [--log log/render_logs/m7a_pose_check.log]
       Without --still: JPEG sequences per sub-shot (coverage.py's options: --only, --subs, --size, --at ...);
       --frames N renders only each sub-shot's first N frames (timing runs).
       M7d comparison renders only: --wides-z 2.4 (the eye-level park wides raised, tilt kept), --m7d-off brow
       (an M7d part off). Always pass --log: without it the pose report goes to log/render_logs/m7a_pose_check.log.
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE / "ep"))


def _opt(name, default=None):
    if name in sys.argv:
        i = sys.argv.index(name)
        v = sys.argv[i + 1]
        del sys.argv[i:i + 2]
        return v
    return default


ENGINE = _opt("--engine", "eevee")
LOGP = _opt("--log", "log/render_logs/m7a_pose_check.log")
WIDES_Z = _opt("--wides-z")            # M7d comparison renders only: the eye-level park wides at this camera height
M7D_OFF = _opt("--m7d-off", "")        # M7d comparison renders only: M7d parts switched off (e.g. brow)

import coverage_m5c as CM  # noqa: E402  (patches coverage.py with the M5c3 performances; its __main__ doesn't run)
import look as LK  # noqa: E402

C = CM.C
CM.LOG = C.ROOT / LOGP
LK.enable(ENGINE)
C.haze = LK.haze
C.SETTINGS = LK.settings
C.EXPOSURE = LK.exposure
# M7b (production log 37+): steam as rising wisps, the cameras' fixes (O04a follows the phone, O18e racks from the
# ringing phone, steam cards face the camera), and the shaders' clock keyed after each build's layers
C.steam = LK.steam
C.CAMERA_HOOK = LK.camera_hook
_layers_m5c = C.layers


def _layers_m7(b, n, room, notes):
    _layers_m5c(b, n, room, notes)
    LK.after_layers(b, n, room, notes)


C.layers = _layers_m7

if LK.M7C:
    # M7c (production log 44+; decisions 35+): the rebuilt park's cameras (config/look_m7.json m7c.cameras replace the
    # park presets; O19b's M5 keys are replaced by its rise up the back slope over the new crest), its fog curtains in
    # place of M5b's fog cards, and the sub-shots a generated clip replaces in the M7 assembly (O22d: not rendered)
    import park_m7c as PK
    for _part in filter(None, M7D_OFF.split(",")):
        PK.M7D[_part]["on"] = False
    if WIDES_Z:
        # M7d (weak point 5; decisions 39.2): the eye-level wides raised to WIDES_Z with their tilt kept (the target
        # rises by the same amount), for the options sheet; the park's tree placement still reads the approved camera
        for _name in LK.CFG["m7d"]["wides_options"]["presets"]:
            _c = LK.CFG["m7c"]["cameras"][_name]
            _dz = float(WIDES_Z) - _c["loc"][2]
            _c["loc"] = [_c["loc"][0], _c["loc"][1], float(WIDES_Z)]
            _c["target"] = [_c["target"][0], _c["target"][1], _c["target"][2] + _dz]
    for _name, _over in LK.CFG["m7c"]["cameras"].items():
        if _name in C.COV["cameras"]["park"]:
            _c = C.COV["cameras"]["park"][_name]
            _c.pop("board", None)
            _c.update(_over)
    for _s in C.COV["subs"]:
        if _s["id"] in LK.CFG["m7c"]["clip_subs"]:
            _s["source"] = "clip"
    C.fog_cards = PK.fog_cards
    _shot = C.A.shot

    def _shot_m7c(sid, n):
        keys, expo, notes = _shot(sid, n)
        if sid == "O19b":
            _sub = next(x for x in C.COV["subs"] if x["id"] == "O19b")
            keys = PK.o19b_keys(n, _sub["frames"] + _sub.get("xfade_in", 0))
            notes.append("M7c: O19b rises up the back slope over the crest")
        return keys, expo, notes
    C.A.shot = _shot_m7c

if LK.M7D:
    # M7d (production log 50+; decisions 42): every close_banjo re-aimed so the head reads in three-quarter view
    # (blender/look.py banjo_three_quarter; the cut, lens, move and drift stay coverage.make_camera's)
    _cam_base_m7c = C.cam_base

    def _cam_base_m7d(sub, c, b):
        base = _cam_base_m7c(sub, c, b)
        if sub.get("camera") in LK.CFG["m7d"]["closes"]["banjo"]["cams"]:
            base = LK.banjo_three_quarter(sub, b, base)
        return base
    C.cam_base = _cam_base_m7d

FRAMES = _opt("--frames")              # timing runs: only the first N frames of each sub-shot's sequence
if FRAMES:
    _lr = C.local_range

    def _local_range(s, b, n=int(FRAMES)):
        f0, f1 = _lr(s, b)
        return f0, min(f1, f0 + n)
    C.local_range = _local_range

if __name__ == "__main__":
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    if "--samples" in argv:
        LK.SAMPLES[0] = int(argv[argv.index("--samples") + 1])
    if "--out" in argv:
        (C.ROOT / argv[argv.index("--out") + 1]).mkdir(parents=True, exist_ok=True)
    C.main()
    CM.write_report()
