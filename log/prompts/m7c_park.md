# M7c prompts and seeds: the far plate's extension and O22d

Append-only; one row per take (`scripts/m7c_plate.py`). Prompts verbatim in `log/prompts/m7c/<pass>.txt` and below.

Extension: model `flux2_dev_fp8mixed.safetensors`, text encoder `mistral_3_small_flux2_fp4_mixed.safetensors`, VAE `flux2-vae.safetensors`; 28 steps, euler, guidance 4.0; ComfyUI v0.42.1, outpainting: the canvas VAE-encoded, SetLatentNoiseMask with the mask, DifferentialDiffusion on the model (the mask value is the local denoise strength), Flux2Scheduler, SamplerCustomAdvanced. No negative prompt (FLUX.2 [dev] is guidance-distilled); the constraints are written into the prompt.

O22d: ComfyUI template `video_ltx2_3_i2v` (`ltx-2.3-22b-dev-fp8` + distilled LoRA 0.5, Gemma 3 12B fp4 encoder, x2 spatial upscaler), node settings as `scripts/clips.py`, prompt enhancer off; prompt = motion + '. ' + style; the second-stage noise seed is seed + 1.

### L1 (extension, left)

```
Wide distant panorama from a hilltop, the same misty afternoon continuing to the left of a generic downtown: the city thins out into low-rise blocks and residential neighbourhoods of small houses and street trees on rolling wooded hills, descending in successively paler grey-green layers of fog, dark conifer tree lines between the neighbourhoods, no tall towers; a low flat cloud base across the top; the lower edge of the frame is mist over the dark tops of distant conifers, matte painting background plate, photorealistic, overcast, soft flat grey light, layered atmospheric fog, high detail, sharp, no foreground objects, no people, no faces, no text, no letters or numbers, no signs, no logos, no landmarks, no observation towers, every building a generic anonymous office or apartment block, no boats, no ships, no ferries, no water, no lake, no bay, no river, no sea
```

| Take | Seed | Output | Seconds | When |
| --- | --- | --- | --- | --- |
| L1 | 41 | `assets/gen/stills/m7c_park/extend/L1/L1_s41.png` | 131.5 | 2026-11-16T10:48:21-05:00 |
| L1 | 42 | `assets/gen/stills/m7c_park/extend/L1/L1_s42.png` | 117.2 | 2026-11-16T10:50:18-05:00 |

### R1 (extension, right)

```
Wide distant panorama from a hilltop, the same misty afternoon continuing to the right of a generic downtown: the city thins out into low-rise blocks and residential neighbourhoods of small houses and street trees on rolling wooded hills, descending in successively paler grey-green layers of fog, dark conifer tree lines between the neighbourhoods, no tall towers; a low flat cloud base across the top; the lower edge of the frame is mist over the dark tops of distant conifers, matte painting background plate, photorealistic, overcast, soft flat grey light, layered atmospheric fog, high detail, sharp, no foreground objects, no people, no faces, no text, no letters or numbers, no signs, no logos, no landmarks, no observation towers, every building a generic anonymous office or apartment block, no boats, no ships, no ferries, no water, no lake, no bay, no river, no sea
```

| Take | Seed | Output | Seconds | When |
| --- | --- | --- | --- | --- |
| R1 | 41 | `assets/gen/stills/m7c_park/extend/R1/R1_s41.png` | 108.1 | 2026-11-16T10:52:06-05:00 |
| R1 | 42 | `assets/gen/stills/m7c_park/extend/R1/R1_s42.png` | 113.8 | 2026-11-16T10:54:00-05:00 |

**Run 1 rejected (all four takes above):** a blurred vertical stripe about 64 px wide where the filled half meets the plate. The mask was under 1 for the first 64 px of the part to fill, which held those pixels to the canvas's blurred fill for the first steps. Moved to `archive/assets/gen/stills/m7c_park/extend_v1/`. Fixed in `scripts/m7c_plate.py`: the mask is 1 over the whole part to fill and ramps to 0 over 160 px into the known half. Same prompts and seeds below.

