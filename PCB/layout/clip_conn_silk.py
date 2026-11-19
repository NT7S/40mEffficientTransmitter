"""Clip connector silkscreen at the board edge in the library footprints (pa40 J2/J4 custom parts, project fplib copy of the PJ-102AH).
Local y limits: BNC origin is on the board edge (+Y onto the board); SJ1-3523N edge cut at local y 3.1 (notch) / 4.5; PJ-102AH face at local y 13.7."""
import pcbnew, os
io = pcbnew.PCB_IO_MGR.FindPlugin(pcbnew.PCB_IO_MGR.KICAD_SEXP)
mm = pcbnew.FromMM
ED = 0.3
def clip(lib, name, ymin, ymax):
    io = pcbnew.PCB_IO_MGR.FindPlugin(pcbnew.PCB_IO_MGR.KICAD_SEXP)  # fresh plugin: its cache goes stale after a save
    lp = os.path.abspath(lib); f = io.FootprintLoad(lp, name); n = 0
    for g in list(f.GraphicalItems()):
        if g.GetLayer() != pcbnew.F_SilkS or isinstance(g, pcbnew.PCB_TEXT): continue
        if g.GetShape() == pcbnew.SHAPE_T_SEGMENT:
            s0, e0 = g.GetStart(), g.GetEnd()
            if max(s0.y, e0.y) <= ymin or min(s0.y, e0.y) >= ymax:
                f.Remove(g); n += 1; continue
            def cl(p, q):
                if ymin <= p.y <= ymax: return p
                yt = ymin if p.y < ymin else ymax
                t = (yt - p.y) / (q.y - p.y); return pcbnew.VECTOR2I(int(p.x + t * (q.x - p.x)), int(yt))
            a, c = cl(s0, e0), cl(e0, s0)
            if (a.x, a.y) != (s0.x, s0.y) or (c.x, c.y) != (e0.x, e0.y): n += 1
            g.SetStart(a); g.SetEnd(c)
        else:
            bb = g.GetBoundingBox()
            if bb.GetTop() < ymin or bb.GetBottom() > ymax: f.Remove(g); n += 1
    io.FootprintSave(lp, f); print(name, 'silk items clipped/removed:', n)
clip('pa40.pretty', 'BNC_Molex_73100-0105_Horizontal', mm(ED), mm(100))
clip('pa40.pretty', 'Jack_3.5mm_CUI_SJ1-3523N_Horizontal_DS', mm(-100), mm(3.1 - ED))
clip('fplib/Connector_BarrelJack.pretty', 'BarrelJack_CUI_PJ-102AH_Horizontal', mm(-100), mm(13.7 - ED))
