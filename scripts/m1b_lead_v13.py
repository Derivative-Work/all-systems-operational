"""M1b: the lead vocal as it sits in the v1.3 master, and its transcript, for scripts/timing_map.py.

The human repainted the bridge (lyrics v1.3) in Suno and re-bounced the master in Logic with the repaint on the lead
track (human interventions 24). Outside the bridge the new master is the old one to float rounding (production log),
so the lead is the old lead stem with the repaint spliced in over the repaint's own sounding span (150.98-170.10 s;
the master's change starts at the same sample and the old lead's tail after 170.10 s is still in the master).
The transcript is merged the same way at word level: the old lead transcript's words outside the span, the repaint
transcript's inside.

Usage: .venv/bin/python -I scripts/m1b_lead_v13.py
Writes: audio/stems/0 Lead Vocals v1.3.aif (git-ignored; in the manifest), timing/whisper_lead_v13.json
"""
import json

import numpy as np
import soundfile as sf

OLD = "audio/stems/0 Lead Vocals.aif"
REPAINT = "audio/stems/0a Lead Vocals repaint.aif"
OUT = "audio/stems/0 Lead Vocals v1.3.aif"
T_OLD, T_REPAINT, T_OUT = "timing/whisper_lead.json", "timing/whisper_lead_repaint.json", "timing/whisper_lead_v13.json"

old, sr = sf.read(OLD, dtype="int16")
rp, sr2 = sf.read(REPAINT, dtype="int16")
assert sr == sr2 == 48000 and old.shape[1] == rp.shape[1] == 2
nz = np.nonzero(np.any(rp != 0, axis=1))[0]
a, b = int(nz[0]), int(nz[-1]) + 1
lead = old.copy()
lead[a:b] = rp[a:b]
sf.write(OUT, lead, sr, format="AIFF", subtype="PCM_16")
t0, t1 = a / sr, b / sr
print(f"repaint spliced over samples {a}-{b} ({t0:.3f}-{t1:.3f} s) -> {OUT}")

told, trp = json.load(open(T_OLD)), json.load(open(T_REPAINT))
segs = []
for s in told["segments"]:
    words = [w for w in s["words"] if w["start"] < 0 or w["end"] <= t0 or w["start"] >= t1]
    if not words:
        continue
    if len(words) < len(s["words"]):  # split a segment that straddles the span into its two sides
        for side in ([w for w in words if 0 <= w["end"] <= t0], [w for w in words if w["start"] >= t1]):
            if side:
                segs.append({"start": side[0]["start"], "end": side[-1]["end"],
                             "text": " ".join(w["w"] for w in side), "words": side, "from": T_OLD})
    else:
        segs.append({**s, "from": T_OLD})
for s in trp["segments"]:
    words = [w for w in s["words"] if t0 <= w["start"] < t1]
    segs.append({"start": words[0]["start"], "end": words[-1]["end"], "text": " ".join(w["w"] for w in words),
                 "words": words, "from": T_REPAINT})
segs.sort(key=lambda s: s["start"])
json.dump({"model": told["model"], "stem": OUT, "merged_from": [T_OLD, T_REPAINT], "span": [round(t0, 3), round(t1, 3)],
           "segments": segs}, open(T_OUT, "w"), indent=1)
print(f"{len(segs)} segments -> {T_OUT}")
