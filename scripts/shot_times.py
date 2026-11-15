"""M2: resolve every shot cue (config/shot_cues.json) to song time, video time and frames: timing/shot_times.json.

Adapted from Ever Present's scripts/shot_times.py (commit 726343c; itself from The Distillation Job). Changes: 30 fps
(Remotion); video time = song time + the bookend lead-in (shot_cues lead_in_s); snapping to a downbeat or a beat per
shot, inside the grid's reliable spans; cues for the stops, the claps, the backing Hey!s and echoes; timed marks
inside shots; overlays; the post-roll after the music. Cue syntax: the _doc in config/shot_cues.json.
Shot IDs are checked against the brief's shot list in docs/brief.md.
Usage: .venv/bin/python -I scripts/shot_times.py
"""
import json
import re
from pathlib import Path

CUES, TIMING, OUT = Path("config/shot_cues.json"), Path("timing/timing_map.json"), Path("timing/shot_times.json")
MAX_SNAP = {"downbeat": 0.45, "beat": 0.3}
SHORT_S = 1.5


def line(tm, section, li):
    return next(s for s in tm["sections"] if s["name"] == section)["lines"][int(li)]


def nearest(ts, t):
    return min(range(len(ts)), key=lambda k: abs(ts[k] - t))


def resolve(cue, tm, starts):
    b = tm["beats"]
    if cue.startswith("t:"):
        return float(cue[2:]), cue
    if cue.startswith("event:"):
        parts = cue.split(":")
        v = tm["events"][parts[1]]
        return (v[int(parts[2])] if len(parts) > 2 else v), cue
    if cue.startswith(("hey:", "echo:")):
        kind, ref = cue.split(":", 1)
        sec, li = ref.split("|")
        h = line(tm, sec, li)[kind]
        return h["start"], f"{kind} after {sec} {li}" + ("" if h.get("found", True) else " (weak: check by ear)")
    if cue.startswith(("bars_before:", "beats_after:", "beats_before:")):
        kind, rest = cue.split(":", 1)
        ref, n = rest.rsplit(":", 1)
        t0 = starts[ref] if ref in starts else resolve(ref, tm, starts)[0]
        i = nearest(b["beats"], t0)
        step = {"bars_before": -4, "beats_after": 1, "beats_before": -1}[kind] * int(n)
        return b["beats"][i + step], f"{n} {kind.replace('_', ' ')} {ref}"
    kind, _, ref = cue.partition(":") if cue[:4] in ("end:", "mid:") else ("start", "", cue)
    sec, li, wi = ref.split("|")
    w = line(tm, sec, li)["words"][int(wi)]
    t = {"start": w["start"], "end": w["end"], "mid": (w["start"] + w["end"]) / 2}[kind]
    return t, f"{'' if kind == 'start' else kind + ' of '}{w['w']!r} ({sec} {li}.{wi})"


def reliable(tm, t):
    return any(a <= t <= z for a, z in tm["beats"]["reliable_span"])


def snap(tm, t, mode, max_s=None):
    if not mode or not reliable(tm, t):
        return t
    ts = tm["beats"]["downbeats"] if mode == "downbeat" else tm["beats"]["beats"]
    c = ts[nearest(ts, t)]
    return c if abs(c - t) <= (max_s or MAX_SNAP[mode]) else t


def bar_beat(tm, t):
    b = tm["beats"]
    i = nearest(b["beats"], t)
    return f"{b['bar'][i]}.{b['beat_in_bar'][i]}" + ("" if abs(b["beats"][i] - t) < 0.05 else "~")


def brief_rows():
    rows = {}
    for m in re.finditer(r"^\| (O\d\d) \|(.*)\|$", Path("docs/brief.md").read_text(), re.M):
        cells = [c.strip() for c in m.group(2).split("|")]
        rows[m.group(1)] = {"section": cells[0], "lyric": cells[1], "shot": cells[2]}
    return rows


