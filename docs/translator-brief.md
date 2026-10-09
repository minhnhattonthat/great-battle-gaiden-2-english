# Translator brief - The Great Battle Gaiden 2: Matsuri da Wasshoi (SNES, Banpresto 1994)

You translate part of the Japanese script of this game into English for a fan patch. It is a light, goofy action game:
the Compati Heroes (SD Ultraman Great, Kamen Rider Black RX, Gundam GP03 Stamen and the original hero Roa) defend a
festival town, Neo Asakusa, from kaiju and mobile suits. Tone: comedic, festival banter, hammy villains, stall keepers'
patter. The sound-test notes (ids 0A2-0C4) are joke comments by the developers about each music track.
Work only on the batch named in your dispatch. Do all translation yourself; do not dispatch subagents.

## Read first
1. `glossary.md` - rulings and names (binding). `work/tl/terms_<batch>.txt` lists the rows that occur in your batch.
2. `docs/re/text.md` section "Codes" if a control code puzzles you.

## Input: `work/tl/<batch>.tsv`
`id<TAB>speaker<TAB>box<TAB>Japanese`. Box = `WxR`: W tiles per line (1 tile = 1 letter, space or punctuation mark),
R rows per page. Lines are in game order; neighbouring ids are often the same scene - use them for context.
Japanese codes: `{n}` line break, `{page}` new page, `{key}` wait for button, `{wait:XX}` timed pause,
`{fast}`/`{slow}` print instantly / normally (used around speaker names and whole messages), `{end}` end.

## Output: `work/tl/<batch>.out.tsv`, written with your file-write tool (not a shell heredoc)
`id<TAB>English`, every input id exactly once, same order. Plain ASCII only: letters, digits, space and
`! ? ( ) : / " . ' , -` (no other punctuation exists in the font: no `;`, `&`, `*`, `%`, `+`, `=`).
- Copy `{fast}`, `{slow}` and `{end}` exactly (same count). Keep every `{key}` (you may add more), and keep
  `{wait:XX}` pauses where the beat matters (count is free).
- Do NOT write `{n}` for normal line breaks: the build word-wraps each page to its box. Use `{n}` only after a
  speaker-name line (`{fast}Great{slow}{n}"...`), and for deliberate layout (sound-test titles, lists).
- A page holds about W x R letters when packed (R lines of W). If the English needs more room, split it into more
  pages: every `{page}` must come right after `{key}` (player presses a button) or `{wait:XX}` (auto-advance;
  use the same XX as the Japanese page it splits, `{wait:20}` or more for a long page). Messages with no `{key}`
  and no `{page}` (shop lines, character profiles) must fit ONE page: rephrase, don't add pages there.
- Leading spaces: keep the Japanese indentation only where it is layout (centred titles); drop full-width
  indent spaces at the start of normal lines.
- Check any message's layout: `python -X utf8 tools/batches.py fit <HDR> "<English>"` (HDR = the box header;
  `tools/batches.py fit C192 "..."`) - the header for an id is in `script/msg.json` ("hdr").

## Validate
Run `python -X utf8 tools/batches.py check <batch>` from the repo root and fix every reported id until it prints OK.

## Style
- Faithful: keep the information and order of ideas; adapt idiom, not meaning. Don't add details the Japanese
  doesn't state; don't summarise or skip. Adapt wordplay so the joke still lands (no translator notes).
- Names and terms exactly as in the glossary. Never abbreviate to fit; if a line can't fit without losing meaning,
  add a page (where allowed) and report `LONG: id`.
- Honorifics kept (-san, -sama, -kun...), Japanese name order. Hepburn without macrons for names not in the glossary.
- Punctuation: 「」 -> "...", ”...” -> "...", ・・・ / 、、、 -> `...`, ！！ -> `!!`, ？ -> `?`, ～ -> drop or `-`.
- Voices: RX and Great talk rough and Edo-casual ("Ain't", "pal"); Stamen calm; Roa an eager young hero; villains
  hammy; stall keepers chirpy patter ("Step right up!"). Emmy (guide) cheerful.

## Consistency
Never edit `glossary.md`. For a recurring name or term not in it, pick a form, use it consistently, and report it.

## Report (reply with only this)
Files written and entry count; then any lines: `NEW TERM: jp -> en`, `UNSURE: id - note`, `LONG: id - note`.
