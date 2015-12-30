#! /usr/bin/env python
#encoding: utf-8

#Filename: machLearning.py  
#Author: fk zhang
#E-mail:  
#Date: 2015-11-25
#Description:  
import sys
sys.path.insert(0,'..') 
import datetime
import machlearning.miscCommon as miscCommon
import machlearning.bigData as bigData
import machlearning.bigDataCommon as bigDataCommon
import common.common as common
from model.data_model import *
import os
from math import *
import operator
import re

outputFileDir = '/data/CKR/src/dms/machlearning/'
def main():
    testFlag="ALL"
    print "Begin"
    print miscCommon.getTime()
    finddata = data_model('machinelearning_d_YSJ').find()
    if len(finddata) == 0:
        return
    else:
        devids = []
        for item in finddata:
            devids.append(item['devid'])
    #devids = ['31150409501938158542']
    for devID in devids:
        beginTime = miscCommon.getNow()
        dataSet=getSourcedata(devID)
        if len(dataSet) < 100:
		continue
        devType=bigDataCommon.CONST_BGANA_BGYSJ
        bigType="KG"
        if testFlag=="ALL":
            #训练样本，返回的是模型
            result=bigData.train(devID,bigType,devType, dataSet,  calSaving=True)
        strT=devID+"model.json"
        outfilename=os.path.join(outputFileDir, strT)
        if testFlag=="ALL":
            #保存样本结果
            miscCommon.saveJsonData(outfilename, result)
        model=miscCommon.loadJsonData(outfilename)
        #print model
        infraTypeID=""
        YMDHMS=miscCommon.getNow().YMDHMS
        #YMDHMS = '20151206030000'
        nextweek_YMD = (miscCommon.getNow().now + datetime.timedelta(days=7)).strftime('%Y%m%d')
        requestMode=bigDataCommon.CONST_BGANA_MODE_WEEK
        print
        result = []
        actionList=bigData.getCommand(devID,bigType, devType,infraTypeID,YMDHMS,model, requestMode)
        for i in [0,1]:
            temp = {'CMD':'AEA0','IMGroup':'','devID':devID,'sender':'system','wifiMAC':'','exeTime':'','actionID':'','duration':'','inst':'','createTime':YMDHMS}
            hour = actionList[i].get('hour')
            min = actionList[i].get('min')
            todolist = actionList[i].get('todo')
            action = todolist[0].get('actionID')
            day = nextweek_YMD
            #day = '20151213'
            if hour<10:
                hour = '0' + str(hour)
            else:
                hour = str(hour)
            if min <10:
                min = '0' + str(min)
            else:
                min = str(min)
            exeTime = day + hour + min + '00'
            temp['exeTime'] = exeTime
            temp['actionID'] = action
         #   data_model('YSJ_forcast').update_set(condition={'devID':devID,'exeTime':re.compile(day),'actionID':action},values=temp,upsert=True)
            print temp
        endTime=miscCommon.getNow()
        print miscCommon.getTime()
        print endTime.now-beginTime.now
        print "End"

def getSourcedata(devid):
    now = miscCommon.getNow().now
    pre_time = now - datetime.timedelta(days=14)
    pre = pre_time.strftime('%Y%m%d%H%M%S')[:8]
    starttime = pre
    endtime = now.strftime('%Y%m%d%H%M%S')[:8]
    #starttime = '20151207000000'
    #endtime =   '20151220235959'
    sourcedata = common.getlogPowerinfo(devid,starttime,endtime)
    for item in sourcedata:
        w = item['W']
        devid = item['devid']
        time = item['time']
        item['cmd'] = '3001'
        item['inst'] = ''
        item['temp'] = ''
        item['actionid'] = '2'
        if item['P'] < 0:
            count = fabs(item['P'])
            item['P'] = 0
    sourcedata = sorted(sourcedata,key=operator.itemgetter('time'),reverse=False)
    for item in sourcedata:
        if 'inst' not in item.keys():
            item['inst'] = ''
            item['temp'] = ''
            item['cmd'] = '3001'
            item['actionid'] = '2'
        if '_id' in item.keys():
            del item['_id']
        #print item
    #miscCommon.saveJsonData('/data/CKR/src/dms/machlearning/data.json', sourcedata)
    return sourcedata	
    
if __name__ == "__main__":	
    main()
