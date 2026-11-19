# Project-local footprints for pa40-classe rev 7. Dimensions cited in each descr.
import uuid, math, os
U=lambda: str(uuid.uuid4())
OUT=os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'PCB', 'lib', 'pa40.pretty')
def eff(sz=1.0,th=0.15): return f'(effects (font (size {sz} {sz}) (thickness {th})))'
def prop(name,val,at,layer,hide=False,sz=1.0):
    return f'(property "{name}" "{val}" (at {at[0]} {at[1]} 0) (layer "{layer}"){" (hide yes)" if hide else ""} (uuid "{U()}") {eff(sz)})'
def line(a,b,layer,w): return f'(fp_line (start {a[0]:.4f} {a[1]:.4f}) (end {b[0]:.4f} {b[1]:.4f}) (stroke (width {w}) (type solid)) (layer "{layer}") (uuid "{U()}"))'
def rect(a,b,layer,w): return f'(fp_rect (start {a[0]} {a[1]}) (end {b[0]} {b[1]}) (stroke (width {w}) (type solid)) (fill no) (layer "{layer}") (uuid "{U()}"))'
def circle(c,r,layer,w,fill='no'): return f'(fp_circle (center {c[0]} {c[1]}) (end {c[0]+r:.4f} {c[1]}) (stroke (width {w}) (type solid)) (fill {fill}) (layer "{layer}") (uuid "{U()}"))'
def arc(s,m,e,layer,w): return f'(fp_arc (start {s[0]} {s[1]}) (mid {m[0]} {m[1]}) (end {e[0]} {e[1]}) (stroke (width {w}) (type solid)) (layer "{layer}") (uuid "{U()}"))'
def text(t,at,layer,sz=1.0): return f'(fp_text user "{t}" (at {at[0]} {at[1]} 0) (layer "{layer}") (uuid "{U()}") {eff(sz)})'
def tht(num,at,size,drill): return f'(pad "{num}" thru_hole circle (at {at[0]} {at[1]}) (size {size} {size}) (drill {drill}) (layers "*.Cu" "*.Mask") (remove_unused_layers no) (uuid "{U()}"))'
def npth(at,d): return f'(pad "" np_thru_hole circle (at {at[0]} {at[1]}) (size {d} {d}) (drill {d}) (layers "*.Cu" "*.Mask") (uuid "{U()}"))'
def write(name,descr,tags,attr,items,refat,valat):
    s=f'''(footprint "{name}" (version 20241229) (generator "pa40_gen_fp") (generator_version "1") (layer "F.Cu")
 (descr "{descr}") (tags "{tags}")
 {prop("Reference","REF**",refat,"F.SilkS")}
 {prop("Value",name,valat,"F.Fab")}
 {prop("Datasheet","",(0,0),"F.Fab",True)}
 {prop("Description",descr,(0,0),"F.Fab",True)}
 (attr {attr})
 {chr(10).join(items)}
 (embedded_fonts no)
)'''
    open(f'{OUT}/{name}.kicad_mod','w').write(s)

# 1) HC-49/US dual footprint: THT (Abracon ABL) + SMD (Abracon ABLS) on shared pads 1/2
# ABL: pitch 4.88 +-0.20, lead dia 0.457, body 11.5 x 5.0 max (ABL datasheet p.4)
# ABLS: body 11.4 x 4.7, leads 12.7 overall, land 5.6 x 2.1 mm at 9.5 mm centres (ABLS drawing 450669 p.3)
it=[]
for n,sx in (('1',-1),('2',1)):
    it.append(f'(pad "{n}" smd rect (at {sx*4.75} 0) (size 5.6 2.1) (layers "F.Cu" "F.Paste" "F.Mask") (uuid "{U()}"))')
    it.append(tht(n,(sx*2.44,0),1.5,0.8))
# silk: SMD/THT body outline, kept 0.6 mm off the SMD pads (pads span y +-1.05)
for y in (-2.75,2.75): it.append(line((-6.0,y),(6.0,y),'F.SilkS',0.12))
for x in (-6.0,6.0):
    it.append(line((x,-2.75),(x,-1.65),'F.SilkS',0.12)); it.append(line((x,1.65),(x,2.75),'F.SilkS',0.12))
