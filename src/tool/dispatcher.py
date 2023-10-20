import os
from time import sleep
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from src.tool.sys import getCurrentTime, readFile
from src.tool.config import (
    FTP_NETLIST_PATH, FTP_SIM_PASS_PATH, FTP_SIM_FAIL_PATH)


class GatewayHandler(FileSystemEventHandler):
    def __init__(self):
        self.focusPath = FTP_NETLIST_PATH
        self.passPath = FTP_SIM_PASS_PATH
        self.failPath = FTP_SIM_FAIL_PATH
        os.makedirs(self.focusPath, exist_ok=True)
        os.makedirs(self.passPath, exist_ok=True)
        os.makedirs(self.failPath, exist_ok=True)
        super().__init__()

    def on_created(self, event):
        return

    def on_modified(self, event):
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

        for line in readFile(statusFile):
            line = line.lower()
            if line.startswith('success') and os.path.isfile(rawFile):
                print('{} simulation success: {}'.format(now, spFile))
                print('{} sim output rawfile: {}'.format(now, rawFile))

                spBaseName = os.path.basename(spFile)
                spFileNew = os.path.join(self.passPath, spBaseName)
                if os.path.isfile(spFile) and not os.path.isfile(spFileNew):
                    os.rename(spFile, spFileNew)

                rawBaseName = os.path.basename(rawFile)
                rawFileNew = os.path.join(self.passPath, rawBaseName)
                if os.path.isfile(rawFile) and not os.path.isfile(rawFileNew):
                    os.rename(rawFile, rawFileNew)
                break

            elif line.startswith('fail'):
                print('{} simulation failure: {}'.format(now, spFile))

                spBaseName = os.path.basename(spFile)
                spFileNew = os.path.join(self.failPath, spBaseName)
                if os.path.isfile(spFile) and not os.path.isfile(spFileNew):
                    os.rename(spFile, spFileNew)
                break
        os.remove(statusFile)
        return

def run():
    handler = GatewayHandler()
    observer = Observer()
    observer.schedule(handler, handler.focusPath, recursive=True)
    observer.start()
    try:
        while True:
            sleep(0.5)
    except:
        observer.stop()
    observer.join()