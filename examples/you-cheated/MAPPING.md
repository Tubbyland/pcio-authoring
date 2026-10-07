# Worked Example: the You Cheated! table

A real table, used here to show how the schema maps onto a game and how edits were
made. IDs are from the actual export (schemaVersion 8) and will differ in your copy —
re-derive them by unpacking your own file.

## Game (current rules)

Five-card draw. Custom **Cheat** cards are wild. At showdown the player who revealed
the **most Cheats loses a life and is knocked out of the pot** (so the pot goes to
the next-best hand). Ties on Cheat count: nobody loses a life. Deck starts with 6
Cheats and gains 2 after each round, reaching 20 by the 8th and final round. Players
start with 3 lives and 100 chips; 5-chip ante. **No chip↔life exchange in either
direction.** A player may **bet a life** to stay in without chips; if they win the
pot they **reclaim that life**.

## Widget map (this export)

| Role | Type | ID |
|------|------|----|
| Draw deck | holder | `TqY9lI48` ("Deck") |
| Cheat reserve | holder | `XOuPPggT` ("Wild Cards") |
| Standard 52 collection | cardDeck | `qZYu4eqG` |
| Cheat collection (20) | cardDeck | `XVsC5jPr` |
| Pot | holder | `PQJWcdDd` ("Place your bets!") |
| Discard | holder | `aBG899CE` |
| Round counter (1–8) | counter | `Wv2cbSAp` |
| Seats P1–P4 | seat | `ZJk8BQFa`, `YdeGNkH6`, `VJ6xUnmG`, `9t8ayUfE` |
| Lives holders P1–P4 | holder | `bOD3NPH8`, `UqW1Ux4r`, `CB4EhN1K`, `cqJMUG3W` |
| Life collections P1–P4 | cardDeck | `oLTI6DVk`, `St89kjXZ`, `ZV5zvOKS`, `l7Gi74wK` |
| Chip collections P1–P4 | cardDeck | `VLtxvD9n`, `cYxjrL34`, `2gL52gpe`, `k3PPxPLa` |
| Winnings/stack holders P1–P4 | holder | `C5PGwBNB`, `bBpR3P9c`, `c4MjoA0H`, `trrqJTu7` |
| Deal buttons P1–P4 | automationButton | `Eo3xw3Im`, `WfFaP6v3`, `cqFM9Jba`, `c987m3bN` |
| Lost Lives holder (added) | holder | `lostLives1` |

Lives and chips are **objects**, not counters: each life is a card in a per-player
life collection (3 each); each chip is a piece in a per-player chip collection
(100 each).

## Edits made (v2 → v3)

**v2 — logic + clean start**
- Deal buttons: set `quantity` to **5** and `moveFlip` to `faceUp` (they had no
  quantity, so each dealt the whole deck).
- "Next Round": appended a step moving **2 Cheats** from reserve `XOuPPggT` → deck
  `TqY9lI48` (face down), so escalation 6→20 is automatic.
- Clean round-1 state: gathered all 52 standard cards into the deck (9 were stranded
  in the `hand` dock from testing), seeded **6 Cheats** into the deck with **14** in
  reserve, cleared `seatedUser` on the two test seats.
- Repurposed "Add to Deck" → **"+2 Cheats"** (quantity 2) as a manual backup.
- Chips left at 100 per player.

**v3 — life tokens**
- Added per-player **"Bet a Life"** buttons: move 1 life from the player's Lives
  holder → pot `PQJWcdDd`.
- Added per-player **"Lose a Life"** buttons: move 1 life from the player's Lives
  holder → new **Lost Lives** holder `lostLives1` (kept separate from the discard so
  lost lives are never dealt as cards).
- Set the pot's `allowedDecks` to null so a life token can enter it.

**v3 play-test fix (made in-app by Sam)**
- "Next Round" now ends with a **Shuffle** step on the deck. Without it, the 2 Cheats
  added each round landed on top of the deck and stayed there (auto-shuffle does not
  cover moved cards). The exact JSON for this step is pending capture from an export.
- Play-test confirmed the escalation curve: Round 3 showed deck 62 (52 + 10 Cheats),
  reserve 10.
- Layout: P2/P3 "Bet a Life"/"Lose a Life" buttons overlap the bottom hand dock;
  nudge in Edit Mode.

## Not automatable (and why)

- **"Most Cheats loses a life"** — needs counting + comparison across hands. The
  engine has no conditional logic, so this is enforced by a human clicking the
  loser's "Lose a Life" button.

## Planned next (v4)

- Per-player **"Reclaim Life"**: move the player's own life token out of the pot
  back to their Lives holder, scoped by that player's life collection (see
  `../../docs/automation-reference.md` §6). Only the bettor, only on a win.
- Fix the Rules `urlButton` to a public link (currently a private Drive URL).
