#!/usr/bin/env bash
# M1b: review stills of the v1.3 bridge's Remotion pieces (the whiteboard on each sung line, the denial tags, the
# status pages' stamp, the fact card) into review/m1b/, then the sheet review/m1b_remotion.jpg.
# Usage: scripts/m1b_stills.sh
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
OUT=review/m1b
mkdir -p "$OUT"
STILLS=(
  "M7-O18-Whiteboard 25 board-f025-root-cause"
  "M7-O18-Whiteboard 84 board-f084-july-fix"
  "M7-O18-Whiteboard 98 board-f098-circled"
  "M7-O18-Whiteboard 170 board-f170-contributing"
  "M7-O18-Whiteboard 290 board-f290-three-factors"
  "M7-O18-Whiteboard 345 board-f345-not-related"
  "M7-O18-Whiteboard 420 board-f420-full-report-lessons"
  "M7-O18-Whiteboard 575 board-f575-end"
  "M7-O18-Whiteboard-full 0 board-full"
  "M7-O18-Whiteboard-nrOnly 0 board-nr-only"
  "M7-O18-DenialTags 305 tags-f305"
  "M7-O18-DenialTags 360 tags-f360"
  "O02-StatusPage 100 O02-StatusPage"
  "O23-StatusPage 0 O23-StatusPage"
  "M5-FactCard 30 FactCard"
)
for row in "${STILLS[@]}"; do
  read -r id frame name <<<"$row"
  npx remotion still "$id" "$OUT/$name.png" --frame="$frame" --image-format=png --concurrency=2 --gl=swangle --log=error
  echo "$OUT/$name.png"
done
files=(); for row in "${STILLS[@]}"; do read -r id frame name <<<"$row"; files+=("$OUT/$name.png"); done
.venv/bin/python -I scripts/contact_sheet.py review/m1b_remotion.jpg "${files[@]}"
