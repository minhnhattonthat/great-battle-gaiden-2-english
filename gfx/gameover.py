"""Game over screen: GAME OVER logo + YES/NO, drawn straight into the BG1 tiles; called by tools/build.py.

BG1 uses 16x16 tiles (large tile n = 8x8 tiles n, n+1, n+16, n+17), chr VRAM $0000 <- ROM 0x55100 (raw).
The tilemap comes from a record stream at ROM 0x10CEF0: word count, word VRAM address, count entries. The JP logo
records (60 bytes) become two 13-entry rows; はい/いいえ keep their records (YES = tiles 46 48, NO = 4A 42).
The YES/NO cursor swaps palettes 2/3 in CGRAM, so the tilemap is static.
"""
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
import gfx  # noqa: E402
import gfxtext  # noqa: E402

CHR = 0x55100
STREAM = 0x10CEF0
LOGO_SLOTS = [0x02, 0x04, 0x06, 0x08, 0x0A, 0x0C, 0x0E, 0x20, 0x22, 0x24, 0x26, 0x28, 0x2A, 0x2C, 0x2E, 0x40]
YES, NO = [0x46, 0x48], [0x4A, 0x42]
FONT = "C:/Windows/Fonts/impact.ttf"


def put_large(rom, n, px):
    """px: 16x16 index rows -> large tile n."""
    for sy in range(2):
        for sx in range(2):
            sub = [row[sx * 8:sx * 8 + 8] for row in px[sy * 8:sy * 8 + 8]]
            o = CHR + (n + sx + 16 * sy) * 32
            rom[o:o + 32] = gfx.encode(sub, 4)


def letter(ch):
    """32x16 index image of one letter: pink gradient body (2..13), outline 1."""
    font = ImageFont.truetype(FONT, 34)
    l, t, r, b = font.getbbox(ch)
    m = Image.new("1", (r - l, b - t))
    ImageDraw.Draw(m).text((-l, -t), ch, font=font, fill=1)
    m = m.resize((min(m.width, 14), 28), Image.NEAREST)
    ox = (16 - m.width) // 2
    body = {(ox + x, 2 + y) for y in range(m.height) for x in range(m.width) if m.getpixel((x, y))}
    px = [[0] * 16 for _ in range(32)]
    for (x, y) in body:
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if 0 <= x + dx < 16 and 0 <= y + dy < 32:
                    px[y + dy][x + dx] = 1
    for (x, y) in body:
        px[y][x] = 2 + (y - 2) * 12 // 28
    return px


def word(text, width):
    """16 x width index image: 5x7 caps doubled, fill 3 (top) / 4 (bottom), outline 1."""
    tw, th, body = gfxtext.word_mask(text)
    ox = (width - tw) // 2
    px = [[0] * width for _ in range(16)]
    for (x, y) in body:
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                px[y + dy][ox + x + dx] = 1
    for (x, y) in body:
        px[y][ox + x] = 3 if y < 8 else 4
    return px


def apply(rom):
    slots = iter(LOGO_SLOTS)
    top, bottom = [0, 0], [0, 0]
    for ch in "GAME OVER":
        if ch == " ":
            top.append(0)
            bottom.append(0)
            continue
        px, u, d = letter(ch), next(slots), next(slots)
        put_large(rom, u, px[:16])
        put_large(rom, d, px[16:])
        top.append(0x0400 | u)
        bottom.append(0x0400 | d)
    top += [0, 0]
    bottom += [0, 0]
    assert len(top) == 13
    rec = b""
    for addr, row in ((0x5041, top), (0x5061, bottom)):
        rec += len(row).to_bytes(2, "little") + addr.to_bytes(2, "little") + b"".join(e.to_bytes(2, "little") for e in row)
    assert len(rec) == 60 and rom[STREAM:STREAM + 4] == bytes.fromhex("02004150"), "stream changed?"
    rom[STREAM:STREAM + 60] = rec
    for slots_, text in ((YES, "YES"), (NO, "NO")):
        px = word(text, 32)
        for i, n in enumerate(slots_):
            put_large(rom, n, [row[i * 16:i * 16 + 16] for row in px])
    no = STREAM + 60 + 8 + 4  # いいえ record entries: 4A 42 (blank third)
    assert rom[no - 4:no] == bytes.fromhex("03000a51")
    rom[no:no + 6] = bytes.fromhex("4a0842080000")
