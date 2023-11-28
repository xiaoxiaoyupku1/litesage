import os
from time import sleep
from tempfile import NamedTemporaryFile
from pickle import load
from PySide6.QtCore import QThread, Signal

from src.tool.network import getIpAddr
from src.tool.sys import getCurrentTime
from src.tool.config import RETR_SIM_STATUS_INTVL


class SimTrackThread(QThread):
    simprep = Signal(int)   # simulation status

    def __init__(self):
        super().__init__()
        self.checked = False
        self.gateway = None
        self.remoteNetlistPath = None
        self.message = ''

    def setTrack(self, gateway, remoteNetlistPath):
        self.gateway = gateway
        self.remoteNetlistPath = remoteNetlistPath

    def run(self):
        if self.checked:
            resp, self.message = checkSimStatus(self.gateway, self.remoteNetlistPath)
            self.simprep.emit(resp)


class SigTrackThread(QThread):
    sigprep = Signal(int)

    def __init__(self):
        super().__init__()
        self.gateway = None
        self.remoteNetlistPath = None

    def setTrack(self, gateway, remoteNetlistPath):
        self.gateway = gateway
        self.remoteNetlistPath = remoteNetlistPath

    def run(self):
        resp = checkSigResult(self.gateway, self.remoteNetlistPath)
        self.sigprep.emit(resp)


class GdsTrackThread(QThread):
    gdsprep = Signal(int)

    def __init__(self):
        super().__init__()
        self.gateway = None
        self.remoteNetlistPath = None

    def setTrack(self, gateway, remoteNetlistPath):
        self.gateway = gateway
        self.remoteNetlistPath = remoteNetlistPath

    def run(self):
        resp = checkGdsResult(self.gateway, self.remoteNetlistPath)
        self.gdsprep.emit(resp)


def runSimulation(gateway, netlist):
    timeTag = getCurrentTime()
    liblines = [
        '.lib "D:\\process\\btpr-c140\\current\\lib\\process\\btpr-c140.lib"',
        '.lib "D:\\process\\btpr-c140\\current\\lib\\process\\btpr-c140_parasitic_devices.lib"',
        '.lib "D:\\process\\btpr-c140\\current\\lib\\process\\btpr-c140_process_corner.lib"',
        '.lib "D:\\process\\btpr-c140\\current\\lib\\ecs\\analog\\netlists\\btpr-c140.spi"',
        '.lib "D:\\process\\btpr-c140\\current\\lib\\ecs\\analog\\ip.spi"',
        '.param rel_mnl=0 rel_mpl=0 rel_RC=0',
        '.param rel_bip=rel_mnl rel_DIO=rel_mnl',
        '.param rel_mnh=rel_mnl rel_mph=rel_mpl',
        '.options fastaccess list acct',
        'rbkd_{} $g_cbkd $g_csub 1m'.format(timeTag),
        'rsub_{} $g_csub sgnd 1m'.format(timeTag),
        'vsgnd_{} sgnd 0 0'.format(timeTag),
    ]
    netlist = ['*'] + liblines + netlist

    localPath = ''
    fp = NamedTemporaryFile(delete=False) 
    try:
        fp.write(bytes('\n'.join(netlist), encoding='utf-8'))
        fp.seek(0)
        localPath = fp.name
        remotePath = '{}_{}_{}.sp'.format(timeTag,
                                          getIpAddr(public=True), 
                                          getIpAddr(public=False))
        remotePath = os.path.join('/netlists', remotePath)

        gateway.uploadFile(localPath, remotePath)
    finally:
        fp.close()
        if os.path.isfile(localPath):
            os.remove(localPath)

    return remotePath

