"""BG graphics round trip: render a layer from a PPU dump (tools/lua/ppudump.lua), export a screen rectangle to an
editable PNG, import the edited PNG back into the ROM tiles it came from.

    python -X utf8 tools/gfx.py render DUMP --bg 1 [--out bg1.png]
    python -X utf8 tools/gfx.py export DUMP --bg 1 --rect X,Y,W,H --out gfx/title.png   # 8x8 cells, map coords
    python -X utf8 tools/gfx.py import gfx/title.png ROM --map VRAMBYTE:ROMOFF[,...]       # edits ROM in place

export writes PNG + .json beside it (cells: map cell -> VRAM tile, palette, flips). import maps every pixel back to
its cell's palette (exact colours only), un-flips, and writes the tile to ROM via the VRAM->ROM mapping (raw
graphics; find it with tools/vramfind.py). It refuses tiles used outside the rectangle or edited two ways.
"""
import argparse
import json
from pathlib import Path

from PIL import Image


def load(dump):
    d = Path(dump)
    ppu = dict(line.split("=", 1) for line in (d / "ppu.txt").read_text().splitlines() if "=" in line)
    cg = (d / "cgram.bin").read_bytes()
    pal = []
    for i in range(256):
        c = cg[2 * i] | cg[2 * i + 1] << 8
        pal.append(((c & 31) * 255 // 31, (c >> 5 & 31) * 255 // 31, (c >> 10 & 31) * 255 // 31))
    return (d / "vram.bin").read_bytes(), pal, ppu


def layer(ppu, bg):
    i = bg - 1
    mode = int(ppu["ppu.bgMode"])
    bpp = {0: (2, 2, 2, 2), 1: (4, 4, 2, 0)}[mode][i]
    return dict(bpp=bpp, chr=int(ppu[f"ppu.layers[{i}].chrAddress"]) * 2, map=int(ppu[f"ppu.layers[{i}].tilemapAddress"]) * 2,
                large=ppu[f"ppu.layers[{i}].largeTiles"] == "true", palbase=0 if mode else 32 * i)


def cells(vram, L, w=32, h=32):
    """{(cx, cy): (tile byte addr, palette, hflip, vflip)} for every 8x8 cell of a 32x32-entry map."""
    out, step = {}, 2 if L["large"] else 1
    for my in range(h):
        for mx in range(w):
            e = vram[L["map"] + 2 * (my * 32 + mx)] | vram[L["map"] + 2 * (my * 32 + mx) + 1] << 8
            n, p, hf, vf = e & 0x3FF, e >> 10 & 7, bool(e & 0x4000), bool(e & 0x8000)
            for sy in range(step):
                for sx in range(step):
                    sub = n + (step - 1 - sx if hf else sx) + 16 * (step - 1 - sy if vf else sy)
                    addr = (L["chr"] + (sub & 0x3FF) * 8 * L["bpp"]) & 0xFFFF
                    out[(mx * step + sx, my * step + sy)] = (addr, p, hf, vf)
    return out


def decode(vram, addr, bpp):
    return [[sum(((vram[(addr + (p // 2) * 16 + y * 2 + (p & 1)) & 0xFFFF] >> (7 - x)) & 1) << p for p in range(bpp))
             for x in range(8)] for y in range(8)]


def encode(px, bpp):
    out = bytearray(8 * bpp)
    for y in range(8):
        for x in range(8):
            for p in range(bpp):
                if px[y][x] >> p & 1:
                    out[(p // 2) * 16 + y * 2 + (p & 1)] |= 0x80 >> x
    return bytes(out)


def colour(pal, L, p, idx):
    return pal[L["palbase"] + p * (1 << L["bpp"]) + idx] if idx else (255, 0, 255)


def draw(vram, pal, L, cellmap, rect):
    x0, y0, w, h = rect
    img = Image.new("RGB", (w * 8, h * 8))
    for cy in range(h):
        for cx in range(w):
            addr, p, hf, vf = cellmap[(x0 + cx, y0 + cy)]
            t = decode(vram, addr, L["bpp"])
            for y in range(8):
                for x in range(8):
                    img.putpixel((cx * 8 + x, cy * 8 + y), colour(pal, L, p, t[7 - y if vf else y][7 - x if hf else x]))
    return img


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["render", "export", "import"])
    ap.add_argument("src")
    ap.add_argument("rom", nargs="?")
    ap.add_argument("--bg", type=int, default=1)
    ap.add_argument("--rect")
    ap.add_argument("--out")
    ap.add_argument("--map")
    a = ap.parse_args()
    if a.cmd in ("render", "export"):
        vram, pal, ppu = load(a.src)
        L = layer(ppu, a.bg)
        n = 64 if L["large"] else 32
        cm = cells(vram, L)
        rect = tuple(map(int, a.rect.split(","))) if a.rect else (0, 0, n, n)
        img = draw(vram, pal, L, cm, rect)
        out = Path(a.out or f"bg{a.bg}.png")
        out.parent.mkdir(parents=True, exist_ok=True)
        img.save(out)
        if a.cmd == "export":
            used = {cm[(rect[0] + x, rect[1] + y)][0] for y in range(rect[3]) for x in range(rect[2])}
            meta = dict(layer=L, rect=rect, palette=pal, cells={f"{x},{y}": v for (x, y), v in cm.items()},
                        orig={f"{t:04X}": vram[t:t + 8 * L["bpp"]].hex() for t in used})
            out.with_suffix(".json").write_text(json.dumps(meta))
        print(out)
        return
    rom = bytearray(Path(a.rom).read_bytes())
    print(f"{import_png(a.src, rom, a.map)} tiles written")
    Path(a.rom).write_bytes(rom)


def import_png(png, rom, mapping):
    """Write the edited PNG's tiles into rom (bytearray). mapping: 'VRAMBYTE:ROMOFF[,...]' hex. -> tiles changed."""
    meta = json.loads(Path(png).with_suffix(".json").read_text())
    L, (x0, y0, w, h), pal = meta["layer"], meta["rect"], [tuple(c) for c in meta["palette"]]
    cm = {tuple(map(int, k.split(","))): v for k, v in meta["cells"].items()}
    maps = [tuple(int(s, 16) for s in m.split(":")) for m in mapping.split(",")]
    img = Image.open(png).convert("RGB")
    inside = {(x0 + cx, y0 + cy) for cy in range(h) for cx in range(w)}
    tiles = {}
    for (cx, cy) in sorted(inside):
        addr, p, hf, vf = cm[(cx, cy)]
        lut = {colour(pal, L, p, i): i for i in range(1 << L["bpp"])[::-1]}
        px = [[0] * 8 for _ in range(8)]
        for y in range(8):
            for x in range(8):
                c = img.getpixel(((cx - x0) * 8 + x, (cy - y0) * 8 + y))
                if c not in lut:
                    raise SystemExit(f"cell {cx},{cy} pixel {x},{y}: colour {c} not in palette {p}")
                px[7 - y if vf else y][7 - x if hf else x] = lut[c]
        data = encode(px, L["bpp"])
        if tiles.get(addr, data) != data:
            raise SystemExit(f"tile {addr:04X} edited two different ways (cell {cx},{cy})")
        tiles[addr] = data
    changed = 0
    for addr, data in tiles.items():
        if meta["orig"][f"{addr:04X}"] == data.hex():
            continue  # untouched in the PNG
        src = next((ro + addr - vb for vb, ro in maps if vb <= addr < vb + 0x10000), None)
        if src is None:
            raise SystemExit(f"tile {addr:04X}: no --map")
        if rom[src:src + len(data)] == data:
            continue
        users = [c for c, v in cm.items() if v[0] == addr and c not in inside]
        if users:
            raise SystemExit(f"tile {addr:04X} changed but also used outside the rect at {users[:4]}")
        rom[src:src + len(data)] = data
        changed += 1
    return changed


if __name__ == "__main__":
    main()
