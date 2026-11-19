# Writes gate_r1_table.tex and gate_clamp_table.tex from ../sim/v5/summary_v5.json and clamp_dc.json
import json
S=json.load(open('../sim/v5/summary_v5.json')); D=json.load(open('../sim/v5/clamp_dc.json'))
R={r['name']:r for r in S['rows']}
def fr(x): return f"{x:g}"
def row(r,first):
    return (f"{first} & {r['P1']:.3f} & {100*r['eta_d']:.2f} & {100*r['eta_tot']:.2f} & {r['pts_tot']:+.3f} & "
            f"{r['vgmax']:.2f} & {r['vgmin']:.2f} & {1000*r['I5']:.2f} \\\\")
o=[r"\begin{table}[p]\centering\footnotesize\setlength{\tabcolsep}{3.5pt}",
r"\caption{Gate R1 and gate-loop inductance sweep, trimmed PA + LPF at \SI{12.0}{\volt}\simv. Driver as before: ideal 0--5\,V, 1\,ns edges, \SI{7}{\ohm} output (estimate). Loop L is assumed and lumped between R1 and the Q1 gate pad; 5\,nH is a stress case. Whole-transmitter efficiency uses the Table~\ref{tab:budget} overheads with the simulated gate-drive power; $\Delta$ is in percentage points against R1 \SI{0}{\ohm}, 2\,nH (the earlier baseline) \cite{projsim}.}\label{tab:gate-r1}",
r"\begin{tabular}{@{}llrrrrrrr@{}}\toprule",
r"Loop L & R1 ($\Omega$) & $P_{out}$ (W) & $\eta_D$ (\%) & $\eta_{tot}$ (\%) & $\Delta\eta_{tot}$ (pts) & $V_{g,max}$ (V) & $V_{g,min}$ (V) & $I_{5V,gate}$ (mA) \\ \midrule"]
for L in (0,1,2,5):
    for i,r1 in enumerate((0,1,2.2,3.3,4.7,10)):
        n=f"g_r{fr(r1)}_l{L}_none".replace('.','p')
        o.append(("\\multirow{6}{*}{"+(f"{L}\\,nH" if L<5 else "5\\,nH (stress)")+"} " if i==0 else "")+" & "+row(R[n],fr(r1)))
    o.append(r"\midrule" if L<5 else r"\bottomrule")
o.append(r"\end{tabular}\end{table}")
open('gate_r1_table.tex','w').write("\n".join(o)+"\n")
lab={'none':'none','bat54':'BAT54W','z5v6':'BZX84C5V6','z6v2':'BZX84C6V2','bat54+z5v6':'BAT54W + C5V6','bat54+z6v2':'BAT54W + C6V2'}
o=[r"\begin{table}[tbp]\centering\footnotesize\setlength{\tabcolsep}{3.5pt}",
r"\caption{Gate-source clamps at the Q1 gate pad (Diodes Inc. models \cite{diodesSpice}), trimmed PA + LPF\simv. Columns as Table~\ref{tab:gate-r1}; $P_{cl}$ is the power dissipated in the clamp model \cite{projsim}.}\label{tab:gate-clamp}",
r"\begin{tabular}{@{}lllrrrrrr@{}}\toprule",
r"Loop L & R1 ($\Omega$) & Clamp & $\eta_{tot}$ (\%) & $\Delta\eta_{tot}$ (pts) & $V_{g,max}$ (V) & $V_{g,min}$ (V) & $I_{5V,gate}$ (mA) & $P_{cl}$ (mW) \\ \midrule"]
for L,r1 in ((2,0),(2,2.2),(5,0)):
    names=[f"g_r{fr(r1)}_l{L}_none".replace('.','p')]+[f"g_r{r1:.1f}_l{L}_{c}".replace('.','p').replace('+','_') for c in ('bat54','z5v6','z6v2','bat54+z5v6','bat54+z6v2')]
    cl=['none','bat54','z5v6','z6v2','bat54+z5v6','bat54+z6v2']
    for i,(n,c) in enumerate(zip(names,cl)):
        r=R[n]
        o.append((f"{L}\\,nH" if i==0 else "")+" & "+(fr(r1) if i==0 else "")+f" & {lab[c]} & {100*r['eta_tot']:.2f} & {r['pts_tot']:+.3f} & {r['vgmax']:.2f} & {r['vgmin']:.2f} & {1000*r['I5']:.2f} & {1000*r['Pcl']:.2f} \\\\")
    o.append(r"\midrule" if (L,r1)!=(5,0) else r"\bottomrule")
