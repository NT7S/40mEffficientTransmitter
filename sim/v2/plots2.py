import numpy as np, json, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
F=7.030e6; T=1/F
plt.rcParams.update({'font.size':12,'axes.grid':True,'grid.alpha':0.35,'figure.facecolor':'white','axes.facecolor':'white','savefig.facecolor':'white'})
R={r['name']:r for r in json.load(open('results_v2.json'))}
def load(fn):
    d=np.loadtxt(fn); return d[:,0],d[:,1],d[:,3],d[:,5]
def spec(fn,ncyc=100,per=512):
    t,vd,vg,vo=load(fn); t0=t[-1]-ncyc*T; M=ncyc*per; tt=t0+np.arange(M)*(ncyc*T/M); v=np.interp(tt,t,vo)
    X=np.abs(np.fft.rfft(v*np.blackman(M))); f=np.fft.rfftfreq(M,tt[1]-tt[0]); return f,20*np.log10(X/X[ncyc]+1e-12)
V=[('v2_as_drawn','As drawn: C1 285 pF, L2 2.18 µH','tab:red',(8,6)),('v2_trimmed','Trimmed: C1 260 pF, L2 2.122 µH','tab:blue',(8,-14))]
fig,ax=plt.subplots(figsize=(11,6))
for nm,lab,c,off in V:
    f,S=spec(nm+'.dat.gz'); r=R[nm]; k=np.arange(2,11); h=[r['dBc'][str(i)] for i in k]
    ax.plot(f/1e6,S,color=c,lw=1.0,alpha=0.5)
    ax.plot(k*F/1e6,h,'o',color=c,ms=7,label=f"{lab} ({r['P1']:.2f} W)")
    for kk,hv in zip(k[:3],h[:3]): ax.annotate(f'{hv:.1f}',(kk*F/1e6,hv),textcoords='offset points',xytext=off,color=c,fontsize=10)
ax.axhline(-43,color='k',ls='--',lw=1.5); ax.text(73,-41.5,'FCC §97.307(d): −43 dBc',ha='right',fontsize=11)
ax.axhline(-53,color='gray',ls=':',lw=1.5); ax.text(73,-51.5,'−53 dBc (10 dB design margin)',ha='right',fontsize=10,color='dimgray')
ax.set_xlim(0,75); ax.set_ylim(-110,5); ax.set_xticks([k*F/1e6 for k in range(1,11)]); ax.set_xticklabels([f'{k}f\n{k*7.03:.1f}' for k in range(1,11)])
ax.set_xlabel('Frequency (MHz)'); ax.set_ylabel('Level relative to fundamental (dBc)')
ax.set_title('Simulated spectrum at J2 (50 Ω), PA + 3-pole elliptic LPF as drawn (ngspice, EPC2036 model)\nLPF 270 pF, 13 t T-80-6 (0.76 µH, Qu 320) || 168 pF, 270 pF. Dots: harmonics; lines: windowed FFT')
ax.legend(loc='upper right',bbox_to_anchor=(1,0.93)); fig.tight_layout(); fig.savefig('spectrum_v2.png',dpi=130)
fig,ax=plt.subplots(figsize=(11,6)); ax2=ax.twinx(); ax2.grid(False)
for nm,lab,c,off in V:
    t,vd,vg,vo=load(nm+'.dat.gz'); m=t>=t[-1]-3*T; tt=(t[m]-t[m][0])*1e9
    ax.plot(tt,vd[m],color=c,lw=1.8,ls='-' if nm.endswith('drawn') else '--',label='Drain, '+lab)
t,vd,vg,vo=load('v2_as_drawn.dat.gz'); m=t>=t[-1]-3*T; tt=(t[m]-t[m][0])*1e9
ax2.plot(tt,vg[m],color='tab:green',lw=1.5,label='Gate (as drawn)')
ax.set_ylim(-5,56); ax2.set_ylim(-1,12.3); ax.set_xlabel('Time (ns), last 3 cycles of 300'); ax.set_ylabel('Drain voltage (V)'); ax2.set_ylabel('Gate voltage (V)',color='tab:green')
ax.axhline(42.7,color='gray',ls=':',lw=1.2); ax.text(2,44.0,'Page estimate: 42.7 V peak (Sokal eq. 3)',fontsize=10,color='dimgray')
h1,l1=ax.get_legend_handles_labels(); h2,l2=ax2.get_legend_handles_labels(); ax.legend(h1+h2,l1+l2,loc='upper center',ncol=2,fontsize=10.5)
ax.set_title('Simulated drain and gate voltage with the LPF, 12.0 V, 7.030 MHz (ngspice, EPC2036 model)')
fig.tight_layout(); fig.savefig('waveforms_v2.png',dpi=130)
