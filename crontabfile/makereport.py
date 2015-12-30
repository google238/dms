#encoding:utf-8
import sys
sys.path.insert(0,'..')
import time
import datetime
import pymongo
import re
import operator
import json
from model.data_model import *
import common.common as common 
import types
from config.config_default import *
import calendar
#import sys
reload(sys)
sys.setdefaultencoding('utf8')


rain = ['阵雨转小到中雨',
'阵雨转小雨',
'中雨',
'小雨转中雨',
'暴雨转中雨',
'晴转小雨',
'多云转小雨',
'小雨',
'阴转中雨',
'阴转雷阵雨',
'中雨转雷阵雨',
'阴转阵雨',
'小雨转阵雨',
'小雨转大雨',
'中雨转小雨',
'大雨',
'雷阵雨转小到中雨',
'雷阵雨转小雨',
'阴转小雨',
'阵雨',
'雷阵雨',
'雷阵雨转中雨',
'中雨转大雨',
'雷阵雨转阴',
'多云转中雨',
'大雨转阵雨',
'多云转阵雨',
'多云转雷阵雨',
'小雨转阴',
'阵雨转雷阵雨',
'小雨转小到中雨',
'雷阵雨转多云',
'中雨转阵雨',
'阵雨转多云',
'中到大雨转多云',
'小到中雨转多云',
'大到暴雨转多云',
'小到中雨转阵雨',
'暴雨转大雨',
'小雨转中到大雨',
'暴雨',
'大雨转中雨',
'中雨转多云',
'阵雨转晴',
'大雨转多云',
'暴雨转小雨',
'大到暴雨转阵雨',
'中到大雨转中雨',
'中到大雨',
'晴转阵雨',
'小雨转多云',
'小雨转晴',
'暴雨转多云',
'中雨转阴',
'暴雨转阴',
'暴雨转阵雨',
'大雨转小雨',
'晴转中雨',
'大到暴雨转雷阵雨',
'大雨转雷阵雨',
'暴雨转雷阵雨',
'大到暴雨',
'雷阵雨转暴雨',
'中雨转暴雨',
'中雨转中到大雨',
'中雨转大到暴雨',
'多云转小到中雨',
'中到大雨转阵雨',
'雷阵雨转阵雨',
'大到暴雨转中雨',
'大到暴雨转小雨',
'雷阵雨转晴',
'小到中雨',
'中雨转晴',
'阵雨转中雨',
'阴转大雨',
'阵雨转阴',
'中到大雨转雷阵雨',
'暴雨转晴',
'大雨转晴',
'小到中雨转小雨',
'大到暴雨转阴',
'阵雨转大雨',
'小到中雨转中雨',
'小雨转暴雨',
'雷阵雨转大雨',
'多云转雨夹雪',
'雷阵雨转中到大雨',
'大雨转暴雨',
'阴转小到中雨',
'多云转大雨',
'大雨转大到暴雨',
'阴转中到大雨',
'小雨转雷阵雨',
'中雨转小到中雨',
'中到大雨转小雨',
'大雨转阴',
'多云转中到大雨',
'多云转大到暴雨',
'中到大雨转大雨',
'雷阵雨转大到暴雨',
'小到中雨转阴',
'阵雨转中到大雨',
'中到大雨转阴',
'大雨转中到大雨',
'暴雨转大暴雨',
'多云转暴雨',
'阵雨转暴雨',
'大暴雨',
'中雨转大暴雨',
'雨夹雪',
'晴转小到中雨',
'小到中雨转雷阵雨',
'中到大雨转小到中雨',
'阵雨转大到暴雨',
'暴雨转中到大雨',
'中到大雨转暴雨',
'小到中雨转大雨',
'大暴雨转大雨',
'大雨转大暴雨',
'大到暴雨转大暴雨',
'大暴雨转中雨',
'大到暴雨转暴雨',
'中到大雨转大到暴雨',
'大暴雨转暴雨',
'阴转大到暴雨',
'小到中雨转中到大雨',
'暴雨转小到中雨',
'暴雨转大到暴雨',
'暴雨到大暴雨转大雨',
'暴雨到大暴雨转中雨',
'暴雨到大暴雨转中到大雨',
'小到中雨转大到暴雨',
'大到暴雨转大雨',
'大雨转小到中雨',
'大到暴雨转中到大雨',
'大到暴雨转小到中雨',
'小到中雨转暴雨',
'中到大雨转大暴雨',
'小雨转大到暴雨',
'大暴雨转小雨',
'大到暴雨转晴',
'雾转雷阵雨',
'大暴雨转阵雨',
'小雨转小雪',
'阴转暴雨',
'小雨转雨夹雪',
'阵雨转雨夹雪',
'阴转雨夹雪',
'小雨转大暴雨',
'晴转大雨',
'冻雨',
'雷阵雨伴有冰雹',
'雨夹雪转小雨',
'大暴雨转阴',
'晴转雷阵雨',
'特大暴雨']

