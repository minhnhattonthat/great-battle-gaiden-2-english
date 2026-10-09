# Text engine (message printer, bank $01)

ROM: LoROM, 10 Mbit (1.25 MB), header size byte $0B (2 MB), no SRAM. Build pads to 2 MB: banks $28-$3F free (0xFF).

## Messages
- Message id in `$043E` (12 bits; bit 15 = running). Start: `$01:85B1`; per-char printer `$01:8692`.
- Header table `$1A:C000` (word per id, 0xC6 ids) -> 6-byte header at `$1A:C18C-C1EB` (16 headers):
  `+0 speed` (frames/char), `+1 attr` (tilemap high byte, $20), `+2 word` VRAM start (BG3 tilemap word addr),
  `+4 word` VRAM of the blinking {key} arrow (tile $E9).
- Body table `$1A:C1EC` (word per id) -> body in bank $1A, file 0xD4378-0xD6F48. Bodies 196 unique (2 shared).
  Orphan old message 0xD5552-0xD5599 (unreferenced). After 0xD6F49: 4 KB of 0xAA-ish filler (unused).
- Only `$01:850B/8510` (pre-pass) and `$01:86A2/86A7` (printer) load the body table; build moves it to `$28:8000`.

## Codes (byte = BG3 font tile; tbl/jp.tbl)
| byte | name | effect |
|---|---|---|
| FF | {end} | `$043E` = 0 |
| FE | {n} | VRAM += $40 (2 rows: dakuten row + line). Wrap at $5C00 (-$400) |
| FD | {page} | page clear (pre-pass `$01:84FB`), VRAM back to start |
| FC xx | {wait:xx} | wait xx frames |
| FB | {key} | blinking arrow, wait for button |
| FA / F9 | {fast} / {slow} | print without / with per-char delay |
| 98 / 99 | ゛ ゜ | drawn one row up, one column left (over previous char) |
- Space = tile 00 (no sound). Other bytes print tile n with attr from the header.
- Page-clear pre-pass (`$01:84FB`) walks the WHOLE message: for every line of every page it clears
  (count of bytes on that line) tiles at the line row and the row above, writing $2C00. Union of all pages = clean box.
  It counted control bytes as chars (fixed in asm: prepass_count).

## Font
- BG3 2bpp, raw (uncompressed) at ROM 0x4000 (tile n at 0x4000 + n*16), 256 tiles. VRAM chr word $4000, map $5800.
- Already has: 0-9 = 10-19, `: ! ( ) ・ ?` = 1A-1F, A-Z = 21-3A, a-z = 3B-54, / = 57, " = 58, . = 59, ' = 5A.
  Katakana 60-97 (ー=97), hiragana A0-D6, 「」= 9B/9C, 、= 9D. No kanji.
- Blank tiles (free for new glyphs): 5F, 9E, 9F, EB-F8 (F9-FF are control codes, can't print). Used: 5F `,`, 9E `-`.

## English layout (asm/main.asm, tools/build.py)
- Line pitch 1 row ($20) instead of 2; headers start 1 row higher, so a 2-line JP box holds 4 English lines.
  Build double-spaces a message (JP positions, leading {n}) when every page fits that way.
- Box size per header = widest JP line x 2 rows per JP line (build.boxes). Verified in game: C1C2 (char-select
  talk, 6 rows), C1D4 (player-select description, 4 rows), C1C8 (overworld intro, no box).

## Not yet found
- Text outside the message engine: title, 春のお祭り banner (graphic), stage names, minigames, ending/credits.
