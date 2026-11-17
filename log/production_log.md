# Production log

Append-only. One entry per generation, render or analysis step.

## 1. 2026-11-15 — Project setup and inputs

- Brief (rev 106) read with the docs tools; mirrored with `python3 -I scripts/mirror_brief.py <saved read> docs/brief.md` (Ever Present's converter, ids changed).
- Planning chat: `node scripts/fetch_share.mjs https://claude.ai/share/2d5ec79c-6269-49d3-81d6-f350535afa1a docs/planning_chat/planning_chat` → `planning_chat.json` (snapshot "Potential song: All Systems Operational (11/12 M365 outage)", taken 2026-11-15T09:28:56Z, 66 messages, indices 0–71; 4–5, 20–21 and 42–43 are on abandoned branches, 2026-11-13 to 2026-11-15); `python3 -I scripts/chat_snapshot_to_md.py … > planning_chat.md`.
- Suno take: `node scripts/fetch_suno.mjs https://suno.com/s/YPILkHDbsibStgNf docs/suno` (resolves to `suno.com/song/e7994418-…?sh=YPILkHDbsibStgNf`); `python3 -I scripts/suno_clip.py docs/suno e7994418-9310-4096-8663-99aa58d5fc76` → `docs/suno/clip.json`, `docs/suno/lyrics.txt` (copied to `lyrics/as_pasted.txt`). Style prompt and settings in `log/prompts/m1_suno.md`.
- Lyrics as pasted = the brief's v1.2 lyrics verbatim (diffed), less the two "SWAP POINT" markers.
- Audio, copied from `~/Downloads`:
  - `audio/track/All Systems Operational.wav`: the human's Logic master with the hard stops, 48 kHz stereo f32, 239.58 s, sample peak −1.04 dBFS, −13.8 LUFS integrated, LRA 9.5 LU, sha256 `99ac5258…`.
  - `audio/postfilter/all-systems-operational-master-deslopped.wav`: the post-filtered master (human interventions 3), 48 kHz stereo s24, 239.58 s, sample peak −0.57 dBFS, −13.8 LUFS, sha256 `c5688ad7…`.
  - `audio/stems/`: 12 Logic exports of Suno's stems (lead and backing vocals, drums, bass, guitar, keyboard, percussion, strings, synth, other, brass, woodwinds), AIFF 48 kHz stereo s16, 239.58 s each.
  - `audio/extra/Clap 2 - Warm Embers.aif`: the human's added clap track (a Logic loop), AIFF 48 kHz stereo s16, 98.30 s from 0, sha256 `e0cbdec5…`.
- Screenshots: `assets/screenshots/` (9 PNGs and `slack-5a.mov`, H.264 1734×760 with AAC, 15.9 s), copied from `~/Downloads/all-systems-operational-shots/` (human interventions 4). Git-ignored; in the manifest.
- Environment: `uv sync` from Ever Present's `pyproject.toml`/`uv.lock` (renamed) → `.venv` (hard-linked from the uv cache; disk unchanged at 34 GB free); `PUPPETEER_SKIP_DOWNLOAD=1 npm install` (puppeteer 24.43.1; Chrome 148.0.7778.97 already in `~/.cache/puppeteer`).

## 2. 2026-11-15 — Audio checks (CPU only; the GPU is on Ever Present's render)

- Hard stops (`ffmpeg … silencedetect=n=-60dB:d=0.25` on both masters): lead-in silence 0–1.09 s. Stop 1 at 95.06 s: 0.53 s of silence, one clap at 95.59 s (peak −12.0 dBFS), 0.53 s of silence, band back at 96.79 s. Stop 2 ("stay on the—"): 201.80–203.19 s, 1.40 s of silence and no clap. All stems tested (drums, lead, percussion, guitar) are below −91 dBFS through both stops, so the edits are in the stems too.
- Clap track (`silencedetect=n=-50dB:d=0.1`): four claps, at 94.39, 95.59, 96.79 and 98.00 s, 1.20 s apart (two beats at 100 bpm). Only the 95.59 s clap falls in a stop. Its spacing puts it on the grid of the claps before and after, not late; to check against the beat grid at M2. The brief asks for one clap "nudged late" after each hard stop.
- Post-filter vs Logic master (`.venv/bin/python`, numpy): 0-sample lag (60–70 s), equal length; the difference is −36.1 dB below the music overall and −44.3 to −32.5 dB in every 2 s window above −60 dB. In line with Ever Present (−34.4 dB) on the same checkpoint. The sample peak rises from −1.04 to −0.57 dBFS.
- Tempo: librosa beat tracker on the master, 99.4 bpm (the prompt asked for 100). Key: chroma (CQT) against Krumhansl profiles: G minor 0.72, B♭ major 0.54 (relative keys), F major 0.42. Confirm by ear at M1.

## 3. 2026-11-15 — Kits imported (copies; the sibling projects untouched)

- Ever Present people and band: `blender/ep/` (figlib, gait, make_figures, stage_props, figure_sheet, motion_sheet, gb) from commit 726343c; `assets/figures/figures.blend` (library v6, sha256 `a587ce45…`) with `assets/mpfb/assets_pack`, `assets/mpfb/clean` and the MPFB 2.0.18 add-on zip (the blend's textures are relative paths into them). `blender/ep/README.md`.
- Sandbox Rhapsody probes: `blender/lib/sr_kit.py` (f77185c) and `sr_anim.py` (9ff2b2a), `ROOT` changed to `parents[2]`; `config/look.json` = Sandbox Rhapsody's look plus `standby` `#5fe39a` (Not Yet's green probe LED). `blender/lib/README.md`; probe colours in decisions 3.
- Little Switch: `remotion/src/defaultOn/` copied unchanged from `../distillation-allegedly/src/defaultOn` (d335c15), itself an unchanged copy of Default On's rig at 7fc03b7. Default On's own repo isn't on this machine.
- Plan: `docs/plan.md` (milestones M0–M8).

## 4. 2026-11-15 — Outage-report spike sourced; brief rev 113 (human interventions 6)

- Searched for the Nov 12 Downdetector spike (WebSearch, standard then extended; WebFetch on the hits). There's no capture to reuse: Downdetector's own charts are branded, and the brief's guardrail already calls for a made-up, unlabeled outage graph. So O01's spike will be a Remotion chart drawn from reported counts:
  - [GV Wire, Nov 12](https://gvwire.com/2026/11/12/microsoft-outlook-down-for-thousands-of-users-downdetector-shows/), rolling update: 2,400+ at 9:50 a.m. PT; 5,500+ at 9:53; 13,000+ at 9:58; 25,000+ at 10:03; 65,000+ at 10:08; "130,00" (sic, 130,000) at 10:17. Its later figures (550,000 at 11:11, 600,000 at 11:25) aren't corroborated anywhere else, so they're left out.
  - The search's summary attributes 130,000+ Outlook reports around 1:27 p.m. ET to Reuters; [TechRepublic](https://www.techrepublic.com/article/news-microsoft-outlook-outage-130000-reports-2026/) returned 403, so this is unchecked. The brief's fact card already cites the Washington Post for almost 130,000 U.S. reports just after 1 p.m.
  - [Al Jazeera, Nov 13](https://www.aljazeera.com/news/2026/11/13/microsoft-hit-by-global-outages-what-happened-and-why): "at least 43,000 reports of problems with Outlook from users in 72 countries" at about 07:00 GMT Friday; 74 countries and territories within about an hour of the start.
  - [BleepingComputer](https://www.bleepingcomputer.com/news/microsoft/massive-microsoft-365-outage-disrupts-outlook-teams-copilot-worldwide/): "complaints surged Thursday afternoon" (no counts).
  - The creator's #it-self-help thread starts at 12:57 p.m. ET (9:57 PT), inside the climb.
- Brief edited directly (human's directions; rev 106 → 113): the O01 row and the "Opening bookend" paragraph now hold the spike chart, the real screenshots (≤ 3 s, the "No license found" one a placeholder) and the recreated chat post ("no video yet" struck through, play clicked, the song starts on the cut to O02); the faces guardrail gets the creator's name and photo as the one exception. Mirror regenerated: `python3 -I scripts/mirror_brief.py <saved read> docs/brief.md` (diff: those three places and the header only).

## 5. 2026-11-15 — Brief rev 116; licence files (human interventions 7)

- Brief edited directly (rev 113 → 116): the O01 row dates the placeholder capture to Friday, Nov 13, and the post now strikes through "(my last meme about this, I promise)", then "no video yet", before play. The bookend paragraph matches. Mirror regenerated with `scripts/mirror_brief.py`.
- `LICENSE-media.md` (CC BY-NC-SA 4.0, modelled on The Distillation Job's) and `LICENSES/CC-BY-NC-SA-4.0.txt` (copied from it); `LICENSE` (MIT) was added in step 4. `blender/ep/README.md` and `CLAUDE.md` record the relicensed kit. Checked first: the copied Ever Present files hold no sanctuary set, scripture or AI-pastor code, only generic poses, walk, people builder and stage props.

## 6. 2026-11-15 — M3: Remotion screen kit (built by a subagent; reviewed by the agent)

- **Setup:** `package.json` pins Ever Present's versions (remotion and @remotion/cli 4.0.534, react/react-dom 18.3.1, typescript 5.6.3, @types/react 18.3.12; puppeteer 24.43.1); `PUPPETEER_SKIP_DOWNLOAD=1 npm install` (node_modules 771 MB). `tsconfig.json` from Ever Present; `remotion.config.ts` (entry `remotion/src/index.ts`, public dir `remotion/public`, concurrency 2). `npx tsc --noEmit` is clean; Remotion prints a harmless zod version warning.
- **Data:** `config/incident.json`, the brief's block verbatim; every changeable detail reads it.
- **Compositions:** 43 at 30 fps, in `remotion/src/Root.tsx`. Durations are placeholders in `remotion/src/config.ts` until M2.
  - O01 bookend (8.2 s): spike chart, then the real screens (2.6 s), then the recreated post with both strike-throughs and the click on play.
  - Status page in four states: green, investigating, renewed errors, flicker. The flicker is seeded from `config/seeds.json` with salt 23.
  - Lower thirds; the #it-help phone chat, framed and as a bare screen texture; the calendar; buffering freezes; the technical-difficulties card.
  - Little Switch in six states. `SwitchCameo` is wrapped unchanged; strain and sag are wrapper transforms only.
  - Textures: kick-drum head (plus the branch-B LGTM version), table tent, Polaroid (placeholder photo), ON AIR lit and unlit, the 50.3 FM station sign, and the whiteboard in four versions (two fill levels, full, branch C, diff preview).
  - End sequence: disclosure, fact card, end card, final card.
  - Text not dictated by the brief or the human (service names, the invented #it-help names and messages, calendar events, kickers) is listed in the subagent's report and visible on the sheet.
- **Fonts** (OFL 1.1, licence files and sha256 in `remotion/public/fonts/SOURCES.md`): Inter (copied from Ever Present), Work Sans and Caveat (from github.com/google/fonts).
- **Real assets** (git-ignored `remotion/public/real/`, re-created by `render_stills.sh`): the two screenshots, plus `creator_avatar.png`, a 66×66 crop of slack-5.png at (29,1019).
- **Stills:** `remotion/render_stills.sh` → 58 stills in `review/m3/screens/`, then the sheet `review/m3_screens.jpg` (`scripts/contact_sheet.py`, adapted from Ever Present). `npx remotion still … --gl=swangle`, CPU only; no videos rendered.
- **Agent review:** looked at the sheet and at full size at the chat post, spike, status page, whiteboard and fact card. One fix: the spike chart's labels were Pacific while the screenshot captions are Eastern. Now the axis reads 12:50–1:20 p.m., "2 a.m. Fri" and "Eastern time"; the data stay in PT as reported, shifted only at display. This also lines up with the fact card's "just after 1 p.m." (Washington Post). O01a f59 re-rendered and the sheet rebuilt.
- **For a later check:** the fact card's "wider outage followed at 1:26 p.m." (Digital Trends) falls after the spike's 130,000 at 1:17 p.m. ET. The counts likely track the Exchange problems that began at 11:17, but the fact-card check at M7 should confirm the wording.

## 7. 2026-11-15 — Transcription (M1 evidence); stop 1 re-measured

- `cp -r ../ever-present/.venv/nltk_data .venv/ && chmod -R go-w .venv/nltk_data`; then `NLTK_DATA=$PWD/.venv/nltk_data .venv/bin/python scripts/transcribe_vocals.py "audio/stems/0 Lead Vocals.aif" timing/whisper_lead.json`, and the same on `1 Backing Vocals.aif` → `timing/whisper_backing.json` (WhisperX 3.8.6, large-v3; the script is copied from Ever Present; logs beside the outputs). Run on the GPU next to the M3 board renders.
- Lyrics as sung: `log/ai_changes.md` 2. "fail" is sung whole.
- **Correction to entry 2:** stop 1 starts at about 93.9 s, not 95.06. The master in 0.1 s windows: −22 dB through "fail", −34.5 dB at 93.9, −50 dB at 94.1. The 94.39 s clap rings (−28 dB), then it decays to digital silence at 95.06. So three claps fall in the stop (94.39, 95.59 and 96.79 s), then the solo "We're seeing renewed errors" (97.08–98.44 s), then the band. Decisions 4 still holds: one steady clap every two beats.
- Listening clips from the post-filtered master: `audio/check/listen_stop1.wav` (89–100 s), `audio/check/listen_stop2.wav` (196–210 s).

## 8. 2026-11-15 — M3: grey-box sets and lighting board (built by a subagent; reviewed by the agent)

- **Code** (all new; `blender/ep/` and `blender/lib/` untouched):
  - `blender/aso_kit.py`: links the people, puts the Remotion textures on planes, and holds the rain-on-glass, fog and string-light materials, the world and Eevee settings.
  - `blender/poses.py`: the poses the library lacks. They are built at set time from a linked person's rig, re-aimed with figlib.
  - `blender/aso_props.py`: acoustic guitar, banjo, tambourine, the 22" kick drum with the SESSION 503 head, chairs, mugs, server rack, laptops, speakerphone, chargers, evergreens, the lamp post with its outlet box, an umbrella. All blank.
  - `blender/sets.py`: `build(room, state)` for live, cafe, treehouse, park and void.
  - `blender/board.py`; `scripts/board_sheet.py` (from Ever Present); `config/aso_look.json`, holding this video's palette and light levels (`config/look.json` is unchanged).
- **Textures:** `npx remotion still <id> assets/gen/tex/<name>.png --frame=<f> --image-format=png --concurrency=2 --gl=swangle`. That gives kick_head, table_tent, polaroid, onair_lit/unlit, station_sign, whiteboard_full (f300), switch_on/off, and phone_chat (f140, not yet mapped).
- **Board:** `blender -b --factory-startup --python blender/board.py -- --out review/m3/board`. 18 stills at 1280×720, Eevee, 32 samples, 0.5–1.6 s each on the RTX 5090; building each set takes 0.1–25 s, about 3.5 min for the whole board. Shots: O03, O04, O07, O08, O08c, O09, O10, O11, O12, O12c, O14–O18, O19, O20, O22. Sheet: `.venv/bin/python -I scripts/board_sheet.py review/m3/board review/m3_board.jpg 3`.
- **Rooms** (metres):
  - Live room 14 × 10 × 4.6: five tall rainy windows in a dark panelled wall, nothing outside (no plaza), warm practicals, red rugs, no blue light.
  - Cafe 12 × 9 × 3.6: steamed windows, string lights.
  - Treehouse 7 × 6.
  - Park: hill crest, generic skyline 430–490 m away in fog; no Needle, no water.
- **Cast and crowds:** crowds of 20 (live room), 16 (cafe) and 24 (park), and 3 in the treehouse; library people 3, 8, 12, 17 and 22 are the band, 30 the host. Probes at 1.7× scale: green Anthropic, amber OpenAI.
- **Agent review**, three rounds; drafts in `archive/review/m3/board_v1_intermediate/` (`_d1`–`_d7`, `_r1`–`_r10`):
  1. **Faces:** O18's band and O17's crowd were front-lit with readable faces. The light came from bounce under the skylights, and Eevee doesn't support the camera-ray world trick. Fix: an emissive sky dome over a near-black world, the skylights moved behind the band, the whiteboard glowing at 2.4, O18 at −1.0 EV, O17's string lights cut to 5 W practicals at −0.6 EV. Both now read as silhouettes.
  2. **Worship gesture:** the crowds used Ever Present's "raised" pose (open palms overhead), which reads as worship. Replaced in every crowd with clap, clap_open, fist, mug_raise and phone. Only the tambourine player keeps a raised arm.
  3. **Salute/rifle read:** O11's first "push" pose gave single arms extended straight forward and up, which reads as a straight-arm salute or a rifle in silhouette. Rule now at the top of `blender/poses.py`: no arm straight from shoulder to wrist pointing forward or forward-and-up. `push` became a lean-in crush with face-height claps; `fist` is an elbow-down pump; `mug_raise` is an L-shaped toast. O10's host uses a new bent-arm `reach`. Checked at full size by both agents: O09, O11, O17, O20.
- **Open for the final look:**
  - O19's evergreens and fog are flat; the park trees are cones and the drizzle is heavy near the camera.
  - O04's phone has the placeholder screen (the chat texture isn't mapped yet).
  - Faint profiles at frame edges: O04 (band 3 m away, the holder's cheek), O11 (one at the top right), O17 (left and right edges), O12/O12c (side profiles against the wall).
  - Poses needing a figure-library rebuild (`blender/ep/make_figures.py`) for grips and motion loops: clap, mug_raise (mug parented to the hand), push, fist, instrument holds for guitar and banjo, tambourine, kick drum.
  - The probes' folded arms dip into their coasters; the Polaroid photo is a placeholder.
  - O22's home-movie grain and warm grade are post work.

## 9. 2026-11-15 — M2: lyrics as sung, timing map, shot cues, review video

- **One command:** `scripts/m2.sh` (22 s; WhisperX alignment on the GPU for a few seconds, the rest CPU). It runs the four scripts below and rewrites every output, so the map follows the master until M1 locks it. Adapted from Ever Present's M2 scripts (726343c); each header says what changed. No random process here, so no seed is read.
- **Lyrics as sung:** `lyrics/as_sung.txt` = `lyrics/as_pasted.txt` with unique section names, the backing parts in braces (`{Hey!}`, `{we are aware}`), the directions in parentheses, and the stops cut as written: "without fai—" (human interventions 8) and "Please stay on the—". Whisper's mishearings (AI changes 2) are not used as text; they only anchor the windows.
- **Timing map:** `scripts/timing_map.py` → `timing/timing_map.json`, log `timing/timing_map.log`. Inputs in `config/timing.json`.
  - Words: 307 lead words force-aligned (wav2vec2) on the lead stem, one segment per line, in windows from `timing/whisper_lead.json`. Six window overrides: both "Five-oh-three" lines (Whisper wrote "503", or missed it); "We're seeing renewed errors" (the aligner put "We're" in the fade at 93.8 s); "Remember Wednesday?" and "operational?" (the whistle is on the lead stem); the final chorus's "All" (it landed on the build's Hey!). Low scores: "up" ×2, "fine", "it" (short words; the line starts are what the cues use).
  - Echoes: the three pre-chorus echoes aligned on the backing stem: 46.02, 48.35, 50.89 s.
  - Hey!s: 23 on the backing stem. Eight are Whisper's "hey"; eleven are clear onsets after silence; two are onsets through the sustained gang vocal (62.24, 88.69 s). Two are weak and flagged (chorus 1 line 1 at 56.24 s, final chorus line 2 at 186.21 s): check by ear. Where they're clear, the Hey!s fall on beat 4, a beat before the next line.
  - Beats: tracked on the drums stem at 48 kHz, hop 128, in three segments split at the stops. 99.79 bpm to stop 1 (sd 9 ms), 99.99 bpm from stop 1 to stop 2 (sd 11 ms), about 100.5 bpm in the outro (sd 39 ms; it slows, and the drums are out from 214 to 226 s). The M0 figure of 99.4 bpm was the 22 kHz tracker rounding to its 11.6 ms frames. Stop 1 is filled by 12 interpolated beats (0.6005 s): the four claps (94.39, 95.59, 96.79, 98.00 s) land on beats 2 and 4 within 25 ms. Stop 2 inserted time: the outro's grid is 0.21 s off the chorus's. 399 beats, 100 downbeats.
  - Bars: the stomp hits every beat, so bar 1 is anchored on the sung "SYS-" of chorus 1 and of the final chorus. Both anchors agree across stop 1, and they put verse 1, build 1, verse 2, both choruses, the bridge, build 2, both stops and the band's return on downbeats. The outro's bar 1 is the first tracked beat (unchecked). Reliable spans: 1.2–201.8 s and 203.19–214.0 s; cues outside them are on words.
  - Events measured on the master: stop 1 at 93.80 s (the band's fade starts, a downbeat), stop 2 at 201.80 s (silence, a downbeat), sound back at 203.19 s (the whistle), drums in at 16.54 s, band back at 98.62 s (the downbeat after the fourth clap; not 98.0), last vocal 234.94 s, last sound 239.35 s.
- **Shot cues:** `config/shot_cues.json` (O01–O24, checked against the brief) → `scripts/shot_times.py` → `timing/shot_times.json` (song time, video time and 30 fps frames, bar.beat, the snap, marks inside each shot), log `timing/shot_times.log`. Bookend lead-in 8.4 s, so the video is 271.98 s with the post-roll. Musical cuts are on downbeats (up to 0.34 s from the word) or, for O08 and O16, on a beat. O12 and O21 land on the measured stops. Shortest: O21 1.39 s (the stop-2 silence), O13 1.82 s. Longest: O22 31.0 s, O09 28.9 s, O17 28.8 s, O03 19.2 s. Choices for the human in decisions 6–9.
- **Remotion:** BEAT = 18 frames fits (100.0 bpm). Recommended DUR values are in `config/shot_cues.json` `remotion`; `remotion/src/config.ts` is unchanged.
- **SRTs:** `scripts/export_srt.py` → `lyrics/as_sung_lines.srt` (68 cues) and `lyrics/as_sung_words.srt` (337), song time; `--video` writes `_video` copies offset by the lead-in.
- **Review video:** `scripts/m2_review.py` → `review/m2_timing.mp4` (960×540, 30 fps, 271.98 s, 6.6 MB, libx264 CPU; git-ignored, in the manifest). It plays 8.4 s of silence for the bookend, then the post-filtered master with a click on every beat (higher on bar 1), then the silent post-roll. On screen: shot ID, the brief's section, lyric cue and shot text, the cue note, the marks as they happen, the section and the as-sung line with the current word, Hey!s and echoes, bar.beat, song and video time. Intermediates in `timing/check/` (git-ignored). Seven frames checked (O01, O04, O08, O12, O13, O22, O24).
- `scripts/manifest.sh` → 215 files.

## 10. 2026-11-15 — M4 started: O06 fax still, first batch (9 takes; stopped for low memory)

- **Checks first:** the RTX 5090 was idle (361 MiB, desktop only), ComfyUI was not running and its queue was empty, and 33 GB were free on disk.
- **ComfyUI:** v0.42.1 in `~/ComfyUI`, started by the agent with `~/ComfyUI/.venv/bin/python ~/ComfyUI/main.py --listen 127.0.0.1 --port 8188`, and stopped by the agent after the batch.
- **Model:** FLUX.2 [dev], the same files Ever Present used (its `config/models.tsv`, HF revision `ed33133c` of Comfy-Org/flux2-dev). Ever Present logged no hashes, so the agent hashed them (sha256):
  - `flux2_dev_fp8mixed.safetensors` `863a82e4ff950a42a6b0e80bea824828f129eb1a8fbbdbd9e8cb29859127b486`
  - `mistral_3_small_flux2_fp4_mixed.safetensors` `1ee1ff334d78228d73049ef0ee4fcd21c1700536b5a45c06547af057f92463a7`
  - `flux2-vae.safetensors` `d64f3a68e1cc4f9f4e29b6e0da38a0204fe9a49f2d4053f0ec1fa1ca02f9c4b5`
  - 28 steps, euler, guidance 4, 1920×1088, as Ever Present.
- **Scripts:**
  - `scripts/comfy_client.py` is copied from Ever Present (90c999d); only the client id changed.
  - `scripts/stills.py` is adapted from Ever Present's (90c999d). It reads `config/m4_stills.json` and the seeds in `config/seeds.json`, and it drops the reference images and the pick grid. The graph is unchanged.
  - `scripts/m4_sheet.py` is new: a contact sheet with the agent's notes.
- **Config:**
  - `config/m4_stills.json` holds three O06 prompt variants (A: a cluttered desk; B: a low angle with the trading floor behind; C: a wider empty desk) and the O07 fog-tower plate.
  - FLUX.2 [dev] takes no negative prompt, so the brief's negatives (faces, people, logos, brands, text, boat, ship, ferry, water) are written into each prompt as "no …", as in Ever Present.
  - `config/seeds.json` gains `m4_stills`: 41–45, the main seed and the next four.
- **Commands:**
  - `.venv/bin/python -I scripts/stills.py O06_fax_a > log/m4_batch1.log`
  - then, while that was still running, `.venv/bin/python -I scripts/stills.py O06_fax_b O06_fax_c O07_fogtower >> log/m4_batch1.log`. The two shared one ComfyUI queue, so some times include waits.
  - 50–60 s per take when run alone.
- **Stopped:** Claude Code killed the second process for low system memory after B seed 43. ComfyUI held 32 GB of the machine's 38 GB of RAM.
  - B seed 44 was already queued and finished. It was copied from `~/ComfyUI/output/aso/` to `assets/gen/stills/O06_fax_b/O06_fax_b_s44.png`.
  - Not run: B seed 45, all of C, and the fog tower.
  - The agent did not restart the batch. The same command resumes it, since existing takes are skipped.
- **Outputs:** `assets/gen/stills/O06_fax_{a,b}/` (9 PNGs, 25 MB; git-ignored, in the manifest). ComfyUI's own copies are in `~/ComfyUI/output/aso/`. Prompts and seeds are verbatim in `log/prompts/m4_fax.md` and `log/prompts/m4/*.txt`.
- **Sheet:** `.venv/bin/python -I scripts/m4_sheet.py review/m4_fax_sheet.jpg O06_fax_a O06_fax_b --title "…"` → `review/m4_fax_sheet.jpg`. The notes are in `config/m4_stills.json` `review`.
- **Agent review:** every take was viewed at full size, with enlarged crops of the monitor UI, bezels and fax panels.
  - **Kept: 5.** A s41–s45 and B s41, apart from A s41 below.
  - **Maybe: 1.** A s41: the bottom of each monitor has a blurred row of round app icons that reads as an OS taskbar.
  - **Rejected: 3, all from variant B.** B s42, s43 and s44 have silhouetted people on the trading floor behind. They also have a logo-like emblem or badge, and in s44 a near-readable pseudo-wordmark ("FAX … System").
  - Variant B's "trading floor, rows of desks" brings in people. A v2 would need "deserted", or would drop the floor.
  - Every take carries unreadable pseudo-text on the monitors and the fax keys. None reads as a brand.
  - Nothing shows water beyond rain on the window glass (as in the M3 board), and there are no boats.
  - The agent's order is A s45, A s42, A s43. The human picks.
- **Planned image-to-video** (not run; it waits for the human's pick):
  - Model: LTX-2.3 image-to-video, as in Ever Present: ComfyUI template `video_ltx2_3_i2v` (Ever Present's `comfy/api/video_ltx2_3_i2v.api.json` and `scripts/clips.py`, to be copied in). It uses `ltx-2.3-22b-dev-fp8` with the distilled LoRA at 0.5, the Gemma 3 12B fp4 encoder and the ×2 spatial upscaler, all installed. `ltx-2.3-22b-distilled-fp8` is also installed.
  - Format: 1280×720 at 24 fps, two seeds.
  - Length: 5 s for a 4.81 s shot. The page should curl at 2.38 s into the shot, on "fax" (the cue mark); the timing is fitted at the edit.
  - Motion: a locked-off camera; the page slowly curls further up and out of the tray; the monitors flicker faintly; soft rain light drifts across the desk; the lamp stays steady; nobody enters the frame.
  - Memory: LTX is heavier than FLUX in RAM. Run it with nothing else open, or start ComfyUI with a lower RAM cache.

## 11. 2026-11-15 — M4: O06 image-to-video, four LTX-2.3 takes (none locked-off; s41 recommended)

- **Checks first:** 33 GB free on disk; 34 GB RAM available, 8.8 GB swap already in use; the GPU idle (361 MiB); ComfyUI not running.
- **ComfyUI:** v0.42.1, started by the agent with Ever Present's command and no extra memory flags, as Ever Present ran LTX: `~/ComfyUI/.venv/bin/python ~/ComfyUI/main.py --listen 127.0.0.1 --port 8188` (log `log/m4_comfy_clips.log`). One job at a time. Stopped by the agent afterwards; RAM went back to 3 GB used.
- **Scripts and graph:**
  - `comfy/api/video_ltx2_3_i2v.api.json` is copied unchanged from Ever Present (90c999d; sha256 `5d537d56…760718d`). It is the API form of ComfyUI's `video_ltx2_3_i2v` template, Comfy Org, MIT.
  - `scripts/clips.py` is adapted from Ever Present's (up to 9645c9b). The still comes from `config/m4_clips.json`, seeds from `config/seeds.json` by name, and rows go to `log/prompts/m4_fax.md`. Node settings are unchanged.
  - `scripts/m4_clip_review.py` is new, with its frame sheet adapted from Ever Present's `scripts/clip_sheet.py` (6a9070b).
- **Config:** `config/m4_clips.json` is new. `config/seeds.json` gains `m4_clips` (41, 42: the main seed and the next) and `m4_clips_v2` (43, 44, for the one allowed revision).
- **Models** (sha256):
  - `ltx-2.3-22b-dev-fp8.safetensors` `28606c5b5a06ce56f896d4dfcb20f212739e07a68fbe48e53638188449d26450`
  - `ltx_2.3_22b_distilled_1.1_lora_dynamic_fro09_avg_rank_111_bf16.safetensors` (strength 0.5) `31e0c0195fb841bf31af78e8b60858f489e87ddcea4a5239abc80943da65e3ac`
  - `gemma_3_12B_it_fp4_mixed.safetensors` `aaca463d11e6d8d2a4bdb0d6299214c15ef78a3f73e0ef8113d5a9d0219b3f6d`
  - `ltx-2.3-spatial-upscaler-x2-1.1.safetensors` `5f416311fa8172b65af67530758964708d29a317b830d689a51143b7f91913ed`
- **Settings:** the template's two stages (8 + 3 sigmas, euler, CFG 1), prompt enhancer off. 1280×704 (LTX rounds to 32; decisions 10), 24 fps, 5 s = 121 frames, from `assets/gen/stills/O06_fax_a/O06_fax_a_s45.png`.
- **Commands:**
  - `.venv/bin/python -I scripts/clips.py O06 > log/m4_clips.log`: seeds 41, 42. 40.9 s and 19.0 s; 60 s wall time with model loading.
  - Both takes pushed in, so the one allowed revision followed: `.venv/bin/python -I scripts/clips.py O06 --tag v2 --seeds-key m4_clips_v2 --motion "<v2>" >> log/m4_clips.log`, seeds 43, 44. 20.2 s and 18.0 s; 38 s wall time.
  - Wall times are in `log/m4_clips.time`. Prompts (v1, v2) are verbatim in `log/prompts/m4_fax.md`.
- **Memory** (sampled every 2 s): peak 37.0 GB RAM used of 38 (2.0 GB available), swap up from 8.8 to 11.5 GB, VRAM peak 31.9 GB of 32.6. Nothing was killed. Idle ComfyUI held about 32 GB until stopped.
- **Outputs:** `assets/gen/clips/O06/O06_s41.mp4`, `O06_s42.mp4`, `O06_v2_s43.mp4`, `O06_v2_s44.mp4` (git-ignored, in the manifest).
- **Review:** `.venv/bin/python -I scripts/m4_clip_review.py O06 review/m4_fax_clips.jpg review/m4_fax_clips.mp4` → `review/m4_fax_clips.jpg` (frames 1, 30, 60, 90, 121 per take, with notes) and `review/m4_fax_clips.mp4` (2×2 preview, 640 px each; in the manifest).
  - The agent viewed every frame on the sheet at full size, plus crops of the window and the monitors. Camera motion was measured from frame 1 to frame 121 (ORB features and a similarity fit).
  - **All four push in**, despite "locked-off" (v1) and "fixed tripod … no zoom, no push-in" (v2). Scale by the last frame: s41 1.12, s42 1.31, v2 s43 1.09, v2 s44 1.22.
  - **s41, recommended:** a smooth, slow push. The page curls further up and out and keeps its shape. The monitors and the rain on the glass shimmer faintly, the lamp stays steady, and nobody appears. The monitor pseudo-text stays unreadable, as in the still.
  - **Rejected:**
    - s42: a strong push that crops the lamp; the page barely moves.
    - v2 s43: the page stands up, then folds forward like a lid.
    - v2 s44: the strongest push; the page grows tall and the mug leaves the frame.
  - No take shows faces, people, logos or water.
  - Notes are in `config/m4_clips.json` `review`; `kept` is left for the human.

## 12. 2026-11-15 — M4: remaining stills (O06 variant C, O07 fog tower)

- **Checks first:** 33 GB free on disk, 34 GB RAM available, the GPU idle, and nothing else on ComfyUI.
- **ComfyUI:** started fresh by the agent with the same command (log `log/m4_comfy_stills2.log`), then stopped after the batch.
- **Command:** `.venv/bin/python -I scripts/stills.py O06_fax_c O07_fogtower > log/m4_batch2.log`, one process. The model and settings are as in production log 10.
  - 9 takes, 49–70 s each; 483 s wall time.
  - Not run: O06_fax_b seed 45. The task named only C and the fog tower; `scripts/stills.py O06_fax_b` would resume it.
- **Memory** (sampled every 2 s): peak 35.7 GB RAM used (about 2–3.4 GB available) and 11.9 GB swap. VRAM peak 32.1 GB. Nothing was killed.
- **Outputs:**
  - `assets/gen/stills/O06_fax_c/O06_fax_c_s4{1..5}.png` and `assets/gen/stills/O07_fogtower/O07_fogtower_s4{1..4}.png` (git-ignored, in the manifest).
  - Rows are in `log/prompts/m4_fax.md`.
- **Sheets** (notes in `config/m4_stills.json` `review`):
  - `.venv/bin/python -I scripts/m4_sheet.py review/m4_fax_sheet.jpg O06_fax_a O06_fax_b O06_fax_c --title "…"` → `review/m4_fax_sheet.jpg` (14 takes).
  - `.venv/bin/python -I scripts/m4_sheet.py review/m4_fogtower_sheet.jpg O07_fogtower --cols 2 --title "…"` → `review/m4_fogtower_sheet.jpg`.
- **Agent review:** every take was viewed at full size, with crops of the fax panels and the tower bases.
  - **O06 C:** keep s45 (pick 1), s42 (pick 2) and s44; maybe s41 and s43.
    - C is wider, so the fax is smaller than in the picked A s45.
    - s41 and s43 have upright pages with lines of unreadable pseudo-text. s43 also has a small orange badge-like label on the fax.
    - No people, logos or boats.
  - **O07 fog tower:** keep s44 (pick 1) and s43 (pick 2); maybe s41 and s42.
    - s41's top makes a cross-like silhouette. s42 has a pagoda roof and graffiti-like marks.
    - None looks like the Space Needle: no saucer, only a plain column with a small platform.
    - The tops are clearer than "mostly hidden in fog" asked for; the fog could be thickened at the grade.
    - No water, no skyline, no people.

## 13. 2026-11-15 — M5: Remotion durations set; the animatic's Remotion pieces rendered

- **Checks first:** the RTX 5090 idle (361 MiB), 34 GB RAM available, 33 GB free on disk. Remotion runs on the CPU (`--gl=swangle`, concurrency 2).
- **Durations:** `remotion/src/config.ts` now takes `DUR` from `config/shot_cues.json`: the M2 `remotion.DUR_s` block (approved, human interventions 9) and the post-roll (end card 6 s, final card 3 s, fact card 15 s). The M3 placeholders are gone. It also reads `timing/shot_times.json` for exact shot lengths (`shotFrames`) and cue frames (`mark`), as Ever Present's config did.
- **Components** (small changes, defaults unchanged so the M3 compositions still render as before):
  - `LowerThird`: `inAt` (enter on a cue), `echoAt` (each echo on its sung frame), `tickAt` (the uptime ticker settles on its cue).
  - `CaptionOverlay`: `at`, `corner`, `size`. `PhoneChatScreen`: `askAt` (the question arrives on "is email down"). `SwitchPlane`: `strainAt`. `Whiteboard`: `reveal`, each segment written in on its bridge line.
  - New `components/M5.tsx`: `LiveOverlay` (O11: viewer count, chat flood on the Hey!s, Switch straining in a small inset; invented handles) and `DisclosurePanel` (O17, decisions 7). The disclosure text is the brief's (`Cards.tsx`).
- **Compositions:** `M5-*` in `Root.tsx`, each its shot's exact length, events on the M2 cue frames (O02 row flips at 4.86 s song time; O05 drains to empty on "empty"; O08 echoes on 44.75/47.16/49.51/50.91 s; O13 card then the red row on "errors"; O18 board lines on their sung lines).
- **Command:** `scripts/m5_remotion.sh` (new; adapted from Ever Present's, 9301de4) → `renders/m5/remotion/`: 13 h264 files (full-frame shots, end cards, the O04 phone screen at 540×1170 and the O18 whiteboard at 1200×750 as textures) and 11 ProRes 4444 overlays with alpha, all at `--scale=0.5`. 3 min 48 s wall time; per piece in `log/render_logs/m5_remotion.log`.
- **Checked** at single frames before the run (scratchpad stills): the O11 overlay (the chat column first overlapped the Switch inset; shortened), the disclosure panel, the O08 lower third, the whiteboard at frame 470 and the phone screen.

## 14. 2026-11-15 — M5: pose fixes; Blender shots rendered with motion

- **Poses** (`blender/poses.py`; human interventions 8, "hands held to their heads as if confused"):
  - `push` (O11) and `clap_open` (O12's clapper) now clap at chest height, not face height.
  - `fist` lifts the fist clear of the head on a bent elbow (upper arm out and a little up, forearm upright). From behind, the old fist beside the head also read as a hand at the head.
  - No arm points straight forward or forward-and-up; claps are at the chest. Checked at board size (`blender/board.py --only O11,O12c`, scratchpad) and in the animatic.
  - New for animation: `key_claps` (claps keyed on given frames; `wide` opens to `clap_open`), `key_mugs` (a lowered mug pose and the toast keyed on given frames; the mug is now parented to the hand bone) and `still` (a frozen copy of a library person, for the freezes).
- **Script:** `blender/animatic.py` (new; adapted from Ever Present's `blender/shots.py`, 9301de4). It builds each shot from the M3 board's room, state and camera (`board.FRAMES`), adds a camera move and keys the cued events on the cue frames from `timing/shot_times.json`. Per shot in decisions 11:
  - claps on beats 2 and 4 of the grid (O03 from the drums' entry, O09, O11, O17, O19b, O20);
  - O10: Switch ON and ON AIR lit at 85.38 s;
  - O12: frozen, with the late clapper closing on 94.39 and 95.59 s (the 96.79 s clap is the cut) and Switch dropping as ON AIR goes dark;
  - O15: the LED dims on "song" (115.40 s) and is back on "(It wrote it anyway)" (117.04 s);
  - O16: the bulb cascade from 119.05 to 121.48 s, with the strand lights keyed out;
  - O17: mugs up on the four Hey!s;
  - O18: the Remotion whiteboard as a movie texture;
  - O19: two parts (decisions 11);
  - O21: frozen, Switch drops at 202.42 s;
  - O22: one walker up the path and over the crest.
  - Small fix to `blender/sets.py`: optional `clapper_at`/`clapper_face` state keys (O12 only; the board's defaults are unchanged).
- **Settings:** 960×540, 30 fps, Eevee, 8 samples, JPEG q92. No random process beyond the sets' seeded ones (`config/seeds.json` main 41).
- **Command:** `/usr/bin/time -v blender -b --factory-startup --python blender/animatic.py -- --out renders/m5/blender` → 19 sequences, 6,957 frames (O08c's 72-frame cutaway and O19 in two parts included).
  - 20 min 31 s wall time; per shot 4–178 s, about 0.15–0.2 s a frame (log `log/render_logs/m5_blender.log`).
  - Peak: Blender 4.4 GB RSS; system RAM 8.5 GB used of 38; VRAM 3.4 GB (sampled every 2 s, `log/render_logs/m5_blender_mem.log`).
  - The sequences were then moved to `renders/m5/frames_blender/` (frame sequences stay out of the manifest, as `scripts/manifest.sh` intends); the script's default is now that path.
- **Re-renders after review:**
  - O20/O21: the lamp post with Switch had left the frame. O20's push was shortened. 155 s (`m5_blender_r2.log`).
  - O12: the clapper was unreadable. First the board's O12c camera, then the clapper side-on against a window with wider claps (`m5_blender_r3.log`, `m5_blender_r4.log`; 13 s each).
  - Superseded sequences are in `archive/renders/m5/frames_blender_v1/` (O12, O12_r2, O12_r3, O20, O21).
- **O07t:** `blender … -- --only O07t` → `renders/m5/O07t.png`, the server rack on a transparent film for the fog-tower alternate.
- **Tests before the run** (scratchpad, `--frames`): every shot at 3–4 frames. Fixes made before the full run:
  - O04's camera now eases toward the phone; with the old push, the phone slid out of frame and its screen couldn't be pinned.
  - O14's push was shortened (it cropped the probes).
  - O22's walker stays on the gravel path, which floats up to 0.5 m over the slope near its far end. Below it, his legs were hidden.

## 15. 2026-11-15 — M5: the animatic assembled and reviewed; the two O07 excerpts

- **Script:** `scripts/animatic.py` (new; adapted from Ever Present's, 9301de4). Every shot is exactly its `shot_times.json` frame count. Frames are composited in numpy:
  - the Remotion overlays (alpha);
  - O04's phone screen pinned to the Blender phone: the bright quad found per frame, corners smoothed over 3 frames;
  - O06's clip;
  - O08's inserts;
  - O19's cross-fade;
  - O22's warm grade and grain from "Remember Wednesday" (208.52 s; grain seeded from `config/seeds.json` main 41).
  - A small label at the top centre gives each shot's ID and source.
  - The master goes under it from 8.4 s (`adelay`), with silence after the music.
- **Commands:**
  - `.venv/bin/python -I scripts/animatic.py` → `review/m5_animatic.mp4`: 960×540, 30 fps, h264 + AAC 192k, 8,699 frames = 289.97 s, 96 MB. 62 s wall time, 5.2 GB peak RSS. Log: `log/render_logs/m5_assembly.log`; sources in `renders/m5/m5_animatic_sources.json`; segments in `renders/m5/segments/`.
  - `… --excerpt O05:O08 --o07 server --out review/m5_o07_server.mp4` and `… --o07 fogtower --out review/m5_o07_fogtower.mp4`: 722 frames, 24.07 s each (video 39.67–63.73 s, with audio).
  - `.venv/bin/python -I scripts/m5_sheet.py review/m5_animatic.mp4 review/m5_animatic_sheet.jpg` (new): one frame per shot and per end card, 27 frames.
- **Per-shot sources:**
  - Remotion: O01, O02, O05, O13, O23, O24 and the end cards.
  - Blender motion: O03, O04 (+ the Remotion screen), O07, O08 (+ the phone and treehouse inserts), O09, O10, O11, O14–O20, O22.
  - Blender freezes: O12, O21.
  - Clip: O06 (`O06_s41`, cropped to fill from 1280×704, native speed from frame 0; nothing to align, decisions 11).
  - O07 alternate: the fog-tower still with a slow push.
  - No shot is a held still, except the O07 alternate, which is a still by design.
- **Checks:**
  - **Cuts:** frames on both sides of every cut. The label and picture change exactly on each shot's `start_frame`, so every cut is on its cue to the frame.
  - **Audio:** the master is cross-correlated at 36.27 s song time against the animatic (44.67 s) and the excerpt. Lag 0 at 8 kHz.
  - **Events checked on frames:**
    - O01's two strike-throughs and the click on play.
    - O02's row flip.
    - O04's question, then its +1.
    - O08's reply and the cutaway.
    - O09's ticker at 99.9%.
    - O10 before and after the flip.
    - O12's clap in and out, with ON AIR dark.
    - O13's card, then the red row.
    - O15's LED dimmed and back.
    - O16 dark after the cascade.
    - O17's mugs up and the disclosure panel (122.65–140.65 s).
    - O18's board lines.
    - O19's cross-fade.
    - O21's Switch before and after the drop.
    - O22's grade.
  - **Guardrails:** Blender frames viewed at full size (O03, O04, O09, O11, O12, O14, O16–O22).
    - No arm points straight forward. Claps are at chest height. Fists are clear of the head. No open palms held high.
    - The cafe's toast arm reads as out to the side.
    - No water or boats. No tower in the park.
    - Still open, as at M3: faint side profiles at O17's left edge, and the band's dim faces in O09/O18. The park's people are lit and coloured, not silhouettes, as on the approved M3 board; at 540p the band's faces are a few pixels.
  - **Fixes from this review:** O12 (camera and clapper) and O20/O21 (lamp post), production log 14.
- **Weak, for the human:**
  - O12's clap is visible but small under the freeze's dimming.
  - O15's LED dim is subtle: the dome and iris lose their glow; the iris keeps its green base colour.
  - O19's first second is near black (the closed door from inside).
  - O22's walker hasn't quite gone over the crest by the cut.
  - The O04 phone text can't be read at 540p.
  - The O07 alternate's server is a flat cut-out on the lawn with a drawn shadow.
- `scripts/manifest.sh` → 303 files.

## 16. 2026-11-15 — M5b: the music map

- **Why:** the human finds the M5 animatic slow and dry (human interventions 13; decisions 12). Cuts, camera and light in M5b follow this map.
- **Script:** `scripts/music_map.py` (new; reads the stems as Ever Present's `scripts/vocal_env.py` does). Inputs: the 12 stems, the master, the clap track and the M2 grid in `timing/timing_map.json`. No random process, so no seed.
- **Command:** `.venv/bin/python -I scripts/music_map.py --plot` → `timing/music_map.json`, `review/m5b_music_map.png`, log `timing/music_map.log`. 5 s on the CPU.
- **What's in it:**
  - Per-bar energy (101 bars) for the master and every stem, in dB and 0–1.
  - Hits on the grid, each with its beat, bar.beat and offset:
    - kick: 497, 240 of them "main" (on the beat and strong); the rest are 8th-note pickups.
    - tambourine: 439, on the percussion stem.
    - guitar strums: 434, with a count per bar.
    - lead syllable onsets: 450.
    - the four stop-1 claps from the clap track.
  - Backbeat list: beats 2 and 4 wherever the drums play (157 beats).
  - Envelopes at 30 fps: lead, backing (the gang swell), drums, mix.
  - The stops, copied from M2.
- **Hey!s:** all 23 cross-checked on the backing stem. 21 are clear onsets (rise 8–37 dB).
  - The two M2 flagged are still weak. At 56.24 s the rise is 6.4 dB and the level step +0.9 dB: the gang sustains through it. At 186.21 s the rise is 8.4 dB, the step +6.4 dB.
  - Two more are soft (rise under 8 dB, no level step), at 124.69 and 129.24 s, but Whisper heard "hey" at both.
  - Where they're clear, the Hey!s sit on beat 4 or about 0.25 s after beat 3 or 4 (an 8th late).
- **Limits:**
  - The claps can't be told from the stomp in the drums stem: the stomp is broadband and hits every beat, and no band shows a steady 2-and-4 accent (`beat_profile`). The animation claps on the backbeat list, as M5 did.
  - The kick band also catches the 8th-note pickups, so only the "main" kicks drive bumps and the kick foot.

## 17. 2026-11-15 — M5b: the coverage plan

- **Script:** `scripts/coverage.py` (new) → `config/coverage.json` and `docs/coverage.md` (the readable table). Inputs: `timing/music_map.json` and `timing/shot_times.json`. No random process.
- **Command:** `.venv/bin/python -I scripts/coverage.py`.
- **Result:** 94 shots, 93 cuts (M5: 27 shots). The O-shot boundaries stay on the M2 cues. Same 8,699 frames and end order as M5.
  - Cuts per section: stomp-clap 4 (plus O03's two intro shots), chorus 1 8, post-chorus 1 4, build 1 8 (O10 plus seven in O11), verse 2 6, chorus 2 8, post-chorus 2 4, bridge 5, build 2 5, final chorus 10, outro 8.
  - Choruses cut every 1–2 bars, on downbeats or Hey!s. Verses and the bridge cut every 2 bars. Both builds speed up into their stops: bars, then half bars, then single beats (O08e–g, O11c–g, O19c–e, O20g–j).
  - The freezes O12 and O21 hold one angle. O21's angle is O20's last shot (O20j), so the stream freezes on the frame it was showing.
  - The longest hold in the music is O02 (7.27 s, Remotion). The longest Blender hold is O19a (5.8 s, M5's door move).
- **Cuts:** every cut is on a downbeat, a beat, or a Hey!, with three exceptions:
  - O17i cuts on the sung "Five-oh-three" (140.94 s), as M2 marked it.
  - M5's O08 insert boundaries and O19's dissolve keep M5's frames.
  - The weak Hey! at 56.24 s isn't used as a cut; O09's first shot runs to the next downbeat.
- **Cameras:** 62 presets across the five rooms, listed in `config/coverage.json` `cameras`. Some are fixed. Others are found per shot: a crowd member by pose, with a clear line to their hands or head, or the walker, tracked.
- **Camera test:** `blender -b --factory-startup --python blender/coverage.py -- --still --out <scratchpad>` rendered one frame per shot (83 Blender shots, 4 min 42 s). The script is logged in the next entry. Fixed from the test:
  - Hands closes were black or blocked. The camera now aims at the hand bones and checks for a clear line, trying either side.
  - The backs of heads were too close (the frame was black). The camera is now 1 m back, with the head in a third of the frame.
  - Faces in the mids and closes: the backing singer's profile read as a face, so it was replaced by a close on the guitar. The tambourine closes went to 85 mm, aimed at the tambourine. The mids and closes on people get darker exposure (−0.3 to −1.3 stops, more in the cafe, whose band is side-lit). The cafe's backs-of-heads shot no longer racks to the band.
  - O11c: the crush fills the floor in front of the kick, so its kick close is an oblique angle from the right.
  - O17e's mug close was replaced by the mugs from behind, from the other side. O17k's steamed window read blank, so it was replaced by the string lights.
  - O08d's console close was replaced by a view over the host's shoulder to the band.
- **Spare presets, not used:** Switch's conduit, the treehouse skylight, the probe's mug with steam.

## 18. 2026-11-15 — M5b: camera, light and ambient motion (`blender/coverage.py`)

- **Script:** `blender/coverage.py` (new). It renders every Blender shot in `config/coverage.json`.
  - Each O-shot is built once, as M5 did (`blender/animatic.py` `shot()`), with all of M5's cued events. Then the M5b layers are keyed on that build's timeline, and each of its shots renders its own frame range through its own camera.
  - The freezes (O12, O21) get no M5b layers.
- **Seeds:** every random draw is a `gb.rng(name)` stream off `config/seeds.json` main 41: `m5b_cam_<shot>`, `m5b_crowd_<O-shot>`, `m5b_band_<O-shot>`, `m5b_onair_O11`, `m5b_lamp_O20`.
- **Camera** (keyed every frame):
  - Each shot's preset and move, eased: a push, a truck, M5's own keys, or tracking the walker. The builds push faster.
  - Handheld drift: three sines per channel at 0.12–0.75 Hz. Position drifts up to 1.4 cm on wides and 0.6 cm on closes; rotation up to 0.22° on wides and 0.45° on closes. None on the freezes, on O20j (it matches O21) or on O04 (its phone screen is pinned in the edit).
  - A 7 mm drop and a 0.18° nod on each main kick, decaying over about 70 ms, scaled by the hit and the bar's drums energy (half that on closes).
  - Eevee depth of field on the closes and mids (f/1.8–2.8). The live room's and the park's backs-of-heads shots, the mugs and the treehouse table rack from the foreground to the band or the whiteboard, 0.6 s in, over 0.4 s.
- **Light:**
  - Practicals (the live room's bulbs and lamp, the cafe's strand and hub lights, the bulb emission) pulse with the main kicks, ×0.8 to ×1.34.
  - The window lights (the sun in the park) lift ×1.55 on every Hey!, decaying over 0.22 s.
  - Haze, as an Eevee volume (density 0.022 in the live room, 0.007 in the cafe, 0.015 in the treehouse), with a spot through each window. The spots light little but the haze, so the beams show.
    - Cost: the O09 stills rendered in 0.4 s a frame with the haze; a sequence test ran at about 0.2 s a frame.
    - It doesn't light the faces: an A/B with and without (scratchpad) showed the same faces; the beams read as a glow, not hard shafts.
  - ON AIR flickers through the last beat and a half before stop 1 (from beat 39.3), more off than on as it nears 93.80 s. Before stop 2, the park lamp flickers and Switch strains on his box (from 199.41 s).
  - "Service has been restored" (170.57 and 175.39 s): the door light ramps up in O19a, and the sky (sun) in O19b.
  - The cafe's string lights chase the lead vocal: each sung syllable (the music map's lead onsets) sends a pulse out from the hub along every strand, 0.9 s to the hooks. O16's cascade still puts each bulb out on M5's frame.
- **Ambient:**
  - Rain streaks run down every pane: the window shader's streak texture is keyed.
  - The drizzle falls at 3.2 m/s, looped with a copy stacked above.
  - Three fog cards drift across the park's skyline.
  - Steam rises off the probes' mugs (an animated noise on crossed planes).
  - The umbrella turns slowly on a pivot at the hand.
- **Test** (`--subs O11f,O11g,O16a,O09b,O20i,O17c`, scratchpad): 2 min 20 s, 4.5 GB peak RSS, about 0.2 s a frame.
  - Checked on frame strips: ON AIR flickering, the bulb cascade from the hub, the claps, the mugs going up on the Hey! and coming down, the lamp and Switch before stop 2, the drizzle.
  - Frame-to-frame change (mean difference 1.4–4.5 out of 255) shows the drift and the kick bumps without jumps.
- The people motion in the same script is logged in the next entry.

## 19. 2026-11-15 — M5b: first-pass motion for the people (`blender/coverage.py`)

- **Crowd** (every crowd member, the umbrella holder too; seeded per person, `m5b_crowd_<O-shot>`):
  - A bounce on the half notes (1.8–4.8 cm) and a side-to-side sway (1.2–3.4°), both on the grid with each person's own lag (−0.14 to +0.21 beat), scaled by the bar's mix energy.
  - A surge toward the band (10–32 cm) through the choruses and builds, eased over a bar; they settle back in the verses.
  - A small hop (2–7 cm) and a forward lean (up to 1.5°) on each Hey!.
- **Claps:** each clapper gets their own copy of M5's clap rig and keys (claps on the backbeat), shifted by their own lag of −1 to +3 frames. Before this, every clapper of one library person clapped in unison. O20 and O19b have 10 such clappers; O09 6; O17 7.
- **Band** (`m5b_band_<O-shot>`):
  - A bob on every beat (0.8–1.8 cm and a 1.2° nod), on half notes in the bridge.
  - The four singers lean 7° into their mics on each Hey!; the mic stands no longer follow the singer.
  - The kick player is a local copy of the library person, with his own copy of the library's loop. His right leg lifts the foot 13 cm two frames before each main kick and drops on it. The first try had the signs reversed and pushed the foot into the floor (checked on bone positions, then fixed).
  - The tambourine shakes on the percussion hits (above 0.35 strength).
- **Kick closes reframed:** from the front, the foot was hidden behind the drum. The kick closes now look from the player's right, low, so the foot on the pedal side and the SESSION 503 head share the frame (O03c, O08e, O09d, O11c, O14b, O17a, O19c, O20d; checked on stills).
- **Pose rules:** nothing here changes an arm pose. The sway and lean turn whole people about their feet; the claps and mugs are M5's poses. `blender/poses.py` is unchanged.
- **Not done (M5c):** strumming, the banjo hand, the tambourine arm, fist pumps on the Hey!s, the walk-off's planted feet, singing heads. The library's own sway loops still run under all of it.

## 20. 2026-11-15 — M5b: rendered, assembled and reviewed

- **Checks first:** the RTX 5090 idle (361 MiB), 34 GB RAM available, 32 GB free on disk.
- **Blender:** `/usr/bin/time -v blender -b --factory-startup --python blender/coverage.py -- --out renders/m5b/frames` → 83 shot sequences, 6,405 frames (960×540, Eevee, 8 samples, JPEG q92).
  - 21 min 36 s wall time, per O-shot 4–219 s; about 0.2 s a frame with the haze (log `log/render_logs/m5b_blender.log`).
  - Peak: Blender 4.4 GB RSS; system RAM 11.1 GB used of 38; VRAM 3.4 GB (sampled every 5 s, `log/render_logs/m5b_blender_mem.log`).
  - Frames: 521 MB in `renders/m5b/frames/` (out of the manifest, like M5's).
- **Assembly:** `scripts/m5b_animatic.py` (new). It reuses M5's `scripts/animatic.py` composites: overlays, O04's pinned screen, O06's clip, O08's inserts, O19's dissolve, O22's grade, the end sequence. Each Blender O-shot is now the concatenation of its shots. The label names the shot and its angle.
  - `.venv/bin/python -I scripts/m5b_animatic.py` → `review/m5b_animatic.mp4`: 960×540, 30 fps, h264 + AAC 192k, the post-filtered master, 8,699 frames = 289.97 s (M5's length and end order). 108 MB. 1 min 4 s, 5.2 GB peak RSS. Logs: `log/render_logs/m5b_assembly.log`, `m5b_assembly_final.log`. Segments in `renders/m5b/segments/`.
  - `… --share` → `review/m5b_animatic_share.mp4` (h264 650 kb/s, AAC 128k): 25.0 MB.
  - `… --sheet` → `review/m5b_coverage_sheet.jpg`: one frame per shot (its middle), with its id, length and framing; 94 tiles.
  - M5's outputs (`review/m5_*`, `renders/m5/`) are untouched.
- **Checks:**
  - **Cuts:** `… --check` (`log/render_logs/m5b_cut_check.log`).
    - For all 93 cuts, the review label changes on the planned frame. For 91 of them, the biggest picture change within ±2 frames is that frame too.
    - The two exceptions are ON AIR flickering on and off 2 frames into O11g, and 1 frame before O12a's cut. The cut itself is on the frame.
    - O19b is M5's dissolve.
  - **Audio:** cross-correlated against M5's animatic at 40–50 s: lag 0.
  - **Events:** each checked on frames in the shot that covers it:
    - O03's lower third; O04's phone screen (pinned); O08's echoes, reply and cutaway; O09's 503 head and uptime ticker.
    - O10's Switch and ON AIR; O11's viewer count, chat and inset, with ON AIR flickering in O11g; O12's freeze.
    - O14's table tent and Polaroid; O15's LED; O16's cascade from the hub (O16a) out the strands (O16b).
    - O17's mugs on the Hey!s (O17b–e) and the disclosure panel over O17a–h; O18's whiteboard lines.
    - O19's lower third back to green; O20's umbrella, Switch straining and the lamp; O21's freeze on O20j's angle; O22's grade, Switch OFF and the walker.
  - **Guardrails:** every Blender shot viewed at full size (960×540), 122 frames (two each for the shots with people), in 2×2 grids (scratchpad).
    - No arm points straight forward or forward-and-up; claps are at the chest, and the fists are M5's bent-elbow pumps.
    - No hand rests at a head; no open palms held high. The tambourine is held up in the library's raised hand (approved at M3).
    - No water, boats or tower: the skyline is the generic boxes in fog.
- **Fixes from this review** (14 shots re-rendered: `--subs O03e,O08g,O09c,O09g,O11d,O11f,O17c,O17e,O17g,O17l,O18b,O18c,O18e,O20g`, 4 min 30 s, `log/render_logs/m5b_blender_r2.log`; then O20g, `m5b_blender_r3.log`). Superseded frames are in `archive/renders/m5b/frames_v1/` and `frames_v2/`.
  - The racks to the band brought its faces into focus. The live room's backs-of-heads shots now rack past the band to the rain on the glass. The cafe's mugs rack to the glass. The cafe's backs-of-heads shot doesn't rack.
  - The mids over the crowd now focus on the heads in front, with the band soft.
  - The treehouse's whiteboard mid, side and table shots are 0.5–0.8 stops darker.
  - The park's backs-of-heads shot (O20g) looked over a woman's shoulder at the band, whose faces are lit in the park. It now frames heads and a fist against the fog and the skyline, with the band out of frame.
- **Still open (for the human, decisions 14):** faces that are dim but present, as on the M3 board, in the wides and some mids:
  - the band in the live room's wides and the treehouse;
  - the cafe crowd's sideways-turned heads (O17c, O17d);
  - the guitarist at the edge of O09g after its rack;
  - blurred band faces behind the park's banjo close (O20f).
- `scripts/manifest.sh` → 337 files.

## 21. 2026-11-15 — M5c: holds, grips and stem-driven performances (code and tests)

- **Why at set time, not a rebuild:** decisions 15. Nothing in `blender/ep/` or `assets/figures/figures.blend` changes.
- **Code** (all new):
  - `blender/perf.py`: per-person copies, an FK/IK body solver (two-bone IK for arms and legs, as `blender/ep/gait.py` does the walk), keying, and the pose-rule check.
  - `blender/perf_band.py`: the five holds and performances. Guitar: fretting hand on the neck, sliding chord positions per bar (seeded `m5c_chords`); strumming hand on eighths, crossing the strings on each strum onset (`hits.strums`), ghost strokes between, scaled by the bar's guitar energy. Banjo: fretting hand; picking fingers on 16ths, from the guitar stem's energy. Kick: footboard and beater on every kick hit above 0.4, heel lift on the main kicks, claps on the backbeat. Tambourine: shakes on the percussion hits above 0.35, slaps into the left palm on 2 and 4. Lead singer: hand on the stand, head and upper body from the lead envelope, a nod per syllable. All standing players: a bob on the beat (half-time in O18), a weight shift, breathing, lean-ins on the Hey!s and with the backing envelope, feet planted.
  - `blender/perf_crowd.py`: every crowd member keyed per person (`m5c_crowd_<build>`): half-note bounce with their own lag, sway, chorus lean and a 2.5–6 cm surge (hips, feet planted), Hey! hops for some, stomps on the main kicks of beats 1 and 3 for a third, claps at chest height with their own lag (−1 to +3 frames; about half of the standing people join in the choruses), fist pumps on the Hey!s, mug toasts on the cafe Hey!s (the mug in front of the shoulder). O22's walker: `gait.py`'s planted-foot walk, 0.49 m/s, 1.45 steps/s, along M5's 15.2 m path.
  - `blender/perf_props.py`: kick drum, pedal and beater, mic stands at each singer's mouth, the tambourine.
  - `blender/coverage_m5c.py`: runs M5b's `blender/coverage.py` with all of this, band-relative camera presets, cameras aimed at the solved pose, and the freezes holding the performers' poses at the stop (seeded as the shot before, so O20j's last frame matches O21).
  - `scripts/coverage_m5c.py` → `config/coverage_m5c.json`, `docs/coverage_m5c.md`: nine close swaps, cuts and frames asserted unchanged. Command: `.venv/bin/python -I scripts/coverage_m5c.py`.
  - `blender/perf_sheet.py`: the performance sheet and a frame-timing check. `scripts/m5c_animatic.py`: assembly.
- **Tests** (stills in the scratchpad, `--still` at mid, first and last frames): the holds from the front and side; every swapped close; O20j's last frame against O21a's first (same poses); O12a, O22c, O22e.
- **Fixed from the tests:**
  - The kick player's toe reached the batter head's plane: ankle and toe moved back 4 cm.
  - Fists pumped 0–3 cm above the head's top: lowered 11 cm.
  - O11c kept M5b's camera override (a kick close): overrides are now dropped on swapped shots. M5b's spare `switch_cord` aimed above Switch: re-aimed.
  - The beater close first hid the beater behind the shoe: now from above the pedal. The fret close showed the banjo player's chin: now from below the neck. The lean-in from behind first framed only the back of the head, then a crowd face: now from below, the head and mic against the dark upper wall. The kept tambourine close aimed at where the tambourine was held up in M5b: now band-relative.
  - The walker's foot check measured against the hill below the crest: now the plank only.
- **Timing check** (O09, whole build, by frame): the beater is most forward on the kick's frame for 48 of 58 kicks and within one frame for all; the strumming hand crosses the strings on the onset's frame for 39 of 67 strums, within one frame for 63 (the rest are 16th-note onsets between eighths); the tambourine is lowest one frame before 9 of 9 slaps.
- **Walker:** feet planted on the plank, at most 3.2 mm of movement in a stance frame (mean 0.07 mm).

## 22. 2026-11-15 — M5c: first full render and review (superseded)

- **Checks first:** the RTX 5090 idle (363 MiB), 34 GB RAM available, 31 GB free on disk.
- **Command:** `/usr/bin/time -v blender -b --factory-startup --python blender/coverage_m5c.py -- --out renders/m5c/frames` → 83 shot sequences, 6,405 frames (960×540, Eevee, 8 samples, JPEG q92), 318 MB.
  - 23 min 40 s wall time (M5b: 21 min 36 s); per O-shot 4–221 s; the performances add 1–5 s per build.
  - Peak: Blender 5.4 GB RSS; system RAM 8.6 GB used; VRAM 3.45 GB (sampled every 5 s).
  - Logs: `log/render_logs/m5c_blender_v1.log`, `m5c_blender_mem_v1.log`, `m5c_pose_check_v1.log`.
- **Pose check (every solved frame, 330 figures):** no straight forward arm, no hand within 0.20 m of a head (closest 0.35 m: the banjo's fretting hand). One crowd fist cleared the top of the head by 1 cm on 4 frames over three builds at Hey!s.
- **Review** of every Blender sub-shot at full size, two frames each (2×1 grids in the scratchpad). Found:
  - Claps: at the closed frame the fingers of the two hands crossed into each other (O03d, O08f, O19d and the other hand closes). The hands now meet with a 5 cm half-gap, pointing forward, not inward.
  - O09d (the lean-in from behind): the singer's ear and cheek edge, and a dim face low in the background. Moved more directly behind and 0.4 stops darker.
  - O09h (fretting hand): the singer's blurred face behind the hand. Now looking down past the hand to the floor.
  - O14b: the probe's mug floated 1.8 cm over the table (M3's placement; the close made it show). Set down.
  - O20g: with the fists lower, M5b's aim showed only sky. Aimed lower (heads and fists against the skyline); logged in `docs/coverage_m5c.md`.
  - O20h: the strumming hand lay against the guitar's top. The strum point is 1.5 cm further out.
  - The fist pump is capped 13 cm below the top of the head.
- **Unchanged and seen to work:** the band holds in every room, the kick pedal and beater, the tambourine, the mic heights, the toasts in O17b, the freezes (O20j's last frame and O21a's first match), the walker's planted feet.
- Superseded frames: `archive/renders/m5c/frames_v1/`.

## 23. 2026-11-15 — M5c: rendered, assembled and reviewed

- **Fixes after the first render** (entry 22), checked on stills first. Two went back: O20g re-aimed lower showed the park band's lit faces, so it keeps M5b's camera; the first fret-close fix framed the floor without the hand, so it now looks down onto the hand on the neck.
- **Checks first:** the RTX 5090 idle (363 MiB), 33 GB RAM available, 30 GB free on disk.
- **Blender:** `/usr/bin/time -v blender -b --factory-startup --python blender/coverage_m5c.py -- --out renders/m5c/frames` → 83 shot sequences, 6,405 frames, 317 MB in `renders/m5c/frames/` (out of the manifest, like M5b's).
  - 23 min 51 s wall time. Peak: Blender 5.5 GB RSS; system RAM 8.5 GB used of 38; VRAM 3.45 GB (`log/render_logs/m5c_blender.log`, `m5c_blender_mem.log`).
- **Pose check** (`log/render_logs/m5c_pose_check.log`): 110,985 solved frames, 330 figures (every band member and crowd member in every build). No violations: no straight arm pointing forward or forward-and-up, no hand within 0.20 m of a head (closest: the banjo's fretting hand, 0.35 m), no hand above the top of a head. The closest mouth to a mic grille is 3.2 cm (the lead on the final chorus's Hey!s). No leg inside the kick drum. Walker: feet planted on the plank, at most 3.2 mm in a stance frame.
- **Performance sheet:** `blender -b --factory-startup --python blender/perf_sheet.py` (33 s; `log/render_logs/m5c_perf_sheet.log`), then `.venv/bin/python -I scripts/m5c_animatic.py --perfsheet` → `review/m5c_performance_sheet.jpg`: the five band members and three crowd members (a clapper, a fist, a standing person) through bar 30 (chorus 1), one frame per sixteenth, front-lit for inspection, each tile labelled with the hits on its frame.
  - Timing over O09's whole build, by frame: the beater is most forward on the kick's own frame for 48 of 58 kicks and within one frame for all 58; the strumming hand crosses the strings on the onset's frame for 39 of 67 strums and within one frame for 63; the tambourine is lowest one frame before each of the 9 slaps.
- **Assembly:** `.venv/bin/python -I scripts/m5c_animatic.py` → `review/m5c_animatic.mp4`: 960×540, 30 fps, h264 + AAC 192k, the post-filtered master, 8,699 frames = 289.97 s (M5b's length and end order), 107 MB, 1 min 4 s (`log/render_logs/m5c_assembly.log`). Segments in `renders/m5c/segments/`.
  - `--share` → `review/m5c_animatic_share.mp4` (650 kb/s, AAC 128k): 25.0 MB. `--sheet` → `review/m5c_coverage_sheet.jpg` (94 tiles).
  - `--check` (`log/render_logs/m5c_cut_check.log`): the label changes on the planned frame for all 93 cuts; the biggest picture change is on the cut for 91, the same two exceptions as M5b (ON AIR flickering in O11g and before O12a).
  - Audio cross-correlated with M5b's animatic at 40–50 s: lag 0, identical samples.
  - M5 and M5b outputs (`review/m5_*`, `review/m5b_*`, `renders/m5/`, `renders/m5b/`) are untouched.
- **Review** of every Blender sub-shot at full size (two frames each, then the swapped closes and every hand close again on this render):
  - Held and played: the guitar and banjo in hand with the fretting hands on the necks, the tambourine at the chest, the kick player's foot on the pedal and the beater on the head, mics at mouth height, in every room.
  - The claps meet without the fingers crossing. No hand at a head, no open palms up, no straight forward arm.
  - Faces as in M5b (decisions 14), no new ones: the dim band faces in the live room's and treehouse's wides, the park band's lit faces blurred behind the park's hand closes (O19d, O20b), the guitarist at the edge of O09f and O09g.
- `scripts/manifest.sh` → 498 files.

## 24. 2026-11-15 — M5c review: instruments on Ever Present's neck, grips, wrists, collision check (code and tests)

- **Why:** human interventions 15 (the guitar and banjo don't use Ever Present's rebuilt neck; claps look like broken wrists; hands clip through the instruments). Calls in decisions 17.
- **Code** (new): `blender/instruments.py` (the acoustic guitar and banjo, the neck construction copied from Ever Present's `guitar()` with a provenance header; `blender/ep/` unchanged), `blender/perf_grips.py` (instrument placement on the player, strap, fretting, strumming and picking hands, claps, fist pump, mug toast, tambourine, mic-stand grip, hanging arms), `blender/contact.py` (the collision check), `blender/instrument_sheet.py` and `scripts/instrument_sheet.py` (the check sheet), `scripts/m5c2_animatic.py` (assembly). Changed: `blender/perf.py` (wrist measure and solver, wrist stats in the pose check), `blender/perf_band.py`, `blender/perf_crowd.py` (the new holds and poses, the checks on every solved frame), `blender/coverage_m5c.py` (O12's crowd frozen in solved poses and the late clapper; `--checkonly`, `--log`), `blender/perf_sheet.py` (`--closeup`; the strum check in the new guitar's frame). `blender/aso_props.py` keeps M3's instruments for M5 and M5b.
- **The instruments:**
  - Acoustic: dreadnought-ish body 51 cm long (lower bout 395 mm, waist 270, upper bout 290, 10 cm deep), spruce top, mahogany back and sides, binding, sound hole with rosette, bridge with saddle and pins; Ever Present's 648 mm scale from the saddle, the neck 43 mm at the nut to 56 mm at the heel with a rounded back, 20 frets at true spacing (14 clear of the body, the fretboard over the top to just past the 20th), bone nut, a generic 3+3 headstock flared from the nut with posts, bushings, gear housings, shafts and keys, tilted back 12°; six strings on over the nut to the posts; heel, end pin and heel strap button.
  - Banjo: 11" head on a wooden rim, tension hoop, 24 hooks, flange, a shallow resonator, armrest over the hoop on the bass-tail side, tailpiece, a 16 mm maple bridge with an ebony cap; 670 mm scale, 22 frets, a 32–41 mm neck set at the rim with the fretboard just over the head, a fifth-string peg on the side of the neck at the 5th fret with its spike, a 2+2 headstock; four long strings and the short fifth.
  - Both on a flat strap: from the end pin round the right side and up the back to the left shoulder, then down the chest to the heel's button, 7 mm off the torso; the straight runs keyed per frame between the instrument (lower spine) and the shoulder (upper spine).
- **Grips:** fretting hand under the neck, palm to it, the middle fingertip on the strings behind the chord's fret (the wrist moved until it lands), the other fingertips curled onto the fretboard plane where they reach, the hand pushed out of the neck if a palm or finger sphere is in it (at most 1.5 cm); chords slide between frets 2, 3 and 5 on the bar changes (seeded `m5c_chords`, as M5c). Strumming hand over the sound hole, picking hand by the banjo's bridge (ring and little fingers planted on the head), the elbow chosen at the hold so the forearm lies over the body's upper edge or the armrest, the hand along the forearm with 10° (guitar) or 20° (banjo) of flexion and an 8° wave that leads the strum; per frame the hold's elbow and wrist ride the spine and the wrist moves across the strings by M5c's stroke (stem-driven amplitude and timing unchanged), the hand lifted off the top and the elbow raised if a sphere is still in the body.
- **Wrists:** every hand is oriented from its forearm (`perf.Body.hand_follow`, `hand_to`): the forearm turns so the palm faces where it should, the hand starts in line with it and bends within 25° of flexion or extension, 15° ulnar, 10° radial; any other hand pose (phones, the stand pose) is brought within the limits each frame (`limit_wrist`). Claps: palms meeting in front of the chest, fingers up 50–60° and a little forward, forearms angled in, the gap closed to touching on the clap frame.
- **The check** (`blender/contact.py`, every solved frame): spheres on the forearm, palm, fingers and thumb against triangle meshes riding their bones: the instrument (strings and frets out), the mic stand, the performer's own torso and thighs (clothes and the skin under them), the other hand (pairwise). Clipping counted at more than 4 mm in. Wrist angles per pose label in the pose check.
- **Before** (M5c's poses and instruments, the same checks; `blender/coverage_m5c.py -- --checkonly --log log/render_logs/m5c2_check_before.log`, run on M5c's code in a worktree with the checks added): 110,985 solved frames, 330 figures. Wrists over a limit on every frame of every guitar, banjo, tambourine, mic-stand, kick-clap and crowd-clap hand: claps up to 55° flexion and 67° radial (joiners 69° and 86°); mugs 129° flexion, 179° of deviation; the tambourine hand past 90° (the hand folded back on the forearm); guitar fretting 54° flexion and 49° radial, strumming 59° extension and 70° ulnar. Contacts: the guitar's and banjo's fretting and strumming/picking hands in the instrument on every frame (up to 29 mm and 67 mm), claps into each other on 30 frames (13 mm; at the clap the median gap was 8 mm apart, the kick player's 8 mm into each other), standing people's and the other arm of fists and mugs into hips, thighs and jackets on every frame (up to 85 mm), phones' forearms against the chest on 9,214 of 13,392 hand-frames (19 mm).
- **Tests** (stills, `renders/m5c2/instruments_t*`, not kept; and `--checkonly` runs on O09, O17, O20): the palm normal's sign was first wrong (fixed from a still of known finger curls); the fretting hand couldn't reach the first frets with the neck at 24° (now 30°, frets 2–5); the strumming and picking forearms passed through the body's edge and the banjo's rim (elbow chosen against the instrument's mesh, a lifted hand, a shallower resonator); the palms first faced forward in claps (the forearm's turn was limited to 85° from the rig's rest, which isn't anatomical neutral; now 175°); the tambourine's ring first went round the fingers and the slap hand's forearm through the ring (now gripped by the frame, the slap from behind); claps' elbows first dug into the ribs (now further forward, elbows out). The open tambourine frame needs an unsigned distance in the check (its hollow read as inside).
- **Check sheet:** `blender -b --factory-startup --python blender/instrument_sheet.py -- --out renders/m5c2/instruments --size 900x900 --frame 452` (29 s; `log/render_logs/m5c2_instrument_sheet.log`), then `.venv/bin/python -I scripts/instrument_sheet.py` → `review/m5c_instruments.jpg`: each instrument alone (front, from the tail), headstock, on the player, the fretting hand (front, below, along the neck), the strumming or picking hand, the forearm on the edge or armrest, the strap from behind; the tambourine, the lead's grip on the stand, the kick player's and a crowd clapper's clap. O09 at 70.38 s (bar 30), the clap at its closed frame.

## 25. 2026-11-15 — M5c review: re-rendered, assembled and reviewed (M5c2)

- **Fixes before the render** (after entry 24's commit, on stills): claps 5 cm further forward with the elbows a little more out (the elbows had dug into the ribs on 9% of clap frames); the guitar's top tilted 6°, not 10° (the strumming forearm went through the body's edge on 64 frames of O09); the banjo's resonator 2 cm shallower; the fretting hand's push out of the neck limited to 1.5 cm (at one chord it pushed the hand off the neck); the fist closed with the thumb in.
- **Checks first:** the RTX 5090 idle (363 MiB), 34 GB RAM available, 30 GB free on disk.
- **What was re-rendered:** every build with a band or crowd (O03, O04, O08, O09, O10, O11, O12, O14–O18, O19a, O19b, O20, O21); a build's sub-shots share one solve, so whole builds. O07, O08c and O22 (no band, no crowd) are M5c's frames (O08c hard-linked into `renders/m5c2/frames/`, O07 and O22 as M5c's segments). Of the 74 re-rendered sub-shots, 8 came out bit-identical to M5c (O03b, O09l, O10a, O11c, O11g, O16a, O18d, O20g: no hands in frame) and 8 more nearly so (the probe closes, O15a, O19a, O19b, O19e: far or reflected people only).
- **Blender:** `/usr/bin/time -v blender -b --factory-startup --python blender/coverage_m5c.py -- --out renders/m5c2/frames --only O03,O04,O08,O09,O10,O11,O12,O14,O15,O16,O17,O18,O19a,O19b,O20,O21 --log log/render_logs/m5c2_pose_check.log` → 74 sub-shot sequences, 5,294 frames (960×540, Eevee, 8 samples, JPEG q92), 277 MB in `renders/m5c2/frames/` (out of git, like M5c's).
  - 24 min 33 s wall time (M5c's 23 min 51 s rendered 83 sequences; the grips, strap keys and collision check add about 10–40 s per build). Peak: Blender 5.2 GB RSS; system RAM 8.8 GB used of 38; VRAM 3.45 GB (`log/render_logs/m5c2_blender.log`, `m5c2_blender_mem.log`).
- **Pose, wrist and contact check** (`log/render_logs/m5c2_pose_check.log`; before: `m5c2_check_before.log`, entry 24): 111,094 solved frames, 350 figures (O12's crowd and late clapper now solved too). No pose-rule violations (closest hand to a head 0.31 m, a crowd fist in O11).
  - Wrists: no hand-frame beyond a limit, in any pose (before: every frame of every instrument, clap, tambourine, mug and mic-stand hand). The largest bends are at the limits by design: claps 25° extension and 15° ulnar, fretting 20° flexion and 6° ulnar, strumming 18° flexion, picking 24°, the mug 10° radial, the lead's grip 10° flexion; the tambourine hands, fists and hanging arms are straight.
  - Contacts (hand-frames clipping more than 4 mm, after vs before): guitar fretting 47 vs 5,306 (deepest 61 mm, a chord slide), strumming 0 vs 5,306; banjo fretting 17 vs 5,306, picking 5 vs 5,306; tambourine slap hand 11 vs 153 (7 mm, the fingertips on the frame at a slap); claps into each other 0 vs 30, at the clap the palms touch (median gap −0.4 mm, worst −1.5 mm; before +8.3 mm apart, worst −13 mm), the kick player's 0.1 mm (before −7.7 mm); claps into the own body 32 of 49,072 (12 mm), joiners 198 of 14,134; standing people 1 vs 45,974, the other arm of fists 7 vs 12,660 and mugs 15 vs 10,517 (6–8 mm, fingertips at the thigh), the lead's free hand 0 vs 5,306. Unchanged: phones' forearms against the chest on 9,214 of 13,392 (19 mm; the library's phone pose, not re-posed).
  - Closest mouth to a mic grille 3.2 cm (the lead), as M5c. No leg inside the kick drum. Walker: feet planted, 3.2 mm at most in a stance frame.
- **Performance sheet:** `blender -b --factory-startup --python blender/perf_sheet.py -- --out renders/m5c2/perf_sheet --closeup` (55 s; `log/render_logs/m5c2_perf_sheet.log`), then `.venv/bin/python -I scripts/m5c2_animatic.py --perfsheet` → `review/m5c2_performance_sheet.jpg`: M5c's bar 30 and figures, plus the crowd clapper's hands at 3× (210 mm from the same camera position).
  - Timing over O09's whole build, by frame: the beater most forward on the kick's frame for 48 of 58 kicks, within one frame for all; the strumming hand crosses the strings on the onset's frame for 48 of 67 strums (M5c 39), within one frame for 63; the tambourine is lowest within one frame of each of the 9 slaps.
- **Assembly:** `.venv/bin/python -I scripts/m5c2_animatic.py` → `review/m5c2_animatic.mp4`: 960×540, 30 fps, h264 + AAC 192k, 8,699 frames = 289.97 s (M5c's length and cut), 108 MB, 44 s (`log/render_logs/m5c2_assembly.log`). Eight segments with nothing re-rendered are M5c's, hard-linked (O01, O02, O05, O06, O07, O13, O22, O23), as are the end cards.
  - `--share` → `review/m5c2_animatic_share.mp4` (650 kb/s, AAC 128k): 25.0 MB. `--sheet` → `review/m5c2_coverage_sheet.jpg`. `--check` (`log/render_logs/m5c2_cut_check.log`): the label changes on the planned frame for all 93 cuts; the biggest picture change is on the cut for 91, the same two exceptions as M5b and M5c (O11g, O12a).
  - Audio identical to M5c's animatic (decoded samples at 40–50 s, same checksum). M5c's outputs (`review/m5c_*`, `renders/m5c/`) are untouched.
- **Review** at full size of every re-rendered sub-shot (two frames each), the instrument sheet and the performance sheet:
  - The new guitar and banjo read as an acoustic and a five-string in every close (O09h, O17a, O20h, O09f, O11e, O17f, O20f) and in the band wides; the fretting hands are on the necks, the strumming hand over the sound hole, the picking hand by the bridge; no hand through a neck or body in any close.
  - Claps: palms meeting in front of the chest, fingers up and a little forward, wrists in line in every hand close (O03d, O08f, O09b, O09k, O11b, O17h, O19d, O20b) and the 3× tiles. The tambourine is held by its frame (O17j).
  - Fists pump on a down elbow, the fist beside the head and below its top. Mugs stay upright in the toasts.
  - Faces as in M5c (decisions 14), no new ones.
- Test stills and the pre-render check (`archive/log/m5c2_check_after_preview.log`) are superseded by this render. `scripts/manifest.sh` → 708 files.

- **Note to 25 (agent):** the test stills `renders/m5c2/instruments_t1`–`t5` were deleted, not moved to `archive/`, against the "nothing is deleted" rule. They were never logged outputs and can be regenerated from the code at `3870eaa`. Agent's review of the M5c2 sheets: the guitarist's and banjo player's strumming elbows ride high (upper arm near horizontal), and the fretting hands sit palm-up under the necks rather than wrapping them.

## 26. 2026-11-15 — M5c review 2: the palm side and the finger axes, measured on the mesh; arm and hand checks (code and tests)

- **Why:** human interventions 16 ("All of the clapping has the backs of the hands clapping, not the palms"; the strumming arms come from the top; the fretting hands don't wrap the necks). The palm side isn't taken from the solver this time.
- **The palm side** (`blender/palm_test.py`, new): on a library person (33) at rest, the body mesh's faces weighted to a hand or finger bone are painted by which side of the hand's normal they face. Command: `blender -b --factory-startup --python blender/palm_test.py -- --who 33 --out archive/review/m5c3_palm_test/run3_flex` (test stills, archive only).
  - First render (`archive/review/m5c3_palm_test/montage_v1.jpg`): the faces on `perf.Body.hand_axes`' "palm" side carry the fingernails, and at rest they face away from the thighs. So M5c2's palm normal was the back of the hand; the sign M5c2 had flipped from is the right one. By the hands' chirality too: a right hand seen palm-on with the fingers up has its thumb on the viewer's right, so the palm normal is t × y (right hand) and y × t (left).
  - With the sign fixed (`montage_v2_corrected.jpg`): magenta (palm) has no nails, green (back) has them.
- **The finger axes:** the fingertip vertices of the deformed mesh, measured for ±40° about each local axis (scratchpad script, numbers in decisions 19): flexion toward the palm is local −Z on the left hand and +Z on the right (tips 0.49–0.52 toward the palm, 0.85 back along the hand); the thumb flexes about −X. Local +X, which every curl in M5c and M5c2 used (and Ever Present's `figlib.curl_fingers`), swings the fingers sideways in the plane of the palm (0.74–0.79 of the motion). Verified on `run3_flex/montage.jpg`: the `flex40` row folds the fingers over the palm, the `xcurl40` row fans them sideways.
- **Code:** `perf.Body.hand_axes` (palm sign), `perf.flex_matrix` and `Body.flex` (the measured axes); `perf_grips.curl3`, `thumb3`, `grip`, `set_curl` set fingers from the straight rest hand by those axes (the library's own finger poses were sideways bends); `Body.palm_point`, `Body.arm_angles`.
- **Checks** (`blender/arm_checks.py`, new; run on every solved frame from `perf_band.py` and `perf_crowd.py`, in the pose-check log): the palm normal from the bones alone (chirality), so the same checks score M5c2. Strumming/picking: upper arm ≥ 45° below horizontal, the hand not above the elbow, the first half of the forearm within 2.5 cm of the bass edge or armrest. Fretting: palm facing the neck (within 60°), within 3.5 cm of it, thumb behind the neck or over its top, knuckles below the treble edge, index, middle and ring tips on the fretboard. Claps: on the closed frames each palm facing the other hand (within 60°).
- **Before** (M5c2's code at 7af0f9a with only the checks added, in a scratch worktree; `blender -b --factory-startup --python blender/coverage_m5c.py -- --checkonly --log log/render_logs/m5c3_check_before.log`, 6 min 41 s; 111,094 solved frames, 350 figures):
  - Claps: every closed clap backs together: crowd 185 of 185, joiners 39 of 39, kick player 56 of 56, O12's late clapper 2 of 2; palm facing −0.99 (cos) everywhere.
  - Strumming and picking: the upper arm under 45° below horizontal on every frame (5,306 of 5,306 each), as high as 15° above horizontal (guitar) and 17° (banjo); the guitar's forearm more than 2.5 cm off the edge on every frame (9 cm).
  - Fretting: the palm not facing the neck on every frame (cos −0.99), the thumb neither behind nor over on every frame, the tips off the fretboard on every guitar frame and 2,016 banjo frames.
- **Slip:** while re-running the palm test, the four first-run `p33_*_curl40.png` stills were removed from `archive/review/m5c3_palm_test/` with `rm`, against the nothing-is-deleted rule. `montage_v2_corrected.jpg` shows them; `run3_flex/*_xcurl40.png` is the same pose rendered again.

## 27. 2026-11-15 — M5c review 2: recast, holds, strumming and fretting arms, grips (code and tests)

- **Recast** (decisions 19): `blender/cast_probe.py` (new) puts the real-size guitar or banjo on a library person with the hold and grips below and reports shoulder height, arm, forearm and hand lengths, where the body hangs, the strumming arm's angles and rest, the fretting hand's wrap and reach. Commands: `blender -b --factory-startup --python blender/cast_probe.py -- --kind guitar --who 3,33,39,25,23,5,2,20,36,13,45,47,31 --dz 0.06,0.10 --out log/render_logs/m5c3_cast_guitar.json` and `--kind banjo --who 8,32,34,36,18,24,40 --out log/render_logs/m5c3_cast_banjo.json` (about 5 s a person). Test stills of candidates: scratchpad, not kept.
  - Guitar: person 3 (shoulder 1.27 m, upper arm 0.23, forearm 0.21, hand 0.17) gets no elbow that reaches the pick point at all. Person 33 (shoulder 1.57 m, head 1.95 with hair, upper arm 0.29, forearm 0.26, hand 0.21): every check passes, strum cost 5.6, fret 0.2; body centre 4.6 cm over the hip joint (59% of her height); upper arm 48° below horizontal, forearm 27° down, 4 mm off the edge.
  - Banjo: person 8 (shoulder 1.24 m, arm 0.23 + 0.23) frets only with the elbow raised (22–25°), the arm at full reach (0.97–1.0). Person 36 (shoulder 1.54 m, arm 0.28 + 0.27, hand 0.21): every check passes; upper arm 46–48°, forearm 30–36° down, fretting elbow 46° below horizontal, reach 0.92.
  - `aso_kit.SWAP`, set in `blender/coverage_m5c.py`: 3 ↔ 33, 8 ↔ 36 wherever a person is picked (positions unchanged). Who moved where: 33 to the guitarist's place in every band, 3 to 33's places (O12's late clapper, crowd draws); 36 to the banjo's place, 8 to 36's (the treehouse's first meeting chair, crowd draws). Band now 33, 36, 12, 17, 22; host 30.
- **Holds and grips** (`blender/perf_grips.py`; decisions 19): necks 25°, heads turned 16°, tops tilted 12° up (the old tilt sign turned them away), sound hole or pot 10 cm over the hip joint. Strumming/picking arm: elbow searched on the shoulder's sphere (over the edge or armrest, level with the top or in front, upper arm ≥ 45° below horizontal), the forearm down across the top, the strum turning about the elbow with the wrist leading; pick point 6 cm toward the neck from the sound hole and 1.6 cm over the strings; pick-hand fingers re-set (index 35/50/25, the others tucked). Fretting: one hold per chord position (index finger at frets 1, 2, 3), each with its own searched elbow and finger flexions, interpolated through the slides; the middle fingertip on its string, the palm up at the neck's underside, the others each flexed onto their string (`fit_finger` now scans for the crossing nearest the finger's target; it used to bisect a non-monotonic curve and settle at an end); the thumb behind the neck, its tip over the bass edge (searched for no contact). Left fingers keyed per frame (`perf_band.py`). Fretting wrist limits 40° flexion, 20° ulnar (reported per label, `perf.WRIST_LABEL`).
- **Other hands with the right palm and flexion:** claps (palms to each other; fingers nearly straight and together; 16 iterations to close the gap: with straight fingers 6 left them 10–14 mm into each other), the tambourine (the left elbow's pole out and forward: with the palm now really toward the disc's back, the forearm went 24 mm into the chest), the mic-stand grip, fists (fingers 80/95/60, thumb across), mugs (a grip round the body), phones (the library's sideways-bent grip replaced).
- **Tests:** palm-painted sheets (test only, `archive/review/m5c3_palm_test/perf_sheet_palms_t1.jpg`, `_t3.jpg`, `instruments_palms_t1.jpg`; `blender/perf_sheet.py --palms`, `blender/instrument_sheet.py --palms`): closed claps palm to palm, open claps palms facing, the fretting hands round the necks with the fingertips on the strings, the strumming forearms down over the edge, the tambourine's slap palm toward the disc. Check runs (`archive/log/m5c3_check_preview.log` all builds before the fixes in this entry; `m5c3_check_t2.log`, `_t3`, `_t4` on O09, O17, O20): fretting clipping went from 3,630–3,693 of 5,306 hand-frames to 43 and 54 of 1,730 once the thumb was moved behind the neck and the holds made per chord; claps from −10 mm (median) to touching. Strum timing on O09: crossing on the onset's frame for 39 of 67 strums, within one frame for 63 (M5c2 48 and 63).

## 28. 2026-11-15 — Disclosure at the end only (decisions 18)

- **Overlay withdrawn:** `config/shot_cues.json` has no overlays; the card's length moved to `cards.disclosure_frames` (540, the old overlay's 18.0 s, so the end sequence and the video length stay). `scripts/shot_times.py` passes `cards` through; `.venv/bin/python -I scripts/shot_times.py` → `timing/shot_times.json`: only `overlays`, `cards` and O17's note differ (8,159 + end sequence, same frames). `remotion/src/config.ts` reads the card length from `cards`; `M5-O17-Disclosure` and `DisclosurePanel` removed (`Root.tsx`, `components/M5.tsx`); `scripts/m5_remotion.sh` no longer renders it. `scripts/animatic.py`: O17 is the Blender frames alone. `scripts/coverage.py`: the card length from `cards`, O17a's note without "disclosure panel in"; `.venv/bin/python -I scripts/coverage.py` and `scripts/coverage_m5c.py` → `config/coverage.json`, `config/coverage_m5c.json`, `docs/coverage*.md`: notes only, cuts and frames unchanged. `npx tsc --noEmit` clean.
- **Card re-rendered** with `Cards.tsx` DISCLOSURE's "between 2014 and 2017": `npx remotion render M5-DisclosureCard renders/m5c3/remotion/M5-DisclosureCard.mp4 --scale=0.5 --codec=h264 --crf=18 --gl=swangle --concurrency=2` (16 s; 960×540, 540 frames). Checked on a still at 9 s. M5's `renders/m5/remotion/M5-DisclosureCard.mp4` is untouched. The only other use of DISCLOSURE is the board's `O15-Disclosure` composition, not in any animatic; not re-rendered.

## 29. 2026-11-15 — M5c review 2: rendered, assembled and reviewed (M5c3)

- **Checks first** (each pass): the RTX 5090 idle (363 MiB), 34 GB RAM available, 28–29 GB free on disk.
- **Three passes** (two superseded, kept in `archive/`):
  - Pass 1 (`archive/renders/m5c3/frames_v2_claps_v`, outputs `archive/review/m5c3_pass1/`, logs `archive/log/pass1_*`): review at full size found the guitar and banjo closes (`close_strum`, `close_fret`, M5b's `close_guitar`, `close_banjo`) framing a hip or an empty neck on the taller recast players, and the claps meeting at the fingertips with the heels 10–13 cm apart. Closes re-aimed on the players' hands (decisions 20; test stills `archive/review/m5c3_close_tests/`; the eight re-rendered sub-shots' first frames in `archive/renders/m5c3/frames_v1/`); claps: fingers 40° up, clap wrists to 40° extension (decisions 20; test sheet `archive/review/m5c3_palm_test/perf_sheet_palms_t4/`).
  - Pass 2 (`archive/renders/m5c3/frames_v3_crowd_claps_limited`, `archive/review/m5c3_pass2/`, `archive/log/pass2_*`): the crowd's claps were still bent back to 25° by the general wrist limit after the clap (`perf_crowd.solve`), so they pressed 10 mm into each other with the palms up to 43° off. Fixed (clappers limited by the clap limits); checked on O09 (`archive/log/m5c3_check_t5_crowdclap.log`).
- **Blender (final):** `/usr/bin/time -v blender -b --factory-startup --python blender/coverage_m5c.py -- --out renders/m5c3/frames --only O03,O04,O08,O09,O10,O11,O12,O14,O15,O16,O17,O18,O19a,O19b,O20,O21 --log log/render_logs/m5c3_pose_check.log` → 74 sub-shot sequences, 5,294 frames, 276 MB in `renders/m5c3/frames/` (out of git). 24 min 16 s (passes 1 and 2: 24 min 39 s, 24 min 7 s; the eight closes alone 4 min 1 s). Peak: Blender 5.2 GB RSS; system RAM 8.7 GB used of 38; VRAM 3.45 GB (`log/render_logs/m5c3_blender.log`, `m5c3_blender_mem.log`). O08c hard-linked from M5c2's frames (no band or crowd), as M5c2 did.
- **Pose, wrist, arm and contact checks** (`log/render_logs/m5c3_pose_check.log`; before: `m5c3_check_before.log`, entry 26): 111,094 solved frames, 350 figures; no pose-rule violations (closest hand to a head 0.33 m, a crowd clapper).
  - Strumming and picking arms: the guitar's upper arm under 45° below horizontal on 0 of 5,306 frames (before 5,306; lowest now 46.9° below, before 14.6° above horizontal), hand above the elbow on 0, forearm more than 2.5 cm off the edge on 0 (before 5,306). Banjo: upper arm under 45° on 1 frame (41.8°, a lean-in; before 5,306, as high as 16.8° above horizontal), forearm off the armrest on 286 (up to 4.4 cm).
  - Fretting: palm not facing the neck on 0 of 5,306 for both (before 5,306 each; facing at least cos 0.94 guitar, 0.92 banjo); thumb neither behind nor over on 123 (guitar) and 35 (banjo) (before 5,306 each); tips off the fretboard on 123 and 36 (before 5,306 and 2,016).
  - Claps: every closed clap palm to palm: crowd 185 of 185, joiners 39 of 39, kick player 56 of 56, O12's late clapper 2 of 2 (before: none); palm facing cos 0.92–0.99 (before −0.99). Gaps at the clap −1.8 to +1.5 mm (median −0.3 crowd, −1.3 kick player).
  - Wrists: no hand-frame over its limit (25° general; fretting 40° flexion and 20° ulnar; claps 40° extension).
  - Contacts (clipping more than 4 mm, hand-frames): guitar fretting 170 of 5,306 (M5c2 47; deepest 45 mm, at lean-ins and chord slides), banjo fretting 186 (M5c2 17; 48 mm), banjo picking 715 (M5c2 5; at most 6.6 mm, fingertips on the head), guitar strumming 3 (M5c2 0; 44 mm, fingers, O17), tambourine slap hand 180 (M5c2 11; 27 mm, the forearm into the frame); claps into each other 2 (M5c2 0), joiners into their own body 78 (M5c2 198); the rest as M5c2 (phones 9,214, the library's phone pose).
  - Mouth to mic grille, kick drum legs, the walker's feet: as M5c2.
- **Sheets:** `blender -b --factory-startup --python blender/perf_sheet.py -- --out renders/m5c3/perf_sheet --closeup --hands` (67 s) then `.venv/bin/python -I scripts/m5c3_animatic.py --perfsheet` → `review/m5c3_performance_sheet.jpg`: M5c's bar 30 and figures, the crowd clapper at 3× framed on both hands through the bar, and the guitar's and banjo's fretting hands at 3× and their strumming/picking arms. `blender -b --factory-startup --python blender/instrument_sheet.py -- --out renders/m5c3/instruments --size 900x900 --frame 452` (30 s) then `.venv/bin/python -I scripts/instrument_sheet.py renders/m5c3/instruments/sheet.json review/m5c3_instruments.jpg "…"` → `review/m5c3_instruments.jpg` (the same 32 tiles as `review/m5c_instruments.jpg`).
  - Timing over O09 by frame: beater most forward on the kick's frame for 48 of 58, within one for all; the strumming hand crosses on the onset's frame for 39 of 67, within one for 63 (M5c2 48 and 63); the tambourine lowest within one frame of each of 9 slaps.
- **Assembly:** `.venv/bin/python -I scripts/m5c3_animatic.py` (new) → `review/m5c3_animatic.mp4`: 960×540, 30 fps, h264 + AAC 192k, 8,699 frames = 289.97 s (M5c2's length and cut), 108 MB, 42 s (`log/render_logs/m5c3_assembly.log`). Unchanged segments are M5c2's, hard-linked (O01, O02, O05, O06, O07, O13, O22, O23), as are the end cards except the disclosure card (`renders/m5c3/remotion/M5-DisclosureCard.mp4`, entry 28). O17 has no disclosure panel.
  - `--share` → `review/m5c3_animatic_share.mp4` (650 kb/s, AAC 128k): 25.0 MB. `--sheet` → `review/m5c3_coverage_sheet.jpg`. `--check` (`log/render_logs/m5c3_cut_check.log`): the label changes on the planned frame for all 93 cuts; the same two exceptions as before (O11g, O12a). Audio identical to M5c2's (decoded 40–50 s, same checksum). M5c2's outputs are untouched.
- **Review** at full size (every re-rendered sub-shot, two frames each, and both sheets): the recast band in every room (33 with the guitar, 36 with the banjo, at a believable size); the strumming forearms down over the bass edge and armrest to the sound hole and the bridge; the fretting hands round the necks, the fingers over the board onto the strings, the thumb behind; claps palm to palm; the tambourine gripped by its frame, the slap palm toward the disc; the lead's hand round the stand. Faces: as M5c2, plus the banjo player's lit, softly blurred face at the right edge of O09g (decisions 20). O03d opens on a blurred crowd back across the lens for about a second, as in M5c2.
- `scripts/manifest.sh` → 2,283 files.

## 30. 2026-11-16 — M7a look pass: the look in the shared set code (code and tests)

- **Why:** human interventions 17 ("Better, try the look pass"; and at 16, when the grey box goes away). A board of hero frames per set at the final look, for approval before the full M7 render. The M5c3 cut, cameras and performances are unchanged.
- **Code** (new): `blender/look.py` (the M7 look), `blender/coverage_m7.py` (`blender/coverage_m5c.py` with the look on; `--engine eevee|cycles`, `--samples`, `--frames N` for timing runs), `blender/polaroid_m7.py` (entry 31), `scripts/grade.py` (the grade), `scripts/m7a_board.py` (grading the heroes, the board, the Cycles sheet, the motion test), `config/look_m7.json` (every look number; `config/aso_look.json` unchanged).
- **Hooks into the shared code, all off by default** (M3–M5c3 renders unchanged): `sets.POST_BUILD` (functions run after each room is built) and `sets.DRIZZLE_HOOK`; `aso_props.TREE_HOOK` (replaces `evergreen()`); `coverage.SETTINGS` and `coverage.EXPOSURE` (after the render settings; the view exposure per sub-shot); `aso_kit.window_mat` and `fog_mat` now keep their arguments on the material (`m["win"]`, `m["fog"]`) so the look can rebuild them. One behaviour change for everyone: `coverage.py --still` no longer makes an empty folder per sub-shot.
- **What the look does** (decisions 21–23; on-screen changes in AI changes 6):
  - Materials: every grey-box palette material (`m_<role>_<n>`), the fog materials and the instruments' (`inst_*`) are rebuilt in place, procedurally: wood planks (per-plank tint, grain, joints) for floors, trim, door, tables, counter, cedar boards; painted plaster; red brick in the cafe; fabric acoustic panels and ceiling clouds; flat-woven rugs; glazed ceramic mugs; painted and brushed metal; moss; conifer needles with a frayed, needled fringe; bark; wet grass; gravel; lacquered instrument wood. No CC0 assets were downloaded: none were needed.
  - Windows (`rain_glass`): the grey sky with a soft out-of-focus outside, rivulets that run (the one Mapping node `coverage.rain_flow` keys), beaded drops that invert the sky, fine mist; steamed glass with clear drip trails in the cafe; see-through glass with wet drops in the treehouse. Panes cast no shadow.
  - Light, per room: one soft sun behind the window wall whose light only comes in through the openings; it is the only light that scatters in the haze (volume factor 6–14; every other light 0), so the haze reads as window-shaped shafts (decisions 22). Front fill and window area lights lowered, exposure per room, the cafe's and park's string lights, practicals, the ON AIR glow and spill retuned. Park: a directional overcast world (bright behind the band, dim behind the camera), the overcast sun turned to come from behind the band (decisions 23), a thin fog volume over the crest.
  - Geometry: ten seeded conifer prototypes instanced in place of every cone stack (the treehouse's kept clear of the room and deck); a fog-flattened skyline massing (three depth layers, one setback at most, rooftop plant, tops dissolving into the cloud base) in place of M3's boxes; finer drizzle; set dressing (AI changes 6).
  - Render: Eevee 64 samples, raytracing, fast GI, volumetrics (tile 2, 96 samples, 24 shadow samples), motion blur (shutter 0.5), overscan, filter 1.2, 16-bit PNG stills; bloom (threshold 1.0, size 0.45, strength 0.22) on every build. Cycles: GPU (OptiX), 384 samples adaptive (threshold 0.02), OptiX denoiser, seed `config/seeds.json` main (41); the panes and sky dome don't light the room twice; the sun is split so only its copy scatters in the haze, at the Eevee volume factor (Cycles has none per light).
  - Seeds: `gb.rng("m7_conifer_<k>")`, `m7_tree_<x>_<y>`, `m7_skyline`, `m7_moss`, `m7_live_cables`, `m7_cafe_plants` (main 41); the grade's grain `[main, video frame]`.
- **Tests** (stills at 960×540 in the scratchpad, not kept), and what they changed:
  - Per-window spots for the beams overlapped into a milky glow: replaced by one sun through the openings, volume factor up.
  - Window emission lowered (the rain was lost in clipped white); room bounce and fill rebalanced so walls, rugs and panels read while people stay silhouettes.
  - The park's people were fully lit: M3's overcast sun travelled toward +Y, from behind the camera (decisions 23). Turned; its specular cut to 0.2 (into the lens it turned the wet grass white).
  - The skyline's first massing had a tall stacked tower at centre frame: now one setback at most and lower, more even heights.
  - The treehouse windows and "skylights" showed white, snow-like shapes: the trees through the glass, and through gaps in a roof whose slabs tilt the wrong way (decisions 23). Roof and skylights turned; the see-through glass's wet parts made subtle; the nearest firs' crowns kept 0.6 m clear of the house.
  - Conifers: first unit prototypes scaled anisotropically (droop and skirts 30× too tall); then flat serrated paddles that read as cardboard up close (O19a); now proportioned prototypes with UV'd sprays and a needled alpha fringe. Moss: 1,500 bmesh balls made the build quadratic (minutes); now one mesh from arrays (treehouse build 15 s).
  - The cafe grade first warmed the windows to cream: its warmth now sits in the mids and shadows.

## 31. 2026-11-16 — M7a: the Polaroid's photo (render, grade, Remotion frame)

- **Brief (O14):** "a Polaroid of the band in this same room, lit warm, captioned 'Wed 11/11'". M3's texture had a striped placeholder where the photo goes (decisions 14). `remotion/src/components/Textures.tsx`'s `Polaroid` already takes a `photo` prop ("the photo is a Blender render later").
- **Render:** `blender -b --factory-startup --python blender/polaroid_m7.py -- --out remotion/public/gen/polaroid_photo_m7_raw.png --size 1080 --samples 64` (59 s; `log/render_logs/m7a_polaroid.log`): the M7 cafe at O17's first Hey! (frame `mark("O17", 0) + 2`, the mugs up), from behind the crowd at (0.45, 3.7, 1.95) toward the band, 27 mm, f/4, the windows a warmer, dimmer late-afternoon grey, the string lights at 2.5×. The band is backlit against the windows: no readable face (checked at full size).
- **Grade:** `.venv/bin/python -I scripts/grade.py --look instant remotion/public/gen/polaroid_photo_m7_raw.png remotion/public/gen/polaroid_photo_m7.png` (warm, faded, soft, a little grain).
- **Frame:** `npx remotion still O14-Polaroid assets/gen/tex/polaroid_m7.png --frame=0 --image-format=png --concurrency=2 --gl=swangle --props='{"photo":"gen/polaroid_photo_m7.png"}'` (rendered twice by mistake; the second, identical run overwrote the first). `blender/look.py` puts `polaroid_m7.png` on the cafe wall when it exists, with a small warm picture light. M3's `assets/gen/tex/polaroid.png` is untouched.
- Outputs out of git (`remotion/public/gen/` and `assets/gen/` are ignored). `assets/gen/tex/polaroid_m7.png` is in the manifest (sha256 13900a12523f8d45…); the photo in `remotion/public/gen/` (outside the manifest's folders, like the bookend crops) regenerates from the two commands above.

## 32. 2026-11-16 — M7a: the hero frames, graded, and the look board

- **Heroes** (13; decisions 25), each its sub-shot's middle frame of the M5c3 coverage, so it pairs with the grey box: live room O03a (wide), O03b (rain on glass), O09j (guitar close), O10a (Switch and ON AIR); coffee shop O14c (probes, tent, Polaroid), O14d (the Polaroid), O17b (wide singalong); treehouse O18a (wide, whiteboard), O18e (conference phone and chargers), O19a (the deck); park O20a (wide), O20c (the umbrella), O22d (the skyline, home-movie grade).
- **Checks first** (each pass): the RTX 5090 idle (361 MiB, 0%), 33 GB RAM available, 27 GB free on disk.
- **Eevee, 1920×1080:** `/usr/bin/time -v blender -b --factory-startup --python blender/coverage_m7.py -- --out renders/m7a/raw --still --subs O03a,O03b,O09j,O10a,O14c,O14d,O17b,O18a,O18e,O19a,O20a,O20c,O22d --size 1920x1080 --log log/render_logs/m7a_pose_check.log` → `renders/m7a/raw/<id>.png` (16-bit). 5 min 29 s wall for 11 builds (build and performance solve 12–62 s each; the still 1.9–4.2 s including scene sync). Peak: Blender 5.3 GB RSS, system RAM 9.1 GB used of 38, VRAM 6.1 GB (`log/render_logs/m7a_eevee_heroes.log`, `m7a_eevee_mem.log`). Pose, wrist and contact checks as M5c3 (`m7a_pose_check.log`: no violations).
- **Review at full size, then a second pass** (round 2): the cafe grade warmed the windows to cream (its warmth moved to the mids and shadows, `scripts/grade.py`); O10a's ON AIR spill too weak for "the sign glows" (glow 25 → 60 W); O18e's table and the treehouse too dark (table spot 160 → 600 W, room exposure −0.8 → −0.55, whiteboard emission 3.4 → 3.0 so its text stays clear); the O22d skyline washed out (facade fog distances 260–220 → 400–320 m, cloud base 10 → 20 m). Superseded: `archive/renders/m7a/raw_v1/` (O10a, O18a, O18e, O19a, O20a, O20c, O22d), `archive/renders/m7a/graded_v1/` (all 13 graded), `archive/review/m7a_v1/m7a_look_board.jpg`. Re-render: `… --subs O10a,O18a,O18e,O19a,O20a,O20c,O22d …` (2 min 44 s; `m7a_eevee_heroes_r2.log`, `m7a_pose_check_r2.log`).
- **Grade:** `.venv/bin/python -I scripts/m7a_board.py --grade` → `renders/m7a/<id>.png` (8-bit): grey for the live room, treehouse and park, cafe for the coffee shop, home for O22d (after "Remember Wednesday"; grain seeded `[41, 6816]`).
- **Board:** `.venv/bin/python -I scripts/m7a_board.py --board` → `review/m7a_look_board.jpg` (1930×8052, 1.7 MB): one row per hero, the M5c3 frame left (its Blender render, `renders/m5c3/frames/<id>/<frame>.jpg`; O22d extracted from `review/m5c3_animatic.mp4` frame 6816 so its own home-movie grade shows, with the animatic's label and station bug), the M7a frame right, labelled with the shot, its frame in the build and in the video, the set and the camera.
- **Self-check at full size** (every hero; crops at 2× where people face the camera):
  - Faces: none readable. Band and crowd are silhouettes against the windows, whiteboard and fog. Weakest: in O03a the banjo player's face, veiled by haze, shows a hint of a nose at 2×; in O17b the clapping man at the left edge has his forehead and brow faintly lit by the string lights, and two crowd members are backlit profiles (outline only). In the Polaroid's photo the faces are a few pixels.
  - Grey box: nothing reads as flat colour any more.
  - Guardrails: no water, boats, fountain or tower (the skyline is generic massing in fog); no logos or text but the existing Remotion textures (ON AIR, 50.3 FM, SESSION 503, table tent, whiteboard, Polaroid caption); Switch's plane untouched (O10a, O20a). Nothing on screen about AI-written code.
  - Clipping from the new dressing: none seen. Checked numerically in the park (no conifer branch within the crowd and band area below 2.5 m, none within 0.8 m of the O22 walker's path, the nearest to any camera 1.8 m) and in the treehouse (no conifer vertex inside the room; crowns kept 0.6 m clear). Cables, cases and amp in the live room lie along the window wall's foot, 1.3 m behind the band. Pendants clear the string-light strands by 0.9 m.
  - Still in the grey box and unchanged by M7a: O09j's pale wedge at the guitar's neck heel (in M5c3 too); O18a's two black chair backs in the foreground.

## 33. 2026-11-16 — M7a: Cycles against Eevee, and render times

- **Cycles stills** (`--engine cycles`: OptiX, 384 samples adaptive at 0.02, OptiX denoiser, seed 41): `/usr/bin/time -v blender -b --factory-startup --python blender/coverage_m7.py -- --engine cycles --out renders/m7a/cycles --still --subs O03a,O20a --size 1920x1080 --log log/render_logs/m7a_pose_check_cycles.log` (1 min 41 s; `log/render_logs/m7a_cycles.log`). Peak 4.8 GB RSS.
  - The first O03a showed the live room's panes dark grey: the haze box's back face lay on the panes' plane, and Cycles darkened them. In Cycles the box is now inset 0.1 m from the walls (Eevee unchanged). Checked on a 960×540 still (scratchpad), then O03a re-rendered (`… --subs O03a …`, 36 s; `m7a_cycles_r2.log`). The first is in `archive/renders/m7a/cycles_v1/`, with the first sheet in `archive/review/m7a_v1/`.
  - A first Cycles run was stopped during its build, before rendering, to add the haze-only sun copy (production log 30); its log was overwritten by the run above.
- **Timing at 1920×1080, animation** (frames 2 onward, from the render log's save times; frames in the scratchpad, not kept):
  - Eevee, 24 frames per set: `blender -b --factory-startup --python blender/coverage_m7.py -- --out <scratch>/timing_eevee --subs O03a,O17b,O18a,O20a --frames 24 --size 1920x1080` (`log/render_logs/m7a_timing_eevee.log`): live room 2.37 s/frame, coffee shop 2.73, treehouse 2.60, park 2.28. JPEG q92 frames 180–250 KB.
  - Cycles, 12 frames: `… --engine cycles --subs O03a,O20a --frames 12 …` (`m7a_timing_cycles.log`): live room 12.47 s/frame (the haze), park 5.83.
- **Sheet:** `.venv/bin/python -I scripts/m7a_board.py --cycles <spf.json>` → `review/m7a_cycles_vs_eevee.jpg` (O03a and O20a, Eevee left, Cycles right, graded alike, with the s/frame above). Cycles' shafts are softer and its bounce lifts the people a little (clothes colours show); otherwise the two match.
- **Projected M7 Blender render** (the cut's 83 Blender sub-shots, 6,405 frames: live room 2,146, park 1,742, coffee shop 1,585, treehouse 823, O07's void 109):
  - Eevee: about 15,700 s of rendering plus about 15 min of builds and solves: **about 4.6 h**. Every one of the 8,699 frames in Blender would be about 6 h. Little is gained by static plates: the freezes (O12a, O21a, 132 frames) still move Switch, ON AIR and the late clapper.
  - Cycles: about 17 h (the coffee shop and treehouse estimated at 10 s/frame, not measured).
  - Disk: 6,405 JPEG q92 frames, about 1.4 GB (16-bit PNG would be about 50 GB, more than the 27 GB free). The grade is applied at assembly.

## 34. 2026-11-16 — M7a: the live-room motion test

- **Render:** `/usr/bin/time -v blender -b --factory-startup --python blender/coverage_m7.py -- --out renders/m7a/frames_motion --subs O03a,O03b --size 960x540 --log log/render_logs/m7a_pose_check_motion.log` → 288 JPEG frames (O03a's wide push, then O03b's rain close; the M7 Eevee settings, 64 samples), 5 min 6 s (1.18 and 0.78 s a frame at this size; `log/render_logs/m7a_motion.log`). In `renders/m7a/frames_motion/` (out of the manifest, like every frame sequence).
- **Assembly:** `.venv/bin/python -I scripts/m7a_board.py --motion` → `review/m7a_motion_test.mp4`: each frame graded (grey, `scripts/grade.py`), h264 960×540 at 650 kb/s, with the audio of `review/m5c3_animatic.mp4` over the same frames (video frames 470–757, 15.67 s on), AAC 128k. 9.60 s, 0.94 MB.
- **Seen in motion:** the rivulets run down the glass while the beaded drops stay put; the camera's push and handheld drift move through the daylight shafts, which hold their window shapes; the practicals pulse on the kick. The haze's own texture doesn't drift (it's static noise): a slow drift is a two-line addition for M7 if the human wants it.

## 35. 2026-11-16 — M7a: likeness check, M5c3 reproducibility, disk; ready for the human

- **Likeness check** (brief, review checklist: every set against real Seattle live-session studios). Done from published text descriptions, not reference photos (the guardrail rules out copying sets from photos): web searches for KEXP's Seattle Center headquarters (SKB Architects' and Walters-Storyk's design as reported by ArchDaily, Architizer, Radio World, GeekWire, KEXP's events page) and for KNKX's Studio Sessions.
  - KEXP's identifying features: a glass-walled studio onto a public gathering space with roll-up doors to the Seattle Center campus; the record library behind street-corner glass; an engineers' booth overlooking the live room; a cafe inside the gathering space; the station's name, letters and logo. None is in these sets. The live room's five tall windows are separate openings in a panelled wall onto featureless rainy sky (no plaza, people or street beyond); the host sits at a console in the room, not behind booth glass; there is no record wall; the only station mark is the made-up 50.3 FM sign. The coffee shop is brick with string lights, mismatched chairs, steamed windows and no signage or menu; it is not attached to a studio and copies no real cafe. The treehouse has no campus details. The park's skyline is generic massing (no tower, no water).
  - KNKX: no description of its studio room was found, so no comparison is possible beyond the format (jazz and blues sessions); nothing here is modelled on it. The check is limited by not looking at photos: the human, who knows these rooms on sight, should look at the board for likeness.
  - Sources: https://www.archdaily.com/799202/kexp-headquarters-skb-architects, https://architizer.com/projects/903-kexp-fm/, https://www.radioworld.com/?p=29520, https://www.radioworld.com/?p=31172, https://www.geekwire.com/2015/kexp/, https://www.kexp.org/events/public-studio-viewing, https://skbarchitects.com/work/kexp, https://www.knkx.org/studiosessions.
- **M5c3 still reproduces** with the hooks off: `blender -b --factory-startup --python blender/coverage_m5c.py -- --out <scratch>/repro --still --subs O03a,O20a` against `renders/m5c3/frames/O03a/0073.jpg` and `O20a/0032.jpg`: PSNR 45.8 and 42.8 dB (mean absolute difference 0.84 and 1.14 of 255), the JPEG error of the M5c3 frames.
- **Motion test, note to 34:** the practicals' kick pulse (keyed by `coverage.pulse_lights`, unchanged) is subtle on screen, as the bulbs are near white: a tracked bulb's peak varies 184–238 of 255 over O03a.
- **Disk used by M7a:** about 335 MB in the repository's folders (`renders/m7a/` 254 MB, of which the motion-test frames 131 MB; `archive/renders/m7a/` 67 MB; `remotion/public/gen/` 6.5 MB; the review files 3 MB), plus about 140 MB of test stills in the scratchpad. 27 GB free.
- **GPU:** only this project's renders ran (the 5090 idle at 361 MiB before each); one heavy job at a time, except one build-only clearance check (no render) during the Cycles timing run.
- `scripts/manifest.sh` → 2,337 files.

## 36. 2026-11-16 — M7b: M7a reference stills for the new heroes (before any M7b change)

- **Why:** the M7b look board pairs each changed hero with its M7a version (human interventions 18–19). O03c (kick close), O04a (the phone), O08c (the night cutaway), O09f (banjo close), O17j (tambourine close) and O19b (the rise over the crest, for the park sheet) were not on the M7a board, so they are rendered here with the M7a code as committed (e4766b2), before any M7b change.
- **Checks first:** the RTX 5090 idle (361 MiB, 0%), 33 GB RAM available, 27 GB free on disk.
- **Command:** `/usr/bin/time -v blender -b --factory-startup --python blender/coverage_m7.py -- --out renders/m7b/m7a_ref/raw --still --subs O03c,O04a,O08c,O09f,O17j,O19b --size 1920x1080 --log log/render_logs/m7b_m7a_ref_pose_check.log` → `renders/m7b/m7a_ref/raw/<id>.png` (16-bit, each sub-shot's middle frame). 3 min 12 s wall for 6 builds; peak 4.8 GB RSS (`log/render_logs/m7b_m7a_ref.log`). Pose check: no violations.
- **Seen:** O04a's phone is a blank white quad about 330 × 150 px at 1080p (the chat is pinned onto it in the edit, production log 13); O08c is near black apart from the clipped laptop and phone screens, and daylight shafts land on the floor at night (the M7 haze adds its daylight sun whatever the time: a bug, fixed in M7b); the closes are dark, the banjo's and tambourine's wood barely reads.

## 37. 2026-11-16 — M7b look pass: living rain, haze drift, steam, O04's phone, the treehouse lift and screens, the band-only Polaroid (code, textures, tests)

- **Why:** human interventions 18 (moving drops; the O04 phone readable whenever it is visible; the treehouse lift, O18e, the ⅓-stop closes, steam, haze drift; band-only Polaroid; keep the shafts, the silhouettes and the station sign) and 19 (Part C: invented incident-night content on the treehouse laptops and phones; this supersedes "leave the screens blank").
- **Everything goes through the shared M7 code** (`blender/look.py`, enabled by `blender/coverage_m7.py`), so the full M7 render inherits it; no hero-only change. One new hook in shared code, off by default: `coverage.CAMERA_HOOK` (run after each sub-shot's camera is keyed). With it unset, M3–M5c3 are unchanged (checked in production log 43). `blender/ep/` and the sibling projects are untouched.
- **Rain on glass that lives** (`look.raindrops_group`, a shader node group in every pane's `rain_glass`; decisions 27): beads on two grids (1.1 and 1.9 cm cells) appear at a random spot, grow (area with time) and vanish when they merge or run, then come back elsewhere (the cycle index re-seeds the spot); runners in 5 × 18 cm cells collect at the top, then slide in three stick-slip jerks along a wiggling track, shrinking and leaving a thin wet trail and a line of tiny beads, and the beads in their path merge into them. On the cafe's steamed glass the runner's path is wiped clear; the old drip trails stay. Live room, cafe and treehouse panes and skylights alike. Deterministic: a function of the pane position, its seed and the clock (white noise on cell ids). M7a's rivulets are kept.
- **The clock:** a Value node `m7_clock` in each shader that moves (panes, haze, steam), keyed linearly per build with the song time (`look.clock`, after each build's layers through `coverage_m7`'s wrapper).
- **Haze drift** (`look.haze`, `config/look_m7.json` `haze_drift`): the haze's noise slides 8 cm/s sideways and 2 cm/s up and evolves (4D noise, W on the clock), with a finer layer drifting 2.2× faster (±25% density), so the shafts move. At night (O08c) there is no haze and no daylight sun: M7a added its daylight shafts to the night cutaway (production log 36).
- **Steam** (`look.steam`, replacing `coverage.steam` in M7): a camera-facing card on each of the probes' two mugs and about half the cafe's table mugs (`gb.rng("m7b_steam")`), three thin wisps that curl as they rise (a sine travelling up at about 12 cm/s with a slow sideways sway), widen and thin with height, broken into puffs; faint warm white. A Locked Track constraint keeps each card upright and turned to the sub-shot's camera (retargeted by `camera_hook`).
- **O04's phone** (decisions 28): `remotion/src/components/PhoneChat.tsx` `PhoneChatBig`: one message ("is email down for anyone else?") and the +1 count in big type, set high on the screen above where the holder's thumb hovers, the "dramatization" caption kept; same cue frames as M5 (the question on "inbox", +1 on the Hey!). `look.o04_phone` gives the phone holder its own copy (the library's motion loop kept) and maps the texture onto the phone's screen face, lit and in perspective (emission 0.9: white UI at about 200 of 255 graded, nothing clipped). `look.o04_camera`: a closer camera over the right shoulder, about 0.44 m from the screen and 30° off its normal, 28 mm, following the phone (±5-frame average), the screen low left, its top up, focus on it at f/2.8, a little handheld drift (`gb.rng("m7b_cam_O04a")`). The edit's pinned overlay (`scripts/animatic.py` `o04`) is no longer needed in M7.
- **The treehouse** (decisions 29): `look.treehouse_lift`: five soft area lights (down from under the ridge, up to the roof, the two side walls, the back wall) that light only the set as built (light linking: a receiver collection of the room's own meshes; people, instruments, screens and panes excluded), warm neutral by day (90/40/35 W), dim cool blue at night (90/25/70 W). Exposure unchanged (−0.55). Treehouse bands stay near-black silhouettes. O18e: its −0.5 camera offset dropped (`m7b.cam_expo_override`), focus starts on seat 2's dashboard and racks to the whiteboard at 1.3 s (`look.o18e_focus`).
- **The treehouse screens** (human interventions 19; decisions 30): `remotion/src/components/TreehouseScreens.tsx`: `TwoFactor` (a second-factor sign-in that keeps timing out), `AlertCall` (an automated alert ringing from (206) 555-0147), `Dashboard` (an invented service-health board, the 5xx rate spiking from about 10:26, tiles going red), `Terminal` (a health check returning 503s, timeouts and retries), `Agent` (an invented, unbranded assistant, "Kestrel", read-only, that can't reach the mail connector and summarises the log), `VideoCall` (a bridge call of six tiles with initials, some muted). Each in a night variant (O08c, 72 frames, 11:47 p.m.) and a day variant (the O18 bridge, 576 frames, 2:52 p.m.), with a loop phase per build so the heroes land on a readable beat. `look.treehouse_screens`: seat 0's laptop the assistant, seat 1's the terminal, seat 2's the dashboard; a fourth laptop beside the speakerphone, turned to the room, on the call; seat 0's phone the second factor, seat 1's the #it-help thread (O08's still), seat 2's dark while the alert rings face up on the table. Night: an area light on each laptop's screen (6 W, no specular) and a faint glow over the ringing phone; day: emission only, dimmer than the windows. A monospace face for the terminal: Noto Sans Mono (OFL), copied from the system package with its licence (`remotion/public/fonts/SOURCES.md`).
- **Closes +⅓ stop** (`m7b.close_lift`): close_guitar, close_banjo, close_fret, close_strum, close_tamb, close_kick and close_beater (decisions 29).
- **Polaroid, band only** (decisions 31): `blender/polaroid_m7.py` hides the crowd and moves the camera to about the crowd's front line (0.25, 4.3, 1.62) toward the band, 32 mm; the string lights stay at the room's level (M7a's 2.5× lit the band's faces once the crowd was gone: first take archived) and the exposure +0.15 instead of +0.5. `--with-crowd` renders M7a's. `look.py` uses `polaroid_m7b.png` when it exists.
- **Commands:**
  - `scripts/m7b_remotion.sh` (new) → `assets/gen/tex/m7b/<composition>/frames/` (13 image sequences: O04's phone, PNG 720×1560, 143 frames; the treehouse's six × night and day, JPEG q95) and `assets/gen/tex/m7b/it_help_o08.png`: 129 s, 521 MB (`log/render_logs/m7b_remotion.log`). Re-run for O04's phone after its re-layout: `scripts/m7b_remotion.sh M7-O04-PhoneScreen`.
  - `blender -b --factory-startup --python blender/polaroid_m7.py -- --out remotion/public/gen/polaroid_photo_m7b_raw.png --size 1080 --samples 64` (60 s; `log/render_logs/m7b_polaroid_r2.log`), `.venv/bin/python -I scripts/grade.py --look instant remotion/public/gen/polaroid_photo_m7b_raw.png remotion/public/gen/polaroid_photo_m7b.png`, `npx remotion still O14-Polaroid assets/gen/tex/polaroid_m7b.png --frame=0 --image-format=png --concurrency=2 --gl=swangle --props='{"photo":"gen/polaroid_photo_m7b.png"}'`.
  - Archived (`mv`): M7a's Polaroid (`archive/assets/gen/tex/polaroid_m7.png`, `archive/remotion/public/gen/polaroid_photo_m7{,_raw}.png`) and the first band-only take, whose faces read (`archive/remotion/public/gen/m7b_v1/`).
  - The first Polaroid run wrote its pose report over `log/render_logs/m7a_pose_check.log` (coverage_m7's default); restored from git, and `polaroid_m7.py` now writes its own (`m7b_polaroid_pose_check.log`).
- **Tests** (960×540, 16 samples, in the scratchpad, not kept), and what they changed:
  - Drops: the first beads were sparser than M7a's and soft-edged: density up (fine 0.55 → 0.72, medium 0.35 → 0.45, sizes +10%), edge 30% → 14% (as crisp as M7a's).
  - O04a: four camera framings. The phone held flat at chest height means a legible screen and the band can't share the frame: a framing that tilts up to the room puts the camera inside the holder's head (rejected); the closest legible framing shows the floor and crowd legs beyond, soft. The holder's thumb hovers over the screen's right half: the message moved above it.
  - O18e: a ray-cast probe of the table from O18e's camera (a scratch script): the ringing phone at any clear spot lies 1.5 m off at 16° to the lens, too flat for its caller ID; the dashboard laptop, 1 m off, is the readable screen, so the rack starts there.
  - O08c: the first night fill (12 W) left the room black; 90/25/70 W reads as a dim cool room round the screens. Laptop screen lights with specular put white ellipses on the keyboard decks: specular off.
  - Steam (60-frame sequence): wisps rise and curl; the cards stay upright and face the camera through O14c's push.

## 38. 2026-11-16 — M7b: the hero frames, the look board and the screens sheet

- **Heroes** (12; the human's list plus O03b and O03c): live room O03b (rain), O03c (kick close), O04a (the phone), O09f (banjo close), O09j (guitar close); the treehouse at night O08c; coffee shop O14c, O14d, O17b, O17j (tambourine close); treehouse O18a, O18e. Each is its sub-shot's middle frame, except O04a, shown at 90% of the shot (the question arrives at 50%; the middle frame is rendered too, `renders/m7b/O04a_mid.png`).
- **Checks first** (each run): the RTX 5090 idle (361 MiB), 33 GB RAM available, 26 GB free on disk.
- **Render** (Eevee, 1920×1080, M7 settings): `/usr/bin/time -v blender -b --factory-startup --python blender/coverage_m7.py -- --out renders/m7b/raw --still --subs O03b,O03c,O04a,O08c,O09f,O09j,O14c,O14d,O17b,O17j,O18a,O18e --size 1920x1080 --log log/render_logs/m7b_pose_check_r3.log` (3 min 52 s for 7 builds, peak 5.2 GB RSS; `log/render_logs/m7b_heroes_r3.log`) and `… --out renders/m7b/raw_late --still --subs O04a --at 0.9 …` (22 s; `m7b_heroes_o04late_r3.log`). Pose checks: no violations.
- **Superseded** (`mv`): the first round (`archive/renders/m7b/raw_v1/`: O08c with the 12 W night fill and the screen-light glare, O18e caught mid-rack) and the second (`archive/renders/m7b/raw_v2/`, `raw_late_v1/`: the drops' softer edge, production log 37). Their logs: `m7b_heroes.log`, `m7b_heroes_r2.log`, `m7b_heroes_o04late.log`.
- **Grade and sheets:** `.venv/bin/python -I scripts/m7b_board.py --grade --board --screens` (new script) → `renders/m7b/<id>.png` (grey for the live room and treehouse, cafe for the coffee shop; the M7a references of production log 36 graded the same way into `renders/m7b/m7a_ref/`), `review/m7b_look_board.jpg` (1930×7726, 1.2 MB: M7a left, M7b right, what changed above each pair) and `review/m7b_screens.jpg` (1930×2702: O04's texture before the question, with it, after the +1; O04a at 1080p 1:1 and at 960 wide 1:1; the six treehouse textures at O08c's and O18e's frames; O08c and O18e as rendered).
- **Self-check, every hero at full size:**
  - **O04 legibility:** at 1080p "# it-help", "Dana 12:57 PM", "is email down / for anyone else?", "+1 7" and "dramatization" read; the question is set at about 21 px (capitals about 15 px). At 960 wide (enlarged 1:1 crops) the question, the sender and "+1 7" still read. The thumb no longer covers the text. Before the question arrives the screen shows the empty channel.
  - **Faces:** none readable. O04a: the holder's hand and the blurred floor and legs beyond (the pale shape top right is the rug). O08c: three backs of heads; seat 0's ear and the edge of a cheek, no features. O14d: the band in the Polaroid is backlit, faces a few dark pixels. O17b: as M7a (the clapper's faintly lit brow at the left edge). O18a: silhouettes, the kick player and banjo player dark. O18e: the back of a head. Closes: hands and instruments only; in O17j the tambourine player's head is out of frame above.
  - **Silhouettes and the lift:** O18a's cedar walls, roof boards and beams read; the band is as dark as in M7a. O08c reads as a dim cedar room round four glowing laptops, people dark against them.
  - **Screens:** O08c at 1080p: the assistant's headline ("I can't reach the mail connector."), the dashboard's "5xx error rate" and value, the call grid's initials read; the terminal is texture; the phones' text is a few pixels. O18e: the dashboard in focus (title, rate, the tile names and DOWN) until the rack; the ringing phone shows as an incoming call (rings, red and green buttons), its caller ID too small. O18a: the fourth laptop's call grid at the bottom left.
  - **Guardrails:** no real product's name, logo, colours or layout on any screen; invented names; the caller ID 555-0147; nothing about AI-written code (the assistant only reads logs and is blocked; the terminal is a health check); no water, boats or tower. O04's screen and O08c's whiteboard carry "dramatization"; O18's caption is added at assembly, as before. Station sign, shafts and silhouettes as M7a.
  - **Drops at 1:1** (O03b against M7a): as many beads, as crisp, sizes more varied; runners with their trails.
  - **Other phones and screens:** the live room's crowd phones (six, in the wides) stay blank glowing screens, too small for text; the host's console monitors stay blank; O08's IT-reply insert is the full-frame Remotion phone (fine at 1080p). Unreadable text that is on screen: the treehouse terminal and phones in O08c, the ringing phone's caller ID in O18e (decisions 30).

## 39. 2026-11-16 — M7b: the treehouse dashboard after brief rev 136

- **Why:** brief rev 136 (human interventions 20, commit 20f6ea7) builds on Microsoft's preliminary report; the coordinator's note for Part C: the dashboard may echo the sourced story with invented labels; no screen mentions the July fix, who or what wrote it, or the load tests; nothing from the report reproduced; no config diff any more (decisions 33).
- **Changed:** `remotion/src/components/TreehouseScreens.tsx` `Dashboard`: the 5xx chart from 08:00 PT with a first rise from 8:20 a.m. PT and the climb from 10:26; a "gateway pool · unresponsive" grid of 60 servers going red from the left past a dashed 80% line (O08c 78 → 85%, O18 60 → 86% over each build); "capacity offline 13.8%"; "auto-reroute ON" with pool a → pool b → pool c; four services DOWN. The other five screens already kept off the July fix, the load tests and any change history (checked: the terminal is a health check, the assistant reads logs and is blocked).
- **Commands:** the two dashboard sequences archived (`archive/assets/gen/tex/m7b_v1/`) and re-rendered: `scripts/m7b_remotion.sh M7-Tree-Dashboard-night M7-Tree-Dashboard-day` (22 s; `log/render_logs/m7b_remotion_r2.log`). O08c and O18e re-rendered (`… --out renders/m7b/raw --still --subs O08c,O18e --size 1920x1080 --log log/render_logs/m7b_pose_check_r4.log`, 36 s; `m7b_heroes_r4.log`; the previous pair in `archive/renders/m7b/raw_v3/`), then `.venv/bin/python -I scripts/m7b_board.py --grade --board --screens`.
- **Seen at 1080p:** O18e (dashboard in focus) "5xx error rate 31.3%", "gateway pool · unresponsive 84%", "capacity offline 13.8%", "auto-reroute ON", the four DOWN tiles read; O08c: the rate and "gateway pool · unresponsive 82%" read, the grid reads as mostly red.
- Not touched (waiting for the new master): the O02/O23 stamp, O18's whiteboard and its two tags, the fact card.

## 40. 2026-11-16 — M7b: the motion test (drops, haze drift, steam)

- **Render** (960×540, the M7 Eevee settings, 64 samples; each sub-shot's first 120 frames): `/usr/bin/time -v blender -b --factory-startup --python blender/coverage_m7.py -- --out renders/m7b/frames_motion --subs O03a,O03b --frames 120 --size 960x540 --log log/render_logs/m7b_pose_check_motion_r2.log` (4 min 46 s; `log/render_logs/m7b_motion_r2.log`) and `… --subs O14c,O18a …` (7 min 23 s; `m7b_motion_r3.log`, `m7b_pose_check_motion_r3.log`): 1.3 s a frame in the live room, 1.0 in the coffee shop, 2.1 in the treehouse (its screens and lift lights). The first run of all four (`m7b_motion.log`, 12 min) had the drops' softer edge: its frames are in `archive/renders/m7b/frames_motion_v1/`.
- **Assembly:** `.venv/bin/python -I scripts/m7b_board.py --motion` → `review/m7b_motion_test.mp4`: 14.0 s, 420 frames, each graded (grey, cafe), h264 960×540 at 634 kb/s, AAC 128k, 1.35 MB. Four segments, each with the master's audio from its own time in `review/m5c3_animatic.mp4`: O03b 4.0 s (rain on glass, video 20.47 s), O03a 3.0 s (the wide's push through the shafts, 16.33 s), O14c 4.0 s (the probes' table, steam, the steamed windows, 111.83 s), O18a 3.0 s (the treehouse windows and skylights, 159.83 s).
- **Seen in motion:** beads appear and swell; runners pause and slide in jerks, leave a trail and a line of tiny beads and sweep the beads below them; the rivulets still run. The shafts keep their window shapes while the haze inside them drifts and changes. The steam rises in two or three curling wisps that thin out and break up, the cards staying upright through O14c's push. The treehouse panes and skylights carry the same rain; the band stays in silhouette.

## 41. 2026-11-16 — M7b, Part B: the hilltop park, diagnosis (no rebuild)

- **Why:** human interventions 18 ("the whole hilltop scene is off ... starting from the hill itself") and 19 (a generated far plate behind the Blender park; the rebuild waits for a direction from the concept stills).
- **Frames:** `.venv/bin/python -I scripts/m7b_park_sheet.py --frames` → `review/m7b_park_frames.jpg` (the middle frame of all 22 park sub-shots, O19b–O22g, from `review/m5c3_animatic.mp4`, then the M7a look of O20a, O19b, O20c and O22d). Read with `blender/sets.py` `park`, `hill_z` and `blender/look.py` `park`, `skyline`, `conifer`.
- **Diagnosis, one line per item:**
  - **Scale:** the city's nearest blocks are 300 m off and up to 80 m tall, the firs 14–30 m at 13–120 m, so towers, trees and crowd come out about the same size in frame: the skyline reads as a model set just behind the trees, not a city kilometres away.
  - **The hilltop:** there is no crest. `hill_z` is a 60 m-wide Gaussian dome 32 m high: under the crowd it falls 0.9 m in 10 m, and from a 1.6–1.75 m camera its own curve is the horizon (O19b shows a grey hemisphere). Nothing falls away in front of the crowd, no slope or treetops below a brow, and the city's base is only 2–5° below eye level, so it never reads as below.
  - **Ground surface, paths, grass:** one noise-tinted grass shader on a smooth mesh (no mown stripes, tussocks, trodden or muddy patches, wet sheen in hollows, blades at the edges); the path is a straight 2 × 16 m slab with hard edges and no border; nothing else a park has (edging, a bench, a bin, a low rail at a viewpoint).
  - **Tree placement and density:** 140 firs scattered in a ring 13–123 m out with a hard wedge cut for the view, evenly spaced, one shape family, no undergrowth, saplings or ground contact; flat sprays with an alpha fringe, so close up they read as cut-outs; the frame is symmetric, a tall fir at each side.
  - **Fog depth layering:** each surface fades on its own exponential with distance, with no fog banks between layers and one flat fog colour, so near trees, far trees and skyline are three flat greys; the skyline is three evenly spaced rows of flat-topped boxes with uniform floor bands: stacked rectangles, no streets, no mid-ground roofs or street trees, no distant ridges.
  - **Horizon and camera height:** the cameras sit at 1.6–1.75 m aimed slightly up at the band (targets at 2.0 m), so the horizon cuts mid-frame behind the crowd's heads; O20e's high wide (4.6 m) sees more lawn but still no drop; the sky is a flat bright card.
  - **Lamp post:** a plain cylinder with a box-and-cone head, no base, banding or glazing, glowing white in daylight: it reads as a prop.
  - **A real foggy hilltop park over a city:** the lawn rolls to a brow where the ground drops away; the tops of the slope's trees show just below it; then a mid-ground of roofs and street trees descends in paler layers; the city sits kilometres off with its base well below the horizon and its towers half dissolved into a low cloud base; the near wet grass is dark and saturated and contrast falls off layer by layer; the people stand on the near lawn with only air behind them.
- **Recommendation for the rebuild (with the human's far plate, human interventions 19):**
  - **Generated plate:** everything beyond about 150 m: the city (2–6 km), the mid-ground neighbourhoods and ridges, the far tree lines, the fog layers and the sky, as one wide plate (at least 2560 px wide, wider than 16:9 so the wides and O20e's truck stay inside it) on a large curved card about 1 km out. At that distance no camera here (the largest move is O19b's 15 m rise) shows parallax. O22d is the same plate animated.
  - **Stays 3D:** the crest lawn and path people stand on (contact, feet, the walker in O22c), the brow and the first 20–40 m of the drop (O19b rises over it), the near firs within about 60 m (they parallax in O19b and O20e and frame the wides), the lamp post with Switch and its outlet box, the umbrella, drizzle and the near fog.
  - **Between (optional):** the treetops just below the brow (40–150 m) as 2.5D cards cut from the plate's own trees, if the rebuild wants a cheap middle layer.
  - **Rebuild the hill itself:** a real crest (a plateau of 15–20 m with a defined brow and a 25–35° slope beyond), the city's base 80–120 m below the crest, cameras that can see past the brow.

## 42. 2026-11-16 — M7b, Part B: park concept stills and far-plate candidates (FLUX.2 [dev])

- **Why:** human interventions 18–19: concept stills to agree the park's direction before it is rebuilt, and candidates for the generated far plate the human chose (decisions 32). Reference only, not footage.
- **Checks first:** no Blender running, the RTX 5090 idle (361 MiB, 0%), 33 GB RAM available, 25 GB free on disk; nothing else on ComfyUI.
- **ComfyUI:** v0.42.1, started by the agent (`~/ComfyUI/.venv/bin/python ~/ComfyUI/main.py --listen 127.0.0.1 --port 8188`, log `log/m7b_comfy.log`), one job at a time; afterwards the models were freed (`/free`) and the server stopped by its PID. Memory sampled every 2 s (`log/render_logs/m7b_comfy_mem.log`): peak 37.4 GB RAM used (1.7 GB available), VRAM peak 32.1 GB. Nothing was killed. RAM back to 3 GB used after.
- **Model and graph:** M4's (`config/m4_stills.json`; hashes in production log 10): FLUX.2 [dev] fp8mixed, the Mistral 3 small fp4 text encoder, flux2-vae; 28 steps, euler, guidance 4.
- **New:** `config/m7b_park_concepts.json` (prompts as subject + style; the constraints written into each style as "no …": no people, faces, text, signs, logos, landmarks, observation towers, boats, ships, ferries, water, lake, bay, river, sea; every building generic), `scripts/m7b_concepts.py` (adapted from `scripts/stills.py`, graph unchanged), `config/seeds.json` `m7b_park_concepts` (41, 42). Prompts verbatim in `log/prompts/m7b/<item>.txt` and `log/prompts/m7b_park.md`, one row per take.
- **Command:** `/usr/bin/time -v .venv/bin/python -I scripts/m7b_concepts.py > log/m7b_concepts_batch.log` → `assets/gen/stills/m7b_park/<item>/<item>_s<seed>.png`: 3 concept prompts at 1920×1088 (park_crest_a and park_crest_b for O20a, park_rise for O19b; 49–82 s each) and 2 plate prompts at 2560×1440 (plate_city, plate_ridges; 106–108 s each), 2 seeds each: 10 takes, 12 min 53 s.
- **Review** (every take at full size; `config/m7b_park_concepts.json` `review`, `log/prompts/m7b_park.md`): no take has people, text or a landmark tower. **Rejected:** plate_city s41 (a pale fog band under the city reads as a lake, and its tallest dark stepped tower may evoke a real one). **Not kept:** park_crest_a s41 (redundant). **Kept:** 5 concepts, 3 plates.
  - The two park_crest_b takes are the direction the diagnosis asks for: a lawn that ends at a brow, the ground falling away, roofs and bare trees below, the city kilometres off and below the horizon, fog in layers. FLUX's own hills (park_crest_a, park_rise) come out as domes too, so the brow has to be modelled, not prompted.
  - **Far plate:** plate_city s42 is the recommended plate (generic towers in the cloud base, streets and conifer lines in fog; it would need extending sideways for O20e's truck); plate_ridges s41 and s42 give the far tree lines, their towns are slab housing (use the ridges only).
- **Sheet:** `.venv/bin/python -I scripts/m7b_park_sheet.py --concepts` → `review/m7b_park_concepts.jpg` (1930×3111, 0.9 MB): the current O20a and O19b, the five concepts and three plates labelled, the two takes not kept small at the bottom.
- `assets/gen/stills/m7b_park/` is out of git (in the manifest); ComfyUI's own copies are in `~/ComfyUI/output/aso_m7b/`.

## 43. 2026-11-16 — M7b: M5c3 reproducibility, disk, GPU; ready for the human

- **M5c3 still reproduces** with the M7 hooks off (`coverage.CAMERA_HOOK` is new in shared code): `blender -b --factory-startup --python blender/coverage_m5c.py -- --out <scratch>/repro --still --subs O03a,O04a,O20a --log <scratch>/repro_pose.log` against `renders/m5c3/frames/O03a/0073.jpg`, `O04a/0072.jpg`, `O20a/0032.jpg`: PSNR 45.8, 47.8 and 42.8 dB (mean absolute difference 0.84, 0.57, 1.14 of 255), the JPEG error of the M5c3 frames, as in production log 35.
- **Disk used by M7b:** about 1.2 GB in the repository's folders (`assets/gen/tex/m7b/` 536 MB of screen-texture sequences, `renders/m7b/` 348 MB of which the motion frames are most, `archive/renders/m7b/` 138 MB, `archive/assets/gen/tex/m7b_v1/` 82 MB, `assets/gen/stills/m7b_park/` 42 MB, the Polaroid and review files about 20 MB), plus 43 MB of test stills in the scratchpad and ComfyUI's own 42 MB copy of the stills. 25 GB free.
- **GPU and RAM:** only this project's jobs ran, one heavy job at a time (the RTX 5090 at 361 MiB before each); ComfyUI ran only with Blender stopped and was shut down afterwards (production log 42).
- **Superseded, in `archive/`:** M7a's Polaroid and the first band-only take; the hero rounds before the final one; the first motion frames; the pre-rev-136 dashboard sequences. Nothing deleted.
- **Calls for the human:** decisions 34.
- `scripts/manifest.sh` → 2,409 files.

## 44. 2026-11-16 — M7c: M7b reference stills of every park hero (before any M7c change)

- **Why:** the coordinator's M7c brief (human interventions 22: rebuild the hilltop park in the direction of concepts 1–2, with the generated far plate; three small fixes). The M7c park board pairs each park hero with its M7b look, and only O19a, O20a, O20c and O22d were on an earlier board, so every park hero is rendered here with the code as committed (93b6de6), before any M7c change.
- **Checks first:** the RTX 5090 idle (361 MiB, 0%), 34 GB RAM available, 25 GB free on disk, no other job running.
- **Command:** `/usr/bin/time -v blender -b --factory-startup --python blender/coverage_m7.py -- --out renders/m7c/m7b_ref/raw --still --subs O19a,O19b,O19e,O20a,O20c,O20e,O20g,O20i,O21a,O22a,O22b,O22c,O22d,O22f,O22g --size 1920x1080 --log log/render_logs/m7c_m7b_ref_pose_check.log` → `renders/m7c/m7b_ref/raw/<id>.png` (16-bit, each sub-shot's middle frame). 4 min 0 s wall for 5 builds; peak 4.6 GB RSS (`log/render_logs/m7c_m7b_ref.log`). Pose check: no violations.

## 45. 2026-11-16 — M7c Part B: the assistant unnamed, O04's question from the first frame, the crowd phones' screens (Remotion)

- **Why:** human interventions 22 (1: drop "Kestrel", Microsoft's ASP.NET Core web server, and label the screen "assistant · read-only"; 2: O04a's question on the phone from the start, the +1 still climbing on the Hey!) and the coordinator's Part B 3 (the live room's crowd phones, blank glowing screens in M7b, decisions 28: plausible, generic, unreadable at distance, nothing branded).
- **Changed:** `remotion/src/components/TreehouseScreens.tsx` `Agent`: the header is a plain tile (three lines, no letter) and "assistant · read-only"; the composer reads "Ask about the logs…"; no name anywhere (`grep -r Kestrel remotion/src scripts blender config` finds nothing). `remotion/src/Root.tsx`: `M7-O04-PhoneScreen` takes `askAt: -100` (the question and "+1 6" from frame 0; "+1 7" on the Hey!, the M5 cue). M5's `M5-O04-PhoneScreen` is unchanged.
- **New:** `remotion/src/components/CrowdPhones.tsx`: `CrowdLock` (a dim generic wallpaper, "Thursday, November 12", 1:04, the #it-help notification and "mail · couldn't refresh · 3 tries"), `CrowdCamera` (recording the band: a crop of the M7a live-room wide `renders/m7a/O03a.png`, a red dot and 0:41, a shutter ring; no real camera app's UI); the chat is M5's `PhoneChatScreen` (the #it-help thread, +1 7). Compositions `M7c-Crowd-Lock`, `M7c-Crowd-Camera`, `M7c-Crowd-Chat` (stills). `scripts/m7c_remotion.sh` (new) renders them and re-runs `scripts/m7b_remotion.sh` for the three changed sequences.
- **Commands:** the M7b sequences archived first (`mv` to `archive/assets/gen/tex/m7b_v2/`: `M7-O04-PhoneScreen`, `M7-Tree-Agent-night`, `M7-Tree-Agent-day`), then `scripts/m7c_remotion.sh` (31 s; `log/render_logs/m7c_remotion.log`) → `assets/gen/tex/m7b/M7-O04-PhoneScreen/frames/` (143 PNG), `M7-Tree-Agent-night/frames/` (72), `M7-Tree-Agent-day/frames/` (576), `remotion/public/gen/m7c_viewfinder.jpg` (480×1040 crop of `renders/m7a/O03a.png`), `assets/gen/tex/m7c/crowd_lock.jpg`, `crowd_camera.jpg`, `crowd_chat.jpg` (540×1170, JPEG q95).
- **Checked by eye** (full-size frames): the assistant's header reads "assistant · read-only" with no name or initial; O04's frame 0 shows the question and "+1 6", the last frame "+1 7"; the crowd textures carry no brand, logo or real UI, and the camera view's band is backlit (no readable face at the texture's own size).

## 46. 2026-11-16 — M7c Part A: the far plate extended (FLUX.2 [dev] outpainting) and O22d generated (LTX-2.3)

- **Why:** human interventions 19 and 22: far plate 1 (`plate_city_s42`) behind the rebuilt park, plates 2–3 (`plate_ridges_s41/s42`) as the far tree lines, wide enough for O20e; O22d is the same plate animated by image-to-video.
- **Checks first:** no Blender running, the RTX 5090 idle (361 MiB), 34 GB RAM available, 25 GB free on disk, nothing else on ComfyUI.
- **ComfyUI:** v0.42.1, started by the agent (`~/ComfyUI/.venv/bin/python ~/ComfyUI/main.py --listen 127.0.0.1 --port 8188`, log `log/m7c_comfy.log`), one job at a time; FLUX freed (`/free`) before LTX; stopped by its PID afterwards (RAM back to 3 GB used). Memory sampled every 2 s by a sampler that exits with the server (`log/render_logs/m7c_comfy_mem.log`; its first attempt watched the wrapper's PID and stopped early): peak 37.3 GB RAM used (1.75 GB available), swap 13.7 GB, VRAM 32.1 GB. Nothing was killed.
- **New:** `config/m7c_plate.json` (passes, prompts as subject + style with the constraints written in as "no ...", the layout, picks, review, O22d), `scripts/m7c_plate.py` (`--extend`, `--compose`, `--o22d`, `--sheet`), `blender/m7c_agx_lut.py`; `config/seeds.json` `m7c_plate_extend` (41, 42) and `m7c_o22d` (41, 42, 43). Prompts verbatim in `log/prompts/m7c/<pass>.txt` and `log/prompts/m7c_park.md` (one row per take, the review table).
- **Outpainting** (model, steps, sampler and guidance as M4 and M7b): each pass is a 2560×1440 canvas of 1280 px of the panorama so far and 1280 px to fill; VAEEncode, SetLatentNoiseMask, DifferentialDiffusion (the mask value is the local denoise strength), Flux2Scheduler, SamplerCustomAdvanced. L1 and R1 continue the city to the left and right; L2 and R2 start from the ridges plates' halves next to the city (init strength 0.9) for the far tree lines, their far town regenerated.
  - Run 1 (`log/m7c_extend_1.log`, 7 min 51 s): L1, R1 × 2 seeds. **Rejected:** a blurred stripe at every seam (the mask was under 1 for the first 64 px of the filled half). Archived to `archive/assets/gen/stills/m7c_park/extend_v1/`; the mask fixed (1 over the whole filled half, ramping to 0 over 160 px into the known half).
  - Run 2 (`log/m7c_extend_2.log`, 7 min 16 s): L1, R1 × 2. Picks L1_s42, R1_s41.
  - Run 3 (`log/m7c_extend_3.log`, 7 min 22 s): L2, R2 × 2. **Rejected:** the ridges plates' far slab blocks stayed (M7b took those plates for their tree lines only); R2_s41 also had a hard vertical edge. Archived to `archive/assets/gen/stills/m7c_park/extend_v2/`; the full-strength band next to the junction widened (520 px, 200 px soft edge) and rows 360–600 of the ridges half regenerated from a blurred fill.
  - Run 4 (`log/m7c_extend_4.log`, 7 min 33 s): L2, R2 × 2. Picks L2_s42, R2_s42; R2_s41 rejected (a hard edge and a flat green patch like a sports field), L2_s41 not picked (a sharp-topped pale fog band, too close to a lake).
  - 106–131 s a take. Outputs `assets/gen/stills/m7c_park/extend/<pass>/<pass>_s<seed>.png` with each pass's canvas and mask; ComfyUI's own copies in `~/ComfyUI/output/aso_m7c/`.
- **Panorama:** `.venv/bin/python -I scripts/m7c_plate.py --compose` → `assets/gen/stills/m7c_park/pano/pano.png` (7680×1440: L2, L1, the original plate, R1, R2; about 128° at 60 px a degree). Each seam is blended inside its pass's mask ramp (160 px); the sky's brightness is evened across the seams (a per-column gain from the sky rows' medians, smoothed at 60 and 900 px) and, near each seam, the bright featureless sky rows are blurred along the horizon with their fine grain kept: the cloud deck's bands had ended at the passes' edges (checked at 1:1 before and after). The plate in the centre is untouched below the cloud deck.
- **The Blender texture:** `blender -b --factory-startup --python blender/m7c_agx_lut.py` (`log/render_logs/m7c_agx_lut.log`) → `assets/gen/tex/m7c/agx_lut.png` and `.json`: 2,048 scene-linear greys saved through the park wides' colour management (AgX, Medium High Contrast, exposure −0.2). `--compose` maps each panorama value through its inverse (per channel), so the plate reads in the render as generated, and writes `assets/gen/tex/m7c/park_backdrop.png` (7680×1440, 16-bit RGBA, Non-Color: linear / 9.15, alpha fading the top rows 40–220 out into the sky; below the mist band, rows 1180–1270, the valley-fog colour; the outer 360 columns soften to their own profile) and `park_backdrop.json` (the scale; the sky, horizon-haze and valley-fog colours, scene-linear, that the 3D's world and fog match).
- **O22d:** `.venv/bin/python -I scripts/m7c_plate.py --o22d` (`log/m7c_o22d.log`, 1 min 17 s): input `assets/gen/stills/m7c_park/o22d/o22d_input.png` (the plate's crop [318, 0, 2322, 1102] at LTX's 1280×704 aspect, no extension in it); 1280×704, 24 fps, 5 s; seeds 41–43 (40, 18, 18 s) → `assets/gen/clips/O22d/O22d_s41.mp4`, `_s42`, `_s43`. Camera motion, frame 1 to 121 (ORB features, similarity fit; a scratch check): s41 scale 0.997, drift (14, 18) px; s42 scale 1.042, pan 34 px; s43 scale 1.22 (a push). **Pick O22d_s41** (nearly locked; the fog bank thickens and drifts over the wooded hill and the houses, the cloud base holds over the tower tops, buildings keep their shapes at 1:1). s42 not picked (a fallback), s43 rejected.
- **Review:** no take kept has people, faces, text, logos, water, boats, a lake-like band or a landmark tower; the bright fog bands in L2_s42 and R2_s42 read as fog at 1:1 (tree tops through them, soft edges). Notes in `config/m7c_plate.json` `review` and `o22d.review`; the sheet comes with the board (production log 48).

## 47. 2026-11-16 — M7c Part A: the hilltop park rebuilt from the hill up (code, tests, heroes)

- **Why:** human interventions 18 ("the whole hilltop scene is off … starting from the hill itself") and 22 (rebuild to concepts 1–2, with the generated far plate); the coordinator's list from production log 41's diagnosis (crest and brow, scale and distance, camera height and horizon, ground surface, tree placement, 3D firs with depth, fog in depth, the lamp post).
- **Code** (everything in the M7 path; `blender/ep/`, sets, coverage, animatic and perf code untouched, so M5c3 reproduces: production log 49):
  - New: `blender/park_m7c.py` (the ground's height function, rim and profiles; the lawn, gravel, stone, puddle, needle, bark, blade and painted materials with layered fog; the ground mesh, path, kerbs, terrace, wall, bench, puddles and blades; fir and bare-tree prototypes and their placement; houses; the far plate's cylinder and the world matched to it; the near haze; the fog curtains; the lamp post; O19b's keys).
  - `blender/look.py`: `M7C` (config m7c.on); `enable()` points `sets.hill_z` at the new ground; `park()` hands the park to `park_m7c.build` after the sun is set (the M7a skyline and fog box are not built); `conifer()` skips the park's M3 cone-tree calls and gives the treehouse's forest the new firs (`_m7c_forest_mats`: the forest's own fog, the day's lighter forest fog), with the crown-clearance reach raised for the longer sprays; `after_layers()` re-excludes the performers' copies from the view layer (the O22 stray-copy bug, decisions 37) and textures the live room's crowd phones (`crowd_phones`); `settings()` sets volumetric_end 160 m in the park.
  - `blender/coverage_m7.py`: the park presets replaced from config m7c.cameras (decisions 36), O19b's M5 keys replaced (`park_m7c.o19b_keys`, fitted to the O19b sub-shot and then held), M5b's fog cards replaced by the curtains, O22d marked "clip" so it isn't rendered.
  - `config/look_m7.json` m7c: the ground, path, viewpoint, puddles, blades, trees (10 hand-placed framing firs and 8 seeded groups), houses, backdrop, fog, lamp, cameras, clip_subs, crowd phones.
  - Seeds: `gb.rng("m7c_fir_<k>")`, `m7c_bare_<k>`, `m7c_trees`, `m7c_path`, `m7c_puddles`, `m7c_fringe`, `m7c_houses`, `m7c_park` (main 41).
- **What the park is now:** the crest at z 0 under the crowd and band; its rim 13–15 m behind the band, 14 m behind the camera side, 22 m to the sides. The brow rolls 0.75 m over 5 m, then the ground drops at 32° toward the view (−16 m at 26 m past the rim, −38 m at 86 m, −71 m at 236 m), 18° on the camera side and 26° at the sides. The 3D runs to 260 m out (93,000-vertex ground). The plate sits 2 km out, the city 2–4 km off in it, its base about 2° below the eye and well below the crest. In the park: 218 firs from 10 prototypes (4.5–34 m), 122 bare trees from 6 prototypes, 12 houses, a 1.7 m gravel path (now 50 m, down the back slope) with 140 kerbs, a viewpoint terrace with a 12-block wall and a bench, 9 puddles, 8,040 blades, 4 fog curtains.
- **Test passes** (960×540, 16 samples, in the scratchpad, not kept), and what each changed:
  1. O20a: the firs read as bare poles. Their sprays were horizontal plates, invisible edge-on from eye height; the lawn was near black; a bright haze and a 16 m fog curtain right behind the band hid the drop. Fix: sprays rolled round their branch, a hanging card on more branches, fuller alpha; the lawn brighter and wetter; the haze 0.005 → 0.0022 per m; the curtains lowered into the valley.
  2. O20a, O20e, O20c: the drop and the plate read from O20e (the valley, the city, bare trees at the brow); the firs still looked like flat fronds. Fix: more, smaller sprays and interwhorl branches.
  3. O19b, O22a, O22c, O22f: the kerbs stepped on the back slope (now pitched along it); the firs' tiers too regular (whorls jittered, more droop); the lawn read white from below the crest (its sheen cut).
  4. O19b at its "last" frame was still mid-rise: M5's keys ran over the whole build, under the closes. The keys are now fitted to the O19b sub-shot and held.
  5. O19b's start: the path ended in mid-slope (extended to y −40), young firs moved closer to the rise.
  6. O19a, O20a, O20e, O20c: the firs rebuilt as clusters of sprays fanned round each branch, with clumpy, ragged needle alpha in place of a serrated comb. They no longer read as flat sprays from the deck, the lawn or below.
- **Heroes, round 1** (`log/render_logs/m7c_heroes_r1.log`, `m7c_pose_check_r1.log`; 4 min 15 s): O19a, O19b, O19e, O20a, O20c, O20e, O20g, O20i, O21a, O22a, O22b, O22c, O22f, O22g at 1920×1080. They showed the firs still frond-like (fixed in test 6), M5c3–M7b's second figure in O22a (decisions 37) and a stray clamp cylinder on the lamp post that read as a second post in O22b (removed). Archived to `archive/renders/m7c/raw_v1/` and `graded_v1/`.
- **Heroes, round 2:** `/usr/bin/time -v blender -b --factory-startup --python blender/coverage_m7.py -- --out renders/m7c/raw --still --subs O19a,O19b,O19e,O20a,O20c,O20e,O20g,O20i,O21a,O22a,O22b,O22c,O22f,O22g --size 1920x1080 --log log/render_logs/m7c_pose_check_r2.log` (4 min 16 s for 5 builds; peak 5.2 GB RSS; `log/render_logs/m7c_heroes_r2.log`). Each still took 1.9–6.8 s with scene sync; park builds 45–75 s with the performances. Pose check: no violations. O22d is not rendered (decisions 35).
- **Fixes stills:** `… --out renders/m7c/fixes/raw --still --subs O03a,O08c …`, `… --still --at first --subs O04a …` and `… --still --subs O03f …` (`log/render_logs/m7c_fixes*.log`): the crowd phones textured, 6 of 6 in each live build.

## 48. 2026-11-16 — M7c: the park board, the plates sheet, the fixes sheet and the motion test; the self-check

- **New:** `scripts/m7c_board.py` (`--grade`, `--board`, `--plates`, `--fixes`, `--motion`) and `scripts/m7_inserts.py`. The latter slots O22d's clip into the M7 assembly as `scripts/animatic.py` slots O06's: the picked take read by time (24 → 30 fps, no interpolation, from its first frame), Lanczos to cover 1920×1080 (1964×1080, centre crop), trimmed to the sub-shot's 141 frames, graded home with grain seeded per video frame.
- **Grade:** `.venv/bin/python -I scripts/m7c_board.py --grade` → `renders/m7c/<id>.png` and `renders/m7c/m7b_ref/<id>.png` (grey; home for O22b on, from "Remember Wednesday"). O22d's M7c frame is the clip's middle frame. The fixes stills were graded the same way into `renders/m7c/fixes/` (O03a, O03f, O08c; O04a at its first video frame).
- **Sheets:** `.venv/bin/python -I scripts/m7c_board.py --board --plates --fixes`:
  - `review/m7c_park_board.jpg` (1930×9190, 2.4 MB): 15 park heroes (O19a, O19b, O19e, O20a, O20c, O20e, O20g, O20i, O21a, O22a, O22b, O22c, O22d, O22f, O22g), M7b left and M7c right, labelled.
  - `review/m7c_plates.jpg` (1930×4935, 1.2 MB): the three source plates, the panorama with its seams marked, each pass's two takes with the notes, both rejected runs, and O22d's three takes (frames 1, 61, 121) with the pick.
  - `review/m7c_fixes.jpg` (1930×5513, 0.8 MB): the assistant texture by day and night; O08c at 1080p with a 3× crop of the assistant's laptop; O04a's first frame at 960 wide, its texture and a 1:1 crop; O03f (the high wide over the live-room crowd) with 3× crops of two crowd phones, and the three phone textures.
- **Motion test:** `/usr/bin/time -v blender -b --factory-startup --python blender/coverage_m7.py -- --out renders/m7c/frames_motion --subs O19a,O19b,O20e --size 960x540 --log log/render_logs/m7c_pose_check_motion.log` (9 min 37 s; `log/render_logs/m7c_motion.log`). Seconds a frame at 960×540: O19a 0.83 (the treehouse and its new forest), O19b 1.39, O20e 1.46. Then `.venv/bin/python -I scripts/m7c_board.py --motion` → `review/m7c_motion_test.mp4`: 17.3 s, 519 frames, h264 960×540 at 650 kb/s (558 kb/s measured), AAC 128k, 1.5 MB. O19a then O19b with M5's 10-frame dissolve (9.6 s, the door to the crest), O20e (3.0 s, the truck past the plate), O22d (4.7 s, the generated clip, home grade). Each part carries the master's audio from its own time in `review/m5c3_animatic.mp4`. The graded frames are in `renders/m7c/frames_motion/graded/` (out of the manifest, like every frame sequence).
- **1080p timing** (the full M7 render's estimate): `blender -b --factory-startup --python blender/coverage_m7.py -- --out <scratch>/timing --subs O20a,O22a --frames 24 --size 1920x1080` (`log/render_logs/m7c_timing.log`): 2.64 and 2.25 s a frame (frames 2–24), against M7a's 2.28 in the park. The new park adds about 0.2 s a frame, so the cut's 1,742 park frames take about 6 min longer.
- **Self-check, every frame at full size** (crops at 1:1 and 2–3× where people face the camera or text could show):
  - **Faces:** none readable. The band faces the camera only as backlit silhouettes (O20a, O21a, O19b, O20e from above); O20g's head is out of focus and dark; the walker is seen from behind (O22a, O22f) or at the feet (O22c). M5c3–M7b's second figure, which faced the camera in O22a, is gone (decisions 37). The live room's phones show no person; the camera view's band is backlit.
  - **Guardrails:** no water but nine small puddles (up to about 1.5 m); no bay or lake-like band in the plate (its pale bands are fog with tree tops through them); no boats; no Space Needle or recognisable tower (generic towers in the cloud base); no logos or text but the existing Remotion textures (SESSION 503, Switch, the dramatization captions); one umbrella; Switch's plane untouched; nothing about AI-written code.
  - **Plate:** no visible seam between plate and 3D. The plate's lower edge sits behind the 3D slope and the valley fog; the sky fades into the world with no line; at the plate's seams the sky is evened. In O20e's truck the plate holds still while the crest, firs and crowd move past it, which is right for something 2–4 km away; at 2 km its parallax in any move here is under 0.5 px. The weakest point is a hill fading into a vertical bank of fog at the L1 seam (22° left of centre); it reads as fog.
  - **Clipping:** none seen. Firs keep clear of the crowd and band (the framing firs stand 12–20 m out, their lowest branches 2 m or more up; placement keeps every crown out of the people's circle) and of every camera path. O19b's rise passes no crown (its frames' brightness runs smoothly, with no frame swallowed by foliage). The bench is 1.8 m from the walker's end point. The kerbs follow the slope.
  - **Still weak:** see decisions 39 and the report. The firs are clustered cards, convincing as silhouettes and in fog, flatter in shading up close. The O08c night panes' pale shapes are pre-existing.

## 49. 2026-11-16 — M7c: M5c3 reproducibility, disk, GPU; ready for the human

- **M5c3 still reproduces** with the M7 hooks off (this pass changed only `blender/look.py`, `blender/coverage_m7.py`, the new `blender/park_m7c.py` and `blender/m7c_agx_lut.py`, and the M7 config): `blender -b --factory-startup --python blender/coverage_m5c.py -- --out <scratch>/repro --still --subs O03a,O04a,O20a,O22a` (`log/render_logs/m7c_m5c3_repro.log`) against `renders/m5c3/frames/O03a/0073.jpg`, `O04a/0072.jpg`, `O20a/0032.jpg` and `renders/m5c/frames/O22a/0055.jpg`: PSNR 45.8, 47.8, 42.8 and 45.6 dB (mean absolute difference 0.84, 0.57, 1.14 and 0.87 of 255), the JPEG error of those frames, as in production log 43. The M5c frame of O22a has the stray second figure too (decisions 37).
- **Render times:** park heroes 1.9–6.8 s a still at 1080p (4 min 16 s for 14 stills in 5 builds); park animation 2.25–2.64 s a frame at 1080p (M7a: 2.28); the motion test 0.83–1.46 s a frame at 960×540; FLUX.2 outpainting 106–131 s a take (4 runs, 16 takes, about 30 min); LTX-2.3 18–40 s a take.
- **Disk used by M7c:** about 1.2 GB in the repository's folders: `renders/m7c/` 639 MB (the motion frames 333 MB, of which the graded PNGs 299 MB; heroes, references and fixes 281 MB); `archive/renders/m7c/` 148 MB; `assets/gen/stills/m7c_park/` 86 MB and `archive/assets/gen/stills/m7c_park/` 67 MB; `assets/gen/tex/m7c/` 42 MB; the re-rendered screen sequences 85 MB, with the old ones archived (`archive/assets/gen/tex/m7b_v2/`, 82 MB); `assets/gen/clips/O22d/` 2.4 MB; the review files 6 MB. Outside the repository: ComfyUI's own copies (`~/ComfyUI/output/aso_m7c/`, 101 MB) and test stills in the scratchpad (about 100 MB). 24 GB free.
- **GPU and RAM:** only this project's jobs ran, one heavy job at a time; ComfyUI ran only with Blender stopped and was stopped by its PID afterwards (production log 46; peak 37.3 GB RAM used, VRAM 32.1 GB). Blender peaked at 5.3 GB RSS.
- **Superseded, in `archive/`:** the M7b screen sequences (`assets/gen/tex/m7b_v2/`), two rejected outpainting runs (`assets/gen/stills/m7c_park/extend_v1/`, `extend_v2/`), the first M7c hero round (`renders/m7c/raw_v1/`, `graded_v1/`). Its logs were renamed `_r1`, not overwritten. Nothing deleted.
- **Calls for the human:** decisions 39.

## 50. 2026-11-16 — M7d: M7c reference stills of the instrument closes and O19b's start (before any M7d change)

- **Why:** human interventions 23 (M7c approved; one more pass, M7d, on the weak points already flagged). The M7d board pairs each change with the approved version. The park heroes are already in `renders/m7c/` (M7c) and O08c in `renders/m7c/fixes/`; the instrument closes (weak point 6) were only rendered at M7b in the live room, and O19b's opening (the coordinator's point 7) never as a still. They are rendered here with the code as committed (f3afa8d), before any M7d change.
- **Checks first:** no Blender or ComfyUI running, the RTX 5090 idle (361 MiB), 34 GB RAM available, 24 GB free on disk.
- **Commands:**
  - `/usr/bin/time -v blender -b --factory-startup --python blender/coverage_m7.py -- --out renders/m7d/m7c_ref/raw --still --subs O09f,O09h,O09j,O11e,O17a,O17f,O20f,O20h --size 1920x1080 --log log/render_logs/m7d_m7c_ref_pose_check.log` → `renders/m7d/m7c_ref/raw/<id>.png` (16-bit, each sub-shot's middle frame): every banjo close (close_banjo: O09f, O11e, O17f, O20f; close_fret: O09h) and every guitar close (close_guitar: O09j; close_strum: O17a, O20h). 3 min 10 s for 4 builds, peak 5.2 GB RSS (`log/render_logs/m7d_m7c_ref.log`). Pose check: no violations.
  - `… --out renders/m7d/m7c_ref/raw_first --still --at 0.1 --subs O19b --size 1920x1080 --log log/render_logs/m7d_m7c_ref_o19b_pose_check.log` → `renders/m7d/m7c_ref/raw_first/O19b.png` (frame 13 of 123, the start of the rise); 56 s (`log/render_logs/m7d_m7c_ref_o19b.log`). No violations.
- **Seen:** the guitar closes are near-black bodies against the windows (O09j's spruce top barely separates from the shirt); every close_banjo sees the pot edge-on (the rim and brackets, not the head). O19b's start: at the top of the path the crest's back edge is a flat-topped block with sloped sides, the path's level bed standing proud where the lawn rolls down round it (`blender/park_m7c.py` flat_mask keeps the bed level inside the rim on the back slope too).

## 51. 2026-11-16 — M7d: the far plate's L1 seam inpainted (FLUX.2 [dev]); the panorama and its Blender texture rebuilt

- **Why:** human interventions 23, weak point 2: at the L1 seam of the approved panorama (about 22° left of centre, columns near 2560) a hill fades into a vertical bank of fog (decisions 39.3).
- **Checks first:** no Blender running, the RTX 5090 idle (484 MiB), 34 GB RAM available, 24 GB free on disk.
- **ComfyUI:** v0.42.1, started by the agent (`~/ComfyUI/.venv/bin/python ~/ComfyUI/main.py --listen 127.0.0.1 --port 8188`, log `log/m7d_comfy.log`; PID 4121806, the server itself), one job at a time; models freed (`/free`) and the server stopped by its PID afterwards. Memory sampled every 2 s by a loop on that PID, which exited with it (`log/render_logs/m7d_comfy_mem.log`): peak 37.0 GB RAM used (2.1 GB available), swap 13.7 GB, VRAM 31.7 GB. Nothing was killed; RAM back to 3 GB used.
- **New:** `config/m7d_plate.json` (the crop, the soft mask, the prompt, the pick and the review), `scripts/m7d_plate.py` (`--seam`, `--compose`, `--sheet`), `config/seeds.json` `m7d_seam` (41, 42, 43). The prompt verbatim in `log/prompts/m7d/seam.txt` and `log/prompts/m7d_seam.md` (one row per take, the review table).
- **Inpaint:** M7c's outpainting graph (FLUX.2 [dev] fp8mixed, 28 steps, euler, guidance 4; VAEEncode, SetLatentNoiseMask, DifferentialDiffusion) on a 2048×1440 crop of the approved panorama (columns 1536–3584); the mask, in panorama coordinates, is strength 1 over columns 2380–2760 and rows 230–690, a smoothstep to 0 over 200 px to the sides and 80 px above and below, so the evened sky above and the houses and mist band below are held. `/usr/bin/time -v .venv/bin/python -I scripts/m7d_plate.py --seam > log/m7d_seam_1.log` → `assets/gen/stills/m7d_park/seam/seam_s41.png`, `_s42`, `_s43` (with `canvas_seam.png`, `mask_seam.png`): 89–99 s a take, 4 min 39 s with the model load.
- **Review** (each take at full size and pasted into the panorama at 1:1; `config/m7d_plate.json` review): **pick seam_s41** (the hill tapers into horizontal fog banks and a lower tree line descends behind the blocks; no vertical wall; its thin pale band has soft edges and tree tops through it: fog, not water). seam_s42 rejected (a bright flat band with a hard top edge: lake-like); seam_s43 not picked (a bright flat patch, and the upper ridge again ends in a soft vertical fade). No take has water, boats, a tower or landmark, text, faces or logos.
- **Compose:** the approved panorama and its Blender texture moved first (`mv`: `archive/assets/gen/stills/m7c_park/pano_m7c/pano.png`, `archive/assets/gen/tex/m7c/backdrop_m7c/park_backdrop.png` and `.json`), then `.venv/bin/python -I scripts/m7d_plate.py --compose` → `assets/gen/stills/m7c_park/pano/pano.png` (the approved panorama with seam_s41 pasted through the same mask: 0 of 10,575,600 pixels outside the mask changed) and `assets/gen/tex/m7c/park_backdrop.png` and `.json` through `scripts/m7c_plate.py` backdrop (the inverse view transform, as M7c). The texture's scale and its sky, horizon-haze and valley-fog colours are unchanged (the JSON is identical), so the 3D fog still meets the plate.
- **Sheet:** `.venv/bin/python -I scripts/m7d_plate.py --sheet` → `review/m7d_plates.jpg` (1930×2574, 0.58 MB): the seam band before and after with the mask outlined, 1:1 crops, the panorama after, the canvas, the mask and the three takes with verdicts.

## 52. 2026-11-16 — M1b: the v1.3 master post-filtered, compared with v1.2 and re-timed

- **Inputs** (human interventions 24), copied from `~/Downloads`; the v1.2 files moved to `archive/audio/v1.2/` (`mv`):
  - `audio/track/All Systems Operational.wav`: the v1.3 Logic master. 48 kHz stereo f32, 239.58 s (the same length to the sample), sample peak −1.04 dBFS, sha256 `79255b2f…`.
  - `audio/stems/0a Lead Vocals repaint.aif`: the repainted lead. AIFF 48 kHz stereo s16, 170.67 s from 0, sounding 150.98–170.10 s, sha256 `32428988…`.
  - The other stems are the Nov 15 exports; `0 Lead Vocals.aif` in the export folder is byte-identical to `audio/stems/`.
- **Post-filter** (run by the agent; the human ran v1.2's):
  - Run in `~/Code/music-deslop` at 68441e2, clean tree, the same commit as v1.2: `uv run --frozen python -m postfilter.infer --in <repo>/audio/track/All\ Systems\ Operational.wav --out <repo>/audio/postfilter/.new-deslopped.wav --ckpt ../music-deslop-data/release/m6f_10k.safetensors --source suno`.
  - 21.9 s, 6.7 GB peak RSS, no fallback passages (`log/render_logs/m1b_postfilter.log`).
  - Renamed to `audio/postfilter/all-systems-operational-master-deslopped.wav`: s24, sample peak −0.57 dBFS, sha256 `f04d35a0…`.
- **Comparison:** `.venv/bin/python -I scripts/m1b_compare.py > log/render_logs/m1b_compare.log` (new).
  - **Outside the bridge:** v1.3 equals v1.2 to float rounding (−126 to −167 dB re the music), with one exception. Stop 1's first clap (94.385 s) has the same timing (0-sample lag), but its first 20 ms differ (−7 dB re the clap) and it is 0.3 dB quieter. The other three claps are identical (−117 to −123 dB). This is for the human's ear.
  - **Bridge:** the master changes from 150.98 to 171.45 s. The change correlates 0.964 with the lead swap (repaint minus old lead, at the master's 47-sample latency behind the stems).
    - What's left after removing the best-fit swap is 9–19 dB below the music. That is consistent with the master bus reacting to the new vocal, but it can't be checked without re-exported stems.
  - **Post-filter:** it changes v1.3 by −33.6 dB re the music (v1.2: −33.5; bridge −32.9 against −31.8). Outside 145–175 s the two outputs match to −58 dB re the music; the clap is the exception.
- **Transcript:** `NLTK_DATA=$PWD/.venv/nltk_data .venv/bin/python scripts/transcribe_vocals.py "audio/stems/0a Lead Vocals repaint.aif" timing/whisper_lead_repaint.json` (WhisperX 3.8.6 large-v3; log beside it). The bridge is sung as v1.3 writes it, with "(We're committed to doing better)" twice (AI changes 9).
- **The lead as it sits in the master:** `.venv/bin/python -I scripts/m1b_lead_v13.py` (new).
  - It writes `audio/stems/0 Lead Vocals v1.3.aif`, the old lead with the repaint spliced over 150.980–170.095 s, the repaint's sounding span. The master's change starts at the same sample, and the old lead's tail after 170.10 s is still in the master.
  - It writes `timing/whisper_lead_v13.json`, the transcripts merged the same way at word level.
  - `config/timing.json` points `stems.lead` and a new `transcript` key at them; `scripts/timing_map.py` reads `transcript` (default: the old path).
- **Lyrics:** `lyrics/as_sung.txt`'s bridge is now v1.3 as sung (13 lines).
- **Re-timed:** `scripts/timing_map.py`, `scripts/shot_times.py`, `scripts/export_srt.py` and `--video` (logs in `timing/`). These are M2's steps less the click-track review video.
  - **Bridge:** 151.758–170.569 s.
    - 151.76–152.50 s: Root cause
    - 152.54–154.42 s: A fix from back in July
    - 154.43–156.14 s: Tested on the smaller machines
    - 156.15–157.18 s: Contributing factors
    - 157.30–159.16 s: Teams came over for the night
    - 159.17–160.16 s: An unrelated issue
    - 160.22–161.32 s: And a separate issue
    - 161.36–163.58 s: (Not related to cyber, AI or agents)
    - 163.67–164.32 s: Full report
    - 164.41–165.10 s: On the twentieth
    - 165.23–166.06 s: Lessons learned
    - 166.10–168.38 s: (We're committed to doing better)
    - 168.39–170.06 s: (We're committed to doing better)
  - **Outside the bridge:** beats, bars, events, Hey!s and echoes are identical. 15 word edges moved by 1–100 ms (the largest: "you" ends at 13.44 s, was 13.54), because the lead-stem threshold for word edges is the whole stem's median, now −34.3 dB (was −34.7).
  - **Shots:** every shot's start and end frame is unchanged. O18 is still 151.449–170.647 s; its cue "Root" now sits 309 ms after the downbeat it snaps to, inside the 450 ms limit. In `timing/shot_times.json` only `master_sha256` and O18's marks change.
  - **O18's marks** (`config/shot_cues.json`, v1.3; decisions 40):
    - 152.079 s (frame 19 of 576): whiteboard: root cause
    - 152.541 s (frame 33 of 576): whiteboard: the July fix (circled, branch A)
    - 154.425 s (frame 89 of 576): whiteboard: tested on smaller machines
    - 156.146 s (frame 141 of 576): whiteboard: contributing factors
    - 157.304 s (frame 176 of 576): whiteboard: Teams failover onto the gateway
    - 159.167 s (frame 232 of 576): whiteboard: capacity out (unrelated issue)
    - 160.223 s (frame 263 of 576): whiteboard: bulkheads failed (separate issue)
    - 161.364 s (frame 297 of 576): whiteboard: not related to cyber, AI or agents; denial tag 1 pins to it ('Microsoft, Nov 13, two days before its root-cause report.')
    - 162.847 s (frame 342 of 576): denial tag 2 ('The report doesn't say who or what wrote the July fix.'), a beat later: one half-time beat (two beats of the grid)
    - 163.666 s (frame 367 of 576): whiteboard: full report
    - 164.405 s (frame 389 of 576): whiteboard: on the 20th
    - 165.233 s (frame 414 of 576): whiteboard: lessons learned
    - 166.105 s (frame 440 of 576): whiteboard: we're committed to doing better
    - 168.386 s (frame 508 of 576): 'we're committed to doing better', sung again (the repaint doubles the line)
- **Next:** the Remotion whiteboard (v1.3 text, the July fix circled), the two denial tags, the status stamp (Thu 11:15 a.m.) and the fact card.

## 53. 2026-11-16 — M1b: the v1.3 bridge on screen: the whiteboard, the denial tags, the stamp, the fact card, O18 at the M7 look, the v1.3 music map

- **Remotion** (`npx tsc --noEmit` clean):
  - `config.ts`: `STAMP` is "Last updated: Thu 11:15 a.m." (brief rev 136; was 12:58 p.m.); the `Incident` type gains `denialTag`.
  - `Textures.tsx`: the whiteboard rebuilt for lyrics v1.3 (decisions 41).
    - Root cause (`incident.json`), with "July fix" circled in red marker as its line ends (branch A).
    - "↳ tested on smaller machines".
    - Contributing factors: `incident.json`'s three.
    - Microsoft's Nov 13 words, quoted on a line of their own: "not related to cyber or AI / agents".
    - "Lessons learned:", left blank as in M5.
    - "Full report: Nov 20" ("to follow" in branch C).
    - Removed: the branch-A config-diff box (the brief has no diff any more) and the credit line.
  - `Root.tsx`: `O18_REVEAL` for O18's v1.3 marks (production log 52), new compositions `M7-O18-Whiteboard`, `-full`, `-nrOnly` and `M7-O18-DenialTags`; the obsolete `O18-Whiteboard-diffPreview` removed. `M5-O18-Whiteboard` now builds the v1.3 board too; M5's v1.2 render stays in `renders/m5/remotion/`, which M5c3 reads, so M5c3 still reproduces.
  - `LowerThird.tsx`: `DenialTags`, the two tags in the lower thirds' panel (coral tab, paper card, Work Sans). Tag 1 comes in on "(Not" (frame 297 of O18), tag 2 two grid beats later (frame 342); both go at the cut to O18e (frame 504), 6.9 s on screen. A leader line runs from the panel to a pin on the board's quote line.
  - `Cards.tsx`: the fact card's lines are now the brief's (rev 141), verbatim.
- **Stills:** `scripts/m1b_stills.sh` (new) → `review/m1b/` (15 PNGs: the board at each line, full, the quote line alone, the tags, O02, O23, the fact card) and `review/m1b_remotion.jpg`; 30 s, CPU.
  - Fixes after looking:
    - the full-board composition rendered blank (its fill ran over one frame; it now takes `full`);
    - the circle drew only part of its loop (its dash length broke under a non-scaling stroke; it is now drawn in pixels);
    - the circle was too wide (Caveat runs about 0.33 em a character, not 0.42).
- **The pin:** `blender -b --factory-startup --python blender/o18_pins.py -- --subs O18c,O18d --size 1920x1080 --out <scratch> --log log/render_logs/m1b_o18_pins_pose_check.log` (new) → `timing/o18_pins.json`. 28 s, 1.6 GB RSS; log `log/render_logs/m1b_o18_pins.log`.
  - It builds O18 as the M7 render does and, instead of rendering, projects board texture pixel (225, 888) of 2400×1500, just left of the quote line's opening mark, through O18c's and O18d's cameras on every frame.
  - The pin is in frame on all 216 frames, and nothing stands in front of it (ray cast).
  - The panel sits at the lower thirds' place, 110 px up. In O18d it sits 56 px up (`bottoms`): at 110 it covered the board's last line, "Full report: Nov 20". The first overlay (110 px throughout) is in `archive/renders/m1b/remotion/M7-O18-DenialTags_v1.mov`.
- **Renders:** `scripts/m1b_remotion.sh` (new); log `log/render_logs/m1b_remotion.log`.
  - `assets/gen/tex/m1b/M7-O18-Whiteboard/frames/`: 576 JPEGs (q95, 1800×1125), 20 s, 104 MB, out of the manifest like the M7b screens. The M5 movie was 1200×750, soft in O18d's close.
  - `renders/m1b/remotion/M7-O18-DenialTags.mov`: ProRes 4444, 1920×1080, 576 frames, 16 s.
- **O18 at the M7 look with the v1.3 board:** `blender -b --factory-startup --python blender/m1b_o18.py -- --out renders/m1b/raw --still --at 0.5 --subs O18a,O18b,O18c,O18d --size 1920x1080 --log log/render_logs/m1b_o18_pose_check.log` (new).
  - It is `coverage_m7.py` with the whiteboard swapped for the board sequence after the O18 build, mapped as `look.py` maps the M7b screens. 1 min 2 s, 4.1 GB RSS; pose checks pass.
  - Graded with `scripts/grade.py --look grey` → `renders/m1b/graded/`. Sheet: `.venv/bin/python -I scripts/m1b_sheet.py` (new) → `review/m1b_o18.jpg`: the four sub-shots with the tags composited from the .mov, the board texture, the fact card and the stamp.
- **Music map for v1.3:** `.venv/bin/python -I scripts/music_map.py --v13 --plot` → `timing/music_map_v13.json`, `review/m1b_music_map.png`.
  - The singer's motion follows `env_30fps.lead` and O14–O16's string lights follow `lead_onsets`; both were from the v1.2 lead.
  - The map keeps the v1.2 lead's scales (the envelope's 99th-percentile top and the onsets' 95th-percentile rise). So outside the repainted span (150.98–170.10 s) the lead envelope and onsets equal v1.2's exactly. Inside, 573 envelope frames change, and the lead onsets go from 33 to 48.
  - The script's default mode now reads the archived v1.2 master and keeps Suno's 12 numbered stems only. Rebuilt that way, `timing/music_map.json` matches the committed file except bar 64's section label and the beat profile of Post-Chorus 2 and the bridge (section bounds come from the v1.3 timing map). Blender reads neither, and the committed file is left as it was (`git checkout`).
- **Self-check:**
  - The board quotes only Microsoft's Nov 13 words. "Tested on smaller machines" is the lyric, not the report's wording. The fact card quotes "tended to focus on weaker hardware", which is the brief's own line.
  - The tags read `incident.json`'s `denialTag`. The stamp reads 11:15 a.m. on every row of O02 and O23.
  - No readable faces in the four O18 stills. The pin sits on the quote line's opening mark in O18c and O18d.
  - The fact card fits the frame at 31 px, but it now runs to about 210 words on a 15 s card (decisions 41).
- **Not yet in the M7 render:** `coverage_m7.py` still shows M5's v1.2 board and reads `timing/music_map.json`. After M7d finishes with `blender/look.py`, the board swap and the v1.3 music map go into the M7 path, and the M7 assembly composites the tags' .mov over O18.
- **Also restored:** a coverage_m7.py run without `--log` (13:35, the M7d step's) had emptied the committed `log/render_logs/m7a_pose_check.log`. Restored with `git checkout`, and the M7d agent was told.

## 54. 2026-11-16 — M7d look pass: firs as volumes, thinner bare trees, O08c's night outside, the drop cues, the instrument closes, O19b's back path (code, tests, heroes)

- **Why:** human interventions 23 ("keep going on what you already recognize as weak"): weak points 1 (firs flat up close), 3 (bare trees dark and dense from O20e), 4 (O08c's pale flat shapes behind the forest), 5 (the drop in the eye-level wides), 6 (the guitar close dark, the banjo close edge-on) and the coordinator's point 7 (O19b's start: a flat-topped block at the crest). Weak point 2 (the seam) is production log 51. How each is fixed, and the camera change: decisions 42.
- **Code** (everything in the M7 path, off with the look; `blender/ep/`, `sets.py`, `coverage.py`, `coverage_m5c.py` and the performance code untouched, so M5c3 reproduces: production log 56):
  - `config/look_m7.json` `m7d` (on): `firs`, `bare`, `o19b`, `brow`, `night`, `closes`, `wides_options`.
  - `blender/park_m7c.py`: `fir_mesh` (per-vertex normals from an ellipsoid crown proxy and the branch tier, an occlusion `shade`, a per-branch `clump`, the proxy normal as a vector attribute `pn`, branch tubes; M7d's values from `gb.rng("m7d_fir_k")`, so M7c's seeded draws are untouched); `_needles_m7d` (a needle fringe of uneven length at each spray's edge, colour from the occlusion and the branch value, translucency strongest at the skin, the overcast's term on the proxy normal in world space); `bare_mesh` (the same draws; `gb.rng("m7d_bare_k")` keeps about half the level-4 branches, a third of the level-5 ones and a quarter of the twigs; slimmer from level 2; normalised by the full tree's height); the bare bark paler, less sheen, fog distance 100 m; `flat_mask` (the back path's bed follows the roll for y < −9.5); `brow_cues` (six fir crowns below the brow, the brow path and its kerbs, the terrace railing; `gb.rng("m7d_brow")`); `bark_mat` takes spec and roughness; `_mesh` takes vector attributes.
  - `blender/look.py`: `M7D`; the treehouse forest's needles with the overcast term (day 2.0, night 0); `treehouse_night_outside` (the night forest floor, a night sky dome, the panes' rain at 0.45 at night); `banjo_three_quarter` and `guitar_light` (a spot keyed to the close's frames), reached through `coverage_m7`'s `cam_base` wrapper and `camera_hook`.
  - `blender/coverage_m7.py`: the close_banjo re-aim; comparison switches `--wides-z Z` (the eye-level park wides raised, tilt kept) and `--m7d-off part`, for the options sheet only.
- **Tests** (960×540 and 1920×1080, 16–32 samples, in the scratchpad, not kept), and what each changed:
  1. Firs (O19a, O20a, O20c, O22a): the first shading (proxy normals, occlusion, a small emission on the normal's up component) barely showed: on near-black needles the fog veil is about ten times brighter than the dim overcast world's light. A scratch probe swapped needle-material variants in a built scene (`probe_firs.py`): the overcast term on the crown proxy's normal (world space, from above and the bright side), times the occlusion, in a grey-green tone, reads as volume at strength 1.2 (park) and 2.0 (treehouse); a regular needle comb read as hatching (now uneven lengths, jitter).
  2. Bare trees: fog distance 38 m made them paler than the fog behind them (the level haze's blue); 70 m still pale; 100 m with low sheen and darker bark reads as grey lace in the fog.
  3. O08c: a probe (`o08c_probe.py`) rendered the night with the firs, then the whole outside, then the panes hidden: the pale band was the forest floor (it went with the outside; the night world is near black). Fixed as decisions 42; the first night sky (0.6) didn't show through the panes' speckle: the sky raised to 1.3 and the panes' rain dimmed to 0.45 at night.
  4. Drop cues: the first crowns were all skipped (too near the flank firs and bare trees); placed by angle from the empty wide's camera (±13–15°, 28–52 m) and checked against firs only. The brow path reads from O20e; the railing reads in every wide that sees the terrace.
  5. Closes: a 6 W area light on the guitar lit the player's arm orange: replaced by a 40° spot (2 W live, 1.2 W cafe). The banjo re-aim on the neck side (39°) put the mic stand's pole through the head and, in O11e, the player's arm over half the frame; a probe (`probe_cams.py`) compared 30°, 38°, 48°, 38° with 14° elevation and the pot side: the pot side at about 36° is clear in all four.
  6. O19b at 10%: the block is gone; the crest's back edge is a soft rounded line with the path running over it.
- **The scratch probes wrote the default pose log:** `probe_firs.py` and `o08c_probe.py` imported `coverage_m7` without `--log`, so each build wrote an empty pose report over the committed `log/render_logs/m7a_pose_check.log` (about 13:35). The coordinator restored it with `git checkout`; both probes now pass a scratch `--log`, and it matches HEAD again.
- **Heroes, round 1:** `/usr/bin/time -v blender -b --factory-startup --python blender/coverage_m7.py -- --out renders/m7d/raw --still --subs O08c,O09f,O09h,O09j,O11e,O17a,O17f,O18a,O18e,O19a,O19b,O19e,O20a,O20c,O20e,O20f,O20g,O20h,O20i,O21a,O22a,O22b,O22c,O22f,O22g --size 1920x1080 --log log/render_logs/m7d_pose_check_r1.log` (7 min 13 s for 10 builds, peak 5.6 GB RSS; `log/render_logs/m7d_heroes_r1.log`): 1.8–7.4 s a still. Pose check: no violations. Its four banjo closes (neck side) are superseded: `archive/renders/m7d/raw_r1/`.
- **Heroes, round 2 (the banjo closes on the pot side):** `… --out renders/m7d/raw --still --subs O09f,O11e,O17f,O20f --size 1920x1080 --log log/render_logs/m7d_pose_check_r2.log` (3 min 1 s; `m7d_heroes_r2.log`). No violations.
- **O19b's start:** `… --out renders/m7d/raw_first --still --at 0.1 --subs O19b --size 1920x1080 --log log/render_logs/m7d_o19b_first_r1_pose_check.log` (57 s; `m7d_o19b_first_r1.log`). A first run was stopped by the agent before it rendered (`m7d_o19b_first_r0_stopped.log`: the chain after it had its switches before `--`).

## 55. 2026-11-16 — M7d: the 2.4 m options, the board, the wides sheet, the motion test; the self-check

- **The 2.4 m options** (weak point 5; decisions 39.2), for the sheet only, the approved cameras untouched: `/usr/bin/time -v blender -b --factory-startup --python blender/coverage_m7.py -- --wides-z 2.4 --m7d-off brow --out renders/m7d/options/z24/raw --still --subs O20a,O21a,O22a,O22f --size 1920x1080 --log log/render_logs/m7d_options_z24_pose_check.log` (2 min 49 s; `m7d_options_z24.log`) and `… -- --wides-z 2.4 --out renders/m7d/options/cues24/raw …` (2 min 43 s; `m7d_options_cues24.log`; pose report `m7d_options_cues24_pose_check.log`). The wide, o21 and empty presets at 2.4 m, each target raised by the same amount (the tilt kept). No violations.
- **Grade and sheets:** `.venv/bin/python -I scripts/m7d_board.py --grade --board --wides` (new script, the M7c board's pattern) → `renders/m7d/<id>.png`, `renders/m7d/m7c_ref/<id>.png`, `renders/m7d/options/<option>/<id>.png` (grey, cafe, home from "Remember Wednesday", as M7c); `review/m7d_board.jpg` (1930×15972, 3.5 MB: seven sections, one per weak point, the approved frame left and M7d right at 960 per side, with 1:1 crops of the firs (O19a, O19b, O20a), the seam's place in O22a, the bare trees in O20e, the terrace in O22f and O19b's crest, and O08c's back windows at 2.5×); `review/m7d_wides_options.jpg` (1930×4766, 1.5 MB: O20a, O21a, O22a, O22f, each 2×2: approved, the cues at 1.8 m, 2.4 m without the cues, the cues at 2.4 m).
- **Motion test:** `/usr/bin/time -v blender -b --factory-startup --python blender/coverage_m7.py -- --out renders/m7d/frames_motion --subs O19a,O19b,O20e,O09f,O09j --size 960x540 --log log/render_logs/m7d_pose_check_motion.log` (12 min 55 s; `m7d_motion.log`; no violations): seconds a frame at 960×540, O19a 0.85, O19b 1.40, O20e 1.46 (M7c: 0.83, 1.39, 1.46), O09j 1.19, O09f 1.06. Then `.venv/bin/python -I scripts/m7d_board.py --motion` → `review/m7d_motion_test.mp4`: 17.4 s, 521 frames, h264 960×540 at 650 kb/s (536 kb/s measured), AAC 128k, 1.46 MB: O19a then O19b with M5's dissolve (9.6 s: the deck's firs, the rise up the back slope over the crest), O20e (3.0 s: the truck past the brow's bare trees, the railing and the plate), O09j (2.4 s: the guitar close with its spot), O09f (2.4 s: the banjo close from the pot side). Each part carries the master's audio from its own time in `review/m5c3_animatic.mp4` (outside the bridge, unchanged by the v1.3 master). The graded frames are in `renders/m7d/frames_motion/graded/` (out of the manifest, like every frame sequence).
- **Self-check, every hero at full size** (25 sub-shots and O19b's start; crops at 1:1, 2.5× on O08c's windows):
  - **Faces:** none readable. The re-aimed banjo closes frame the pot, the strumming hand and the strap; the player's head is above the frame; the band behind is soft and backlit (O09f, O11e) or out of frame. The guitar spot is keyed to the close's own frames, and the closes frame the body and hands only. Park and treehouse: as M7c (backs, silhouettes, O20g's head out of focus).
  - **Guardrails:** the seam's pick has no water or lake-like band (its pale band is soft fog with tree tops through it), no boats, tower or landmark, text, faces or logos; the railing, crowns and path are generic park dressing. No new text anywhere. Nothing about AI-written code. O18a shows the whiteboard's current texture, which this pass doesn't touch (M1b's).
  - **Plate seams:** in O20a, O22a and O22f the L1 seam's place (left of the city, behind the left firs) shows the hill sloping into horizontal fog; no line or band at the inpaint's edges at 1:1; the other seams as M7c.
  - **Pose checks:** no violations in any run (`m7d_pose_check_r1`, `_r2`, `_motion`, `m7d_o19b_first_r1_pose_check`, `m7d_options_*_pose_check`).
  - **Silhouettes and fog:** the people as dark as M7c's; the firs' silhouettes and their fading with distance unchanged; the near firs lighter on the side turned to the sky.
  - **Still weak:** see decisions 43.

## 56. 2026-11-16 — M7d: M5c3 reproducibility, render cost, disk, GPU; ready for the human

- **M5c3 still reproduces** with the M7 hooks off (this pass changed only `blender/look.py`, `blender/park_m7c.py`, `blender/coverage_m7.py` and the M7 config): `blender -b --factory-startup --python blender/coverage_m5c.py -- --out <scratch>/repro --still --subs O03a,O04a,O20a,O22a --log <scratch>/repro/pose.log` (`log/render_logs/m7d_m5c3_repro.log`) against `renders/m5c3/frames/O03a/0073.jpg`, `O04a/0072.jpg`, `O20a/0032.jpg` and `renders/m5c/frames/O22a/0055.jpg`: PSNR 45.8, 47.8, 42.8 and 45.6 dB (mean absolute difference 0.84, 0.57, 1.14 and 0.87 of 255), as in production log 49.
- **Render cost at 1920×1080** (the M7 settings, frames 2–24 of each sub-shot): `blender -b --factory-startup --python blender/coverage_m7.py -- --out <scratch>/timing --subs O08c,O09j,O19a,O20a,O22a --frames 24 --size 1920x1080 --log <scratch>/timing/pose.log` (`log/render_logs/m7d_timing.log`) and the same with `--m7d-off firs` for O19a, O20a, O22a (`m7d_timing_firs_off.log`). Seconds a frame: O20a 2.66 (firs as M7c 2.67; M7c's own run 2.64), O22a 2.27 (2.22; M7c 2.25), O19a 2.33 (2.34), O08c 1.24, O09j 2.57. The fir shading, the branch tubes and the drop cues cost nothing measurable (within 2%); builds take a few seconds longer for the prototypes' attributes and tubes (the park builds 56–82 s, M7c 45–75 s). At 960×540 the motion test ran at M7c's speed (production log 55). Hero stills 1.8–7.4 s each.
- **ComfyUI and FLUX.2:** 89–99 s a take, three takes (production log 51); peak 37.0 GB RAM used, VRAM 31.7 GB; stopped by its PID.
- **Disk used by M7d:** about 0.8 GB in the repository's folders: `renders/m7d/` 685 MB (the motion frames 279 MB, heroes 197 MB, options 94 MB, the M7c references 73 MB), `archive/renders/m7d/` 27 MB (the first banjo closes), `assets/gen/stills/m7d_park/` 20 MB, the archived M7c panorama and backdrop 60 MB, the review files 7 MB. Outside it: test renders in the scratchpad (413 MB) and ComfyUI's own copies (`~/ComfyUI/output/aso_m7d/`, 15 MB). 23 GB free.
- **GPU and RAM:** only this project's jobs ran, one Blender or ComfyUI at a time (ComfyUI only with Blender stopped, production log 51); the RTX 5090 back to 361 MiB, 34 GB RAM available. Blender peaked at 5.6 GB RSS. The coordinator's M1b audio jobs ran alongside some Blender runs, as agreed.
- **Superseded, in `archive/`:** the M7c panorama and its Blender texture (`archive/assets/gen/stills/m7c_park/pano_m7c/`, `archive/assets/gen/tex/m7c/backdrop_m7c/`), the first banjo closes (`archive/renders/m7d/raw_r1/`). The stopped O19b run's log kept as `_r0_stopped`. Nothing deleted.
- **Calls for the human:** decisions 43.

## 57. 2026-11-16 — M1b: the v1.3 board and music map in the M7 render path

- **Why:** production log 53 left the M7 path on M5's v1.2 board movie and `timing/music_map.json`, until M7d had finished with `blender/look.py` (it has: production log 56).
- **Code:**
  - `blender/coverage.py` reads the map named by `ASO_MUSIC_MAP` in `timing/`. Unset, it reads `music_map.json` as before, so M5c3 is untouched.
  - `blender/coverage_m7.py` sets `ASO_MUSIC_MAP` to `config/look_m7.json` `m1b.music_map` (`music_map_v13.json`) before it imports the M5c3 code, and prints the map it uses.
  - `blender/look.py` (`M1B`, `whiteboard_v13`): after O18's layers, the whiteboard shows `m1b.whiteboard` (`assets/gen/tex/m1b/M7-O18-Whiteboard/frames`, 576 frames, 1800×1125), mapped as the M7b screens are.
  - `blender/m1b_o18.py` (production log 53) is now redundant; it is kept as the record of that review render.
- **Check:** `blender -b --factory-startup --python blender/coverage_m7.py -- --out renders/m1b/m7path --still --at 0.5 --subs O18c,O18d --size 1920x1080 --log log/render_logs/m1b_m7path_pose_check.log` (33 s, 3.1 GB RSS; `log/render_logs/m1b_m7path.log`).
  - It prints "M1b: music map timing/music_map_v13.json", and the build notes say "M1b: the v1.3 whiteboard (576 frames, 1800x1125)".
  - Against production log 53's `renders/m1b/raw/` stills: O18c PSNR 72.8 dB, O18d 97.7 dB, with no pixel off by more than 30. The O18c difference is the singer's pose on the v1.3 lead envelope.
- **Left for the M7 assembly:** composite `renders/m1b/remotion/M7-O18-DenialTags.mov` over O18.

## 58. 2026-11-16 — M1b: the post-filtered v1.3 master for the human's listen

- **Why:** human interventions 25 ("Send me the audio here so I can review it"), before locking M1.
- **Encodes** (review copies; the WAVs stay the sources):
  - `ffmpeg -i audio/postfilter/all-systems-operational-master-deslopped.wav -c:a libmp3lame -b:a 320k … review/m1b/audio/all-systems-operational-v13-postfiltered.mp3` (239.6 s, 9.6 MB).
  - Stop 1's first clap, the one place outside the bridge where v1.3 differs from v1.2 (production log 52): 90–100 s of the post-filtered v1.2 master (`archive/audio/v1.2/postfilter/`), 1.5 s of silence, then 90–100 s of the post-filtered v1.3, each with 50 ms fades → `review/m1b/audio/stop1-clap-v12-then-v13.mp3` (21.5 s, 0.9 MB). The clap is at 4.4 s into each half (94.38 s in the master, 1:42.8 in the video).
- **Sent** to the human with SendUserFile.

## 59. 2026-11-16 — M7: the empty wides at 2.4 m; the full Eevee render started

- **Why:** human interventions 25 (M7d approved with decisions 43's recommendations; keep going).
- **The empty wides** (decisions 43.3): `config/look_m7.json` m7c.cameras.empty to loc z 2.4 (was 1.85) and target z 1.6 (was 1.05), the tilt kept, as the `--wides-z 2.4` comparison renders did (production log 55); `_doc_empty_z` records it. Only O22a and O22f use this preset. The crowd wides (`wide`, `o21`) stay at 1.8 m. The park's tree placement reads the `wide` preset only, so nothing else moves.
- **Check:** `blender -b --factory-startup --python blender/coverage_m7.py -- --out <scratch>/empty24 --still --subs O22a,O22f --size 1920x1080` (51 s) against `renders/m7d/options/cues24/raw/`: PSNR 76.9 dB (O22a) and 101.9 dB (O22f), the same frames.
- **Full render:** `scripts/m7_render.sh` (new: one `blender -b --factory-startup --python blender/coverage_m7.py -- --out renders/m7/frames --only <build> --size 1920x1080` per build in coverage.py's order, each under `/usr/bin/time -v`; a build whose log ends in "done" is skipped on a rerun) `| tee log/render_logs/m7_render.log` → `renders/m7/frames/<sub-shot>/`, JPEG q92 (out of git). Logs `log/render_logs/m7_<build>.log`, pose reports `m7_pose_check_<build>.log`. Expected: 82 sub-shots (O22d is the generated clip), about 4.6 h (production log 33), about 1.4 GB; 23 GB free at the start; GPU idle and nothing else running before it.

## 60. 2026-11-16 — M7: the end sequence for reading, for review

- **Why:** human interventions 25; decisions 44.
- **Code:** `config/end_cards_m7.json` (new: reading rate, settle, minimum, fades, order, the fact card's pages); `remotion/src/components/EndCards.tsx` (new: `FactPage`, `END_PLAN`, `EndSequence`); `remotion/src/components/Cards.tsx` exports its `Card` layout (no other change, so the M5 cards render as before); `remotion/src/Root.tsx` registers `M7-EndSequence` and, for review, `M7-End-<card>` (each card alone, its hold as its length). `npx tsc` clean.
- **Render:** `scripts/m7_end.sh` (new) → the stills `review/m7_end/<card>.png` (each card's last frame), `review/m7_end/plan.txt` (the compositions' lengths), `renders/m7/remotion/M7-EndSequence.mp4` (4,242 frames, 141.4 s, h264 CRF 18, silent, 3.2 MB; 103 s to render at concurrency 2 alongside the M7 Blender render), then `.venv/bin/python -I scripts/m7_end_sheet.py` (new) → `review/m7_end_sheet.jpg` (1950×2414).
- **Checked by eye:** the pages at full size (no line breaks inside a source's name or a time; the heading at one height on every page; the longest page, the report's, fits with room); the transitions in the movie at frames 352, 462, 1166, 1172 and 4230 (dark cards cross-fade into the light ones; page turns show no doubled text; the end fades to black).
- **First pass:** with every card cross-faded, two pages of text showed through each other for 0.4 s at each page turn; replaced (same file names) before review. The first layout, with each page's text block centred, moved the heading from page to page; replaced with a fixed-height block.
- **Sent** to the human: the sheet and the movie.
- **Note:** the M7 Blender render ran alongside (production log 59); O03a took 2.65 s a frame (2.37 s in production log 33's timing), in part from these renders sharing the CPU.

## 61. 2026-11-16 — M7: the credits instrumental post-filtered and analysed

- **Why:** human interventions 26.
- **Post-filter:** in `~/Code/music-deslop` at 68441e2 (clean tree, as for the master): `/usr/bin/time -v uv run --frozen python -m postfilter.infer --in <repo>/audio/credits/All\ Systems\ Operational\ (credits\ EDM).wav --out <repo>/audio/postfilter/.new-credits-deslopped.wav --ckpt ../music-deslop-data/release/m6f_10k.safetensors --source suno` (25.7 s, 6.1 GB peak RSS, no fallback passages; `log/render_logs/m7_credits_postfilter.log`), alongside the M7 Blender render. Renamed to `audio/postfilter/all-systems-operational-credits-deslopped.wav`: s24, 212.4 s, sha256 `e11526f5…`.
- **Analysis:** `.venv/bin/python -I scripts/m7_credits.py` (new) → `timing/credits_grid.json`, `log/render_logs/m7_credits_analysis.log`:
  - The post-filter changed it by −33.2 dB re its input (the master: −33.6), most at 211 s (−28.6 dB). Sample peak −3.98 dBFS (input −4.12).
  - Loudness (ffmpeg ebur128): input −15.8 LUFS, post-filtered −15.7 LUFS; the post-filtered master −13.7 LUFS. Left as delivered: the credits sit 2 LU under the song.
  - Tempo drifts from about 103.2 bpm (0.581 s a beat) at the start to 105.1 (0.571 s) by 2:00, so a straight grid fits badly (beats off it by up to 0.3 s). Beats are tracked instead (librosa's dynamic programming, 310 beats, 20.6–197.6 s); the intro (0–20.6 s) and the outro have no beat. Downbeats: every fourth tracked beat from the first, which the kick's entry (22.87 s) and nearly every section change confirm; the intro's bar lines extrapolated back.
  - 19 section changes (the 4 beats after a downbeat against the 4 before: more than 2.5 dB in level or 10 dB under 150 Hz), each moved to the strongest onset within 0.2 s; the strongest are the kick's entry (22.87 s), 41.38, 60.04, the drop (96.87), 115.29/117.45, the breakdown (124.47), 160.56.
  - Fade-out points, where the music thins by 5 dB or more: 154.64 s (a two-bar drop-out before the last build), and the track's end (212.4).
- **Sent** to the human: the full post-filtered track as MP3 320k (`review/m7/audio/all-systems-operational-credits-postfiltered.mp3`, 8.5 MB).

## 62. 2026-11-16 — M7: the end sequence on the instrumental, with its music; the preview

- **Why:** decisions 45.
- **Code:** `remotion/src/components/EndCards.tsx` reads `timing/credits_grid.json` and, with `config/end_cards_m7.json` snap set (`window_s` 6, `window_frac` 0.5, `picture_fade_s` 0.8, `music_fade_s` 2.4), starts each card on the music; unsnapped, the holds are as in production log 60. `npx tsc` clean.
- **Render:** `scripts/m7_end.sh` (now also cuts the music and builds the preview) → stills, `review/m7_end/plan.txt` (M7-EndSequence 4,639 frames, 154.63 s; end 408, final 139, fact pages 764, 490, 1,105, 828, disclosure 905 frames), `renders/m7/remotion/M7-EndSequence.mp4` (111 s to render, alongside Blender), `review/m7_end_sheet.jpg`, then:
  - `ffmpeg … -af "atrim=0:154.6333,afade=t=out:st=152.2333:d=2.4" … audio/credits/credits-m7-end.wav` (the post-filtered instrumental from its start, cut and faded with the sequence; −78 dB at the end).
  - `review/m7_end_preview.mp4`: the song's last 6 s (video 241.979–247.979 s from `review/m5c3_animatic.mp4`, O23, with the post-filtered v1.3 master's audio, song 233.579–239.579 s), then the sequence with its music; h264 650k, AAC 128k, 160.7 s, 9.4 MB.
- **Checked:** the music cut's level through the fade (−17 dB at 150 s, −31 at 153, −78 at the end). The changes on the music are as decisions 45 lists.
- **Sent** to the human: the preview.
- **For the M7 assembly:** the end sequence and `audio/credits/credits-m7-end.wav` follow O23 at video frame 7439 (song 239.579 s), in place of the M5 O24 and the end cards.

## 63. 2026-11-16 — M7: the credits track's sections for the human's review

- **Why:** human interventions 27.
- **`scripts/m7_credits.py`** now also writes each section change's level and low-band change and its beat index into `timing/credits_grid.json`; times, strengths, downbeats and fade-out points are unchanged (compared with the previous file).
- **`.venv/bin/python -I scripts/m7_credits_sections.py`** (new) →
  - `review/m7_credits_sections.png` (2400×1400; in the manifest): level and the band under 150 Hz over the track (0.25 s windows, smoothed over 0.75 s), the 19 section changes numbered (bold where the strength is 20 dB or more), the fade-out point (F) and the last tracked beat (B), the end cards' spans under it with the unused 2:34.6–3:32.4 hatched, and a key naming each change. The names are the agent's reading of the measurements.
  - `review/m7/audio/credits-sections-marked.mp3`: the full post-filtered track with 23 clicks at −14 dBFS: 880 Hz on each section change, 1760 Hz on the card changes that fall on a downbeat and not on a section change (0:13.6, 0:18.2, 0:43.7), and a longer 1760 Hz one on the fade-out point.
  - `review/m7/credits_sections.txt`: the same as labels (start, end, name; tab-separated, Audacity's format), with the card spans.
- **Sent** to the human.
- **Correction:** production log 61 and decisions 45 call the drop-out at the fade-out point "two-bar". The measurements give one bar out (2:33.7), one back in (2:36.0), one out again (2:38.3), then the final drop (2:40.6).
- **Not marked:** the chart shows the low band falling again around 3:04–3:08 and through most of the outro after 3:17.6. The detector didn't mark these: the first is under its threshold, and no beats were tracked after 3:17.6.

## 64. 2026-11-16 — The GitHub repository: pushed; README, METADATA and the media licence for public

- **Why:** human interventions 28.
- **Checked before the push** (`git log --all --name-only`, `git rev-list --objects --all`, `git grep` over every revision): 435 paths ever tracked, all still in HEAD; the largest blob 3.4 MB (`review/m7d_board.jpg`), about 60 MB in all; no keys, tokens or private keys; no email addresses in tracked files; every commit by the human's GitHub address (the same as the other series repos). The creator's screenshots, the Slack captures and the avatar crop are git-ignored (`assets/screenshots/`, `remotion/public/real/`) and were never committed; `docs/suno/` holds the clip record and page text only (the raw dumps are ignored). The render logs carry this machine's home path, as the sibling repos' logs do. Nothing tracked comes from Ever Present beyond `blender/ep/` and the shared tooling adapted from it, each with a provenance header; most of those scripts are already public, MIT-licensed, in the other series repos.
- **One image to settle:** `review/m3_screens.jpg` (710f260), the M3 contact sheet of every screen, has the placeholder "No license found" capture as one tile (about 230×130 px in the 3450 px sheet; Microsoft's dialog and the "real screenshot · Fri, Nov 13" caption, no names or addresses). For the human before the repository goes public (METADATA.md's checklist).
- **Push:** `git remote add origin https://github.com/Derivative-Work/all-systems-operational.git && git push -u origin main` (main, 90 commits; the repository private).
- **Prepared like the other series repos** (modelled on The Distillation Job's, the latest):
  - `README.md`: the video, its status (in production; report day still to come), the conflict of interest, how it was made, what's real and what's made up, the fact card verbatim with its sources, where things are, reproducing it, licences, credits.
  - `METADATA.md`: the YouTube title, description, chapters (the current cut: song as timed, the end cards fading at 2:34.6 of the credits music), tags and settings, and the checklist before upload (the final report, the audits, the cards' placeholders, the credits music's origin, the capture, the news, making the repository public, the intervention count).
  - `LICENSE-media.md`: the v1.3 repaint and the credits music under "covers"; the fonts (OFL 1.1) and the image-to-video graph (Comfy Org, MIT) under "doesn't cover"; the contact sheet with the placeholder capture named; the repository link in the attribution line.
- **GitHub settings** match the other public series repos already (issues and projects on, wiki and discussions off, no description or topics, the homepage left for the YouTube link). Visibility stays private: the human makes it public.

## 65. 2026-11-16 — M7 render: progress check, O03 to O20b; a defect in O08a

- **Why:** human interventions 29.
- **Progress** (`log/render_logs/m7_render.log`): 16 of 19 builds done (O03 to O19b), every one exit 0; O20 rendering. 5,020 frames so far, 743 MB; 21 GB free on disk. Left: about 1,220 frames (O20c–j, O21a, O22 without the generated O22d), at 2.4–2.7 s a frame in the park.
- **Checks on every finished sub-shot:** frame count against the plan (`docs/coverage.md`), gaps in the numbering, and frames under half their sub-shot's median file size. Only O19b differs from the plan, by design: 123 frames, not 113, because O19a's last 10 frames dissolve into it (`scripts/coverage.py`, `xfade_in`).
- **Sheet:** the middle frame of each sub-shot → `scripts/contact_sheet.py review/m7/render_progress_O03-O20b.jpg … --cols 6 --cell 560` (67 sub-shots; O20c was still rendering). Spot checks at half size: O09d and O17g are backs of heads, not faces; O18d matches the approved M1b board (`review/m1b_o18.jpg`), its root-cause line running off the top of the frame as approved.
- **Defect, O08a (video 0:52.9, "We are aware"):** for the first 17 frames (0.57 s) a flat beige surface right at the lens fills most of the frame, then slides off to the left as the camera moves. The approved M5c3 pass has the same wipe (`review/m7/o08a_occluder_m7_vs_m5c3.jpg`, M7 above M5c3 at frames 1, 6, 12, 18, 30 and 45), so it comes from O08's camera (`blender/board.py` and `blender/animatic.py`, the M5 move starting at (6.1, 1.0, 1.55)), not the M7 look. To do after the render: find the object (a ray from the camera at frame 1) and move the start of the camera clear of it, then re-render O08 (431 s).

## 66. 2026-11-16 — M7 render finished; every frame checked for anything at the lens; four camera faults and the lantern fixed

- **Why:** the render finishing (production log 59), O08a's wipe (production log 65), human interventions 30.
- **The render:** `scripts/m7_render.sh`, all 19 builds exit 0 (`log/render_logs/m7_render.log`): 15,753 s (4 h 23 min), 6,264 frames at 1920×1080, 999 MB, peak RSS 4.6 GB (O20). Every planned Blender sub-shot rendered (O08b is the Remotion phone insert, O22d the generated clip); counts match the plan except O19b's 10-frame dissolve pre-roll, by design; no gaps; the pose checks report no violations in any build; no tracebacks.
- **By eye, O20–O22** (`review/m7/render_park_O20-O22.jpg`, each sub-shot at a quarter, half and three quarters): as the M7c/M7d boards. O20d is the singer's lean-in from behind (the M5c swap), O20g the tops of heads against the skyline (decisions 15–16).
- **New check, `blender/camera_clearance.py`:** builds every sub-shot exactly as the render does and, on every frame, casts 15 rays (5 across, 3 down) from the camera through the frame, flagging anything nearer than 0.25 m. Runs: `blender -b --factory-startup --python blender/camera_clearance.py -- --only O19a,O19b,O20,O21,O22 --still --at first --size 320x180 --samples 1 --out <scratch> --log <scratch>/pose_park.log --report log/render_logs/m7_camera_clearance.jsonl` (5 min 18 s; `m7_camera_clearance_park.log`), then the other 14 builds with `--ignore drizzle,haze_volume` (9 min 27 s; `m7_camera_clearance_rest.log`). All 82 sub-shots, 6,264 frames. Flags:
  - **O08a:** the camera inside the live room's floor-lamp shade (`lamp_shade`, `blender/sets.py`) for its first 17 frames (diagnosed with a scratch ray probe first). Also in the approved M5c3.
  - **O03d** (the first clapping-hands close, 0:19): the camera trucks through `crowd14`, the clapper `crowd15`'s neighbour, for its first 36 of 72 frames: a dark blur until the hands appear. Also in M5c3 (frames 1 and 20 as dark).
  - **O11e** (a one-beat banjo close, 1:40): `crowd19` between the camera and the banjo, the camera inside her for 7 of 18 frames; frames 1–4 mostly her dark back.
  - **Not faults:** O04a (the holder's shoulder at 11 cm: the over-the-shoulder phone shot, M7b's design); drizzle streaks passing the lens (O20d, O22e, O22f, one frame each); O19a crossing the haze volume's boundary as it leaves the treehouse (checked by eye at frames 92–114: the fog is continuous).
  - Ownership checked with a scratch probe (the hit object's collection and its instancer): O03d's body is `perf_crowd14_O03`, O11e's `perf_crowd19_O11`; neither is the shot's subject.
- **The fix for the three** (decisions 46): `config/look_m7.json` `fixes.hide_from_camera` {O08a: lamp_shade, O03d: crowd14, O11e: crowd19}; `blender/look.py` `hide_from_camera`, called first in the M7 camera hook, hides the object (a person whole: the instancer and everything it instances) from camera rays for that one sub-shot and restores it for the next. They keep their shadows and light. Stills checked against the frames as rendered (`review/m7/o08a_fix.jpg`, `review/m7/occluder_fixes_O03d_O11e.jpg`): the shot's subject is clear from frame 1; once the camera is clear of the object, the frame is unchanged (O03d frame 50).
- **The lamppost** (human interventions 30):
  - No camera near it (the park clearance run above).
  - **Its lantern was misbuilt** (`blender/park_m7c.py` `lamp_post`, M7c): the four panes have their corners on the diagonals, but the tray, cap and pyramid roof are 4-sided cylinders whose corners bmesh puts on the axes (checked: `create_cone(segments=4)` gives (±1, 0), (0, ±1)). So the roof overhung askew and the panes' corners stood out past the tray, most visible in O22g's close. Fixed: `aso_props.B.cyl` gets `spin` (default 0, so every other prop is unchanged), and the three are spun π/4. Still: `--still --at first --subs O22g` (1 min 5 s) → `review/m7/lantern_fix_O22g.jpg`.
  - Which sub-shots show the lantern (a scratch probe projecting a 7×7×7 grid over the lantern's box into each camera, every 3rd frame, occlusion ignored): O19b, O20e, O22a, O22f, O22g.
  - **O22b**: the walker heads for the overlook on a line just behind the post, so after about frame 160 of 110–253 he's behind the post and the box, slivers showing on either side. Not changed (decisions 46).
- **Re-renders** (old frames moved to `archive/renders/m7/frames_v1/<sub>/`):
  - `--subs O08a,O19b,O20e,O22a,O22f,O22g` (`log/render_logs/m7_fixes_r1.log`): O08a done (45 frames, 132 s); then the hook raised `ReferenceError` restoring `lamp_shade`, removed with the O08 build, and Blender exited 0 anyway. Fixed (the restore skips removed objects).
  - `--subs O19b,O20e,O22a,O22f,O22g` (`m7_fixes_r2.log`) and then `--subs O03d,O11e` (`m7_fixes_r3.log`): running.
