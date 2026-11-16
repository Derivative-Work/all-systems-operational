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

## 18. 2026-11-15 — Disclosure only at the end (human)

- Replaces decisions 7: no disclosure panel over O17; the full card plays once at the end, after the fact card (brief rev 121), and in the description. The audit prompt still asks whether the disclosure is "prominent and honest enough"; with the card at the end only, that question goes to the auditors as is.

## 19. 2026-11-15 — M5c review 2: recast, holds, grips and the hand rig (agent)

- **Recast (human interventions 16: "use a different player"):** the guitarist is person 33, not 3; the banjo player is person 36, not 8. The instruments stay at real size (the 648 mm dreadnought, the 670 mm banjo). Measured with `blender/cast_probe.py` on 20 people (`log/render_logs/m5c3_cast_guitar.json`, `m5c3_cast_banjo.json`): person 3 (shoulder 1.27 m, upper arm 0.23, forearm 0.21) can't reach the guitar's pick point at all with the strumming arm down; person 8 (shoulder 1.24 m) only fretted the banjo with the elbow raised. 33 (shoulder 1.57 m, arm 0.29 + 0.26, hand 0.21) and 36 (shoulder 1.54 m, arm 0.28 + 0.27, hand 0.21) pass every check with the lowest costs. Ever Present's guitar problem was the instrument (a 0.95 m scale); what applies here is the real-size neck (already in) and casting by hand by index (its `BAND`).
- **Swapped, not moved:** `aso_kit.SWAP` (set in `blender/coverage_m5c.py`) exchanges 3 with 33 and 8 with 36 wherever a person is picked, so everyone stands where they stood: 33 takes the guitarist's place and 3 takes 33's (O12's late clapper); 36 takes the banjo's place and 8 takes 36's (a treehouse meeting chair); crowd draws swap the same way. M5 and M5b are unchanged (empty swap).
- **Silhouettes:** 33 wears the same t-shirt-and-jeans outfit as 3, with long grey hair; 36 wears the same dark suit as 8, with a grey afro. The band no longer has an Asian member (8 was the only one). The Asian alternatives didn't fit: 32 frets with the elbow raised, 34 is the library's tallest (2.08 m), 45 fails the thumb check and needs the guitar lower. 40 fits the banjo but looks like the host (30: same outfit, bald, same build). Call for the human.
- **Holds:** necks 25° up (M5c2: 30°, 34°), heads turned 16° toward the room (6°, 8°), tops tilted 12° up toward the player, the sound hole or pot centre 10 cm over the hip joint (18 cm); the guitar body's centre is 4.6 cm over 33's hip joint, 59% of her height. `instruments.frame_matrix`'s tilt turns the top down for positive angles, the opposite of its docstring, so M5c2's +6°/+10° had the tops facing away from the players.
- **Strumming/picking arm:** searched over elbow positions on the sphere round the shoulder: the upper arm at least 45° below horizontal (about 62 preferred), the elbow over the bass edge of the lower bout (the banjo's armrest), level with the top or in front of it, the forearm down across the top to the pick point, the wrist flexed 25° (banjo 15°). The pick point moved to 6 cm past the sound hole's centre toward the neck and 1.6 cm over the strings (the pick reaches them): from an elbow on the edge, a real-size forearm and hand reach past the sound hole. The banjo picks 5 cm from the bridge (was 1.5). The strum is the forearm turning about the elbow plus the wrist.
- **Fretting hand:** placed by the middle fingertip on its string (index finger at frets 1, 2, 3: open-position chords, now in reach; M5c2: 2, 3, 5), the elbow searched so the palm faces the neck from below and the hand crosses it, the fingers each flexed onto the fretboard. The fretting wrist may flex 40° and deviate 20° ulnar (the general limit, kept for every other hand, is 25° and 15°): from an elbow by the side, the first frets need it, as on a real player. Call for the human.
- **The hand rig:** two things measured on the mesh, not assumed (`blender/palm_test.py`). The palm normal had the wrong sign (M5c2 flipped it the wrong way after a still); it's now the side without fingernails. And finger flexion is about the finger bones' local Z (−Z left, +Z right; the thumb −X), not X: +X, used for every curl in M5c and M5c2 and in Ever Present's `figlib.py`, swings the fingers sideways in the plane of the palm. Every grip is now set from the straight rest hand by the measured axis: fretting, pick hand, banjo fingers, clap fingers, the tambourine grip and slap hand, the mic-stand grip, fists, mugs and phones (the library's phone and mug grips were sideways bends too).
- **Ever Present:** its `figlib.curl_fingers` has the same X curl, which may be why its hands looked "like they're trying to awkwardly grasp something" (its human interventions, M6). Not changed there (read-only); for the human to pass on.

## 20. 2026-11-15 — M5c review 2: claps, the re-aimed closes, calls for the human (agent)

- **Claps:** with the palms the right way round, the hands met at the fingertips with the heels 10–13 cm apart (a V): the fingers pointed up at 54°, the elbows pulled out, and the wrists couldn't extend past 25°. Now the fingers rise 40°, the elbows follow the forearm more (pole weight 0.5), and clapping wrists may extend 40° (the general limit stays 25° extension, 15° ulnar, 10° radial). The palm centres at the closed frame are 4–7 cm apart, about one palm's thickness each side, on four library people (M5c2: 11–14 cm). M5c's "broken wrists" were 55° of extension with 67° radial deviation at the same time; 40° of extension alone is an ordinary clap. Call for the human, like the fretting limit (decisions 19).
- **Closes on the recast players:** the two band-relative closes from M5c (`close_strum`, `close_fret`) were fixed points in the player's figure frame, and M5b's `close_guitar` and `close_banjo` fixed points in each room; tuned for persons 3 and 8, they framed a hip or an empty neck on 33 and 36. Each now keeps its direction and distance and is re-centred on the player's solved hand at the sub-shot's middle frame (`anchor`, `reanchor` in `scripts/coverage_m5c.py`; `blender/coverage_m5c.py`). Sub-shots: O09f, O09h, O09j, O11e, O17a, O17f, O20f, O20h. Cuts, frames and cameras of every other sub-shot unchanged.
- **For the human:** (1) the recast (33, 36) and the band without an Asian member (decisions 19); (2) the fretting wrist at 40° and the clap wrist at 40°; (3) chord positions now at frets 1–3 (open position) with a thumb over the top: a folk grip, not a classical one; (4) the strummer picks 6 cm past the sound hole's centre, toward the fretboard's end (from an elbow over the edge, a real-size arm reaches there); (5) O09g shows the banjo player's lit face softly blurred at the right edge (36 is taller and lit differently from 8; the old face note in decisions 14 was about the guitarist there); (6) O03d opens on a blurred crowd back across the lens for about a second (as in M5c2, M5b's framing).

