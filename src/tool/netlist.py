from src.hmi.group import SchInst
from src.tool.design import Design

ALL_USED_MODELS = []
ALL_IP_INSTS = []

def createNetlist(scene, viewOnly=False):
    """ SPICE format: viewOnly prettfies device model names if true """
    netlist = []
    comments = []
    subckts, knownDesigns = [], []
    global ALL_USED_MODELS
    ALL_USED_MODELS = []
    global ALL_IP_INSTS
    ALL_IP_INSTS = []

    gndNets = getActualLevelGndNets(scene)

    for design in scene.designs:
        line = design.name
        for pin in design.pins:
            conn = design.conns[pin]
            conn = '0' if conn in gndNets else conn
            line += ' {}'.format(conn)
        line += ' {}'.format(design.model)
        ALL_USED_MODELS.append(design.model)
        netlist.append(line)

        if design.model not in knownDesigns:
            line = '.subckt {} {}'.format(design.model, ' '.join(design.pins))
            subckts.append(line)
            insts = _createInstNetlist(design, design.name, viewOnly)
            subckts += insts
            subckts += ['.ends', '']
            knownDesigns.append(design.model)

    netlist += _createInstNetlist(scene, '', viewOnly)

    if len(scene.simtexts) > 0:
        netlist += ['']
        for simtext in scene.simtexts:
            netlist.append(simtext.toPlainText().strip())

    results = ['*'] + getIpInsts() + subckts + netlist
    return [ln.lower() for ln in results]


def _createInstNetlist(parent, parentName, viewOnly):
    global ALL_IP_INSTS
    global ALL_USED_MODELS
    netlist = []

    net_pin_mapping = {}
    if isinstance(parent, Design):
        for pin, net in parent.initial_conns.items():
            net_pin_mapping[net] = pin

    gndNets = getActualLevelGndNets(parent, net_pin_mapping=net_pin_mapping)

    for inst in parent.symbols:
        if not isinstance(inst, SchInst) or inst.model == 'GND':
            continue
        line = 'X' + inst.name if inst.isXInst() else inst.name

        if inst.isIp():
            instName = '{}:{}'.format(parentName, line) \
                       if len(parentName) > 0 else line
            ALL_IP_INSTS.append(instName)

        for p in inst.pins:
            conn = inst.conns[p]
            conn = net_pin_mapping.get(conn, conn)
            conn = '0' if conn in gndNets else conn
            line += ' {}'.format(conn)

        modelName = inst.model if viewOnly else inst.spmodel
        if inst.isModelVisible():
            line = patchGlobalNodes(line, inst.lib, inst.model)
            line += ' {}'.format(modelName)
        ALL_USED_MODELS.append(inst.model)
        for param in inst.params:
            if param.isUsedInNetlist():
                if len(param.name) > 0:
                    expr = ' {}={}'.format(param.name, param.value)
                else:
                    expr = param.value
                line += ' {}'.format(expr)
        netlist.append(line)

    return netlist


def getAllUsedModels():
    global ALL_USED_MODELS
    return list(set(ALL_USED_MODELS))


def getIpInsts():
    global ALL_IP_INSTS
    lines = ['* ip instance: '+i for i in ALL_IP_INSTS]
    return lines + ['']


def getActualLevelGndNets(parent, net_pin_mapping=None):
    gndNets = []
    if net_pin_mapping is None:
        net_pin_mapping = {}
        if isinstance(parent, Design):
            for pin, net in parent.initial_conns.items():
                net_pin_mapping[net] = pin

    for inst in parent.symbols:
        if inst.model == 'GND':
            p = inst.pins[0]
            gndNets.append(net_pin_mapping.get(inst.conns[p], inst.conns[p]))
    return gndNets


NO_PSB_LIST = [
    'RHR', 'RMET1', 'RMET2', 'RPOLY1', 'RFUSEM2', 'RFUSEPOLY',
    'ROPTION', 'RSMEAR', 'RSUB', 'IPROBE',
]
def patchGlobalNodes(line, lib, model):
    if lib == 'pdk' and model not in NO_PSB_LIST:
        line += ' $G_CSUB'
    return line
