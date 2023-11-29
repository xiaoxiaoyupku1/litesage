PDK_INFO = r"""
DEF MN15G40
Type:HV_MOS
Model:MNHA
Descr:高压非对称NMOS
Pin:D,G,S
Param:wn,y,str,20u,,,m,,Width
Param:ln,y,str,3u,,,m,,Length
Param:mult,y,int,1,1,,,,Multil
ENDDEF

DEF MN15G40T
Type:HV_MOS
Model:MNHAT
Descr:高压厚氧非对称NMOS
Pin:D,G,S
Param:wn,y,str,20u,,,m,,Width
Param:ln,y,str,3u,,,m,,Length
Param:mult,y,int,1,1,,,,Multil
ENDDEF

DEF MN40G40S
Type:HV_MOS
Model:MNHS
Descr:高压对称NMOS
Pin:D,G,S
Param:wn,y,str,20u,,,m,,Width
Param:ln,y,str,3u,,,m,,Length
Param:mult,y,int,1,1,,,,Multil
ENDDEF

DEF MN40G40ST
Type:HV_MOS
Model:MNHST
Descr:高压对称厚氧NMOS
Pin:D,G,S
Param:wn,y,str,20u,,,m,,Width
Param:ln,y,str,3u,,,m,,Length
Param:mult,y,int,1,1,,,,Multil
ENDDEF

DEF MN5
Type:MOS
Model:MNL
Descr:低压NMOS
Pin:D,G,S
Param:wn,y,str,5u,,,m,,Width
Param:ln,y,str,5u,,,m,,Length
Param:mult,y,int,1,1,,,,Multil
ENDDEF

DEF MP40G40S
Type:HV_MOS
Model:MPHS
Descr:高压对称PMOS
Pin:D,G,S,B
Param:wn,y,str,20u,,,m,,Width
Param:ln,y,str,3u,,,m,,Length
Param:mult,y,int,1,1,,,,Multil
ENDDEF

DEF MP40G40ST
Type:HV_MOS
Model:MPHST
Descr:高压对称厚氧PMOS
Pin:D,G,S,B
Param:wn,y,str,20u,,,m,,Width
Param:ln,y,str,3u,,,m,,Length
Param:mult,y,int,1,1,,,,Multil
ENDDEF

DEF MP5
Type:MOS
Model:MPL
Descr:低压PMOS
Pin:D,G,S,B
Param:wn,y,str,5u,,,m,,Width
Param:ln,y,str,5u,,,m,,Length
Param:mult,y,int,1,1,,,,Multil
ENDDEF

DEF QN5
Type:BJT
Model:QNL
Descr:低压NPN
Pin:C,B,E
Param:,n,str,L,,,V,,Voltage
Param:mult,y,int,1,1,,,,Multil
ENDDEF

DEF QP5
Type:BJT
Model:QPVL
Descr:低压纵向PNP
Pin:B,E
Param:mult,y,int,1,1,,,,Multil
ENDDEF

DEF MN15G40I
Type:HV_MOS
Model:MNHIA
Descr:高压独立隔离岛非对称NMOS
Pin:D,G,S,B
Param:wn,y,str,20u,,,m,,Width
Param:ln,y,str,3u,,,m,,Length
Param:mult,y,int,1,1,,,,Multil
ENDDEF

DEF MN40G40TI
Type:HV_MOS
Model:MNHIAT
Descr:高压独立隔离岛厚氧非对称NMOS
Pin:D,G,S,B
Param:wn,y,str,20u,,,m,,Width
Param:ln,y,str,3u,,,m,,Length
Param:mult,y,int,1,1,,,,Multil
ENDDEF

DEF MP15G40
Type:HV_MOS
Model:MPHA
Descr:高压非对称PMOS
Pin:D,G,S,B
Param:wn,y,str,20u,,,m,,Width
Param:ln,y,str,3u,,,m,,Length
Param:mult,y,int,1,1,,,,Multil
ENDDEF

DEF MP40G40T
Type:HV_MOS
Model:MPHAT
Descr:高压厚氧非对称PMOS
Pin:D,G,S,B
Param:wn,y,str,20u,,,m,,Width
Param:ln,y,str,3u,,,m,,Length
Param:mult,y,int,1,1,,,,Multil
ENDDEF

DEF DN13
Type:Diode
Model:DNPPWL
Descr:低压DIODE
Pin:T1,T2
Param:mult,y,int,1,1,,,,Multil
ENDDEF

DEF DNW54
Type:Diode
Model:DNWPSB
Descr:DIODE
Pin:T1,T2
Param:mult,y,int,1,1,,,,Multil
ENDDEF

DEF DNW47
Type:Diode
Model:DNWPSBBN
Descr:DIODE
Pin:T1,T2
Param:mult,y,int,1,1,,,,Multil
ENDDEF

DEF DP15
Type:Diode
Model:DPPNW
Descr:DIODE
Pin:T1,T2
Param:mult,y,int,1,1,,,,Multil
ENDDEF

DEF DPW51
Type:Diode
Model:DPWNWBN
Descr:DIODE
Pin:T1,T2
Param:mult,y,int,1,1,,,,Multil
ENDDEF

DEF RHPO1080
Type:Resistor
Model:RHR
Descr:高值电阻
Descr:R=(L/W)*RS
Descr:[解释：L-电阻长度；W-电阻宽度；RHR最小宽度限制：2U，电阻上走的电流越多，电阻需越宽；RS为方块电阻；RHR方块电阻1080;适用于5.4k-9.25k之间]
Pin:T1,T2
Param:value,y,str,8k,5.4k,1M,,,Value
Param:wjb,y,str,2u,2u,,,,Width
ENDDEF

DEF RN38
Type:Resistor
Model:RNPL
Descr:NPLUS电阻
Descr:R=(L/W)*RS
Descr:[解释：L-电阻长度；W-电阻宽度；RHR最小宽度限制：1.2U，电阻上走的电流越多，电阻需越宽；RS为方块电阻；方块电阻38;适用于190-1.9k之间]
Pin:T1,T2
Param:value,y,str,500,190,1.9k,,,Value
Param:wjb,y,str,1.2u,1.2u,,,,Width
ENDDEF

DEF RNW1850
Type:Resistor
Model:RNWH
Descr:高压NWELL电阻
Descr:R=(L/W)*RS
Descr:[解释：L-电阻长度；W-电阻宽度；RHR最小宽度限制：5U，电阻上走的电流越多，电阻需越宽；RS为方块电阻；方块电阻1850;适用于9.25k以上]
Pin:T1,T2
Param:value,y,str,15k,9.25k,,,,Value
Param:wjb,y,str,5u,5u,,,,Width
ENDDEF

DEF RLPO28
Type:Resistor
Model:RPOLY1
Descr:POLY电阻
Descr:R=(L/W)*RS
Descr:[解释：L-电阻长度；W-电阻宽度；RHR最小宽度限制：1U，电阻上走的电流越多，电阻需越宽；RS为方块电阻；方块电阻28；适用于140-1.4k之间]
Pin:T1,T2
Param:value,y,str,400,140,1.4k,,,Value
Param:wjb,y,str,2u,1u,,,,Width
ENDDEF

DEF RP55
Type:Resistor
Model:RPPH
Descr:高压PPLUS电阻。
Descr:R=(L/W)*RS
Descr:[解释：L-电阻长度；W-电阻宽度；RHR最小宽度限制：1.2U，电阻上走的电流越多，电阻需越宽；RS为方块电阻；方块电阻55；适用于275-2.75k之间]
Pin:T1,T2,T3
Param:value,y,str,1k,275,2.75k,,,Value
Param:wjb,y,str,1.2u,1.2u,,,,Width
ENDDEF

DEF DZENER
Type:Diode
Model:ZZPNW
Descr:ZENER
Pin:T1,T2
Param:mult,y,int,1,1,,,,Multil
ENDDEF
"""