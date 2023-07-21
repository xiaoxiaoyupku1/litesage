from src.hmi.group import SchInst

def createNetlist(scene):
    netlist = ['*']
    for inst in scene.symbols:
        if not isinstance(inst, SchInst):
            continue

        line = inst.name
        for p in inst.pins:
            line += ' {}'.format(inst.conns[p])
        line += ' {}'.format(inst.model)
        for param in inst.params:
            if param.isUsedInNetlist():
                if len(param.name) > 0:
                    expr = '{}={}'.format(param.name, param.value)
                else:
                    expr = param.value
                line += ' {}'.format(expr)
        netlist.append(line)

    return netlist