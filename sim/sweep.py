import json, sys
from concurrent.futures import ProcessPoolExecutor
import pa
def job(a):
    c1,l2=a
    out=pa.run(c1,300,name=f'pa40_c1_{int(c1*1e12)}_l2_{int(l2*1e9)}',l2=l2)
    r,_=pa.analyze(*out); r['C1_pF']=c1*1e12; r['L2_uH']=l2*1e6; return r
cases=[(c,2.18e-6) for c in (260e-12,285e-12,310e-12)]+[(285e-12,2.122e-6),(260e-12,2.122e-6),(310e-12,2.122e-6)]
with ProcessPoolExecutor(6) as ex: res=list(ex.map(job,cases))
json.dump(res,open('sweep.json','w'),indent=1,default=float)
for r in res: print(f"C1 {r['C1_pF']:.0f} L2 {r['L2_uH']:.3f}  P1 {r['P1']:.3f} Pdc {r['Pdc']:.3f} eta {100*r['eta1']:.2f}% Vpk {r['vdpk']:.1f} Von {r['v_turnon']:.2f} Vmin {r['vdmin']:.2f} H2 {r['dBc'][2]:.1f} H3 {r['dBc'][3]:.1f} conv {r['P1']-r['P1_prev_window']:.1e}")
