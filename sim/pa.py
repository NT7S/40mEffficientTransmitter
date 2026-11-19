import subprocess, numpy as np, sys, json
F=7.030e6; T=1/F
def netlist(c1=285e-12, ncyc=500, lpf=None, name='pa40', il1=0.35, l2=2.18e-6):
    lpf_txt=''
    out='out'
    if lpf: lpf_txt=lpf; out='load'
    else: lpf_txt='RLOAD out 0 50\n'
    return f"""* 40 m 5 W single-ended GaN class E PA, tank + L-match (pa40-classe.kicad_sch rev A)
* Values from the schematic / Page; losses are estimates (see comments)
.include EPC2036_ngspice.lib
.param per={T}
* Supply 12.0 V, ideal source with 10 mOhm (estimate)
VDD vdd_src 0 12.0
RSRC vdd_src vdd 0.01
* C14/C15 decoupling at L1 cold end (placeholders), with 10 mOhm ESR (estimate)
C14 vdd c14 0.1u ic=12
RC14 c14 0 0.01
C15 vdd c15 10n ic=12
RC15 c15 0 0.01
* L1 FT-50-61 26t #24, 47 uH: copper 37 mOhm (7 mW at 0.434 A, Page), core Rp 277 kOhm at 7.03 MHz (Page)
L1 vdd l1m 47u ic={il1}
RL1 l1m d 0.037
RP1 vdd d 277k
* Q1 EPC2036 (EPC model)
XQ1 g d 0 EPC2036
* C1 shunt (external), ESR 20 mOhm (Page estimate for C0G)
C1 d c1m {c1}
RC1 c1m 0 0.02
* C2 series 424.5 pF, ESR 20 mOhm
C2 d c2m 424.5p ic=12
RC2 c2m n2 0.02
* L2 T-80-6 22t #16, 2.18 uH, Qu 330 at 7.03 MHz -> Rs = 0.292 Ohm (Page)
L2 n2 l2m {l2}
RL2 l2m out 0.292
* C3 731 pF shunt at 50 Ohm side, ESR 20 mOhm
C3 out c3m 731p
RC3 c3m 0 0.02
{lpf_txt}
* Gate drive: 74LVC1G17 at 5 V as ideal 0-5 V square, 1 ns edges, 7 Ohm output (estimate),
* R1 = 0 Ohm, 2 nH gate loop (estimate). 50 % duty.
VDRV drv 0 PULSE(0 5 0 1n 1n {{per/2-1n}} {{per}})
RDRV drv g1 7
LG g1 g 2n
.options reltol=1e-3 itl4=100 gmin=1e-12
.tran 0.05n {ncyc*T} 0 0.05n uic
.control
set filetype=ascii
run
linearize v(d) v(g) v({out}) i(VDD) i(VDRV)
wrdata {name}.dat v(d) v(g) v({out}) i(VDD) i(VDRV)
.endc
.end
"""
def run(c1=285e-12, ncyc=500, lpf=None, name='pa40', il1=0.35, l2=2.18e-6):
    open(name+'.cir','w').write(netlist(c1,ncyc,lpf,name,il1,l2))
    r=subprocess.run(['ngspice','-b',name+'.cir'],capture_output=True,text=True)
    if r.returncode: print(r.stdout[-2000:],r.stderr[-2000:]); sys.exit(1)
    d=np.loadtxt(name+'.dat')
    t=d[:,0]; vd=d[:,1]; vg=d[:,3]; vo=d[:,5]; idd=-d[:,7]; idrv=-d[:,9]
    return t,vd,vg,vo,idd,idrv
def analyze(t,vd,vg,vo,idd,idrv,ncyc_fft=100):
    dt=t[1]-t[0]; N=int(round(T/dt))
    # resample onto exact grid for integer cycles
    tend=t[-1]; t0=tend-ncyc_fft*T
    M=ncyc_fft*512
    tt=t0+np.arange(M)*(ncyc_fft*T/M)
    v=np.interp(tt,t,vo); i_=np.interp(tt,t,idd); d_=np.interp(tt,t,vd); g_=np.interp(tt,t,vg); ir=np.interp(tt,t,idrv)
    X=np.fft.rfft(v)/M*2
    h={k:abs(X[k*ncyc_fft]) for k in range(1,11)}
    P1=h[1]**2/2/50
    Pdc=12.0*i_.mean()
    Pout_tot=np.mean(v**2)/50
    # turn-on: gate crossing 1.5 V rising, look up drain V
    vs=[];
    idx=np.where((g_[:-1]<1.5)&(g_[1:]>=1.5))[0]
    vs=d_[idx]
    Pdrv=5.0*0  # driver power: ideal source power delivered
    Pgate=np.mean(np.interp(tt,t,vg)*0)
    res=dict(P1=P1,Pout_tot=Pout_tot,Pdc=Pdc,eta1=P1/Pdc,eta_tot=Pout_tot/Pdc,
             vdpk=d_.max(),vdmin=d_.min(),v_turnon=float(np.mean(vs)),vgpk=g_.max(),vgmin=g_.min(),
             Idc=i_.mean(), dBc={k:20*np.log10(h[k]/h[1]) for k in range(2,11)})
    # convergence: P1 and Idc in the previous window of the same length
    t0b=t0-ncyc_fft*T; ttb=t0b+np.arange(M)*(ncyc_fft*T/M)
    vb=np.interp(ttb,t,vo); Xb=np.fft.rfft(vb)/M*2
    res['P1_prev_window']=abs(Xb[ncyc_fft])**2/100; res['Idc_prev_window']=np.interp(ttb,t,idd).mean()
    return res,(tt,v,d_,g_)
if __name__=='__main__':
    c1=float(sys.argv[1]) if len(sys.argv)>1 else 285e-12
    ncyc=int(sys.argv[2]) if len(sys.argv)>2 else 500
    out=run(c1,ncyc,name=f'pa40_c1_{int(c1*1e12)}')
    res,_=analyze(*out)
    print(json.dumps(res,indent=1,default=float))
