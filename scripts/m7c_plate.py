"""M7c: the park's far plate (human interventions 19 and 22; decisions 35+), from far plate 1 (plate_city_s42, M7b) and
plates 2-3 (plate_ridges_s41/s42) as the far tree lines.

  --extend PASS [PASS ...]  FLUX.2 [dev] outpainting via ComfyUI (config/m7c_plate.json passes L1, R1, L2, R2): a
                            2560x1440 canvas of 1280 px of the panorama so far and 1280 px to fill, a noise mask
                            (SetLatentNoiseMask) with differential diffusion (the mask value is the local denoise
                            strength); L2 and R2 start the filled half from the ridges plate's half next to the city.
                            Seeds config/seeds.json m7c_plate_extend; one take per seed:
                            assets/gen/stills/m7c_park/extend/<pass>/<pass>_s<seed>.png (inputs beside them).
  --compose                 the panorama from the picks (config/m7c_plate.json picks): 7680x1440, seams blended inside
                            each pass's mask ramp -> assets/gen/stills/m7c_park/pano/pano.png; and the backdrop texture
                            for Blender (assets/gen/tex/m7c/park_backdrop.png, 16-bit RGBA, Non-Color): each value
                            mapped through the inverse of the park's view transform (AgX, its look and exposure:
                            assets/gen/tex/m7c/agx_lut.png from blender/m7c_agx_lut.py), so the plate reads in the
                            render as it does here; the top fades out into the sky (alpha), the bottom into the valley
                            fog; with assets/gen/tex/m7c/park_backdrop.json (the scale and the fog and sky colours,
                            scene-linear, that blender/park_m7c.py matches to it).
  --o22d                    LTX-2.3 image-to-video of the plate's centre for O22d (config o22d; ComfyUI template
                            video_ltx2_3_i2v, node settings as scripts/clips.py): assets/gen/clips/O22d/O22d_s<seed>.mp4,
                            seeds config/seeds.json m7c_o22d.
  --sheet                   review/m7c_plates.jpg: the plates used, the passes and their takes, the panorama, the O22d
                            takes with the pick.
Prompts verbatim in log/prompts/m7c/<pass>.txt and log/prompts/m7c_park.md (one row per take). ComfyUI runs on
127.0.0.1:8188, one job at a time. Takes that already exist are skipped, so a command resumes.
Usage: .venv/bin/python -I scripts/m7c_plate.py --extend L1 R1 | --compose | --o22d | --sheet
"""
import argparse
import copy
import datetime
import json
import sys
from pathlib import Path

import cv2
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import comfy_client as cc  # noqa: E402

CFG = json.loads((ROOT / "config/m7c_plate.json").read_text())
SEEDS = json.loads((ROOT / "config/seeds.json").read_text())
OUT = ROOT / "assets/gen/stills/m7c_park"
TEX = ROOT / "assets/gen/tex/m7c"
PROMPTS = ROOT / "log/prompts/m7c"
LOG = ROOT / "log/prompts/m7c_park.md"
W, H = CFG["canvas"]
HW = W // 2
# panorama columns of each part
COLS = {"L2": (0, 1280), "L1": (1280, 2560), "plate": (2560, 5120), "R1": (5120, 6400), "R2": (6400, 7680)}


def log_header():
    if LOG.exists():
        return
    m = CFG["model"]
    LOG.write_text(
        "# M7c prompts and seeds: the far plate's extension and O22d\n\nAppend-only; one row per take "
        "(`scripts/m7c_plate.py`). Prompts verbatim in `log/prompts/m7c/<pass>.txt` and below.\n\n"
        f"Extension: model `{m['unet']}`, text encoder `{m['clip']}`, VAE `{m['vae']}`; {m['steps']} steps, "
        f"{m['sampler']}, guidance {m['guidance']}; ComfyUI v0.42.1, outpainting: the canvas VAE-encoded, "
        "SetLatentNoiseMask with the mask, DifferentialDiffusion on the model (the mask value is the local denoise "
        "strength), Flux2Scheduler, SamplerCustomAdvanced. No negative prompt (FLUX.2 [dev] is guidance-distilled); "
        "the constraints are written into the prompt.\n\n"
        "O22d: ComfyUI template `video_ltx2_3_i2v` (`ltx-2.3-22b-dev-fp8` + distilled LoRA 0.5, Gemma 3 12B fp4 "
        "encoder, x2 spatial upscaler), node settings as `scripts/clips.py`, prompt enhancer off; prompt = motion + "
        "'. ' + style; the second-stage noise seed is seed + 1.\n")


