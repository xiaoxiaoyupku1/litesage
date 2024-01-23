import os
from sys import exit
from shutil import copy
from time import sleep
import subprocess
from src.tool.sys import getCurrentTime, readFile

from src.tool.config import (
    FTP_SIM_NETLIST_DIR, FTP_SIM_PASS_DIR, FTP_SIM_FAIL_DIR,
    FH_SIM_PROC_DIR, FH_SIM_WAVE_DIR, FTP_SIM_WAVE_DIR,
)
from src.tool.config import (
    FTP_LAY_NETLIST_DIR, FTP_LAY_PASS_DIR, FH_LAY_PROC_DIR,
    FH_LAY_GDS_S1_DIR, FTP_LAY_GDS_S1_DIR,
    FTP_LAY_GDS_S2_DIR, FH_LAY_GDS_S2_DIR,
)


class GatewayHandler():
    def __init__(self):
        self.simFtpNetlistDir = FTP_SIM_NETLIST_DIR
        self.simFtpPassDir = FTP_SIM_PASS_DIR
        self.simFtpFailDir = FTP_SIM_FAIL_DIR
        self.simFhProcDir = FH_SIM_PROC_DIR
        self.simFhWaveDir = FH_SIM_WAVE_DIR
        self.simFtpWaveDir = FTP_SIM_WAVE_DIR

        self.layFtpNetlistDir = FTP_LAY_NETLIST_DIR
        self.layFtpPassDir = FTP_LAY_PASS_DIR
        self.layFhProcDir = FH_LAY_PROC_DIR
        self.layFhGdsS1Dir = FH_LAY_GDS_S1_DIR
        self.layFtpGdsS1Dir = FTP_LAY_GDS_S1_DIR
        self.layFtpGdsS2Dir = FTP_LAY_GDS_S2_DIR
        self.layFhGdsS2Dir = FH_LAY_GDS_S2_DIR

        self.doneWaves = []
        self.doneStatus = []
        self.doneLayouts = []
        self.doneGdsS1s = []
        self.doneGdsS2s = []

        self.initDirs()

    def initDirs(self):
        for directory in (self.simFtpNetlistDir,
                          self.simFtpPassDir,
                          self.simFtpFailDir,
                          self.simFtpWaveDir):
            os.makedirs(directory, exist_ok=True)
        for directory in (os.path.dirname(self.layFtpNetlistDir),
                          self.layFtpNetlistDir,
                          self.layFtpPassDir,
                          self.layFtpGdsS1Dir,
                          self.layFtpGdsS2Dir):
            os.makedirs(directory, exist_ok=True)

    def checkReadPerm(self, filePath):
        while not os.access(filePath, os.R_OK):
            print('... waiting for reading permission of {}'.format(filePath))
            sleep(0.5)

    def grantFilePerm(self, filePath):
        command = 'icacls "{}" /grant Everyone:F /t /q'.format(filePath)
        subprocess.run(command, shell=True)

    def run(self):
        count = 0
        while True:
            sleep(0.5)
            self.checkSimStatus()
            self.checkSigResults()
            self.checkLayNetlist()
            self.checkGdsS1()
            self.checkGdsS2()
            count += 1 
            if count % 100000 == 0:
                count = 0
                self.doneWaves.clear()
                self.doneStatus.clear()
                self.doneLayouts.clear()
                self.doneGdsS1s.clear()
                self.doneGdsS2s.clear()

    def checkSimStatus(self):
        for baseName in os.listdir(self.simFtpNetlistDir):
            if baseName.endswith('.status'):
                ftpSts = os.path.join(self.simFtpNetlistDir, baseName)
                base = os.path.splitext(baseName)[0]
                ftpWave = os.path.join(self.simFtpNetlistDir, f'{base}.raw')
                ftpSp = os.path.join(self.simFtpNetlistDir, f'{base}.sp')

                ftpPassSp = os.path.join(self.simFtpPassDir, f'{base}.sp')
                ftpPassWave = os.path.join(self.simFtpPassDir, f'{base}.raw')
                ftpPassSts = os.path.join(self.simFtpPassDir, f'{base}.status')
                fhSp = os.path.join(self.simFhProcDir, f'{base}.sp')
                fhWave = os.path.join(self.simFhProcDir, f'{base}.raw')
                ftpFailSp = os.path.join(self.simFtpFailDir, f'{base}.sp')
                ftpFailSts = os.path.join(self.simFtpFailDir, f'{base}.status')

                self.checkReadPerm(ftpSts)
                self.checkReadPerm(ftpSp)
                if baseName not in self.doneStatus:
                    stsLines = [l for l in readFile(ftpSts)]
                    for line in stsLines:
                        line = line.lower()
                        if line.startswith('success') and os.path.isfile(ftpWave):
                            self.checkReadPerm(ftpWave)
                            now = getCurrentTime()
                            print(f'{now} simulation succeeded: {ftpSp}')
                            copy(ftpWave, fhWave)
                            self.grantFilePerm(fhWave)
                            copy(ftpWave, ftpPassWave)
                            if os.access(ftpWave, os.W_OK):
                                os.remove(ftpWave)

                            copy(ftpSp, fhSp)
                            self.grantFilePerm(fhSp)
                            copy(ftpSp, ftpPassSp)
                            if os.access(ftpSp, os.W_OK):
                                os.remove(ftpSp)

                            copy(ftpSts, ftpPassSts)
                            if os.access(ftpSts, os.W_OK):
                                os.remove(ftpSts)
                            print(f'{now} move sim output wave: {fhWave}')
                            break
                        
                        elif line.startswith('fail'):
                            now = getCurrentTime()
                            print(f'{now} simulation failed: {ftpSp}')
                            copy(ftpSp, ftpFailSp)
                            if os.access(ftpSp, os.W_OK):
                                os.remove(ftpSp)
                            copy(ftpSts, ftpFailSts)
                            if os.access(ftpSts, os.W_OK):
                                os.remove(ftpSts)
                            break

    def checkSigResults(self):
        for baseName in os.listdir(self.simFhWaveDir):
            if baseName.endswith('.sig'):
                fhWave = os.path.join(self.simFhWaveDir, baseName)
                self.checkReadPerm(fhWave)
                if baseName not in self.doneWaves:
                    ftpWave = os.path.join(self.simFtpWaveDir, baseName)
                    copy(fhWave, ftpWave)
                    now = getCurrentTime()
                    print(f'{now} sim signals generated: {ftpWave}')
                    if os.access(fhWave, os.W_OK):
                        os.remove(fhWave)
                    self.doneWaves.append(baseName)

    def checkLayNetlist(self):
        for baseName in os.listdir(self.layFtpNetlistDir):
            if baseName.endswith('.sp'):
                ftpSp = os.path.join(self.layFtpNetlistDir, baseName)
                self.checkReadPerm(ftpSp)
                if baseName not in self.doneWaves:
                    fhSp = os.path.join(self.layFhProcDir, baseName)
                    copy(ftpSp, fhSp)
                    ftpPassSp = os.path.join(self.layFtpPassDir, baseName)
                    copy(ftpSp, ftpPassSp)
                    now = getCurrentTime()
                    print(f'{now} netlist passed for auto-layout: {fhSp}')
                    if os.access(ftpSp, os.W_OK):
                        os.remove(ftpSp)
                    self.doneLayouts.append(baseName)

    def checkGdsS1(self):
        for baseName in os.listdir(self.layFhGdsS1Dir):
            if baseName.endswith('.gds'):
                fhGds = os.path.join(self.layFhGdsS1Dir, baseName)
                self.checkReadPerm(fhGds)
                if baseName not in self.doneGdsS1s:
                    ftpGds = os.path.join(self.layFtpGdsS1Dir, baseName)
                    copy(fhGds, ftpGds)
                    if os.access(fhGds, os.W_OK):
                        os.remove(fhGds)
                    now = getCurrentTime()
                    print(f'{now} gds s1 passed for auto-layout: {ftpGds}')
                    self.doneGdsS1s.append(baseName)

    def checkGdsS2(self):
        for baseName in os.listdir(self.layFtpGdsS2Dir):
            if baseName.endswith('.gds'):
                ftpGds = os.path.join(self.layFtpGdsS2Dir, baseName)
                self.checkReadPerm(ftpGds)
                if baseName not in self.doneGdsS2s:
                    fhGds = os.path.join(self.layFhGdsS2Dir, baseName)
                    copy(ftpGds, fhGds)
                    if os.access(ftpGds, os.W_OK):
                        os.remove(ftpGds)
                    now = getCurrentTime()
                    print(f'{now} gds s2 passed for auto-layout: {fhGds}')
                    self.doneGdsS2s.append(baseName)

        
def run():
    handler = GatewayHandler()
    try:
        handler.run()
    except KeyboardInterrupt:
        exit()