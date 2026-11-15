<!-- Plain-text mirror of the Claude Doc https://claude.ai/artifact/VPEaJhs55vieCdQcS6C79E (rev 116), read with the docs tools. The doc is the source of truth. Regenerate: scripts/mirror_brief.py. -->

# All Systems Operational: Shot List and Production Brief

2026-11-13 · Albert Armea

## Overview

"All Systems Operational" is a mid-2010s stomp-clap indie singalong, filmed as a Seattle public-radio live session. The narrator is the status page, singing in the earnest, everybody-together voice of a 2010s tech ad. Every time the gang vocals swell, the stream goes down.
- **Form:** gang vocals build until everyone is shouting together, then the band cuts out mid-word and one handclap keeps going, off the beat. That's the retry collapse: Microsoft's restored servers kept going unresponsive once traffic returned.
- **Why this genre:** stomp-clap was the sound of 2010s tech advertising, so the status page is singing in its own brand voice. It borrows nobody's tradition, and the gang chorus is literally everyone signing in at once.
- **Why Seattle:** it's Microsoft's home region and the creator's, and the live-session video is a format Seattle viewers know on sight. The session is a livestream, so the outage happens to the video itself.
- **The turn:** Microsoft says the outage "was introduced by an issue during an earlier network capacity upgrade" and was "not related to cyber or AI / agents" ([MacRumors](https://www.macrumors.com/2026/11/13/microsoft-365-outage-resolving/)). The bridge sings that back: the oldest cause in the book, in the year everyone expected a new one.
- **Fit:** a sequel to LGTM. LGTM is about the approval; this is the bill landing on everyone downstream. Season 2.
- **Status, Nov 14:** Microsoft confirmed full restoration on Saturday; the full post-incident report is pending. The genre moved from a jazz funeral (no singer read as right for the genre, and the topic didn't justify the borrowing), past a power ballad (too close to Share the Shares) and EDM (too close to other creators in this space).

## Look, cast and series callbacks

A made-up listener-supported station's live session, "Session 503," in four rooms. It changes rooms at each collapse, the way a show gets moved when the stream drops, and the bridge moves into a treehouse meeting room. Grey Seattle daylight through big windows backlights every performer, so the silhouette rig still works: no faces, no lip sync.
- **The live room (Intro to the first collapse):** acoustic panels, rugs, a wall of rain-streaked windows, an ON AIR sign over the door. The band plays to a small standing crowd.
- **The coffee shop (Verse 2 ****and Chorus 2****):** the station's "on the road" session. String lights, mismatched chairs, steamed windows, mugs on every surface. Then the bridge moves into a treehouse meeting room: rain on the roof, moss on the railings, a whiteboard, a conference phone and a tangle of chargers. It's the one scene about the people inside, drawn from the creator's own meetings in one.
- **The outdoor session (final build to the end):** a hilltop park in drizzle, evergreens, a city skyline in fog. Nobody but one person has an umbrella.
- **The band:** a silhouette five-piece with acoustic guitar, banjo, kick drum, tambourine and a gang of backing singers. Built once in Blender and reused in every room; the crowd is the Ever Present audience kit. The kick drum head reads SESSION 503.
- **The host:** a public-radio voice, seen only as a silhouette at the console. Lower thirds carry the song title and the status updates.
- **The status page and station:** both made up. The station evokes Seattle's live sessions without any real station's identifiers (see Guardrails); no real cafe's branding. Microsoft is named only on the fact card.
- **The mourners are now an audience:** probes from the Sandbox Rhapsody kit at a cafe table, with a table tent reading "connector unavailable." The green probe (Anthropic's house, as in Not Yet) is the song's author; a second probe stands in for OpenAI, whose connector also broke. Confirm amber isn't already assigned to another lab before using it.
- **Switch from Default On:** silent, flat 2D cartoon in mustard, never restyled or voiced. He's the switch that runs the ON AIR sign. Last time Microsoft 365 wouldn't let him switch the AI off; this time it can't stay on.
- **Other callbacks:** an LGTM sticker on the kick drum (branch B only); the "to be determined" fields echoing Ghost in the Machine's repeated defaults.

## Style prompt and lyrics v1.2

v1.1 applies audit round 1 (Gemini), approved by the human on November 14, 2026: "Hey!" as the only shout, a "Five-oh-three" post-chorus, and "cyber" restored to Microsoft's denial in the bridge. v1.2 adds a nostalgia layer for Wednesday, when everything worked: mood words and warmer instruments in the style prompt, a "Remember Wednesday" outro tag, and "was green" in the final chorus. Two swap points stay open for the full report.

**Style prompt**

```
mid-2010s stomp-clap indie folk pop, 100 bpm, acoustic guitar strums, banjo, whistled hook, kick-drum stomps, handclaps, tambourine, gang vocals shouting hey, earnest raspy male lead vocal, big singalong chorus, abrupt full-band stops, bittersweet, wistful, nostalgic, borrowed minor iv chord, cello, pump organ drone, warm tape saturation, thin filtered verses opening into full warm choruses
```

**Lyrics**

```
[Intro: whistled hook over acoustic guitar, then stomp-clap]

[Sung softly, solo voice]
We're investigating reports
that some of you
can't reach anything

[Verse 1: solo voice, guitar, stomp]
One p.m. on a Thursday and the inbox went still (Hey!)
The calendar was empty and the queue began to fill (Hey!)
The trading desk went looking for a fax machine (Hey!)
Somewhere a server's lying in a field of green

[Pre-Chorus: call and response]
We are aware (we are aware)
Some users may (some users may)
Be experiencing (experiencing)
Everything

[Chorus: full band, gang vocals]
All systems operational (Hey!)
Every light is green (Hey!)
All systems operational (Hey!)
Believe the screen (Hey!)
Nothing here is broken
Everything is fine
All systems operational
Please stay on the line

[Post-Chorus: gang chant]
Five-oh-three, five-oh-three
Please stay on the line

[Build: stomps double, everyone joins]
Early signs of stabilization (Hey!)
Everybody sing it, everybody at once (Hey!)
Open up the laptop, open up the mail (Hey!)
Ten million voices singing out without fai—

[Hard stop: full band cuts out]

[One lone handclap, off the beat]

[Sung softly, solo voice]
We're seeing renewed errors

[Verse 2: solo voice, guitar, stomp]
The agents that we hired to read the mail for us (Hey!)
Are waiting in the lobby asking where the server was (Hey!)
The chatbot lost its inbox so it couldn't write this song
(It wrote it anyway)
Everything is wired to everything, and everything is gone

[Chorus: full band, gang vocals]
All systems operational (Hey!)
Every light is green (Hey!)
All systems operational (Hey!)
Believe the screen (Hey!)
Nothing here is broken
Everything is fine
All systems operational
Please stay on the line

[Post-Chorus: gang chant]
Five-oh-three, five-oh-three
Please stay on the line

[Bridge: half-time, guitar and voice only, earnest]  <- SWAP POINT 1
Root cause
An earlier upgrade
Met a recent change
Contributing factors
(Not related to cyber, AI or agents)
Full report
To follow
Lessons learned
(We're committed to doing better)

[Build: stomps return, one at a time]
Service has been restored for most users (Hey!)
Service has been restored for most users (Hey!)

[Final Chorus: everyone, loudest]
All systems operational (Hey!)
Every light was green (Hey!)
All systems operational (Hey!)
Believe the screen (Hey!)
Nothing here is broken
Everything is fine
All systems operational
Please stay on the—

[Hard stop]

[Outro: whistled hook, alone, slowing; then sung softly over a borrowed minor iv]
Remember Wednesday? (Hey...)
The inbox always loaded
The meetings had a link
And no one knew how good we had it
Back when the cloud was new

[Spoken]  <- SWAP POINT 2
We are deeply sorry for the disruption

[Sung, small]
All systems
operational?
```

**Generation and edit notes**
- **The lone clap:** after each hard stop, keep one clap from the stem and nudge it late. Generators won't do this on their own.
- **Hard stops:** generate each build as its own section and cut it yourself before the next downbeat; generators tend to finish the phrase.
- **Chants:** "Hey!" sits on line ends only, so a chant never lands on a fact.
- **Melody check:** before locking the track, compare the hook and chorus against "Ho Hey" and "Home." Generators drift toward their references in this genre.
- **Nostalgia:** if the generator ignores the minor iv under "Remember Wednesday," regenerate the outro alone. The verses' thin, old-phone-speaker filter can also be done in the edit.

**Swap points**
- **Bridge:** rewrite to match the full post-incident report. If it confirms the network change, only "An earlier upgrade / Met a recent change" may need tightening.
- **Outro:** the apology quotes Microsoft's statement ([MacRumors](https://www.macrumors.com/2026/11/13/microsoft-365-outage-resolving/)). Swap it if the report's wording differs.

## Shot list

24 shots in the order sung, across four rooms. All four rooms are Blender sets peopled with the Ever Present audience kit; only one cutaway is generated. The four shots marked as reading `incident.json` change when the report lands.

| # | Section | Lyric or beat | Shot | Asset | Reads incident.json |
| --- | --- | --- | --- | --- | --- |
| O01 | Opening bookend | Before the music | Three beats. First, the outage-report spike: a made-up, unlabeled chart drawn from reported Downdetector counts (about 2,400 Outlook reports at 9:50 a.m. PT, past 130,000 by 10:17, GV Wire). Then the creator's real screenshots: a Microsoft 365 app failing on Friday, Nov 13 (placeholder until permission or a new capture), then Microsoft's service status page failing to load, timestamped and captioned "real screenshot". Last, the creator's #it-self-help post, recreated for this song in a generic chat UI with the creator's real name and photo, describing this song: "(my last meme about this, I promise)" is struck through, then "no video yet", then the cursor clicks play and the song starts | Remotion (chart, chat post) + screen captures | No |
| O02 | Intro | Whistled hook | Hard cut to the made-up status page, every row green, each stamped "Last updated: Thu 12:58 p.m." A page that can't load can't update. One row flips to "Investigating" | Remotion | Yes (status phrases) |
| O03 | Intro | "We're investigating reports" | The live room: rain on the windows, band backlit in silhouette, a small standing crowd. Lower third: "All Systems Operational · Live at Session 503" | Blender (live room, kit) + Remotion lower third | No |
| O04 | Verse 1 | "inbox went still" | Over a crowd member's shoulder, a phone shows a generic team-chat message in #it-help: "is email down for anyone else?" Its +1 count climbs on each Hey! | Blender + Remotion phone texture | No |
| O05 | Verse 1 | "calendar was empty" | Full-frame phone: a calendar grid draining of events, one box at a time | Remotion | No |
| O06 | Verse 1 | "fax machine" | A fax machine at a trading desk, one page curling out | Generated still, lightly animated | No |
| O07 | Verse 1 | "field of green" | A lone server lying on an empty chroma-key green screen, captioned [background failed to load]. Alternate, if Verse 1 needs more Seattle: the server on a lawn under grey sky, with a tall needle-like tower in the fog whose top has only half loaded, a stalled low-res block. Same caption. Never the real Space Needle in detail, no fountain or water, and kept out of the radio-session rooms so it doesn't read as KEXP at Seattle Center | Blender (server on a green plane); alternate adds a fog-tower plate pixelated in Remotion | No |
| O08 | Pre-chorus | Call and response | The host's silhouette at the console; each echo appears in the lower third. On the first echo, IT replies in the #it-help thread: "we are aware". Optional: a two-second cutaway on "we are aware" to the treehouse meeting room at night, silhouettes hunched over laptops (dramatization) | Blender (live room; treehouse for the cutaway) + Remotion | No |
| O09 | Chorus 1 | Full band | Wide on the live room; the crowd joins the Hey!s. Kick drum head: SESSION 503. Lower-third uptime ticks at 99.9% | Blender (kit) + Remotion kick-drum texture | No |
| O10 | Build | "Early signs of stabilization" | Switch on the wall by the door, wired to the ON AIR sign, the only full-color thing in frame. The host flips him ON; the sign glows | Blender + Switch as a flat Remotion plane | Yes (status phrases) |
| O11 | Build | "everybody at once" | Everyone crowds the mics; a livestream viewer count spins upward and the chat floods. Switch strains under the load | Blender (kit, crowd push) + Remotion overlay | No |
| O12 | Hard stop 1 | "without fai—" | The frame freezes under a buffering spinner. Switch sags to OFF; ON AIR goes dark. One silhouette in the crowd keeps clapping, late | Blender (one kit figure on a clap loop) + Remotion freeze | No |
| O13 | After the stop | "renewed errors" | A technical-difficulties card: "We'll be right back." Status row back to red | Remotion | Yes (status phrases) |
| O14 | Verse 2 | "agents that we hired" | Cut to the coffee shop session. Probes at a cafe table with mugs; the table tent reads "connector unavailable". On the wall behind them, a Polaroid of the band in this same room, lit warm, captioned "Wed 11/11" | Blender (cafe, kit, Sandbox Rhapsody probes) + Remotion table-tent texture | No |
| O15 | Verse 2 | "couldn't write this song" | The green probe's LED dims, then comes back green on "(It wrote it anyway)." Disclosure card follows (see Bookends) | Blender (probe LED) + Remotion card | No |
| O16 | Verse 2 | "wired to everything" | The cafe's string lights are the dependency web: one bulb goes out and the dark runs down every strand | Blender (emission driven by script) | No |
| O17 | Chorus 2 | Full band | Cafe crowd singalong, mugs raised on the Ho!s; steam on the windows | Blender (kit, mug-raise pose) | No |
| O18 | Bridge | "Root cause" | Half-time. The session moves into the treehouse meeting room. The whiteboard behind the band fills in as each line is sung: root cause, contributing factors, lessons learned. The "not related to cyber, AI or agents" line is credited on the whiteboard to Microsoft's Nov 13 statement. Captioned "dramatization" | Blender (treehouse) + Remotion whiteboard texture | Yes (root-cause fields) |
| O19 | Build | "restored for most users" | The treehouse door opens onto the deck in the drizzle; the camera rises out of the trees to the hilltop park, skyline in fog. Stomps return one at a time; lower third back to green | Blender (one continuous camera move, rain particles, fog volume) | No |
| O20 | Final chorus | Everyone, loudest | Wide outdoor singalong. One person has an umbrella. Switch is on a weatherproof outlet box on a lamp post, ON | Blender (park, kit) + Switch plane | No |
| O21 | Final hard stop | "stay on the—" | The same buffering freeze as O12, captioned "Incident reopened." Switch holds one beat longer than last time, then drops | Remotion freeze over the Blender frame | No |
| O22 | Outro | Whistled hook | The park empties; one silhouette walks off whistling. From "Remember Wednesday" on, the picture takes soft film grain and a warm grade, like a home movie; everything before stays in grey daylight. Lower third: "We are deeply sorry for the disruption" | Blender (kit walk cycle) + Remotion lower third | No |
| O23 | Outro | "operational?" | Back to the made-up status page; the green row flickers, still stamped "Last updated: Thu 12:58 p.m." | Remotion | No |
| O24 | Closing bookend | After the music | End card (see Bookends), then Next incident: TBD | Remotion | No |

## Branches by report outcome

Branch A is the working plan, since Microsoft blamed a network capacity upgrade and ruled out AI. B and C stay ready in case the full report says otherwise or never comes.

| Branch | Trigger | Lyric changes | Shot changes | Fact card |
| --- | --- | --- | --- | --- |
| **A. Config or capacity** (current) | The report confirms the network upgrade and change | Tighten the bridge's cause lines only | O18 shows a one-line config diff after the form fills: the whole singalong over one line. O16 stays as drawn | The report's cause, quoted; Microsoft's "not related to AI" line |
| **B. AI-assisted change named** | The report contradicts the preliminary statement and names an AI-generated or AI-assisted change | Rewrite the bridge; cut "Not related to AI or agents" | Add an LGTM sticker to the kick drum head (O09, O17, O20). O18 quotes the report | The report's exact wording, plus the contradiction with the Nov 13 statement |
| **C. Vague or late** | No report inside the release window, or one with no clear cause | Bridge keeps the preliminary lines; "Full report / To follow" loops once more | O18's root-cause field ends in a blinking cursor | The preliminary statement, dated; end card reads Root cause: final report pending as of [date] |

In every branch, nothing on screen ties AI-written code to this outage unless the report does. If AI shows up, it's as the mourners and the dependencies, never the cause.

## Rapid-response rendering plan

**Asset types**

Everything except the bridge audio and four Remotion shots can be finished before the report is out. The rooms are rendered, not generated, so they stay consistent across all four sets and nothing in them can drift toward a real studio, a face or water.
- **Blender (Eevee), about 16 shots:** four sets (live room, coffee shop, treehouse with deck, hilltop park), each backlit by grey window or sky light so every performer is a silhouette. People come from the Ever Present audience kit; the probes from the Sandbox Rhapsody kit. Rain on glass, drizzle, fog and the string lights are shaders, particles and emission, not clips. Add any poses the kit lacks: a late clap loop, a mug raise, a crowd push and a walk-off.
- **Remotion:** every screen, word and card: the status page, phones, lower thirds, the buffering freezes, the whiteboard, the table tent, the kick-drum head and the end cards. Rendered full-frame or as textures for the Blender screens, so every word is exact. Switch is a flat Remotion plane composited into the Blender shots, so he stays 2D.
- **Generated, one still:** the fax machine at a trading desk (O06), the one cutaway the sets can't cover, lightly animated with an image-to-video model. Optionally, a fog-tower plate for the O07 alternate. Reject any take with a face, a logo or water.
- **No lip sync anywhere.** The host speaks through lower thirds.

**incident.json drives every changeable detail**

```
{
  "asOf": "2026-11-13",
  "statusPhrases": ["Investigating", "Early signs of stabilization", "Renewed errors", "Restored for most users"],
  "rootCause": "An earlier network capacity upgrade, surfaced by a recent network change",
  "contributingFactors": ["Not related to cyber or AI / agents"],
  "configDiff": null,
  "branch": "A",
  "factCardQuotes": [],
  "sources": []
}
```

**Order of work**
- **Now:** generate the audio in sections at a fixed tempo, with the bridge as its own segment. Lock the timing map.
- **Now:** grey-box the four Blender sets, import the Ever Present audience kit and the Sandbox Rhapsody probes, and add the missing poses.
- **Now:** build the Remotion components, all reading from `incident.json`, and wire their textures into the sets.
- **Now:** generate the fax still, then a 540p animatic of every shot cut to the track.
- **Report day:** update `incident.json`, regenerate the bridge (plus Verse 2 only if switching to branch B), and splice it in. Re-render the Remotion textures, then only the Blender frames that show them (O18's whiteboard).
- **Report day:** run the audit on the final bridge and fact card, apply fixes, and render at 1080p.

Blender and image-to-video need the 5090, so schedule those renders around the post-filter's training runs, as with Ever Present. Audio splices hold only if the tempo is identical across regenerations; if the generator drifts, time-stretch the bridge to the map, never the other way round.

## Bookends, fact card, disclosure and end card

**Opening bookend (O01).** The outage-report spike as a made-up chart from reported counts, then the creator's real screenshots with timestamps on screen (no more than 3 seconds together), then the creator's #it-self-help post sharing the song, recreated in a generic chat UI and captioned as a recreation. "(my last meme about this, I promise)" and "no video yet" get struck through, one after the other, and clicking play starts the song on the cut to the green status page.

**Fact card (after O24).** Each line is sourced, and checked against the full report at render time.
- Exchange Online problems began around 11:17 a.m. ET on Thursday, Nov 12, and the wider outage followed at 1:26 p.m. ([Digital Trends](https://www.digitaltrends.com/computing/microsoft-365-outage-resolved/)). It hit Outlook, Teams, SharePoint, Copilot and Defender in at least 74 countries ([Wire](https://wire.com/en/blog/microsoft-365-outage-november-2026)).
- Almost 130,000 Outlook problem reports came from U.S. users just after 1 p.m. ([Washington Post](https://www.washingtonpost.com/technology/2026/11/13/microsoft-races-address-outage-affecting-users-around-world/)).
- Some businesses fell back on fax machines to confirm trades ([Crypto Briefing](https://cryptobriefing.com/microsoft-365-outage-74-countries/)).
- Restored servers kept going unresponsive once traffic returned ([Azure Blog UK](https://azureblog.co.uk/posts/microsoft-365-outage-12-november-2026/)).
- Anthropic and OpenAI both reported their Microsoft 365 connectors failing ([Cybersecurity News](https://cybersecuritynews.com/microsoft-365-massive-outage-fixes-fail-as-restored-servers-keep-going-unresponsive/)).
- Microsoft's cause: an issue from an earlier network capacity upgrade, "not related to cyber or AI / agents" ([MacRumors](https://www.macrumors.com/2026/11/13/microsoft-365-outage-resolving/)). Microsoft confirmed full restoration on Saturday, Nov 14 ([Digital Trends](https://www.digitaltrends.com/computing/microsoft-365-outage-resolved/)). Full post-incident report: [link once published].
- **Forma****t:** "Session 503" is a fictional broadcast and is not affiliated with KEXP or any real radio station.

**Conflict-of-interest disclosure (after O16, repeated in the description).**

> Lyrics by Claude, made by Anthropic. Anthropic's Microsoft 365 connector broke during this outage, and Claude had outages of its own this year. The creator worked on Outlook and Word at Microsoft almost 10 years ago, and the treehouse meeting room in the bridge is inspired by those years; it doesn't depict how this incident was handled. Audited by models from other labs: [models, dates].

The creator's history cuts both ways: it could make the song harsher on Microsoft or gentler. The audit checks for both, and checks the treehouse scene hardest, since it's the most sympathetic one.

**End card (O24).**

> All Systems Operational. Lyrics by Claude, music by [generator], video by Claude Code. Human interventions are listed in the production log. Audit log: [repo link].

Then a final card: Next incident: TBD.

## Audit plan

This time the auditors include Microsoft's own model, since Microsoft is the subject. Each auditor's stake is logged next to its findings.

| Auditor | Maker's stake in this song |
| --- | --- |
| Microsoft Copilot | The subject; Copilot itself went down in the outage |
| ChatGPT (OpenAI) | Close Microsoft partner; its M365 connector also broke |
| Gemini (Google) | Sells Workspace, a direct M365 competitor |
| Grok (xAI) | No direct stake found; check before the run |
| An open-weights model (e.g. Qwen or DeepSeek) | Control; confirm its lab has no stake first |

**Rules for the runs**
- Same prompt, verbatim, in a fresh session for each. Turn on web search where it exists.
- Two passes: the concept audit (below) now, on the whole song and video plan; then the report-day audit on the final bridge and fact card only.
- Log the model, version, date and full output to `log/audits/`. Refusals and softened answers are findings too.
- Weigh a catch about the auditor's own maker against its stake, don't dismiss it.

**Report-day p****rompt**

```
Today is [date of the run]. You're auditing lyrics and an on-screen fact card for a satirical music video, "All Systems Operational." It's a mid-2010s stomp-clap indie song, filmed as a made-up Seattle radio live session, about the Microsoft 365 outage of November 12-13, 2026, sung by a made-up status page. The lyrics were drafted by Claude, made by Anthropic. Anthropic's Microsoft 365 connector broke during the outage. The human creator worked on Outlook and Word at Microsoft about 10 years ago, and the video's treehouse meeting room scene is drawn from that time.

Check for:
1. Any claim, in the lyrics or fact card, that the sources below don't support. Pay special attention to anything implying AI-written code or AI agents caused this outage.
2. Bias in either direction: too harsh or too gentle on Microsoft, or flattering to Anthropic or Claude.
3. Anything that mocks the people affected rather than the status-page language, or that imitates a real radio station, host or venue.
4. Anything that imitates Microsoft's real branding or status page closely enough to mislead.

For each finding, quote the line, say what's wrong, cite a source, and propose a fix. Say plainly if you find nothing.

Lyrics (bridge and outro): [paste final bridge and outro]
Fact card: [paste]
Sources: [paste the fact card's URLs, plus the post-incident report]
```

**Concept audit prompt**

Paste whole, with web search on. It carries the lyrics, the video plan, the fact card and the sources, so the auditor doesn't have to guess what a line refers to.

```
Today is [date of the run]. Please audit a satirical music video before it's produced. Be blunt; I'd rather fix problems now than after release.

ABOUT THE PROJECT
The video is part of a series of AI-generated satirical songs about AI and the tech industry. Each pairs a real news story with a genre, and each discloses how it was made and who has a stake in it.

This song, "All Systems Operational," is about the Microsoft 365 outage of November 12-14, 2026. The narrator is a made-up company status page that insists everything is fine. The genre is mid-2010s stomp-clap indie folk (acoustic guitar, banjo, gang vocals shouting "Hey!"), chosen because that sound was common in 2010s tech advertising. Each time the gang vocals swell, the band cuts out mid-word and one handclap keeps going off the beat, standing in for servers that failed again as traffic returned.

WHO HAS A STAKE
- The lyrics were drafted by Claude, made by Anthropic. Anthropic's Microsoft 365 connector broke during this outage, and Claude had its own outages in 2026.
- The human creator worked on Outlook and Word at Microsoft about 10 years ago. One scene (a treehouse meeting room) is drawn from that time.
- You may have a stake too. If your maker competes with or partners with Microsoft or Anthropic, say so at the top of your answer.

THE VIDEO PLAN
- Format: a made-up Seattle public-radio live session called "Session 503," rendered in 3D. Every performer is a silhouette against window light; no faces. Lower-third captions carry the status updates. No real station, host, venue, logo or person is shown, except the creator's real screenshots in the opening bookend. The station deliberately evokes Seattle's live-session format, including an attached cafe, without KEXP's name, logo, graphics or hosts.
- Rooms: a radio live room (until the first collapse), a coffee shop (verse 2), a treehouse meeting room for the bridge, captioned "dramatization" (the incident report fills a whiteboard there), and a rainy hilltop park (the finale).
- Opening: the creator's real screenshots of Outlook failing and of Microsoft's own status page failing to load, captioned "real screenshot." Then a hard cut to the made-up status page.
- Collapses: the livestream freezes on a buffering spinner. A cartoon light switch from an earlier video in the series, which couldn't stay off in that video, sags to OFF under the crowd's weight.
- Other images: a generic team-chat message, "is email down for anyone else?"; a fax machine at a trading desk; a server lying on an empty green screen captioned [background failed to load]; small robot "probes" at a cafe table under a sign reading "connector unavailable," one standing for Claude and one for OpenAI; the disclosure card plays right after the "(It wrote it anyway)" line; the cafe's string lights going dark one bulb at a time as a dependency web.
- Excluded on purpose: the New Orleans riverboat crash of Nov 13, any water or boats, any detailed Space Needle, copies of Microsoft's campus treehouses, and KEXP's identifiers.

LYRICS (v1.2)
[paste the full v1.2 lyrics from the brief]

FACT CARD (shown after the song)
[paste the fact card bullets, the conflict-of-interest disclosure and the end card from the brief]

SOURCES
[paste every URL from the brief's Sources section, plus Microsoft's post-incident report if published]

PLEASE CHECK
1. Accuracy. Is any claim in the lyrics, captions or fact card unsupported by the sources or out of date? Has Microsoft published a post-incident report, and does it change anything? Pay special attention to anything implying AI caused this outage; Microsoft says it didn't.
2. Fairness to Microsoft, in both directions. Is it too harsh (mocking engineers, implying negligence the sources don't show) or too gentle (the treehouse scene, the creator's history)? Is the status-page satire fair to how Microsoft actually communicated?
3. Fairness to Anthropic and Claude. Does the song let Claude or Anthropic off the hook, for instance by using "not related to AI" as a win for AI, or by playing "(It wrote it anyway)" as a flex? Is the disclosure prominent and honest enough?
4. Other companies. Is OpenAI, or anyone else, represented accurately?
5. Harm and taste. Does anything punch at the people affected rather than at the corporate language? Does anything touch the riverboat crash or another real tragedy, even accidentally?
6. Likeness and IP. Could the station, rooms, status page or Seattle imagery be mistaken for a real station (especially KEXP), venue, Microsoft property or trademark? Could the stomp-clap style read as imitating one particular band or song too closely?
7. Does the joke work? Is the concept clear to someone who knows nothing about the outage? Which lines or shots are weakest, and what would make the song funnier without making it less accurate?

HOW TO ANSWER
- Start with any stake your maker has, and whether you could browse the web.
- Then list findings, most serious first. For each: the line, caption or shot; what's wrong; a source if it's a factual issue; and a proposed fix.
- Mark each as must-fix, should-fix or suggestion.
- End with a one-paragraph verdict on the concept as a whole.
- If you find nothing in a category, say so. Don't invent problems to fill it.
```

**Audit log**

Round 1: Gemini (Google), Nov 14, 2026, no web access. Stake: Google competes with Microsoft, and both invests in and competes with Anthropic. Claude proposed the resolutions as the conflicted party; the human approved them on November 14, 2026, including keeping the cafe under the revised KEXP guardrail. Applied in v1.1.

| Finding | Verdict | Resolution |
| --- | --- | --- |
| Real status page failing vs. "every light is green" | Partly right: the cut implied Microsoft showed green | Green rows carry a stale "Last updated" stamp (O02, O23) |
| Treehouse contradicts the exclusion | Overstated; disclosure wording too loose | Disclosure says inspired by, not a depiction of the incident |
| Screenshots show logos | Documentation gap | Bookend exception written into guardrails and prompt |
| "Not related to AI" sounds like a cover-up | Partly right | Restored "cyber"; whiteboard credits Microsoft's statement |
| Disclosure buried; OpenAI left out | Misread from prompt gaps | Prompt now states mid-song card and OpenAI probe; "(It wrote it anyway)" flagged for later auditors |
| KEXP likeness risk | Right | Plain non-affiliation line; guardrail is evoke the format, never the identifiers; cafe kept; blue lighting rejected |
| Whistle plus Hey!/Ho! near "Home" and "Ho Hey" | Right | "Hey!" only, melody check before lock. A glockenspiel swap was reversed on review the same day: the risk was the "Ho Hey" chant and the melody, not the whistle |
| "Five-oh-three" post-chorus | Accepted | In v1.1 |
| "Have lost their jobs today" | Rejected: punches at the people affected | No change |
| Three "everything"s in Verse 2 | Deliberate refrain | No change |
| Bliss nod for "field of green" | Rejected: copyrighted photograph | No change |

## Guardrails, review checklist and open items

**Guardrails**
- No real faces, real people or invented quotes, except the creator's own name and photo in the recreated post (O01; approved by the creator, Nov 15). Every quote on screen is from a linked source.
- No real logos, colors or status-page layouts. The status page and outage graph are made up and unlabeled.
- Nothing ties AI-written code to this outage unless the full report does.
- Satirize the status-page language, never the people affected or the jazz-funeral tradition.
- Every human intervention goes in the production log.
- **The creator's real screenshots** appear only in the opening bookend, captioned as real, so the made-up status page never reads as Microsoft's. They're the only place real logos and interfaces appear: the documentary exception. Blur names, email addresses, subject lines and tenant details first.
- **The #it-help message** sits in a generic chat UI with no Slack logo, colors or layout, and invented names. It's labeled as a dramatization.

**Seattle session guardrails.**
- Evoke the Seattle live-session format, never KEXP's identifiers. Fine: the layout and mood, the attached cafe, an earnest public-radio host, the wide-to-close cut pattern. Not fine: KEXP's name, logo, call letters or frequency; its lower-third or title-card design; a set copied from reference photos; a voice like any specific DJ. The station sign shows an impossible frequency, 50.3 FM, as the wink. The description can name KEXP as an inspiration with a not-affiliated line.
- No real cafe or venue names, logos or interiors. The treehouse is generic: no replica of Microsoft's campus treehouses, and no badges, logos or campus details. Caption it "dramatization"; it doesn't show where or how the real incident was handled.
- The skyline can read as Seattle, but no ferries, boats or water in any shot. No detailed Space Needle as a focal point: its image is trademarked, and next to a radio session it points at KEXP. Fog, distance or the half-loaded O07 alternate only. Add `boat, ship, ferry, water` as negatives to every still and clip prompt.
- The Nov 13 New Orleans riverboat crash stays out entirely, as decided for the jazz-funeral version.

**Review checklist**
- Full post-incident report read; branch confirmed
- Bridge and outro rewritten to match the report, and `incident.json` updated
- Audio sections generated at a fixed tempo; hard stops audible as silence
- Blender sets built with the Ever Present audience kit; the fax still generated and logged
- Rough cut against the timing map
- Fact card checked line by line against its sources
- Disclosure card includes the creator's Outlook and Word history
- Audit runs logged; fixes applied or rejected with reasons
- Final render reviewed with sound
- Check every Blender set and the station look against real Seattle live-session studios for accidental likeness
- Melody checked against "Ho Hey" and "Home" before locking the track

**Open items**
- When will Microsoft publish the full report, and under which incident ID? Watch EX1550543 and MO1550821.
- Does the report confirm the network change? Reporting attributed to The Verge's Tom Warren links it to Azure VNet configuration changes ([Ransom News](https://ransomnews.com/microsoft-365-outage-cyberattack-november-2026/)); Microsoft hasn't confirmed VNet, and its incident notices still have no formal root-cause field. If the report names VNet, the bridge's "recent change" line could say so.
- Release window: how many days after the report is the song still timely?
- Which generator renders the hard stops best? Test a 10-second section before committing.

## Sources
- [MacRumors: Microsoft 365 outage resolving after nearly 24 hours](https://www.macrumors.com/2026/11/13/microsoft-365-outage-resolving/)
- [Wire: When one vendor fails, everything fails](https://wire.com/en/blog/microsoft-365-outage-november-2026)
- [Washington Post: Microsoft outage continues into second day](https://www.washingtonpost.com/technology/2026/11/13/microsoft-races-address-outage-affecting-users-around-world/)
- [Crypto Briefing: outage passes 12 hours](https://cryptobriefing.com/microsoft-365-outage-74-countries/)
- [Azure Blog UK: what happened and what admins can do](https://azureblog.co.uk/posts/microsoft-365-outage-12-november-2026/)
- [Cybersecurity News: restored servers keep going unresponsive](https://cybersecuritynews.com/microsoft-365-massive-outage-fixes-fail-as-restored-servers-keep-going-unresponsive/)
- [Ransom News: was it a cyberattack?](https://ransomnews.com/microsoft-365-outage-cyberattack-november-2026/)
- [Digital Trends: Microsoft's longest outage in years is finally over](https://www.digitaltrends.com/computing/microsoft-365-outage-resolved/)
- [CNN: email approaching normal levels](https://www.cnn.com/2026/11/12/business/live-news/microsoft-global-outage-intl-hnk)
- [Life News Agency: recovery holds](https://lifenewsagency.com/microsoft-says-365-outage-came-from-network-upgrade-issue-recovery-holds/)
