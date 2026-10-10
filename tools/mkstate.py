"""Cold-boot route -> savestate + PPU dump (for gfxpreview.py): mkstate.py NAME ROUTE_FILE_OR_STR FRAMES
Writes work/states/NAME.mss and work/qa/st_NAME/ (vram.bin, cgram.bin, oam.bin, ppu.txt, final.png)."""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
name, route, frames = sys.argv[1], sys.argv[2], sys.argv[3]
(ROOT / "work/states").mkdir(parents=True, exist_ok=True)
flag = "--route" if Path(route).exists() else "--route-str"
subprocess.run([sys.executable, "-X", "utf8", str(ROOT / ".agents/skills/translate-retro-game/scripts/emu.py"),
                str(ROOT / "build/gbg2_en.sfc"), "--out", str(ROOT / "work/qa" / f"st_{name}"), flag, route,
                "--frames", frames, "--state-out", str(ROOT / "work/states" / f"{name}.mss"),
                "--script", str(ROOT / "tools/lua/ppudump.lua")], check=True)
