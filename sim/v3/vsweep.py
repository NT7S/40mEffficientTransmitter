# Class E output vs PA supply voltage (trimmed variant + elliptic LPF), to map the keyed supply ramp to the RF envelope.
import sys, json, subprocess, numpy as np
sys.path.insert(0,'..'); sys.path.insert(0,'../v2'); import pa, sim2
from concurrent.futures import ProcessPoolExecutor
T=pa.T
def run(v):
    name=f'vs_{v:g}V'
    s=pa.netlist(260e-12,300,sim2.LPF,name,0.441*v/12,2.122e-6)
    s=s.replace("linearize v(d) v(g) v(load) i(VDD) i(VDRV)\nwrdata "+name+".dat v(d) v(g) v(load) i(VDD) i(VDRV)",
                "linearize v(d) v(g) v(rf) i(VDD) i(VDRV)\nwrdata "+name+".dat v(d) v(g) v(rf) i(VDD) i(VDRV)")
    s=s.replace('VDD vdd_src 0 12.0',f'VDD vdd_src 0 {v}').replace('ic=12',f'ic={v}')
    s=s.replace('* 40 m 5 W','* PA supply sweep (keying envelope map), trimmed C1 260p L2 2.122u + LPF. 40 m 5 W')
    open(name+'.cir','w').write(s)
    r=subprocess.run(['ngspice','-b',name+'.cir'],capture_output=True,text=True)
    if r.returncode: return {'v':v,'err':r.stdout[-800:]}
    d=np.loadtxt(name+'.dat')
    t,vd,vg,vo,idd,idrv=d[:,0],d[:,1],d[:,3],d[:,5],-d[:,7],-d[:,9]
    res,_=pa.analyze(t,vd,vg,vo,idd,idrv)
    subprocess.run(['gzip','-f',name+'.dat'])
    res['v']=v; return res
if __name__=='__main__':
    vs=[0.0,3.0,6.0,9.0]
    with ProcessPoolExecutor(4) as ex: res=list(ex.map(run,vs))
    json.dump(res,open('vsweep.json','w'),indent=1,default=float)
    for r in res:
        if 'err' in r: print(r); continue
        print(f"V {r['v']}: P1 {r['P1']:.4g} W Pdc {r['Pdc']:.4g} Idc {r['Idc']*1e3:.1f} mA eta {100*r['eta1'] if r['Pdc']>0 else 0:.1f}% conv {r['P1']-r['P1_prev_window']:.1e}")
