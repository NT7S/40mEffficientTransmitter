import pa, lpf, palpf, json
from concurrent.futures import ProcessPoolExecutor
def job(k):
    net=[list(x) for x in palpf.nets['ell38']]; L,C=net[1][1]; net[1]=('T',(L*k,C)); net=[tuple(x) for x in net]
    out=pa.run(285e-12,300,lpf=palpf.spice_lpf(net),name=f'palpf_ell38_trapL_{int(k*100)}',l2=2.18e-6)
    r,_=pa.analyze(*out); r['trapL_factor']=k; return r
if __name__=='__main__':
    with ProcessPoolExecutor(4) as ex: res=list(ex.map(job,(0.95,1.05,0.90,1.10)))
    json.dump(res,open('tol.json','w'),indent=1,default=float)
    for r in res: print(r['trapL_factor'],f"P {r['P1']:.3f} eta {100*r['eta1']:.2f}", " ".join(f"{r['dBc'][k]:.1f}" for k in range(2,11)))
