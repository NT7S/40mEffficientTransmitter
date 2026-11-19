# pa40-classe rev 7: routing v5 (L1 nylon-screw hole)

2026-11-19, KiCad 10.0.8. Copper routing is unchanged from v4 except that one stitching via under
the new L1 hole was dropped. Backups of the v4 state are in `old/pre-v5/`.

## L1 mounting hole
L2 and L3 already have a 3.2 mm NPTH at the core centre for an M3 nylon screw (no copper ring,
`*.Cu` + `*.Mask`). The same hole is now on L1.

- Core: Fair-Rite 5961000301 (FT-50-61), ID 7.15 mm (already cited in the footprint description).
- Hole: 3.2 mm NPTH, same type and drill as L2/L3, centred on the footprint.
- Fit: radial room in the bare ID is (7.15 − 3.2) / 2 = 1.975 mm. L1 is 26 turns of #24 (0.51 mm).
  26 × 0.51 = 13.3 mm of wire on an inner circumference of π × 7.15 ≈ 22.5 mm, so the winding is a
  single layer. After that layer the clear ID is about 7.15 − 2 × 0.51 = 6.13 mm, leaving
  (6.13 − 3.2) / 2 ≈ 1.46 mm around the screw. The same 3.2 mm drill fits; no shrink was needed.
- Courtyard is unchanged (circle plus lead tab). An "M3 nylon" F.Fab label sits inside the ID at
  (0, −2.5), slightly closer to the hole than on T80 so the 0.6 mm text stays inside the smaller ID.
- Library: `pa40.pretty/L_Toroid_FT50_Flat_P7.62mm_Drill1.0mm.kicad_mod`. `gen_fp.py` now passes
  `mount=3.2` for this footprint (do not re-run `gen_fp.py` over the tree; it would reset the
  post-processed courtyards). `layout/route.py` refreshes the L1 instance from the library after
  load so the board matches the library (FootprintNeedsUpdate is false; no lib-mismatch DRC).

## Traces and vias
- The +12V_PA 1.0 mm trace that runs under L1 (C15 to pad 1) comes no closer than 5.3 mm to the
  hole centre, which is 3.2 mm of clearance to the hole wall. No re-route was needed.
- The drain trace to pad 2 does not go under the core.
- One GND stitching via at (149.50, 149.50), 0.86 mm from the centre, sat in the new hole. The
  existing drill keep-out in the via script removed it. Closest remaining via is 3.34 mm from
  the centre. Vias: 398 stitching, 411 total (one fewer than v4).

## Checks
- DRC (`--schematic-parity --refill-zones --severity-all`): **0 violations, 0 unconnected, 0 parity**.
  Report: `layout/drc-routing.rpt`.
- ERC: unchanged (the schematic was not edited).

## Renders (blue mask, white silk, ENIG)
- `routing-v5-top.png`: 2D photo.
- `routing-v5-l1.png`: crop of L1 showing the new centre hole, with the +12V_PA trace clearing it.
- `routing-v5-3d-top.png`, `routing-v5-3d-angle.png`: 3D with `--use-board-stackup-colors`.
