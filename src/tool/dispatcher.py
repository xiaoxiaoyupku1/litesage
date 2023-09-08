import os
from sys import getsizeof
from time import sleep
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from pickle import dump
from src.tool.wave import WaveInfo
from src.tool.sys import getCurrentTime, readFile
from src.tool.config import FTP_NETLIST_PATH, FTP_SIM_RESULT_PATH


class GatewayHandler(FileSystemEventHandler):
    def __init__(self):
        self.rawPath = FTP_SIM_RESULT_PATH
        self.ftpPath = FTP_NETLIST_PATH
        super().__init__()

    def on_created(self, event):
        return

    def on_modified(self, event):
        statusFile = event.src_path
        if not statusFile.endswith('.status'):
            return
        elif not os.path.isfile(statusFile):
            return

        while not os.access(statusFile, os.R_OK):
            print('... waiting for reading permission of {}'.format(statusFile))
            sleep(0.5)

        baseName = os.path.basename(statusFile)
        baseName = os.path.splitext(baseName)[0]
        rawFile = os.path.join(self.rawPath, '{}.raw'.format(baseName))
        sigFile = os.path.join(self.ftpPath, '{}.sig'.format(baseName))
        sigStatusFile = os.path.join(self.ftpPath, '{}.sigStatus'.format(baseName))
        for line in readFile(statusFile):
            if line == 'success' and os.path.isfile(rawFile):
                now = getCurrentTime()
                print('{} raw file found: {}'.format(now, rawFile))
                wave = WaveInfo(rawFile)
                with open(sigFile, 'wb') as fport:
                    if getsizeof(wave) <= 10240000: # <= 10MB
                        dump(wave, fport)
                        with open(sigStatusFile, 'w') as f:
                            f.write('finish dump all')
                    else:
                        sigNames = wave.get_trace_names()
                        dump(sigNames, fport)
                        with open(sigStatusFile, 'w') as f:
                            f.write('finish dump names')
                return
        return

def run():
    handler = GatewayHandler()
    observer = Observer()
    observer.schedule(handler, handler.ftpPath, recursive=True)
    observer.start()
    try:
        while True:
            sleep(0.5)
    except:
        observer.stop()
    observer.join()