## 21. 2026-11-16 — M7a: how the look is built and rendered (agent)

- **In the shared set code, off by default:** `blender/look.py` hooks into `sets.py`, `aso_props.py`, `aso_kit.py` and `coverage.py` (production log 30), so the full M7 render inherits it through `blender/coverage_m7.py` and M3–M5c3 stay reproducible. No hero-frame-only changes: every hero is a `--still` of the M7 coverage at its sub-shot's middle frame.
- **Procedural only:** wood, plaster, brick, fabric, rugs, ceramic, moss, needles, bark, grass and gravel are node-built. The brief allowed CC0 assets (Poly Haven, ambientCG) if they clearly helped; none were needed, so nothing was downloaded. No HDRI: the park's sky is a directional world shader, the rooms' daylight comes from lights.
- **Eevee is the main path** (the brief's engine; the plan allowed Cycles): 64 samples, raytracing, volumetrics, motion blur. Cycles is compared on two heroes (production log 33).
- **The grade is a Python step** (`scripts/grade.py`) on 16-bit stills, not the Blender compositor: the home-movie grain needs seeded per-frame noise, which the compositor lacks, and one function then serves the stills, the motion test and M7's assembly. Bloom stays in the compositor. Looks: grey (live room, treehouse, park), cafe (warm in the mids and shadows only, the windows stay grey daylight), home (O22 from "Remember Wednesday"), instant (the Polaroid's photo).
- **Exposure:** a base per room (`config/look_m7.json`) plus the build's and the camera's M5b offsets, which keep the people angles darker than the wides. M5b's extra −0.9 on the cafe's people angles is dropped; the cafe's room exposure replaces it.

## 22. 2026-11-16 — M7a: the haze as daylight shafts, from a soft sun (agent; for the human)

- The brief: grey Seattle daylight through big windows, and haze that "should read as light beams from the windows, not a glow". Overcast light makes no beams, so this is a stylization. Each room has one soft sun (2.5–4° wide) behind and above its window wall; it reaches inside only through the openings (the panes cast no shadow), so the shafts are window-shaped, parallel and crossed by the mullions, and they land as pools on the floor and rim the band from behind. Only that sun scatters in the haze (Eevee volume factor 14 live, 5 cafe, 6 treehouse); every other light has volume factor 0, so there is no glow round the practicals or windows.
- First tried: a spot per window, as M5b. They overlapped into a uniform milky glow.
- Cycles has no per-light volume factor; it gets a second copy of the sun that lights only the haze (production log 30), so the comparison is like for like.

## 23. 2026-11-16 — M7a: fixes to the approved grey box that change what is on screen (agent)

