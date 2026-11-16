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

## 13. 2026-11-15 — M5b coverage: calls for the human (agent)

- **Cut count:** 94 shots (93 cuts), in the 80–110 range the plan set. M5's single-shot pieces stay single: O01, O02, O04, O05, O06, O07, O10, O12, O13, O15, O21, O23 and the end cards. O15 holds 5.4 s on the probe so the LED's dim and return read in one angle.
- **O17i cuts on a word, not the grid:** the post-chorus cut is on the sung "Five-oh-three" (140.94 s, 0.29 s after beat 59.3, an 8th late like the Hey!s), not on a downbeat. The disclosure panel (to 140.65 s) is gone 9 frames before it.
- **The weak Hey! (56.24 s)** isn't used as a cut point. O09a runs to the downbeat at 57.75 s.
- **No backlit-profile close:** the brief allows backlit profiles, but at 540p the backing singer's profile showed a nose and mouth, so it was replaced by the guitar. Profiles come back only if the M5c figures are darker against the glass.
- **O21's angle is O20j's:** the last half bar of the final chorus cuts to the angle the freeze holds. In M5, O20 pushed into O21's framing.
- **O22's Switch is OFF:** in M5, the outro's lamp post showed Switch ON after he dropped in O21. M5b keeps him OFF (AI changes 4).
- **Stop 2's warning:** the park has no ON AIR sign, so the warning before stop 2 is the lamp flickering and Switch straining on his box (O20i).
- **O19 stays a dissolve:** M5's two moves and the 10-frame dissolve (decisions 11) stay, and three fast closes (kick, hands, tambourine) end the build. The brief's single camera move is still M7 work.

## 14. 2026-11-15 — M5b review: what the human should rule on (agent)

