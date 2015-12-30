# coding: utf-8
import json
import types
import web
import string
import datetime
import time
from model.dms_model import *
from model.data_model import *
from model.userfrom_model import *
from libraries.utils import render, now4yMdHms , http_post
from libraries.decorator import admin_login
import common.common as common 
import common.unparse as unparse
import re
from bson.code import Code

def getCmd_power(starttime,endtime,devid,start,length,draw):
	conditions = dict()
	if devid != '':
		conditions['devid'] = devid
	if starttime != '':
		conditions['starttime'] = {'$gte':starttime}
	if endtime != '':
		conditions['endtime'] = {'$lte':endtime}
	sort = [('starttime',1)]
	data = data_model('powershowgrid').find(conditions=conditions,sort=sort)
	result = dict()
	resultlist = []
	count = 0
	starti = 0
	for item in data:
		count += len(item['result'])
	for item in data:
		for i in item['result']:
			if starti != start:
				starti += 1
				continue
			temp = []
			temp.append(devid)
			temp.append(i['temp'])
			temp.append(i['W'])
			temp.append(i['P'])
			temp.append(common.strTimeToFormat(i['time']))
			if i['cmd'] == '3001':
				temp.append('持续状态')
			elif i['cmd'] == 'devTodo' or i['cmd'] == 'AEA0':
				if i['inst'].startswith('0'):
					temp.append('关闭')
				elif i['inst'].startswith('1'):
					if i['time'] == item['starttime']:
						temp.append("打开(" + i['inst'] + ")")
					else:
						temp.append("调整温度模式(" + i['inst'] + ")")
			resultlist.append(temp)
			if len(resultlist) == length:
				break
		if len(resultlist) == length:
			break
	
	result = {"draw":draw,"recordsTotal":count,"recordsFiltered":count,"aaData":resultlist}
	return result
	

def getTemp(starttime,endtime,devid):
	province = devid.split('_')[0]
	city = devid.split('_')[1]
	conditions = dict()
	conditions['city'] = province
	conditions['area'] = city
	conditions['time'] = {'$gte':starttime,'$lte':endtime}
	sort = [('time',1)]
	data = data_model('live.area.temp.history').find(conditions=conditions,sort=sort)
	result = []
	for item in data:
		if item['temNow'] == '暂无实况':
			continue
		temp = {}
		temp['key'] = common.strTimeToFormat(item['time'])
		temp['value'] = item['temNow']
		result.append(temp)		
	return result

def getCmd(starttime,endtime,devid,start,length,draw):
	sender = False
	if devid.startswith('sender_'):
		devid = devid[7:]
		sender = True
	sort = []
	sort.append(('acceptTime',pymongo.ASCENDING))
	conditions = {}
	conditions['acceptTime'] = {'$gte':starttime,'$lte':endtime}
	if sender:
		pre = devid[:3]
		stuff = devid[3:]
		rexexp = '^' + pre + '.*' + stuff + '$'
		rexexp = re.compile(rexexp)
		conditions['content.sender'] = rexexp
	else:
		conditions['content.devID'] = devid
	conditions['content.CMD'] = {'$exists':True}
	conditions['mark'] = {'$ne':'dev'}
	
	result = dict()
	count = data_model('loger').count(conditions=conditions)
	findlist = data_model('loger').find(conditions=conditions,sort=sort,limit=length,skip=start)
	resultlist = []
	for item in findlist:
		print item
		temp = []
		temp.append(devid)
		temp.append(item["content"]["CMD"])
		temp.append(common.strTimeToFormat(item['acceptTime']))
		resultlist.append(temp)

	result = {"draw":draw,"recordsTotal":count,"recordsFiltered":count,"aaData":resultlist}
	return result
	

def getPower(starttime,endtime,devid,type):		
	result = []	
	sort = [('time',1)]	
	data = common.getPowerinfo(devid,starttime,endtime)
	time1 = starttime
	power = 0
	for item in data:
		temp = {}
		time2 = item['time']
		temp['key'] = common.strTimeToFormat(item['time'])	
		if type == 'power':
			temp['value'] = float('%0.4f'%(float(item['W'])))
			result.append(temp)
			time1 = time2
			power = float('%0.4f'%(float(item['W'])))
		elif type == 'efficiency':
			a = datetime.datetime.strptime(time2,'%Y%m%d%H%M%S')
			b = datetime.datetime.strptime(time1,'%Y%m%d%H%M%S')
			if (a-b).seconds > 600:#两个时间差大于10分钟在这段时间内每隔5分钟填充个0
				while b<a:
					temp1 = {}
					temp1['key'] = common.strTimeToFormat(b.strftime('%Y%m%d%H%M%S'))
					temp1['value'] = 0
					result.append(temp1)
					b = b + datetime.timedelta(seconds=600)
			temp['value'] = int(item['P'])		
			result.append(temp)	
			time1 = time2
	a = datetime.datetime.strptime(endtime,'%Y%m%d%H%M%S')
	b = datetime.datetime.strptime(time1,'%Y%m%d%H%M%S')
	timeflag = time1[:8]
	if (a-b).seconds > 600:#两个时间差大于10分钟在这段时间内每隔5分钟填充个0
		while b<a:
			temp1 = {}
			temp1['key'] = common.strTimeToFormat(b.strftime('%Y%m%d%H%M%S'))
			if type == 'efficiency':
				temp1['value'] = 0
			elif type == 'power':
				if b.strftime('%Y%m%d%H%M%S')[:8] == timeflag:
					temp1['value'] = power
				else:
					temp1['value'] = 0
			result.append(temp1)
			b = b + datetime.timedelta(seconds=600)
	return result
	
	
class griddata:
	def __init__(self):
		return
		
	def GET(self):
		return render("griddata.html")
		
	def POST(self):
		data = web.input()
		type = data['type']
		starttime = data['starttime'].replace('/','').replace(' ','').replace(':','') + '00'
		endtime = data['endtime'].replace('/','').replace(' ','').replace(':','') + '00'
		devid = data['devid']
		if 'start' in data.keys():
			start = int(data["start"])
		if 'length' in data.keys():
			length = int(data["length"])
		if 'draw' in data.keys():
			draw = int(data['draw'])
		
		data = dict()
		result = []
		if type == 'power' or type == 'efficiency':
			result = getPower(starttime,endtime,devid,type)
			data = {'result':result}
		elif type == 'cmd':
			data = getCmd(starttime,endtime,devid,start,length,draw)
		elif type == 'temp':
			result = getTemp(starttime,endtime,devid)
			data = {'result':result}
		elif type == 'cmd_power':
			data = getCmd_power(starttime,endtime,devid,start,length,draw)
		data = json.dumps(data)
		return data
		
class show:
	def __init__(self):
		return
		
	def GET(self):
		return render("gridshow.html")
		
	def POST(self):
		data = web.input()
		tablename = data['tablename']
		key = data['key']
		key = 'this.' + key 
		map = Code("function(){emit("+key+", {count:1});}") 
		reduce = Code("function(key,values){var total = 0;for (var i = 0; i < values.length; i++){total += values[i].count;}return {count:total};}") 
		data_model(tablename).map_reduce(map, reduce, "out") 
		findlist = data_model("out").find()
		data = []
		for item in findlist:
			temp = dict()
			temp['key'] = item['_id']
			temp['value'] = item['value']['count']
			data.append(temp)
		result = dict()
		result = {'result':data}
		result = json.dumps(result)
		return result