"""Password screen texts (BG3 font words written by copy loops in bank $21); called by tools/build.py.

Each loop: LDA #count / LDY #vram / JSL $00FF57 / ... / LDA $00Bxxx,x (long source) / ... / CPX #2*count.
English strings (tilemap words, attr $20 like the original) go to bank $3F; loops are repointed and resized, and
the JP dakuten rows / single ゛゜ writes are blanked. Rows: 15 = prompt line, 18-26 = controls list (moved to
column 3 so the descriptions clear Emmy's sprite on the right).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
from build import EN_CHARS  # noqa: E402

DATA = 0x1F9000  # $3F:9000
CODE = {c: b for c, b in EN_CHARS}


def off(a):
    return ((a & 0x7F0000) >> 1) | (a & 0x7FFF)


def words(text, attr=0x2000, icon=None):
    out = [icon] if icon is not None else []
    return out + [attr | CODE[c] for c in text]


# (loop, layout, vram, words); layout "AY" = LDA #n first, "YA" = LDY first (the B84C loop)
STRINGS = [
    (0x21E828, "AY", 0x59E7, words("Password")),
    (0x21EA24, "AY", 0x59EF, words(", please! ")),
    (0x21ECC4, "AY", 0x59EF, words(" is wrong!")),
    (0x21EEF9, "YA", 0x59E3, words("Write down your password!")),
    (0x21E8B5, "AY", 0x5A43, words("Pad    Move cursor", icon=0x2455)),
    (0x21E8DA, "AY", 0x5A83, words("Button Pick letter", icon=0x2C56)),
    (0x21E8FF, "AY", 0x5AC3, words("Button Erase letter", icon=0x2856)),
    (0x21E924, "AY", 0x5B03, words("Start  Confirm", icon=0x2457)),
    (0x21E949, "AY", 0x5B43, words("Select Menu screen", icon=0x2457)),
    (0x21EA49, "AY", 0x59CE, [0] * 6),   # dakuten row over the prompt
    (0x21ECE9, "AY", 0x59CE, [0] * 6),
]
DAKUTEN_IMM = [0x21E859, 0x21E873, 0x21E97A, 0x21E994, 0x21E9AE, 0x21E9C8, 0x21E9E2, 0x21E9FC, 0x21EA16,
               0x21EEBB, 0x21EED3, 0x21EEEB]  # LDA #$2098/#$2099 -> blank


def apply(rom):
    pos = DATA
    for loop, layout, vram, ws in STRINGS:
        p = off(loop)
        if layout == "AY":
            assert rom[p] == 0xA9 and rom[p + 3] == 0xA0 and rom[p + 15] == 0xBF and rom[p + 26] == 0xE0, hex(loop)
            n_at, v_at, s_at, c_at = p + 1, p + 4, p + 16, p + 27
        else:
            assert rom[p] == 0xA0 and rom[p + 3] == 0xA9 and rom[p + 13] == 0xBF and rom[p + 24] == 0xE0, hex(loop)
            n_at, v_at, s_at, c_at = p + 4, p + 1, p + 14, p + 25
        data = b"".join(w.to_bytes(2, "little") for w in ws)
        rom[pos:pos + len(data)] = data
        src = 0x3F0000 | 0x8000 | (pos & 0x7FFF)
        rom[n_at:n_at + 2] = len(ws).to_bytes(2, "little")
        rom[v_at:v_at + 2] = vram.to_bytes(2, "little")
        rom[s_at:s_at + 3] = src.to_bytes(3, "little")
        rom[c_at:c_at + 2] = (2 * len(ws)).to_bytes(2, "little")
        pos += len(data)
    for a in DAKUTEN_IMM:
        p = off(a)
        assert rom[p] == 0xA9 and rom[p + 1] in (0x98, 0x99) and rom[p + 2] == 0x20, hex(a)
        rom[p + 1] = 0x00
