import re, uuid, math
S='/usr/share/kicad/symbols/'
def block(path,name):
    t=open(path).read(); i=t.find(f'(symbol "{name}"')
    d=0
    for j in range(i,len(t)):
        if t[j]=='(':d+=1
        elif t[j]==')':
            d-=1
            if d==0: return t[i:j+1]
U=lambda: str(uuid.uuid4())
ROOT=U()
BUCK='''(symbol "pa40:TPS62175" (pin_names (offset 0.508)) (exclude_from_sim no) (in_bom yes) (on_board yes)
  (property "Reference" "U" (at 0 10.16 0) (effects (font (size 1.27 1.27))))
  (property "Value" "TPS62175" (at 0 -12.7 0) (effects (font (size 1.27 1.27))))
  (property "Footprint" "Package_SON:WSON-10-1EP_2x3mm_P0.5mm_EP0.84x2.4mm" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
  (property "Datasheet" "https://www.ti.com/lit/ds/symlink/tps62175.pdf" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
  (property "Description" "TI TPS62175 28 V 0.5 A step-down converter, adjustable, WSON-10 (pinout SLVSB35C)" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
  (symbol "TPS62175_0_1" (rectangle (start -7.62 7.62) (end 7.62 -10.16) (stroke (width 0.254) (type default)) (fill (type background))))
  (symbol "TPS62175_1_1"
    (pin power_in line (at -10.16 5.08 0) (length 2.54) (name "VIN" (effects (font (size 1.016 1.016)))) (number "2" (effects (font (size 1.016 1.016)))))
    (pin input line (at -10.16 2.54 0) (length 2.54) (name "EN" (effects (font (size 1.016 1.016)))) (number "3" (effects (font (size 1.016 1.016)))))
    (pin power_out line (at 10.16 5.08 180) (length 2.54) (name "SW" (effects (font (size 1.016 1.016)))) (number "9" (effects (font (size 1.016 1.016)))))
    (pin input line (at 10.16 2.54 180) (length 2.54) (name "VOS" (effects (font (size 1.016 1.016)))) (number "10" (effects (font (size 1.016 1.016)))))
    (pin input line (at 10.16 0 180) (length 2.54) (name "SLEEP" (effects (font (size 1.016 1.016)))) (number "8" (effects (font (size 1.016 1.016)))))
    (pin input line (at 10.16 -2.54 180) (length 2.54) (name "FB" (effects (font (size 1.016 1.016)))) (number "5" (effects (font (size 1.016 1.016)))))
    (pin open_collector line (at 10.16 -5.08 180) (length 2.54) (name "PG" (effects (font (size 1.016 1.016)))) (number "7" (effects (font (size 1.016 1.016)))))
    (pin power_in line (at -10.16 -2.54 0) (length 2.54) (name "PGND" (effects (font (size 1.016 1.016)))) (number "1" (effects (font (size 1.016 1.016)))))
    (pin passive line (at -10.16 0 0) (length 2.54) (name "NC" (effects (font (size 1.016 1.016)))) (number "4" (effects (font (size 1.016 1.016)))))
    (pin power_in line (at -10.16 -5.08 0) (length 2.54) (name "AGND" (effects (font (size 1.016 1.016)))) (number "6" (effects (font (size 1.016 1.016)))))
    (pin passive line (at -10.16 -7.62 0) (length 2.54) (name "EP" (effects (font (size 1.016 1.016)))) (number "11" (effects (font (size 1.016 1.016)))))
  )
  (embedded_fonts no)
)'''
libs={}
# pin-numbered transistor symbols matching the SOT-23 / EPC bump pinouts (onsemi MMBT3904L, AOS AO3407A, EPC2036 land pattern)
DERIV={'pa40:Q_NPN_BEC':('Q_NPN',{'B':'1','E':'2','C':'3'},False),'pa40:Q_PMOS_GSD':('Q_PMOS',{'G':'1','S':'2','D':'3'},False),'pa40:EPC2036':('Q_NMOS',{'G':'1','D':'3','S':'2'},True)}
def lib(lid):
    if lid in libs: return
    if lid=='pa40:TPS62175': libs[lid]=BUCK; return
    if lid in DERIV:
        base,nmap,dup=DERIV[lid]; nn=lid.split(':')[1]
        b=block(S+'Device.kicad_sym',base)
        b=b.replace(f'(symbol "{base}_',f'(symbol "{nn}_').replace(f'(symbol "{base}"',f'(symbol "{lid}"',1)
        b=re.sub(r'\(number "([A-Z])"',lambda m:f'(number "{nmap[m.group(1)]}"',b)
        if dup:   # EPC2036: second source bump (pad 4) stacked on S, hidden
            m=re.search(r'\(pin passive line\s*\(at ([-\d.]+ [-\d.]+ \d+)\)\s*\(length ([-\d.]+)\)\s*\(name "S"',b)
            extra=f'(pin passive line (at {m.group(1)}) (length {m.group(2)}) (hide yes) (name "S" (effects (font (size 1.27 1.27)))) (number "4" (effects (font (size 1.27 1.27)))))'
            k=m.start(); b=b[:k]+extra+'\n'+b[k:]
        libs[lid]=b; return
    l,n=lid.split(':'); b=block(S+l+'.kicad_sym',n)
    b=b.replace(f'(symbol "{n}"',f'(symbol "{lid}"',1)
    if n=='74LVC1G17': b=re.sub(r'\(pin_names([^()]*(\([^()]*\))*[^()]*)\)', lambda m: m.group(0)[:-1]+' (hide yes))', b, count=1) if '(pin_names' in b else b.replace(f'(symbol "{lid}"',f'(symbol "{lid}" (pin_names (hide yes))',1)
    libs[lid]=b
def pins_of(lid):
    b=libs[lid]
    found=re.findall(r'\(pin \w+ \w+\s*\(at ([-\d.]+) ([-\d.]+) (\d+)\)\s*\(length [-\d.]+\)(?:\s*\(hide yes\))?\s*\(name "([^"]*)".*?\(number "([^"]*)"',b,flags=re.S)
    d={num:(float(x),float(y)) for x,y,a,nm,num in found}
    if lid in DERIV: d.update({nm:(float(x),float(y)) for x,y,a,nm,num in found})
    return d
