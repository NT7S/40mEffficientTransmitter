#!/bin/sh
# Run from the KiCad project directory (the parent of this script).
cd "$(dirname "$0")/.."
timeout 300 kicad-cli pcb drc --schematic-parity --refill-zones --severity-all --format json -o layout/drc-routing.json pa40-classe.kicad_pcb >/dev/null 2>&1
python3 - <<'P'
import json,collections
d=json.load(open('layout/drc-routing.json'))
for k in ('violations','unconnected_items','schematic_parity'):
    v=d.get(k,[]); print(k,len(v),dict(collections.Counter(x['type'] for x in v)))
for x in d['violations']+d.get('schematic_parity',[]):
    print(x['type'],'|',x['description'][:90],'|',' / '.join(i['description'] for i in x['items']))
P