sunny = ['晴转多云','晴','多云转晴','阴转晴','晴转阴']
cloudy = ['多云','多云转阴','阴转多云','阴']
snow = ['阵雪转小雪','雨夹雪转小雪','雨夹雪转多云','雷阵雨转雾','雾转阵雨','阴转小雪','雨夹雪转阴','小雪转阵雪','小雪','暴雪','大雪','阵雪','中雪']
fog = ['浮尘','雾转多云','多云转扬沙','扬沙转阵雨','浮尘转阴','浮尘转阵雨','多云转浮尘','雾转晴','晴转浮尘','扬沙转晴','扬沙转浮尘','扬沙转多云','浮尘转晴','扬沙',
		'浮尘转多云','霾','轻度霾','沙尘暴','雾','中度霾','重度霾']

def unicode_convert(t):
	if t:
		t, number = re.subn(': u',': ', t)

		pattern = re.compile('\\\\u[0-9a-f]{4}')
		t_all = pattern.findall(t)

		if t_all:
			for o in t_all:
				n = unichr(eval('0x'+o.replace('\\u', '')))
				t = t.replace(o, n)
		# json转dict，必须是双引号
		addedSingleQuoteJsonStr = re.sub(r"(,?)(\w+?)\s*?:", r"\1'\2':", t);
		doubleQuotedJsonStr = addedSingleQuoteJsonStr.replace("'", "\"");
	return doubleQuotedJsonStr


def getWeather(devid,time):
	weatherinfo = dict()
	city,area = '',''
	findarea = data_model('dev_position').find_one(conditions={'_id':devid})
	if findarea is None:
		pass
	else:
		city,area = findarea['city'],findarea['area']
	if city == '' and area == '':
		findcity = data_model('devCurrInfo').find_one(conditions={'deviceId':devid})
		if findcity is None:
			pass
		else:
			if 'position' in findcity.keys():
				position = eval(findcity['position'])
				city = position['city']
				area = position['area']
				if city != '':
					city = unicode_convert(position['city'])
				if area != '':
					area = unicode_convert(position['area'])
	if city == '' and area == '':
		weatherinfo = {}
	else:
		if city == u'北京市' or city == u'天津市' or city == u'上海市' or city == u'重庆市':
			if area != '':
				area = area[:-1]
		city = city[:-1]
		weathertable = 'weather_' + time
		findweather = data_model(weathertable).find_one(conditions={'city':city,'area':area})
		if findweather is None:
			findweather = data_model(weathertable).find_one(conditions={'city':city})
		if findweather is None:
			return {},'',''
		city = findweather['city']
		area = findweather['area']
		del findweather['_id']
		del findweather['province']
		del findweather['city']
		del findweather['area']
		rain_count = 0
		sunny_count = 0
		cloudy_count = 0
		snow_count = 0
		fog_count = 0
		for key in findweather.keys():
			count = findweather[key]
			key = key.encode('utf8')
			if key in rain:
				rain_count += count
			elif key in sunny:
				sunny_count += count
			elif key in cloudy:
				cloudy_count += count
			elif key in snow:
				snow_count += count
			else:
				fog_count += count
		if rain_count > 0:
			weatherinfo['雨'] = rain_count
		if sunny_count > 0:
			weatherinfo['晴'] = sunny_count
		if cloudy_count > 0:
			weatherinfo['阴'] = cloudy_count
		if snow_count > 0:
			weatherinfo['雪'] = snow_count
		if fog_count > 0:
			weatherinfo['雾'] = fog_count
	return weatherinfo,city,area
	
