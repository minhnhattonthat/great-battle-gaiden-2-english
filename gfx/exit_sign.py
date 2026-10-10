"""Stage select / shop EXIT sign: the 出口 plate (32x32 px, BG1 palette 5) becomes EXIT; called by tools/build.py.

The plate is 16 tiles (4 bpp) at VRAM bytes TILES (row-major), ROM = VRAM + 0x2B000. Interior colour 11, glyphs are a grey
-> white -> grey gradient with a dark-navy (12) shadow to the lower right.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
import gfx  # noqa: E402
import gfxtext  # noqa: E402

TILES = [0x140, 0x160, 0x180, 0x1A0, 0x340, 0x360, 0x380, 0x3A0, 0x1C0, 0x1E0, 0x400, 0x420, 0x3C0, 0x3E0, 0x600, 0x620]
ROM_OFF = 0x2B000
GRAD = [9, 8, 13, 6, 5, 2, 2, 2, 2, 5, 6, 13, 8, 9]
INNER, SHADOW = 11, 12


def apply(rom):
    px = [[0] * 32 for _ in range(32)]
    for i, a in enumerate(TILES):
        t = gfx.decode(rom, ROM_OFF + a, 4)
        for y in range(8):
            px[i // 4 * 8 + y][i % 4 * 8:i % 4 * 8 + 8] = t[y]
    assert px[3][2] == INNER and px[15][5] == SHADOW, "not the 出口 plate"
    for y in range(3, 29):  # wipe the interior
        for x in range(2, 30):
            px[y][x] = INNER
    _, _, body = gfxtext.word_mask("EXIT", 16, 6, sy=2, bold=True)
    ox, oy = 3, 8  # body coords start at 1: glyph box x 4..27, y 9..22
    for x, y in body:
        px[oy + y][ox + x] = GRAD[y - 1]
    for x, y in body:  # shadow right / below
        for dx, dy in ((1, 0), (0, 1), (1, 1)):
            q = (x + dx, y + dy)
            if q not in body and px[oy + q[1]][ox + q[0]] == INNER:
                px[oy + q[1]][ox + q[0]] = SHADOW
    for i, a in enumerate(TILES):
        cell = [row[i % 4 * 8:i % 4 * 8 + 8] for row in px[i // 4 * 8:i // 4 * 8 + 8]]
        rom[ROM_OFF + a:ROM_OFF + a + 32] = gfx.encode(cell, 4)
