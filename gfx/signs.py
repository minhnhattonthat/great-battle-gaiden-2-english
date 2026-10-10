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


BRIDGE_TILES = 0x904C0  # autumn bridge: "はしのうえ" board, 4 tiles (32 px) wide, text rows 2-7, ink f on plate 2
SMALL = {"B": "1110 1001 1110 1001 1001 1110", "R": "1110 1001 1110 1010 1001 1001", "I": "111 010 010 010 010 111",
         "D": "1110 1001 1001 1001 1001 1110", "G": "0111 1000 1011 1001 1001 0111", "E": "1111 1000 1110 1000 1000 1111"}


def bridge(rom):
    px = [[0] * 32 for _ in range(8)]
    for i in range(4):
        t = gfx.decode(rom, BRIDGE_TILES + i * 32, 4)
        for y in range(8):
            px[y][i * 8:i * 8 + 8] = t[y]
    assert px[3][4] == 0xF and px[1][1] == 2, "not the bridge board"
    for y in range(1, 8):
        for x in range(1, 31):
            px[y][x] = 2
    x = 2
    for ch in "BRIDGE":
        g = SMALL[ch].split()
        for dy, line in enumerate(g):
            for dx, bit in enumerate(line):
                if bit == "1":
                    px[2 + dy][x + dx] = 0xF
        x += len(g[0]) + 1
    for i in range(4):
        rom[BRIDGE_TILES + i * 32:BRIDGE_TILES + i * 32 + 32] = gfx.encode([r[i * 8:i * 8 + 8] for r in px], 4)


def apply(rom):
    bridge(rom)
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
