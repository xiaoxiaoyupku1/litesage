import functools
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
        self.connect(host=self.host, port=self.port)
        self.login(user=self.user, passwd=self.passwd)
    
    def catDir(self, path):
        return self.dir(path)

    def makeDir(self, path):
        return self.mkd(path)

    def removeDir(self, path):
        self.rmd(path)

    def downloadFile(self, localPath, remotePath):
        bufsize = 1024
        fp = open(localPath, 'wb')
        self.retrbinary('RETR ' + remotePath, fp.write, bufsize)
        fp.close()

    def isFile(self, remotePath):
        try:
            self.size(remotePath)
            return True
        except:
            return False

    def uploadFile(self, localPath, remotePath):
        bufsize = 1024
        fp = open(localPath, 'rb')
        self.storbinary('STOR ' + remotePath, fp, bufsize)
        fp.close()

    def readFile(self, remotePath):
        fileLines = []
        def _lineCallback(line):
            fileLines.append(line)
        if self.isFile(remotePath):
            self.retrlines('RETR ' + remotePath, _lineCallback)
        return fileLines

    def end(self):
        self.quit()