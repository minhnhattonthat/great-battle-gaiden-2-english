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
- Credits in English. Plans pre-approved. Graphics: translate all, title logo included. No abbreviations (engine work / extra pages first).
- Review agents: multi-openai gpt-6-astra (they can't write files: save reports yourself).

## Engine
- Messages: header $1A:C000 -> 6-byte header (speed, attr, VRAM start, arrow); bodies moved to $28:8000 by build.
- English: existing BG3 font has A-Z a-z 0-9; extra glyphs `,` `-` in blank tiles. Line pitch 1 row (asm);
  build double-spaces when a message fits. Box = widest JP line x 2 rows per JP line (build.boxes).

## Other text (asm/main.asm)
- Stall item names $01:93AE (14 x 16 B: top row + bottom row, 8 tiles each). Game over/continue rows $0B:AB6C/AD13
  (strings $0B:E211). Price 円 tile E8 redrawn as bold ¥ (font/extra.txt). Advance dialogue with B, not A.
- Scans: `--script tools/lua/bg3scan.lua` logs BG3 kana outside messages (none left past boot in a 85k-frame tour).

## Status (2026-10-10)
- Done: all 198 messages translated (b1, b2), astra-reviewed (0 Critical; Importants fixed, docs/review/), item
  names, game-over text. In game checked: intro talk, player select, Emmy guide, stall pop-ups, game over.
- Next: graphics with Japanese (title logo, 春のお祭り stage banners, げーむおーばー + はい/いいえ, HUD 円 sprite,
  stall signs, げーむ sign); reach minigames/bosses/ending (random tour never got past stage 1); release.
- Polish pass: translator notes listed in docs/review/2026-10-10-astra.md.