def log_prompt(key, label, prompt):
    PROMPTS.mkdir(parents=True, exist_ok=True)
    pf = PROMPTS / f"{key}.txt"
    if not pf.exists() or pf.read_text() != prompt + "\n":
        pf.write_text(prompt + "\n")
        with open(LOG, "a") as f:
            f.write(f"\n### {key} ({label})\n\n```\n{prompt}\n```\n\n| Take | Seed | Output | Seconds | When |\n"
                    "| --- | --- | --- | --- | --- |\n")


def log_row(take, seed, dest, secs):
    when = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
    with open(LOG, "a") as f:
        f.write(f"| {take} | {seed} | `{dest.relative_to(ROOT)}` | {secs:.1f} | {when} |\n")


# ---------------------------------------------------------------- outpainting

def plate():
    return cv2.imread(str(ROOT / CFG["source"]))


def pick(p):
    return cv2.imread(str(OUT / "extend" / p / f"{CFG['picks'][p]}.png"))


def known_half(p):
    """The 1280 px of the panorama next to the part a pass fills."""
    spec = CFG["passes"][p]
    if p == "L1":
        return plate()[:, :HW]
    if p == "R1":
        return plate()[:, HW:]
    prev = pick(spec["after"])
    return prev[:, :HW] if spec["side"] == "left" else prev[:, HW:]


def canvas_and_mask(p):
    spec = CFG["passes"][p]
    left = spec["side"] == "left"
    known = known_half(p)
    r1 = CFG["ramp"]
    x = np.arange(W, dtype=np.float32) + 0.5
    d = (HW - x) if left else (x - HW)          # > 0 inside the part to fill, < 0 in the known half
    # 1 over the whole part to fill (a value under 1 holds a pixel to the canvas for the first steps: M7c's first
    # takes kept a blurred stripe of the fill there), ramping to 0 over r1 px into the known half
    mask = np.clip((d + r1) / r1, 0, 1)
    if spec.get("init"):
        ridge = cv2.imread(str(ROOT / CFG["ridges"][spec["init"]]))
        fill = ridge[:, HW:] if left else ridge[:, :HW]           # the ridges plate's half next to the city
        s = CFG["init_strength"]
        t = np.clip((CFG["band"] - d) / CFG.get("band_soft", 64), 0, 1)   # 1 within the band next to the junction
        mask = np.where(d >= 0, s + (1 - s) * t * t * (3 - 2 * t), mask)
        rr = spec.get("regen_rows")
        if rr:
            # the ridges plates' far town (slab blocks: M7b took the plates for their tree lines only) is regenerated:
            # full strength over these rows of the filled half, feathered over 48 rows
            y = np.arange(H, dtype=np.float32)[:, None]
            wy = np.clip(np.minimum(y - rr[0], rr[1] - y) / 48.0, 0, 1)
            m2 = np.repeat(mask[None, :], H, 0)
            m2 = np.where((d >= 0)[None, :], np.maximum(m2, wy), m2)
            fill = fill.copy()
            band = slice(int(rr[0]), int(rr[1]))
            fill[band] = cv2.GaussianBlur(fill, (0, 0), 30)[band]
            can = np.hstack([fill, known]) if left else np.hstack([known, fill])
            return can, (np.clip(m2, 0, 1) * 255 + 0.5).astype(np.uint8)
    else:
        fill = cv2.GaussianBlur(cv2.flip(known, 1), (0, 0), 24)  # mirrored and blurred; fully noised anyway
    can = np.hstack([fill, known]) if left else np.hstack([known, fill])
    m = (np.clip(mask, 0, 1) * 255 + 0.5).astype(np.uint8)
    return can, np.repeat(m[None, :], H, 0)


