# pa40-classe rev 7 — JLCPCB fabrication package

Bare boards only. Jason hand-populates from the DigiKey cart; this package has no PCBA BOM or CPL.

Upload this zip on the JLCPCB order page:

`pa40-classe-rev7-jlcpcb-gerbers.zip`

Generated 2026-11-19 (Pacific) with KiCad 10.0.8 `kicad-cli` from the committed board (`47bbfcb`). Reproduce with `fab/export.sh` from the project root.

Source for these order parameters: `print/jlcpcb-order-notes.md`.

## Order parameters (JLCPCB)

| Item | Setting |
|------|---------|
| Layers | 2 |
| PCB thickness | 1.6 mm |
| Material | FR4 |
| Outer copper weight | 1 oz (35 µm) |
| Board size | 100 × 60 mm, 3 mm corner radii, cutout on the front edge for the 3.5 mm key jack (J4) |
| Soldermask | Blue |
| Silkscreen | White |
| Surface finish | ENIG (needed for the EPC2036 LGA and the WSON-10) |
| Via covering | **Tented** (both sides). The board file already tents vias front and back, so the mask Gerbers have no openings on the 0.3 mm vias. The two U2 (TPS62175) exposed-pad vias sit inside the EP's own mask opening on top and are tented on the bottom, which keeps solder from wicking out the back. |
| Min track / space | 0.127 mm (5 mil) board rule; most of the board is 0.2 mm or more. Q1 (EPC2036) has a 0.15 mm local clearance between its 0.3 mm bumps (0.45 mm pitch), which is inside JLCPCB's standard 0.127 mm capability — no advanced-process option is needed. |
| Min drill | 0.3 mm (all vias are 0.6 / 0.3 mm); 0.5 mm hole-to-hole minimum |
| Remove order number | Optional. There is no reserved silkscreen box; if you want the number off the board, choose “Remove” (or “Specify a location”) at checkout. |
| Quantity | Your choice |
| Assembly | No — bare boards only |

## What's in the zip

Protel extensions, English filenames. The zip is only what JLCPCB's CAM needs (Gerbers + both drill files + the job file). Drill maps, the drill report, DRC report, and PNG previews stay next to the zip in this folder and are not uploaded.

| File | Layer |
|------|--------|
| `pa40-classe-F_Cu.gtl` | Top copper |
| `pa40-classe-B_Cu.gbl` | Bottom copper |
| `pa40-classe-F_Paste.gtp` | Top paste (ignored on a bare-board order; useful if you later want a stencil) |
| `pa40-classe-B_Paste.gbp` | Bottom paste (empty — no bottom SMT) |
| `pa40-classe-F_Silkscreen.gto` | Top silkscreen |
| `pa40-classe-B_Silkscreen.gbo` | Bottom silkscreen (sparse; mostly leftover TH outlines) |
| `pa40-classe-F_Mask.gts` | Top solder mask |
| `pa40-classe-B_Mask.gbs` | Bottom solder mask |
| `pa40-classe-Edge_Cuts.gm1` | Board outline |
| `pa40-classe-PTH.drl` | Plated holes (Excellon) |
| `pa40-classe-NPTH.drl` | Non-plated holes (Excellon) — L1/L2/L3 nylon-screw holes and J4 pegs |
| `pa40-classe-job.gbrjob` | Gerber job (stackup metadata) |

## Export settings

Taken from [JLCPCB's KiCad 9 Gerber guide](https://jlcpcb.com/help/article/how-to-generate-gerber-and-drill-files-in-kicad-9) (updated 2026-11-10). The same options apply in KiCad 10's CLI.

**Gerbers**

- Format: RS-274X, Protel filename extensions (`.gtl`, `.gbl`, …)
- Coordinate format: 4.6, millimetres (KiCad default; `%FSLAX46Y46*%`)
- Extended X2 format: on (embeds `FileFunction` / polarity). JLCPCB currently recommends this; do not pass `--no-x2`.
- Netlist attributes: on
- Subtract soldermask from silkscreen: on
- Check / refill zone fills before plotting: on
- Origin: absolute (same coordinate system as the drill files). The board's aux/drill origin is at (100, 100) mm, the lower-left of the outline, but JLCPCB asks for absolute, so Gerbers and drills were both exported absolute. Do not mix `--use-drill-file-origin` on one and absolute on the other.
- No worksheet / title block
- Precision: 6

**Drill**

- Excellon, millimetres, absolute origin
- Zeros: decimal format (JLCPCB recommended)
- Oval holes: alternate drill mode
- PTH and NPTH in separate files (`--excellon-separate-th`)
- Optional drill maps (Gerber X2) and a drill report are in `gerbers/` for review only

## Hole table

**Non-plated (NPTH)** — 8 holes

| Drill | Count | Use |
|------:|------:|-----|
| 3.20 mm | 3 | L1, L2, L3 M3 nylon-screw holes, centred in each toroid |
| 1.20 mm | 5 | J4 (SJ1-3523N) plastic pegs |

**Plated (PTH)** — 464 holes

| Drill | Count | Use |
|------:|------:|-----|
| 0.30 mm | 411 | Stitching and signal vias (0.6 mm pad) |
| 0.50 mm | 32 | Eight plated vias around each of H1–H4 |
| 0.80 mm | 2 holes + 3 slots | Y1 leads (2); J4 oval slots (3) |
| 0.92 mm | 1 | J2 (BNC) |
| 1.00 mm | 2 | L1 winding leads |
| 1.60 mm | 7 | L2 leads (2), L3 leads (2), J1 (3) |
| 1.80 mm | 2 | J2 (BNC) |
| 3.20 mm | 4 | H1–H4 plated M3 mounting holes, tied to GND |

## Verification

DRC with schematic parity, run on this board before export: 0 violations, 0 unconnected, 0 parity.

PNG previews (pygerber, 20 dpmm) are in `previews/`. Checked:

- Outline is 100 × 60 mm with 3 mm rounded corners and the J4 front-edge cutout
- L1/L2/L3 each have a 3.2 mm NPTH in the core; H1–H4 are 3.2 mm plated in the four corners
- “Rev 7” is in top copper; Etherkit and OSHW logos, “NT7S 2026”, “+12 VDC In”, “Key”, and “Antenna” are on top silk
- The 411 × 0.3 mm vias are tented: no 0.3/0.6 mm apertures in either mask Gerber, and the pour regions in the mask plots are solid
