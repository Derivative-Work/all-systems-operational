"""M2: build timing/timing_map.json on the master's timeline (song time; the Logic master and the post-filtered master
have 0-sample lag, so the map holds for both).

Adapted from Ever Present's scripts/timing_map.py (commit 726343c; itself from The Distillation Job). Changes:
- Lyrics: lyrics/as_sung.txt, lead lines plus backing parts in braces: "{Hey!}" (a shout after the line) and
  "{we are aware}" (an echo). Lead lines are force-aligned (WhisperX wav2vec2, one segment per line) on the lead stem,
  in windows anchored on the lead transcript (timing/whisper_lead.json); config/timing.json overrides the windows
  the transcript can't anchor. Echoes are aligned on the backing stem, between the end of their lead line and the end
  of the next. Hey!s are the strongest onset on the backing stem between the line's last word and the next line.
- Beats: tracked on the drums stem (steady stomp), in segments split at the hard stops (config/timing.json), at 48 kHz
  hop 128 (2.7 ms; the 22 kHz hop 256 tracker rounded the tempo to 99.4 bpm). Stop 1 is filled by interpolation
  between segments; stop 2 inserted time, so the outro keeps its own phase. Bars: downbeats anchored on a sung word
  per segment (the stomp hits every beat, so low-band strength can't find bar 1).
- Events: the two hard stops and the sound's return, measured on the master; the clap track's onsets; the drums'
  entry; first and last vocal.
- Sections: sung sections start at their first word; instrumental sections from config/timing.json. Each section
  ends where the next starts.
The SRTs are written by scripts/export_srt.py.
Usage: NLTK_DATA=$PWD/.venv/nltk_data .venv/bin/python -I scripts/timing_map.py   (or scripts/m2.sh for all of M2)
"""
import difflib
import hashlib
import json
import re
from pathlib import Path

import librosa
import numpy as np
import soundfile as sf
import whisperx

CFG = json.load(open("config/timing.json"))
MASTER = Path(CFG["master"])
STEMS = CFG["stems"]
LYRICS = Path("lyrics/as_sung.txt")
TRANSCRIPT = Path("timing/whisper_lead.json")
OUT = Path("timing/timing_map.json")
FPS = 30  # Remotion (remotion/src/config.ts)


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def norm(word):
    return re.sub(r"[^a-z']", "", word.lower().replace("’", "'"))


def parse_lyrics():
    sections = []
    for raw in LYRICS.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line:
            continue
        m = re.match(r"\[(.+?)\]\s*(?:\((.+)\))?$", line)
        if m:
            sections.append({"name": m.group(1), "note": m.group(2), "lines": []})
            continue
        b = re.match(r"(.*?)\s*\{(.+)\}$", line)
        lead, back = (b.group(1), b.group(2)) if b else (line, None)
        sections[-1]["lines"].append({"text": lead, "backing": back})
    return sections


def line_windows(keys, lines, transcript_words, duration):
    overrides = {k: v for k, v in CFG["line_window_overrides"].items() if not k.startswith("_")}
    lyric_tokens = [(i, norm(w)) for i, text in enumerate(lines) for w in text.split() if keys[i] not in overrides]
    trans = [w for w in transcript_words if w["start"] >= 0]
    sm = difflib.SequenceMatcher(a=[t for _, t in lyric_tokens], b=[norm(w["w"]) for w in trans], autojunk=False)
    first, last = {}, {}
    for a, b, n in sm.get_matching_blocks():
        for k in range(n):
            li, w = lyric_tokens[a + k][0], trans[b + k]
            first.setdefault(li, w["start"])
            last[li] = w["end"]
    for i, key in enumerate(keys):
        if key in overrides:
            first[i], last[i] = overrides[key]
    missing = [lines[i] for i in range(len(lines)) if i not in first]
    if missing:
        raise SystemExit(f"no transcript anchor for lines {missing}")
    windows = []
    for i, key in enumerate(keys):
        if key in overrides:
            windows.append(tuple(overrides[key]))
            continue
        start = last[i - 1] + 0.02 if i > 0 else max(0.0, first[i] - 2.0)
        end = first[i + 1] - 0.02 if i + 1 < len(lines) else min(duration, last[i] + 1.0)
        windows.append((start, end))
    return windows


