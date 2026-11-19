# pa40-classe rev 7: routing v3 (branding)

2026-11-19, KiCad 10.0.8. Copper routing is unchanged from v2 (`routing-v2.md`). `layout/route.py` still regenerates
the whole board. Backups of the v2 state are in `old/pre-v3/` (board, project, route.py, fp-lib-table, pa40.pretty).

## Changes
1. **Etherkit logo (F.Silkscreen).**
   - Source: `EtherkitLogoSmall.kicad_mod`, copied from `NT7S/Si5351AVFO`, path `PCB/lib/Etherkit.pretty/`
     (local clone /workspace/Si5351AVFO @ f8a0547). That folder is Si5351AVFO's project copy of
     `etherkit/EtherkitKicadLibrary` @ 6b9fc0f, re-saved in KiCad 10 format. Same artwork and size as the library
     original (checked against the /workspace/ek clone of etherkit/EtherkitKicadLibrary).
   - Placed as LOGO1 at (187.4, 135.0): 2.54 x 5.20 mm, unscaled, the same size as on Si5351AVFO (100 x 65 mm board).
2. **OSHW logo (F.Silkscreen).**
   - The brief suggested KiCad's stock OSHW logo, but Jason's boards use his own `OSHWLogo4mm`. So to match, it comes
     from the same Si5351AVFO folder (origin etherkit/EtherkitKicadLibrary @ 6b9fc0f), not the KiCad stock library.
   - Placed as LOGO2 at (192.7, 134.6): 4.45 x 4.00 mm. It sits beside the Etherkit logo with the same 5.3 mm
     centre spacing as Si5351AVFO.
   - Both logos sit in the right-edge branding block, under the text, clear of pads and courtyards. The stitching via
     generator keeps vias out from under them.
   - The only edit to the copied files: their `attr` line now also says `board_only exclude_from_pos_files
     exclude_from_bom`. This matches how Si5351AVFO's placed instances are set. Without it, DRC reports either "extra
     footprint" (parity) or "doesn't match library copy".
3. **Text.** "etherkit.com 2026" is now "NT7S 2026". "40m Class E TX" and "Creative Commons / CC-BY-SA 4.0" are
   unchanged. All silk text is horizontal (0 deg).
4. **Rev marking.**
   - It was already top-copper text (F.Cu "Rev 7", 1.5 mm). The white box around it in earlier renders was the GND
     pour clearance, not a knockout. There was no silk duplicate.
   - Now styled like "Rev A" on Si5351AVFO: plain F.Cu text, 1.5 mm, 0.3 mm stroke (was 0.255), not knockout, no
     solder-mask opening (covered by mask). It is not tied to any net. The zone filler keeps the 0.3 mm pour
     clearance around it, so it cannot short into the GND pour.

## Checks
- DRC (`--schematic-parity --refill-zones --severity-all`): **0 violations (errors and warnings), 0 unconnected,
  0 parity**. Report: `layout/drc-routing.rpt`.
- ERC: unchanged from v2 (0 errors). The schematic was not touched.
- Vias: 409 stitching, 422 total. Five fewer than v2, because the logo areas are kept free.

## Renders
- `routing-v3-top.png`: F.Cu, F.SilkS and Edge.Cuts.
- `routing-v3-branding.png`: a 20 x 22 mm crop of the branding block.
- `routing-v3-3d-top.png`: 3D top view.
