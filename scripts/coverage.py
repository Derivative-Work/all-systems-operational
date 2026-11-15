"""M5b: the coverage plan. Splits each O-shot into sub-shots (O09a, O09b ...) with a camera, a move and a cut snapped
to the music (timing/music_map.json, timing/shot_times.json): config/coverage.json and the readable table
docs/coverage.md (plan M5b; decisions 12).

Rules (from the human's note, human interventions 13, and the plan):
- Choruses (and the stomp-clap instrumental) cut every 1-2 bars, on downbeats or Hey!s; verses every 2-4 bars; the
  cuts speed up through each build into its stop (bars, then half bars, then beats); the freezes (O12, O21) hold one
  angle. The O-shot boundaries stay on the M2 cues (approved, human interventions 9).
- The Remotion shots (O01, O02, O05, O13, O23, O24, the cards), O06's clip, O07 and O10 stay one shot each; O08's
  inserts (IT's reply, the treehouse cutaway) stay where M5 put them (decisions 11).
- Every cued event (Switch, ON AIR, the LED, the string lights, the whiteboard lines, the mugs, the disclosure panel,
  the lower thirds) falls in a sub-shot whose camera shows it; each sub-shot lists the marks it covers.
- Closes never show a face: hands, the kick foot and the SESSION 503 head, the banjo neck, the tambourine, mugs,
  rain on glass, ON AIR, Switch and his conduit, backs of heads, backlit profiles. Cameras sit on the audience side
  looking toward the windows (the backlight), so no reverse angle shows a lit face.
- Not any one famous stomp-clap video's look: no single-take walk-through, no lens-flare wash, no barn or field band
  in a line; the coverage is the live-session pattern the brief names (wide to close, cutting on the music).
Cameras are presets per room (`CAMS`): a fixed position and target, a crowd member found by pose near a point
(kind "person": a close on their hands, mug or the back of their head), or the walker, tracked (O22). blender/
coverage.py renders them with handheld drift, kick bumps, the moves and rack focus listed here.
Cut spec: "S" the shot's start; "bar:N" the downbeat of bar N; "beat:N.b" bar N beat b; "hey:T" the Hey! nearest T s;
"mark:K" the shot's M2 mark K (a sung word); "f:K" frame K of the shot (only for M5's insert and dissolve
boundaries). Every cut is checked against the grid.
Usage: .venv/bin/python -I scripts/coverage.py
"""
import json
from pathlib import Path

TS = json.load(open("timing/shot_times.json"))
SH = TS["shots"]
MM = json.load(open("timing/music_map.json"))
TM = json.load(open("timing/timing_map.json"))
LEAD, FPS = TS["lead_in_s"], 30
BEATS = TM["beats"]["beats"]
BIB, BARNO = TM["beats"]["beat_in_bar"], TM["beats"]["bar"]
HEYS = [h["t"] for h in MM["heys"]]
WEAK = {h["t"] for h in MM["heys"] if h["weak"]}

