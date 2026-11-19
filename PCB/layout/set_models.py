import pcbnew, os
io = pcbnew.PCB_IO_MGR.FindPlugin(pcbnew.PCB_IO_MGR.KICAD_SEXP)
P = '${KIPRJMOD}/pa40.3dshapes/'; K = '${KICAD10_3DMODEL_DIR}/'
M = {
 ('pa40.pretty', 'L_Toroid_T80_Flat_P10.16mm_Drill1.6mm'): P + 'L_Toroid_T80_Flat.wrl',
 ('pa40.pretty', 'L_Toroid_FT50_Flat_P7.62mm_Drill1.0mm'): P + 'L_Toroid_FT50_Flat.wrl',
 ('pa40.pretty', 'BNC_Molex_73100-0105_Horizontal'): P + 'BNC_Molex_73100-0105_Horizontal.wrl',
 ('pa40.pretty', 'Crystal_HC49-US_THT_SMD_Combo'): P + 'Crystal_HC49-US_THT_SMD_Combo.wrl',
 ('pa40.pretty', 'C_Trimmer_Voltronics_JZ'): P + 'C_Trimmer_Voltronics_JZ.wrl',
 ('pa40.pretty', 'EPC2036_LGA4_SMD_P0.45mm'): P + 'EPC2036_LGA4.wrl',
 ('fplib/Connector_BarrelJack.pretty', 'BarrelJack_CUI_PJ-102AH_Horizontal'): P + 'BarrelJack_CUI_PJ-102AH_Horizontal.wrl',
 ('fplib/TestPoint.pretty', 'TestPoint_Keystone_5019_Miniature'): P + 'TestPoint_Keystone_5019_Miniature.wrl',
 ('fplib/Inductor_SMD.pretty', 'L_Coilcraft_LPS4018'): K + 'Inductor_SMD.3dshapes/L_Bourns-SRN4018.step',
 ('fplib/Resistor_SMD.pretty', 'R_Shunt_Vishay_WSK2512_6332Metric_T1.19mm'): K + 'Resistor_SMD.3dshapes/R_2512_6332Metric.step',
}
for (lib, name), path in M.items():
    lp = os.path.abspath(lib)
    fp = io.FootprintLoad(lp, name)
    fp.Models().clear()
    m = pcbnew.FP_3DMODEL(); m.m_Filename = path; m.m_Show = True
    fp.Models().push_back(m)
    io.FootprintSave(lp, fp)
    print('set', name, '->', path)
