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
session = web.config._session

j = web.storage()


def getPower_detail(starttime, endtime, devid, start, length, draw):
	finddata = common.getPowerinfo(devid,starttime,endtime)
	count = len(finddata)
	starti = 0
	result = dict()
	resultlist = []
	for item in finddata:
		if starti != start:
			starti += 1
			continue
		del item["_id"]
		if "tablename" in item.keys():
			del item["tablename"]
		keys = item.keys()
		temp = []
		for key in keys:			
			if key.lower().find("time") != -1:		
				item[key] = common.strTimeToFormat(item[key])
			if isinstance(item[key],dict):
				item[key] = unparse.dictTostr(item[key])
			if key == "_id":
				item[key] = str(item[key])
			temp.append(item[key])		
		resultlist.append(temp)
		if len(resultlist) == length:
			break
	result = {"draw":draw,"recordsTotal":count,"recordsFiltered":count,"aaData":resultlist}
	return result
	
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
			temp.append(item['devid'])
			temp.append(i['temp'])
			temp.append(i['W'])
			temp.append(i['P'])
			temp.append(common.strTimeToFormat(i['time']))
			if i['cmd'] == '3001':
				temp.append('持续状态')
			elif i['cmd'] == 'devTodo':
				if i['inst'].startswith('0'):
					temp.append('关闭')
				elif i['inst'].startswith('1'):
					if i['time'] == item['starttime']:
						temp.append("打开(" + i['inst'] + ")")
					else:
						temp.append("调整温度模式(" + i['inst'] + ")")
				else:
					if i['actionid'] == '2':
						temp.append("打开")
					if i['actionid'] == '0':
						temp.append("关闭")
			resultlist.append(temp)
			if len(resultlist) == length:
				break
		if len(resultlist) == length:
			break

	result = {"draw":draw,"recordsTotal":count,"recordsFiltered":count,"aaData":resultlist}
	return result

class data:
	def __init__(self):
		return 
		
	def GET(self):
		return render("data.html")

	def POST(self, *args):
		data = web.input()
		start = int(data["start"])
		length = int(data["length"])
		userfrom = data['userFrom']
		tablename = data["tablename"]
		draw = int(data['draw'])
		ordernum =  int(data['order[0][column]'])
		orderstyle = data['order[0][dir]']
		conditions = {}
		keys = []
		sort = []
		#获取字段名,设定排序条件
		first = data_model(tablename).find_one()
		del first['_id']
		if userfrom == "业务持久化存储服务":
			devid = ''
			starttime = ''
			endtime = ''	
			if "devid" in data.keys():
				devid = data['devid']
				conditions['devid'] = data['devid']
			if 'starttime' in data.keys() and 'endtime' in data.keys() :
				starttime = data['starttime'].replace('/','').replace(' ','').replace(':','')+'00'
				endtime = data['endtime'].replace('/','').replace(' ','').replace(':','')+'00'
				conditions['time'] = {'$gte':starttime,'$lte':endtime}
			elif 'starttime' in data.keys():
				starttime = data['starttime'].replace('/','').replace(' ','').replace(':','')+'00'
				conditions['time'] = {'$gte':starttime}
			elif 'endtime' in data.keys():
				endtime = data['endtime'].replace('/','').replace(' ','').replace(':','')+'00'
				conditions['time'] = {'$lte':endtime}
			keys = first.keys()

			if tablename == 'powershowgrid':
				data = dict()
				data = getCmd_power(starttime, endtime, devid, start, length, draw)
				data = json.dumps(data)
				return data
				
			elif tablename == 'devpower_detail':
				data = dict()
				data = getPower_detail(starttime, endtime, devid, start, length, draw)
				data = json.dumps(data)
				return data
				
		else:
			for key in first.keys():
				if key == "_id" or key == "tablename":
					pass
				else:
					if key in data.keys():#设定查询条件，以%%包围的属于模糊匹配，以‘[’或‘（’开头的属于范围内查找，以‘{}’包围的属于子内容查找，其他请求属于精确匹配
	#					conditions[key] = data[key]
						try:
							value = data[key]
							if value[0] == '%' or value[-1] == '%':#模糊匹配
								pass						
							elif value[0] == '(' or value[0] == '[':
								list = value.split(':')
								left = list[0].split(' ')
								right = list[1].split(' ')
								if left[1] == '':#<=
									if right[1] == ')':
										conditions[key] = {"$lt":right[0]}
									elif right[1] == ']':
										conditions[key] = {"$lte":right[0]}
								elif right[0] == '':#>=
									if left[0] == '(':
										conditions[key] = {"$gt":left[1]}
									elif left[0] == '[':
										conditions[key] = {"$gte":left[1]}
								else:#区间
									tag_left = ''
									tag_right = ''
									if left[0] == '(':
										tag_left = "$gt"
									elif left[0] == '[':
										tag_left = "$gte"
									if right[1] == ')':
										tag_right = "$lt"
									elif right[1] == ']':
										tag_right = "$lte"
									conditions[key] = {tag_left:left[1],tag_right:right[0]}
							elif value[0] == '{' and value[-1] == '}':
								temp = value.split('{')[1].split('}')[0]
								list = temp.split(',')
								for item in list:
									key_child = item.split(':')[0]
									value = item.split(':')[1]
									conditions[key + '.' + key_child] = value
							else:
								conditions[key] = data[key]	
						except Exception as e:
							data = {"draw":draw,"recordsTotal":0,"recordsFiltered":0,"aaData":[]}
							data = json.dumps(data)
							return data					
					keys.append(key)	
	
		temp = []
		ordercolumn = keys[ordernum]
		if orderstyle == 'asc':			
			temp.append(ordercolumn)
			temp.append(pymongo.ASCENDING)
			sort.append(tuple(temp))
		else:
			temp.append(ordercolumn)
			temp.append(pymongo.DESCENDING)
			sort.append(tuple(temp))

		count = data_model(tablename).count(conditions=conditions)
		set = data_model(tablename).find(limit=length,skip=start,sort=sort,conditions=conditions)
		result = []
		for item in set:		
			del item["_id"]
			if "tablename" in item.keys():
				del item["tablename"]
			keys = item.keys()
			temp = []
			for key in keys:			
				if key.lower().find("time") != -1:		
					item[key] = common.strTimeToFormat(item[key])
				if isinstance(item[key],dict):
					item[key] = unparse.dictTostr(item[key])
				if key == "_id":
					item[key] = str(item[key])
				temp.append(item[key])
				
			result.append(temp)
		data = {"draw":draw,"recordsTotal":count,"recordsFiltered":count,"aaData":result}
		data = json.dumps(data)
		return data		

