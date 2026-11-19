#!/usr/bin/env python3
"""Rev 7 placement v1: bring all schematic footprints onto the floorplan board, assign nets, place them.
Positions are board-relative mm (origin = back-left corner, x right, y toward the FRONT edge), as in floorplan/blocks.md."""
import pcbnew, re, os, sys, math, xml.etree.ElementTree as ET
HERE = os.path.dirname(os.path.abspath(__file__)); PRJ = os.path.dirname(HERE)
os.chdir(PRJ)
X0, Y0 = 100.0, 100.0
mm = pcbnew.FromMM
def P(x, y): return pcbnew.VECTOR2I(mm(X0 + x), mm(Y0 + y))

# ---------------- placement table: ref: (x, y, rot_deg) ----------------
PL = {
 # DC in + shunt (back-left)
 'J1': (17.5, 13.7, 180), 'R12': (26.5, 8.0, 90), 'JP1': (26.0, 13.9, 0), 'TP2': (26.5, 1.7, 0),
 'TP1': (24.0, 17.4, 0), 'TP3': (18.7, 17.4, 0), 'C10': (6.0, 15.3, 180), 'C11': (13.5, 17.6, 0), 'C12': (13.5, 19.7, 0),
 # 5 V buck: TI SLVSB35C Fig. 62 arrangement rotated 90 deg CW
 'U2': (35.8, 5.0, 270), 'C21': (36.3, 1.9, 0), 'C22': (39.0, 5.0, 90), 'L4': (37.4, 9.4, 0),
 'R14': (32.9, 5.6, 270), 'R13': (30.9, 5.6, 90), 'FB2': (32.5, 1.9, 0), 'FB3': (41.8, 9.4, 0),
 'C23': (41.8, 12.9, 0), 'TP12': (40.8, 15.9, 0), 'TP13': (35.3, 15.9, 0),
 # gate drive
 'U1': (39.6, 34.4, 0), 'R1': (43.6, 34.6, 0), 'C13': (40.2, 31.2, 180),
 'TP4': (45.5, 32.2, 0), 'TP5': (37.0, 31.0, 0), 'D1': (46.2, 29.0, 270),
 # class E core
 'Q1': (47.0, 34.6, 0), 'C1': (49.6, 34.6, 270), 'TP6': (52.2, 35.8, 0), 'TP7': (49.8, 39.0, 0),
 'L1': (49.0, 48.8, 90), 'C15': (46.6, 37.6, 90), 'C14': (44.5, 38.0, 90),
 # tank (front-right) and LPF (back-right)
 'C2': (53.5, 32.9, 0), 'L2': (72.0, 48.5, 180), 'C3': (65.6, 31.3, 180), 'TP10': (71.8, 29.6, 0), 'TP11': (71.8, 32.4, 0),
 'L3': (65.0, 12.5, 45), 'C16': (66.4, 27.6, 180), 'C19': (85.6, 16.4, 0),
 # RF out (back edge)
 'J2': (85.6, 0.0, 0),
 # PA keying (front edge)
 'J4': (34.25, 55.5, 0), 'Q2': (38.6, 42.6, 0), 'TP14': (38.4, 38.9, 0), 'R2': (35.4, 42.6, 90),
 'C4': (38.6, 45.4, 180), 'R3': (35.0, 46.0, 0), 'TP15': (31.0, 41.5, 0),
 # 7.030 MHz Pierce XO (front-left)
 'Y1': (12.5, 46.0, 0), 'C9': (6.5, 39.8, 270), 'C20': (9.9, 39.8, 270), 'Q4': (14.0, 38.0, 0),
 'C5': (8.5, 34.6, 90), 'R6': (10.5, 34.6, 90), 'R5': (12.5, 34.6, 270), 'R7': (14.0, 41.4, 0), 'C7': (17.6, 41.4, 0),
 'R9': (21.8, 42.6, 90), 'C6': (17.25, 50.6, 0), 'R8': (17.6, 36.0, 270), 'C8': (19.0, 38.6, 0),
 'R10': (21.8, 34.6, 270), 'R11': (21.8, 38.6, 270), 'TP8': (23.9, 36.6, 0), 'TP9': (24.0, 40.8, 0),
}
def l3_local(lx, ly):
    x, y, r = PL['L3']; a = math.radians(r)
    return (x + lx * math.cos(a) + ly * math.sin(a), y - lx * math.sin(a) + ly * math.cos(a), r)
