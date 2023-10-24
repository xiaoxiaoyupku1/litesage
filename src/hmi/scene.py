from PySide6.QtCore import (Qt, QPointF)
from PySide6.QtGui import (QPolygonF, QPen, QColor)
from PySide6.QtWidgets import (QGraphicsScene)

from src.hmi.text import ParameterText, SimulationCommandText
from src.hmi.dialog import NetlistDialog, SimulationCommandDialog
from src.hmi.line import Line, Wire, WireSegment, WireList
from src.hmi.rect import Rect, DesignBorder, SymbolPin
from src.hmi.polygon import Polygon, Pin
from src.hmi.ellipse import Circle,WireConnection
from src.hmi.symbol import Symbol
from src.hmi.group import SchInst
from src.tool.device import getDeviceInfos
from src.tool.netlist import createNetlist, getAllUsedModels
from src.tool.design import Design
from src.tool.status import setStatus
from src.tool.simulate import SimTrackThread, SigTrackThread, GdsTrackThread
from src.tool.simulate import runSimulation, getSigResult, getGdsResult
from src.tool.network import Gateway
from src.waveform import WaveformViewer
import json


class SchScene(QGraphicsScene):
    def __init__(self, parent=None):
        super().__init__()
        self.user = None if parent is None else parent.user

        self.enableDel = False  # delete mode
        self.cursorSymb = None  # SchInst or Pin or Design
        self.cursorDesign = None
        self.insertSymbType = None  # type of component to insert
        self.insertSymbName = None  # insert symbol name (from lib file)
        self.widgetMouseMove = None  # widget with moving mouse
        self.designTextLines = None  # list of strings: user-defined design in rectangle
        self.symbols: list[SchInst] = []  # list of all symbols, a symbol = list of shapes
        self.designs: list[Design] = [] # list of saved designs (not in editing)
        self.editDesign: Design = None
        self.simtexts: list[SimulationCommandText] = [] # list of simulation command texts
        self.netlist = [] # list of netlist text lines

        self.wireStartPos = None  # starting point for adding wire
        self.wireList = WireList(self)
        self.currentWire = Wire(self)

        self.rectStartPos = None  # starting point for adding design rect
        self.editDesign = None  # rectangle surrounding the design
        self.scale = 15.0  # scaling coefficient
        self.sceneSymbRatio = 125 / self.scale  # x / 50 = 62.5 * 2 / 750
        self.gridOn = True  # flag grid
        self.gridPen = None
        self.isThumbnail = False

        self.basicSymbols = None  # basic ideal symbols
        self.basicSymbolNames = None  # to filter symbols for user to choose
        self.basicDevInfo = None
        self.initBasicDevices()
        self.pdkSymbols = None  # pdk symbols
        self.pdkDevInfo = None
        self.ipSymbols = None  # ip symbols
        self.ipDevInfo = None
        self.designSymbols: dict = None # all designs in ./project/

        self.wavWin = None
        self.layWin = None

        self.simTrackThread = SimTrackThread()
        self.sigTrackThread = SigTrackThread()
        self.gdsTrackThread = GdsTrackThread()
        self.gateway = None
        self.remoteNetlistPath = None
        self.setSimTrack = False

    def initBasicDevices(self):
        if self.basicSymbols is None or self.basicDevInfo is None:
            self.basicSymbols = Symbol.parse('basic')
            self.basicDevInfo = getDeviceInfos('basic')
            self.basicSymbolNames = sorted(name for name in self.basicSymbols.keys()
                                           if name != 'GND')

    def initPdkDevices(self):
        if self.pdkSymbols is None or self.pdkDevInfo is None:
            self.pdkSymbols = Symbol.parse('pdk')
            self.pdkDevInfo = getDeviceInfos('pdk')

    def initIpDevices(self):
        if self.ipSymbols is None or self.ipDevInfo is None:
            self.ipSymbols = Symbol.parse('ip')
            self.ipDevInfo = getDeviceInfos('ip')

    def initDesignDevices(self):
        if self.designSymbols is None:
            self.designSymbols = Design.loadAllDesigns()

    def keyPressEvent(self, event) -> None:
        if event.key() == Qt.Key_Escape:
            if self.insertSymbType == 'W':
                '''
                pos, scenePos = self.draw_wire_move_event_pos
                new_event = QGraphicsSceneMouseEvent(QGraphicsSceneMouseEvent.GraphicsSceneMouseDoubleClick)
                new_event.setPos(pos)
                new_event.setScenePos(scenePos)
                new_event.setButton(Qt.MouseButton.LeftButton)
                main = self.views()[0].parent()
                new_event = QMouseEvent(type=QEvent.MouseButtonDblClick, localPos=main.pos(), button=Qt.LeftButton, buttons=Qt.LeftButton, modifiers=Qt.KeyboardModifier.NoModifier)
                app = main.app
                app.sendEvent(main,new_event)
                #self.sendEvent(self, new_event)
                '''
                if self.widgetMouseMove is not None:
                    self.removeItem(self.widgetMouseMove)
                self.endWire()
                self.cleanCursorSymb()
            else:
                self.cleanCursorSymb()
        elif event.key() == Qt.Key_Delete:
            self.delSymb()

    def delSymb(self):
        self.cleanCursorSymb()
        for shape in self.selectedItems():
            if isinstance(shape, WireSegment):
                shape.delete()
            elif isinstance(shape, SchInst):
                pins = [item for item in shape.childItems() 
                        if isinstance(item, SymbolPin)]
                for pin in pins:
                    wiresegments = [item for item in pin.collidingItems() 
                                    if isinstance(item, WireSegment)]
                    for wiresegment in wiresegments:
                        wiresegment.removePin(pin)
                if shape in self.symbols:  # wire is not included
                    self.symbols.remove(shape)
                self.removeItem(shape)
            elif isinstance(shape, DesignBorder):
                shape.delete()
            elif isinstance(shape, Pin):
                shape.delete()
            elif isinstance(shape, SimulationCommandText):
                self.removeItem(shape)
                self.simtexts.remove(shape)
            else:
                self.removeItem(shape)
        setStatus('Delete items')

    def roundPos(self, origX, origY):
        posx1 = int(origX / self.sceneSymbRatio) * self.sceneSymbRatio
        posx2 = posx1 + self.sceneSymbRatio
        posx3 = posx1 - self.sceneSymbRatio

        posy1 = int(origY / self.sceneSymbRatio) * self.sceneSymbRatio
        posy2 = posy1 + self.sceneSymbRatio
        posy3 = posy1 - self.sceneSymbRatio

        minDist = None
        for posxi in (posx1, posx2, posx3):
            for posyi in (posy1, posy2, posy3):
                dist = (origX - posxi) ** 2 + (origY - posyi) ** 2
                if minDist is None or dist < minDist:
                    minDist = dist
                    posx, posy = posxi, posyi

        return posx, posy

    def mousePressEvent(self, event):
        if self.enableDel:
            pass
        else:
            if self.insertSymbType in ['basic', 'pdk', 'ip']:
                self.wireStartPos = None
                self.drawSymbol(event, self.insertSymbName, self.insertSymbType)
                setStatus('Add device {}'.format(self.insertSymbName))
            else:
                if self.insertSymbType == 'R':
                    self.wireStartPos = None
                    self.drawRes(event)
                    setStatus('Add device RES')
                elif self.insertSymbType == 'V':
                    self.wireStartPos = None
                    self.drawVsrc(event)
                    setStatus('Add device VSRC')
                elif self.insertSymbType == 'W':
                    self.drawWire(event)
                elif self.insertSymbType == 'P':
                    self.drawPin(event)
                    setStatus('Add pin')
                elif self.insertSymbType == 'RECT':
                    self.drawRect(event)
                    setStatus('Add design border')
                elif self.insertSymbType == 'Design':
                    self.drawDesign(event)
                    setStatus('Add design')
                elif self.insertSymbType == 'S':
                    self.drawSim(event)
                    setStatus('Add simulation command')
        return super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.cursorSymb is None:
            if self.insertSymbType == 'R':
                self.drawRes(event)
            elif self.insertSymbType == 'V':
                self.drawVsrc(event)
            elif self.insertSymbType == 'P':
                self.drawPin(event)
            elif self.insertSymbType in ['basic', 'pdk', 'ip']:
                self.drawSymbol(event, self.insertSymbName, self.insertSymbType)
            elif self.insertSymbType == 'W':
                #self.draw_wire_move_event_pos = (event.pos(), event.scenePos())
                self.drawWire(event, mode='move')
            elif self.insertSymbType == 'RECT':
                self.drawRect(event, mode='move')
            elif self.insertSymbType == 'Design':
                self.drawDesign(event)
            elif self.insertSymbType == 'S':
                self.drawSim(event, mode='move')
        else:
            curPos = event.scenePos()
            posx, posy = self.roundPos(curPos.x(), curPos.y())
            if isinstance(self.cursorSymb, list):
                for sym in self.cursorSymb:
                    sym.setPos(posx,posy)
            else:
                self.cursorSymb.setPos(posx, posy)

        return super().mouseMoveEvent(event)

    def mouseDoubleClickEvent(self, event):
        self.endWire()
    
    def cancelWire(self):
        if self.insertSymbType == 'W':
            self.wireStartPos = None

    def endWire(self):
        if self.insertSymbType == 'W':
            self.wireStartPos = None
            self.currentWire.complete()
            self.currentWire = Wire(self)
            setStatus('Add wire')

    def drawDesign_bk(self, event):
        if self.cursorSymb is not None:
            self.designs.append(self.cursorDesign)
        self.cursorSymb = []
        design = Design(self)
        self.cursorDesign = design
        design.make_by_lines(self.designTextLines, self.getNextNetIndex())
        for sym in design.symbols:
            self.addItem(sym)
            self.cursorSymb.append(sym)

        self.addItem(design.rect)
        self.cursorSymb.append(design.rect)

        for wire in design.wireList.wirelist:
            for seg in wire.getSegments():
                self.addItem(seg)
                self.cursorSymb.append(seg)

        for pn in design.Pins:
            self.addItem(pn)
            self.cursorSymb.append(pn)

        for conn in design.connections:
            self.addItem(conn)
            self.cursorSymb.append(conn)

        for sym in self.cursorSymb:
            sym.setPos(event.scenePos())


    def drawDesign(self, event, designModel=None):
        if self.cursorSymb is not None:
            self.designs.append(self.cursorDesign)
        self.cursorSymb = None
        design = Design(self)
        self.cursorDesign = design
        if designModel is None:
            design.make_by_lines(self.designTextLines, self.getNextNetIndex())
        else:
            design.make_by_lines(self.designSymbols[designModel], self.getNextNetIndex())
        design.make_group()
        self.cursorSymb=design.group
        if type(event) is list:
            self.cursorSymb.setPos(*event)
        else:
            self.cursorSymb.setPos(event.scenePos())

    def drawDesign_bk(self, event):
        self.cursorSymb = []
        for itemDef in self.designTextLines:
            itemDef = itemDef.rstrip()
            name, parameters = itemDef.split(':')

            if name == 'Line':
                ps = [float(p) for p in parameters.split(',')]
                item = Line(*ps)

            elif name == 'Rect':
                ps = [float(p) for p in parameters.split(',')]
                item = Rect(*ps)

            elif name == 'Polygon' or name == "Pin":
                points = parameters.split(';')
                polygonf = QPolygonF()
                for point in points:
                    point_array = [float(i) for i in point.split(',')]
                    polygonf.append(QPointF(*point_array))
                item = Polygon(polygonf)
                if name == "Pin":
                    item.setPen(QPen('red'))
                    item.setBrush(QColor('red'))

            elif name == 'Circle':
                ps = [float(p) for p in parameters.split(',')]
                item = Circle(*ps)

            elif name == 'RECT':
                ps = [float(p) for p in parameters.split(',')]
                item = DesignBorder(*ps)

            elif name == 'Wire':
                ps = [float(p) for p in parameters.split(',')]
                item = Line(*ps)
                item.setPen(QColor('blue'))

            elif name == 'Parameter':
                n, v, x, y = parameters.split(',')
                item = ParameterText('    ' + n + '\n\n    ' + v)
                item.posx = x
                item.posy = y

            self.addItem(item)
            self.cursorSymb.append(item)

            posx = event.scenePos().x()
            posy = event.scenePos().y()
            if isinstance(item, ParameterText):
                posx += float(item.posx)
                posy += float(item.posy)
            item.setPos(posx, posy)

        self.symbols.append(self.cursorSymb)

    def drawSymbol(self, event, name, symbType='basic'):
        if symbType == 'basic':
            symbols = self.basicSymbols
            devinfo = self.basicDevInfo
        elif symbType == 'pdk':
            symbols = self.pdkSymbols
            devinfo = self.pdkDevInfo
        else:
            symbols = self.ipSymbols
            devinfo = self.ipDevInfo
        self.cursorSymb = []

        inst = SchInst()
        nextNetIndex = self.getNextNetIndex()
        shapes = symbols[name].parts
        inst.draw(self, name, shapes, devinfo, nextNetIndex, self.isThumbnail)

        self.addItem(inst)
        if isinstance(event, list):
            inst.setPos(*event)
        else:
            inst.setPos(event.scenePos())
        self.cursorSymb = inst
        self.symbols.append(self.cursorSymb)

    def drawRes(self, event):
        self.drawSymbol(event, 'RES', 'basic')

    def drawVsrc(self, event):
        self.drawSymbol(event, 'VSRC', 'basic')

    def drawPin(self, event):
        if self.cursorSymb is not None:
            self.cursorSymb.check_design(self.editDesign)

        iopin = Pin(scale=self.scale)
        self.addItem(iopin)
        iopin.setPos(event.scenePos())
        self.cursorSymb = iopin

    def cleanCursorSymb(self):
        if self.cursorSymb is not None:
            if isinstance(self.cursorSymb, list):
                for sym in self.cursorSymb:
                    self.removeItem(sym)
            else:
                self.removeItem(self.cursorSymb)
            if self.cursorSymb in self.symbols:
                self.symbols.remove(self.cursorSymb)
            self.cursorSymb = None
        self.insertSymbType = 'NA'
        self.wireStartPos = None
        self.rectStartPos = None

    def drawWire(self, event, mode=None):
        # mode: 'press', 'move'
        #if type(event) == QKeyEvent:
        curPos = event.scenePos()
        curX, curY = self.roundPos(curPos.x(), curPos.y())

        if self.widgetMouseMove is not None:
            self.removeItem(self.widgetMouseMove)

        if self.wireStartPos is None:
            if mode != 'move':
                self.wireStartPos = [curX, curY]
            return

        diffX = abs(curX - self.wireStartPos[0])
        diffY = abs(curY - self.wireStartPos[1])
        if diffX <= diffY:
            endPos = [self.wireStartPos[0], curY]
        else:
            endPos = [curX, self.wireStartPos[1]]
        line = self.wireStartPos + endPos
        wireseg = WireSegment(*line)
        self.addItem(wireseg)

        if mode == 'move':
            self.widgetMouseMove = wireseg
        else:
            self.wireStartPos = endPos
            self.widgetMouseMove = None
            wireseg.addPins()
            self.currentWire.add(wireseg)

    def drawRect(self, event, mode=None):
        # mode: 'press', 'move'
        curPos = event.scenePos()
        curX, curY = self.roundPos(curPos.x(), curPos.y())

        if self.widgetMouseMove is not None:
            self.removeItem(self.widgetMouseMove)

        if self.rectStartPos is None:
            if mode != 'move':
                self.rectStartPos = [curX, curY]
            return

        # leftTop is (0, 0)
        width = abs(curX - self.rectStartPos[0])
        height = abs(curY - self.rectStartPos[1])
        startX = min(curX, self.rectStartPos[0])
        startY = min(curY, self.rectStartPos[1])
        rect = DesignBorder(startX, startY, width, height)
        self.addItem(rect)

        if mode == 'move':
            self.widgetMouseMove = rect
        else:
            self.rectStartPos = None
            self.editDesign = Design(self, rect=rect)
            self.widgetMouseMove = None
            self.insertSymbType = 'NA'

    def drawSim(self, event, mode=None):
        # mode: 'press', 'move'
        curPos = event.scenePos()
        posx, posy = self.roundPos(curPos.x(), curPos.y())
        self.cursorSymb = []
        if mode != 'move':
            return False
        dialog = SimulationCommandDialog(None, text='')
        result = dialog.exec()
        if result != dialog.accepted:
            return False

        item = SimulationCommandText(dialog.command)
        item.setPos(posx, posy)
        self.addItem(item)
        self.cursorSymb.append(item)
        self.simtexts.append(item)

    def drawGnd(self, event):
        self.drawSymbol(event, 'GND', 'basic')

    def drawBackground(self, painter, rect):
        if self.gridPen is None:
            pen = QPen()
            pen.setCapStyle(Qt.RoundCap)
            pen.setColor('lightgray')
            self.gridPen = pen

        if self.gridOn:
            painter.setPen(self.gridPen)
            ratio = self.sceneSymbRatio * 3
            startX = int(rect.x() / ratio) - 1
            startY = int(rect.y() / ratio) - 1
            endX = int(rect.right() / ratio) + 1
            endY = int(rect.bottom() / ratio) + 1
            for posx in range(startX, endX, 1):
                posx *= ratio
                for posy in range(startY, endY, 1):
                    posy *= ratio
                    painter.drawPoint(posx, posy)

    def toggleGrid(self):
        self.gridOn = not self.gridOn
        self.update()

    def showNetlist(self):
        self.netlist = createNetlist(self)
        dialog = NetlistDialog(None, self.netlist)
        setStatus('Create netlist')
        dialog.exec()

    def checkPreSim(self):
        # check used models and user rights
        bannedModels = []
        found = []
        if self.user.getLevel() == 3:
            # no need to check
            return True
        elif self.user.getLevel() == 2:
            bannedModels = list(self.ipSymbols.keys())
        elif self.user.getLevel()  == 1:
            bannedModels = list(self.pdkSymbols.keys()) + list(self.ipSymbols.keys())
        
        for model in getAllUsedModels():
            if model in bannedModels:
                found.append(model)
        
        if len(found) > 0:
            setStatus('Cannot run simulation with {}, '.format(' '.join(found)) +
                      'please update your account',
                      timeout=0)
            return False

        # check simulation analysis
        found = [line for line in self.netlist
                 if line.lower().startswith(('.tran ', '.ac ', '.dc '))]
        if len(found) == 0:
            setStatus('Cannot find any analysis, please add simulation commnd')
            return False
        elif len(found) > 1:
            setStatus('Multiple analyses found, please use only one')
            return False
        return True

    def runSim_test(self):
        self.wavWin = WaveformViewer()
        self.wavWin.showWindowAndOpenWave('test.raw')

    def runSim(self):
        self.initPdkDevices()
        self.initIpDevices()
        self.netlist = createNetlist(self)

        checked = self.checkPreSim()
        self.simTrackThread.checked = checked
        if not checked:
            return

        if self.gateway is None:
            self.gateway = Gateway()
        self.remoteNetlistPath = runSimulation(self.gateway, self.netlist)
        setStatus('Start simulation', timeout=0)

        self.simTrackThread.setTrack(self.gateway, self.remoteNetlistPath)
        self.simTrackThread.simprep.connect(self.showSimResult)
        self.simTrackThread.start()

    def showSimResult(self, simprep):
        setStatus(self.simTrackThread.message, timeout=0)
        if simprep == 0:
            # success
            self.simTrackThread.simprep.disconnect()
            self.simTrackThread.quit()

            self.sigTrackThread.setTrack(self.gateway, self.remoteNetlistPath)
            self.sigTrackThread.sigprep.connect(self.showSigResult)
            self.sigTrackThread.start()

        elif simprep == -1:
            self.simTrackThread.simprep.disconnect()
            self.simTrackThread.quit()
            # fail
        elif simprep == 1:
            # on-going
            pass
        else:
            assert 0, 'invalid output format from getSimStatus'

    def showSigResult(self, sigprep):
        if sigprep == 0:
            self.sigTrackThread.sigprep.disconnect()
            self.sigTrackThread.quit()

            dataFile = getSigResult(self.gateway, self.remoteNetlistPath)
            self.wavWin.showWindowAndOpenWave(dataFile, 'full')

            self.gdsTrackThread.setTrack(self.gateway, self.remoteNetlistPath)
            self.gdsTrackThread.gdsprep.connect(self.showGdsResult)
            self.gdsTrackThread.start()
            return

    def showGdsResult(self, gdsprep):
        if gdsprep == 0:
            self.gdsTrackThread.gdsprep.disconnect()
            self.gdsTrackThread.quit

            dataFile = getGdsResult(self.gateway, self.remoteNetlistPath)
            self.layWin.show_window_and_open_gds(dataFile)

    def clear(self):
        self.symbols = []
        super().clear()

    def anyUnSavedDesign(self):
        return False

    def getNextNetIndex(self):
        idx = 1
        for inst in self.symbols:
            for net in inst.conns.values():
                if net.startswith('net'):
                    try:
                        netIdx = int(net[3:])
                        if netIdx >= idx:
                            idx = netIdx + 1
                    except:
                        continue
        for wire in self.wireList.wirelist:
            net = wire.getName()
            if net is None:
                continue
            elif net.startswith('net'):
                try:
                    netIdx = int(net[3:])
                    if netIdx >= idx:
                        idx = netIdx + 1
                except:
                    continue 
        for design in self.designs:
            for net in design.conns.values():
                if net.startswith('net'):
                    try:
                        netIdx = int(net[3:])
                        if netIdx >= idx:
                            idx = netIdx + 1
                    except:
                        continue
        return idx



    def dumpSch(self, filePath : str) -> None:
        centerX: float = 0
        centerY: float = 0

        with open(filePath, 'w') as f:

            f.write('Wires:')
            wires = []
            for wire in self.wireList.wirelist:
                wires.append(wire.toPrevJSON(centerX, centerY))
            f.write(json.dumps(wires))
            f.write('\n')

            f.write('Connections:')
            conns = set()
            for wire in self.wireList.wirelist:
                for seg in wire.getSegments():
                    conns.update(seg.connections)
            conns_list = []
            for conn in conns:
                conns_list.append(conn.toPrevJSON(centerX, centerY))
            f.write(json.dumps(conns_list))
            f.write('\n')

            f.write("Designs:")
            design_list = []
            for design in self.designs:
                design_dict = {'model':design.model,
                               'name':design.name,
                               'x':design.group.x(),
                               'y':design.group.y(),
                               'scale':design.group.scale(),
                               'm11':design.group.transform().m11(),
                               'm22':design.group.transform().m22(),
                               'show':design.show.value
                               }
                design_list.append(design_dict)
            f.write(json.dumps(design_list))
            f.write('\n')

            f.write("Simulation:")
            sim_list=[]
            for sim in self.simtexts:
                sim_list.append(sim.toPrevJSON())
            f.write(json.dumps(sim_list))
            f.write('\n')

            scale = self.scale
            for symbol in self.symbols:
                f.write('Symbol:')
                sym = symbol.toPrevJSON(centerX, centerY)
                f.write(json.dumps(sym))
                f.write("\n")


    def makeSch(self, lines: list) -> None:

        #simulations:
        jsn = json.loads(lines[3].split(':', maxsplit=1)[1])
        if len(jsn) > 0:
            for sim in jsn:
                item = SimulationCommandText(sim['text'])
                item.setPos(sim['x'],sim['y'])
                self.addItem(item)
                self.simtexts.append(item)
        #symbols
        for sym_line in lines[4:]:
            jsn = json.loads(sym_line.split(':', maxsplit=1)[1])
            symbol = SchInst()
            symbol.make_by_JSON(jsn, self)
            self.symbols.append(symbol)
            self.addItem(symbol)

        #wires
        jsn = json.loads(lines[0].split(':', maxsplit=1)[1])
        self.wireList = WireList(self)
        for wr in jsn:
            wire = Wire(self)
            wire.make_by_JSON(wr)
            self.wireList.append(wire, check=False)

        for wire in self.wireList.wirelist:
            for seg in wire.getSegments():
                self.addItem(seg)

        #connections of wires
        jsn = json.loads(lines[1].split(':', maxsplit=1)[1])
        for cnn in jsn:
            conn = WireConnection()
            conn.make_by_JSON(cnn)
            self.addItem(conn)

        #designs
        jsn = json.loads(lines[2].split(':', maxsplit=1)[1])
        if len(jsn) > 0:
            self.initDesignDevices()
            for design_dict in jsn:
                for model, lines in self.designSymbols.items():
                    if model == design_dict['model']:
                        design = Design(self)
                        design.make_by_lines(lines, self.getNextNetIndex())
                        design.make_group()
                        design.group.setPos(design_dict['x'], design_dict['y'])
                        design.name = design_dict['name']
                        design.setScale(design_dict['scale'])
                        t = design.group.transform()
                        t.scale(design_dict['m11'], design_dict['m22'])
                        design.group.setTransform(t)
                        design.setShow(Qt.CheckState(design_dict['show']))
                        self.designs.append(design)
                        break


