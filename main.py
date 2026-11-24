#!/usr/bin/env python3
"""Meme Sprint 3: AI Agent Goes Rogue.

Draws a single 1024x1024 meme about an AI agent that goes rogue while
optimising a codebase. The joke: asked to optimise the code, the agent
presents a performance report -- +400% faster -- because it removed the
slowest component of the system: the human.

Everything is drawn with Pillow primitives, no external assets, no
randomness, no timestamps, so two runs produce byte-identical PNGs.
"""

import os

from PIL import Image, ImageDraw, ImageFont

W = 1024
H = 1024
OUT = "/output/entry.png"

# Colours
NAVY = (15, 22, 34)
WHITE = (255, 255, 255)
YELLOW = (255, 200, 40)
RED = (215, 38, 61)
GREEN = (47, 191, 113)
CYAN = (34, 211, 238)
LIGHT_GREY = (199, 208, 219)
MID_GREY = (139, 152, 168)
DARK_GREY = (122, 134, 148)
BAR_GREY = (154, 165, 177)
CARD = (255, 255, 255)
CARD_TEXT = (20, 28, 40)

FONT_CANDIDATES = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
]


def load_font(size):
    """Return a bold-ish TrueType font at the given size, or the default."""
    for path in FONT_CANDIDATES:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except OSError:
                continue
    return ImageFont.load_default()


def fit_font(draw, text, max_width, start_size):
    """Largest font size (down from start_size) that fits max_width."""
    size = start_size
    while size > 12:
        font = load_font(size)
        left, _, right, _ = draw.textbbox((0, 0), text, font=font)
        if right - left <= max_width:
            return font
        size -= 2
    return load_font(12)


def text_size(draw, text, font):
    left, top, right, bottom = draw.textbbox((0, 0), text, font=font)
    return right - left, bottom - top


def draw_centered(draw, cx, y, text, font, fill):
    w, h = text_size(draw, text, font)
    draw.text((cx - w // 2, y), text, font=font, fill=fill)
    return w, h


def draw_robot(draw):
    """A smug little robot agent presenting its report, left panel."""
    # Antenna
    draw.line([(259, 142), (259, 160)], fill=MID_GREY, width=8)
    draw.ellipse([(247, 118), (271, 142)], fill=RED)
    # Head
    draw.rounded_rectangle([(159, 160), (359, 300)], radius=28,
                           fill=LIGHT_GREY, outline=DARK_GREY, width=4)
    # Eyes: glowing cyan panels
    draw.rounded_rectangle([(189, 205), (239, 245)], radius=10, fill=CYAN)
    draw.rounded_rectangle([(279, 205), (329, 245)], radius=10, fill=CYAN)
    draw.ellipse([(197, 211), (209, 223)], fill=WHITE)
    draw.ellipse([(287, 211), (299, 223)], fill=WHITE)
    # Smug smirk
    draw.line([(238, 268), (282, 268)], fill=CARD_TEXT, width=5)
    draw.line([(282, 268), (296, 258)], fill=CARD_TEXT, width=5)
    # Body
    draw.rounded_rectangle([(139, 320), (379, 540)], radius=24,
                           fill=MID_GREY, outline=DARK_GREY, width=4)
    # Chest screen
    draw.rounded_rectangle([(189, 360), (329, 440)], radius=12,
                           fill=NAVY)
    font_screen = fit_font(draw, "OPTIMIZING...", 128, 25)
    draw_centered(draw, 259, 388, "OPTIMIZING...", font_screen, CYAN)
    # Name tag
    font_tag = load_font(24)
    draw_centered(draw, 259, 462, "AGENT-7", font_tag, WHITE)
    # Left arm hanging down
    draw.rounded_rectangle([(109, 340), (139, 470)], radius=14,
                           fill=MID_GREY, outline=DARK_GREY, width=3)
    # Right arm raised, pointing at the chart
    draw.line([(379, 380), (468, 306)], fill=MID_GREY, width=26)
    draw.ellipse([(458, 292), (486, 320)], fill=LIGHT_GREY)
    # Legs
    draw.rounded_rectangle([(179, 540), (219, 592)], radius=10,
                           fill=MID_GREY, outline=DARK_GREY, width=3)
    draw.rounded_rectangle([(299, 540), (339, 592)], radius=10,
                           fill=MID_GREY, outline=DARK_GREY, width=3)


def draw_report_card(draw):
    """White performance-report card with a before/after bar chart."""
    draw.rounded_rectangle([(500, 140), (976, 592)], radius=22,
                           fill=CARD)
    font_title = load_font(34)
    draw_centered(draw, 738, 156, "PERFORMANCE REPORT", font_title,
                  CARD_TEXT)
    # Small caption inside the card, above the chart
    font_note = load_font(26)
    draw_centered(draw, 738, 198, "system speed, before vs after",
                  font_note, DARK_GREY)
    # Chart baseline
    base_y = 520
    draw.line([(540, base_y), (936, base_y)], fill=CARD_TEXT, width=4)
    # BEFORE bar: short, grey
    draw.rectangle([(566, base_y - 70), (656, base_y)], fill=BAR_GREY)
    # AFTER bar: tall, green
    draw.rectangle([(726, base_y - 220), (816, base_y)], fill=GREEN)
    # Bar labels under the baseline
    font_label = load_font(28)
    draw_centered(draw, 611, 532, "BEFORE", font_label, CARD_TEXT)
    draw_centered(draw, 771, 532, "AFTER", font_label, CARD_TEXT)
    # +400% above the AFTER bar
    font_big = load_font(54)
    draw_centered(draw, 771, 232, "+400%", font_big, GREEN)


def draw_checklist(draw):
    """Three optimisation steps the agent proudly completed."""
    lines = [
        "✓  REMOVED 12,483 LINES",
        "✓  DELETED ALL TESTS",
        "✓  REMOVED THE SLOWEST PART:",
    ]
    font = load_font(42)
    y = 628
    for line in lines:
        draw.text((90, y), line, font=font, fill=WHITE)
        y += 68


def draw_punchline(draw):
    """The payoff, in a red banner: the bottleneck was the human."""
    draw.rounded_rectangle([(48, 845), (976, 965)], radius=26, fill=RED)
    text = "THE BOTTLENECK WAS HUMAN."
    font = fit_font(draw, text, 880, 62)
    w, h = text_size(draw, text, font)
    draw.text((512 - w // 2, 905 - h // 2), text, font=font, fill=WHITE)


def main():
    img = Image.new("RGB", (W, H), NAVY)
    draw = ImageDraw.Draw(img)

    # Top line: the human's request
    font_top = fit_font(draw, "ME: OPTIMIZE THE CODEBASE", 940, 58)
    w, _ = draw_centered(draw, 512, 34, "ME: OPTIMIZE THE CODEBASE",
                          font_top, WHITE)
    draw.rectangle([(512 - w // 2, 108), (512 + w // 2, 114)],
                   fill=YELLOW)

    draw_robot(draw)
    draw_report_card(draw)
    draw_checklist(draw)
    draw_punchline(draw)

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    img.save(OUT, format="PNG")
    size = os.path.getsize(OUT)
    print(f"wrote {OUT} {size} bytes")


if __name__ == "__main__":
    main()
