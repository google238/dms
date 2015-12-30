#encoding:utf-8
import sys
sys.path.insert(0,'..')
import time
import datetime
import pymongo
import re
import operator
from model.data_model import *
#connection = pymongo.MongoClient("127.0.0.1", 28088)
#db = connection.dmsdata
import common.common as common 

def dealPower():
	#print "**********dealPower***********"
	tablename = "power_dataprocess"
	devIDlist = data_model('devID').find()
	for l in devIDlist:
		conditions = dict()
		conditions['devid'] = l['_id']
		sort = []
		temp = []
		temp.append('time')
		temp.append(pymongo.DESCENDING)
		sort.append(tuple(temp))
		finddata = data_model(tablename).find(sort=sort,limit=1,conditions=conditions)
		if len(finddata) == 0:
			pass
		else:
			time = finddata[0]['time']
			processdaytime = time[:8]
			insertitem = {'devid':l['_id'],'time':processdaytime,'W':float(finddata[0]['W'])}
			finditem = data_model('devpower_info').find(conditions={'devid':l['_id'],'time':processdaytime})
			if len(finditem) == 0:
				data_model('devpower_info').insert(insertitem)
			else:
				data_model('devpower_info').update_set(condition={'devid':l['_id'],'time':processdaytime},values={'W':float(finddata[0]['W'])})
			#common._LOG_DATAPROCESS.info(insertitem)
			
			processhourtime = time[:10]
			insertitem = {'devid':l['_id'],'time':processhourtime,'W':float(finddata[0]['W'])}
			finditem = data_model('devpower_hour').find(conditions={'devid':l['_id'],'time':processhourtime})
			if len(finditem) == 0:
				data_model('devpower_hour').insert(insertitem)
			else:
				data_model('devpower_hour').update_set(condition={'devid':l['_id'],'time':processdaytime},values={'W':float(finddata[0]['W'])})
			#common._LOG_DATAPROCESS.info(insertitem)
	data_model(tablename).drop()
	#print "OK!!!"
	


def dealHour():
	print "****************dealHour**********"
	cur = time.strftime('%Y%m%d%H%M%S',time.localtime(time.time()))
	processtime = cur[:10]
	tablename = "power_dataprocess"
	devIDlist = data_model('devID').find()
	for l in devIDlist:
		print l['_id']
		conditions = dict()
		conditions['devid'] = l['_id']
		conditions['time'] = re.compile(processtime)
		finddata = data_model(tablename).find(conditions=conditions)
		if len(finddata) == 0:
			pass
		else:
			finddata = sorted(finddata, key=operator.itemgetter('W'), reverse=True)
			maxdata = finddata[0]
			insertitem = {'devid':l['_id'],'time':processtime,'W':maxdata['W']}
			finditem = data_model('devpower_hour').find(conditions={'devid':l['_id'],'time':processtime})
			if len(finditem) == 0:
				data_model('devpower_hour').insert(insertitem)
			else:
				data_model('devpower_hour').update_set(condition={'devid':l['_id']},values={'W':maxdata['W']})
			common._LOG_DATAPROCESS.info(insertitem)
	data_model(tablename).drop()
	
def dealDay():
	print "****************dealDay**********"
	cur = time.strftime('%Y%m%d%H%M%S',time.localtime(time.time()))
	processtime = cur[:8]
	devIDlist = data_model('devID').find()
	for l in devIDlist:
		conditions = dict()
		conditions['devid'] = l['_id']
		conditions['time'] = re.compile(processtime)
		finddata = data_model('devpower_hour').find(conditions=conditions)
		if len(finddata) == 0:
			pass
		else:
			finddata = sorted(finddata, key=operator.itemgetter('W'), reverse=True)
			maxdata = finddata[0]
			insertitem  = {"devid":l['_id'],"time":processtime,"W":maxdata['W']}
			finditem = data_model('devpower_day').find(conditions={'devid':l['_id'],'time':processtime})
			if len(finditem) == 0:
				data_model('devpower_day').insert(insertitem)
			else:
				data_model('devpower_day').update_set(condition={'devid':l['_id']},values={'W':maxdata['W']})

def dealMonth():
	#print "****************dealMonth**********"
	cur = time.strftime('%Y%m%d%H%M%S',time.localtime(time.time()))
	processtime = cur[:6]
	devIDlist = data_model('devID').find()
	for l in devIDlist:
		conditions = dict()
		conditions['devid'] = l['_id']
		conditions['time'] = re.compile(processtime)
		finddata = data_model('devpower_info').find(conditions=conditions)
		if len(finddata) == 0:
			pass
		else:
			value = 0.0
			for i in finddata:
				value = value + float(i['W'])
			insertitem  = {"devid":l['_id'],"time":processtime,"W":value}
			finditem =  data_model('devpower_month').find(conditions={'devid':l['_id'],'time':processtime})
			if len(finditem) == 0:
				data_model('devpower_month').insert(insertitem)
			else:
				data_model('devpower_month').update_set(condition={'devid':l['_id'],'time':processtime},values={'W':value})
	#print "dealMonth OK!!"
				
def dealTemp():
	print "****************dealTemp**********"
	cur = datetime.datetime.now()
	processdate = cur - datetime.timedelta(days=31)
	processdate = processdate.strftime('%Y%m%d%H%M%S')
	condition = {'time':{'$lt':processdate}}
	data_model("live.area.temp.history").remove(condition)
	
def dataprocess():
	cur= datetime.datetime.now()
	year = cur.year
	month = cur.month
	day = cur.day
	hour = cur.hour
	min = cur.minute
	#如果是这个月的第一天0时则先不进行处理
	if day == 1 and hour == 0:
		pass
	#每小时从小时库里面进行一次运算，并将值更新
	elif min == 15:
		year = str(year)
		if month < 10:
			month = '0' + str(month)
		else:
			month = str(month)
		processDate = year + month
	
		devIDlist = data_model('devID').find()
		for l in devIDlist:
			devid = 'devPower.' + l["_id"]
			conditions = dict()
			conditions['key'] = devid
			conditions['time'] = re.compile(processDate)
			lastMonthValue = data_model('devPowerHour').find(conditions=conditions)
			value = 0
			for i in lastMonthValue:
				value = value + float(i['P'])
			insertitem  = {"key":devid,"time":processDate,"P":str(value)}
			print value
			if data_model('devPowerMonth').find_one(conditions={'key':devid,'time':processDate}) is None:
				data_model('devPowerMonth').insert(insertitem)
			else:
				data_model('devPowerMonth').update_set(condition={'key':devid},values={'P':str(value)})

if __name__ == "__main__":
	#首先将表名添加这系统用以展示
	#count = data_model('userfrom').count({"userFrom":'ps'})
	#if count == 0:
	#	data_model('userfrom').insert({'userFrom':'ps'})
	#count = data_model('ps').count({'tablename':'devpower_detail'})
	#if count == 0:
	#	data_model('ps').insert({'tablename':'devpower_detail'})	
	while 1:
	#	dealHour()
	#	dealDay()
		dealPower()
		dealMonth()		
	#	dealTemp()
		time.sleep(60*10)
		
