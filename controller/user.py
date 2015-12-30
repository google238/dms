#encoding:utf-8
import web
import datetime
import time
import pymongo
import string
import common.common as common 
from config.config_default import *
from model.data_model import *
from model.dms_model import *
from model.userfrom_model import *
import json
import common.unparse as unparse
import libraries.rec_config as rec_config
import model.redis_model as redis_model
from threading import Thread
import re
import operator
from bson.objectid import ObjectId


def startthread(data):
	t1 = Thread(target=run,args=(1,data))
	t1.start()
	pass

def getPosition(devid):
	cityname = ''
	area = ''
	findposition = data_model('dev_position').find_one(conditions={'_id':devid})
	if findposition is None:
		pass
	else:
		area = findposition['area']
		cityname = findposition['city']
		if area == '' or cityname == '':
			pass
	return cityname,area


def dealItem(item):
	if item['tablename'] == 'live.area.temp.history':
		insertitem = dict()
		province = item.get('province','')
		city = item.get('city','')
		area = item.get('area','')
		insertitem['province'] = province
		insertitem['city'] = city
		insertitem['area'] = area
		insertitem['index'] = 1.0
		windstate = item.get('windState','')
		statedetailed = item.get('stateDetailed','')
		
		if city == '':#无效天气数据不处理
			return
		'''#配置城市、天气指数
		itemfind = data_model('city_area').find_one(conditions={'province':province,'city':city,'area':area})
		if itemfind == None:
			data_model('city_area').insert(insertitem)
			
		itemfind = data_model('windstate').find_one(conditions={'_id':windstate})
		if itemfind == None:
			data_model('windstate').insert({'_id':windstate,'index':1.0})
		
		itemfind = data_model('stateDetailed').find_one(conditions={'_id':statedetailed})
		if itemfind == None:
			data_model('stateDetailed').insert({'_id':statedetailed,'index':1.0})	
        '''
		#用于统计月报中天气情况
		data_model('temperature_temp').insert({'province':province,'city':city,'area':area,'stateDetailed':statedetailed})
		
		temp1 = int(item['tem1'])
		temp2 = int(item['tem2'])
		if temp1 > temp2 :
			high = temp1
			lower = temp2
		else:
			high = temp2
			lower = temp1
		time = item['time'][:8]
		data_model('temperature').update_set(condition={'city':city,'area':area,'time':time},values={'high':high,'lower':lower},upsert=True)	
		data_model('live.area.temp.new').update_set(condition={'city':city,'area':area,'province':province},values=item,upsert=True)
		
	elif item['tablename'] == 'loger':
		if 'datetime' in item.keys():
			item['acceptTime'] = item['datetime']
			del item['datetime']
		if 'socketOut_P' in item['content'].keys() and 'socketOut_W' in item['content'].keys():
			item['content']['socketOut_P'] = int(item['content']['socketOut_P'])
			item['content']['socketOut_W'] = float('%0.4f'%(float(item['content']['socketOut_W'])))
		system = item['system']
		content = item['content']
		#处理设备从开至关这段时间电量功率数据
		if 'devID' in content.keys() and 'CMD' in content.keys():		
			devID = content['devID']
			data_model('devID').update_set(condition={'_id':devID},values={'system':system},upsert=True)
			cmd = content['CMD']
			time = item['acceptTime']
			todaytime = time[:8]
			userName = ''
			sender = ''
			if 'userName' in content.keys() and 'sender' in content.keys():
				userName = content['userName']
				sender = content['sender']
				data_model('user_dev').update_set(condition={'_id':devID},values={'username':userName,'sender':sender},upsert=True)
			if devID == '':
				return
			if cmd == 'devTodo':
				if content['actionID'] == '2':#插座开
					finditem = data_model('action').find_one(conditions={'devid':devID,'actionid':'6'})
					if finditem is None:#若找到actionid为6说明已经以空调类型操作过，现在是插拔
						pass
					else:
						return
					insertitem = dict()
					insertitem['devid'] = devID
					insertitem['time'] = time
					insertitem['cmd'] = cmd 
					insertitem['inst'] = 'null'
					insertitem['actionid'] = '2'
					findpower = data_model('power_dataprocess').find(conditions={'devid':devID,'time':re.compile(todaytime)},sort=[('time',-1)],limit=1)
					if len(findpower) == 0:
						tablename = "devpower_detail_" + todaytime
						findpower = data_model(tablename).find(conditions={'devid':devID},sort=[('time',-1)],limit=1)
					if len(findpower) == 0:
						insertitem['W'] = 0
					else:
						insertitem['W'] = findpower[0]['W']
					insertitem['P'] = 0
					insertitem['temp'] = ''
					
					#查找之前是否有开动作，有的话先删除再插入
					finditem = data_model('action').find(conditions={'devid':devID,'actionid':'2'},sort=[('time',-1)],limit=1)
					if len(finditem) == 0:
						pass
					else:
						data_model('action').remove(condition={'devid':devID})
					data_model('action').insert(insertitem)	
					data_model('devcmd').insert(insertitem)
					#记录设备类型,1代表普通插座，2代表空调，3代表空净
					data_model('dev_type').update_set(condition={'_id':devID},values={'type':1},upsert=True)
				elif content['actionID'] == '0':#插座关
					finditem = data_model('action').find(conditions={'devid':devID,'actionid':'2'},sort=[('time',-1)],limit=1)
					if len(finditem) == 0:#没有找到开动作
						data_model('action').remove(condition={'devid':devID})
						return
					insertitem = dict()
					insertitem['devid'] = devID
					insertitem['time'] = time
					insertitem['cmd'] = 'devTodo' 
					insertitem['inst'] = 'null'
					insertitem['actionid'] = '0'
					findpower = data_model('power_dataprocess').find(conditions={'devid':devID,'time':{'$lte':time,'$gt':todaytime}},sort=[('time',-1)],limit=1)
					if len(findpower) == 0:
						tablename = "devpower_detail_" + todaytime
						findpower = data_model(tablename).find(conditions={'devid':devID,'time':{'$lte':time}},sort=[('time',-1)],limit=1)
					if len(findpower) == 0:
						insertitem['W'] = 0
					else:
						insertitem['W'] = findpower[0]['W']
					insertitem['P'] = 0
					insertitem['temp'] = ''
					data_model('action').insert(insertitem)
					data_model('devcmd').insert(insertitem)
					starttime = finditem[0]['time']
					endtime = time
					#查找时间段内的数据集
					findset = common.getPowerinfo(devID,starttime,endtime)
					if len(findset) == 0:#这段时间内没有电量信息，忽略本次操作
						data_model('action').remove(condition={'devid':devID})
						return
					findlist = []
					del finditem[0]['_id'] #添加开动作
					findlist.append(finditem[0])
					for item in findset:
						del item['_id']
						item['cmd'] = '3001'
						item['inst'] = ''
						item['actionid'] = ''
						item['temp'] = ''
						findlist.append(item)
					del insertitem['_id']
					findlist.append(insertitem)#添加关动作
					offset,minw,maxw = common.getOffset(findlist)
					p = 0
					findset = sorted(findset, key=operator.itemgetter('P'), reverse=True)
					p = findset[0]['P']										
					if p != 0: # =0的话说明动作时间过短，还没有采集到用电量，本次操作无意义
						cityname,area = getPosition(devID)
						result = {'devid':devID,'type':1,'starttime':starttime,'endtime':endtime,'offset':offset,'result':findlist,'maxP':p,'maxW':maxw,'minW':minw,'city':cityname,'area':area}
						data_model('powershowgrid').insert(result)
						sendToapp = dict()
						sendToapp['devID'] = devID
						sendToapp['CMD'] = 'M0A0'
						sendToapp['userName'] = userName
						sendToapp['sender'] = sender
						sendToapp['type'] = 0
						sendToapp['url'] = ''
						powervalue = float(maxw) - float(minw)
						powervalue = float('%0.4f'%powervalue)			
						runtime = common.timePoor(starttime,endtime)
						runh,runm,runs = common.secTohms(runtime)
						actioninfo = {'devid':devID,'starttime':starttime,'endtime':endtime,'runtime':runtime,'power':powervalue,'P':p}
						data_model('actioninfo').insert(actioninfo)
						sy = starttime[:4]
						sM = starttime[4:6]
						sd = starttime[6:8]
						sh = starttime[8:10]
						sm = starttime[10:12]
						ss = starttime[12:14]
						ey = endtime[:4]
						eM = endtime[4:6]
						ed = endtime[6:8]
						eh = endtime[8:10]
						em = endtime[10:12]
						es = endtime[12:14]
						context = "您的设备%s从%d年%d月%d日%d时%d分%d秒至%d年%d月%d日%d时%d分%d秒共运行时长%d时%d分%d秒,共耗电%0.4f度" % (devID[:15],int(sy),int(sM),int(sd),int(sh),int(sm),int(ss),int(ey),int(eM),int(ed),int(eh),int(em),int(es),runh,runm,runs,powervalue)
						sendToapp['content'] = context
						sendToapp['pushTime'] = ''
						sendToapp['time'] = time
						#data_model('sendtoapp').insert(sendToapp)
					data_model('action').remove(condition={'devid':devID})				
				if 'actionID' in content.keys() and 'inst' in content.keys():
					if content['actionID'] == '6':#空调或者空净设备
						if content['inst'].startswith('T'):#空净,待处理
							data_model('dev_type').update_set(condition={'_id':devID},values={'type':3},upsert=True)
							return
						data_model('dev_type').update_set(condition={'_id':devID},values={'type':2},upsert=True)
						cityname,area = getPosition(devID)
						if cityname == '' or area == '':#没有地理信息
							temp = ''
						else:
							if cityname == '北京市' or cityname == '天津市' or cityname == '上海市' or cityname == '重庆市':
								area = area[:-1]
							cityname = cityname[:-1]
							findtemp = data_model('live.area.temp.new').find(conditions={'city':cityname,'area':area,'time':{'$lte':time}},limit=1,sort=[('time',-1)])
							if len(findtemp) == 0:#没有天气信息
								temp = ''
							else:
								temp = findtemp[0]['temNow']
						insertitem = dict()
						insertitem['devid'] = devID
						insertitem['time'] = time
						insertitem['cmd'] = 'devTodo' 
						insertitem['inst'] = content['inst']
						insertitem['actionid'] = '6'
						findpower = data_model('power_dataprocess').find(conditions={'devid':devID,'time':{'$lte':time,'$gt':todaytime}},sort=[('time',-1)],limit=1)
						if len(findpower) == 0:
							tablename = 'devpower_detail_' + todaytime
							findpower = data_model(tablename).find(conditions={'devid':devID,'time':{'$lte':time}},sort=[('time',-1)],limit=1)
							if len(findpower) == 0:
								insertitem['W'] = 0
							else:
								insertitem['W'] = findpower[0]['W']
						else:
							insertitem['W'] = findpower[0]['W']
						insertitem['P'] = 0
						insertitem['temp'] = temp
						data_model('devcmd').insert(insertitem)
						data_model('action').insert(insertitem)		
						if content['inst'].startswith('0'):
							#查找最早的一条开启状态的指令时间
							conditions = dict()
							conditions['devid'] = devID	
							conditions['actionid'] = '6'
							findcmd = data_model("action").find(conditions=conditions,sort=[('time',1)])
							if len(findcmd) <= 1:#只有一条关动作
								data_model('action').remove(condition={'devid':devID})
								return 
							else:
								starttime = findcmd[0]['time']
							endtime = time
							#查找时间段内的数据集
							findset = common.getPowerinfo(devID,starttime,endtime)
							if len(findset) == 0:
								data_model('action').remove(condition={'devid':devID})
								return
							findlist = []
							for item in findcmd: #将开动作、调整指令添加进列表
								del item['_id']
								findlist.append(item)
							for item in findset:
								del item['_id']
								item['cmd'] = '3001'
								item['inst'] = ''
								item['actionid'] = ''
								item['temp'] = ''
								findlist.append(item)
							findlist = sorted(findlist,key=operator.itemgetter('time'),reverse=False)
							offset,minw,maxw = common.getOffset(findlist)
							p = 0
							findset = sorted(findset, key=operator.itemgetter('P'), reverse=True)
							p = findset[0]['P']							
							if p != 0:# =0 的话说明动作时间过短，还没有采集到用电量，本次操作无意义
								result = {'devid':devID,'type':2,'starttime':starttime,'endtime':endtime,'offset':offset,'result':findlist,'maxP':p,'maxW':maxw,'minW':minw,'city':cityname,'area':area}
								data_model('powershowgrid').insert(result)
								data_model('powershowgrid_temp').insert(result)
								sendToapp = dict()
								sendToapp['devID'] = devID
								sendToapp['CMD'] = 'M0A0'
								sendToapp['userName'] = userName
								sendToapp['sender'] = sender
								sendToapp['type'] = 0
								powervalue = float(maxw) - float(minw)
								powervalue = float('%0.3f'%powervalue)
								runtime = common.timePoor(starttime,endtime)
								worktime = common.worktime(findlist)
								if runtime < worktime:
									runtime,worktime = worktime,runtime
																
								runh,runm,runs = common.secTohms(runtime)
								workh,workm,works = common.secTohms(worktime)
								worktimetab = 'worktime_' + time[:6]
								#data_model('worktime').update_inc(condition={'_id':devID},values={'worktime':worktime,'runtime':runtime},upsert=True)
								
								#计算单次使用的清洗指数
								if 'cityname' == '' or 'area' == '':
									cityindex = 1
									weatherindex = 1
								else:
									findcity = data_model('city_area').find_one(conditions={'area':area,'city':cityname})
									if findcity is None:
										cityindex = 1
									else:
										cityindex = findcity['index']
								findtemp = data_model('live.area.temp.new').find(conditions={'city':cityname,'area':area})
								if len(findtemp) == 0:
									weatherindex = 1
								else:
									weather = findtemp[0]['stateDetailed']
									findweather = data_model('stateDetailed').find_one(conditions={'_id':weather})
									if findweather is None:
										weatherindex = 1
									else:
										weatherindex = findweather['index']
								index = runtime * cityindex * weatherindex
								data_model('dev_index').update_inc(condition={'_id':devID},values={'index':index},upsert=True)
								finditem = data_model('dev_index').find_one(conditions={'_id':devID})
								index = finditem.get('index',0)
								index = int(index/3600)
								data_model(worktimetab).update_inc(condition={'_id':devID},values={'worktime':worktime,'runtime':runtime,'power':powervalue},upsert=True)
								actioninfo = {'devid':devID,'starttime':starttime,'endtime':endtime,'runtime':runtime,'worktime':worktime,'power':powervalue,'P':p}
								data_model('actioninfo').insert(actioninfo)
								context = "您的设备%s运行" %(devID[:15][-4:])
								if runh > 0:
									s = '%d小时%d分钟,耗电%0.3f度'%(runh,runm,powervalue)
								else:
									if runm > 0:
										s = '%d分钟,耗电%0.3f度'%(runm,powervalue)
									else:
										s = '%d秒,耗电%0.3f度'%(runs,powervalue) 
								context = context + s
								sendToapp['content'] = context
								sendToapp['pushTime'] = ''
								sendToapp['time'] = time
								sendToapp['system'] = system
								sendToapp['url'] = 'http://%s/report/single?devid=%s&starttime=%s&endtime=%s&runtime=%d&worktime=%d&power=%0.3f&P=%d&index=%d'%(server,devID,starttime,endtime,runtime,worktime,powervalue,p,index)
								if powervalue > 0.001 and runh < 24 and p>0:
									data_model('sendtoapp').insert(sendToapp)
									data_model('sendtoapp1').insert(sendToapp)
							data_model('action').remove(condition={'devid':devID})
			elif cmd == '3001':
				#更新电量详情表
				tablename = 'devpower_detail_' + todaytime
				gdt_tablename = 'devpower_detail_gdt_' + todaytime
				item = {'_id':devID}
				data_model('devID').update_set(condition=item,values=item,upsert=True)
				if 'socketOut_P' in content.keys() and content['socketOut_P']> 0:
					W = float('%0.4f'%content['socketOut_W'])
					P = int(content['socketOut_P'])
					insertdata = {'time':time,'devid':devID,'W':W,'P':P}
					data_model(tablename).insert(insertdata)
					data_model("power_dataprocess").insert(insertdata)
							
					#处理第三方系统的电量功率
					dealPower_gdt(devID,gdt_tablename,insertdata)
					
				#处理功率为0
				elif 'socketOut_P' in content.keys() and content['socketOut_P'] == 0:
					W = float('%0.4f'%content['socketOut_W'])
					P = content['socketOut_P']
					findone = data_model(tablename).find(conditions={'devid':devID},sort=[('time',-1)],limit=1)
					if len(findone) == 0 or findone[0]['P']>0: 
						insertdata = {'time':time,'devid':devID,'W':W,'P':P}				
						data_model(tablename).insert(insertdata)
					elif findone[0]['P'] == 0:
						insertdata = {'time':time,'devid':devID,'W':W,'P':-1}				
						data_model(tablename).insert(insertdata)
					elif findone[0]['P'] < 0:
						P1 = findone[0]['P']
						time1 = findone[0]['time']
						_id = findone[0]['_id']
						P2 = P1 - 1
						data_model(tablename).update_set(condition={'_id':ObjectId(_id)},values={'time':time,'P':P2},upsert=True)
	
			elif cmd == 'cleanliness':
				#用户清洗指数归0
				data_model('dev_index').update_set(condition={'_id':devID},values={'index':0,'update':todaytime},upsert=True)				
			elif cmd == 'A6A0':
				city = content.get('city','')
				area = content.get('area','')
				sender = content.get('sender','')
				username = content.get('userName','')
				data_model('dev_position').update_set(condition={'_id':devID},values={'system':system,'city':city,'area':area,'sender':sender,'time':time,'username':username},upsert=True)
				
				appid = content.get('appid','')
				#if appid == 'guodiantong':
				#	data_model('whitelist_gdt').update_set(condition={'_id':devID},values={'system':system,'city':city,'area':area,'sender':sender,'time':time,'username':username},upsert=True)
				if appid != '':
					data_model('appID').update_set(condition={'_id':appid},values={'_id':appid},upsert=True)
					table = 'whitelist_' + appid
					data_model(table).update_set(condition={'_id':devID},values={'system':system,'city':city,'area':area,'sender':sender,'time':time,'username':username},upsert=True)

