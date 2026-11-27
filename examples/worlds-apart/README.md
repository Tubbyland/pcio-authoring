# Worlds Apart — playtest room

A generated playingcards.io room for Worlds Apart online playtests. Unlike the
You Cheated! example (an exported room edited by hand), this table is built from
scratch by a script, so it can be rebuilt whenever the card sheets change.

| File | What it is |
|------|------------|
| `cards.json` | Card data, copied from the Google Drive card sheets (WA - PLACES v2, TERRAIN EVENTS v2, CARAVAN EVENTS v2, ITEMS v2, COUNCIL CARDS v2). |
| `build_room.py` | Draws every card face as an SVG and lays out the table. Stdlib only. |
| `worlds-apart-room.pcio` | The built room, ready to import. |
| `layout-mock.png` | A browser mock of the layout. The real room will differ a little. |

## Rebuild after card changes

1. Update `cards.json` from the Drive sheets. Keep the column order given in the
   `*_cols` keys. Leave blank fields as `""` or `"[BLANK]"`; the cards show them as
   `[blank]` or `[Untitled P04]`. Rows with no Card ID are left out.
2. Build and pack:

```bash
cd examples/worlds-apart
python3 build_room.py cards.json build/
python3 ../../tools/pcio_pack.py build/room worlds-apart-room.pcio
```

3. Import into a **new** room at <https://playingcards.io/import>.

Every build shuffles the decks and gives the room fresh widget IDs.

## Layout

Table about 1600 × 1000.

- **Role panels** (top): Pathfinder, Marshal, Elder, Caretaker. Each has a score
  track counter (0–10, starts at 5), AP and VP. The space on the right is for that
  role's face-up Items.
- **The Horizon**: open area for revealed Places.
- **The Path**: three fixed slots (the three-Place window), each with its own
  Progress counter. Tokens don't follow cards in PCIO, so counters avoid stray
  Progress tokens when a Place moves on.
- **Sequence** counter (0–4) and a holder of four role tokens to mark whose
  sequence is running.
- **Flood** and **Timing** token supplies.
- **Pending Events**: open area; put Timing tokens on the cards.
- **Flood Track**: open area for reached Places. The starting Camp (P21) begins here.
- **Decks**: Places and Terrain Events by terrain, each with a discard; Caravan
  Events with an in-play area and a Caravan AP counter; Relic; Council Cards and
  discard; Hunger, Malaise, Injury (10 each); Items and discard.
- **Counters**: Food 20, Population 20, Supplies 20, Round 1.
- **Dice as decks**: Plains, Forest, Mountains and d10 are 10-card decks. Press
  Recall & Shuffle, then flip the top card. The Plains die has the 7 faces from
  the bible plus 3 blank ones; Forest and Mountains faces are all blank. Draw two
  from the d10 for a Relic roll.
- **Hand dock** (bottom): each player's private hand on their own screen.

Everything is manual. There are no automation buttons.

## Status

- **Import-tested 27 Nov 2026.** Card faces, coloured holder backgrounds, custom
  token images and counter sizes all display correctly.
- `autoShuffle` is **off** on every collection. With it on, the importer shuffled
  card types across piles (Forest Places in the Plains pile, Hunger cards showing
  Malaise, the starting Camp replaced). The builder shuffles each pile itself.
- Each pile is its own collection, and only the dice have a Recall & Shuffle
  button, so recalling one pile can't pull cards off the table or out of hands.
  To shuffle any other pile, use its stack menu (click the count tab).
- Players sharing one device share one hand dock, so their hands mix.
- Mountain Pass (P03) is shuffled into the Mountains deck; its placement is an
  open design question.
- Role colours avoid green and grey-blue pairings, and every card also names its
  roles and terrain in text.
