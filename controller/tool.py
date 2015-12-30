# coding: utf-8
import json
import types
import web
import string
from datetime import *
import time
import operator
from model.dms_model import *
from model.data_model import *
from model.userfrom_model import *
from libraries.utils import render, now4yMdHms , http_post
from libraries.decorator import admin_login
import common.common as common 
import common.unparse as unparse

def getSuminfo(devid,starttime,endtime):
	conditions = {'devid':devid,'starttime':{'$gte':starttime},'endtime':{'$lte':endtime}}
	runtime = 0
	worktime = 0
	power = 0.0
	finddata = data_model('actioninfo').find(conditions=conditions)
	for item in finddata:
		runtime += item['runtime']
		worktime += item['worktime']
		power += item['power']
	runh,runm,runs = common.secTohms(runtime)
	workh,workm,works = common.secTohms(worktime)
	context = "设备在这段时间内共工作%d小时%d分%d秒，其中压缩机运行%d小时%d分%d秒，共耗电%0.4f千瓦"%(runh,runm,runs,workh,workm,works,power)
	data = {'context':context}
	return data
	
	
def parseInst(inst,actionid,time,starttime):
	action = ''
	mode = ''
	temp = 0
	if actionid == '0':
		return '关闭','',''
	if actionid == '2':
		return '打开','',''
		
	if inst[0] == '0':
		action = '关闭'
	elif inst[0] == '1':
		if time == starttime:
			action = '打开'
		else:
			action = '调整'
	if inst[1] == '0':
		mode = '自动'
	elif inst[1] == '1':
		mode = '制冷'
	elif inst[1] == '2':
		mode = '制热'
	elif inst[1] == '3':
		mode = '抽湿'
	elif inst[1] == '4':
		mode = '送风'
	else:
		mode = '未知模式'
		
	if inst[2] == '1':
		temp = 32
	elif inst[3] == 'F':
		temp = 31
	elif inst[3] == 'E':
		temp = 30
	elif inst[3] == 'D':
		temp = 29
	elif inst[3] == 'C':
		temp = 28
	elif inst[3] == 'B':
		temp = 27
	elif inst[3] == 'A':
		temp = 26
	else:
		temp = 16 + int(inst[3])
	return action,mode,temp
	
def getActioninst(starttime, endtime, devid, start, length, draw):
	conditions = dict()
	if starttime != '' and endtime != '':
		conditions['time'] = {'$gte':starttime,'$lte':endtime}
	sort = [('time',1)]

	result = dict()
	resultlist = []
	count = 0
	devids = devid.split(',')
	datalist = []
	for id in devids:
		conditions['devid'] = id
		data = data_model('devcmd').find(conditions=conditions,sort=sort)
		count += len(data)
		action = ''
		for i in data:
			if 'actionid' not in i.keys():
				actionid = '6'
			else:
				actionid = i['actionid']
			temp = []
			temp.append(i['devid'])
			temp.append(common.strTimeToFormat(i['time']))
			temp.append(i['W'])
			action,mode,tempi = parseInst(i['inst'],actionid,i['time'],'')
			temp.append(action)
			temp.append(mode)
			temp.append(tempi)
			resultlist.append(temp)
		
	result = {"draw":draw,"recordsTotal":count,"recordsFiltered":count,"aaData":resultlist}
	return result
	
	