PL['C17'] = l3_local(0, 16.4); PL['C18'] = l3_local(0, 19.0)
# hand-placed refdes text (x, y, angle): spots the automatic search cannot find in crowded corners
MANUAL = {'J2': (82.2, 15.0, 0), 'Q1': (47.6, 32.6, 0), 'C17': (73.5, 23.4, 0), 'TP10': (74.4, 29.6, 0), 'TP11': (74.4, 32.4, 0),
          'R13': (30.6, 8.0, 0), 'R14': (33.2, 8.0, 0), 'FB2': (32.5, 3.4, 0), 'TP2': (23.25, 1.9, 90), 'TP4': (43.3, 32.0, 0)}
HINT = {'L1': 'W', 'L2': 'W', 'L3': 'W', 'J1': 'S', 'J2': 'S', 'J4': 'N', 'Y1': 'S', 'C10': 'S', 'R12': 'W'}

# ---------------- libraries and netlist ----------------
libs = dict(re.findall(r'\(name "([^"]+)"\)\(type "KiCad"\)\(uri "\$\{KIPRJMOD\}/([^"]+)"', open('fp-lib-table').read()))
nl = ET.parse('layout/net.xml').getroot()
pinnet = {}
for n in nl.iter('net'):
    for nd in n.iter('node'): pinnet[(nd.get('ref'), nd.get('pin'))] = n.get('name')

b = pcbnew.LoadBoard(sys.argv[1] if len(sys.argv) > 1 else 'pa40-classe.kicad_pcb')
for f in list(b.GetFootprints()):
    if not f.GetReference().startswith('H'): b.Remove(f)
nets = {}
def net(name):
    if name not in nets:
        ni = b.FindNet(name)
        if ni is None:
            ni = pcbnew.NETINFO_ITEM(b, name); b.Add(ni)
        nets[name] = ni
    return nets[name]

comps = list(nl.iter('comp'))
missing = [c.get('ref') for c in comps if c.get('ref') not in PL]
assert not missing, missing
for c in comps:
    ref = c.get('ref'); lib, name = c.findtext('footprint').split(':')
    f = pcbnew.FootprintLoad(os.path.abspath(libs[lib]), name)
    assert f is not None, (ref, lib, name)
    f.SetFPID(pcbnew.LIB_ID(lib, name))
    f.SetReference(ref); f.SetValue(c.findtext('value'))
    f.SetPath(pcbnew.KIID_PATH('/' + c.findtext('tstamps')))
    props = {p.get('name'): p.get('value') for p in c.findall('property')}
    f.SetSheetname(props.get('Sheetname', '')); f.SetSheetfile(props.get('Sheetfile', ''))
    flds = c.find('fields')
    for fl in (flds if flds is not None else []):
        if fl.get('name') == 'MPN':
            fld = pcbnew.PCB_FIELD(f, pcbnew.FIELD_T_USER, 'MPN'); fld.SetText(fl.text or ''); fld.SetVisible(False)
            fld.SetLayer(pcbnew.F_Fab); f.Add(fld)
        if fl.get('name') == 'Description':   # as Update PCB from Schematic would: footprint field follows the symbol
            f.GetField(pcbnew.FIELD_T_DESCRIPTION).SetText(fl.text or '')
    f.SetDNP('dnp' in props)
    f.SetExcludedFromBOM('exclude_from_bom' in props)
    if ref == 'Q1':   # EPC2036 LGA: 0.15 mm pad-to-pad by EPC's land pattern (0.45 mm pitch); board default is 0.2 mm
        f.SetLocalClearance(mm(0.15))
    for pad in f.Pads():
        nn = pinnet.get((ref, pad.GetNumber()))
        if nn: pad.SetNet(net(nn))
    x, y, r = PL[ref]
    f.SetPosition(P(x, y)); f.SetOrientationDegrees(r)
    f.Value().SetVisible(False)
    for g in f.GraphicalItems():   # fab-layer ${REFERENCE} copies: small, so the review plots stay readable
        if isinstance(g, pcbnew.PCB_TEXT) and g.GetLayer() == pcbnew.F_Fab and g.GetTextHeight() > mm(0.6):
            g.SetTextSize(pcbnew.VECTOR2I(mm(0.6), mm(0.6))); g.SetTextThickness(mm(0.09))
    b.Add(f)