def xf(at,rot,mir,p):
    x,y=p   # KiCad order: rotate, then mirror (verified by ERC on a test sheet)
    r=math.radians(rot); xr=x*math.cos(r)-y*math.sin(r); yr=x*math.sin(r)+y*math.cos(r)
    if mir=='y': xr=-xr
    if mir=='x': yr=-yr
    return (round(at[0]+xr,2), round(at[1]-yr,2))

R6='Resistor_SMD:R_0603_1608Metric'; C6='Capacitor_SMD:C_0603_1608Metric'; C8='Capacitor_SMD:C_0805_2012Metric'; C12='Capacitor_SMD:C_1206_3216Metric'
FP={'H1':'MountingHole:MountingHole_3.2mm_M3_Pad_Via','H2':'MountingHole:MountingHole_3.2mm_M3_Pad_Via','H3':'MountingHole:MountingHole_3.2mm_M3_Pad_Via','H4':'MountingHole:MountingHole_3.2mm_M3_Pad_Via',
 'J1':'Connector_BarrelJack:BarrelJack_CUI_PJ-102AH_Horizontal',
 'J2':'pa40:BNC_Molex_73100-0105_Horizontal',
 'J4':'pa40:Jack_3.5mm_CUI_SJ1-3523N_Horizontal_DS',
 'R12':'Resistor_SMD:R_Shunt_Vishay_WSK2512_6332Metric_T1.19mm',
 'JP1':'Jumper:SolderJumper-2_P1.3mm_Open_RoundedPad1.0x1.5mm',
 'TP1':'TestPoint:TestPoint_Keystone_5019_Miniature','TP2':'TestPoint:TestPoint_Keystone_5019_Miniature','TP3':'TestPoint:TestPoint_Keystone_5019_Miniature',
 'C10':'Capacitor_SMD:CP_Elec_6.3x7.7','C11':C8,'C12':C6,'C13':C6,'C14':C8,'C15':C6,'C4':C6,'C5':C6,'C6':C6,'C7':C6,'C8':C6,'C20':C6,
 'C1':C12,'C2':C12,'C3':C12,'C16':C12,'C17':C12,'C18':C12,'C19':C12,
 'C21':C8,'C22':C8,'C23':C8,
 'R1':R6,'R2':R6,'R3':R6,'R5':R6,'R6':R6,'R7':R6,'R8':R6,'R9':R6,'R10':R6,'R11':R6,'R13':R6,'R14':R6,
 'Q1':'pa40:EPC2036_LGA4_SMD_P0.45mm','Q2':'Package_TO_SOT_SMD:SOT-23','Q4':'Package_TO_SOT_SMD:SOT-23',
 'U1':'Package_TO_SOT_SMD:SOT-23-5','U2':'Package_SON:WSON-10-1EP_2x3mm_P0.5mm_EP0.84x2.4mm',
 'Y1':'pa40:Crystal_HC49-US_THT_SMD_Combo','C9':'pa40:C_Trimmer_Voltronics_JZ',
 'L1':'pa40:L_Toroid_FT50_Flat_P7.62mm_Drill1.0mm','L2':'pa40:L_Toroid_T80_Flat_P10.16mm_Drill1.6mm','L3':'pa40:L_Toroid_T80_Flat_P10.16mm_Drill1.6mm',
 'TP4':'TestPoint:TestPoint_Pad_D1.0mm','TP6':'TestPoint:TestPoint_Pad_D1.0mm','TP8':'TestPoint:TestPoint_Pad_D1.0mm','TP10':'TestPoint:TestPoint_Pad_D1.0mm',
 'TP5':'TestPoint:TestPoint_Pad_D1.5mm','TP7':'TestPoint:TestPoint_Pad_D1.5mm','TP9':'TestPoint:TestPoint_Pad_D1.5mm','TP11':'TestPoint:TestPoint_Pad_D1.5mm',
 'TP12':'TestPoint:TestPoint_Keystone_5019_Miniature','TP13':'TestPoint:TestPoint_Keystone_5019_Miniature','TP14':'TestPoint:TestPoint_Keystone_5019_Miniature','TP15':'TestPoint:TestPoint_Keystone_5019_Miniature',
 'D1':'pa40:D_SOT-23_A1_K3',
 'L4':'Inductor_SMD:L_Coilcraft_LPS4018','FB2':'Inductor_SMD:L_0603_1608Metric','FB3':'Inductor_SMD:L_0603_1608Metric'}
MPN={'C1':'KEMET C1206C271J1GACTU + C1206C150J1GACTU','C2':'KEMET C1206C391J2GACTU + C1206C330J2GACTU',
 'C3':'KEMET C1206C681J1GACTU + C1206C510J1GACTU','C16':'KEMET C1206C271J1GACTU','C19':'KEMET C1206C271J1GACTU',
 'C17':'KEMET C1206C151J1GACTU','C18':'KEMET C1206C180J1GACTU','C4':'Samsung CL10B473KB8NNNC',
 'C5':'Murata GRM1885C1H330JA01D','C6':'Murata GRM1885C1H330JA01D','C7':'Yageo CC0603KRX7R9BB104','C13':'Yageo CC0603KRX7R9BB104',
 'C8':'Murata GRM1885C1H102JA01D','C9':'Knowles Voltronics JZ300','C10':'Panasonic EEE-FK1E101P','C11':'Yageo CC0805KKX7R8BB105',
 'C12':'Yageo CC0603JRNPO9BN103','C15':'Yageo CC0603JRNPO9BN103','C14':'Samsung CL21B104KBCNNNC','C20':'Murata GRM1885C1H100JA01D',
 'C21':'Yageo CC0805KKX5R9BB225','C22':'Samsung CL21A226MOQNNNE','C23':'Yageo CC0805KRX5R6BB106',
 'J1':'Same Sky PJ-102AH','J2':'Molex 0731000105','J4':'Same Sky SJ1-3523N',
 'R1':'Yageo RC0603JR-070RL','R2':'Stackpole RMCF0603FT22K0','R3':'Stackpole RMCF0603FT22K0','R6':'Stackpole RMCF0603FT22K0',
 'R5':'Yageo RC0603FR-0747KL','R7':'Yageo RC0603FR-071K5L','R8':'Yageo RC0603FR-073K3L','R9':'Yageo RC0603FR-071KL',
 'R10':'Stackpole RMCF0603FT100K','R14':'Stackpole RMCF0603FT100K','R11':'Yageo RC0603FR-0791KL','R13':'Yageo RC0603FR-07523KL',
 'R12':'Vishay WSK2512R0100FEA','TP1':'Keystone 5019','TP2':'Keystone 5019','TP3':'Keystone 5019','TP12':'Keystone 5019','TP13':'Keystone 5019','TP14':'Keystone 5019','TP15':'Keystone 5019',
 'TP4':'bare pad, no part','TP5':'bare pad, no part','TP6':'bare pad, no part','TP7':'bare pad, no part','TP8':'bare pad, no part','TP9':'bare pad, no part','TP10':'bare pad, no part','TP11':'bare pad, no part',
 'D1':'DNP: SOT-23 A1/K3 footprint, see note 15',
 'Q1':'EPC EPC2036','Q2':'AOS AO3407A','Q4':'onsemi MMBT3904LT1G','U1':'TI SN74LVC1G17DBVR','U2':'TI TPS62175DQCR',
 'L1':'Fair-Rite 5961000301 (FT-50-61)','L2':'Micrometals T80-6','L3':'Micrometals T80-6',
 'L4':'Wurth 74404042100','FB2':'Murata BLM18PG221SN1D','FB3':'Murata BLM18PG221SN1D',
 'Y1':'IQD LFXTAL011525Bulk (HC-49/U, CL 30 pF)'}