class power():
	def __init__(self):
		return
	def GET(self):
		result = dict()
		i = web.input()
		common._LOG.info(str(i))
		if 'devid' in i.keys() and 'time' in i.keys():
			pass
		else:
			return
		devid = i.get('devid')
		datetime = i.get('time')	
		conditions = dict()
		conditions['devid'] = devid
		conditions['time'] = datetime
		finditem = data_model('devpower_info').find(conditions=conditions)
		if len(finditem) == 0:
			return 
		else:
			del finditem[0]['_id']
			return finditem[0]
					
class rank():
	def __init__(self):
		return
	def GET(self):
		result = dict()
		i = web.input()
		common._LOG.info(str(i))
		devid = ''
		nowtime = time.strftime('%Y%m%d%H%M%S',time.localtime(time.time()))
		datetime = nowtime[:8]
		if 'devid' in i.keys():
			devid = i.get('devid')
		if 'time' in i.keys():
			datetime = i.get('time')
		conditions = dict()
		conditions['time'] = datetime
		if devid != '':
			conditions['devid'] = devid
			finditem = data_model('devpower_info').find_one(conditions=conditions)
			if finditem == None:#当日无耗电
				count = data_model('devpower_info').count(conditions={'time':datetime})
				result['count_gt'] = count
				result['count_lt'] = 0
				result['W'] = 0
				result = json.dumps(result)
				return result
			gtdata = data_model('devpower_info').find(conditions={'W':{'$gt':finditem['W']},'time':datetime})
			count_gt = len(gtdata)
			ltdata = data_model('devpower_info').find(conditions={'W':{'$lt':finditem['W']},'time':datetime})
			count_lt = len(ltdata)
			result['count_gt'] = count_gt
			result['count_lt'] = count_lt
			result['W'] = finditem['W']
			result = json.dumps(result)
			return result
		else:
			finddata = data_model('devpower_info').find(conditions=conditions)
			finddata = sorted(finddata, key=operator.itemgetter('W'), reverse=True)			
			for item in finddata:
				del item['_id']
			finddata = json.dumps(finddata)
			return finddata
			
class useractive():
	def __init__(self):
		return
	def POST(self):
		data = web.data()
		return 'OK'
		
		
		
		