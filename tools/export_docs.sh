#!/usr/bin/env bash
# Regenerate docs/ from the schematic and (if present) the PCB.
set -euo pipefail
cd "$(dirname "$0")/.."
SCH=PCB/pa40-classe.kicad_sch
PCB=PCB/pa40-classe.kicad_pcb
mkdir -p docs/svg docs/layout
kicad-cli sch export pdf -o docs/pa40-classe_schematic.pdf "$SCH"
kicad-cli sch export netlist -o docs/pa40-classe.net "$SCH"
kicad-cli sch export svg -o docs/svg "$SCH"
kicad-cli sch erc --severity-all -o docs/erc.rpt "$SCH" || true
grep -E "ERC messages|Errors|Warnings" docs/erc.rpt || true
if [[ -f "$PCB" ]]; then
  kicad-cli pcb drc --schematic-parity --refill-zones --severity-all -o docs/drc.rpt "$PCB" || true
  grep -E "Found [0-9]|violations|unconnected|parity" docs/drc.rpt || true
  # latest layout renders and notes, if present
  if [[ -d PCB/layout ]]; then
    cp -a PCB/layout/routing-v5-*.png PCB/layout/routing-v5.md docs/layout/ 2>/dev/null || true
  fi
fi
