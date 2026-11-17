#!/usr/bin/env bash
# M5: render the animatic's Remotion pieces at 960x540 (--scale=0.5 of the 1920x1080 compositions), one file per piece,
# each its shot's exact length (the M5-* compositions in remotion/src/Root.tsx take it from timing/shot_times.json).
# Adapted from Ever Present's scripts/m5_remotion.sh (9301de4): same render call; adds transparent overlays as ProRes
# 4444 with alpha (lower thirds, captions, freezes, the O11 live overlay) and two textures
# (the O04 phone screen, the O18 whiteboard, which blender/animatic.py maps as a movie texture). CPU only, --gl=swangle,
# concurrency 2 (remotion.config.ts).
# Usage: scripts/m5_remotion.sh [composition-id ...]   (no args: all)
#        M5_REMOTION_OUT=<dir> scripts/m5_remotion.sh ...   (another folder; the M7 review cut uses renders/m7/remotion_review)
#        M5_REMOTION_SCALE=1 M5_REMOTION_OUT=renders/m7/remotion_master scripts/m5_remotion.sh ...   (full size, the master)
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
out=${M5_REMOTION_OUT:-renders/m5/remotion}
scale=${M5_REMOTION_SCALE:-0.5}   # 1 for the 1080p master (scripts/m7_master.py)
mkdir -p "$out"
quiet() { grep -v -i -e zod -e "version mismatch" -e "^-*$" -e "wrong versions" -e "breakages" -e "React context" -e "Type errors" \
  -e "Failed renders" -e "resolve:" -e "package.json has" -e "Remove the" -e "Run .npx" -e "^$" || true; }
want() { [ ${#SEL[@]} -eq 0 ] || [[ " ${SEL[*]} " =~ " $1 " ]]; }
SEL=("$@")
h264() { want "$1" || return 0; t=$(date +%s); npx remotion render "$1" "$out/$1.mp4" --scale=$scale --codec=h264 --crf=18 --gl=swangle --concurrency=2 --log=error 2>&1 | quiet; echo "$1.mp4 $(( $(date +%s) - t )) s"; }
alpha() { want "$1" || return 0; t=$(date +%s); npx remotion render "$1" "$out/$1.mov" --scale=$scale --codec=prores --prores-profile=4444 --pixel-format=yuva444p10le --image-format=png --gl=swangle --concurrency=2 --log=error 2>&1 | quiet; echo "$1.mov $(( $(date +%s) - t )) s"; }
for c in M5-O01 M5-O02 M5-O05 M5-O08-Phone M5-O13-Card M5-O13-Status M5-O23 M5-O24-EndCard M5-O24-FinalCard M5-FactCard M5-DisclosureCard \
         M5-O04-PhoneScreen M5-O18-Whiteboard; do h264 "$c"; done
for c in M5-O03-LT M5-O08-LT M5-O09-LT M5-O19-LT M5-O22-LT M5-O07-Caption M5-Dramatization M5-O11-Live M5-O12-Freeze M5-O21-Freeze; do alpha "$c"; done
