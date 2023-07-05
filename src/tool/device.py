import os

class DeviceInfo():
    def __init__(self):
        self.name = None

    @classmethod
    def parser(cls, infoFile):
        info = {} # to return
        if not os.path.isfile(infoFile):
            return info

        inDef = False
        with open(infoFile, 'r', encoding='utf-8') as F:
            for line in F:
                if not inDef and line.startswith('DEF '):
                    devName = line.split()[1]
                    devDescr = []
                    inDef = True
                elif inDef and line.startswith('ENDDEF'):
                    inDef = False
                    info[devName] = ''.join(devDescr)
                elif inDef:
                    devDescr.append(line)

        return info