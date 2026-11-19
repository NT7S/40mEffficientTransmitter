import json, numpy as np, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
B=json.load(open('../../report/budget.json'))
R=json.load(open('results_r1.json'))+json.load(open('results_stress.json'))+json.load(open('results_clamp.json'))+json.load(open('results_clamp5.json'))
const=B['pu1']+B['posc']
def tot(r):
    p5=r['P_drv_src']+const; pin=r['Pdc']+p5/0.87+B['pmos']+B['pdiv']+B['r12']
    return r['P1']/pin, pin
base=[r for r in R if r['name']=='g_r0_l2_none'][0]; eb,_=tot(base)
rows=[]
for r in R:
    e,pin=tot(r)
    rows.append(dict(name=r['name'],R1=r['R1'],L=r['LG_nH'],clamp=r['clamp'],P1=r['P1'],Pdc=r['Pdc'],eta_d=r['eta1'],eta_tot=e,pts_tot=100*(e-eb),pts_d=100*(r['eta1']-base['eta1']),
        vgmax=r['vg_pad_max'],vgmin=r['vg_pad_min'],vgimax=r['vg_int_max'],vgimin=r['vg_int_min'],I5=r['I_5V_gate'],Pcl=r['P_clamp'],Pin=pin,von=r['v_turnon']))
json.dump(dict(baseline='g_r0_l2_none',eta_tot_base=eb,rows=rows),open('summary_v5.json','w'),indent=1)
for x in rows: print(f"{x['name']:24s} {x['P1']:.3f} W  eta_d {100*x['eta_d']:.2f} ({x['pts_d']:+.3f})  eta_tot {100*x['eta_tot']:.2f} ({x['pts_tot']:+.3f})  vg {x['vgmax']:.2f}/{x['vgmin']:.2f}  I5 {1000*x['I5']:.2f} mA Pcl {1000*x['Pcl']:.2f}")
# plots
def W(n): return np.load(n+'_wave.npz')
fig,ax=plt.subplots(1,3,figsize=(15,4.2),sharey=True)
for n,lab in (('g_r0_l2_none','R1 0 Ω'),('g_r2p2_l2_none','R1 2.2 Ω'),('g_r10_l2_none','R1 10 Ω')):
    w=W(n); ax[0].plot(w['t']*1e9,w['vg'],label=lab)
ax[0].set_title('Gate pad, 2 nH loop (assumed)')
for n,lab in (('g_r0_l5_none','R1 0 Ω'),('g_r1_l5_none','R1 1 Ω'),('g_r2p2_l5_none','R1 2.2 Ω'),('g_r4p7_l5_none','R1 4.7 Ω')):
    w=W(n); ax[1].plot(w['t']*1e9,w['vg'],label=lab)
ax[1].set_title('Gate pad, 5 nH stress loop')
for n,lab in (('g_r0_l5_none','no clamp'),('g_r0p0_l5_bat54','BAT54W'),('g_r0p0_l5_z5v6','BZX84C5V6'),('g_r0p0_l5_z6v2','BZX84C6V2'),('g_r0p0_l5_bat54_z6v2','BAT54W + BZX84C6V2')):
    w=W(n); ax[2].plot(w['t']*1e9,w['vg'],label=lab)
ax[2].set_title('Clamps, R1 0 Ω, 5 nH stress loop')
for a in ax:
    a.axhline(6,color='r',ls='--',lw=0.8); a.text(1,6.05,'6 V abs. max',color='r',fontsize=8)
    a.set_xlabel('time (ns)'); a.grid(alpha=.3); a.legend(fontsize=8,loc='center right'); a.set_xlim(0,3/7.03e6*1e9)
ax[0].set_ylabel('V(gate pad to source) (V)'); ax[0].set_ylim(-1,6.5)
plt.tight_layout(); plt.savefig('gate_v5.png',dpi=130)
# zoomed edges
fig,ax=plt.subplots(1,2,figsize=(12,4))
T=1/7.03e6*1e9
for n,lab in (('g_r0_l2_none','2 nH, R1 0'),('g_r0_l5_none','5 nH, R1 0'),('g_r2p2_l5_none','5 nH, R1 2.2 Ω'),('g_r0p0_l5_z5v6','5 nH, R1 0, BZX84C5V6'),('g_r0p0_l5_bat54','5 nH, R1 0, BAT54W')):
    w=W(n); t=w['t']*1e9
    ax[0].plot(t,w['vg'],label=lab); ax[1].plot(t,w['vg'],label=lab)
ax[0].set_xlim(-1,25); ax[0].set_title('Rising edge'); ax[1].set_xlim(T/2-1,T/2+25); ax[1].set_title('Falling edge')
for a in ax: a.grid(alpha=.3); a.set_xlabel('time (ns)'); a.axhline(6,color='r',ls='--',lw=0.8)
ax[0].set_ylabel('V (V)'); ax[0].legend(fontsize=8); ax[1].set_ylim(-1,1.5); ax[0].set_ylim(3,6.5)
plt.tight_layout(); plt.savefig('gate_edges_v5.png',dpi=130)