# ---------------------------------------------------------------- camera presets (metres; rooms as blender/sets.py)
# framing: wide | mid | close. dof: focus target ("target" or a point) and f-stop; None = no depth of field.
# target_obj: aim at that object's centre (the tambourine moves with its player).
# expo: exposure offset (stops) for the angles nearest the band and crowd, so the silhouettes stay dark in a close.
CAMS = {
    "live": {
        "wide_back": dict(loc=[2.2, 0.5, 2.0], target=[-0.3, 8.5, 1.5], lens=24, framing="wide",
                          what="the M3 board's O03 wide: room, windows, band, crowd"),
        "wide_high": dict(loc=[0.0, 2.2, 2.9], target=[0.0, 8.2, 1.0], lens=30, framing="wide",
                          what="the board's O09 wide down the aisle: the SESSION 503 head"),
        "wide_left": dict(loc=[-5.6, 1.4, 2.5], target=[0.6, 7.9, 1.3], lens=22, framing="wide",
                          what="wide from the front left corner, crowd and band against all five windows"),
        "mid_band": dict(expo=-1.2, loc=[0.9, 4.15, 1.62], target=[0.1, 8.0, 1.35], lens=40, framing="mid",
                         dof=dict(focus=[0.6, 5.2, 1.6], fstop=2.8),
                         what="the band, soft, over the crowd's shoulders (focus on the heads in front)"),
        "crush": dict(loc=[0.6, 3.2, 1.55], target=[0.0, 8.4, 1.7], lens=30, framing="wide",
                      what="the board's O11: the crowd crushed at the mics"),
        "close_kick": dict(loc=[-0.9, 6.6, 0.42], target=[-0.05, 7.7, 0.3], lens=35, framing="close",
                           dof=dict(focus="target", fstop=2.0), what="the kick foot on the pedal side and the SESSION 503 head"),
        "close_hands": dict(expo=-0.5, kind="person", pose="clap", near=[0.6, 5.2], part="hands", side=0.85, lens=50,
                            framing="close", dof=dict(focus="target", fstop=2.0),
                            what="a clapper's hands, side-on against the windows (chin down out of frame)"),
        "close_hands2": dict(expo=-0.5, kind="person", pose="clap", near=[2.2, 4.5], part="hands", side=0.85, lens=50,
                             framing="close", dof=dict(focus="target", fstop=2.0),
                             what="another clapper's hands, from the other side"),
        "close_banjo": dict(expo=-0.8, loc=[2.05, 6.95, 1.12], target=[0.95, 7.5, 1.08], lens=50, framing="close",
                            dof=dict(focus="target", fstop=2.0), what="the banjo's neck and the strumming hand"),
        "close_tamb": dict(expo=-0.4, target_obj="tambourine", loc=[-2.75, 7.05, 1.35], target=[-1.85, 8.05, 1.92], lens=85, framing="close",
                           dof=dict(focus="target", fstop=2.0), what="the tambourine, backlit by a window"),
        "backs": dict(expo=-0.3, kind="person", pose="any", near=[0.0, 5.6], part="back", lens=45, framing="close",
                      dof=dict(focus="person", fstop=2.0, rack_to=[0.4, 10.0, 2.4]), aim=[0.0, 7.9, 1.4],
                      what="the back of a head, racking past the band to the rain on the glass"),
        "rain": dict(expo=-1.3, loc=[2.3, 9.05, 2.2], target=[2.75, 10.0, 2.55], lens=32, framing="close",
                     dof=dict(focus="target", fstop=2.8), what="rain on a window behind the band"),
        "close_guitar": dict(expo=-0.7, loc=[0.15, 6.75, 1.1], target=[-0.9, 7.6, 1.05], lens=50, framing="close",
                             dof=dict(focus="target", fstop=2.0), what="the acoustic guitar's body and strumming hand"),
        "onair": dict(loc=[-5.7, 2.45, 2.35], target=[-7.0, 2.8, 2.72], lens=35, framing="close",
                      what="the ON AIR sign over the door"),
        "switch_cord": dict(loc=[-5.85, 3.65, 1.8], target=[-7.0, 3.3, 1.95], lens=26, framing="close",
                            what="Switch on the wall, his conduit up to ON AIR"),
        "console": dict(loc=[5.75, 1.55, 1.75], target=[2.2, 7.6, 1.15], lens=35, framing="mid",
                        dof=dict(focus=[4.75, 2.9, 1.3], fstop=2.8, rack_to=[0.5, 7.7, 1.3]),
                        what="over the host's shoulder: the mixer, the band beyond against the windows"),
        "board:O04": dict(board="O04", framing="close", what="M5's O04 over-shoulder phone (screen pinned in the edit)"),
        "board:O08": dict(board="O08", framing="mid", what="the board's O08: the host's silhouette at the console"),
        "board:O10": dict(board="O10", framing="mid", what="the board's O10: Switch by the door, ON AIR"),
        "board:O12c": dict(board="O12c", framing="mid", what="M5's O12 freeze camera (the late clapper)"),
    },
    "treehouse": {
        "board:O08c": dict(board="O08c", framing="wide", what="M5's O08 cutaway: the treehouse at night"),
        "wide": dict(loc=[0.25, 0.35, 1.75], target=[0.05, 6.0, 1.65], lens=28, framing="wide",
                     what="the board's O18: the band before the whiteboard"),
        "board_mid": dict(expo=-0.8, loc=[-0.95, 1.4, 1.8], target=[0.1, 5.98, 1.9], lens=38, framing="mid",
                          what="the whiteboard over the band's shoulders"),
        "side": dict(expo=-0.7, loc=[-2.9, 1.15, 1.7], target=[0.6, 5.4, 1.6], lens=26, framing="wide",
                     what="from the far corner: the table, the band in profile, the whiteboard"),
        "board_close": dict(loc=[0.95, 5.3, 1.7], target=[0.25, 5.98, 1.75], lens=26, framing="close",
                            what="close on the whiteboard's lines, a shoulder at the edge"),
        "table": dict(expo=-0.5, loc=[1.55, 1.35, 1.2], target=[0.4, 2.6, 0.8], lens=35, framing="close",
                      dof=dict(focus=[0.55, 2.55, 0.78], fstop=2.0, rack_to=[0.1, 5.98, 1.8]),
                      what="the speakerphone and the chargers, racking to the whiteboard"),
        "skylight": dict(loc=[-0.9, 4.0, 1.75], target=[-1.6, 5.25, 3.1], lens=30, framing="close",
                         what="rain on a skylight over the band"),
        "o19a": dict(m5="O19a", framing="wide", what="M5's O19a move: the door opens, out onto the deck and up"),
    },
    "cafe": {
        "wide": dict(loc=[0.5, 1.2, 1.9], target=[-0.4, 8.0, 1.5], lens=26, framing="wide",
                     what="the board's O17: the crowd, the band, the steamed windows"),
        "wide_side": dict(loc=[4.6, 1.3, 2.35], target=[-1.0, 7.4, 1.35], lens=24, framing="wide",
                          what="wide from the right front corner over the tables"),
        "wide_high": dict(loc=[-4.2, 1.1, 2.9], target=[0.0, 7.0, 1.2], lens=22, framing="wide",
                          what="high wide from the counter side, the string lights overhead"),
        "probes": dict(board="O14", framing="mid", what="the board's O14: the probes, the table tent, the Polaroid"),
        "probe_close": dict(board="O15", framing="close", what="the board's O15: the green probe"),
        "strands": dict(board="O16", framing="wide", what="the board's O16: the string lights"),
        "tent": dict(loc=[4.3, 2.92, 0.88], target=[4.83, 3.0, 0.8], lens=55, framing="close",
                     dof=dict(focus="target", fstop=2.2), what="the table tent: connector unavailable"),
        "polaroid": dict(loc=[5.05, 2.35, 1.25], target=[5.99, 3.0, 1.35], lens=35, framing="close",
                         what="the Polaroid on the pier, the probes below"),
        "mug_steam": dict(loc=[4.2, 2.3, 0.93], target=[4.73, 2.63, 0.84], lens=60, framing="close",
                          dof=dict(focus="target", fstop=2.0), what="steam off the green probe's mug"),
        "hub": dict(loc=[-0.7, 3.1, 2.0], target=[0.4, 4.6, 3.3], lens=35, framing="close",
                    dof=dict(focus=[0.4, 4.6, 3.37], fstop=2.8), what="the hub bulb and the strands leaving it"),
        "close_kick": dict(loc=[-1.3, 6.3, 0.42], target=[-0.45, 7.4, 0.3], lens=35, framing="close",
                           dof=dict(focus="target", fstop=2.0), what="the kick foot on the pedal side and the SESSION 503 head"),
        "close_banjo": dict(expo=-0.8, loc=[1.55, 6.65, 1.12], target=[0.46, 7.2, 1.08], lens=50, framing="close",
                            dof=dict(focus="target", fstop=2.0), what="the banjo's neck and hands"),
        "close_tamb": dict(expo=-0.4, target_obj="tambourine", loc=[-3.05, 6.85, 1.35], target=[-2.15, 7.75, 1.92], lens=85, framing="close",
                           dof=dict(focus="target", fstop=2.0), what="the tambourine against the steamed glass"),
        "close_hands": dict(expo=-0.5, kind="person", pose="clap", near=[0.6, 5.3], part="hands", side=0.85, lens=50,
                            framing="close", dof=dict(focus="target", fstop=2.0), what="a clapper's hands"),
        "mugs_backs": dict(expo=-0.3, loc=[-0.85, 3.75, 1.75], target=[-0.5, 8.5, 2.0], lens=40, framing="mid",
                           dof=dict(focus=[-0.6, 5.3, 1.9], fstop=2.8, rack_to=[-0.5, 9.0, 2.0]),
                           what="raised mugs against the steamed windows, from behind, racking to the glass"),
        "backs": dict(expo=-0.3, kind="person", pose="any", near=[-1.0, 5.6], part="back", lens=45, framing="close",
                      dof=dict(focus="person", fstop=1.8), aim=[-0.4, 7.5, 1.4],
                      what="the back of a head, the band soft beyond (no rack: the cafe band's faces are side-lit)"),
        "mid_band": dict(expo=-1.2, loc=[0.5, 3.95, 1.6], target=[-0.4, 7.6, 1.35], lens=40, framing="mid",
                         dof=dict(focus=[0.2, 5.0, 1.6], fstop=2.8),
                         what="the band, soft, over the crowd's shoulders (focus on the heads in front)"),
    },
    "park": {
        "wide": dict(board="O20", framing="wide", what="the board's O20: the singalong from behind the crowd"),
        "wide_high": dict(loc=[-6.5, -5.5, 4.6], target=[0.0, 4.0, 0.8], lens=24, framing="wide",
                          what="high wide over the crowd to the band and the skyline in fog"),
        "close_kick": dict(loc=[-0.9, 4.7, 0.42], target=[-0.05, 5.8, 0.3], lens=35, framing="close",
                           dof=dict(focus="target", fstop=2.0), what="the kick foot on the pedal side and the SESSION 503 head"),
        "close_hands": dict(expo=-0.5, kind="person", pose="clap", near=[0.5, 2.6], part="hands", side=0.85, lens=50,
                            framing="close", dof=dict(focus="target", fstop=2.0), what="a clapper's hands in the drizzle"),
        "close_banjo": dict(expo=-0.8, loc=[2.05, 4.95, 1.1], target=[0.95, 5.6, 1.06], lens=50, framing="close",
                            dof=dict(focus="target", fstop=2.0), what="the banjo against the fog"),
        "close_tamb": dict(expo=-0.4, target_obj="tambourine", loc=[-2.75, 5.05, 1.35], target=[-1.85, 6.15, 1.92], lens=85, framing="close",
                           dof=dict(focus="target", fstop=2.0), what="the tambourine against the sky"),
        "umbrella": dict(loc=[2.75, 0.05, 1.85], target=[1.85, 1.4, 2.25], lens=40, framing="close",
                         dof=dict(focus=[1.9, 1.3, 2.2], fstop=2.8), what="the one umbrella, turning"),
        "backs": dict(expo=-0.3, kind="person", pose="any", near=[0.0, 2.9], part="back", lens=45, framing="close",
                      dof=dict(focus="person", fstop=2.0, rack_to=[2.5, 80.0, 12.0]), aim=[2.5, 30.0, 7.5],
                      what="the back of a head against the fog and the skyline, the band out of frame (its faces are lit)"),
        "switch": dict(loc=[3.05, -3.75, 1.4], target=[2.7, -2.77, 1.12], lens=35, framing="close",
                       what="Switch on the lamp post's outlet box"),
        "o21": dict(loc=[1.0, -6.1, 1.62], target=[0.3, 6.0, 2.0], lens=28, framing="wide",
                    what="M5's O21 freeze camera (O20's last), the lamp post and Switch in frame"),
        "empty": dict(board="O22", framing="wide", what="the board's O22: the emptied park"),
        "walker_feet": dict(kind="walker", part="feet", lens=40, framing="close",
                            dof=dict(focus="person", fstop=2.0), what="the walker's feet on the gravel, tracked"),
        "walker_back": dict(kind="walker", part="back", lens=50, framing="mid",
                            dof=dict(focus="person", fstop=2.8), what="the walker from behind, tracked"),
        "skyline": dict(loc=[-1.0, -1.5, 1.65], target=[8.0, 430.0, 30.0], lens=60, framing="wide",
                        what="the fog over the generic skyline, drifting"),
        "lamp_rain": dict(expo=-0.8, loc=[1.95, -4.3, 3.0], target=[2.7, -2.6, 3.75], lens=35, framing="close",
                          what="drizzle past the lamp"),
        "o19b": dict(m5="O19b", framing="wide", what="M5's O19b move: rising over the crest to the crowd"),
    },
    "void": {"board:O07": dict(board="O07", framing="mid", what="M5's O07: the server on chroma green")},
}

