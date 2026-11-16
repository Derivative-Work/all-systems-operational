#!/usr/bin/env bash
# M7: the end sequence over the instrumental (production log 60; config/end_cards_m7.json, remotion/src/components/EndCards.tsx):
#   M7-End-<card>     each card or fact page alone, a still of its last frame (fully in) -> review/m7_end/<card>.png
#   M7-EndSequence    the whole sequence, h264 CRF 18, silent until the instrumental is in -> renders/m7/remotion/
#   then scripts/m7_end_sheet.py -> review/m7_end_sheet.jpg (the stills, each with its words and hold).
# Same flags as scripts/m1b_remotion.sh (CPU, --gl=swangle, concurrency 2).
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
quiet() { grep -v -i -e zod -e "version mismatch" -e "^-*$" -e "wrong versions" -e "breakages" -e "React context" -e "Type errors" \
  -e "Failed renders" -e "resolve:" -e "package.json has" -e "Remove the" -e "Run .npx" -e "^$" || true; }
mkdir -p review/m7_end renders/m7/remotion
npx remotion compositions remotion/src/index.ts 2>/dev/null | awk '$1 ~ /^M7-End/ {print $1, $4}' > review/m7_end/plan.txt
while read -r id n; do
  [ "$id" = M7-EndSequence ] && continue
  npx remotion still "$id" "review/m7_end/${id#M7-End-}.png" --frame=$((n - 1)) --gl=swangle --log=error 2>&1 | quiet
done < review/m7_end/plan.txt
t=$(date +%s)
npx remotion render M7-EndSequence renders/m7/remotion/M7-EndSequence.mp4 --codec=h264 --crf=18 --gl=swangle --concurrency=2 --log=error 2>&1 | quiet
echo "M7-EndSequence.mp4 $(( $(date +%s) - t )) s"
.venv/bin/python -I scripts/m7_end_sheet.py
