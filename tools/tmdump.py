"""Print the non-empty entries of a BG tilemap from a ppudump dir: tmdump.py DIR BASE_BYTE_ADDR (e.g. 22528 or 0x5800)."""
import sys

d, base = sys.argv[1], int(sys.argv[2], 0)
v = open(d + "/vram.bin", "rb").read()
for ty in range(32):
    row = [v[base + (ty * 32 + tx) * 2] | v[base + (ty * 32 + tx) * 2 + 1] << 8 for tx in range(32)]
    if any(e & 0x3FF for e in row):
        print("%2d" % ty, " ".join("%04X" % e if e & 0x3FF else "...." for e in row))
