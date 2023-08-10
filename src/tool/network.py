import functools
from threading import Lock
from ftplib import FTP
from urllib.request import urlopen
from socket import gethostbyname
from socket import socket, AF_INET, SOCK_DGRAM


@functools.lru_cache(maxsize=None)
def getIpAddr(public=True, url=None):
    if public:
        if url is None:
            return urlopen('http://ip.42.pl/raw').read().decode('utf-8')
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

    def __init__(self, host, port, user, passwd):
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

    def upload(self, localPath, remotePath):
        bufsize = 1024
        fp = open(localPath, 'rb')
        self.storbinary('STOR ' + remotePath, fp, bufsize)
        fp.close()

    def end(self):
        self.quit()