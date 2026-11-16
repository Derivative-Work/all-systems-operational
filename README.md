# All Systems Operational

**AI-generated satire.** A mid-2010s stomp-clap singalong about the Microsoft 365 outage of November 12–13, 2026, filmed as a made-up Seattle public-radio live session, "Session 503". The narrator is the status page, singing in the earnest, everybody-together voice of a 2010s tech ad. Every time the gang vocals swell, the stream goes down: the band cuts out mid-word, the picture freezes under a buffering spinner, and one handclap keeps going, late. That's the retry collapse: Microsoft's restored servers kept going unresponsive once traffic returned.

> **Status, November 16, 2026: in production.** The final-look render (M7) is under way. Microsoft's final post-incident report is due November 20; on report day (M8) the bridge, the whiteboard and the fact card are checked against it, and the placeholders in square brackets on the cards (`[generator]`, `[repo link]`, `[models, dates]`, `[link once published]`) are filled in. The video isn't published yet.

**Conflict of interest:** the lyrics were drafted by Claude, made by Anthropic. Anthropic's Microsoft 365 connector broke during this outage, and Claude had outages of its own this year. The creator worked on Outlook and Word at Microsoft between 2014 and 2017, and the treehouse meeting room in the bridge is inspired by those years; it doesn't depict how this incident was handled. The disclosure card at the end says all of this. The lyrics and the concept are audited by models from other labs (M6), and every audit finding Claude rejects goes to the human for the final call.

**Nothing on screen ties AI-written code to this outage.** Microsoft said on November 13 that the outage was "not related to cyber or AI / agents"; its preliminary report (November 15) traces it to a latent defect from a July fix and doesn't say who or what wrote that fix. The video says exactly that and no more, unless the full report does.

This repository is the production record the video's end card points to. Claude Code produced the video. A human approved each milestone, picked the takes, made the Suno generation and the Logic Pro master, supplied the credits music and made the screenshots. Each of those 28 interventions so far is logged.

**The production log and decisions are written by the agent and are a record, not a statement of fact about Microsoft or anyone else:** where they discuss the outage, the fact card and its sources are the reference.

## How it was made

| Stage | What | Tools |
| --- | --- | --- |
| Lyrics | Drafted with Claude in the [planning chat](docs/planning_chat/planning_chat.md); the bridge rewritten (v1.3) from Microsoft's preliminary report. The audit by other labs' models comes next (M6) | Claude |
| Song | One Suno take ([`docs/suno/`](docs/suno/)). The human edited its stems in Logic Pro: the two hard stops, a separate handclap from Logic's loops, the master. The bridge was later repainted in Suno for lyrics v1.3. Post-filtered with a cleanup ("deslop") model | Suno v6, Logic Pro, music-deslop M6f |
| Credits music | An instrumental the human supplied, post-filtered; the end cards change on its sections | music-deslop M6f, librosa |
| Timing | Lyrics aligned to the vocal stems; beats, hits and per-bar energy from the stems; every shot and cut cued to a word, a bar or a hit | WhisperX, librosa |
| Rooms and people | Four Blender sets (live room, coffee shop, treehouse meeting room, hilltop park), backlit so every performer is a silhouette: no faces, no lip sync. Band and crowd from the Ever Present people kit, their performances driven by the stems; the probes from Sandbox Rhapsody | Blender 5.2 (Eevee), MPFB with MakeHuman's CC0 assets |
| Generated | The fax machine at a trading desk (O06), as a still and a clip; the hilltop park's far skyline plate (outpainted, one seam inpainted) and one clip of it (O22d) | FLUX.2 [dev] and LTX-2.3 in ComfyUI, on an NVIDIA GeForce RTX 5090 |
| Screens and cards | The status page, phones, calendar, lower thirds, buffering freezes, whiteboard, table tent, kick-drum head, treehouse screens, Little Switch, the fact card and end cards. All made up and typeset, and every changeable detail read from [`config/incident.json`](config/incident.json) | Remotion 4 |
| Real captures | The opening bookend's screenshots (below) | the human's screenshots |
| Human | Milestone approvals, takes, the Suno generation and the master, the credits music, the screenshots, every edit note | a human |

## What's real, and what's made up

Real, in the opening bookend (0:00–0:08) only:
- **The creator's screenshots (0:02–0:05):** Microsoft's status page failing to load ("real screenshot · Thu, Nov 12, 1:07 p.m. ET") and the "No license found" error ("real screenshot · Fri, Nov 13"). They're the only real logos and interfaces in the video, there so the made-up status page never reads as Microsoft's. The "No license found" capture is a placeholder until it has permission or is replaced by the creator's own.
- **The creator's post (0:05–0:08):** the creator sharing this song in their #it-self-help channel, recreated in a generic chat UI and captioned "recreation". The creator's own name and photo are the one real-person exception, with their approval.