# ---------------------------------------------------------------- the plan
# shot: (room, [(suffix, cut spec, camera, move, note)]). move: {"type": "push", "k": fraction toward the target} |
# {"type": "truck", "d": [dx, dy, dz]} | {"type": "m5"} (M5's own keys) | {"type": "hold"} | {"type": "track"};
# "speed" scales the move in the builds.
P = {
    "O03": ("live", [
        ("a", "S", "wide_back", {"type": "push", "k": 0.05}, "intro vocal; lower third in"),
        ("b", "bar:6", "rain", {"type": "truck", "d": [0.25, 0, 0.05]}, "rain on glass, two bars before the stomp"),
        ("c", "bar:8", "close_kick", {"type": "push", "k": 0.04}, "first full stomp bar"),
        ("d", "bar:9", "close_hands", {"type": "truck", "d": [0.0, 0.1, 0]}, "the claps"),
        ("e", "bar:10", "mid_band", {"type": "push", "k": 0.06}, "band over the crowd"),
        ("f", "bar:11", "wide_high", {"type": "push", "k": 0.05}, "wide into verse 1"),
    ]),
    "O04": ("live", [("a", "S", "board:O04", {"type": "m5"}, "M5's phone shot (screen pinned in the edit)")]),
    "O07": ("void", [("a", "S", "board:O07", {"type": "m5"}, "M5's server on green")]),
    "O08": ("live", [
        ("a", "S", "board:O08", {"type": "m5"}, "host at the console; 'We are aware'"),
        ("b", "f:45", "insert:phone", None, "IT's reply (Remotion insert, M5), echo 1 to echo 2"),
        ("c", "f:115", "insert:O08c", {"type": "m5"}, "treehouse cutaway (dramatization), 4 beats"),
        ("d", "f:187", "console", {"type": "push", "k": 0.06}, "back to the host; 'Everything'"),
        ("e", "bar:23", "close_kick", {"type": "push", "k": 0.05}, "the pre-chorus's last bar: two beats"),
        ("f", "beat:23.3", "close_hands", {"type": "push", "k": 0.05}, "one beat"),
        ("g", "beat:23.4", "backs", {"type": "push", "k": 0.08}, "one beat, into the chorus"),
    ]),
    "O09": ("live", [
        ("a", "S", "wide_high", {"type": "push", "k": 0.05}, "chorus 1: the SESSION 503 head down the aisle"),
        ("b", "bar:25", "close_hands", {"type": "truck", "d": [0.0, 0.12, 0]}, "the claps, to Hey! 2"),
        ("c", "hey:59.53", "mid_band", {"type": "push", "k": 0.07}, "Hey! 2 to Hey! 3"),
        ("d", "hey:62.24", "close_kick", {"type": "push", "k": 0.04}, "Hey! 3 to Hey! 4"),
        ("e", "hey:64.35", "wide_left", {"type": "truck", "d": [0.4, 0.2, 0]}, "Hey! 4: the whole room"),
        ("f", "bar:29", "close_banjo", {"type": "truck", "d": [-0.06, 0.06, 0]}, "banjo"),
        ("g", "bar:30", "backs", {"type": "push", "k": 0.05}, "backs of heads, racking to the band"),
        ("h", "bar:31", "close_tamb", {"type": "push", "k": 0.04}, "tambourine, to the post-chorus"),
        ("i", "bar:32", "wide_back", {"type": "push", "k": 0.06}, "post-chorus 'Five-oh-three'"),
        ("j", "bar:33", "close_guitar", {"type": "truck", "d": [0.06, 0.08, 0.0]}, "the guitar"),
        ("k", "bar:34", "close_hands2", {"type": "truck", "d": [0.0, 0.1, 0]}, "hands"),
        ("l", "bar:35", "rain", {"type": "truck", "d": [-0.2, 0, 0]}, "rain on glass into the build"),
    ]),
    "O10": ("live", [("a", "S", "board:O10", {"type": "push", "k": 0.1}, "Switch ON, ON AIR lit (M5)")]),
    "O11": ("live", [
        ("a", "S", "crush", {"type": "push", "k": 0.08, "speed": 1.4}, "the crush; viewer count"),
        ("b", "hey:88.69", "close_hands", {"type": "push", "k": 0.06}, "Hey!: hands"),
        ("c", "beat:38.3", "close_kick", {"type": "push", "k": 0.08}, "half a bar of kick",
         {"loc": [0.9, 7.15, 0.45], "target": [0.0, 7.42, 0.36], "lens": 35}),
        ("d", "hey:91.04", "backs", {"type": "push", "k": 0.1}, "Hey!: chat floods"),
        ("e", "beat:39.2", "close_banjo", {"type": "push", "k": 0.08}, "one beat"),
        ("f", "beat:39.3", "mid_band", {"type": "push", "k": 0.12}, "one beat"),
        ("g", "beat:39.4", "onair", {"type": "push", "k": 0.1}, "ON AIR flickers on 'fai—'"),
    ]),
    "O12": ("live", [("a", "S", "board:O12c", {"type": "hold"}, "the freeze: one angle, one frame held but the clapper")]),
    "O14": ("cafe", [
        ("a", "S", "wide", {"type": "push", "k": 0.05}, "the band comes back, in the cafe"),
        ("b", "bar:43", "close_kick", {"type": "push", "k": 0.04}, "the stomp back"),
        ("c", "bar:44", "probes", {"type": "push", "k": 0.06}, "'The agents that we hired': probes, tent, Polaroid"),
        ("d", "bar:46", "polaroid", {"type": "truck", "d": [0.0, 0.15, 0.0]}, "the Polaroid, Wed 11/11"),
        ("e", "bar:47", "tent", {"type": "push", "k": 0.05}, "connector unavailable"),
    ]),
    "O15": ("cafe", [("a", "S", "probe_close", {"type": "push", "k": 0.08}, "the LED dims and comes back")]),
    "O16": ("cafe", [
        ("a", "S", "hub", {"type": "push", "k": 0.05}, "the hub bulb goes out"),
        ("b", "bar:51", "strands", {"type": "m5"}, "the dark runs down every strand"),
    ]),
    "O17": ("cafe", [
        ("a", "S", "close_kick", {"type": "push", "k": 0.04}, "chorus 2's first downbeat; disclosure panel in"),
        ("b", "hey:124.69", "wide", {"type": "push", "k": 0.05}, "Hey! 1: mugs up"),
        ("c", "hey:126.86", "mugs_backs", {"type": "push", "k": 0.05}, "Hey! 2: mugs against the glass"),
        ("d", "hey:129.24", "wide_side", {"type": "truck", "d": [-0.3, 0.2, 0]}, "Hey! 3: mugs up"),
        ("e", "hey:131.60", "mugs_backs", {"type": "push", "k": 0.05}, "Hey! 4: mugs up, from the other side",
         {"loc": [1.0, 3.8, 1.75], "target": [0.3, 8.5, 2.0]}),
        ("f", "bar:57", "close_banjo", {"type": "truck", "d": [-0.05, 0.06, 0]}, "banjo"),
        ("g", "bar:58", "backs", {"type": "push", "k": 0.05}, "backs, racking to the band"),
        ("h", "bar:59", "close_hands", {"type": "truck", "d": [0, 0.1, 0]}, "hands, to the post-chorus"),
        ("i", "mark:4", "wide_high", {"type": "push", "k": 0.06}, "post-chorus 'Five-oh-three'"),
        ("j", "bar:61", "close_tamb", {"type": "push", "k": 0.04}, "tambourine"),
        ("k", "bar:62", "strands", {"type": "push", "k": 0.06}, "the string lights chasing the melody"),
        ("l", "bar:63", "mid_band", {"type": "push", "k": 0.08}, "into the bridge"),
    ]),
    "O18": ("treehouse", [
        ("a", "S", "wide", {"type": "push", "k": 0.04}, "half-time; root cause, an earlier upgrade, a recent change"),
        ("b", "bar:66", "board_mid", {"type": "truck", "d": [0.25, 0, 0]}, "contributing factors; not related ..."),
        ("c", "bar:68", "side", {"type": "push", "k": 0.05}, "full report, to follow, lessons learned"),
        ("d", "bar:70", "board_close", {"type": "truck", "d": [-0.2, 0, 0]}, "we're committed ..."),
        ("e", "bar:71", "table", {"type": "push", "k": 0.04}, "the speakerphone and chargers, racking to the board"),
    ]),
    "O19": ("park", [
        ("a", "S", "o19a", {"type": "m5"}, "the door opens; light breaks through on 'Service has been restored'"),
        ("b", "f:175", "o19b", {"type": "m5"}, "dissolve (10 frames, M5) into the rise over the crest"),
        ("c", "bar:76", "close_kick", {"type": "push", "k": 0.06, "speed": 1.4}, "stomps return: two beats"),
        ("d", "beat:76.3", "close_hands", {"type": "push", "k": 0.06}, "one beat"),
        ("e", "beat:76.4", "close_tamb", {"type": "push", "k": 0.08}, "one beat, into the final chorus"),
    ]),
    "O20": ("park", [
        ("a", "S", "wide", {"type": "push", "k": 0.04}, "final chorus, the whole hill"),
        ("b", "hey:184.71", "close_hands", {"type": "truck", "d": [0, 0.12, 0]}, "Hey! 1: hands"),
        ("c", "bar:79", "umbrella", {"type": "truck", "d": [-0.15, 0.05, 0]}, "the one umbrella"),
        ("d", "hey:189.51", "close_kick", {"type": "push", "k": 0.05}, "Hey! 3: kick"),
        ("e", "hey:191.61", "wide_high", {"type": "truck", "d": [0.8, 0.4, 0.3]}, "Hey! 4: high wide"),
        ("f", "bar:82", "close_banjo", {"type": "truck", "d": [-0.06, 0.06, 0]}, "banjo"),
        ("g", "bar:83", "backs", {"type": "push", "k": 0.08, "speed": 1.3}, "half bar: backs"),
        ("h", "beat:83.3", "close_tamb", {"type": "push", "k": 0.08}, "half bar: tambourine"),
        ("i", "bar:84", "switch", {"type": "push", "k": 0.1}, "half bar: Switch strains, the lamp flickers"),
        ("j", "beat:84.3", "o21", {"type": "hold"}, "half bar: O21's angle, so the freeze holds the same frame"),
    ]),
    "O21": ("park", [("a", "S", "o21", {"type": "hold"}, "the freeze: Switch holds one beat, then drops")]),
    "O22": ("park", [
        ("a", "S", "empty", {"type": "push", "k": 0.04}, "the park empties; the whistle"),
        ("b", "bar:87", "switch", {"type": "push", "k": 0.05}, "Switch, off; 'Remember Wednesday?' (grade in)"),
        ("c", "bar:89", "walker_feet", {"type": "track"}, "the walker's feet on the gravel"),
        ("d", "bar:91", "skyline", {"type": "truck", "d": [0.6, 0, 0]}, "fog drifting over the skyline"),
        ("e", "bar:93", "walker_back", {"type": "track"}, "the walker from behind; the apology lower third"),
        ("f", "bar:95", "empty", {"type": "push", "k": 0.08}, "the hill, the walker near the crest"),
        ("g", "bar:97", "lamp_rain", {"type": "push", "k": 0.05}, "drizzle past the lamp; 'All systems'"),
    ]),
}
REMOTION = {"O01": "Remotion bookend (spike, real screenshots, chat post)", "O02": "Remotion status page",
            "O05": "Remotion calendar", "O06": "clip O06_s41 (M4)", "O13": "Remotion card, then the status page",
            "O23": "Remotion status page"}
