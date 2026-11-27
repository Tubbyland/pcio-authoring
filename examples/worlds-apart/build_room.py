"""Build a playingcards.io room (.pcio) for Worlds Apart from cards.json.

Usage: python3 build_room.py cards.json out_dir/
Writes out_dir/room/ (unpacked) ready for pcio_pack.py.
"""
import json, os, random, sys, time, uuid
from xml.sax.saxutils import escape

random.seed()
SRC, OUT = sys.argv[1], sys.argv[2]
D = json.load(open(SRC))
ROOM = os.path.join(OUT, "room")
os.makedirs(os.path.join(ROOM, "userassets"), exist_ok=True)

FONT = "Arial, Helvetica, sans-serif"
ROLE_COL = {"Pathfinder": "#d9701c", "Marshal": "#2b63c4", "Elder": "#a8286f", "Caretaker": "#c99a00"}
ROLE_TINT = {"Pathfinder": "rgb(251,231,212)", "Marshal": "rgb(220,232,250)", "Elder": "rgb(246,220,234)", "Caretaker": "rgb(246,237,196)"}
TRACK = {"Pathfinder": "Direction", "Marshal": "Safety", "Elder": "Harmony", "Caretaker": "Wellbeing"}
ROLES = ["Pathfinder", "Marshal", "Elder", "Caretaker"]
TERR_BG = {"Plains": "#f2e4b0", "Forest": "#cfe0c4", "Mountains": "#d9dbe3"}
PLAINS_DIE = ["Extra Progress: 1-2 tokens on the Place that rolled", "Reveal a Plains card", "Draw a Terrain Event",
              "Draw a Caravan Event", "Population Shift (based on Wellbeing)", "Supplies Gain (amount not set)",
              "No Effect", "[blank face]", "[blank face]", "[blank face]"]

def blank(v):
    return v is None or str(v).strip() == "" or str(v).strip().upper() == "[BLANK]"

def rid(n=8):
    return "".join(random.choice("abcdefghijkmnopqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ23456789") for _ in range(n))

# ---------------- SVG helpers ----------------
def wrap(text, size, width):
    per = max(4, int(width / (size * 0.53)))
    out = []
    for para in str(text).split("\n"):
        line = ""
        for w in para.split():
            cand = (line + " " + w).strip()
            if len(cand) <= per:
                line = cand
            else:
                if line:
                    out.append(line)
                while len(w) > per:
                    out.append(w[:per]); w = w[per:]
                line = w
        out.append(line)
    return out

class Svg:
    def __init__(s, w, h, bg="#ffffff"):
        s.w, s.h, s.parts = w, h, [f'<rect width="{w}" height="{h}" fill="{bg}"/>']
    def rect(s, x, y, w, h, fill, rx=0, stroke=None):
        st = f' stroke="{stroke}" stroke-width="0.8"' if stroke else ""
        s.parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}"{st}/>')
    def circle(s, cx, cy, r, fill, stroke="#1b2329"):
        s.parts.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{fill}" stroke="{stroke}" stroke-width="1"/>')
    def text(s, x, y, t, size, weight="normal", fill="#1b2329", anchor="start", italic=False, rotate=None):
        tr = f' transform="rotate({rotate} {x} {y})"' if rotate is not None else ""
        st = ' font-style="italic"' if italic else ""
        s.parts.append(f'<text x="{x}" y="{y}" font-family="{FONT}" font-size="{size}" font-weight="{weight}" fill="{fill}" text-anchor="{anchor}"{st}{tr}>{escape(str(t))}</text>')
    def para(s, x, y, t, size, width, **kw):
        lh = size * 1.18
        for ln in wrap(t, size, width):
            y += lh
            s.text(x, y, ln, size, **kw)
        return y
    def svg(s):
        return f'<svg xmlns="http://www.w3.org/2000/svg" width="{s.w}" height="{s.h}" viewBox="0 0 {s.w} {s.h}">' + "".join(s.parts) + "</svg>"

def lines_needed(t, size, width):
    return len(wrap(t, size, width)) * size * 1.18

ASSETS = {}
def asset(svg_text):
    name = f"{uuid.uuid4()}.svg"
    with open(os.path.join(ROOM, "userassets", name), "w", encoding="utf-8") as f:
        f.write(svg_text)
    return "package://userassets/" + name

GREY = "#6b7680"

