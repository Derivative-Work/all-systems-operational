"""Pieces of the 1080p master for review before the whole is built (human interventions 38: "send me the opening
bookend and credits for me to review"), from scripts/m7_master.py's own segments and audio rules:
  bookend   O01 (the spike, the status page, the chat post), O02 and the first --tail-s of O03, with the song from its
            first downbeat on the cut to O02 -> review/m7_bookend.mp4
  credits   O23 (the song's last shot) with its audio, then the end sequence with the credits music
            -> review/m7_credits.mp4
Both 1920x1080; the credits at a bitrate that keeps the file under 30 MB (review files). (ffmpeg 8's adelay shifts the
timestamps rather than writing silence; aresample=async fills the gap, as the master's concat does.)
Usage: .venv/bin/python -I scripts/m7_pieces.py [--tail-s 3]
"""
import argparse
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, "scripts")
import m7_master as MM  # noqa: E402

R, A, M = MM.R, MM.A, MM.M
SEG = Path("renders/m7/pieces")


def run(cmd):
    subprocess.run(cmd, check=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tail-s", type=float, default=3.0)
    a = ap.parse_args()
    MM.setup()
    A.SEG = SEG
    SEG.mkdir(parents=True, exist_ok=True)
    for sid in ("O01", "O02", "O03", "O23"):
        how, n = M.build(sid)
        print(f"{sid}: {n} frames, {how}", flush=True)
    lead, head = A.TS["lead_in_s"], A.TS["song_audio_from_s"]
    # the bookend: O01 + O02 + the start of O03
    lst = SEG / "bookend.txt"
    lst.write_text("".join(f"file '{(SEG / f'{k}.mp4').resolve()}'\n" for k in ("O01", "O02", "O03")))
    end = A.SHOTS["O03"]["start_frame"] / A.FPS + a.tail_s
    run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(lst), "-i", R.SONG, "-filter_complex",
         f"[1:a]atrim=start={head:.4f},asetpts=PTS-STARTPTS,afade=t=in:d=0.01,adelay={int(round((lead + head) * 1000))}:all=1,"
         f"aresample=async=1:first_pts=0,apad,atrim=end={end:.4f},afade=t=out:st={end - 0.5:.4f}:d=0.5[a]", "-map", "0:v", "-map", "[a]", "-t", f"{end:.4f}",
         "-c:v", "libx264", "-preset", "slow", "-crf", "17", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "256k",
         "-movflags", "+faststart", "review/m7_bookend.mp4"])
    # the credits: O23 with the song's end, then the end sequence with the credits music
    o23 = A.SHOTS["O23"]
    s0, s1 = o23["song_start"], o23["song_end"]
    run(["ffmpeg", "-v", "error", "-y", "-i", str(SEG / "O23.mp4"), "-i", str(R.END_MP4), "-i", R.SONG, "-i", R.CREDITS,
         "-filter_complex",
         f"[0:v]fps=30,setsar=1[v0];[1:v]fps=30,setsar=1[v1];"
         f"[2:a]atrim=start={s0:.4f}:end={s1:.4f},asetpts=PTS-STARTPTS,afade=t=in:d=0.3[a0];[3:a]asetpts=PTS-STARTPTS[a1];"
         f"[v0][a0][v1][a1]concat=n=2:v=1:a=1[v][a]", "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-preset", "slow",
         "-b:v", "1150k", "-maxrate", "2500k", "-bufsize", "5000k", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k",
         "-movflags", "+faststart", "review/m7_credits.mp4"])
    for f in ("review/m7_bookend.mp4", "review/m7_credits.mp4"):
        d = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration,size", "-of", "csv=p=0", f],
                           capture_output=True, text=True).stdout.strip()
        print(f, d)


if __name__ == "__main__":
    main()
