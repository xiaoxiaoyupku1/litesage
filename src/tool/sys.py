from json import loads
from subprocess import getoutput
from datetime import datetime

def getApps():
	cmd = 'powershell -ExecutionPolicy Bypass "Get-StartApps|convertto-json"'
	apps=loads(getoutput(cmd))
	names = {}
	for each in apps:
		names.update({each['Name']:each['AppID']})
	return names

def findApp(app_name):
	apps = getApps()
	for each in sorted(apps,key=len):
		if app_name.upper() in each.upper():
			return each,apps[each]
	else:
		return "Application not found!"

def getCurrentTime():
	now = datetime.now()
	return now.strftime('%Y%m%d%H%M%S')


def readFile(path, encoding=None):
	if encoding is None:
		encoding = 'utf-8'
	with open(path, 'r', encoding=encoding) as port:
		for line in port:
			yield line.strip()