# ---------------- card faces ----------------
PW, PH = 112, 186
EW, EH = 100, 150
IW, IH = 72, 100
CW, CH = 64, 90
DW, DH = 56, 56
TW = 26

def place_svg(r):
    c = dict(zip(D["places_cols"], r))
    terr = "" if blank(c["terrain"]) else c["terrain"]
    s = Svg(PW, PH, TERR_BG.get(terr, "#ffffff"))
    s.rect(0, 0, PW, 15, "#1b2329")
    s.text(5, 11, (terr or "No terrain").upper() + "  ·  " + c["id"], 7.5, "bold", "#ffffff")
    prox = None if blank(c["prox"]) else int(c["prox"])
    s.circle(PW - 13, 27, 10, "#ffffff")
    s.text(PW - 13, 31, prox if prox else "?", 11, "bold", anchor="middle")
    title = f"[Untitled {c['id']}]" if blank(c["title"]) else c["title"]
    y = s.para(5, 16, title, 9, PW - 32, weight="bold", fill=GREY if blank(c["title"]) else "#1b2329", italic=blank(c["title"]))
    y = max(y, 38)
    meta = "Flood slots: " + ("[blank]" if blank(c["flood"]) else c["flood"])
    if not blank(c["keywords"]):
        meta += "  ·  " + c["keywords"]
    s.text(5, y + 9, meta, 6.5, fill=GREY)
    y += 12
    n = max(prox or 0, max([i + 1 for i in range(6) if not blank(c[f"s{i+1}"])] or [0]))
    steps = [(i, "" if blank(c[f"s{i}"]) else c[f"s{i}"]) for i in range(1, n + 1)]
    size = 7.2
    need = sum(max(lines_needed(t or "-", size, PW - 20), size * 1.18) + 2 for _, t in steps)
    while need > PH - y - 4 and size > 5.2:
        size -= 0.3
        need = sum(max(lines_needed(t or "-", size, PW - 20), size * 1.18) + 2 for _, t in steps)
    if not steps:
        s.para(5, y, "No Proximity or steps set", 7, PW - 10, fill=GREY, italic=True)
    for i, t in steps:
        s.text(6, y + size * 1.1, str(i), size, "bold")
        if t:
            y = s.para(16, y, t, size, PW - 20) + 2
        else:
            s.text(16, y + size * 1.1, "-", size, fill=GREY); y += size * 1.18 + 2
        s.parts.append(f'<line x1="4" x2="{PW-4}" y1="{y}" y2="{y}" stroke="#00000022" stroke-width="0.6"/>')
    if not blank(c["desc"]) and PH - y > 22:
        room = PH - y - 4
        dsize = 6
        lines = wrap(c["desc"], dsize, PW - 10)
        maxl = int(room / (dsize * 1.18))
        if maxl >= 2:
            txt = lines[:maxl]
            if len(lines) > maxl:
                txt[-1] = txt[-1][:-3] + "..."
            yy = PH - 3 - len(txt) * dsize * 1.18
            for ln in txt:
                yy += dsize * 1.18
                s.text(5, yy, ln, dsize, fill=GREY, italic=True)
    return s.svg(), title

def event_svg(r):
    c = dict(zip(D["events_cols"], r))
    terr = "" if blank(c["terrain"]) else c["terrain"]
    s = Svg(EW, EH, "#ffffff")
    s.rect(0, 0, EW, 15, TERR_BG.get(terr, "#dddddd"))
    s.text(5, 11, f"EVENT · {(terr or '?').upper()} · {c['id']}", 6.8, "bold")
    t = c["timing"].strip()
    tlabel = "Imm" if (t.lower() == "immediate" or t == "0") else ("?" if blank(t) else t)
    s.circle(EW - 12, 26, 9.5, "#ffffff")
    s.text(EW - 12, 29.5, tlabel, 9 if len(tlabel) < 3 else 6.5, "bold", anchor="middle")
    title = f"[Untitled {c['id']}]" if blank(c["title"]) else c["title"]
    y = s.para(5, 15, title, 8.5, EW - 30, weight="bold", fill=GREY if blank(c["title"]) else "#1b2329", italic=blank(c["title"]))
    y = max(y, 38) + 2
    body = [c["a"]] + ([c["b"]] if not blank(c["b"]) else [])
    size = 7
    while sum(lines_needed(b, size, EW - 10) + 3 for b in body) > EH - y - 4 and size > 5:
        size -= 0.3
    for b in body:
        y = s.para(5, y, b, size, EW - 10) + 3
    if not blank(c["desc"]) and EH - y > 20:
        lines = wrap(c["desc"], 5.8, EW - 10)
        maxl = int((EH - y - 4) / (5.8 * 1.18))
        txt = lines[:maxl]
        if len(lines) > maxl and txt:
            txt[-1] = txt[-1][:-3] + "..."
        yy = EH - 3 - len(txt) * 5.8 * 1.18
        for ln in txt:
            yy += 5.8 * 1.18
            s.text(5, yy, ln, 5.8, fill=GREY, italic=True)
    return s.svg(), title

