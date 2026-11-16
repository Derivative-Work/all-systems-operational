# AI changes

Append-only. Anything the generator changed: words sung differently, sections added or dropped, structure.

## 1. 2026-11-15 — Title

- Suno titled the take "Remember Wednesday" (the outro's new tag line); the song is "All Systems Operational" everywhere else.

Lyrics as sung are checked at M1 (WhisperX on the lead and backing stems), deferred until the GPU is free.

## 2. 2026-11-15 — "without fai—" sung whole (M1 transcription)

- The brief cuts the build mid-word ("Ten million voices singing out without fai—"). In the take, "fail" is sung whole: held on about F4 from 93.17 to 93.85 s (WhisperX word timing; lead pitch by yin), then it decays with the band. The stop lands just after the word, not inside it. Stop 2 ("Please stay on the—", "the" ending 201.77 s, silence from 201.80 s) cuts before "line" as written.
- Everything else is sung as written, in order. Section starts (lead stem, WhisperX): intro vocal 7.52 s; verse 1 26.59; pre-chorus echoes 44.77 (backing); chorus 1 55.11; "Five-oh-three" 73.67; build 84.33; "renewed errors" 97.08; verse 2 103.13; chorus 2 about 120.7; bridge 152.02; "Service has been restored" ×2 about 170–180; final chorus 182.38; "Remember Wednesday?" 208.53; outro to "Operational" 234.90.
- Whisper mishearings (not changes): "We are away" (aware), "cause" (Root cause), "Five on three" (backing), "Some users live, experience it" (backing).

## 3. 2026-11-15 — Correction to entry 2: stop 1 is cut at "fai—" (human, by ear)

- The human hears the stop at "fai—", as the brief writes it. Entry 2's "sung whole" came from WhisperX word timing (which pads word ends) and the lead's held pitch, which is the vowel, not a final "l". The stop's timing in production log 7 (band gone at about 93.9 s, three claps, "We're seeing renewed errors" at 97.08 s) is unchanged. No generator change here: the take matches the lyrics.

## 4. 2026-11-15 — O22's Switch OFF (M5b)

- M5's O22 rebuilt the park with its default state, so Switch was back ON in the outro after dropping in O21. M5b swaps in the OFF texture for O22 (blender/coverage.py), so he stays down after the stop. Decisions 13.

## 5. 2026-11-15 — The guitarist and banjo player recast (M5c review 2)

- The board's band was people 3, 8, 12, 17, 22. The guitarist is now person 33 and the banjo player person 36 (decisions 19): the real-size guitar was too big for person 3, and the banjo for person 8. They swap places with 3 and 8 elsewhere, so no position changes: 3 is now O12's late clapper, 8 a treehouse meeting chair.

## 6. 2026-11-16 — M7a look pass: what is new or different on screen (agent)

Relative to the approved M5c3 grey box (decisions 21–24); cameras, cut and performances unchanged.
- **Every set:** procedural materials on everything that was a flat colour; darker values; performers in silhouette against the windows, sky or whiteboard, with rims; the grade (`scripts/grade.py`).
- **Live room:** rain on the five windows (rivulets, beaded drops); daylight shafts in the haze and window-shaped pools on the floor; flat-woven rugs, fabric panels and clouds, a planked floor that reflects the windows. Added: sills under the windows; fader strips, knobs, small amber and green meter LEDs and two dimly lit monitor screens on the host's console (no text or logos); two road cases and an amp at the ends of the window wall; three cable runs along its foot (nobody stands there); a warm spill light high by the door; the ON AIR sign's red spill raised (60 W). Little Switch's plane is untouched.
- **Coffee shop:** red brick walls; steamed windows with clear drip trails; string lights at 14 (emission) with weaker fill; glazed mugs; painted and wood chairs. Added: two warm pendants over the counter, group heads and a drip tray on the (blank) espresso machine, potted plants on the back sills, a small picture light on the Polaroid, and the Polaroid's photo (decisions 24).
- **Treehouse:** the roof turned the right way (decisions 23), so the room is closed and two skylights show rain; cedar boards; firs through the rainy glass; whiteboard markers in the tray; finer moss on the deck's edge and rails; drizzle beyond the back and left windows; a spot over the conference table (the pendant stays off by day).
- **Hilltop park:** conifers in place of cones; a generic skyline massing in fog in place of boxes (no tower, no water); the sun from behind the band, so the crowd and band are silhouettes; wet grass and gravel; a thin fog over the crest; finer drizzle.

## 7. 2026-11-16 — M7b look pass: what is new or different on screen (agent)

Relative to M7a (approved as the base, human interventions 18); cut, performances and every camera but O04a's unchanged (decisions 27–31).
- **Rain on glass** (every pane and skylight): the beads appear, grow and merge; drops slide down in jerks, leaving trails and tiny beads; on the cafe's steamed glass they wipe clear paths.
- **Haze:** its texture drifts slowly, so the shafts move. None at night (O08c had daylight shafts at night in M7a).
- **Steam:** rising, curling wisps over the probes' mugs and about half the cafe's table mugs.
- **O04:** a new framing, closer over the shoulder; the phone shows one big message ("is email down for anyone else?") and the +1 count, readable; the band is no longer in the frame.
- **Treehouse:** the cedar walls, roof and floor show; the band stays in silhouette. New on screen: invented incident-night content on every laptop and phone (a failing sign-in, an automated alert call from a 555 number, a service dashboard, a health-check terminal, an unbranded assistant that can't reach the mail connector, a bridge call); a fourth laptop beside the speakerphone; a phone face up on the table. O18e racks from the dashboard to the whiteboard.
- **Closes:** the instrument closes are a third of a stop brighter.
- **Polaroid:** the band alone, backlit, from nearer the front.

## 8. 2026-11-16 — M7c: what is new or different on screen (agent)

Relative to M7b (approved as the M7 base, human interventions 22). Cut, performances and the closes' cameras are unchanged; the park's wides and O19b's rise are re-aimed (decisions 36).
- **Hilltop park, rebuilt from the hill up** (human interventions 18, 22; decisions 35–37):
  - The ground: a crest lawn rolling to a real brow, the ground falling away beyond it, the slope's firs and bare trees below.
  - The far plate: the city 2–4 km off, its towers in the cloud base, neighbourhoods and wooded ridges in layered fog, generated and extended to about 128°. The 3D skyline massing is gone.
  - The lawn: wet, patchy and trodden near the path, with blades along the brow and the path's edges.
  - A gravel path with granite kerbs, running from the back slope along the walker's line to a new viewpoint terrace, with a short stone wall and a bench at the brow.
  - Puddles on the path and in a few hollows. No standing water body.
  - Fir crowns made of clustered sprays at many angles, in irregular groups: big firs framing the crest, young firs on the back slope, firs on the flanks of the drop. Bare deciduous trees below the brow. A few houses deep in the valley fog.
  - Fog in layers: valley fog below the crest, a drifting near haze, drifting curtains.
  - A cast-iron park lamp with a warm frosted lantern, carrying the same outlet box and Switch.
  - O22d is the generated plate with fog drifting, not a Blender shot.
  - The stray second figure in O22a is gone (decisions 37).
- **Treehouse:** the firs through the windows and from the deck are the new clustered firs (O08c, O18, O19a).
- **Treehouse screens:** the assistant's screen reads "assistant · read-only", with no name or initial; its composer reads "Ask about the logs…".
- **O04:** the question and its +1 count are on the phone from the shot's first frame. The +1 still climbs on the Hey!.
- **Live room:** the crowd's phones show a camera view of the band, a lock screen or the #it-help chat (generic, unreadable at that size) instead of blank white.

## 9. 2026-11-16 — The v1.3 bridge repaint, as sung

- The bridge is sung as lyrics v1.3 writes it, in order. "On the twentieth" is sung; Whisper writes "20th".
- "(We're committed to doing better)" is sung twice: 166.11–168.38 s and 168.39–170.06 s. The brief writes it once; the old bridge sang it once.

## 10. 2026-11-16 — M7d: what is new or different on screen (agent)

Relative to M7c (approved, human interventions 23). Cut times and performances unchanged; every camera unchanged but the banjo closes (decisions 42).
- **Firs** (the park and the treehouse's forest): the same crowns and silhouettes, now shaded as volumes: the side and tops of each crown turned to the sky lighter grey-green, dark deep inside and under each tier, branches varying in value, a fringe of needles at the sprays' edges, branches showing as thin wood through the gaps. At night (O08c) the forest stays dark.
- **The far plate:** at about 22° left of centre the wooded hill now slopes down into horizontal fog banks instead of ending in a vertical bank of fog (an inpaint of the generated plate; the rest of the panorama is as approved).
- **The bare trees below the brow:** fewer fine branches and twigs, slimmer, paler in the fog; the fog shows through them from O20e.
- **O08c:** behind the forest the back windows show a dark night sky, a little lighter than the trees, and dark fir branches against it; the pale flat shapes (the forest floor in daylight fog) are gone; the rain on the panes is fainter at night.
- **The hilltop:** a dark iron railing on the viewpoint terrace's wall; six more firs on the front slope either side of the view, their crowns rising from below the brow; a gravel path with kerbs leaving the terrace over the brow down the front slope (visible from O20e). On the back slope, where O19b's rise ends, the path follows the crest's roll: the flat-topped block at the top of the path is gone.
- **The instrument closes:** a small warm light on the guitar's top in the guitar closes (O09j, O17a), on for those shots only; every banjo close (O09f, O11e, O17f, O20f) now sees the head in three-quarter view from the pot side (it was edge-on from the neck side), with a faint warm light on the live room's.
