IP_LIB = r"""
FoohuEda-LIBRARY Version 1
#encoding utf-8
#description: ip devices

DEF BG_ACTIVE BG_ACTIVE 0 0 N N 1 F N
DRAW
Wire Wire Line
        -1625.000000 -250.000000 -1250.000000 -250.000000
Wire Wire Line
        1250.000000 250.000000 1625.000000 250.000000
Wire Wire Line
        -1625.000000 250.000000 -1250.000000 250.000000
Wire Wire Line
        1625.000000 -250.000000 1250.000000 -250.000000
P 4 1 0 1 -1250.000000 -875.000000 1250.000000 -875.000000 1250.000000 875.000000 -1250.000000 875.000000 N
X ENABLE 1 -1625.000000 250.000000 0 R 50 50 1 0 B
X PWR 2 -1625.000000 -250.000000 0 R 50 50 1 0 B
X SGND 3 1625.000000 250.000000 0 R 50 50 1 0 B
X BG_ACTIVE 4 1625.000000 -250.000000 0 R 50 50 1 0 B
Text Label -1230.000000 -250.000000 0 125.000000 ~
PWR
Text Label -1230.000000 250.000000 0 125.000000 ~
ENABLE
Text Label 480.000000 -250.000000 0 125.000000 ~
BG_ACTIVE
Text Label 765.000000 250.000000 0 125.000000 ~
SGND
ENDDRAW
ENDDEF

DEF PAD_ESD_MN9 PAD_ESD_MN9 0 0 N N 1 F N
DRAW
Wire Wire Line
        0.000000 200.000000 0.000000 0.000000
Wire Wire Line
        0.000000 1200.000000 0.000000 1400.000000
P 4 1 0 1 -300.000000 200.000000 300.000000 200.000000 300.000000 1200.000000 -300.000000 1200.000000 N
X PAD_PIN 1 0.000000 0.000000 0 R 50 50 1 0 B
X ESD_GND 2 0.000000 1400.000000 0 R 50 50 1 0 B
Text Label -300.000000 350.000000 0 125.000000 ~
PAD_PIN
Text Label -330.000000 1050.000000 0 125.000000 ~
ESD_GND
ENDDRAW
ENDDEF

DEF PAD_ESD_MN25 PAD_ESD_MN25 0 0 N N 1 F N
DRAW
Wire Wire Line
        0.000000 200.000000 0.000000 0.000000
Wire Wire Line
        0.000000 1200.000000 0.000000 1400.000000
P 4 1 0 1 -300.000000 200.000000 300.000000 200.000000 300.000000 1200.000000 -300.000000 1200.000000 N
X PAD_PIN 1 0.000000 0.000000 0 R 50 50 1 0 B
X ESD_GND 2 0.000000 1400.000000 0 R 50 50 1 0 B
Text Label -300.000000 350.000000 0 125.000000 ~
PAD_PIN
Text Label -330.000000 1050.000000 0 125.000000 ~
ESD_GND
ENDDRAW
ENDDEF

DEF PAD_ESD_MN45 PAD_ESD_MN45 0 0 N N 1 F N
DRAW
Wire Wire Line
        0.000000 200.000000 0.000000 0.000000
Wire Wire Line
        0.000000 1200.000000 0.000000 1400.000000
P 4 1 0 1 -300.000000 200.000000 300.000000 200.000000 300.000000 1200.000000 -300.000000 1200.000000 N
X PAD_PIN 1 0.000000 0.000000 0 R 50 50 1 0 B
X ESD_GND 2 0.000000 1400.000000 0 R 50 50 1 0 B
Text Label -300.000000 350.000000 0 125.000000 ~
PAD_PIN
Text Label -330.000000 1050.000000 0 125.000000 ~
ESD_GND
ENDDRAW
ENDDEF

DEF PAD_ESD_MP9 PAD_ESD_MP9 0 0 N N 1 F N
DRAW
Wire Wire Line
        0.000000 200.000000 0.000000 0.000000
Wire Wire Line
        0.000000 1200.000000 0.000000 1400.000000
P 4 1 0 1 -300.000000 200.000000 300.000000 200.000000 300.000000 1200.000000 -300.000000 1200.000000 N
X PAD_PIN 1 0.000000 0.000000 0 R 50 50 1 0 B
X ESD_GND 2 0.000000 1400.000000 0 R 50 50 1 0 B
Text Label -330.000000 350.000000 0 125.000000 ~
ESD_PWR
Text Label -300.000000 1050.000000 0 125.000000 ~
PAD_PIN
ENDDRAW
ENDDEF
"""