syms=[]; wires=[]; juncs=[]; ncs=[]; texts=[]; pwrn=[1]
P={}
def sym(lid,ref,val,at,rot=0,mir=None,refat=None,valat=None,just='left',hide_ref=False,fp='',hide_val=False,dnp=False,in_bom=True):
    fp=fp or FP.get(ref,''); mpn=MPN.get(ref,'')
    if mpn.startswith('bare pad'): in_bom=False
    lib(lid); pins=pins_of(lid); at=(round(at[0],2),round(at[1],2))
    refat=None if refat is None else (round(refat[0],2),round(refat[1],2)); valat=None if valat is None else (round(valat[0],2),round(valat[1],2))
    for n,p in pins.items(): P[(ref,n)]=xf(at,rot,mir,p)
    if refat is None: refat=(at[0]+2.54,at[1]-1.27)
    if valat is None: valat=(at[0]+2.54,at[1]+1.27)
    m=f' (mirror {mir})' if mir else ''
    hr=' (hide yes)' if hide_ref else ''
    j=f' (justify {just})' if just else ''
    pinsx=''.join(f' (pin "{n}" (uuid "{U()}"))' for n in pins if not (lid in DERIV and n.isalpha()))
    syms.append(f'''(symbol (lib_id "{lid}") (at {at[0]} {at[1]} {rot}){m} (unit 1) (exclude_from_sim no) (in_bom {'yes' if in_bom else 'no'}) (on_board yes) (dnp {'yes' if dnp else 'no'}) (uuid "{U()}")
 (property "Reference" "{ref}" (at {refat[0]} {refat[1]} {rot}) (effects (font (size 1.27 1.27)){j}{hr}))
 (property "Value" "{val}" (at {valat[0]} {valat[1]} {rot}) (effects (font (size 1.27 1.27)){j}{' (hide yes)' if hide_val else ''}))
 (property "Footprint" "{fp}" (at {at[0]} {at[1]} 0) (effects (font (size 1.27 1.27)) (hide yes)))
 (property "Datasheet" "~" (at {at[0]} {at[1]} 0) (effects (font (size 1.27 1.27)) (hide yes))){'' if ref.startswith('#') else f' (property "MPN" "{mpn}" (at {at[0]} {at[1]} 0) (effects (font (size 1.27 1.27)) (hide yes)))'}{pinsx}
 (instances (project "pa40-classe" (path "/{ROOT}" (reference "{ref}") (unit 1)))))''')
def pwr(kind,val,at):
    ref=f'#PWR{pwrn[0]:02d}' if kind!='PWR_FLAG' else f'#FLG{pwrn[0]:02d}'; pwrn[0]+=1
    lid='power:'+kind
    va=(at[0],at[1]+3.81) if kind=='GND' else (at[0],at[1]-3.81)
    sym(lid,ref,val,at,refat=at,valat=va,just=None,hide_ref=True,hide_val=(kind=='PWR_FLAG'))
segs=[]
def W(*pts):
    for a,b in zip(pts,pts[1:]):
        if tuple(round(v,2) for v in a)==tuple(round(v,2) for v in b): continue
        segs.append((tuple(round(v,2) for v in a),tuple(round(v,2) for v in b)))
def emit_wires():
    # split any segment at an interior junction or wire endpoint so T-connections are real in KiCad
    pts=set(jp for jp in jpts)|{p for sg in segs for p in sg}
    for a,b in segs:
        inner=[p for p in pts if p not in (a,b) and min(a[0],b[0])<=p[0]<=max(a[0],b[0]) and min(a[1],b[1])<=p[1]<=max(a[1],b[1]) and (a[0]==b[0]==p[0] or a[1]==b[1]==p[1])]
        chain=sorted([a,b]+inner,key=lambda p:(p[0]-a[0])**2+(p[1]-a[1])**2)
        for u,v in zip(chain,chain[1:]): wires.append(f'(wire (pts (xy {u[0]} {u[1]}) (xy {v[0]} {v[1]})) (stroke (width 0) (type default)) (uuid "{U()}"))')
jpts=[]
def J(p):
    jpts.append((round(p[0],2),round(p[1],2))); juncs.append(f'(junction (at {p[0]} {p[1]}) (diameter 0) (color 0 0 0 0) (uuid "{U()}"))')
def NC(p): ncs.append(f'(no_connect (at {p[0]} {p[1]}) (uuid "{U()}"))')
def T(s,at,size=1.27): texts.append(f'(text "{s}" (exclude_from_sim no) (at {at[0]} {at[1]} 0) (effects (font (size {size} {size})) (justify left top)) (uuid "{U()}"))')
def L(s,at): texts.append(f'(label "{s}" (at {at[0]} {at[1]} 0) (effects (font (size 1.27 1.27)) (justify left bottom)) (uuid "{U()}"))')

