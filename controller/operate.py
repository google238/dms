# coding: utf-8
import web
from bson.objectid import ObjectId
import common.common as common 
from config.config_default import *
from model.dms_model import *
from model.userfrom_model import *
from model.data_model import *
from libraries.utils import render, now4yMdHms , http_post
from libraries.decorator import admin_login
session = web.config._session
import json

j = web.storage()

class addchild:
	@admin_login
	def GET(self):
		return render("addchildtable.html",title="添加子表")

class index:
	@admin_login
	def GET(self):
		return render("index.html")

class add:
	@admin_login
	def GET(self):
		return render("apply.html",title="注册子系统")

class show:
	@admin_login
	def GET(self, p):
		if p is None or p == '':
			p = '1'
		p = int(p)
		
		j.bss = dms_model().find_page(pagenum=p)
		j.page = dms_model().get_page(p)
		return render('systemlist.html',**j)
		
	def POST(self,*args):
		return self.GET('1')
		
class delete:
#	@admin_login
	def GET(self,dms_id):
		if dms_id is None:
			raise web.seeother('/dms/admin/show/1')
		
		condition = {'_id': ObjectId(dms_id)}
		dms_model().remove(condition)
		raise web.seeother("/dms/admin/show/1")
		
class userfrom:
	def GET(self):
		dbs = dms_model().find()
		result = []
		for db in dbs:
			result.append(db['remark'])
		
		data = {"userfrom":result}
		data = json.dumps(data)
		return data
		
class tablename:
	def GET(self):
		data = web.input()
		userfrom = ''
		remark = ''
		if data and data['userFrom']:
			remark = data['userFrom']
		conditions = {}
		conditions['remark'] = remark
		user = dms_model().find_one(conditions=conditions)
		if user:
			userfrom = user['userFrom'].lower()
		tns = data_model(userfrom).find()
		result = []
		for tn in tns:
			result.append(tn["tablename"])
		data = {"tablename":result}
		data = json.dumps(data)
		return data

class key:
	def GET(self):
		data = web.input()
		tablename = ''
		if data and data['tablename']:
			tablename = data['tablename']
		set = data_model(tablename).find_one()
		if set is None:
			return
		result = []
		for item in set.keys():
			result.append(item)
		data = {"keys":result}
		data = json.dumps(data)
		return data