END = [("O24-end", "O24 end card", 180), ("O24-final", "O24 'Next incident: TBD'", 90), ("fact", "fact card", 450),
       ("disclosure", "full disclosure card", None)]
BUILDS = {"O08c": "treehouse", "O19a": "treehouse", "O19b": "park"}


def vframe(t):
    return int(round((t + LEAD) * FPS))


def bar_start(n):
    return next(t for t, b, bb in zip(BEATS, BIB, BARNO) if bb == n and b == 1)


def resolve(spec, sid):
    s = SH[sid]
    if spec == "S":
        return s["song_start"], s["start_frame"], "shot start (M2 cue)"
    kind, v = spec.split(":")
    if kind == "bar":
        t = bar_start(int(v))
        return t, vframe(t), f"downbeat, bar {v}"
    if kind == "beat":
        n, b = (int(x) for x in v.split("."))
        t = next(tt for tt, bi, bb in zip(BEATS, BIB, BARNO) if bb == n and bi == b)
        return t, vframe(t), f"beat {n}.{b}"
    if kind == "hey":
        t = min(HEYS, key=lambda h: abs(h - float(v)))
        assert abs(t - float(v)) < 0.05, (spec, t)
        return t, vframe(t), f"Hey! {t:.2f}" + (" (weak)" if t in WEAK else "")
    if kind == "mark":
        m = s["marks"][int(v)]
        f = s["start_frame"] + m["frame_in_shot"]
        i = min(range(len(BEATS)), key=lambda k: abs(BEATS[k] - m["song_t"]))
        return m["song_t"], f, f"on the sung word ({m['what'][:28]}; {(m['song_t'] - BEATS[i]) * 1000:+.0f} ms from beat {BARNO[i]}.{BIB[i]})"
    if kind == "f":
        f = s["start_frame"] + int(v)
        return round(f / FPS - LEAD, 3), f, f"frame {v} of {sid} (M5 insert/dissolve)"
    raise ValueError(spec)


