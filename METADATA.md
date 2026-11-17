# Upload metadata

YouTube metadata for the main video, ready to paste at upload once the checklist below is done. Written by the agent; the human uploads. **Draft as of November 17, 2026:** the master is built (production log 81). The upload doesn't wait for Microsoft's final report (human interventions 37).

**Before uploading:**
- **Re-check the news and every link** before the upload. Links checked November 17 (production log 77): all live but the Washington Post's, which refuses automated fetches; open it in a browser (the human confirmed its 130,000 figure on November 17). The repository's link works once it's public. If the check is later than November 17, update "As of" under WHAT HAPPENED.
- **Make the repository public.** The end card and the description link to it; it's private until then.
- **Intervention count:** update the number in the description (`grep -c '^## ' log/human_interventions.md`; the master's credits slide reads 45, built 2026-11-17; the log is at 46). If more are logged before the upload, run `scripts/m7_end.sh` and `scripts/m7_master.py --end-only` again so the slide agrees.
- **Chapters:** recompute from the final cut (`timing/shot_times.json`, and the end sequence's plan in `review/m7_end/plan.txt`). The ones below are the current cut's, from the shots' starts (the intro's chapter starts at 0:10, not at the song's 0:07.6, because YouTube wants each chapter at least 10 s long; the song starts on its first downbeat, decisions 47): the end cards fade at 2:34.6 into the credits music (decisions 45; kept, human interventions 32).

---

## Main video (16:9, 1920×1080, 30 fps)

**File:** `renders/m7/master/all-systems-operational-master.mp4` (6:39.4: the 7.6 s bookend, the song from its first downbeat, 3:57.2, then 2:34.6 of cards). Captions: `lyrics/as_sung_lines_video.srt` (72 cues, the v1.3 lyrics as sung, line by line, in video time). Thumbnail: `review/thumbnail/thumbnail.jpg` (1280×720, `scripts/thumbnail_bait.py`; option P3, the human's pick).

### Title

Recommended (62 characters):

```
All Systems Operational — a stomp-clap singalong by a status page
```

Alternatives:
- `All Systems Operational: an AI-made singalong about the Microsoft 365 outage`
- `All Systems Operational (Live at Session 503) — AI-made stomp-clap satire`

### Description

```
AI-generated satire. A stomp-clap singalong sung by a status page, filmed as a made-up Seattle radio live session. Every time the gang vocals swell, the stream goes down.

On November 12–13, 2026, Microsoft 365 went down for most of a day. Here it is in the earnest, everybody-together voice of a 2010s tech ad.

A disclosure: the lyrics were drafted by Claude, made by Anthropic. Anthropic's Microsoft 365 connector broke during this outage, and Claude had outages of its own this year. The creator worked on Outlook and Word at Microsoft between 2014 and 2017, and the treehouse meeting room in the bridge is inspired by those years; it doesn't depict how this incident was handled.

Made with AI (credits below). The status-page screenshot and the creator's profile photo at the start are real; everything else on screen is made up. A human approved each stage and picked the takes; all 45 of those interventions are logged, with every prompt and production step:
https://github.com/Derivative-Work/all-systems-operational

CHAPTERS
0:00 The outage, for real
0:10 Intro: we're investigating reports
0:31 Verse 1: the inbox went still
0:49 Pre-chorus: we are aware
1:00 Chorus: all systems operational
1:29 Build: everybody at once
1:43 Verse 2: the agents that we hired
2:07 Chorus 2
2:36 Bridge: root cause
2:55 Build: restored for most users
3:07 Final chorus
3:27 Outro: remember Wednesday?
4:04 Credits
4:25 What happened
6:09 Disclosure

WHAT HAPPENED
(As of November 17, 2026.)
• Exchange Online problems began at 11:20 a.m. ET on Thursday, Nov 12, per Microsoft's preliminary report, and the wider outage followed at 1:26 p.m. (Digital Trends). It hit Outlook, Teams, SharePoint, Copilot and Defender in at least 74 countries. (Wire)
• Almost 130,000 Outlook problem reports came from U.S. users just after 1 p.m. (Washington Post)
• Some businesses fell back on fax machines to confirm trades. (Crypto Briefing)
• Restored servers kept going unresponsive once traffic returned. (Azure Blog UK)
• Anthropic and OpenAI both reported their Microsoft 365 connectors failing. (Cybersecurity News)
• Microsoft's preliminary post-incident report (Nov 15; EX1550543/MO1550821 in the Microsoft 365 admin center) names three factors: a latent defect from a July fix to its networking gateway servers, which its load tests missed; a routine Teams failover onto the same gateway; and nearly 14% of capacity out from an unrelated issue. Automatic rerouting spread the failure until more than 80% of servers were unresponsive. (The Register) Impact ended Friday, Nov 13, at 11:10 a.m. ET. The final report is due Nov 20.
• On Nov 13 Microsoft said the outage was "not related to cyber or AI / agents" (MacRumors). That came two days before its preliminary report, which doesn't mention AI or say who or what wrote the July fix.

SOURCES
Digital Trends: https://www.digitaltrends.com/computing/microsoft-365-outage-resolved/
Wire: https://wire.com/en/blog/microsoft-365-outage-november-2026
Washington Post: https://www.washingtonpost.com/technology/2026/11/13/microsoft-races-address-outage-affecting-users-around-world/
Crypto Briefing: https://cryptobriefing.com/microsoft-365-outage-74-countries/
Azure Blog UK: https://azureblog.co.uk/posts/microsoft-365-outage-12-november-2026/
Cybersecurity News: https://cybersecuritynews.com/microsoft-365-massive-outage-fixes-fail-as-restored-servers-keep-going-unresponsive/
The Register: https://www.theregister.com/saas/2026/11/16/microsoft-blames-monster-email-outage-on-software-defect-introduced-in-july-fix/5310026
MacRumors: https://www.macrumors.com/2026/11/13/microsoft-365-outage-resolving/
The opening spike: Downdetector counts reported by GV Wire: https://gvwire.com/2026/11/12/microsoft-outlook-down-for-thousands-of-users-downdetector-shows/

"Session 503" is a fictional broadcast, inspired by Seattle's live radio sessions. It is not affiliated with KEXP or any real radio station.

CREDITS
Words: Claude, audited before production by Gemini (Google), Nov 14
Music: Suno V6, edited and mastered by a human in Logic Pro; post-filtered with music-deslop
Credits music: an instrumental cover in Suno V6, post-filtered the same way
Rooms and people: Blender, with the people kit from Ever Present (MPFB, MakeHuman CC0 assets)
Two shots: FLUX.2 [dev] and LTX-2.3 in ComfyUI
Screens, cards and edit: Claude Code with Opus 5.5 (Remotion)
Little Switch: from Default On, https://github.com/Derivative-Work/default-on
The probes: from Sandbox Rhapsody, https://github.com/Derivative-Work/sandbox-rhapsody
Type: Inter, Work Sans, Caveat and Noto Sans Mono (SIL OFL)
Video and assets: CC BY-NC-SA 4.0 · Code: MIT
Satire. Not affiliated with or endorsed by Microsoft or any company named here.
#AIgenerated #musicvideo #satire
```

### Tags

Paste as one comma-separated line:

```
All Systems Operational, AI music video, AI generated, AI satire, Microsoft 365 outage, Outlook outage, Teams outage, status page, cloud outage, stomp clap, indie folk, singalong, live session, Session 503, Suno, Claude, Claude Code, Blender, Remotion, Derivative Work
```

### Settings

| Setting | Value |
|---|---|
| Category | Music |
| Audience | Not made for kids |
| Altered or synthetic content | **Yes.** The singing voice is AI-generated, and the rooms, people and two shots are rendered or generated. The real screenshot at the start is captioned "real screenshot"; the chat post is captioned "recreation" and its "(slop warning)" is highlighted as the in-video AI disclosure, the #it-help chat and the treehouse "dramatization". |
| Language / caption language | English / English |
| Captions | Upload `lyrics/as_sung_lines_video.srt` as English subtitles (72 cues, the lyrics as sung, line by line). Regenerate it if report day changes the bridge. |
| License | Standard YouTube License. YouTube's only Creative Commons option is CC BY, which would drop the NC-SA terms; the description states the licence instead. |
| Thumbnail | `review/thumbnail/thumbnail.jpg`: the treehouse's invented night dashboard close up (the gateway pool 84% unresponsive, ringed; services down) under the made-up status page's "All systems operational" banner, with one of the dashboard's DOWN tags as a stamp (option P3, human interventions 45; C before it, human interventions 39, is in `archive/review/thumbnail/thumbnail_C_pick.jpg`). Not the real screenshot or the creator's photo: those stay in the bookend. |
| Chapters | From the description (first chapter at 0:00; each over 10 s). |
| End screen | Over the disclosure card's last 20 s (from about 6:22). Put the elements in the bottom corners, clear of the card's text. |
| Comments | Open. |
| Visibility | Unlisted for a check pass, then public. |

---

## Short (vertical cut A, 1080×1920, 30 fps)

**File:** `renders/vertical/all-systems-operational-short-A.mp4` (53.9 s, 12 MB; `scripts/vertical_short.py`, human interventions 46): "We are aware" through the first chorus and the build to the first hard stop ("without fai—"), "We'll be right back" and "We're seeing renewed errors". Stacked: the made-up status page on top (every row green; Mail turns to "Renewed errors" at the end, the banner doesn't), the 16:9 picture, the lyric below, "AI-GENERATED SATIRE" throughout. Captions are burned in. Upload it after the main video is public, so the description and the related-video link can point to it.

### Title

Recommended (54 characters):

```
All Systems Operational — the status page sings along
```

Alternatives:
- `Every light is green (the stream is down)`
- `The Microsoft 365 outage as a stomp-clap singalong`

### Description

```
AI-generated satire: the Microsoft 365 outage of November 12–13, 2026, as a stomp-clap singalong sung by a status page. Every time the gang vocals swell, the stream goes down.

Full video: <the main video's link>

Made with AI: lyrics drafted by Claude (made by Anthropic, whose Microsoft 365 connector broke in this outage), music by Suno, video by Claude Code with Blender and Remotion. A human approved each stage. Everything on screen is made up. Production log: https://github.com/Derivative-Work/all-systems-operational

#AIgenerated #satire #Shorts
```

### Settings

| Setting | Value |
|---|---|
| Altered or synthetic content | **Yes** (the singing voice, the rooms and people). |
| Related video | The main video. |
| Category / audience | Music / not made for kids. |
| Captions | Burned in; no subtitle file. |
| Thumbnail | Shorts pick a frame; in the app, choose one from the chorus (about 0:11, the status banner over the singer). |