# ---------------- Edge.Cuts: split the front edge at J4's built-in notch ----------------
j4 = b.FindFootprintByReference('J4'); jx = pcbnew.ToMM(j4.GetPosition().x)
for d in list(b.GetDrawings()):
    if d.GetLayer() == pcbnew.Edge_Cuts and d.GetShape() == pcbnew.SHAPE_T_SEGMENT:
        s, e = d.GetStart(), d.GetEnd()
        if s.y == e.y == mm(Y0 + 60):
            xs = sorted([pcbnew.ToMM(s.x), pcbnew.ToMM(e.x)])
            b.Remove(d)
            for a, c2 in ((xs[0], jx - 6.5), (jx + 6.5, xs[1])):
                seg = pcbnew.PCB_SHAPE(b, pcbnew.SHAPE_T_SEGMENT); seg.SetLayer(pcbnew.Edge_Cuts); seg.SetWidth(mm(0.1))
                seg.SetStart(pcbnew.VECTOR2I(mm(a), mm(Y0 + 60))); seg.SetEnd(pcbnew.VECTOR2I(mm(c2), mm(Y0 + 60))); b.Add(seg)

# ---------------- branding block: move below C19 ----------------
for d in b.GetDrawings():
    if isinstance(d, pcbnew.PCB_TEXT) and d.GetLayer() in (pcbnew.F_SilkS, pcbnew.F_Cu) and pcbnew.ToMM(d.GetPosition().x) > X0 + 80:
        p = d.GetPosition(); d.SetPosition(pcbnew.VECTOR2I(p.x, p.y + mm(4.0)))

# ---------------- refdes silkscreen: horizontal, 0.8 mm, clear of pads, other silk and big bodies ----------------
def rect_of(bb, m=0.0):
    return (pcbnew.ToMM(bb.GetLeft()) - m, pcbnew.ToMM(bb.GetTop()) - m, pcbnew.ToMM(bb.GetRight()) + m, pcbnew.ToMM(bb.GetBottom()) + m)
def hit(a, c): return a[0] < c[2] and c[0] < a[2] and a[1] < c[3] and c[1] < a[3]
edge = (X0 + 0.5, Y0 + 0.5, X0 + 99.5, Y0 + 59.5)
obst = []; obst_crt = {}
for f in b.GetFootprints():
    for p in f.Pads(): obst.append((f.GetReference(), rect_of(p.GetBoundingBox(), 0.2)))
    for g in f.GraphicalItems():
        if g.GetLayer() == pcbnew.F_SilkS and not isinstance(g, pcbnew.PCB_TEXT):
            obst.append((f.GetReference(), rect_of(g.GetBoundingBox(), 0.15)))
    cy = f.GetCourtyard(pcbnew.F_Cu)
    if cy.OutlineCount(): obst_crt[f.GetReference()] = rect_of(cy.BBox())
for d in b.GetDrawings():
    if d.GetLayer() in (pcbnew.F_SilkS, pcbnew.F_Cu) or d.GetLayer() == pcbnew.Edge_Cuts:
        obst.append(('', rect_of(d.GetBoundingBox(), 0.3)))
big = {'L1', 'L2', 'L3', 'J1', 'J2', 'J4', 'Y1', 'C10', 'C9', 'R12', 'U1', 'Q2', 'Q4', 'U2'}
DIRP = {'N': 0, 'S': 0.3, 'E': 0.6, 'W': 0.6}
placed_txt = []
for ref, (x, y, a) in MANUAL.items():
    t = b.FindFootprintByReference(ref).Reference()
    t.SetTextSize(pcbnew.VECTOR2I(mm(0.8), mm(0.8))); t.SetTextThickness(mm(0.15)); t.SetKeepUpright(True); t.SetVisible(True)
    t.SetHorizJustify(pcbnew.GR_TEXT_H_ALIGN_CENTER); t.SetVertJustify(pcbnew.GR_TEXT_V_ALIGN_CENTER)
    t.SetPosition(P(x, y)); t.SetTextAngleDegrees(a); placed_txt.append(rect_of(t.GetBoundingBox(), 0.1))
