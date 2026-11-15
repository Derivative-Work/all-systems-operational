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

## 10. 2026-11-15 — O06 clip is 1280×704 and not locked-off (agent)

- The plan says 1280×720. LTX-2.3 works in multiples of 32, so the template's output is 1280×704, as Ever Present's clips were. The still is cropped to 16:9 at the edit or scaled to fit; nothing important is near the top or bottom edge.
- The brief asks for a locked-off camera. All four takes push in (production log 11). The agent recommends s41, the gentlest. At the edit it can either be counter-cropped to hold still (framed as its last frame, about 12% softer) or kept as a slow push. The human decides at the gate.

## 11. 2026-11-15 — M5 animatic: how some shots are staged (agent; for the human at the M5 gate)

- **O08's inserts:** the brief puts IT's "we are aware" reply and the optional treehouse cutaway both on the first echo. Both are in: the framed phone with the reply lands on echo 1 (46.02 s) and holds to echo 2 (48.35 s), then the treehouse cutaway (night, "dramatization") holds 4 beats to 50.75 s, then back to the host. The lower-third echoes run over all three. Either insert can be dropped.
- **O19 in two parts:** the treehouse and the park are separate Blender sets, so the "one continuous camera move" is two moves cross-faded through the drizzle (10 frames): the door opens and the camera goes out onto the deck and up into the trees (5.8 s), then it rises over the hill's crest to the crowd (6.2 s). A single move needs both sets in one scene; that's M7 work.
- **O11's Switch:** Switch is on the wall by the door, out of O11's frame, so he strains in a small inset in the livestream overlay (bottom right), from the second Hey!.
- **O13:** the "We'll be right back" card holds to "errors" (97.75 s), then the status page with the row back to red, to the band's return.
- **O12 and O21 freezes:** everyone is a frozen copy of their pose; only the late clapper (O12), Switch and the ON AIR sign move. O12: the sign is lit for 3 frames, then dark as Switch drops. O21: Switch sags for one beat, then drops on 202.42 s.
- **O12's camera and clapper:** from the board's O12 wide the late clapper was too small to read, so O12 uses the board's close camera (O12c, same state; ON AIR, Switch and the 50.3 FM sign are still in frame). The clapper stands side-on to it, against a window (`clapper_at`/`clapper_face` in `blender/sets.py`, used only here), and opens wider between claps. M3's board is unchanged.
- **O21's camera** is O20's last frame. O20's push was shortened so the lamp post with Switch stays in frame through both.
- **O06:** the clip plays from its first frame at its own speed. Its curl is continuous, with no single page event to put on "fax", so nothing was shifted.
- **O07 alternate** (excerpt only): the fog-tower plate s44 with the void's server rack laid on the lawn as a cut-out, the tower's top half pixelated (the stalled block), a slow push, the same caption.
- **End sequence:** end card, "Next incident: TBD", fact card (as approved), then the full disclosure card (18 s, the overlay's length), which decisions 7 promised "full length in the end sequence" but the M2 post-roll left out. The animatic is 289.97 s, not 271.98. If approved, M7 adds it to `config/shot_cues.json` `post_roll`; or it can go before the fact card.
- **O22:** the park is empty from the start of the shot (the crowd is gone after the freeze); one walker goes up the path and over the crest.

## 12. 2026-11-15 — More coverage and motion before the final look (human asked; agent's plan, approved)

- **Why:** the M5 animatic holds one angle per O-shot, up to 19–31 s (O03, O09, O17, O18, O20, O22). The human: "Without more cuts it's going to be slow and dry if it doesn't read as musical."
- **Plan:** two new milestones before M7 (`docs/plan.md`). M5b: a music map from the stems, each O-shot split into wide/mid/close angles cut to bars and hits (the brief's wide-to-close live-session pattern), camera and light cued to the music, ambient motion, first-pass crowd motion; reviewed as a grey-box animatic. M5c: the figure-library rebuild with stem-driven performances. Shot IDs stay the scene IDs; angles are sub-shots (O09a, O09b…). No faces in any close: hands, feet, instruments, backs and backlit profiles only.
