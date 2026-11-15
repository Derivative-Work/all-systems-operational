"""M5: the animatic, every shot at 960x540, 30 fps, cut to the post-filtered master (brief, M5; plan M5).

Adapted from Ever Present's scripts/animatic.py (9301de4): every shot in timing/shot_times.json becomes one segment of
exactly (end_frame - start_frame) frames, so the cut stays on the M2 cues (approved, human interventions 9); the
segments are joined and the master laid under them, with the 8.4 s bookend lead-in before it. Changes: frames are
composited here in numpy (Remotion overlays with alpha, the O04 phone screen pinned to the Blender phone, the O06 clip
cropped to fill, the O07 alternate, O22's home-movie grade), not by ffmpeg filters; the end sequence adds the full
disclosure card after the fact card (decisions 11); review labels are drawn small at the top centre.

Sources per shot:
- Remotion: renders/m5/remotion/<composition>.mp4 (scripts/m5_remotion.sh), overlays <composition>.mov (alpha)
- Blender: renders/m5/frames_blender/<shot>/####.jpg (blender/animatic.py)
- O06: assets/gen/clips/O06/O06_s41.mp4 (human interventions 12), 24 -> 30 fps by time, cropped to fill
- O07 alternate: assets/gen/stills/O07_fogtower/O07_fogtower_s44.png, the server cut-out (renders/m5/O07t.png)
  on the lawn, the tower's top half pixelated (stalled), a slow push

Usage: .venv/bin/python -I scripts/animatic.py [--out review/m5_animatic.mp4] [--o07 server|fogtower]
       [--excerpt O05:O08 --out review/m5_o07_server.mp4] [--only O04,O06 (segments only)]
"""
import argparse
import json
import subprocess
from pathlib import Path

import cv2
import numpy as np

W, H, FPS = 960, 540, 30
TS = json.load(open("timing/shot_times.json"))
SHOTS = TS["shots"]
SEEDS = json.load(open("config/seeds.json"))
MASTER = json.load(open("config/timing.json"))["review_audio"]
REM = Path("renders/m5/remotion")
BL = Path("renders/m5/frames_blender")      # frame sequences: out of the manifest (scripts/manifest.sh), regenerable
SEG = Path("renders/m5/segments")
O06_CLIP = "assets/gen/clips/O06/O06_s41.mp4"
O07_TOWER = "assets/gen/stills/O07_fogtower/O07_fogtower_s44.png"
DISCLOSURE_FRAMES = TS["overlays"]["disclosure"]["end_frame"] - TS["overlays"]["disclosure"]["start_frame"]
O19A, XF = 175, 10                       # blender/animatic.py: O19's two parts and their cross-fade
O08_PHONE = (45, 115)                    # O08 inserts (frames in the shot): IT's reply from echo 1 to echo 2,
O08_TREE = (115, 187)                    # then the treehouse cutaway for 4 beats (decisions 11)
END = [("O24", "M5-O24-EndCard", 180), ("O24", "M5-O24-FinalCard", 90), ("fact", "M5-FactCard", 450),
       ("disclosure", "M5-DisclosureCard", DISCLOSURE_FRAMES)]


def nfr(sid):
    s = SHOTS[sid]
    return s["end_frame"] - s["start_frame"]


def mark(sid, i):
    return SHOTS[sid]["marks"][i]["frame_in_shot"]


# ---------------------------------------------------------------- readers

def read_video(path, n=None, pix="bgr24", size=(W, H), fill=False):
    """Decode a video (or image sequence pattern) to a list of frames at size; fill=True scales to cover and
    centre-crops (no letterbox)."""
    vf = f"scale={size[0]}:{size[1]}" if not fill else \
        f"scale={size[0]}:{size[1]}:force_original_aspect_ratio=increase,crop={size[0]}:{size[1]}"
    cmd = ["ffmpeg", "-v", "error", "-i", str(path), "-vf", vf, "-f", "rawvideo", "-pix_fmt", pix, "-"]
    raw = subprocess.run(cmd, check=True, capture_output=True).stdout
    c = 4 if pix in ("bgra", "rgba") else 3
    a = np.frombuffer(raw, np.uint8).reshape(-1, size[1], size[0], c).copy()
    frames = list(a)
    if n is not None:
        frames = (frames + [frames[-1]] * n)[:n]
    return frames


def blender(sid, n):
    d = BL / sid
    files = sorted(d.glob("[0-9]*.jpg"))
    if len(files) < n:
        raise SystemExit(f"{sid}: {len(files)} frames rendered, {n} needed (blender/animatic.py)")
    return [cv2.resize(cv2.imread(str(f)), (W, H), interpolation=cv2.INTER_AREA) for f in files[:n]]


