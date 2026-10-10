"""One-off drawer for gfx/endpic.png (ending picture: Emperor Festival's takoyaki stall), run after
`tools/gfx.py export work/qa/cut10_pic --bg 1 --rect 7,3,19,9 --out gfx/endpic.png` (dump: work/cut.py 10 7300).
Red banner たこやき -> TAKOYAKI, blue sign ハッカ・パ(イプ) -> MINT. Colours are the picture's own."""
import sys
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
from gfxtext import word_mask  # noqa: E402

png = Path(__file__).with_name("endpic.png")
im = Image.open(png).convert("RGB")
RED, BLACK, GREY, LIGHT, DARK = (115, 0, 0), (0, 0, 0), (131, 131, 131), (164, 164, 164), (74, 74, 74)
BLUE = (57, 57, 115)


def erase(box, inks, bg):
    x0, y0, x1, y1 = box
    for y in range(y0, y1):
        for x in range(x0, x1):
            if im.getpixel((x, y)) in inks:
                im.putpixel((x, y), bg)


def draw(text, x0, y0, w, fill, edge, low=None, **kw):
    tw, th, body = word_mask(text, **kw)
    ox = x0 + (w - tw) // 2
    for x, y in body:
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                q = (x + dx, y + dy)
                if q not in body and edge:
                    im.putpixel((ox + q[0], y0 + q[1]), edge)
    for x, y in body:
        im.putpixel((ox + x, y0 + y), low if low and y > th * 5 // 8 else fill)


erase((36, 8, 113, 17), {BLACK, GREY, LIGHT, DARK}, RED)
erase((36, 17, 113, 23), {GREY, LIGHT, DARK}, RED)
draw("TAKOYAKI", 38, 8, 74, LIGHT, BLACK, GREY, h=13, sy=1.5, bold=True, adv=9)  # row 3 tiles are shared frame
erase((76, 38, 136, 56), {GREY, LIGHT, DARK, (106, 106, 106), BLACK}, BLUE)
draw("MINT", 76, 39, 58, GREY, None, None, sx=2, sy=2, adv=13)
im.save(png)
print(png)
