# Human interventions

Append-only. Every human action: when, what, and why.

## 1. 2026-11-13 to 2026-11-15 (logged retroactively) — Planning chat and brief

- **What:** The human asked about SaaS reliability and the M365 outage (2026-11-13), asked how it could fit the series given the overlap with LGTM, asked for genres and a jazz-funeral draft, and for shots and a rapid-response rendering plan to wait for the incident report. They asked for the disclosure to include their Outlook and Word work at Microsoft, had the brief made (2026-11-14), and proposed the Bliss nod, the Not Yet/Sandbox Rhapsody probes and the real screenshots. They had the New Orleans riverboat crash left out, chose a silent Little Switch, compared drafts, then dropped the jazz funeral ("I cannot get a singer that reads as someone who should be singing this genre, and the topic doesn't have a hook that justifies the appropriation") and the EDM ("far too close to the rest of the creators in this space") for a mid-2010s "hey-ho" indie song. They set the look (a Seattle KEXP-like live session, coffee shop, outdoor session; a treehouse meeting room "as I often met in at Microsoft"), asked that rooms be rendered with Ever Present's audience kit, ran audit round 1 in Gemini and ruled on it, and asked for more nostalgia (v1.2, 2026-11-15).
- **Evidence:** `docs/planning_chat/` (66 messages, indices 0–71; 4–5, 20–21 and 42–43 are on abandoned branches and not in the share; snapshot taken 2026-11-15T09:28:56Z); the brief, rev 106.

## 2. 2026-11-15T01:49:19Z (Suno's created_at; logged retroactively) — Suno take

- **What:** The human generated the song in Suno and chose this take.
- **Take:** clip `e7994418-9310-4096-8663-99aa58d5fc76`, shared as https://suno.com/s/YPILkHDbsibStgNf, title on Suno "Remember Wednesday". Model v6 (`chirp-hawk`), 236.8 s, task `gen`, max mode, sliders `style_weight 0.8`, `aug_creativity 3`. Rejected takes aren't visible from the share page.
- **Style prompt:** a rewrite of the brief's v1.2 prompt (`log/prompts/m1_suno.md`). The record doesn't say who rewrote it.
- **Lyrics:** `lyrics/as_pasted.txt`: the brief's v1.2 lyrics verbatim, without the two "SWAP POINT" markers.
- **Why:** The agent has no access to Suno.

## 3. 2026-11-15 03:27–03:45 local (file times; logged retroactively) — Logic edit, master, post-filter, stems

- **What:** In Apple Logic Pro the human took Suno's stems, added the hard stops and mastered the song (`~/Downloads/All Systems Operational.wav`, 03:27, 239.58 s, 2.78 s longer than the take). They added a separate handclap track, Logic's "Clap 2 - Warm Embers" (exported 03:45, 98.3 s). Then they ran the post-filter (from the shell history):
  `uv run python -m postfilter.infer --in ~/Downloads/All\ Systems\ Operational.wav --out ~/Downloads/all-systems-operational-master-deslopped.wav --ckpt ../music-deslop-data/release/m6f_10k.safetensors --source suno`
  music-deslop is at `68441e2` with a clean tree now; that it was the same at run time is assumed. The 12 stems in `~/Downloads/All Systems Operational/` were exported from Logic at 03:45 and carry the edits.
- **Status:** not yet locked (M1).

## 4. 2026-11-15 03:57–04:19 local (file times) — Real screenshots

- **What:** `~/Downloads/all-systems-operational-shots/`: Microsoft's service status page blank (`status-page-broken.png`) and loaded with "Service degradation" (`status-page-working.png`), the "No license found" error (`m365-license-failed-outage.png`), six redacted Slack screenshots of the #it-self-help channel (`slack-1`…`slack-6.png`) and a 15.9 s screen recording of the earlier jazz-funeral revision playing in that channel (`slack-5a.mov`).
- **Use (human):** the Slack shots are "for text style reference only", except that one "could be a good bookend as it shows an earlier revision of this song in the #it-self-help channel".

## 5. 2026-11-15 — Production started

