"""M7d: the far plate's L1 seam (human interventions 23, weak point 2; decisions 40; config/m7d_plate.json).

At the L1 seam of the approved M7c panorama (about 22 degrees left of centre, columns near 2560) a hill fades into a
vertical bank of fog. This inpaints a band across the seam with FLUX.2 [dev] (the M7c outpainting graph: VAEEncode,
SetLatentNoiseMask, DifferentialDiffusion, so the soft mask's value is the local denoise strength) on a 2048x1440 crop
of the panorama, then pastes the pick back through the same mask, so the approved panorama is unchanged outside it,
and rebuilds the Blender texture the way M7c did (scripts/m7c_plate.py backdrop: the inverse view transform, the top
faded into the sky, the bottom into the valley fog).

  --seam     the takes: assets/gen/stills/m7d_park/seam/seam_s<seed>.png (2048x1440, the crop), with the canvas
             and the mask beside them; seeds config/seeds.json m7d_seam; one take per seed, existing takes skipped
  --compose  the pick (config/m7d_plate.json pick) into the approved panorama (approved_pano, the M7c file moved to
             archive/) -> assets/gen/stills/m7c_park/pano/pano.png; checks that nothing outside the mask changed;
             then the Blender texture assets/gen/tex/m7c/park_backdrop.png and .json (scripts/m7c_plate.py backdrop)
  --sheet    review/m7d_plates.jpg: the seam before and after (the band and 1:1 crops), the mask, every take with
             its verdict (config/m7d_plate.json review)
Prompts verbatim in log/prompts/m7d/seam.txt and log/prompts/m7d_seam.md (one row per take). ComfyUI on
127.0.0.1:8188, one job at a time.
Usage: .venv/bin/python -I scripts/m7d_plate.py --seam | --compose | --sheet
"""
import argparse
import datetime
import json
import sys
from pathlib import Path

import cv2
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

CFG = json.loads((ROOT / "config/m7d_plate.json").read_text())
C7 = json.loads((ROOT / "config/m7c_plate.json").read_text())
SEEDS = json.loads((ROOT / "config/seeds.json").read_text())
OUT = ROOT / "assets/gen/stills/m7d_park/seam"
PANO = ROOT / "assets/gen/stills/m7c_park/pano/pano.png"
PROMPTS = ROOT / "log/prompts/m7d"
LOG = ROOT / "log/prompts/m7d_seam.md"
H = 1440


def approved():
    """The approved M7c panorama: the archived copy once --compose has replaced it, else the live file."""
    a = ROOT / CFG["approved_pano"]
    return cv2.imread(str(a if a.exists() else PANO))


def mask_full(w=7680):
    """The soft mask over the whole panorama (float 0..1)."""
    M = CFG["mask"]
    x = np.arange(w, dtype=np.float32) + 0.5
    y = np.arange(H, dtype=np.float32) + 0.5

    def ss(t):
        t = np.clip(t, 0, 1)
        return t * t * (3 - 2 * t)
    mx = np.minimum(ss((x - (M["c0"] - M["feather_x"])) / M["feather_x"]), ss(((M["c1"] + M["feather_x"]) - x) / M["feather_x"]))
    my = np.minimum(ss((y - (M["r0"] - M["feather_y"])) / M["feather_y"]), ss(((M["r1"] + M["feather_y"]) - y) / M["feather_y"]))
    return M["core"] * my[:, None] * mx[None, :]


def prompt():
    return CFG["subject"] + ", " + C7["style"]


def log_header():
    if LOG.exists():
        return
    m = C7["model"]
    a, b = CFG["crop"]
    M = CFG["mask"]
    LOG.write_text(
        "# M7d prompts and seeds: the far plate's L1 seam\n\nAppend-only; one row per take (`scripts/m7d_plate.py "
        "--seam`). The prompt verbatim in `log/prompts/m7d/seam.txt` and below.\n\n"
        f"Inpaint: model `{m['unet']}`, text encoder `{m['clip']}`, VAE `{m['vae']}`; {m['steps']} steps, "
        f"{m['sampler']}, guidance {m['guidance']}; ComfyUI v0.42.1, the M7c outpainting graph: the canvas "
        "VAE-encoded, SetLatentNoiseMask with the mask, DifferentialDiffusion on the model (the mask value is the "
        "local denoise strength), Flux2Scheduler, SamplerCustomAdvanced. No negative prompt (FLUX.2 [dev] is "
        "guidance-distilled); the constraints are written into the prompt (M7c's style).\n\n"
        f"Canvas: columns {a}-{b} of the approved M7c panorama (2048x1440). Mask (panorama coordinates): "
        f"strength {M['core']} over columns {M['c0']}-{M['c1']} and rows {M['r0']}-{M['r1']}, a smoothstep to 0 "
        f"over {M['feather_x']} px to the sides and {M['feather_y']} px above and below. The pick is pasted back "
        "through the same mask, so nothing outside it changes.\n")