# ---------- supply block ----------
sym('Connector:Barrel_Jack_Switch','J1','12.0 V in, center +',(22.86,43.18),refat=(22.86,35.56),valat=(22.86,38.1),just=None)
NC(P[('J1','3')])  # PJ-102AH pin 3: NC switch to sleeve, unused
y12=40.64
# R12: 4-terminal current shunt right after J1 (DNP-able), JP1 bypass, TP1/TP2 on the Kelvin sense pins
sym('Device:R_Shunt','R12','10m 1%',(40.64,y12),rot=90,refat=(40.64,43.18),valat=(40.64,45.72),just=None)
W(P[('J1','1')],(33.02,y12),P[('R12','1')]); J((33.02,y12))
yj=50.8
sym('Jumper:SolderJumper_2_Open','JP1','DNP shunt: close JP1',(40.64,yj),refat=(40.64,yj-3.81),valat=(34.29,yj+3.81),just='left',hide_ref=True)
W((33.02,y12),(33.02,yj),P[('JP1','1')]); W(P[('JP1','2')],(48.26,yj),(48.26,y12)); J((48.26,y12))
for pin,tp,x,lab,jst in [('2','TP1',35.56,'I+','right'),('3','TP2',45.72,'I-','left')]:
    sp=P[('R12',pin)]
    sym('Connector:TestPoint',tp,lab,(x,30.48),refat=(x-1.27 if jst=='right' else x+1.27,27.94),valat=(x-1.27 if jst=='right' else x+1.27,30.48),just=jst)
    W(sp,(sp[0],33.02),(x,33.02),(x,30.48))
xs=[48.26,50.8,53.34,58.42,68.58,81.28]
W(P[('R12','4')],*[(x,y12) for x in xs])
pwr('PWR_FLAG','PWR_FLAG',(50.8,y12)); pwr('VDD','+12V',(53.34,y12))
for x in (50.8,53.34,58.42,68.58): J((x,y12))
W(P[('J1','2')],(30.48,50.8),(27.94,50.8)); pwr('GND','GND',(30.48,50.8)); pwr('PWR_FLAG','PWR_FLAG',(27.94,50.8))
for ref,val,x in [('C10','100u',58.42),('C11','1u X7R',68.58),('C12','10n C0G',81.28)]:
    sym('Device:C_Small',ref,val,(x,45.72))
    W((x,y12),P[(ref,'1')]); pwr('GND','GND',P[(ref,'2')])
sym('Connector:TestPoint','TP3','GND',(63.5,30.48),refat=(64.77,27.94),valat=(64.77,30.48))
W((63.5,30.48),(63.5,33.02)); pwr('GND','GND',(63.5,33.02))
# ---------- driver ----------
yd=101.6
sym('74xGxx:74LVC1G17','U1','74LVC1G17',(43.18,yd),refat=(48.26,109.22),valat=(48.26,111.76))
W((22.86,yd),P[('U1','2')]); L('xo',(22.86,yd))
NC(P[('U1','1')])
vcc=P[('U1','5')]
W(vcc,(vcc[0],88.9)); pwr('VDD','+5V',(vcc[0],88.9))
sym('Device:C_Small','C13','0.1u X7R',(53.34,91.44))
W((vcc[0],88.9),P[('C13','1')])
pwr('GND','GND',P[('C13','2')])
pwr('GND','GND',P[('U1','3')])
sym('Device:R_Small_US','R1','0R',(60.96,yd),rot=90,refat=(60.96,96.52),valat=(60.96,98.81),just=None)
W(P[('U1','4')],P[('R1','2')] if P[('R1','2')][0]<P[('R1','1')][0] else P[('R1','1')])
rr=P[('R1','1')] if P[('R1','1')][0]>P[('R1','2')][0] else P[('R1','2')]
sym('pa40:EPC2036','Q1','EPC2036',(83.82,yd),refat=(88.9,100.33),valat=(88.9,102.87))
W(rr,P[('Q1','G')]); pwr('GND','GND',P[('Q1','S')])
L('gate',(63.5,yd))
# rev 6 (was F): DNP gate-source clamp D1 right at the Q1 gate (cathode to gate, anode to source/GND)
sym('Device:D_Zener_Small','D1','DNP clamp',(68.58,yd+2.54),rot=270,refat=(64.77,103.505),valat=(64.77,106.045),just='left',dnp=True)
J((68.58,yd)); pwr('GND','GND',P[('D1','2')])
# rev 6 (was F): gate probe pair TP4 (gate, after R1) + TP5 (GND for the probe ground spring)
sym('Connector:TestPoint','TP4','gate',(73.66,yd),refat=(72.39,96.52),valat=(72.39,99.06),just='right'); J((73.66,yd))
sym('Connector:TestPoint','TP5','GND',(73.66,109.22),refat=(74.93,105.41),valat=(74.93,107.95))
W((73.66,109.22),(73.66,111.76)); pwr('GND','GND',(73.66,111.76))
# ---------- drain / tank ----------
D=P[('Q1','D')]; yt=86.36
W(D,(D[0],yt))
sym('Device:L_Small','L1','47u FT50-61 26t #24',(D[0],76.2))
W(P[('L1','2')],(D[0],yt)); J((D[0],yt))
ys=68.58
W(P[('L1','1')],(D[0],ys),(D[0]+2.54,ys)); L('+12V_PA',(D[0]+2.54,ys)); J((D[0],ys))
for ref,val,x in [('C14','0.1u X7R',68.58),('C15','10n C0G',53.34)]:
    sym('Device:C_Small',ref,val,(x,73.66))
    W(P[(ref,'1')],(x,ys)); pwr('GND','GND',P[(ref,'2')])
