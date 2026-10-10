"""Shooting-game power-up shop texts (BG3 font words); called by tools/build.py after asar.

Card names: the routine at $19:83BD copies a blob of tilemap records (first record's VRAM/count read separately, the
rest copied raw: LDA #$1C words). The English blob lives at $3F:9300 with wider names (8 tiles for the first three, 6
for Shield) and the three long LDA operands + the word count are repointed. "のこりおこづかい" is the 8-word string
at $19:87F4 (digits follow it): replaced in place. The sold-out writer is in asm/main.asm.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
from build import EN_CHARS  # noqa: E402

CODE = {c: b for c, b in EN_CHARS}
BLOB = 0x1F9300  # $3F:9300
LOOP_COUNT, LONG_READS = 0xC83C0, (0xC83C5, 0xC83CC, 0xC83D8)  # LDA #$001C; LDA $07F384,x
REMAIN = 0xC87F4


def words(text):
    return [0x2000 | CODE[c] for c in text]


def apply(rom):
    blob = ([0x5844, 8] + words("Rapid UP") + [8, 0x5850] + words("Speed UP") + [8, 0x5984] + words("Power UP")
            + [6, 0x5991] + words("Shield"))
    assert rom[LOOP_COUNT:LOOP_COUNT + 3] == bytes([0xA9, 0x1C, 0x00]), "card name loop moved"
    rom[LOOP_COUNT + 1:LOOP_COUNT + 3] = (len(blob) - 2).to_bytes(2, "little")
    for a in LONG_READS:
        assert rom[a:a + 4] == bytes([0xBF, 0x84, 0xF3, 0x07]), hex(a)
        rom[a + 1:a + 4] = bytes([0x00, 0x93, 0x3F])
    data = b"".join(w.to_bytes(2, "little") for w in blob)
    assert set(rom[BLOB:BLOB + len(data)]) == {0xFF}, "shop blob area not free"
    rom[BLOB:BLOB + len(data)] = data
    assert rom[REMAIN:REMAIN + 4] == bytes([0xB8, 0x20, 0xA9, 0x20]), "のこりおこづかい moved"
    rom[REMAIN:REMAIN + 16] = b"".join(w.to_bytes(2, "little") for w in words("Money:  "))
