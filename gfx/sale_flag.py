"""Winter boss's sale flag (大安売) in the boss sprite sheet at ROM 0xB8000 (4 bpp, 16 tiles per row); called by build.

The flag is drawn in several swinging poses, each pose using tiles of columns 12-14. The red ink (index 12, shading 9)
on the white cloth (index 2) is painted out to cloth white, leaving a plain flag. Only tiles that have both cloth and
red ink, and none of the orange (11) / bright red (15) body colours, are touched.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
import gfx  # noqa: E402

BASE, TILES = 0xB8000, 0x2000 // 32


def apply(rom):
    n = 0
    for t in (21, 193, 180, 166, 167):  # cloth tiles of the other poses (grey cloth with black outline)
        o = BASE + t * 32
        px = gfx.decode(rom, o, 4)
        for y in range(8):
            for x in range(8):
                if px[y][x] in (12, 9):
                    nb = [px[j][i] for j, i in ((y - 1, x), (y + 1, x), (y, x - 1), (y, x + 1))
                          if 0 <= i < 8 and 0 <= j < 8 and px[j][i] not in (12, 9, 0, 1)]
                    px[y][x] = max(set(nb), key=nb.count) if nb else 3
        rom[o:o + 32] = gfx.encode(px, 4)
    for t in range(TILES):
        if t % 16 not in (11, 12, 13, 14):
            continue
        o = BASE + t * 32
        px = gfx.decode(rom, o, 4)
        flat = [p for r in px for p in r]
        cloth = flat.count(2) + flat.count(3)
        if 12 in flat and cloth >= 4 and 15 not in flat and not {5, 6, 7} & set(flat):  # 5-7: armour greys
            fill = 2 if flat.count(2) >= flat.count(3) else 3
            rom[o:o + 32] = gfx.encode([[fill if p in (12, 9) else p for p in r] for r in px], 4)
            n += 1
        elif 9 in flat and cloth >= 8 and not {1, 6, 7, 8, 13, 14, 15} & set(flat):  # pure cloth tile, dark ink left
            fill = 2 if flat.count(2) >= flat.count(3) else 3
            rom[o:o + 32] = gfx.encode([[fill if p in (9, 12) else p for p in r] for r in px], 4)
        elif 12 in flat and 15 not in flat:  # mixed tiles: stray ink -> its neighbours' colour
            for y in range(8):
                for x in range(8):
                    if px[y][x] == 12:
                        nb = [px[j][i] for j, i in ((y - 1, x), (y + 1, x), (y, x - 1), (y, x + 1))
                              if 0 <= i < 8 and 0 <= j < 8 and px[j][i] not in (12, 9, 0)]
                        px[y][x] = max(set(nb), key=nb.count) if nb else 0
            rom[o:o + 32] = gfx.encode(px, 4)
    assert n >= 6, n