def over(base, ovl, start=0):
    """Alpha-composite overlay frames (BGRA) onto base frames from base index `start`."""
    for i, o in enumerate(ovl):
        j = start + i
        if j >= len(base):
            break
        a = o[:, :, 3:4].astype(np.float32) / 255.0
        base[j] = (base[j].astype(np.float32) * (1 - a) + o[:, :, :3].astype(np.float32) * a).astype(np.uint8)
    return base


def overlay(name, n):
    return read_video(REM / f"{name}.mov", n, pix="bgra")


# ---------------------------------------------------------------- special shots

def phone_quad(f, prev):
    """O04: the Blender phone's blank screen: the largest bright quad in the lower 60% of the frame."""
    g = cv2.cvtColor(f, cv2.COLOR_BGR2GRAY)
    g[: int(H * 0.4)] = 0
    _, m = cv2.threshold(g, 200, 255, cv2.THRESH_BINARY)
    cs, _ = cv2.findContours(m, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cs = [c for c in cs if cv2.contourArea(c) > 300]
    if not cs:
        return prev
    c = max(cs, key=cv2.contourArea)
    box = cv2.boxPoints(cv2.minAreaRect(c)).astype(np.float32)
    ctr = box.mean(0)
    # long axis, pointing to the screen's top (the far end: smaller y)
    e1, e2 = box[1] - box[0], box[2] - box[1]
    ax = e1 if np.linalg.norm(e1) > np.linalg.norm(e2) else e2
    ax = ax / np.linalg.norm(ax)
    if ax[1] > 0:
        ax = -ax
    right = np.array([-ax[1], ax[0]])
    def pick(sa, sr):
        return max(box, key=lambda p: sa * np.dot(p - ctr, ax) + sr * np.dot(p - ctr, right))
    q = np.array([pick(1, -1), pick(1, 1), pick(-1, 1), pick(-1, -1)], np.float32)   # TL TR BR BL
    return q


def o04(n):
    base = blender("O04", n)
    scr = read_video(REM / "M5-O04-PhoneScreen.mp4", n, size=(540, 1170))
    qs, prev = [], None
    for f in base:
        prev = phone_quad(f, prev)
        qs.append(prev)
    qs = np.array(qs)
    # light temporal smoothing of the corners (3-frame mean)
    sm = qs.copy()
    for i in range(len(qs)):
        sm[i] = qs[max(0, i - 1): i + 2].mean(0)
    src = np.array([[0, 0], [539, 0], [539, 1169], [0, 1169]], np.float32)
    for i, f in enumerate(base):
        q = sm[i].copy()
        c = q.mean(0)
        q = c + (q - c) * 1.04                                    # cover the glowing rim
        M = cv2.getPerspectiveTransform(src, q.astype(np.float32))
        warped = cv2.warpPerspective(scr[i], M, (W, H), flags=cv2.INTER_AREA)
        mask = cv2.warpPerspective(np.full((1170, 540), 255, np.uint8), M, (W, H))
        a = (mask.astype(np.float32) / 255.0)[:, :, None]
        base[i] = (f * (1 - a) + warped * a).astype(np.uint8)
    return base, "blender motion + Remotion phone screen pinned to the phone"


def o06(n):
    """The picked clip, 24 -> 30 fps by time (no interpolation), cropped to fill 960x540, trimmed to the cue."""
    src = read_video(O06_CLIP, fill=True)
    m = len(src)
    spare = m / 24.0 - n / FPS
    g = [cv2.cvtColor(f, cv2.COLOR_BGR2GRAY).astype(np.float32) for f in src]
    motion = [0.0] + [float(np.abs(g[i] - g[i - 1]).mean()) for i in range(1, m)]
    k = int(np.argmax(np.convolve(motion, np.ones(5) / 5, "same")))
    want = mark("O06", 0) / FPS
    # The take's curl is continuous (production log 11) and its frame-difference peak is the push at the end, not a
    # page event, so there's nothing to align to 'fax': the clip plays from its first frame (the picked still).
    off = 0.0
    out = [src[min(m - 1, int(round((i / FPS + off) * 24)))].copy() for i in range(n)]
    return out, f"clip O06_s41 cropped to fill, from {off:.2f} s at native speed"


def o07_tower(n):
    """The fog-tower alternate: the plate, the server cut-out on the lawn, the tower's top half pixelated (a stalled
    low-res block), a slow push (1.0 -> 1.06)."""
    im = cv2.imread(O07_TOWER)                                   # 1920 x 1088
    x0, y0, x1, y1 = 872, 190, 1036, 540                         # the tower's top half
    blk = im[y0:y1, x0:x1]
    b = 22
    small = cv2.resize(blk, ((x1 - x0) // b, (y1 - y0) // b), interpolation=cv2.INTER_AREA)
    im[y0:y1, x0:x1] = cv2.resize(small, (x1 - x0, y1 - y0), interpolation=cv2.INTER_NEAREST)
    rack = cv2.imread("renders/m5/O07t.png", cv2.IMREAD_UNCHANGED)
    if rack is not None:
        h = 300
        r = cv2.resize(rack, (int(rack.shape[1] * h / rack.shape[0]), h), interpolation=cv2.INTER_AREA)
        cx, by = 700, 1010
        X0, Y0 = cx - r.shape[1] // 2, by - h
        # a soft contact shadow under it
        sh = np.zeros(im.shape[:2], np.float32)
        cv2.ellipse(sh, (cx, by - 6), (int(r.shape[1] * 0.48), 26), 0, 0, 360, 0.55, -1)
        sh = cv2.GaussianBlur(sh, (0, 0), 14)[:, :, None]
        im = (im * (1 - sh)).astype(np.uint8)
        a = r[:, :, 3:4].astype(np.float32) / 255
        roi = im[Y0:Y0 + h, X0:X0 + r.shape[1]].astype(np.float32)
        im[Y0:Y0 + h, X0:X0 + r.shape[1]] = (roi * (1 - a) + r[:, :, :3] * a).astype(np.uint8)
    out = []
    for i in range(n):
        z = 1 + 0.06 * i / max(n - 1, 1)
        cw, ch = 1920 / z, 1080 / z
        X, Y = (1920 - cw) / 2, (1088 - ch) / 2
        out.append(cv2.resize(im[int(Y):int(Y + ch), int(X):int(X + cw)], (W, H), interpolation=cv2.INTER_AREA))
    return out, "fog-tower still s44 + server cut-out, top half pixelated, slow push"


def home_movie(frames, start):
    """O22 from 'Remember Wednesday': soft film grain and a warm grade (brief, O22); grain seeded from seeds.json."""
    rng = np.random.default_rng(SEEDS["main"])
    for i in range(start, len(frames)):
        f = frames[i].astype(np.float32)
        f = f * np.array([0.86, 1.0, 1.08], np.float32) + np.array([6, 8, 12], np.float32)   # BGR: warmer, lifted
        f = 255 * (f / 255) ** 0.95
        f += rng.normal(0, 7, f.shape[:2])[:, :, None]
        frames[i] = np.clip(f, 0, 255).astype(np.uint8)
    return frames


# ---------------------------------------------------------------- segments

def segment(sid, o07="server"):
    """(frames, source description) for one shot (or end-sequence item)."""
    if sid in ("O01", "O02", "O05", "O23"):
        return read_video(REM / f"M5-{sid}.mp4", nfr(sid)), "remotion"
    n = nfr(sid) if sid in SHOTS and sid != "O24" else None
    if sid == "O03":
        return over(blender(sid, n), overlay("M5-O03-LT", n)), "blender motion + lower third"
    if sid == "O04":
        return o04(n)
    if sid == "O06":
        return o06(n)
    if sid == "O07":
        if o07 == "fogtower":
            fr, how = o07_tower(n)
        else:
            fr, how = blender(sid, n), "blender motion (server on chroma green)"
        return over(fr, overlay("M5-O07-Caption", n)), how + " + caption"
    if sid == "O08":
        fr = blender(sid, n)
        a, b = O08_PHONE
        fr[a:b] = read_video(REM / "M5-O08-Phone.mp4", b - a)
        a, b = O08_TREE
        tree = blender("O08c", b - a)
        fr[a:b] = over(tree, overlay("M5-Dramatization", b - a))
        return over(fr, overlay("M5-O08-LT", n)), "blender motion + echo lower thirds; inserts: Remotion phone (IT reply), blender treehouse cutaway"
    if sid == "O09":
        return over(blender(sid, n), overlay("M5-O09-LT", n)), "blender motion + uptime lower third"
    if sid == "O11":
        return over(blender(sid, n), overlay("M5-O11-Live", n)), "blender motion + live overlay (viewers, chat, Switch inset)"
    if sid == "O12":
        return over(blender(sid, n), overlay("M5-O12-Freeze", n)), "blender freeze (clapper, Switch, ON AIR) + buffering"
    if sid == "O13":
        k = mark("O13", 0)
        return read_video(REM / "M5-O13-Card.mp4", k) + read_video(REM / "M5-O13-Status.mp4", n - k), "remotion card, then status row red"
    if sid == "O17":
        return over(blender(sid, n), overlay("M5-O17-Disclosure", DISCLOSURE_FRAMES)), "blender motion + disclosure panel"
    if sid == "O18":
        return over(blender(sid, n), overlay("M5-Dramatization", n)), "blender motion, whiteboard movie texture + caption"
    if sid == "O19":
        a = blender("O19a", O19A)
        b = blender("O19b", n - O19A + XF)
        for i in range(XF):
            t = (i + 1) / (XF + 1)
            a[O19A - XF + i] = cv2.addWeighted(a[O19A - XF + i], 1 - t, b[i], t, 0)
        fr = a + b[XF:]
        return over(fr, overlay("M5-O19-LT", n)), "blender motion, two parts cross-faded + lower third"
    if sid == "O21":
        return over(blender(sid, n), overlay("M5-O21-Freeze", n)), "blender freeze (Switch drops) + buffering, caption"
    if sid == "O22":
        fr = home_movie(blender(sid, n), mark("O22", 0))
        return over(fr, overlay("M5-O22-LT", n)), "blender motion (walk-off), home-movie grade + lower third"
    if sid in SHOTS:
        return blender(sid, n), "blender motion"
    raise KeyError(sid)


def label(frames, text):
    for f in frames:
        (tw, th), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.42, 1)
        x = (W - tw) // 2
        cv2.rectangle(f, (x - 6, 4), (x + tw + 6, 10 + th + 4), (0, 0, 0), -1)
        cv2.putText(f, text, (x, 10 + th), cv2.FONT_HERSHEY_SIMPLEX, 0.42, (235, 235, 235), 1, cv2.LINE_AA)
    return frames


def write(frames, path):
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{W}x{H}", "-r", str(FPS),
                          "-i", "-", "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p",
                          "-video_track_timescale", "15360", str(path)], stdin=subprocess.PIPE)
    for f in frames:
        p.stdin.write(np.ascontiguousarray(f).tobytes())
    p.stdin.close()
    p.wait()


