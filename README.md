# PlayingCards.io Authoring Kit

Reverse-engineered reference and tooling for building **playingcards.io** virtual
tabletop rooms by editing the `.pcio` file directly, rather than clicking through
the in-app editor.

Maintained for Grow Giant Games tables (You Cheated!, Worlds Apart, Rogues to
Riches). Written to be usable from claude.ai Projects and from Claude Code.

## Why edit the file directly?

A `.pcio` export is just a ZIP whose main payload, `widgets.json`, is a flat,
human-readable list of every widget on the table. That means repetitive or precise
work — defining 20 custom cards, wiring per-player automation buttons, resetting a
room to a clean starting state — can be done with a script far faster and more
reliably than dragging in the editor. You then re-import the file into a fresh room.

## What's here

| Path | What it is |
|------|------------|
| `docs/pcio-format.md` | The file format and the widget schema (archive layout, every widget type's fields). |
| `docs/automation-reference.md` | How automation buttons work: the `clickRoutine` structure and the function/argument schema, with confirmed vs. not-yet-captured functions. |
| `docs/limitations.md` | What the platform **cannot** do (no conditional logic), plus the gotchas that bite you. |
| `tools/pcio_unpack.py` | Unpack a `.pcio` into a directory and pretty-print `widgets.json`. |
| `tools/pcio_pack.py` | Repack a directory into a valid `.pcio` (correct ZIP structure). |
| `examples/you-cheated/MAPPING.md` | Worked example: the You Cheated! table — widget IDs, mechanics, and what was changed. |

## Core workflow

```bash
# 1. Unpack
python3 tools/pcio_unpack.py mytable.pcio work/

# 2. Edit work/widgets.json  (by hand or with a script)

# 3. Repack
python3 tools/pcio_pack.py work/ mytable-v2.pcio

# 4. Import at https://playingcards.io/import  (into a NEW room, so the original is safe)
```

## Ground truth vs. inference

Everything here was derived from (a) real `.pcio` exports and (b) the official docs
at <https://playingcards.io/docs/>. Where a detail is confirmed from an actual file
it is stated plainly; where it is inferred or not yet captured it is marked **TODO**
or **unverified**. Treat the marked items as "verify before relying on," and when you
confirm one, update the doc. The fastest way to capture an unknown is the
**discovery recipe** in `docs/automation-reference.md`: build the feature once in the
app, export, unpack, and read the JSON it produced.

## Status of the knowledge base

- Format + widget schema: **confirmed** from exports.
- `MOVE_CARDS_BETWEEN_HOLDERS`, `CHANGE_COUNTER`: **confirmed** (args documented here).
- Other automation functions (shuffle, flip, rotate, sort, shift, recall, dice,
  spinner, timer, chooser, stand-up, finish-turn, reverse-turn): **names not yet
  captured** — use the discovery recipe.
