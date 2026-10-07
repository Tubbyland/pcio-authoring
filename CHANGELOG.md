# Changelog

## 2026-10-07 — initial
- First reverse-engineered reference of the `.pcio` format and `widgets.json`
  schema (schemaVersion 8), from real exports plus playingcards.io docs.
- Confirmed automation functions `MOVE_CARDS_BETWEEN_HOLDERS` and `CHANGE_COUNTER`
  with argument schema; recorded the "quantity defaults to all" gotcha.
- Documented the no-conditional-logic limitation and its design consequences.
- Added `tools/pcio_unpack.py` and `tools/pcio_pack.py`.
- Added the You Cheated! worked example (widget map, v2/v3 edits).

### Open TODOs
- Capture exact `func`/`args` for shuffle, flip, rotate, sort, shift, recall, dice,
  spinner, timer, chooser, stand-up, finish-turn, reverse-turn (discovery recipe in
  `docs/automation-reference.md` §5).
- Verify the counter-reference value wrapper and the "keep as-is" flip literal.
