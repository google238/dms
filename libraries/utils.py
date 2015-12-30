# -- coding: utf8 --
__author__ = 'michael'
import os
from jinja2 import Environment,FileSystemLoader
import web
import json
import urllib2
import traceback
import time
from bson.objectid import ObjectId
from config.config_default import *

session = web.config._session

def render(template_name, **context):
    extensions = context.pop('extensions', [])
    globals = context.pop('globals', {'session':session,'base':base_path})

    jinja_env = Environment(
            loader=FileSystemLoader(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates')),
            extensions=extensions
            )
    jinja_env.globals.update(globals)

    #jinja_env.update_template_context(context)
    return jinja_env.get_template(template_name).render(context)

# 当前时间
def now4yMdHms():
    return time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))

def now4timestamp():
    return time.localtime(time.time())

def ymdhms2mill(a):
    return time.mktime(time.strptime(a,'%Y-%m-%d %H:%M:%S'))

def mill2ymdhms(a):
    timeTuple = time.localtime(float(a))
    return time.strftime('%Y-%m-%d %H:%M:%S',timeTuple)

class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return json.JSONEncoder.default(self, o)


def http_post(url,postData):
    """
    发送post请求
    :param url:
    :param postData:
    :return:
    """
    jdata = json.dumps(postData)              # 对数据进行JSON格式化编码
    req = urllib2.Request(url, jdata)         # 生成页面请求的完整数据
    response = urllib2.urlopen(req)           # 发送页面请求
    returnJson = json.loads(response.read())
    return returnJson                         # 获取服务器返回的页面信息

'''
def doHTTPRequest(serviceURL, data=""):
    returnData = ''
    try:
        if data:
            #post
			data = json.dumps(data)
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
'''