def main():
    tm = json.load(open(TIMING))
    cfg = json.load(open(CUES))
    fps, lead = cfg["fps"], cfg["lead_in_s"]
    end_music = tm["audio"]["duration_s"]
    brief = brief_rows()
    if [s["id"] for s in cfg["shots"]] != list(brief):
        raise SystemExit("shot IDs differ from the brief's shot list (docs/brief.md)")
    starts, rows = {}, []
    for s in cfg["shots"]:
        if s["cue"] in ("pre", "post"):
            continue
        raw, label = resolve(s["cue"], tm, starts)
        t = snap(tm, raw, s.get("snap"), s.get("max_snap_s"))
        starts[s["id"]] = t
        rows.append({**s, "t": t, "raw": raw, "label": label})
    if [r["t"] for r in rows] != sorted(r["t"] for r in rows):
        raise SystemExit("shot cues are out of order")
    pr = cfg["post_roll"]
    o24_len = pr["O24_end_card_s"] + pr["O24_final_card_s"]
    vf = lambda song_t: round((song_t + lead) * fps)
    out, short = {}, []
    for s in cfg["shots"]:
        if s["cue"] == "pre":
            out[s["id"]] = {"placement": "before the music", "song_start": -lead, "song_end": 0.0,
                            "video_start": 0.0, "video_end": lead, "duration": lead,
                            "start_frame": 0, "end_frame": vf(0.0), "parts_s": cfg["lead_in_parts_s"], "note": s.get("note")}
    for i, r in enumerate(rows):
        end = rows[i + 1]["t"] if i + 1 < len(rows) else end_music
        d = {"song_start": round(r["t"], 3), "song_end": round(end, 3), "duration": round(end - r["t"], 3),
             "video_start": round(r["t"] + lead, 3), "video_end": round(end + lead, 3),
             "start_frame": vf(r["t"]), "end_frame": vf(end), "frames": vf(end) - vf(r["t"]),
             "bar_beat": bar_beat(tm, r["t"]), "cue": r["label"], "snapped_ms": round((r["t"] - r["raw"]) * 1000)}
        if r.get("note"):
            d["note"] = r["note"]
        if r.get("marks"):
            d["marks"] = []
            for m in r["marks"]:
                t, label = resolve(m["cue"], tm, starts)
                if not r["t"] - 0.01 <= t <= end + 0.01:
                    raise SystemExit(f"{r['id']}: mark {m['what']!r} at {t:.2f} is outside the shot")
                d["marks"].append({"what": m["what"], "song_t": round(t, 3), "video_t": round(t + lead, 3),
                                   "frame_in_shot": round((t - r["t"]) * fps), "cue": label})
        out[r["id"]] = d
        if end - r["t"] < SHORT_S:
            short.append(f"{r['id']}: {end - r['t']:.2f} s")
    for s in cfg["shots"]:
        if s["cue"] == "post":
            out[s["id"]] = {"placement": "after the music", "song_start": end_music, "song_end": end_music + o24_len,
                            "video_start": round(end_music + lead, 3), "video_end": round(end_music + lead + o24_len, 3),
                            "duration": o24_len, "start_frame": vf(end_music), "end_frame": vf(end_music + o24_len),
                            "note": s.get("note")}
    overlays = {}
    for o in cfg.get("overlays", []):
        a = snap(tm, resolve(o["start"], tm, starts)[0], o.get("start_snap"))
        z = snap(tm, resolve(o["end"], tm, starts)[0], o.get("end_snap"))
        overlays[o["id"]] = {"song_start": round(a, 3), "song_end": round(z, 3), "duration": round(z - a, 3),
                             "start_frame": vf(a), "end_frame": vf(z), "note": o["note"]}
    fact = {"song_start": end_music + o24_len, "duration": pr["fact_card_s"],
            "start_frame": vf(end_music + o24_len), "end_frame": vf(end_music + o24_len + pr["fact_card_s"])}
    order = [s["id"] for s in cfg["shots"]]
    total = end_music + lead + o24_len + pr["fact_card_s"]
    json.dump({"generated_by": "scripts/shot_times.py", "fps": fps, "lead_in_s": lead, "music_end_song": end_music,
               "video_length_s": round(total, 3), "video_frames": round(total * fps),
               "master_sha256": tm["audio"]["sha256"], "shots": {k: out[k] for k in order},
               "overlays": overlays, "fact_card_after_O24": fact, "short_shots": short},
              open(OUT, "w"), indent=1, ensure_ascii=False)
    for k in order:
        s = out[k]
        print(f"{k} song {s['song_start']:7.2f}-{s['song_end']:7.2f} ({s['duration']:5.2f} s) video {s['video_start']:7.2f}"
              f" f{s['start_frame']}-{s['end_frame']} {s.get('bar_beat', ''):6s} snap {s.get('snapped_ms', 0):+4d}ms"
              f"  {s.get('cue', s.get('placement'))}")
    for k, o in overlays.items():
        print(f"overlay {k}: {o['song_start']:.2f}-{o['song_end']:.2f} ({o['duration']:.2f} s)")
    print(f"music ends {end_music:.2f} s (song); video {total:.2f} s; shots under {SHORT_S} s:", *short or ["none"], sep="\n  ")


if __name__ == "__main__":
    main()
