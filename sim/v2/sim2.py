import sys, json, subprocess, numpy as np
sys.path.insert(0,'..'); import pa
from concurrent.futures import ProcessPoolExecutor
F=pa.F; T=pa.T; w=2*np.pi*F
QL=320; QC=1000   # Page estimates: T-80-6 LPF inductor Qu about 320; C0G Q 1000
AL=45e-6/100**2   # T-80-6 AL 45 uH per 100 turns
L3=AL*13**2       # 13 t as wound = 0.7605 uH
LPF=f"""* 3-pole elliptic LPF as drawn (C16, L3||C17+C18, C19); ESRs from Q at 7.03 MHz
VFIN out fin 0
C16 fin c16m 270p
RC16 c16m 0 {1/(w*270e-12*QC):.5f}
L3 fin l3m {L3:.6e}
RL3 l3m rf {w*L3/QL:.5f}
C17 fin c17m 150p
RC17 c17m rf {1/(w*150e-12*QC):.5f}
C18 fin c18m 18p
RC18 c18m rf {1/(w*18e-12*QC):.5f}
C19 rf c19m 270p
RC19 c19m 0 {1/(w*270e-12*QC):.5f}
RLOAD rf 0 50
VSENSE rf load 0
RDUMMY load 0 1e12
"""
def run(c1,l2,name,ncyc=300):
    s=pa.netlist(c1,ncyc,LPF,name,0.35,l2)
    s=s.replace("linearize v(d) v(g) v(load) i(VDD) i(VDRV)\nwrdata "+name+".dat v(d) v(g) v(load) i(VDD) i(VDRV)",
                "linearize v(d) v(g) v(rf) i(VDD) i(VDRV) v(out) i(VFIN)\nwrdata "+name+".dat v(d) v(g) v(rf) i(VDD) i(VDRV) v(out) i(VFIN)")
    assert 'v(out) i(VFIN)' in s
    s=s.replace('* 40 m 5 W single-ended GaN class E PA, tank + L-match','* 40 m 5 W single-ended GaN class E PA, tank + L-match + 3-pole elliptic LPF')
    open(name+'.cir','w').write(s)
    r=subprocess.run(['ngspice','-b',name+'.cir'],capture_output=True,text=True)
    if r.returncode: print(r.stdout[-1500:]); raise SystemExit(1)
    d=np.loadtxt(name+'.dat')
    t,vd,vg,vo,idd,idrv,vin,ifin=d[:,0],d[:,1],d[:,3],d[:,5],-d[:,7],-d[:,9],d[:,11],d[:,13]
    res,_=pa.analyze(t,vd,vg,vo,idd,idrv)
    # filter input power (all frequencies) over the same 100-cycle window
    t0=t[-1]-100*T; m=t>=t0
    tt=np.linspace(t0,t[-1],100*512,endpoint=False)
    pin=np.mean(np.interp(tt,t,vin)*np.interp(tt,t,ifin))
    res['P_filter_in']=pin; res['P_filter_loss']=pin-res['Pout_tot']
    res.update(C1_pF=c1*1e12,L2_uH=l2*1e6,name=name)
    return res
cases=[(285e-12,2.18e-6,'v2_as_drawn'),(260e-12,2.122e-6,'v2_trimmed')]
if __name__=='__main__':
    print('L3 as wound',L3,'RL3',w*L3/QL)
    with ProcessPoolExecutor(2) as ex: res=list(ex.map(lambda a: None, [])) if False else list(ex.map(run,*zip(*cases)))
    json.dump(res,open('results_v2.json','w'),indent=1,default=float)
    for r in res:
        print(f"{r['name']}: Pout1 {r['P1']:.3f} W, Pout_tot {r['Pout_tot']:.3f}, Pdc {r['Pdc']:.3f} W (Idc {1000*r['Idc']:.0f} mA), eta {100*r['eta1']:.2f}%, Vpk {r['vdpk']:.1f}, Von {r['v_turnon']:.2f}, Vmin {r['vdmin']:.2f}, Vg {r['vgpk']:.2f}/{r['vgmin']:.2f}, filt in {r['P_filter_in']:.3f} loss {1000*r['P_filter_loss']:.1f} mW ({100*r['P_filter_loss']/r['P_filter_in']:.2f}%), conv {r['P1']-r['P1_prev_window']:.1e}")
        print('   dBc', ' '.join(f"{k}:{r['dBc'][k]:.1f}" for k in range(2,11)))
