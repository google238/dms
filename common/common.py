# coding: utf-8
import logging
import platform
import time
import datetime
import math
from logging.handlers import TimedRotatingFileHandler
from config.config_default import *
from model.data_model import *
import operator

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
	
	days = (end - start).days
	seconds = (end - start).seconds
	seconds += days * 24 * 3600
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
				if sec > 300:
					sec = 120
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
	
def getdaylist(starttime,endtime):#获取时间段内的日期列表
	starty = int(starttime[:4])
	startm = int(starttime[4:6])
	startd = int(starttime[6:8])
	
	endy = int(endtime[:4])
	endm = int(endtime[4:6])
	endd = int(endtime[6:8])
	
	start = datetime.datetime(starty,startm,startd)
	end = datetime.datetime(endy,endm,endd)
	
	daylist = []
	d = (end - start).days
	for i in range(0,d+1):
		date = start + datetime.timedelta(i)
		date = date.strftime('%Y%m%d')
		daylist.append(date)
	return daylist
	
def getfixPowerinfo(devid,starttime,endtime):#获取时间段内的电量明细列表
	now = datetime.datetime.now().strftime('%Y%m%d')
	start = starttime[:8]
	end = endtime[:8]
	finddata = []
	conditions = {'devid':devid,'time':{'$gt':starttime,'$lt':endtime}}
	sort = [('time',1)]
	
	if start == end:
		if start == now:
			tablename = "devpower_detail_" + start	
		else:
			tablename = 'devpower_log_' + start
		finddata = data_model(tablename).find(conditions=conditions,sort=sort)
	else:
		daylist = getdaylist(starttime,endtime)
		for day in daylist:
			if day == now:
				tablename = "devpower_detail_" + day
			else:
				tablename = 'devpower_log_' + day
			finditem = data_model(tablename).find(conditions=conditions,sort=sort)
			finddata.extend(finditem)
	return finddata
    
def getPowerinfo(devid,starttime,endtime):#获取时间段内的电量明细列表
	start = starttime[:8]
	end = endtime[:8]
	finddata = []
	conditions = {'devid':devid,'time':{'$gt':starttime,'$lt':endtime}}
	sort = [('time',1)]
	
	if start == end:
		tablename = "devpower_detail_" + start	
		finddata = data_model(tablename).find(conditions=conditions,sort=sort)
	else:
		daylist = getdaylist(starttime,endtime)
		for day in daylist:
			tablename = "devpower_detail_" + day
			finditem = data_model(tablename).find(conditions=conditions,sort=sort)
			finddata.extend(finditem)
	return finddata
    
def getlogPowerinfo(devid,starttime,endtime):#获取时间段内的电量明细列表
	start = starttime[:8]
	end = endtime[:8]
	finddata = []
	conditions = {'devid':devid,'time':{'$gt':starttime,'$lt':endtime}}
	sort = [('time',1)]
	
	if start == end:
		tablename = "devpower_log_" + start	
		finddata = data_model(tablename).find(conditions=conditions,sort=sort)
	else:
		daylist = getdaylist(starttime,endtime)
		for day in daylist:
			tablename = "devpower_log_" + day
			finditem = data_model(tablename).find(conditions=conditions,sort=sort)
			finddata.extend(finditem)
	return finddata
    
	
def getPowerpoor(devid,starttime,endtime,minw,maxw):#获取时间段内的电量差值，重点关注不在同一天时间的
	start = starttime[:8]
	end = endtime[:8]
	if start == end:
		pass
	else:
		daylist = getdaylist(starttime,endtime)
		del daylist[-1]
		powervalue = []
		for i in daylist:
			finditem = data_model('devpower_info').find(conditions={'devid':devid,'time':i})
			if len(finditem) == 0:
				continue
			power  = finditem[0]['W']
			powervalue.append(power)
		for value in powervalue:
			maxw += value
	return float('%0.4f'%(maxw-minw))
	
def getOffset(findset):
	findset = sorted(findset,key=operator.itemgetter('time'),reverse=False)
	offset = 0
	minW = findset[0]['W']
	maxW = findset[-1]['W']
	w1 = 0
	w2 = 0
	for i in findset:
		w2 = i['W']
		if w2 < w1:#此处有插拔，或者是遇到了隔天电量清零，修改偏移量
			offset += w1
		w1 = w2		
	maxW += offset
	return offset,minW,maxW
	
def encrypt(key, s):
	b = bytearray(str(s).encode("utf8"))
	n = len(b) # 求出 b 的字节数
	c = bytearray(n*2)
	j = 0
	for i in range(0, n):
		b1 = b[i]
		b2 = b1 ^ key # b1 = b2^ key
		c1 = b2 % 16
		c2 = b2 // 16 # b2 = c2*16 + c1
		c1 = c1 + 65
		c2 = c2 + 65 # c1,c2都是0~15之间的数,加上65就变成了A-P 的字符的编码
		c[j] = c1
		c[j+1] = c2
		j = j+2
	return c.decode("utf8")

def decrypt(key, s):
	c = bytearray(str(s).encode("utf8"))
	n = len(c) # 计算 b 的字节数
	if n % 2 != 0 :
		return ""
	n = n // 2
	b = bytearray(n)
	j = 0
	for i in range(0, n):
		c1 = c[j]
		c2 = c[j+1]
		j = j+2
		c1 = c1 - 65
		c2 = c2 - 65
		b2 = c2*16 + c1
		b1 = b2^ key
		b[i]= b1
	try:
		return b.decode("utf8")
	except:
		return "failed"		
'''
def timeDelta(type='day',direction='+',value):
	now = datetime.datetime.now()
	if type == 'day':
		if direction == '+':
			result = now + datetime.timedelta(days=value)
		else:
			result = now - datetime.timedelta(days=value)
	else:
		if direction == '+':
			result = now + datetime.timedelta(seconds=value)
		else:
			result = now - datetime.timedelta(seconds=value)
	return result
'''
