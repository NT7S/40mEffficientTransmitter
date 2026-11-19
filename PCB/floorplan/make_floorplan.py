#!/usr/bin/env python3
"""Rev 7 board outline + functional-block floorplan (no parts placed).
Board-relative coords: origin = board top-left at absolute (100,100) mm, x right, y down."""
import pcbnew, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from blocks import BLOCKS, ENVELOPES, BOARD_W, BOARD_H, HOLES, CORNER_R, NOTES, EDGE_LABELS

X0, Y0 = 100.0, 100.0
mm = pcbnew.FromMM
def P(x, y): return pcbnew.VECTOR2I(mm(X0 + x), mm(Y0 + y))

b = pcbnew.BOARD()
b.SetCopperLayerCount(2)
ls = pcbnew.LSET()
for L in (pcbnew.F_Cu, pcbnew.B_Cu, pcbnew.F_SilkS, pcbnew.B_SilkS, pcbnew.F_Mask, pcbnew.B_Mask,
          pcbnew.F_Paste, pcbnew.B_Paste, pcbnew.F_Fab, pcbnew.B_Fab, pcbnew.F_CrtYd, pcbnew.B_CrtYd,
          pcbnew.Edge_Cuts, pcbnew.Margin, pcbnew.Dwgs_User, pcbnew.Cmts_User, pcbnew.User_1, pcbnew.User_2):
    ls.AddLayer(L)
b.SetEnabledLayers(ls); b.SetVisibleLayers(ls)
b.SetLayerName(pcbnew.User_1, "Floorplan")
b.SetLayerName(pcbnew.User_2, "Envelopes")
ds = b.GetDesignSettings()
ds.SetBoardThickness(mm(1.6))
ds.SetAuxOrigin(P(0, 0)); ds.SetGridOrigin(P(0, 0))
tb = b.GetTitleBlock()
tb.SetTitle("40 m 5 W GaN class E CW TX - floorplan (no parts placed)")
tb.SetRevision("7"); tb.SetCompany("Etherkit / NT7S"); tb.SetDate("2026-11-19")
tb.SetComment(0, "Board 100 x 60 mm, 2 layers, FR-4 1.6 mm; JLCPCB bare board, hand populated")
tb.SetComment(1, "User.1 Floorplan = block regions; User.2 Envelopes = courtyard boxes of the large parts")

def seg(layer, a, c, w=0.1):
    s = pcbnew.PCB_SHAPE(b, pcbnew.SHAPE_T_SEGMENT); s.SetStart(P(*a)); s.SetEnd(P(*c))
    s.SetLayer(layer); s.SetWidth(mm(w)); b.Add(s)
def arc(layer, start, mid, end, w=0.1):
    s = pcbnew.PCB_SHAPE(b, pcbnew.SHAPE_T_ARC); s.SetArcGeometry(P(*start), P(*mid), P(*end))
    s.SetLayer(layer); s.SetWidth(mm(w)); b.Add(s)
def poly(layer, pts, w=0.15):
    for i in range(len(pts)): seg(layer, pts[i], pts[(i + 1) % len(pts)], w)
def circle(layer, c, r, w=0.1):
    s = pcbnew.PCB_SHAPE(b, pcbnew.SHAPE_T_CIRCLE); s.SetCenter(P(*c)); s.SetEnd(P(c[0] + r, c[1]))
    s.SetLayer(layer); s.SetWidth(mm(w)); b.Add(s)
def text(layer, s, at, size=1.0, th=None, left=True, bold=False):
    t = pcbnew.PCB_TEXT(b); t.SetText(s); t.SetPosition(P(*at)); t.SetLayer(layer)
    t.SetTextSize(pcbnew.VECTOR2I(mm(size), mm(size))); t.SetTextThickness(mm(th or size * 0.15))
    if left: t.SetHorizJustify(pcbnew.GR_TEXT_H_ALIGN_LEFT)
    t.SetVertJustify(pcbnew.GR_TEXT_V_ALIGN_TOP)
    if bold: t.SetBold(True)
    b.Add(t)

# ---- Edge.Cuts: 100 x 60 rectangle, CORNER_R corners (same style as Si5351AVFO) ----
W, H, r = BOARD_W, BOARD_H, CORNER_R
k = r * (1 - 0.70710678)
seg(pcbnew.Edge_Cuts, (r, 0), (W - r, 0)); seg(pcbnew.Edge_Cuts, (W, r), (W, H - r))
seg(pcbnew.Edge_Cuts, (W - r, H), (r, H)); seg(pcbnew.Edge_Cuts, (0, H - r), (0, r))
arc(pcbnew.Edge_Cuts, (0, r), (k, k), (r, 0)); arc(pcbnew.Edge_Cuts, (W - r, 0), (W - k, k), (W, r))
arc(pcbnew.Edge_Cuts, (W, H - r), (W - k, H - k), (W - r, H)); arc(pcbnew.Edge_Cuts, (r, H), (k, H - k), (0, H - r))