it.append(rect((-5.7,-2.35),(5.7,2.35),'F.Fab',0.1))          # ABLS body 11.4 x 4.7
it.append(line((-3.25,-2.5),(3.25,-2.5),'F.Fab',0.1)); it.append(line((-3.25,2.5),(3.25,2.5),'F.Fab',0.1))  # ABL body 11.5 x 5.0 obround
it.append(arc((-3.25,-2.5),(-5.75,0),(-3.25,2.5),'F.Fab',0.1)); it.append(arc((3.25,-2.5),(5.75,0),(3.25,2.5),'F.Fab',0.1))
it.append(rect((-8.05,-3.05),(8.05,3.05),'F.CrtYd',0.05))
it.append(text('${REFERENCE}',(0,0),'F.Fab',0.8))
write('Crystal_HC49-US_THT_SMD_Combo','HC-49/US crystal, fits through-hole (Abracon ABL: 4.88 mm pitch, 0.457 mm leads) or SMD (Abracon ABLS land 5.6 x 2.1 mm, 9.5 mm centres); THT holes sit inside the SMD pads',
      'crystal HC49 HC-49/US SMD THT combo dual','through_hole',it,(0,-4.0),(0,4.0))

# 2) T-80 flat-mount toroid (Micrometals T80-6: OD 20.19 nom / 20.70 max coated, ID 12.57 / 12.07 min, Ht 6.35 / 6.99)
def toroid(name,descr,od_max,od_nom,id_nom,padx,pady,pad,drill,mount=None):
    it=[]
    r=od_max/2
    it.append(circle((0,0),round(r+0.15,3),'F.SilkS',0.12))
    it.append(circle((0,0),od_nom/2,'F.Fab',0.1)); it.append(circle((0,0),id_nom/2,'F.Fab',0.1))
    it.append(tht('1',(-padx,pady),pad,drill)); it.append(tht('2',(padx,pady),pad,drill))
    if mount: it.append(npth((0,0),mount)); it.append(text('M3 nylon',(0,-1.5*1.0-mount/2),'F.Fab',0.6))
    cy=pady+pad/2+0.25; cr=r+0.5
    it.append(rect((-cr,-cr),(cr,max(cy,cr)),'F.CrtYd',0.05))
    it.append(text('${REFERENCE}',(0,id_nom/2+1.0 if not mount else id_nom/2-1.0),'F.Fab',0.8))
    write(name,descr,'toroid flat horizontal','through_hole',it,(0,-cr-1.2),(0,max(cy,cr)+1.2))
toroid('L_Toroid_T80_Flat_P10.16mm_Drill1.6mm','Micrometals T-80 toroid mounted flat (OD 20.19 mm nom, 20.70 mm max coated; ID 12.57 mm; Ht 6.35 mm, T80-6 datasheet rev 20190524). Two leads exit below, holes 1.6 mm for #16 enamel or thinner; optional 3.2 mm NPTH for an M3 nylon screw',
       20.70,20.19,12.57,5.08,12.7,2.8,1.6,mount=3.2)
toroid('L_Toroid_FT50_Flat_P7.62mm_Drill1.0mm','Fair-Rite FT-50 size toroid (5961000301: OD 12.7 +-0.25, ID 7.15, Ht 4.9 mm) mounted flat; holes 1.0 mm for #24 enamel; optional 3.2 mm NPTH for an M3 nylon screw (fits the 7.15 mm ID with room for 26 t #24)',
       12.95,12.7,7.15,3.81,8.89,2.0,1.0,mount=3.2)

# 3) EPC2036 land pattern: EPC2036 datasheet p.6 (SMD mask openings 200 um +20/-10, 450 um pitch;
# stencil 250 um square, R60 corners, 100 um laser cut). Copper enlarged to 300 um so the 200 um opening
# stays solder-mask defined with AN009's 2 mil copper-to-mask registration tolerance (AN009 p.3).
it=[]
P={'1':(-0.225,-0.225),'2':(-0.225,0.225),'3':(0.225,-0.225),'4':(0.225,0.225)}
for n,(x,y) in P.items():
    it.append(f'(pad "{n}" smd circle (at {x} {y}) (size 0.3 0.3) (layers "F.Cu" "F.Mask") (solder_mask_margin -0.05) (uuid "{U()}"))')
    it.append(f'(pad "" smd roundrect (at {x} {y}) (size 0.25 0.25) (layers "F.Paste") (roundrect_rratio 0.24) (uuid "{U()}"))')
