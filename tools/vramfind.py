"""Find where VRAM contents come from in the ROM (raw copies only): every 32-byte VRAM tile that occurs in the ROM.

    python -X utf8 tools/vramfind.py VRAM.bin ROM [--lo 0000 --hi 8000] [--tile 32]
Prints runs of consecutive VRAM tiles that map to consecutive ROM offsets; tiles not found are likely compressed.
"""
import argparse

ap = argparse.ArgumentParser()
ap.add_argument("vram")
ap.add_argument("rom")
ap.add_argument("--lo", type=lambda s: int(s, 16), default=0)
ap.add_argument("--hi", type=lambda s: int(s, 16), default=0x10000)
ap.add_argument("--tile", type=int, default=32)
a = ap.parse_args()
v, rom = open(a.vram, "rb").read(), open(a.rom, "rb").read()
runs, cur, missing = [], None, 0
for va in range(a.lo, a.hi, a.tile):
    t = v[va:va + a.tile]
    if len(set(t)) <= 1:
        cur = None
        continue
    hit = rom.find(t) if cur is None else (cur[1] + a.tile if rom[cur[1] + a.tile:cur[1] + 2 * a.tile] == t else rom.find(t))
    if hit < 0:
        missing += 1
        cur = None
    elif cur and hit == cur[1] + a.tile and va == cur[2] + a.tile:
        cur[1], cur[2] = hit, va
    else:
        cur = [hit, hit, va, va]
        runs.append(cur)
for r in runs:
    if r[1] > r[0]:
        print(f"VRAM byte {r[3]:05X}-{r[2] + a.tile - 1:05X} <- ROM {r[0]:06X}-{r[1] + a.tile - 1:06X}")
print(f"{missing} non-blank tiles not found raw")