def build_of(sid, suffix, cam):
    if sid == "O08" and suffix == "c":
        return "O08c"
    if sid == "O19":
        return "O19a" if suffix == "a" else "O19b"
    return sid


def main():
    subs = []
    order = sorted([k for k in SH if k != "O24"], key=lambda k: SH[k]["start_frame"])
    for sid in order:
        s = SH[sid]
        if sid in REMOTION:
            subs.append(dict(id=sid, shot=sid, source="remotion" if sid != "O06" else "clip", camera=None,
                             framing="screen" if sid != "O06" else "close", start_t=s["song_start"],
                             end_t=s["song_end"], start_frame=s["start_frame"], end_frame=s["end_frame"],
                             snap="shot start (M2 cue)", note=REMOTION[sid]))
            continue
        room, plan = P[sid]
        cuts = [resolve(c[1], sid) for c in plan]
        for k, (suf, spec, cam, move, note, *over) in enumerate(plan):
            t0, f0, snap = cuts[k]
            t1, f1 = (cuts[k + 1][0], cuts[k + 1][1]) if k + 1 < len(plan) else (s["song_end"], s["end_frame"])
            b = build_of(sid, suf, cam)
            r = BUILDS.get(b, room)
            src = "remotion-insert" if cam == "insert:phone" else "blender"
            cname = "board:O08c" if cam == "insert:O08c" else cam
            c = CAMS[r].get(cname) if src == "blender" else None
            if src == "blender" and c is None:
                raise KeyError(f"{sid}{suf}: no camera {cname} in {r}")
            sub = dict(id=sid + suf, shot=sid, build=b, room=r, source=src, camera=cname if c else None,
                       framing=c["framing"] if c else "screen", lens=c.get("lens") if c else None,
                       move=move, start_t=round(t0, 3), end_t=round(t1, 3), start_frame=f0, end_frame=f1,
                       snap=snap, note=note)
            if over:
                sub["cam_override"] = over[0]
            if sid == "O19" and suf == "b":
                sub["xfade_in"] = 10                       # O19a's last 10 frames dissolve into it (M5)
            subs.append(sub)
    # the end sequence (after O23, as in M5)
    f = SH["O24"]["start_frame"]
    dis = TS["overlays"]["disclosure"]["end_frame"] - TS["overlays"]["disclosure"]["start_frame"]
    for cid, what, n in END:
        n = n or dis
        subs.append(dict(id=cid, shot="O24" if cid.startswith("O24") else cid, source="remotion", camera=None,
                         framing="screen", start_frame=f, end_frame=f + n, snap="end sequence (M5)", note=what))
        f += n
    # marks covered, lengths, checks
    for x in subs:
        x["frames"] = x["end_frame"] - x["start_frame"]
        x["seconds"] = round(x["frames"] / FPS, 2)
        sh = SH.get(x["shot"])
        x["covers"] = [m["what"] for m in (sh or {}).get("marks", [])
                       if sh and x["start_frame"] <= sh["start_frame"] + m["frame_in_shot"] < x["end_frame"]]
        assert x["frames"] > 0, x["id"]
    for a, b in zip(subs, subs[1:]):
        assert a["end_frame"] == b["start_frame"], (a["id"], b["id"])
    sections = {}
    for x in subs:
        t = x.get("start_t")
        sec = "End sequence" if t is None else next(
            (s["name"] for s in reversed(TM["sections"]) if s["start"] <= t + 0.2), "Bookend") if t >= 0 else "Bookend"
        x["section"] = sec
        sections.setdefault(sec, []).append(x["id"])
    hold = max((x for x in subs if x.get("start_t") is not None and x["start_t"] >= 0), key=lambda x: x["frames"])
    out = dict(
        generated_by="scripts/coverage.py", fps=FPS, lead_in_s=LEAD,
        rules=__doc__.split("Rules")[1].split("Cameras are")[0].strip(),
        total_shots=len(subs), cuts=len(subs) - 1, video_frames=f,
        per_section={k: len(v) for k, v in sections.items()},
        longest_hold=dict(id=hold["id"], seconds=hold["seconds"]),
        cameras=CAMS, subs=subs)
    Path("config/coverage.json").write_text(json.dumps(out, indent=1))
    md(out)
    print(f"config/coverage.json: {len(subs)} shots ({len(subs) - 1} cuts), {f} frames; longest {hold['id']} {hold['seconds']} s")
    for k, v in sections.items():
        print(f"  {k:14s} {len(v):3d}  {' '.join(v)}")


