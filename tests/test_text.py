import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import batches  # noqa: E402
import build  # noqa: E402
import text  # noqa: E402

SKILL = ROOT / ".claude" / "skills" / "translate-retro-game" / "scripts"


def test_roundtrip():
    assert text.roundtrip()


def test_coverage():
    assert text.coverage()


def test_lint_and_glossary():
    script = text.load()
    assert batches.problems(script, {e["id"]: e["en"] for e in script if e["en"]}) == []


def test_wrap_keeps_indent_and_hard_breaks():
    assert build.wrap("  Go team go{n}Compati Heroes!", 8) == ["  Go", "team go", "Compati", "Heroes!"]
    assert build.wrap("ab{wait:10} cd", 5) == ["ab{wait:10} cd"]


def test_layout_double_spaces_when_it_fits():
    pages, double, errs = build.layout("Hello there{key}{page}Bye{key}{end}", (12, 4))
    assert (pages, double, errs) == ([["Hello there{key}"], ["Bye{key}"]], True, [])
    assert build.encode_layout(pages, double) == build.EN.encode("{n}Hello there{key}{page}{n}Bye{key}{end}")
    pages, double, errs = build.layout("one two three four five{end}", (9, 4))
    assert not double and len(pages[0]) == 3 and errs == []
    assert build.layout("one two three four five six seven eight{end}", (9, 4))[2]


def test_lint_catches_bad_page_and_codes():
    e = {"id": "X", "hdr": "C192", "jp": "あ{key}{page}い{fast}{slow}{end}", "en": "a{page}b{end}"}
    errs = build.lint([e])
    assert any("control codes" in m for m in errs) and any("{page} not preceded" in m for m in errs)


def test_marker_build_writes_only_allowed_ranges(tmp_path):
    out = tmp_path / "m.sfc"
    build.build(out, use_marker=True)
    ranges = (ROOT / "tools" / "allowed_ranges.txt").read_text().split("\n")
    args = [r.split()[0] for r in ranges if r.strip()]
    r = subprocess.run([sys.executable, "-X", "utf8", str(SKILL / "romdiff.py"), str(text.ROM), str(out), *args],
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr
