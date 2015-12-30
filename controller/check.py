# coding: utf-8
import json
import types
import web
import sys
import hashlib
import urllib2
import uuid
import string
from datetime import *
import time
import operator
from model.data_model import *
from libraries.utils import render, now4yMdHms , http_post
from libraries.decorator import admin_login
import common.common as common 
import common.unparse as unparse
session = web.config._session

j = web.storage()

# ------------------------------------------------------------------------------------------------
# ******************************************************
# ***********检测信息图片上传*********************************
# ******************************************************
# ------------------------------------------------------------------------------------------------

LINEND = '\r\n'
PREFIX = '--'
CHARSET = 'UTF-8'

def buildFileAuth():
	auth = {"time": str(int(time.time() * 1000)), "username": auth_name}
	auth["secret"] = hashlib.md5(auth["time"][4:len(auth["time"])]+auth["username"]).hexdigest()

	return json.dumps(auth,separators=(',', ':'))


def buildHttpData(auth, filename, inputParams):
	BOUNDARY = uuid.uuid4().hex
	data = [PREFIX, BOUNDARY, LINEND, 'Content-Disposition: form-data; name="Auth"', LINEND,
			'Content-Transfer-Encoding: 8bit', LINEND, LINEND, auth, LINEND, PREFIX, BOUNDARY, LINEND,
			'Content-Disposition: form-data; name="img"; filename="%s"' % filename, LINEND,
			'Content-Type: image/jpg; charset=' + CHARSET, LINEND, LINEND, inputParams, LINEND, PREFIX,
			BOUNDARY, PREFIX, LINEND]
	http_body = ''.join(data)
	return BOUNDARY, http_body
	
# 初始化非上传广告内容
def initData():
    return {
        "name" : "" ,
        "devid" : "" ,
        "time" : "" ,
        "devinfo" : "",
        "runstatus" : "",
        "efficiency" : 0,
        "status" : [],
		"abnormal":[],
		"principle":[]
    }	
			
