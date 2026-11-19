"""Floorplan data for rev 7, v2: J1 and J2 on the back edge (top, y=0), J4 on the front edge (bottom, y=60).
Block membership follows the gen.py schematic sections and block titles.
Board-relative mm: origin = board top-left (back-left corner), x right, y down (toward the front). Board 100 x 60."""
import textwrap
BOARD_W, BOARD_H, CORNER_R = 100.0, 60.0, 3.0
HOLES = [(4, 4), (96, 4), (96, 56), (4, 56)]

def rect(x1, y1, x2, y2): return [(x1, y1), (x2, y1), (x2, y2), (x1, y2)]

BLOCKS = [
 dict(key="dc", title="DC IN + SHUNT", sch="12.0 V input, current shunt and decoupling",
      refs="J1 R12 JP1 TP1 TP2 TP3 C10 C11 C12".split(),
      poly=[(9.5, 0), (29.5, 0), (29.5, 21), (0.8, 21), (0.8, 9.5), (9.5, 9.5)],
      label_at=(1.4, 17.7), label_lines=["J1 R12 JP1 C10 C11 C12 TP1-TP3"]),
 dict(key="buck", title="5 V BUCK", sch="5 V buck: TPS62175 (TI SLVSB35C Fig. 8), ferrite-bead filtered",
      refs="U2 L4 FB2 FB3 C21 C22 C23 R13 R14 TP12 TP13".split(),
      poly=rect(30, 0.8, 43.5, 15), label_at=(30.6, 1.6), label_lines=["U2 L4 FB2 FB3", "C21 C22 C23", "R13 R14", "TP12 TP13"]),
 dict(key="xo", title="7.030 MHz PIERCE XO", sch="7.030 MHz Pierce oscillator (MMBT3904, about 0.8 mA)",
      refs="Q4 Y1 C5 C6 C7 C8 C9 C20 R5 R6 R7 R8 R9 R10 R11 TP8 TP9".split(),
      poly=[(0.8, 28), (24.5, 28), (24.5, 59.2), (9.5, 59.2), (9.5, 50.5), (0.8, 50.5)],
      label_at=(1.4, 28.8), label_lines=["Q4 Y1 C5-C9 C20", "R5-R11 TP8/TP9", "(Y1 kept low, away", "from J1 and the buck)"]),
 dict(key="gate", title="GATE DRIVE", sch="Gate drive",
      refs="U1 C13 R1 D1 TP4 TP5".split(),
      poly=rect(30, 20, 41.5, 37), label_at=(30.6, 20.8), label_lines=["U1 C13 R1", "D1 TP4 TP5", "(D1, TP4 at", "Q1 gate pad)"]),
 dict(key="key", title="PA KEYING", sch="PA keying (PMOS high side, as OpenBeacon 2)",
      refs="J4 Q2 R2 R3 C4 TP14 TP15".split(),
      poly=rect(25, 38, 41.5, 60), label_at=(25.6, 38.8), label_lines=["J4 Q2 R2 R3 C4", "TP14 TP15", "+12V_PA to L1 (right)"]),
 dict(key="pa", title="CLASS E CORE", sch="Class E stage: L1 feed, C1 (part of the schematic's class E block)",
      refs="Q1 L1 C1 C14 C15 TP6 TP7".split(),
      poly=rect(42, 30.2, 57.5, 59.2), label_at=(42.6, 31.0), label_lines=["Q1 C1 C14 C15", "TP6 TP7 L1"]),
 dict(key="lpf", title="3-POLE ELLIPTIC LPF", sch="3-pole elliptic LPF (trap 14.06 MHz)",
      refs="C16 L3 C17 C18 C19".split(),
      poly=rect(53.8, 0.8, 79.5, 29.8), label_at=(54.3, 26.95), label_lines=["C16 L3 C17 C18 C19 (C19 at J2)"]),
 dict(key="tank", title="CLASS E: C2-L2 TANK + C3", sch="Class E stage: C2-L2 tank, C3 match (part of the schematic's class E block)",
      refs="C2 L2 C3 TP10 TP11".split(),
      poly=rect(58.5, 30.2, 84, 59.2), label_at=(59.0, 30.6), label_lines=["C2 L2 C3 TP10 TP11 (out_50r probe)"]),
 dict(key="rf", title="RF OUT", sch="J2 RF out, 50 ohm",
      refs=["J2"], poly=rect(79.6, 0, 91.4, 16.5), label_at=(80.3, 14.4), label_lines=[]),
 dict(key="brand", title="BRANDING", sch="(board text and logos, no schematic parts)",
      refs=[], poly=rect(84.5, 17.5, 99.2, 40), label_at=(85.0, 35.4), label_lines=["logos: Etherkit", "+ OSHW 4 mm"]),
]

