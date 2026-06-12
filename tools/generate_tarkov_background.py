# Generates res/themes/Tarkov/background.png (320x480 portrait)
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "res" / "themes" / "Tarkov"
OUT.mkdir(parents=True, exist_ok=True)

W, H = 320, 480
BG = (16, 18, 14)
PANEL = (26, 29, 22)
ACCENT = (158, 134, 67)  # tarkov gold
TEXT_DIM = (120, 125, 110)

img = Image.new("RGB", (W, H), BG)
d = ImageDraw.Draw(img)

font_dir = ROOT / "res" / "fonts"
title_font = ImageFont.truetype(str(font_dir / "roboto" / "Roboto-Bold.ttf"), 22)
label_font = ImageFont.truetype(str(font_dir / "roboto" / "Roboto-Regular.ttf"), 13)

# Header
d.rectangle([0, 0, W, 56], fill=PANEL)
d.text((16, 14), "TARKOV QUESTS", font=title_font, fill=ACCENT)
d.rectangle([0, 56, W, 58], fill=ACCENT)

# Stats zone labels
d.text((16, 70), "Niveau", font=label_font, fill=TEXT_DIM)
d.text((120, 70), "Quetes terminees", font=label_font, fill=TEXT_DIM)

# Progress bar slot background
d.rectangle([16, 130, W - 16, 146], fill=PANEL)

# Available quests section
d.rectangle([0, 162, W, 188], fill=PANEL)
d.text((16, 167), "QUETES DISPONIBLES", font=label_font, fill=ACCENT)

img.save(OUT / "background.png")
print(f"Saved {OUT / 'background.png'}")