- **Faces at the M3 level:** no close shows a face. The wides and some mids show the same dim faces the approved M3 board has: the live room's and treehouse's band, the cafe crowd, and the park's lit, coloured people. The mids are darker than the wides (−0.5 to −1.3 stops) and focus on the foreground. Fixing them for real (darker skin values or hoods under the backlight, or fewer front-lit sources in the cafe and park) is M5c's or M7's. The worst remaining frames: O17c, O17d (cafe crowd), O09g's last second (the guitarist), O20f's background.
- **The haze is a glow, not shafts:** Eevee's volume over the room, with a spot through each window, reads as atmosphere. Hard beams need the panes to let light through (they're emissive and opaque so nothing outside shows). Left for M7.
- **The kick close is from the player's right**, so the foot on the pedal reads; the 503 head is seen at an angle. The front-on head is in the wides.
- **O20g frames fists against the skyline**, not the band, because the park band's faces are lit.
- **Rain closes (O03b, O09l) are pale:** the streaks are faint at 540p. A stronger streak shader is a one-line change for M7.
- **O14d (the Polaroid)** is a flat grey placeholder photo (M3's texture). The close makes that obvious.

## 15. 2026-11-15 — M5c: performances added at set time, not a library rebuild; what changed on set (agent)

- **No rebuild:** every person in `assets/figures/figures.blend` is already a full Mixamo rig with deforming meshes. A rebuild through `blender/ep/make_figures.py` (MPFB, every person in every pose) would only re-bake the same rigs with other loops, and grips and per-song timing need the music map at set time anyway. So each performer gets their own copy of their library person at build time (as `blender/poses.py` and M5b's clappers already did), posed and keyed per frame by a small FK/IK solver (`blender/perf.py`). The library file is untouched; `blender/ep/` is untouched (only `gait.py` is called, as is).
- **The library's sway loops are dropped** on every performer and crowd member: the solver keys the whole body, with the feet re-solved every frame so nothing slides. M5b's whole-person bounce, surge and lean (which moved the feet) are gone.
- **The kick player sits 17 cm to his left** of where M5's kit put him, so his right foot is on the pedal at the drum's centre; the kick drum stays where the cameras expect it. The pedal and beater are new separate parts (`blender/perf_props.py`).
- **The kit's snare is gone:** nobody played it. The kick player claps on the backbeat instead (stomp-clap).
- **The lead singer is person 22** (M3's "backing singer" spot, the only band member without an instrument): a male lead, as the style prompt has. Head and upper body follow the lead vocal envelope. No jaw: the Mixamo rig has no jaw bone.
- **The tambourine is held at chest height**, not raised overhead (M3's raised arm): shakes on the percussion hits, slaps into the open left hand on 2 and 4.
- **Mic stands are rebuilt per singer** at their own mouth height, the mic 9 cm off; the lean-ins bring the mouth to 3–5 cm.
- **Fists are 11 cm lower** than M5's fist pose, so a pumping fist stays below the top of the head.
- **Closes:** nine repeated closes swapped (`docs/coverage_m5c.md`), cuts unchanged. M5b's fixed tambourine close is now aimed at the tambourine where it's held (only O17j uses it). The treehouse skylight spare isn't used: no repeat falls in a treehouse shot.

## 16. 2026-11-15 — M5c review: calls for the human (agent)

- **The swaps** (`docs/coverage_m5c.md`): kick close kept in O03c and O19c, tambourine close in O17j; the beater (O08e, O19e), the singer's lean-in from behind (O09d, O20d), the banjo's fretting hand (O09h), Switch and his conduit (O11c), the probe's mug (O14b), the strumming hand (O17a, O20h). The treehouse skylight isn't used.
- **The lead singer is the fifth band member** (decisions 15). If the human hears the lead as the guitarist, the head motion moves to the guitarist in one line.
- **O20g** keeps M5b's camera: with the fists pumping lower, it's mostly the skyline with the tops of heads. Re-aiming it showed the park band's lit faces. M7 could give it a fist in frame or a different person.
- **O03c** shows the 503 head but not the pedal (the player moved to put his foot on it); the pedal is in the beater closes.
- **The hand closes** (O03d, O08f, O09b, O11b, O17h, O19d, O20b) are still seven of the same framing, now with different people clapping at different lags. Not asked for; an M7 candidate.

## 17. 2026-11-15 — M5c review: instruments, grips and hand poses (agent)

- **Ever Present's neck, copied, not imported:** `blender/ep/stage_props.py`'s `guitar()` builds the neck inline with the electric's body, so the neck, fretboard, frets, nut, headstock and tuners are copied into `blender/instruments.py` (provenance header) and generalised to any frame, scale, fret count, width and tuner layout. `blender/ep/` is unchanged.
- **Small departures from Ever Present's neck:** the headstock tilts back 12° on the guitar and 10° on the banjo (Ever Present's is flat; an acoustic's is angled); the tuner keys stand across the headstock's face (Ever Present's lie flat on it and read as flags in a close); the strings run on over the nut to the posts.
- **The banjo** has a narrower neck than the guitar (32 mm at the nut, 41 at the heel), 4 long strings and the short 5th, a 2+2 headstock, and a shallow resonator (7.8 cm deep overall): with a 10 cm pot the picking forearm went through the rim.
- **Holds:** the guitar's neck rises 30° (M5c: 28°), the banjo's 34° (M5c: 32°), both turned 6–8° toward the room and their tops tilted 6° (guitar) and 10° (banjo) up, the sound hole (pot centre) 18 cm over the hips. Steeper and higher than M5c because these players' arms are short (upper arm 23 cm, forearm 21 cm): at 24° the fretting hand couldn't reach the first frets and the strumming forearm couldn't reach the body's edge.
- **Chord positions:** the fretting hand plays at frets 2, 3 and 5 (index finger), a capo-style position, not open chords at the nut: the nut is out of these players' reach with a neutral wrist.
- **The wrists come from the forearm:** each hand continues along its forearm, then bends at most 25° (flexion or extension), 15° ulnar, 10° radial. The palm's facing comes from turning the forearm (pronation and supination; up to 175° from the rig's rest, which isn't anatomical neutral); the hand doesn't roll at the wrist.
- **Tambourine:** gripped by its frame (the band in the palm, fingers round its edge), the disc out from the palm facing forward, not held up by the rim with the wrist bent back. The slap is now the disc brought back onto the open left palm, which waits behind it (between the disc and the chest): from in front, the left forearm would pass through the ring.
- **Fist pump (task 5):** elbow down: the upper arm out and a little forward, 30–45° below horizontal; the forearm upright at the top of the pump, forward and up at about 50° at the bottom; the fist in line with the forearm, palm in, at least 15 cm under the top of the head (the wrist). M5c's arm out to the side at shoulder height is gone.
- **Mug toast:** the elbow out and forward below the shoulder, the forearm up and in, the palm facing in so the mug stands; a 10° radial bend keeps it level. The mug is re-seated in the re-posed hand (it rides the hand bone, as before).
- **Claps:** palms meet 7 cm under the shoulders and 30 cm in front of them, the elbows a little out, fingers up 50–60°, the right hand 8° more forward than the left (so a clap at its closed frame doesn't read as hands pressed together in prayer); fingers together and nearly straight. People joining the chorus claps bring their hands up from the waist instead of blending from their hold.
- **Hanging arms** (standing people, the other arm of a fist or mug, the lead's free hand) are turned out from the shoulder, up to 16°, until the forearm and hand clear the hips and jacket by 12 mm.
- **O12's crowd** is frozen in the M5c solved poses (seeded as O11, as O21 uses O20), not the library's clap poses, which had the broken wrists; the late clapper claps with the solver's clap on the same frames.
- **The contact check** counts forearm spheres from 40% of the forearm's length: nearer the elbow the sleeve meets the torso's side whenever an arm hangs. The before and after numbers both use this.
- **M5c's frames stay where they are** (`renders/m5c/frames/`), since `review/m5c_animatic.mp4` is kept for comparison and they regenerate it; M5c2 renders into `renders/m5c2/frames/`. Superseded M5c2 frames, if any, go to `archive/`.
