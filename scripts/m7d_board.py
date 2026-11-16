"""M7d review sheets (human interventions 23; production log 50+; decisions 42).

  --grade    the M7d heroes renders/m7d/raw/<id>.png (blender/coverage_m7.py --still, 1920x1080, 16-bit) and O19b's start
             renders/m7d/raw_first/O19b.png -> renders/m7d/<id>.png, O19b_first.png; the M7c references of production
             log 50 (renders/m7d/m7c_ref/raw, raw_first) -> renders/m7d/m7c_ref/<id>.png; the wides options
             (renders/m7d/options/<option>/raw) -> renders/m7d/options/<option>/<id>.png. Looks as M7c (scripts/grade.py
             grey, cafe, home from "Remember Wednesday").
  --board    review/m7d_board.jpg: per weak point, the approved version (M7c; the closes' M7c references; O08c's M7c
             fixes still) left and M7d right at 1080p scaled to 960, captioned, with 1:1 crops where the change is fine
             detail (fir shading, the plate's seam, the window panes)
  --wides    review/m7d_wides_options.jpg: the eye-level wides (O20a, O21a, O22a, O22f): approved; the cues at 1.8 m;
             2.4 m without the cues; the cues at 2.4 m
  --motion   review/m7d_motion_test.mp4: O19a + O19b (M5's dissolve: the deck, the rise onto the crest), O20e (the truck
             past the plate and the brow), O09j (the guitar close) and O09f (the banjo close), each with the master's audio
             at its own song time (review/m5c3_animatic.mp4); 960x540, h264 at 650 kb/s, AAC 128k
Usage: .venv/bin/python -I scripts/m7d_board.py --grade | --board | --wides | --motion
"""
import argparse
import subprocess
import sys
from pathlib import Path

import cv2
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import grade as G  # noqa: E402
import m7a_board as MA  # noqa: E402

FPS = 30
D = ROOT / "renders/m7d"
REF = D / "m7c_ref"
M7C = ROOT / "renders/m7c"
OPT = D / "options"
OPTIONS = [("approved", "approved (M7c): cameras at 1.8 m, no cues"), ("cues18", "M7d: the drop cues, cameras at 1.8 m (as approved)"),
           ("z24", "M7d without the drop cues, cameras at 2.4 m (tilt kept)"), ("cues24", "M7d: the drop cues and cameras at 2.4 m")]
WIDES = ["O20a", "O21a", "O22a", "O22f"]
ROOMS = {"O08": "treehouse", "O09": "live room", "O11": "live room", "O17": "coffee shop", "O18": "treehouse",
         "O19a": "treehouse", "O19": "hilltop park", "O20": "hilltop park", "O21": "hilltop park", "O22": "hilltop park"}


def look(sid):
    room = next(v for k, v in ROOMS.items() if sid.startswith(k))
    return MA.look_of(sid, room)


def vframe(sid):
    return MA.frames_of(sid)[1]


def _grade_file(src, dst, sid):
    im = cv2.imread(str(src), cv2.IMREAD_UNCHANGED)
    if im is None:
        print(f"{sid}: no {src}")
        return
    dst.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(dst), G.grade(im[:, :, :3], look(sid), vframe(sid)))


def do_grade():
    for src in sorted((D / "raw").glob("*.png")):
        _grade_file(src, D / src.name, src.stem)
    for src in sorted((REF / "raw").glob("*.png")):
        _grade_file(src, REF / src.name, src.stem)
    for d, dst in ((D / "raw_first", D), (REF / "raw_first", REF)):
        p = d / "O19b.png"
        if p.exists():
            _grade_file(p, dst / "O19b_first.png", "O19b")
    for o in OPT.glob("*/raw"):
        for src in sorted(o.glob("*.png")):
            _grade_file(src, o.parent / src.name, src.stem)
    print("graded")


def label(w, text, h=30, scale=0.55, color=(235, 235, 235)):
    return MA.bar(w, text, h, scale, color)


def gap(h, w=10):
    return np.full((h, w, 3), 24, np.uint8)


def approved(sid):
    """The approved frame: M7c's park heroes; the closes' and O19b-start M7c references (production log 50);
    O08c's M7c fixes still."""
    for p in (REF / f"{sid}.png", M7C / f"{sid}.png", M7C / "fixes" / f"{sid}.png"):
        if p.exists():
            return cv2.imread(str(p)), str(p.relative_to(ROOT))
    return None, ""


