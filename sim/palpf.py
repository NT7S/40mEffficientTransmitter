import pa, lpf, json, numpy as np
from concurrent.futures import ProcessPoolExecutor
F=lpf.F; w=2*np.pi*F
def spice_lpf(net,Ql=320,Qc=1000):
    s=["* LPF: inductor Qu %d (series R at 7.03 MHz), capacitor Q %d (ESR at 7.03 MHz), 50 Ohm load"%(Ql,Qc)]
    node='out'; n=0
    for i,(k,e) in enumerate(net):
        if k=='C':
            s.append(f"CF{i} {node} cf{i} {e:.6e}\nRCF{i} cf{i} 0 {1/(w*e*Qc):.5f}")
        elif k=='L':
            nn=f'f{i}'; s.append(f"LF{i} {node} lf{i} {e:.6e}\nRLF{i} lf{i} {nn} {w*e/Ql:.5f}"); node=nn
        elif k=='T':
            L,C=e; nn=f'f{i}'
            s.append(f"LF{i} {node} lf{i} {L:.6e}\nRLF{i} lf{i} {nn} {w*L/Ql:.5f}\nCT{i} {node} ct{i} {C:.6e}\nRCT{i} ct{i} {nn} {1/(w*C*Qc):.5f}"); node=nn
    s.append(f"RLOAD {node} 0 50\nVSENSE {node} load 0\nRDUMMY load 0 1e12")
    return "\n".join(s)+"\n"
Os,Am,O2,c13,c2,l2=lpf.ZV[38]
nets={'ell38':lpf.cc03(c13,c2,l2,2*F/O2),'cheb5':lpf.ladder(lpf.G['cheb5_0.1'],8.5e6),'cheb3':lpf.ladder(lpf.G['cheb3_0.1'],8.5e6)}
cases=[('ell38',285e-12,2.18e-6),('cheb5',285e-12,2.18e-6),('cheb3',285e-12,2.18e-6),('ell38',260e-12,2.122e-6),('cheb5',260e-12,2.122e-6)]
def job(c):
    nm,c1,l2v=c
    name=f'palpf_{nm}_c1_{int(c1*1e12)}_l2_{int(l2v*1e9)}'
    out=pa.run(c1,300,lpf=spice_lpf(nets[nm]),name=name,l2=l2v)
    r,_=pa.analyze(*out); r.update(case=nm,C1_pF=c1*1e12,L2_uH=l2v*1e6); return r
if __name__=='__main__':
    with ProcessPoolExecutor(5) as ex: res=list(ex.map(job,cases))
    json.dump(res,open('palpf.json','w'),indent=1,default=float)
    for r in res: print(f"{r['case']} C1 {r['C1_pF']:.0f} L2 {r['L2_uH']:.3f}  Pload1 {r['P1']:.3f} Pdc {r['Pdc']:.3f} eta {100*r['eta1']:.2f}% Vpk {r['vdpk']:.1f} Von {r['v_turnon']:.2f} conv {r['P1']-r['P1_prev_window']:.1e} | "+" ".join(f"{r['dBc'][k]:.1f}" for k in range(2,11)))
