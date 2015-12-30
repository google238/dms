__author__ = 'michael'
__metaclass__ = type
import web
from model import *
from config.config_default import *
import base64
session = web.config._session
j = web.storage()


class user_model(model):
    def __init__(self):
        super(user_model, self).__init__('admin_resource')
		
    @staticmethod
    def update_session(user):
        session.user_id = user['_id']
        session.name = user['username']
        session.user_type = user['user_type']

    def auth_cookie(self, handler):
        try:
            if session.user_id is None:
                auth = web.cookies().get('auth')
                auth_list = base64.decodestring(auth).split('|')
                user = self.find_one({'_id':auth_list[1], 'password':auth_list[0]})
                if user is None:
                    web.setcookie('auth', auth, -1)
                else:
                    self.update_session(user['id'])
        except:
            pass
        return handler()

    @staticmethod
    def set_cookie(user):
        auth = base64.encodestring(user["password"]+'|'+str(user["_id"]))
        web.setcookie('auth', auth, cookie_expires)
