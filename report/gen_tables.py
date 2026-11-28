import re
"""Generate LaTeX tables from project data files (no hand-typed numbers)."""
import csv, json
def esc(s):
    rep={'\\':r'\textbackslash{}','&':r'\&','%':r'\%','$':r'\$','#':r'\#','_':r'\_','{':r'\{','}':r'\}','~':r'\textasciitilde{}','^':r'\^{}'}
    s=''.join(rep.get(c,c) for c in s)
    return s.replace('Ω',r'\ensuremath{\Omega}').replace('µ',r'\ensuremath{\mu}').replace('±',r'\ensuremath{\pm}').replace('×',r'\ensuremath{\times}').replace('–','--').replace('≈',r'\ensuremath{\approx}')
rows=list(csv.reader(open('../bom/bom-digikey-rev7.csv')))
hdr,body=rows[0],rows[1:]
out=[r'\begin{longtable}{@{}p{1.8cm}r >{\raggedright\arraybackslash}p{2.3cm} >{\raggedright\arraybackslash}p{1.9cm} p{3.7cm} p{4.4cm} r r >{\raggedright\arraybackslash}p{3.9cm}@{}}',
 "\\caption{DigiKey bill of materials, rev 7, generated from \\texttt{bom-digikey-rev7.csv}. Quantity-0 lines are copper pads or DNP footprints. Unit prices at quantity 1 in USD from the DigiKey US API on 18 Nov 2026. Y1 is not a DigiKey part and is excluded from the total. Check prices and stock in the cart before ordering.}\\label{tab:bom}\\\\",
 r'\toprule Refs & Qty & Value & Mfr & MPN & DigiKey PN & Unit & Ext & Note\\ \midrule\endfirsthead',
 r'\toprule Refs & Qty & Value & Mfr & MPN & DigiKey PN & Unit & Ext & Note\\ \midrule\endhead',
 r'\midrule\multicolumn{9}{r}{\emph{continued}}\\\endfoot\bottomrule\endlastfoot']
for r in body:
    refs,qty,val,pkg,mfr,mpn,dk,stock,unit,ext,via,note=(r+['']*12)[:12]
    if refs=='TOTAL':
        out.append(r'\midrule \multicolumn{7}{@{}l}{\textbf{Total, DigiKey parts, quantity-1 prices}} & \textbf{'+ext+r'} & '+esc(note)+r'\\ \midrule'); continue
    if not via:
        v=''
    elif via.startswith('web'):
        v='search'
    elif via.startswith('theparts'):
        v='aggreg.'
    elif 'Jason' in via or via.startswith('DigiKey US'):
        v=None  # already a complete source phrase; append via as-is
        src=via
    else:
        v='DK page'
    n=esc(note)
    if v:
        n=(n+'; ' if n else '')+'via '+v
    elif v is None:
        n=(n+'; ' if n else '')+esc(src)
    out.append(' & '.join([re.sub(r',(?=\S)',', ',esc(refs)),esc(qty),esc(val),esc(mfr),esc(mpn),r'\texttt{\footnotesize '+esc(dk)+'}',esc(unit),esc(ext),n.replace(r'\_',r'\_\allowbreak{}')])+r'\\')
out.append(r'\end{longtable}')
open('bom_table.tex','w').write('\n'.join(out)+'\n')

r3=json.load(open('../sim/v3/results_v3.json'))['tx']
v2=json.load(open('../sim/v2/results_v2.json'))
tr=[x for x in v2 if x['name']=='v2_trimmed'][0]
eta_buck=0.87   # read off TI SLVSB35C Fig. 9 (Page, rev 5)
p5=r3['P_5V']; p5in=p5/eta_buck
R12=0.0020
pin=r3['Pdc_pa']+p5in+r3['P_pmos']+r3['P_gate_divider']+R12
d=dict(pout=r3['Pout'],pdc_pa=r3['Pdc_pa'],pfilt_in=tr['P_filter_in'],pfilt_loss=tr['P_filter_loss'],
       pa_loss=r3['Pdc_pa']-tr['P_filter_in'],pgate=r3['P_gate'],pu1=r3['P_U1_cpd'],posc=r3['P_osc'],p5=p5,p5in=p5in,
       buck_loss=p5in-p5,pmos=r3['P_pmos'],pdiv=r3['P_gate_divider'],r12=R12,pin=pin,iin=pin/12.0,eta=r3['Pout']/pin,
       eta_drain=tr['eta1'])
json.dump(d,open('budget.json','w'),indent=1)
for k,v in d.items(): print(k, round(v,5))
