"""Preview graphics edits on an old savestate without a cold route: patch the dump's VRAM tiles with the built ROM's
tiles for every gfx/graphics.json PNG entry, load the state, write the patched VRAM into the emulator, screenshot.

    python -X utf8 tools/gfxpreview.py STATE.mss DUMPDIR OUT [--rom build/gbg2_en.sfc] [--frames 6]

DUMPDIR = tools/lua/ppudump.lua output of the same state. State files saved by a newer Mesen need byte 4 = 1
(python: d = bytearray(open(f, 'rb').read()); d[4] = 1). Script (.py) entries are not previewed.
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

ap = argparse.ArgumentParser()
ap.add_argument("state")
ap.add_argument("dump")
ap.add_argument("out")
ap.add_argument("--rom", default=str(ROOT / "build" / "gbg2_en.sfc"))
ap.add_argument("--frames", type=int, default=6)
a = ap.parse_args()

rom = Path(a.rom).read_bytes()
vram = bytearray((Path(a.dump) / "vram.bin").read_bytes())
n = 0
for g in json.loads((ROOT / "gfx" / "graphics.json").read_text(encoding="utf-8")):
    if "png" not in g:
        continue
    meta = json.loads((ROOT / "gfx" / g["png"]).with_suffix(".json").read_text())
    maps = [tuple(int(s, 16) for s in m.split(":")) for m in g["map"].split(",")]
    for key, orig in meta["orig"].items():
        addr, size = int(key, 16), len(orig) // 2
        if vram[addr:addr + size].hex() != orig:
            continue  # this screen does not show the entry's original tile
        src = next((ro + addr - vb for vb, ro in maps if vb <= addr < vb + 0x10000), None)
        if src is not None and vram[addr:addr + size] != rom[src:src + size]:
            vram[addr:addr + size] = rom[src:src + size]
            n += 1
out = Path(a.out)
out.mkdir(parents=True, exist_ok=True)
(out / "vram_patched.bin").write_bytes(vram)
lua = out / "vramload.lua"
lua.write_text(
    'local data = L.read_file("%s")\n'
    "local c = 0\n"  # the state load eats the first frames: count our own
    "L.on_frame(function() c = c + 1; if c == 3 then for i = 1, #data do emu.write(i - 1, data:byte(i), emu.memType.snesVideoRam) end end end)\n"
    % (out / "vram_patched.bin").resolve().as_posix(), encoding="utf-8")
print(n, "tiles patched")
subprocess.run([sys.executable, "-X", "utf8", str(ROOT / ".agents/skills/translate-retro-game/scripts/emu.py"), a.rom,
                "--out", str(out), "--state-in", a.state, "--frames", str(a.frames), "--script", str(lua)], check=True)