def md(o):
    L = ["# Coverage plan (M5b)", "",
         "Generated by `scripts/coverage.py` from `timing/music_map.json` and `timing/shot_times.json`; the data is "
         "`config/coverage.json`. Times are song time (s); frames are video frames at 30 fps (song time + 8.4 s). "
         "Blender sub-shots are rendered by `blender/coverage.py`.", "",
         f"**{o['total_shots']} shots, {o['cuts']} cuts** (M5: 27 shots). Longest hold in the music: "
         f"{o['longest_hold']['id']}, {o['longest_hold']['seconds']} s (the bookend and the end cards are cards).", "", "## Rules", "", o["rules"], "",
         "## Shots per section", "", "| Section | Shots |", "| --- | --- |"]
    L += [f"| {k} | {v} |" for k, v in o["per_section"].items()]
    L += ["", "## Sub-shots", "",
          "| Sub-shot | Section | Song time | Frames | Length | Cut on | Framing | Camera | Move | Covers | Note |",
          "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
    for x in o["subs"]:
        st = f"{x['start_t']:.2f}–{x['end_t']:.2f}" if "start_t" in x else "after the music"
        cam = x.get("camera") or x["source"]
        what = ""
        if x.get("camera"):
            what = o["cameras"][x["room"]][x["camera"]]["what"]
        mv = x.get("move") or {}
        mvs = {"push": f"push {mv.get('k', 0):.0%}", "truck": "truck", "m5": "M5's move", "hold": "hold",
               "track": "tracking"}.get(mv.get("type"), "—")
        lens = f", {x['lens']} mm" if x.get("lens") else ""
        L.append(f"| {x['id']} | {x['section']} | {st} | {x['start_frame']}–{x['end_frame']} | {x['seconds']:.2f} s | "
                 f"{x['snap']} | {x['framing']}{lens} | {cam}: {what} | {mvs} | {'; '.join(x['covers'])} | {x['note']} |")
    L += ["", "All moves get handheld drift (seeded per sub-shot), a small bump on the kick and, in the builds, a faster "
          "push; see `blender/coverage.py`."]
    Path("docs/coverage.md").write_text("\n".join(L) + "\n")


if __name__ == "__main__":
    main()
