import numpy as np, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
F=7.030e6; T=1/F
plt.rcParams.update({'font.size':12,'axes.grid':True,'grid.alpha':0.35,'figure.facecolor':'white','axes.facecolor':'white','savefig.facecolor':'white'})
def load(fn):
    d=np.loadtxt(fn); return d[:,0],d[:,1],d[:,3],d[:,5],-d[:,7]
def spectrum(fn,ncyc=100,per=512):
    t,vd,vg,vo,idd=load(fn); t0=t[-1]-ncyc*T; M=ncyc*per
    tt=t0+np.arange(M)*(ncyc*T/M); v=np.interp(tt,t,vo)
    win=np.blackman(M); X=np.abs(np.fft.rfft(v*win)); f=np.fft.rfftfreq(M,tt[1]-tt[0])
    Xr=np.abs(np.fft.rfft(v)); h=np.array([Xr[k*ncyc] for k in range(1,11)])
    return f,20*np.log10(X/X[ncyc]+1e-12),20*np.log10(h/h[0])
fig,ax=plt.subplots(figsize=(11,6))
cases=[('pa40_c1_285_l2_2180.dat.gz','PA + tank + L-match only (no LPF)','tab:red'),
       ('palpf_ell38_c1_285_l2_2180.dat.gz','With 3-pole elliptic LPF (2f zero)','tab:blue')]
for i,(fn,lab,c) in enumerate(cases):
    f,S,h=spectrum(fn)
    ax.plot(f/1e6,S,color=c,lw=1.0,alpha=0.55)
    k=np.arange(2,11); ax.plot(k*F/1e6,h[1:],'o',color=c,ms=7,label=lab)
    for kk,hv in zip(k,h[1:]):
        if kk<=4: ax.annotate(f'{hv:.1f}',(kk*F/1e6,hv),textcoords='offset points',xytext=(8 if i==0 else 8,6 if i==0 else -14),color=c,fontsize=10)
ax.axhline(-43,color='k',ls='--',lw=1.5); ax.text(73,-41.5,'FCC §97.307(d): −43 dBc',ha='right',fontsize=11)
ax.axhline(-53,color='gray',ls=':',lw=1.5); ax.text(73,-51.5,'−53 dBc (−43 dBc with a 10 dB design margin)',ha='right',fontsize=10,color='dimgray')
ax.set_xlim(0,75); ax.set_ylim(-110,5); ax.set_xticks([k*F/1e6 for k in range(1,11)]); ax.set_xticklabels([f'{k}f\n{k*7.03:.1f}' for k in range(1,11)])
ax.set_xlabel('Frequency (MHz)'); ax.set_ylabel('Level relative to fundamental (dBc)')
ax.set_title('Simulated output spectrum into 50 Ω, 40 m GaN class E PA (ngspice, EPC2036 model)\nC1 285 pF, L2 2.18 µH; dots = harmonic levels, lines = Blackman-windowed FFT over 100 cycles')
ax.legend(loc='upper right',bbox_to_anchor=(1,0.93)); ax.text(73,-62,'Elliptic trap tuned to 14.06 MHz. With the trap L off by ±10 %,\n2f stays at −54 to −63 dBc in the same simulation.',ha='right',fontsize=10,color='tab:blue'); fig.tight_layout(); fig.savefig('spectrum.png',dpi=130)
# waveforms
fig,ax=plt.subplots(figsize=(11,6)); ax2=ax.twinx(); ax2.grid(False)
for fn,lab,c,ls in [('pa40_c1_285_l2_2180.dat.gz','Drain, C1 285 pF (schematic)','tab:red','-'),('pa40_c1_260_l2_2180.dat.gz','Drain, C1 260 pF','tab:orange','--')]:
    t,vd,vg,vo,idd=load(fn); m=t>=t[-1]-3*T; tt=(t[m]-t[m][0])*1e9
    ax.plot(tt,vd[m],color=c,ls=ls,lw=1.8,label=lab)
t,vd,vg,vo,idd=load('pa40_c1_285_l2_2180.dat.gz'); m=t>=t[-1]-3*T; tt=(t[m]-t[m][0])*1e9
ax2.plot(tt,vg[m],color='tab:blue',lw=1.5,label='Gate (EPC2036 gate pin)')
ax.set_ylim(-5,56); ax2.set_ylim(-1,12.3); ax.set_xlabel('Time (ns), last 3 cycles of 300'); ax.set_ylabel('Drain voltage (V)'); ax2.set_ylabel('Gate voltage (V)',color='tab:blue')
ax.axhline(42.7,color='gray',ls=':',lw=1.2); ax.text(2,44.0,'Page estimate: 42.7 V peak (Sokal eq. 3)',fontsize=10,color='dimgray')
h1,l1=ax.get_legend_handles_labels(); h2,l2=ax2.get_legend_handles_labels(); ax.legend(h1+h2,l1+l2,loc='upper center',ncol=3,fontsize=10.5)
ax.set_title('Simulated drain and gate voltage, 12.0 V, 7.030 MHz (ngspice, EPC2036 model)')
fig.tight_layout(); fig.savefig('waveforms.png',dpi=130)
