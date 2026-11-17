# Upload metadata

YouTube metadata for the main video, ready to paste at upload once the checklist below is done. Written by the agent; the human uploads. **Draft as of November 16, 2026:** the video is still rendering (M7), and report day (M8) changes the fact card, possibly the bridge, and the times below.

**Before uploading:**
- **The final report** (due November 20): read it, confirm the branch (A is the working plan; brief, "Branches by report outcome"), check the bridge, the whiteboard and the fact card against it, and fill in the fact card's "[link once published]". If it names an AI-assisted change, the description's "What happened" changes with the card.
- **The audits** (M6): run in each lab's app and logged in `log/audits/`. Fill in "[models, dates]" in the disclosure card, the description and the README.
- **The end card's placeholders:** "music by [generator]" (Suno: the song and the credits instrumental are both Suno V6) and "Audit log: [repo link]" (https://github.com/Derivative-Work/all-systems-operational).
- **Re-check the news and every link** the day before. Everything here is as of November 16.
- **Make the repository public.** The end card and the description link to it; it's private until then.
- **Intervention count:** update the number in the description (`grep -c '^## ' log/human_interventions.md`; 28 on 2026-11-16).
- **Chapters:** recompute from the final cut (`timing/shot_times.json`, and the end sequence's plan in `review/m7_end/plan.txt`). The ones below are the current cut's, from the shots' starts (the intro's chapter starts at 0:10, not at the song's 0:07.6, because YouTube wants each chapter at least 10 s long; the song starts on its first downbeat, decisions 47): the end cards fade at 2:34.6 into the credits music (decisions 45; kept, human interventions 32).

---

## Main video (16:9, 1920×1080, 30 fps)

**File:** to come at M7/M8 (6:39.4 with the current end sequence: the 7.6 s bookend, the song from its first downbeat, 3:57.2, then 2:34.6 of cards). Captions: `lyrics/as_sung_lines_video.srt` (72 cues, the v1.3 lyrics as sung, line by line, in video time). Thumbnail: not made yet.

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

On November 12–13, 2026, Microsoft 365 went down for most of a day: Outlook, Teams, SharePoint, Copilot and Defender, in at least 74 countries. Restored servers kept going unresponsive once traffic returned. Here it is in the earnest, everybody-together voice of a 2010s tech ad.

A disclosure: the lyrics were drafted by Claude, made by Anthropic. Anthropic's Microsoft 365 connector broke during this outage, and Claude had outages of its own this year. The creator worked on Outlook and Word at Microsoft between 2014 and 2017, and the treehouse meeting room in the bridge is inspired by those years; it doesn't depict how this incident was handled. Audited by models from other labs: [models, dates].

Made with AI: the song by Suno (edited and mastered by a human in Logic Pro), the words by Claude, the video by Claude Code in Blender and Remotion, two shots by FLUX.2 and LTX-2.3. The screenshot at the start is real; everything else on screen is made up. A human approved each stage and picked the takes. Each of those 28 interventions is logged, along with every prompt and production step:
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
4:04 End card
4:23 What happened
6:09 Disclosure

WHAT HAPPENED
(As of November 16, 2026.)
• Exchange Online problems began at 11:20 a.m. ET on Thursday, Nov 12, per Microsoft's preliminary report, and the wider outage followed at 1:26 p.m. (Digital Trends). It hit Outlook, Teams, SharePoint, Copilot and Defender in at least 74 countries. (Wire)
• Almost 130,000 Outlook problem reports came from U.S. users just after 1 p.m. (Washington Post)
• Some businesses fell back on fax machines to confirm trades. (Crypto Briefing)
• Restored servers kept going unresponsive once traffic returned. (Azure Blog UK)
• Anthropic and OpenAI both reported their Microsoft 365 connectors failing. (Cybersecurity News)
• Microsoft's preliminary post-incident report (Nov 15) names three factors: a latent defect from a July fix to its networking gateway servers, which its load tests missed; a routine Teams failover onto the same gateway; and nearly 14% of capacity out from an unrelated issue. Automatic rerouting spread the failure until more than 80% of servers were unresponsive. (The Register) Impact ended Friday, Nov 13, at 11:10 a.m. ET. The final report is due Nov 20: [link once published]
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
The outage-report spike at the start is drawn from Downdetector counts reported by GV Wire: https://gvwire.com/2026/11/12/microsoft-outlook-down-for-thousands-of-users-downdetector-shows/

"Session 503" is a fictional broadcast, inspired by Seattle's live radio sessions. It is not affiliated with KEXP or any real radio station.

CREDITS
Words: Claude, audited by [models, dates]
Music: Suno V6, edited and mastered by a human in Logic Pro; post-filtered with music-deslop (M6f 10k)
Credits music: an instrumental cover of the song in Suno V6, post-filtered with music-deslop
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
| Altered or synthetic content | **Yes.** The singing voice is AI-generated, and the rooms, people and two shots are rendered or generated. The real screenshot at the start is captioned "real screenshot"; the chat post is captioned "recreation", the #it-help chat and the treehouse "dramatization". |
| Language / caption language | English / English |
| Captions | Upload `lyrics/as_sung_lines_video.srt` as English subtitles (72 cues, the lyrics as sung, line by line). Regenerate it if report day changes the bridge. |
| License | Standard YouTube License. YouTube's only Creative Commons option is CC BY, which would drop the NC-SA terms; the description states the licence instead. |
| Thumbnail | To come. Not the real screenshot or the creator's photo: those stay in the bookend. |
| Chapters | From the description (first chapter at 0:00; each over 10 s). |
| End screen | Over the disclosure card's last 20 s (from about 6:22). Put the elements in the bottom corners, clear of the card's text. |
| Comments | Open. |
| Visibility | Unlisted for a check pass, then public. |
