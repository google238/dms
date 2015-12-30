#!/usr/bin/python
# -- coding: utf8 --
__author__ = 'wen'
import traceback
import json
import urllib2

# 配置服务器redis连接信息
# 发送数据给dms
#10.9.23.219
#118.192.76.159
dms_addr = "http://118.192.76.159/dms/useractive"
send_url = {
	'loger' : 'http://coachuatiis.chinacloudapp.cn:8060/getData.ashx'
}

def send_data(data):
	"""
	:rtype : object
	"""
	if not data:
		return
	# 发送数据到dms
	# headers = {'content-type': 'application/json'}
	rec = Rec_params(data)
	response = doHTTPRequest(dms_addr, data=rec.get_data())

def doHTTPRequest(serviceURL, data=""):
	returnData = ''
	try:
		if data:
			#post
			req = urllib2.Request(serviceURL, data)
		else:
			#get
			req = urllib2.Request(serviceURL)	
		response = urllib2.urlopen(req)
		returnData = response.read()
	except Exception:
		print returnData
		traceback.print_exc()
	return returnData


class Rec_params(object):

	def __init__(self, data):
		self.data = data

	def get_data(self):
		"""
		:return: json
		"""    
		return json.dumps(self.data)

		
def Send(data):
	#data = json.dumps(data)
	send_data(data)
