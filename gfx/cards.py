"""Attract copyright cards (BG3 text from tilemap record groups in bank $21, tiles in the 0x100+ chr block); called
by tools/build.py.

Each card is a group of records [count, VRAM word, entries...] ended by a 0 count, reached through the pointer table at
$21:BC30. The Japanese text is 16 px kanji drawn from custom tiles; the English uses the ordinary BG3 font tiles (8 px,
same palette 0 = yellow face / black shadow) on rows 14-15 (the cleared band) and ends the group early. © is font tile
$9F (font/extra.txt). The BANPRESTO 1994 card is already Latin and stays.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
from build import EN_CHARS  # noqa: E402

CODE = {c: b for c, b in EN_CHARS}
CODE["©"] = 0x9F


def off(a):
    return ((a & 0x7F0000) >> 1) | (a & 0x7FFF)


def rec(row, col, text):
    return [len(text), 0x5800 + row * 32 + col] + [0x2000 | CODE[c] for c in text]


RIDER = [("© Ishimori Pro/Toei", 14, 10), ("(Kamen Rider Club)", 15, 12)]
ULTRA = [("© Tsuburaya Pro", 14, 12)]
GUNDAM = [("© Sotsu Agency /", 14, 12), ("Sunrise", 15, 14)]

# (group address, first words that must match, records)
CARDS = [
    (0x21CC34, [0x000C, 0x59CC, 0x2100], RIDER),
    (0x21CC0A, [0x0008, 0x59CE, 0x2100], ULTRA),
    (0x21CBB0, [0x0014, 0x59CA, 0x2100], GUNDAM),  # 0x21CB66 is the BANPRESTO 1994 card: already Latin
]
# all-licences page: rider rows 16 and 18, ultra 20, Sotsu/Sunrise 22-23, Banpresto (rows 24-25, already Latin) kept
LIST = [("© Ishimori Pro/Toei", 16, 8), ("(Kamen Rider Club)", 18, 8), ("© Tsuburaya Pro", 20, 8),
        ("© Sotsu Agency /", 22, 8), ("Sunrise", 23, 10)]


def words_at(rom, p, n):
    return [rom[p + 2 * i] | rom[p + 2 * i + 1] << 8 for i in range(n)]


def put(rom, p, ws, room):
    assert len(ws) <= room, f"{len(ws)} words > {room} at {p:X}"
    rom[p:p + 2 * len(ws)] = b"".join(w.to_bytes(2, "little") for w in ws)


def apply(rom):
    for addr, head, items in CARDS:
        p = off(addr)
        assert words_at(rom, p, 3) == head, hex(addr)
        n = 0
        while words_at(rom, p + 2 * n, 1)[0]:  # old group length in words, terminator included
            n += 2 + words_at(rom, p + 2 * n, 1)[0]
        ws = [w for t, r, c in items for w in rec(r, c, t)] + [0]
        put(rom, p, ws, n + 1)
    # combined list: ten records; keep the two Banpresto records (rows 22-23) as they are
    p = off(0x21CA08)
    assert words_at(rom, p, 3) == [0x000C, 0x5A08, 0x2100]
    banp = [p + 0xF8, p + 0x11C]  # records 9 and 10 start at 0x10CB00 / 0x10CB24
    assert words_at(rom, banp[0], 2) == [16, 0x5B08] and words_at(rom, banp[1], 2) == [16, 0x5B28]
    keep = [words_at(rom, a, 18) for a in banp]
    head = [w for t, r, c in LIST for w in rec(r, c, t)]
    ws = head + keep[0] + keep[1] + [0]
    put(rom, p, ws, (0x10CB48 - 0x10CA08) // 2 + 1)
