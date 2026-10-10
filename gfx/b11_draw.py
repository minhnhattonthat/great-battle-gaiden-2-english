"""One-off drawer for gfx/b11_prize.png (scene 11/29 boss float, placard 市長賞 -> PRIZE), run after
`tools/gfx.py export work/qa/st_boss11 --bg 1 --rect 21,9,6,4 --out gfx/b11_prize.png` (dump: work/scene.py boss11 11 3000)."""
import sys
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
from gfxtext import word_mask  # noqa: E402

png = Path(__file__).with_name("b11_prize.png")
im = Image.open(png).convert("RGB")
WHITE, RED, ORANGE = (255, 255, 255), (205, 0, 0), (213, 74, 0)
plate = [(x, y) for y in range(9, 22) for x in range(8, 41)]
for x, y in plate:
    if im.getpixel((x, y)) in (RED, ORANGE):
        im.putpixel((x, y), WHITE)
for y in range(11, 21):  # the kanji's dark drop shadow inside the plate
    for x in range(10, 39):
        if im.getpixel((x, y)) in ((24, 24, 24), (115, 115, 148), (255, 131, 0)):
            im.putpixel((x, y), WHITE)
tw, th, body = word_mask("PRIZE", 8, 6)
ox, oy = 8 + (33 - tw) // 2, 11
for x, y in body:
    im.putpixel((ox + x, oy + y), RED)
im.save(png)
print(png)
