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
