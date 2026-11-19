#!/usr/bin/env python3
"""Routing v1 for pa40-classe rev 7 (KiCad 10 pcbnew). Idempotent: strips all tracks, vias and zones from the
canonical board, then lays down the hand-planned routes below, GND zones on both layers and GND stitching vias.
Coordinates are absolute board mm (board outline 100..200 x 100..160)."""
import pcbnew, math, os, sys
PRJ = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); os.chdir(PRJ)
BRD = 'pa40-classe.kicad_pcb'
PRETTY = 'lib/pa40.pretty' if os.path.isdir('lib/pa40.pretty') else 'pa40.pretty'

b = pcbnew.LoadBoard(BRD)
mm = pcbnew.FromMM
F, B = pcbnew.F_Cu, pcbnew.B_Cu
# idempotent: drop previous copper and the logos/labels this script re-adds
for t in list(b.GetTracks()): b.Remove(t)
for z in list(b.Zones()): b.Remove(z)
for ref in ('LOGO1', 'LOGO2'):
    f = b.FindFootprintByReference(ref)
    if f: b.Remove(f)
for d in list(b.GetDrawings()):
    if d.GetClass() == 'PCB_TEXT' and d.GetLayer() == pcbnew.F_SilkS and d.GetText() in ('+12 VDC In', 'Antenna', 'Key'):
        b.Remove(d)

# v5: refresh L1 from pa40.pretty so the M3 nylon NPTH is present
def refresh_from_lib(ref, pretty, name):
    old = b.FindFootprintByReference(ref)
    new = pcbnew.FootprintLoad(pretty, name)
    new.SetFPID(old.GetFPID()); new.SetPosition(old.GetPosition()); new.SetOrientation(old.GetOrientation())
    new.SetReference(old.GetReference()); new.SetValue(old.GetValue())
    new.SetPath(old.GetPath()); new.SetSheetname(old.GetSheetname()); new.SetSheetfile(old.GetSheetfile())
    new.SetAttributes(old.GetAttributes()); new.SetLayer(old.GetLayer())
    for field in old.GetFields():
        n = field.GetName()
        new.SetField(n, field.GetText())
        nf = new.GetField(n)
        nf.SetPosition(field.GetPosition()); nf.SetLayer(field.GetLayer()); nf.SetVisible(field.IsVisible())
        if hasattr(field, 'GetTextSize'):
            nf.SetTextSize(field.GetTextSize()); nf.SetTextThickness(field.GetTextThickness())
    nets = {p.GetNumber(): p.GetNet() for p in old.Pads() if p.GetNumber()}
    for p in new.Pads():
        if p.GetNumber() in nets: p.SetNet(nets[p.GetNumber()])
    b.Remove(old); b.Add(new)
refresh_from_lib('L1', PRETTY, 'L_Toroid_FT50_Flat_P7.62mm_Drill1.0mm')

# ---------------- v2: H1-H4 grounded and linked to the new schematic symbols (MountingHole_Pad -> GND) ----------------
HSYM = {'H1': 'fd776354-9abb-4907-8769-ace0834de854', 'H2': '4fc63596-9ab4-4a44-85b9-ed868ee7d052', 'H3': '96171e2e-93b9-4e0e-93ef-a4e27ba6335c', 'H4': '438517ac-1003-4788-ab9d-185bbcb2c243'}
for ref, u in HSYM.items():
    f = b.FindFootprintByReference(ref)
    f.SetPath(pcbnew.KIID_PATH('/' + u)); f.SetSheetname('pa40-classe'); f.SetSheetfile('pa40-classe.kicad_sch')
    f.SetAttributes(f.GetAttributes() & ~pcbnew.FP_BOARD_ONLY)
    for p in f.Pads(): p.SetNet(b.FindNet('GND'))
    f.SetValue('MountingHole_Pad'); f.SetField('MPN', '')