# ---- M3 mounting holes: MountingHole_3.2mm_M3_Pad_Via (as Si5351AVFO H1-H4) ----
def mounting_hole(ref, c):
    f = pcbnew.FOOTPRINT(b)
    f.SetFPID(pcbnew.LIB_ID("MountingHole", "MountingHole_3.2mm_M3_Pad_Via"))
    f.SetReference(ref); f.SetValue("M3")
    f.Reference().SetVisible(False); f.Value().SetVisible(False); f.Value().SetLayer(pcbnew.F_Fab)
    f.SetAttributes(pcbnew.FP_BOARD_ONLY | pcbnew.FP_EXCLUDE_FROM_BOM | pcbnew.FP_EXCLUDE_FROM_POS_FILES)
    f.SetLibDescription("Mounting Hole 3.2mm, M3, plated 6.4 mm pad with 8 x 0.5 mm stitching vias")
    pads = [(0, 0, 6.4, 3.2)] + [(x, y, 0.8, 0.5) for x, y in
        [(-2.4, 0), (2.4, 0), (0, -2.4), (0, 2.4), (-1.697056, -1.697056), (-1.697056, 1.697056),
         (1.697056, -1.697056), (1.697056, 1.697056)]]
    for x, y, d, dr in pads:
        p = pcbnew.PAD(f); p.SetNumber("1"); p.SetAttribute(pcbnew.PAD_ATTRIB_PTH)
        p.SetShape(pcbnew.PAD_SHAPE_CIRCLE); p.SetSize(pcbnew.VECTOR2I(mm(d), mm(d)))
        p.SetDrillSize(pcbnew.VECTOR2I(mm(dr), mm(dr))); p.SetLayerSet(pcbnew.PAD.PTHMask())
        p.SetPosition(pcbnew.VECTOR2I(mm(x), mm(y))); f.Add(p)
    cy = pcbnew.PCB_SHAPE(f, pcbnew.SHAPE_T_CIRCLE); cy.SetCenter(pcbnew.VECTOR2I(0, 0))
    cy.SetEnd(pcbnew.VECTOR2I(mm(3.45), 0)); cy.SetLayer(pcbnew.F_CrtYd); cy.SetWidth(mm(0.05)); f.Add(cy)
    cm = pcbnew.PCB_SHAPE(f, pcbnew.SHAPE_T_CIRCLE); cm.SetCenter(pcbnew.VECTOR2I(0, 0))
    cm.SetEnd(pcbnew.VECTOR2I(mm(3.2), 0)); cm.SetLayer(pcbnew.Cmts_User); cm.SetWidth(mm(0.15)); f.Add(cm)
    f.SetPosition(P(*c)); b.Add(f)
    return f
for i, c in enumerate(HOLES, 1):
    mounting_hole(f"H{i}", c)
    circle(pcbnew.User_1, c, 4.5, 0.1)   # M3 head/washer keepout drawn on the floorplan layer

# ---- floorplan blocks (User.1) ----
for blk in BLOCKS:
    poly(pcbnew.User_1, blk["poly"], 0.2)
    x, y = blk["label_at"]
    text(pcbnew.User_1, blk["title"], (x, y), 1.0, 0.18, bold=True)
    yy = y + 1.5
    for line in blk["label_lines"]:
        text(pcbnew.User_1, line, (x, yy), 0.75, 0.11); yy += 1.05
# ---- large-part envelopes (User.2): courtyard extents from the project footprints ----
for e in ENVELOPES:
    x1, y1, x2, y2 = e["rect"]
    poly(pcbnew.User_2, [(x1, y1), (x2, y1), (x2, y2), (x1, y2)], 0.1)
    if e.get("core"): circle(pcbnew.User_2, e["core"][0], e["core"][1], 0.1)
    text(pcbnew.User_2, e["label"], e.get("label_at", (x1 + 0.6, y1 + 0.5)), 0.75, 0.11)
# ---- notes outside the board (User.1) ----
for i, s in enumerate(NOTES):
    text(pcbnew.User_1, s, (0, H + 3.4 + i * 1.35), 0.85, 0.11)

for s_, at, size in EDGE_LABELS:
    text(pcbnew.User_1, s_, at, size, size * 0.17, bold=True)

# ---- branding: title on F.SilkS, rev on F.Cu (Jason's convention, Si5351AVFO "Rev A" is F.Cu) ----
from blocks import BRAND
for s, at, size, layer in BRAND:
    text({"F.SilkS": pcbnew.F_SilkS, "F.Cu": pcbnew.F_Cu}[layer], s, at, size, size * 0.17)

out = sys.argv[1]
pcbnew.SaveBoard(out, b)
print("saved", out)
