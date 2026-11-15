# Decisions

Append-only. Deviations from the brief, each with why and who decided.

## 1. 2026-11-15 — Suno style prompt rewritten (logged; human's choice at generation time)

- The prompt used differs from the brief's v1.2 (`log/prompts/m1_suno.md`): the mood words "bittersweet, wistful, nostalgic" are gone and a vocal direction is added. Whether the nostalgia layer survived is for the M1 listen ("Remember Wednesday" outro over the minor iv).

## 2. 2026-11-15 — Folder layout and vendored kits

- Ever Present's layout (`audio/ timing/ assets/ blender/ remotion/ renders/ review/ edit/ log/ archive/ docs/ lyrics/ config/ scripts/`).
- Kits are copied in, not linked, so the sibling projects stay untouched: Ever Present's people and band kit in `blender/ep/` with `assets/figures/` and `assets/mpfb/` (see `blender/ep/README.md`); the Sandbox Rhapsody probe kit in `blender/lib/` (one path line changed, `blender/lib/README.md`); the Little Switch rig in `remotion/src/defaultOn/`, copied unchanged from The Distillation Job's unchanged copy of Default On (its README gives the upstream commit).
- The Ever Present material stays off public remotes unless the human says otherwise (CLAUDE.md).

## 3. 2026-11-15 — Probe colours

- The brief asks to confirm amber isn't already assigned to another lab. In Sandbox Rhapsody amber (`#ffa21f`) was the agents' colour, and those agents were OpenAI's; Not Yet made its probe green (`#5fe39a`) to set it apart. So green for Anthropic and amber for OpenAI matches the series. Agent's finding; for the human to confirm at M3.

## 4. 2026-11-15 — The lone clap stays where the human put it (agent's proposal, for the human to confirm)

- The brief's edit notes ask for one clap "nudged late" after each hard stop. The human's clap track keeps a steady clap every two beats (94.39, 95.59, 96.79, 98.00 s) through stop 1, and there is none in stop 2.
- Proposal: keep both. A clap on a fixed interval while everything else is stopped is what a retry loop sounds like; the lateness goes in the picture instead (O12: the frame is frozen and one silhouette's clap still animates, on the beat but out of step with a frozen crowd). Stop 2 with no clap is the retries giving up, which suits "Incident reopened" and the end.

## 5. 2026-11-15 — Licence (human)

- Like the rest of the series: MIT for the repository (`LICENSE`, copied from The Distillation Job), Creative Commons for the video (`LICENSE-media.md` to come, modelled on The Distillation Job's CC BY-NC-SA 4.0 unless the human says otherwise).
- Conflict: the Ever Present kit (decisions 2) is all rights reserved and private. Open for the human: relicense the generic people and band kit here, or keep it out of the public repository.

## 6. 2026-11-15 — M2 shot cues: choices for the human to rule on (agent)

- **Bookend lead-in 8.4 s:** spike 2.4, real screenshots 2.4 (cap 3), chat post 3.6; 14 beats of 18 frames. The click on play is the cut to O02 at song time 0, then 1.09 s of silence before the whistle. Remotion's placeholder is 8.2 s.
- **O02/O03:** O03 starts on the downbeat before "We're investigating" (7.26 s), so the row flips to "Investigating" a bar earlier, in O02 (4.85 s). O03 then holds the soft vocal and the stomp-clap instrumental to verse 1 (19.2 s).
- **O04–O07:** one sung line each, cut on the line's downbeat. O07's downbeat falls on "-where", so "Some-" is heard over the fax.
- **O08:** cut on beat 3 as "green" ends (44.52 s), since the call starts mid-bar. The optional treehouse cutaway and IT's reply both sit on the first echo (46.02 s).
- **O09 and O17** each hold their chorus and the "Five-oh-three" post-chorus (about 29 s); the shot list has no separate post-chorus shot. A mark at "Five-oh-three" shows where a second angle fits.
- **O10** is one bar (2.39 s).
- **O12/O13:** the freeze lands on the band's cut at 93.80 s. O13's card comes in on the third clap (96.79 s), 0.43 s before "We're seeing renewed errors", and holds 1.8 s.
- **O14** starts when the band comes back (98.62 s, two bars before "The agents"), so the cafe arrives with the band, not with the verse.
- **O21/O22:** the stop-2 freeze is the 1.39 s of silence; Switch drops one beat in (202.42 s); O22 starts on the whistle's first sound (203.19 s).
- **O23** starts on "operational?" (234.20 s), as the shot list says, 4.8 s after "All systems", and runs to the end of the music. O22 is 31 s.
- **After the music:** O24 = end card 6 s + "Next incident: TBD" 3 s, then the fact card 15 s ("after O24" in the brief). The Remotion end sequence runs disclosure, fact card, end card, final card instead.

## 7. 2026-11-15 — The disclosure is an overlay on O17, not a card between O16 and O17 (agent's proposal)

- The brief places the disclosure "after O16" (O15: "Disclosure card follows"). Between O16 and O17 there's no gap in the song, and its 77 words need about 25 s. A full-frame card there would stop the chorus.
- Proposal: a panel over O17's chorus, from its first downbeat to "Five-oh-three" (122.65–140.65 s, 18 s), and full length in the end sequence and the description. `config/shot_cues.json` `overlays`.

## 8. 2026-11-15 — O04's +1 count climbs once (agent)

- The brief says the +1 count "climbs on each Hey!", but O04 holds only verse 1's first line, so only one Hey! (30.64 s) falls in it. The other two land in O05 (35.44 s) and O06 (39.98 s). Options: one climb in O04; a notification badge on O05's phone; or O04 holding two lines. Cues keep one climb.

## 9. 2026-11-15 — O17's "Ho!s" read as the Hey!s (agent)

- O17 has mugs raised "on the Ho!s", but since v1.1 the only shout is "Hey!". The mug raises are cued on chorus 2's four Hey!s (124.69, 126.86, 129.24, 131.60 s).