# ---------------- v3: branding (Jason 2026-11-19) ----------------
# Logos: EtherkitLogoSmall + OSHWLogo4mm copied unchanged from NT7S/Si5351AVFO PCB/lib/Etherkit.pretty (project copy of
# etherkit/EtherkitKicadLibrary @6b9fc0f) into pa40.pretty; placed side by side as on Si5351AVFO (5.3 mm apart).
LOGOS = [('EtherkitLogoSmall', 'LOGO1', 187.4, 135.0), ('OSHWLogo4mm', 'LOGO2', 192.7, 134.6)]
logo_boxes = []
for name, ref, x, y in LOGOS:
    f = pcbnew.FootprintLoad(PRETTY, name)
    f.SetFPID(pcbnew.LIB_ID('pa40', name)); f.SetReference(ref)
    f.SetPosition(pcbnew.VECTOR2I(mm(x), mm(y)))
    b.Add(f)
    logo_boxes.append(list(f.GraphicalItems())[0].GetBoundingBox())
for d in b.GetDrawings():
    if d.GetClass() == 'PCB_TEXT':
        if d.GetText() == 'etherkit.com 2026': d.SetText('NT7S 2026')
        if d.GetText() == 'Rev 7':      # copper text on F.Cu, covered by mask, like "Rev A" on Si5351AVFO (1.5 mm / 0.3 mm)
            assert d.GetLayer() == F; d.SetTextThickness(mm(0.3)); d.SetIsKnockout(False)
# v4: jack labels on F.SilkS, just inside the board, beside each jack (not under the body)
def silk(text, x, y, size, thick):
    t = pcbnew.PCB_TEXT(b); t.SetText(text)
    t.SetPosition(pcbnew.VECTOR2I(mm(x), mm(y)))
    t.SetTextSize(pcbnew.VECTOR2I(mm(size), mm(size))); t.SetTextThickness(mm(thick))
    t.SetLayer(pcbnew.F_SilkS)
    t.SetHorizJustify(pcbnew.GR_TEXT_H_ALIGN_LEFT); t.SetVertJustify(pcbnew.GR_TEXT_V_ALIGN_CENTER)
    b.Add(t)
silk('+12 VDC In', 101.30, 109.60, 1.0, 0.17)   # left of J1, in the gap between H1 and C10
silk('Antenna',    188.50, 115.50, 1.2, 0.20)   # south of J2, right of C19
silk('Key',        124.00, 156.80, 1.2, 0.20)   # left of J4, near the front edge
# ---------------- v2: Q1 source bumps get no direct pour connection (each leaves on a 0.25 mm track like gate/drain) ----
q1 = b.FindFootprintByReference('Q1')
for p in q1.Pads():
    if p.GetNumber() in ('2', '4'): p.SetLocalZoneConnection(pcbnew.ZONE_CONNECTION_NONE)

ds = b.GetDesignSettings()
ds.m_MinClearance = mm(0.127); ds.m_TrackMinWidth = mm(0.127); ds.m_MinThroughDrill = mm(0.3)
ds.m_ViasMinSize = mm(0.5); ds.m_ViasMinAnnularWidth = mm(0.13); ds.m_HoleToHoleMin = mm(0.5)
ds.m_HoleClearance = mm(0.25); ds.m_CopperEdgeClearance = mm(0.5)

def net(n):
    ni = b.FindNet(n); assert ni, n; return ni
def T(n, w, *pts, layer=F):
    ni = net(n)
    for a, c in zip(pts, pts[1:]):
        t = pcbnew.PCB_TRACK(b); t.SetStart(pcbnew.VECTOR2I(mm(a[0]), mm(a[1]))); t.SetEnd(pcbnew.VECTOR2I(mm(c[0]), mm(c[1])))
        t.SetWidth(mm(w)); t.SetLayer(layer); t.SetNet(ni); b.Add(t)
def V(n, x, y, d=0.6, h=0.3):
    v = pcbnew.PCB_VIA(b); v.SetPosition(pcbnew.VECTOR2I(mm(x), mm(y))); v.SetDrill(mm(h)); v.SetWidth(mm(d))
    v.SetLayerPair(F, B); v.SetNet(net(n)); b.Add(v); return v

