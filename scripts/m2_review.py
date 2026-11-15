"""M2 gate: a review video to check the timing map and the shot cues by ear and eye.

Adapted from Ever Present's scripts/m2_review.py (commit 726343c; itself from The Distillation Job). Changes: video
time (the bookend lead-in, silent, then the song), 30 fps, the shot list's columns for O01-O24, marks inside shots,
overlays, the backing Hey!s and echoes, a click with an accent on bar 1, and the post-roll.
Dark 960x540 frame. Top: shot ID, section and lyric cue from the brief, the brief's shot text (wrapped), the cue
note. Middle: the shot's marks as they happen. Bottom: the section (from the timing map) and the as-sung line with
the current word highlighted; Hey!s and echoes in orange. Corner: bar.beat, song time and video time.
Audio: the post-filtered master (config/timing.json review_audio; 0-sample lag to the Logic master) plus a click on
every beat, higher on bar 1, after lead_in_s of silence; the post-roll is silent.
Usage: .venv/bin/python -I scripts/m2_review.py  ->  review/m2_timing.mp4 (and timing/check/m2_review.ass, master_click.wav)
"""
import json
import re
import subprocess
import textwrap
from pathlib import Path

import numpy as np
import soundfile as sf

tm = json.load(open("timing/timing_map.json"))
st = json.load(open("timing/shot_times.json"))
shots = st["shots"]
lead, fps = st["lead_in_s"], st["fps"]
cues = {s["id"]: s for s in json.load(open("config/shot_cues.json"))["shots"]}
brief = {}
for m in re.finditer(r"^\| (O\d\d) \|(.*)\|$", Path("docs/brief.md").read_text(), re.M):
    c = [x.strip() for x in m.group(2).split("|")]
    brief[m.group(1)] = {"section": c[0], "lyric": c[1], "shot": c[2]}
check = Path("timing/check"); check.mkdir(parents=True, exist_ok=True)
OUT = Path("review/m2_timing.mp4"); OUT.parent.mkdir(exist_ok=True)

# audio: silence for the lead-in, the master plus the click, silence for the post-roll
master, sr = sf.read(json.load(open("config/timing.json"))["review_audio"], always_2d=True)
total = st["video_length_s"]
mix = np.zeros((int(round(total * sr)) + sr, 2))
off = int(round(lead * sr))
mix[off:off + len(master)] = master
b = tm["beats"]
n = int(0.03 * sr); env = np.exp(-np.arange(n) / (0.006 * sr))
for t, k in zip(b["beats"], b["beat_in_bar"]):
    f, g = (1760, 0.2) if k == 1 else (1100, 0.11)
    i = off + int(round(t * sr))
    mix[i:i + n] += (g * env * np.sin(2 * np.pi * f * np.arange(n) / sr))[:, None]
mix *= min(1.0, 0.999 / np.abs(mix).max())
sf.write(check / "master_click.wav", mix, sr, subtype="PCM_24")


def ts(t):
    cs = int(round(t * 100)); return f"{cs // 360000}:{cs // 6000 % 60:02d}:{cs // 100 % 60:02d}.{cs % 100:02d}"


def esc(s):
    return s.replace("{", "(").replace("}", ")").replace("\n", " ").replace("\\", "/").replace("*", "")


def wrap(s, width):
    return "\\N".join(textwrap.wrap(esc(s), width))


ev = []
V = lambda t: t + lead  # song time -> video time
for sid, s in shots.items():
    d = brief[sid]
    top = (f"{{\\b1\\fs30}}{sid}{{\\b0\\fs18}}   {esc(d['section'])} · {esc(d['lyric'])}"
           f"   {{\\c&H999999&}}song {s['song_start']:.2f}-{s['song_end']:.2f} s, {s['duration']:.2f} s{{\\c&HFFFFFF&}}"
           f"\\N{{\\fs17}}{wrap(d['shot'], 98)}")
    note = s.get("note")
    if note:
        top += f"\\N{{\\fs16\\c&H66CCFF&}}cue: {wrap(note, 100)}"
    ev.append(f"Dialogue: 1,{ts(s['video_start'])},{ts(s['video_end'])},Shot,,0,0,0,,{top}")
    for m in s.get("marks", []):
        ev.append(f"Dialogue: 1,{ts(m['video_t'])},{ts(min(m['video_t'] + 1.5, s['video_end']))},Mark,,0,0,0,,"
                  f"{{\\c&H55DDFF&}}▶ {esc(m['what'])}")
for oid, o in st["overlays"].items():
    ev.append(f"Dialogue: 1,{ts(V(o['song_start']))},{ts(V(o['song_end']))},Overlay,,0,0,0,,"
              f"{{\\c&HFFAA66&}}[overlay: {oid}]")
