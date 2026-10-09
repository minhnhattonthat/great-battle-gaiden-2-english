"""Draw the English title logo into gfx/title_logo.png (exported BG1 rect, palette 1; see gfx/graphics.json).

    python -X utf8 gfx/logo.py            # rewrites gfx/title_logo.png from the export in work/gfx/logo_bg1.*

Line 1 (red, like 祭だ): IT'S A FESTIVAL!   Line 2 (white/blue, like ワッショイ): WASSHOI!
Cells marked blank in the original are shared tiles: drawing there is an error.
"""
import json
import shutil
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "work" / "gfx" / "logo_bg1"
OUT = ROOT / "gfx" / "title_logo"
FONT = "C:/Windows/Fonts/ariblk.ttf"
PAL = 1  # BG palette of every logo cell
RED = [7, 8, 9, 10, 11]          # bright -> dark red
RED_EDGE, RED_RIM = 5, 2         # dark navy outline, white rim
WHITE, SHADE, BLUE_EDGE, BLUE_RIM = 2, 12, 14, 5


def mask(text, size, width):
    font = ImageFont.truetype(FONT, size)
    l, t, r, b = font.getbbox(text)
    m = Image.new("1", (r - l, b - t))
    ImageDraw.Draw(m).text((-l, -t), text, font=font, fill=1)
    if m.width > width:  # squeeze horizontally to fit
        m = m.resize((width, m.height), Image.NEAREST)
    return m


def grow(px, n=1):
    out = set(px)
    for _ in range(n):
        out |= {(x + dx, y + dy) for x, y in out for dx in (-1, 0, 1) for dy in (-1, 0, 1)}
    return out


def main():
    meta = json.loads(SRC.with_suffix(".json").read_text())
    x0, y0, w, h = meta["rect"]
    pal = [tuple(c) for c in meta["palette"]]
    blank = {(cx, cy) for cy in range(h) for cx in range(w)
             if not meta["orig"][f"{meta['cells'][f'{x0 + cx},{y0 + cy}'][0]:04X}"].strip("0")}
    img = Image.new("RGB", (w * 8, h * 8), (255, 0, 255))
    layers = []  # (pixels, colour fn)

    def place(text, size, top, maxw, fill, edge, rim, cx):
        m = mask(text, size, maxw)
        ox = cx - m.width // 2
        body = {(ox + x, top + y) for y in range(m.height) for x in range(m.width) if m.getpixel((x, y))}
        e1 = grow(body) - body
        e2 = grow(body, 2) - body - e1
        ys = [y for _, y in body]
        lo, hi = min(ys), max(ys)
        for (x, y) in e2:
            layers.append(((x, y), rim))
        for (x, y) in e1:
            layers.append(((x, y), edge))
        for (x, y) in body:
            layers.append(((x, y), fill(y, lo, hi)))

    # usable cells: rows 2-3 cols 3-18 (x 24-151), rows 4-7 cols 3-20 (x 24-167); 2 px of rim each side
    place("IT'S A FESTIVAL!", 14, 18, 122, lambda y, lo, hi: RED[min(4, (y - lo) * 5 // (hi - lo + 1))], RED_EDGE,
          RED_RIM, 88)
    place("WASSHOI!", 24, 36, 138, lambda y, lo, hi: WHITE if y < lo + (hi - lo) * 2 // 3 else SHADE, BLUE_EDGE,
          BLUE_RIM, 96)
    for (x, y), idx in layers:
        if not (0 <= x < w * 8 and 0 <= y < h * 8):
            continue
        if (x // 8, y // 8) in blank:
            raise SystemExit(f"pixel {x},{y} lands in shared blank cell {x // 8},{y // 8}")
        img.putpixel((x, y), pal[PAL * 16 + idx])
    img.save(OUT.with_suffix(".png"))
    shutil.copy(SRC.with_suffix(".json"), OUT.with_suffix(".json"))
    print(OUT.with_suffix(".png"))


if __name__ == "__main__":
    main()