- **Treehouse roof:** M3's two roof slabs and both skylights are rotated the wrong way (`rotation -s*ang`): each slope rises toward its eave, a butterfly roof with open gaps over the room. The grey sky through the gaps read as skylights in every grey-box treehouse frame. M7 turns them the right way (`blender/look.py`, not `sets.py`, so M3–M5c3 reproduce): the roof is closed, and the two real skylights (1.0 × 1.2 m, rain on the glass) sit under it.
- **Park sun:** M3's "overcast" sun travelled toward +Y, from behind the camera, so it lit the crowd's backs and the band's faces. That is why every grey-box park shot had fully lit, colourful people (decisions 14, 16). M7's comes from behind the band, high and soft (50° up, 60° wide), with its glare on the wet grass cut, and the sky is brighter behind the band than behind the camera.
- **Replaced, not restyled:** M3's cone-stack trees (conifer prototypes), the box skyline (a fog-flattened massing), the 4 mm drizzle (1.5 mm, fainter, 1.6× as many: drizzle, not a downpour), the treehouse's moss pebbles (finer cushions in drifts and hanging strands).
- **Polaroid:** M3's placeholder photo is replaced by a Blender render (decisions 24).

## 24. 2026-11-16 — M7a: the Polaroid's photo is the cafe session, rendered (agent; for the human)

- The photo is a Blender render of this cafe at the chorus 2 singalong (mugs up), seen from behind the crowd with the band backlit against the windows, warmed and faded as an instant print (production log 31). It is rendered, not generated, as the brief wants for the rooms. It shows the same day's session ("Wed 11/11" is the caption the brief gives, the day before the outage), not an earlier one: the brief doesn't say which.
- The crowd is in it because the session is a singalong; the human may prefer the band alone. It's a one-line change (hide the crowd before the render).

## 25. 2026-11-16 — M7a: thirteen heroes, not ten to twelve (agent)

- Three or four per set and each set's signature element: rain on glass (O03b), Switch and ON AIR (O10a), the Polaroid close (O14d, since its photo is new), the whiteboard (O18a), the conference phone and chargers (O18e), the skyline in fog and the home-movie grade (O22d). O19a (the deck, moss on the railings, the conifers up close) was added after the conifers and moss were found weak up close; it's the treehouse's only outdoor view. O08c's night cutaway isn't on the board: it uses the same materials with the lights off.
- No camera was moved. Proposals, not done: none needed for the look; O18e reads only as a dark insert (its camera offset darkens it 0.5 stop; dropping that offset is a one-line change).

## 26. 2026-11-16 — M7a look board: calls for the human (agent)

