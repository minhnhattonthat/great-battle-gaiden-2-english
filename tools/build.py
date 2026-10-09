"""Build the English ROM: pad to 2 MB, extra font glyphs, asar asm/main.asm, then lay out and pack the script.

    python -X utf8 tools/build.py [--marker] [--out build/gbg2_en.sfc]

`en` text per message: pages split by {page}; the build word-wraps each page to its box (BOXES) and lays the lines
out one row apart, or two rows apart (the Japanese layout) when every page of the message fits that way.
{n} forces a line break. Control codes are zero-width. Empty `en` = Japanese, or a marker with --marker.
"""
import argparse
import importlib.util
import json
import re
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import gfx  # noqa: E402
import text  # noqa: E402
from tbl import Table  # noqa: E402

ROOT = text.ROOT
BUILD = ROOT / "build"
ASAR = ROOT / "tools" / "asar" / "asar.exe"
SIZE = 0x200000
BODY_BANK, BODY_TABLE = 0x28, 0x8000  # must match asm/main.asm
BODY_END = 0x28FFFF                   # bodies stay in bank $28
EN_CHARS = ([(" ", 0x00)] + [(str(i), 0x10 + i) for i in range(10)] + list(zip(":!()", range(0x1A, 0x1E)))
            + [("?", 0x1F)] + [(chr(65 + i), 0x21 + i) for i in range(26)] + [(chr(97 + i), 0x3B + i) for i in range(26)]
            + [("/", 0x57), ('"', 0x58), (".", 0x59), ("'", 0x5A), (",", 0x5F), ("-", 0x9E)])
CTRL_LINES = [line for line in (ROOT / "tbl" / "jp.tbl").read_text(encoding="utf-8").splitlines() if "={" in line]
EN = Table([f"{b:02X}={c}" for c, b in EN_CHARS] + CTRL_LINES)
CTRL = re.compile(r"\{[a-z]+(?::[0-9A-F]{2})?\}")
MARKER = "The quick brown fox jumps over the lazy dog by the festival gate while the band plays on and on."


def boxes(script):
    """Per header: (width in tiles, rows). From the Japanese: widest line, 2 rows per line of the fullest page."""
    geo = defaultdict(lambda: [0, 0])
    for e in script:
        g = geo[e["hdr"]]
        for page in e["jp"].replace("{end}", "").split("{page}"):
            lines = page.split("{n}")
            g[1] = max(g[1], 2 * len(lines))
            for line in lines:
                g[0] = max(g[0], width(line))
    return {h: tuple(v) for h, v in geo.items()}


def width(s):
    return len(CTRL.sub("", s))


def wrap(page, w):
    """Greedy word wrap of one page to w tiles. {n} is a hard break; leading codes + spaces of a hard line are kept
    (indent), runs of spaces inside a line collapse to one."""
    out = []
    for hard in page.split("{n}"):
        lead = re.match(r"(?:\{[^}]*\}| )*", hard)
        line, started = lead[0], False
        for word in hard[lead.end():].split(" "):
            if not word:
                continue
            cand = f"{line} {word}" if started else line + word
            if started and width(cand) > w:
                out.append(line)
                line = word
            else:
                line = cand
            started = True
        out.append(line)
    return out


def layout(en, box):
    """-> (pages as lists of lines, double_spaced, errors)."""
    w, rows = box
    body = en[:-len("{end}")] if en.endswith("{end}") else en
    pages = [wrap(p, w) for p in body.split("{page}")]
    errs = [f"line {width(line)} > {w} tiles: {line!r}" for p in pages for line in p if width(line) > w]
    errs += [f"page has {len(p)} lines > {rows}: {p!r}" for p in pages if len(p) > rows]
    if not en.endswith("{end}"):
        errs.append("missing {end}")
    double = all(2 * len(p) <= rows for p in pages if any(line.strip(" ") or CTRL.search(line) for line in p))
    return pages, double, errs


def encode_layout(pages, double):
    out = []
    for p in pages:
        if not p or p == [""]:
            out.append("")
            continue
        out.append(("{n}" if double else "") + ("{n}{n}" if double else "{n}").join(p))
    return EN.encode("{page}".join(out) + "{end}")


def marker(e, box):
    """Fill every page of the Japanese structure with '<id> quick brown fox...' to the box, keep its codes."""
    w, rows = box
    pages = []
    for i, page in enumerate(e["jp"].replace("{end}", "").split("{page}")):
        codes = "".join(c for c in CTRL.findall(page) if c != "{n}")
        if not page.replace("{n}", "").strip("　") and not codes:
            pages.append("")
            continue
        lines = wrap(f"{e['id']}.{i + 1} {MARKER}", w)[:rows]
        pages.append("{n}".join(lines) + codes)
    return "{page}".join(pages) + "{end}"


def codes(s, drop=("{n}", "{page}", "{key}")):
    return sorted(re.sub(r":..", "", c) for c in CTRL.findall(s) if c not in drop and not c.startswith("{wait"))


