"""Render the fictional test letters in cases.json as PNG photos (A4 at 150 dpi).

Usage: python3 tests/letters/render_letters.py
Needs Pillow and the DejaVu fonts. All names, offices and numbers are invented.
"""
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def render(case):
    page = Image.new("RGB", (1240, 1754), "white")
    draw = ImageDraw.Draw(page)
    small, body, head = ImageFont.truetype(FONT, 22), ImageFont.truetype(FONT, 28), ImageFont.truetype(BOLD, 34)
    draw.text((100, 90), case["sender"], font=head, fill="black")
    draw.text((100, 140), "Musterstraße 1 · 12345 Musterstadt", font=small, fill="#444")
    draw.text((100, 260), "Max/Maria Beispiel · Beispielweg 7 · 12345 Musterstadt", font=small, fill="#444")
    draw.text((860, 330), "Musterstadt, 25.11.2026", font=small, fill="black")
    y = 430
    for i, line in enumerate(case["lines"]):
        draw.text((100, y), line, font=head if i == 0 else body, fill="black")
        y += 70 if i == 0 else 52
    draw.text((100, y + 60), "Mit freundlichen Grüßen", font=body, fill="black")
    draw.text((100, y + 112), "Im Auftrag – Testbrief, alle Angaben erfunden", font=small, fill="#666")
    page.save(HERE / f"{case['id']}.png", optimize=True)


if __name__ == "__main__":
    cases = json.loads((HERE / "cases.json").read_text(encoding="utf-8"))
    for case in cases:
        render(case)
    print(f"rendered {len(cases)} letters")
