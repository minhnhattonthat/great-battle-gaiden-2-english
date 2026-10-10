"""Stage banner (春のお祭り etc.): sprite glyphs in one 4bpp sheet at ROM 0x36400 (16 tiles = 128 px per row),
redrawn in place; called by tools/build.py.

The game shows [season][の][お][祭][り] as five 32x32 sprites, picking the sheet window per season, so each glyph
is replaced inside its own bounding box: seasons -> condensed SPRING / SUMMER / AUTUMN / WINTER, and the four
phrase glyphs -> FE / ST / IV / AL ("... FESTIVAL"). Outline index 6; fill = the glyph's two main indices (upper
/ lower half). Only spring (stage 1) has been seen in game.
"""
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
import gfx  # noqa: E402

BASE, ROWS = 0x36400, 9          # sheet rows of 16 tiles
FONT = "C:/Windows/Fonts/impact.ttf"
EDGE = 6
SEASONS = {"WINTER", "SPRING", "SUMMER", "AUTUMN"}
# (erase x0, x1, y0, y1), (draw y0, y1), English. Spring shows sheet rows 0-3 (season) and rows 4-7 (の お 祭; り
# wraps in from rows 5-8 of columns 0-3), so the words share a baseline at sprite row 31. Rows 8+ of columns 4-15
# hold other sprites: never touch them.
GLYPHS = [((0, 32, 8, 40), (13, 32), "WINTER"), ((32, 64, 0, 32), (13, 32), "SPRING"),
          ((64, 96, 0, 40), (13, 32), "SUMMER"), ((96, 128, 0, 40), (13, 32), "AUTUMN"),
          ((32, 64, 40, 64), (41, 64), "FE"), ((64, 96, 40, 64), (41, 64), "ST"), ((96, 128, 40, 64), (41, 64), "IV"),
          ((0, 32, 40, 72), (49, 72), "AL")]


def sheet(rom):
    px = [[0] * 128 for _ in range(ROWS * 8)]
    for t in range(ROWS * 16):
        tile = gfx.decode(rom, BASE + t * 32, 4)
        for y in range(8):
            for x in range(8):
                px[(t // 16) * 8 + y][(t % 16) * 8 + x] = tile[y][x]
    return px


def unsheet(rom, px):
    for t in range(ROWS * 16):
        tile = [px[(t // 16) * 8 + y][(t % 16) * 8:(t % 16) * 8 + 8] for y in range(8)]
        rom[BASE + t * 32:BASE + t * 32 + 32] = gfx.encode(tile, 4)


def text_mask(text, w, h):
    font = ImageFont.truetype(FONT, 40)
    l, t, r, b = font.getbbox(text)
    m = Image.new("1", (r - l, b - t))
    ImageDraw.Draw(m).text((-l, -t), text, font=font, fill=1)
    return m.resize((w, h), Image.NEAREST)


def apply(rom):
    px = sheet(rom)
    for (x0, x1, y0, y1), (dy0, dy1), word in GLYPHS:
        pts = [(x, y) for y in range(y0, y1) for x in range(x0, x1) if px[y][x]]
        counts = {}
        for x, y in pts:
            if px[y][x] != EDGE:
                counts[px[y][x]] = counts.get(px[y][x], 0) + 1
        main = sorted(counts, key=counts.get, reverse=True)
        top2 = main[:2] if len(main) > 1 and counts[main[1]] * 4 >= counts[main[0]] else main[:1]
        fills = sorted(top2, key=lambda i: sum(y for x, y in pts if px[y][x] == i) / counts[i])  # top to bottom
        if word == "FE":
            fills = [2]  # の was dark green; FESTIVAL reads as one word in red (index 2, as お 祭 り)
        for x, y in pts:
            px[y][x] = 0
        if word in SEASONS:  # six letters do not fit one 32 px sprite: two lines of three over the visible window
            rows = [(word[:3], y0 + 1, y0 + 15), (word[3:], y0 + 17, y0 + 31)]
            top, hh = y0 + 1, 30
        else:
            rows = [(word, dy0 + 1, dy1 - 1)]
            top, hh = dy0 + 1, dy1 - dy0 - 2
        body = set()
        for txt, ry0, ry1 in rows:
            w, h = x1 - x0 - 2, ry1 - ry0
            m = text_mask(txt, w, h)
            body |= {(x0 + 1 + x, ry0 + y) for y in range(h) for x in range(w) if m.getpixel((x, y))}
        for x, y in body:
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    if (x + dx, y + dy) not in body:
                        px[y + dy][x + dx] = EDGE
        for x, y in body:
            px[y][x] = fills[min(len(fills) - 1, (y - top) * len(fills) // hh)]
    unsheet(rom, px)
