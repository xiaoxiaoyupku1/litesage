from src.hmi.group import SchInst
from src.tool.design import Design

ALL_USED_MODELS = []

def createNetlist(scene):
    """ SPICE format """
    netlist = []
    subckts, knownDesigns = [], []
    global ALL_USED_MODELS
    ALL_USED_MODELS = []

    for design in scene.designs:
        line = design.name
        for pin in design.pins:
            line += ' {}'.format(design.conns[pin])
        line += ' {}'.format(design.model)
        ALL_USED_MODELS.append(design.model)
        netlist.append(line)

        if design.model not in knownDesigns:
            line = '.subckt {} {}'.format(design.model, ' '.join(design.pins))
            subckts.append(line)
            insts = _createInstNetlist(design)
            subckts += insts
            subckts += ['.ends', '']
            knownDesigns.append(design.model)

    netlist += _createInstNetlist(scene)

    for simtext in scene.simtexts:
        netlist.append(simtext.toPlainText())

    return ['*'] + subckts + netlist


def _createInstNetlist(parent):
    global ALL_USED_MODELS
    netlist = []

    net_pin_mapping = {}
    if isinstance(parent, Design):
        for pin, net in parent.initial_conns.items():
            net_pin_mapping[net] = pin

    for inst in parent.symbols:
        if not isinstance(inst, SchInst):
            continue
        line = inst.name
        for p in inst.pins:
            line += ' {}'.format(net_pin_mapping.get(inst.conns[p], inst.conns[p]))
        line += ' {}'.format(inst.model)
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