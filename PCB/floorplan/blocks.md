# pa40-classe rev 7: PCB floorplan blocks (v2, 2026-11-19)

Board 100 x 60 mm, 3 mm corner radius, 2 layers, FR-4 1.6 mm. No parts placed yet.

**Edges:** the top edge (y = 0) is the BACK (rear panel) and holds J1 DC in and J2 RF out. The bottom edge (y = 60) is the FRONT (front panel) and holds the J4 key jack. This follows Jason's 2026-11-19 review.

Coordinates are board-relative mm: origin at the back-left corner, x to the right, y toward the front. In `pa40-classe.kicad_pcb` that corner is at absolute (100, 100) mm, and the aux and grid origins are set there.

Block membership follows the schematic sections and block titles in `gen.py`, which generates `pa40-classe.kicad_sch`. The refdes list was checked against a fresh netlist export (`floorplan/net-rev7.xml`): all 68 parts appear exactly once. The v1 floorplan, with the jacks on the left and right edges, is in `old/pre-backfront/`.

| Block | Schematic block (gen.py) | Region x1,y1 to x2,y2 | Size W x H | Refdes |
|---|---|---|---|---|
| DC IN + SHUNT | 12.0 V input, current shunt and decoupling | 0.8,0 to 29.5,21 (9.5 mm corner notch for the mounting hole) | 28.7 x 21.0 | J1 R12 JP1 TP1 TP2 TP3 C10 C11 C12 |
| 5 V BUCK | 5 V buck: TPS62175 (TI SLVSB35C Fig. 8), ferrite-bead filtered | 30,0.8 to 43.5,15 | 13.5 x 14.2 | U2 L4 FB2 FB3 C21 C22 C23 R13 R14 TP12 TP13 |
| 7.030 MHz PIERCE XO | 7.030 MHz Pierce oscillator (MMBT3904, about 0.8 mA) | 0.8,28 to 24.5,59.2 (9.5 mm corner notch for the mounting hole) | 23.7 x 31.2 | Q4 Y1 C5 C6 C7 C8 C9 C20 R5 R6 R7 R8 R9 R10 R11 TP8 TP9 |
| GATE DRIVE | Gate drive | 30,20 to 41.5,37 | 11.5 x 17.0 | U1 C13 R1 D1 TP4 TP5 |
| PA KEYING | PA keying (PMOS high side, as OpenBeacon 2) | 25,38 to 41.5,60 | 16.5 x 22.0 | J4 Q2 R2 R3 C4 TP14 TP15 |
| CLASS E CORE | Class E stage: L1 feed, C1 (part of the schematic's class E block) | 42,30.2 to 57.5,59.2 | 15.5 x 29.0 | Q1 L1 C1 C14 C15 TP6 TP7 |
| 3-POLE ELLIPTIC LPF | 3-pole elliptic LPF (trap 14.06 MHz) | 53.8,0.8 to 79.5,29.8 | 25.7 x 29.0 | C16 L3 C17 C18 C19 |
| CLASS E: C2-L2 TANK + C3 | Class E stage: C2-L2 tank, C3 match (part of the schematic's class E block) | 58.5,30.2 to 84,59.2 | 25.5 x 29.0 | C2 L2 C3 TP10 TP11 |
| RF OUT | J2 RF out, 50 ohm | 79.6,0 to 91.4,16.5 | 11.8 x 16.5 | J2 |
| BRANDING | (board text and logos, no schematic parts) | 84.5,17.5 to 99.2,40 | 14.7 x 22.5 | - |

Spare: x 42-53.8, y 0.8-29.8, between the buck and gate drive and L3, is left as GND pour. So is the y 21-28 strip between the DC input and the XO.

## Large-part envelopes (User.2)

Each envelope is the courtyard extent read from the project footprint, rotated to its floorplan orientation. For the jacks, only the part on the board is drawn.

| Ref | Envelope x1,y1 to x2,y2 | Note |
|---|---|---|
| J1 | 12,0 to 23.5,15.5 | back edge, plug entry facing off the back; body front flush with the edge |
| J2 | 79.9,0 to 91.3,13.8 | back edge; Molex 73100-0105 origin on the edge, 13.5 mm of body overhangs the back |
| J4 | 28,47.55 to 40.5,60 | front edge; the footprint Edge.Cuts notch (4.4 x 1.4 mm) lands on the front edge |
| L1 | 42.025,39.36 to 55.975,56.475 | FT50-61 flat, core r 6.975 at (49,49.5), leads up toward Q1 |
| L3 | 54.15,1.65 to 75.85,26.85 | T80-6 flat (LPF), core r 10.85 at (65,12.5), leads down toward the out_50r strip |
| L2 | 61.15,33.15 to 82.85,58.35 | T80-6 flat (tank), core r 10.85 at (72,47.5), leads up toward the out_50r strip |
| Y1 | 4,42 to 20.1,48.1 | HC-49 THT/SMD combo, kept in the lower part of the XO block |
| C10 | 1.5,9.8 to 10.9,16.9 | 100 uF 6.3x7.7 electrolytic |
| R12 | 24.6,2.5 to 28.4,11.3 | WSK2512 Kelvin shunt |

## Spacing checks (edge to edge; toroids measured from the core circle)

- L2 to L3: 14.0 mm (13.3 mm in v1). L1 to L2: 5.3 mm (same as v1). L1 to L3: 22.5 mm.
- L3 to the J2 envelope: 4.1 mm. L2 to the J2 envelope: 23.8 mm.
- Buck block to L3: 10.7 mm (v1: 15.1 mm to L3). Buck to L2: 32.4 mm. Buck to L1: 28 mm.
- XO block to buck block: 14.1 mm (v1: 20 mm). Y1 envelope to buck block: 28.8 mm (v1: 25.4 mm).
- XO block to J1: 12.5 mm. XO block to the DC block: 7 mm, across a free GND strip. Y1 to J1: 26.5 mm.
- XO block to L1: 17.5 mm. Y1 to L1: 22 mm. XO to L3: 32.5 mm. XO to L2: 36.6 mm. XO block to the class E core block: 17.5 mm.
- Keying block to L1 envelope: 0.5 mm (Q2 to L1 +12V_PA path is short). Gate drive block to the class E core block: 0.5 mm.
- Jack envelopes to mounting-hole centres: J1 8.0 mm, J2 4.7 mm, J4 24 mm. All are outside the 4.5 mm keepout radius.

## Layers

- **Edge.Cuts:** 100 x 60 mm outline with 3 mm-radius corner arcs.
- **User.1, named Floorplan:** block regions, labels, hole keepout circles, the BACK and FRONT edge labels, and the notes below the board.
- **User.2, named Envelopes:** large-part courtyard boxes, plus the toroid core circles.
- **F.SilkS:** "40m Class E TX", "etherkit.com 2026", "Creative Commons" and "CC-BY-SA 4.0".
- **F.Cu:** "Rev 7", kept with the branding block as on Si5351AVFO.
- **Holes:** H1 to H4 use MountingHole_3.2mm_M3_Pad_Via (3.2 mm plated hole, 6.4 mm pad and 8 stitching vias), centred 4 mm in from both edges. They are board-only and have no net yet. The footprint is in the project lib `fplib/MountingHole.pretty`.

## Notes

- FLOORPLAN rev 7 v2, no parts placed. Board 100 x 60 mm, 3 mm corner radius, 2 layers, FR-4 1.6 mm. Top edge (y=0) = BACK, bottom edge (y=60) = FRONT. Origin = back-left corner. Blue (User.1) = blocks; orange (User.2) = courtyards of the large parts (on-board part only; the J1 and J2 bodies overhang the back edge, the J4 nose the front edge); red = F.Cu; green = F.SilkS.
- Signal: XO -> U1 gate drive -> Q1 -> C2-L2 tank -> C3 (out_50r strip between L2 and L3) -> LPF (C16, L3 || C17+C18, C19) -> J2 on the back edge. DC: J1 -> R12/JP1 -> +12V run down the x=25-30 channel -> Q2 keyed +12V_PA -> L1; +12V -> U2 buck -> +5V to XO and U1.
- B.Cu: unbroken GND plane. Top GND pour stitched to it, with a via fence around L2/L3, C16-C19 and J2. GND vias at the Q1 source, C1 and C3 ground pads; keep the U1-R1-Q1 gate loop and the Q1-C1 drain loop tight.
- L2 and L3 lie flat, so both axes are normal to the board: isolation is by spacing (cores 14 mm apart edge to edge). Keep L4 (buck) away from L2/L3 (gen.py note 12) and from Y1. The free strip y=21-28 at the left is GND pour between the DC input and the XO.
- H1-H4: MountingHole_3.2mm_M3_Pad_Via, 4 mm in from both edges; circles = 4.5 mm radius keepout. The J4 footprint carries its own Edge.Cuts notch: split the front edge at J4 when it is placed.
