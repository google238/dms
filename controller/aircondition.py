# coding: utf-8
import json
import types
import web
import string
import datetime
import time
from model.data_model import *
import common.common as common 
import common.unparse as unparse
from libraries.utils import render, now4yMdHms , http_post
import re
import operator

class editor_city:
	def __init__(self):
		return
	
	def GET(self):
		return
	
	def POST(self):
		data = web.input()
		province = data['data[province]']
		city = data['data[city]']
		area = data['data[area]']
		index = float(data['data[index]'])
		action = data['action']
		insertitem = {'province':province,'city':city,'area':area,'index':index}
		if action == 'edit' or action == 'create':	
			data_model('city_area').update_set(condition={'province':province,'city':city,'area':area},values=insertitem,upsert=True)
		elif action == 'remove':
			data.model('city_area').remove(condition={'province':province,'city':city,'area':area})
			insertitem = {'province':'','city':'','area':'','index':1}
		data = json.dumps(insertitem)
		return data
		
class editor_temp:
	def __init__(self):
		return
	
	def GET(self):
		return
	
	def POST(self):
		data = web.input()
		tablename = ''
		value = ''
		if 'data[wind]' in data.keys():
			tablename = 'windstate'
			value = data['data[wind]']
		elif 'data[weather]' in data.keys():
			tablename = 'stateDetailed'
			value = data['data[weather]']
		index = float(data['data[index]'])
		action = data['action']
		insertitem = {'_id':value,'index':index}
		if action == 'edit' or action == 'create':	
			data_model(tablename).update_set(condition={'_id':value},values=insertitem,upsert=True)
		elif action == 'remove':
			data.model(tablename).remove(condition={'_id':value})
			insertitem = {}
		data = json.dumps(insertitem)
		return data

class city:
	def __init__(self):
		return
		
	def GET(self):
		return render("city.html")
		
	def POST(self,*args):
		data = web.input()
		start = int(data["start"])
		length = int(data["length"])
		draw = int(data['draw'])
		ordernum =  int(data['order[0][column]'])
		orderstyle = data['order[0][dir]']
		province = data['province']
		resultdata = []
		finddata = data_model('city_area').find(conditions={'province':province},sort=[('city',-1)])
		for item in finddata:
			temp = []
			if item['province'] == '北京' or item['province'] == '天津' or item['province'] == '上海' or item['province'] == '重庆':
				temp.append('')
			else:
				temp.append(item['province'])
			temp.append(item['city'])
			temp.append(item['area'])
			temp.append(item['index'])
			resultdata.append(temp)
		count = len(finddata)	
		data = {"draw":draw,"recordsTotal":count,"recordsFiltered":count,"aaData":resultdata}
		data = json.dumps(data)
		return data		

		
class temp:
	def __init__(self):
		return
		
	def GET(self):
		return render("temperature.html")
		
	def POST(self,*args):
		data = web.input()
		draw = int(data['draw'])
		style = data['style']
		resultdata = []
		finddata = []
		if style == '1':
			finddata = data_model('windstate').find()
		elif style == '2':
			finddata = data_model('stateDetailed').find()
		for item in finddata:
			temp = []
			temp.append(item['_id'])
			temp.append(item['index'])
			resultdata.append(temp)
		count = len(finddata)	
		data = {"draw":draw,"recordsTotal":count,"recordsFiltered":count,"aaData":resultdata}
		data = json.dumps(data)
		return data	
		
def getWeather(devid,time):
	weatherinfo = dict()		
	city,area = '',''
	findarea = data_model('dev_position').find_one(conditions={'_id':devid})
	if findarea is None:
		pass
	else:
		city,area = findarea['city'],findarea['area']
	if city == '' and area == '':
		weatherinfo = {}
	else:
		city = city[:-1]
		if city == '北京' or city == '天津' or city == '上海' or city == '重庆':
			area = area[:-1]
		weathertable = 'weather_' + time
		findweather = data_model(weathertable).find_one(conditions={'city':city,'area':area})
		if findweather is None:
			weatherinfo = {}
		else:
			del findweather['_id']
			weatherinfo = findweather
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
	
	findpower1 = data_model('devpower_month').find_one(conditions={'devid':devid,'time':time})
	findpower2 = data_model('devpower_month').find_one(conditions={'devid':devid,'time':pretime})
	if findpower1 is None:
		power = 0
	else:
		power = findpower1['W']
	if findpower2 is None:
		power_pre = 0
	else:
		power_pre = findpower2['W']
	return power,power_pre
	
	
def getEfficiency(devid,time):
	starttime = time + '01000000'
	endtime = time + '31235959'
	
	finddata = common.getPowerinfo(devid,starttime,endtime)
	for item in finddata:
		del item['_id']
		del item['devid']	
	return finddata
	
def getCityindex(city,area):
	finditem = data_model('city_area').find_one(conditions={'city':city,'area':area})
	if finditem is None:
		index = 1.0
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
	tablename = 'worktime_' + time
	finditem = data_model(tablename).find_one(conditions={'_id':devid})
	if finditem is None:
		worktime = 0
		runtime = 0
	else:
		worktime = finditem['worktime']
		runtime = finditem['runtime']
	return worktime,runtime	
		
class info:
	def __init__(self):
		return
		
	def GET(self):
		data = web.input()
		devid = data['devid']
		time = data['time']
		weatherinfo,city,area = getWeather(devid,time)
		power,power_pre = getPower(devid,time)
		efficiencyinfo = getEfficiency(devid,time)
		cityindex = getCityindex(city,area)
		listtime,listlower,listhigh = getTemperature(city,area,time)
		worktime,runtime = getWorktime(devid,time)
		result = dict()
		result['devid'] = devid
		result['weather'] = weatherinfo
		result['power'] = power
		result['power_pre'] = power_pre
		result['cityindex'] = cityindex
		result['efficiency'] = efficiencyinfo
		result['temperature'] = {'time':listtime,'lower':listlower,'high':listhigh}
		result['worktime'] = worktime
		result['runtime'] = runtime
		result = json.dumps(result)
		return result
		
		
		
		