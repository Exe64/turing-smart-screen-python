#!/usr/bin/env python3
"""Generate the Claude Code theme background for 320x480 Turing Smart Screen."""

from PIL import Image, ImageDraw, ImageFont, ImageFilter
import math

WIDTH = 320
HEIGHT = 480

img = Image.new('RGB', (WIDTH, HEIGHT), (18, 18, 24))
draw = ImageDraw.Draw(img)

BG_DARK = (18, 18, 24)
BG_CARD = (30, 32, 42)
CARD_BORDER = (55, 60, 80)
CLAUDE_ORANGE = (217, 119, 52)
CLAUDE_CREAM = (244, 226, 198)
ACCENT_BLUE = (100, 140, 220)
TEXT_DIM = (120, 125, 140)
WHITE = (255, 255, 255)

def draw_rounded_rect(draw, xy, radius, fill, outline=None):
    x0, y0, x1, y1 = xy
    draw.rounded_rectangle(xy, radius=radius, fill=fill, outline=outline)

# Header area (0-70)
draw_rounded_rect(draw, (8, 8, 312, 66), radius=12, fill=BG_CARD, outline=CARD_BORDER)

# Draw a simple Claude logo (stylized circle with gradient feel)
cx, cy = 38, 37
for r in range(18, 0, -1):
    ratio = r / 18
    c = tuple(int(CLAUDE_ORANGE[i] * ratio + BG_CARD[i] * (1 - ratio)) for i in range(3))
    draw.ellipse((cx - r, cy - r, cx + r, cy + r), fill=c)
# Inner sparkle
draw.ellipse((cx - 5, cy - 5, cx + 5, cy + 5), fill=CLAUDE_CREAM)

# 5h section (76-196)
draw_rounded_rect(draw, (8, 76, 312, 196), radius=12, fill=BG_CARD, outline=CARD_BORDER)

# Bar background for 5h
draw_rounded_rect(draw, (20, 162, 300, 182), radius=6, fill=(20, 22, 30))

# Weekly section (206-326)
draw_rounded_rect(draw, (8, 206, 312, 326), radius=12, fill=BG_CARD, outline=CARD_BORDER)

# Bar background for weekly
draw_rounded_rect(draw, (20, 292, 300, 312), radius=6, fill=(20, 22, 30))

# Details section (336-472) - two sub-cards side by side
draw_rounded_rect(draw, (8, 336, 154, 420), radius=12, fill=BG_CARD, outline=CARD_BORDER)
draw_rounded_rect(draw, (166, 336, 312, 420), radius=12, fill=BG_CARD, outline=CARD_BORDER)

# Extra usage section
draw_rounded_rect(draw, (8, 430, 312, 472), radius=12, fill=BG_CARD, outline=CARD_BORDER)

# Add subtle grid pattern
for y in range(0, HEIGHT, 40):
    draw.line([(0, y), (WIDTH, y)], fill=(25, 27, 35), width=1)
for x in range(0, WIDTH, 40):
    draw.line([(x, 0), (x, HEIGHT)], fill=(25, 27, 35), width=1)

# Re-draw cards on top of grid
draw_rounded_rect(draw, (8, 8, 312, 66), radius=12, fill=BG_CARD, outline=CARD_BORDER)
draw_rounded_rect(draw, (8, 76, 312, 196), radius=12, fill=BG_CARD, outline=CARD_BORDER)
draw_rounded_rect(draw, (8, 206, 312, 326), radius=12, fill=BG_CARD, outline=CARD_BORDER)
draw_rounded_rect(draw, (8, 336, 154, 420), radius=12, fill=BG_CARD, outline=CARD_BORDER)
draw_rounded_rect(draw, (166, 336, 312, 420), radius=12, fill=BG_CARD, outline=CARD_BORDER)
draw_rounded_rect(draw, (8, 430, 312, 472), radius=12, fill=BG_CARD, outline=CARD_BORDER)

# Re-draw bar backgrounds
draw_rounded_rect(draw, (20, 162, 300, 182), radius=6, fill=(20, 22, 30))
draw_rounded_rect(draw, (20, 292, 300, 312), radius=6, fill=(20, 22, 30))

# Re-draw logo
for r in range(18, 0, -1):
    ratio = r / 18
    c = tuple(int(CLAUDE_ORANGE[i] * ratio + BG_CARD[i] * (1 - ratio)) for i in range(3))
    draw.ellipse((cx - r, cy - r, cx + r, cy + r), fill=c)
draw.ellipse((cx - 5, cy - 5, cx + 5, cy + 5), fill=CLAUDE_CREAM)

# Static labels with a system font
try:
    font_path = "res/fonts/jetbrains-mono/JetBrainsMono-Bold.ttf"
    font_title = ImageFont.truetype(font_path, 18)
    font_label = ImageFont.truetype(font_path, 13)
    font_small = ImageFont.truetype(font_path, 11)
except:
    font_title = ImageFont.load_default()
    font_label = font_title
    font_small = font_title

# Header text
draw.text((62, 22), "CLAUDE CODE", font=font_title, fill=WHITE)
draw.text((62, 44), "Usage Monitor", font=font_small, fill=TEXT_DIM)

# 5h section labels
draw.text((20, 84), "5-HOUR WINDOW", font=font_label, fill=CLAUDE_ORANGE)

# Weekly section labels
draw.text((20, 214), "WEEKLY USAGE", font=font_label, fill=ACCENT_BLUE)

# Detail section labels
draw.text((18, 344), "Sonnet", font=font_small, fill=TEXT_DIM)
draw.text((176, 344), "Extra", font=font_small, fill=TEXT_DIM)

# Extra usage label
draw.text((20, 440), "Credits:", font=font_small, fill=TEXT_DIM)

img.save("res/themes/ClaudeCode/background.png")
print("Background generated: res/themes/ClaudeCode/background.png")
