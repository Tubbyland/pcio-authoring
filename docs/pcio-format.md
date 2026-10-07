# The `.pcio` File Format and Widget Schema

*Confirmed from real exports (schemaVersion 8). Fields marked **unverified** have
not been observed directly.*

## 1. Archive structure

A `.pcio` file is a **ZIP archive, stored uncompressed** (compression method
`store`). Re-pack with `ZIP_STORED` to match what the platform produces.

Contents at the archive root:

```
schemaVersion        # text, e.g. "8"
variantId            # text, opaque room-variant id
variantDate          # text, epoch milliseconds
widgets.json         # the whole table (see below)
userassets/          # custom art referenced by custom decks
  <uuid>.png | .svg | .jpg
```

Notes:
- Keep all four root entries plus `userassets/` on a repack. An explicit
  `userassets/` directory entry is optional; the asset files carry the prefix.
- Do not rename asset files; custom card `image` fields point at these paths.
- Importing creates a **new room**, so `variantId`/`variantDate` need not be
  regenerated for a working import.

## 2. `widgets.json`

A single **flat JSON array**. Each element is one widget (a card, a holder, a
button, a chip, a seat, …). There is no nesting; parent/child relationships are
expressed by ID references (`parent`, `layoutStackParent`).

Every widget has at least:

| Field | Meaning |
|-------|---------|
| `id` | Short unique string (e.g. `"TqY9lI48"`), or a fixed name like `"hand"`. Referenced by other widgets and by automations. |
| `type` | Widget type (see §3). |
| `x`, `y` | Position in pixels; origin is top-left of the table. |
| `z` | Stacking order; higher is on top. |

Optional common fields: `width`, `height` (omit to use the type's default size),
`parent`, `owner`, `dragging`, `draggingType`, `label`.

### Coordinate / layout tips
- The table is a large plane; observed tables span roughly `x: 0–1530`,
  `y: 36–900`. Place new widgets in open bands and nudge in-app afterward.
- Cards inside a holder are laid out by the holder, so exact `x/y` on a held card
  matters little. Stack **order**, however, is not randomised for you — see the
  `autoShuffle` note below.

## 3. Widget types

Observed in real files: `card`, `piece`, `holder`, `cardDeck`, `seat`, `hand`,
`automationButton`, `urlButton`, `counter`. Documented but not yet observed in an
export: dice, spinner, timer, chooser (**unverified** schema).

### 3.1 `cardDeck` — a collection definition
Defines a set of card (or piece) faces; the "home" collection a `card`/`piece`
belongs to via its `deck` field.

| Field | Meaning |
|-------|---------|
| `collectionName` | Human label (e.g. `"Wild Cards"`, `"P1 Chips"`); may be null. |
| `cardTypes` | Dict `cardTypeKey -> {label, image}`. For the standard deck, keys look like `spades-a`, `hearts-10`, plus `joker-black/red/blue`. Custom decks use keys like `type-<uuid>` with `image` pointing at `/img/...` or a `userassets/...` file. |
| `cardWidth`, `cardHeight` | Card size. |
| `faceTemplate`, `backTemplate` | Rendering templates (layers). |
| `autoShuffle` | Collection-level shuffle setting. **Tested: it does NOT shuffle cards that an automation moves into a holder** — moved cards land on top and stay there. Add an explicit shuffle step after any move into a draw deck. |
| `showUnflipped`, `hasShuffleButton`, `mainBorderRadius`, `collectionType` | Display/behaviour options. |

A collection's cards can far outnumber its `cardTypes` (duplicates via multi-deck).

### 3.2 `card`
| Field | Meaning |
|-------|---------|
| `deck` | ID of the `cardDeck` collection it belongs to. |
| `cardType` | Key into that deck's `cardTypes`. |
| `parent` | ID of the holder/seat it sits in, `"hand"` for the hand dock, or null when loose on the table. |
| `layoutStackParent` | ID of the stack root when stacked (null if not). |
| `faceup` | Boolean. In a private seat, face-up shows the face to the seated player only. |
| `owner` | User ID of the owning player, or null. |
| `x`, `y`, `z` | Position / stack order. |

### 3.3 `piece` — tokens (e.g. chips)
Like a card but typically no `faceup`. Has `deck` (the piece collection, e.g.
`"P1 Chips"`), `cardType` (e.g. `"white"`), `parent`, `x/y/z`, optional `label`.

### 3.4 `holder`
A container that organises objects and is the target/source of most automations.

| Field | Meaning |
|-------|---------|
| `label` | Top label text. |
| `allowedDecks` | List of collection IDs permitted to be placed here, or null for "any". Relax to null if an automation must move an unexpected object type in. |
| `width`, `height` | Size (applied before rotation). |
| `layoutType` | `Pile` (stack), `Spread`, `Grid`, or `Freeform`. |
| `hideStackTab` | Hide the count tab. |
| `enableChildrenSnapToSimilar` | Freeform snapping. |
| `mainBackground`, `mainOutlines`, `mainTextStyle` | Styling (optional). |

### 3.5 `seat` (Player Seat)
| Field | Meaning |
|-------|---------|
| `seatIndex` | Turn order (0-based). |
| `seatedUser` | User ID of the occupant, or null. **Clear this to reset a room** that holds a live test. |
| `seatColor`, `seatInitials`, `seatLabel` | Per-seat display. |

Players press Enter to sit. A `hand`/seat's contents are private to the occupant.
Move Objects targeting a seat moves to/from that seated player's hand. There is **no
"current player" token** — to act per player you need one widget per seat (see the
You Cheated example).

### 3.6 `hand`
The bottom hand dock; a single special widget with the fixed id `"hand"`. Leave it
in place; don't rebuild its contents from tool output.

### 3.7 `counter`
| Field | Meaning |
|-------|---------|
| `label`, `counterValue`, `counterMin`, `counterMax`, `owner` | Self-explanatory; value is clamped to min/max. |

### 3.8 `automationButton`
See `automation-reference.md`. Key fields: `label`, `clickRoutine`, `x/y/z`,
optional `width`/`height`.

### 3.9 `urlButton`
`label` + `clickURL`. Opens a link (e.g. a rules PDF). Note: a private Google Drive
link only works for people with access — use a public link or the itch.io page for
a shared table.

## 4. Collections vs. holders (important mental model)

- A **collection** (`cardDeck`) is the *home identity* of a set of cards/pieces —
  "these 20 are the Cheats," "these are P1's chips."
- A **holder** is a *place on the table* where objects currently sit.
- Automations can select objects **by holder** ("whatever is in the Deck") or **by
  collection** ("all the Cheats, wherever they are"). Choosing the right selector is
  most of the skill: collection-based selection is how you reliably round up a
  specific player's tokens no matter where they ended up.
