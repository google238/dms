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

	tablename = "powershowgrid_temp"
	data = data_model(tablename).find()
	for item in data:
		devid = item['devid']
		city = item['city']
		area = item['area']
		for i in item['result']:
			temp = dict()
			temp['devid'] = devid
			temp['city'] = city
			temp['area'] = area
			if i['cmd'] == 'devTodo':
				temp['temp'] = i['temp']
				temp['inst'] = i['inst'][:4]
				temp['time'] = i['time']
				data_model('modeldata').insert(temp)
	data_model(tablename).drop()

	


if __name__ == "__main__":	
	while 1:
		dealModel()	
		time.sleep(60*10)
		