def order():
    return sorted([k for k in SHOTS if k != "O24"], key=lambda k: SHOTS[k]["start_frame"])


def build_segment(sid, o07):
    key = f"{sid}_{o07}" if sid == "O07" else sid
    fr, how = segment(sid, o07)
    n = nfr(sid)
    assert len(fr) == n, (sid, len(fr), n)
    write(label(fr, f"{sid}  {how}"), SEG / f"{key}.mp4")
    return key, how, n


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="review/m5_animatic.mp4")
    ap.add_argument("--o07", default="server", choices=["server", "fogtower"])
    ap.add_argument("--excerpt", default="", help="FIRST:LAST shot IDs, e.g. O05:O08")
    ap.add_argument("--only", default="", help="rebuild these segments only")
    ap.add_argument("--reuse", action="store_true", help="reuse existing segments")
    a = ap.parse_args()
    SEG.mkdir(parents=True, exist_ok=True)
    shots = order()
    if a.excerpt:
        f, l = a.excerpt.split(":")
        shots = shots[shots.index(f): shots.index(l) + 1]
    only = set(filter(None, a.only.split(",")))
    keys, sources = [], {}
    for sid in shots:
        key = f"{sid}_{a.o07}" if sid == "O07" else sid
        if (only and sid not in only) or (a.reuse and (SEG / f"{key}.mp4").exists() and sid not in only):
            keys.append(key)
            continue
        key, how, n = build_segment(sid, a.o07)
        keys.append(key)
        sources[sid] = how
        print(f"{sid:5s} {n:4d} f  {how}", flush=True)
    if only:
        return
    if not a.excerpt:
        for name, comp, n in END:
            fr = read_video(REM / f"{comp}.mp4", n)
            write(label(fr, f"{name}  remotion"), SEG / f"end_{comp}.mp4")
            keys.append(f"end_{comp}")
            sources[comp] = "remotion"
    lst = SEG / f"list_{Path(a.out).stem}.txt"
    lst.write_text("".join(f"file '{(SEG / f'{k}.mp4').resolve()}'\n" for k in keys))
    joined = SEG / f"joined_{Path(a.out).stem}.mp4"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", str(joined)], check=True)
    nframes = int(subprocess.run(["ffprobe", "-v", "error", "-count_frames", "-select_streams", "v:0", "-show_entries", "stream=nb_read_frames",
                                  "-of", "csv=p=0", str(joined)], capture_output=True, text=True).stdout.strip())
    t0 = SHOTS[shots[0]]["start_frame"] / FPS                  # video time of the first frame
    dur = nframes / FPS
    # audio: the master starts at the lead-in (video time 8.4 s); silence before and after
    lead = TS["lead_in_s"]
    af = f"adelay={int(round(lead * 1000))}:all=1,apad=whole_dur={t0 + dur:.3f},atrim=start={t0:.3f}:end={t0 + dur:.3f},asetpts=PTS-STARTPTS"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(joined), "-i", MASTER, "-filter_complex", f"[1:a]{af}[a]", "-map", "0:v",
                    "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", a.out], check=True)
    json.dump(sources, open(f"renders/m5/{Path(a.out).stem}_sources.json", "w"), indent=1)
    print(f"{a.out}: {nframes} frames, {dur:.3f} s (from video {t0:.3f} s)")


if __name__ == "__main__":
    main()
