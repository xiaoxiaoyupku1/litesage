IP_INFO = r"""
DEF LDO
Type:LDO
Model:LDO
Descr:低压降稳压器Low-Dropout Regulator
Pin:vcc,vm,vss,vout
ENDDEF

DEF BG_ACTIVE
Type:BANDGAP
Model:BG_ACTIVE
Descr:带隙基准源Bandgap Reference
Pin:PWR,ENABLE,OUT,SGND
ENDDEF
"""