W((53.34,ys),(68.58,ys),(D[0],ys)); J((68.58,ys))
L('drain',(D[0]+1.27,yt))
# rev 6 (was F): drain probe pair TP6 (drain) + TP7 (GND, place at the Q1 source end of C1)
sym('Connector:TestPoint','TP6','drain',(93.98,yt),refat=(95.25,81.28),valat=(95.25,83.82)); J((93.98,yt))
S1=P[('Q1','S')]
W(S1,(S1[0]+2.54,S1[1])); J(S1)
sym('Connector:TestPoint','TP7','GND',(S1[0]+2.54,S1[1]),rot=270,refat=(S1[0]+7.62,S1[1]-1.27),valat=(S1[0]+7.62,S1[1]+1.27),just='right')
x1=99.06
sym('Device:C_Small','C1','285p C0G',(x1,yt+2.54))
W((D[0],yt),(x1,yt)); W(P[('C1','1')],(x1,yt)); J((x1,yt)); pwr('GND','GND',P[('C1','2')])
sym('Device:C_Small','C2','424.5p C0G',(109.22,yt),rot=90,refat=(109.22,80.01),valat=(109.22,82.55),just=None)
a,b=sorted([P[('C2','1')],P[('C2','2')]])
W((x1,yt),a)
# rev 7 layout: L2 mirrored (pin 2 = C2 end) to shorten the C2-L2 run on the PCB
sym('Device:L_Small','L2','2.18u T80-6 22t #16',(127.0,yt),rot=90,mir='y',refat=(127.0,80.01),valat=(127.0,82.55),just=None)
c,d=sorted([P[('L2','1')],P[('L2','2')]])
W(b,c)
xo=142.24
sym('Device:C_Small','C3','731p C0G',(xo,yt+2.54))
W(d,(xo,yt)); W(P[('C3','1')],(xo,yt)); J((xo,yt)); pwr('GND','GND',P[('C3','2')])
L('out_50r',(xo+5.08,yt))
# rev 6 (was F): tank-output probe pair TP10 (out_50r, before the LPF) + TP11 (GND at the C3 ground pad)
sym('Connector:TestPoint','TP10','out_50r',(xo+2.54,yt),refat=(xo+3.81,yt-6.35),valat=(xo+3.81,yt-3.81)); J((xo+2.54,yt))
C3g=P[('C3','2')]
W(C3g,(C3g[0]-2.54,C3g[1])); J(C3g)
sym('Connector:TestPoint','TP11','GND',(C3g[0]-2.54,C3g[1]),rot=90,refat=(C3g[0]-7.62,C3g[1]-1.27),valat=(C3g[0]-7.62,C3g[1]+1.27),just='left')
# ---------- 3-pole elliptic LPF (Zverev CC 03, rho 10%, theta 38 deg, zero at 14.06 MHz) ----------
xa=157.48
sym('Device:C_Small','C16','270p C0G',(xa,yt+2.54))
xt=172.72
sym('Device:L_Small','L3','0.76u T80-6 13t',(xt,yt),rot=90,refat=(xt,yt-21.59),valat=(xt,yt-19.05),just=None)
la,lb=sorted([P[('L3','1')],P[('L3','2')]])
W((xo,yt),(xa,yt),la); W(P[('C16','1')],(xa,yt)); J((xa,yt)); pwr('GND','GND',P[('C16','2')])
yc1=yt-7.62; yc2=yt-15.24
sa,sb=la[0]-2.54,lb[0]+2.54   # trap stubs 2.54 mm clear of the L3 pins (rev 3 nit)
sym('Device:C_Small','C17','150p C0G',(xt,yc1),rot=90,refat=(sa-1.27,yc1-1.27),valat=(sa-1.27,yc1+1.27),just='left')
sym('Device:C_Small','C18','18p C0G',(xt,yc2),rot=90,refat=(sa-1.27,yc2-1.27),valat=(sa-1.27,yc2+1.27),just='left')
for x,pin in ((sa,'a'),(sb,'b')):
    W((x,yt),(x,yc1)); W((x,yc1),(x,yc2)); J((x,yt)); J((x,yc1))
for ref in ('C17','C18'):
    p1,p2=sorted([P[(ref,'1')],P[(ref,'2')]]); W((sa,p1[1]),p1); W(p2,(sb,p2[1]))
