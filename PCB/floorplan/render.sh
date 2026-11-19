#!/bin/bash
# Render the floorplan PNG from the board with kicad-cli, recolored for a white background.
set -e
cd "$(dirname "$0")"
kicad-cli pcb export svg --mode-single --exclude-drawing-sheet --page-size-mode 1 \
  -l Edge.Cuts,User.1,User.2,F.SilkS,F.Cu -o fp-raw.svg ../pa40-classe.kicad_pcb >/dev/null
python3 - <<'P'
import re
s=open('fp-raw.svg').read()
for a,b in {'D0D2CD':'000000','C2C2C2':'1F4E9A','5994DC':'B35900','F2EDA1':'1B7F3A','C83434':'C00000'}.items():
    s=s.replace('#'+a,'#'+b)
x,y,w,h=97,95.5,106,88
s=re.sub(r'width="[^"]+" height="[^"]+" viewBox="[^"]+"',f'width="{w}mm" height="{h}mm" viewBox="{x} {y} {w} {h}"',s,count=1)
s=s.replace('<title>',f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="#FFFFFF" stroke="none"/><title>',1)
open('pa40-floorplan-rev7.svg','w').write(s)
P
rsvg-convert -b white -w 3200 pa40-floorplan-rev7.svg -o pa40-floorplan-rev7.png
echo rendered
rm -f fp-raw.svg
