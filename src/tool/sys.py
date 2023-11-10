import os
from datetime import datetime
from time import sleep


def getCurrentTime():
	now = datetime.now()
	return now.strftime('%Y%m%d%H%M%S')


def readFile(path, encoding=None):
	if encoding is None:
		encoding = 'utf-8'
	wait = True
	while wait:
		if os.access(path, os.R_OK):
			wait = False
		sleep(0.1)
	with open(path, 'r', encoding=encoding) as port:
		for line in port:
			yield line.strip()