def log_prompt(key, label, text):
    PROMPTS.mkdir(parents=True, exist_ok=True)
    pf = PROMPTS / f"{key}.txt"
    if not pf.exists() or pf.read_text() != text + "\n":
        pf.write_text(text + "\n")
        with open(LOG, "a") as f:
            f.write(f"\n### {key} ({label})\n\n```\n{text}\n```\n\n| Take | Seed | Output | Seconds | When |\n"
                    "| --- | --- | --- | --- | --- |\n")


def log_row(take, seed, dest, secs):
    when = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
    with open(LOG, "a") as f:
        f.write(f"| {take} | {seed} | `{dest.relative_to(ROOT)}` | {secs:.1f} | {when} |\n")


def graph(text, seed, canvas_name, mask_name, prefix, w, h):
    m = C7["model"]
    return {
        "12": {"class_type": "UNETLoader", "inputs": {"unet_name": m["unet"], "weight_dtype": "default"}},
        "38": {"class_type": "CLIPLoader", "inputs": {"clip_name": m["clip"], "type": "flux2", "device": "default"}},
        "10": {"class_type": "VAELoader", "inputs": {"vae_name": m["vae"]}},
        "50": {"class_type": "DifferentialDiffusion", "inputs": {"model": ["12", 0]}},
        "6": {"class_type": "CLIPTextEncode", "inputs": {"text": text, "clip": ["38", 0]}},
        "26": {"class_type": "FluxGuidance", "inputs": {"conditioning": ["6", 0], "guidance": m["guidance"]}},
        "60": {"class_type": "LoadImage", "inputs": {"image": canvas_name}},
        "61": {"class_type": "LoadImageMask", "inputs": {"image": mask_name, "channel": "red"}},
        "62": {"class_type": "VAEEncode", "inputs": {"pixels": ["60", 0], "vae": ["10", 0]}},
        "63": {"class_type": "SetLatentNoiseMask", "inputs": {"samples": ["62", 0], "mask": ["61", 0]}},
        "22": {"class_type": "BasicGuider", "inputs": {"model": ["50", 0], "conditioning": ["26", 0]}},
        "25": {"class_type": "RandomNoise", "inputs": {"noise_seed": seed}},
        "16": {"class_type": "KSamplerSelect", "inputs": {"sampler_name": m["sampler"]}},
        "48": {"class_type": "Flux2Scheduler", "inputs": {"steps": m["steps"], "width": w, "height": h}},
        "13": {"class_type": "SamplerCustomAdvanced",
               "inputs": {"noise": ["25", 0], "guider": ["22", 0], "sampler": ["16", 0], "sigmas": ["48", 0],
                          "latent_image": ["63", 0]}},
        "8": {"class_type": "VAEDecode", "inputs": {"samples": ["13", 0], "vae": ["10", 0]}},
        "9": {"class_type": "SaveImage", "inputs": {"images": ["8", 0], "filename_prefix": prefix}},
    }


def seam():
    import comfy_client as cc
    log_header()
    text = prompt()
    log_prompt("seam", "inpaint across the L1 seam", text)
    a, b = CFG["crop"]
    pano = approved()
    can = pano[:, a:b]
    m = (np.clip(mask_full()[:, a:b], 0, 1) * 255 + 0.5).astype(np.uint8)
    OUT.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(OUT / "canvas_seam.png"), can)
    cv2.imwrite(str(OUT / "mask_seam.png"), m)
    cn, mn = cc.upload_image(OUT / "canvas_seam.png"), cc.upload_image(OUT / "mask_seam.png")
    for seed in SEEDS[CFG["seeds_key"]]:
        dest = OUT / f"seam_s{seed}.png"
        if dest.exists():
            continue
        outputs, secs = cc.run(graph(text, seed, cn, mn, f"aso_m7d/seam_s{seed}", b - a, H))
        cc.download(outputs["9"]["images"][0], dest)
        log_row("seam", seed, dest, secs)
        print(f"seam seed {seed}: {dest} ({secs:.1f} s)", flush=True)


