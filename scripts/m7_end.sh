#!/usr/bin/env bash
# M7: the end sequence over the instrumental (production log 60; config/end_cards_m7.json, remotion/src/components/EndCards.tsx):
#   M7-End-<card>     each card or fact page alone, a still of its last frame (fully in) -> review/m7_end/<card>.png
#   M7-EndSequence    the whole sequence, h264 CRF 18, silent until the instrumental is in -> renders/m7/remotion/
#   then scripts/m7_end_sheet.py -> review/m7_end_sheet.jpg (the stills, each with its words and hold);
#   with snap on (the instrumental, config/end_cards_m7.json): the music for the sequence, the post-filtered credits
#   instrumental from its start, cut at the sequence's end and faded out over music_fade_s -> audio/credits/credits-m7-end.wav
#   (s24); and the review preview: the song's last 6 s (O23 from review/m5c3_animatic.mp4 with the post-filtered v1.3
#   master's audio), then the sequence with its music -> review/m7_end_preview.mp4 (h264 650k, AAC 128k).
# Same flags as scripts/m1b_remotion.sh (CPU, --gl=swangle, concurrency 2).
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
quiet() { grep -v -i -e zod -e "version mismatch" -e "^-*$" -e "wrong versions" -e "breakages" -e "React context" -e "Type errors" \
  -e "Failed renders" -e "resolve:" -e "package.json has" -e "Remove the" -e "Run .npx" -e "^$" || true; }
mkdir -p review/m7_end renders/m7/remotion
# the credits' {interventions} and {repo_url} (human interventions 39): config/release.json, from the log as it stands
N=$(grep -c '^## ' log/human_interventions.md)
printf '{\n "_doc": "Written by scripts/m7_end.sh: the end credits'"'"' {interventions} (the entries in log/human_interventions.md) and {repo_url}.",\n "interventions": %s,\n "repo_url": "github.com/Derivative-Work/all-systems-operational"\n}\n' "$N" > config/release.json
npx remotion compositions remotion/src/index.ts 2>/dev/null | awk '$1 ~ /^M7-End/ {print $1, $4}' > review/m7_end/plan.txt
while read -r id n; do
  [ "$id" = M7-EndSequence ] && continue
  npx remotion still "$id" "review/m7_end/${id#M7-End-}.png" --frame=$((n - 1)) --gl=swangle --log=error 2>&1 | quiet
done < review/m7_end/plan.txt
t=$(date +%s)
npx remotion render M7-EndSequence renders/m7/remotion/M7-EndSequence.mp4 --codec=h264 --crf=18 --gl=swangle --concurrency=2 --log=error 2>&1 | quiet
echo "M7-EndSequence.mp4 $(( $(date +%s) - t )) s"
.venv/bin/python -I scripts/m7_end_sheet.py
END=$(awk '$1=="M7-EndSequence"{printf "%.4f", $2/30}' review/m7_end/plan.txt)
FADE=$(.venv/bin/python -I -c "import json; s=json.load(open('config/end_cards_m7.json'))['snap']; print(s['music_fade_s'] if s else 0)")
[ "$FADE" = 0 ] && exit 0
ST=$(.venv/bin/python -I -c "print(round($END - $FADE, 4))")
ffmpeg -v error -y -i audio/postfilter/all-systems-operational-credits-deslopped.wav -af "atrim=0:$END,afade=t=out:st=$ST:d=$FADE" \
  -c:a pcm_s24le audio/credits/credits-m7-end.wav
# the song's last 6 s: video 241.979-247.979 s = song 233.579-239.579 s (lead-in 8.4 s; O24 starts at video frame 7439)
ffmpeg -v error -y -ss 241.979 -t 6 -i review/m5c3_animatic.mp4 -ss 233.579 -t 6 -i audio/postfilter/all-systems-operational-master-deslopped.wav \
  -i renders/m7/remotion/M7-EndSequence.mp4 -i audio/credits/credits-m7-end.wav \
  -filter_complex "[0:v]scale=1920:1080,fps=30,setsar=1[v0];[2:v]fps=30,setsar=1[v1];[v0][1:a][v1][3:a]concat=n=2:v=1:a=1[v][a]" \
  -map "[v]" -map "[a]" -c:v libx264 -b:v 650k -preset slow -pix_fmt yuv420p -c:a aac -b:a 128k -movflags +faststart review/m7_end_preview.mp4
echo "review/m7_end_preview.mp4 $(ffprobe -v error -show_entries format=duration,size -of csv=p=0 review/m7_end_preview.mp4)"
