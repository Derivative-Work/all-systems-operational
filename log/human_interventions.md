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
