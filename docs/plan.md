# Production plan

Milestones for the brief (rev 106), in the order of its "Order of work", with a human gate at the end of each. Shots
that read `incident.json` (O02, O10, O13, O18) and the bridge audio wait for the full post-incident report; everything
else can be finished before it. Branch A (config or capacity) is the working plan.

| # | Milestone | Agent does | Human gate | Needs the GPU |
| --- | --- | --- | --- | --- |
| M0 | Setup and import (done 2026-11-15) | Brief mirror, planning chat and Suno captures, audio, screenshots, the three kits, logs | Answer the open questions below | No |
| M1 | Audio lock | WhisperX on the lead and backing stems; lyrics as sung vs the brief; hard stops, the lone clap, key, tempo, loudness, post-filter check; listening clips | Lock the master (post-filtered or not), the clap timing, the melody check against "Ho Hey" and "Home" | WhisperX (or CPU, slower) |
| M2 | Timing map | Lyrics as sung, forced alignment, beat grid (about 100 bpm), `config/shot_cues.json` for O01–O24, shot times, a review video with the click | Approve the cues | No |
| M3 | Grey-box and screen kit | Four Blender sets (live room, coffee shop, treehouse with deck, hilltop park) with Ever Present's people and band, the Sandbox Rhapsody probes (green Anthropic, amber OpenAI) and a lighting board; new poses (late clap, mug raise, crowd push, walk-off); band instruments the kit lacks (banjo, tambourine, kick drum with the SESSION 503 head). Remotion: status page, phones, calendar, lower thirds, buffering freeze, whiteboard, table tent, kick-drum head, cards, the Little Switch plane, all reading `incident.json` | Approve the rooms and the screens | Blender board renders |
| M4 | Generated still | The fax-at-a-trading-desk still (O06), lightly animated; optional fog-tower plate (O07 alternate). Negatives: faces, logos, boat, ship, ferry, water | Pick takes | ComfyUI |
| M5 | Animatic | 540p animatic of every shot cut to the locked master, bookends included | Approve the cut | Blender, Eevee |
| M6 | Concept audit | Triage the auditors' outputs (Copilot, ChatGPT, Grok, an open-weights model; Gemini round 1 is done), with each maker's stake beside its findings | Run the audits in each lab's app; rule on rejected findings | No |
| M7 | Final look | Final-look renders and 1080p cut for every shot that doesn't wait for the report; disclosure card; end cards | Review with sound | Blender, Cycles or Eevee |
| M8 | Report day | Update `incident.json`, pick the branch, tighten or regenerate the bridge and splice it (time-stretch the bridge to the map, never the reverse), re-render O02/O10/O13/O18 and the fact card; report-day audit; captions, description, release | Final approval | Short re-renders |

The concept audit prompt in the brief is ready now and doesn't depend on any render, so the human can run it while
M1–M5 proceed.

## Open questions from M0

See the latest entry in `log/production_log.md` and the session summary; answers go in `log/human_interventions.md`.
