"""Whole-ROM tile sheets for finding baked-in text: romsheets.py ROM OUTDIR [--bpp 4] [--start 0] [--end 140000]
One PNG per 256 KB: four 64 KB columns, each 32 tiles wide (grey ramp, 1:1). Name = <hex start>.png; compressed data
looks like noise, graphics like pictures. View with the image reader, then zoom into the hits with tilesheet.py --at."""
import argparse
from pathlib import Path

from PIL import Image

ap = argparse.ArgumentParser()
ap.add_argument("rom")
ap.add_argument("out")
ap.add_argument("--bpp", type=int, default=4)
ap.add_argument("--start", type=lambda s: int(s, 16), default=0)
ap.add_argument("--end", type=lambda s: int(s, 16), default=0x140000)
a = ap.parse_args()
rom = Path(a.rom).read_bytes()
out = Path(a.out)
out.mkdir(parents=True, exist_ok=True)
bpp, tsize = a.bpp, 8 * a.bpp
per_col = 0x10000
tiles_per_col = per_col // tsize
rows = tiles_per_col // 32
ramp = [int(255 * i / ((1 << bpp) - 1)) for i in range((1 << bpp))]
for base in range(a.start, a.end, 4 * per_col):
    img = Image.new("L", (4 * 256 + 3 * 4, rows * 8), 128)
    px = img.load()
    for col in range(4):
        for t in range(tiles_per_col):
            o = base + col * per_col + t * tsize
            if o + tsize > len(rom):
                break
            ox, oy = col * 260 + (t % 32) * 8, (t // 32) * 8
            for y in range(8):
                planes = [(rom[o + (p // 2) * 16 + y * 2 + (p & 1)]) for p in range(bpp)]
                for x in range(8):
                    v = sum(((planes[p] >> (7 - x)) & 1) << p for p in range(bpp))
                    px[ox + x, oy + y] = 255 - ramp[v]
    img.save(out / f"{base:06X}.png")
    print(out / f"{base:06X}.png")
