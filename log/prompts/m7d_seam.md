# M7d prompts and seeds: the far plate's L1 seam

Append-only; one row per take (`scripts/m7d_plate.py --seam`). The prompt verbatim in `log/prompts/m7d/seam.txt` and below.

Inpaint: model `flux2_dev_fp8mixed.safetensors`, text encoder `mistral_3_small_flux2_fp4_mixed.safetensors`, VAE `flux2-vae.safetensors`; 28 steps, euler, guidance 4.0; ComfyUI v0.42.1, the M7c outpainting graph: the canvas VAE-encoded, SetLatentNoiseMask with the mask, DifferentialDiffusion on the model (the mask value is the local denoise strength), Flux2Scheduler, SamplerCustomAdvanced. No negative prompt (FLUX.2 [dev] is guidance-distilled); the constraints are written into the prompt (M7c's style).

Canvas: columns 1536-3584 of the approved M7c panorama (2048x1440). Mask (panorama coordinates): strength 1.0 over columns 2380-2760 and rows 230-690, a smoothstep to 0 over 200 px to the sides and 80 px above and below. The pick is pasted back through the same mask, so nothing outside it changes.

### seam (inpaint across the L1 seam)

```
Wide distant panorama from a hilltop on the same misty afternoon: a long dark wooded hill on the left slopes gently down toward the right and dissolves into soft horizontal layers of fog, its conifer tree line continuing unbroken down into the valley behind the low-rise blocks at the city's edge; paler forested ridges behind it fade into the low flat cloud base; the fog lies in horizontal banks across the hillside and the valley, with tree tops showing through it, matte painting background plate, photorealistic, overcast, soft flat grey light, layered atmospheric fog, high detail, sharp, no foreground objects, no people, no faces, no text, no letters or numbers, no signs, no logos, no landmarks, no observation towers, every building a generic anonymous office or apartment block, no boats, no ships, no ferries, no water, no lake, no bay, no river, no sea
```

| Take | Seed | Output | Seconds | When |
| --- | --- | --- | --- | --- |
| seam | 41 | `assets/gen/stills/m7d_park/seam/seam_s41.png` | 98.7 | 2026-11-16T13:04:18-05:00 |
| seam | 42 | `assets/gen/stills/m7d_park/seam/seam_s42.png` | 89.2 | 2026-11-16T13:05:47-05:00 |
| seam | 43 | `assets/gen/stills/m7d_park/seam/seam_s43.png` | 90.2 | 2026-11-16T13:07:17-05:00 |

## Review (agent, production log 51)

Every take viewed at full size and pasted into the panorama through the mask, at 1:1. Checked for: water, a bay or a lake-like fog band, boats, the Space Needle or any recognisable tower or skyline, logos or text, faces or people, a visible mask edge. None found in the pick.

| Take | Verdict | Why |
| --- | --- | --- |
| seam_s41 | **picked** | the hill tapers into horizontal fog banks, a lower tree line descends behind the blocks; no vertical fog wall; the thin pale band between ridges has soft edges and tree tops through it (fog, not water); no mask edge at 1:1 |
| seam_s42 | rejected | a bright flat band with a hard top edge between the hill and the lower tree line: lake-like |
| seam_s43 | not picked | a crisp slope with a bright flat patch at its foot, and the upper ridge again ending in a soft vertical fade at the band's right side |