PWR, SIG = 1.0, 0.3
# ---------------- power entry, shunt, +12V ----------------
T('Net-(JP1-A)', 1.5, (117.5, 113.7), (123.0, 113.7), (125.6, 111.4))
T('Net-(JP1-A)', 0.6, (125.35, 113.6), (125.35, 112.0))
T('Net-(R12-Pad3)', SIG, (125.23, 104.2), (125.23, 102.4))                      # Kelvin sense to TP2
T('Net-(R12-Pad2)', SIG, (127.77, 112.0), (127.77, 112.6), (128.35, 113.2), (128.35, 115.9), (127.2, 117.05), (125.6, 117.05))  # Kelvin sense to TP1
T('+12V', 0.6, (126.65, 114.2), (126.65, 115.3)); V('+12V', 126.65, 115.3)     # JP1.2 hop (bottom) to the trunk
T('+12V', PWR, (126.65, 115.3), (129.5, 115.3), layer=B); V('+12V', 129.5, 115.3)
T('+12V', PWR, (129.5, 115.3), (129.5, 106.5), (128.0, 105.0))                 # trunk up to R12.4
T('+12V', 0.8, (129.5, 106.5), (129.5, 103.6), (131.4, 101.9))                 # to FB2 (buck input)
T('+12V', PWR, (129.5, 115.3), (129.5, 120.5), (128.8, 121.2), (113.2, 121.2), (112.7, 120.7), (112.7, 119.7))  # bulk caps
T('+12V', 0.8, (112.7, 119.7), (112.6, 117.6))
T('+12V', PWR, (112.6, 117.6), (111.0, 116.0), (109.6, 115.3))
T('+12V', PWR, (129.5, 120.5), (129.5, 131.0)); V('+12V', 129.5, 131.0)        # hop A under +5V and xo
T('+12V', PWR, (129.5, 131.0), (129.5, 135.8), layer=B); V('+12V', 129.5, 135.8)
T('+12V', PWR, (129.5, 135.8), (128.0, 137.3), (128.0, 143.1), (128.5, 143.6), (135.2, 143.6))
T('+12V', 0.6, (135.4, 143.5), (137.6, 143.55))                                 # R2.1 - Q2.2 (source)
# ---------------- buck TPS62175 (TI layout example: Cin at VIN/PGND, tight SW node, VOS from Cout) ----------------
T('Net-(U2-EN)', 0.6, (133.2, 101.9), (135.35, 101.9))
T('Net-(U2-EN)', 0.25, (135.35, 102.4), (135.8, 103.1), (135.8, 103.8))
T('Net-(U2-EN)', 0.25, (135.8, 103.1), (136.3, 103.1), (136.3, 103.8))
T('GND', 0.25, (137.25, 102.4), (136.8, 103.3), (136.8, 104.8))                 # Cin GND -> PGND -> EP
T('GND', 0.25, (135.3, 104.0), (135.3, 104.8))
T('GND', 0.25, (134.8, 106.0), (134.8, 105.2))
V('GND', 135.3, 105.0); V('GND', 136.3, 105.0)                                  # EP vias
T('GND', 0.4, (138.4, 104.05), (137.3, 104.05)); T('GND', 0.25, (137.3, 104.05), (136.8, 104.05))                                 # Cout GND -> PGND
T('Net-(U2-FB)', 0.25, (134.8, 103.8), (134.8, 103.3), (133.5, 103.3), (132.9, 103.9), (132.9, 104.78), (130.9, 104.78))
T('Net-(U2-SW)', 0.25, (136.3, 106.0), (136.3, 108.0))
T('Net-(U2-SLEEP)', 0.25, (136.8, 106.0), (138.4, 106.0))                       # VOS -> Cout
T('Net-(U2-SLEEP)', 0.6, (139.0, 106.0), (138.9, 107.8))                        # Cout -> L4
T('Net-(U2-SLEEP)', 0.6, (139.0, 109.4), (140.8, 109.4))                        # L4 -> FB3
T('Net-(U2-SLEEP)', 0.25, (135.8, 106.0), (135.8, 106.75), (133.9, 106.75), (133.6, 107.3), (131.4, 107.3), (130.9, 106.8))  # SLEEP + FB top
T('Net-(U2-SLEEP)', 0.25, (133.6, 107.3), (133.6, 111.9), (138.9, 111.9), (138.9, 111.0))  # tie SLEEP/FB-top to Vout at L4.2
# ---------------- +5V ----------------
T('+5V', 0.8, (142.6, 109.4), (142.6, 110.6), (140.85, 112.4), (140.85, 115.2))
T('+5V', 0.6, (141.0, 116.6), (141.0, 131.2), (140.95, 133.3))
T('+5V', 0.4, (140.95, 132.4), (122.5, 132.4), (121.8, 133.1), (121.8, 133.6))
T('+5V', 0.4, (122.5, 132.4), (117.6, 132.4), (117.6, 135.0))
T('+5V', 0.4, (117.6, 132.4), (112.5, 132.4), (112.5, 133.6))
# ---------------- XO ----------------
T('/xo', SIG, (121.8, 135.43), (121.8, 137.78))
T('/xo', SIG, (120.0, 138.4), (121.0, 137.78), (121.8, 137.78))
T('/xo', SIG, (121.8, 136.6), (123.9, 136.6))
T('/xo', SIG, (123.9, 136.6), (124.4, 136.6), (126.6, 134.4), (138.4, 134.4))
T('Net-(Q4-B)', SIG, (108.5, 135.5), (112.5, 135.5))
T('Net-(Q4-B)', SIG, (112.6, 135.6), (112.6, 137.0))
T('Net-(Q4-B)', SIG, (106.5, 137.7), (107.0, 137.6), (108.5, 136.1), (108.5, 135.5))
T('Net-(Q4-B)', SIG, (109.9, 138.8), (109.9, 136.8), (110.5, 136.2), (110.5, 135.5))
T('Net-(Q4-E)', SIG, (113.1, 139.0), (113.1, 141.2))
T('Net-(Q4-E)', SIG, (113.3, 139.0), (114.0, 139.7), (116.3, 139.7), (116.83, 140.4), (116.83, 141.2))
T('Net-(Q4-C)', SIG, (115.0, 138.0), (117.4, 138.0))
T('Net-(Q4-C)', SIG, (117.4, 138.0), (117.6, 137.0))
T('Net-(Q4-C)', SIG, (117.4, 138.0), (118.1, 138.5))
T('Net-(Q4-C)', SIG, (118.2, 138.8), (118.2, 139.6), (120.6, 139.6), (120.6, 140.7), (121.5, 141.6), (121.8, 141.78))
T('Net-(C6-Pad1)', SIG, (121.8, 143.5), (119.6, 145.6))
T('Net-(C6-Pad1)', SIG, (116.47, 150.4), (116.47, 146.6))
T('Net-(C20-Pad2)', SIG, (106.5, 141.9), (106.5, 145.4))
T('Net-(C20-Pad2)', SIG, (109.9, 140.8), (109.9, 145.4))
# ---------------- keying: J4, Q2 PMOS switch ----------------
T('Net-(J4-PadT)', SIG, (135.9, 146.0), (136.6, 146.0), (139.25, 148.65), (139.25, 149.8))
T('Net-(Q2-G)', 0.4, (132.6, 141.6), (135.4, 141.6), (135.6, 141.7), (137.5, 141.65))
V('Net-(Q2-G)', 132.3, 142.0); T('Net-(Q2-G)', SIG, (132.3, 142.0), (133.0, 145.8), layer=B); V('Net-(Q2-G)', 133.0, 145.8)  # hop B under +12V
T('Net-(Q2-G)', SIG, (133.0, 145.8), (133.6, 146.0), (134.18, 146.0))
T('Net-(Q2-G)', SIG, (134.18, 145.7), (134.6, 144.95), (137.3, 144.95), (137.82, 145.3))
T('/+12V_PA', 0.8, (139.6, 142.6), (139.6, 139.5))
T('/+12V_PA', 0.5, (139.4, 145.2), (139.6, 142.8))
T('/+12V_PA', PWR, (140.0, 139.0), (144.5, 139.0))
T('/+12V_PA', 0.8, (144.5, 139.0), (145.8, 139.0), (146.6, 138.4))
T('/+12V_PA', PWR, (146.6, 138.6), (147.3, 139.6), (149.0, 141.3), (157.6, 149.9), (157.89, 151.8))   # to L1 cold end (pad 1)
# ---------------- gate drive ----------------
T('Net-(R1-Pad1)', 0.4, (140.9, 135.35), (141.9, 135.35), (142.6, 134.65))
T('/gate', 0.4, (144.43, 134.6), (145.6, 134.6))
T('/gate', 0.25, (145.6, 134.6), (145.9, 134.375), (146.775, 134.375))
T('/gate', SIG, (145.5, 132.5), (145.6, 134.6))
T('/gate', SIG, (145.5, 131.9), (146.2, 130.5))
T('GND', 0.3, (138.5, 135.35), (137.2, 135.35)); V('GND', 136.9, 135.35)        # U1 GND straight to the plane
# ---------------- Q1 power loop ----------------
# v2: one 0.25 mm neck per source bump (same as gate/drain), joined by a 0.6 mm bar 0.78 mm below the bump centres
T('GND', 0.25, (146.775, 134.825), (146.775, 135.6))
T('GND', 0.25, (147.225, 134.825), (147.225, 135.6))
T('GND', 0.6, (146.775, 135.6), (147.225, 135.6))
T('GND', 0.6, (146.775, 135.6), (145.5, 135.85))                                 # to source via W
T('GND', 0.6, (147.6, 135.9), (147.9, 136.9))                                    # to source via SE
T('GND', 0.6, (147.0, 135.6), (147.0, 135.9), (148.9, 135.9))
T('GND', 0.6, (147.0, 135.9), (146.6, 136.5))
T('GND', 0.6, (145.0, 137.0), (146.3, 136.83))
V('GND', 147.9, 136.9); V('GND', 145.5, 135.85); V('GND', 148.2, 138.0)
T('/drain', 0.25, (147.225, 134.375), (147.7, 133.9))
T('/drain', 0.8, (147.7, 133.9), (149.0, 133.2))
T('/drain', 1.2, (149.6, 133.0), (152.0, 133.0))
T('/drain', 0.8, (152.1, 133.6), (152.2, 135.8))
T('/drain', PWR, (152.2, 135.8), (153.4, 137.0), (157.89, 141.5), (157.89, 144.99))   # to L1 hot end (pad 2)
# ---------------- tank, match, LPF, output ----------------
T('Net-(C2-Pad2)', 1.2, (155.0, 132.9), (156.1, 134.0), (165.8, 134.0), (166.92, 135.8))
T('/out_50r', 1.2, (167.5, 131.3), (167.5, 127.6), (170.39, 125.07), (175.55, 125.14))
T('/out_50r', 1.0, (175.55, 125.14), (177.39, 126.98))
T('/out_50r', 1.2, (177.08, 135.8), (177.08, 134.0), (173.6, 130.5), (172.7, 129.6), (167.5, 129.6))
T('/rf_out', 1.0, (179.48, 124.89), (177.64, 123.05))
T('/rf_out', 1.5, (177.64, 123.05), (177.57, 117.89))
MS = 2.4   # CPWG: 2.4 mm track, 1.0 mm gap to the F.Cu pour (rule area below), B.Cu plane -> ~51 ohm
T('/rf_out', MS, (177.57, 117.89), (184.12, 116.4), (185.6, 112.4))
T('GND', 0.8, (187.07, 116.4), (188.6, 116.4)); V('GND', 188.6, 116.4)          # C19 GND straight to the plane
# F.Cu "no copper pour" rule area = the CPWG tracks inflated by 1.0 mm (deterministic gap; zone filler in pcbnew
# Python does not see .kicad_dru rules, a rule area it does)
def cpwg_keepout(gap=1.0):
    ps = pcbnew.SHAPE_POLY_SET()
    for t in b.GetTracks():
        if t.Type() == pcbnew.PCB_TRACE_T and t.GetNetname() == '/rf_out' and abs(pcbnew.ToMM(t.GetWidth()) - MS) < 1e-3:
            t.TransformShapeToPolygon(ps, F, mm(gap), mm(0.005), pcbnew.ERROR_OUTSIDE)
    ps.Simplify()
    z = pcbnew.ZONE(b); z.SetIsRuleArea(True); z.SetLayer(F)
    z.SetDoNotAllowZoneFills(True); z.SetDoNotAllowTracks(False); z.SetDoNotAllowVias(False); z.SetDoNotAllowPads(False); z.SetDoNotAllowFootprints(False)
    z.SetZoneName('rf_out CPWG gap'); z.Outline().Append(ps); b.Add(z)
