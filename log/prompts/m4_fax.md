# M4 prompts and seeds: O06 fax still, O07 fog-tower plate

Append-only from here on; one row per take (`scripts/stills.py`). Prompts verbatim below and in `log/prompts/m4/<item>.txt`.

Model `flux2_dev_fp8mixed.safetensors`, text encoder `mistral_3_small_flux2_fp4_mixed.safetensors`, VAE `flux2-vae.safetensors`; 28 steps, euler, guidance 4.0; ComfyUI v0.42.1, text-to-image. No negative prompt (FLUX.2 [dev] is guidance-distilled); the negatives are written into the prompt. Seeds from `config/seeds.json` `m4_stills` (41–45; the fog tower the first four).

Batch 1 (2026-11-15, production log 10) ran as two overlapping processes on one ComfyUI queue, so the rows were re-sorted once by the agent before the first commit, and the seconds for a45, b41 and b42 include queue waits. The second process was stopped by Claude Code for low system memory after b43. The b44 render had already been queued and finished in ComfyUI; it was copied from `~/ComfyUI/output/aso/O06_fax_b_s44_00001_.png`, so its time was not measured. O06_fax_b seed 45, O06_fax_c and O07_fogtower were not run.

## Prompts

### O06_fax_a (O06)

Seeds 41, 42, 43, 44, 45.

```
A boxy beige plastic office fax machine from the early 2000s sits on a cluttered trading desk late at night, a single white sheet of paper curling up and out of its output tray, lit warmly by a desk lamp beside it; behind it a row of three computer monitors glows dimly with abstract blurred candlestick charts and coloured lines that cannot be read; a corded desk phone, scattered blank papers, a plain mug and tangled cables around it; rain streaks on a dark window in the far background, cinematic film still, night interior, photorealistic, dark and moody, low-key lighting, a warm tungsten desk lamp is the main light against deep shadow, cool faint glow from the screens, muted colour, shallow depth of field, subtle 35mm film grain, 16:9 widescreen, nobody in the room, no people, no hands, no faces, no text, no letters or numbers, no logos, no brand names, no labels, no boats, no ships, no ferries, no water
```

### O06_fax_b (O06)

Seeds 41, 42, 43, 44, 45.

```
Close low angle at desk height on an old grey office fax machine, one blank sheet of paper curling up and out of the tray toward the camera and catching the warm lamp light; out of focus behind it a dark empty trading floor at night, rows of desks with banks of monitors glowing faint amber and green with abstract unreadable charts; heavy shadows, cinematic film still, night interior, photorealistic, dark and moody, low-key lighting, a warm tungsten desk lamp is the main light against deep shadow, cool faint glow from the screens, muted colour, shallow depth of field, subtle 35mm film grain, 16:9 widescreen, nobody in the room, no people, no hands, no faces, no text, no letters or numbers, no logos, no brand names, no labels, no boats, no ships, no ferries, no water
```

### O06_fax_c (O06): queued, not run yet

Seeds 41, 42, 43, 44, 45.

```
Medium wide shot of an empty trading desk at night in a dark office, a boxy fax machine in the middle of the desk under a warm desk lamp, one page curling out of it, a multi-monitor rig of six screens glowing dimly with abstract blurred charts, an empty office chair pushed back, scattered blank paper and sticky notes, a tall dark window behind with rain on the glass, cinematic film still, night interior, photorealistic, dark and moody, low-key lighting, a warm tungsten desk lamp is the main light against deep shadow, cool faint glow from the screens, muted colour, shallow depth of field, subtle 35mm film grain, 16:9 widescreen, nobody in the room, no people, no hands, no faces, no text, no letters or numbers, no logos, no brand names, no labels, no boats, no ships, no ferries, no water
```

### O07_fogtower (O07 alternate): queued, not run yet

Seeds 41, 42, 43, 44.

```
A wide empty mown lawn on a hilltop under a heavy pale grey sky, an open patch of grass in the foreground, dark evergreen trees at the edges; far in the distance a single tall slender plain concrete tower, a thin column with a small simple flat platform at the top, mostly hidden in thick fog, its upper part faint and washed out, cinematic film still, overcast daylight exterior, soft flat grey light, light drizzle, photorealistic, muted greens and greys, 16:9 widescreen, no people, no faces, no text, no letters or numbers, no logos, no brand names, no city skyline, no boats, no ships, no ferries, no water, no lake, no fountain
```

## Takes

