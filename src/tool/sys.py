from datetime import datetime


def getCurrentTime():
	now = datetime.now()
	return now.strftime('%Y%m%d%H%M%S')


def readFile(path, encoding=None):
	if encoding is None:
		encoding = 'utf-8'
	with open(path, 'r', encoding=encoding) as port:
		for line in port:
			yield line.strip()