it.append(rect((-0.45,-0.45),(0.45,0.45),'F.Fab',0.05))
for a,b in [((-0.6,-0.6),(0.6,-0.6)),((0.6,-0.6),(0.6,0.6)),((0.6,0.6),(-0.6,0.6)),((-0.6,0.6),(-0.6,-0.6))]: it.append(line(a,b,'F.SilkS',0.1))
it.append(circle((-0.8,-0.8),0.08,'F.SilkS',0.1,'yes'))
it.append(rect((-1.0,-1.0),(1.0,1.0),'F.CrtYd',0.05))
write('EPC2036_LGA4_SMD_P0.45mm','EPC2036 land pattern per EPC2036 datasheet p.6: solder-mask-defined 0.20 mm openings at 0.45 mm pitch on 0.30 mm copper (2 mil registration margin, EPC AN009 p.3); stencil 0.25 mm square R0.06, 0.1 mm thick. Pad 1 gate, 3 drain, 2 and 4 source. Order ENIG and tell the fab not to change mask openings',
      'EPC2036 eGaN LGA BGA chip scale','smd',it,(0,-1.6),(0,1.6))
print(os.listdir(OUT))

# 4) Knowles Voltronics JZ trimmer (JZ300 for C9). J-Series datasheet p.4 (JZ series): body 4.5 x 3.2 x 1.5 mm;
# solder pad layout 4.75 mm outer, 3.05 mm inner, 1.4 mm wide -> pads 0.85 x 1.4 at +-1.95 mm.
it=[]
for n,sx in (('1',-1),('2',1)):
    it.append(f'(pad "{n}" smd rect (at {sx*1.95} 0) (size 0.85 1.4) (layers "F.Cu" "F.Paste" "F.Mask") (uuid "{U()}"))')
pts=[(-1.85,-1.6),(2.25,-1.6),(2.25,1.6),(-1.85,1.6),(-2.25,1.2),(-2.25,-1.2),(-1.85,-1.6)]  # chamfered side as drawn
for a,b in zip(pts,pts[1:]): it.append(line(a,b,'F.Fab',0.1))
for y in (-1.75,1.75): it.append(line((-1.5,y),(1.5,y),'F.SilkS',0.12))
it.append(rect((-2.7,-1.95),(2.7,1.95),'F.CrtYd',0.05))
it.append(text('${REFERENCE}',(0,0),'F.Fab',0.6))
write('C_Trimmer_Voltronics_JZ','Knowles Voltronics JZ-series SMD trimmer, 4.5 x 3.2 x 1.5 mm; land 0.85 x 1.4 mm pads, 4.75 mm outer / 3.05 mm inner (J-Series datasheet, JZ page)',
      'trimmer capacitor JZ300 Voltronics','smd',it,(0,-2.9),(0,2.9))


# 5) Molex 73100-0105 (0731000105, DigiKey WM5524-ND) right-angle through-hole 50 ohm BNC jack.
# All hole positions and hole diameters are the nominal values from the recommended PCB pattern
# on Molex sales drawing SD-73100-0105 (archived from molex.com/pdm_docs/sd/731000105_sd.pdf).
# Origin: intersection of EDGE OF PCB (datum B / datum A) with the connector axis.
# +Y is onto the board; -Y is off-board (jack opening).
# Shell holes, 2 places: dia 1.80 +0.10/-0.00, 7.60 ±0.05 apart, 4.60 ±0.05 from the edge,
#   true position dia 0.08 to datum B.
# Center hole: dia 0.92 +0.10/-0.00, 7.80 ±0.05 from the shell-hole line (12.40 from the edge),
#   3.80 ±0.05 from each shell hole (on the axis), true position dia 0.08 to datum B.
# Body, REF on the same drawing: 13.00 from jack face to the shoulder at the board edge;
#   main body 21.80 long x 9.65 wide, so the back is at Y=8.80 on the board.
# Rear boss is not dimensioned; length 2.20 and width 2.50 were measured from the top view
#   scaled to the 21.80 REF (boss ends at Y=11.00).
# The drawing specifies holes, not pads. Annular rings: 0.44 mm on the center (pad 1.80) and
#   0.50 mm on the shell posts (pad 2.80).
# KiCad Connector_Coaxial:BNC_Amphenol_B6252HB-NPP3G-50_Horizontal does not match this pattern
#   (four pads, 5.08/2.54 spacing, drills 0.89 and 2.01).
# Datasheet recommended PCB thickness is 2.40 mm; pin length below the seating plane is 3.00 REF,
#   so the pins still protrude through a 1.6 mm board.
it=[]
# pads
def tht2(num,at,size,drill):
    return f'(pad "{num}" thru_hole circle (at {at[0]:.2f} {at[1]:.2f}) (size {size:.2f} {size:.2f}) (drill {drill:.2f}) (layers "*.Cu" "*.Mask") (remove_unused_layers no) (uuid "{U()}"))'