def outpaint_graph(prompt, seed, canvas_name, mask_name, prefix):
    m = CFG["model"]
    return {
        "12": {"class_type": "UNETLoader", "inputs": {"unet_name": m["unet"], "weight_dtype": "default"}},
        "38": {"class_type": "CLIPLoader", "inputs": {"clip_name": m["clip"], "type": "flux2", "device": "default"}},
        "10": {"class_type": "VAELoader", "inputs": {"vae_name": m["vae"]}},
        "50": {"class_type": "DifferentialDiffusion", "inputs": {"model": ["12", 0]}},
        "6": {"class_type": "CLIPTextEncode", "inputs": {"text": prompt, "clip": ["38", 0]}},
        "26": {"class_type": "FluxGuidance", "inputs": {"conditioning": ["6", 0], "guidance": m["guidance"]}},
        "60": {"class_type": "LoadImage", "inputs": {"image": canvas_name}},
        "61": {"class_type": "LoadImageMask", "inputs": {"image": mask_name, "channel": "red"}},
        "62": {"class_type": "VAEEncode", "inputs": {"pixels": ["60", 0], "vae": ["10", 0]}},
        "63": {"class_type": "SetLatentNoiseMask", "inputs": {"samples": ["62", 0], "mask": ["61", 0]}},
        "22": {"class_type": "BasicGuider", "inputs": {"model": ["50", 0], "conditioning": ["26", 0]}},
        "25": {"class_type": "RandomNoise", "inputs": {"noise_seed": seed}},
        "16": {"class_type": "KSamplerSelect", "inputs": {"sampler_name": m["sampler"]}},
        "48": {"class_type": "Flux2Scheduler", "inputs": {"steps": m["steps"], "width": W, "height": H}},
        "13": {"class_type": "SamplerCustomAdvanced",
               "inputs": {"noise": ["25", 0], "guider": ["22", 0], "sampler": ["16", 0], "sigmas": ["48", 0],
                          "latent_image": ["63", 0]}},
        "8": {"class_type": "VAEDecode", "inputs": {"samples": ["13", 0], "vae": ["10", 0]}},
        "9": {"class_type": "SaveImage", "inputs": {"images": ["8", 0], "filename_prefix": prefix}},
    }


def extend(passes):
    log_header()
    for p in passes:
        spec = CFG["passes"][p]
        prompt = spec["subject"] + ", " + CFG["style"]
        log_prompt(p, f"extension, {spec['side']}" + (", from the ridges plate" if spec.get("init") else ""), prompt)
        d = OUT / "extend" / p
        d.mkdir(parents=True, exist_ok=True)
        can, mask = canvas_and_mask(p)
        cv2.imwrite(str(d / f"canvas_{p}.png"), can)
        cv2.imwrite(str(d / f"mask_{p}.png"), mask)
        cn, mn = cc.upload_image(d / f"canvas_{p}.png"), cc.upload_image(d / f"mask_{p}.png")
        for seed in SEEDS["m7c_plate_extend"]:
            dest = d / f"{p}_s{seed}.png"
            if dest.exists():
                continue
            outputs, secs = cc.run(outpaint_graph(prompt, seed, cn, mn, f"aso_m7c/{p}_s{seed}"))
            cc.download(outputs["9"]["images"][0], dest)
            log_row(p, seed, dest, secs)
            print(f"{p} seed {seed}: {dest} ({secs:.1f} s)", flush=True)


# ---------------------------------------------------------------- the panorama and the Blender texture

def compose():
    pano = np.zeros((H, 7680, 3), np.float32)
    a, b = COLS["plate"]
    pano[:, a:b] = plate()
    r1 = CFG["ramp"]
    for p in ("L1", "R1", "L2", "R2"):
        g = pick(p).astype(np.float32)
        left = CFG["passes"][p]["side"] == "left"
        a, b = COLS[p]
        if left:
            pano[:, a:b] = g[:, :HW]
            w = (np.arange(r1, dtype=np.float32) / r1)[None, :, None]          # gen -> what was there, over the ramp
            pano[:, b:b + r1] = (1 - w) * g[:, HW:HW + r1] + w * pano[:, b:b + r1]
        else:
            pano[:, a:b] = g[:, HW:]
            w = (np.arange(r1, dtype=np.float32) / r1)[None, ::-1, None]
            pano[:, a - r1:a] = (1 - w) * g[:, HW - r1:HW] + w * pano[:, a - r1:a]
    pano = harmonise_sky(pano)
    pano = np.clip(pano + 0.5, 0, 255).astype(np.uint8)
    (OUT / "pano").mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(OUT / "pano" / "pano.png"), pano)
    backdrop(pano)
    print(f"{OUT / 'pano' / 'pano.png'}: {pano.shape[1]}x{pano.shape[0]}")


