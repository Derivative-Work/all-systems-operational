# M7b prompts and seeds: park concept stills and far-plate candidates

Append-only; one row per take (`scripts/m7b_concepts.py`). Prompts verbatim in `log/prompts/m7b/<item>.txt` and below. Reference for the park's direction, not footage (production log 40).

Model `flux2_dev_fp8mixed.safetensors`, text encoder `mistral_3_small_flux2_fp4_mixed.safetensors`, VAE `flux2-vae.safetensors`; 28 steps, euler, guidance 4.0; ComfyUI v0.42.1, text-to-image. No negative prompt (FLUX.2 [dev] is guidance-distilled); the constraints are written into the prompt.

## Prompts

### park_crest_a (O20a)

```
Eye-level view from the grassy crest of a small hilltop city park, standing where the back of a crowd would be: wet mown lawn and a worn gravel path in the foreground rising gently to a rounded brow about twenty metres ahead, beyond which the ground drops away steeply out of sight; tall dark Douglas firs and cedars frame both sides, some close, more further down the slope; a slender black cast-iron park lamp post on the right; far below and several kilometres away, across misty air, a generic downtown of anonymous office towers and mid-rise blocks fades into layers of fog, with wooded ridges and rooftops of residential streets descending toward it; a low uniform grey cloud base, cinematic film still, overcast autumn afternoon, light drizzle, soft flat grey daylight, layered fog and mist, photorealistic, muted greens and slate greys, natural colour, 35mm lens, 16:9 widescreen, no people, no faces, no text, no letters or numbers, no signs, no logos, no brand names, no landmarks, no observation towers, every building a generic anonymous office or apartment block, no boats, no ships, no ferries, no water, no lake, no bay, no river, no sea, no fountain
```

| Item | Seed | Size | Output | Seconds | When |
| --- | --- | --- | --- | --- | --- |
| park_crest_a | 41 | 1920×1088 | `assets/gen/stills/m7b_park/park_crest_a/park_crest_a_s41.png` | 82.0 | 2026-11-16T10:02:50-05:00 |
| park_crest_a | 42 | 1920×1088 | `assets/gen/stills/m7b_park/park_crest_a/park_crest_a_s42.png` | 50.1 | 2026-11-16T10:03:40-05:00 |

### park_crest_b (O20a)

```
An empty hilltop park lawn at the top of a steep wooded slope, seen at eye level: a gravel viewpoint path and a low worn stone edging along the brow, wet uneven grass with darker trodden patches, a few tall firs on each side and the tops of more firs just visible below the brow; far below the horizon line, a generic city skyline of plain rectangular towers in the distance, layered in pale fog, the nearer neighbourhoods of houses and bare trees in grey-green layers between; drizzle in the air, cinematic film still, overcast autumn afternoon, light drizzle, soft flat grey daylight, layered fog and mist, photorealistic, muted greens and slate greys, natural colour, 35mm lens, 16:9 widescreen, no people, no faces, no text, no letters or numbers, no signs, no logos, no brand names, no landmarks, no observation towers, every building a generic anonymous office or apartment block, no boats, no ships, no ferries, no water, no lake, no bay, no river, no sea, no fountain
```

| Item | Seed | Size | Output | Seconds | When |
| --- | --- | --- | --- | --- | --- |
| park_crest_b | 41 | 1920×1088 | `assets/gen/stills/m7b_park/park_crest_b/park_crest_b_s41.png` | 59.8 | 2026-11-16T10:04:40-05:00 |
| park_crest_b | 42 | 1920×1088 | `assets/gen/stills/m7b_park/park_crest_b/park_crest_b_s42.png` | 49.3 | 2026-11-16T10:05:29-05:00 |

### park_rise (O19b)

```
View from about fifteen metres up, rising just above the wet tops of dark fir trees on a hillside, looking over the rounded grassy crest of a small hilltop park with a single lamp post on the crest, toward a generic distant downtown of anonymous towers in layered fog far below and far away; fir tops close in the lower foreground, the lawn's brow in the middle distance, wooded slopes falling away beyond it, cinematic film still, overcast autumn afternoon, light drizzle, soft flat grey daylight, layered fog and mist, photorealistic, muted greens and slate greys, natural colour, 35mm lens, 16:9 widescreen, no people, no faces, no text, no letters or numbers, no signs, no logos, no brand names, no landmarks, no observation towers, every building a generic anonymous office or apartment block, no boats, no ships, no ferries, no water, no lake, no bay, no river, no sea, no fountain
```

