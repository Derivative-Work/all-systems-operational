"""M4: LTX-2.3 image-to-video clips from the picked stills (config/m4_clips.json).

Adapted from Ever Present's scripts/clips.py (90c999d, later revisions up to 9645c9b), itself from The Distillation Job.
Changed here: the still is named per clip in config/m4_clips.json (no stills.json 'kept' lookup), seeds come from
config/seeds.json by name, rows go to log/prompts/m4_fax.md, and the ComfyUI prefix is aso/. The graph and the node
settings are Ever Present's unchanged.

Graph: ComfyUI's video_ltx2_3_i2v template in API form (comfy/api/video_ltx2_3_i2v.api.json, copied unchanged from
Ever Present 90c999d; Comfy Org's comfyui-workflow-templates, MIT). Sets the still (node 269), prompt (320:319; the
prompt enhancer switch 320:328 stays off so the prompt is used as written), size (320:312 width, 320:299 height), fps
(320:300), seconds (320:301) and both noise seeds (320:276 seed, 320:277 seed + 1). The template's audio branch runs
but its audio is discarded (the song is the only audio).
Outputs assets/gen/clips/<clip>/<clip>[_<tag>]_s<seed>.mp4.
Usage: .venv/bin/python -I scripts/clips.py [clip ...] [--tag v2 --motion "..." --seeds-key m4_clips_v2]
       (ComfyUI running, one job at a time)
"""
import argparse
import copy
import datetime
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import comfy_client as cc  # noqa: E402

CFG = json.load(open("config/m4_clips.json"))
SEEDS = json.load(open("config/seeds.json"))
BASE = json.load(open("comfy/api/video_ltx2_3_i2v.api.json"))
OUT, LOG = Path("assets/gen/clips"), Path("log/prompts/m4_fax.md")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("clips", nargs="*")
    ap.add_argument("--tag", help="file tag for these takes (a revised prompt)")
    ap.add_argument("--motion", help="motion prompt instead of the config's")
    ap.add_argument("--seeds-key", help="seeds.json key instead of the config's")
    a = ap.parse_args()
    clips = a.clips or list(CFG["clips"])
    header = "## Clips: LTX-2.3 image-to-video"
    if header not in LOG.read_text():
        with open(LOG, "a") as f:
            f.write(f"\n{header}\n\nComfyUI template `video_ltx2_3_i2v` (`ltx-2.3-22b-dev-fp8` + distilled LoRA 0.5, "
                    "Gemma 3 12B fp4 encoder, x2 spatial upscaler), via `scripts/clips.py`; graph as in Ever Present. "
                    "Prompt = motion + '. ' + the clip style (`config/m4_clips.json`), prompt enhancer off. "
                    "Seeds from `config/seeds.json`; the second-stage noise seed is seed + 1.\n\n"
                    "| Clip | Still | Seed | Output | Seconds | When |\n| --- | --- | --- | --- | --- | --- |\n")
    for clip in clips:
        spec = dict(CFG["clips"][clip])
        if a.motion:
            spec["motion"] = a.motion
        tag = a.tag or spec.get("tag")
        src = Path(spec["still"])
        name = cc.upload_image(src)
        prompt = spec["motion"] + ". " + CFG["style"]
        print(f"{clip} prompt: {prompt}", flush=True)
        for seed in SEEDS[a.seeds_key or spec["seeds_key"]]:
            dest = OUT / clip / f"{clip}{'_' + tag if tag else ''}_s{seed}.mp4"
            if dest.exists():
                continue
            g = copy.deepcopy(BASE)
            g["269"]["inputs"]["image"] = name
            g["320:319"]["inputs"]["value"] = prompt
            g["320:328"]["inputs"]["value"] = False
            g["320:312"]["inputs"]["value"], g["320:299"]["inputs"]["value"] = CFG["size"]
            g["320:300"]["inputs"]["value"] = CFG["fps"]
            g["320:301"]["inputs"]["value"] = spec.get("seconds", CFG["seconds"])
            g["320:276"]["inputs"]["noise_seed"] = seed
            g["320:277"]["inputs"]["noise_seed"] = seed + 1
            g["75"]["inputs"]["filename_prefix"] = f"aso/{dest.stem}"
            outputs, secs = cc.run(g)
            vid = next(v for k, vs in outputs["75"].items() if k in ("images", "videos", "gifs") for v in vs)
            cc.download(vid, dest)
            when = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
            with open(LOG, "a") as f:
                f.write(f"| {clip}{' ' + tag if tag else ''} | `{src}` | {seed} | `{dest}` | {secs:.1f} | {when} |\n")
            print(f"{clip} seed {seed}: {dest} ({secs:.1f} s)", flush=True)


if __name__ == "__main__":
    main()
