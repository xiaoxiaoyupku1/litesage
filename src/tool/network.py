import os
import functools
from time import sleep
from threading import Lock
from ftplib import FTP
from urllib.request import urlopen
from json import load
from socket import gethostbyname
from socket import socket, AF_INET, SOCK_DGRAM
from src.tool.config import HOST, PORT, USER, PASSWD


@functools.lru_cache(maxsize=None)
def getIpAddr(public=True, url=None):
    if public:
        if url is None:
            # return urlopen('http://ip.42.pl/raw').read().decode('utf-8')
            return load(urlopen('http://httpbin.org/ip'))['origin']
        else:
            return gethostbyname(url)
    else:
        s = socket(AF_INET, SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        addr = s.getsockname()[0]
        s.close()
        return addr


class Gateway(FTP):
    _instance_lock = Lock()

    def __init__(self, host=HOST, port=PORT, user=USER, passwd=PASSWD):
        super().__init__()
        self.set_debuglevel(2)
        self.host = host  # str
        self.port = port  # int
        self.user = user  # str
        self.passwd = passwd  # str
        self.init()

    def __new__(cls, *args, **kwargs):
        if not hasattr(Gateway, "_instance"):
            with Gateway._instance_lock:
                if not hasattr(Gateway, '_instance'):
                    Gateway._instance = object.__new__(cls)
        return Gateway._instance

    def init(self):
        connected = False
        try:
            self.connect(host=self.host, port=self.port)
            self.login(user=self.user, passwd=self.passwd)
            connected = True
        except:
            pass
        finally:
            assert connected, 'FTP connection error'

    def reconnect(self):
        self.close()
        self.init()
    
    def catDir(self, path):
        return self.dir(path)

    def makeDir(self, path):
        return self.mkd(path)

    def removeDir(self, path):
        self.rmd(path)

    def downloadFile(self, localPath, remotePath):
        pwd = self.pwd()
        remoteDir = os.path.dirname(remotePath)
        if len(remoteDir) > 0:
            self.cwd(remoteDir)
            remotePath = os.path.basename(remotePath)
        bufsize = 1024

        while self.retrFile('RETR ' + remotePath, localPath, bufsize) == -1:
            sleep(0.5)

        self.cwd(pwd)

    def retrFile(self, cmd, savePath, bufsize):
        fp = open(savePath, 'wb')
        try:
            self.retrbinary(cmd, fp.write, bufsize)
            fp.close()
            return 0
        except:
            fp.close()
            return -1

    def isFile(self, remotePath):
        pwd = self.pwd()
        remoteDir = os.path.dirname(remotePath)
        try:
            if len(remoteDir) > 0:
                self.cwd(remoteDir)
                remotePath = os.path.basename(remotePath)
            while True:
                size1 = self.size(remotePath)
                sleep(0.1)
                size2 = self.size(remotePath)
                if size1 == size2:
                    self.cwd(pwd)
                    return True
        except:
            self.cwd(pwd)
            return False
        finally:
            self.cwd(pwd)

    def uploadFile(self, localPath, remotePath):
        pwd = self.pwd()
        bufsize = 1024
        fp = open(localPath, 'rb')
        remoteDir = os.path.dirname(remotePath)
        if len(remoteDir) > 0:
            self.cwd(remoteDir)
            remotePath = os.path.basename(remotePath)
        try:
            self.storbinary('STOR ' + remotePath, fp, bufsize)
        except:
            self.reconnect()
            self.storbinary('STOR ' + remotePath, fp, bufsize)
        self.cwd(pwd)
        fp.close()

    def readFile(self, remotePath):
        fileLines = []
        def _lineCallback(line):
            fileLines.append(line)

        pwd = self.pwd()
        remoteDir = os.path.dirname(remotePath)
        if len(remoteDir) > 0:
            self.cwd(remoteDir)
            remotePath = os.path.basename(remotePath)
        if self.isFile(remotePath):
            try:
                self.retrlines('RETR ' + remotePath, _lineCallback)
            except:
                pass
        self.cwd(pwd)
        return fileLines

    def end(self):
        self.quit()

    def isConnected(self):
        try:
            self.voidcmd('NOOP')
        except:
            return False
        return True