import os
from shutil import copy
from time import sleep
import subprocess
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from src.tool.sys import getCurrentTime, readFile
from src.tool.config import (
    FTP_NETLIST_PATH, FTP_SIM_PASS_PATH, FTP_SIM_FAIL_PATH, FTP_WAVE_PATH,
    FTP_LAGEN_PATH, FTP_LAGEN_S1_PATH, FTP_LAGEN_S2_PATH,
    FH_POST_PATH, FH_WAVE_PATH, FH_GDS_S1_PATH, FH_GDS_S2_PATH)


class GatewayHandler(FileSystemEventHandler):
    def __init__(self):
        self.netlistPath = FTP_NETLIST_PATH
        self.passPath = FTP_SIM_PASS_PATH
        self.failPath = FTP_SIM_FAIL_PATH
        self.wavePath = FTP_WAVE_PATH
        self.laGenPath = FTP_LAGEN_PATH
        self.laGenS1Path = FTP_LAGEN_S1_PATH
        self.laGenS2Path = FTP_LAGEN_S2_PATH

        os.makedirs(self.netlistPath, exist_ok=True)
        os.makedirs(self.passPath, exist_ok=True)
        os.makedirs(self.failPath, exist_ok=True)
        os.makedirs(self.wavePath, exist_ok=True)
        os.makedirs(self.laGenPath, exist_ok=True)
        os.makedirs(self.laGenS1Path, exist_ok=True)
        os.makedirs(self.laGenS2Path, exist_ok=True)

        self.fhPostPath = FH_POST_PATH
        self.fhWavePath = FH_WAVE_PATH
        self.fhGdsS1Path = FH_GDS_S1_PATH
        self.fhGdsS2Path = FH_GDS_S2_PATH

        super().__init__()

    def on_created(self, event):
        return
    
    def grantFilePerm(self, filePath):
        command = 'icacls "{}" /grant Everyone:F /t /q'.format(filePath)
        subprocess.run(command, shell=True)

    def fileInDir(self, filePath, dir):
        fileDir = os.path.dirname(filePath)

        dir1 = os.path.abspath(fileDir)
        dir2 = os.path.abspath(dir)

        dir1 = os.path.normcase(dir1)
        dir2 = os.path.normcase(dir2)

        return dir1 == dir2

    def on_modified(self, event):
        mfile = event.src_path
        if self.fileInDir(mfile, self.netlistPath):
            self._on_modified_netlist(event)
        # elif self.fileInDir(mfile, self.fhWavePath):
        #     self._on_modified_wave(event)
        # elif self.fileInDir(mfile, self.fhGdsS1Path):
        #     self._on_modified_gdss1(event)
        # elif self.fileInDir(mfile, self.laGenS2Path):
        #     self._on_modified_gdss2(event)

    def _on_modified_netlist(self, event):
        statusFile = event.src_path
        now = getCurrentTime()

        if not statusFile.endswith('.status'):
            return
        elif not os.path.isfile(statusFile):
            return

        while not os.access(statusFile, os.R_OK):
            print('... waiting for reading permission of {}'.format(statusFile))
            sleep(0.5)

        name = os.path.splitext(statusFile)[0]
        rawFile = name + '.raw'
        spFile = name + '.sp'
        statusFileNew = ''

        statusLines = [l for l in readFile(statusFile)]
        for line in statusLines:
            line = line.lower()
            if line.startswith('success') and os.path.isfile(rawFile):
                print('{} simulation success: {}'.format(now, spFile))
                print('{} sim output rawfile: {}'.format(now, rawFile))

                spBaseName = os.path.basename(spFile)
                spFileNew = os.path.join(self.passPath, spBaseName)
                if os.path.isfile(spFile) and not os.path.isfile(spFileNew):
                    spFilePost = os.path.join(self.fhPostPath, spBaseName)
                    copy(spFile, spFilePost)
                    self.grantFilePerm(spFilePost)
                    os.rename(spFile, spFileNew)

                rawBaseName = os.path.basename(rawFile)
                rawFileNew = os.path.join(self.passPath, rawBaseName)
                if os.path.isfile(rawFile) and not os.path.isfile(rawFileNew):
                    rawFilePost = os.path.join(self.fhPostPath, rawBaseName)
                    copy(rawFile, rawFilePost)
                    self.grantFilePerm(rawFilePost)
                    os.rename(rawFile, rawFileNew)
                os.remove(statusFile)
                break

            elif line.startswith('fail'):
                print('{} simulation failure: {}'.format(now, spFile))

                spBaseName = os.path.basename(spFile)
                spFileNew = os.path.join(self.failPath, spBaseName)
                if os.path.isfile(spFile) and not os.path.isfile(spFileNew):
                    os.rename(spFile, spFileNew)

                statusBaseName = os.path.basename(statusFile)
                statusFileNew = os.path.join(self.failPath, statusBaseName)
                if os.path.isfile(statusFile) and not os.path.isfile(statusFileNew):
                    os.rename(statusFile, statusFileNew)
                break
        return
    
    def _on_modified_wave(self, event):
        sigFile = event.src_path
        now = getCurrentTime()
        if not sigFile.endswith('.sig'):
            return
        elif not os.path.isfile(sigFile):
            return
        
        while not os.access(sigFile, os.W_OK):
            print('... waiting for reading permission of {}'.format(sigFile))
            sleep(0.5)

        print('{} wave parsing success: {}'.format(now, sigFile))
        sigBaseName = os.path.basename(sigFile)
        sigFileNew = os.path.join(self.wavePath, sigBaseName)
        if not os.path.isfile(sigFileNew):
            os.rename(sigFile, sigFileNew)

    def _on_modified_gdss1(self, event):
        gdsFile = event.src_path
        now = getCurrentTime()
        if not gdsFile.endswith('.gds'):
            return
        elif not os.path.isfile(gdsFile):
            return
        
        while not os.access(gdsFile, os.W_OK):
            print('... waiting for reading permission of {}'.format(gdsFile))
            sleep(0.5)

        print('{} gds s1 success: {}'.format(now, gdsFile))
        gdsBaseName = os.path.basename(gdsFile)
        gdsFileNew = os.path.join(self.laGenS1Path, gdsBaseName)
        if not os.path.isfile(gdsFileNew):
            os.rename(gdsFile, gdsFileNew)

    def _on_modified_gdss2(self, event):
        gdsFile = event.src_path
        now = getCurrentTime()
        if not gdsFile.endswith('.gds'):
            return
        elif not os.path.isfile(gdsFile):
            return
        
        print('{} gds s2 success: {}'.format(now, gdsFile))
        while not os.access(gdsFile, os.W_OK):
            print('... waiting for reading permission of {}'.format(gdsFile))
            sleep(0.5)

        gdsBaseName = os.path.basename(gdsFile)
        gdsFileNew = os.path.join(self.fhGdsS2Path, gdsBaseName)
        if not os.path.isfile(gdsFileNew):
            os.rename(gdsFile, gdsFileNew)


def run():
    observer = Observer()
    handler1 = GatewayHandler()
    observer.schedule(handler1, handler1.netlistPath, recursive=True)
    # handler2 = GatewayHandler()
    # observer.schedule(handler2, handler2.fhWavePath, recursive=True)
    # handler3 = GatewayHandler()
    # observer.schedule(handler3, handler3.fhGdsS1Path, recursive=True)
    # handler4 = GatewayHandler()
    # observer.schedule(handler4, handler4.laGenS2Path, recursive=True)
    observer.start()
    try:
        while True:
            sleep(1)
    except:
        observer.stop()
    observer.join()