xb=185.42
sym('Device:C_Small','C19','270p C0G',(xb,yt+2.54))
W(lb,(xb,yt)); W(P[('C19','1')],(xb,yt)); J((xb,yt)); pwr('GND','GND',P[('C19','2')])
sym('Connector:Conn_Coaxial','J2','RF out, 50 Ω',(200.66,yt),refat=(200.66,80.01),valat=(200.66,82.55),just=None)
W((xb,yt),P[('J2','1')]); pwr('GND','GND',P[('J2','2')])
L('rf_out',(xb+1.27,yt))
T('3-pole elliptic LPF',(150.62,100.33),1.524)
T('trap 14.06 MHz: tune by spreading L3 turns',(150.62,103.505))
# ---------- PA keying: PMOS high side on the PA rail (topology copied from OpenBeacon 2) ----------
yk=40.64
sym('pa40:Q_PMOS_GSD','Q2','AO3407A',(139.7,yk+2.54),rot=90,mir='y',refat=(139.7,33.02),valat=(139.7,35.56),just=None)
S2,D2,G2=P[('Q2','S')],P[('Q2','D')],P[('Q2','G')]
pwr('VDD','+12V',(124.46,yk)); W((124.46,yk),S2)
yg=G2[1]+2.54
sym('Device:R_Small_US','R2','22k',(129.54,yk+5.08),refat=(127.94,44.45),valat=(127.94,46.99),just='right')
W((129.54,yk),P[('R2','1')]); J((129.54,yk))
W(P[('R2','2')],(129.54,yg),(149.86,yg)); W(G2,(G2[0],yg)); J((G2[0],yg))
sym('Device:C_Small','C4','47n X7R',(149.86,yk+5.08),refat=(151.13,44.45),valat=(151.13,46.99))
W(D2,(149.86,yk),(154.94,yk)); W((149.86,yk),P[('C4','1')]); J((149.86,yk)); W(P[('C4','2')],(149.86,yg))
W((154.94,yk),(160.02,yk)); L('+12V_PA',(160.02,yk))
# rev 6 (was F): TP14 keyed PA rail, TP15 Q2 gate (keying), Keystone 5019
sym('Connector:TestPoint','TP14','PA rail',(157.48,yk),refat=(158.75,34.29),valat=(158.75,36.83)); J((157.48,yk))
sym('Connector:TestPoint','TP15','Q2 gate',(147.32,yg),mir='x',refat=(148.59,53.34),valat=(148.59,55.88)); J((147.32,yg))
sym('Device:R_Small_US','R3','22k',(G2[0],yg+5.08),refat=(G2[0]+1.27,yg+3.81),valat=(G2[0]+1.27,yg+6.35))
W((G2[0],yg),P[('R3','1')])
r3b=P[('R3','2')]
W(r3b,(r3b[0],yg+10.16+2.54),(132.08,yg+10.16+2.54))
sym('Connector_Audio:AudioJack3','J4','KEY 3.5 mm',(127.0,yg+15.24),mir='x',refat=(124.46,yg+8.89),valat=(124.46,yg+22.86),just=None)
NC(P[('J4','R')])  # ring unused: a mono plug shorts ring to sleeve
k2=P[('J4','S')]
W(k2,(k2[0]+2.54,k2[1]),(k2[0]+2.54,k2[1]+2.54)); pwr('GND','GND',(k2[0]+2.54,k2[1]+2.54))
T('PA keying (PMOS high side, as OpenBeacon 2)',(119.38,27.94),1.524)
# ---------- 7.030 MHz Pierce oscillator (discrete MMBT3904) ----------
oy=22.86
yb=127.0+oy; ytop=yb-20.32
sym('pa40:Q_NPN_BEC','Q4','MMBT3904',(50.8,yb),refat=(55.88,yb-1.27),valat=(55.88,yb+1.27))
B4,C4p,E4=P[('Q4','B')],P[('Q4','C')],P[('Q4','E')]
# base line with CB, RB1 (up), RB2 (down)
W((17.78,yb),B4)
for x in (30.48,35.56,40.64): J((x,yb))
sym('Device:C_Small','C5','33p C0G',(30.48,yb+5.08),refat=(26.67,yb+3.81),valat=(26.67,yb+6.35),just='right')
W((30.48,yb),P[('C5','1')]); pwr('GND','GND',P[('C5','2')])
sym('Device:R_Small_US','R5','47k',(35.56,yb-5.08),refat=(36.83,yb-6.35),valat=(36.83,yb-3.81))
W(P[('R5','2')],(35.56,yb)); pwr('VDD','+5V',P[('R5','1')])
sym('Device:R_Small_US','R6','22k',(40.64,yb+5.08),refat=(41.91,yb+3.81),valat=(41.91,yb+6.35))
W((40.64,yb),P[('R6','1')]); pwr('GND','GND',P[('R6','2')])
# emitter
ye=E4[1]+1.27
sym('Device:R_Small_US','R7','1.5k',(E4[0],ye+3.81),refat=(E4[0]-1.27,ye+2.54),valat=(E4[0]-1.27,ye+5.08),just='right')
W(E4,P[('R7','1')]); J((E4[0],ye)); pwr('GND','GND',P[('R7','2')])
sym('Device:C_Small','C7','100n X7R',(58.42,ye+3.81),refat=(59.69,ye+2.54),valat=(59.69,ye+5.08))
W((E4[0],ye),(58.42,ye),P[('C7','1')]); pwr('GND','GND',P[('C7','2')])
# crystal loop over the top: base -> Y1 -> cx (C6 to GND) -> R9 -> collector
W((17.78,yb),(17.78,ytop))
sym('Device:Crystal_Small','Y1','7.030 MHz',(35.56,ytop),refat=(35.56,ytop-5.08),valat=(35.56,ytop-2.54),just=None)
W((17.78,ytop),(20.32,ytop)); J((20.32,ytop)); J((30.48,ytop))
sym('Device:C_Trim_Small','C9','5.5-30p',(25.4,ytop),rot=90,refat=(24.13,ytop-5.08),valat=(24.13,ytop-2.54),just=None)
c9a,c9b=sorted([P[('C9','1')],P[('C9','2')]])
W((20.32,ytop),c9a); W(c9b,(30.48,ytop),P[('Y1','1')])
sym('Device:C_Small','C20','10p C0G',(25.4,ytop+5.08),rot=90,refat=(25.4,ytop+7.62),valat=(25.4,ytop+10.16),just=None)
c20a,c20b=sorted([P[('C20','1')],P[('C20','2')]])
W((20.32,ytop),(20.32,ytop+5.08),c20a); W(c20b,(30.48,ytop+5.08),(30.48,ytop))
sym('Device:C_Small','C6','33p C0G',(43.18,ytop+2.54),refat=(41.91,ytop+1.27),valat=(41.91,ytop+3.81),just='right')
W(P[('Y1','2')],(43.18,ytop)); W((43.18,ytop),P[('C6','1')]); J((43.18,ytop)); pwr('GND','GND',P[('C6','2')])
sym('Device:R_Small_US','R9','1k',(48.26,ytop),rot=90,refat=(48.26,ytop-5.08),valat=(48.26,ytop-2.54),just=None)
r9a,r9b=sorted([P[('R9','1')],P[('R9','2')]])
W((43.18,ytop),r9a); W(r9b,(C4p[0],ytop),C4p)
# collector load and output coupling
yr=ytop+5.08
J((C4p[0],yr)); W((C4p[0],yr),(60.96,yr))
sym('Device:R_Small_US','R8','3.3k',(60.96,yr-2.54),refat=(62.23,yr-3.81),valat=(62.23,yr-1.27))
pwr('VDD','+5V',P[('R8','1')])
yo=yr+2.54
J((C4p[0],yo))
sym('Device:C_Small','C8','1n C0G',(66.04,yo),rot=90,refat=(66.04,yo+2.54),valat=(66.04,yo+5.08),just=None)
c8a,c8b=sorted([P[('C8','1')],P[('C8','2')]])
W((C4p[0],yo),c8a); W(c8b,(73.66,yo),(81.28,yo)); J((73.66,yo)); L('xo',(76.2,yo))
# rev 6 (was F): XO probe pair TP8 (xo = U1 input) + TP9 (GND)
sym('Connector:TestPoint','TP8','xo',(81.28,yo),refat=(82.55,yo-5.08),valat=(82.55,yo-2.54))
sym('Connector:TestPoint','TP9','GND',(83.82,yo+5.08),refat=(85.09,yo+1.27),valat=(85.09,yo+3.81))
W((83.82,yo+5.08),(83.82,yo+7.62)); pwr('GND','GND',(83.82,yo+7.62))
sym('Device:R_Small_US','R10','100k',(73.66,yo-5.08),refat=(74.93,yo-6.35),valat=(74.93,yo-3.81))
W(P[('R10','2')],(73.66,yo)); pwr('VDD','+5V',P[('R10','1')])
sym('Device:R_Small_US','R11','91k',(73.66,yo+5.08),refat=(74.93,yo+3.81),valat=(74.93,yo+6.35))
W((73.66,yo),P[('R11','1')]); pwr('GND','GND',P[('R11','2')])
T('7.030 MHz Pierce oscillator (MMBT3904, about 0.8 mA)',(20.32,121.92),1.524)
# ---------- 5 V buck: TPS62175 per TI SLVSB35C Fig. 8 ----------
ux,uy=127.0,134.62
sym('pa40:TPS62175','U2','TPS62175',(ux,uy),refat=(ux-7.62,uy-10.16),valat=(ux-7.62,uy+12.7))
yv=P[('U2','2')][1]
pwr('VDD','+12V',(88.9,yv))
sym('Device:FerriteBead_Small','FB2','BLM18PG221',(99.06,yv),rot=90,refat=(99.06,yv-5.08),valat=(99.06,yv-2.54),just=None)
f2a,f2b=sorted([P[('FB2','1')],P[('FB2','2')]])
W((88.9,yv),f2a); W(f2b,(106.68,yv),(109.22,yv),(111.76,yv),P[('U2','2')]); J((106.68,yv)); J((111.76,yv)); J((109.22,yv)); pwr('PWR_FLAG','PWR_FLAG',(109.22,yv))
sym('Device:C_Small','C21','2.2u 50V X5R',(106.68,yv+5.08),refat=(105.41,yv+3.81),valat=(105.41,yv+6.35),just='right')
W((106.68,yv),P[('C21','1')]); pwr('GND','GND',P[('C21','2')])
W((111.76,yv),(111.76,P[('U2','3')][1]),P[('U2','3')])
sw=P[('U2','9')]; xl=142.24
sym('Device:L_Small','L4','10u',(xl,yv),rot=90,refat=(xl,yv-5.08),valat=(xl,yv-2.54),just=None)
la4,lb4=sorted([P[('L4','1')],P[('L4','2')]])
W(sw,la4)
xv,xr,xc=149.86,157.48,170.18
W(lb4,(xv,yv),(xr,yv),(xc,yv)); J((xv,yv)); J((xr,yv)); J((xc,yv))
vos,slp,fbp,pg=P[('U2','10')],P[('U2','8')],P[('U2','5')],P[('U2','7')]
W(vos,(xv,vos[1])); W(slp,(xv,slp[1])); W((xv,yv),(xv,vos[1]),(xv,slp[1])); J((xv,vos[1]))
sym('Device:R_Small_US','R13','523k 1%',(xr,yv+5.08),refat=(xr+1.27,yv+3.81),valat=(xr+1.27,yv+6.35))
W((xr,yv),P[('R13','1')])
W(fbp,(xr,fbp[1])); W(P[('R13','2')],(xr,fbp[1])); J((xr,fbp[1]))
sym('Device:R_Small_US','R14','100k 1%',(xr,fbp[1]+5.08),refat=(xr+1.27,fbp[1]+3.81),valat=(xr+1.27,fbp[1]+6.35))
W((xr,fbp[1]),P[('R14','1')]); pwr('GND','GND',P[('R14','2')])
NC(pg)
sym('Device:C_Small','C22','22u 10V X5R',(xc,yv+5.08),refat=(xc+1.27,yv+3.81),valat=(xc+1.27,yv+6.35))
W((xc,yv),P[('C22','1')]); pwr('GND','GND',P[('C22','2')])
xb3=177.8
sym('Device:FerriteBead_Small','FB3','BLM18PG221',(xb3,yv),rot=90,refat=(xb3,yv-5.08),valat=(xb3,yv-2.54),just=None)
f3a,f3b=sorted([P[('FB3','1')],P[('FB3','2')]])
W((xc,yv),f3a)
xo5=187.96
sym('Device:C_Small','C23','10u 10V X5R',(xo5,yv+5.08),refat=(xo5+1.27,yv+3.81),valat=(xo5+1.27,yv+6.35))
W(f3b,(xo5,yv),(190.5,yv),(193.04,yv)); J((xo5,yv)); J((190.5,yv)); pwr('PWR_FLAG','PWR_FLAG',(190.5,yv)); W((xo5,yv),P[('C23','1')]); pwr('GND','GND',P[('C23','2')])
pwr('VDD','+5V',(193.04,yv))
# rev 6 (was F): TP12 +5V and TP13 GND (Keystone 5019) at the buck output
W((193.04,yv),(200.66,yv)); J((193.04,yv))
sym('Connector:TestPoint','TP12','+5V',(200.66,yv),refat=(201.93,yv-5.08),valat=(201.93,yv-2.54))
sym('Connector:TestPoint','TP13','GND',(200.66,yv+12.7),refat=(201.93,yv+8.89),valat=(201.93,yv+11.43))
W((200.66,yv+12.7),(200.66,yv+15.24)); pwr('GND','GND',(200.66,yv+15.24))
gp=[P[('U2',n)] for n in ('4','1','6','11')]
gx=gp[0][0]-2.54
for p in gp: W(p,(gx,p[1]))
W((gx,gp[0][1]),(gx,gp[-1][1]+2.54)); J((gx,gp[1][1])); J((gx,gp[2][1])); J((gx,gp[3][1]))
pwr('GND','GND',(gx,gp[-1][1]+2.54))
T('5 V buck: TPS62175 (TI SLVSB35C Fig. 8), ferrite-bead filtered',(93.98,118.11),1.524)
T('Vout = 0.8 V x (1 + R13/R14) = 4.98 V. SLEEP to VOUT: normal mode. PG unused.',(93.98,154.94))
# block titles
T('12.0 V input, current shunt and decoupling',(20.32,22.86),1.524)
T('Gate drive',(20.32,83.82),1.524)
T('Class E stage: L1 feed, C1, C2-L2 tank, C3 match',(60.96,58.42),1.27)
notes=[
"NOTES (values from the page 'Efficient 5 W 40 m PA: options',",
"worked example 7.030 MHz, 12.0 V, 5.0 W, QL 5; Sokal AACD 2001)",
"1. C1: 338.7 pF total shunt incl. EPC2036 Coss -> about 285 pF",
"   external (page). Sim: about 260 pF gives ZVS. Trim on the bench.",
"2. C2 424.5 pF (eq. 9). L2 = 1.616 + 0.507 uH L-match = 2.122 uH;",
"   wound 2.18 uH, T-80-6 22 t #16. C3 731 pF = L-match at 50 ohm.",
"3. RF caps C0G/NP0 1206: C1, C3, C16-C19 100 V; C2 200 V (est.",
"   58 V pk = 12 V DC + 46 V RF). C1-C3 are E12 pairs (BOM CSV).",
"4. L1 FT-50-61 (Fair-Rite 5961000301) 26 t #24, about 47 uH.",
"5. Q1 EPC2036: 100 V, 73 mOhm max; peak drain about 43 V. GATE ABS",
"   MAX 6 V: 5 V rail only, tiny gate loop, ESD care. R1 0R; see T2.",
"6. U1 SN74LVC1G17 at 5 V, input biased about 2.4 V (R10/R11). XO",
"   swing 0.7-4.0 V (sim) clears VT+ 3.33 V max, VT- 1.51 V min.",
"7. LPF: Zverev CC 03 (rho 10 %, theta 38 deg), trap at 14.06 MHz.",
"   L3 13 t T-80-6 (about 0.76 uH): tune the trap by spreading L3.",
"8. XO: Q4 MMBT3904 (2N3904 die in SOT-23), 0.79 mA (sim). Y1",
"   IQD LFXTAL011525Bulk (HC-49/U THT, CL 30 pF) or any SMD HC-49/US",
"   on the combo footprint. C9 Voltronics JZ300 (5.5-30 pF) || C20",
"   10p in series with Y1 (sim was for CL 20 pF; retrim). R9 limits",
"   drive to about 80 uW (sim). XO and U1 run continuously.",
"9. KEYING as OpenBeacon 2: Q2 AO3407A high side, R2/R3 22k, C4",
"   47n: about 1.4 ms rise, 5 ms fall (sim); Vgs keyed -6 V. J4:",
"   3.5 mm TRS jack SJ1-3523N: key across tip and sleeve (tip shorted to",
"   GND = TX). Ring NC, never tied to tip: a mono plug grounds the ring.",
"   +12V_PA is the keyed PA rail. J1 PJ-102AH 5.5x2.1 plug, center +.",
"10. R12 shunt, OPTIONAL / DNP: WSK2512R0100FEA 10 mOhm 1 %.",
"   10 mV/A (4.4 mV at 444 mA) across TP1/TP2. DNP: close JP1.",
"11. U2 TPS62175DQCR (TI SLVSB35C Fig. 8): Vin 4.75-28 V, 1 MHz",
"   DCS-Control with power save. L4 Wurth 74404042100 10u, 4018 (LPS4018 pads).",
"   SLEEP to VOUT (normal mode, about 87 % at 5 mA vs 84 % in sleep,",
"   12 V, Fig. 9/11). EN to VIN. +5V load about 5 mA (8 mA max).",
"12. FB2/FB3 BLM18PG221SN1D with C21/C23 keep buck ripple off +12V",
"   and +5V. 7th harmonic of 1 MHz is near 7 MHz: check spurs on a",
"   spectrum analyzer and keep L4 away from L2/L3.",
"13. Through-hole by choice: J1, J2, J4 (cable strain), L1-L3.",
"14. Q1: 0.20 mm mask-defined pads on 0.30 mm Cu (EPC ds p.6); ENIG.",
]
for i,s in enumerate(notes): T(s,(208.28,30.48+i*3.556))
tpn=[
"REV 6 TEST POINTS. Probe pairs, signal pad + GND pad for a probe ground spring: TP4/TP5 gate, TP6/TP7 drain, TP8/TP9 xo, TP10/TP11 out_50r.",
"T1. Pairs are bare SMD pads (1.0 mm signal, 1.5 mm GND), not loops, for less C and loop area on RF nodes. Layout: GND pad within 5 mm",
"   (aim 2.5-3 mm) of its signal pad, GND via straight to the plane at Q1 source / C3 / U1 GND. TP4 at the Q1 gate pad, after R1.",
"T2. R1 0R (sim: no gate overshoot with a 2 nH loop); fit 2.2R if TP4 shows over 5.5 V. D1 DNP: zeners cost 0.12-0.14 points and",
"   a 6V2 cannot hold the gate under 6 V; BAT54 only limits undershoot. SOT-23, K to gate, A to source. See report sec. 3-4.",
"T3. Drain about 43 V pk (sim): use a 10x low-C probe; its C adds to C1, so retune C1 with it off. DC points (Keystone 5019): TP12 +5V,",
"   TP13 GND, TP14 PA rail, TP15 Q2 gate. PA current: TP1-TP2 across R12 (10 mV/A). RF output: J2.",
]
for i,s in enumerate(tpn): T(s,(20.32,172.72+i*3.556))
# rev 7 layout v2: plated M3 mounting holes H1-H4 tied to GND (same approach as Si5351AVFO)
T('Mounting holes: plated M3 pads, tied to GND',(172.72,30.48),1.27)
for i,x in enumerate((175.26,182.88,190.5,198.12)):
    ref=f'H{i+1}'
    sym('Mechanical:MountingHole_Pad',ref,'MountingHole_Pad',(x,38.1),refat=(x+2.54,36.83),valat=(x+2.54,39.37),hide_val=True,in_bom=False)
    pwr('GND','GND',P[(ref,'1')])