f = st["fact_card_after_O24"]
ev.append(f"Dialogue: 1,{ts(V(f['song_start']))},{ts(V(f['song_start'] + f['duration']))},Shot,,0,0,0,,"
          f"{{\\b1\\fs30}}Fact card{{\\b0\\fs18}}   after O24 (brief: Bookends)")
for sec in tm["sections"]:
    head = f"{{\\fs18\\c&HAAAAAA&}}{esc(sec['name'])}" + (f" ({esc(sec['note'])})" if sec.get("note") else "")
    ev.append(f"Dialogue: 0,{ts(V(sec['start']))},{ts(V(sec['end']))},Section,,0,0,0,,{head}")
    for li, line in enumerate(sec["lines"]):
        ws = line["words"]
        nxt = sec["lines"][li + 1]["start"] if li + 1 < len(sec["lines"]) else sec["end"]
        extra = line.get("echo") or line.get("hey")
        line_end = max(ws[-1]["end"], extra["end"] if extra else 0) + 0.4
        line_end = min(max(line_end, ws[-1]["end"] + 0.3), max(nxt, ws[-1]["end"] + 0.3))
        for i, w in enumerate(ws):
            a = w["start"]; z = ws[i + 1]["start"] if i + 1 < len(ws) else line_end
            text = " ".join((f"{{\\c&H00FFFF&}}{esc(x['w'])}{{\\c&HFFFFFF&}}" if j == i else esc(x["w"])) for j, x in enumerate(ws))
            ev.append(f"Dialogue: 0,{ts(V(a))},{ts(V(z))},Lyric,,0,0,0,,{text}")
        if extra:
            ev.append(f"Dialogue: 0,{ts(V(extra['start']))},{ts(V(max(extra['end'], extra['start'] + 0.5)))},Back,,0,0,0,,"
                      f"{{\\c&H3399FF&}}({esc(extra['text'])})" + ("" if extra.get("found", True) else " ?"))
for k, (t, kb) in enumerate(zip(b["beats"], b["beat_in_bar"])):
    e = b["beats"][k + 1] if k + 1 < len(b["beats"]) else t + 0.6
    col = "&H00FFFF&" if kb == 1 else "&H999999&"
    ev.append(f"Dialogue: 0,{ts(V(t))},{ts(V(e))},Beat,,0,0,0,,{{\\c{col}}}bar {b['bar'][k]}.{kb}"
              f"{{\\c&H999999&}}  song {t:6.2f}  video {V(t):6.2f}  {b['kind'][k][:5]}")
ev.append(f"Dialogue: 0,{ts(0)},{ts(lead)},Beat,,0,0,0,,{{\\c&H999999&}}bookend lead-in (silent): {lead:.1f} s")
for k, e in tm["events"].items():
    if isinstance(e, (int, float)) and k in ("stop1", "stop2", "back2", "band_back1", "drums_in"):
        ev.append(f"Dialogue: 2,{ts(V(e))},{ts(V(e) + 1.2)},Event,,0,0,0,,{{\\c&H4444FF&}}● {k} {e:.2f} s")
ass = f"""[Script Info]
ScriptType: v4.00+
PlayResX: 960
PlayResY: 540
WrapStyle: 2

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Shot,DejaVu Sans,18,&H00FFFFFF,&H00FFFFFF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,1,0,7,24,24,18,1
Style: Mark,DejaVu Sans,22,&H00FFFFFF,&H00FFFFFF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,1,0,4,24,24,0,1
Style: Overlay,DejaVu Sans,18,&H00FFFFFF,&H00FFFFFF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,1,0,6,24,24,0,1
Style: Section,DejaVu Sans,18,&H00FFFFFF,&H00FFFFFF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,1,0,1,24,24,96,1
Style: Lyric,DejaVu Sans,28,&H00FFFFFF,&H00FFFFFF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,1,0,1,24,24,56,1
Style: Back,DejaVu Sans,24,&H00FFFFFF,&H00FFFFFF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,1,0,3,24,24,56,1
Style: Beat,DejaVu Sans Mono,16,&H00999999,&H00FFFFFF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,1,0,1,24,24,16,1
Style: Event,DejaVu Sans Mono,18,&H00FFFFFF,&H00FFFFFF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,1,0,3,24,24,16,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
""" + "\n".join(ev) + "\n"
(check / "m2_review.ass").write_text(ass, encoding="utf-8")
subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i", f"color=c=0x181a1f:s=960x540:r={fps}:d={total}",
                "-i", str(check / "master_click.wav"), "-vf", f"ass={check / 'm2_review.ass'}", "-c:v", "libx264",
                "-preset", "veryfast", "-crf", "28", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k",
                "-shortest", str(OUT)], check=True)
print(OUT, f"{total:.2f} s")