### Run 2 (L1, R1; mask fixed)

| Take | Seed | Output | Seconds | When |
| --- | --- | --- | --- | --- |
| L1 | 41 | `assets/gen/stills/m7c_park/extend/L1/L1_s41.png` | 106.2 | 2026-11-16T10:58:51-05:00 |
| L1 | 42 | `assets/gen/stills/m7c_park/extend/L1/L1_s42.png` | 111.4 | 2026-11-16T11:00:42-05:00 |
| R1 | 41 | `assets/gen/stills/m7c_park/extend/R1/R1_s41.png` | 107.2 | 2026-11-16T11:02:29-05:00 |
| R1 | 42 | `assets/gen/stills/m7c_park/extend/R1/R1_s42.png` | 110.2 | 2026-11-16T11:04:20-05:00 |

Picks: L1_s42, R1_s41 (notes in `config/m7c_plate.json` review).

### Run 3 (L2, R2: the far sides from the ridges plates)

| Take | Seed | Output | Seconds | When |
| --- | --- | --- | --- | --- |

### L2 (extension, left, from the ridges plate)

```
Wide distant panorama from a hilltop, the same misty afternoon: forested ridgelines of dark conifers receding into thick fog, each ridge paler than the one before, a few rooftops of small houses in the nearer valleys, no buildings on the ridges, no towers; a low flat cloud base across the top; the lower edge of the frame is mist over the dark tops of distant conifers, matte painting background plate, photorealistic, overcast, soft flat grey light, layered atmospheric fog, high detail, sharp, no foreground objects, no people, no faces, no text, no letters or numbers, no signs, no logos, no landmarks, no observation towers, every building a generic anonymous office or apartment block, no boats, no ships, no ferries, no water, no lake, no bay, no river, no sea
```

| Take | Seed | Output | Seconds | When |
| --- | --- | --- | --- | --- |
| L2 | 41 | `assets/gen/stills/m7c_park/extend/L2/L2_s41.png` | 107.1 | 2026-11-16T11:06:30-05:00 |
| L2 | 42 | `assets/gen/stills/m7c_park/extend/L2/L2_s42.png` | 111.1 | 2026-11-16T11:08:21-05:00 |

### R2 (extension, right, from the ridges plate)

```
Wide distant panorama from a hilltop, the same misty afternoon: forested ridgelines of dark conifers receding into thick fog, each ridge paler than the one before, a few rooftops of small houses in the nearer valleys, no buildings on the ridges, no towers; a low flat cloud base across the top; the lower edge of the frame is mist over the dark tops of distant conifers, matte painting background plate, photorealistic, overcast, soft flat grey light, layered atmospheric fog, high detail, sharp, no foreground objects, no people, no faces, no text, no letters or numbers, no signs, no logos, no landmarks, no observation towers, every building a generic anonymous office or apartment block, no boats, no ships, no ferries, no water, no lake, no bay, no river, no sea
```

| Take | Seed | Output | Seconds | When |
| --- | --- | --- | --- | --- |
| R2 | 41 | `assets/gen/stills/m7c_park/extend/R2/R2_s41.png` | 112.1 | 2026-11-16T11:10:14-05:00 |
| R2 | 42 | `assets/gen/stills/m7c_park/extend/R2/R2_s42.png` | 111.1 | 2026-11-16T11:12:05-05:00 |

**Run 3 rejected (L2 and R2 above, both seeds):** the ridges plates' far town (slab blocks, which M7b took the plates for their tree lines only) stayed on the far horizon at init strength 0.86; R2 s41 also has a hard vertical edge where the ridges' forest begins (the full-strength band next to the junction was too narrow). Moved to `archive/assets/gen/stills/m7c_park/extend_v2/`. Run 4: the band 520 px with a 200 px soft edge, init strength 0.9, and the far-town rows (360-600) regenerated at full strength from a blurred fill. Same prompts and seeds.

### Run 4 (L2, R2)

