"""Translation batches: split, check, merge, pairs, apply, fit.

    python -X utf8 tools/batches.py split             # -> work/tl/<batch>.tsv (+ terms) for every batch
    python -X utf8 tools/batches.py check <batch>     # validate work/tl/<batch>.out.tsv; prints OK
    python -X utf8 tools/batches.py merge <batch>     # check, then write the English into script/msg.json
    python -X utf8 tools/batches.py pairs <batch>     # reviewer input -> work/tl/<batch>.pairs.txt
    python -X utf8 tools/batches.py apply FILE        # id<TAB>EN fixes straight into script/msg.json (checked)
    python -X utf8 tools/batches.py fit HDR "text"    # show the layout of one message in header HDR's box
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import build  # noqa: E402
import text  # noqa: E402

ROOT = text.ROOT
TL = ROOT / "work" / "tl"
BATCHES = {"b1": (0x000, 0x060), "b2": (0x061, 0x0C5)}
SPEAKER = re.compile(r"^\{fast\}([^{]+)\{slow\}(?:\{wait:..\})?\{n\}")


def batch_entries(script, name):
    lo, hi = BATCHES[name]
    return [e for e in script if lo <= int(e["id"], 16) <= hi]


def glossary_rows():
    rows = []
    for line in (ROOT / "glossary.md").read_text(encoding="utf-8").splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if line.startswith("|") and len(cells) >= 2 and cells[0] not in ("JP", "") and not set(cells[0]) <= set("-"):
            rows.append(cells)
    return rows


def split():
    script, box = text.load(), build.boxes(text.load())
    TL.mkdir(parents=True, exist_ok=True)
    gl = glossary_rows()
    for name in BATCHES:
        es = batch_entries(script, name)
        lines = []
        for e in es:
            m = SPEAKER.match(e["jp"])
            w, rows = box[e["hdr"]]
            lines.append(f"{e['id']}\t{m[1] if m else ''}\t{w}x{rows}\t{e['jp']}")
        (TL / f"{name}.tsv").write_text("\n".join(lines) + "\n", encoding="utf-8")
        joined = "".join(e["jp"] for e in es)
        terms = [" | ".join(r) for r in gl if r[0] in joined]
        (TL / f"terms_{name}.txt").write_text("\n".join(terms) + "\n", encoding="utf-8")
        print(f"{name}: {len(es)} entries, {len(terms)} terms")


def read_out(path):
    out = {}
    for n, line in enumerate(Path(path).read_text(encoding="utf-8-sig").splitlines(), 1):
        if not line.strip():
            continue
        if "\t" not in line:
            raise SystemExit(f"{path}:{n}: no tab")
        k, v = line.split("\t", 1)
        if k in out:
            raise SystemExit(f"{path}:{n}: duplicate id {k}")
        out[k] = v
    return out


def problems(script, en):
    by_id = {e["id"]: e for e in script}
    errs = [f"{k}: unknown id" for k in en if k not in by_id]
    trial = [dict(by_id[k], en=v) for k, v in en.items() if k in by_id]
    errs += build.lint(trial, build.boxes(script))
    errs += [f"{k}: tab or \\u escape" for k, v in en.items() if "\t" in v or "\\u" in v]
    for row in glossary_rows():
        jp, eng = row[0], row[1]
        avoid = [a.strip() for a in row[4].split(",")] if len(row) > 4 and row[4] else []
        for e in trial:
            if jp in e["jp"] and eng and eng.lower() not in e["en"].lower():
                errs.append(f"{e['id']}: glossary {jp} -> {eng} missing")
            errs += [f"{e['id']}: avoid {a!r}" for a in avoid if a and re.search(rf"\b{re.escape(a)}\b", e["en"])]
    return errs


def check(name, merge=False):
    script = text.load()
    ids = [e["id"] for e in batch_entries(script, name)]
    en = read_out(TL / f"{name}.out.tsv")
    errs = problems(script, en)
    errs += [f"{k}: missing" for k in ids if k not in en] + [f"{k}: not in batch" for k in en if k not in ids]
    if errs:
        print("\n".join(errs + [f"{len(errs)} errors"]))
        return False
    if merge:
        for e in script:
            if e["id"] in en:
                e["en"] = en[e["id"]]
        text.save(script)
        print(f"merged {len(en)} entries")
    else:
        print("OK")
    return True


def apply(path):
    script = text.load()
    en = read_out(path)
    errs = problems(script, en)
    if errs:
        sys.exit("\n".join(errs + [f"{len(errs)} errors, nothing applied"]))
    for e in script:
        if e["id"] in en:
            e["en"] = en[e["id"]]
    text.save(script)
    print(f"applied {len(en)} entries")


def pairs(name):
    script = text.load()
    es = batch_entries(script, name)
    out = []
    for e in es:
        out += [f">> {e['id']} | {e['jp']}", f"   EN: {e['en'] or '(untranslated)'}", ""]
    p = TL / f"{name}.pairs.txt"
    p.write_text("\n".join(out), encoding="utf-8")
    print(p)


def fit(hdr, s):
    box = build.boxes(text.load())[hdr]
    pages, double, errs = build.layout(s if s.endswith("{end}") else s + "{end}", box)
    print(f"box {box[0]} tiles x {box[1]} rows, {'double' if double else 'single'}-spaced")
    for i, p in enumerate(pages, 1):
        for line in p:
            print(f"p{i} {build.width(line):2} |{build.CTRL.sub('', line)}")
    print("\n".join(errs) or "fits")


if __name__ == "__main__":
    cmd, args = (sys.argv[1], sys.argv[2:]) if len(sys.argv) > 1 else ("", [])
    if cmd == "split":
        split()
    elif cmd in ("check", "merge"):
        sys.exit(0 if check(args[0], cmd == "merge") else 1)
    elif cmd == "pairs":
        pairs(args[0])
    elif cmd == "apply":
        apply(args[0])
    elif cmd == "fit":
        fit(args[0], args[1])
    else:
        sys.exit(__doc__)
