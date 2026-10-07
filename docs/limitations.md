# Limitations and Gotchas

## 1. No conditional logic (the big one)

playingcards.io automations are a **fixed, sequential list of steps**. There is:

- no if/then/else,
- no counting objects and comparing between players,
- no branching on game state,
- no "winner" or "most/least" detection.

Confirmed from the docs ("the automation will go through the steps and run each in
order one-by-one") and from inspecting real files (no condition fields anywhere in
`clickRoutine`).

**Design consequence.** Any rule of the form "whoever has the most/least X ..." or
"if a player's count reaches Y ..." **cannot be enforced by the table.** It stays a
human judgment. The best you can do is make the *consequence* one click:

- Example (You Cheated!): "the player who revealed the most Cheats loses a life"
  cannot be auto-detected. Instead each seat gets a **"Lose a Life"** button; a human
  eyeballs the showdown and clicks the loser's button.

What a popup *can* do is collect a number or let the clicker pick an object — useful
input, but still not a computed decision.

## 2. Deal quantity defaults to "all"

A `MOVE_CARDS_BETWEEN_HOLDERS` with no `quantity` moves the **entire** source. A
"Deal" button with the field left blank deals the whole deck to one seat. Always set
a number.

## 3. Recall / move destinations matter — don't shuffle stray cards into the deck

If a "Next Round" routine recalls a holder (e.g. a discard) back into the draw deck,
anything sitting in that holder goes too. Keep off-deck items (lost life tokens,
bet tokens) in **their own holders**, never the discard, or they'll be dealt as
cards next round. Select by **collection** when you need to move only one kind of
object out of a mixed holder.

## 4. `allowedDecks` can reject a move target

A holder with `allowedDecks` set will refuse objects outside that list. If an
automation must move an unexpected type in (e.g., a life *card* into a chip *pot*),
set the destination holder's `allowedDecks` to null.

## 5. Rooms expire

Rooms are removed after inactivity (2 weeks; 30 days with an account). A permanent,
always-available or lockable table needs the paid subscription. For sharing, keep
the authoritative room as the `.pcio` file in version control and re-import as
needed.

## 6. Custom card art needs direct, public URLs

Image layers must point to a **direct image file URL** (or a bundled
`userassets/...` file). A link to a Dropbox/Drive *page* won't render. Text-only
custom cards (no image) are the zero-friction option.

## 7. Repack correctly

Re-zip with **store** (no compression) and keep the root files
(`schemaVersion`, `variantId`, `variantDate`, `widgets.json`) plus `userassets/`.
`tools/pcio_pack.py` does this.

## 8. Always import into a NEW room when testing

Importing into an existing room **replaces** its contents. Import edited files into a
fresh room (<https://playingcards.io/import>) so an in-progress game is never lost.

## 9. Can't fully test from outside the app

Editing JSON is reliable for structure and wiring, but the only way to confirm an
automation *behaves* is to import and click it. Build, import, click one round,
adjust. Keep changes small and verifiable.
