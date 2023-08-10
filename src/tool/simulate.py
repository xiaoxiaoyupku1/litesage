import os
from tempfile import NamedTemporaryFile
from src.tool.network import Gateway
from src.tool.network import getIpAddr

HOST = '127.0.0.1'
PORT = 8080
USER = 'admin'
PASSWD = 'password'

def runSimulation(netlist):
    localPath = ''
    fp = NamedTemporaryFile(delete=False) 
    try:
        fp.write(bytes('\n'.join(netlist), encoding='utf-8'))
        fp.seek(0)
        localPath = fp.name
        baseName = os.path.basename(localPath)
        remotePath = '{}_{}.sp'.format(getIpAddr(), baseName)

        gtw = Gateway(HOST, PORT, USER, PASSWD)
        gtw.upload(localPath, remotePath)
        gtw.end()
    finally:
        fp.close()
        if os.path.isfile(localPath):
            os.remove(localPath)

    return remotePath


def getSimResult(remoteNetlistPath):
    assert remoteNetlistPath.endswith('.sp')
    remoteDir = os.path.dirname(remoteNetlistPath)
    remoteWavePath = os.path.join(remoteDir, 'waveform.ac0')
    localWave = NamedTemporaryFile(delete=False, suffix='.ac0')
    localWavePath = localWave.name
    gtw = Gateway(HOST, PORT, USER, PASSWD)
    gtw.downloadFile(localWavePath, remoteWavePath)
    gtw.end()
    return localWavePath