| Take | Seed | Output | Seconds | When |
| --- | --- | --- | --- | --- |
| L2 | 41 | `assets/gen/stills/m7c_park/extend/L2/L2_s41.png` | 112.1 | 2026-11-16T11:14:21-05:00 |
| L2 | 42 | `assets/gen/stills/m7c_park/extend/L2/L2_s42.png` | 113.3 | 2026-11-16T11:16:15-05:00 |
| R2 | 41 | `assets/gen/stills/m7c_park/extend/R2/R2_s41.png` | 114.1 | 2026-11-16T11:18:09-05:00 |
| R2 | 42 | `assets/gen/stills/m7c_park/extend/R2/R2_s42.png` | 113.1 | 2026-11-16T11:20:02-05:00 |

### O22d (image-to-video from assets/gen/stills/m7c_park/o22d/o22d_input.png, crop [318, 0, 2322, 1102] of the plate)

```
A locked-off static tripod shot from a hilltop of a distant generic city in fog: the framing never moves, no zoom, no push-in, no pan, no tilt. Thin layers of fog drift slowly sideways across the towers and the wooded hills below them, and the low cloud base slides slowly over the tops of the tallest towers. The buildings and the trees keep their exact shapes. Nothing else moves: no people, no birds, no vehicles, no lights switching on. Realistic film footage, overcast afternoon, soft flat grey daylight, subtle 35mm film grain, a completely static locked-off camera, every building keeps its exact shape, no people, no faces, no text, no logos, no boats, no ships, no ferries, no water
```

| Take | Seed | Output | Seconds | When |
| --- | --- | --- | --- | --- |
| O22d | 41 | `assets/gen/clips/O22d/O22d_s41.mp4` | 40.4 | 2026-11-16T11:21:26-05:00 |
| O22d | 42 | `assets/gen/clips/O22d/O22d_s42.mp4` | 18.2 | 2026-11-16T11:21:44-05:00 |
| O22d | 43 | `assets/gen/clips/O22d/O22d_s43.mp4` | 17.5 | 2026-11-16T11:22:01-05:00 |

## Review (agent, production log 46)

Every take viewed at full size, each seam at 1:1; O22d's frames 1, 61 and 121 at full size and 1:1 crops of the city. Checked for: water, a bay or a lake-like fog band, boats, the Space Needle or any recognisable tower or skyline, logos or text, faces or people. None found in a kept take.

| Take | Verdict | Why |
| --- | --- | --- |
| L1_s41, L1_s42, R1_s41, R1_s42 (run 1) | rejected | a blurred stripe at the seam (mask under 1 there); archived |
| L1_s41 (run 2) | not picked | a pointed church-like spire, the one sharp vertical on that skyline |
| L1_s42 (run 2) | **picked** | mid-rise blocks and houses on a wooded hill, ridges in the cloud base |
| R1_s41 (run 2) | **picked** | the city's edge into low blocks, a wooded hill, ridges receding |
| R1_s42 (run 2) | not picked | a denser band of blocks, less recession |
| L2_s41, L2_s42, R2_s41, R2_s42 (run 3) | rejected | the ridges plates' far slab blocks kept (tree lines only); R2_s41 also a hard vertical edge; archived |
| L2_s41 (run 4) | not picked | a pale fog band with a sharp top edge between dark ridges, close to M7b's lake-like band |
| L2_s42 (run 4) | **picked** | a forested ridge, soft fog banks with tree tops through them (fog, not water, at 1:1) |
| R2_s41 (run 4) | rejected | a hard vertical edge where the forest begins, and a flat green patch like a sports field |
| R2_s42 (run 4) | **picked** | ridges receding in fog, a forest rising on the right, a few houses |
| O22d_s41 | **picked** | nearly locked (scale 0.997, 23 px drift over 5 s); fog thickens and drifts over the hill and the houses; buildings keep their shapes |
| O22d_s42 | not picked | a slow push (scale 1.042) and a 34 px pan; a fallback |
| O22d_s43 | rejected | a strong push-in (scale 1.22) |
