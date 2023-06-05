from json import loads
from subprocess import getoutput

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