emit_wires()
tb=f'''(title_block (title "40 m 5 W GaN class E CW TX: XO, PMOS keying, LPF") (date "2026-11-18") (rev "7")
 (company "Etherkit / NT7S")
 (comment 1 "Source: Efficient 5 W 40 m PA: options, worked example")
 (comment 2 "Rev 7: DC jack J1, 3.5 mm key jack J4, J2 Molex 0731000105 BNC. Rev 6 (was F): TP4-TP15, DNP D1")
 (comment 3 "Rev 5 (was E): SMT, TPS62175 buck. Prototype revs 1-6 were A-F"))'''
out=f'''(kicad_sch (version 20250114) (generator "eeschema") (generator_version "9.0") (uuid "{ROOT}") (paper "A4")
{tb}
(lib_symbols
{chr(10).join(libs.values())}
)
{chr(10).join(juncs)}
{chr(10).join(ncs)}
{chr(10).join(wires)}
{chr(10).join(texts)}
{chr(10).join(syms)}
(sheet_instances (path "/" (page "1")))
(embedded_fonts no)
)'''
open('pa40-classe.kicad_sch','w').write(out)
open('pa40.kicad_sym','w').write('(kicad_symbol_lib (version 20241209) (generator "gen") '+'\n'.join(v.replace(f'"{k}"','"'+k.split(':')[1]+'"',1) for k,v in libs.items() if k.startswith('pa40:'))+')')
open('sym-lib-table','w').write('(sym_lib_table (version 7) (lib (name "pa40")(type "KiCad")(uri "${KIPRJMOD}/pa40.kicad_sym")(options "")(descr "")))')
print("ok", len(syms))
