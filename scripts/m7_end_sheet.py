"""M7 end sequence review sheet: each card or fact page (review/m7_end/<card>.png, scripts/m7_end.sh) with its words and
hold (review/m7_end/plan.txt, from the compositions' lengths; config/end_cards_m7.json's reading rate).
Usage: .venv/bin/python -I scripts/m7_end_sheet.py  -> review/m7_end_sheet.jpg
"""
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

TILE = (960, 540)
FONT = ImageFont.truetype("remotion/public/fonts/Inter-VF.ttf", 22)
cfg = json.loads(Path("config/end_cards_m7.json").read_text())
plan = [ln.split() for ln in Path("review/m7_end/plan.txt").read_text().splitlines()]
frames = {i.removeprefix("M7-End-"): int(n) for i, n in plan}
total = frames.pop("M7-EndSequence")
names = {"end": "end card", "final": "final card", "disclosure": "disclosure"}
cards = list(frames)
cols, cap_h = 2, 40
rows = (len(cards) + cols - 1) // cols
sheet = Image.new("RGB", (cols * TILE[0] + (cols + 1) * 10, rows * (TILE[1] + cap_h) + (rows + 1) * 10 + 44), (24, 24, 26))
d = ImageDraw.Draw(sheet)
d.text((14, 12), f"M7 end sequence: {len(cards)} cards, {total / 30:.1f} s at {cfg['wpm']} words a minute plus "
       f"{cfg['settle_s']:.0f} s a card (config/end_cards_m7.json); silent until the instrumental is in", fill=(230, 230, 230), font=FONT)
for i, c in enumerate(cards):
    x, y = 10 + (i % cols) * (TILE[0] + 10), 54 + (i // cols) * (TILE[1] + cap_h + 10)
    sheet.paste(Image.open(f"review/m7_end/{c}.png").convert("RGB").resize(TILE, Image.LANCZOS), (x, y))
    label = names.get(c, f"fact card, page {c.removeprefix('fact')} of {sum(k.startswith('fact') for k in cards)}")
    d.text((x + 4, y + TILE[1] + 8), f"{label}: {frames[c] / 30:.0f} s", fill=(230, 230, 230), font=FONT)
sheet.save("review/m7_end_sheet.jpg", quality=88)
print("review/m7_end_sheet.jpg", sheet.size)
