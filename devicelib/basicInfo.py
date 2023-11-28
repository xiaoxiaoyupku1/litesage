BASIC_INFO = r"""
DEF CAP
Type:Capacitor
Model:CAP
Pin:T1,T2
Param:,y,str,1p,,,F,,Value(F)
ENDDEF

DEF ISRC
Type:Current Source
Model:
Pin:T1,T2
Param:,y,str,,,,,,Value
ENDDEF

DEF DIO
Type:Diode
Pin:T1,T2
Model:DIODE
Descr:Breakdown Voltage(V) = 6
ENDDEF

DEF IND1
Type:Inductor
Model:IND
Pin:T1,T2
Param:,y,str,1,,,,,Value
ENDDEF

DEF IND2
Type:Inductor
Model:IND
Pin:T1,T2
Param:,y,str,1,,,,,Value
ENDDEF

DEF NMOS
Type:MOS
Model:NMOS
Pin:G,S,D
ENDDEF

DEF NPN
Type:BJT
Model:NPN
Pin:B,C,E
ENDDEF

DEF PMOS
Type:MOS
Model:PMOS
Pin:G,S,D
ENDDEF

DEF PNP
Type:BJT
Model:PNP
Pin:B,C,E
ENDDEF

DEF RES
Type:Resistor
Model:RES
Pin:T1,T2
Param:,y,str,1K,,,Ω,,Value(Ω)
ENDDEF

DEF SW
Type:Switch
Model:Switch
Pin:S1,S2,V1,V2
ENDDEF

DEF VCCS1
Type:Source
Model:VCCS1
Pin:T1,T2,T3,T4
Param:gm,y,str,,,,,,gm
ENDDEF

DEF VCCS2
Type:Source
Model:VCCS2
Pin:T1,T2,T3,T4
Param:gm,y,str,,,,,,gm
ENDDEF

DEF VCVS1
Type:Source
Model:VCVS1
Pin:T1,T2,T3,T4
Param:e,y,str,,,,,,e
ENDDEF

DEF VCVS2
Type:Source
Model:VCVS2
Pin:T1,T2,T3,T4
Param:e,y,str,,,,,,e
ENDDEF

DEF VSRC
Type:Voltage Source
Model:
Pin:T1,T2
Param:,y,str,,,,,,Value
ENDDEF

DEF ZENER
Type:Diode
Model:DIODE
Pin::T1,T2
Descr:Breakdown Voltage(V) = 6
ENDDEF

DEF GND
Type:
Model:
Pin:GND
ENDDEF
"""