def harmonise_sky(pano):
    """The sky's brightness across the seams: each pass's cloud deck came out a few levels lighter or darker than the
    plate's, which showed as soft vertical steps in the sky over 160 px seams. Per column, the median of the sky rows
    (above the towers' tops) is smoothed twice (60 px: keeps the steps; 900 px: removes them); their ratio is a gain
    applied to the rows above the horizon, fading out toward the horizon, so only the sky's low-frequency brightness
    changes (the clouds' detail and the city stay as generated)."""
    P = CFG.get("backdrop", {})
    r0, r1 = P.get("sky_level_rows", [120, 380])
    fade = P.get("sky_gain_fade", [380, 560])
    prof = np.median(pano[r0:r1], axis=0)                               # (W, 3)
    k = lambda sig: cv2.GaussianBlur(prof[None], (0, 0), sigmaX=sig, sigmaY=0.1, borderType=cv2.BORDER_REFLECT)[0]  # noqa: E731
    gain = k(900) / np.maximum(k(60), 1.0)
    rows = np.arange(H, dtype=np.float32)
    wv = np.clip((fade[1] - rows) / (fade[1] - fade[0]), 0, 1)[:, None, None]
    pano = pano * (1 + (gain[None] - 1) * wv)
    # the cloud deck's structure also stopped at the seams (a band ending at a pass's edge): near each seam the bright,
    # featureless sky rows are blurred along the horizon (bands kept, their ends smoothed), their fine grain kept
    x = pano
    hb = cv2.GaussianBlur(x, (0, 0), sigmaX=P.get("sky_blur", 220), sigmaY=4)
    detail = x - cv2.GaussianBlur(x, (0, 0), 3)
    sr = P.get("sky_soft_rows", [340, 470])
    wv2 = np.clip((sr[1] - rows) / (sr[1] - sr[0]), 0, 1)[:, None]
    wl = np.clip((x.mean(2) - 175.0) / 20.0, 0, 1)
    cols = np.arange(x.shape[1], dtype=np.float32)
    wh = np.zeros_like(cols)
    for xs in (1280, 2560, 5120, 6400):
        wh = np.maximum(wh, np.clip(1 - np.abs(cols - xs) / P.get("sky_soft_half", 900), 0, 1))
    w = (wv2 * wl * (wh * wh * (3 - 2 * wh))[None, :])[..., None]
    return x * (1 - w) + (hb + detail) * w


def agx_inverse():
    """display (0..1 sRGB) -> scene-linear emission, from the LUT blender/m7c_agx_lut.py wrote (a ramp of linear
    values through the park's view transform, saved as rendered)."""
    lut = json.loads((TEX / "agx_lut.json").read_text())
    vals = np.array(lut["linear"], np.float64)
    disp = cv2.imread(str(TEX / "agx_lut.png"), cv2.IMREAD_UNCHANGED)[0, :, :3][:, ::-1].astype(np.float64) / 65535.0
    y = disp.mean(1)
    keep = np.concatenate([[True], np.diff(y) > 1e-7])
    return lambda d: np.interp(d, y[keep], vals[keep]), y.min(), y.max()