def pair(sid, what, tw=960, right=None, left=None, lt="", rt=""):
    th = tw * 9 // 16
    a, src = left if left is not None else approved(sid)
    b = right if right is not None else cv2.imread(str(D / f"{sid}.png"))
    W2 = 2 * tw + 10
    rows = [label(W2, f"{sid}  |  {what}", 32, 0.52)]
    rows.append(np.hstack([label(tw, lt or f"approved: {src}", 24, 0.42, (170, 170, 170)), gap(24),
                           label(tw, rt or "M7d", 24, 0.42, (170, 220, 170))]))
    rows.append(np.hstack([cv2.resize(a, (tw, th), interpolation=cv2.INTER_AREA), gap(th),
                           cv2.resize(b, (tw, th), interpolation=cv2.INTER_AREA)]))
    return rows


def crops(sid, boxes, scale, note, left=None, right=None, W2=1930):
    """1:1 (or scale x) crops of the approved frame and M7d side by side, per box (x, y, w, h) in the 1080p frame."""
    a = left if left is not None else approved(sid)[0]
    b = right if right is not None else cv2.imread(str(D / f"{sid}.png"))
    rows = [label(W2, note, 24, 0.42, (170, 170, 170))]
    for (x, y, w, h) in boxes:
        ca = cv2.resize(a[y:y + h, x:x + w], (int(w * scale), int(h * scale)), interpolation=cv2.INTER_NEAREST)
        cb = cv2.resize(b[y:y + h, x:x + w], (int(w * scale), int(h * scale)), interpolation=cv2.INTER_NEAREST)
        r = np.hstack([ca, gap(ca.shape[0]), cb])
        if r.shape[1] < W2:
            r = np.hstack([r, np.full((r.shape[0], W2 - r.shape[1], 3), 24, np.uint8)])
        rows.append(r[:, :W2])
    return rows


SECTIONS = [
    ("1. Firs shade as volumes", "The fir prototypes (park and treehouse forest) keep their M7c crowns and silhouettes; M7d adds per-vertex normals "
     "from a crown proxy and the branch tier, occlusion deep inside and under the tiers, a value per branch, a needle fringe at each spray's "
     "edge, the branches as thin tubes, and the overcast's light from above and the far side on the crown proxy (blender/park_m7c.py).",
     [("O19a", "the deck: the treehouse forest's firs up close", [(600, 60, 940, 500)]),
      ("O19b", "the rise: young firs on the back slope (middle frame)", [(0, 0, 940, 520), (1100, 0, 820, 520)]),
      ("O20c", "the umbrella: firs soft beyond", []),
      ("O20a", "the wide: framing firs at the frame edges", [(1400, 0, 520, 500)])]),
    ("2. The far plate's seam", "The L1 seam (about 22 degrees left of centre) inpainted with FLUX.2 [dev] across a soft band; the approved "
     "panorama unchanged elsewhere (review/m7d_plates.jpg). In the wides the seam sits behind the left firs: 1:1 crops at its place.",
     [("O20e", "the high wide: the plate across the frame", []),
      ("O22a", "the emptied wide: the seam's place left of the city", [(180, 380, 700, 300)])]),
    ("3. The bare trees at the brow", "Thinner (fewer of the finest branches and twigs, slimmer from the second level), paler bark with less "
     "sheen, and more aerial perspective (fog distance 100 m, was 130), so the fog reads through them.",
     [("O20e", "the high wide: the bare trees below the brow", [(560, 380, 900, 360)])]),
    ("4. O08c's night panes", "The pale flat shapes were the forest floor 9 m down in the day's pale fog (its fog material kept the "
     "default emit at night); at night it takes the night fog, a night sky a little lighter than the forest stands behind the trees, "
     "and the rain on the panes glows less.",
     [("O08c", "the night cutaway: the back windows", [(180, 0, 380, 170), (1420, 0, 380, 170)])]),
    ("5. The drop in the eye-level wides (cameras unchanged at 1.8 m)", "Set dressing only: a railing on the viewpoint terrace's retaining "
     "wall, fir crowns rising from below the brow on either side of the view, a path leaving the terrace over the brow down the front "
     "slope. The camera-height options are on review/m7d_wides_options.jpg.",
     [("O20a", "the wide", []), ("O22a", "the emptied wide", []), ("O22f", "the walker at the brow", [(1100, 380, 820, 300)])]),
    ("6. The instrument closes", "Guitar: a small warm spot (2 W live, 1.2 W cafe) grazing the top from the side away from the camera, keyed "
     "on for the close's frames only; exposure unchanged (+1/3 stop). Banjo: every close_banjo re-aimed to about 39 degrees off the head's "
     "normal (was 85-89, edge-on), same distance, lens, cut, move and drift; a 1 W spot on the live room's.",
     [("O09j", "close_guitar, live room", []), ("O17a", "close_strum, coffee shop", []),
      ("O09f", "close_banjo, live room", []), ("O11e", "close_banjo, live room (one beat)", []),
      ("O17f", "close_banjo, coffee shop", []), ("O20f", "close_banjo, park", [])]),
    ("7. O19b's start: the crest seen from below", "The path's level bed stood proud on the back slope where the lawn rolls over the "
     "crest's back edge (a flat-topped block with sloped sides); on the back slope it now follows the roll. Frame 13 of 123.",
     [("O19b_first", "O19b at 10%: the top of the path at the crest", [])]),
]


