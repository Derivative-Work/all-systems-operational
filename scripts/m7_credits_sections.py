"""M7: the credits instrumental's sections as the agent has them (timing/credits_grid.json, scripts/m7_credits.py), for
the human to check by ear (human interventions 27):
  review/m7_credits_sections.png               level and low band over time, each section change marked and named, the
                                               end cards' spans under it, the part not used hatched
  review/m7/audio/credits-sections-marked.mp3  the full post-filtered track with a click on every section change (low
                                               click) and on the card changes that fall on a downbeat instead (high click)
  review/m7/credits_sections.txt               the same as labels (start, end, name: tab-separated; Audacity's format)
The names are the agent's reading of the measurements (level and the band under 150 Hz), not the track's own labels.
Usage: .venv/bin/python -I scripts/m7_credits_sections.py
"""
import json
import subprocess
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import soundfile as sf  # noqa: E402
from matplotlib.patches import Rectangle  # noqa: E402

G = json.loads(Path("timing/credits_grid.json").read_text())
PF = Path(G["audio"])
plan = dict(ln.split() for ln in Path("review/m7_end/plan.txt").read_text().splitlines())
end_s = int(plan.pop("M7-EndSequence")) / 30
CARDS = [("end card", "M7-End-end"), ("Next incident: TBD", "M7-End-final"), ("fact 1", "M7-End-fact1"),
         ("fact 2", "M7-End-fact2"), ("fact 3", "M7-End-fact3"), ("fact 4", "M7-End-fact4"), ("disclosure", "M7-End-disclosure")]
spans, t = [], 0.0
for name, cid in CARDS:
    d = int(plan[cid]) / 30
    spans.append((name, t, t + d))
    t += d

# the agent's names for what changes at each section change (from level_db and low_db; checked against the log)
NAMES = {22.869: "kick and bass in", 34.453: "bass out (1 bar)", 39.077: "bass out (1 bar)", 41.381: "full band back",
         60.043: "louder section", 76.080: "bass out, quieter", 89.952: "quieter: lead-up to the drop",
         94.571: "bass out (1 bar)", 96.869: "the drop (biggest change)", 115.291: "bass out (1 bar)",
         117.451: "bass back", 124.469: "breakdown", 133.643: "swell (1 bar)", 135.952: "back down",
         142.677: "build", 153.691: "drop-out (1 bar)", 155.979: "back in (1 bar)", 158.267: "out again (1 bar)",
         160.560: "final drop"}
secs = G["sections"]
for s in secs:
    s["name"] = NAMES.get(s["t"], "change")
beats = np.array(G["beats_s"])
extra = [(f"beat stops (last tracked beat)", float(beats[-1]))]

y, sr = sf.read(PF, always_2d=True)
m = y.mean(axis=1)
hop = int(0.25 * sr)
tt = np.arange(0, len(m) - hop, hop) / sr
lvl = np.array([20 * np.log10(np.sqrt(np.mean(m[int(a * sr):int(a * sr) + hop] ** 2)) + 1e-9) for a in tt])
spec = np.abs(np.fft.rfft(np.lib.stride_tricks.sliding_window_view(m, 4096)[::hop] * np.hanning(4096), axis=1))
fq = np.fft.rfftfreq(4096, 1 / sr)
low = 20 * np.log10(np.sqrt((spec[:, fq < 150] ** 2).sum(axis=1)) / 4096 * 2 + 1e-9)
low = low[:len(tt)]
tt_low = tt[:len(low)]

# ---- the chart
SURF, INK, INK2, MUTED, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#8b8a85", "#e6e5e1"
S1, S2 = "#2a78d6", "#eb6834"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 13, "text.color": INK, "axes.labelcolor": INK2,
                     "xtick.color": INK2, "ytick.color": INK2})
fig = plt.figure(figsize=(24, 14), dpi=100, facecolor=SURF)
ax = fig.add_axes([0.04, 0.47, 0.94, 0.42], facecolor=SURF)
bx = fig.add_axes([0.04, 0.30, 0.94, 0.09], facecolor=SURF, sharex=ax)
kx = fig.add_axes([0.04, 0.01, 0.94, 0.22], facecolor=SURF)
kx.axis("off")
smooth = lambda v: np.convolve(v, np.ones(3) / 3, mode="same")  # noqa: E731  (0.75 s)
lvl, low = smooth(lvl), smooth(low)
L = G["length_s"]
ax.plot(tt, lvl, color=S1, lw=2, label="level (RMS, dBFS)")
ax.plot(tt_low, low, color=S2, lw=2, label="under 150 Hz (dB)")
ax.set_xlim(0, L)
ax.set_ylim(-75, -2)
ax.grid(axis="y", color=GRID, lw=1)
for sp in ("top", "right", "left"):
    ax.spines[sp].set_visible(False)
ax.spines["bottom"].set_color(GRID)
ax.set_ylabel("dB")
ax.text(tt[-1] + 1, lvl[-8], "", color=INK2)
ax.legend(loc="lower left", frameon=False, ncol=2, fontsize=13, bbox_to_anchor=(0.0, 1.0))
fmt = lambda s: f"{int(s // 60)}:{s % 60:04.1f}"  # noqa: E731
# each change numbered at the top of its line (two staggered rows where lines are close); the names go in the key below
key = []
prev = -99
row = 0
for i, s in enumerate(secs, 1):
    strong = s["strength"] >= 20
    ax.axvline(s["t"], color=INK if strong else MUTED, lw=1.8 if strong else 1, zorder=0)
    row = 1 - row if s["t"] - prev < 6 else 0
    prev = s["t"]
    ax.text(s["t"], -6 - row * 4.5, str(i), ha="center", va="center", fontsize=12, color=INK, fontweight="bold" if strong else "normal",
            bbox={"facecolor": SURF, "edgecolor": INK if strong else MUTED, "boxstyle": "round,pad=0.25", "lw": 1})
    key.append((str(i), s["t"], s["name"] + f"  (level {s['level_db']:+.1f}, low {s['low_db']:+.1f} dB)", strong))
