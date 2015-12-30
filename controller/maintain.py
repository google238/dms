# coding: utf-8
import types
import random
import hashlib
import web
import uuid
import datetime
import time
import pymongo
import string
import common.common as common 
from config.config_default import *
from model.dms_model import *
from model.user_model import *
from model.data_model import *
from libraries.utils import render, now4yMdHms , http_post
session = web.config._session
j = web.storage()


class addchildtable:
	def POST(self):
		form = web.input()
		print form
		if form["tablename"] == '' or form["tablename"] is None:
			return render("addchildtable.html",msg="表名不能为空！")
		data_model("childtable").insert(form)
		return render("addchildtable.html", msg="添加成功")
		

class submit:
	def __init__(self):
		if session.get('user_id'):
		#	raise web.SeeOther("")
			pass
				
	def GET(self):
		return "this is a test"
		
	def POST(self):
		form = web.input()
		if form['userFrom'] is None or form['userFrom'] == '':
			return render("apply.html", msg="业务名不能为空")
			
		if form['level'] is None or form['level'] == '':
			return render("apply.html", msg="保存等级不能为空")
			
		if form['tagID'] is None or form['tagID'] == '':
			return render("apply.html", msg="业务ID不能为空")
			
		userFrom = form['userFrom'].lower()
		level = form['level']	
		tagID = form['tagID']
		remark = ''
		if form['remark']:
			remark = form['remark']
		
		condition_user = {'userFrom':userFrom}		
		item_user = dms_model().find_one(condition_user)
		
		condition_id = {'tagID':tagID}		
		item_id = dms_model().find_one(condition_id)
		if item_user:
			return render("apply.html", msg="此系统用户已注册")
		if item_id:
			return render("apply.html", msg="ID号已注册")
		else:		
			item = {"userFrom":userFrom,"tagID":tagID,"level":level, "remark":remark}
			dms_model().insert(item)
			return render("apply.html", msg="注册成功")

			
class login:
	def __init__(self):
#		if session.get('user_id'):
#			raise web.SeeOther("")
#		print web.cookies().get('dms_sessid')
		pass
			
	def GET(self):
		return render("login.html")
#		user = web.cookies().get('dms_sessid')
#		print user
#		if user:
#			session.user_id = '0000000000'
#			session.name = user
#			session.user_type = 'admin'
#			raise web.SeeOther("/dms/admin/index")
#		else:
#			raise web.SeeOther("http://op.chakonger.net/web/admin/gotoSysList.do?sysname=%s&adminname=%s" % ('DMS',''))
		
	def POST(self):
		form = web.input()
		condition = {'username': form['username']}
		if form is None or form['username'] is None or form['username'] == '' :
			return render("login.html", msg='用户名不能为空')

		user = user_model().find_one(condition)
	
		if user is None:
			return render("login.html", msg='用户名不存在')
		
		auth_from_form = hashlib.md5(hashlib.md5(form['password']).hexdigest() + user['auth']).hexdigest()
			
		if auth_from_form != user['password']:
			return render("login.html", msg='密码错误')
			
		user_model().update_session(user)
		user_model().set_cookie(user)
		return render("index.html")


class logout:
	def GET(self):
		session.kill()
		web.setcookie('auth','',-1)
		return web.SeeOther('/dms/admin/login')
#		if hasattr(session,'user_type') and session.user_type != 'admin':
#			redict = '/dms/admin/login'
#		else:
#			redict = "http://op.chakonger.net/web/admin/gotoSysList.do?sysname=%s&adminname=%s" % ('dms',session.name)
#		session.kill()
#		web.setcookie('auth', '', -1)
#		return web.SeeOther(redict)
		

	
		

