"""M7c review sheets (production log 44+; human interventions 22).

  --grade    renders/m7c/raw/<id>.png and the M7b references renders/m7c/m7b_ref/raw/<id>.png (blender/coverage_m7.py
             --still, 1920x1080, 16-bit) -> renders/m7c/<id>.png and renders/m7c/m7b_ref/<id>.png (scripts/grade.py:
             grey, or home for O22 from "Remember Wednesday"); O22d's M7c frame is the generated clip's middle frame
             (scripts/m7_inserts.py, graded home)
  --board    review/m7c_park_board.jpg: every park hero, M7b left, M7c right, labelled
  --plates   review/m7c_plates.jpg: the plates used, each extension pass's takes (pick and rejects), the panorama with
             the passes marked, the O22d takes (first, middle and last frames) with the pick
  --fixes    review/m7c_fixes.jpg: the assistant screen (texture and in the treehouse), O04a's first frame (and its
             texture), a live-room crowd-phone frame with a 1:1 crop
  --motion   review/m7c_motion_test.mp4: O19a + O19b (the dissolve, the rise onto the crest), O20e (the truck past the
             plate) and O22d (the generated clip), each with the master's audio at its own song time; 960x540, h264 at
             650 kb/s, AAC 128k
Usage: .venv/bin/python -I scripts/m7c_board.py --grade | --board | --plates | --fixes | --motion
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

import cv2
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import grade as G  # noqa: E402
import m7_inserts as MI  # noqa: E402
import m7a_board as MA  # noqa: E402

FPS = 30
RAW, OUT = ROOT / "renders/m7c/raw", ROOT / "renders/m7c"
REF = ROOT / "renders/m7c/m7b_ref"
PL = json.loads((ROOT / "config/m7c_plate.json").read_text())
HEROES = [  # id, what it shows / what changed
    ("O19a", "the deck (treehouse): the door opens onto the deck, the volumetric firs through the drizzle"),
    ("O19b", "the rise: up the back slope out of the young firs, over the crest's back edge"),
    ("O19e", "close: the kick pedal; the new crest's lawn and firs soft beyond"),
    ("O20a", "the wide (camera 1.8 m, aimed a little down): the lawn to the brow, the drop, the city 2-4 km off"),
    ("O20c", "the one umbrella"),
    ("O20e", "the high wide (camera 5.4 m, behind the crowd): the crest, the brow, the valley, the plate"),
    ("O20g", "backs: a head against the fog and the city"),
    ("O20i", "Switch on the new lamp post's outlet box (box and Switch where M7b had them)"),
    ("O21a", "the freeze's frame (the buffering overlay is added at assembly)"),
    ("O22a", "the emptied park (camera 1.85 m, aimed a little down)"),
    ("O22b", "Switch, off: home-movie grade from here"),
    ("O22c", "the walker's feet on the gravel path, kerbs and blades"),
    ("O22d", "fog over the skyline: the generated plate animated (LTX-2.3), not rendered"),
    ("O22f", "the hill, the walker near the brow at the viewpoint"),
    ("O22g", "drizzle past the new lantern"),
]


def look(sid):
    return MA.look_of(sid, "hilltop park") if sid != "O19a" else "grey"


def vframe(sid):
    return MA.frames_of(sid)[1]


def do_grade():
    for sid, _ in HEROES:
        for src_dir, dst_dir in ((RAW, OUT), (REF / "raw", REF)):
            src = src_dir / f"{sid}.png"
            if sid == "O22d" and dst_dir == OUT:
                fr, _ = MI.o22d((1920, 1080))
                cv2.imwrite(str(OUT / "O22d.png"), fr[len(fr) // 2])
                continue
            if not src.exists():
                print(f"{sid}: no {src}")
                continue
            im = cv2.imread(str(src), cv2.IMREAD_UNCHANGED)
            cv2.imwrite(str(dst_dir / f"{sid}.png"), G.grade(im[:, :, :3], look(sid), vframe(sid)))
        print(f"{sid}: {look(sid)}")


def label(w, text, h=30, scale=0.55, color=(235, 235, 235)):
    return MA.bar(w, text, h, scale, color)


def board(out="review/m7c_park_board.jpg", tw=960):
    th = tw * 9 // 16
    W2 = 2 * tw + 10
    rows = [label(W2, "M7c park board: every park hero at the final look. Left: M7b (the park as approved for the M7 base). "
                      "Right: M7c (the park rebuilt from the hill up).", 40, 0.62),
            label(W2, "Each pair is the same sub-shot, frame and performance; cameras changed for the new hill are noted "
                      "(decisions 36). Eevee 1920x1080, graded; O22 from Remember Wednesday in the home-movie grade.", 30, 0.5,
                  (170, 170, 170))]
    for sid, what in HEROES:
        mid, vf = MA.frames_of(sid)
        a = cv2.imread(str(REF / f"{sid}.png"))
        b = cv2.imread(str(OUT / f"{sid}.png"))
        a = cv2.resize(a, (tw, th), interpolation=cv2.INTER_AREA)
        b = cv2.resize(b, (tw, th), interpolation=cv2.INTER_AREA)
        cam = MA.SUBS[sid]["camera"]
        rows.append(label(W2, f"{sid}  |  frame {mid} of the build (video frame {vf}, {vf / FPS:.2f} s)  |  camera {cam}  |  {what}", 34, 0.55))
        left = "M7b (renders/m7c/m7b_ref)" if sid != "O22d" else "M7b: the Blender O22d (renders/m7c/m7b_ref)"
        right = "M7c" if sid != "O22d" else f"M7c: the generated clip {PL['o22d'].get('pick', '?')}, middle frame (scripts/m7_inserts.py)"
        rows.append(np.hstack([label(tw, left, 24, 0.45, (170, 170, 170)), np.full((24, 10, 3), 24, np.uint8),
                               label(tw, right, 24, 0.45, (170, 220, 170))]))
        rows.append(np.hstack([a, np.full((th, 10, 3), 24, np.uint8), b]))
        rows.append(np.full((10, W2, 3), 24, np.uint8))
    im = np.vstack(rows)
    cv2.imwrite(str(ROOT / out), im, [cv2.IMWRITE_JPEG_QUALITY, 88])
    print(f"{out}: {im.shape[1]}x{im.shape[0]}, {(ROOT / out).stat().st_size / 1e6:.2f} MB")


def _fit(im, w):
    return cv2.resize(im, (w, int(im.shape[0] * w / im.shape[1])), interpolation=cv2.INTER_AREA)


def plates(out="review/m7c_plates.jpg", W=1930):
    rv = PL.get("review", {})
    rows = [label(W, "M7c far plate: the plates used, the extension (FLUX.2 [dev] outpainting), the panorama, and O22d "
                     "(LTX-2.3 image-to-video). Reference: config/m7c_plate.json, log/prompts/m7c_park.md.", 40, 0.6)]
    src = [cv2.imread(str(ROOT / PL["source"])), cv2.imread(str(ROOT / PL["ridges"]["left"])), cv2.imread(str(ROOT / PL["ridges"]["right"]))]
    tw = (W - 20) // 3
    rows.append(np.hstack([label(tw, "far plate 1: plate_city_s42 (M7b, approved)", 26, 0.48), np.full((26, 10, 3), 24, np.uint8),
                           label(tw, "plate 2: plate_ridges_s41 (left tree lines)", 26, 0.48), np.full((26, 10, 3), 24, np.uint8),
                           label(tw, "plate 3: plate_ridges_s42 (right tree lines)", 26, 0.48)]))
    ims = [_fit(s, tw) for s in src]
    rows.append(np.hstack([ims[0], np.full((ims[0].shape[0], 10, 3), 24, np.uint8), ims[1], np.full((ims[0].shape[0], 10, 3), 24, np.uint8), ims[2]]))
    pano = cv2.imread(str(ROOT / "assets/gen/stills/m7c_park/pano/pano.png"))
    if pano is not None:
        p = _fit(pano, W)
        sc = W / pano.shape[1]
        for x, t in ((1280, "L2 | L1"), (2560, "L1 | plate"), (5120, "plate | R1"), (6400, "R1 | R2")):
            cv2.line(p, (int(x * sc), 0), (int(x * sc), 14), (60, 200, 255), 2)
            cv2.putText(p, t, (int(x * sc) + 4, 12), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (60, 200, 255), 1, cv2.LINE_AA)
        rows.append(label(W, "The panorama (7680x1440: L2, L1, the original plate, R1, R2; about 128 degrees at 60 px per degree); "
                             "marks at the pass seams (blended over 160 px inside each pass's mask ramp).", 30, 0.5))
        rows.append(p)
    for pss in ("L1", "R1", "L2", "R2"):
        d = ROOT / "assets/gen/stills/m7c_park/extend" / pss
        takes = sorted(d.glob(f"{pss}_s*.png"))
        if not takes:
            continue
        tw2 = (W - 10) // 2
        heads, ims2 = [], []
        for t in takes[:2]:
            pick = PL.get("picks", {}).get(pss) == t.stem
            note = rv.get(t.stem, "")
            heads.append(label(tw2, f"{t.stem}: {note or ('picked' if pick else 'not picked')}"[:140], 26, 0.42,
                               (170, 230, 170) if pick else (200, 170, 170)))
            ims2.append(_fit(cv2.imread(str(t)), tw2))
        while len(ims2) < 2:
            heads.append(label(tw2, "", 26)); ims2.append(np.full_like(ims2[0], 24))
        rows.append(label(W, f"Pass {pss}: {PL['passes'][pss]['side']} side" + (" (started from the ridges plate)" if PL['passes'][pss].get('init') else "")
                          + "; the known half is the panorama so far, the other half generated", 28, 0.5))
        rows.append(np.hstack([heads[0], np.full((26, 10, 3), 24, np.uint8), heads[1]]))
        rows.append(np.hstack([ims2[0], np.full((ims2[0].shape[0], 10, 3), 24, np.uint8), ims2[1]]))
    for v, why in (("extend_v1", "run 1 (L1, R1): a blurred stripe at each seam (the mask was under 1 there); fixed and re-run"),
                   ("extend_v2", "run 3 (L2, R2): the ridges plates' far slab blocks kept (tree lines only); R2_s41 also a hard edge; re-run")):
        rej = sorted((ROOT / "archive/assets/gen/stills/m7c_park" / v).glob("*/*_s*.png"))
        if rej:
            tw3 = (W - 30) // 4
            rows.append(label(W, f"Rejected, archived, {why}: " + ", ".join(t.stem for t in rej[:4]), 28, 0.48, (200, 170, 170)))
            ims3 = [_fit(cv2.imread(str(t)), tw3) for t in rej[:4]]
            rows.append(np.hstack(sum([[im, np.full((im.shape[0], 10, 3), 24, np.uint8)] for im in ims3], [])[:-1]))
    clips = sorted((ROOT / "assets/gen/clips/O22d").glob("O22d_s*.mp4"))
    if clips:
        rows.append(label(W, "O22d: LTX-2.3 image-to-video of the plate's centre (1280x704, 24 fps, 5 s); frames 1, 61, 121 of each take; "
                             "pick in green (config/m7c_plate.json o22d).", 30, 0.5))
        tw4 = (W - 20) // 3
        for c in clips:
            fr = MI.read_clip(c, (tw4, tw4 * 704 // 1280))
            pick = PL["o22d"].get("pick") == c.stem
            note = PL["o22d"].get("review", {}).get(c.stem, "")
            rows.append(label(W, f"{c.stem}: {note}"[:210], 26, 0.45,
                              (170, 230, 170) if pick else (200, 170, 170)))
            sel = [fr[0], fr[len(fr) // 2], fr[-1]]
            rows.append(np.hstack([sel[0], np.full((sel[0].shape[0], 10, 3), 24, np.uint8), sel[1], np.full((sel[0].shape[0], 10, 3), 24, np.uint8), sel[2]]))
    rows = [r if r.shape[1] == W else np.hstack([r, np.full((r.shape[0], W - r.shape[1], 3), 24, np.uint8)]) for r in rows]
    im = np.vstack(rows)
    cv2.imwrite(str(ROOT / out), im, [cv2.IMWRITE_JPEG_QUALITY, 88])
    print(f"{out}: {im.shape[1]}x{im.shape[0]}, {(ROOT / out).stat().st_size / 1e6:.2f} MB")


def fixes(out="review/m7c_fixes.jpg", W=1930):
    rows = [label(W, "M7c small fixes (human interventions 22): the assistant screen unnamed, O04a's question from the first frame, "
                     "the live room's crowd phones.", 40, 0.6)]
    tex = ROOT / "assets/gen/tex/m7b"
    ag_d = cv2.imread(str(sorted((tex / "M7-Tree-Agent-day/frames").glob("*"))[300]))
    ag_n = cv2.imread(str(sorted((tex / "M7-Tree-Agent-night/frames").glob("*"))[60]))
    tw = (W - 10) // 2
    rows.append(np.hstack([label(tw, "1. the assistant screen, day (O18), frame 300: the header reads 'assistant - read-only' (a middle dot on screen), no name or initial", 26, 0.45),
                           np.full((26, 10, 3), 24, np.uint8), label(tw, "the same, night (O08c), frame 60", 26, 0.45)]))
    a, b = _fit(ag_d, tw), _fit(ag_n, tw)
    rows.append(np.hstack([a, np.full((a.shape[0], 10, 3), 24, np.uint8), b]))
    for sid, crop, what in (("O08c", None, "the assistant on seat 0's laptop in O08c, the night cutaway (1080p, graded): its header and headline at the laptop's size"),):
        p = OUT / "fixes" / f"{sid}.png"
        if p.exists():
            im = cv2.imread(str(p))
            rows.append(label(W, what, 26, 0.45))
            rows.append(_fit(im, W))
            c = im[490:700, 330:640]
            rows.append(label(W, "the assistant's laptop in O08c, 1:1 enlarged 3x: the header and the headline 'I can't reach the mail connector.'", 24, 0.42, (170, 170, 170)))
            rows.append(cv2.resize(c, (c.shape[1] * 3, c.shape[0] * 3), interpolation=cv2.INTER_NEAREST))
    ph = sorted((tex / "M7-O04-PhoneScreen/frames").glob("*"))
    p0 = OUT / "fixes" / "O04a.png"            # rendered --at first
    if p0.exists():
        im = cv2.imread(str(p0))
        t0 = cv2.imread(str(ph[0]))
        t0 = cv2.resize(t0, (int(t0.shape[1] * 540 / t0.shape[0]), 540), interpolation=cv2.INTER_AREA)
        fr = cv2.resize(im, (960, 540), interpolation=cv2.INTER_AREA)
        crop = im[300:840, 200:200 + (W - 960 - t0.shape[1] - 20)]
        rows.append(label(W, "2. O04a's first frame: the question is on the phone from the start (M7b: it arrived halfway); "
                             "left, the frame at 960 wide; middle, its texture frame 1; right, the frame 1:1", 26, 0.45))
        rows.append(np.hstack([fr, np.full((540, 10, 3), 24, np.uint8), t0, np.full((540, 10, 3), 24, np.uint8), crop]))
    pl = OUT / "fixes" / "O03f.png"
    if pl.exists():
        im = cv2.imread(str(pl))
        info = json.loads((OUT / "fixes" / "crowd_phone.json").read_text()) if (OUT / "fixes" / "crowd_phone.json").exists() else {}
        rows.append(label(W, f"3. the live room's crowd phones: {info.get('what', '')}", 26, 0.45))
        rows.append(_fit(im, W))
        for (x, y, w, h, t) in info.get("crops", []):
            c = im[y:y + h, x:x + w]
            c = cv2.resize(c, (w * 3, h * 3), interpolation=cv2.INTER_NEAREST)
            rows.append(label(W, t, 24, 0.42, (170, 170, 170)))
            rows.append(c)
        tx = [cv2.imread(str(ROOT / f"assets/gen/tex/m7c/crowd_{k}.jpg")) for k in ("camera", "lock", "chat")]
        tx = [cv2.resize(t, (200, 433), interpolation=cv2.INTER_AREA) for t in tx]
        rows.append(label(W, "their textures: a camera recording the band, a lock screen, the #it-help chat (unreadable at the wides' size)", 24, 0.42))
        rows.append(np.hstack(sum([[t, np.full((433, 10, 3), 24, np.uint8)] for t in tx], [])[:-1]))
    rows = [r if r.shape[1] == W else np.hstack([r, np.full((r.shape[0], W - r.shape[1], 3), 24, np.uint8)]) for r in rows]
    im = np.vstack(rows)
    cv2.imwrite(str(ROOT / out), im, [cv2.IMWRITE_JPEG_QUALITY, 90])
    print(f"{out}: {im.shape[1]}x{im.shape[0]}, {(ROOT / out).stat().st_size / 1e6:.2f} MB")


def motion(out="review/m7c_motion_test.mp4"):
    """O19a + O19b with M5's 10-frame dissolve, O20e, then O22d's clip; graded per frame; each segment carries the
    master's audio from its own song time."""
    fm = OUT / "frames_motion"
    tmp = fm / "graded"
    tmp.mkdir(parents=True, exist_ok=True)
    segs, k = [], 0

    def load(sid, extra=0):
        s = MA.SUBS[sid]
        files = sorted((fm / sid).glob("*.jpg"))
        v0 = MA.vstart(s["build"])
        return [(cv2.imread(str(f)), v0 + int(f.stem) - 1) for f in files]
    a = load("O19a")
    b = load("O19b")
    xf = MA.SUBS["O19b"].get("xfade_in", 0)
    seq = a[:-xf] if xf else a
    for i in range(xf):
        t = (i + 1) / (xf + 1)
        seq.append((cv2.addWeighted(a[len(a) - xf + i][0], 1 - t, b[i][0], t, 0), a[len(a) - xf + i][1]))
    seq += b[xf:]
    o19 = [(G.grade(f, "grey", vf), vf) for f, vf in seq]
    o20e = [(G.grade(f, "grey", vf), vf) for f, vf in load("O20e")]
    d, _ = MI.o22d((960, 540))
    v0d = MA.SUBS["O22d"]["start_frame"]
    o22d = [(f, v0d + i) for i, f in enumerate(d)]
    for part in (o19, o20e, o22d):
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
    for k in ("grade", "board", "plates", "fixes", "motion"):
        ap.add_argument(f"--{k}", action="store_true")
    a = ap.parse_args()
    if a.grade:
        do_grade()
    if a.board:
        board()
    if a.plates:
        plates()
    if a.fixes:
        fixes()
    if a.motion:
        motion()


if __name__ == "__main__":
    main()
