import os
from src.tool.sys import findApp

def runLayout(gdsfile):
    app = findApp('klayout (default)')
    apppath = app[1]
    assert os.path.isfile(apppath), 'cannot find {}'.format(str(app))
    cmd = "{} -e {}".format(apppath, gdsfile)
    # print(cmd)
    os.popen(cmd)