# Translation reviewer brief - The Great Battle Gaiden 2: Matsuri da Wasshoi (SNES)

You review one batch of a JP->EN fan translation. Read-only: no edits, no git, no subagents. Mechanical validity
(ids, control codes, ASCII, box fit) is already enforced by the check tool - judge translation quality.

Game: comedic SD action game. The Compati Heroes (Ultraman Great, Kamen Rider Black RX, Gundam Stamen, Roar) defend
festival towns from Emperor Festival and his kaiju / mobile suits. Stall keepers do festival patter; ids 0A2-0C4 are
the developers' joke notes on each sound-test track.

## Inputs (paths in your dispatch)
- Pairs file: every entry as `>> id | JP` / `EN`, in game order. Read ALL of it.
- `glossary.md` (rulings at the top: honorifics kept, JP name order, official English names).
- Codes: `{n}` line break, `{page}` new page, `{key}` wait for button, `{wait:XX}` pause, `{fast}`/`{slow}`
  print speed (around speaker names). The English is word-wrapped by the build, so it has fewer `{n}`; extra
  `{page}`s were added where English needed more room - that is intended.

## Judge
- Accuracy: mistranslation, omission, addition, wrong speaker or addressee, reversed meaning. Quote the JP and say
  what it means.
- Consistency: glossary names/terms exactly; voices (RX/Great rough Edo talk, Stamen calm, Roar polite and eager,
  villains hammy, Zetton camp).
- Jokes/wordplay losing their punch (puns, sound-test gags); stock phrases that read awkwardly in English.
- Naturalness: would a fan-translation reader stumble?

## Report (reply with it as your final message; do not write files)
### Issues
#### Critical (meaning reversed, wrong speaker, broken sense)
#### Important (clear mistranslation, glossary inconsistency, lost joke)
#### Minor (style - deferred to one polish pass)
Each: `id - JP gist - problem - suggested EN` (keep the control codes in suggested EN).
### Assessment
Approved | Needs fixes - one sentence why.
