# Sandbox Rhapsody kit (vendored)

`sr_kit.py` (commit f77185c) and `sr_anim.py` (commit 9ff2b2a), copied from `../sandbox-rhapsody/scenes/blender/lib/`
on 2026-11-15. One line changed in each: `ROOT` is `parents[2]`, because the files sit at `blender/lib/` here
(`scenes/blender/lib/` there). Colours come from `config/look.json` (Sandbox Rhapsody's palette plus `standby`).

Probes: `probe(name, loc, led_role=…)`.
- Green, Anthropic's (the song's author): `led_role="standby"`, `#5fe39a`, as Not Yet's crib probe.
- Amber, OpenAI's (its connector also broke): `led_role="amber"`, `#ffa21f`. Amber was the agents' colour in Sandbox
  Rhapsody, and those agents were OpenAI's, so this is consistent with the series rather than a clash. Not Yet made
  its probe green to set it apart from those amber agents.

Not Yet vendored the same kit with motion blur added to `setup_render`; take that change from `../not-yet` if needed.
