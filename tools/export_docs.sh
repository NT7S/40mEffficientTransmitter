#!/usr/bin/env bash
# Regenerate docs/ from the schematic. Run after every schematic change.
set -euo pipefail
cd "$(dirname "$0")/.."
SCH=PCB/pa40-classe.kicad_sch
mkdir -p docs/svg
kicad-cli sch export pdf -o docs/pa40-classe_schematic.pdf "$SCH"
kicad-cli sch export netlist -o docs/pa40-classe.net "$SCH"
kicad-cli sch export svg -o docs/svg "$SCH"
kicad-cli sch erc -o docs/erc.rpt "$SCH" || true
grep -E "ERC messages|Errors|Warnings" docs/erc.rpt || true
