import os
from time import sleep
from tempfile import NamedTemporaryFile
from PySide6.QtCore import QObject, Signal


from src.tool.network import getIpAddr
from src.tool.sys import getCurrentTime
from src.tool.status import setStatus
from src.tool.config import RETR_SIM_STATUS_INTVL


class SimTrackThread(QObject):
    success = Signal(int)

    def __init__(self):
        super().__init__()
        self.checked = False
        self.gateway = None
        self.remoteNetlistPath = None

    def setTrack(self, gateway, remoteNetlistPath):
        self.gateway = gateway
        self.remoteNetlistPath = remoteNetlistPath

    def trackSim(self):
        if self.checked:
            resp = getSimStatus(self.gateway, self.remoteNetlistPath)
            self.success.emit(resp)


def runSimulation(gateway, netlist):
    localPath = ''
    fp = NamedTemporaryFile(delete=False) 
    try:
        fp.write(bytes('\n'.join(netlist), encoding='utf-8'))
        fp.seek(0)
        localPath = fp.name
        remotePath = '{}_{}_{}.sp'.format(getCurrentTime(),
                                          getIpAddr(public=True), 
                                          getIpAddr(public=False))

        gateway.uploadFile(localPath, remotePath)
    finally:
        fp.close()
        if os.path.isfile(localPath):
            os.remove(localPath)

    return remotePath


def getSimStatus(gateway, remoteNetlistPath):
    # 0: success, -1: failure
    success = None
    interval = RETR_SIM_STATUS_INTVL

    def _readStatusFile(interval, success):
        for line in gateway.readFile(remoteStatusPath):
            if line.startswith('Simulation left time'):
                lefttime = float(line.split('left time')[1].strip())  # left time always in seconds
                interval = lefttime / 10.0
                setStatus(line, timeout=0)
            elif line == 'success':
                success = 0
                setStatus(line)
            elif line == 'fail':
                success = -1
                setStatus(line)
        return interval, success

    name = os.path.splitext(remoteNetlistPath)[0]
    remoteStatusPath = name + '.status'

    while success is None:
        sleep(interval)
        interval, success = _readStatusFile(interval, success)

    return success


def getSimResult(gateway, remoteNetlistPath):
    remoteDir = os.path.dirname(remoteNetlistPath)
    remoteWavePath = os.path.join(remoteDir, 'waveform.ac0')
    localWave = NamedTemporaryFile(delete=False, suffix='.ac0')
    localWavePath = localWave.name
    gateway.downloadFile(localWavePath, remoteWavePath)
    return localWavePath
    # return waveInfo