def board(out="review/m7d_board.jpg", tw=960):
    W2 = 2 * tw + 10
    rows = [label(W2, "M7d board: the weak points flagged at M7c (human interventions 23). Left: approved (M7c, or the M7c reference "
                      "of a shot M7c didn't change). Right: M7d.", 40, 0.62),
            label(W2, "Every pair is the same sub-shot, frame and performance at 1920x1080 (shown at 960), Eevee, graded; crops are "
                      "1:1 or enlarged where noted. Calls for the human: decisions 43.", 30, 0.5, (170, 170, 170))]
    for title, what, items in SECTIONS:
        rows.append(np.full((14, W2, 3), 24, np.uint8))
        rows.append(label(W2, title, 40, 0.7, (120, 210, 255)))
        for k in range(0, len(what), 190):
            rows.append(label(W2, what[k:k + 190], 24, 0.45, (200, 200, 200)))
        for sid, cap, boxes in items:
            if sid == "O19b_first":
                a = cv2.imread(str(REF / "O19b_first.png"))
                b = cv2.imread(str(D / "O19b_first.png"))
                rows += pair("O19b", cap, tw, right=b, left=(a, "renders/m7d/m7c_ref/O19b_first.png"))
                rows += crops("O19b", [(560, 300, 900, 300)], 1.0, "1:1, the crest at the top of the path: approved left, M7d right",
                              left=a, right=b)
                continue
            rows += pair(sid, cap, tw)
            if boxes:
                sc = 1.0 if sum(b[2] for b in boxes) * 2 + 10 <= W2 + 10 else 0.0
                for bx in boxes:
                    s = 1.0
                    if sid == "O08c":
                        s = 2.5
                    if bx[2] * 2 * s + 10 > W2:
                        s = (W2 - 10) / (2 * bx[2])
                    rows += crops(sid, [bx], s, f"{'1:1' if s == 1.0 else f'{s:.2g}x'} crop at ({bx[0]}, {bx[1]}): approved left, M7d right")
                _ = sc
        rows.append(np.full((10, W2, 3), 24, np.uint8))
    rows = [r if r.shape[1] == W2 else np.hstack([r, np.full((r.shape[0], W2 - r.shape[1], 3), 24, np.uint8)])[:, :W2] for r in rows]
    im = np.vstack(rows)
    cv2.imwrite(str(ROOT / out), im, [cv2.IMWRITE_JPEG_QUALITY, 86])
    print(f"{out}: {im.shape[1]}x{im.shape[0]}, {(ROOT / out).stat().st_size / 1e6:.2f} MB")


def option_frame(opt, sid):
    if opt == "approved":
        return cv2.imread(str(M7C / f"{sid}.png"))
    if opt == "cues18":
        return cv2.imread(str(D / f"{sid}.png"))
    return cv2.imread(str(OPT / opt / f"{sid}.png"))