cpwg_keepout()
def q1_keepout():
    # F.Cu no-pour box around the four EPC2036 bumps: every bump sees only its 0.25 mm neck, not the pour
    z = pcbnew.ZONE(b); z.SetIsRuleArea(True); z.SetLayer(F); z.SetZoneName('Q1 bump no-pour')
    z.SetDoNotAllowZoneFills(True); z.SetDoNotAllowTracks(False); z.SetDoNotAllowVias(False); z.SetDoNotAllowPads(False); z.SetDoNotAllowFootprints(False)
    o = z.Outline(); o.NewOutline()
    for x, y in ((146.0, 133.75), (148.0, 133.75), (148.0, 135.45), (146.0, 135.45)): o.Append(mm(x), mm(y))
    b.Add(z)
q1_keepout()
ds.m_TentViasFront = True; ds.m_TentViasBack = True    # JLCPCB order: Via Covering = Tented


# ---------------- GND stitching vias ----------------
# Grid 4 mm board-wide, 2 mm over the PA/tank/LPF/output area and around the gate driver and XO. A candidate is kept
# only if it clears all non-GND copper on both layers by 0.35 mm, every drill by 0.6 mm, the board edge by 1.2 mm,
# copper text, and SMD courtyards (so no via sits under or between small-part pads).
def stitch():
    nonGND = []
    for f in b.GetFootprints():
        for p in f.Pads():
            for L in (F, B):
                if p.IsOnLayer(L) and p.GetNetname() != 'GND': nonGND.append(p.GetEffectiveShape(L))
    for t in b.GetTracks():
        if t.GetNetname() != 'GND': nonGND.append(t.GetEffectiveShape(t.GetLayer() if t.Type() == pcbnew.PCB_TRACE_T else F))
    drills = [(p.GetPosition(), p.GetDrillSize().x) for f in b.GetFootprints() for p in f.Pads() if p.GetDrillSize().x > 0]
    drills += [(t.GetPosition(), t.GetDrill()) for t in b.GetTracks() if t.Type() == pcbnew.PCB_VIA_T]
    crt = []
    for f in b.GetFootprints():
        if f.GetAttributes() & pcbnew.FP_SMD:
            bb = f.GetCourtyard(F).BBox(); crt.append(bb)
    txt = [d.GetBoundingBox() for d in b.GetDrawings() if d.GetLayer() in (F, pcbnew.F_SilkS) and d.GetClass() == 'PCB_TEXT']
    txt += logo_boxes   # no stitching vias under the silkscreen logos
    pts = []
    # via fence along both sides of the CPWG output run, 2.5 mm pitch, 0.6 mm outside the pour gap
    for t in b.GetTracks():
        if t.Type() == pcbnew.PCB_TRACE_T and t.GetNetname() == '/rf_out' and abs(pcbnew.ToMM(t.GetWidth()) - MS) < 1e-3:
            x0, y0, x1, y1 = (pcbnew.ToMM(v) for v in (t.GetStart().x, t.GetStart().y, t.GetEnd().x, t.GetEnd().y))
            L = math.hypot(x1 - x0, y1 - y0); ux, uy = (x1 - x0) / L, (y1 - y0) / L; off = MS / 2 + 1.0 + 0.6
            for k in range(int(L // 2.5) + 1):
                px, py = x0 + ux * k * 2.5, y0 + uy * k * 2.5
                for sg in (1, -1): pts.append((round(px - uy * off * sg, 2), round(py + ux * off * sg, 2)))
    for gx in range(0, 26):
        for gy in range(0, 16):
            pts.append((101.5 + gx * 4, 101.5 + gy * 4))
    def fine(x0, x1, y0, y1, st):
        x = x0
        while x <= x1:
            y = y0
            while y <= y1: pts.append((round(x, 2), round(y, 2))); y += st
            x += st
    fine(142, 192, 108, 142, 3)     # gate driver, Q1, tank, LPF, output to J2
    fine(104, 126, 130, 154, 3)     # XO
    fine(130, 145, 100, 114, 3)     # buck
    kept = []
    for x, y in pts:
        if not (101.2 <= x <= 198.8 and 101.2 <= y <= 158.8): continue
        if any(math.hypot(x - hx, y - hy) < 4.5 for hx in (104, 196) for hy in (104, 156)): continue   # mounting-hole corners
        c = pcbnew.VECTOR2I(mm(x), mm(y))
        if any((abs(x - k[0]) < 1.2 and abs(y - k[1]) < 1.2) for k in kept): continue
        if any(math.hypot(pcbnew.ToMM(dp.x) - x, pcbnew.ToMM(dp.y) - y) < 0.15 + pcbnew.ToMM(dd) / 2 + 0.6 for dp, dd in drills): continue
        if any(bb.GetInflated(mm(0.2)).Contains(c) for bb in crt): continue
        if any(bb.GetInflated(mm(0.5)).Contains(c) for bb in txt): continue
        if any(z.GetIsRuleArea() and z.Outline().Collide(c, mm(0.5)) for z in b.Zones()): continue
        sh = pcbnew.SHAPE_CIRCLE(c, mm(0.3))
        if any(o.Collide(sh, mm(0.35)) for o in nonGND): continue
        kept.append((x, y))
    for x, y in kept: V('GND', x, y)
    return len(kept)
nst = stitch()

# ---------------- GND zones ----------------
def zone(layer, prio=0):
    z = pcbnew.ZONE(b); z.SetLayer(layer); z.SetNet(net('GND')); z.SetIsFilled(False)
    o = z.Outline(); o.NewOutline()
    for x, y in ((100.3, 100.3), (199.7, 100.3), (199.7, 159.7), (100.3, 159.7)): o.Append(mm(x), mm(y))
    z.SetLocalClearance(mm(0.3)); z.SetMinThickness(mm(0.25))
    z.SetPadConnection(pcbnew.ZONE_CONNECTION_THT_THERMAL)
    z.SetThermalReliefGap(mm(0.5)); z.SetThermalReliefSpokeWidth(mm(0.5))
    z.SetIslandRemovalMode(pcbnew.ISLAND_REMOVAL_MODE_ALWAYS)
    z.SetAssignedPriority(prio); b.Add(z); return z
zone(F); zone(B)
pcbnew.ZONE_FILLER(b).Fill(b.Zones())
b.Save(BRD)
print('stitching vias', nst)
print('routed: tracks', len([t for t in b.GetTracks() if t.Type() == pcbnew.PCB_TRACE_T]), 'vias', len([t for t in b.GetTracks() if t.Type() == pcbnew.PCB_VIA_T]))