| Item | Seed | Size | Output | Seconds | When |
| --- | --- | --- | --- | --- | --- |
| O06_fax_a | 41 | 1920×1088 | `assets/gen/stills/O06_fax_a/O06_fax_a_s41.png` | 77.0 | 2026-11-15T09:15:43-05:00 |
| O06_fax_a | 42 | 1920×1088 | `assets/gen/stills/O06_fax_a/O06_fax_a_s42.png` | 49.4 | 2026-11-15T09:16:33-05:00 |
| O06_fax_a | 43 | 1920×1088 | `assets/gen/stills/O06_fax_a/O06_fax_a_s43.png` | 56.1 | 2026-11-15T09:17:29-05:00 |
| O06_fax_a | 44 | 1920×1088 | `assets/gen/stills/O06_fax_a/O06_fax_a_s44.png` | 57.1 | 2026-11-15T09:18:26-05:00 |
| O06_fax_a | 45 | 1920×1088 | `assets/gen/stills/O06_fax_a/O06_fax_a_s45.png` | 103.2 | 2026-11-15T09:20:09-05:00 |
| O06_fax_b | 41 | 1920×1088 | `assets/gen/stills/O06_fax_b/O06_fax_b_s41.png` | 90.1 | 2026-11-15T09:19:18-05:00 |
| O06_fax_b | 42 | 1920×1088 | `assets/gen/stills/O06_fax_b/O06_fax_b_s42.png` | 108.9 | 2026-11-15T09:21:07-05:00 |
| O06_fax_b | 43 | 1920×1088 | `assets/gen/stills/O06_fax_b/O06_fax_b_s43.png` | 55.1 | 2026-11-15T09:22:02-05:00 |
| O06_fax_b | 44 | 1920×1088 | `assets/gen/stills/O06_fax_b/O06_fax_b_s44.png` | — | 2026-11-15T09:22:55-05:00 (ComfyUI output file time) |

## Clips: LTX-2.3 image-to-video

ComfyUI template `video_ltx2_3_i2v` (`ltx-2.3-22b-dev-fp8` + distilled LoRA 0.5, Gemma 3 12B fp4 encoder, x2 spatial upscaler), via `scripts/clips.py`; graph as in Ever Present. Prompt = motion + '. ' + the clip style (`config/m4_clips.json`), prompt enhancer off. The template's own negative prompt is unchanged ("pc game, console game, video game, cartoon, childish, ugly"; CFG 1, as in the template). 1280×720, 24 fps, 5 s (121 frames). Seeds from `config/seeds.json` `m4_clips` (41, 42); the second-stage noise seed is seed + 1 (42, 43).

### O06 (from `assets/gen/stills/O06_fax_a/O06_fax_a_s45.png`), prompt v1

```
Locked-off static shot, the camera does not move. The single white sheet of paper slowly curls further up and out of the fax machine's output tray. The computer monitors flicker faintly. Soft light from the rain on the window drifts slowly across the desk. The desk lamp stays steady. Nobody enters the frame. No new text or logos appear. Realistic film footage, night interior, dark and moody, low-key light, subtle 35mm film grain, a completely static locked-off camera, every object keeps its exact shape, the room stays empty, no people, no hands, no faces, no text, no logos
```

| Clip | Still | Seed | Output | Seconds | When |
| --- | --- | --- | --- | --- | --- |
| O06 | `assets/gen/stills/O06_fax_a/O06_fax_a_s45.png` | 41 | `assets/gen/clips/O06/O06_s41.mp4` | 40.9 | 2026-11-15T09:35:57-05:00 |
| O06 | `assets/gen/stills/O06_fax_a/O06_fax_a_s45.png` | 42 | `assets/gen/clips/O06/O06_s42.mp4` | 19.0 | 2026-11-15T09:36:16-05:00 |

### O06, prompt v2 (one revision: both v1 seeds pushed in)

Seeds `m4_clips_v2` (43, 44); second-stage seeds 44, 45. Same still, style and settings.

```
A fixed tripod shot: the framing stays exactly the same from the first frame to the last, no zoom, no push-in, no pan, no tilt; the desk, the fax machine, the monitors, the lamp, the phone and the mug stay exactly where they are. The only motion: the white sheet of paper in the fax machine's top slot slowly curls further up and back; the charts on the monitors flicker faintly; a soft shimmer of rain-light drifts slowly across the desk. Nobody enters the frame. No new text or logos appear. Realistic film footage, night interior, dark and moody, low-key light, subtle 35mm film grain, a completely static locked-off camera, every object keeps its exact shape, the room stays empty, no people, no hands, no faces, no text, no logos
```

| Clip | Still | Seed | Output | Seconds | When |
| --- | --- | --- | --- | --- | --- |
| O06 v2 | `assets/gen/stills/O06_fax_a/O06_fax_a_s45.png` | 43 | `assets/gen/clips/O06/O06_v2_s43.mp4` | 20.2 | 2026-11-15T09:37:14-05:00 |
| O06 v2 | `assets/gen/stills/O06_fax_a/O06_fax_a_s45.png` | 44 | `assets/gen/clips/O06/O06_v2_s44.mp4` | 18.0 | 2026-11-15T09:37:32-05:00 |