def dealPower_gdt(devID,gdt_tablename,insertdata):
	W = insertdata.get('W')
	findid = data_model('whitelist_guodiantong').find_one(conditions={'_id':devID})
	if findid is None:
		pass
	else:
		findone = data_model(gdt_tablename).find(conditions={'devid':devID},sort=[('time',-1)])
		if len(findone) == 0:
			insertdata['base'] = 0
		else:
			pre_W = findone[0].get('W',0)
			base = findone[0].get('base',0)
			if W >= pre_W:
				insertdata['base'] = base
			else:
				base += pre_W
				insertdata['base'] = base
		data_model(gdt_tablename).insert(insertdata)
					
#def run(n,data):
def deal(data):
	result = {"status":0,"msg":"","options":{}}		
	msg = json.loads(data)
		
	#读取字典内容
	if "userFrom" not in msg.keys():
		result["status"] = 1
		result["msg"] = "缺少必要字段"
		return result
	if "tagID" not in msg.keys():
		result["status"] = 1
		result["msg"] = "缺少必要字段"
		return result		
	if "options" not in msg.keys() or len(msg["options"])<1:
		result["status"] = 1
		result["msg"] = "无有效数据保存"
		return result
	'''		
	userFrom = msg["userFrom"].lower()
	tagID = msg["tagID"]
	condition = {"userFrom":userFrom}
	item = dms_model().find_one(condition)
	if not item:
		result["status"] = 1
		result["msg"] = "此系统还未注册"
		return result
	if int(item["tagID"]) == tagID:
		pass
	else:
		result["status"] = 1
		result["msg"] = "业务名与业务ID不符"
		return result
	level = string.atoi(item["level"])	
	conditions = dict()
	conditions["userFrom"] = userFrom
	set = userfrom_model().count(conditions)
	if set == 0:
		userfrom_model().insert(conditions)
    '''
	level = 1
	data = msg["options"]
	#获取数据表名
	tablename = data[0]['tablename']
	#insertdata = {"tablename":tablename}
	#set = data_model(userFrom).count(insertdata)
	#if set == 0:
	#	data_model(userFrom).insert(insertdata)

	for item in data:
		item["acceptTime"] = time.strftime('%Y%m%d%H%M%S',time.localtime(time.time()))
		if tablename == 'loger' and 'CMD' in item['content'].keys() and item['content']['CMD'] == '3001' and 'connInterval' in item['content'].keys():#过滤掉请求获取电量信息的指令
			continue
		if tablename == 'live.area.temp.history' and item['key'].startswith('1'):#过滤掉天气数据中key为代号的信息
		#if tablename == 'live.area.temp.history' and 'key' in item.keys():#过滤掉天气数据中含key的记录
			continue
		if tablename == 'loger' or tablename == 'live.area.temp.history':
			dealItem(item)
		try:
			if tablename == 'devCurrInfo':
				devid = item.get('deviceId','None')
				item["acceptTime"] = time.strftime('%Y%m%d%H%M%S',time.localtime(time.time()))
				data_model('devCurrInfo').remove(condition={'deviceId':devid})
				data_model('devCurrInfo').insert(item)
			elif tablename == 'live.area.temp.history':
				if item.get('city','') == '':
					pass
				else:
					data_model(tablename).insert(item)
			elif tablename == 'machinelearning_d_YSJ':
				id = item.get('_id')
				data_model(tablename).update_set(condition={'_id':id},values=item,upsert=True)
			elif tablename == 'devPower_P' or tablename == 'user_position':
				pass
			else:
				data_model(tablename).insert(item)
		except Exception as e:
			print e
		#	common._LOG.info('%s:%s'%(type(e), str(e)))	
		#	common._LOG.info("保存失败!")
			
	result["status"] = 0
	result["msg"] = "OK"
	return result
	
class user():
	def __init__(self):
		return
		
	def GET(self):
		result = {"status":0,"msg":"","options":{}}
		i = web.input()
		userfrom = i.get("userFrom").lower()
		condition = {'userFrom': userfrom}
		item = dms_model().find_one(condition)

		if not item:
			result["status"] = 1
			result["msg"] = "系统还未注册"
			return result
		else:
			result["status"] = 0
			result["msg"] = "OK"
			result["options"]["tagID"] = item["tagID"]
			return result			

	def POST(self):
		result = {"status":0,"msg":"OK"}		
		data = web.data()
		result = deal(data)
		return result
