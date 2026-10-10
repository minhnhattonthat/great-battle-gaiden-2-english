"""Minigame "GAME CLEAR" / "GAME OVER" banner (げーむくりあー / げーむおーばー); called by tools/build.py.

BG3 tiles 0x124-0x135 (2 bpp, palette 1: 1 outline, 2 fill, 3 shade; ROM 0xA8590 + (tile - 0x101) * 16) now hold nine
8x16 letters (top tile, bottom tile) and the three tilemap copies (shooting, block break, chick/other: two 14-tile
variants each, 28 words per variant, A = clear, B = over) are rewritten in place to spell the words with them.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
import gfx  # noqa: E402
import gfxtext  # noqa: E402

CHR = 0xA8590 - 0x101 * 16
LETTERS = "GAMECLROV"
FIRST = 0x124
BLOCKS = [0xABB9D, 0xB27E3, 0xCDA04]  # row 1 of variant A; B follows 28 words later
WORDS_A, WORDS_B = "GAME CLEAR", "GAME OVER"
BLANK = 0x2500


def letter_tiles(ch):
    _, _, body = gfxtext.word_mask(ch, 16, 8, sy=2, bold=True)
    px = [[0] * 8 for _ in range(16)]
    for x, y in body:
        px[y][x] = 3 if y >= 8 else 2
    for x, y in body:
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                qx, qy = x + dx, y + dy
                if (qx, qy) not in body and 0 <= qx < 8 and 0 <= qy < 16:
                    px[qy][qx] = 1
    return px[:8], px[8:]


def rows(word):
    cells = [None] * 2 + [c if c != " " else None for c in word] + [None] * (14 - 2 - len(word))
    top = [BLANK if c is None else 0x2500 | FIRST + 2 * LETTERS.index(c) for c in cells]
    bot = [BLANK if c is None else 0x2500 | FIRST + 2 * LETTERS.index(c) + 1 for c in cells]
    return top, bot


def apply(rom):
    for i, ch in enumerate(LETTERS):
        for k, t in enumerate(letter_tiles(ch)):
            o = CHR + (FIRST + 2 * i + k) * 16
            rom[o:o + 16] = gfx.encode(t, 2)
    new = [w for word in (WORDS_A, WORDS_B) for r in rows(word) for w in r]
    for a in BLOCKS:
        old = [rom[a + 2 * i] | rom[a + 2 * i + 1] << 8 for i in range(56)]
        assert old[:3] == [0x2500, 0x2524, 0x2526] and old[38:41] == [0x2535, 0x2537, 0x2539], hex(a)
        rom[a:a + 112] = b"".join(w.to_bytes(2, "little") for w in new)
