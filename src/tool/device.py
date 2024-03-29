from src.tool.num import EngNum
from devicelib.basicInfo import BASIC_INFO
from devicelib.pdkInfo import PDK_INFO
from devicelib.ipInfo import IP_INFO


def getDeviceInfos(lib):
    """return list of DeviceInfo"""
    deviceInfoDict = {}
    if lib == 'basic':
        infotext = BASIC_INFO
    elif lib == 'pdk':
        infotext = PDK_INFO
    elif lib == 'ip':
        infotext = IP_INFO
    else:
        infotext = ''

    inDef = False
    for line in infotext.splitlines():
        line = line.strip()
        if not inDef and line.startswith('DEF '):
            devName = line.split()[1]
            devType = ''
            devModel = ''
            devPins = []
            devDescrLines = []
            devParamLines = []
            inDef = True
        elif inDef and line.startswith('ENDDEF'):
            inDef = False
            devInfo = DeviceInfo(devName, devType, devModel, devPins, devDescrLines, devParamLines, lib)
            deviceInfoDict[devName] = devInfo
        elif inDef and line.startswith('Type:'):
            devType = line[5:]
        elif inDef and line.startswith('Model:'):
            devModel = line[6:]
        elif inDef and line.startswith('Descr:'):
            devDescrLines.append(line[6:])
        elif inDef and line.startswith('Param:'):
            devParamLines.append(line[6:])
        elif inDef and line.startswith('Pin:'):
            devPins = line[4:].split(',')
            devPins = [p.strip() for p in devPins]

    return deviceInfoDict


class DeviceInfo():
    def __init__(self, devName, devType, devModel, devPins, devDescrLines, devParamLines, lib):
        self.lib = lib # 'basic', 'pdk', 'ip'
        self.name = devName
        self.type = devType
        self.model = devModel
        self.pins = devPins
        self.descrLines = devDescrLines

        self.head = self.parseNameHead()

        self.prompt = ''
        self.parsePrompt()    # displayed on device selection window

        self.paramNames = []
        self.paramList = []
        self.parseParams(devParamLines)

    def parseNameHead(self):
        if len(self.type) == 0:
            return 'I'
        elif self.lib == 'ip':
            return 'X'
        return DEVNAME_HEAD_MAPPING.get(self.type.lower(), self.type[0].upper())

    def parsePrompt(self):
        # if len(self.descrLines) == 0:
        #     self.prompt = '\u7c7b\u578b\uff1a\n{}'.format(self.type)
        # else:
        #     self.prompt = '\u7c7b\u578b\uff1a\n{}\n\n\u4fe1\u606f\uff1a\n{}'.format(
        #         self.type, '\n'.join(self.descrLines))
        self.prompt = '\n'.join(self.descrLines)

    def getPrompt(self):
        return self.prompt

    def getPins(self):
        return self.pins

    def getParamNames(self):
        return self.paramNames

    def getParamList(self):
        return self.paramList
        
    def parseParams(self, devParamLines):
        for line in devParamLines:
            devParam = DeviceParam(line)
            self.paramNames.append(devParam.getName())
            self.paramList.append(devParam)


class DeviceParam():
    def __init__(self, paramLine=None):
        self.name = None        # param name to be used in netlist
                                # (can be empty string, R1 n1 n2 5K)
        self.usedInNetlist = None # y or n: whether used in netlist
        self.type = None        # str, int, bool, cyclic
        self.defVal = None
        self.minVal = None
        self.maxVal = None
        self.value = None       # actual value
        self.unit = None
        self.choices = None     # list of strings
        self.prompt = None      # label displayed on GUI
        if paramLine is not None:
            self.parse(paramLine)

    def parse(self, paramLine):
        """
        Param:Name,Type,DefaultValue,MinValue,MaxValue,Unit,Choices,Prompt
        Param:R,y,str,1K,,,Ohm,,Value
        """
        items = [item.strip() for item in paramLine.split(',')]
        parName, parUsedInNetlist, parType, defVal, minVal, maxVal, unit, choices, prompt = items
        self.name = parName
        self.usedInNetlist = parUsedInNetlist.lower() == 'y'
        self.type = parType.lower()
        self.defVal = defVal
        self.minVal = None if len(minVal) == 0 else EngNum(minVal)
        self.maxVal = None if len(maxVal) == 0 else EngNum(maxVal)
        self.value = defVal
        self.unit = unit
        self.choices = choices.split()
        self.prompt = prompt

    def getPrompt(self):
        return self.prompt

    def getName(self):
        return self.name

    def isUsedInNetlist(self):
        return self.usedInNetlist
    def getValue(self):
        return self.value

    def toPrevJSON(self):
        ret = {}
        for k in self.__dict__:
            v = getattr(self, k)
            if type(v) is EngNum:
                ret[k] = v.__repr__()
            else:
                ret[k] = v
        return ret

    def make_by_JSON(self, jsn):
        for k in self.__dict__:
            setattr(self, k, jsn[k])
        self.minVal = None if self.minVal is None else EngNum(self.minVal)
        self.maxVal = None if self.maxVal is None else EngNum(self.maxVal)


DEVNAME_HEAD_MAPPING = {
    'capacitor': 'C',
    'resistor': 'R',
    'inductor': 'L',
    'diode': 'D',
    'current source': 'I',
    'voltage source': 'V',
    'bjt': 'Q',
    'mos': 'M',
    'hv_mos': 'M',
    'source': 'E',
    'switch': 'W',
}