- **What:** "Let's get started with the brief … The planning chat, which you'll also need to archive … The previous projects are in the parent directory -- you can look but don't touch. In particular, pay attention to Ever Present (band and audience kits), Sandbox Rhapsody (probe kit), Default On (switch kit). The song, including master and stems, are in ~/Downloads. I generated it in Suno …, got their stems, then added the hard stops and mastered in Apple Logic Pro, then ran the postfilter. … Just plan and import for now: don't start any large renders or generations as Ever Present is still rendering."

## 6. 2026-11-15 — Answers to the M0 questions

- **Lone clap:** "I couldn't figure out how to properly time these, so this is what made sense musically based solely on the text. How do these flow into the scenes?" (agent's reading in decisions 4, open).
- **Bookend:** "I'm good with my photo being here (it's also the same one as my GitHub photo that goes on the repository). The video could be better suited as an opening bookend: make it accurate to this song, and then cross out the "no video yet" before clicking play." Brief rev 113.
- **"No license found" capture:** "I will get permission for that capture or create my own. Use it for now as a placeholder if it works conceptually."
- **Outage-report spike:** "See about finding the outage report spike online -- I don't have one for you" (production log 4).
- **Licence:** "This one will be like the rest of the series (CC video, MIT repo)" (decisions 5).
- **Transcription:** "Hold off on the transcription for now."

## 7. 2026-11-15 — Clap, bookend post, capture date, spike, licence

- **Clap:** "That explains why it fit musically when I put it in that way, so I won't change it for this." Decisions 4 approved: the clap stays on the beat, stop 2 has none.
- **Bookend post:** "keep the "meme" bit, but animate crossing it out for self-awareness". The post describes this song (agent's draft accepted without changes: "“All Systems Operational” — a singalong for the M365 services, as a mid-2010s stomp-clap song", player at 3:59). "(my last meme about this, I promise)" and "no video yet" are struck through in turn before play. Brief rev 116.
- **"No license found" capture:** "it was on Friday" (Nov 13).
- **Spike chart from reported counts:** "works for me".
- **Licence:** "yes, relicense": the generic Ever Present people and band kit (`blender/ep/`) is MIT in this repository; Ever Present stays private. Decisions 5 closed.

## 8. 2026-11-15 — M3 board approved; stop 1 heard as "fai—"

- **Board:** "The board is good." M3 grey-box gate passed (production log 8, `review/m3_board.jpg`).
- **Pose note:** "I see a people with hands held to their heads as if confused, but I'm assuming that will be fixed with the figure library." Most likely the face-height claps of `push` and `clap_open` (O11, O12c, O17). Taken as a pose fix for the figure-library rebuild: claps at chest height, hands never resting at the head.
- **Stop 1:** "By ear, it is cut at "fai--"." Overrides the agent's reading in AI changes 2 (AI changes 3). No re-cut needed; the brief stands as written.

## 9. 2026-11-15 — M2 cues approved

- **What:** "These all make sense to me, keep going." M2 gate passed: `config/shot_cues.json` as committed in cead0e1, with every call in decisions 6–9 accepted as proposed (8.4 s bookend; disclosure as an overlay on O17's chorus plus the full card at the end; O09/O17 holding their post-choruses; O23 on "operational?"; O13 at 1.8 s; the end order and the smaller calls as logged). Next: M4.

## 10. 2026-11-15 — GPU freed; memory setting

- **GPU:** "I've paused work on Ever Present, so the GPU is all yours until this is done."
- **Memory:** the human realised this session was started without their memory environment variable, so generations might fail. The M4 batch did stop on low RAM (production log 10); the agent is to be restarted with the variable before the rest of M4 runs.

## 11. 2026-11-15 — Restarted with the memory setting; fax take picked

- **Restart:** the session was restarted with `CLAUDE_CODE_DISABLE_BG_SHELL_PRESSURE_REAP` set, so background jobs aren't killed under memory pressure.
- **Pick:** "a_s45 is good. Keep going." O06 uses `O06_fax_a_s45` (the agent's first pick). Next: image-to-video of that still.

## 12. 2026-11-15 — M4 takes picked

- **What:** "Go with your recommendations. I'll review the field of green shot in context once we have it." O06 is `O06_s41` kept as a slow push (no counter-crop). O07 stays the server on green, with `O07_fogtower_s44` (the tower on the lawn) as the spare; the human will judge O07 in the animatic. M4 gate passed; next: M5.

## 13. 2026-11-15 — Animatic: needs more motion and cuts

- **What:** "What's the plan for adding motion and interest to these while fleshing out the models? Without more cuts it's going to be slow and dry if it doesn't read as musical." The agent proposed coverage, stem-driven performance and music-cued camera and light (decisions 12); the human: "Yes go ahead." The M5 staging calls (decisions 11) and the 290 s length are still open for the human.

## 14. 2026-11-15 — M5b reviewed; go ahead with M5c

- **What:** after the M5b animatic (94 shots), the human: "yes go ahead with the figure-library rebuild". Taken as approval of the M5b rhythm and coverage; the M5 staging calls (decisions 11), the 290 s length and the M5b calls (decisions 13–14) are not yet ruled on. The agent noted for later: the SESSION 503 kick-head close repeats about eight times and the tambourine close four.

## 15. 2026-11-15 — M5c review: guitar, wrists, clipping

- **What:** "For the guitar (and parts shared with the banjo, likely the neck etc.), check Ever Present again. Its guitar has been updated since you imported it. The hand positions are a bit awkward: when clapping, people look like they have broken wrists; and it's clipping through the instruments."
- **Agent's check:** the vendored `blender/ep/stage_props.py` is from 726343c, Ever Present's guitar rebuild (its production log 96: 648 mm scale, 43–56 mm neck, 22 true-spaced frets, nut, generic 3+3 headstock), and is unchanged since. But M3 built this video's acoustic guitar and banjo from scratch in `blender/aso_props.py` and never used that neck, so the instruments here have the old problems (bare neck, wrong scale). Next: rebuild both instruments on Ever Present's neck, fix the wrists and the clipping.

## 16. 2026-11-15 — M5c2 review; disclosure wording and placement

- **What:** "The strumming arms are all angled out the wrong way -- they should be resting downwards rather than coming from the top. Getting this right for the guitarist was previously difficult because the guitar is comically large for that guitarist. Maybe use a different player rather than trying to force a viable strum on this combination. The left hands on both the guitarist and banjo player are not wrapping the neck of the guitar. All of the clapping has the backs of the hands clapping, not the palms. Let's credit my experience as "The creator worked on Outlook and Word at Microsoft between 2014 and 2017...", and I think it's fine to just have it at the end rather than also having it pop up in the middle of the song."
- **Also asked:** when the grey-box geometry is supposed to be gone.
- **Applied now:** brief rev 116 → 121 (the disclosure, the two audit-prompt mentions and the format note say "between 2014 and 2017"; the disclosure plays at the end, after the fact card); mirror updated by the same edits; `remotion/src/components/Cards.tsx` DISCLOSURE; CLAUDE.md. Decisions 7's O17 overlay is withdrawn (decisions 18).

## 17. 2026-11-16 — M5c3 reviewed; go ahead with the look pass

- **What:** after the M5c3 animatic, instrument sheet and performance sheet: "Better, try the look pass". Taken as approval of the M5c3 performance pass (recast 3 → 33 and 8 → 36, arms down, fretting grips, palm-to-palm claps, disclosure at the end only) as a base for the look work.
- **Not yet ruled on:** the calls in decisions 19–20 (the recast and the band no longer having an Asian member; the raised fretting and clap wrist limits; the banjo player's blurred face in O09g; O03d's opening crowd back), and the earlier open calls (decisions 11, 13–14, the 290 s length). They stand as proposed until the human rules.
- **Next:** a look board before the full M7 render: hero frames per set (live room, coffee shop, treehouse, hilltop park) with final materials, set dressing, haze and grade, for approval.

## 18. 2026-11-16 — M7a look board reviewed

- **What:** "Eevee is fine." On decisions 26:
  1. "Yes those are mostly fine as the base, though we could use some motion on the water droplets and make sure that the phone's Slack messages are readable when it is visible". The look per set is approved as the M7 base. The beaded drops on glass should move, and the O04 phone's chat (the brief's generic chat UI, which the human calls Slack) must be readable whenever it is on screen.
  2. "In addition to what you pointed out, the whole hilltop scene is off, not just what you pointed out, starting from the hill itself." The park is to be redone from the ground up, not just the firs and skyline.
  3. "Keep the light shafts".
  4. "Keep the near-black silhouettes".
  5. "Band only Polaroid".
  6. "Station sign is good as-is" (the 50.3 FM · listener-supported radio sign, checked for likeness to KEXP's 90.3).
- **Also accepted, from the agent's list:** the treehouse lift, O18e, the ⅓-stop lift on instrument closes, mug steam and haze drift go ahead. The roof and park-sun fixes (decisions 26.5) and the Eevee JPEG plan (26.6) were not objected to.
- **Asked:** whether any shots could be generated without losing much, especially ones with nothing composited (kick head, Switch); and whether anything is planned for the treehouse laptop and phone screens. The agent found nothing planned: they are blank emissive white.

## 19. 2026-11-16 — Generated plates for the park; what the treehouse screens show

- **Generated shots:** "Go with your recommendations". That means a generated far plate behind the Blender park, carrying the distant city in fog and the far tree lines. O22d (fog over the skyline) is that same plate, animated by image-to-video, so the skyline matches the O20 wides. Everything people touch stays rendered: the ground, the crest, the near firs, the lamp post with Switch, the umbrella. Every other shot stays rendered.
  - This deviates from the brief's "rendered, not generated" rule for the rooms. The agent logs it in decisions.
  - Takes with a real landmark, water, a face or a logo are rejected.
  - The park rebuild still waits for the human to pick a direction from the M7b concept stills.
- **Treehouse screens:** "Phones and laptops: let's lean in a bit more to how this plausibly could be playing out: someone struggling to 2FA in, someone with a robo-call from a fake number as a stand-in for a page looking at an invented dashboard, invented code and agent screens, the generic video call you mentioned".
  - Each laptop and phone gets invented, plausible incident-night content in place of blank white.
  - Guardrails for it (agent): generic UIs only, with no real product's logo, colours or layout. Names are invented. The caller ID is a fictional 555-01xx number. No phone at an ear, because of the pose rule that keeps hands 0.20 m from heads.
  - Nothing on any screen ties AI-written code to the outage. The agent screen shows an agent blocked or reading logs, never writing or shipping the fix.
  - The O08c and O18 shots stay captioned "dramatization".
- **Source of the screen ideas:** "(I don't have any inside information, these are just guesses)". The screen content is the creator's guess at a plausible incident night, not knowledge of how this incident was handled. That matches the disclosure ("it doesn't depict how this incident was handled").

## 20. 2026-11-16 — Brief rev 136: Microsoft's preliminary post-incident report; new master coming

- **What:** "re-read the brief -- it incorporates data from the preliminary PIR from yesterday. I will repaint the song and get you a new master and stems later today (non-vocal parts within changed sections and everything outside of the changed sections should be unaffected)."
- **The human's brief edits (rev 121 → 136), mirrored into `docs/brief.md`:**
  - **Lyrics v1.3:** the bridge is rewritten from Microsoft's preliminary report (Nov 15) and grows from 9 lines to 12. "An earlier upgrade / Met a recent change" becomes "A fix from back in July / Tested on the smaller machines". Contributing factors gain "Teams came over for the night / An unrelated issue / And a separate issue". "To follow" becomes "On the twentieth". Both swap points stay open until the final report, due Nov 20.
  - **O02/O23 stamp:** "Last updated: Thu 11:15 a.m." (was 12:58 p.m.).
  - **O18:** the whiteboard paraphrases the report, quoting a few words at most. On "(Not related to cyber, AI or agents)" an on-screen tag pins to that line, in the status lower-thirds' style: "Microsoft, Nov 13, the day before its root-cause report." A beat later: "The report doesn't say who or what wrote the July fix."
  - **Branch A:** no config diff any more. O18 shows the July fix circled at the top of the whiteboard instead.
  - **`incident.json`:** new rootCause, three contributingFactors and a new `denialTag` field; `config/incident.json` updated to match.
  - **Fact card:** Exchange problems from 11:20 a.m. ET Thursday (per the report); the report's three factors; impact ended Fri Nov 13 at 11:10 a.m. ET; Nov 13's denial placed the day before the report.
  - **Guardrail:** the report carries a no-reproduction notice, so quote a few words at most and never show its pages.
  - **Sources:** the preliminary report (EX1550543/MO1550821, copy supplied by the creator) and The Register (Nov 16).
- **Audio:** the human will repaint the changed sections in Suno and supply a new master and stems later today. Outside the changed sections, and the non-vocal parts inside them, should be unchanged, so the cut and every non-bridge cue should hold. M1's lock and the bridge's vocal timings (the O18 whiteboard cues) wait for it.

## 21. 2026-11-16 — Report date confirmed; brief fixed

- **What:** "Report is dated the 15th. Fix the brief". The agent edited the brief (rev 136 → 141):
  - the O18 tag and `incident.json`'s denialTag now read "Microsoft, Nov 13, two days before its root-cause report.";
  - the fact-card bullet reads "That came two days before its preliminary report";
  - the concept-audit prompt reads "November 12-13" (was 12-14) and "LYRICS (v1.3)".
- **Updated to match:** the mirror `docs/brief.md`, `config/incident.json` and CLAUDE.md (outage of November 12–13).
- **Not edited, flagged for the human:**
  - the Overview's "The turn" still frames the bridge as singing back Nov 13's "earlier network capacity upgrade" line, while v1.3 now sings the July fix;
  - the concept-audit prompt's SOURCES line still says to paste "Microsoft's post-incident report if published", but the report carries a no-reproduction notice.

## 22. 2026-11-16 — M7b reviewed: screens, O04 framing, park direction

- **What:** on the M7b look board, screens sheet, park concepts and motion test:
  1. "Treehouse is good as suggested". The screen content is approved with the assistant's name dropped: "Kestrel" is Microsoft's ASP.NET Core web server, so the screen will read "assistant · read-only". Seat 1's phone keeps the #it-help thread.
  2. "Framing is good as suggested". O04a keeps the close phone framing without the band, and the question is on screen from the start of the shot.
  3. "Park suggestions are good". The hill is rebuilt in the direction of concepts 1–2 (park_crest_s41 and park_crest_b_s42): a lawn running to a brow, the ground falling away, roofs and bare trees below, and the city 2–4 km off in the cloud. Far plate 1 (plate_city_s42) goes behind it, with plates 2–3 (plate_ridges_s41/s42) as the far tree lines.
  4. "Yes, leave the cut alone". No insert for the ringing phone's caller ID or the timeout message.
- **Also accepted as proposed:** the M7b look as the base for the full M7 render (decisions 34).

## 23. 2026-11-16 — M7c approved; one more pass on the known weak points

- **What:** on the M7c park board, plates sheet, motion test and fixes sheet: "These are great, keep going on what you already recognize as weak".
- **Approved:** the M7c park as the M7 park, with decisions 39's recommendations: the camera changes (decisions 36), the extended far plate with the sky evened across its seams, O22d as the generated LTX-2.3 take s41, the stray O22a figure removed in the M7 path, Switch 12.5 cm lower, and the crowd phones' content. Not chosen separately: the 2.4 m option for the eye-level wides, which belongs to the weak point below.
- **Next (M7d), the weak points already flagged to the human:**
  1. the firs shade flat up close (clustered cards);
  2. at the L1 seam of the far plate, about 22° left of centre, a hill fades into a vertical bank of fog;
  3. the bare trees at the brow are dark and dense from O20e;
  4. O08c's night window panes show pale, flat shapes behind the forest (decisions 39.8);
  5. the eye-level wides show the drop mostly as air and distance rather than visible slope;
  6. from the M7b report: the guitar close is still dark and the banjo close sees the instrument edge-on.
- Approved looks stay as they are outside these points. The whiteboard, tags, stamp, fact card and audio still wait for the new master.

## 24. 2026-11-16 — The v1.3 master and the bridge repaint

- **What:** "new master is in "~/Downloads/All Systems Operational.wav", and the stem of the repaint is in "~/Downloads/All Systems Operational/0a Lead Vocals repaint.aif". I haven't run the postfilter on the master yet; you'll have to do that".
- **Files** (file times 13:12):
  - The v1.3 Logic master, with the bridge repainted in Suno to lyrics v1.3.
  - The repainted lead vocal, exported from Logic.
  - The other 12 stems and the clap track in the same folder are the Nov 15 exports, unchanged.
- **Post-filter:** run by the agent this time, with the command the human used for v1.2 (human interventions 3).

## 25. 2026-11-16 — M7d approved; the end cards go over an instrumental; the v1.3 master sent for review

- **What:** on the M7d board, wides options, plates and motion test, and the M1b report: "Much better, keep going. I have an instrumental track for you to put in the credits and end cards so don't worry about length, just make it readable. Send me the audio here so I can review it".
- **Approved:** the M7d pass as the M7 look, with decisions 43's recommendations: the firs' overcast term kept; the crowd wides (O20a, O21a, and O20j) at 1.8 m with the drop cues; the empty wides (O22a, O22f) raised to 2.4 m with the cues (the lamp's lantern enters the top of the frame); the banjo closes re-aimed; the guitar spot; the brow path kept. "Keep going" also starts the full M7 render, which the last report named as the next step. The bridge cut (the denial tags landing 9 frames into O18c) is kept as recommended.
- **End cards:** the human has an instrumental track for the credits and end cards (not yet supplied; nothing new in `~/Downloads` at 15:40). Length no longer limits them: the fact card's 15 s, which the M1b report flagged as too short for about 210 words, gives way to reading time, and the cards are to be laid out for reading.
- **Audio:** the human asked for the post-filtered v1.3 master to listen to before locking M1 (production log 58). Still open: locking M1 after that listen, and where bulkheads belong (the board lists them, the fact card doesn't).

## 26. 2026-11-16 — The credits instrumental

- **What:** "it's in ~/Downloads/All Systems Operational (credits EDM).wav -- you'll need to run the postfilter on it too".
- **File:** `~/Downloads/All Systems Operational (credits EDM).wav` (file time 17:07; 212.4 s, 16-bit 48 kHz stereo; sha256 `faf569d6…`), copied to `audio/credits/`. The human's instrumental for the credits and end cards (human interventions 25). How it was made isn't stated; the post-filter ran with `--source suno`, as for the master.
- **Post-filter:** run by the agent (production log 61).

## 27. 2026-11-16 — The credits track's sections asked for

- **What:** after the end-sequence preview: "send me the sections as you have them so I can review".
- **Sent** (production log 63): the section map, the track with a click on each change, and the changes as labels. The human is checking the agent's section changes by ear before the end sequence's timing is settled; decisions 45's options are still open.

## 28. 2026-11-16 — Repository created; push; prepare it for public

- **What:** "I created https://github.com/Derivative-Work/all-systems-operational and gave you access. Push up what you have, then prepare the repo (which will be public) like the others".
- **Repository:** private and empty when the push began. Pushing is allowed from here on; it was "never push" until now. The Ever Present material that isn't relicensed stays off it (CLAUDE.md); the relicensed kit in `blender/ep/` goes up.
- **Checked before the push** (all 89 commits, every path ever tracked): no keys or tokens, and no email addresses in tracked files. Every commit is by the human's GitHub address, the same as the other series repos. The creator's real screenshots, the Slack captures and the avatar crop are git-ignored and were never committed. Nothing from Microsoft's post-incident report beyond the brief's short quotes. One tracked image shows the placeholder "No license found" capture (human interventions 6): `review/m3_screens.jpg`, committed in 710f260, has it as one thumbnail (about 140 px wide, no names or addresses). For the human to settle before the repo goes public.
