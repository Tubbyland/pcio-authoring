# Automation Reference

Automation buttons run a fixed list of steps, in order, with **no conditional
logic** (see `limitations.md`). This file documents the `clickRoutine` structure and
the argument schema, separating what is **confirmed** from a real file vs. not yet
captured.

## 1. `clickRoutine` structure

```jsonc
"clickRoutine": {
  "steps": [
    {
      "id": "<string>",
      "branches": [
        { "func": "<FUNCTION_NAME>", "args": { ... } }
      ]
    }
    // ...more steps, executed top to bottom
  ],
  "popupMessage": "Are you sure?"   // optional confirmation prompt
}
```

- `steps` run sequentially, one by one.
- `branches` has been observed only ever as a **single-element array** — treat it as
  the container for the step's action, not as conditional branching. The platform
  exposes no if/then, so do not expect multiple branches to mean a condition.
- `popupMessage` (optional) shows a confirm/input popup before the routine runs. The
  popup can also collect a number or an object selection from the player.

## 2. Value wrappers

Arguments are wrapped to say where the value comes from:

- Literal: `{ "type": "literal", "value": <X> }`
- Query (select objects): `{ "type": "query", "queryWidgetTypes": ["card","piece"],
  "holders": [<id>...], "collections": [<id>...] }`
  - Give `holders` to select "objects currently in these places," and/or
    `collections` to select "objects belonging to these collections, wherever they
    are." Use an empty list for one you don't need.
- Counter reference (for quantities/numbers): **documented** (Move's quantity and
  Change Counter can read another counter) but the exact JSON is **unverified** —
  capture it with the discovery recipe before relying on it.

## 3. Confirmed functions

### 3.1 `MOVE_CARDS_BETWEEN_HOLDERS`
Moves objects from selected sources to one or more destination holders/seats.

```jsonc
{
  "func": "MOVE_CARDS_BETWEEN_HOLDERS",
  "args": {
    "objects":  { "type": "query",
                  "queryWidgetTypes": ["card"],         // or ["card","piece"]
                  "holders": ["<sourceHolderId>"],      // and/or:
                  "collections": ["<collectionId>"] },
    "to":       { "type": "literal", "value": ["<destHolderOrSeatId>"] },
    "quantity": { "type": "literal", "value": 5 },      // a number, or "all"
    "moveFlip": { "type": "literal", "value": "faceUp" } // "faceUp" | "faceDown"
  }
}
```

- **Quantity gotcha (confirmed):** if `quantity` is omitted, the move takes the
  **entire** source. Always set a number for "deal N." The docs phrase the inverse:
  "to deal the entire pile, set the number larger than the pile, e.g. 1000."
- `to.value` is a **list**; multiple destinations distribute "N to each."
- `moveFlip` values confirmed: `"faceUp"`, `"faceDown"`. A "keep as-is" option is
  documented in the UI; its literal value is **unverified**.
- Targeting a **seat** as destination deals into that seated player's private hand.

### 3.2 `CHANGE_COUNTER`
```jsonc
{
  "func": "CHANGE_COUNTER",
  "args": {
    "counterChangeMode": { "type": "literal", "value": "inc" }, // "inc"|"dec"|"set"
    "changeNumber":      { "type": "literal", "value": 1 },
    "counters":          { "type": "literal", "value": ["<counterId>"] }
  }
}
```
- Value is clamped to the counter's `counterMin`/`counterMax`.
- UI modes "Increase By / Decrease By / Set To" map to `inc` / `dec` / `set`.

## 4. Functions documented but not yet captured

These automations exist in the UI (so they're usable), but their exact `func`
strings and `args` have **not been observed** in a file yet. Do not guess the
string — capture it (see §5). UI names, for orientation:

- Shift Objects (move along an ordered path of holders, N steps, wrap/edge)
- Recall Objects (gather a **collection** back to its deck home; options "Include
  Holders", "Include Hands", "Flip Cards")
- Flip / Rotate / Shuffle / Sort Objects
- Change Dice, Spin Spinner, Start/Pause Timer, Change Timer, Change Chooser
- Stand Up Players, Finish Turn, Reverse Turn Direction

Note: in existing tables, a "recall everything to the deck" effect is often built
with `MOVE_CARDS_BETWEEN_HOLDERS` using a `collections` query, rather than the
dedicated Recall function — that pattern is confirmed and reliable.

## 5. Discovery recipe (how to capture an unknown function)

1. In the app (Edit Mode), create an automation button that does the one thing you
   want (e.g., a Shuffle step).
2. Export the room (briefcase → Room Options → Export).
3. `python3 tools/pcio_unpack.py that.pcio work/`
4. Open `work/widgets.json`, find your button, and copy the exact `func` + `args`.
5. Add it to §3 of this file so it becomes confirmed knowledge.

## 6. Per-player pattern (because there is no "current player")

To give each player their own action, create one button per seat, each hard-wired to
that player's holder/collection. Example — "reclaim my bet life" for player 1, i.e.
pull P1's own life token back out of the shared pot:

```jsonc
{
  "func": "MOVE_CARDS_BETWEEN_HOLDERS",
  "args": {
    "objects":  { "type": "query", "queryWidgetTypes": ["card"],
                  "holders": ["<potHolderId>"],
                  "collections": ["<p1LifeCollectionId>"] }, // only P1's life
    "to":       { "type": "literal", "value": ["<p1LivesHolderId>"] },
    "quantity": { "type": "literal", "value": "all" },
    "moveFlip": { "type": "literal", "value": "faceUp" }
  }
}
```
The `collections` filter is what makes it safe when several players have tokens in
the same pot.
