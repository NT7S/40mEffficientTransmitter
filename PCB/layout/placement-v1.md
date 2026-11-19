# pa40-classe rev 7: placement v1 (no routing)

Created 2026-11-19 with KiCad 10.0.8. Board saved in KiCad 10 format (20260206).
The board is rebuilt by `layout/place.py old/pre-placement/pa40-classe.kicad_pcb`. Edit the PL / MANUAL tables there to move parts.

## Checks
- DRC: `kicad-cli pcb drc --schematic-parity --refill-zones --severity-all` (KiCad 10.0.8). Output is in `layout/drc-placement.rpt` and `.json`.
  - 0 violations
  - 0 schematic-parity issues
  - 113 unconnected items (nothing is routed yet)
- Parts: 68 schematic footprints with nets, plus H1-H4.
  - H1-H4 are board-only: no symbol, no net.

## Renders
- `placement-v1-top.png`: F.Cu, F.SilkS, F.Fab, F.CrtYd and Edge.Cuts.
  - Ratsnest overlay: blue for signal nets, faint green for GND.
  - Orange dashed outlines show the v2 floorplan blocks.
- `placement-v1-3d-top.png`, `placement-v1-3d-angle.png`: viewed from the back edge, showing J1 and J2.

## Library changes (originals are in `old/pre-placement/libs/`)
- **3D model references added:**
  - Project VRMLs from `layout/make_3d.py` (low-fidelity): BNC, PJ-102AH, both toroids, the HC-49 combo, the JZ trimmer, EPC2036 and Keystone 5019.
  - Substitute stock models:
    - LPS4018 uses the Bourns SRN4018 model.
    - WSK2512 uses the R_2512_6332Metric model.
- **Toroid courtyards (T80, FT50):** the rectangle is replaced with the body outline, i.e. the core circle plus a lead tab around the pads.
- **Connector silkscreen** is clipped at the board edge on the BNC, the SJ1-3523N and the PJ-102AH (in the project fplib copy).
