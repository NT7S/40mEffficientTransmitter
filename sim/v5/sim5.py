# Rev F gate-drive mitigation study: R1 sweep x gate-loop L, then gate-source clamps.
# Base: trimmed design (C1 260 pF, L2 2.122 uH) + 3-pole elliptic LPF, as sim/v2/v2_trimmed.
# Driver modeled as before: ideal 0-5 V square, 1 ns edges, 7 ohm output (estimate).
import sys, json, subprocess, numpy as np, re
sys.path.insert(0,'..'); sys.path.insert(0,'../v2')
import pa, sim2
from concurrent.futures import ProcessPoolExecutor
F=pa.F; T=pa.T
MODELS="""* Diodes Inc. SPICE models (diodes.com/spice/download/...): BZX84C5V6 (886), BZX84C6V2 (887), BAT54W (438)
.include models/BZX84C5V6.spice.txt
.include models/BZX84C6V2.spice.txt
.include models/BAT54W.spice.txt
"""
CL={'none':'',
    'bat54':'DCL1 0 gc DI_BAT54W\n',
    'z5v6':'XZ1 0 gc DI_BZX84C5V6\n',
    'z6v2':'XZ1 0 gc DI_BZX84C6V2\n',
    'bat54+z5v6':'DCL1 0 gc DI_BAT54W\nXZ1 0 gc DI_BZX84C5V6\n',
    'bat54+z6v2':'DCL1 0 gc DI_BAT54W\nXZ1 0 gc DI_BZX84C6V2\n'}
def deck(r1,lg,clamp,name,ncyc=300):
    s=pa.netlist(260e-12,ncyc,sim2.LPF,name,0.35,2.122e-6)
    old=s[s.index('* Gate drive:'):s.index('.options')]
    new=f"""* Gate drive: 74LVC1G17 at 5 V as ideal 0-5 V square, 1 ns edges, 7 Ohm output (estimate, as v2).
* R1 = {r1} Ohm; gate loop L = {lg} nH (assumed, lumped between R1 and the Q1 gate pad); clamp = {clamp}
VDRV drv 0 PULSE(0 5 0 1n 1n {{per/2-1n}} {{per}})
RDRV drv g1 7
R1 g1 g2 {max(r1,1e-4)}
{'LG g2 g '+str(lg)+'n' if lg>0 else 'RLG g2 g 1e-4'}
VCL g gc 0
{CL[clamp]}{MODELS if clamp!='none' else ''}"""
    s=s.replace(old,new)
    s=s.replace("linearize v(d) v(g) v(load) i(VDD) i(VDRV)\nwrdata "+name+".dat v(d) v(g) v(load) i(VDD) i(VDRV)",
        "linearize v(d) v(g) v(rf) i(VDD) i(VDRV) v(out) i(VFIN) v(drv) i(VCL) v(xq1.gate)\nwrdata "+name+".dat v(d) v(g) v(rf) i(VDD) i(VDRV) v(out) i(VFIN) v(drv) i(VCL) v(xq1.gate)")
    assert 'v(xq1.gate)' in s
    return s
def run(args):
    r1,lg,clamp=args
    name=f"g_r{r1}_l{lg}_{clamp}".replace('.','p').replace('+','_')
    open(name+'.cir','w').write(deck(r1,lg,clamp,name))
    r=subprocess.run(['ngspice','-b',name+'.cir'],capture_output=True,text=True)
    if r.returncode or 'rror' in r.stdout[-3000:] and 'Error' in r.stdout: print(name, r.stdout[-1500:])
    d=np.loadtxt(name+'.dat')
    t,vd,vg,vo,idd,idrv,vin,ifin,vdrv,icl,vgi=d[:,0],d[:,1],d[:,3],d[:,5],-d[:,7],-d[:,9],d[:,11],d[:,13],d[:,15],d[:,17],d[:,19]
    res,_=pa.analyze(t,vd,vg,vo,idd,idrv)
    t0=t[-1]-100*T; tt=np.linspace(t0,t[-1],100*512,endpoint=False)
    I=lambda x: np.interp(tt,t,x)
    res['P_filter_in']=float(np.mean(I(vin)*I(ifin)))
    res['P_drv_src']=float(np.mean(I(vdrv)*I(idrv)))          # power drawn from the ideal 5 V source
    res['I_5V_gate']=res['P_drv_src']/5.0
    res['P_clamp']=float(np.mean(I(vg)*I(icl)))
    res['vg_pad_max']=float(I(vg).max()); res['vg_pad_min']=float(I(vg).min())
    res['vg_int_max']=float(I(vgi).max()); res['vg_int_min']=float(I(vgi).min())
    res['icl_pk']=float(np.abs(I(icl)).max())
    res.update(R1=r1,LG_nH=lg,clamp=clamp,name=name)
    # keep a few cycles of waveform for plots
    m=t>=t[-1]-3*T
    np.savez_compressed(name+'_wave.npz',t=t[m]-t[m][0],vg=vg[m],vgi=vgi[m],vd=vd[m],icl=icl[m])
    import os; os.remove(name+'.dat')
    return res
if __name__=='__main__':
    which=sys.argv[1]
    if which=='r1':
        cases=[(r,l,'none') for l in (0,1,2) for r in (0,1,2.2,3.3,4.7,10)]
    elif which=='stress':
        cases=[(r,5,'none') for r in (0,1,2.2,3.3,4.7,10)]
    elif which=='clamp5':
        cases=[(0.0,5,c) for c in ('bat54','z5v6','z6v2','bat54+z5v6','bat54+z6v2')]
    else:
        best=float(sys.argv[2])
        cases=[(r,2,c) for r in sorted({0.0,best}) for c in ('bat54','z5v6','z6v2','bat54+z5v6','bat54+z6v2')]
    with ProcessPoolExecutor(8) as ex: res=list(ex.map(run,cases))
    json.dump(res,open(f'results_{which}.json','w'),indent=1,default=float)
    for r in res:
        print(f"{r['name']:28s} P1 {r['P1']:.3f} Pdc {r['Pdc']:.3f} eta {100*r['eta1']:.2f} Ig5 {1000*r['I_5V_gate']:.2f} mA vg {r['vg_pad_max']:.2f}/{r['vg_pad_min']:.2f} int {r['vg_int_max']:.2f}/{r['vg_int_min']:.2f} Pcl {1000*r['P_clamp']:.2f} mW Von {r['v_turnon']:.2f}")
