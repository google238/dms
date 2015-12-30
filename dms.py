#!/usr/bin/python
# coding: utf-8
import sys
if sys.getdefaultencoding() != 'utf-8':
    reload(sys)
    sys.setdefaultencoding('utf-8')
from config.urls import urls
from config.config_default import *
import web
from libraries.dmssession import DMSSession
from common.mongostore import MongoStore 
import pymongo
web.config.debug = False
app = web.application(urls, globals())

connection = pymongo.MongoClient(serv_name, mongo_port)
db = connection.test1

if web.config.get('_session') is None:
    web.config.session_parameters['cookie_name'] = 'dms_sessid'
    web.config.session_parameters['cookie_path'] = '/'
    web.config.session_parameters['timeout'] = 60 * 3 
    web.config.session_parameters['ignore_expiry'] = False
    web.config.session_parameters['ignore_change_ip'] = True
    web.config.session_parameters['secret_key'] = 'Jp3kLsy5Fre2m6sNxz9RwAq'
    web.config.session_parameters['expired_message'] = 'Session expired, will redirect...'
    #session = DMSSession(app, web.session.DiskStore('sessions'), {})
    session = DMSSession(app,  MongoStore(db, 'sessions'), initializer={'user_id': None})
    # session = web.session.Session(app, web.session.DiskStore('sessions'), initializer={'user_id': None})
    web.config._session = session
else:
    session = web.config._session

def session_hook():
    web.ctx.session = session
app.add_processor(web.loadhook(session_hook))	

if __name__ == "__main__":
	if running_env == 'production':
		web.wsgi.runwsgi = lambda func,addr=None:web.wsgi.runfcgi(func,addr)
	app.run()
