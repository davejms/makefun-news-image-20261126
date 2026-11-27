#!/usr/bin/env python3
"""Sum up 26 November 2026 world news in one image.

Entry for the make.fun bounty "Sum up 26 November's world news in
one image" (news-image-20261126).

Run:  python3 main.py

Writes ./.makefun/output/output.png -- one 1024x1024 PNG, at most
1 MiB, built deterministically from the news items embedded below.
Standard library only. No network access, no randomness, no clocks:
running the program twice produces byte-identical output.

Sources (26 November 2026): Al Jazeera, The Guardian, UN News,
Euronews, PBS NewsHour.
"""

import os
import struct
import sys
import zlib

WIDTH = 1024
HEIGHT = 1024
OUT_DIR = os.path.join(".makefun", "output")
OUT_FILE = os.path.join(OUT_DIR, "output.png")

PAPER = (253, 252, 247)
INK = (20, 20, 20)
GREY = (90, 88, 80)
CARD = (255, 255, 255)
BORDER = (216, 210, 196)
RED = (180, 35, 24)
WHITE = (255, 255, 255)

# 5x7 bitmap font. Each glyph is 7 rows of 5 characters, "1" = ink.
FONT = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    "D": ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    "J": ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "Q": ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "V": ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    "W": ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    "X": ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    "Y": ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    "3": ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    "6": ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    ".": ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ",": ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    "-": ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    ":": ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    "(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ")": ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    "%": ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    "+": ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
    "/": ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    "&": ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    "?": ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
}

# (kicker, accent colour, headline, body) -- all verified from the
# sources listed above, for Thursday 26 November 2026.
STORIES = [
    ("MIDDLE EAST", (180, 35, 24),
     "DRONES HIT KUWAIT, TWO KILLED",
     "IRANIAN DRONES HIT A VITAL SITE IN KUWAIT. TWO ITALIAN "
     "WORKERS WERE KILLED AND FOUR INJURED."),
    ("GAZA", (29, 78, 216),
     "16 SCHOOLCHILDREN KILLED IN GAZA",
     "GAZA'S EDUCATION MINISTRY SAID ISRAELI STRIKES HAVE KILLED "
     "AT LEAST 16 SCHOOLCHILDREN IN NOVEMBER."),
    ("UKRAINE", (176, 110, 0),
     "RUSSIA HITS UKRAINE ENERGY SITES",
     "RUSSIAN DRONE STRIKES HIT UKRAINIAN REGIONS AND ENERGY "
     "FACILITIES AS EU LEADERS MET TO TALK ABOUT SUPPORT."),
    ("GLOBAL ECONOMY", (13, 120, 110),
     "WORLD SHIPPING SET TO STALL IN 2026",
     "THE UN TRADE BODY UNCTAD SAID CONTAINER SHIPPING VOLUMES "
     "WILL NOT GROW IN 2026, WHILE COSTS KEEP RISING."),
    ("EGYPT", (194, 65, 12),
     "CAIRO TANKER FIRE KILLS AT LEAST 31",
     "A FUEL TANKER OVERTURNED AND CAUGHT FIRE ON A HIGHWAY NEAR "
     "CAIRO, KILLING AT LEAST 31 PEOPLE AND INJURING 25."),
    ("THAILAND", (109, 40, 217),
     "FIRE AT BANGKOK OIL DEPOT",
     "A MAJOR FIRE BROKE OUT AT AN OIL DEPOT IN BANGKOK. A VESSEL "
     "CARRYING 7,000 TONNES OF DIESEL ALSO SANK."),
    ("HEALTH", (21, 128, 61),
     "EBOLA CASES PASS 12,000 IN DR CONGO",
     "THE UN SAID EBOLA CASES IN THE DEMOCRATIC REPUBLIC OF CONGO "
     "HAVE PASSED 12,000 AS THE OUTBREAK CONTINUES."),
    ("UNITED STATES", (51, 65, 85),
     "STORMY THANKSGIVING IN NORTH AMERICA",
     "STORMS AND HIGH TIDES BATTERED THE EAST AND WEST COASTS, "
     "CAUSING DELAYS AND DAMAGE ON THANKSGIVING DAY."),
]


