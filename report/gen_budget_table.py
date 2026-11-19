# Writes budget_table.tex from budget.json (produced by gen_tables.py).
import json
d=json.load(open('budget.json'))
mw=lambda x: f"{x*1000:.1f}"
rows=[
("RF output at J2", f"{d['pout']:.3f}", "W", "Trimmed PA + LPF run"),
("PA rail input (drain, L1, tank, LPF)", f"{d['pdc_pa']:.3f}", "W", "Same run"),
("\\quad of which: LPF loss", mw(d['pfilt_loss']), "mW", "Power into C16 node minus power at J2"),
("\\quad of which: Q1, L1, tank and L-match loss", mw(d['pa_loss']), "mW", "PA rail input minus LPF input"),
("Q2 keying switch", mw(d['pmos']), "mW", "Keying run, fitted model"),
("R2 + R3 divider while keyed", mw(d['pdiv']), "mW", "$12^2/\\SI{44}{\\kilo\\ohm}$"),
("5\\,V loads from 12\\,V via buck", mw(d['p5in']), "mW", f"{mw(d['p5'])} mW / 0.87 (buck loss {mw(d['buck_loss'])} mW)"),
("\\quad 5\\,V load: Q1 gate drive", mw(d['pgate']), "mW", "Trimmed run, ideal driver"),
("\\quad 5\\,V load: U1 internal", mw(d['pu1']), "mW", "$C_{pd}$ \\SI{26}{\\pico\\farad} $\\times 5^2 \\times f$"),
("\\quad 5\\,V load: oscillator", mw(d['posc']), "mW", "Oscillator run"),
("R12 shunt (if fitted)", mw(d['r12']), "mW", "\\SI{444.5}{\\milli\\ampere}$^2\\times$\\SI{10}{\\milli\\ohm}"),
]
out=["\\begin{table}[h]\\centering\\small","\\caption{Key-down power budget at \\SI{12.0}{\\volt} (simulated and estimated) \\cite{projsim,projnotes,tiTPS62175}.}\\label{tab:budget}",
"\\begin{tabularx}{\\textwidth}{@{}Yrl L{5.6cm}@{}}","\\toprule Item & Power & Unit & Basis \\\\ \\midrule"]
out+=[" & ".join(r)+" \\\\" for r in rows]
out+=["\\midrule",
f"\\textbf{{Total from 12.0\\,V}} & \\textbf{{{d['pin']:.3f}}} & W & {d['iin']*1000:.1f}\\,mA \\\\",
f"Drain efficiency (PA + LPF) & {d['eta_drain']*100:.1f} & \\% & Trimmed run \\\\",
f"\\textbf{{Whole-transmitter efficiency}} & \\textbf{{{d['eta']*100:.1f}}} & \\% & RF out / total in \\\\",
"Key-up draw & about 30 & mW & About \\SI{2.5}{\\milli\\ampere}; oscillator, U1, gate drive running (estimate) \\\\",
"\\bottomrule\\end{tabularx}\\end{table}"]
open('budget_table.tex','w').write("\n".join(out)+"\n")
