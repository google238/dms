#! /usr/bin/env python
#encoding: utf-8

#Filename: bigData.py  
#Author: Steven Lian
#E-mail: steven.lian@gmail.com  
#Date: 2015-11-13
#Description:   the program is for chakonger bigData analysis

# 张宇系统对bigData部分的函数调用 2015/11/11
# bigData.getCommand(devID,devType,infraTypeID,YMDHMS, requestMode,wday=-1)
# bigData.train(devID,bigType,devType, dataSet, requestMode=CONST_BGANA_MODE_WEEK,  calSaving=False):
# bigData.getModel(devID)
 
CONST_bigData_Ver = "CODE:20151129"

from bigDataCommon import *
import operator
#from miscCommon import *


#****************************************************************%
#get version
#****************************************************************%
def getVersion():
    result=CONST_bigData_Ver+"_"+CONST_bigDataCommon_Ver
#    "_"+irDataFunction.CONST_irDataFunction_Ver+"_"+irDataCommon.CONST_irDataCommon_Ver
    return result

def cmp_YMDHMS(a, b):
    if a>b:
        return 1
    elif a<b:
        return -1
    else:
        return 0

def train(devID,bigType,devType, dataSet, requestMode=CONST_BGANA_MODE_WEEK,  calSaving=False, dataOption=""):
    result=None
    #sort data
    dataSet.sort(cmp=cmp_YMDHMS, key=operator.itemgetter('time'))
    #load sample data    
    midSet=transPowerUsageData(dataSet, devType)
    wattTimeList=midSet["wattTimeList"]
    wattTimeListLen=len(wattTimeList)
    if devType==CONST_BGANA_BGYSJ:
        #prepare sample data to array foramat
#        wattTimeList=filterPowerData(wattTimeList, getThreshold(devType,"durationRange"))
        wattDataList=transWattTimeSample(wattTimeList)
        clusterNumList=getThreshold(devType, "label_count") 
        for clusterNum in clusterNumList:
            labels=calKMeans(wattDataList, clusterNum)
            wattTimeData=addLabel2WattData(wattTimeList, labels)
            wattKeyValSet=calYSJWattKeyValue(wattTimeData, clusterNum)
            if wattKeyValSet<>{}:
                break
        if wattKeyValSet == {}:
            clusterNum,labels = calMeanShift(wattDataList)
            wattTimeData=addLabel2WattData(wattTimeList, labels)
            wattKeyValSet=calYSJWattKeyValue(wattTimeData, clusterNum)
        if wattKeyValSet<>{}:
            result={}
            result["clusterNum"]=clusterNum
            result["powerCount"]=midSet["powerCount"]
            if requestMode==CONST_BGANA_MODE_WEEK:
                wdayBeginEndSet=calWeekYSJControlBehaiver(wattTimeData, wattKeyValSet)
                result["devID"]=devID
                result["devType"]=devType
                result["bigType"]=bigType
                result["requestMode"]=requestMode
                result[requestMode]=wdayBeginEndSet
                result["keyValSet"]=wattKeyValSet
                if calSaving==True:
                    savingSet=calPowerSaving(wattTimeData, wdayBeginEndSet)
                    result["saving"]=savingSet
                if dataOption=="ALL":
                    result["wattTimeData"]=wattTimeData
            else:
                wattKeyValSet=calWattKeyValue(wattTimeData, clusterNum)
                wdayBeginEndSet=calControlBehaiver(wattTimeData, wattKeyValSet)
            

    elif devType == CONST_BGANA_BGRSQ:
        #prepare sample data to array foramat
        wattDataList=transWattTimeSample(wattTimeList)
        clusterNumList=getThreshold(devType, "label_count")
        for clusterNum in clusterNumList:
            labels=calKMeans(wattDataList, clusterNum)
            wattTimeData=addLabel2WattData(wattTimeList, labels)
            wattKeyValSet=calRSQWattKeyValue(wattTimeData, clusterNum)
            if wattKeyValSet<>{}:
                break
        if wattKeyValSet<>{}:
            result={}
            result["clusterNum"]=clusterNum
            result["powerCount"]=midSet["powerCount"]
            if requestMode==CONST_BGANA_MODE_WEEK:
                wdayBeginEndSet=calWeekRSQControlBehaiver(wattTimeData, wattKeyValSet)
                result["devID"]=devID
                result["devType"]=devType
                result["bigType"]=bigType
                result["requestMode"]=requestMode
                result[requestMode]=wdayBeginEndSet
                result["keyValSet"]=wattKeyValSet
                if calSaving==True:
                    savingSet=calPowerSaving(wattTimeData, wdayBeginEndSet)
                    result["saving"]=savingSet
                if dataOption=="ALL":
                    result["wattTimeData"]=wattTimeData
            else:
                wattKeyValSet=calWattKeyValue(wattTimeData, clusterNum)
                wdayBeginEndSet=calControlBehaiver(wattTimeData, wattKeyValSet)
            pass
        
    elif devType == CONST_BGANA_KT:
        pass
    else:
        pass
    print result
    return result
        
