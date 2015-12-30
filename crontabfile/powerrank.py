#-*-coding:utf-8-*-
import sys
sys.path.insert(0,'..')
import time
import datetime
import pymongo
import re
import operator
from model.data_model import *
import common.common as common 
#import sys
reload(sys)
sys.setdefaultencoding('utf-8')

def dealPowerrank(d3):
	tablename = "devpower_detail_" + d3
	devIDlist = data_model('devID').find()
	for l in devIDlist:
		conditions = dict()
		conditions['devid'] = l['_id']
		finddata = data_model(tablename).find(conditions=conditions,sort=[('time',1)])
		if len(finddata) == 0:
			pass
		else:
			offset = 0
			maxW = finddata[-1]['W']
			w1 = 0
			w2 = 0
			for i in finddata:
				w2 = i['W']
				if w2 < w1:
					offset += w1
				w1 = w2		
			maxW += offset
			insertitem = dict()
			insertitem['devid'] = l['_id']
			insertitem['W'] = float('%0.4f'%maxW)	
			insertitem['time'] = d3
			#data_model('devpower_temp').insert(insertitem)
			data_model('devpower_temp').update_set(condition={'devid':l['_id'],'time':d3},values=insertitem,upsert=True)
			
			
def createReport(d3):	

	finddata = data_model('devpower_temp').find(conditions={'time':d3},sort=[('W',-1)])
	count = len(finddata)
	if count == 0:
		return
	else:
		ranking = 1
		for item in finddata:
			power = item['W']
			devid = item['devid']
			username = ''
			sender = ''
			finditem = data_model('user_dev').find_one(conditions={'_id':devid})
			if finditem is None:
				findsender = data_model('dev_position').find_one(conditions={'_id':devid})
				if findsender is None:
					pass
				else:
					if 'sender' in findsender.keys():
						sender = findsender['sender']
			else:
				username = finditem['username']
				sender = finditem['sender']
			if ranking == count:
				rate = 0
			else:
				rate = float('%0.3f'%(float(count - ranking)/count)) * 100
			content = "您的设备%s昨日耗电%0.4f度，在活动用户中排名第%d，您的用电量高于%d%%的人"%(devid[:15],power,ranking,rate)
			insertitem = dict()
			insertitem['devid'] = devid
			insertitem['time'] = d3
			insertitem['sender'] = sender
			insertitem['username'] = username
			insertitem['power'] = float('%0.4f'%power)
			insertitem['count'] = count
			insertitem['ranking'] = ranking
			insertitem['rate'] = rate
			insertitem['content'] = content
			#data_model('power_ranking').insert(insertitem)
			data_model('power_ranking').update_set(condition={'devid':devid,'time':d3},values=insertitem,upsert=True)
			ranking += 1
	
if __name__ == "__main__":
	d1 = datetime.datetime.now()
	d3 = d1 - datetime.timedelta(days=1)
	d3 = d3.strftime('%Y%m%d')
	dealPowerrank(d3)
	createReport(d3)	
