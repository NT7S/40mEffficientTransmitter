import re, os, xml.etree.ElementTree as ET
libs=dict(re.findall(r'\(name "([^"]+)"\)\(type "KiCad"\)\(uri "\$\{KIPRJMOD\}/([^"]+)"',open('fp-lib-table').read()))
def parse(s):
    toks=re.findall(r'\(|\)|"(?:[^"\\]|\\.)*"|[^\s()]+',s); st=[[]]
    for t in toks:
        if t=='(': st.append([])
        elif t==')': x=st.pop(); st[-1].append(x)
        else: st[-1].append(t)
    return st[0][0]
def find(n,k): return [c for c in n if isinstance(c,list) and c and c[0]==k]
def crtyd(fp):
    l,n=fp.split(':'); t=parse(open(f"{libs[l]}/{n}.kicad_mod").read())
    xs=[];ys=[]
    for g in t:
        if not(isinstance(g,list) and g[0] in('fp_line','fp_rect','fp_circle','fp_poly','fp_arc')): continue
        lay=find(g,'layer')
        if not lay or 'CrtYd' not in lay[0][1]: continue
        if g[0]=='fp_circle':
            c=find(g,'center')[0];e=find(g,'end')[0];cx,cy=float(c[1]),float(c[2]);r=((float(e[1])-cx)**2+(float(e[2])-cy)**2)**.5
            xs+= [cx-r,cx+r]; ys+=[cy-r,cy+r]; continue
        pts=[]
        for k in('start','end','mid'): pts+=find(g,k)
        for p in find(g,'pts'): pts+=find(p,'xy')
        for p in pts: xs.append(float(p[1])); ys.append(float(p[2]))
    return (min(xs),min(ys),max(xs),max(ys)) if xs else None
if __name__=='__main__':
    r=ET.parse('floorplan/net-rev7.xml').getroot(); seen={}
    for c in r.iter('comp'): seen.setdefault(c.findtext('footprint'),[]).append(c.get('ref'))
    tot=0
    for fp,refs in seen.items():
        b=crtyd(fp); w,h=b[2]-b[0],b[3]-b[1]; tot+=w*h*len(refs)
        print(f"{fp.split(':')[1]:55s} {w:5.1f} x {h:5.1f}  {','.join(refs)}")
    print('total courtyard area mm2', round(tot))
