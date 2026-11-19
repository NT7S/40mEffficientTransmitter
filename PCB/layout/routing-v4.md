# pa40-classe rev 7: routing v4 (jack labels + blue-mask renders)

2026-11-19, KiCad 10.0.8. Copper routing is unchanged from v3 (`routing-v3.md`) except that stitching
vias were pulled out from under the new (and existing) silkscreen text. `layout/route.py` still
regenerates the whole board. Backups of the v3 state are in `old/pre-v4/`.

## Jack labels (F.Silkscreen)
All three are horizontal, left-justified, and sit on the board just inside the edge, beside the jack
so they stay visible with the connector installed (checked against courtyards and the 3D models).

| Label | Position (mm) | Size / stroke | Bounding box (mm) | Placement |
|---|---|---|---|---|
| +12 VDC In | 101.30, 109.60 | 1.0 / 0.17 mm | 101.30–110.51 × 108.72–110.48 | Left of J1, in the gap between H1 and C10. 1.0 mm is the largest size that fits that gap (1.1 mm would run into J1). Same size as "40m Class E TX". |
| Antenna | 188.50, 115.50 | 1.2 / 0.20 mm | 188.50–195.95 × 114.45–116.55 | South of J2 (in front of the BNC, on the board), to the right of C19. |
| Key | 124.00, 156.80 | 1.2 / 0.20 mm | 124.00–127.50 × 155.75–157.85 | Left of J4, near the front edge. |

## Vias moved off the silk
The stitching-via keeper already avoided F.Cu text (the Rev 7 copper) and the logo bounding boxes, but
not F.Silkscreen text, which is why vias sat under "Creative Commons" / "CC-BY-SA 4.0". It now skips
any candidate that falls in a silk or copper text box (inflated 0.5 mm). Result: **399 stitching vias,
412 vias in total** (10 fewer than v3's 409 / 422). The two license lines, the three new labels, and
the other branding silk are all clear of via holes.

## Renders (blue mask, white silk, ENIG)
The board stackup was already blue mask / white silk / ENIG; earlier 3D shots looked green because
`kicad-cli pcb render` was not given `--use-board-stackup-colors`. That flag is now the default in
`layout/make_3d.py:render_board()`.

`layout/render_cu.py` now defaults to a 2D photo look (blue mask, traces showing through as a darker
blue, gold at mask openings, white silk). Colours were sampled from a stackup 3D render. Pass
`--technical` for the old red-copper / yellow-silk review drawing. `layout/render_top.py` is still
the placement/ratsnest technical view; its header points at `render_cu.py` for the photo look.

- `routing-v4-top.png`: 2D photo, 2400 px. Mask is blue, pads are gold, silk is white; all three
  labels are legible and not under a jack.
- `routing-v4-labels.png`: the same photo look, slightly tighter crop of the board.
- `routing-v4-3d-top.png`: 3D top, high quality, `--use-board-stackup-colors`. Blue mask confirmed;
  labels visible beside J1, J2 and J4 with the parts in place.
- `routing-v4-3d-angle.png`: 3D perspective, `--rotate -45,0,30`. Same colours; "Key", "Antenna" and
  "+12 VDC In" all readable.

## Checks
- DRC (`--schematic-parity --refill-zones --severity-all`): **0 violations (errors and warnings),
  0 unconnected, 0 parity**. Report: `layout/drc-routing.rpt`.
- ERC: unchanged (the schematic was not edited).