o.append(r"\end{tabular}\end{table}")
z5,z6,b=D['z5v6'],D['z6v2'],D['bat54']
o+=[r"\begin{table}[tbp]\centering\small",
r"\caption{Clamp DC behaviour: model (ngspice DC sweep of the Diodes Inc. models \cite{diodesSpice}) against the onsemi datasheet limits \cite{onsemiBZX84,onsemiBAT54}. The EPC2036 gate is rated \SI{6}{\volt} / \SI{-4}{\volt}, with up to \SI{0.9}{\milli\ampere} forward gate leakage at \SI{5}{\volt} \cite{epc2036ds}.}\label{tab:clamp-dc}",
r"\begin{tabularx}{\textwidth}{@{}L{3.6cm}L{2.7cm}L{2.7cm}Y@{}}\toprule",
r"Quantity & BZX84C5V6 & BZX84C6V2 & BAT54 \\ \midrule",
f"Leakage at \\SI{{5.0}}{{\\volt}}, model & \\SI{{{z5['I_at_5V_uA']:.1f}}}{{\\micro\\ampere}} & \\SI{{{z6['I_at_5V_uA']*1000:.2f}}}{{\\nano\\ampere}} & \\SI{{{b['I_at_5V_uA']:.1f}}}{{\\micro\\ampere}} (equal to the model's IS; an artefact) \\\\",
r"Leakage, datasheet max & \SI{1}{\micro\ampere} at \SI{2}{\volt} & \SI{3}{\micro\ampere} at \SI{4}{\volt} & \SI{2}{\micro\ampere} at \SI{25}{\volt} \\",
f"Clamp voltage at 1 / 5 / 20\\,mA, model & {z5['V_at_1mA']:.2f} / {z5['V_at_5mA']:.2f} / {z5['V_at_20mA']:.2f}\\,V & {z6['V_at_1mA']:.2f} / {z6['V_at_5mA']:.2f} / {z6['V_at_20mA']:.2f}\\,V & -- \\\\",
r"$V_Z$ datasheet (min--max) at 1 / 5 / 20\,mA & 4.8--6.0 / 5.2--6.0 / 5.2--6.3\,V & 5.6--6.6 / 5.8--6.6 / 5.8--6.8\,V & -- \\",
f"Forward voltage at \\SI{{10}}{{\\milli\\ampere}}, model & {z5['Vf_at_10mA']:.2f}\\,V & {z6['Vf_at_10mA']:.2f}\\,V & {b['Vf_at_10mA']:.2f}\\,V (datasheet 0.35 typ, 0.40 max) \\\\",
r"Capacitance & model CJO \SI{57.6}{\pico\farad}; datasheet \SI{200}{\pico\farad} at \SI{0}{\volt} & model CJO \SI{49.4}{\pico\farad}; datasheet \SI{185}{\pico\farad} at \SI{0}{\volt} & model CJO \SI{13.3}{\pico\farad}; datasheet 7.6 typ, \SI{10}{\pico\farad} max at \SI{1}{\volt} \\",
r"\bottomrule\end{tabularx}\end{table}"]
open('gate_clamp_table.tex','w').write("\n".join(o)+"\n")
print('ok')
import re
for f in ('gate_r1_table.tex','gate_clamp_table.tex'):
    t=open(f).read(); t=re.sub(r' & -(?=\d)',' & $-$',t); open(f,'w').write(t)