Made up, everywhere else:
- **The outage-report spike (0:00–0:02):** an unlabeled chart drawn from reported Downdetector counts ([GV Wire, Nov 12](https://gvwire.com/2026/11/12/microsoft-outlook-down-for-thousands-of-users-downdetector-shows/)), not a capture.
- **The status page, the station and the session:** "Session 503" at 50.3 FM (an impossible frequency) is a fictional broadcast, not affiliated with KEXP or any real radio station. It evokes Seattle's live-session format without any station's name, logo or design.
- **The #it-help chat** (invented names) and **the treehouse meeting room** are captioned "dramatization". The treehouse doesn't depict where or how the real incident was handled.
- **The whiteboard** sings the bridge back: root cause, contributing factors, lessons learned. On "(Not related to cyber, AI or agents)" two tags land: "Microsoft, Nov 13, two days before its root-cause report." and "The report doesn't say who or what wrote the July fix."

## Sources

### The fact card, verbatim

Four pages after the song. Microsoft's preliminary report carries a no-reproduction notice, so the card quotes a few words of it at most and never shows its pages.

1. Exchange Online problems began at 11:20 a.m. ET on Thursday, Nov 12, per Microsoft's preliminary report, and the wider outage followed at 1:26 p.m. *([Digital Trends](https://www.digitaltrends.com/computing/microsoft-365-outage-resolved/))*. It hit Outlook, Teams, SharePoint, Copilot and Defender in at least 74 countries *([Wire](https://wire.com/en/blog/microsoft-365-outage-november-2026))*.
2. Almost 130,000 Outlook problem reports came from U.S. users just after 1 p.m. *([Washington Post](https://www.washingtonpost.com/technology/2026/11/13/microsoft-races-address-outage-affecting-users-around-world/))*.
3. Some businesses fell back on fax machines to confirm trades *([Crypto Briefing](https://cryptobriefing.com/microsoft-365-outage-74-countries/))*.
4. Restored servers kept going unresponsive once traffic returned *([Azure Blog UK](https://azureblog.co.uk/posts/microsoft-365-outage-12-november-2026/))*.
5. Anthropic and OpenAI both reported their Microsoft 365 connectors failing *([Cybersecurity News](https://cybersecuritynews.com/microsoft-365-massive-outage-fixes-fail-as-restored-servers-keep-going-unresponsive/))*.
6. Microsoft's preliminary post-incident report (Nov 15) names three factors: a latent defect from a July fix to its networking gateway servers, which its load tests missed because they "tended to focus on weaker hardware"; a routine Teams failover onto the same gateway; and nearly 14% of capacity out from an unrelated issue. Automatic rerouting spread the failure until more than 80% of servers were unresponsive *([The Register](https://www.theregister.com/saas/2026/11/16/microsoft-blames-monster-email-outage-on-software-defect-introduced-in-july-fix/5310026))*. Impact ended Friday, Nov 13, at 11:10 a.m. ET. Final report due Nov 20: [link once published].
7. On Nov 13 Microsoft said the outage was "not related to cyber or AI / agents" *([MacRumors](https://www.macrumors.com/2026/11/13/microsoft-365-outage-resolving/))*. That came two days before its preliminary report, which doesn't mention AI or say who or what wrote the July fix.
8. **Format:** "Session 503" is a fictional broadcast and is not affiliated with KEXP or any real radio station.

The brief lists every source the production used ([`docs/brief.md`](docs/brief.md#sources)). The links are as of the brief's revision 141 (November 16); they're reopened and checked against the final report on report day.

## Where things are

- [`log/production_log.md`](log/production_log.md): every generation, analysis and render, with the command, model, prompt, seed, inputs, outputs and whether it was kept.
- [`log/human_interventions.md`](log/human_interventions.md): every human action, in the human's words.
- [`log/decisions.md`](log/decisions.md): every deviation from the brief, and why. [`log/ai_changes.md`](log/ai_changes.md): what the song generator changed from the lyrics as written.
- [`log/prompts/`](log/prompts/): every prompt and seed, verbatim. [`log/render_logs/`](log/render_logs/): the render and check logs.
- [`docs/brief.md`](docs/brief.md): a plain-text mirror of the brief (overview, look, lyrics, shot list O01–O24, report branches, rendering plan, cards, audit plan, guardrails). The video deviates from it where `log/decisions.md` says so. [`docs/plan.md`](docs/plan.md): the milestones. [`docs/coverage.md`](docs/coverage.md) and [`docs/coverage_m5c.md`](docs/coverage_m5c.md): the cut, 94 shots cut to bars and hits.
- [`docs/planning_chat/`](docs/planning_chat/): the planning chat. [`docs/suno/`](docs/suno/): the Suno take's page record and the lyrics as submitted. [`lyrics/`](lyrics/): the lyrics as pasted and as sung, with word and line timings.
- [`config/`](config/): `incident.json` (every detail that waits for the report), the look, the coverage plan, shot cues, end cards and seeds. [`timing/`](timing/): the timing map, the music maps, shot times and the credits music's sections.
- [`blender/`](blender/): the sets, the look, the coverage and the performances. [`blender/ep/`](blender/ep/) and [`blender/lib/`](blender/lib/): the people and probe kits, each with a README on where it came from.
- [`remotion/`](remotion/): every screen and card. [`remotion/src/defaultOn/`](remotion/src/defaultOn/): Little Switch, copied unchanged from [Default On](https://github.com/Derivative-Work/default-on).
- [`scripts/`](scripts/): one script per step, each documented at the top. [`comfy/api/`](comfy/api/): the image-to-video graph.
- [`review/`](review/): the contact sheets and boards from each milestone gate. [`archive/`](archive/): rejected passes, kept.
- [`METADATA.md`](METADATA.md): the YouTube title, description, chapters, tags and settings, and the checklist before upload.

## Reproducing it

Large files (audio, screenshots, the figure library, generated stills and clips, renders, the edit) are not in git; [`MANIFEST.sha256`](MANIFEST.sha256) lists them with checksums. A release archive with the video, the audio that can't be regenerated, and every still and clip the production made comes with publication.

Until then, the commands are in the production log, step by step, and each script's header says what it reads and writes.
- **Environment:** `uv sync` (Python, pinned in `uv.lock`), `PUPPETEER_SKIP_DOWNLOAD=1 npm install` (Remotion 4.0.534), Blender 5.2, and ComfyUI for the generated shots.
- **Seeds:** every random process reads its seed from [`config/seeds.json`](config/seeds.json) (main seed 41). Stills and clips with the same seed, weights and ComfyUI version should match on the same GPU (production used an NVIDIA GeForce RTX 5090, 32 GB); expect small differences elsewhere.
- **Can't be regenerated:** the song (Suno doesn't give the same song twice), the Logic master, and the credits music. The post-filter model is private for now, so the archive will keep the post-filtered audio.
- **Not in the archive:** the Slack screenshots the creator supplied as text-style reference only (private).

## Licences

- **Video and assets:** [CC BY-NC-SA 4.0](LICENSE-media.md). That file lists exactly what it covers and what it doesn't (the kits, fonts, the real captures, the ComfyUI graph, the clap loop, Suno's records).
- **Code:** [MIT](LICENSE). Rendering it needs [Remotion](https://www.remotion.dev), which has its own licence: free for individuals, small companies and non-profits.

## Credits

- **Lyrics:** Claude, drafted in the [planning chat](docs/planning_chat/planning_chat.md). Audited by [models, dates].
- **Music:** Suno v6, one take ("Remember Wednesday" on Suno, e7994418), its bridge repainted for lyrics v1.3. Edited and mastered by the human in Logic Pro, with Logic's "Clap 2 - Warm Embers" loop.
- **Credits music:** an instrumental supplied by the human.
- **Post-filter:** music-deslop (M6f, 10k steps), a cleanup model for AI-generated music that Claude Code built and trained from a human-written spec, on Creative Commons audio only (training data listed in the [Folks Like Us README](https://github.com/Derivative-Work/folks-like-us#mastering-model-training-data)). The model is private for now.
- **Video:** Claude Code with Claude Opus 5.5, in Blender and Remotion. The fax still and the park's far plate are from FLUX.2 [dev] (Black Forest Labs), their clips from LTX-2.3 (Lightricks), each used under its own licence.
- **The people and band:** the people kit from Ever Present, by the same author (unreleased), relicensed MIT here ([`blender/ep/`](blender/ep/)); the people are built with MPFB from MakeHuman's CC0 assets.
- **The probes:** from [Sandbox Rhapsody](https://github.com/Derivative-Work/sandbox-rhapsody) ([`blender/lib/`](blender/lib/)), green for Anthropic, amber for OpenAI.
- **Little Switch:** from [Default On](https://github.com/Derivative-Work/default-on); the rig is used unchanged.
- **Fonts:** [Inter](https://fonts.google.com/specimen/Inter), [Work Sans](https://fonts.google.com/specimen/Work+Sans), [Caveat](https://fonts.google.com/specimen/Caveat) and [Noto Sans Mono](https://fonts.google.com/noto/specimen/Noto+Sans+Mono) (SIL Open Font License 1.1), in [`remotion/public/fonts/`](remotion/public/fonts/).

Satire. Not affiliated with or endorsed by Microsoft, KEXP or any company or station named here.
