PDK_INFO = r"""
DEF MNHA
Type:HV_MOS
Model:mnha
Descr:高压非对称NMOS
Pin:D,G,S
Param:wn,y,str,20u,,,m,,Width
Param:ln,y,str,3u,,,m,,Length
Param:mult,y,int,1,1,,,,Multil
ENDDEF

DEF MNHAT
Type:HV_MOS
Model:mnhat
Descr:高压厚氧非对称NMOS
Pin:D,G,S
Param:wn,y,str,20u,,,m,,Width
Param:ln,y,str,3u,,,m,,Length
Param:mult,y,int,1,1,,,,Multil
ENDDEF

DEF MNHS
Type:HV_MOS
Model:mnhs
Descr:高压对称NMOS
Pin:D,G,S
Param:wn,y,str,20u,,,m,,Width
Param:ln,y,str,3u,,,m,,Length
Param:mult,y,int,1,1,,,,Multil
ENDDEF

DEF MNHST
Type:HV_MOS
Model:mnhst
Descr:高压对称厚氧NMOS
Pin:D,G,S
Param:wn,y,str,20u,,,m,,Width
Param:ln,y,str,3u,,,m,,Length
Param:mult,y,int,1,1,,,,Multil
ENDDEF

DEF MNL
Type:MOS
Model:mnl
Descr:低压NMOS
Pin:D,G,S
Param:wn,y,str,5u,,,m,,Width
Param:ln,y,str,5u,,,m,,Length
Param:mult,y,int,1,1,,,,Multil
ENDDEF

DEF MPHS
Type:HV_MOS
Model:mphs
Descr:高压对称PMOS
Pin:D,G,S,B
Param:wn,y,str,20u,,,m,,Width
Param:ln,y,str,3u,,,m,,Length
Param:mult,y,int,1,1,,,,Multil
ENDDEF

DEF MPHST
Type:HV_MOS
Model:mphst
Descr:高压对称厚氧PMOS
Pin:D,G,S,B
Param:wn,y,str,20u,,,m,,Width
Param:ln,y,str,3u,,,m,,Length
Param:mult,y,int,1,1,,,,Multil
ENDDEF

DEF MPL
Type:MOS
Model:mpl
Descr:低压PMOS
Pin:D,G,S,B
Param:wn,y,str,5u,,,m,,Width
Param:ln,y,str,5u,,,m,,Length
Param:mult,y,int,1,1,,,,Multil
ENDDEF

DEF QNH
Type:BJT
Model:qnh
Descr:高压NPN
Pin:C,B,E
Param:,n,str,H,,,V,,Voltage
Param:mult,y,int,1,1,,,,Multil
ENDDEF

DEF QNH_HV
Type:BJT
Model:qnh_hv
Descr:高压NPN大器件，M=2000，表示2000个emitter，可以走大电流。
Pin:C,B,E
ENDDEF

DEF QNL
Type:BJT
Model:qnl
Descr:低压NPN
Pin:C,B,E
Param:,n,str,L,,,V,,Voltage
Param:mult,y,int,1,1,,,,Multil
ENDDEF

DEF QPVH
Type:BJT
Model:qpvh
Descr:高压纵向PNP
Pin:B,E
Param:mult,y,int,1,1,,,,Multil
ENDDEF

DEF QPVL
Type:BJT
Model:qpvl
Descr:低压纵向PNP
Pin:B,E
Param:mult,y,int,1,1,,,,Multil
ENDDEF

DEF QPVPWH
Type:BJT
Model:qpvpwh
Descr:高压纵向PNP（BE结击穿电压比较大）
Pin:B,E
Param:mult,y,int,1,1,,,,Multil
ENDDEF

DEF MNHIA
Type:HV_MOS
Model:mnhia
Descr:高压独立隔离岛非对称NMOS
Pin:D,G,S,B
Param:wn,y,str,20u,,,m,,Width
Param:ln,y,str,3u,,,m,,Length
Param:mult,y,int,1,1,,,,Multil
ENDDEF

DEF MNHIAT
Type:HV_MOS
Model:mnhiat
Descr:高压独立隔离岛厚氧非对称NMOS
Pin:D,G,S,B
Param:wn,y,str,20u,,,m,,Width
Param:ln,y,str,3u,,,m,,Length
Param:mult,y,int,1,1,,,,Multil
ENDDEF

DEF MPHA
Type:HV_MOS
Model:mpha
Descr:高压非对称PMOS
Pin:D,G,S,B
Param:wn,y,str,20u,,,m,,Width
Param:ln,y,str,3u,,,m,,Length
Param:mult,y,int,1,1,,,,Multil
ENDDEF

DEF MPHAT
Type:HV_MOS
Model:mphat
Descr:高压厚氧非对称PMOS
Pin:D,G,S,B
Param:wn,y,str,20u,,,m,,Width
Param:ln,y,str,3u,,,m,,Length
Param:mult,y,int,1,1,,,,Multil
ENDDEF

DEF DNPPWL
Type:Diode
Model:dnppwl
Descr:低压DIODE
Pin:T1,T2
Param:mult,y,int,1,1,,,,Multil
ENDDEF

DEF DNPPWH
Type:Diode
Model:dnppwh
Descr:高压DIODE
Pin:T1,T2
Param:mult,y,int,1,1,,,,Multil
ENDDEF

DEF DNPPWPSB
Type:Diode
Model:dnppwpsb
Descr:DIODE
Pin:T1,T2
Param:mult,y,int,1,1,,,,Multil
ENDDEF

DEF DNWPSB
Type:Diode
Model:dnwpsb
Descr:DIODE
Pin:T1,T2
Param:mult,y,int,1,1,,,,Multil
ENDDEF

DEF DNWPSBBN
Type:Diode
Model:dnwpsbbn
Descr:DIODE
Pin:T1,T2
Param:mult,y,int,1,1,,,,Multil
ENDDEF

DEF DPPNW
Type:Diode
Model:dppnw
Descr:DIODE
Pin:T1,T2
Param:mult,y,int,1,1,,,,Multil
ENDDEF

DEF DPWNWBN
Type:Diode
Model:dpwnwbn
Descr:DIODE
Pin:T1,T2
Param:mult,y,int,1,1,,,,Multil
ENDDEF

DEF CPONWL
Type:Capacitor
Model:cponwl
Descr:低压薄氧电容（poly-to-nwell）
Pin:T1,T2
Param:value,y,str,10p,,,,,Value
ENDDEF

DEF CPONWH
Type:Capacitor
Model:cponwh
Descr:高压薄氧电容（poly-fox-nwell）
Pin:T1,T2
Param:value,y,str,10p,,,,,Value
ENDDEF

DEF CPONWTL
Type:Capacitor
Model:cponwtl
Descr:低压厚氧电容（poly-to-nwell）
Pin:T1,T2
Param:value,y,str,10p,,,,,Value
ENDDEF

DEF CPONWTH
Type:Capacitor
Model:cponwth
Descr:高压厚氧电容（poly-fox-nwell）
Pin:T1,T2
Param:value,y,str,10p,,,,,Value
ENDDEF

DEF RHR
Type:Resistor
Model:rhr
Descr:高值电阻
Descr:R=(L/W)*RS
Descr:[解释：L-电阻长度；W-电阻宽度；RHR最小宽度限制：2U，电阻上走的电流越多，电阻需越宽；RS为方块电阻；RHR方块电阻1080;适用于5.4k-9.25k之间]
Pin:T1,T2
Param:value,y,str,8k,5.4k,1M,,,Value
Param:wjb,y,str,2u,2u,,,,Width
ENDDEF

DEF RMET1
Type:Resistor
Model:rmet1
Descr:MET1电阻
Pin:T1,T2
Param:value,y,str,1,,,,,Value
Param:wjb,y,str,4u,,,,,Width
ENDDEF

DEF RMET2
Type:Resistor
Model:rmet2
Descr:MET2电阻
Pin:T1,T2
Param:value,y,str,1,,,,,Value
Param:wjb,y,str,4u,,,,,Width
ENDDEF

DEF RNPL
Type:Resistor
Model:rnpl
Descr:NPLUS电阻
Descr:R=(L/W)*RS
Descr:[解释：L-电阻长度；W-电阻宽度；RHR最小宽度限制：1.2U，电阻上走的电流越多，电阻需越宽；RS为方块电阻；方块电阻38;适用于190-1.9k之间]
Pin:T1,T2
Param:value,y,str,500,190,1.9k,,,Value
Param:wjb,y,str,1.2u,1.2u,,,,Width
ENDDEF

DEF RNWL
Type:Resistor
Model:rnwl
Descr:低压NWELL电阻
Descr:R=(L/W)*RS
Descr:[解释：L-电阻长度；W-电阻宽度；RHR最小宽度限制：5U，电阻上走的电流越多，电阻需越宽；RS为方块电阻；方块电阻1850;适用于9.25k以上]
Pin:T1,T2
Param:value,y,str,15k,9.25k,,,,Value
Param:wjb,y,str,5u,5u,,,,Width
ENDDEF

DEF RNWH
Type:Resistor
Model:rnwh
Descr:高压NWELL电阻
Descr:R=(L/W)*RS
Descr:[解释：L-电阻长度；W-电阻宽度；RHR最小宽度限制：5U，电阻上走的电流越多，电阻需越宽；RS为方块电阻；方块电阻1850;适用于9.25k以上]
Pin:T1,T2
Param:value,y,str,15k,9.25k,,,,Value
Param:wjb,y,str,5u,5u,,,,Width
ENDDEF

DEF RPOLY1
Type:Resistor
Model:rpoly1
Descr:POLY电阻
Descr:R=(L/W)*RS
Descr:[解释：L-电阻长度；W-电阻宽度；RHR最小宽度限制：1U，电阻上走的电流越多，电阻需越宽；RS为方块电阻；方块电阻28；适用于140-1.4k之间]
Pin:T1,T2
Param:value,y,str,400,140,1.4k,,,Value
Param:wjb,y,str,2u,1u,,,,Width
ENDDEF

DEF RPPL
Type:Resistor
Model:rppl
Descr:低压PPLUS电阻
Descr:R=(L/W)*RS
Descr:[解释：L-电阻长度；W-电阻宽度；RHR最小宽度限制：1.2U，电阻上走的电流越多，电阻需越宽；RS为方块电阻；方块电阻55；适用于275-2.75k之间]
Pin:T1,T2,T3
Param:value,y,str,1k,275,2.75k,,,Value
Param:wjb,y,str,1.2u,1.2u,,,,Width
ENDDEF

DEF RPPH
Type:Resistor
Model:rpph
Descr:高压PPLUS电阻。
Descr:R=(L/W)*RS
Descr:[解释：L-电阻长度；W-电阻宽度；RHR最小宽度限制：1.2U，电阻上走的电流越多，电阻需越宽；RS为方块电阻；方块电阻55；适用于275-2.75k之间]
Pin:T1,T2,T3
Param:value,y,str,1k,275,2.75k,,,Value
Param:wjb,y,str,1.2u,1.2u,,,,Width
ENDDEF

DEF RFUSEM2
Type:Resistor
Model:rfusem2
Descr:RFUSEM2
Pin:T1,T2
ENDDEF

DEF RFUSEPOLY
Type:RFUSE
Model:rfusepoly
Descr:RFUSEPOLY
Pin:T1,T2
ENDDEF

DEF ROPTION
Type:ROPTION
Model:roption
Descr:ROPTION
Pin:T1,T2
ENDDEF

DEF RSMEAR
Type:RSMEAR
Model:rsmear
Descr:RSMEAR
Pin:T1,T2
ENDDEF

DEF RSUB
Type:RSUB
Model:rsub
Descr:RSUB
Pin:T1,T2
ENDDEF

DEF ZZPNW
Type:Diode
Model:zzpnw
Descr:ZENER
Pin:T1,T2
Param:mult,y,int,1,1,,,,Multil
ENDDEF

DEF ESD_DNWPSB
Type:ESD
Model:ESD_DNWPSB
Descr:ESD保护
Pin:T1,T2
ENDDEF

DEF ESD_MNHA
Type:ESD
Model:ESD_MNHA
Descr:ESD保护
Pin:D,S
ENDDEF

DEF ESD_MNHIA
Type:ESD
Model:ESD_MNHIA
Descr:ESD保护
Pin:D,S
ENDDEF

DEF ESD_MNL
Type:ESD
Model:ESD_MNL
Descr:ESD保护
Pin:D,S
ENDDEF

DEF ESD_MPL
Type:ESD
Model:ESD_MPL
Descr:ESD保护
Pin:D,S
ENDDEF

DEF ESD_QNH
Type:ESD
Model:ESD_QNH
Descr:ESD保护
Pin:C,B
ENDDEF

DEF ESD_QNL
Type:ESD
Model:ESD_QNL
Descr:ESD保护
Pin:C,B
ENDDEF

DEF PAD_22
Type:PAD
Model:pad_22
Descr:PAD
Pin:T1
ENDDEF

DEF PAD_60
Type:PAD
Model:pad_60
Descr:PAD
Pin:T1
ENDDEF

DEF PAD_80
Type:PAD
Model:pad_80
Descr:PAD
Pin:T1
ENDDEF

DEF PAD_100
Type:PAD
Model:pad_100
Descr:PAD
Pin:T1
ENDDEF

DEF IPROBE
Type:IPROBE
Model:iprobe
Descr:IPROBE
Pin:T1,T2
ENDDEF
"""