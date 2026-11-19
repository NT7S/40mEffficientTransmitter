import gzip
import json, numpy as np, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
res={}
# ---- PA supply sweep: Pout vs Vdd (trimmed + LPF); 12 V point from v2
sw=json.load(open('vsweep.json')); v2=json.load(open('../v2/results_v2.json'))[1]
V=[r['v'] for r in sw]+[12.0]; P=[r['P1'] for r in sw]+[v2['P1']]; I=[r['Idc'] for r in sw]+[v2['Idc']]
o=np.argsort(V); V=np.array(V)[o]; P=np.array(P)[o]; I=np.array(I)[o]
res['sweep']=[dict(V=float(a),P1_W=float(b),Idc_A=float(c),eta=float(b/(a*c)) if a>0 else None,R_dc=float(a/c) if a>0 else None) for a,b,c in zip(V,P,I)]
res['backwave_W']=float(P[0]); res['backwave_dBc']=float(10*np.log10(P[0]/P[-1])); res['backwave_dBm']=float(10*np.log10(P[0]/1e-3))
amp=lambda v: np.sqrt(np.interp(v,V,P)/P[-1])   # relative RF amplitude vs PA rail voltage
# ---- keying
fig,ax=plt.subplots(3,1,figsize=(9,8),sharex=True)
res['keying']={}
for c,col in [('10n','tab:gray'),('47n','tab:blue')]:
    d=np.loadtxt(gzip.open(f'key_{c}.dat.gz')); t=d[:,0]; key=d[:,1]; g=d[:,3]; vpa=d[:,5]; pq=d[:,7]
    a=amp(np.clip(vpa,0,12))
    def cr(y,lvl,start,up):
        m=t>start; i=np.where(y[m]>=lvl)[0][0] if up else np.where(y[m]<=lvl)[0][0]; return t[m][i]
    k={}
    k['rise_10_90_ms']=1e3*(cr(a,.9,1e-3,1)-cr(a,.1,1e-3,1)); k['delay_on_10_ms']=1e3*(cr(a,.1,1e-3,1)-1e-3)
    k['fall_90_10_ms']=1e3*(cr(a,.1,16e-3,0)-cr(a,.9,16e-3,0)); k['delay_off_90_ms']=1e3*(cr(a,.9,16e-3,0)-16e-3)
    m=(t>12e-3)&(t<15e-3); k['Vgs_on']=float(g[m].mean()-12); k['P_pmos_mW']=1e3*float(pq[m].mean()); k['Vpa_on']=float(vpa[m].mean())
    res['keying'][c]=k
    lab=f'C4 = {c}'+(' (OB2 value)' if c=='10n' else ' (rev C)')
    ax[0].plot(1e3*t,g-12,col,label=lab); ax[1].plot(1e3*t,vpa,col,label=lab); ax[2].plot(1e3*t,a,col,label=lab)
    if c=='47n':
        tt=np.linspace(0,30e-3,300000); vv=np.interp(tt,t,vpa)
        rf=amp(np.clip(vv,0,12))*np.sin(2*np.pi*tt/(30e-3/150))  # illustrative carrier, not to scale