def caravan_svg(r):
    c = dict(zip(D["caravan_cols"], r))
    s = Svg(EW, EH, "#fff8ec")
    s.rect(0, 0, EW, 15, "#7a4a1d")
    s.text(5, 11, f"CARAVAN EVENT · {c['id']}", 6.8, "bold", "#ffffff")
    title = f"[Untitled {c['id']}]" if blank(c["title"]) else c["title"]
    y = s.para(5, 15, title, 8.5, EW - 10, weight="bold", fill=GREY if blank(c["title"]) else "#1b2329", italic=blank(c["title"]))
    rows = [c["a"]]
    if not blank(c["b"]): rows.append(c["b"])
    meta = []
    if not blank(c["persist"]): meta.append("Persistent: " + c["persist"])
    if not blank(c["ap"]): meta.append("AP to clear: " + c["ap"])
    if not blank(c["esc"]): meta.append("Escalation: " + c["esc"])
    size = 7
    allr = rows + meta
    while sum(lines_needed(b, size, EW - 10) + 3 for b in allr) > EH - y - 4 and size > 5:
        size -= 0.3
    y += 2
    for b in rows:
        y = s.para(5, y, b, size, EW - 10) + 3
    for b in meta:
        y = s.para(5, y, b, size, EW - 10, fill=GREY) + 2
    return s.svg(), title

def item_svg(r):
    c = dict(zip(D["items_cols"], r))
    s = Svg(IW, IH, "#fdfbf4")
    s.rect(0, 0, IW, 12, "#3b3f46")
    s.text(4, 9, f"ITEM · {c['id']}", 6, "bold", "#ffffff")
    title = f"[Unnamed {c['id']}]" if blank(c["name"]) else c["name"]
    y = s.para(4, 12, title, 7.5, IW - 8, weight="bold", fill=GREY if blank(c["name"]) else "#1b2329", italic=blank(c["name"]))
    rows = []
    if not blank(c["role"]): rows.append(("Role: " + c["role"], "#1b2329"))
    trig = "" if blank(c["trigger"]) else c["trigger"] + ": "
    rows.append(("Group: " + (trig + c["group"] if not blank(c["group"]) else "[blank]"), "#1b2329" if not blank(c["group"]) else GREY))
    rows.append(("Track: " + ("[blank]" if blank(c["track"]) else c["track"]), "#1b2329" if not blank(c["track"]) else GREY))
    if not blank(c["discard"]): rows.append((c["discard"], GREY))
    size = 6
    while sum(lines_needed(t, size, IW - 8) + 2 for t, _ in rows) > IH - y - 3 and size > 4.2:
        size -= 0.2
    y += 1
    for t, col in rows:
        y = s.para(4, y, t, size, IW - 8, fill=col) + 2
    return s.svg(), title

def cc_svg(a, b):
    s = Svg(CW, CH, "#ffffff")
    s.rect(0, 0, CW, CH / 2, ROLE_COL[a]); s.rect(0, CH / 2, CW, CH / 2, ROLE_COL[b])
    s.parts.append(f'<line x1="0" x2="{CW}" y1="{CH/2}" y2="{CH/2}" stroke="#ffffff" stroke-width="1.5"/>')
    for role, cy, rot in ((a, CH * 0.25, None), (b, CH * 0.75, 180)):
        s.text(CW / 2, cy + 3, role.upper(), 8.2, "bold", "#ffffff", "middle", rotate=rot)
        s.text(CW / 2, cy + (14 if rot is None else -9), role[0], 12, "bold", "#ffffff", "middle", rotate=rot)
    return s.svg()

