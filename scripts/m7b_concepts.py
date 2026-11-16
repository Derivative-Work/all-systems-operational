"""M7b: park concept stills and far-plate candidates with FLUX.2 [dev] via ComfyUI (production log 40; human
interventions 18-19). Reference for agreeing the park's direction, not footage.

Adapted from scripts/stills.py (M4): config is config/m7b_park_concepts.json; seeds come from config/seeds.json
"m7b_park_concepts"; outputs go to assets/gen/stills/m7b_park/<item>/<item>_s<seed>.png; prompts verbatim in
log/prompts/m7b/<item>.txt and log/prompts/m7b_park.md (with one row per take). The graph is M4's (Ever Present's),
unchanged; the model, steps, sampler and guidance are M4's.
Usage: .venv/bin/python -I scripts/m7b_concepts.py [item ...]   (ComfyUI running on 127.0.0.1:8188)
Takes that already exist are skipped, so the same command resumes a batch.
"""
import argparse
import datetime
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import comfy_client as cc  # noqa: E402

CFG = json.load(open("config/m7b_park_concepts.json"))
SEEDS = json.load(open("config/seeds.json"))["m7b_park_concepts"]
OUT = Path("assets/gen/stills/m7b_park")
PROMPTS = Path("log/prompts/m7b")
LOG = Path("log/prompts/m7b_park.md")


def graph(prompt, seed, w, h, prefix):
    m = CFG["model"]
    return {
        "12": {"class_type": "UNETLoader", "inputs": {"unet_name": m["unet"], "weight_dtype": "default"}},
        "38": {"class_type": "CLIPLoader", "inputs": {"clip_name": m["clip"], "type": "flux2", "device": "default"}},
        "10": {"class_type": "VAELoader", "inputs": {"vae_name": m["vae"]}},
        "6": {"class_type": "CLIPTextEncode", "inputs": {"text": prompt, "clip": ["38", 0]}},
        "26": {"class_type": "FluxGuidance", "inputs": {"conditioning": ["6", 0], "guidance": m["guidance"]}},
        "22": {"class_type": "BasicGuider", "inputs": {"model": ["12", 0], "conditioning": ["26", 0]}},
        "25": {"class_type": "RandomNoise", "inputs": {"noise_seed": seed}},
        "16": {"class_type": "KSamplerSelect", "inputs": {"sampler_name": m["sampler"]}},
        "48": {"class_type": "Flux2Scheduler", "inputs": {"steps": m["steps"], "width": w, "height": h}},
        "47": {"class_type": "EmptyFlux2LatentImage", "inputs": {"width": w, "height": h, "batch_size": 1}},
        "13": {"class_type": "SamplerCustomAdvanced",
               "inputs": {"noise": ["25", 0], "guider": ["22", 0], "sampler": ["16", 0], "sigmas": ["48", 0],
                          "latent_image": ["47", 0]}},
        "8": {"class_type": "VAEDecode", "inputs": {"samples": ["13", 0], "vae": ["10", 0]}},
        "9": {"class_type": "SaveImage", "inputs": {"images": ["8", 0], "filename_prefix": prefix}},
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("items", nargs="*")
    args = ap.parse_args()
    items = args.items or list(CFG["items"])
    m = CFG["model"]
    PROMPTS.mkdir(parents=True, exist_ok=True)
    if not LOG.exists():
        LOG.write_text(
            "# M7b prompts and seeds: park concept stills and far-plate candidates\n\nAppend-only; one row per take "
            "(`scripts/m7b_concepts.py`). Prompts verbatim in `log/prompts/m7b/<item>.txt` and below. Reference for the "
            "park's direction, not footage (production log 40).\n\n"
            f"Model `{m['unet']}`, text encoder `{m['clip']}`, VAE `{m['vae']}`; {m['steps']} steps, {m['sampler']}, "
            f"guidance {m['guidance']}; ComfyUI v0.42.1, text-to-image. No negative prompt (FLUX.2 [dev] is "
            "guidance-distilled); the constraints are written into the prompt.\n\n## Prompts\n")
    for item in items:
        spec = CFG["items"][item]
        prompt = spec["subject"] + ", " + CFG["style_sets"][spec["style"]]
        pfile = PROMPTS / f"{item}.txt"
        if not pfile.exists() or pfile.read_text() != prompt + "\n":
            pfile.write_text(prompt + "\n")
            with open(LOG, "a") as f:
                f.write(f"\n### {item} ({spec['shot']})\n\n```\n{prompt}\n```\n")
        w, h = spec["size"]
        header = False
        for seed in SEEDS:
            dest = OUT / item / f"{item}_s{seed}.png"
            if dest.exists():
                continue
            outputs, secs = cc.run(graph(prompt, seed, w, h, f"aso_m7b/{item}_s{seed}"))
            cc.download(outputs["9"]["images"][0], dest)
            when = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
            with open(LOG, "a") as f:
                if not header:
                    f.write("\n| Item | Seed | Size | Output | Seconds | When |\n| --- | --- | --- | --- | --- | --- |\n")
                    header = True
                f.write(f"| {item} | {seed} | {w}×{h} | `{dest}` | {secs:.1f} | {when} |\n")
            print(f"{item} seed {seed}: {dest} ({secs:.1f} s)", flush=True)


if __name__ == "__main__":
    main()
