FHSchema Schematic File Version 1
EELAYER 30 0
EELAYER END
$Descr A4 11693 8268
encoding utf-8
Sheet 1 1
Title "demo"
Date "May 16 15:10:52 2023"
Rev "1"
Comp "basic"
Comment1 ""
Comment2 ""
Comment3 ""
Comment4 ""
$EndDescr
$Comp
L basic:res R0
U 1 1 612E6D41
P 0.000000 -375.000000
F 0 "R0" H 90.000000 -288.000000 80 0000 L CNN
F 1 "res" H 90.000000 -208.000000 30 0000 L CNN
F 2 "R=1K" H 90.000000 -158.000000 30 0000 L CNN
F 3 "x" H 90.000000 -108.000000 30 0000 L CNN
F 4 "" H 90.000000 -58.000000 30 0000 L CNN
F 5 "model=" H 0.000000 -375.000000 10 0001 L CNN
F 6 "r=1K" H 0.000000 -375.000000 10 0001 L CNN
F 7 "l=" H 0.000000 -375.000000 10 0001 L CNN
F 8 "w=" H 0.000000 -375.000000 10 0001 L CNN
F 9 "m=" H 0.000000 -375.000000 10 0001 L CNN
F 10 "scale=" H 0.000000 -375.000000 10 0001 L CNN
F 11 "trise=" H 0.000000 -375.000000 10 0001 L CNN
F 12 "tc1=" H 0.000000 -375.000000 10 0001 L CNN
F 13 "tc2=" H 0.000000 -375.000000 10 0001 L CNN
F 14 "resform=" H 0.000000 -375.000000 10 0001 L CNN
F 15 "isnoisy= " H 0.000000 -375.000000 10 0001 L CNN
F 16 "c=" H 0.000000 -375.000000 10 0001 L CNN
F 17 "tc1r=" H 0.000000 -375.000000 10 0001 L CNN
F 18 "tc2r=" H 0.000000 -375.000000 10 0001 L CNN
F 19 "tc1c=" H 0.000000 -375.000000 10 0001 L CNN
F 20 "tc2c=" H 0.000000 -375.000000 10 0001 L CNN
F 21 "scaler=" H 0.000000 -375.000000 10 0001 L CNN
F 22 "scalec=" H 0.000000 -375.000000 10 0001 L CNN
F 23 "ac=" H 0.000000 -375.000000 10 0001 L CNN
F 24 "dtemp=" H 0.000000 -375.000000 10 0001 L CNN
F 25 "hrc=" H 0.000000 -375.000000 10 0001 L CNN
        1 0 0 1
$EndComp
$Comp
L basic:vdc V0
U 1 1 612E6D41
P 562.500000 -375.000000
F 0 "V0" H 662.500000 -188.000000 80 0000 L CNN
F 5 "noisefile=" H 562.500000 -375.000000 10 0001 L CNN
F 6 "FNpairs=0" H 562.500000 -375.000000 10 0001 L CNN
F 7 "vdc=5" H 562.500000 -375.000000 10 0001 L CNN
F 8 "acm=" H 562.500000 -375.000000 10 0001 L CNN
F 9 "acp=" H 562.500000 -375.000000 10 0001 L CNN
F 10 "xfm=" H 562.500000 -375.000000 10 0001 L CNN
F 11 "pacm=" H 562.500000 -375.000000 10 0001 L CNN
F 12 "pacp=" H 562.500000 -375.000000 10 0001 L CNN
F 13 "tc1=" H 562.500000 -375.000000 10 0001 L CNN
F 14 "tc2=" H 562.500000 -375.000000 10 0001 L CNN
F 15 "tnom=" H 562.500000 -375.000000 10 0001 L CNN
F 16 "srcType=dc" H 562.500000 -375.000000 10 0001 L CNN
        1 0 0 1
$EndComp
$Comp
L basic:gnd I0
U 1 1 612E6D41
P 250.000000 250.000000
        1 0 0 1
$EndComp
Wire Wire Line gnd!
        0.000000 125.000000 0.000000 0.000000
Wire Wire Line gnd!
        0.000000 125.000000 250.000000 125.000000
Wire Wire Line gnd!
        250.000000 250.000000 250.000000 125.000000
Wire Wire Line gnd!
        250.000000 125.000000 562.500000 125.000000
Connection ~ 250.000000 125.000000 21.875000
Wire Wire Line gnd!
        562.500000 125.000000 562.500000 0.000000
Wire Wire Line net2
        0.000000 -375.000000 0.000000 -625.000000
Wire Wire Line net2
        0.000000 -625.000000 562.500000 -625.000000
Wire Wire Line net2
        562.500000 -375.000000 562.500000 -625.000000