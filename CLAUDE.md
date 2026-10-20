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
- Player bug reports: GitHub issues (`gh issue list --label bug`). Copy the attached save into `work/states/`, reproduce in the emulator, fix, commit with `Fixes #N`, and update the Status section.

## Engine
- Messages: header $1A:C000 -> 6-byte header (speed, attr, VRAM start, arrow); bodies moved to $28:8000 by build.
- English: existing BG3 font has A-Z a-z 0-9; extra glyphs `,` `-` in blank tiles. Line pitch 1 row (asm);
  build double-spaces when a message fits. Box = widest JP line x 2 rows per JP line (build.boxes).

## Other text (asm/main.asm)
- Stall item names $01:93AE (14 x 16 B: top row + bottom row, 8 tiles each). Game over/continue rows $0B:AB6C/AD13
  (strings $0B:E211). Price 円 tile E8 redrawn as bold ¥ (font/extra.txt). Advance dialogue with B, not A.
- Scans: `--script tools/lua/bg3scan.lua` logs BG3 kana outside messages (none left past boot in a 85k-frame tour).

## Graphics (gfx/, applied by build from gfx/graphics.json)
- PNG entries: `tools/gfx.py export DUMP --bg N|0 --rect` (0 = sprites) from a `tools/lua/ppudump.lua` dump, edit
  (tools/gfxtext.py spec or a gfx/*.py drawer), import maps VRAM->ROM (find with tools/vramfind.py). Script entries:
  gfx/<name>.py apply(rom) for tiles + tilemap record streams (bank $21: word count, word VRAM, entries).
- Done: title logo/top line/menu, MINIGAME sub-menu, stage banner (spring + summer seen), game over + YES/NO, HUD YEN,
  password screen, game corner header, attract copyright cards (gfx/cards.py), puzzle SCORE/LEVEL/NEXT, stall puzzle
  FULL plaque, Chick Catch yen, stage select STAGE + EXIT sign, shooting shop (gfx/shop.py + asm sold-out), minigame
  GAME OVER/CLEAR banner (gfx/mg_over.py).
- QA helpers: tools/mkstate.py (route -> state + PPU dump), tools/gfxpreview.py (patch an old state's VRAM with new
  tiles), tools/tmdump.py, stack.py, montage.py, romsheets.py, tools/routes/mg_*.txt. Newer-Mesen savestates: byte 4 = 1.
- Warp to any stage: password slots = 8 nibbles at WRAM $0900+2i (v0 key != 0, v2 = (v0+season+4*area)&15, v4..v10
  data, v12 | v14<<4 = -(v0+v2+v4+v6+v8+v10) & 255); poke them on the password screen, press Start (work/pwrun.py).

## Status (2026-10-10)
- Done: all 198 messages translated + astra-reviewed (docs/review/), item names, game over/continue text, graphics
  above. In game checked: title, password, minigame menu, game corner, intro talk, player select, Emmy guide, stall
  pop-ups, stage banner, HUD, game over.
- Also done: stall signs TAKOYAKI/CORN/CANDY (gfx/signs.py), autumn bridge board BRIDGE, all four banners seen
  (two-line season words), minigames (puzzle, stage select, shop, Chick Catch, Block Break, shooter) reviewed.
- Scene warp: after the password is accepted poke WRAM $040B = scene (0-33; 6 per season, bosses e.g. 3, 5, 9, 11,
  15, 17, 21, 23, 33) -> work/scene.py. Cutscenes: $0454 read at $01:9935 (table $01:CF3B); 10 = ending + staff roll
  (work/cut.py 10). Done there: staff roll (gfx/staffroll.py), THE END, ending picture signs, boss float PRIZE placard.
- Left on purpose / open: Kaminarimon landmark kanji (雷門 lantern, 金龍山 plaque, scene 3). The 大安売 flag on the
  scene 23 boss is painted blank (gfx/sale_flag.py).
- Next: autumn board's second text line (under はしのうえ, tiles 0x90880+, not seen in game), the two open items above
  (ask the user), then release (BPS, README). All 34 scenes + ending reviewed by screenshots (work/scenes_all.py).
- Polish pass: translator notes listed in docs/review/2026-10-10-astra.md.