def dis_svg(t):
    s = Svg(CW, CH, "#3a1d1a")
    s.rect(3, 3, CW - 6, CH - 6, "none", 4, "#e8b3ad")
    s.text(CW / 2, 22, "DISRUPTION", 6.5, "bold", "#e8b3ad", "middle")
    s.text(CW / 2, CH / 2 + 4, t, 11, "bold", "#ffffff", "middle")
    s.text(CW / 2, CH - 12, "Breaks the sequence", 5.2, fill="#e8b3ad", anchor="middle")
    return s.svg()

def die_svg(label, face, text):
    s = Svg(DW, DH, "#ffffff")
    s.rect(0, 0, DW, 11, "#1b2329")
    s.text(DW / 2, 8.5, label.upper(), 6, "bold", "#ffffff", "middle")
    if text is None:
        s.text(DW / 2, 40, str(face), 22, "bold", anchor="middle")
    else:
        s.text(4, 19, str(face), 7, "bold")
        s.para(4, 19, text, 6.2, DW - 8, fill=GREY if text.startswith("[") else "#1b2329")
    return s.svg()

def token_svg(fill, letter, fg="#ffffff", size=TW):
    s = Svg(size, size, "none")
    s.parts = [f'<circle cx="{size/2}" cy="{size/2}" r="{size/2-1}" fill="{fill}" stroke="#1b2329" stroke-width="1"/>']
    s.text(size / 2, size / 2 + 4, letter, 11, "bold", fg, "middle")
    return s.svg()

# ---------------- widgets ----------------
W = []
Z = [100]
def z():
    Z[0] += 1; return Z[0]

def holder(label, x, y, w, h, shuffle=False, free=False, bg=None):
    h_ = {"id": rid(), "type": "holder", "x": x, "y": y, "z": z(), "label": label, "width": w, "height": h,
          "allowedDecks": None, "hasShuffleButton": shuffle}
    if free:
        h_.update({"layoutType": "freeform", "hideStackTab": True, "enableChildrenSnapToSimilar": False})
    if bg:
        h_["mainBackground"] = {"fill": {"type": "color", "color": bg}}
    W.append(h_); return h_

def counter(label, x, y, val, lo, hi, w=88, h=58):
    c = {"id": rid(), "type": "counter", "x": x, "y": y, "z": 0, "label": label, "counterValue": val,
         "counterMin": lo, "counterMax": hi, "width": w, "height": h}
    W.append(c); return c

BACK = {"includeBorder": "heavy", "includeRadius": True,
        "objects": [{"type": "image", "x": 0, "y": 0, "w": 0, "h": 0, "color": "#840202", "valueType": "static", "value": "/img/cardbacks/cardback-red.svg"}]}

def deck(name, w, h, home, pieces=False):
    d = {"id": rid(), "type": "cardDeck", "collectionName": name, "cardTypes": {}, "cardWidth": w, "cardHeight": h,
         "faceTemplate": {"includeBorder": False if pieces else "heavy", "includeRadius": not pieces,
                          "objects": [{"type": "image", "x": 0, "y": 0, "w": w, "h": h, "color": "transparent" if pieces else "white",
                                       "valueType": "dynamic", "value": "image"}]},
         "showUnflipped": True, "owner": None, "parent": home["id"], "x": home["x"], "y": home["y"], "z": z()}
    if pieces:
        d["collectionType"] = "pieces"
    else:
        b = json.loads(json.dumps(BACK)); b["objects"][0]["w"] = w; b["objects"][0]["h"] = h
        d["backTemplate"] = b; d["autoShuffle"] = False  # True makes PCIO shuffle card types across ALL holders of the deck at import
    W.append(d); return d

def ctype(dk, label, svg_text):
    key = "type-" + str(uuid.uuid4())
    dk["cardTypes"][key] = {"label": label, "image": asset(svg_text)}
    return key

def put(dk, key, hold, faceup=False, piece=False, dx=4, dy=4):
    o = {"id": rid(), "type": "piece" if piece else "card", "deck": dk["id"], "cardType": key, "parent": hold["id"],
         "x": hold["x"] + dx, "y": hold["y"] + dy, "z": z(), "owner": None, "layoutStackParent": None}
    if not piece:
        o["faceup"] = faceup
    W.append(o); return o

# Spacing rules learned from the live room (27 Nov 2026):
# - PCIO draws a holder's label ABOVE its top edge (~18 px), so every row needs a
#   gap of at least GAP above it, and nothing may sit just above a labelled holder.
# - Counters draw about 92 px wide whatever width is set, so give each 100 px.
# - A Recall & Shuffle button hangs ~26 px below its holder.
GAP = 22
CTR = 92          # counter width
ROW = PH + 16     # height of the Horizon / Path / Flood Track rows

