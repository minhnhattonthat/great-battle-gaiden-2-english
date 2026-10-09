"""Message script: dump, roundtrip, coverage. The game's text engine is documented in docs/re/text.md.

    python -X utf8 tools/text.py dump [--force]   # rom/orig.sfc -> script/msg.json (never clobbers English)
    python -X utf8 tools/text.py roundtrip        # re-encode every jp string, compare with the ROM
    python -X utf8 tools/text.py coverage         # body area fully explained (messages + known orphans)
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
from tbl import Table  # noqa: E402

ROM = ROOT / "rom" / "orig.sfc"
SCRIPT = ROOT / "script" / "msg.json"
JP = Table.load(ROOT / "tbl" / "jp.tbl")

BANK = 0x1A
HDR_TABLE = 0xC000   # $1A:C000, word per message -> 6-byte header (speed, attr, vram start, aux)
BODY_TABLE = 0xC1EC  # $1A:C1EC, word per message -> body text in bank $1A
COUNT = 0xC6         # entries in both tables (body table ends where the first body starts, $C378)
BODY_LO, BODY_HI = 0xD4378, 0xD6F49  # file range of all bodies (end exclusive)
ORPHANS = [(0xD5552, 0xD559A)]       # unreferenced old message between bodies (kept as is)


def off(addr):
    return ((addr & 0x7F0000) >> 1) | (addr & 0x7FFF)


def word(rom, o):
    return rom[o] | rom[o + 1] << 8


def entries(rom):
    """Yield (index, header ptr, body ptr, body file offset) for every message."""
    for i in range(COUNT):
        h = word(rom, off(BANK << 16 | HDR_TABLE) + 2 * i)
        b = word(rom, off(BANK << 16 | BODY_TABLE) + 2 * i)
        yield i, h, b, off(BANK << 16 | b)


def load():
    return json.loads(SCRIPT.read_text(encoding="utf-8"))


def save(data):
    SCRIPT.write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")


def dump(force=False):
    rom = ROM.read_bytes()
    old = {e["id"]: e for e in load()} if SCRIPT.exists() else {}
    if old and not force:
        sys.exit("script/msg.json exists; use --force (keeps en/notes of existing ids)")
    first = {}
    out = []
    for i, h, b, o in entries(rom):
        jp, _ = JP.decode(rom, o)
        e = {"id": f"{i:03X}", "hdr": f"{h:04X}", "ptr": f"{b:04X}", "jp": jp, "en": "", "notes": ""}
        if b in first:
            e["same_as"] = first[b]
        else:
            first[b] = e["id"]
        prev = old.get(e["id"], {})
        e["en"], e["notes"] = prev.get("en", ""), prev.get("notes", "")
        out.append(e)
    save(out)
    print(f"{len(out)} messages -> {SCRIPT.relative_to(ROOT)}")


def roundtrip():
    rom = ROM.read_bytes()
    bad = 0
    for e, (i, h, b, o) in zip(load(), entries(rom)):
        enc = JP.encode(e["jp"])
        if rom[o:o + len(enc)] != enc:
            bad += 1
            print(f"{e['id']}: re-encoded jp differs from ROM at {o:06X}")
    print(f"roundtrip: {bad} bad")
    return bad == 0


def coverage():
    rom = ROM.read_bytes()
    spans = set(ORPHANS)
    for e, (i, h, b, o) in zip(load(), entries(rom)):
        spans.add((o, o + len(JP.encode(e["jp"]))))
    pos, gaps = BODY_LO, []
    for s, t in sorted(spans):
        if s > pos:
            gaps.append((pos, s))
        pos = max(pos, t)
    if pos != BODY_HI:
        gaps.append((pos, BODY_HI))
    for s, t in gaps:
        print(f"gap {s:06X}-{t:06X}")
    print(f"coverage: {len(gaps)} gaps")
    return not gaps


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "dump":
        dump("--force" in sys.argv)
    elif cmd == "roundtrip":
        sys.exit(0 if roundtrip() else 1)
    elif cmd == "coverage":
        sys.exit(0 if coverage() else 1)
    else:
        sys.exit(__doc__)