def wides(out="review/m7d_wides_options.jpg", tw=960):
    th = tw * 9 // 16
    W2 = 2 * tw + 10
    rows = [label(W2, "M7d: the drop in the eye-level wides, options (human interventions 23, weak point 5; decisions 39.2, 42, 43).", 40, 0.62),
            label(W2, "Per shot, 2x2: approved | the cues at 1.8 m (as approved; in M7d by default)  /  2.4 m without the cues | the cues at "
                      "2.4 m. 2.4 m keeps each camera's tilt (its target rises by the same amount).", 30, 0.48, (170, 170, 170))]
    for sid in WIDES:
        rows.append(np.full((12, W2, 3), 24, np.uint8))
        rows.append(label(W2, f"{sid}  |  camera {MA.SUBS[sid]['camera']}", 34, 0.6, (120, 210, 255)))
        for pr in ((0, 1), (2, 3)):
            ims, heads = [], []
            for i in pr:
                o, t = OPTIONS[i]
                f = option_frame(o, sid)
                ims.append(cv2.resize(f, (tw, th), interpolation=cv2.INTER_AREA) if f is not None else np.full((th, tw, 3), 24, np.uint8))
                heads.append(label(tw, t, 24, 0.45, (170, 220, 170) if o != "approved" else (170, 170, 170)))
            rows.append(np.hstack([heads[0], gap(24), heads[1]]))
            rows.append(np.hstack([ims[0], gap(th), ims[1]]))
    im = np.vstack(rows)
    cv2.imwrite(str(ROOT / out), im, [cv2.IMWRITE_JPEG_QUALITY, 86])
    print(f"{out}: {im.shape[1]}x{im.shape[0]}, {(ROOT / out).stat().st_size / 1e6:.2f} MB")


def motion(out="review/m7d_motion_test.mp4"):
    fm = D / "frames_motion"
    tmp = fm / "graded"
    tmp.mkdir(parents=True, exist_ok=True)

    def load(sid):
        s = MA.SUBS[sid]
        files = sorted((fm / sid).glob("*.jpg"))
        v0 = MA.vstart(s["build"])
        return [(cv2.imread(str(f)), v0 + int(f.stem) - 1) for f in files]
    a, b = load("O19a"), load("O19b")
    xf = MA.SUBS["O19b"].get("xfade_in", 0)
    seq = a[:-xf] if xf else a
    for i in range(xf):
        t = (i + 1) / (xf + 1)
        seq.append((cv2.addWeighted(a[len(a) - xf + i][0], 1 - t, b[i][0], t, 0), a[len(a) - xf + i][1]))
    seq += b[xf:]
    parts = [[(G.grade(f, "grey", vf), vf) for f, vf in seq]]
    for sid in ("O20e", "O09j", "O09f"):
        parts.append([(G.grade(f, look(sid), vf), vf) for f, vf in load(sid)])
    segs, k = [], 0
    for part in parts:
        for f, vf in part:
            cv2.imwrite(str(tmp / f"{k:05d}.png"), f)
            k += 1
        segs.append((part[0][1] / FPS, len(part) / FPS))
    filt = "".join(f"[1:a]atrim=start={t0:.4f}:duration={dd:.4f},asetpts=PTS-STARTPTS[a{i}];" for i, (t0, dd) in enumerate(segs))
    filt += "".join(f"[a{i}]" for i in range(len(segs))) + f"concat=n={len(segs)}:v=0:a=1[aout]"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-framerate", str(FPS), "-i", str(tmp / "%05d.png"),
                    "-i", str(ROOT / "review/m5c3_animatic.mp4"), "-filter_complex", filt, "-map", "0:v", "-map", "[aout]",
                    "-c:v", "libx264", "-b:v", "650k", "-maxrate", "900k", "-bufsize", "1300k", "-pix_fmt", "yuv420p",
                    "-c:a", "aac", "-b:a", "128k", "-shortest", "-movflags", "+faststart", str(ROOT / out)], check=True)
    print(f"{out}: {k} frames, {k / FPS:.2f} s, segments {[(round(t, 2), round(dd, 2)) for t, dd in segs]}, "
          f"{(ROOT / out).stat().st_size / 1e6:.2f} MB")


def main():
    ap = argparse.ArgumentParser()
    for k in ("grade", "board", "wides", "motion"):
        ap.add_argument(f"--{k}", action="store_true")
    a = ap.parse_args()
    if a.grade:
        do_grade()
    if a.board:
        board()
    if a.wides:
        wides()
    if a.motion:
        motion()


if __name__ == "__main__":
    main()