fades = G["ends_s"]
for x in fades[:-1]:
    ax.axvline(x, color=INK, lw=1.2, ls=(0, (2, 2)))
    ax.text(x, -71, "F", ha="center", va="center", fontsize=12, color=INK, bbox={"facecolor": SURF, "edgecolor": INK, "boxstyle": "round,pad=0.25"})
    key.append(("F", x, "fade-out point: the music thins (the end sequence ends here)", True))
for name, x in extra:
    ax.axvline(x, color=MUTED, lw=1, ls=(0, (4, 3)), zorder=0)
    ax.text(x, -71, "B", ha="center", va="center", fontsize=12, color=INK2, bbox={"facecolor": SURF, "edgecolor": MUTED, "boxstyle": "round,pad=0.25"})
    key.append(("B", x, "last tracked beat; the outro follows", False))
key.sort(key=lambda k: k[1])
per = (len(key) + 2) // 3
for j, (lab, x, text, strong) in enumerate(key):
    c, r = divmod(j, per)
    kx.text(c / 3, 1 - r * (1 / per), f"{lab:>2}   {fmt(x)}   {text}", transform=kx.transAxes, fontsize=12.5, va="top",
            color=INK, fontweight="bold" if strong else "normal", family="DejaVu Sans Mono")
ax.set_title(f"Credits instrumental, post-filtered ({fmt(L)}): section changes as the agent measured them "
             f"(bold: the strongest; names in the key below). Tempo drifts from about 103 to 105 bpm.", loc="left", fontsize=16, color=INK, pad=34)
plt.setp(ax.get_xticklabels(), visible=False)

# card spans
greys = ["#d9d7d1", "#c4c2bb"]
for i, (name, a, b) in enumerate(spans):
    bx.add_patch(Rectangle((a + 0.15, 0.15), b - a - 0.3, 0.7, facecolor=greys[i % 2], edgecolor="none"))
    short = "TBD" if name.startswith("Next") else name
    bx.text((a + b) / 2, 0.5, short if b - a < 10 else f"{short}\n{fmt(a)}-{fmt(b)}", ha="center", va="center", fontsize=11.5, color=INK)
bx.add_patch(Rectangle((end_s + 0.15, 0.15), L - end_s - 0.3, 0.7, facecolor=SURF, edgecolor=MUTED, hatch="//", lw=1))
bx.text((end_s + L) / 2, 0.5, f"not used ({fmt(end_s)}-{fmt(L)})", ha="center", va="center", fontsize=12, color=INK2,
        bbox={"facecolor": SURF, "edgecolor": "none", "pad": 2})
bx.set_ylim(0, 1)
bx.set_yticks([])
for sp in ("top", "right", "left"):
    bx.spines[sp].set_visible(False)
bx.spines["bottom"].set_color(GRID)
bx.set_xticks(np.arange(0, L, 15))
bx.set_xticklabels([fmt(x)[:-2] for x in np.arange(0, L, 15)])
bx.set_xlabel("track time (m:ss); the end sequence starts with the track")
bx.text(0, 1.08, "End cards (each at least its reading time; changes on the strongest section change after it, else the next downbeat)",
        transform=bx.transAxes, fontsize=12.5, color=INK2)
fig.savefig("review/m7_credits_sections.png", facecolor=SURF)
print("review/m7_credits_sections.png")

# ---- labels
Path("review/m7").mkdir(parents=True, exist_ok=True)
rows = [(0.0, secs[0]["t"], "intro (no beat)")]
for s, n in zip(secs, secs[1:] + [{"t": float(beats[-1])}]):
    rows.append((s["t"], n["t"], f"{s['name']} (level {s['level_db']:+.1f} dB, under 150 Hz {s['low_db']:+.1f} dB)"))
rows.append((float(beats[-1]), L, "outro (no beat tracked)"))
lines = [f"{a:.3f}\t{b:.3f}\t{n}" for a, b, n in rows]
lines += [f"{a:.3f}\t{b:.3f}\tCARD {n}" for n, a, b in spans]
lines += [f"{x:.3f}\t{x:.3f}\tFADE-OUT POINT" for x in fades[:-1]]
Path("review/m7/credits_sections.txt").write_text("\n".join(lines) + "\n")
print("review/m7/credits_sections.txt", len(lines), "labels")

# ---- marked audio: a low click on each section change, a high click on card changes that aren't on one
def click(f, ms=18, db=-14):
    n = int(sr * ms / 1000)
    return (10 ** (db / 20)) * np.sin(2 * np.pi * f * np.arange(n) / sr) * np.hanning(n)
out = y.copy()
sec_t = [s["t"] for s in secs]
marks = [(t_, click(880)) for t_ in sec_t]
marks += [(a, click(1760)) for _, a, _ in spans[1:] if min(abs(a - x) for x in sec_t) > 0.05]
marks += [(fades[0], click(1760, ms=40))]
for t_, c in marks:
    i = int(t_ * sr)
    j = min(len(out), i + len(c))
    out[i:j] += c[:j - i, None]
tmp = Path("review/m7/audio/.marked.wav")
tmp.parent.mkdir(parents=True, exist_ok=True)
sf.write(tmp, out, sr, subtype="PCM_24")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(tmp), "-c:a", "libmp3lame", "-b:a", "320k",
                "review/m7/audio/credits-sections-marked.mp3"], check=True)
tmp.unlink()
print("review/m7/audio/credits-sections-marked.mp3", len(marks), "clicks")
