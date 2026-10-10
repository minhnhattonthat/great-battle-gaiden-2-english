"""Ending staff roll (BG3 text, message-font bytes, FF-terminated lines); called by tools/build.py.

The roll is a table of 85 line pointers at $01:C30C (0-terminated; lines may repeat) into strings at $01:C3B8-$01:C675.
The table keeps its order; the strings are repacked in place with English (roles flush left, names indented two
tiles: three, as in the Japanese, does not fit; bank $01 has no free space). The four © lines and
(KAMEN RIDER CLUB) are already Latin and are copied unchanged. "Design Work" points into "Game Design Work".
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
from build import EN_CHARS  # noqa: E402

CODE = {c: b for c, b in EN_CHARS}
TABLE, START, END = 0xC30C, 0xC3B8, 0xC676   # file offsets (bank $01: file = CPU address)
N = "  "
EN = {
    0xC3B8: "Game Design Work", 0xC3C6: N + "Datte Yasuda", 0xC3D3: N + "Software Team",
    0xC3EE: N + "SUGAR BEET", 0xC3FC: N + '"Hakase"', 0xC405: N + "MIURA SHINTARO", 0xC417: N + '"Fumiuo"',
    0xC421: N + "BUG BUG", 0xC42C: "System Program", 0xC438: "Main Program", 0xC443: "Minigame Program",
    0xC451: "Boss Stage Program", 0xC461: "OP/ED Program", 0xC46E: "Graphic Design",
    0xC47C: N + "Koakuma Terashima", 0xC489: N + 'Cannon "Yumoyumo"', 0xC497: N + "Itahana Toshiyuki",
    0xC4A4: "Chief Designer", 0xC4C7: N + "Bon-chan's Mama", 0xC4D4: "Music", 0xC4DA: N + "KAJIYA PROJECT",
    0xC4EC: "Character Costume", 0xC503: N + "Lay-up", 0xC50D: "Emperor Festival",
    0xC51A: "Rough Costume Design", 0xC53E: "Special Thanks", 0xC549: N + "The Debuggers",
    0xC559: "Supervisor", 0xC565: N + "Hard-Boiled Ishikawa", 0xC57F: "Producer", 0xC589: N + "Shimomichi Takashi",
    0xC595: "Executive Producer", 0xC5A9: N + "Sugiura Yukimasa", 0xC5B7: "",
    0xC612: "The Great Battle Gaiden 2", 0xC65A: N + "Morikazu Naoko", 0xC667: "Matsuri da Wasshoi Staff",
}
KEEP = [0xC5B8, 0xC5D2, 0xC5E7, 0xC5FE, 0xC643]  # Latin already
DESIGN_WORK = 0xC4F9


def raw(rom, p):
    e = rom.index(0xFF, p)
    return bytes(rom[p:e])


def apply(rom):
    ptrs, a = [], TABLE
    while rom[a] | rom[a + 1] << 8:
        ptrs.append(rom[a] | rom[a + 1] << 8)
        a += 2
    assert len(ptrs) == 85 and rom[START:START + 2] == bytes([0x68, 0x98]), "staff roll moved"
    assert set(ptrs) <= set(EN) | set(KEEP) | {DESIGN_WORK}, sorted(set(ptrs) - set(EN) - set(KEEP))
    blobs = {p: bytes(CODE[c] for c in s) for p, s in EN.items()}
    blobs.update({p: raw(rom, p) for p in KEEP})
    new, pos, out = {}, START, bytearray()
    for p in sorted(blobs):
        assert len(blobs[p]) <= 32, hex(p)
        new[p] = pos
        out += blobs[p] + b"\xFF"
        pos += len(blobs[p]) + 1
    assert pos <= END, f"staff roll {pos - END} bytes too long"
    rom[START:START + len(out)] = out
    rom[START + len(out):END] = b"\xFF" * (END - START - len(out))
    new[DESIGN_WORK] = new[0xC3B8] + 5
    for i, p in enumerate(ptrs):
        rom[TABLE + 2 * i:TABLE + 2 * i + 2] = new[p].to_bytes(2, "little")