def checkSimStatus(gateway, remoteNetlistPath):
    tag = os.path.splitext(os.path.basename(remoteNetlistPath))[0]
    origNetlistPath = remoteNetlistPath
    origNetlistStatus = os.path.splitext(origNetlistPath)[0] + '.status'
    origNetlistStatus = os.path.join(r'/netlists', tag + '.status')
    failNetlistPath = os.path.join(r'/simFailed', tag + '.sp')
    failNetlistStatus = os.path.join(r'/simFailed', tag + '.status')
    passNetlistPath = os.path.join(r'/simProcessed', tag + '.sp')

    result = None
    message = ''
    # 0: success, -1: failure, 1: simulating
    interval = 0.5
    while result is None:
        if gateway.isFile(failNetlistPath):
            lines = gateway.readFile(failNetlistStatus)
            message = 'Simulation failed: ' + ' '.join(lines)
            result = -1
        elif gateway.isFile(passNetlistPath):
            message = 'Simulation succeeded'
            result = 0
        elif gateway.isFile(origNetlistPath) and gateway.isFile(origNetlistStatus):
            lines = gateway.readFile(origNetlistStatus)
            message = 'Simulation on-going'
            message = message + lines[0] if len(lines) > 0 else message
            # TODO: read origNetlistStatus and update interval value
            # setStatus(message)
        sleep(interval)
    return result, message

# def getSimStatus(gateway, remoteNetlistPath):
#     # 0: success, -1: failure
#     success = None
#     interval = RETR_SIM_STATUS_INTVL
# 
#     def _readStatusFile(interval, success):
#         for line in gateway.readFile(remoteStatusPath):
#             if line.startswith('Simulation left time'):
#                 lefttime = float(line.split('left time')[1].strip())  # left time always in seconds
#                 interval = lefttime / 10.0
#                 setStatus(line, timeout=0)
#             elif 'success' in line.lower():
#                 success = 0
#                 setStatus(line)
#             elif 'fail' in line.lower():
#                 success = -1
#                 setStatus(line)
#         return interval, success
# 
#     name = os.path.splitext(remoteNetlistPath)[0]
#     remoteStatusPath = name + '.status'
# 
#     while success is None:
#         sleep(interval)
#         interval, success = _readStatusFile(interval, success)
# 
#     return success


# def getSigResult(gateway, remoteNetlistPath):
#     sigprep = None
# 
#     def _readSigFile(sigprep):
#         for line in gateway.readFile(remoteSigPath):
#             if line.startswith('finish dump all'):
#                 sigprep = 1
#             elif line.startswith('finish dump names'):
#                 sigprep = 2
#             elif line.startswith('finish dump single'):
#                 sigprep = 3
#         return sigprep
# 
#     name = os.path.splitext(remoteNetlistPath)[0]
#     remoteSigPath = name + '.sigStatus'
# 
#     while sigprep is None:
#         sleep(1)
#         sigprep = _readSigFile(sigprep)
# 
#     return sigprep

def checkSigResult(gateway, remoteNetlistPath):
    # 0:success, -1: failure
    baseName = os.path.splitext(os.path.basename(remoteNetlistPath))[0]
    sigFile = os.path.join(r'/waves', baseName + '.sig')

    interval = 0.5
    while True:
        if gateway.isFile(sigFile):
            return 0
        sleep(interval)

def getSigResult(gateway, remoteNetlistPath):
    baseName = os.path.splitext(os.path.basename(remoteNetlistPath))[0]
    remoteSigPath = os.path.join(r'/waves', baseName + '.sig')
    localSig = NamedTemporaryFile(delete=False, suffix='.sig')
    localSigPath = localSig.name
    gateway.downloadFile(localSigPath, remoteSigPath)

    assert os.path.isfile(localSigPath)
    assert os.access(localSigPath, os.R_OK)
    with open(localSigPath, 'rb') as fport:
        data = load(fport)
    return data

def checkGdsResult(gateway, remoteNetlistPath):
    # 0:success, -1: failure
    baseName = os.path.splitext(os.path.basename(remoteNetlistPath))[0]
    sigFile = os.path.join(r'/LaGen/gdsS1', baseName + '.gds')

    interval = 0.5
    while True:
        if gateway.isFile(sigFile):
            return 0
        sleep(interval)

def getGdsResult(gateway, remoteNetlistPath):
    baseName = os.path.splitext(os.path.basename(remoteNetlistPath))[0]
    remoteGdsPath = os.path.join(r'/LaGen/gdsS1', baseName + '.gds')
    localGds = NamedTemporaryFile(delete=False, suffix='.gds')
    localGdsPath = localGds.name
    gateway.downloadFile(localGdsPath, remoteGdsPath)

    assert os.path.isfile(localGdsPath)
    assert os.access(localGdsPath, os.R_OK)
    return localGdsPath