| Item | Seed | Size | Output | Seconds | When |
| --- | --- | --- | --- | --- | --- |
| park_rise | 41 | 1920×1088 | `assets/gen/stills/m7b_park/park_rise/park_rise_s41.png` | 51.1 | 2026-11-16T10:06:20-05:00 |
| park_rise | 42 | 1920×1088 | `assets/gen/stills/m7b_park/park_rise/park_rise_s42.png` | 50.1 | 2026-11-16T10:07:10-05:00 |

### plate_city (far plate (O20 wides, O22d))

```
Wide distant view from a hilltop, nothing in the foreground: a generic downtown skyline of anonymous office towers and mid-rise blocks about three kilometres away and well below the viewer, in layered fog; in front of it, wooded ridges and residential neighbourhoods of small houses and street trees descend in successively paler grey-green layers; the tops of the tallest towers dissolve into a low flat cloud base; the lower edge of the frame is mist over the dark tops of distant conifers, matte painting background plate, photorealistic, overcast, soft flat grey light, layered atmospheric fog, high detail, sharp, no foreground objects, no people, no text, no letters or numbers, no signs, no logos, no landmarks, no observation towers, every building a generic anonymous office or apartment block, no boats, no ships, no ferries, no water, no lake, no bay, no river, no sea
```

| Item | Seed | Size | Output | Seconds | When |
| --- | --- | --- | --- | --- | --- |
| plate_city | 41 | 2560×1440 | `assets/gen/stills/m7b_park/plate_city/plate_city_s41.png` | 107.2 | 2026-11-16T10:08:57-05:00 |
| plate_city | 42 | 2560×1440 | `assets/gen/stills/m7b_park/plate_city/plate_city_s42.png` | 108.4 | 2026-11-16T10:10:46-05:00 |

### plate_ridges (far plate (O20 wides, O22d))

```
Wide view across layered forested hills and ridgelines of dark conifers receding into thick fog, each ridge paler than the one before, with a generic distant city of plain low towers barely visible in the farthest layer, under a low uniform grey cloud base; no foreground, the nearest ridge already a hundred metres away and below the viewer, matte painting background plate, photorealistic, overcast, soft flat grey light, layered atmospheric fog, high detail, sharp, no foreground objects, no people, no text, no letters or numbers, no signs, no logos, no landmarks, no observation towers, every building a generic anonymous office or apartment block, no boats, no ships, no ferries, no water, no lake, no bay, no river, no sea
```

| Item | Seed | Size | Output | Seconds | When |
| --- | --- | --- | --- | --- | --- |
| plate_ridges | 41 | 2560×1440 | `assets/gen/stills/m7b_park/plate_ridges/plate_ridges_s41.png` | 106.1 | 2026-11-16T10:12:32-05:00 |
| plate_ridges | 42 | 2560×1440 | `assets/gen/stills/m7b_park/plate_ridges/plate_ridges_s42.png` | 108.3 | 2026-11-16T10:14:20-05:00 |

## Review (agent, production log 42)

Every take viewed at full size. Constraints checked: no people (none in any take), no water, bay or boats, no Space Needle or other recognisable tower or landmark, no logos or text, no recognisable real skyline.

| Take | Verdict | Why |
| --- | --- | --- |
| park_crest_a_s41 | not kept | as s42 with a busier, more lit skyline and the same mound; no constraint broken |
| park_crest_a_s42 | kept (concept 3) | lamp post and firs at the crest, towers dissolving into the cloud base; the foreground is a mown mound, not a brow |
| park_crest_b_s41 | kept (concept 1) | the brow: lawn to an edge, the drop, roofs and bare trees below, the city far off; rain puddles on the lawn (not a body of water) |
| park_crest_b_s42 | kept (concept 2) | the same brow, taller firs |
| park_rise_s41 | kept (concept 5, O19b) | over fir tops to the crest's lamp post; the hill is a dome and the city too close |
| park_rise_s42 | kept (concept 4, O19b) | the O19b rise; the hill is a dome |
| plate_city_s41 | **rejected** | the pale fog band under the city reads as a lake (water guardrail), and its tallest dark stepped tower may evoke a real one (real-skyline rule) |
| plate_city_s42 | kept (far plate 1, recommended) | generic towers in the cloud base, streets and conifer lines in layered fog; the fog reads as fog |
| plate_ridges_s41 | kept (far plate 2) | forested ridges in fog; the far town is slab housing that reads less like the Northwest: tree lines only |
| plate_ridges_s42 | kept (far plate 3) | fog-filled conifer valleys; a band of far slab blocks: tree lines only |
