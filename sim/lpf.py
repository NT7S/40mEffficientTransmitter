import numpy as np, json
R0=50.0; F=7.030e6
QL_T80=320; QL_T106=370; QC=1000   # Page estimates (LPF inductor table; C Q 1000)
def Zc(C,w,Q=QC): return 1/(1j*w*C)+1/(w*C*Q)          # series ESR model
def Zl(L,w,Q): return 1j*w*L+w*L/Q
def abcd_shunt(Z): return np.array([[1,0],[1/Z,1]],complex)
def abcd_series(Z): return np.array([[1,Z],[0,1]],complex)
def response(net,f,Ql):
    w=2*np.pi*f; M=np.eye(2,dtype=complex)
    for kind,el in net:
        if kind=='C': M=M@abcd_shunt(Zc(el,w))
        elif kind=='L': M=M@abcd_series(Zl(el,w,Ql))
        elif kind=='T':  # series trap L || C
            L,C=el; Z=1/(1/Zl(L,w,Ql)+1/Zc(C,w)); M=M@abcd_series(Z)
    A,B,Cc,D=M.ravel()
    s21=2/(A+B/R0+Cc*R0+D)
    Zin=(A*R0+B)/(Cc*R0+D); s11=(Zin-R0)/(Zin+R0)
    return s21,s11
def ladder(g,fc,first='C'):
    wc=2*np.pi*fc; net=[]; k=first
    for gi in g:
        net.append(('C',gi/(R0*wc)) if k=='C' else ('L',gi*R0/wc)); k='L' if k=='C' else 'C'
    return net
def cc03(c13,c2,l2,fc):
    wc=2*np.pi*fc
    return [('C',c13/(R0*wc)),('T',(l2*R0/wc,c2/(R0*wc))),('C',c13/(R0*wc))]
# EMRFD Table 3.1 p.3.5 (0.1 dB Chebyshev), no errata listed for Table 3.1
G={'cheb3_0.1':[1.032,1.147,1.032],'cheb5_0.1':[1.147,1.371,1.975,1.371,1.147],'cheb7_0.1':[1.18,1.423,2.097,1.573,2.097,1.423,1.18]}
# Zverev 1967 p.175 (PDF 186), CC03 rho=10%, K2=1: theta: (Omega_s, Amin, Omega2, C1=C3, C2, L2)
ZV={36:(1.7013,15.45,1.9165,0.6570,0.3536,0.7701),38:(1.6243,13.98,1.8245,0.6354,0.4095,0.7335),40:(1.5557,12.59,1.7423,0.6129,0.4737,0.6955)}
def designs():
    d={}
    d['3-pole 0.1 dB Chebyshev, fc 8.5 MHz']=ladder(G['cheb3_0.1'],8.5e6)
    d['5-pole 0.1 dB Chebyshev, fc 8.5 MHz (Page)']=ladder(G['cheb5_0.1'],8.5e6)
    d['7-pole 0.1 dB Chebyshev, fc 8.5 MHz (Page)']=ladder(G['cheb7_0.1'],8.5e6)
    for th,(Os,Am,O2,c13,c2,l2) in ZV.items():
        fc=2*F/O2   # place the zero exactly on 2f
        d[f'3-pole elliptic CC03 rho10% theta{th}, zero at 14.06 MHz (fc {fc/1e6:.2f} MHz)']=cc03(c13,c2,l2,fc)
    return d
def summarize(net,Ql):
    out={}
    s21,s11=response(net,F,Ql)
    out['IL_dB']=-20*np.log10(abs(s21)); out['diss_pct']=100*(1-abs(s21)**2-abs(s11)**2); out['RL_dB']=-20*np.log10(abs(s11))
    for k in range(2,11):
        s,_=response(net,k*F,Ql); out[f'A{k}']=-20*np.log10(abs(s))
    s,_=response(net,7.3e6,Ql); out['IL_7.3']=-20*np.log10(abs(s))
    s,_=response(net,7.0e6,Ql); out['IL_7.0']=-20*np.log10(abs(s))
    return out
if __name__=='__main__':
    res={}
    for name,net in designs().items():
        r=summarize(net,QL_T80); r106=summarize(net,QL_T106)
        r['diss_pct_T106']=r106['diss_pct']
        r['elements']=[(k,e) for k,e in net]
        res[name]=r
        print(f"{name}\n  IL {r['IL_dB']:.3f} dB diss {r['diss_pct']:.2f}% (T106 {r106['diss_pct']:.2f}%) RL {r['RL_dB']:.1f} dB IL7.0/7.3 {r['IL_7.0']:.3f}/{r['IL_7.3']:.3f}  A2..A5 "+" ".join(f"{r[f'A{k}']:.1f}" for k in range(2,6))+"  A6..10 "+" ".join(f"{r[f'A{k}']:.1f}" for k in range(6,11)))
        print("  ",[(k,(tuple(f'{x*1e9 if x>1e-8 else x*1e12:.1f}' for x in e) if isinstance(e,tuple) else (f'{e*1e6:.3f}uH' if k=='L' else f'{e*1e12:.0f}pF'))) for k,e in net])
    json.dump(res,open('lpf_options.json','w'),indent=1,default=lambda x: str(x))