class report():
	def __init__(self):
		return
		
	def GET(self):
		return render('check.html')
		
	def POST(self):
		upload = dict()
		images = dict()
		try:
			inputParams = web.input(weatherimg={},run={},normal_detail1={},abnormal_detail1={},abnormal_detail2={})
		except ValueError, e:
			return render("check.html",error="文件过大",title="提交资源" )
		
		devid = inputParams.get('devid','')
		name = inputParams.get('name','')
		time = inputParams.get('time','').replace('-','').replace(' ','').replace(':','').replace('/','')
		devinfo = inputParams.get('devinfo','')
		runstatus = inputParams.get('runstatus','')
		efficiency = inputParams.get('efficiency',0)
		status = inputParams.get('status','')
		abnormal_reason = inputParams.get('abnormal_reason','')
		principle = inputParams.get('principle','')
		if devid == '' or name == '' or time == '' or devinfo == '' or runstatus == '' or efficiency == 0 or status == '' or abnormal_reason == '' or principle == '':
			return render("check.html",error="必要信息不足",title="提交资源" )
		statuslist = status.split('&')
		abnormallist = abnormal_reason.split('&')
		principlelist = principle.split('&')
		
		upload['devid'] = devid
		upload['name'] = name
		upload['time'] = time
		upload['devinfo'] = devinfo
		upload['runstatus'] = runstatus
		upload['efficiency'] = efficiency
		upload['status'] = statuslist
		upload['abnormal_reason'] = abnormallist
		upload['principle'] = principlelist
		upload['flag'] = 'false'#1表示无异常细节图2,2表示有

		if 'weatherimg' in inputParams: # to check if the file-object is created
			# check size
			try:
				filepath=inputParams.weatherimg.filename.replace('\\','/') # replaces the windows-style slashes with linux ones.
				filename=filepath.split('/')[-1] # splits the and chooses the last part (the filename with extension)
				auth = buildFileAuth()
				BOUNDARY, http_body = buildHttpData(auth, filename, inputParams.weatherimg.file.read())
				req = urllib2.Request(url = img_upload,data = http_body)
				req.add_header('Content-Type','multipart/form-data; boundary=%s' % BOUNDARY)
				req.add_header('User-Agent','Mozilla/5.0')
				res_data = urllib2.urlopen(req)
				response = json.loads(res_data.read())
				if response['errCode'] == 1:
					images['weatherimg'] = ''
				else:
					images['weatherimg'] = response['resultData']
			except:
				images['weatherimg'] = ''
				
		if 'run' in inputParams: # to check if the file-object is created
			try:
				filepath=inputParams.run.filename.replace('\\','/') # replaces the windows-style slashes with linux ones.
				filename=filepath.split('/')[-1] # splits the and chooses the last part (the filename with extension)
				auth = buildFileAuth()
				BOUNDARY, http_body = buildHttpData(auth, filename, inputParams.run.file.read())
				req = urllib2.Request(url = img_upload,data = http_body)
				req.add_header('Content-Type','multipart/form-data; boundary=%s' % BOUNDARY)
				req.add_header('User-Agent','Mozilla/5.0')
				res_data = urllib2.urlopen(req)
				response = json.loads(res_data.read())
				if response['errCode'] == 1:
					images['run'] = ''
				else:
					images['run'] = response['resultData']
			except:
				images['run'] = ''
				
		if 'abnormal_detail1' in inputParams: # to check if the file-object is created
			try:
				filepath=inputParams.abnormal_detail1.filename.replace('\\','/') # replaces the windows-style slashes with linux ones.
				if filepath == '':
					images['abnormal_detail1'] = ''
				else:
					filename=filepath.split('/')[-1] # splits the and chooses the last part (the filename with extension)
					auth = buildFileAuth()
					BOUNDARY, http_body = buildHttpData(auth, filename, inputParams.abnormal_detail1.file.read())
					req = urllib2.Request(url = img_upload,data = http_body)
					req.add_header('Content-Type','multipart/form-data; boundary=%s' % BOUNDARY)
					req.add_header('User-Agent','Mozilla/5.0')
					res_data = urllib2.urlopen(req)
					response = json.loads(res_data.read())
					if response['errCode'] == 1:
						images['abnormal_detail1'] = ''
					else:
						images['abnormal_detail1'] = response['resultData']
			except:
				images['abnormal_detail1'] = ''
				
		if 'abnormal_detail2' in inputParams: # to check if the file-object is created
			try:
				filepath=inputParams.abnormal_detail2.filename.replace('\\','/') # replaces the windows-style slashes with linux ones.
				if filepath == '':
					images['abnormal_detail2'] = ''
				else:
					filename=filepath.split('/')[-1] # splits the and chooses the last part (the filename with extension)
					auth = buildFileAuth()
					BOUNDARY, http_body = buildHttpData(auth, filename, inputParams.abnormal_detail2.file.read())
					req = urllib2.Request(url = img_upload,data = http_body)
					req.add_header('Content-Type','multipart/form-data; boundary=%s' % BOUNDARY)
					req.add_header('User-Agent','Mozilla/5.0')
					res_data = urllib2.urlopen(req)
					response = json.loads(res_data.read())
					if response['errCode'] == 1:
						images['abnormal_detail2'] = ''
					else:
						images['abnormal_detail2'] = response['resultData']
						upload['flag'] = 'true'
			except:
				images['abnormal_detail2'] = ''
				
				
		if 'normal_detail1' in inputParams: # to check if the file-object is created
			try:
				filepath=inputParams.normal_detail1.filename.replace('\\','/') # replaces the windows-style slashes with linux ones.
				filename=filepath.split('/')[-1] # splits the and chooses the last part (the filename with extension)
				auth = buildFileAuth()
				BOUNDARY, http_body = buildHttpData(auth, filename, inputParams.normal_detail1.file.read())
				req = urllib2.Request(url = img_upload,data = http_body)
				req.add_header('Content-Type','multipart/form-data; boundary=%s' % BOUNDARY)
				req.add_header('User-Agent','Mozilla/5.0')
				res_data = urllib2.urlopen(req)
				response = json.loads(res_data.read())
				if response['errCode'] == 1:
					images['normal_detail1'] = ''
				else:
					images['normal_detail1'] = response['resultData']
			except:
				images['normal_detail1'] = ''
				
					
		upload['images'] = images
		
		finditem = data_model('check').find_one(conditions={'devid':devid,'time':time})
		if finditem is None:
			pass
		else:
			data_model('check').remove(condition={'devid':devid,'time':time})
		data_model('check').insert(upload)
		finditem = data_model('user_dev').find_one(conditions={'_id':devid})
		if finditem is None:
			pass
		else:
			findsys = data_model('devID').find_one(conditions={'_id':devid})
			system = findsys.get('system','')
			if system == '':
				findloger = data_model('loger').find_one(conditions={'content.devID':devid})
				system = findloger.get('system','')	
			sender = finditem['sender']
			username = finditem['username']
			url = 'http://%s/report/check?time=%s&devid=%s'%(server,time,devid)
			content = '体检报告'
			finditem = data_model('check_info').find_one(conditions={'devid':devid,'time':time})
			if finditem is None:
				pass
			else:
				data_model('check_info').remove(condition={'devid':devid,'time':time})
			data_model('check_info').insert({'devid':devid,'time':time,'sender':sender,'url':url,'username':username,'content':content,'system':system})
		return render('check.html')
		
		
