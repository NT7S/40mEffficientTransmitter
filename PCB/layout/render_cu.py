#!/usr/bin/env python3
"""Board renders for pa40-classe.

Default is a 2D 'photo' look: blue solder mask, white silk, ENIG (gold) pads, matching the
board stackup and `kicad-cli pcb render --use-board-stackup-colors`. Pass --technical for the
old red-copper / yellow-silk review drawing (plus optional ratsnest from layout/drc-routing.json).

usage: render_cu.py OUT.png [LAYERS] [x0 y0 w h] [--technical] [--no-rats] [--px=N]

LAYERS is used only with --technical (default Edge.Cuts,F.Cu,F.SilkS). Photo mode always uses
Edge.Cuts + F.Cu + F.Mask + F.SilkS. The optional x0 y0 w h crop is in KiCad page millimetres
(the board sits at 100,100 on the A4 page).
"""
import subprocess, sys, os, re, json, numpy as np
from PIL import Image, ImageDraw
PRJ = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); os.chdir(PRJ)
args = sys.argv[1:]
flags = {a for a in args if a.startswith('--')}
a = [x for x in args if not x.startswith('--')]
technical = '--technical' in flags
out = a[0]
layers = a[1] if (technical and len(a) > 1 and not re.match(r'^-?\d', a[1])) else 'Edge.Cuts,F.Cu,F.SilkS'
rest = a[2:] if layers in a[1:2] else a[1:]
vb = rest[:4] if len(rest) >= 4 else ['96', '84', '108', '80']
px = 2160
for x in flags:
    if x.startswith('--px='): px = int(x[5:])
os.makedirs('/tmp/r', exist_ok=True)
w, h = float(vb[2]), float(vb[3])
py = int(px * h / w)

def export_svg(path, layers):
    subprocess.run(['kicad-cli', 'pcb', 'export', 'svg', '--mode-single', '--exclude-drawing-sheet',
                    '--page-size-mode', '0', '--drill-shape-opt', '2', '-l', layers,
                    '-o', path, 'pa40-classe.kicad_pcb'], check=True, capture_output=True)
    s = open(path).read()
    s = re.sub(r'viewBox="[^"]*"', 'viewBox="%s"' % ' '.join(vb), s, count=1)
    s = re.sub(r'width="[^"]*" height="[^"]*"', f'width="{px}" height="{py}"', s, count=1)
    return s

if technical:
    svg = '/tmp/r/cu.svg'
    s = export_svg(svg, layers)
    g = ['<g id="rats" style="fill:none;stroke:#ff00ff;stroke-width:0.12;stroke-linecap:round">']
    if '--no-rats' not in flags and os.path.exists('layout/drc-routing.json'):
        for u in json.load(open('layout/drc-routing.json')).get('unconnected_items', []):
            p = [i['pos'] for i in u['items']]
            if len(p) == 2:
                g.append(f'<line x1="{p[0]["x"]}" y1="{p[0]["y"]}" x2="{p[1]["x"]}" y2="{p[1]["y"]}"/>')
    g.append('</g>')
    s = s.replace('<title>', '<rect x="0" y="0" width="4000" height="4000" fill="#ffffff"/><title>', 1)
    s = s.replace('</svg>', '\n'.join(g) + '\n</svg>')
    open('/tmp/r/cu2.svg', 'w').write(s)
    subprocess.run(['rsvg-convert', '-o', out, '/tmp/r/cu2.svg'], check=True)
    print('wrote', out, 'technical')
    sys.exit(0)

# ---- photo: blue mask, white silk, ENIG pads (colours sampled from kicad-cli stackup 3D) ----
BLUE = np.array((98, 98, 202), np.uint8)       # solder mask
TRACE = np.array((51, 92, 202), np.uint8)      # copper under the mask
GOLD = np.array((244, 216, 35), np.uint8)      # ENIG
FR4 = np.array((196, 168, 96), np.uint8)       # mask opening over bare laminate
HOLE = np.array((40, 47, 47), np.uint8)
SILK = np.array((255, 255, 255), np.uint8)
EDGE = np.array((40, 40, 50), np.uint8)
BG = np.array((255, 255, 255), np.uint8)

def raster(layers, key_hex, bg='#000000'):
    """Raster one or more layers. Pixels that differ from bg are 'on' (layer presence)."""
    raw = '/tmp/r/ly.svg'
    s = export_svg(raw, layers)
    s = s.replace('<title>', f'<rect x="0" y="0" width="4000" height="4000" fill="{bg}"/><title>', 1)
    open('/tmp/r/ly2.svg', 'w').write(s)
    png = '/tmp/r/ly.png'
    subprocess.run(['rsvg-convert', '-o', png, '/tmp/r/ly2.svg'], check=True)
    im = np.array(Image.open(png).convert('RGB'))
    # 'on' = not the background colour
    bgv = tuple(int(bg[i:i+2], 16) for i in (1, 3, 5))
    on = np.any(im != bgv, axis=2)
    return im, on

cu_im, cu = raster('F.Cu', '#C83434')
# holes are plotted black on the copper layer (drill-shape-opt 2)
hole = np.all(cu_im == (0, 0, 0), axis=2) & cu
cu = cu & ~hole
_, msk = raster('F.Mask', '#D864FF')          # F.Mask plot = openings
silk_im, silk = raster('F.SilkS', '#FFFFFF')
# silk is white: with a black bg, any non-black is silk (and some fab-dark glyphs). redo silk with explicit detect of near-white
# already: non-black on silk layer. Copper-colored? silk should be white. Fine.
_, edge = raster('Edge.Cuts', '#D0D2CD')

# board interior: flood-fill from a point known to be on the board (150, 130) mm
# pick a seed that's inside this crop and on the board (crop centre, then known interior points)
seeds = [(float(vb[0]) + w/2, float(vb[1]) + h/2), (150, 130), (120, 120), (180, 140), (110, 110), (190, 150)]
ix = iy = None
for sx, sy in seeds:
    cx, cy = int((sx - float(vb[0])) / w * px), int((sy - float(vb[1])) / h * py)
    if 0 <= cx < px and 0 <= cy < py and not edge[cy, cx]:
        ix, iy = cx, cy; break
if ix is None:
    ix, iy = px//2, py//2
board = np.zeros((py, px), dtype=bool)
# flood from (ix,iy) staying off the edge lines and off the outside
# Use a simple iterative fill on a padded copy
from collections import deque
vis = edge.copy()
if 0 <= ix < px and 0 <= iy < py and not vis[iy, ix]:
    q = deque([(ix, iy)])
    vis[iy, ix] = True
    while q:
        x, y = q.popleft()
        board[y, x] = True
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = x + dx, y + dy
            if 0 <= nx < px and 0 <= ny < py and not vis[ny, nx]:
                vis[ny, nx] = True
                q.append((nx, ny))

img = np.tile(BG, (py, px, 1))
img[board] = BLUE
img[board & cu & ~msk] = TRACE
img[board & cu & msk] = GOLD
img[board & ~cu & msk & ~hole] = FR4
img[hole] = HOLE
img[silk & board] = SILK
img[edge] = EDGE
Image.fromarray(img, 'RGB').save(out)
print('wrote', out, 'photo', px, 'x', py, 'board_px', int(board.sum()))
