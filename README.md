# The Great Battle Gaiden 2: Matsuri da Wasshoi — English patch

A full English fan translation of **The Great Battle Gaiden 2: Matsuri da Wasshoi** (ザ・グレイトバトル外伝2 まつりだワッショイ,
Banpresto, Super Famicom, 1994). Text and the Japanese baked into graphics are translated; there is no Japanese-only
screen left that I know of, apart from the items under *Known issues*.

Version **1.1**.

Changes in 1.1: the Winter-castle boss flag no longer says 大安売.

**Found a bug?** [Report it](../../issues/new/choose): untranslated text, typos, overflow, crashes. Attaching a savestate
helps most.

## Translation status

| Part | Status |
|---|---|
| All 198 script messages (story, bosses, stall keepers, Emmy's guide, game corner, BGM commentary), reviewed | Translated |
| Title screen and logo, menus, password screen, game over / continue, HUD, shop, player select | Translated |
| Stage banners (SPRING / SUMMER / AUTUMN / WINTER FESTIVAL), stall item names and signs, attract-mode copyright cards, ending picture signs | Partly translated (Kaminarimon gate kanji signs kept; one autumn bridge-board line may be Japanese) |
| Game Corner minigames (menu, stage select, shooting shop, puzzle labels SCORE / LEVEL / NEXT / FULL, Chick Catch, GAME OVER / GAME CLEAR banners) | Translated |
| THE END and the full staff roll | Translated (some lines shortened to fit) |

Known issues: see [Known issues](#known-issues) below.

Naming: official English names for the Compati Heroes where they exist (Great, RX, Roar...), otherwise Hepburn without
macrons. Honorifics are kept and names stay in Japanese order. Full list: `glossary.md`.

Tip: advance dialogue with **B**, as in the original.

## How to patch

You need your own dump of the Japanese ROM (header-less `.sfc`):

| | |
|---|---|
| Name | The Great Battle Gaiden 2 - Matsuri da Wasshoi (Japan).sfc |
| Size | 1,310,720 bytes (1.25 MB) |
| CRC32 | `83806E38` |
| SHA-1 | `76941A710D54943E30212B90C8A14DC1995FE3D2` |
| MD5 | `8C19E5107985ED27FAC3AD8BD2EB1D70` |

Apply `The Great Battle Gaiden 2 - English v1.1.bps` with [Floating IPS](https://github.com/Alcaro/Flips),
[RomPatcher.js](https://www.romhacking.net/patch/) or [beat](https://github.com/Themaister/beat). The result is a 2 MB
ROM (the extra space holds the English text and code):

| | |
|---|---|
| Size | 2,097,152 bytes |
| CRC32 | `2C174C5E` |
| SHA-1 | `0B2DAB658DD9290C0B52614AFFC39D4236A47A11` |
| MD5 | `2C44774F2E61571B8D50F61EC686A734` |

Tested on Mesen2 (headless and GUI). It should run on other accurate emulators and on flash carts that take 2 MB
LoROM; it has not been tested on real hardware.

## Known issues

- The Kaminarimon gate in the Asakusa boss room still shows its real-world kanji signs (雷門 lantern, 金龍山 plaque).
- A second text line on the autumn bridge board (a tile set that never appeared in my playthroughs) may still be Japanese.
- Staff roll lines are shortened where the original space ran out (e.g. "OP/ED Program", "Software Team").
- Stage banner words are split in two lines (SPR/ING, SUM/MER...) because six letters do not fit one sprite.

Please report anything else you find as an issue, with a screenshot or savestate.

## Building from source

Needs Python 3.12 with Pillow, the original ROM at `rom/orig.sfc`, and [asar](https://github.com/RPGHacker/asar)
at `tools/asar/asar.exe`.

```
python -X utf8 tools/build.py          # -> build/gbg2_en.sfc
python -X utf8 tools/check.py          # tests + text lint
```

Layout: `script/msg.json` (Japanese and English side by side), `asm/main.asm` (engine patches), `gfx/` (graphics
scripts and PNGs), `docs/re/` (reverse-engineering notes), `CLAUDE.md` (commands, findings, QA helpers such as the
password/scene warp used to reach every stage and boss).

## Credits

Translation and hacking: minhnhattonthat, with AI assistance (Claude; script review by a second model).
Original game © Banpresto 1994; Kamen Rider © Ishimori Pro / Toei, Ultraman © Tsuburaya Pro, Gundam © Sotsu Agency /
Sunrise. This is an unofficial fan project, not affiliated with or endorsed by any rights holder. The patch contains no
original game data; do not ask for ROMs.

## Support

If you enjoy this translation, you can support my work on Ko-fi:

[![Support me on Ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/minhnhattonthat)
