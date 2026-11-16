#!/usr/bin/env bash
# M7c: the Remotion textures changed or added in this pass (production log 44+), same flags as scripts/m7b_remotion.sh:
#   M7-Tree-Agent-night/day   the assistant screen, unnamed: "assistant · read-only" (human interventions 22)
#   M7-O04-PhoneScreen        O04's phone with the question from the first frame (human interventions 22)
#     (both through scripts/m7b_remotion.sh, into assets/gen/tex/m7b/<composition>/frames/; archive the old frames first)
#   M7c-Crowd-Lock/Camera/Chat  the live room's crowd phones (stills, 540x1170 JPEG q95) -> assets/gen/tex/m7c/
# The camera view's picture is a crop of the M7a live-room wide (renders/m7a/O03a.png, the band backlit): written to
# remotion/public/gen/m7c_viewfinder.jpg first.
# Usage: scripts/m7c_remotion.sh [screens|crowd ...]   (no args: both)
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
quiet() { grep -v -i -e zod -e "version mismatch" -e "^-*$" -e "wrong versions" -e "breakages" -e "React context" -e "Type errors" \
  -e "Failed renders" -e "resolve:" -e "package.json has" -e "Remove the" -e "Run .npx" -e "^$" || true; }
SEL=("$@")
want() { [ ${#SEL[@]} -eq 0 ] || [[ " ${SEL[*]} " =~ " $1 " ]]; }
if want screens; then
  scripts/m7b_remotion.sh M7-O04-PhoneScreen M7-Tree-Agent-night M7-Tree-Agent-day
fi
if want crowd; then
  out=assets/gen/tex/m7c
  mkdir -p "$out" remotion/public/gen
  .venv/bin/python -I -c "
import cv2
im = cv2.imread('renders/m7a/O03a.png')
cv2.imwrite('remotion/public/gen/m7c_viewfinder.jpg', im[40:1080, 890:1370], [cv2.IMWRITE_JPEG_QUALITY, 92])
"
  for c in Lock Camera Chat; do
    npx remotion still "M7c-Crowd-$c" "$out/crowd_$(echo $c | tr A-Z a-z).jpg" --frame=0 --scale=0.5 --image-format=jpeg --jpeg-quality=95 \
      --gl=swangle --log=error 2>&1 | quiet
    echo "$out/crowd_$(echo $c | tr A-Z a-z).jpg"
  done
fi
