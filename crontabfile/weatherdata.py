#encoding:utf-8
import sys
sys.path.insert(0,'..')
import time
import datetime
import pymongo
import re
import operator
from model.data_model import *
import common.common as common 

def dealModel():
#	print "**********dealModel***********"
	tablename = "temperature_temp"
	now = time.strftime('%Y%m')
	tablename1 = 'weather_' + now
	finddata = data_model(tablename).find()
	data_model(tablename).drop()
	for item in finddata:
		province = item['province']
		city = item['city']
		area = item['area']
		statedetailed = item['stateDetailed']			
		finditem = data_model(tablename1).find_one(conditions={'city':city,'area':area,'province':province})

		if finditem is None:
			data_model(tablename1).insert({'city':city,'area':area,'province':province,statedetailed:1})
		else:
			if statedetailed not in finditem.keys():
				data_model(tablename1).update_set(condition={'city':city,'area':area,'province':province}, values={statedetailed:1})
			else:
				data_model(tablename1).update_inc({'city':city,'area':area,'province':province},values={statedetailed:1})
	
#	print 'ok'
	
if __name__ == "__main__":	
	while 1:
		dealModel()	
		time.sleep(60*60)	

		
