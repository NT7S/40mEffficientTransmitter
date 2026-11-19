# pa40-classe rev 7: JLCPCB order notes

Use this checklist when compiling the JLCPCB package (Gerbers + drill). Bare boards only; Jason hand-populates.

- **Order with tented vias (Via Covering: Tented)** - requested by Jason 2026-11-19, mainly for U2 thermal pad vias.
  - The board file already tents vias on both sides (Board Setup > Solder Mask/Paste: tent vias front + back), so the
    mask Gerbers have no via openings. The two U2 (TPS62175) exposed-pad vias sit inside the EP's own mask opening on
    top, so tenting covers them on the bottom side only; that is what keeps solder from wicking out the back.
- Layers: 2
- Thickness: 1.6 mm, FR4, 1 oz (35 um) outer copper
- Size: 100 x 60 mm, rounded corners, 4 x M3 plated mounting holes (H1-H4, tied to GND)
- Solder mask: blue
- Silkscreen: white
- Surface finish: ENIG (flat pads for the EPC2036 LGA and the WSON-10)
- Min trace / space: 0.127 mm (5 mil) board rule; most of the board is at 0.2 mm or more
- Q1 (EPC2036) land pattern: 0.15 mm local clearance between its 0.3 mm bumps (0.45 mm pitch); inside JLCPCB's
  standard 0.127 mm capability, so no advanced-process option is needed
- Drill: 0.3 mm minimum (all vias 0.6 / 0.3 mm), 0.5 mm hole-to-hole minimum
- Remove order number: optional (no reserved spot on the silkscreen yet)