def filterPowerData(wattTimeList, range):
    result=[]
    for a in wattTimeList:
        if a["duration"]< range:
            result.append(a)
    return result

# temp solution
def addCommand(bigType, infraTypeID, scheduleSet):
    result=[]
    if bigType=="KG":
        for a in scheduleSet:
            set1={}
            if a=="begin":
                set1["hour"]=scheduleSet[a]["hour"]
                set1["min"]=scheduleSet[a]["min"]
                set1["wday"]=scheduleSet[a]["wday"]
                set1["todo"]=[{"actionID":"2"}]
            elif a=="end":
                set1["hour"]=scheduleSet[a]["hour"]
                set1["min"]=scheduleSet[a]["min"]
                set1["wday"]=scheduleSet[a]["wday"]
                set1["todo"]=[{"actionID":"0"}]
            else:
                pass
            if set1<>{}:
                result.append(set1)
    return result

#special handle , add additional timer
def addAddtionalCommand(aList, times, timeSlot):
    return aList

    
def getCommand(devID,bigType, devType,infraTypeID,YMDHMS,model, requestMode=CONST_BGANA_MODE_WEEK,wday=-1):
    result=[]
    if wday >=0 and wday<7:
        weekDay=wday
    else:
        weekDay = YMDYMS2datetime(YMDHMS, "wday")
    if devType==CONST_BGANA_BGYSJ:
        if requestMode==CONST_BGANA_MODE_WEEK:
            wdayBeginEndSet=model[0]
            try:
                try:
                    scheduleList=wdayBeginEndSet[requestMode][weekDay]
                except:
                    weekDay=str(weekDay) # ?????
                    scheduleList=wdayBeginEndSet[requestMode][weekDay]
            except:
                scheduleList=[]
            if bigType=="KG":
                scheduleList=addAddtionalCommand(scheduleList, times=2, timeSlot=5)
            actionList=[]
            list1=[]
            for aSet in scheduleList:
                list1=addCommand(bigType, infraTypeID, aSet)
                actionList.extend(list1)
            if len(actionList)>0:
                result=actionList
    #
    elif devType == CONST_BGANA_BGRSQ:
        if requestMode==CONST_BGANA_MODE_WEEK:
            wdayBeginEndSet=model[0]
            try:
                try:
                    scheduleList=wdayBeginEndSet[requestMode][weekDay]
                except:
                    weekDay=str(weekDay) # ?????
                    scheduleList=wdayBeginEndSet[requestMode][weekDay]
            except:
                scheduleList=[]
            actionList=[]
            list1=[]
            for aSet in scheduleList:
                list1=addCommand(bigType, infraTypeID, aSet)
                actionList.extend(list1)
            if len(actionList)>0:
                result=actionList
        pass
    elif devType == CONST_BGANA_KT:
        pass
    else:
        pass
    return result
 
