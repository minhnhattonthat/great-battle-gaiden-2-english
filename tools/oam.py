"""List OAM sprites from a PPU dump (tools/lua/ppudump.lua).

    python -X utf8 tools/oam.py DUMP [--box X0,Y0,X1,Y1]
Prints index, x, y, size, tile (VRAM byte address), palette, flips, priority.
"""
import argparse
from pathlib import Path

SIZES = {0: ((8, 8), (16, 16)), 1: ((8, 8), (32, 32)), 2: ((8, 8), (64, 64)), 3: ((16, 16), (32, 32)),
         4: ((16, 16), (64, 64)), 5: ((32, 32), (64, 64))}


def sprites(dump):
    d = Path(dump)
    oam = (d / "oam.bin").read_bytes()
    ppu = dict(line.split("=", 1) for line in (d / "ppu.txt").read_text().splitlines() if "=" in line)
    base, gap = int(ppu["ppu.oamBaseAddress"]) * 2, int(ppu["ppu.oamAddressOffset"]) * 2
    small, large = SIZES[int(ppu["ppu.oamMode"])]
    out = []
    for i in range(128):
        x, y, t, a = oam[4 * i:4 * i + 4]
        hi = oam[512 + i // 4] >> (2 * (i % 4)) & 3
        x |= (hi & 1) << 8
        x = x - 512 if x >= 256 else x
        size = large if hi & 2 else small
        tile = t | (a & 1) << 8
        addr = (base + (gap if tile >= 256 else 0) + (tile & 0xFF) * 32) & 0xFFFF
        out.append(dict(i=i, x=x, y=y, w=size[0], h=size[1], tile=tile, addr=addr, pal=a >> 1 & 7,
                        prio=a >> 4 & 3, hf=bool(a & 0x40), vf=bool(a & 0x80)))
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("dump")
    ap.add_argument("--box")
    a = ap.parse_args()
    box = tuple(map(int, a.box.split(","))) if a.box else (-64, 0, 256, 240)
    for s in sprites(a.dump):
        if box[0] <= s["x"] < box[2] and box[1] <= s["y"] < box[3]:
            print(f"{s['i']:3} x={s['x']:4} y={s['y']:3} {s['w']}x{s['h']} tile={s['tile']:03X} @{s['addr']:04X} "
                  f"pal={s['pal']} prio={s['prio']}{' H' if s['hf'] else ''}{' V' if s['vf'] else ''}")
