"""Password screen header plaque パスワード -> PASSWORD; writes gfx/pw_head.png from work/gfx/pw_head.* (BG1 export).

    python -X utf8 gfx/pw_head.py

The kana are pure black on a horizontal-gradient plaque: erase by copying each pixel from the row above, then draw
the word in black.
"""
import shutil
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
SRC, OUT = ROOT / "work" / "gfx" / "pw_head", ROOT / "gfx" / "pw_head"
BLACK = (0, 0, 0)
X0, X1, Y0, Y1 = 20, 108, 17, 31  # plaque interior in the PNG


def main():
    im = Image.open(SRC.with_suffix(".png")).convert("RGB")
    for y in range(Y0, Y1):
        for x in range(X0, X1):
            if im.getpixel((x, y)) == BLACK:
                im.putpixel((x, y), im.getpixel((x, y - 1)))
    font = ImageFont.truetype("C:/Windows/Fonts/impact.ttf", 20)
    text = "PASSWORD"
    l, t, r, b = font.getbbox(text)
    m = Image.new("1", (r - l, b - t))
    ImageDraw.Draw(m).text((-l, -t), text, font=font, fill=1)
    m = m.resize((min(m.width, X1 - X0 - 8), 11), Image.NEAREST)
    ox, oy = (X0 + X1 - m.width) // 2, 18
    for y in range(m.height):
        for x in range(m.width):
            if m.getpixel((x, y)):
                im.putpixel((ox + x, oy + y), BLACK)
    im.save(OUT.with_suffix(".png"))
    shutil.copy(SRC.with_suffix(".json"), OUT.with_suffix(".json"))
    print(OUT.with_suffix(".png"))


if __name__ == "__main__":
    main()