def getActioninfo(starttime,endtime,devid,start,length,draw):
	conditions = dict()
	if starttime != '':
		conditions['starttime'] = {'$gte':starttime}
	if endtime != '':
		conditions['endtime'] = {'$lte':endtime}
	sort = [('starttime',1)]

	result = dict()
	resultlist = []
	count = 0
	starti = 0
	devids = devid.split(',')
	datalist = []
	for id in devids:
		conditions['devid'] = id
		data = data_model('powershowgrid').find(conditions=conditions,sort=sort)
		datalist.append(data)
	for data in datalist:#处理每个设备
		for item in data:#处理某个设备的某一次完整操作
			for i in item['result']:
				if 'actionid' not in i.keys():
					i['actionid'] = 'null'
				if i['cmd'] == '3001':
					continue
				if i['inst'].startswith('0') or i['actionid'] == '0':
					count += 2 #每个结束动作都会有一个小的汇总信息
				elif i['inst'].startswith('1') or i['actionid'] == '2':
					count += 1 
		if len(data) > 0:
			count += 1 #最后设备在此查询时间段内会有一个总的汇总信息,若没有操作则没有汇总信息
	for data in datalist:
		if len(data) == 0:
			continue
		runtime = 0
		power = 0.0
		for item in data:
			stime = item['starttime']
			id = item['devid']
			for i in item['result']:
				if i['cmd'] == '3001':
					continue
				actionid = i['actionid']
				temp = []
				temp.append(item['devid'])
				temp.append(common.strTimeToFormat(i['time']))
				temp.append(i['W'])
				action,mode,tempi = parseInst(i['inst'],actionid,i['time'],stime)
				temp.append(action)
				temp.append(mode)
				temp.append(tempi)
				resultlist.append(temp)
			#添加小的汇总信息			
			finddata = data_model('actioninfo').find(conditions={'devid':id,'starttime':stime})
			temp = []
			temp.append(id)
			temp.append(finddata[0]['runtime'])
			runtime += finddata[0]['runtime']
			temp.append(finddata[0]['power'])
			power += finddata[0]['power']
			temp.append('')
			temp.append('')
			temp.append('')
			resultlist.append(temp)
		#添加总的汇总信息
		temp = []
		temp.append(id)
		temp.append(runtime)
		temp.append(float('%0.4f'%power))
		temp.append('')
		temp.append('')
		temp.append('')
		resultlist.append(temp)	
	result = {"draw":draw,"recordsTotal":count,"recordsFiltered":count,"aaData":resultlist}
	return result

class power():
	def __init__(self):
		return
		
	def GET(self):
		return render('power.html')
		
	def POST(self):
		data = web.input()
		start = int(data["start"])
		length = int(data["length"])
		starttime = data['starttime'].replace('/','').replace(' ','').replace(':','')+'00'
		endtime = data["endtime"].replace('/','').replace(' ','').replace(':','')+'00'
		devid = data['devid']
		userid = data['userid']
		draw = int(data['draw'])
		ordernum =  int(data['order[0][column]'])
		orderstyle = data['order[0][dir]']	
		ids = devid.split(',')
		result = []
		count = 0

		for id in ids:
			#conditions = dict()
			#conditions['devid'] = id
			#conditions['time'] = {'$lte':endtime,'$gte':starttime}
			#maxitem = data_model('devpower_detail').find(conditions=conditions,sort=sort1,limit=1)
			#minitem = data_model('devpower_detail').find(conditions=conditions,sort=sort2,limit=1)
			finddata = common.getPowerinfo(id,starttime,endtime)
			if len(finddata) == 0:
				continue
			else:
				count += 1
				temp = []
				max = finddata[-1]
				min = finddata[0]
				maxW = float('%0.4f'%max['W'])
				minW = float('%0.4f'%min['W'])
				maxTime = max['time']
				minTime = min['time']
				power = maxW - minW
				power = float('%0.4f'%power)
				temp.append(id)
				temp.append(power)
				temp.append(minW)
				temp.append(common.strTimeToFormat(minTime))
				temp.append(maxW)
				temp.append(common.strTimeToFormat(maxTime))
				result.append(temp)

		data = {"draw":draw,"recordsTotal":count,"recordsFiltered":count,"aaData":result}
		data = json.dumps(data)
		return data
		
class actioninfo():
	def __init__(self):
		return 
		
	def GET(self):
		return render('actioninfo.html')
	
	def POST(self):
		data = web.input()
		start = int(data["start"])
		length = int(data["length"])
		draw = int(data['draw'])
		devid = data['devid']
		type = data['type']
		ordernum =  int(data['order[0][column]'])
		orderstyle = data['order[0][dir]']
		starttime = data['starttime'].replace('/','').replace(' ','').replace(':','')+'00'
		endtime = data['endtime'].replace('/','').replace(' ','').replace(':','')+'00'
		data = dict()
		if type == '2':
			data = getActioninfo(starttime, endtime, devid, start, length, draw)
		elif type == '1':
			data = getActioninst(starttime, endtime, devid, start, length, draw)
		data = json.dumps(data)
		return data
		
class suminfo():
	def __init__(self):
		return
	def GET(self):
		return
	def POST(self):
		data = web.input()
		devid = data['devid']
		starttime = data['starttime'].replace('/','').replace(' ','').replace(':','')+'00'
		endtime = data['endtime'].replace('/','').replace(' ','').replace(':','')+'00'
		data = getSuminfo(devid,starttime,endtime)
		data = json.dumps(data)
		return data