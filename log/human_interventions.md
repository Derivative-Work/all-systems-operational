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
