#-*-coding:utf-8-*-
import sys
sys.path.insert(0,'..')
import datetime
from model.data_model import *
from model.statistic_model import *
from bson.code import Code
#import sys
reload(sys)
sys.setdefaultencoding('utf-8')
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

def dealstatistic(d3):
    statisInfo = 'statistic_info_' + d3
    statisUser = 'statistic_user_' + d3
    statisArea = 'statistic_area_' + d3
    statisPro = 'statistic_area_province_' + d3
    
    tablename = 'devpower_detail_' + d3
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
        statistic_model(statisInfo).insert(temp)
    print 'Info ok!'
    key = 'this.username' 
    map = Code("function(){emit(this.username,this._id);}") 
    reduce = Code("function(key,values){return {ids:values};}") 
    statistic_model(statisInfo).map_reduce(map, reduce, statisUser)
    print 'User ok!'
    key = 'this.city' 
    map = Code("function(){emit("+key+", {count:1});}") 
    reduce = Code("function(key,values){var total = 0;for (var i = 0; i < values.length; i++){total += values[i].count;}return {count:total};}") 
    statistic_model(statisInfo).map_reduce(map, reduce, statisArea)
    print 'Area ok!'
    finddata = statistic_model(statisArea).find()
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
            statistic_model(statisPro).update_inc(condition={'_id':p}, values={'count':count}, upsert=True, multi=True)
    print 'Province ok!'
    

if __name__ == "__main__":
    d1 = datetime.datetime.now()
    d3 = d1 - datetime.timedelta(days=1)
    d3 = d3.strftime('%Y%m%d')
    dealstatistic(d3)

