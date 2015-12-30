# coding: utf-8
import json
import web
import sys
import datetime
import operator
from model.data_model import *
from model.statistic_model import *
from libraries.utils import render, now4yMdHms , http_post
import common.common as common 
from bson.code import Code
import re


def unicode_convert(t):
    if t:
        t, number = re.subn(': u',': ', t)
        pattern = re.compile('\\\\u[0-9a-f]{4}')
        t_all = pattern.findall(t)

        if t_all:
            for o in t_all:
                n = unichr(eval('0x'+o.replace('\\u', '')))
                t = t.replace(o, n)
        # json转dict，必须是双引号
        addedSingleQuoteJsonStr = re.sub(r"(,?)(\w+?)\s*?:", r"\1'\2':", t);
        doubleQuotedJsonStr = addedSingleQuoteJsonStr.replace("'", "\"");
    return doubleQuotedJsonStr


class list():
    def __init__(self):
        return 
        
    def GET(self):
        return render('statistic_list.html')

    def POST(self):
        data = web.input()
        time = data['time']
        type = data['type']
        #draw = int(data['draw'])
        now = datetime.datetime.now().strftime('%Y%m%d')
        if now == time:
            statistic_model('statistic_info_'+time).drop() 
            statistic_model('statistic_area_'+time).drop()       
            statistic_model('statistic_user_'+time).drop()
            statistic_model('statistic_area_province_'+time).drop()        
        statistictable = 'statistic_info_' + time
        
        find = []
        find = statistic_model(statistictable).find()
        count = 0
        if len(find) == 0:#从未处理过
            tablename = 'devpower_detail_' + time
            key = 'this.devid' 
            map = Code("function(){if(this.W>0){emit("+key+", {count:1});}}") 
            reduce = Code("function(key,values){var total = 0;for (var i = 0; i < values.length; i++){total += values[i].count;}return {count:total};}") 
            data_model(tablename).map_reduce(map, reduce, "statistic_out")
            finddata = data_model('statistic_out').find();
            for item in finddata:
                id = item['_id']
                devtype = ''
                regtime = ''
                city = ''
                area = ''
                username = ''
                findone = data_model('devCurrInfo').find_one(conditions={'deviceId':id})
                if findone is None:
                    devtype = ''
                    findreg = data_model('dev_position').find_one(conditions={'_id':id})
                    if findreg is None:
                        pass
                    else:
                        username = findreg.get('userName','')
                        regtime = findreg.get('time','')
                        city = findreg.get('city','')
                        area = findreg.get('area','')
                else:
                    username = findone.get('userName','')
                    regtime = findone.get('regTime','')
                    devtype = findone.get('devType','')
                    if 'position' not in findone.keys():
                        pass
                    else:
                        position = eval(findone['position'])
                        city = position.get('city','')
                        area = position.get('area','')
                        if city != '':
                            city = unicode_convert(city)
                        if area != '':
                            area = unicode_convert(area)
                temp = {'_id':id,'username':username,'devtype':devtype,'regtime':regtime,'city':city,'area':area}
                statistic_model(statistictable).insert(temp)
                find.append(temp)
        result = []
        if type == '1':
            count = len(find)              
            for item in find:
                temp = []
                temp.append(item['_id'])
            #    temp.append(item['username'])
                temp.append(item['devtype'])
                temp.append(item['regtime'])
                temp.append(item['city'])
                temp.append(item['area'])
                result.append(temp)
        elif type == '2':
            user_tablename ='statistic_user_' + time
            finddata = statistic_model(user_tablename).find()
            if len(finddata) == 0:
                key = 'this.username' 
                map = Code("function(){emit(this.username,this._id);}") 
                reduce = Code("function(key,values){return {ids:values};}") 
                statistic_model(statistictable).map_reduce(map, reduce, user_tablename)
                finddata = statistic_model(user_tablename).find();
            count = len(finddata)
            for item in finddata:
                temp = []
                temp.append(item['_id'])
                if isinstance(item['value'],dict):
                    temp.append(item['value']['ids'])
                else:
                    temp.append(item['value'])
                result.append(temp)

        elif type == '3':
            area_tablename = 'statistic_area_' + time
            finddata = statistic_model(area_tablename).find()
            if len(finddata) == 0:
                key = 'this.city' 
                map = Code("function(){emit("+key+", {count:1});}") 
                reduce = Code("function(key,values){var total = 0;for (var i = 0; i < values.length; i++){total += values[i].count;}return {count:total};}") 
                statistic_model(statistictable).map_reduce(map, reduce, area_tablename)
                finddata = statistic_model(area_tablename).find()
            count = len(finddata)
            for item in finddata:
                temp = []
                temp.append(item['_id'])
                temp.append(item.get('value').get('count'))
                result.append(temp)
        elif type == '4':
            area_pro_tablename = 'statistic_area_province_' + time
            find = statistic_model(area_pro_tablename).find()
            if len(find) == 0:
                area_tablename = 'statistic_area_' + time
                finddata = statistic_model(area_tablename).find()
                if len(finddata) == 0:
                    key = 'this.city' 
                    map = Code("function(){emit("+key+", {count:1});}") 
                    reduce = Code("function(key,values){var total = 0;for (var i = 0; i < values.length; i++){total += values[i].count;}return {count:total};}") 
                    statistic_model(statistictable).map_reduce(map, reduce, area_tablename)
                    finddata = statistic_model(area_tablename).find()
                for item in finddata:
                    if item['_id'] == '':
                        continue
                    else:
                        city = item['_id']
                        k = city
                        city = city[:-1]
                        count = item.get('value').get('count')
                        s = data_model('city_area').find_one(conditions={'city':city})
                        if s is None:
                            continue
                        p = s.get('province','')
                        statistic_model(area_pro_tablename).update_inc(condition={'_id':p}, values={'count':count}, upsert=True, multi=True)
                find = statistic_model(area_pro_tablename).find()
            series0 = {'data':[]}
            series1 = {'data':[]}
            series2 = {'data':[]}
            for item in find:
                temp = {'name':'','value':''}
                temp['name'] = item['_id']
                temp['value'] = int(item['count'])
                if item['count']<=20:
                    series2['data'].append(temp)
                elif item['count']<=100:
                    series1['data'].append(temp)
                else:
                    series0['data'].append(temp)
            temp = []
            temp.append(series0)
            temp.append(series1)
            temp.append(series2)
            data = {'option':{'series':temp}}
            data = json.dumps(data)
            return data
        data = {"draw":0,"recordsTotal":count,"recordsFiltered":count,"aaData":result}
        data = json.dumps(data)
        return data
 

class trend():
    def __init__(self):
        return 
        
    def GET(self):
        return render('statistic_trend.html')

    def POST(self):
        data = web.input()
        starttime = data['starttime']
        endtime = data['endtime']
        type = data['type']
        daylist = common.getdaylist(starttime,endtime)
        if type == 'device':
            flag = 'info'
        elif type == 'user':
            flag = 'user'
        result = []
        for day in daylist:
            tablename = 'statistic_' + flag + '_' + day
            count = statistic_model(tablename).count()
            temp = {'key':'','value':0}
            temp['key'] = common.strTimeToFormat(day)
            temp['value'] = count
            result.append(temp)
        data = {'result':result}      
        data = json.dumps(data)
        return data
        