from devicelib.basicLib import BASIC_LIB
from devicelib.pdkLib import PDK_LIB
from devicelib.ipLib import IP_LIB


class Symbol():
    def __init__(self):
        self.name = None
        self.reference = None
        self.unused = None
        self.text_offset = None
        self.draw_pinnumber = None
        self.draw_pinname = None
        self.unit_count = None
        self.units_locked = None
        self.option_flag = None

        self.parts = [] # line, cycle, pin ...

    @classmethod
    def parse(cls, lib):
        symbols = {} # to return
        if lib == 'basic':
            libtext = BASIC_LIB
        elif lib == 'pdk':
            libtext = PDK_LIB
        elif lib == 'ip':
            libtext = IP_LIB
        else:
            libtext = ''

        symbol = None # temp
        scope = [] # temp

        for line in libtext.splitlines():
            tokens = line.strip().split()
            if line.startswith('#'):
                pass
            elif line.lower().startswith("foohueda-librar") or line.startswith('#') or len(tokens) == 0:
                pass
            elif line.lower().startswith("def "):
                assert scope == [], "not valid libfile syntax: {}".format(line)
                scope.append("def")
                # 0   1       2         3      4           5              6            7          8            9
                # DEF VSOURCE V         0      40          Y              Y            1          F            N
                # DEF opin    opin      0      0           N              N            1          F            P
                # def name    reference unused text_offset draw_pinnumber draw_pinname unit_count units_locked option_flag

                assert len(tokens) >= 10, "not valid libfile syntax: {}".format(line)
                symbol = Symbol()
                symbol.name = tokens[1]
                symbol.reference = tokens[2]
                symbol.unused = int(tokens[3])
                symbol.text_offset = int(tokens[4])
                symbol.draw_pinnumber = tokens[5]
                assert symbol.draw_pinnumber in ['Y', 'N']
                symbol.draw_pinname = tokens[6]
                assert symbol.draw_pinname in ['Y', 'N']
                symbol.unit_count = int(tokens[7])
                symbol.units_locked = tokens[8]
                assert symbol.units_locked in ['L', 'F']
                symbol.option_flag = tokens[9]
                assert symbol.option_flag in ['N', 'P']  # normal or power
            elif line.lower().startswith("enddef"):
                assert scope.pop() == "def", "not valid libfile syntax: {}".format(line)
                symbols[symbol.name]=symbol
                symbol = None #reset

            elif line.lower().startswith("draw"):
                assert scope[-1] == "def"
                scope.append("draw")

            elif line.lower().startswith("enddraw"):
                assert scope.pop() == "draw", "not valid libfile syntax: {}".format(line)

            elif line.lower().startswith("wire "):
                assert scope[-1] == "draw"
                scope.append(tokens[1].lower())

            elif line.lower().startswith('text label '):
                assert scope[-1] == "draw"
                scope.append(tokens[1].lower())
                part = [scope[-1]]
                part.extend(tokens[2:-1])

            else:
                if scope[-1] in ('wire', 'bus'):
                    part = [scope[-1]]
                    part.extend(tokens)
                    symbol.parts.append(part)
                    scope.pop()

                elif scope[-1] == 'label':
                    # Text Label posx posy orient dimension
                    # texts...
                    part.extend([line.strip()])
                    symbol.parts.append(part)
                    scope.pop()

                elif scope[-1] == "draw":
                    part_type = tokens[0].lower()
                    if part_type == 'x':
                        symbol.parts.append(tokens)
                    elif part_type == 'c':
                        symbol.parts.append(tokens)
                    elif part_type == 'a':
                        symbol.parts.append(tokens)
                    elif part_type == 'p':
                        symbol.parts.append(tokens)
                    else:
                        assert 0, "not defined so far: {}".format(line)
                else:
                    assert 0, "not valid libfile syntax: {}".format(line)

        return symbols