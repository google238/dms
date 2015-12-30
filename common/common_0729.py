# coding: utf-8
import logging
import platform
import time
import datetime
from logging.handlers import TimedRotatingFileHandler
from config.config_default import *
from model.data_model import *

#记录日志
def getLoger(title, filebasename):
	if platform.system() == 'Windows' :
		logfile = logpath_win + "\\%s"%(filebasename)
	else:
		logfile = logpath_linux + "%s"%(filebasename)
	
	logger = logging.getLogger(title)
	formatter = logging.Formatter('%(name)-12s %(asctime)s %(levelname)-8s %(message)s')
	file_handler = logging.FileHandler(logfile)
	file_handler.setFormatter(formatter)
	logger.addHandler(file_handler)
	logger.setLevel(logging.INFO)
	return logger

filetime = time.strftime('%Y%m%d%H%M%S',time.localtime(time.time()))
logfile = 'dms_' + filetime + '.log'
#dp_logfile = 'dms_dp_' + filetime + '.log'
_LOG = getLoger("DMS", logfile)	
#_LOG_DATAPROCESS = getLoger("DMS_DP",dp_logfile)
#_LOG = getLoger("DMS", "dms.log")	
	
#解析xml文件	
def paraseMsgXml(rootElem): 
	msg = {}  
	if rootElem.tag == 'xml':  
		for child in rootElem:  
			msg[child.tag] =child.text
	#_LOG.info(msg)
	return msg
	
def strTimeToFormat(strTime):
		length = len(strTime)
		date = ''
		year = ''
		month = ''
		day = ''
		hour = ''
		min = ''
		sec = ''
		if length >=4:
			year = strTime[:4]
		if length >=6:
			month = strTime[4:6]
		if length >=8:
			day = strTime[6:8]
		if length >=10:
			hour = strTime[8:10]
		if length >=12:
			min = strTime[10:12]
		if length >=14:
			sec = strTime[12:14]
		
		if year != '':
			date = date + year
		if month != '':
			date = date + '-' + month
		if day != '':
			date = date + '-' + day
		if hour != '':
			date = date + ' ' + hour
		if min != '':
			date = date + ':' + min
		if sec != '':
			date = date + ':' + sec
		return date
	
def timePoor(starttime,endtime):
	startyear = int(starttime[:4])
	startmonth = int(starttime[4:6])
	startday = int(starttime[6:8])
	starthour = int(starttime[8:10])
	startmin = int(starttime[10:12])
	startsec = int(starttime[12:14])
	
	endyear = int(endtime[:4])
	endmonth = int(endtime[4:6])
	endday = int(endtime[6:8])
	endhour = int(endtime[8:10])
	endmin = int(endtime[10:12])
	endsec = int(endtime[12:14])
	
	start = datetime.datetime(startyear,startmonth,startday,starthour,startmin,startsec)
	end = datetime.datetime(endyear,endmonth,endday,endhour,endmin,endsec)
	
	seconds = (end - start).seconds
	return seconds

def worktime(findlist):
	flag = 0
	second = 0
	starttime = ''
	endtime = ''
	for item in findlist:
		if item['P'] >= 300:
			if flag == 0:
				flag = 1
				starttime = item['time']
			if flag == 1:
				continue
		if item['P'] < 300:
			if flag == 1:
				flag = 0
				endtime = item['time']
				sec = timePoor(starttime,endtime)
				second += sec
			if flag == 0:
				continue
	return second
	
def secTohms(second):
	h = 0
	m = 0
	s = 0
	h = second/3600
	m = (second%3600)/60
	s = (second%3600)%60
	return h,m,s
	
def getPowerinfo(devid,starttime,endtime):
	start = starttime[:8]
	finddata = []
	end = endtime[:8]
	if start == end:
		tablename = "devpower_detail_" + start
		conditions = {'devid':devid,'time':{'$gt':starttime,'$lt':endtime}}
		sort = [('time',1)]
		finddata = data_model(tablename).find(conditions=conditions,sort=sort)
	return finddata