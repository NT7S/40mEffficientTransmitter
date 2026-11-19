"""Replace the rectangular courtyard of the flat toroid footprints with the body outline: core circle (max coated OD/2 + 0.5)
joined to a lead tab around the two pads (pad edge + 0.25). Rotated toroids then stop claiming the empty rectangle corners."""
import pcbnew, math, os
io = pcbnew.PCB_IO_MGR.FindPlugin(pcbnew.PCB_IO_MGR.KICAD_SEXP)
lib = os.path.abspath('pa40.pretty')
for name, r, w, ybot in (('L_Toroid_T80_Flat_P10.16mm_Drill1.6mm', 10.85, 6.75, 14.35),
                         ('L_Toroid_FT50_Flat_P7.62mm_Drill1.0mm', 6.975, 5.1, 10.14)):
    fp = io.FootprintLoad(lib, name)
    for g in list(fp.GraphicalItems()):
        if g.GetLayer() == pcbnew.F_CrtYd: fp.Remove(g)
    a0 = math.asin(w / r)              # angle from +Y (down) where the tab side meets the circle
    pts = [(w, ybot), (w, r * math.cos(a0))]
    n = 72
    for i in range(1, n):
        a = a0 + (2 * math.pi - 2 * a0) * i / n   # sweep round the top of the core from the +x side to the -x side
        pts.append((r * math.sin(a), r * math.cos(a)))
    pts += [(-w, r * math.cos(a0)), (-w, ybot)]
    sh = pcbnew.PCB_SHAPE(fp, pcbnew.SHAPE_T_POLY); sh.SetLayer(pcbnew.F_CrtYd); sh.SetWidth(pcbnew.FromMM(0.05)); sh.SetFilled(False)
    sh.SetPolyPoints([pcbnew.VECTOR2I(pcbnew.FromMM(x), pcbnew.FromMM(y)) for x, y in pts])
    fp.Add(sh)
    io.FootprintSave(lib, fp); print('courtyard', name)