# ---- Row 1: role panels
Y1 = GAP
for i, r in enumerate(ROLES):
    x = 8 + i * 398
    holder(f"{r}  ·  {TRACK[r]}", x, Y1, 390, 112, free=True, bg=ROLE_TINT[r])
    for j, (lab, val, hi) in enumerate(((TRACK[r], 5, 10), ("AP", 0, 99), ("VP", 0, 20))):
        counter(lab, x + 8 + j * 100, Y1 + 27, val, 0, hi, w=CTR)

# ---- Row 2: Horizon + Place decks
Y2 = Y1 + 112 + GAP
holder("The Horizon  ·  revealed Places", 8, Y2, 1100, ROW, free=True, bg="rgb(236,236,230)")
pdecks = {}
for i, t in enumerate(["Plains", "Forest", "Mountains"]):
    pdecks[t] = holder(f"{t} Places", 1116 + i * 121, Y2, PW + 8, PH + 8)
pdisc = holder("Place discard", 1116 + 3 * 121, Y2, PW + 8, PH + 8)

# ---- Row 3: Path slots, Sequence and tokens, pending events, event decks
Y3 = Y2 + ROW + GAP
for i in range(3):
    x = 8 + i * 226
    holder(f"Path {i+1}", x, Y3, PW + 8, ROW, free=True, bg="rgb(240,232,214)")
    counter("Progress", x + PW + 14, Y3 + 30, 0, 0, 10, w=CTR)
counter("Sequence", 690, Y3 + 12, 0, 0, 4, w=CTR)
seqh = holder("Role", 792, Y3, 80, 80, free=True)
floodh = holder("Flood", 690, Y3 + 102, 92, 100, free=True, bg="rgb(214,230,241)")
timeh = holder("Timing", 792, Y3 + 102, 80, 100, free=True)
holder("Pending Events", 884, Y3, 224, ROW, free=True)
edecks = {}
for i, t in enumerate(["Plains", "Forest", "Mountains"]):
    edecks[t] = holder(f"{t} Events", 1116 + i * 121, Y3 + 28, EW + 8, EH + 8)
edisc = holder("Event discard", 1116 + 3 * 121, Y3 + 28, EW + 8, EH + 8)

# ---- Row 4: Flood Track, Caravan, Relic
Y4 = Y3 + ROW + GAP
flood = holder("Flood Track  ·  Places reached", 8, Y4, 1100, ROW, free=True, bg="rgb(214,230,241)")
cdeck = holder("Caravan Events", 1116, Y4 + 28, EW + 8, EH + 8)
holder("Caravan Events in play", 1232, Y4, 236, ROW, free=True)
counter("Caravan AP", 1240, Y4 + ROW - 66, 0, 0, 60, w=CTR)
holder("Relic", 1480, Y4 + 28, EW + 8, EH + 8)

# ---- Row 5: Council Cards, Disruption, hand, Items, counters, dice
Y5 = Y4 + ROW + GAP
ccdeck = holder("Council", 8, Y5, CW + 8, CH + 8)
ccdisc = holder("CC discard", 90, Y5, CW + 8, CH + 8)
dish = {}
for i, t in enumerate(["Hunger", "Malaise", "Injury"]):
    dish[t] = holder(t, 172 + i * 82, Y5, CW + 8, CH + 8)
