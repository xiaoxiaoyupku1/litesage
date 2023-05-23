from json import loads
from subprocess import getoutput
import os

def get_apps():
	cmd = 'powershell -ExecutionPolicy Bypass "Get-StartApps|convertto-json"'
	apps=loads(getoutput(cmd))
	names = {}
	for each in apps:
		names.update({each['Name']:each['AppID']})
	return names

def find_app(app_name):
	apps = get_apps()
	for each in sorted(apps,key=len):
		if app_name.upper() in each.upper():
			return each,apps[each]
	else:
		return "Application not found!"

def run_layout(gdsfile):
    app = find_app('klayout (default)')
    apppath = app[1]
    assert os.path.isfile(apppath), 'cannot find {}'.format(str(app))
    cmd = "{} -e {}".format(apppath, gdsfile)
    # print(cmd)
    os.popen(cmd)