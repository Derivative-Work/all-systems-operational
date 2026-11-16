"""M5b: the music map. What the band plays, bar by bar and hit by hit, on the M2 beat grid, so cuts, camera and light
can follow the music (plan M5b; decisions 12).

Inputs: the stems (audio/stems/, the Logic export of Suno's stems, human interventions 3), the human's clap track
(audio/extra/, decisions 4), the master (config/timing.json) and timing/timing_map.json (the approved M2 grid, lyrics
and Hey!s). Song time throughout; 30 fps frames are song time x 30 (add the 8.4 s lead-in for video time).

Method (onsets read as in Ever Present's scripts/vocal_env.py: mono stems, RMS in short windows, dB):
- Per-bar energy: RMS of the bar (downbeat to downbeat) in dBFS for the master and every stem, plus a 0-1 value over
  the 40 dB below that track's loudest bar. Bars before the first downbeat and after the last are one "bar 0" and
  one tail.
- Hits: a band-limited stem, RMS in 5 ms windows (dB), onset strength = the rise over the previous 30 ms; peaks
  above a threshold, at least `gap` apart. Each hit gets its nearest beat (index, bar.beat) and offset in ms, and a
  0-1 strength (the rise, scaled to that list's 95th percentile).
    kick:        drums stem, 30-150 Hz (the stomp/kick)
    kick "main": on the beat (within 75 ms) and strength >= 0.5 (the stomp); the rest are 8th-note pickups
    snare_clap:  drums stem, 1.5-6 kHz onsets not masked by the kick. The stomp is broadband, so this catches most
                 beats; the claps can't be split from it by band (beat_profile: the band peaks by beat in bar per
                 section; no consistent 2-and-4 accent), so
    backbeat:    beats 2 and 4 of the grid wherever the drums play (the clap grid the animation uses, as M5's)
    clap_track:  the human's clap track (the four claps in stop 1), level onsets as in M2
    tambourine:  percussion stem, above 6 kHz
    strums:      guitar stem, 1.5-8 kHz (pick attacks); also counted per bar (strum density)
    lead_onsets: lead stem, 200 Hz-4 kHz (sung syllables: the string lights chase these in O14-O16)
- Hey!s: the 23 M2 Hey!s (timing_map lines' "hey"), each cross-checked on the backing stem: the strongest onset within
  +-0.15 s, its rise in dB and the backing level 0.1 s after vs 0.2 s before. The two M2 flagged as weak (56.24 s,
  186.21 s) are reported with the same numbers.
- Envelopes at 30 fps (one value per frame of song time, 0-1 over the 30 dB below the 99th percentile, as
  vocal_env.py): lead, backing (the gang swell), drums, full mix.
- Stops: the M2 events (stop1, stop2, back2, band back), copied.
Output: timing/music_map.json. Plot: review/m5b_music_map.png (scripts/music_map.py --plot).
No random process, so no seed is read.
Usage: .venv/bin/python -I scripts/music_map.py [--plot]
"""
import json
import re
import sys
from pathlib import Path

import numpy as np
import soundfile as sf
from scipy.signal import butter, sosfiltfilt

CFG = json.load(open("config/timing.json"))
TM = json.load(open("timing/timing_map.json"))
OUT = Path("timing/music_map.json")
PNG = Path("review/m5b_music_map.png")
STEM_DIR = Path("audio/stems")
# Suno's 12 stems as exported (numbered "N Name.aif"); M1b's repaint and v1.3 lead are kept out of the per-stem list
STEMS = {p.stem.split(" ", 1)[1].lower().replace(" ", "_"): p for p in sorted(STEM_DIR.glob("*.aif"))
         if re.fullmatch(r"\d+ [A-Za-z ]+", p.stem)}
MASTER = CFG["master"]
if "--v13" in sys.argv:
    # M1b (production log 53): the v1.3 master and lead (config/timing.json) -> timing/music_map_v13.json, for the M7
    # render. Without it, the v1.2 inputs (archived) rebuild timing/music_map.json, which the M5c3 cut was made from.
    STEMS["lead_vocals"] = Path(CFG["stems"]["lead"])
    OUT, PNG = Path("timing/music_map_v13.json"), Path("review/m1b_music_map.png")
else:
    MASTER = "archive/audio/v1.2/track/All Systems Operational.wav"
FPS = 30
HOP_S = 0.005

BEATS = np.array(TM["beats"]["beats"])
BIB = TM["beats"]["beat_in_bar"]
BARNO = TM["beats"]["bar"]
DOWN = np.array(TM["beats"]["downbeats"])