def merged(take, pano=None):
    """The approved panorama with a take pasted back through the mask (float32 BGR)."""
    pano = approved() if pano is None else pano
    a, b = CFG["crop"]
    g = cv2.imread(str(OUT / f"{take}.png")).astype(np.float32)
    out = pano.astype(np.float32).copy()
    w = mask_full()[:, a:b, None]
    out[:, a:b] = (1 - w) * out[:, a:b] + w * g
    return out


def compose():
    pick = CFG.get("pick")
    if not pick:
        raise SystemExit("no pick in config/m7d_plate.json")
    pano = approved()
    if not (ROOT / CFG["approved_pano"]).exists():
        raise SystemExit(f"move the approved panorama to {CFG['approved_pano']} first (nothing is overwritten)")
    out = np.clip(merged(pick, pano) + 0.5, 0, 255).astype(np.uint8)
    outside = mask_full() <= 0.0
    diff = np.abs(out.astype(np.int16) - pano.astype(np.int16)).max(2)
    print(f"outside the mask: {int((diff[outside] > 0).sum())} pixels changed of {int(outside.sum())}; "
          f"inside: max change {int(diff[~outside].max())}")
    PANO.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(PANO), out)
    import m7c_plate
    m7c_plate.backdrop(out)
    print(f"{PANO}: the approved panorama with {pick} through the seam mask")


