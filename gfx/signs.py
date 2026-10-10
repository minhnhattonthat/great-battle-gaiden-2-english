"""Stall signs in the shared stall sheet (ROM 0x51000, 16 tiles = 128 px per row; text band = sheet rows y 42-49);
called by tools/build.py.

Each sign is 8 px of kanji/kana on a flat plate whose colour changes with the row (plate tiles are not touched
outside the text pixels). The Japanese ink (and the octopus on the takoyaki sign) is erased to the row's plate colour and
the English is drawn with the 5x7 pixel font in the ink colour. Only the three stalls of this sheet are covered here.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
import gfx  # noqa: E402
from gfxtext import FONT5x7  # noqa: E402

BASE = 0x51000
Y0, Y1 = 42, 49  # text band
NARROW_I = "111 010 010 010 010 010 111"
# name, x0, x1 (plate interior), ink colours to erase, ink colour, text, letter pitch
SIGNS = [("takoyaki", 1, 46, {8, 5, 0xE, 0xD}, 8, "TAKOYAKI", 6),
         ("corn", 49, 94, {8}, 8, "CORN", 10),   # pitch 10 = bold letters
         ("candy", 97, 127, {8}, 8, "CANDY", 6)]


def apply(rom):
    px = [[0] * 128 for _ in range(16)]  # sheet rows 5-6
    for r in (5, 6):
        for c in range(16):
            t = gfx.decode(rom, BASE + (r * 16 + c) * 32, 4)
            for y in range(8):
                px[(r - 5) * 8 + y][c * 8:c * 8 + 8] = t[y]
    top = 40
    for name, x0, x1, inks, ink, text, pitch in SIGNS:
        for y in range(Y0, Y1 + 1):
            row = px[y - top]
            bgs = [v for v in row[x0:x1 + 1] if v not in inks]
            bg = max(set(bgs), key=bgs.count)
            for x in range(x0, x1 + 1):
                if row[x] in inks:
                    row[x] = bg
        bold = pitch >= 10
        glyphs = [NARROW_I.split() if ch == "I" else FONT5x7[ch].split() for ch in text]
        widths = [len(g[0]) + bold for g in glyphs]
        gap = pitch - 5 - bold if pitch != 6 else 1
        total = sum(widths) + (len(text) - 1) * gap
        x = x0 + (x1 - x0 + 1 - total) // 2
        for g, w in zip(glyphs, widths):
            for dy, line in enumerate(g):
                for dx, bit in enumerate(line):
                    if bit == "1":
                        for b in range(1 + bold):
                            px[Y0 - top + dy][x + dx + b] = ink
            x += w + gap
    for r in (5, 6):
        for c in range(16):
            tile = [px[(r - 5) * 8 + y][c * 8:c * 8 + 8] for y in range(8)]
            o = BASE + (r * 16 + c) * 32
            rom[o:o + 32] = gfx.encode(tile, 4)
