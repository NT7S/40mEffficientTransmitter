# 40mEffficientTransmitter

A crystal-controlled 5 W 40 m CW transmitter built for the 2027 FDIM QRP Transmitter Efficiency Challenge, which scores the DC-to-RF efficiency of the whole transmitter at 12.0 V and 4-6 W into 50 Ω.

The power stage is a single-ended class-E amplifier using an EPC2036 eGaN FET, designed with Sokal's equations and followed by a 3-pole elliptic low-pass filter. A discrete Pierce oscillator on 7.030 MHz, a 5 V Schmitt buffer (SN74LVC1G17) as gate driver, a high-side PMOS keying switch and a TPS62175 buck converter complete the transmitter. In ngspice the PA with its filter delivers 5.10 W at 96.4 % drain efficiency, and the estimated whole-transmitter efficiency is 95.6 %. These are simulation results, not measurements.

The full design justification, simulation results, build plan and test plan are in the [design report](report/report.pdf).

## Status

Prototype, **rev 7**. The PCB layout is complete: 100 × 60 mm, 2-layer, 1.6 mm FR4, designed for JLCPCB (blue soldermask, white silkscreen, ENIG, tented vias). DRC is clean (0 violations, 0 unconnected items, 0 schematic-parity issues). ERC reports 0 errors.

Prototype revisions are numbered (1, 2, 3, ...). Letters, starting from A, are kept for released boards. Revisions 1-6 were first labelled A-F.

| Rev | Was | Change |
|-----|-----|--------|
| 1 | A | Class-E PA stage with tank and L-match, no LPF |
| 2 | B | 3-pole elliptic LPF added |
| 3 | C | Discrete Pierce oscillator replaces the external drive; PMOS keying of the PA rail; trap junctions moved clear of L3 |
| 4 | D | Q3/R4 removed (key shorts R3 to GND); optional R12 shunt with TP1/TP2 and JP1; trimmable oscillator (C9) |
| 5 | E | SMT parts; TPS62175 buck with ferrite-bead filters; footprints and MPNs for every part |
| 6 | F | Probe test points TP4-TP15 with GND pads; DNP gate clamp D1; gate R1/clamp study |
| 7 | - | J1 DC barrel jack (Same Sky PJ-102AH), J4 3.5 mm key jack (Same Sky SJ1-3523N); J2 changed to Molex 0731000105 (DigiKey WM5524-ND) |

Only rev 7 files are in this repository.

## Folders

| Folder | Contents |
|--------|----------|
| [`PCB/`](PCB/) | KiCad 10.0.8 project (`pa40-classe`): schematic, board, custom design rules, project symbol library `pa40.kicad_sym`, project-local footprint libraries in `PCB/lib/` (`pa40.pretty` plus the KiCad stock subset the design uses, including `MountingHole.pretty`), 3-D models in `PCB/pa40.3dshapes/`, layout scripts and notes in `PCB/layout/`, the floorplan in `PCB/floorplan/`, and the JLCPCB Gerber package in [`PCB/production/`](PCB/production/) |
| [`docs/`](docs/) | Schematic PDF and SVG, netlist, ERC and DRC reports, footprint renders, [layout renders](docs/layout/), [datasheet links](docs/datasheets.md) |
| [`bom/`](bom/) | DigiKey BOM with prices and stock (`bom-digikey-rev7.csv`), BOM bulk-add file for one board, and cart file for two boards plus spares |
| [`report/`](report/) | LaTeX source and built PDF of the design report, with the scripts that write its tables |
| [`sim/`](sim/) | ngspice decks and Python scripts for the PA, LPF, keying, oscillator and gate-drive simulations |
| [`print/`](print/) | Printable DigiKey cart checklist, and [JLCPCB order notes](print/jlcpcb-order-notes.md) |
| [`tools/`](tools/) | Schematic and footprint generators, and `export_docs.sh` |

## Building

- Bare boards from JLCPCB. Upload [`PCB/production/pa40-classe-rev7-jlcpcb-gerbers.zip`](PCB/production/pa40-classe-rev7-jlcpcb-gerbers.zip); order parameters and a hole table are in [`PCB/production/README.md`](PCB/production/README.md) (also `print/jlcpcb-order-notes.md`). Parts from DigiKey; the boards are hand-populated.
- Y1 is not in the DigiKey cart. Supply your own 7.030 MHz HC-49 crystal. The footprint takes an HC-49/US crystal, through-hole (4.88 mm lead pitch) or SMD. The BOM part (IQD LFXTAL011525Bulk) is CL 30 pF, but the oscillator simulation assumed CL 20 pF, so trim C9 for frequency.
- L1-L3 are hand-wound toroids (L1 FT-50-61; L2, L3 T80-6) and are not in the DigiKey cart. Winding data is in the report.
- D1 is unfitted. JP1 is a solder jumper: bridge it if R12 is not fitted.
- U2 (TPS62175DQCR) was out of stock at DigiKey on 18 Nov 2026. Check stock and prices in the cart before ordering.

## Regenerating

The committed schematic and footprints already include later in-place edits (L2 pin swap, L1 nylon-screw hole, Etherkit and OSHW logos, courtyard post-processing). Do not re-run `gen.py` or `gen_fp.py` against the live files unless you intend to regenerate from scratch; both assign new UUIDs and `gen_fp.py` would drop the post-processed courtyards.

- Schematic (from scratch only): `gen.py` writes the schematic, the symbol library and `sym-lib-table`. Run it from `PCB/` (`cd PCB && python3 ../tools/gen.py`). It reads KiCad's stock symbols from `/usr/share/kicad/symbols/`.
- Footprints (from scratch only): `python3 tools/gen_fp.py` rewrites `PCB/lib/pa40.pretty`.
- Layout: from `PCB/`, `python3 layout/route.py` reloads the board, strips tracks and zones, and re-routes. Then `sh layout/drc.sh` (needs `kicad-cli`). Top copper photo: `python3 layout/render_cu.py`. 3-D views: `python3 layout/make_3d.py` (pass `--use-board-stackup-colors` is already built in). The latest renders and notes are `PCB/layout/routing-v5-*.png` and `PCB/layout/routing-v5.md`.
- Docs: `tools/export_docs.sh` rewrites the schematic PDF, netlist, SVG, `docs/erc.rpt` and, when the board is present, `docs/drc.rpt` and copies the v5 layout renders into `docs/layout/`.
- Fabrication Gerbers: from the project root, `PCB/production/export.sh` (or `fab/export.sh` in the work tree) writes Gerbers and drill files with JLCPCB's KiCad settings. Zip only the layer files, the two `.drl` files, and the `.gbrjob` as `pa40-classe-rev7-jlcpcb-gerbers.zip`.
- Report: in `report/`, run `python3 gen_tables.py`, `python3 gen_budget_table.py` and `python3 gen_gate_tables.py`, then `latexmk -pdf -jobname=report main.tex`.
- Simulations: the decks in `sim/` run in ngspice. Raw waveform output (`.dat`, `.dat.gz`, `.npz`) is not committed; rerun the scripts to regenerate it.

## License

This work is licensed under the [Creative Commons Attribution-ShareAlike 4.0 International License](https://creativecommons.org/licenses/by-sa/4.0/); see `LICENSE`. Third-party SPICE models in `sim/` keep their original copyright notices and terms.
