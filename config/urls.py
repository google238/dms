# -- coding: utf8 --
pre_fix = 'controller.'
urls = (
	"/dms/admin/submit", pre_fix + "maintain.submit",
	#登陆
	"/dms/admin/login", pre_fix + "maintain.login",
	#注销
	"/dms/admin/logout", pre_fix + "maintain.logout",
	#子系统注册页
	"/dms/admin/add", pre_fix + "operate.add",
	#首页
	"/dms/admin/index", pre_fix + "operate.index",
	#查询子系统
	"/dms/admin/show/(|\d+)", pre_fix + "operate.show",
	#删除
	"/dms/admin/del/(\w+)", pre_fix + "operate.delete",
	#用户提交数据
	"/dms/user", pre_fix + "user.user",
	#数据展示页面
	"/dms/admin/data", pre_fix + "data.data",
	"/dms/admin/userfrom", pre_fix + "operate.userfrom",
	"/dms/admin/tablename", pre_fix + "operate.tablename",
	"/dms/admin/key", pre_fix + "operate.key",
	"/dms/admin/addchild", pre_fix + "operate.addchild",
	"/dms/admin/addchildtable", pre_fix + "maintain.addchildtable",
	
	"/dms/admin/griddata", pre_fix + "griddata.griddata",
	"/dms/admin/griddata/show", pre_fix + "griddata.show",
	#设备用电排行接口
	"/dms/rank", pre_fix + "data.rank",
	#设备用电量接口
	"/dms/devpower", pre_fix + "data.power",
	#推送设备一次运行使用电量
	"/dms/useractive", pre_fix + "data.useractive",
	#计算设备在某个时间段的耗电情况
	"/dms/data/power", pre_fix + 'tool.power',
	#展示设备在某个时间段的开关动作以及模式变化情况
	"/dms/data/actioninfo", pre_fix + 'tool.actioninfo',
	#设备动作信息汇总
	"/dms/data/actioninfo/summary", pre_fix + 'tool.suminfo',
	#设置空调清洗指数
	"/dms/maintain/city", pre_fix + 'aircondition.city',
	"/dms/maintain/temp", pre_fix + 'aircondition.temp',
	"/dms/maintain/city_editor", pre_fix + 'aircondition.editor_city',
	"/dms/maintain/temp_editor", pre_fix + 'aircondition.editor_temp',
	
	#空调健康参数
	"/dms/aircondition/info", pre_fix + 'aircondition.info',
	
	#空调检测信息生成
	"/dms/check/post", pre_fix + 'check.report',
	#获取空调检测信息
	"/dms/check/change", pre_fix + 'check.getInfo',
	#编辑空调检测信息
	"/dms/check/edit", pre_fix + 'check.edit',
    
    "/dms/statistic/list", pre_fix + 'statistic.list',
    "/dms/statistic/trend", pre_fix + 'statistic.trend'
	 
)