def sheet(out="review/m7d_plates.jpg", W=1930):
    import m7c_board as MB
    lab = MB.label
    rows = [lab(W, "M7d far plate: the L1 seam (about 22 degrees left of centre) inpainted with FLUX.2 [dev] across a soft band; "
                   "the approved panorama kept everywhere else. config/m7d_plate.json, log/prompts/m7d_seam.md.", 40, 0.6)]
    pano0 = approved()
    pick = CFG.get("pick")
    a, b = CFG["crop"]
    msk = mask_full()
    # the band before and after, the mask outlined
    x0, x1, y0, y1 = 1700, 3500, 120, 1180
    before = pano0[y0:y1, x0:x1].copy()
    after = np.clip(merged(pick, pano0) + 0.5, 0, 255).astype(np.uint8)[y0:y1, x0:x1] if pick else before.copy()
    cont = (msk[y0:y1, x0:x1] > 0.02).astype(np.uint8)
    cs, _ = cv2.findContours(cont, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    tw = (W - 10) // 2
    bm = before.copy()
    cv2.drawContours(bm, cs, -1, (60, 200, 255), 2)
    rows.append(np.hstack([lab(tw, "before (M7c, approved): the hill ends in a vertical bank of fog at column ~2560; "
                                   "orange: the mask's outer edge", 26, 0.45), np.full((26, 10, 3), 24, np.uint8),
                           lab(tw, f"after (M7d): {pick or 'no pick yet'} through the mask", 26, 0.45, (170, 230, 170))]))
    rows.append(np.hstack([MB._fit(bm, tw), np.full((MB._fit(bm, tw).shape[0], 10, 3), 24, np.uint8), MB._fit(after, tw)]))
    # 1:1 crops at the seam
    cx0, cy0 = 2240, 240
    c0 = pano0[cy0:cy0 + 520, cx0:cx0 + 940]
    c1 = (np.clip(merged(pick, pano0) + 0.5, 0, 255).astype(np.uint8) if pick else pano0)[cy0:cy0 + 520, cx0:cx0 + 940]
    rows.append(np.hstack([lab(940, f"before, 1:1 (columns {cx0}-{cx0 + 940}, rows {cy0}-{cy0 + 520})", 24, 0.42, (170, 170, 170)),
                           np.full((24, 10, 3), 24, np.uint8), lab(940, "after, 1:1", 24, 0.42, (170, 170, 170))]))
    rows.append(np.hstack([c0, np.full((520, 10, 3), 24, np.uint8), c1]))
    # the whole panorama after, with the band marked
    full = np.clip(merged(pick, pano0) + 0.5, 0, 255).astype(np.uint8) if pick else pano0.copy()
    p = MB._fit(full, W)
    sc = W / full.shape[1]
    M = CFG["mask"]
    for xx in (M["c0"] - M["feather_x"], M["c1"] + M["feather_x"]):
        cv2.line(p, (int(xx * sc), 0), (int(xx * sc), 16), (60, 200, 255), 2)
    rows.append(lab(W, "the panorama after (7680x1440), the band's outer edges marked; unchanged outside it", 26, 0.45))
    rows.append(p)
    # the canvas, the mask and every take
    rv = CFG.get("review", {})
    takes = sorted(OUT.glob("seam_s*.png"))
    tw3 = (W - 20) // 3
    can = cv2.imread(str(OUT / "canvas_seam.png"))
    mk = cv2.cvtColor(cv2.imread(str(OUT / "mask_seam.png"), cv2.IMREAD_GRAYSCALE), cv2.COLOR_GRAY2BGR)
    if can is not None:
        rows.append(np.hstack([lab(tw3, f"the canvas: columns {a}-{b} of the approved panorama", 26, 0.42), np.full((26, 10, 3), 24, np.uint8),
                               lab(tw3, "the mask (white: regenerated; the value is the local denoise strength)", 26, 0.42),
                               np.full((26, 10, 3), 24, np.uint8), lab(tw3, "", 26, 0.42)]))
        ci, mi = MB._fit(can, tw3), MB._fit(mk, tw3)
        rows.append(np.hstack([ci, np.full((ci.shape[0], 10, 3), 24, np.uint8), mi, np.full((ci.shape[0], 10, 3), 24, np.uint8),
                               np.full_like(ci, 24)]))
    for i in range(0, len(takes), 3):
        grp = takes[i:i + 3]
        heads, ims = [], []
        for t in grp:
            note = rv.get(t.stem, "")
            ok = pick == t.stem
            heads.append(lab(tw3, f"{t.stem}: {note or ('picked' if ok else '')}"[:95], 26, 0.42,
                             (170, 230, 170) if ok else (200, 170, 170)))
            ims.append(MB._fit(cv2.imread(str(t)), tw3))
        while len(ims) < 3:
            heads.append(lab(tw3, "", 26)); ims.append(np.full_like(ims[0], 24))
        rows.append(np.hstack(sum([[hh, np.full((26, 10, 3), 24, np.uint8)] for hh in heads], [])[:-1]))
        rows.append(np.hstack(sum([[im, np.full((im.shape[0], 10, 3), 24, np.uint8)] for im in ims], [])[:-1]))
        for t in grp:
            note = rv.get(t.stem, "")
            if len(note) > 95:
                rows.append(lab(W, f"{t.stem}: {note}"[:250], 22, 0.4, (170, 170, 170)))
    rej = sorted((ROOT / "archive/assets/gen/stills/m7d_park").glob("*/seam_s*.png"))
    if rej:
        rows.append(lab(W, "Rejected runs, archived: " + ", ".join(f"{t.parent.name}/{t.stem}" for t in rej), 26, 0.45, (200, 170, 170)))
        ims = [MB._fit(cv2.imread(str(t)), tw3) for t in rej[:3]]
        while len(ims) < 3:
            ims.append(np.full_like(ims[0], 24))
        rows.append(np.hstack(sum([[im, np.full((im.shape[0], 10, 3), 24, np.uint8)] for im in ims], [])[:-1]))
    rows = [r if r.shape[1] == W else np.hstack([r, np.full((r.shape[0], W - r.shape[1], 3), 24, np.uint8)]) for r in rows]
    im = np.vstack(rows)
    cv2.imwrite(str(ROOT / out), im, [cv2.IMWRITE_JPEG_QUALITY, 88])
    print(f"{out}: {im.shape[1]}x{im.shape[0]}, {(ROOT / out).stat().st_size / 1e6:.2f} MB")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seam", action="store_true")
    ap.add_argument("--compose", action="store_true")
    ap.add_argument("--sheet", action="store_true")
    a = ap.parse_args()
    if a.seam:
        seam()
    if a.compose:
        compose()
    if a.sheet:
        sheet()


if __name__ == "__main__":
    main()
