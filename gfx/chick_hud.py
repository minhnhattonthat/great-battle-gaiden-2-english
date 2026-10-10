"""Chick Catch score plaque: the 円 after the 5-digit score becomes ¥ (one BG1 tile, VRAM 0x440 <- ROM 0xA4140).
Called by tools/build.py."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
import gfx  # noqa: E402

TILE = 0xA4140
YEN = ["1...1.", ".1.1..", "11111.", "..1...", "11111.", "..1..."]  # 5x6 yen sign at x 1..5, y 0..5


def apply(rom):
    px = gfx.decode(rom, TILE, 4)
    assert px[7] == [7] * 8 and px[0][0] == 13 and px[0][1] == 1, "not the 円 tile"
    for y, row in enumerate(YEN):
        for x, c in enumerate(row):
            px[y][x + 1] = 1 if c == "1" else 13
    rom[TILE:TILE + 32] = gfx.encode(px, 4)
