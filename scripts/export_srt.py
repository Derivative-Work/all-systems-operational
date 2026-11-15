"""M2: the lyrics as sung, as SRTs from timing/timing_map.json, for checking sync by ear (and the start of M8's captions).

Adapted from Ever Present's scripts/timing_map.py (write_srt) and scripts/export_srt.py (the line rule), commit 726343c.
- lyrics/as_sung_lines.srt: one cue per lead line, with its backing Hey! or echo in parentheses as in the lyrics;
  a line shows from its first word to the next line's start, capped TAIL_S after its last sound, at least MIN_S,
  never overlapping the next.
- lyrics/as_sung_words.srt: one cue per word (lead words, then the backing Hey!s and echoes, merged in time order;
  a backing cue may overlap a lead one).
Song time (the master). Pass --video to add the bookend lead-in (config/shot_cues.json lead_in_s) for the edit.
Usage: .venv/bin/python -I scripts/export_srt.py [--video]
"""
import json
import sys

TAIL_S, MIN_S = 1.0, 1.0
tm = json.load(open("timing/timing_map.json"))
video = "--video" in sys.argv
off = json.load(open("config/shot_cues.json"))["lead_in_s"] if video else 0.0
suffix = "_video" if video else ""


def ts(t):
    ms = int(round((t + off) * 1000))
    return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"


def write(path, items):
    with open(path, "w", encoding="utf-8") as f:
        for n, (a, b, text) in enumerate(items, 1):
            f.write(f"{n}\n{ts(a)} --> {ts(b)}\n{text}\n\n")
    print(path, len(items), "cues")


lines = [l for s in tm["sections"] for l in s["lines"]]
cues = []
for i, l in enumerate(lines):
    extra = l.get("hey") or l.get("echo")
    text = l["text"] + (f" ({extra['text']})" if extra else "")
    last = max(l["end"], extra["end"] if extra else 0)
    nxt = lines[i + 1]["start"] if i + 1 < len(lines) else 1e9
    end = min(max(l["start"] + MIN_S, last + TAIL_S if last + TAIL_S < nxt else nxt), nxt)
    cues.append((l["start"], end, text))
write(f"lyrics/as_sung_lines{suffix}.srt", cues)
words = [(w["start"], max(w["end"], w["start"] + 0.15), w["w"]) for l in lines for w in l["words"]]
for l in lines:
    if l.get("echo"):
        words += [(w["start"], max(w["end"], w["start"] + 0.15), f"({w['w']})") for w in l["echo"]["words"]]
    if l.get("hey"):
        h = l["hey"]
        words.append((h["start"], max(h["end"], h["start"] + 0.3), f"({h['text']})" + ("" if h["found"] else " ?")))
write(f"lyrics/as_sung_words{suffix}.srt", sorted(words))