def getPower(devid,time):
	power = 0
	power_pre = 0
	
	nowyear = int(time[:4])
	nowmonth = int(time[4:6])
	preyear = nowyear
	premonth = nowmonth - 1
	if premonth == 0:
		premonth = 12
		preyear -= 1
	preyear = str(preyear)
	if premonth < 10:
		premonth = '0' + str(premonth)
	else:
		premonth = str(premonth)		
	pretime = preyear + premonth
	
	findpower = data_model('devPowerHistory').find(conditions={'deviceId':devid,'time':re.compile(time)})
	findpowerpre = data_model('devPowerHistory').find(conditions={'deviceid':devid,'time':re.compile(pretime)})
	for i in findpower:
		power += float(i['devPower'])
		power = float('%0.4f'%power)
	for j in findpowerpre:
		power_pre += float(j['devPower'])
		power_pre = float('%0.4f'%power_pre)
	return power,power_pre
	
	
def getEfficiency(devid,time):
	year = int(time[:4])
	month = int(time[4:6])
	day = calendar.monthrange(year,month)[1]
	
	starttime = time + '01000000'
	endtime = time + str(day) +'235959'
	
	finddata = common.getPowerinfo(devid,starttime,endtime)
	for item in finddata:
		del item['_id']
		del item['devid']
	return finddata
	
def getCityindex(city,area):
	finditem = data_model('city_area').find_one(conditions={'city':city,'area':area})
	if finditem is None:
		#index = 1.0
		finditem = data_model('city_area').find_one(conditions={'city':city})
		if finditem is None:
			index = 1.0
		else:
			index = finditem['index']
	else:
		index = finditem['index']
	return index
	
def getTemperature(city,area,time):
	list1 = []
	list2 = []
	list3 = []
	finditem = data_model('temperature').find(conditions={'city':city,'area':area,'time':re.compile(time)})
	if len(finditem) == 0:
			pass
	else:
		finditem = sorted(finditem,key=operator.itemgetter('time'),reverse=False)
		for item in finditem:
			itemtime = item['time']
			high = item['high']
			lower = item['lower']
			list1.append(itemtime)
			list2.append(high)
			list3.append(lower)
	return list1,list2,list3
	
def getWorktime(devid,time):
	findindex = data_model('dev_index').find_one(conditions={'_id':devid})
	if findindex is None:
		index = 0
		starttime = '20150801'
	else:
		index = findindex['index']
		starttime = findindex.get('update','20150801')
	tablename = 'worktime_' + time
	finditem = data_model(tablename).find_one(conditions={'_id':devid})
	if finditem is None:
		worktime = 0
		runtime = 0
		power = 0
	else:
		worktime = finditem['worktime']
		runtime = finditem['runtime']
		if worktime > runtime:
			worktime,runtime = runtime,worktime
		power = finditem.get('power',0)
		if power == 0:
			finditem = data_model('devPowerHistory').find(conditions={'deviceId':devid,'time':re.compile(time)})
			for item in finditem:
				power += float(item.get('devPower',0))
		
	nowyear = int(time[:4])
	nowmonth = int(time[4:6])
	preyear = nowyear
	premonth = nowmonth - 1
	if premonth == 0:
		premonth = 12
		preyear -= 1
	preyear = str(preyear)
	if premonth < 10:
		premonth = '0' + str(premonth)
	else:
		premonth = str(premonth)		
	pretime = preyear + premonth
	tablename_pre = 'worktime_' + pretime
	finditem = data_model(tablename_pre).find_one(conditions={'_id':devid})
	if finditem is None:
		worktime_pre = 0
		power_pre = 0
	else:
		worktime_pre = finditem['worktime']
		power_pre = finditem.get('power',0)
		if power_pre == 0:
			finditem = data_model('devPowerHistory').find(conditions={'deviceId':devid,'time':re.compile(pretime)})
			for item in finditem:
				power_pre += item.get('devPower',0)
	
	
	return worktime,runtime,index,worktime_pre,starttime,power,power_pre

