#!/usr/bin/env python3
"""Top-view placement render (technical red-copper; for the blue-mask photo look use render_cu.py).

Top-view placement render: kicad-cli SVG of F.Cu/F.SilkS/F.Fab/F.Courtyard/Edge.Cuts plus a ratsnest overlay
(minimum spanning tree of pad centres per net, computed here because kicad-cli does not plot ratsnest) and faint floorplan blocks."""
import pcbnew, subprocess, sys, os, math, re
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'floorplan'))
import blocks
PRJ = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); os.chdir(PRJ)
out = sys.argv[1] if len(sys.argv) > 1 else 'layout/placement-v1-top.png'
svg = '/tmp/r/top.svg'; os.makedirs('/tmp/r', exist_ok=True)
subprocess.run(['kicad-cli', 'pcb', 'export', 'svg', '--mode-single', '--exclude-drawing-sheet', '--page-size-mode', '0',
                '-l', 'Edge.Cuts,F.Cu,F.SilkS,F.Fab,F.Courtyard', '-o', svg, 'pa40-classe.kicad_pcb'], check=True, capture_output=True)
b = pcbnew.LoadBoard('pa40-classe.kicad_pcb')
pads = {}
for f in b.GetFootprints():
    for p in f.Pads():
        n = p.GetNetname()
        if n and not n.startswith('unconnected'):
            pads.setdefault(n, []).append((pcbnew.ToMM(p.GetPosition().x), pcbnew.ToMM(p.GetPosition().y), f.GetReference()))
lines = []
for n, pts in pads.items():
    # one point per footprint+location (merge same-net pads of one footprint that are within 1 mm)
    if len(pts) < 2: continue
    inT = [0]; rest = list(range(1, len(pts)))
    while rest:
        bd = None
        for i in inT:
            for j in rest:
                d = math.dist(pts[i][:2], pts[j][:2])
                if bd is None or d < bd[0]: bd = (d, i, j)
        _, i, j = bd; inT.append(j); rest.remove(j)
        if pts[i][2] != pts[j][2] or n != 'GND': lines.append((n, pts[i][:2], pts[j][:2]))
g = ['<g id="ratsnest" style="fill:none;stroke-linecap:round">']
for n, a, c in lines:
    col, w, op = ('#2a7f2a', 0.10, 0.45) if n == 'GND' else ('#0050ff', 0.13, 0.85)
    g.append(f'<line x1="{a[0]:.3f}" y1="{a[1]:.3f}" x2="{c[0]:.3f}" y2="{c[1]:.3f}" stroke="{col}" stroke-width="{w}" stroke-opacity="{op}"/>')
g.append('</g><g id="blocks" style="fill:none;stroke:#ff8c00;stroke-width:0.12;stroke-dasharray:0.8 0.6;stroke-opacity:0.7">')
for bl in blocks.BLOCKS:
    pts = ' '.join(f'{x + 100:.2f},{y + 100:.2f}' for x, y in bl['poly'])
    g.append(f'<polygon points="{pts}"/>')
    lx, ly = bl['poly'][0]
g.append('</g>')
s = open(svg).read()
s = re.sub(r'viewBox="[^"]*"', 'viewBox="96 84 108 80"', s, count=1)
s = re.sub(r'width="[^"]*" height="[^"]*"', 'width="2160" height="1600"', s, count=1)
s = s.replace('<title>', '<rect x="0" y="0" width="400" height="300" fill="#ffffff"/><title>', 1)
s = s.replace('</svg>', '\n'.join(g) + '\n</svg>')
open('/tmp/r/top2.svg', 'w').write(s)
subprocess.run(['rsvg-convert', '-b', 'white', '-o', out, '/tmp/r/top2.svg'], check=True)
print('wrote', out, len(lines), 'ratsnest lines')
