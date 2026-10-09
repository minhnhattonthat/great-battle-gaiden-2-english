"""Render the 16x16 1bpp dialogue font (file 0x8000, 32 bytes/glyph: left 8x16 column, then right) as a labelled grid.

    python -X utf8 tools/fontview.py ROM OUT.png [--start 0] [--count 512] [--cols 16] [--scale 2]
"""
import argparse

from PIL import Image, ImageDraw

FONT = 0x8000


def glyph(rom, code):
    g = rom[FONT + code * 32:FONT + code * 32 + 32]
    return [[(g[r + 16 * (c // 8)] >> (7 - c % 8)) & 1 for c in range(16)] for r in range(16)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("rom")
    ap.add_argument("out")
    ap.add_argument("--start", type=lambda s: int(s, 0), default=0)
    ap.add_argument("--count", type=lambda s: int(s, 0), default=512)
    ap.add_argument("--cols", type=int, default=16)
    ap.add_argument("--scale", type=int, default=2)
    a = ap.parse_args()
    rom = open(a.rom, "rb").read()
    cw, ch = 16 * a.scale + 4, 16 * a.scale + 12
    rows = (a.count + a.cols - 1) // a.cols
    img = Image.new("RGB", (a.cols * cw, rows * ch), "white")
    d = ImageDraw.Draw(img)
    for i in range(a.count):
        code = a.start + i
        x0, y0 = (i % a.cols) * cw, (i // a.cols) * ch
        d.text((x0 + 1, y0), f"{code:03X}", fill="red")
        for r, row in enumerate(glyph(rom, code)):
            for c, px in enumerate(row):
                if px:
                    d.rectangle([x0 + 2 + c * a.scale, y0 + 11 + r * a.scale,
                                 x0 + 1 + (c + 1) * a.scale, y0 + 10 + (r + 1) * a.scale], fill="black")
    img.save(a.out)


if __name__ == "__main__":
    main()
