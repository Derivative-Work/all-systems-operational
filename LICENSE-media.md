# Licence for the video and its assets

Copyright 2026 Albert Armea.

"All Systems Operational" (the video) and its assets are licensed under the
[Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International licence](https://creativecommons.org/licenses/by-nc-sa/4.0/)
(CC BY-NC-SA 4.0). The full legal code is in [LICENSES/CC-BY-NC-SA-4.0.txt](LICENSES/CC-BY-NC-SA-4.0.txt).

The code is under the MIT licence instead: see [LICENSE](LICENSE).

## What this covers

- The video in all its cuts, with its captions and thumbnail.
- The music: the Suno v6 take and its v1.3 repaint, their stems, the Logic project and the Logic masters with the hard
  stops, the clap track as used, and the post-filtered masters; the credits music as post-filtered and cut for the end
  sequence.
- The rendered frames, the generated stills, plates and clips, and the figure library as built (`assets/figures/`).
- The on-screen text: status page, lower thirds, cards, the recreated chat post and every other label, and the frames
  the code renders from them.
- The production record, written by the agent: the logs and prompts under `log/`, the timing maps, the lyrics files
  and the documents under `docs/`, and the planning chat in `docs/planning_chat/`.

## What this doesn't cover

- **Code** (`scripts/`, `blender/`, `remotion/`, `config/` and the build files): MIT, see [LICENSE](LICENSE). Where a
  source file holds both code and on-screen text or design, the code is MIT and the frames it renders are
  CC BY-NC-SA.
- **The people and band kit** (`blender/ep/`): from Ever Present, by the same author, relicensed under MIT for this
  repository on 2026-11-15 (Ever Present itself stays unpublished). The figure library is built from MakeHuman's
  CC0 system assets (`assets/mpfb/`, fetched, not stored in git), with the MPFB add-on under its own licence.
- **The probe kit** (`blender/lib/`): from Sandbox Rhapsody, by the same author, MIT.
- **Little Switch** (`remotion/src/defaultOn/`): the rig and palette are copied unchanged from Default On, by the same
  author, and stay under that project's terms; the frames of the cameo are covered as above.
- **The real capture in the opening bookend** (`assets/screenshots/`): Microsoft's interface and logos belong to
  Microsoft. It appears as a documentary record and isn't licensed here. Nor is the "No license found" capture, a
  placeholder cut from the video, which the M3 contact sheet (`review/m3_screens.jpg`) shows as one tile.
- **The fonts** in `remotion/public/fonts/` (Inter, Work Sans, Caveat, Noto Sans Mono): SIL Open Font License 1.1,
  licence text beside each font (`SOURCES.md`).
- **The image-to-video graph** (`comfy/api/video_ltx2_3_i2v.api.json`): the API form of ComfyUI's template, Comfy Org,
  MIT. The generative models (FLUX.2 [dev], LTX-2.3) are used under their own licences and aren't offered here.
- **Remotion**, which renders the screens and cards, is not part of this repository; it is used under its own
  [Remotion License](https://www.remotion.dev/license).
- **The Clap 2 - Warm Embers loop** is one of Apple's Logic Pro loops, used in the music under Apple's terms for its
  loops; the loop itself isn't offered here. The Logic project in the release refers to it without including it (Logic
  offers to install Apple's pack when the project opens).
- **The auditors' outputs** in `log/audits/` are kept verbatim as a record of the audit, only as far as each
  provider's terms allow.
- **The Suno page records** in `docs/suno/` are Suno's metadata for the take, kept as a record.
- **The news reports and company statements** behind the fact card and the spike chart are cited, not reproduced.

## Attribution

Credit "All Systems Operational" by Albert Armea, made with Claude Code (Opus 5.5) and Suno v6, licensed
CC BY-NC-SA 4.0, with a link to https://github.com/Derivative-Work/all-systems-operational.