def aligned_words(model, meta, audio, segments):
    out = whisperx.align(segments, model, meta, audio, "cuda", return_char_alignments=False)["segments"]
    flat = [w for seg in out for w in seg["words"]]
    want = [w for s in segments for w in s["text"].split()]
    if [w["word"] for w in flat] != want:
        raise SystemExit(f"aligned words differ from the lyrics: {[w['word'] for w in flat]} vs {want}")
    for i, w in enumerate(flat):  # a word with no alignable characters: give it the gap after the previous word
        if "start" not in w:
            prev = flat[i - 1]
            w["start"], w["end"], w["score"], w["filled"] = prev["end"], prev["end"] + 0.2, 0.0, True
    return flat


def align(sections, duration):
    lines = [l for s in sections for l in s["lines"]]
    keys = [f"{s['name']}|{j}" for s in sections for j in range(len(s["lines"]))]
    twords = [w for seg in json.load(open(TRANSCRIPT))["segments"] for w in seg["words"]]
    windows = line_windows(keys, [l["text"] for l in lines], twords, duration)
    model, meta = whisperx.load_align_model(language_code="en", device="cuda")
    lead_audio = whisperx.load_audio(STEMS["lead"])
    flat = aligned_words(model, meta, lead_audio, [{"start": a, "end": b, "text": l["text"]}
                                                   for l, (a, b) in zip(lines, windows)])
    pos = 0
    for l, win in zip(lines, windows):
        n = len(l["text"].split())
        l["words"] = [{"w": w["word"], "start": round(w["start"], 3), "end": round(w["end"], 3),
                       "score": round(w.get("score", 0.0), 3), **({"filled": True} if w.get("filled") else {})}
                      for w in flat[pos:pos + n]]
        l["window"] = [round(win[0], 3), round(win[1], 3)]
        pos += n
    # echoes on the backing stem: from the end of the lead line to the end of the next lead line
    back_audio = whisperx.load_audio(STEMS["backing"])
    echoes = [(i, l) for i, l in enumerate(lines) if l["backing"] and not l["backing"].lower().startswith("hey")]
    segs = []
    for i, l in echoes:
        a = l["words"][-1]["end"] - 0.3
        b = lines[i + 1]["words"][-1]["end"] if i + 1 < len(lines) else a + 3.0
        segs.append({"start": a, "end": b, "text": l["backing"]})
    if segs:
        flat = aligned_words(model, meta, back_audio, segs)
        pos = 0
        for (i, l), s in zip(echoes, segs):
            n = len(s["text"].split())
            ws = flat[pos:pos + n]
            pos += n
            l["echo"] = {"text": l["backing"], "start": round(ws[0]["start"], 3), "end": round(ws[-1]["end"], 3),
                         "stem": "backing", "words": [{"w": w["word"], "start": round(w["start"], 3),
                                                       "end": round(w["end"], 3), "score": round(w.get("score", 0.0), 3)}
                                                      for w in ws]}
    return lines


def level_db(path, frame_s):
    x, sr = sf.read(path, always_2d=True)
    x = x.mean(axis=1)
    hop = int(sr * frame_s)
    n = len(x) // hop
    return 20 * np.log10(np.sqrt((x[: n * hop].reshape(n, hop) ** 2).mean(axis=1)) + 1e-12)


def refine(lines, frame_s=0.02, below_median_db=10.0, gap_s=0.25):
    """As in Ever Present (from Folks Like Us): move lead word starts in silence to the first onset, and ends before a
    pause to where the voice drops. On the lead stem."""
    db = level_db(STEMS["lead"], frame_s)
    thr = np.median(db[db > -50]) - below_median_db
    loud = db >= thr
    words = [w for line in lines for w in line["words"]]
    f = lambda t: int(round(t / frame_s))
    for i, w in enumerate(words):
        a, b = f(w["start"]), f(w["end"])
        if not loud[a:a + 3].all():
            onset = next((k for k in range(a, b) if loud[k:k + 3].all()), None)
            if onset is not None:
                w["start_aligner"], w["start"] = w["start"], round(onset * frame_s, 3)
        nxt = words[i + 1]["start"] if i + 1 < len(words) else len(db) * frame_s
        if nxt - w["end"] >= gap_s or (w["end"] - w["start"] > 1.5 and nxt - w["end"] < 0.05):
            k = f(w["start"] + 0.1)
            while k < f(nxt) and loud[k:k + 5].any():
                k += 1
            w["end_aligner"], w["end"] = w["end"], round(min(k * frame_s, nxt), 3)
    for line in lines:
        line["start"], line["end"] = line["words"][0]["start"], line["words"][-1]["end"]
    return round(float(thr), 1)


