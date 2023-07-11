import os

def getDeviceInfos(infoFile):
    """return list of DeviceInfo"""
    deviceInfoDict = {}
    if not os.path.isfile(infoFile):
        print('invalid info file: {}'.format(infoFile))
        return deviceInfoDict

    inDef = False
    with open(infoFile, 'r', encoding='utf-8') as F:
        for line in F:
            line = line.strip()
            if not inDef and line.startswith('DEF '):
                devName = line.split()[1]
                devType = ''
                devModel = ''
                devDescrLines = []
                devParamLines = []
                inDef = True
            elif inDef and line.startswith('ENDDEF'):
                inDef = False
                devInfo = DeviceInfo(devName, devType, devModel, devDescrLines, devParamLines)
                deviceInfoDict[devName] = devInfo
            elif inDef and line.startswith('Type:'):
                devType = line[5:]
            elif inDef and line.startswith('Model:'):
                devModel = line[6:]
            elif inDef and line.startswith('Descr:'):
                devDescrLines.append(line[6:])
            elif inDef and line.startswith('Param:'):
                devParamLines.append(line[6:])

    return deviceInfoDict


class DeviceInfo():
    def __init__(self, devName, devType, devModel, devDescrLines, devParamLines):
        self.name = devName
        self.type = devType
        self.model = devModel
        self.descrLines = devDescrLines

        self.prompt = ''
        self.parsePrompt()    # displayed on device selection window

        self.paramNames = []
        self.paramList = []
        self.parseParams(devParamLines)

    def parsePrompt(self):
        # if len(self.descrLines) == 0:
        #     self.prompt = '\u7c7b\u578b\uff1a\n{}'.format(self.type)
        # else:
        #     self.prompt = '\u7c7b\u578b\uff1a\n{}\n\n\u4fe1\u606f\uff1a\n{}'.format(
        #         self.type, '\n'.join(self.descrLines))
        self.prompt = '\n'.join(self.descrLines)

    def getPrompt(self):
        return self.prompt
        
    def parseParams(self, devParamLines):
        for line in devParamLines:
            devParam = DeviceParam(line)
            self.paramNames.append(devParam.name)
            self.paramList.append(devParam)


class DeviceParam():
    def __init__(self, paramLine):
        self.name = None        # param name to be used in netlist
                                # (can be empty string, R1 n1 n2 5K)
        self.type = None        # str, int, bool, cyclic
        self.defVal = None
        self.minVal = None
        self.maxVal = None
        self.unit = None
        self.choices = None     # list of strings
        self.parse(paramLine)

    def parse(self, paramLine):
        """
        Param:Name,Type,DefaultValue,MinValue,MaxValue,Unit,Choices,Prompt
        Param:R,str,1K,,,Ohm,,Value
        """
        items = [item.strip() for item in paramLine.split(',')]
        parName, parType, defVal, minVal, maxVal, unit, choices, prompt = items
        self.name = parName
        self.type = parType.lower()
        self.defVal = defVal
        self.minVal = minVal
        self.maxVal = maxVal
        self.unit = unit
        self.choices = choices.split()
        self.prompt = prompt