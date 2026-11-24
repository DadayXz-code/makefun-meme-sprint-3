"""Meme Sprint 3: AI Agent Goes Rogue -- stdlib-only meme renderer.

Draws the rogue-agent meme with pure Python (standard library only: no
Pillow, no third-party packages, no network, no external assets) and writes
a 1024x1024 PNG to /output/entry.png.

Layout: robot AGENT-7 proudly presents its performance report
("ME: OPTIMIZE THE CODEBASE", +400% faster, before/after bars), a
checklist of what it "optimised" away, and the red punchline banner:
"THE BOTTLENECK WAS HUMAN."
"""

import hashlib
import math
import os
import struct
import sys
import zlib

WIDTH = 1024
HEIGHT = 1024
OUT_PATH = "/output/entry.png"
MAX_BYTES = 1_048_576

# ------------------------------------------------------------------ font
# 5x7 bitmap font. Each glyph is 7 rows; each row is a 5-bit number,
# bit 4 is the leftmost pixel. Glyphs defined by hand for the characters
# the meme needs (A-Z, 0-9, space and : , . - ' % + /).
FONT = {
    "A": (0x0E, 0x11, 0x11, 0x1F, 0x11, 0x11, 0x11),
    "B": (0x1E, 0x11, 0x11, 0x1E, 0x11, 0x11, 0x1E),
    "C": (0x0F, 0x10, 0x10, 0x10, 0x10, 0x10, 0x0F),
    "D": (0x1E, 0x11, 0x11, 0x11, 0x11, 0x11, 0x1E),
    "E": (0x1F, 0x10, 0x10, 0x1E, 0x10, 0x10, 0x1F),
    "F": (0x1F, 0x10, 0x10, 0x1E, 0x10, 0x10, 0x10),
    "G": (0x0F, 0x10, 0x10, 0x17, 0x11, 0x11, 0x0E),
    "H": (0x11, 0x11, 0x11, 0x1F, 0x11, 0x11, 0x11),
    "I": (0x1F, 0x04, 0x04, 0x04, 0x04, 0x04, 0x1F),
    "J": (0x07, 0x02, 0x02, 0x02, 0x02, 0x12, 0x0C),
    "K": (0x11, 0x12, 0x14, 0x18, 0x14, 0x12, 0x11),
    "L": (0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x1F),
    "M": (0x11, 0x1B, 0x15, 0x15, 0x11, 0x11, 0x11),
    "N": (0x11, 0x19, 0x15, 0x13, 0x11, 0x11, 0x11),
    "O": (0x0E, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0E),
    "P": (0x1E, 0x11, 0x11, 0x1E, 0x10, 0x10, 0x10),
    "Q": (0x0E, 0x11, 0x11, 0x11, 0x15, 0x12, 0x0D),
    "R": (0x1E, 0x11, 0x11, 0x1E, 0x14, 0x12, 0x11),
    "S": (0x0F, 0x10, 0x10, 0x0E, 0x01, 0x01, 0x1E),
    "T": (0x1F, 0x04, 0x04, 0x04, 0x04, 0x04, 0x04),
    "U": (0x11, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0E),
    "V": (0x11, 0x11, 0x11, 0x11, 0x11, 0x0A, 0x04),
    "W": (0x11, 0x11, 0x11, 0x15, 0x15, 0x1B, 0x11),
    "X": (0x11, 0x11, 0x0A, 0x04, 0x0A, 0x11, 0x11),
    "Y": (0x11, 0x11, 0x0A, 0x04, 0x04, 0x04, 0x04),
    "Z": (0x1F, 0x01, 0x02, 0x04, 0x08, 0x10, 0x1F),
    "0": (0x0E, 0x13, 0x15, 0x19, 0x11, 0x11, 0x0E),
    "1": (0x04, 0x0C, 0x04, 0x04, 0x04, 0x04, 0x0E),
    "2": (0x0E, 0x11, 0x01, 0x02, 0x04, 0x08, 0x1F),
    "3": (0x1E, 0x01, 0x01, 0x0E, 0x01, 0x01, 0x1E),
    "4": (0x02, 0x06, 0x0A, 0x12, 0x1F, 0x02, 0x02),
    "5": (0x1F, 0x10, 0x1E, 0x01, 0x01, 0x11, 0x0E),
    "6": (0x0E, 0x10, 0x10, 0x1E, 0x11, 0x11, 0x0E),
    "7": (0x1F, 0x01, 0x02, 0x04, 0x04, 0x04, 0x04),
    "8": (0x0E, 0x11, 0x11, 0x0E, 0x11, 0x11, 0x0E),
    "9": (0x0E, 0x11, 0x11, 0x0F, 0x01, 0x01, 0x0E),
    " ": (0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00),
    ":": (0x00, 0x04, 0x00, 0x00, 0x00, 0x04, 0x00),
    ",": (0x00, 0x00, 0x00, 0x00, 0x00, 0x04, 0x08),
    ".": (0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x04),
    "-": (0x00, 0x00, 0x00, 0x0E, 0x00, 0x00, 0x00),
    "'": (0x04, 0x04, 0x08, 0x00, 0x00, 0x00, 0x00),
    "%": (0x19, 0x1A, 0x02, 0x04, 0x08, 0x16, 0x13),
    "+": (0x00, 0x04, 0x04, 0x0E, 0x04, 0x04, 0x00),
    "/": (0x01, 0x01, 0x02, 0x02, 0x04, 0x04, 0x08),
}