class getInfo():
	def GET(self):
		return render('checkinfo_change.html')
	def POST(self):
		data = web.input()
		devid = data['devid']
		time = data['time']
		item = data_model('check').find_one(conditions={'devid':devid,'time':time})
		if item is None:
			return {}
		else:
			del item['_id']
			item = json.dumps(item)
			return item
			
			
class edit():
	def __init__(self):
		return
		
	def POST(self):
		upload = dict()
		images = dict()
		try:
			inputParams = web.input(weatherimg={},run={},normal_detail1={},abnormal_detail1={},abnormal_detail2={})
		except ValueError, e:
			return render("checkinfo_change.html",error="文件过大",title="提交资源" )

		devid = inputParams.get('devid','')
		name = inputParams.get('name','')
		time = inputParams.get('time','').replace('-','').replace(' ','').replace(':','').replace('/','')
		devinfo = inputParams.get('devinfo','')
		runstatus = inputParams.get('runstatus','')
		efficiency = inputParams.get('efficiency',0)
		status = inputParams.get('status','')
		abnormal_reason = inputParams.get('abnormal_reason','')
		principle = inputParams.get('principle','')

		if devid == '' or name == '' or time == '' or devinfo == '' or runstatus == '' or efficiency == 0 or status == '' or abnormal_reason == '' or principle == '':
			return render("checkinfo_change.html",error="必要信息不足",title="提交资源" )
		statuslist = status.split('&')
		abnormallist = abnormal_reason.split('&')
		principlelist = principle.split('&')
		
		upload['devid'] = devid
		upload['name'] = name
		upload['time'] = time
		upload['devinfo'] = devinfo
		upload['runstatus'] = runstatus
		upload['efficiency'] = efficiency
		upload['status'] = statuslist
		upload['abnormal_reason'] = abnormallist
		upload['principle'] = principlelist
		upload['flag'] = 'false'#1表示无异常细节图2,2表示有
		
		finditem = data_model('check').find_one(conditions={'devid':devid,'time':time})
		data_model('check').remove(condition={'devid':devid,'time':time})

		if 'weatherimg' in inputParams: # to check if the file-object is created
			# check size
			try:
				filepath=inputParams.weatherimg.filename.replace('\\','/') # replaces the windows-style slashes with linux ones.
				if filepath == '':
					images['weatherimg'] = finditem['images']['weatherimg']
				else:
					filename=filepath.split('/')[-1] # splits the and chooses the last part (the filename with extension)
					auth = buildFileAuth()
					BOUNDARY, http_body = buildHttpData(auth, filename, inputParams.weatherimg.file.read())
					req = urllib2.Request(url = img_upload,data = http_body)
					req.add_header('Content-Type','multipart/form-data; boundary=%s' % BOUNDARY)
					req.add_header('User-Agent','Mozilla/5.0')
					res_data = urllib2.urlopen(req)
					response = json.loads(res_data.read())
					if response['errCode'] == 1:
						images['weatherimg'] = ''
					else:
						images['weatherimg'] = response['resultData']
			except:
				images['weatherimg'] = ''
				
		if 'run' in inputParams: # to check if the file-object is created
			try:
				filepath=inputParams.run.filename.replace('\\','/') # replaces the windows-style slashes with linux ones.
				if filepath == '':
					images['run'] = finditem['images']['run']
				else:
					filename=filepath.split('/')[-1] # splits the and chooses the last part (the filename with extension)
					auth = buildFileAuth()
					BOUNDARY, http_body = buildHttpData(auth, filename, inputParams.run.file.read())
					req = urllib2.Request(url = img_upload,data = http_body)
					req.add_header('Content-Type','multipart/form-data; boundary=%s' % BOUNDARY)
					req.add_header('User-Agent','Mozilla/5.0')
					res_data = urllib2.urlopen(req)
					response = json.loads(res_data.read())
					if response['errCode'] == 1:
						images['run'] = ''
					else:
						images['run'] = response['resultData']
			except:
				images['run'] = ''
				
		if 'abnormal_detail1' in inputParams: # to check if the file-object is created
			try:
				filepath=inputParams.abnormal_detail1.filename.replace('\\','/') # replaces the windows-style slashes with linux ones.
				if filepath == '':
					if runstatus == 'normal':
						images['abnormal_detail1'] = ''
					else:
						images['abnormal_detail1'] = finditem['images']['abnormal_detail1']
				else:
					filename=filepath.split('/')[-1] # splits the and chooses the last part (the filename with extension)
					auth = buildFileAuth()
					BOUNDARY, http_body = buildHttpData(auth, filename, inputParams.abnormal_detail1.file.read())
					req = urllib2.Request(url = img_upload,data = http_body)
					req.add_header('Content-Type','multipart/form-data; boundary=%s' % BOUNDARY)
					req.add_header('User-Agent','Mozilla/5.0')
					res_data = urllib2.urlopen(req)
					response = json.loads(res_data.read())
					if response['errCode'] == 1:
						images['abnormal_detail1'] = ''
					else:
						images['abnormal_detail1'] = response['resultData']
			except:
				images['abnormal_detail1'] = ''
				
		if 'abnormal_detail2' in inputParams: # to check if the file-object is created
			try:
				filepath=inputParams.abnormal_detail2.filename.replace('\\','/') # replaces the windows-style slashes with linux ones.
				if filepath == '':
					if runstatus == 'normal':
						images['abnormal_detail2'] = ''
					else:
						images['abnormal_detail2'] = finditem['images']['abnormal_detail2']
				else:
					filename=filepath.split('/')[-1] # splits the and chooses the last part (the filename with extension)
					auth = buildFileAuth()
					BOUNDARY, http_body = buildHttpData(auth, filename, inputParams.abnormal_detail2.file.read())
					req = urllib2.Request(url = img_upload,data = http_body)
					req.add_header('Content-Type','multipart/form-data; boundary=%s' % BOUNDARY)
					req.add_header('User-Agent','Mozilla/5.0')
					res_data = urllib2.urlopen(req)
					response = json.loads(res_data.read())
					if response['errCode'] == 1:
						images['abnormal_detail2'] = ''
					else:
						images['abnormal_detail2'] = response['resultData']
						upload['flag'] = 'true'
			except:
				images['abnormal_detail2'] = ''
				
				
		if 'normal_detail1' in inputParams: # to check if the file-object is created
			try:
				filepath=inputParams.normal_detail1.filename.replace('\\','/') # replaces the windows-style slashes with linux ones.
				if filepath == '':
					images['normal_detail1'] = finditem['images']['normal_detail1']
				else:
					filename=filepath.split('/')[-1] # splits the and chooses the last part (the filename with extension)
					auth = buildFileAuth()
					BOUNDARY, http_body = buildHttpData(auth, filename, inputParams.normal_detail1.file.read())
					req = urllib2.Request(url = img_upload,data = http_body)
					req.add_header('Content-Type','multipart/form-data; boundary=%s' % BOUNDARY)
					req.add_header('User-Agent','Mozilla/5.0')
					res_data = urllib2.urlopen(req)
					response = json.loads(res_data.read())
					if response['errCode'] == 1:
						images['normal_detail1'] = ''
					else:
						images['normal_detail1'] = response['resultData']
			except:
				images['normal_detail1'] = ''	
		upload['images'] = images
		
		data_model('check').insert(upload)
		
		return render('checkinfo_change.html')