def lint(script, box=None):
    """Errors for translated entries: layout, encodability, control codes, page breaks, leftover Japanese.
    box: header geometry from the FULL script (pass it when linting a subset)."""
    box, errs = box or boxes(script), []
    for e in script:
        en = e["en"]
        if not en:
            continue
        msgs = layout(en, box[e["hdr"]])[2]
        try:
            EN.encode(en)
        except ValueError as x:
            msgs.append(str(x))
        if codes(en) != codes(e["jp"]):
            msgs.append(f"control codes {codes(en)} != jp {codes(e['jp'])}")
        if e["jp"].count("{key}") > en.count("{key}"):
            msgs.append("fewer {key} than jp")
        for m in re.finditer(r"\{page\}", en):
            if not re.search(r"(\{key\}|\{wait:..\})$", en[:m.start()]):
                msgs.append("{page} not preceded by {key} or {wait:XX}")
        if re.search(r"[぀-ヿ一-鿿！-～]", en):
            msgs.append("Japanese/full-width characters")
        errs += [f"{e['id']}: {m}" for m in msgs]
    return errs


def font_extra(rom):
    tile, rows, replace = None, [], False
    for line in (ROOT / "font" / "extra.txt").read_text(encoding="utf-8").splitlines():
        if line.startswith("@"):
            tile, rows, replace = int(line.split()[1], 16), [], line.split()[-1] == "replace"
        elif tile is not None and len(line) == 8 and not line.startswith("#"):
            rows.append(line)
            if len(rows) == 8:
                data = bytearray()
                for r in rows:
                    px = [".123".index(c) for c in r]
                    data += bytes([sum((p & 1) << (7 - x) for x, p in enumerate(px)),
                                   sum((p >> 1) << (7 - x) for x, p in enumerate(px))])
                o = 0x4000 + tile * 16
                if any(rom[o:o + 16]) and not replace:
                    raise SystemExit(f"font/extra.txt: tile {tile:02X} is not blank in the original")
                rom[o:o + 16] = data
                tile = None


def build(out, use_marker=False):
    script = text.load()
    box = boxes(script)
    rom = bytearray(text.ROM.read_bytes())
    rom += b"\xFF" * (SIZE - len(rom))
    font_extra(rom)
    BUILD.mkdir(exist_ok=True)
    # asar char map so asm can write English strings: db "Continue?"
    (BUILD / "en_chars.asm").write_text("".join(f"'{c}' = ${b:02X}\n" for c, b in EN_CHARS if c != "'")
                                        + "''' = $5A\n", encoding="utf-8", newline="\n")
    out.write_bytes(rom)
    r = subprocess.run([str(ASAR), "--no-title-check", "--fix-checksum=off",str(ROOT / "asm" / "main.asm"), str(out)],
                       capture_output=True, text=True)
    if r.returncode:
        raise SystemExit(f"asar failed:\n{r.stdout}{r.stderr}")
    rom = bytearray(out.read_bytes())
    for g in json.loads((ROOT / "gfx" / "graphics.json").read_text(encoding="utf-8")):
        if "script" in g:  # gfx/<name>.py with apply(rom): draws tiles / tilemaps directly
            spec = importlib.util.spec_from_file_location(g["script"], ROOT / "gfx" / g["script"])
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            mod.apply(rom)
        else:
            gfx.import_png(ROOT / "gfx" / g["png"], rom, g["map"], g.get("allow_outside", False))

    # headers: start one row higher (lines are 1 row apart now; see asm)
    for h in {e["hdr"] for e in script}:
        o = text.off(text.BANK << 16 | int(h, 16)) + 2
        vram = text.word(rom, o)
        if vram:
            rom[o:o + 2] = (vram - 0x20).to_bytes(2, "little")

    errors, blobs = [], {}
    for e in script:
        src = e["en"] or (marker(e, box[e["hdr"]]) if use_marker else None)
        if src is None:
            blobs[e["id"]] = text.JP.encode(e["jp"])  # untranslated: Japanese (renders with the new pitch)
            continue
        pages, double, errs = layout(src, box[e["hdr"]])
        errors += [f"{e['id']}: {m}" for m in errs]
        blobs[e["id"]] = encode_layout(pages, double)
    if errors:
        raise SystemExit("layout errors:\n" + "\n".join(errors))

    table = text.off(BODY_BANK << 16 | BODY_TABLE)
    pos = table + 2 * text.COUNT
    placed = {}
    for i, e in enumerate(script):
        blob = blobs[e["id"]]
        if blob not in placed:
            if pos + len(blob) > text.off(BODY_END) + 1:
                raise SystemExit(f"bank ${BODY_BANK:02X} full at message {e['id']}")
            placed[blob] = pos
            rom[pos:pos + len(blob)] = blob
            pos += len(blob)
        ptr = 0x8000 | (placed[blob] & 0x7FFF)
        rom[table + 2 * i:table + 2 * i + 2] = ptr.to_bytes(2, "little")
    out.write_bytes(rom)
    used = pos - table
    print(f"built {out}: {len(placed)} bodies, bank ${BODY_BANK:02X} {used:#x}/0x8000 bytes")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--marker", action="store_true")
    ap.add_argument("--out", type=Path)
    ap.add_argument("--lint", action="store_true", help="only lint script/msg.json")
    a = ap.parse_args()
    if a.lint:
        errs = lint(text.load())
        print("\n".join(errs + [f"lint: {len(errs)} errors"]))
        sys.exit(1 if errs else 0)
    build(a.out or BUILD / ("gbg2_marker.sfc" if a.marker else "gbg2_en.sfc"), a.marker)