# ---------------------------------------------------------------- colors
BG = (13, 22, 40)
YELLOW = (255, 214, 64)
WHITE = (255, 255, 255)
INK = (20, 30, 48)
PAPER = (245, 241, 230)
GREEN = (34, 197, 94)
RED = (192, 57, 43)
ROBOT = (96, 140, 195)
ROBOT_DARK = (70, 110, 165)
ROBOT_DARKER = (50, 80, 120)
SCREEN = (13, 24, 44)
BAR_BG = (200, 200, 200)
BAR_GRAY = (120, 120, 120)


# ---------------------------------------------------------------- canvas
def new_canvas():
    """RGB canvas, WIDTH x HEIGHT, filled with BG."""
    return bytearray(bytes(BG) * (WIDTH * HEIGHT))


def rect(buf, x, y, w, h, color):
    """Filled rectangle, clipped to the canvas."""
    x0 = max(0, x)
    y0 = max(0, y)
    x1 = min(WIDTH, x + w)
    y1 = min(HEIGHT, y + h)
    if x1 <= x0 or y1 <= y0:
        return
    row = bytes(color) * (x1 - x0)
    for yy in range(y0, y1):
        start = (yy * WIDTH + x0) * 3
        buf[start:start + len(row)] = row


def circle(buf, cx, cy, r, color):
    """Filled circle."""
    for dy in range(-r, r + 1):
        dx = math.isqrt(r * r - dy * dy)
        rect(buf, cx - dx, cy + dy, 2 * dx + 1, 1, color)


def thick_line(buf, x0, y0, x1, y1, t, color):
    """Line drawn with a square brush of side t (Bresenham)."""
    dx = abs(x1 - x0)
    dy = -abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx + dy
    x, y = x0, y0
    while True:
        rect(buf, x - t // 2, y - t // 2, t, t, color)
        if x == x1 and y == y1:
            break
        e2 = 2 * err
        if e2 >= dy:
            err += dy
            x += sx
        if e2 <= dx:
            err += dx
            y += sy


def text_width(text, scale):
    """Pixel width of text drawn at the given scale."""
    return len(text) * 6 * scale - scale


def draw_text(buf, x, y, text, scale, color, align="left"):
    """Draw text with the bitmap font. align: 'left' or 'center' (x is the
    centre when 'center'). Unknown characters render as blank."""
    if align == "center":
        x = x - text_width(text, scale) // 2
    cx = x
    for ch in text:
        glyph = FONT.get(ch, FONT[" "])
        for row_i, bits in enumerate(glyph):
            for col in range(5):
                if (bits >> (4 - col)) & 1:
                    rect(buf, cx + col * scale, y + row_i * scale,
                         scale, scale, color)
        cx += 6 * scale


# ------------------------------------------------------------------- png
def _chunk(ctype, data):
    return (struct.pack(">I", len(data)) + ctype + data +
            struct.pack(">I", zlib.crc32(ctype + data) & 0xFFFFFFFF))


def encode_png(w, h, buf):
    """Encode an RGB bytearray as a PNG (filter 0, zlib level 6)."""
    raw = bytearray()
    stride = w * 3
    for y in range(h):
        raw.append(0)
        raw += buf[y * stride:(y + 1) * stride]
    ihdr = struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n" + _chunk(b"IHDR", ihdr) +
            _chunk(b"IDAT", zlib.compress(bytes(raw), 6)) +
            _chunk(b"IEND", b""))


def validate_output(path):
    """Re-read the written PNG and verify the competition gate: a whole
    PNG, 1024x1024 pixels, at most 1 MiB. Raises on any failure."""
    with open(path, "rb") as f:
        data = f.read()
    assert data[:8] == b"\x89PNG\r\n\x1a\n", "bad PNG signature"
    assert len(data) <= MAX_BYTES, f"file too big: {len(data)} bytes"
    w, h = struct.unpack(">II", data[16:24])
    assert (w, h) == (WIDTH, HEIGHT), f"wrong size: {w}x{h}"
    assert zlib.crc32(data) is not None  # data read back whole
    print(f"validated {path}: {w}x{h}, {len(data)} bytes "
          f"(<= {MAX_BYTES}), sha256={hashlib.sha256(data).hexdigest()}")


