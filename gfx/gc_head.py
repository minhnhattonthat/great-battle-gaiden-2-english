"""Game corner header げーむこーなー -> GAME CORNER (BG1, 16x16 tiles); called by tools/build.py.

Chr: VRAM X <- ROM 0xA8980 + X (raw). The header is two 16-entry tilemap records (rows 2-3) in the bank $21
stream at 0x10D38C / 0x10D3B0. The three ー bars reuse one tile pair, so the 8 unique glyph columns are moved to
the centre (cols 4-11) to hold the English, and the ー tiles become plain curtain for the sides. Glyph pixels
(palette 1 indices 1, 2, 7, 14) are erased with each row's most common curtain colour.
"""
from PIL import Image, ImageDraw, ImageFont

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
import gfx  # noqa: E402

CHR = 0xA8980
REC = [(0x10D38C, 0x5040), (0x10D3B0, 0x5060)]
TOP = [0x6404, 0x2422, 0x2424, 0x2422, 0x240A, 0x240C, 0x242A, 0x242C, 0x2442, 0x2444, 0x244A, 0x244C, 0x2424, 0x2422,
       0x2424, 0x2404]
BOT = [0x2408, 0x2426, 0x2428, 0x2426, 0x240E, 0x2420, 0x242E, 0x2440, 0x2446, 0x2448, 0x244E, 0x2460, 0x2428, 0x2426,
       0x2428, 0x2406]
GLYPH = {1, 2, 7, 14}
WHITE, BLACK, SHADE = 2, 1, 14


def get(rom, n):
    px = [[0] * 16 for _ in range(16)]
    for sy in range(2):
        for sx in range(2):
            t = gfx.decode(rom, CHR + (n + sx + 16 * sy) * 32, 4)
            for y in range(8):
                for x in range(8):
                    px[sy * 8 + y][sx * 8 + x] = t[y][x]
    return px


def put(rom, n, px):
    for sy in range(2):
        for sx in range(2):
            o = CHR + (n + sx + 16 * sy) * 32
            rom[o:o + 32] = gfx.encode([row[sx * 8:sx * 8 + 8] for row in px[sy * 8:sy * 8 + 8]], 4)


def apply(rom):
    for (o, vram), row in zip(REC, (TOP, BOT)):
        assert rom[o:o + 4] == (16).to_bytes(2, "little") + vram.to_bytes(2, "little"), hex(o)
        rom[o + 4:o + 36] = b"".join(e.to_bytes(2, "little") for e in row)
    # strip of cols 1-14 in the new layout, 224 x 32
    cols = list(range(1, 15))
    strip = [[0] * (16 * len(cols)) for _ in range(32)]
    for i, c in enumerate(cols):
        for r, row in enumerate((TOP, BOT)):
            t = get(rom, row[c] & 0x3FF)
            for y in range(16):
                strip[r * 16 + y][i * 16:i * 16 + 16] = t[y]
    for y in range(32):  # erase: the row's most common curtain colour (copying down smeared fold highlights)
        glyph = GLYPH | ({3, 4, 15} if y < 26 else set())  # orange glyph shading; rows 26+ are the orange fringe
        bg = [i for i in strip[y] if i not in glyph]
        fill = max(set(bg), key=bg.count) if bg else 5
        strip[y] = [fill if i in glyph else i for i in strip[y]]
    # GAME CORNER over cols 4-11 (strip x 48-175)
    font = ImageFont.truetype("C:/Windows/Fonts/ariblk.ttf", 30)
    l, t, r, b = font.getbbox("GAME CORNER")
    m = Image.new("1", (r - l, b - t))
    ImageDraw.Draw(m).text((-l, -t), "GAME CORNER", font=font, fill=1)
    m = m.resize((122, 20), Image.NEAREST)
    ox, oy = 48 + 3, 6
    body = {(ox + x, oy + y) for y in range(m.height) for x in range(m.width) if m.getpixel((x, y))}
    for x, y in body:
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if (x + dx, y + dy) not in body:
                    strip[y + dy][x + dx] = BLACK
    for x, y in body:
        strip[y][x] = WHITE if y < oy + 13 else SHADE
    done = set()
    for i, c in enumerate(cols):
        for r, row in enumerate((TOP, BOT)):
            n = row[c] & 0x3FF
            if n in done:
                continue
            done.add(n)
            put(rom, n, [strip[r * 16 + y][i * 16:i * 16 + 16] for y in range(16)])
