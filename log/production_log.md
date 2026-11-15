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