def fill_rect(buf, x, y, w, h, color):
    """Fill a rectangle in the RGB canvas buffer."""
    if w <= 0 or h <= 0:
        return
    row = bytes(color) * w
    for yy in range(y, y + h):
        start = (yy * WIDTH + x) * 3
        buf[start:start + w * 3] = row


def draw_glyph(buf, x, y, glyph, scale, color):
    for r, bits in enumerate(glyph):
        for c, bit in enumerate(bits):
            if bit == "1":
                fill_rect(buf, x + c * scale, y + r * scale,
                          scale, scale, color)


def text_width(text, scale):
    if not text:
        return 0
    return (len(text) * 6 - 1) * scale


def draw_text(buf, x, y, text, scale, color):
    cx = x
    for ch in text:
        if ch == " ":
            cx += 6 * scale
            continue
        glyph = FONT.get(ch)
        if glyph is not None:
            draw_glyph(buf, cx, y, glyph, scale, color)
        cx += 6 * scale


def wrap(text, max_width, scale):
    lines = []
    cur = ""
    for word in text.split(" "):
        trial = word if not cur else cur + " " + word
        if text_width(trial, scale) <= max_width or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_card(buf, x, y, w, h, kicker, color, headline, body):
    fill_rect(buf, x, y, w, h, CARD)
    fill_rect(buf, x, y, w, 1, BORDER)
    fill_rect(buf, x, y + h - 1, w, 1, BORDER)
    fill_rect(buf, x, y, 1, h, BORDER)
    fill_rect(buf, x + w - 1, y, 1, h, BORDER)
    fill_rect(buf, x, y, 10, h, color)
    chip_w = text_width(kicker, 2) + 16
    fill_rect(buf, x + 22, y + 14, chip_w, 24, color)
    draw_text(buf, x + 30, y + 19, kicker, 2, WHITE)
    hy = y + 48
    for i, line in enumerate(wrap(headline, 440, 3)[:2]):
        draw_text(buf, x + 22, hy + i * 25, line, 3, INK)
    by = y + 106
    for i, line in enumerate(wrap(body, 440, 2)[:4]):
        draw_text(buf, x + 22, by + i * 18, line, 2, INK)


def build():
    buf = bytearray(PAPER) * (WIDTH * HEIGHT)
    # Masthead.
    draw_text(buf, 262, 22, "THE WORLD IN ONE PAGE", 4, INK)
    draw_text(buf, 345, 62, "THURSDAY, 26 NOVEMBER 2026", 2, GREY)
    fill_rect(buf, 24, 100, 976, 4, RED)
    # Eight stories, two columns by four rows.
    cell_w, cell_h = 478, 196
    for i, story in enumerate(STORIES):
        col = i % 2
        row = i // 2
        x = 24 + col * (cell_w + 20)
        y = 118 + row * (cell_h + 14)
        draw_card(buf, x, y, cell_w, cell_h, *story)
    # Footer.
    draw_text(buf, 24, 958,
              "SOURCES: AL JAZEERA, THE GUARDIAN, UN NEWS, EURONEWS, "
              "PBS NEWSHOUR.", 2, GREY)
    draw_text(buf, 24, 982, "ALL EVENTS TOOK PLACE ON 26 NOVEMBER 2026.",
              2, GREY)
    return buf


def _chunk(kind, data):
    return (struct.pack(">I", len(data)) + kind + data +
            struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF))


def write_png(path, buf, width, height):
    raw = bytearray()
    stride = width * 3
    for y in range(height):
        raw.append(0)  # filter: none
        raw += buf[y * stride:(y + 1) * stride]
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    png = b"\x89PNG\r\n\x1a\n"
    png += _chunk(b"IHDR", ihdr)
    png += _chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += _chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)
    return len(png)


def main():
    buf = build()
    os.makedirs(OUT_DIR, exist_ok=True)
    size = write_png(OUT_FILE, buf, WIDTH, HEIGHT)
    print("Wrote %s (%d bytes)" % (OUT_FILE, size))
    if size > 1000000:
        print("WARNING: output is larger than 1 MiB", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