order = sorted([f for f in b.GetFootprints() if f.GetReference() not in MANUAL], key=lambda f: (f.GetReference()[0] != 'L', f.GetReference()))
for f in order:
    ref = f.GetReference(); t = f.Reference()
    t.SetTextSize(pcbnew.VECTOR2I(mm(0.8), mm(0.8))); t.SetTextThickness(mm(0.15)); t.SetTextAngleDegrees(0)
    t.SetKeepUpright(True); t.SetVisible(True)
    t.SetHorizJustify(pcbnew.GR_TEXT_H_ALIGN_CENTER); t.SetVertJustify(pcbnew.GR_TEXT_V_ALIGN_CENTER)
    if ref.startswith('H'): t.SetVisible(False); continue
    cr = obst_crt.get(ref) or rect_of(f.GetBoundingBox(False))
    cx, cy0 = (cr[0] + cr[2]) / 2, (cr[1] + cr[3]) / 2
    t.SetPosition(P(0, 0)); tb = rect_of(t.GetBoundingBox()); tw, th = tb[2] - tb[0], tb[3] - tb[1]
    own_ok = ref not in big   # small parts: label may sit over their own courtyard margin, never over pads
    h0 = HINT.get(ref)
    best = None
    for step in range(0, 26):
        g = -0.4 + 0.12 * step if own_ok else 0.15 + 0.12 * step
        for k, pos in (('N', (cx, cr[1] - th / 2 - g)), ('S', (cx, cr[3] + th / 2 + g)), ('E', (cr[2] + tw / 2 + g, cy0)), ('W', (cr[0] - tw / 2 - g, cy0))):
            for sh in (0, -0.8, 0.8, -1.6, 1.6):
                p2 = (pos[0] + (sh if k in 'NS' else 0), pos[1] + (sh if k in 'EW' else 0))
                tr = (p2[0] - tw / 2, p2[1] - th / 2, p2[0] + tw / 2, p2[1] + th / 2)
                if not (tr[0] >= edge[0] and tr[1] >= edge[1] and tr[2] <= edge[2] and tr[3] <= edge[3]): continue
                if any(hit(tr, o) for _, o in obst) or any(hit(tr, o) for o in placed_txt): continue
                if any(hit(tr, r2) for k2, r2 in obst_crt.items() if k2 != ref and k2 in big): continue
                if not own_ok and hit(tr, cr): continue
                cost = max(g, 0) + abs(sh) * 0.6 + (0 if k == h0 else DIRP[k] + (0.5 if h0 else 0))
                if best is None or cost < best[0]: best = (cost, p2, tr)
    if best is None:
        print('refdes: no clean spot for', ref); continue
    _, pos, tr = best
    t.SetPosition(pcbnew.VECTOR2I(mm(pos[0]), mm(pos[1]))); placed_txt.append(tr)

b.BuildConnectivity()
pcbnew.SaveBoard('pa40-classe.kicad_pcb', b)
print('placed', len(comps), 'footprints; nets', len(nets))

# ---------------- stackup: 2-layer 1.6 mm, blue mask, white silk, ENIG (EPC2036 land pattern note asks for ENIG) ----------------
STACKUP = '''		(stackup
			(layer "F.SilkS" (type "Top Silk Screen") (color "White"))
			(layer "F.Paste" (type "Top Solder Paste"))
			(layer "F.Mask" (type "Top Solder Mask") (color "Blue") (thickness 0.01))
			(layer "F.Cu" (type "copper") (thickness 0.035))
			(layer "dielectric 1" (type "core") (color "FR4 natural") (thickness 1.51) (material "FR4") (epsilon_r 4.5) (loss_tangent 0.02))
			(layer "B.Cu" (type "copper") (thickness 0.035))
			(layer "B.Mask" (type "Bottom Solder Mask") (color "Blue") (thickness 0.01))
			(layer "B.Paste" (type "Bottom Solder Paste"))
			(layer "B.SilkS" (type "Bottom Silk Screen") (color "White"))
			(copper_finish "ENIG")
			(dielectric_constraints no)
		)
'''
txt = open('pa40-classe.kicad_pcb').read()
if '(stackup' not in txt:
    txt = txt.replace('\t(setup\n', '\t(setup\n' + STACKUP, 1)
    open('pa40-classe.kicad_pcb', 'w').write(txt)