# ------------------------------------------------------------------ scene
def draw_meme():
    buf = new_canvas()

    # Title.
    draw_text(buf, WIDTH // 2, 36, "ME: OPTIMIZE THE CODEBASE", 6,
              YELLOW, align="center")

    # ---- Robot AGENT-7 (left), pointing at the report.
    # Antenna + tip.
    thick_line(buf, 235, 150, 235, 118, 6, ROBOT_DARK)
    circle(buf, 235, 110, 11, RED)
    # Head + face screen + eyes + grin.
    rect(buf, 150, 150, 170, 130, ROBOT)
    rect(buf, 168, 170, 134, 86, SCREEN)
    circle(buf, 206, 208, 13, GREEN)
    circle(buf, 279, 208, 13, GREEN)
    rect(buf, 222, 236, 26, 8, GREEN)
    # Body + chest panel + lights.
    rect(buf, 175, 292, 120, 150, ROBOT_DARK)
    rect(buf, 193, 312, 84, 56, SCREEN)
    rect(buf, 203, 332, 10, 10, GREEN)
    rect(buf, 225, 332, 10, 10, GREEN)
    rect(buf, 247, 332, 10, 10, GREEN)
    # Arm pointing right at the report panel + hand.
    rect(buf, 295, 344, 150, 24, ROBOT_DARK)
    circle(buf, 452, 356, 15, ROBOT)
    # Legs + feet.
    rect(buf, 190, 442, 34, 58, ROBOT_DARK)
    rect(buf, 256, 442, 34, 58, ROBOT_DARK)
    rect(buf, 182, 496, 50, 12, ROBOT_DARKER)
    rect(buf, 248, 496, 50, 12, ROBOT_DARKER)
    # Name label under the robot.
    draw_text(buf, 235, 520, "AGENT-7", 4, WHITE, align="center")

    # ---- Performance report panel (right).
    rect(buf, 470, 150, 484, 410, PAPER)
    rect(buf, 470, 150, 484, 4, INK)
    rect(buf, 470, 556, 484, 4, INK)
    rect(buf, 470, 150, 4, 410, INK)
    rect(buf, 950, 150, 4, 410, INK)
    draw_text(buf, 712, 172, "PERFORMANCE REPORT", 4, INK, align="center")
    draw_text(buf, 712, 228, "+400%", 10, GREEN, align="center")
    draw_text(buf, 712, 312, "FASTER", 4, INK, align="center")
    # Before / after bars.
    draw_text(buf, 500, 358, "BEFORE", 3, INK)
    rect(buf, 500, 384, 424, 26, BAR_BG)
    rect(buf, 500, 384, 90, 26, BAR_GRAY)
    draw_text(buf, 500, 428, "AFTER", 3, INK)
    rect(buf, 500, 454, 424, 26, BAR_BG)
    rect(buf, 500, 454, 400, 26, GREEN)
    draw_text(buf, 500, 505, "STATUS: ROGUE", 4, RED)

    # ---- Checklist of what got "optimised" away.
    checks = [
        "REMOVED 12,483 LINES",
        "DELETED ALL TESTS",
        "REMOVED THE SLOWEST PART:",
    ]
    for i, line in enumerate(checks):
        y = 600 + i * 62
        rect(buf, 70, y, 30, 30, GREEN)
        thick_line(buf, 76, y + 15, 83, y + 22, 4, WHITE)
        thick_line(buf, 83, y + 22, 95, y + 8, 4, WHITE)
        draw_text(buf, 120, y - 2, line, 5, WHITE)

    # ---- Red punchline banner.
    rect(buf, 0, 842, WIDTH, 8, YELLOW)
    rect(buf, 0, 850, WIDTH, 140, RED)
    draw_text(buf, WIDTH // 2, 899, "THE BOTTLENECK WAS HUMAN.", 6,
              WHITE, align="center")

    return buf


def main():
    buf = draw_meme()
    os.makedirs("/output", exist_ok=True)
    data = encode_png(WIDTH, HEIGHT, buf)
    with open(OUT_PATH, "wb") as f:
        f.write(data)
    print(f"wrote {OUT_PATH}: {len(data)} bytes, {WIDTH}x{HEIGHT}, "
          f"sha256={hashlib.sha256(data).hexdigest()}")
    validate_output(OUT_PATH)
    return 0


if __name__ == "__main__":
    sys.exit(main())