def find_heys(lines, frame_s=0.01):
    """'{Hey!}': between the start of the line's last word and the next line's first word (max 2.5 s), Whisper's
    'hey' on the backing stem (timing/whisper_backing.json) if it heard one there, else the strongest backing-stem
    onset; 'found' is false when that onset is weak (the gang vocal sustains through most chorus Hey!s)."""
    y, sr = librosa.load(STEMS["backing"], sr=None, mono=True)
    hop = int(sr * frame_s)
    onset = librosa.onset.onset_strength(y=y, sr=sr, hop_length=hop)
    db = level_db(STEMS["backing"], frame_s)
    wb = [w for seg in json.load(open("timing/whisper_backing.json"))["segments"] for w in seg["words"]
          if norm(w["w"]) == "hey"]
    found = []
    for i, l in enumerate(lines):
        if not (l["backing"] and l["backing"].lower().startswith("hey")):
            continue
        a = l["words"][-1]["start"]
        nxt = lines[i + 1]["start"] if i + 1 < len(lines) else a + 2.5
        b = min(nxt + 0.1, a + 2.5)
        heard = [w for w in wb if a <= w["start"] < b]
        if heard:
            h = {"start": round(heard[0]["start"], 3), "end": round(heard[0]["end"], 3), "how": "whisper", "found": True}
        else:
            ia, ib = int(a / frame_s), int(b / frame_s)
            k = ia + int(np.argmax(onset[ia:ib]))
            peak = db[k:k + 15].max()
            floor = db[max(ia, k - 30):k + 1].min()
            e = k + 25
            while e < len(db) and e < k + 60 and db[e] > peak - 12:
                e += 1
            h = {"start": round(k * frame_s, 3), "end": round(e * frame_s, 3), "how": "onset",
                 "rise_db": round(float(min(peak - floor, 99)), 1), "found": bool(peak > -35 and peak - floor >= 8)}
        l["hey"] = {"text": l["backing"], "stem": "backing", **h}
        found.append(l["hey"])
    return found


def track(src, sr, span, hop, start_bpm):
    a, b = int(span[0] * sr), int(span[1] * sr)
    _, frames = librosa.beat.beat_track(y=src[a:b], sr=sr, hop_length=hop, start_bpm=start_bpm, tightness=400)
    return librosa.frames_to_time(frames, sr=sr, hop_length=hop) + span[0]


