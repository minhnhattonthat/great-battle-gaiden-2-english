"""Contact sheet of the distinct shots of a run dir: runsheet.py RUNDIR OUT.png [FIRST_FRAME] [COLS] [MAX]"""
import glob
import sys

from PIL import Image

d, out = sys.argv[1], sys.argv[2]
first = int(sys.argv[3]) if len(sys.argv) > 3 else 0
cols = int(sys.argv[4]) if len(sys.argv) > 4 else 4
mx = int(sys.argv[5]) if len(sys.argv) > 5 else 16
seen, files = set(), []
for f in sorted(glob.glob(d + "/f0*.png")):
    if int(f.rsplit("f", 1)[1][:6]) < first:
        continue
    b = Image.open(f).convert("RGB").tobytes()
    if b not in seen:
        seen.add(b)
        files.append(f)
files = files[:mx]
rows = (len(files) + cols - 1) // cols
s = Image.new("RGB", (256 * cols, 239 * rows))
for i, f in enumerate(files):
    s.paste(Image.open(f).convert("RGB"), ((i % cols) * 256, (i // cols) * 239))
s.save(out)
print([x.rsplit("f", 1)[1][:6] for x in files])