def load(path):
    y, sr = sf.read(str(path), always_2d=True)
    return y.mean(1), sr


def band(y, sr, lo=None, hi=None):
    if lo and hi:
        sos = butter(4, [lo, hi], "bandpass", fs=sr, output="sos")
    elif lo:
        sos = butter(4, lo, "highpass", fs=sr, output="sos")
    else:
        sos = butter(4, hi, "lowpass", fs=sr, output="sos")
    return sosfiltfilt(sos, y)


def rms_db(y, sr, win_s):
    hop = int(sr * win_s)
    n = len(y) // hop
    fr = y[:n * hop].reshape(n, hop)
    return 20 * np.log10(np.sqrt((fr ** 2).mean(1)) + 1e-9)


def env01(db, span=30.0, top=None):
    top = np.percentile(db, 99) if top is None else top
    return np.clip((db - (top - span)) / span, 0, 1)


def nearest_beat(t):
    i = int(np.argmin(np.abs(BEATS - t)))
    return i, f"{BARNO[i]}.{BIB[i]}", round((t - BEATS[i]) * 1000)


def hits(db, gap, floor_db, min_rise, look=6):
    """Peaks of the rise over the previous `look` windows (30 ms), above floor_db and min_rise dB, at least gap s apart."""
    rise = np.zeros_like(db)
    rise[look:] = db[look:] - np.min(np.lib.stride_tricks.sliding_window_view(db, look)[:-1], axis=1)
    out = []
    k, n, g = 1, len(db), int(gap / HOP_S)
    while k < n - 1:
        if rise[k] >= min_rise and db[k] > floor_db and rise[k] >= rise[k - 1] and rise[k] >= rise[k + 1]:
            # the onset's peak level within the next 40 ms
            j = k + int(np.argmax(db[k:k + 8]))
            best = max(range(k, min(n, k + g // 2)), key=lambda q: rise[q])
            out.append((best * HOP_S, float(rise[best]), float(db[j])))
            k = best + g
        else:
            k += 1
    return out


def hit_list(raw, p95=None):
    if not raw:
        return []
    p95 = np.percentile([r for _, r, _ in raw], 95) if p95 is None else p95
    out = []
    for t, r, lvl in raw:
        i, bb, off = nearest_beat(t)
        out.append({"t": round(t, 3), "beat": i, "bar_beat": bb, "off_ms": off, "strength": round(min(1.0, r / p95), 3),
                    "rise_db": round(r, 1), "level_db": round(lvl, 1)})
    return out


def bar_spans(end):
    edges = [0.0] + list(DOWN) + [end]
    spans = []
    for k in range(len(edges) - 1):
        a, b = edges[k], edges[k + 1]
        if b - a < 0.05:
            continue
        spans.append({"bar": 0 if k == 0 else k, "start": round(a, 3), "end": round(b, 3)})
    spans[-1]["bar"] = "tail"
    return spans


def section_at(t):
    name = None
    for s in TM["sections"]:
        if s["start"] <= t + 1e-3:
            name = s["name"]
    return name


def main():
    plot = "--plot" in sys.argv
    mix, sr = load(MASTER)
    dur = len(mix) / sr
    tracks = {"mix": mix}
    for k, p in STEMS.items():
        tracks[k], _ = load(p)
    bars = bar_spans(dur)
    global ev_stop1, ev_back1, ev_stop2, ev_back2
    ev_stop1, ev_back1 = TM["events"]["stop1"], TM["events"]["band_back1"]
    ev_stop2, ev_back2 = TM["events"]["stop2"], TM["events"]["back2"]
    # per-bar energy
    energy = {}
    for k, y in tracks.items():
        dbs = []
        for b in bars:
            seg = y[int(b["start"] * sr): int(b["end"] * sr)]
            dbs.append(float(20 * np.log10(np.sqrt((seg ** 2).mean()) + 1e-9)))
        top = max(dbs)
        energy[k] = {"db": [round(v, 1) for v in dbs], "norm": [round(float(np.clip((v - (top - 40)) / 40, 0, 1)), 3) for v in dbs]}
    for i, b in enumerate(bars):
        b["section"] = section_at(b["start"] + 0.01)
        b["mix_norm"] = energy["mix"]["norm"][i]
    # hits
    d = tracks["drums"]
    kick_db = rms_db(band(d, sr, 30, 150), sr, HOP_S)
    hi_db = rms_db(band(d, sr, 1500, 6000), sr, HOP_S)
    kick = hit_list(hits(kick_db, 0.22, -40, 8))
    snare = hit_list(hits(hi_db, 0.22, -42, 9))
    # a snare/clap is a high-band onset that isn't just the kick's click: the high band's peak within 10 dB of the
    # kick band's, or no kick within 30 ms
    kt = np.array([h["t"] for h in kick])
    def is_clap(h):
        k = int(h["t"] / HOP_S)
        near = len(kt) and np.min(np.abs(kt - h["t"])) < 0.03
        return (not near) or hi_db[k:k + 8].max() > kick_db[k:k + 8].max() - 10
    snare = [h for h in snare if is_clap(h)]
    for h in kick:                     # the stomp on the beat vs the 8th-note pickups between
        h["main"] = bool(abs(h["off_ms"]) < 75 and h["strength"] >= 0.5)
    # per-beat profile: the low and high band peaks (+-40 ms) on every grid beat, averaged by beat in bar per section;
    # the claps can't be split from the stomp by band
    prof, backbeat = {}, []
    dr_db = rms_db(d, sr, HOP_S)
    for t, bib in zip(BEATS, BIB):
        if t < 1.0:
            continue
        k = int(t / HOP_S)
        lo_, hi_ = float(kick_db[k - 8:k + 8].max()), float(hi_db[k - 8:k + 8].max())
        sec = section_at(t)
        prof.setdefault(sec, {}).setdefault(int(bib), []).append((lo_, hi_))
        playing = dr_db[k - 8:k + 8].max() > -30 and not (ev_stop1 <= t < ev_back1 or ev_stop2 <= t < ev_back2)
        if bib in (2, 4) and playing:
            backbeat.append({"t": round(float(t), 3), "beat": int(np.argmin(np.abs(BEATS - t))), "hi_db": round(hi_, 1)})
    beat_profile = {sec: {b: [round(float(np.mean([x[0] for x in v])), 1), round(float(np.mean([x[1] for x in v])), 1)]
                          for b, v in sorted(by.items())} for sec, by in prof.items()}
    tamb = hit_list(hits(rms_db(band(tracks["percussion"], sr, 6000, None), sr, HOP_S), 0.1, -55, 8))
    strums = hit_list(hits(rms_db(band(tracks["guitar"], sr, 1500, 8000), sr, HOP_S), 0.09, -50, 6))
    # --v13: the lead's scales (the envelope's 99th-percentile top, the onsets' 95th-percentile rise) stay the v1.2
    # lead's, so outside the repainted bridge the lead's envelope and onsets are v1.2's (the stems are identical there)
    ref = None
    if "--v13" in sys.argv:
        y0, _ = load("audio/stems/0 Lead Vocals.aif")
        ref = {"top": float(np.percentile(rms_db(band(y0, sr, 150, 6000), sr, 1 / FPS), 99)),
               "p95": float(np.percentile([r for _, r, _ in hits(rms_db(band(y0, sr, 200, 4000), sr, HOP_S), 0.15, -45, 9)], 95))}
    lead_on = hit_list(hits(rms_db(band(tracks["lead_vocals"], sr, 200, 4000), sr, HOP_S), 0.15, -45, 9),
                       ref["p95"] if ref else None)
    claps = [{"t": t, **dict(zip(("beat", "bar_beat", "off_ms"), nearest_beat(t)))} for t in TM["events"]["claps"]]
    # strum density per bar
    st_t = np.array([h["t"] for h in strums])
    for b in bars:
        b["strums"] = int(((st_t >= b["start"]) & (st_t < b["end"])).sum())
        b["kicks"] = sum(1 for h in kick if b["start"] <= h["t"] < b["end"])
        b["tamb"] = sum(1 for h in tamb if b["start"] <= h["t"] < b["end"])
    # Hey!s cross-checked on the backing stem
    bk = tracks["backing_vocals"]
    bk_db = rms_db(band(bk, sr, 150, 6000), sr, HOP_S)
    bk_rise = np.zeros_like(bk_db)
    bk_rise[6:] = bk_db[6:] - np.min(np.lib.stride_tricks.sliding_window_view(bk_db, 6)[:-1], axis=1)
    heys = []
    for s in TM["sections"]:
        for l in s["lines"]:
            h = l.get("hey")
            if not h:
                continue
            t = h["start"]
            a, b_ = int((t - 0.15) / HOP_S), int((t + 0.15) / HOP_S)
            k = a + int(np.argmax(bk_rise[a:b_]))
            after = float(bk_db[int((t + 0.02) / HOP_S): int((t + 0.12) / HOP_S)].mean())
            before = float(bk_db[int((t - 0.2) / HOP_S): int((t - 0.02) / HOP_S)].mean())
            i, bb, off = nearest_beat(t)
            heys.append({"t": t, "section": s["name"], "line": l["text"], "m2_how": h["how"], "m2_found": h["found"],
                         "beat": i, "bar_beat": bb, "off_ms": off,
                         "backing_onset_t": round(k * HOP_S, 3), "backing_rise_db": round(float(bk_rise[k]), 1),
                         "level_step_db": round(after - before, 1),
                         "weak": (not h["found"]) or float(bk_rise[k]) < 6})
    # envelopes at 30 fps, song time
    def env(y, lo=None, hi=None, top=None):
        db = rms_db(y if lo is None else band(y, sr, lo, hi), sr, 1 / FPS)
        return [round(float(v), 3) for v in env01(db, top=top)]
    envs = {"lead": env(tracks["lead_vocals"], 150, 6000, ref["top"] if ref else None), "backing": env(bk, 150, 6000), "drums": env(d),
            "mix": env(mix)}
    ev = TM["events"]
    out = {
        "generated_by": "scripts/music_map.py", "time": "song time (s); frames = song time x 30 (+ 252 for video frames)",
        "fps": FPS, "duration_s": round(dur, 3),
        "grid": {"bpm": [s["bpm"] for s in TM["beats"]["segments"]], "beats": len(BEATS), "downbeats": len(DOWN),
                 "source": "timing/timing_map.json beats (M2, approved)"},
        "stops": {"stop1": ev["stop1"], "claps_in_stop1": ev["claps"], "band_back1": ev["band_back1"],
                  "stop2": ev["stop2"], "back2": ev["back2"], "drums_in": ev["drums_in"], "music_end": ev["music_end"],
                  "drums_out_outro": [214.0, 226.0]},
        "bars": bars, "energy": energy,
        "beat_profile": {"_doc": "per section, beat in bar: [kick band peak dB, 1.5-6 kHz peak dB], mean over the section's grid beats", **beat_profile},
        "hits": {"kick": kick, "backbeat": backbeat, "snare_clap": snare, "clap_track": claps, "tambourine": tamb, "strums": strums,
                 "lead_onsets": lead_on},
        "heys": heys,
        "env_30fps": envs,
        "method": __doc__.split("Method")[1].split("Output:")[0].strip(),
    }
    OUT.write_text(json.dumps(out, separators=(",", ":")))
    print(f"{OUT}: {len(bars)} bars, kick {len(kick)}, snare/clap {len(snare)}, tamb {len(tamb)}, strums {len(strums)}, "
          f"lead onsets {len(lead_on)}, heys {len(heys)} ({sum(h['weak'] for h in heys)} weak)")
    for h in heys:
        print(f"  hey {h['t']:7.2f} {h['bar_beat']:>6s} {h['off_ms']:+4d} ms  rise {h['backing_rise_db']:5.1f} dB  "
              f"step {h['level_step_db']:+5.1f} dB  m2 {h['m2_how']}/{h['m2_found']}  {'WEAK' if h['weak'] else ''}")
    kb = [h for h in kick]
    offs = np.array([h["off_ms"] for h in kb])
    print(f"kick: median offset {np.median(offs):+.0f} ms, {np.mean(np.abs(offs) < 40) * 100:.0f}% within 40 ms of a beat")
    if plot:
        draw(out)


def draw(m):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    ink, muted, grid = "#0b0b0b", "#6b6a66", "#e4e3df"
    C = {"kick": "#2a78d6", "snare_clap": "#eb6834", "tambourine": "#1baf7a", "hey": "#6250d6", "clap": "#e87ba4"}
    fig, ax = plt.subplots(5, 1, figsize=(22, 13), sharex=True, gridspec_kw={"height_ratios": [1.1, 1.6, 1.0, 1.0, 1.0]})
    fig.patch.set_facecolor("#fcfcfb")
    bars = m["bars"]
    t = np.arange(len(m["env_30fps"]["lead"])) / FPS
    for a in ax:
        a.set_facecolor("#fcfcfb")
        for s in ("top", "right"):
            a.spines[s].set_visible(False)
        for s in ("left", "bottom"):
            a.spines[s].set_color(muted)
        a.tick_params(colors=muted, labelsize=8)
        for b in bars:
            a.axvline(b["start"], color=grid, lw=0.6, zorder=0)
        for k in ("stop1", "stop2", "back2", "band_back1"):
            a.axvline(m["stops"][k], color=ink, lw=1.0, ls=":", zorder=1)
    # 0: sections and per-bar mix energy
    a = ax[0]
    xs = [b["start"] for b in bars]
    ws = [b["end"] - b["start"] for b in bars]
    a.bar(xs, [b["mix_norm"] for b in bars], width=ws, align="edge", color="#2a78d6", edgecolor="#fcfcfb", lw=1)
    a.set_ylabel("mix energy\nper bar (0-1)", color=ink, fontsize=9)
    for i, s in enumerate(TM["sections"]):
        a.text(s["start"] + 0.3, 1.02 + 0.09 * (i % 2), s["name"], fontsize=7.5, color=ink, va="bottom", clip_on=False)
    a.set_ylim(0, 1)
    a.set_title("All Systems Operational: music map (song time, s). Grey lines: downbeats; dotted: stop 1, band back, "
                "stop 2, sound back", loc="left", fontsize=11, color=ink, pad=30)
    # 1: per-stem energy heat rows
    a = ax[1]
    names = ["lead_vocals", "backing_vocals", "drums", "percussion", "guitar", "bass", "keyboard", "strings", "synth",
             "brass", "woodwinds", "other"]
    for r, k in enumerate(names):
        v = m["energy"][k]["norm"]
        for b, x in zip(bars, v):
            a.add_patch(plt.Rectangle((b["start"], r), b["end"] - b["start"], 0.9,
                                      color=plt.cm.Blues(0.08 + 0.92 * x), lw=0))
    a.set_ylim(len(names), -0.1)
    a.set_yticks([r + 0.45 for r in range(len(names))])
    a.set_yticklabels([n.replace("_", " ") for n in names], fontsize=8, color=ink)
    a.set_ylabel("stem energy per bar\n(light to dark: 0-1)", color=ink, fontsize=9)
    # 2: hits
    a = ax[2]
    rows = [("kick", "kick (drums < 150 Hz)"), ("snare_clap", "snare / clap (drums 1.5-6 kHz)"),
            ("tambourine", "tambourine (percussion > 6 kHz)")]
    for r, (k, lab) in enumerate(rows):
        hs = m["hits"][k]
        a.vlines([h["t"] for h in hs], r + 0.1, r + 0.1 + 0.8 * np.array([h["strength"] for h in hs]), color=C[k], lw=0.9)
        a.text(-2, r + 0.5, lab, ha="right", va="center", fontsize=8, color=ink)
    a.vlines([h["t"] for h in m["hits"]["clap_track"]], 3.1, 3.9, color=C["clap"], lw=2)
    a.text(-2, 3.5, "clap track (stop 1)", ha="right", va="center", fontsize=8, color=ink)
    for h in m["heys"]:
        a.vlines(h["t"], 4.1, 4.9, color=C["hey"], lw=2 if not h["weak"] else 1, ls="-" if not h["weak"] else "--")
        if h["weak"]:
            a.text(h["t"] + 0.4, 4.85, f"weak {h['t']:.2f}", fontsize=7, color=ink, va="top")
    a.text(-2, 4.5, "Hey! (dashed: weak)", ha="right", va="center", fontsize=8, color=ink)
    a.set_ylim(0, 5)
    a.set_yticks([])
    a.set_title("hits (bar height: strength)", loc="left", fontsize=9, color=ink)
    # 3: strum density
    a = ax[3]
    a.bar(xs, [b["strums"] for b in bars], width=ws, align="edge", color="#1baf7a", edgecolor="#fcfcfb", lw=1)
    a.set_ylabel("guitar strums\nper bar", color=ink, fontsize=9)
    # 4: envelopes
    a = ax[4]
    a.plot(t, m["env_30fps"]["lead"], color="#2a78d6", lw=0.8, label="lead vocal")
    a.plot(t, m["env_30fps"]["backing"], color="#eb6834", lw=0.8, alpha=0.85, label="backing (gang)")
    a.set_ylim(0, 1.05)
    a.set_ylabel("vocal envelope\n(30 fps, 0-1)", color=ink, fontsize=9)
    a.legend(loc="upper left", fontsize=8, frameon=False, ncol=2)
    a.set_xlabel("song time (s)", color=ink, fontsize=9)
    a.set_xlim(0, m["duration_s"])
    a.set_xticks(np.arange(0, m["duration_s"], 10))
    fig.tight_layout()
    fig.savefig(PNG, dpi=90)
    print(f"{PNG}")


if __name__ == "__main__":
    main()