def dealReport(time,month):
	tablename = 'report_month_%s' %(time)
	table = 'worktime_' + time
	devIDlist = data_model(table).find()
	count = 0
	for l in devIDlist:	
		devid =  l['_id']
		print devid
		#if devid != '32150609600232212924':
		#	continue
		finditem = data_model('devID').find_one(conditions={'_id':devid})
		if finditem is None:
			system = ''
		else:
			system = finditem.get('system','')
		result = dict()
		finduser = data_model('user_dev').find_one(conditions={'_id':devid})
		if finduser is None:
			print '无用户名'
			continue
		else:
			username = finduser['username']	
			sender = finduser['sender']
		result['_id'] = devid
		result['username'] = username[-4:]
		
			
		worktime,runtime,index,worktime_pre,starttime,power,power_pre = getWorktime(devid,time)
		if worktime == 0:#表里无记录说明此设备不是空调类型，不予处理
			print "不是空调"
			continue
		weatherinfo,city,area = getWeather(devid,time)
		if city == '' or area == '':#无法确定用户地理信息，不予处理
			print '无地理信息'
			continue
		#power,power_pre = getPower(devid,time)
		if power == 0:#查询月份电量为0，说明无工作，不予处理，查询的是devpowerhistory表
			print '无电量'
			continue
		efficiencyinfo = getEfficiency(devid,time)

		cityindex = getCityindex(city,area)
		listtime,listhigh,listlower = getTemperature(city,area,time)
		
		data  = []	
		for key in weatherinfo.keys():
			temp = dict()
			temp['name'] = key
			temp['value'] = weatherinfo[key]
			data.append(temp)
		
		result['weather'] = {'key':weatherinfo.keys(),'value':data}
		result['power'] = power
		result['power_pre'] = power_pre
		result['cityindex'] = cityindex
		result['efficiency'] = efficiencyinfo
		result['temperature'] = {'time':listtime,'lower':listlower,'high':listhigh}
		result['worktime'] = worktime
		result['runtime'] = runtime
		result['index'] = index
		result['starttime'] = common.strTimeToFormat(starttime)
			
		year1 = int(time[:4])
		month1 = int(time[4:6])
		if month1 == 1:
			month2 = 12
			year2 = year - 1
		else:
			month2 = month1 - 1
			year2 = year1
		
		day1 = calendar.monthrange(year1,month1)[1]
		day2 = calendar.monthrange(year2,month2)[1]
			
		avgpower = float(power)/day1
		avgpower = float('%0.3f'%avgpower)
		if power_pre == 0:
			avgpower_pre = 0
		else:
			avgpower_pre = float(power_pre)/day2
			avgpower_pre = float('%0.3f'%avgpower_pre)
		result['powerinfo'] = {'now':[float('%0.3f'%power),avgpower], 'pre':[float('%0.3f'%power_pre),avgpower_pre]}
		
		data_model(tablename).insert(result)
		count += 1
	#	finditem = data_model('user_dev').find_one(conditions={'_id':devid})
	#	if finditem is None:
	#		pass
	#	else:
		if system == '':
			findloger = data_model('loger').find_one(conditions={'content.devID':devid})
			if findloger is None:
				system = 'LV_1'
			else:
				system = findloger.get('system','LV_1')	
	#	sender = finditem['sender']
	#	username = finditem['username']
		findname = data_model('devCurrInfo').find_one(conditions={'deviceId':devid})
		if findname is None:
			name = '设备' + devid[:15][-4:]
		else:
			name = findname.get('devName', '设备' + devid[:15][-4:])
		content = '%s %s年%d月份使用情况汇总'%(name,time[:4],month)
		url = 'http://%s/report/month?month=%s&devid=%s'%(server,time,common.encrypt(15,devid))
		data_model('month_report_test').insert({'devid':devid,'month':time,'sender':sender,'url':url,'username':username,'content':content,'system':system})
		print count
	print 'OK'
	
		
		
if __name__ == "__main__":	
	'''	
	nowtime = time.localtime()
	year = nowtime.tm_year
	month = nowtime.tm_mon
	if month == 1:
		month = 12
		year -= 1
	else:
		month -= 1
	if month < 10:
		time = str(year) + '0' + str(month)
	else:
		time = str(year) + str(month)
	'''
	now = datetime.datetime.now()
	pre_time = now - datetime.timedelta(days=2)
	time = pre_time.strftime('%Y%m')
	month = int(time[4:])
	
	print time,month
	dealReport(time,month)
		
