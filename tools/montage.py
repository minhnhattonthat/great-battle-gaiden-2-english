"""Grid of full-size screenshots (QA helper): montage.py OUT.png COLS shot1.png shot2.png ..."""
import sys

from PIL import Image

out, cols, files = sys.argv[1], int(sys.argv[2]), sys.argv[3:]
ims = [Image.open(f).convert("RGB") for f in files]
w, h = ims[0].size
sheet = Image.new("RGB", (w * cols, h * ((len(ims) + cols - 1) // cols)))
for i, im in enumerate(ims):
    sheet.paste(im, (w * (i % cols), h * (i // cols)))
sheet.save(out)