W.append({"id": "hand", "type": "hand", "x": 424, "y": Y5, "z": 1, "dragging": None, "width": 480, "height": 1000 - Y5 - 4})
ideck = holder("Items", 914, Y5, IW + 8, IH + 8)
idisc = holder("Discard", 1000, Y5, IW + 8, IH + 8)
for j, (lab, val, lo, hi) in enumerate((("Food", 20, 0, 99), ("Population", 20, 0, 40), ("Supplies", 20, 0, 99), ("Round", 1, 1, 30))):
    counter(lab, 1090 + (j % 2) * 100, Y5 + (j // 2) * 82, val, lo, hi, w=CTR)
dice = {}
for i, t in enumerate(["Plains die", "Forest die", "Mountains die", "d10"]):
    dice[t] = holder(t.replace(" die", ""), 1300 + i * 75, Y5, DW + 8, DH + 8, shuffle=True)

# ---------------- populate ----------------
def shuffled(xs):
    xs = list(xs); random.shuffle(xs); return xs

# One deck (collection) per pile, so a pile's Recall can never pull cards from another pile.
placeD = {t: deck(f"{t} Places", PW, PH, pdecks[t]) for t in pdecks}
for r in shuffled(D["places"]):
    svg, title = place_svg(r)
    c = dict(zip(D["places_cols"], r))
    terr = c["terrain"] if c["terrain"] in pdecks else "Plains"
    key = ctype(placeD[terr], f"{r[0]} {title}", svg)
    if r[0] == "P21":
        put(placeD[terr], key, flood, faceup=True, dx=10, dy=8)
        continue
    put(placeD[terr], key, pdecks[terr])

eventD = {t: deck(f"{t} Events", EW, EH, edecks[t]) for t in edecks}
for r in shuffled(D["events"]):
    svg, title = event_svg(r)
    terr = r[2] if r[2] in edecks else "Plains"
    put(eventD[terr], ctype(eventD[terr], f"{r[0]} {title}", svg), edecks[terr])

carD = deck("Caravan Events", EW, EH, cdeck)
for r in shuffled(D["caravan"]):
    svg, title = caravan_svg(r)
    put(carD, ctype(carD, f"{r[0]} {title}", svg), cdeck)

itemD = deck("Items", IW, IH, ideck)
for r in shuffled(D["items"]):
    svg, title = item_svg(r)
    put(itemD, ctype(itemD, f"{r[0]} {title}", svg), ideck)

ccD = deck("Council Cards", CW, CH, ccdeck)
cc = []
for cid, a, b, q in D["council"]:
    key = ctype(ccD, f"{a} / {b}", cc_svg(a, b))
    cc += [key] * int(q)
for key in shuffled(cc):
    put(ccD, key, ccdeck)

for t in ["Hunger", "Malaise", "Injury"]:
    disD = deck(t, CW, CH, dish[t])
    key = ctype(disD, t, dis_svg(t))
    for _ in range(10):
        put(disD, key, dish[t], faceup=True)

for name, faces in (("Plains die", PLAINS_DIE), ("Forest die", ["[blank face]"] * 10),
                    ("Mountains die", ["[blank face]"] * 10), ("d10", [None] * 10)):
    dk = deck(name, DW, DH, dice[name])
    keys = [ctype(dk, f"{name} {i+1}", die_svg(name, i + 1, faces[i])) for i in range(10)]
    for k in shuffled(keys):
        put(dk, k, dice[name])

floodD = deck("Flood tokens", TW, TW, floodh, pieces=True)
fk = ctype(floodD, "Flood", token_svg("#1f5f8b", "F"))
for i in range(40):
    put(floodD, fk, floodh, piece=True, dx=8 + (i % 4) * 4, dy=24 + (i // 4) * 2)
timeD = deck("Timing tokens", TW, TW, timeh, pieces=True)
tk = ctype(timeD, "Timing", token_svg("#ffffff", "T", "#1b2329"))
for i in range(30):
    put(timeD, tk, timeh, piece=True, dx=8 + (i % 4) * 4, dy=24 + (i // 4) * 2)
seqD = deck("Sequence role", 30, 30, seqh, pieces=True)
for i, r in enumerate(ROLES):
    k = ctype(seqD, r, token_svg(ROLE_COL[r], r[0], size=30))
    put(seqD, k, seqh, piece=True, dx=6 + (i % 2) * 38, dy=24 + (i // 2) * 34)

# counters on top of everything
for w in W:
    if w["type"] == "counter":
        w["z"] = z()

with open(os.path.join(ROOM, "widgets.json"), "w", encoding="utf-8") as f:
    json.dump(W, f, ensure_ascii=False, separators=(",", ":"))
open(os.path.join(ROOM, "schemaVersion"), "w").write("8")
open(os.path.join(ROOM, "variantId"), "w").write(uuid.uuid4().hex[:24])
open(os.path.join(ROOM, "variantDate"), "w").write(str(int(time.time() * 1000)))

ext = [(w["x"] + w.get("width", 0), w["y"] + w.get("height", 0)) for w in W if w["type"] in ("holder", "counter", "hand")]
print("widgets", len(W), "assets", len(os.listdir(os.path.join(ROOM, "userassets"))),
      "extent", max(e[0] for e in ext), max(e[1] for e in ext))
