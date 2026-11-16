"""M1b: what changed between the v1.2 and v1.3 masters, and what the post-filter did to each.

Usage: .venv/bin/python -I scripts/m1b_compare.py > log/render_logs/m1b_compare.log
Reads the archived v1.2 master and post-filter output (archive/audio/v1.2/) and the current ones (audio/), the old
lead stem, and the v1.3 lead (scripts/m1b_lead_v13.py).
"""
import numpy as np
import soundfile as sf

SR = 48000
LAT = 47  # the Logic master lags the stems by 47 samples (cross-correlation, lead stem vs master)


def load(p):
    x, sr = sf.read(p, dtype="float64")
    assert sr == SR
    return x


def db(x):
    return 10 * np.log10(np.mean(x ** 2) + 1e-30)


mo = load("archive/audio/v1.2/track/All Systems Operational.wav")
mn = load("audio/track/All Systems Operational.wav")
po = load("archive/audio/v1.2/postfilter/all-systems-operational-master-deslopped.wav")
pn = load("audio/postfilter/all-systems-operational-master-deslopped.wav")
ol = load("audio/stems/0 Lead Vocals.aif")
nl = load("audio/stems/0 Lead Vocals v1.3.aif")
print(f"lengths (samples): v1.2 master {len(mo)}, v1.3 master {len(mn)}, post-filtered {len(po)} / {len(pn)}")

# 1. Where the masters differ: runs of differing samples merged over gaps < 50 ms, each run's difference level
d = mn - mo
idx = np.nonzero(np.any(d != 0, axis=1))[0]
runs, s, p = [], idx[0], idx[0]
for i in idx[1:]:
    if i - p > int(0.05 * SR):
        runs.append((s, p + 1))
        s = i
    p = i
runs.append((s, p + 1))
print("\n1. Masters (v1.3 - v1.2): runs of differing samples")
small = [r for r in runs if db(d[r[0]:r[1]]) - db(mo[r[0]:r[1]]) < -100]
for a, b in runs:
    rel = db(d[a:b]) - db(mo[a:b])
    if rel >= -100:
        print(f"  {a / SR:9.3f}-{b / SR:9.3f} s  difference {rel:6.1f} dB re the music, max |diff| {np.abs(d[a:b]).max():.3g}")
print(f"  plus {len(small)} short runs at {min(db(d[a:b]) - db(mo[a:b]) for a, b in small):.0f} to "
      f"{max(db(d[a:b]) - db(mo[a:b]) for a, b in small):.0f} dB re the music (float rounding), "
      f"{small[0][0] / SR:.1f}-{small[-1][1] / SR:.1f} s")

# 2. Is the bridge change the lead swap? The master change against the lead change, at the master's latency
a0, a1 = int(150.9 * SR), int(170.6 * SR)
x, y = d[a0 + LAT:a1 + LAT].ravel(), (nl - ol)[a0:a1].ravel()
print(f"\n2. Bridge 150.9-170.6 s: correlation of the master's change with the lead's change: {x @ y / np.sqrt((x @ x) * (y @ y)):.3f}")
print("   per 1 s: the master's change after removing the best-fit lead change, dB re the music")
row = []
for t in range(151, 170):
    s0 = t * SR
    a, b = d[s0 + LAT:s0 + LAT + SR].ravel(), (nl - ol)[s0:s0 + SR].ravel()
    g = (a @ b) / (b @ b + 1e-20)
    row.append(f"{t}:{db(a - g * b) - db(mn[s0:s0 + SR]):.0f}")
print("   " + " ".join(row))

# 3. Stop 1's first clap (94.385 s): timing and level
c0, c1 = int(94.335 * SR), int(94.635 * SR)
xo, xn = mo[c0:c1, 0], mn[c0:c1, 0]
cc = np.correlate(xn, xo, "full")
print(f"\n3. Stop 1's first clap: lag {np.argmax(cc) - (len(xo) - 1)} samples; level v1.2 {db(mo[c0:c1]):.1f} dB, "
      f"v1.3 {db(mn[c0:c1]):.1f} dB; difference {db(d[c0:c1]) - db(mo[c0:c1]):.1f} dB re the clap; "
      f"first 20 ms {db(d[int(94.38 * SR):int(94.40 * SR)]) - db(mo[int(94.38 * SR):int(94.40 * SR)]):.1f} dB")
for t in (95.59, 96.79, 97.995):
    s0 = int((t - 0.05) * SR)
    print(f"   clap at {t} s: difference {db(d[s0:s0 + int(0.3 * SR)]) - db(mo[s0:s0 + int(0.3 * SR)]):.0f} dB re the clap")

# 4. The post-filter: its change on each master, and the two outputs against each other
outside = np.r_[0:int(145 * SR), int(175 * SR):len(mn)]
br = slice(151 * SR, 170 * SR)
print("\n4. Post-filter (music-deslop 68441e2, m6f_10k, --source suno)")
print(f"   change re its input: whole v1.2 {db(po - mo) - db(mo):.1f} dB, v1.3 {db(pn - mn) - db(mn):.1f} dB; "
      f"bridge v1.2 {db(po[br] - mo[br]) - db(mo[br]):.1f}, v1.3 {db(pn[br] - mn[br]) - db(mn[br]):.1f}; "
      f"outside 145-175 s v1.2 {db(po[outside] - mo[outside]) - db(mo[outside]):.1f}, v1.3 {db(pn[outside] - mn[outside]) - db(mn[outside]):.1f}")
print(f"   sample peaks: v1.3 master {20 * np.log10(np.abs(mn).max()):.2f} dBFS, post-filtered {20 * np.log10(np.abs(pn).max()):.2f} dBFS")
dp = pn - po
print(f"   v1.3 vs v1.2 post-filtered, outside 145-175 s: {db(dp[outside]) - db(po[outside]):.1f} dB re the music")
row = []
for t in list(range(88, 102)) + list(range(140, 152)) + list(range(169, 180)):
    s0 = t * SR
    row.append(f"{t}:{db(dp[s0:s0 + SR]) - db(po[s0:s0 + SR]):.0f}")
print("   per 1 s (dB re the music): " + " ".join(row))
