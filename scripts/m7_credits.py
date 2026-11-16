"""M7: the credits instrumental (human interventions 26): what the post-filter changed, its beats and its section changes,
for timing the end sequence's card changes (config/end_cards_m7.json snap; remotion/src/components/EndCards.tsx).
The tempo drifts (about 103 bpm early to 105 late), so the beats are tracked (librosa's dynamic programming) rather
than a straight grid. A section change is a tracked downbeat (every fourth beat from the first, which the kick's entry
and most changes confirm) where the 4 beats after differ from the 4 before by more than 2.5 dB in level or 10 dB in
the low band (under 150 Hz), each moved to the strongest onset within 0.2 s; in the beatless intro, the bar lines
extrapolated back from the first beat. A fade-out point is where the music thins (the level falls by 5 dB or more over
a beat or two) and the track's end.
Usage: .venv/bin/python -I scripts/m7_credits.py  -> timing/credits_grid.json, log/render_logs/m7_credits_analysis.log
"""
import json
from pathlib import Path

import librosa
import numpy as np
import soundfile as sf

SRC = Path("audio/credits/All Systems Operational (credits EDM).wav")
PF = Path("audio/postfilter/all-systems-operational-credits-deslopped.wav")
out = []
say = lambda s: (print(s), out.append(s))  # noqa: E731

x, sr = sf.read(SRC, always_2d=True)
y, sr2 = sf.read(PF, always_2d=True)
assert sr == sr2 == 48000 and len(x) == len(y), (sr, sr2, len(x), len(y))
db = lambda v: 10 * np.log10(np.mean(v ** 2) + 1e-20)  # noqa: E731
say(f"length {len(x) / sr:.3f} s; sample peaks: input {20 * np.log10(np.abs(x).max()):.2f} dBFS, post-filtered {20 * np.log10(np.abs(y).max()):.2f} dBFS")
say(f"post-filter change re its input: whole {db(y - x) - db(x):.1f} dB")
per = [(int(t), db(y[t * sr:(t + 1) * sr] - x[t * sr:(t + 1) * sr]) - db(x[t * sr:(t + 1) * sr])) for t in range(int(len(x) / sr))]
loudest = sorted(per, key=lambda p: -p[1])[:5]
say("  the 5 seconds it changed most (dB re the music): " + ", ".join(f"{t} s {v:.1f}" for t, v in loudest))

mono = y.mean(axis=1).astype(np.float32)
hop = 256
env = librosa.onset.onset_strength(y=mono, sr=sr, hop_length=hop)
ft = librosa.frames_to_time(np.arange(len(env)), sr=sr, hop_length=hop)
tempo, beats = librosa.beat.beat_track(onset_envelope=env, sr=sr, hop_length=hop, units="time", start_bpm=104, tightness=100)
ibi = np.diff(beats)
say(f"tracked beats: {len(beats)}, {beats[0]:.3f}-{beats[-1]:.3f} s; spacing by 30 s: " + ", ".join(
    f"{a}-{a + 30} s {np.median(ibi[(beats[:-1] >= a) & (beats[:-1] < a + 30)]):.4f}" for a in range(0, 200, 30)
    if ((beats[:-1] >= a) & (beats[:-1] < a + 30)).sum() > 2))
S = np.abs(librosa.stft(mono, n_fft=2048, hop_length=hop))
lowE = S[librosa.fft_frequencies(sr=sr, n_fft=2048) < 150].sum(axis=0)
fr = lambda t: int(librosa.time_to_frames(t, sr=sr, hop_length=hop))  # noqa: E731
def lv(a, b):
    return 20 * np.log10(np.sqrt(np.mean(mono[int(a * sr):int(b * sr)] ** 2)) + 1e-9)
bl = np.array([lv(beats[i], beats[i + 1]) for i in range(len(beats) - 1)])
ll = np.array([20 * np.log10(lowE[fr(beats[i]):fr(beats[i + 1])].mean() + 1e-9) for i in range(len(beats) - 1)])
def refine(t):
    s = (ft > t - 0.2) & (ft < t + 0.2)
    return float(ft[s][np.argmax(env[s])])
bounds, ends = [], []
for i in range(4, len(bl) - 4, 4):
    d, dl = bl[i:i + 4].mean() - bl[i - 4:i].mean(), ll[i:i + 4].mean() - ll[i - 4:i].mean()
    if abs(d) > 2.5 or abs(dl) > 10:
        bounds.append((refine(beats[i]), i, d, dl))
    k = min(i + 2, len(bl))
    if bl[i:k].mean() - bl[i - 4:i].mean() <= -5:
        ends.append((beats[i], i))
P = float(np.median(ibi[:16]))
intro = [beats[0] - 4 * P * k for k in range(1, int(beats[0] // (4 * P)) + 1)][::-1]
intro = [refine(t) for t in intro if t > 2.0]
say(f"intro bar lines (from the first beat back, {4 * P:.3f} s a bar): " + ", ".join(f"{t:.3f}" for t in intro))
say("section changes (downbeat, beat index, level and low-band change in dB):")
for t, i, d, dl in bounds:
    say(f"  {t:8.3f}  beat {i:3d}  level {d:+5.1f}  low {dl:+6.1f}")
# fade-out points: the music's own thinning (the quietest 0.1 s inside the drop), and the track's end
fades = []
for t, i in ends:
    w = int(0.1 * sr)
    a0, a1 = beats[i], beats[min(i + 4, len(beats) - 1)]
    q = [(lv(a, a + 0.1), a) for a in np.arange(a0, a1, 0.05)]
    fades.append(round(float(min(q)[1]), 3))
fades = sorted(set(fades)) + [round(len(y) / sr, 3)]
say("fade-out points: " + ", ".join(f"{t:.3f}" for t in fades))
a = np.abs(mono)
say(f"first sound above -60 dBFS at {np.argmax(a > 1e-3) / sr:.3f} s; last at {(len(a) - np.argmax(a[::-1] > 1e-3)) / sr:.3f} s")
Path("timing/credits_grid.json").write_text(json.dumps({
    "_doc": "scripts/m7_credits.py: the post-filtered credits instrumental's tracked beats, downbeats (the beatless intro's "
            "extrapolated), section changes (strength: the level and low-band changes in dB, summed) and fade-out "
            "points (audio time, s, from the track's start, which is the end sequence's first frame), for the M7 end "
            "sequence (config/end_cards_m7.json snap).",
    "audio": str(PF), "length_s": round(len(y) / sr, 4),
    "sections": [{"t": round(float(t), 3), "strength": round(float(abs(d) + abs(dl)), 1), "level_db": round(float(d), 1),
                  "low_db": round(float(dl), 1), "beat": int(i)} for t, i, d, dl in bounds],
    "downbeats_s": [round(t, 3) for t in intro] + [round(float(b), 3) for b in beats[::4]],
    "ends_s": fades,
    "beats_s": [round(float(b), 4) for b in beats]}, indent=1) + "\n")
Path("log/render_logs/m7_credits_analysis.log").write_text("\n".join(out) + "\n")
