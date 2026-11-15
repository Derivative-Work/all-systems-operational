#!/usr/bin/env bash
# M3 screen kit: renders review stills of every composition into review/m3/screens/<name>.png (1920x1080; textures at
# their own sizes), then the contact sheet review/m3_screens.jpg. Stills only (no video renders while the GPU is
# shared); Remotion's concurrency is 2 (remotion.config.ts). Animated compositions get 2-4 telling frames.
# Usage: remotion/render_stills.sh [composition-id ...]   (no args: all, plus the contact sheet)
set -euo pipefail
cd "$(dirname "$0")/.."
OUT=review/m3/screens
mkdir -p "$OUT" remotion/public/real

# The creator's real screenshots and avatar (git-ignored; O01 only). The avatar is cropped from his own 9:39 AM
# message in slack-5.png (the one approved real-person exception).
REAL=remotion/public/real
[ -f "$REAL/status-page-broken.png" ] || cp assets/screenshots/status-page-broken.png "$REAL/"
[ -f "$REAL/m365-license-failed-outage.png" ] || cp assets/screenshots/m365-license-failed-outage.png "$REAL/"
[ -f "$REAL/creator_avatar.png" ] || .venv/bin/python -I -c "
from PIL import Image
Image.open('assets/screenshots/slack-5.png').convert('RGB').crop((29, 1019, 95, 1085)).save('$REAL/creator_avatar.png')"

# id  frame  [output name]
STILLS=(
  "O01a-SpikeChart 20 O01a-SpikeChart-f20"
  "O01a-SpikeChart 36 O01a-SpikeChart-f36"
  "O01a-SpikeChart 59 O01a-SpikeChart-f59"
  "O01b-RealScreens 20 O01b-RealScreens-license"
  "O01b-RealScreens 60 O01b-RealScreens-statuspage"
  "O01c-ChatPost 10 O01c-ChatPost-hold"
  "O01c-ChatPost 50 O01c-ChatPost-struck"
  "O01c-ChatPost 80 O01c-ChatPost-cursor"
  "O01c-ChatPost 101 O01c-ChatPost-click"
  "StatusPage-allGreen 0"
  "O02-StatusPage 100 O02-StatusPage-investigating"
  "O13-StatusPage 20"
  "O23-StatusPage 0 O23-StatusPage-f0"
  "O23-StatusPage 12 O23-StatusPage-f12-dip"
  "O03-LowerThird 30"
  "O08-LowerThird 30 O08-LowerThird-echo1"
  "O08-LowerThird 102 O08-LowerThird-echo2"
  "O08-LowerThird 174 O08-LowerThird-echo3"
  "O08-LowerThird 246 O08-LowerThird-echo4"
  "O09-LowerThird 60"
  "O19-LowerThird 30"
  "O22-LowerThird 30"
  "O04-PhoneChat 10 O04-PhoneChat-f10"
  "O04-PhoneChat 140 O04-PhoneChat-f140"
  "O04-PhoneChatScreen 140"
  "O08-PhoneChat 40"
  "O08-PhoneChatScreen 40"
  "O05-Calendar 5 O05-Calendar-full"
  "O05-Calendar 70 O05-Calendar-draining"
  "O05-Calendar 140 O05-Calendar-empty"
  "O05-CalendarScreen 5"
  "O12-BufferingFreeze 10"
  "O21-BufferingFreeze 10"
  "Caption-dramatization 0"
  "O13-TechnicalDifficulties 30"
  "O10-Switch 0 O10-Switch-on"
  "Switch-off 0"
  "O11-Switch 5 O11-Switch-straining"
  "O12-Switch 16 O12-Switch-sagging"
  "O12-Switch 40 O12-Switch-dropped"
  "O21-Switch 30 O21-Switch-holding"
  "O21-Switch 60 O21-Switch-dropped"
  "O09-KickDrumHead 0"
  "KickDrumHead-branchB 0"
  "O14-TableTent 0"
  "O14-Polaroid 0"
  "OnAirSign-lit 0"
  "OnAirSign-unlit 0"
  "StationSign 0"
  "O18-Whiteboard 90 O18-Whiteboard-fill30"
  "O18-Whiteboard 200 O18-Whiteboard-fill70"
  "O18-Whiteboard 300 O18-Whiteboard-full"
  "O18-Whiteboard-branchC 288"
  "O18-Whiteboard-diffPreview 300"
  "O15-Disclosure 30"
  "O24-FactCard 30"
  "O24-EndCard 30"
  "O24-FinalCard 30"
)
for row in "${STILLS[@]}"; do
  read -r id frame name <<<"$row"; name=${name:-$id}
  if [ $# -gt 0 ] && [[ ! " $* " =~ " $id " ]]; then continue; fi
  npx remotion still "$id" "$OUT/$name.png" --frame="$frame" --image-format=png --concurrency=2 --gl=swangle --log=error
  echo "$OUT/$name.png"
done
# Contact sheet, in the order above.
if [ $# -eq 0 ] || [ "${SHEET:-0}" = 1 ]; then
  files=(); for row in "${STILLS[@]}"; do read -r id frame name <<<"$row"; files+=("$OUT/${name:-$id}.png"); done
  .venv/bin/python -I scripts/contact_sheet.py review/m3_screens.jpg "${files[@]}"
fi