def backdrop(pano):
    """The Blender texture: per channel through the inverse view transform, as 16-bit Non-Color with a scale; alpha
    fades the cloud deck out into the sky at the top; the bottom fades into the valley-fog colour below the mist
    band; the outer columns soften into their own vertical profile (the image clamps beyond them)."""
    P = CFG.get("backdrop", {})
    inv, lo, hi = agx_inverse()
    x = pano[:, :, ::-1].astype(np.float32) / 255.0                   # RGB display
    rows = np.arange(H, dtype=np.float32)[:, None]
    # bottom: the mist band (rows ~1150-1250 of the plate) into a constant valley-fog colour below it
    fog_rows = slice(*P.get("fog_rows", [1170, 1230]))
    fog_rgb = np.median(x[fog_rows].reshape(-1, 3), 0)
    b0, b1 = P.get("bottom_fade", [1180, 1270])
    wb = np.clip((rows - b0) / (b1 - b0), 0, 1)[..., None]
    wb = wb * wb * (3 - 2 * wb)
    x = x * (1 - wb) + fog_rgb[None, None] * wb
    # outer columns: soften into a horizontal average of the edge strip
    e = P.get("edge_soft", 360)
    for side in (0, 1):
        sl = slice(0, e) if side == 0 else slice(x.shape[1] - e, x.shape[1])
        prof = x[:, sl].mean(1, keepdims=True)
        t = np.linspace(1, 0, e, dtype=np.float32) if side == 0 else np.linspace(0, 1, e, dtype=np.float32)
        t = (t * t)[None, :, None]
        x[:, sl] = x[:, sl] * (1 - t) + prof * t
    sky_rgb = np.median(x[P.get("sky_rows", [10, 120])[0]:P.get("sky_rows", [10, 120])[1]].reshape(-1, 3), 0)
    lr = P.get("level_rows", [560, 620])
    level_rgb = np.percentile(x[lr[0]:lr[1]].reshape(-1, 3), 75, axis=0)     # the haze at the horizon, not the towers
    a0, a1 = P.get("top_fade", [40, 220])
    alpha = np.clip((rows - a0) / (a1 - a0), 0, 1)
    alpha = alpha * alpha * (3 - 2 * alpha)
    lin = inv(np.clip(x, lo, hi)).astype(np.float32)
    scale = float(np.ceil(lin.max() * 1.02 * 100) / 100)
    rgba = np.concatenate([lin / scale, np.repeat(alpha, x.shape[1], 1)[..., None]], 2)
    TEX.mkdir(parents=True, exist_ok=True)
    out16 = (np.clip(rgba, 0, 1) * 65535 + 0.5).astype(np.uint16)
    cv2.imwrite(str(TEX / "park_backdrop.png"), out16[:, :, [2, 1, 0, 3]])
    meta = {"_doc": "scripts/m7c_plate.py --compose: park_backdrop.png holds scene-linear emission / scale (Non-Color), "
                    "alpha in A; the sky and valley-fog colours (scene-linear) the 3D matches to the plate's top and its "
                    "mist band; display values (0..1 sRGB) for the record.",
            "scale": scale, "size": [int(x.shape[1]), H],
            "sky_lin": [float(v) for v in inv(sky_rgb)], "sky_display": [float(v) for v in sky_rgb],
            "fog_lin": [float(v) for v in inv(fog_rgb)], "fog_display": [float(v) for v in fog_rgb],
            "level_lin": [float(v) for v in inv(level_rgb)], "level_display": [float(v) for v in level_rgb]}
    (TEX / "park_backdrop.json").write_text(json.dumps(meta, indent=1) + "\n")
    print(f"{TEX / 'park_backdrop.png'}: scale {scale}, sky {meta['sky_display']}, fog {meta['fog_display']}")


# ---------------------------------------------------------------- O22d

def o22d():
    log_header()
    spec = CFG["o22d"]
    base = json.loads((ROOT / "comfy/api/video_ltx2_3_i2v.api.json").read_text())
    x0, y0, x1, y1 = spec["crop"]
    still = OUT / "o22d" / "o22d_input.png"
    still.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(still), cv2.resize(plate()[y0:y1, x0:x1], tuple(spec["size"]), interpolation=cv2.INTER_AREA))
    name = cc.upload_image(still)
    prompt = spec["motion"] + ". " + spec["style"]
    log_prompt("O22d", f"image-to-video from {still.relative_to(ROOT)}, crop {spec['crop']} of the plate", prompt)
    for seed in SEEDS["m7c_o22d"]:
        dest = ROOT / "assets/gen/clips/O22d" / f"O22d_s{seed}.mp4"
        if dest.exists():
            continue
        g = copy.deepcopy(base)
        g["269"]["inputs"]["image"] = name
        g["320:319"]["inputs"]["value"] = prompt
        g["320:328"]["inputs"]["value"] = False
        g["320:312"]["inputs"]["value"], g["320:299"]["inputs"]["value"] = spec["size"]
        g["320:300"]["inputs"]["value"] = spec["fps"]
        g["320:301"]["inputs"]["value"] = spec["seconds"]
        g["320:276"]["inputs"]["noise_seed"] = seed
        g["320:277"]["inputs"]["noise_seed"] = seed + 1
        g["75"]["inputs"]["filename_prefix"] = f"aso_m7c/{dest.stem}"
        outputs, secs = cc.run(g)
        vid = next(v for k, vs in outputs["75"].items() if k in ("images", "videos", "gifs") for v in vs)
        cc.download(vid, dest)
        log_row("O22d", seed, dest, secs)
        print(f"O22d seed {seed}: {dest} ({secs:.1f} s)", flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--extend", nargs="+")
    ap.add_argument("--compose", action="store_true")
    ap.add_argument("--o22d", action="store_true")
    ap.add_argument("--sheet", action="store_true")
    a = ap.parse_args()
    if a.extend:
        extend(a.extend)
    if a.compose:
        compose()
    if a.o22d:
        o22d()
    if a.sheet:
        import m7c_board
        m7c_board.plates()


if __name__ == "__main__":
    main()