ENVELOPES = [
 dict(ref="J1", label="J1 PJ-102AH", rect=(12, 0, 23.5, 15.5), label_at=(12.6, 7.0)),
 dict(ref="J2", label="J2 BNC", rect=(79.9, 0, 91.3, 13.8), label_at=(82.6, 7.0)),
 dict(ref="J4", label="J4 SJ1-3523N", rect=(28, 47.55, 40.5, 60), label_at=(28.5, 53.0)),
 dict(ref="L1", label="L1 FT50-61", rect=(42.025, 39.36, 55.975, 56.475), core=((49, 49.5), 6.975), label_at=(45.4, 48.9)),
 dict(ref="L3", label="L3 T80-6 (LPF)", rect=(54.15, 1.65, 75.85, 26.85), core=((65, 12.5), 10.85), label_at=(59.6, 11.9)),
 dict(ref="L2", label="L2 T80-6 (tank)", rect=(61.15, 33.15, 82.85, 58.35), core=((72, 47.5), 10.85), label_at=(66.2, 46.9)),
 dict(ref="Y1", label="Y1 HC-49 combo", rect=(4.0, 42.0, 20.1, 48.1), label_at=(6.6, 44.6)),
 dict(ref="C10", label="C10", rect=(1.5, 9.8, 10.9, 16.9), label_at=(4.2, 12.9)),
 dict(ref="R12", label="R12", rect=(24.6, 2.5, 28.4, 11.3), label_at=(25.0, 6.4)),
]

BRAND = [  # (text, at, size, layer)
 ("40m Class E TX", (85.0, 18.5), 1.0, "F.SilkS"),
 ("Rev 7", (85.0, 20.5), 1.5, "F.Cu"),
 ("etherkit.com 2026", (85.0, 22.9), 0.8, "F.SilkS"),
 ("Creative Commons", (85.0, 24.3), 0.8, "F.SilkS"),
 ("CC-BY-SA 4.0", (85.0, 25.5), 0.8, "F.SilkS"),
]

EDGE_LABELS = [  # User.1, outside the board
 ("BACK EDGE (rear panel): J1 DC IN, J2 RF OUT", (30.0, -2.6), 1.2),
 ("FRONT EDGE (front panel): J4 KEY", (30.0, 61.0), 1.2),
]

NOTES_RAW = [
 "FLOORPLAN rev 7 v2, no parts placed. Board 100 x 60 mm, 3 mm corner radius, 2 layers, FR-4 1.6 mm. Top edge (y=0) = BACK, bottom edge (y=60) = FRONT. Origin = back-left corner. Blue (User.1) = blocks; orange (User.2) = courtyards of the large parts (on-board part only; the J1 and J2 bodies overhang the back edge, the J4 nose the front edge); red = F.Cu; green = F.SilkS.",
 "Signal: XO -> U1 gate drive -> Q1 -> C2-L2 tank -> C3 (out_50r strip between L2 and L3) -> LPF (C16, L3 || C17+C18, C19) -> J2 on the back edge. DC: J1 -> R12/JP1 -> +12V run down the x=25-30 channel -> Q2 keyed +12V_PA -> L1; +12V -> U2 buck -> +5V to XO and U1.",
 "B.Cu: unbroken GND plane. Top GND pour stitched to it, with a via fence around L2/L3, C16-C19 and J2. GND vias at the Q1 source, C1 and C3 ground pads; keep the U1-R1-Q1 gate loop and the Q1-C1 drain loop tight.",
 "L2 and L3 lie flat, so both axes are normal to the board: isolation is by spacing (cores 14 mm apart edge to edge). Keep L4 (buck) away from L2/L3 (gen.py note 12) and from Y1. The free strip y=21-28 at the left is GND pour between the DC input and the XO.",
 "H1-H4: MountingHole_3.2mm_M3_Pad_Via, 4 mm in from both edges; circles = 4.5 mm radius keepout. The J4 footprint carries its own Edge.Cuts notch: split the front edge at J4 when it is placed.",
]
NOTES = [l for n in NOTES_RAW for l in textwrap.wrap(n, 118, subsequent_indent="   ")]
