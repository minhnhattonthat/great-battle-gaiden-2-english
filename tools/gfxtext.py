"""Draw outlined pixel-caps words into an exported graphics PNG (tools/gfx.py export), in each cell's own palette.

    python -X utf8 tools/gfxtext.py work/gfx/title_menu.png --spec gfx/title_menu.txt

Spec lines: `X Y W TEXT` (pixels inside the PNG; W = box the word is centred in) plus options after `|`:
`clear` (wipe the box to colour 0 first), `h=16` (16 = 5x7 font doubled in height, 8 = plain), `fill=2 low=3 edge=1`
(palette indices: upper fill, lower fill, outline), `adv=7` (letter advance, default 8 when h=16 else 6).
"""
import argparse
import json
from pathlib import Path

from PIL import Image

FONT5x7 = {
    "A": "01110 10001 10001 11111 10001 10001 10001", "B": "11110 10001 10001 11110 10001 10001 11110",
    "C": "01110 10001 10000 10000 10000 10001 01110", "D": "11110 10001 10001 10001 10001 10001 11110",
    "E": "11111 10000 10000 11110 10000 10000 11111", "F": "11111 10000 10000 11110 10000 10000 10000",
    "G": "01110 10001 10000 10111 10001 10001 01111", "H": "10001 10001 10001 11111 10001 10001 10001",
    "I": "01110 00100 00100 00100 00100 00100 01110", "J": "00111 00010 00010 00010 00010 10010 01100",
    "K": "10001 10010 10100 11000 10100 10010 10001", "L": "10000 10000 10000 10000 10000 10000 11111",
    "M": "10001 11011 10101 10101 10001 10001 10001", "N": "10001 11001 10101 10011 10001 10001 10001",
    "O": "01110 10001 10001 10001 10001 10001 01110", "P": "11110 10001 10001 11110 10000 10000 10000",
    "Q": "01110 10001 10001 10001 10101 10010 01101", "R": "11110 10001 10001 11110 10100 10010 10001",
    "S": "01111 10000 10000 01110 00001 00001 11110", "T": "11111 00100 00100 00100 00100 00100 00100",
    "U": "10001 10001 10001 10001 10001 10001 01110", "V": "10001 10001 10001 10001 10001 01010 00100",
    "W": "10001 10001 10001 10101 10101 10101 01010", "X": "10001 10001 01010 00100 01010 10001 10001",
    "Y": "10001 10001 01010 00100 00100 00100 00100", "Z": "11111 00001 00010 00100 01000 10000 11111",
    "0": "01110 10001 10011 10101 11001 10001 01110", "1": "00100 01100 00100 00100 00100 00100 01110",
    "2": "01110 10001 00001 00010 00100 01000 11111", "3": "11110 00001 00001 01110 00001 00001 11110",
    "4": "00010 00110 01010 10010 11111 00010 00010", "5": "11111 10000 11110 00001 00001 10001 01110",
    "6": "00110 01000 10000 11110 10001 10001 01110", "7": "11111 00001 00010 00100 01000 01000 01000",
    "8": "01110 10001 10001 01110 10001 10001 01110", "9": "01110 10001 10001 01111 00001 00010 01100",
    "!": "00100 00100 00100 00100 00100 00000 00100", "?": "01110 10001 00001 00010 00100 00000 00100",
    ".": "00000 00000 00000 00000 00000 00000 00100", "-": "00000 00000 00000 11111 00000 00000 00000",
    "'": "00100 00100 01000 00000 00000 00000 00000", " ": "00000 00000 00000 00000 00000 00000 00000",
}


def word_mask(text, h=16, adv=None):
    """-> (w, h, set of fill pixels with their row) for the glyph bodies (bold, before outline)."""
    adv = adv or (8 if h == 16 else 6)
    scale = 2 if h == 16 else 1
    px = set()
    for i, ch in enumerate(text.upper()):
        rows = FONT5x7[ch].split()
        for y, row in enumerate(rows):
            for x, bit in enumerate(row):
                if bit == "1":
                    for dy in range(scale):
                        for dx in (0, 1) if h == 16 else (0,):
                            px.add((i * adv + 1 + x + dx, 1 + y * scale + dy))
    width = len(text) * adv
    return width, h, px


def paint(img, meta, x0, y0, w, text, fill=2, low=3, edge=1, h=16, adv=None, clear=False):
    lay, (rx, ry, _, _), pal = meta["layer"], meta["rect"], [tuple(c) for c in meta["palette"]]
    cells = {tuple(map(int, k.split(","))): v for k, v in meta["cells"].items()}

    def put(x, y, idx):
        cell = cells[(rx + x // 8, ry + y // 8)]
        p = cell[1]
        img.putpixel((x, y), pal[lay["palbase"] + p * (1 << lay["bpp"]) + idx] if idx else (255, 0, 255))

    if clear:
        for y in range(y0, y0 + h):
            for x in range(x0, x0 + w):
                put(x, y, 0)
    tw, th, body = word_mask(text, h, adv)
    ox = x0 + (w - tw) // 2
    for (x, y) in body:
        put(ox + x, y0 + y, low if y >= th * 5 // 8 + 1 else fill)
    for (x, y) in body:
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                q = (x + dx, y + dy)
                if q not in body and 0 <= ox + q[0] < img.width and 0 <= y0 + q[1] < img.height:
                    put(ox + q[0], y0 + q[1], edge)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("png")
    ap.add_argument("--spec", required=True)
    a = ap.parse_args()
    png = Path(a.png)
    meta = json.loads(png.with_suffix(".json").read_text())
    img = Image.open(png).convert("RGB")
    for line in Path(a.spec).read_text(encoding="utf-8").splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        main_part, _, opts = line.partition("|")
        x, y, w, text = main_part.strip().split(" ", 3)
        kw = {}
        for o in opts.split():
            k, _, v = o.partition("=")
            kw[k] = True if not v else int(v)
        paint(img, meta, int(x), int(y), int(w), text, **kw)
    img.save(png)
    print(png)


if __name__ == "__main__":
    main()