def beats(lines_by_key, duration):
    c = CFG["beats"]
    y, sr = librosa.load(STEMS["drums"], sr=None, mono=True)
    segs = [track(y, sr, s, c["hop"], c["start_bpm"]) for s in c["segments"]]
    times, src, seg_of = [], [], []
    stats = []
    for n, t in enumerate(segs):
        k = np.arange(len(t))
        p = np.polyfit(k, t, 1)
        stats.append({"span": c["segments"][n], "tracked": [round(float(t[0]), 3), round(float(t[-1]), 3)],
                      "n": len(t), "ibi_s": round(float(p[0]), 5), "bpm": round(60 / float(p[0]), 3),
                      "resid_sd_ms": round(float((t - np.polyval(p, k)).std() * 1000), 1)})
    ibis = [s["ibi_s"] for s in stats]
    # before segment 0: extend back at its interval
    t0 = segs[0][0]
    pre = [t0 - ibis[0] * m for m in range(int(t0 // ibis[0]), 0, -1)]
    times += pre; src += ["extrapolated"] * len(pre); seg_of += [0] * len(pre)
    gaps = []
    for n, t in enumerate(segs):
        times += list(t); src += ["tracked"] * len(t); seg_of += [n] * len(t)
        if n + 1 < len(segs):
            nxt = segs[n + 1][0]
            steps = (nxt - t[-1]) / ibis[n]
            if abs(steps - round(steps)) < 0.25:   # continuous: fill evenly
                m = int(round(steps))
                fill = [t[-1] + (nxt - t[-1]) * j / m for j in range(1, m)]
                gaps.append({"after_segment": n, "kind": "interpolated", "beats": m - 1,
                             "steps": round(float(steps), 3), "ibi_s": round((nxt - t[-1]) / m, 5)})
                kind = "interpolated"
            else:                                  # phase jump: extend, stop short of the next segment
                fill = [t[-1] + ibis[n] * j for j in range(1, int(steps)) if t[-1] + ibis[n] * j < nxt - 0.5 * ibis[n + 1]]
                gaps.append({"after_segment": n, "kind": "phase jump", "beats": len(fill), "steps": round(float(steps), 3),
                             "jump_s": round(float(nxt - (t[-1] + ibis[n] * round(steps))), 3)})
                kind = "extrapolated"
            times += fill; src += [kind] * len(fill); seg_of += [n] * len(fill)
    last = segs[-1][-1]
    post = [last + ibis[-1] * j for j in range(1, int((duration - last) // ibis[-1]) + 1)]
    times += post; src += ["extrapolated"] * len(post); seg_of += [len(segs) - 1] * len(post)
    times = np.array(times)
    # bars: per segment, the beat nearest the anchor is a downbeat; beats before the first anchor count back
    anchors = {}
    for n in range(len(segs)):
        ref = c["downbeat_anchors"][str(n)]
        if ref == "first":
            ta = segs[n][0]
        else:
            sec, li, wi = ref.split("|")
            ta = lines_by_key[(sec, int(li))]["words"][int(wi)]["start"]
        idx = [i for i in range(len(times)) if seg_of[i] == n]
        anchors[n] = min(idx, key=lambda i: abs(times[i] - ta))
    beat_in_bar = [0] * len(times)
    for n in range(len(segs)):
        a = anchors[n]
        for i in range(len(times)):
            if seg_of[i] == n or (n == 0 and seg_of[i] == 0):
                beat_in_bar[i] = (i - a) % 4 + 1
    # does segment 1's bar phase continue segment 0's across stop 1?
    a0, a1 = anchors[0], anchors.get(1)
    continuity = None if a1 is None else {"segments_0_1_same_bar_phase": (a1 - a0) % 4 == 0}
    bars, bar = [], 0
    for i in range(len(times)):
        if beat_in_bar[i] == 1 or i == 0:
            bar += 1
        bars.append(bar)
    r = lambda ts: [round(float(t), 3) for t in ts]
    return {"source": STEMS["drums"], "hop": c["hop"], "segments": stats, "gaps": gaps, "continuity": continuity,
            "beats": r(times), "beat_in_bar": beat_in_bar, "bar": bars, "kind": src, "segment": seg_of,
            "downbeats": r(times[[i for i in range(len(times)) if beat_in_bar[i] == 1]]),
            "reliable_span": c["reliable_span"],
            "remotion": {"fps": FPS, "beat_frames_at_100bpm": 18,
                         "drift_frames_per_100_beats": {f"segment {n}": round((s["ibi_s"] - 0.6) * 100 * FPS, 2)
                                                        for n, s in enumerate(stats)}}}


def stops(duration):
    x, sr = sf.read(MASTER, always_2d=True)
    m = np.abs(x).max(axis=1)
    db10 = level_db(MASTER, 0.01)
    out = {}
    for name, s in CFG["stops"].items():
        if name.startswith("_"):
            continue
        a, b = int(s["search_from"] * sr), int(s["search_to"] * sr)
        if s["mode"] == "silence":  # sample peak under -80 dBFS for the next 0.1 s
            q = m[a:b + int(0.1 * sr)] < 10 ** (-80 / 20)
            run = int(0.1 * sr)
            z = next(i for i in range(b - a) if q[i] and q[i:i + run].all())
            t = (a + z) / sr
        elif s["mode"] == "sound":
            z = np.where(m[a:b] > 10 ** (-60 / 20))[0]
            t = (a + z[0]) / sr
        else:  # drop
            t = None
            for k in range(int(s["search_from"] / 0.01), int(s["search_to"] / 0.01)):
                ref = np.median(db10[k - 30:k])
                if db10[k] < ref - 3 and all(db10[k + j] < ref - 3 for j in range(1, 10)):
                    t = k * 0.01
                    break
        out[name] = round(float(t), 3)
    return out


def clap_onsets():
    x, sr = sf.read(CFG["clap_track"]["file"], always_2d=True)
    db = level_db(CFG["clap_track"]["file"], 0.005)
    on, prev = [], -999
    for k in range(1, len(db)):
        if db[k] > -40 and db[k - 1] <= -40 and k * 0.005 - prev > 0.3:
            prev = k * 0.005
            on.append(round(prev, 3))
    return on


def drums_in(after=10.0):
    db = level_db(STEMS["drums"], 0.005)
    k = int(after / 0.005)
    while db[k] < -40:
        k += 1
    return round(k * 0.005, 3)


def main():
    info = sf.info(MASTER)
    duration = round(info.frames / info.samplerate, 3)
    sections = parse_lyrics()
    lines = align(sections, duration)
    thr = refine(lines)
    heys = find_heys(lines)
    by_key = {(s["name"], j): l for s in sections for j, l in enumerate(s["lines"])}
    for s in sections:
        s["start"] = s["lines"][0]["start"]
        for l in s["lines"]:
            if l["backing"] is None:
                del l["backing"]
    b = beats(by_key, duration)
    ev = stops(duration)
    first, last = sections[0]["lines"][0]["start"], sections[-1]["lines"][-1]["end"]
    i_back = next(i for i, t in enumerate(b["beats"]) if t > ev["stop1"] + 3 and b["kind"][i] == "tracked")
    ev.update({"first_vocal": first, "last_vocal": last, "drums_in": drums_in(), "band_back1": b["beats"][i_back],
               "claps": clap_onsets(), "music_end": duration})
    for inst in CFG["instrumental_sections"]:
        cue = inst["start"]
        t = float(cue[2:]) if cue.startswith("t:") else ev[cue.split(":", 1)[1]]
        sections.append({"name": inst["name"], "note": inst["note"], "lines": [], "start": t, "instrumental": True})
    sections.sort(key=lambda s: s["start"])
    for i, s in enumerate(sections):
        s["end"] = sections[i + 1]["start"] if i + 1 < len(sections) else duration
    tm = {
        "generated_by": "scripts/timing_map.py",
        "time": "song time: seconds on the master's timeline (video time = song time + the bookend lead-in, config/shot_cues.json)",
        "fps": FPS,
        "audio": {"master": str(MASTER), "sha256": sha256(MASTER), "duration_s": duration,
                  "review_audio": CFG["review_audio"]},
        "alignment": {"method": "whisperx.align (wav2vec2 en), one segment per lyric line; lead lines on the lead stem, echoes on the backing stem",
                      "lyrics": str(LYRICS), "anchors": str(TRANSCRIPT),
                      "refined": f"lead-stem level threshold {thr} dB; originals kept as start_aligner/end_aligner",
                      "heys": "strongest backing-stem onset after the line (found=false: weak, check by ear)"},
        "beats": b,
        "sections": sections,
        "events": ev,
    }
    OUT.parent.mkdir(exist_ok=True)
    json.dump(tm, open(OUT, "w"), indent=1, ensure_ascii=False)
    for s in b["segments"]:
        print(f"segment {s['span']}: {s['bpm']} bpm (ibi {s['ibi_s']} s, sd {s['resid_sd_ms']} ms), tracked {s['tracked']}")
    print("gaps:", b["gaps"], "| continuity:", b["continuity"])
    print(f"{len(b['beats'])} beats, {len(b['downbeats'])} downbeats; Remotion drift (frames per 100 beats at 18 f/beat):",
          b["remotion"]["drift_frames_per_100_beats"])
    print("events:", {k: v for k, v in ev.items() if k != "claps"}, "claps", ev["claps"])
    for s in sections:
        print(f"{s['name']:14s} {s['start']:7.2f}-{s['end']:7.2f}  {len(s['lines'])} lines")
    words = [w for l in lines for w in l["words"]]
    print(f"{len(words)} lead words; low score (<0.3): {[(w['w'], w['start'], w['score']) for w in words if w['score'] < 0.3]}")
    print("heys:", [(h["start"], h["how"], h["found"], h.get("rise_db")) for h in heys])
    print("echoes:", [(l["echo"]["text"], l["echo"]["start"], l["echo"]["end"]) for l in lines if "echo" in l])


if __name__ == "__main__":
    main()