1. **The look, per set:** approve it as the base for M7, or name what to change. Recommendation: approve. The live room and the park are the strongest; the coffee shop is close. The treehouse is the weakest: very dark, the cedar barely reads.
2. **Shafts from a stylized sun** (decisions 22) rather than strictly flat overcast. Recommendation: keep. The brief asks for beams, and they make the live room.
3. **Silhouette depth:** people are near-black in Eevee (Cycles' bounce lifts them a little). Recommendation: keep. If the band should show more of the instruments, raise the room exposure by ⅓ stop on the closes only.
4. **The Polaroid's photo** (decisions 24): the cafe session with the crowd, warm. Recommendation: keep; the band alone is a one-line change.
5. **Roof and park sun fixes** (decisions 23): they change the look of approved grey-box frames (the treehouse's "skylights" were gaps in the roof; the park's people were lit from behind the camera). Recommendation: accept; both were bugs.
6. **M7 render plan:** Eevee at 1920×1080, 64 samples, about 4.6 h for the cut's 6,405 Blender frames; JPEG q92 frames (about 1.4 GB), graded at assembly. Recommendation: Eevee. Cycles costs 2.5–5× the time (about 17 h) for softer shafts and a little more bounce.
7. **Small additions for M7, not done here:** a slow drift in the haze (production log 34); O18e's camera offset (−0.5) dropped so the table reads (decisions 25). Recommendation: do both.
8. **Likeness** (production log 35): no KEXP identifier or layout found, from text descriptions only. Recommendation: the human glances at the board for likeness to rooms they know.

## 27. 2026-11-16 — M7b: how the rain lives (agent)

- Human interventions 18: "some motion on the water droplets". The drops are a shader, not particles or a fluid simulation: beads on two grids that appear, grow, merge and come back elsewhere; runners that collect, slide in stick-slip jerks down a wiggling track, shrink, leave a trail and beads, and sweep up the beads in their path (production log 37). It is a function of the pane position, a seed and the clock, so any frame renders the same alone or in sequence, and it costs nothing at render time. Simulated drops (Blender's fluids, or particles with collisions) would be truer in the merges but slow, hard to seed per frame and not Eevee-friendly.
- M7a's rivulets (the keyed Mapping) are kept under them; the static Voronoi beads are replaced.
- The beads are as many and as crisp as M7a's (checked at 1:1); the drops never fall faster than about 15 cm/s, slower than real drops on a vertical pane, so they read at 24–30 fps without strobing.

## 28. 2026-11-16 — M7b: O04's phone is a texture on the Blender phone, with its own camera (agent; for the human)

- Human interventions 18: the chat "readable when it is visible". The M5 animatic pinned a Remotion video onto the brightest quad in the frame (`scripts/animatic.py` `o04`): about 150 px wide at 1080p, clipped white, small type. M7b maps the texture onto the phone's screen in Blender (lit, in perspective, not clipped) and redesigns it for the size: one message and the +1 count, big, above the holder's thumb; no earlier messages, no composer. The channel, names, times and cue frames are M5's; "dramatization" stays on the screen.
- **Camera (allowed for O04a):** over the right shoulder, about 0.44 m from the screen, following it smoothly. At 1080p the question is set at about 21 px (capitals about 15 px, a 23 px line pitch), half that at 960 wide; the agent read the question, the sender and the +1 count at both (production log 38). The band no longer shows: the phone is held flat at chest height, and no framing that keeps the type legible also reaches the band (the one that tilts up to the room puts the lens inside the holder's head); the floor, rug and crowd's legs show beyond, soft.
- The question still arrives on "inbox", halfway through the 4.8 s shot (the approved M5 cue); before that the phone shows the empty #it-help channel. Option for the human: show the question from the start and keep only the +1 on the Hey!.
- The live room's other phones (six crowd members, in the wides) stay blank glowing screens: no text to read at that size.

## 29. 2026-11-16 — M7b: the treehouse lift, O08c at night, the closes (agent)

- **Lift by light linking, not exposure:** raising the exposure would lift the band with the room. Five soft fills light only the set's own meshes (walls, roof, beams, floor, table, chairs, props); people, instruments, the panes and the screens are not in their receiver collection. Eevee's fast GI still bounces a little of it, so the silhouettes are near black rather than black, as before. Treehouse exposure unchanged (−0.55); O18e's −0.5 camera offset dropped as asked.
- **O08c at night:** M7a's haze added the daylight sun and its shafts at night (a bug: the haze didn't know the time of day). M7b has no haze at night; a dim cool fill on the set (light-linked like the day's) and the screens as the light.
- **Closes +⅓ stop:** the six named presets and close_beater (the kick's pedal close, O08e and O19e, which shows the same SESSION 503 head), so every instrument close is treated alike. close_beater is not on the human's list: a one-line revert in `config/look_m7.json` if unwanted.

## 30. 2026-11-16 — M7b: the treehouse screens' content (agent; for the human)

- Human interventions 19: "someone struggling to 2FA in, someone with a robo-call from a fake number as a stand-in for a page looking at an invented dashboard, invented code and agent screens, the generic video call"; "(I don't have any inside information, these are just guesses)". So: a guess at a plausible night, not how this incident was handled; O08c and O18 keep "dramatization".
- **What each screen says** (`remotion/src/components/TreehouseScreens.tsx`):
  - seat 0's phone: "Sign-in request · work account · attempt n", "Enter the number shown on your other screen", "Verifying…", then "Request timed out / No response from the sign-in service. / Try again", looping every 3.6 s with a new two-digit number. A plain shield icon, no app name.
  - the phone on the table: "incoming call / Automated alert / (206) 555-0147 / Seattle, WA", pulsing rings round a bell, Decline and Accept. 555-0147 is in the fiction range (555-0100 to 0199).
  - seat 2's laptop: "service health · prod-west", "sev 1 open", the time; "5xx error rate" with the live value (about 30%) and a chart from 09:00 (flat, a climb from about 09:50, high from 10:26 with noise); tiles mailflow-west, authn-edge, cal-sync, connector-hub DOWN, files-api OK, search-idx DEGRADED (some flip during the shot); retries per minute, p95 latency. Invented service names; the video's palette (ink, coral, the status lights), not a real console's.
  - seat 1's laptop: a terminal, `ops@bastion-2:~/runbooks/mail$ ./health-check --tier mail --region west --every 0.3s`, then a line every 0.3 s: `GET /healthz <service> 503 Service Unavailable … retry 1/3`, `timeout after 5000 ms`, some `200 OK`; a "503 × n" counter. Investigation only: no code change, no diff, no commit (the config diff is reserved for O18 on report day).
  - seat 0's laptop: "Kestrel · read-only · logs" (an invented assistant, a plain "K" tile; a cool grey-green theme, chosen so it is not a warm cream with a coral accent like any real assistant); the user's "summarize the mail errors since 10:26"; a tool row "mail connector — connector unavailable · retry in n s"; the headline "I can't reach the mail connector." (O14's table tent); then, typed out: "Reading the health-check log instead: mailflow-west has returned 503s and timeouts since 10:26 a.m. PT, and sign-in retries are timing out too. Nothing in the log says why yet." It never proposes, writes or deploys a fix.
  - the fourth laptop (new, beside the speakerphone, turned to the room): "sev 1 bridge · mail", a running timer since 10:26, six dark tiles with initials: Tess · on call (speaking, a coral ring), Ren (as in O08's "Ren (IT)"), Marco, Ola, Sam, Priya; four muted.
  - seat 1's phone: O08's #it-help thread (Dana's question, IT's "we are aware"), as a still. seat 2's phone: dark, in their hands, while the alert rings on the table.
- **Times:** O08c at 11:47 p.m. Thursday; the bridge (O18) at 2:52 p.m. Thursday. The wider outage from 10:26 a.m. PT (1:26 p.m. ET), as the coordinator's brief for this pass gives; nothing on screen names a cause.
- **Readable where the screen is big enough:** at 1080p in O08c, the assistant's headline and the dashboard's rate read, the call grid and the chart read as shapes; the timeout and caller ID are a few pixels. In O18e the dashboard is in focus for 1.3 s (title, rate, tile names readable), then the rack to the whiteboard; the ringing phone is in the frame but 1.5 m off and nearly edge-on, so its caller ID doesn't read (production log 37).
- **For the human:** the assistant's wording and name; whether the caller ID and the assistant's line need their own insert to be read; seat 1's phone showing the users' #it-help thread; the fourth laptop.

## 31. 2026-11-16 — M7b: the band-only Polaroid (agent)

- Human interventions 18: "Band only Polaroid". With the crowd hidden, M7a's camera framed an empty floor and the string lights at 2.5× front-lit the band (faces read in the first take, archived). The camera moved to about the crowd's front line, the string lights stay at the room's level, so the band is backlit against the warm windows as the rest of the cafe is; faces stay dark at the photo's size on the wall (a few pixels in O14d).

## 32. 2026-11-16 — M7b: a generated far plate for the park (agent, on the human's ruling)

- The brief's rendering plan says the rooms are "rendered, not generated, so they stay consistent across all four sets and nothing in them can drift toward a real studio, a face or water". Human interventions 19 makes one exception: the park's far plate (the distant city and the far tree lines in layered fog, one plate behind the Blender set) is generated, and O22d is the same plate animated with image-to-video. Everything people touch stays rendered (the ground, the crest, the near firs, the lamp post with Switch, the umbrella); every other shot stays rendered.
- The plate has no people, faces, text, logos, water, boats or landmark towers; takes with any are rejected (as M4). It stays behind fog, so a tower that half-resolves into a recognisable shape is rejected too.
- This pass only makes concept stills and plate candidates for the human to pick a direction from (production log 42); the park is not rebuilt yet.

## 33. 2026-11-16 — M7b: the treehouse screens after brief rev 136 (agent; supersedes parts of 30)

- Brief rev 136 (human interventions 20) builds on Microsoft's preliminary report. For the screens (coordinator's note):
  - **No config diff:** decisions 30's "the config diff is reserved for O18 on report day" no longer applies; branch A now circles the July fix on the whiteboard. The terminal is still a health check: no diff, no commit, no change history on any screen.
  - **The dashboard echoes the sourced story with invented labels** (`TreehouseScreens.tsx` `Dashboard`): the 5xx rate from 08:00 PT, a first rise from 8:20 a.m. PT (Exchange problems from 11:20 a.m. ET) and the climb from 10:26 a.m. PT (1:26 p.m. ET), high through the night; "gateway pool · unresponsive", 60 servers going red from the left past a dashed 80% line (O08c 78 → 85%, O18 60 → 86%); "capacity offline 13.8%" (nearly 14%); "auto-reroute ON", pool a → pool b → pool c; mailflow-west, authn-edge, cal-sync and connector-hub DOWN. Numbers only: no words from the report, no internal names, no cause.
  - **Kept out of every screen:** the July fix, who or what wrote it, the load tests (the whiteboard's and the tags'). The assistant reads logs and is blocked; the terminal probes endpoints; neither hints that an AI wrote or caused anything.
  - **O08c** stays Thursday 11:47 p.m., after the wider outage and once "Teams came over for the night"; the alert call and the timing-out sign-ins fit it. The bridge (O18) stays Thursday 2:52 p.m.
- Not changed here (waiting for the new master): the O02/O23 stamp, O18's whiteboard text and its two tags, the fact card.

## 34. 2026-11-16 — M7b: calls for the human (agent)

1. **The M7b look** (`review/m7b_look_board.jpg`, `review/m7b_motion_test.mp4`): living drops, haze drift, steam wisps, the treehouse lift, the closes' +⅓ stop, the band-only Polaroid, as the base for the full M7 render. Recommendation: approve.
2. **O04a** (decisions 28): the new framing loses the band behind the phone in exchange for a readable screen; and the question still arrives halfway (the approved M5 cue). Recommendation: keep the framing; consider showing the question from the shot's start so it reads for all 4.8 s.
3. **The treehouse screens** (decisions 30, 33; `review/m7b_screens.jpg`): the content and wording, especially the assistant ("Kestrel", read-only, "I can't reach the mail connector.", its log summary), seat 1's phone showing the users' #it-help thread, the fourth laptop on the call, and the dashboard echoing the report's numbers (past 80% unresponsive, 13.8% capacity offline, auto-reroute). The caller ID and the timeout read only as shapes (O08c, O18e); an insert would make them readable if wanted. Recommendation: keep; no insert.
4. **close_beater** in the +⅓ stop with the six named closes (decisions 29). Recommendation: keep.
5. **The park** (production log 41–42, `review/m7b_park_concepts.jpg`): pick a direction. Recommendation: concept 1/2's brow for the rebuilt crest; far plate 1 (plate_city s42) for the city, extended sideways for O20e, with plates 2–3's ridges as the far tree lines; firs within about 60 m, the crest, the brow, the lamp post and the umbrella stay 3D. Then an image-to-video take of the plate for O22d.
6. **The live room's crowd phones** stay blank glowing screens in the wides (too small for text). Recommendation: leave them.

## 35. 2026-11-16 — M7c: the park's far plate, extended, and O22d generated (agent, on the human's ruling; extends 32)

- **What is generated:** everything past the 3D set's reach, as one panorama (7680×1440, about 128° at 60 px a degree): far plate 1 (`plate_city_s42`) in the centre, unchanged below the cloud deck; FLUX.2 [dev] outpainting continues the city's edges to each side (L1, R1) and grows the far sides from plates 2–3 as the far tree lines (L2, R2; their far towns regenerated, since M7b took those plates for the tree lines only). The sky's brightness and the cloud deck's bands are evened across the seams (`scripts/m7c_plate.py` compose): an edit of generated pixels, logged. Takes, rejects and prompts: production log 46, `log/prompts/m7c_park.md`.
- **How it sits behind the set:** on a cylinder section 2 km round the crest (±115°), mapped by angle (azimuth 0 = panorama column 3880; the horizon row 560 at the crest's eye height, 1.8 m). At 2 km no camera here shows parallax against it (the largest move, O19b's, is 16 m). It is emissive, mapped through the inverse of the park's view transform (AgX, its look, the wides' exposure), so it reads in the render as generated and gets the same grade as the frame. Its top fades into the sky, and the world's camera colour is set to the plate's own sky, so the fade has no seam; below its mist band it holds the valley-fog colour. The 3D's fog takes its colours from the plate (the horizon haze at the crest's level, the mist band below), so 3D and plate meet in the same greys.
- **What stays 3D:** the crest and its rim, the brow and the whole drop to about 250 m (so O19b and O20e see real slope, not plate), every fir and bare tree (to about 240 m), a few houses deep in the valley fog, the path, kerbs, terrace, bench and puddles, the lamp post with Switch, the umbrella, all people, the drizzle, the near haze and the fog curtains over the drop and in front of the plate's lower edge.
- **O22d is generated:** LTX-2.3 of the plate's centre (not the extension), the pick nearly locked-off (s41), upscaled with Lanczos to 1080 and graded home like the rest of O22 from "Remember Wednesday". With O06, it is the video's second generated moving shot; the brief's plan names one ("Generated, one still … lightly animated"). Human interventions 19 and 22 ask for it. It replaces the Blender O22d in the M7 assembly (`config/look_m7.json` m7c.clip_subs; `scripts/m7_inserts.py`, slotted as `scripts/animatic.py` slots O06's clip), and `blender/coverage_m7.py` no longer renders it.

## 36. 2026-11-16 — M7c: cameras changed for the new hill (agent; for the human)

Only the park presets below changed (`config/look_m7.json` m7c.cameras; `blender/coverage_m7.py` replaces the presets in the M7 path only, so M5c3 reproduces). Every cut time, move type and lens is as M5c3's. Every close is unchanged: the kick, the beater, the hands, the umbrella, the banjo, the backs, the tambourine, the strum, lean_back, Switch, walker_feet, walker_back and lamp_rain. The skyline camera (O22d) is not rendered any more (decisions 35).

| Preset | Sub-shots | M5c3–M7b | M7c | Why |
| --- | --- | --- | --- | --- |
| wide | O20a | (1.0, −6.5, 1.6) → (0.3, 6.0, 2.0), 28 mm (board O20) | (1.0, −7.0, 1.8) → (0.3, 6.0, 1.25), 28 mm | aimed 2.4° down, not 1.8° up: the horizon moves from about 55% to 44% from the top, so the lawn runs to the brow below the crowd's heads; heads stay against the fog and the plate; Switch's lamp post stays in frame |
| o21 | O20j, O21a | (1.0, −6.1, 1.62) → (0.3, 6.0, 2.0) | (1.0, −6.6, 1.8) → (0.3, 6.0, 1.25) | as the wide, so the freeze holds the same frame (O20j and O21a share it as before) |
| wide_high | O20e | (−6.5, −5.5, 4.6) → (0.0, 4.0, 0.8), 24 mm | (−5.2, −8.5, 5.4) → (0.8, 8.0, 0.4), 24 mm; truck (0.8, 0.4, 0.3) as before | higher and further behind, aimed 18° off the view instead of 34°: the crest, the brow, the valley and the city fill the frame |
| empty | O22a, O22f | (0.0, −7.0, 1.7) → (0.5, 12.0, 2.5) (board O22) | (0.3, −7.6, 1.85) → (1.3, 12.0, 1.05) | aimed down a little: the path runs to the viewpoint, and the walker stands at the brow against the fog in O22f |
| o19b | O19b | M5's keys: (0.0, −16, dome + 1.0) → (0.4, −8.5, 4.2) over the whole O19b build (195 frames), so the camera was still rising under O19c–e's closes | three keys over the O19b sub-shot's own 123 frames, then held: (0.25, −26, ground + 1.5) among young firs on the back slope → (0.3, −18.5, + 2.5) → (0.4, −10.5, 3.8) over the crest's back edge, looking at (0.3–0.4, 6, 2.4 → 0.8) | the new crest has a back slope to rise out of; the rise lands on the crest within O19b (M5's move ended out of sight under the closes) |

## 37. 2026-11-16 — M7c: the hill, and what stays where (agent)

- **Ground:** a crest at z 0 where people stand (flat within ±1 cm under the crowd and band, as M3's ground was there), inside an irregular rim; the lawn rolls over a convex brow about 13–15 m behind the band and drops about 32° toward the view, 18° on the camera side, 26° at the sides, easing to about 12° far down (−16 m at 26 m past the rim, −38 m at 86 m, −71 m at 236 m). One height function (`blender/park_m7c.py` ground_z) serves the mesh, paths, trees and walker; `sets.hill_z` points at it in the M7 path only.
- **The walker (M5c3's gait, unchanged):** walks the same straight line, (1, −3) to (3.2, 12). The gravel path lies along it, 2 cm up as M3's plank was, so the walker's feet sit as before. The line ends on a viewpoint terrace at the brow, with a short stone retaining wall where the ground falls away and a bench. The path runs back down the camera-side slope out of frame.
- **The lamp post:** a new, generic cast-iron park lamp (plinth, fluted shaft, collars, a four-sided frosted lantern). M3's outlet box and Switch's plane stay at their M7b world position: the new ground at the post is 12.5 cm higher than M3's dome was, so Switch is 12.5 cm nearer the ground than before. The plane itself is untouched. The lantern glows warm (the M5b flicker keys still drive it).
- **A bug fixed (changes on-screen content):** in O22 the walker's own copy also rendered a second time at the world origin, as a figure standing on the path facing the camera. It shows in M5c3's and M7b's O22a: two people where the brief has one walking off. The cause is that `poses.finish()` excludes the copies' holder only if the holder exists when the set is built; O22 has no crowd, so the holder was created afterwards. The M7 path now excludes it again after the performances (`blender/look.py` after_layers). M5c3's code is unchanged.
- **The forest firs everywhere:** the treehouse's forest (O08c, O18, O19a) uses the same new firs as the park, as the brief for this pass asks ("no flat sprays"). Its fog and clearances are unchanged.
- **The fog:** surface fog to 130 m; the valley below −4 m fills over 16 m; colours from the plate. A near haze volume over the crest and the first of the drop (0.0022 per m, drifting on the clock). Four terrain-following curtains: three over the drop and one in front of the plate's lower edge, each drifting. Eevee's volumetric_end goes to 160 m in the park. M5b's fog cards are replaced in the M7 path.

## 38. 2026-11-16 — M7c Part B: the assistant unnamed, O04a from the start, the crowd phones (agent)

- **The assistant** (human interventions 22): "assistant · read-only" in the header, a plain tile with three lines in place of the "K", and "Ask about the logs…" in the composer. No name anywhere, so nothing on screen collides with a real product. What it says is unchanged (decisions 30, 33): it reads logs and is blocked; it never writes or ships a fix.
- **O04a** (human interventions 22): the question and "+1 6" are on the phone from frame 0, and the count goes to "+1 7" on the Hey! (the M5 cue). M7-O04-PhoneScreen only; M5's composition is unchanged. The cut, the camera and the holder's motion are unchanged (decisions 28).
- **The crowd phones** (decisions 28 had left them blank; this pass's brief asks for content): the six phone holders in the live room's stand-mode builds (O03, O04) show, by turns in name order, a camera view recording the band (a crop of the M7a live-room wide, with a red dot, a timer and a shutter ring), a lock screen (Thursday, November 12, 1:04, the #it-help notification), or M5's #it-help chat. None has a real app's look, logo or name. They are mapped onto each holder's own performance copy, oriented by the phone, at emission 0.55 (M7b's O04 screen is 0.9), so they are a light screen in a dim room, not a lamp. They can't be read at the wides' size: the clearest view, O03f, shows two of them a few dozen pixels across at 1080p.

## 39. 2026-11-16 — M7c: calls for the human (agent)

1. **The new park** (`review/m7c_park_board.jpg`, `review/m7c_motion_test.mp4`): the crest and brow, the drop with firs and bare trees, the viewpoint terrace and bench, the generated city 2–4 km off in layered fog, the clustered firs, the new lamp. Recommendation: approve it as the M7 park.
2. **The camera changes** (decisions 36): the wide and freeze frames aimed 2.4° down from 1.8 m; O20e higher and further behind; O22's empty wides aimed down; O19b's rise rebuilt up a new back slope, landing within O19b. Recommendation: approve. If the wides should show more of the drop, raise them to about 2.4 m, which puts more of the crowd's heads against the plate's darker mid-ground.
3. **The far plate** (`review/m7c_plates.jpg`): the extension (L1 and R1 the city's edges, L2 and R2 grown from the ridges plates) and the sky evened across the seams. Recommendation: approve. Its weakest spot is at about 22° left of centre (the L1 seam), where a hill fades into a vertical bank of fog; it reads as fog.
4. **O22d** is now generated (LTX-2.3 s41, nearly locked; s42 is a fallback with a slow push). That makes a second generated moving shot (decisions 35). Recommendation: keep s41.
5. **The stray figure in O22a** is gone (decisions 37); it was in the approved M5c3 animatic. Recommendation: accept; it was a bug.
6. **Switch** sits 12.5 cm nearer the ground than before, because the ground at the lamp rose and Switch kept its M7b world position (decisions 37). Recommendation: accept; no camera's framing changed.
7. **The crowd phones' content** (decisions 38). Recommendation: keep.
8. **Pre-existing, not changed here:** O08c's lower window panes show pale, flat shapes behind the forest at night. M7a and M7b have them too (the night sky behind the panes reads light), and the new firs change their outline. Recommendation: fix in the M7 render pass with the treehouse's night background.

## 40. 2026-11-16 — M1b: timing the v1.3 bridge (agent)

1. **The timing reads the lead as it sits in the master:** the old lead with the repaint spliced in. The repaint stem alone would leave the rest of the song without a lead. Every non-bridge cue holds (production log 52).
2. **Denial tag 2, "a beat later":** two beats of the grid after tag 1. The bridge is half-time, so that is one felt beat, 1.2 s (162.847 s against tag 1's 161.364 s). Tag 1 lands on "(Not", the line's first word.
3. **The doubled "(We're committed to doing better)":** the whiteboard writes it once, on the first; the second is marked but writes nothing.
4. **Stop 1's first clap** sounds slightly different in v1.3 (production log 52). It is left as delivered and flagged for the human.
5. **M1 lock:** recommended, with the post-filtered v1.3 master as the video's audio. The plan's M1 gate is the human's.

## 41. 2026-11-16 — M1b: the v1.3 whiteboard and the denial tags (agent; for the human)

1. **The board's words:**
   - It writes `incident.json`'s root cause and three factors, the lyric's "tested on smaller machines" under the root cause, and Microsoft's Nov 13 words in quotes.
   - "Lessons learned:" stays blank, as in M5. "Full report:" reads "Nov 20".
   - `incident.json` has no field for the three new strings, so they sit in `Textures.tsx` (`TESTED`, `DENIAL`, `REPORT_DUE`). Branch B drops the quote line; branch C writes "to follow".
2. **No credit line under the quote** (M5's "— Microsoft statement, Nov 13"). Tag 1 comes in on the frame the quote starts and credits and dates it, so a credit on the board would say it twice.
3. **The tags sit where the lower thirds do**, with a leader to a pin on the quote line. They are not beside the line: in O18c the board is small and a panel there would cover the band.
   - In O18d the panel sits 56 px from the bottom, not 110, so that the board's last line stays clear. The step falls on the cut.
4. **"(Not related…)" now lands 9 frames into O18c** (side wide); in v1.2 it fell in O18b (board mid). The cut stays as approved. The pin reads in O18c, and O18d (board close) then shows the whole board with both tags.
   - The alternative is to swap O18b's and O18c's cameras so the tags land on the board-mid framing. Recommendation: keep the cut.
5. **The M7 render gets its own music map** (`timing/music_map_v13.json`). M5c3 keeps `timing/music_map.json`, so M5c3 still reproduces (the PSNR check). Only the lead inside the repainted span differs.
6. **For the human: the fact card's length.** The brief's text is now about 210 words on a 15 s card (`config/shot_cues.json` post-roll). At about 3 words a second that needs about 70 s. Options: lengthen the card (and the video), split it in two, or trim. Not changed.
