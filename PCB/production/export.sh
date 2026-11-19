#!/usr/bin/env bash
# Export JLCPCB Gerber + drill package for pa40-classe rev 7.
# Settings follow JLCPCB's KiCad 9 guide (updated 2026-11-10):
#   https://jlcpcb.com/help/article/how-to-generate-gerber-and-drill-files-in-kicad-9
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUT="$ROOT/fab/gerbers"
mkdir -p "$OUT"
rm -f "$OUT"/*

cd "$ROOT"
kicad-cli pcb export gerbers \
  --output "$OUT" \
  --layers F.Cu,B.Cu,F.Paste,B.Paste,F.Silkscreen,B.Silkscreen,F.Mask,B.Mask,Edge.Cuts \
  --subtract-soldermask \
  --check-zones \
  --precision 6 \
  pa40-classe.kicad_pcb

kicad-cli pcb export drill \
  --output "$OUT" \
  --format excellon \
  --drill-origin absolute \
  --excellon-units mm \
  --excellon-zeros-format decimal \
  --excellon-oval-format alternate \
  --excellon-separate-th \
  --generate-map \
  --map-format gerberx2 \
  --generate-report \
  --report-path "$OUT/pa40-classe-drill-report.rpt" \
  pa40-classe.kicad_pcb

echo "Exported to $OUT:"
ls -la "$OUT"
