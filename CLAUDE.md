# The Great Battle Gaiden 2: Matsuri da Wasshoi (SNES) English translation

Skill: translate-retro-game (H:/translation/great-battle-gaiden-2/.claude/skills/translate-retro-game/SKILL.md). Read it before ROM, text or QA work.

## Commands (run from repo root; always `python -X utf8`)
- Build:   `python -X utf8 tools/build.py [--marker]` -> build/gbg2_en.sfc (pad 2 MB, font/extra.txt, asar asm/main.asm, script)
- Check:   `python -X utf8 tools/check.py` (pytest tests/ + `build.py --lint`; the pre-commit hook runs this)
- Text:    `tools/text.py dump|roundtrip|coverage`; `tools/batches.py split|check|merge|pairs <b1|b2>`, `apply FILE`, `fit HDR "text"`
- Smoke:   `python -X utf8 .claude/skills/translate-retro-game/scripts/emu.py build/gbg2_en.sfc --out work/qa/smoke --route tools/routes/boot.txt --smoke`
- Msg QA:  add `--script tools/lua/msglog.lua` to any emu.py run: logs message ids, shots m<id>_p<n>.png at each {key}/end.
- Release: not built yet (BPS via skill bps.py; fix checksum there). Never publish without the user.

## Paths
- ROM: `rom/orig.sfc` (CRC32 83806E38, SHA-1 76941a710d54943e30212b90c8a14dc1995fe3d2; gitignored). Mesen2: tools/mesen2, asar: tools/asar.
- Text: script/msg.json (198 messages, jp beside en). Table tbl/jp.tbl. Glossary + rulings: glossary.md. Brief: docs/translator-brief.md.
- RE notes: docs/re/text.md. Allowed ROM writes: tools/allowed_ranges.txt. States: work/states/ (charsel = first talk, overworld).
- Helpers: tools/dis65816.py, relsearch.py, tilesheet.py, bgview.py; tools/lua/ (msglog, vramdump, romreads, ...).

## Rulings (user, 2026-10-10)
- Names: official English (franchise) first, else Hepburn no macrons. Honorifics kept, JP name order.
- Credits in English. Plans pre-approved. No abbreviations (engine work / extra pages first).
- Review agents: multi-openai gpt-6-astra (they can't write files: save reports yourself).

## Engine
- Messages: header $1A:C000 -> 6-byte header (speed, attr, VRAM start, arrow); bodies moved to $28:8000 by build.
- English: existing BG3 font has A-Z a-z 0-9; extra glyphs `,` `-` in blank tiles. Line pitch 1 row (asm);
  build double-spaces when a message fits. Box = widest JP line x 2 rows per JP line (build.boxes).

## Status (2026-10-10)
- Done: recon, roundtrip/coverage, engine spike (marker build boots, boxes verified for C1C2/C1D4/C1C8).
- Next: glossary from docs/research-names.md, translate b1/b2, astra review, find non-message text (title, 春のお祭り
  banner graphic, stage names, minigames, ending/credits).
