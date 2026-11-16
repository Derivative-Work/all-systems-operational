"""M5c: the coverage plan with the repeated closes swapped: config/coverage_m5c.json and docs/coverage_m5c.md.

Reads config/coverage.json (M5b, approved: human interventions 14) and changes only what's inside nine sub-shots:
cut times, frames, lengths and order are copied unchanged (checked below). The human noticed the SESSION 503
kick-head close is used eight times and the tambourine close four; now that hands and instruments perform
(blender/perf_band.py), most repeats become new closes. Kept: O03c and O19c (the kick, where the stomp first comes
in and where it returns) and O17j (the tambourine against the steamed glass).

New camera presets are band-relative ("kind": "band"): loc and target in a band member's figure frame (-Y toward
the room, +X the player's left, metres; blender/coverage_m5c.py resolves them per room). No face in any of them:
hands, the pedal and beater, the back of the singer's head.
Usage: .venv/bin/python -I scripts/coverage_m5c.py
"""
import copy
import json
from pathlib import Path

SRC = json.load(open("config/coverage.json"))

ROOM_CAMS = {
    # Switch on the wall by the door and his conduit up to ON AIR (M5b's spare switch_cord aimed above him)
    "live": {"switch_cord": {"loc": [-4.75, 4.5, 1.7], "target": [-7.0, 3.35, 1.95], "lens": 24, "framing": "close",
                             "what": "Switch on the wall, his conduit up to ON AIR"}},
}

BAND_CAMS = {
    # the beater hitting the batter head, from above the pedal on the player's right, beside the shin
    "close_beater": {"kind": "band", "role": "kick", "loc": [-0.42, -0.36, 0.62], "target": [0.0, -0.7, 0.14],
                     "lens": 35, "framing": "close", "expo": -0.2, "dof": {"focus": [0.0, -0.69, 0.22], "fstop": 2.8},
                     "what": "the kick pedal: the beater hitting the batter head, the foot on the board"},
    # the strumming hand over the sound hole, from below the player's right elbow, the face out of frame
    # (M5c review 2: offsets from the solved strumming hand, so it follows the recast guitarist; same direction)
    "close_strum": {"kind": "band", "role": "guitar", "anchor": "RightHand", "loc": [-0.49, -0.42, -0.14],
                    "target": [0.0, 0.0, 0.0],
                    "lens": 50, "framing": "close", "expo": 0.3, "dof": {"focus": "target", "fstop": 2.0},
                    "what": "the guitar's strumming hand over the sound hole"},
    # the banjo's fretting hand on the neck, from beside the player's head looking down past the hand to the floor
    # (M5c review 2: offsets from the solved fretting hand, so it follows the recast banjo player; same direction)
    "close_fret": {"kind": "band", "role": "banjo", "anchor": "LeftHand", "loc": [-0.29, -0.40, 0.35],
                   "target": [0.0, 0.0, 0.0],
                   "lens": 55, "framing": "close", "expo": -0.6, "dof": {"focus": "target", "fstop": 2.0},
                   "what": "the banjo's fretting hand on the neck"},
    # the lead singer leaning in to the mic, from behind and below the shoulder, looking up past the head at the mic
    # against the dark upper wall (no crowd in frame: from behind the band the crowd is front-lit)
    "lean_back": {"kind": "band", "role": "singer", "loc": [0.28, 0.62, 1.25], "target": [-0.04, -0.45, 1.78],
                  "lens": 40, "framing": "close", "expo": -1.0, "dof": {"focus": [0.0, -0.12, 1.52], "fstop": 2.0},
                  "what": "the singer's lean-in to the mic, from behind"},
    # (replaces M5b's fixed close_tamb, aimed where the tambourine was held up: it's at chest height now)
    "close_tamb": {"kind": "band", "role": "tamb", "loc": [-0.78, -1.25, 0.95], "target": [-0.18, -0.4, 1.2],
                   "lens": 85, "framing": "close", "expo": -0.4, "dof": {"focus": "target", "fstop": 2.0},
                   "what": "the tambourine in the player's hand, backlit"},
}

# sub-shot: (room, camera, move, note)
SWAPS = {
    "O08e": ("live", "close_beater", {"type": "push", "k": 0.05}, "the beater hitting the head: two beats"),
    "O09d": ("live", "lean_back", {"type": "push", "k": 0.04}, "Hey! 3: the singer leans in, from behind"),
    "O09h": ("live", "close_fret", {"type": "truck", "d": [0.0, 0.06, 0.0]}, "the banjo's fretting hand, to the post-chorus"),
    "O11c": ("live", "switch_cord", {"type": "push", "k": 0.08}, "half a bar: Switch on the wall, his conduit up to ON AIR"),
    "O14b": ("cafe", "mug_steam", {"type": "push", "k": 0.04}, "the stomp back: steam off the green probe's mug"),
    "O17a": ("cafe", "close_strum", {"type": "push", "k": 0.04}, "chorus 2's first downbeat: the strumming hand"),
    "O19e": ("park", "close_beater", {"type": "push", "k": 0.08}, "one beat into the final chorus: the beater"),
    "O20d": ("park", "lean_back", {"type": "push", "k": 0.05}, "Hey! 3: the singer leans in, from behind"),
    "O20h": ("park", "close_strum", {"type": "push", "k": 0.08}, "half bar: the strumming hand"),
}


# M5b's closes on the guitar and banjo, fixed in each room: re-centred on the recast player's hand (role, bone,
# figure-frame offset; M5c review 2)
REANCHOR = {"close_guitar": ["guitar", "RightHand", [0.10, 0.0, 0.04]],
            "close_banjo": ["banjo", "RightHand", [0.14, 0.0, 0.04]]}

# other sub-shots whose camera needs a change now that the people move differently: {sub-shot: (override, why)}
ADJUST = {}       # (O20g was re-aimed lower in the first review; it showed the park band's lit faces: back to M5b's)


def main():
    out = copy.deepcopy(SRC)
    out["generated_by"] = "scripts/coverage_m5c.py (from config/coverage.json, M5b)"
    for room in ("live", "cafe", "park", "treehouse"):
        out["cameras"].setdefault(room, {})
        for k, v in BAND_CAMS.items():
            out["cameras"][room][k] = v
        for k, v in ROOM_CAMS.get(room, {}).items():
            out["cameras"][room][k] = v
    # M5c review 2: M5b's fixed guitar and banjo closes follow the recast players' hands (same direction, distance)
    for room, cams in out["cameras"].items():
        for k, v in REANCHOR.items():
            if k in cams:
                cams[k] = {**cams[k], "reanchor": v}
    rows = []
    for s in out["subs"]:
        if s["id"] in SWAPS:
            room, cam, mv, note = SWAPS[s["id"]]
            assert s["room"] == room and cam in out["cameras"][room], (s["id"], room, cam)
            old = s["camera"]
            c = out["cameras"][room][cam]
            s["m5b_camera"] = old
            if s.pop("cam_override", None) is not None:
                s["m5b_cam_override"] = True
            s["camera"], s["move"], s["note"] = cam, mv, note
            s["lens"] = c.get("lens", s.get("lens"))
            s["framing"] = c.get("framing", s["framing"])
            rows.append((s["id"], s["section"], f"{s['start_t']:.2f}–{s['end_t']:.2f}", s["seconds"], old, cam,
                         c["what"], note))
    for s in out["subs"]:
        if s["id"] in ADJUST:
            ov, why = ADJUST[s["id"]]
            s["cam_override"] = {**(s.get("cam_override") or {}), **ov}
            rows.append((s["id"], s["section"], f"{s['start_t']:.2f}–{s['end_t']:.2f}", s["seconds"], s["camera"],
                         s["camera"] + " (re-aimed)", why, s["note"]))
    # nothing but the swapped sub-shots' cameras changes: same ids, cuts, frames, order
    keys = ("id", "shot", "build", "room", "source", "start_t", "end_t", "start_frame", "end_frame", "frames", "snap",
            "covers", "section")
    for a, b in zip(SRC["subs"], out["subs"]):
        for k in keys:
            assert a.get(k) == b.get(k), (a["id"], k)
    assert len(SRC["subs"]) == len(out["subs"])
    Path("config/coverage_m5c.json").write_text(json.dumps(out, indent=1))
    kick = [s["id"] for s in out["subs"] if s.get("camera") == "close_kick"]
    tamb = [s["id"] for s in out["subs"] if s.get("camera") == "close_tamb"]
    L = ["# Coverage plan, M5c swaps", "",
         "Generated by `scripts/coverage_m5c.py` from `config/coverage.json` (M5b, `docs/coverage.md`); the data is "
         "`config/coverage_m5c.json`. Same 94 shots, cut times and frames as M5b; only these sub-shots' cameras "
         "change. Rendered by `blender/coverage_m5c.py`.", "",
         "| Sub-shot | Section | Song time | Length | M5b camera | M5c camera | What | Note |",
         "| --- | --- | --- | --- | --- | --- | --- | --- |"]
    L += [f"| {r[0]} | {r[1]} | {r[2]} | {r[3]:.2f} s | {r[4]} | {r[5]} | {r[6]} | {r[7]} |" for r in rows]
    L += ["", f"The kick-head close is now in {len(kick)} sub-shots ({', '.join(kick)}; M5b: 8); the tambourine close "
          f"in {len(tamb)} ({', '.join(tamb)}; M5b: 4).", "",
          "Unused spare: the treehouse skylight (no repeated close falls in a treehouse shot)."]
    Path("docs/coverage_m5c.md").write_text("\n".join(L) + "\n")
    print(f"config/coverage_m5c.json: {len(SWAPS)} swaps, {len(ADJUST)} re-aimed; kick closes {kick}; tambourine closes {tamb}")


if __name__ == "__main__":
    main()