it.append(tht2('1',(0.00,12.40),1.80,0.92))          # center contact
it.append(tht2('2',(-3.80,4.60),2.80,1.80))          # shell
it.append(tht2('2',( 3.80,4.60),2.80,1.80))
# F.Fab: exact body from the drawing
Wbody=9.65/2  # 4.825
it.append(rect((-Wbody,-13.00),(Wbody,8.80),'F.Fab',0.1))
it.append(rect((-1.25,8.80),(1.25,11.00),'F.Fab',0.1))
it.append(line((-5.5,0.0),(5.5,0.0),'F.Fab',0.1))  # board edge
it.append(text('PCB EDGE',(6.8,0.0),'F.Fab',0.6))
it.append(text('${REFERENCE}',(0,-6.0),'F.Fab',0.8))
# F.SilkS: 0.15 mm outside the body, gapped around the shell pads
# Shell pad r=1.40, clearance 0.20 -> keepout r=1.60. Silk x=±4.975.
# Overlap in Y when |y-4.60| < sqrt(1.60**2 - (4.975-3.80)**2) = 1.086; use 1.20 for margin.
silk_x=round(Wbody+0.15,3)  # 4.975
y_front=-13.15
y_back=8.95
y_gap_lo=3.40
y_gap_hi=5.80
it.append(line((-silk_x,y_front),(silk_x,y_front),'F.SilkS',0.12))
for sx in (-silk_x, silk_x):
    it.append(line((sx,y_front),(sx,y_gap_lo),'F.SilkS',0.12))
    it.append(line((sx,y_gap_hi),(sx,y_back),'F.SilkS',0.12))
# back of main body, leaving a gap for the boss silk
it.append(line((-silk_x,y_back),(-1.40,y_back),'F.SilkS',0.12))
it.append(line(( 1.40,y_back),( silk_x,y_back),'F.SilkS',0.12))
# boss, 0.15 mm outside
it.append(line((-1.40,y_back),(-1.40,11.15),'F.SilkS',0.12))
it.append(line((-1.40,11.15),( 1.40,11.15),'F.SilkS',0.12))
it.append(line(( 1.40,11.15),( 1.40,y_back),'F.SilkS',0.12))
# board-edge ticks on silk (the full edge line is on Fab)
it.append(line((-5.50,0.0),(-silk_x,0.0),'F.SilkS',0.12))
it.append(line(( silk_x,0.0),( 5.50,0.0),'F.SilkS',0.12))
# pin 1 marker, clear of the 1.80 pad (pad extends to x=±0.90)
it.append(circle((2.00,12.40),0.25,'F.SilkS',0.12,'yes'))
# courtyard: 0.50 mm around body, boss and pads
# pads: shell |x|<=5.20, y 3.20-6.00; center |x|<=0.90, y 11.50-13.30
# body |x|<=4.825, y -13.00-8.80; boss |x|<=1.25, y 8.80-11.00
it.append(rect((-5.70,-13.50),(5.70,13.80),'F.CrtYd',0.05))
write('BNC_Molex_73100-0105_Horizontal',
      'Molex 73100-0105 (0731000105) 50 ohm right-angle TH BNC jack. Recommended PCB pattern from Molex SD-73100-0105: origin at board edge on the axis, +Y onto the board; shell holes dia 1.80 at (+/-3.80, 4.60), center hole dia 0.92 at (0, 12.40). Body 21.80 x 9.65, 13.00 overhang. Pads: 1.80/0.92 center, 2.80/1.80 shell (drawing gives holes only). KiCad BNC_Amphenol_B6252HB-NPP3G-50_Horizontal does not match. Rec. PCB 2.40 mm; 3.00 mm pins still clear a 1.6 mm board.',
      'BNC coaxial jack Molex 73100-0105 0731000105 WM5524 right-angle through-hole',
      'through_hole',it,(0,15.50),(0,-14.80))
