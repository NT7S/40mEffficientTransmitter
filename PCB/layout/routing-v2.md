# pa40-classe rev 7: routing v2

2026-11-19, KiCad 10.0.8. Follows routing v1 (`routing-v1.md`, still valid for everything not listed here).
`layout/route.py` regenerates the whole board from `old/pre-routing/pa40-classe.after-L2swap.kicad_pcb`.
Backups of the v1 state are in `old/pre-v2/`.

Jason's review of v1: the +12V_PA trace under L1 and the SLEEP loop around L4 are fine as they are.

## Changes
1. **H1-H4 grounded.**
   - Schematic: four `Mechanical:MountingHole_Pad` symbols (H1-H4, in_bom no) with GND power symbols
     (#PWR44-#PWR47) and a text label. They are placed in the empty area to the right of the PA keying block.
     This was a small in-place edit; `gen.py` has the matching code (FP entries plus a loop before `emit_wires()`),
     and the new instances are what gen.py emits. gen.py was not re-run on the real file, so the existing UUIDs and
     footprint links are unchanged.
   - Board: the existing `MountingHole_3.2mm_M3_Pad_Via` footprints are kept (same 3.2 mm plated hole, 6.4 mm pad,
     8 stitching vias, same positions). They are now linked to the new symbols (path, sheet), the board-only
     attribute is removed, all pads are on GND, and the value is set to `MountingHole_Pad`. They connect to both
     pours with thermal spokes (PTH rule of the zone).
2. **Q1 source bumps no longer flood to the pour.**
   - Before: source bumps 2 and 4 were solid to the F.Cu GND pour (zone rule: THT thermal / SMD solid), while gate
     and drain saw only 0.25 mm traces. Hot air or reflow would bring the gate/drain bumps to temperature first, and
     the source bumps, heat-sunk by the pour and plane, could lag (tilt, cold joint).
   - Chosen: **no zone connection** (pad local override `ZONE_CONNECTION_NONE`) on pads 2 and 4, plus an F.Cu
     "Q1 bump no-pour" rule area (146.0-148.0 x 133.75-135.45) so the pour cannot reach the bump area at all.
     Thermal relief was not used: on a 0.3 mm bump the spokes (0.5 mm wide, with 0.3 mm gap) would be wider than
     the pad and could not fit between the 0.15 mm bump gaps, so they would act as an uncontrolled solid strap.
   - Each source bump now leaves on its own 0.25 mm neck (same width as gate and drain), straight down. The two
     necks join a 0.6 mm bar 0.78 mm below the bump centres. From that bar, 0.6 mm tracks go to source via W
     (145.5/135.85, 1.3 mm), to C14/C15 GND, and to C1 GND / source via SE (147.9/136.9). The third via (148.2/138.0)
     is through the pour.
   - All four bumps now see similar copper: a 0.25 mm neck about 0.5-0.7 mm long before wider copper.
   - Added source path: about 0.5 mm of 0.25 mm neck per bump before the bar or pour (they used to touch the pour
     about 0.3 mm from the bump edge). The two necks are in parallel, about 0.15 nH added in total. That is small
     next to the C1/C14/C15 package inductance. The via distance is unchanged.
3. **Via tenting.** Board setup tents vias front and back (`m_TentViasFront/Back` set in route.py; it was already
   on). Order note: `print/jlcpcb-order-notes.md`.
4. Stitching vias: the script now keeps 4.5 mm away from the mounting-hole centres, because the grounded hole pads
   would otherwise allow a corner via outside the pour. 414 stitching vias, 427 vias in total.

## Checks
- ERC: **0 errors**, 24 warnings (`lib_symbol_mismatch`, the same pre-existing set as v1). Report: `erc.rpt`.
- DRC (`--schematic-parity --refill-zones --severity-all`): **0 violations (errors and warnings), 0 unconnected,
  0 parity**. Report: `layout/drc-routing.rpt` / `.json`.

## Renders
- `routing-v2-top.png`: F.Cu, F.SilkS and Edge.Cuts.
- `routing-v2-bottom.png`: B.Cu, seen from the top.
- `routing-v2-q1-zoom.png`: a 5 x 4 mm crop of F.Cu + F.Fab around the four bumps.

## Note on gen.py
gen.py now reads the KiCad 10 symbol libraries. Some library pin positions differ from the KiCad 9 copies embedded
in the schematic (R_Shunt, SolderJumper), so a full gen.py re-run would also move a few wire ends. This is the same
cause as the 24 ERC lib_symbol_mismatch warnings. It is not from this change, but it is one more reason not to
re-run gen.py over the real schematic.
