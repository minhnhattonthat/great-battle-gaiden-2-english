"""Stack crops of several screenshots into one PNG: stack.py OUT.png X,Y,W,H shot1.png shot2.png ... (QA helper)."""
import sys

from PIL import Image

out, box, files = sys.argv[1], tuple(map(int, sys.argv[2].split(","))), sys.argv[3:]
x, y, w, h = box
crops = [Image.open(f).convert("RGB").crop((x, y, x + w, y + h)) for f in files]
sheet = Image.new("RGB", (w, h * len(crops)))
for i, c in enumerate(crops):
    sheet.paste(c, (0, i * h))
sheet.save(out)
