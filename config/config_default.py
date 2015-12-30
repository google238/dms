# coding: utf-8
#数据库服务地址+端口号
import web
import cgi

web.config.debug = True

#port = 27017
#serv_name = "localhost"

#log文件路径
logpath_win = "c:\\test\\"
logpath_linux = "/data/CKR/log/dms/"

#base_path = "http://localhost:8080/static"
cgi.maxlen = 0# 1MB
# cookie失效时长
cookie_expires = 60*15

#服务器地址
server = "118.192.76.159"
#server = "192.168.5.188"

#running_env = 'local'
running_env = 'production'

import os
home = ''
os.environ["SCRIPT_NAME"] = home
os.environ["REAL_SCRIPT_NAME"] = home

# 文件服务器地址配置
auth_name = "18610935308"
img_upload = "http://120.132.51.222:8090/FileSystem/mobile/imgUpload.do"

#静态文件路径
if running_env == 'local':
	base_path = "http://118.192.76.159:8080/static"
	serv_name = "localhost"
	mongo_port = 27017
else:
	base_path = "http://"+ server +"/static/dms/static"
	serv_name = "10.10.160.75"
	mongo_port = 28088
