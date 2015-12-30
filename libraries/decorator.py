# -- coding: utf8 --
import web
session = web.config._session
from config.config_default import *

def admin_login(f, *args):
    def new_f(*args):
        if session.get('user_id') is None:
            return web.seeother("/dms/admin/login")
        else:
            return f(*args)
    return new_f