ax[0].plot(1e3*t,key-0,'k:',lw=1,label='KEY (V)')
ax[0].set_ylabel('Vgs Q2 (V)'); ax[0].legend(fontsize=8); ax[0].grid(alpha=.3)
ax[1].set_ylabel('PA rail +12V_PA (V)'); ax[1].legend(fontsize=8); ax[1].grid(alpha=.3)
ax[2].set_ylabel('RF amplitude (rel.)'); ax[2].set_xlabel('time (ms)'); ax[2].legend(fontsize=8); ax[2].grid(alpha=.3)
ax[0].set_title('PMOS keying (OB2 topology, AO3407A fitted model), KEY high 1-16 ms\nRF envelope = sqrt(Pout(Vrail)/Pout(12 V)) from the PA supply sweep (trimmed variant + LPF)',fontsize=9)
plt.tight_layout(); plt.savefig('keying_v3.png',dpi=110); plt.close()
# ---- sweep plot
plt.figure(figsize=(6,4)); plt.plot(V,P,'o-',label='ngspice'); vv=np.linspace(0,12,50); plt.plot(vv,P[-1]*(vv/12)**2,'--',label='P(12 V) x (V/12)^2')
plt.xlabel('PA rail (V)'); plt.ylabel('P out at 50 ohm (W)'); plt.grid(alpha=.3); plt.legend(); plt.title('Class E output vs rail (trimmed + LPF)',fontsize=10)
plt.tight_layout(); plt.savefig('pout_vs_vdd_v3.png',dpi=110); plt.close()
# ---- oscillator
d=np.loadtxt(gzip.open('osc_v3.dat.gz')); t=d[:,0]; vc=d[:,1]; vin=d[:,3]; sch=d[:,5]; icc=d[:,7]; ix=d[:,9]
fig,ax=plt.subplots(3,1,figsize=(9,8))
ax[0].plot(1e3*t[::20],vc[::20],lw=.3); ax[0].set_xlabel('time (ms)'); ax[0].set_ylabel('Q4 collector (V)'); ax[0].set_title('Pierce start-up from power-up (crystal model is a placeholder; real start-up time differs)',fontsize=9); ax[0].grid(alpha=.3)
m=t>6.9993e-3
ax[1].plot(1e6*(t[m]-t[m][0]),vin[m],label='U1 input (after CK, bias 100k/91k)'); 
for y,yt_,s in [(3.33,3.33,'VT+ max (5.5 V)'),(2.19,2.3,'VT+ min (4.5 V)'),(1.97,1.85,'VT- max (4.5 V)'),(1.51,1.45,'VT- min (4.5 V)')]: ax[1].axhline(y,ls=':',lw=.8,color='r'); ax[1].text(0.71,yt_,s,fontsize=7,color='r',va='center')
ax[1].plot(1e6*(t[m]-t[m][0]),sch[m],label='U1 output (behavioral)'); ax[1].set_xlim(0,0.85); ax[1].set_xlabel('time (us)'); ax[1].set_ylabel('V'); ax[1].legend(fontsize=7,loc='upper right'); ax[1].grid(alpha=.3)
k=int(round((1/7.03e6)/(t[1]-t[0]))); ia=np.convolve(icc,np.ones(k)/k,'same'); ax[2].plot(1e3*t[::20],1e3*ia[::20],lw=.8); ax[2].set_ylabel('osc I from +5V, 1-cycle avg (mA)'); ax[2].set_xlabel('time (ms)'); ax[2].grid(alpha=.3); ax[2].set_ylim(0.6,1.2)
plt.tight_layout(); plt.savefig('osc_v3.png',dpi=110); plt.close()
mm=t>6.9e-3
up=t[1:][(sch[:-1]<2.5)&(sch[1:]>=2.5)&mm[1:]]; dn=t[1:][(sch[:-1]>=2.5)&(sch[1:]<2.5)&mm[1:]]
per=np.diff(up).mean(); hi=np.mean([dn[dn>u][0]-u for u in up[:-1]])
gaps=np.diff(t[1:][(sch[:-1]<2.5)&(sch[1:]>=2.5)]); allup=t[1:][(sch[:-1]<2.5)&(sch[1:]>=2.5)]; bad=np.where(gaps>1.5*per)[0]
res['osc']=dict(Icc_mA=1e3*icc[mm].mean(),P_mW=5e3*icc[mm].mean(),Vin_min=vin[mm].min(),Vin_max=vin[mm].max(),Vc_pp=np.ptp(vc[mm]),
  Ixtal_rms_mA=1e3*np.sqrt(np.mean(ix[mm]**2)),drive_uW=1e6*np.mean(ix[mm]**2)*20,f_Hz=1/per,duty=hi/per,
  clean_toggle_from_ms=1e3*allup[bad[-1]+1] if len(bad) else 1e3*allup[0])
# ---- whole transmitter (keyed down)
Pgate=0.016588; Pcpd=26e-12*25*7.03e6; Posc=res['osc']['P_mW']/1e3; eta_buck=0.85
P5=Pgate+Pcpd+Posc; Ppmos=res['keying']['47n']['P_pmos_mW']/1e3; Pdiv=12**2/44e3
Pin=v2['Pdc']+Ppmos+Pdiv+P5/eta_buck
res['tx']=dict(Pout=v2['P1'],Pdc_pa=v2['Pdc'],P_gate=Pgate,P_U1_cpd=Pcpd,P_osc=Posc,P_5V=P5,eta_buck_assumed=eta_buck,P_5V_from_12V=P5/eta_buck,P_pmos=Ppmos,P_gate_divider=Pdiv,P_in_12V=Pin,eta_total=v2['P1']/Pin,I_in=Pin/12,keyup_W=P5/eta_buck)
json.dump(res,open('results_v3.json','w'),indent=1,default=float)
print(json.dumps(res,indent=1,default=float))
