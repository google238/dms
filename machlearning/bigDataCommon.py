#! /usr/bin/env python
#encoding: utf-8

#Filename: bigDataCommon.py  
#Author: Steven Lian
#E-mail: steven.lian@gmail.com  
#Date: 2015-8-13
#Description:   
import numpy as np
from miscCommon import *
from sklearn.cluster import KMeans,MiniBatchKMeans
from sklearn.cluster import MeanShift, estimate_bandwidth

CONST_bigDataCommon_Ver = "COMM:20151201"

# define common global var:
# bigData analysis type:
CONST_BGANA_BGYSJ="BGYSJ"
CONST_BGANA_BGRSQ="BGRSQ"
CONST_BGANA_BGKT="BGKT"

# power count threshold
CONST_POWERCOUNT_THRESHOLD=239

#type const

CONST_LABEL_K_THRESHOLD=5 # ignore rate 0.5%
CONST_LABEL_SCALE_RATIO=1000

CONST_PULSE_SLOT=600 # 4mins


gaBigDataAnaTypeSet={
CONST_BGANA_BGYSJ:{"devTypeList":["饮水机"], 
    "threshold":{"motor":0,"KWHRange":[[0.005,0.03]],"durationRange":600, 
    "label_count":[3, 4, 5, 6,7,8,9,10], "label_min":2, "label_position":1},  
    }, 
CONST_BGANA_BGRSQ:{"devTypeList":["热水器", "红外热水器"], 
    "threshold":{"motor":0,"KWHRange":[[0.05,0.2]],
    "label_count":[4, 5, 6, 7], "label_min":2, "label_position":1},  
    "splitSlot":30, 
    }, 
CONST_BGANA_BGKT:{"devTypeList":["空调"], 
    "threshold":{"motor":0,"KWHRange":[[0.005,0.03]], 
    "label_count":[5], "label_min":2, "label_position":1},  
    }, 
}


# request mode:

CONST_BGANA_MODE_DAY="day"
CONST_BGANA_MODE_WEEK="week"
CONST_BGANA_MODE_MONTH="month"
CONST_WDAYRANGE=(0, 1, 2, 3, 4, 5, 6)

CONST_WEEKSTAMP_MAX= 100079  #59+23*60+6*60*24
CONST_WEEKSTAMP_MIN=0

def devType2AnaType(inDevType):
    result=None
    aBigDataAnaTypeSet=gaBigDataAnaTypeSet
    for a in aBigDataAnaTypeSet:
        dataList=aBigDataAnaTypeSet[a]
        for b in dataList:
            devType=b["devType"]
            nT1=devType.decode("utf8")
            if devType==inDevType or nT1==inDevType:
                result=a
                break
    return result
    

#common function:
def YMDYMS2datetime(YMDHMS, option="ALL"):
    t = time.strptime(YMDHMS,'%Y%m%d%H%M%S')
    year=t[0]
    month=t[1]
    day=t[2]
    hour=t[3]
    min=t[4]
    wday=t[6]
    if option =="year":
        return year
    elif option == "month":
        return month
    elif option=="day":
        return day
    elif option=="wday":
        return wday
    elif option =="hour":
        return hour
    elif option=="min":
        return min
    else:
        return t
        
    
def YMDYMS2WeekDay(YMDHMS):
#    import time, datetime
    return YMDYMS2datetime(YMDHMS, "wday")


CONST_SLOTSPLITTIME=300 # 5 minues 
CONST_SLOTSPLITIME_MIN=5
def YMDYMS2WeekStamp(YMDHMS, splitSlot=CONST_SLOTSPLITIME_MIN):
#    import time, datetime
    t = time.strptime(YMDHMS,'%Y%m%d%H%M%S')    
    wday=t[6]
    hour=t[3]
    min=t[4]
    min=int(t[4]/splitSlot)*splitSlot
    nStamp=min+hour*60+wday*60*24
    return nStamp

def getWeekStampBeginEndTime(wday):
#    nStamp=min+hour*60+wday*60*24
    if wday>6 or wday<0:
        beginVal=CONST_WEEKSTAMP_MIN
        endVal=CONST_WEEKSTAMP_MAX
    else:
        beginVal=0+0*60+wday*1440 #60*24
        endVal=beginVal+1440 #60+60*23
    return beginVal, endVal
    
# weekDay Stamp conver to weekday + hour + min
def weekStamp2WHM(LVStamp):
    if LVStamp>= 10080: #7*1440
        LVStamp=10079
    elif LVStamp<0:
        LVStamp=0
    wday=int(LVStamp/(1440)) # 60*24
    val=LVStamp-1440*wday
    hour=int(val/60)
    min=val-hour*60
    result={"wday":wday, "hour":hour, "min":min, "weekStamp":LVStamp}
    return result

def addWeekStamp(t1, t2, wday=10):
    t=t1+t2
    beginVal, endVal=getWeekStampBeginEndTime(wday)
    if t<beginVal:
        t=beginVal
    if t>endVal:
        t=endVal
    return t
    
def genEmptyWeekStampSet():
    result={}
    for wday in range(0, 6):
        for hour in range(0, 23):
            for min in range(0, 60/CONST_SLOTSPLITIME_MIN):
                nStamp=min+hour*60+wday*60*24
                result[nStamp]=""
    return result

class timeSlot:
    def __init__(self, step=30):
        self.slotStep=step
        self.slotList=[]
    
    def fill(self, dataList):
        aSet=set([])
        for a in dataList:
            nT1=int(a/self.slotStep)
            aSet.add(nT1)
        self.slotList=list(aSet)
        self.slotListCount=len(self.slotList)
        return self.slotList
        
    def covert(self):
        result=[]
        if self.slotListCount==1:
            set1={"begin":{}, "end":{}}
            slot=self.slotList[0]
            beginStamp=slot*self.slotStep
            endStamp=(slot+1)*self.slotStep
            set1["begin"]=weekStamp2WHM(beginStamp)
            set1["end"]=weekStamp2WHM(endStamp)
            result.append(set1)
        elif self.slotListCount>1:
            slot=self.slotList[0]
            beginStamp=slot*self.slotStep
            preSlot=slot
            for i in range(1, self.slotListCount):
                slot=self.slotList[i]
                set1={"begin":{}, "end":{}}
                if (slot-preSlot)>1:
                    endStamp=(preSlot+1)*self.slotStep
                    set1["begin"]=weekStamp2WHM(beginStamp)
                    set1["end"]=weekStamp2WHM(endStamp)
                    beginStamp=slot*self.slotStep
                    result.append(set1)
                preSlot=slot
                
        return result
   
def calMeanShift(dataSet):
    dataSet = np.array(dataSet)
    bandwidth = estimate_bandwidth(dataSet, quantile=0.005) 
    ms = MeanShift(bandwidth=bandwidth, bin_seeding=True)
    ms.fit(dataSet)
    labels = ms.labels_
    labels_unique = np.unique(labels)
    return  len(labels_unique),labels 

# logic
def calKMeans(dataSet, clusterNum):
    km = KMeans(n_clusters = clusterNum)
    km.fit(dataSet)
    labels = km.labels_
    return labels

def addLabel2WattData(dataList, labels):
    i=0
    for a in dataList:
        a["label"]=labels[i]
        i+=1
    return dataList

CONST_MINWATT_THRESOLD=999999999.0
def calYSJWattKeyValue(dataList, clusterNum, devType=CONST_BGANA_BGYSJ):
    CONST_OPTIMIZE_VAL=-0.1
    labelSet={}
    for label in range(clusterNum):
        labelSet[label]={"max":0.0, "min":CONST_MINWATT_THRESOLD, "avg":0.0, "total":0.0, "count":0}
    nLabelCount=0
    for a in dataList:
        label=a["label"]
        watt=a["durationKWH"]
        if watt > labelSet[label]["max"]:
            labelSet[label]["max"]=watt
        if watt < labelSet[label]["min"]:
            labelSet[label]["min"]=watt
        labelSet[label]["total"]+=watt
        labelSet[label]["count"]+=1
    # 判断数据的有效性， 删除特别奇异的数据 
    nLabelCount=0;nLabelItemCount=0
    for label in range(clusterNum):
        labelSet[label]["avg"]=labelSet[label]["total"]/ labelSet[label]["count"]
        nLabelCount+=labelSet[label]["count"]
        nLabelItemCount+=1
    for label in range(clusterNum):
        nT1=CONST_LABEL_SCALE_RATIO*labelSet[label]["count"]/nLabelCount
        if nT1<CONST_LABEL_K_THRESHOLD:
            del labelSet[label]
            nLabelItemCount-=1
    #calculate the threshold
    wattThreshold=0
    minList=[];maxList=[]
    for label in labelSet:
        minList.append(labelSet[label]["min"])
        maxList.append(labelSet[label]["max"])
    minList.sort()
#    maxList.sort()
    label_position=getThreshold(devType, "label_position")
    if label_position<nLabelItemCount:
        wattThreshold=minList[label_position]#special handle
    rightFlag=0
    KWHRange=getThreshold(devType, "KWHRange")
    for a in KWHRange:
        if wattThreshold>a[0] and wattThreshold<a[1]:
            rightFlag=1
            break
    if nLabelItemCount<getThreshold(devType, "label_min"):   
        rightFlag=0
    if rightFlag==1:
        labelSet["wattThreshold"]=wattThreshold    
    else:
        labelSet={}
    return labelSet

def calWeekYSJControlBehaiver(dataList, keyValSet):
    CONST_YSJ_BEGIN=-15
    CONST_YSJ_END=15
    # the watt threshold for behaivor
    wattThreshold=keyValSet["wattThreshold"]
    # determine power on off schedule
    weekTimeSet={}
    maxDuration=0
    for data in dataList:
        currTime=data["currTime"]
        watt=data["durationKWH"]
        duration=data["duration"]

        LVStamp=YMDYMS2WeekStamp(currTime)
        if LVStamp not in weekTimeSet:
            weekTimeSet[LVStamp]=0
        if watt>wattThreshold:
            print watt,currTime
            weekTimeSet[LVStamp]+=1
        else:
            weekTimeSet[LVStamp]+=0
        if duration>maxDuration:
            maxDuration=duration   
  # calculate the begin time and end time by day
    wdayBeginEndSet={}
    for wday in CONST_WDAYRANGE:
        wDayDataCount=0
        wdayBeginEndSet[wday]={"begin":{}, "end":{}}            
        beginVal, endVal=getWeekStampBeginEndTime(wday)
        aTimeList=[]
        aTimeLen=0
        for LVStamp in weekTimeSet:
            if LVStamp>beginVal and LVStamp<endVal:
                if weekTimeSet[LVStamp]>=1:
                    aTimeList.append(LVStamp)
                    aTimeLen+=1
                wDayDataCount+=1
        if aTimeLen>0 and aTimeLen <=2:
            #need more analysis, only 1-2 data
            beginStamp=59+23*60+wday*60*24
            endStamp=0
            for data in aTimeList:
                if beginStamp>data:
                    beginStamp=data
                if endStamp<data:
                    endStamp=data
        elif aTimeLen>2:
            aTimeList.sort()
            beginStamp=aTimeList[1]
            endStamp=aTimeList[-1]
            beginStamp=addWeekStamp(beginStamp, CONST_YSJ_BEGIN)
            endStamp=addWeekStamp(endStamp, CONST_YSJ_END)
            pass
        else:
            beginStamp=(beginVal+endVal)/2
            endStamp=beginStamp
            
#            beginStamp=min(aList)
#            endStamp=max(aList)
        wdayList=[]
        set1={}
        if wDayDataCount>0:
            set1["begin"]=weekStamp2WHM(beginStamp)
            set1["end"]=weekStamp2WHM(endStamp)
        else: 
            # no data in this wday, don't do anthing
            set1["begin"]=weekStamp2WHM(beginStamp)
            set1["end"]=weekStamp2WHM(endStamp)
        wdayList.append(set1)
        wdayBeginEndSet[wday]=wdayList
    return wdayBeginEndSet


def calRSQWattKeyValue(dataList, clusterNum, devType=CONST_BGANA_BGRSQ):
    labelSet={}
    for label in range(clusterNum):
        labelSet[label]={"max":0.0, "min":CONST_MINWATT_THRESOLD, "avg":0.0, "total":0.0, "count":0}
    nLabelCount=0
    for a in dataList:
        label=a["label"]
        watt=a["durationKWH"]
        if watt > labelSet[label]["max"]:
            labelSet[label]["max"]=watt
        if watt < labelSet[label]["min"]:
            labelSet[label]["min"]=watt
        labelSet[label]["total"]+=watt
        labelSet[label]["count"]+=1
    # 判断数据的有效性， 删除特别奇异的数据 
    nLabelCount=0;nLabelItemCount=0
    for label in range(clusterNum):
        labelSet[label]["avg"]=labelSet[label]["total"]/ labelSet[label]["count"]
        nLabelCount+=labelSet[label]["count"]
        nLabelItemCount+=1
    for label in range(clusterNum):
        nT1=CONST_LABEL_SCALE_RATIO*labelSet[label]["count"]/nLabelCount
        if nT1<CONST_LABEL_K_THRESHOLD:
            del labelSet[label]
            nLabelItemCount-=1
    # calculate the watt threshold for behaivor
    wattThreshold=0
    minList=[];maxList=[]
    for label in labelSet:
        minList.append(labelSet[label]["min"])
        maxList.append(labelSet[label]["max"])
    minList.sort()
#    sorted(maxList)
    label_position=getThreshold(devType, "label_position")
    if label_position<nLabelItemCount:
        wattThreshold=minList[label_position]#special handle
    rightFlag=0
    KWHRange=getThreshold(devType, "KWHRange")
    for a in KWHRange:
        if wattThreshold>a[0] and wattThreshold<a[1]:
            rightFlag=1
            break
    if nLabelItemCount<getThreshold(devType, "label_min"):   
        rightFlag=0
    if rightFlag==1:
        labelSet["wattThreshold"]=wattThreshold    
    else:
        labelSet={}

    return labelSet

def calWeekRSQControlBehaiver(dataList, keyValSet):
    CONST_OPTIMIZE_VAL=-0.1
    CONST_RSQ_BEGIN=-15
    CONST_RSQ_END=15
    # get the watt threshold for behaivor
    wattThreshold=keyValSet["wattThreshold"]
    # determine power on off schedule
    weekTimeSet={}
    maxDuration=0
    for data in dataList:
        currTime=data["currTime"]
        watt=data["durationKWH"]
        duration=data["duration"]
        LVStampDuration=int(duration/60)+1
#        if LVStampDuration<1:
#            LVStampDuration=1
        LVStamp=YMDYMS2WeekStamp(currTime)
        for i in range(LVStamp, LVStamp+LVStampDuration):
            if i not in weekTimeSet:
                weekTimeSet[i]=0
            if watt>wattThreshold:
                weekTimeSet[i]+=1
            else:
                weekTimeSet[i]+=0
        if duration>maxDuration:
            maxDuration=duration
        
  # calculate the begin time and end time by day
    x = timeSlot()
    x.fill(weekTimeSet)
    sList=x.covert()
    wdayBeginEndSet={}
    wDayDataCount=0
    for wday in CONST_WDAYRANGE:
        wdayBeginEndSet[wday]=[]
    for s in sList:
        wday=s["begin"]["wday"]
        wdayBeginEndSet[wday].append(s)
        wDayDataCount+=1
    return wdayBeginEndSet


# saving calculation

def calPowerSaving(dataList, wdayBeginEndSet):
    weekTimeSet={}
    savingWatt=0.0
    usedWatt=0.0
    totalWatt=0.0
    for data in dataList:
        currTime=data["currTime"]
        watt=data["durationKWH"]
        LVStamp=YMDYMS2WeekStamp(currTime)
        totalWatt+=watt
        for wbe in wdayBeginEndSet:
            wDataList=wdayBeginEndSet[wbe]
            for wData in wDataList:
                beginStamp=wData["begin"]["weekStamp"]
                endStamp=wData["end"]["weekStamp"]
                if LVStamp > beginStamp and LVStamp < endStamp:
                    usedWatt+=watt
                pass
    savingWatt=totalWatt-usedWatt
    savingPercent=float(savingWatt)/totalWatt
    resultSet={"totalWatt":totalWatt, "savingWatt":savingWatt, "savingPercent":savingPercent}
    return resultSet

 
# prepare samples
def sortPowerTimeDict(sIn):
    aDict= sorted(sIn.iteritems(), key=lambda d:d[0])
    aList=[];bList=[];cList=[]
    for a in aDict:
        aList.append(a[0]["P"])
        bList.append(a[0]["dtime"])
        cList.append(a[0])
    return aList, bList, cList

def transWattTimeSample(dataList):
    wattSampleData=[]
    for a in dataList:
        watt=a["durationKWH"]
        list1=[]
        list1.append(watt)
        wattSampleData.append(list1)
    return wattSampleData

def getThreshold(devType, requestData):
    try:
        motorThreshold=gaBigDataAnaTypeSet[devType]["threshold"][requestData]
    except:
        motorThreshold=0
    return motorThreshold

def transPowerUsageData(devResultList, devType=CONST_BGANA_BGYSJ):
    
    motorThreshold=getThreshold(devType, "motor")
    
    # calculate the power usage.
    aPowerList=[]
    aWattList=[]
    aYMDTimeList=[]
    aPowerTimeList=[]
#    dPowerTime={}
    sessionSet1={}

    totalDuration=0
    currP, preP=0, 0
    motorDuration=0.0
    motorCount=0
    motorPower=0.0
    # calculate power 
    currW, preW, currRealW, totalW=0.0, 0.0, 0.0, 0.0 	#用于耗电计算
    minW, maxW, auxW=0.0, 0.0, 0.0 	#用于耗电计算
    firstW, lastW, addW, subW=0.0, 0.0, 0.0, 0.0	#用于耗电计算
    requestPreTemp, requestCurrTemp, requestAvgTemp=CONST_DEFAULT_TEMP, 0.0, 0.0	#用于设定温度计算
    preTemp, currTemp, avgTemp=CONST_DEFAULT_TEMP, 0.0, 0.0 #用于外界温度计算
    guessBigType, KGHWCount="KG", 0	#判断类型
    tempDuration=0
    beginTime, preTime, currTime="", "", ""	#按照需要时间筛选
    preYMD, currYMD="", ""	#按照需要日期筛选
    i=0
    for r in devResultList:
        currW=float(r["W"])
        currTime=r["time"]
        currYMD=currTime[0:8]
        currP=int(r["P"])
        aPowerList.append(currP)
        aYMDTimeList.append(currTime)
        aPowerTimeList.append(str2Time(currTime))
        currInst=r["inst"]
        requestCurrTemp=isACInst(currInst, "T")
        if requestCurrTemp<0:
            requestCurrTemp=requestPreTemp
        else:
            #guessBigType="KGHW"
            KGHWCount+=1
        currTemp=r["temp"]
        currDuration=0.0
        #temperature
        try:
            currTemp=int(currTemp)
        except:
            currTemp=preTemp

        if i==0:#初始化数据
            minW=currW
            preW=currW
            beginTime=currTime
            preTime=currTime
            preYMD=currYMD
            requestPreTemp=requestCurrTemp
            preP=currP
        else:
            currDuration=diffTime(preTime, currTime)
            totalDuration+=currDuration
            if abs(requestPreTemp)<=0.001 or abs(preTemp)<=0.001:
                tempDuration+=0
            else:
                requestAvgTemp+=currDuration*requestPreTemp
                avgTemp+=currDuration*preTemp
                tempDuration+=currDuration
        # calculate motor time
        if currP>motorThreshold:
            if preP>motorThreshold:
                motorDuration+=currDuration	#计算压缩机工作时间
            motorCount+=1
            motorPower+=currP
        if currW<preW:	
            auxW+=preW	#计算设备重启造成的计算错误
        currRealW=currW+auxW
        aWattList.append(currRealW)
        set1={}
#        set1["W"]=aWattList[i]
#        set1["P"]=aPowerList[i]
#        set1["dtime"]=aPowerTimeList[i]
#        dPowerTime[currTime]=set1
        # preData 保留前一个值
        preW=currW
        preTime=currTime
        preYMD=currYMD
        rPreTemp=requestCurrTemp
        preP=currP
        i+=1
    nCount=i # data length
    #power meter
    maxW=currW
    totalW=maxW+auxW-minW
    if motorCount>0:	#计算算数平均功率
        motorPower=motorPower/motorCount
    if tempDuration>0:	#计算平均设定温度
        requestAvgTemp=requestAvgTemp/tempDuration
        avgTemp=avgTemp/tempDuration  

    sessionSet1["motorPower"]=int(motorPower)
    if motorDuration>0:	#计算按压缩机工作时间计算的平均功耗，可能比实际的值高
        nT1=int(totalW*1000/(motorDuration/3600.0))
    else:
        nT1=0
    sessionSet1["motorPowerAvg"]=nT1
    sessionSet1["motorDuration"]=int(motorDuration)
    sessionSet1["totalDuration"]=int(totalDuration)
    sessionSet1["avgTemp"]=int(avgTemp)
    sessionSet1["requestAvgTemp"]=requestAvgTemp
    sessionSet1["KWH"]=round(totalW, 4)
    #sessionSet1["guessBigType"]=guessBigType
    sessionSet1["KGHWHCount"]=KGHWCount
    
    if totalDuration>0:	#计算压缩机工作时间占比和这个时间段的平均功耗
        nT1=round(motorDuration/totalDuration, 2)     
        nT2=totalW/(totalDuration/3600.0)
    else:
        nT1=0
        nT2=0
    sessionSet1["motorDurationRate"]=nT1
    sessionSet1["avgKWH"]=round(nT2, 2)

#    aPowerList, aPowerTimeList, aYMDTimeList =sortPowerTimeDict(dPowerTime)

    # calculate watt time relation
    aWattTimeList=[]
    if nCount>1:
        preWatt=0.0; currWatt=0.0
        preP=aPowerList[0]
        preW=aWattList[0]
        preTime=aYMDTimeList[0]
        preWatt=preW; currWatt=preW
        preWattTime=preTime; currWattTime=preTime
        for i in range(1, nCount):
            currP=aPowerList[i]
            currW=aWattList[i]
            currTime=aYMDTimeList[i]
            currDuration=diffTime(preTime, currTime)
            # calculate duration time and watt
            if currP==0 : # ==0 
#            if currP==0 and currDuration<CONST_PULSE_SLOT: # ==0 and in  4 minus temp solution
                currWatt=currW
                currWattTime=currTime
                durationWatt=currWatt-preWatt
                preWatt=currWatt
                durationTime=diffTime(preWattTime, currWattTime)
                preWattTime=currWattTime
               
                if durationWatt>0.001:
                    setWattTime={"currTime":preWattTime, "duration":durationTime, "durationKWH":durationWatt}
                    aWattTimeList.append(setWattTime)
                else:
                    pass
#            elif currDuration > CONST_PULSE_SLOT: # ==0 or 4 minus temp solution 
#                currWatt=preW
#                currWattTime=preTime
#                durationWatt=currWatt-preWatt
#                preWatt=currWatt
#                durationTime=diffTime(preWattTime, currWattTime)
#                preWattTime=currWattTime
#                if durationWatt>0:
#                    setWattTime={"currTime":preWattTime, "duration":durationTime, "durationKWH":durationWatt}
#                    aWattTimeList.append(setWattTime)
#                else:
#                    pass
            preP=currP
            preW=currW
            preTime=currTime
        


    #sort the data
#    aPowerList, aPowerTimeList, aYMDTimeList =sortPowerTimeDict(dPowerTime)
    resultSet={"powerCount":nCount,"powerList":aPowerList, "powerTimeList":aPowerTimeList, "session":sessionSet1, \
    "YMDTimeList":aYMDTimeList, "wattList":aWattList, "wattTimeList":aWattTimeList}
#    return aPowerList, aPowerTimeList,sessionSet1, aYMDTimeList, 
    return resultSet

# old function

#************************************************************************************#
# to Calculate the air codition type, and determine if its status is nomal function: ACBEGIN
#********************"**************************************************************#
CONST_SCALE_RATE=10000
CONST_FAN_THRESHOLD=100
CONST_POWER_DIVIDNUM=100
CONST_WATT_THRESHOLD=1.0
CONST_IGNORE_TIMESLOT=300
CONST_DERICATIVE=10000
CONST_DERICATIVE_IGNORE_THRESHOLD=0.1
CONST_DERICATIVE_THRESHOLD=130
CONST_BIANPIN_DERICATIVE=130
CONST_BIANPIN_STDEV=100
CONST_MININUM_NUM=500
CONST_FANCOUNT_THRESHOLD=10
CONST_FANPOWER_THRESHOLD=15
CONST_STDEV_THRESHOLD=100
CONST_ACPOWER_THRESHOLD=400
CONST_DEFAULT_TEMP=25
CONST_KGHW_THRESHOLD=5

gACPowerRangeList=[
{"powerType":700, "ACType":"BIANPIN","powerAlias":"1PL", "low":650, "high":800}, 
{"powerType":700, "ACType":"DINGPIN","powerAlias":"1PL", "low":750, "high":900}, 
{"powerType":850, "ACType":"BIANPIN","powerAlias":"1P", "low":700, "high":900}, 
{"powerType":850, "ACType":"DINGPIN","powerAlias":"1P", "low":800, "high":1000}, 
{"powerType":1000, "ACType":"BIANPIN","powerAlias":"1.5P", "low":900, "high":1100}, 
{"powerType":1100, "ACType":"DINGPIN","powerAlias":"1.5P", "low":1000, "high":1200}, 
{"powerType":1500, "ACType":"BIANPIN","powerAlias":"2P", "low":1350, "high":1500}, 
{"powerType":1500, "ACType":"DINGPIN","powerAlias":"2P", "low":1400, "high":1600}, 
{"powerType":2100, "ACType":"BIANPIN","powerAlias":"3P", "low":2000, "high":2300}, 
{"powerType":2100, "ACType":"DINGPIN","powerAlias":"3P", "low":2100, "high":2500}, 
]

    

def getACPowerType(sIn):
    result={"powerType":"", "powerAlias":""}
    global gACPowerRangeList
    aList=gACPowerRangeList
    power=sIn["maxP"]
    ACType=sIn["ACType"]
    for a in aList:
        if ACType==a["ACType"]:
            if power >= a["low"] and power <= a["high"]:
                result["powerType"]=a["powerType"]
                result["powerAlias"]=a["powerAlias"]
                break
    return result

def calPowerUsage(devResultList, ):
    # calculate the power usage.
    aPowerList=[]
    aWattList=[]
    aYMDTimeList=[]
    aPowerTimeList=[]
    dPowerTime={}
    sessionSet1={}

    totalDuration=0
    currP, preP=0, 0
    motorDuration=0.0
    motorCount=0
    motorPower=0.0
    # calculate power 
    currW, preW, currRealW, totalW=0.0, 0.0, 0.0, 0.0 	#用于耗电计算
    minW, maxW, auxW=0.0, 0.0, 0.0 	#用于耗电计算
    firstW, lastW, addW, subW=0.0, 0.0, 0.0, 0.0	#用于耗电计算
    requestPreTemp, requestCurrTemp, requestAvgTemp=CONST_DEFAULT_TEMP, 0.0, 0.0	#用于设定温度计算
    preTemp, currTemp, avgTemp=CONST_DEFAULT_TEMP, 0.0, 0.0 #用于外界温度计算
    guessBigType, KGHWCount="KG", 0	#判断类型
    tempDuration=0
    beginTime, preTime, currTime="", "", ""	#按照需要时间筛选
    preYMD, currYMD="", ""	#按照需要日期筛选
    i=0
    for r in devResultList:
        currW=float(r["W"])
        currTime=r["time"]
        currYMD=currTime[0:8]
        currP=int(r["P"])
        aPowerList.append(currP)
        aYMDTimeList.append(currTime)
        aPowerTimeList.append(str2Time(currTime))
        dPowerTime[currTime]=currP
        currInst=r["inst"]
        requestCurrTemp=isACInst(currInst, "T")
        if requestCurrTemp<0:
            requestCurrTemp=requestPreTemp
        else:
            #guessBigType="KGHW"
            KGHWCount+=1
        currTemp=r["temp"]
        currDuration=0.0
        #temperature
        try:
            currTemp=int(currTemp)
        except:
            currTemp=preTemp

        if i==0:#初始化数据
            minW=currW
            preW=currW
            beginTime=currTime
            preTime=currTime
            preYMD=currYMD
            requestPreTemp=requestCurrTemp
            preP=currP
        else:
            currDuration=diffTimeNew(preTime, currTime)
            totalDuration+=currDuration
            if abs(requestPreTemp)<=0.001 or abs(preTemp)<=0.001:
                tempDuration+=0
            else:
                requestAvgTemp+=currDuration*requestPreTemp
                avgTemp+=currDuration*preTemp
                tempDuration+=currDuration
        # calculate motor time
        if currP>CONST_MOTOR_THRESHOLD:
            if preP>CONST_MOTOR_THRESHOLD:
                motorDuration+=currDuration	#计算压缩机工作时间
            motorCount+=1
            motorPower+=currP
        if currW<preW:	
            auxW+=preW	#计算设备重启造成的计算错误
        currRealW=currW+auxW
        aWattList.append(currRealW)
        # preData 保留前一个值
        preW=currW
        preTime=currTime
        preYMD=currYMD
        rPreTemp=requestCurrTemp
        preP=currP
        i+=1
    nCount=i # data length
    #power meter
    maxW=currW
    totalW=maxW+auxW-minW
    if motorCount>0:	#计算算数平均功率
        motorPower=motorPower/motorCount
    if tempDuration>0:	#计算平均设定温度
        requestAvgTemp=requestAvgTemp/tempDuration
        avgTemp=avgTemp/tempDuration  
        
    #put into a log file 保存中间数据
#    sessionSet1["devID"]=devResultList[0]["devid"]
#    sessionSet1["beginTime"]=devResultList[0]["time"]
    sessionSet1["motorPower"]=int(motorPower)
    if motorDuration>0:	#计算按压缩机工作时间计算的平均功耗，可能比实际的值高
        nT1=int(totalW*1000/(motorDuration/3600.0))
    else:
        nT1=0
    sessionSet1["motorPowerAvg"]=nT1
    sessionSet1["motorDuration"]=int(motorDuration)
    sessionSet1["totalDuration"]=int(totalDuration)
    sessionSet1["avgTemp"]=int(avgTemp)
    sessionSet1["requestAvgTemp"]=requestAvgTemp
    sessionSet1["KW"]=round(totalW, 4)
    #sessionSet1["guessBigType"]=guessBigType
    sessionSet1["KGHWCount"]=KGHWCount
    
    if totalDuration>0:	#计算压缩机工作时间占比和这个时间段的平均功耗
        nT1=round(motorDuration/totalDuration, 2)     
        nT2=totalW/(totalDuration/3600.0)
    else:
        nT1=0
        nT2=0
    sessionSet1["motorDurationRate"]=nT1
    sessionSet1["avgKWH"]=round(nT2, 2)

    # calculate watt time relation
    aWattTimeList=[]
    if nCount>1:
        preWatt=0.0; currWatt=0.0
        preP=aPowerList[0]
        preW=aWattList[0]
        preTime=aYMDTimeList[0]
        preWatt=preW; currWatt=preW
        preWattTime=preTime; currWattTime=preTime
        for i in range(1, nCount):
            preP=aPowerList[i]
            preW=aWattList[i]
            preTime=aYMDTimeList[i]
            currDuration=diffTimeNew(preTime, currTime)
            # calculate duration time and watt
            if currP==0 and currDuration<239: # ==0 and in  4 minus temp solution
                currWatt=currW
                currWattTime=currTime
                durationWatt=currWatt-preWatt
                preWatt=currWatt
                durationTime=diffTimeNew(preWattTime, currWattTime)
                preWattTime=currWattTime
                if durationWatt>0:
                    setWattTime={"currTime":preWattTime, "duration":durationTime, "durationWatt":durationWatt}
                    aWattTimeList.append(setWattTime)
                else:
                    pass
            elif currDuration > 239: # ==0 or 4 minus temp solution 
                currWatt=preW
                currWattTime=preTime
                durationWatt=currWatt-preWatt
                preWatt=currWatt
                durationTime=diffTimeNew(preWattTime, currWattTime)
                preWattTime=currWattTime
                if durationWatt>0:
                    setWattTime={"currTime":preWattTime, "duration":durationTime, "durationWatt":durationWatt}
                    aWattTimeList.append(setWattTime)
                else:
                    pass


    #sort the data
    aPowerList, aPowerTimeList, aYMDTimeList =sortPowerTimeDict(dPowerTime)
    resultSet={"powerList":aPowerList, "powerTimeList":aPowerTimeList, "session":sessionSet1, \
    "YMDTimeList":aYMDTimeList, "wattList":aWattList, "wattTimeList":aWattTimeList}
#    return aPowerList, aPowerTimeList,sessionSet1, aYMDTimeList, 
    return resultSet


def calCMDUsage(devResultList):
    aList=[]
    count=0
    for r in devResultList:
        set1={}
        if "cmd" in r:
            set1["CMD"]=r["cmd"]
            cmd=r["cmd"]
        else:
            set1["CMD"]=""
            cmd=""
        if "actionid" in r:
            set1["actionID"]=r["actionid"]
            actionID=r["actionid"]
        else:
            set1["actionID"]=""
            actionID=""

        if "inst" in r:
            set1["inst"]=r["inst"]
        else:
            set1["inst"]=""
        if "temp" in r:
            set1["temp"]=r["temp"]
        else:
            set1["temp"]=""
        if "time" in r:
            set1["YMDHMS"]=r["time"]
        else:
            set1["YMDHMS"]=""            
        if actionID in ["0", "2", "6", "7","100"] or cmd in ["3006"]:
            aList.append(set1)
            count+=1

    return aList, count
            
#************************************************************************************#
# to Calculate the pop num from a List
#********************"*************************************************************#
def calPopNum(sIn):
    result={"count":0}
    nCount=0
    nTotal=0
    nMax=0
    nMin=0
    nAvg=0
    set1={}
    pop, nPopCount=0, 0

    for a in sIn:
        if nCount==0:
            nMax=a
            nMin=a
        else:
            if a>nMax:
                nMax=a
            if a < nMin:
                nMin=a
        if a in set1:
            set1[a]+=1
            if nPopCount < set1[a]:
                nPopCount=set1[a]
                pop=a
        else:
            set1[a]=1
            pop=a
        nCount+=1
        nTotal+=a
    if nCount>0:
        nAvg=nTotal/nCount
    result["count"]=nCount
    result["max"]=int(nMax)
    result["min"]=int(nMin)
    result["avg"]=nAvg
    result["pop"]=pop
    result=dict(result, **set1)
    return result

#************************************************************************************#
# to Calculate the pop num from a List
#********************"*************************************************************#
def calStDevAvg(sIn):
    result={"count":0}
    aList=[]
    nCount=0
    nTotal=0
    nMax=0
    nMin=0
    nAvg=0
    stDev=0.0
    for a in sIn:
        if nCount==0:
            nMax=a
            nMin=a
        else:
            if a>nMax:
                nMax=a
            if a < nMin:
                nMin=a
        nTotal+=a
        nCount+=1
    if nMax>0:
        for a in sIn:
            nT1=int(a*100/nMax)
            aList.append(nT1)
        if nCount>0:
            nAvg=nTotal/nCount
            nAvg=int(nAvg*100/nMax)
            nT0=0
            for a in aList:
                nT1=(a-nAvg)
                nT1=nT1*nT1
                nT0+=nT1
            stDev=round(nT0/nCount, 2)
    result["count"]=nCount
    result["max"]=int(nMax)
    result["min"]=int(nMin)
    result["avg"]=nAvg
    result["stDev"]=stDev
    return result



def calMotorDist(sIn):
    result={"count":0, "max":0, "min":0, "P0":0,"P1":0, "P2":0, "P3":0, "P4":0,\
    "P5":0,"P6":0, "P7":0, "P8":0, "P9":0, "P10":0}
    nMax=sIn["max"]
    nCount=sIn["count"]
    piece=int(nMax/10)
    popName, popCount="", 0
    for a in sIn:
        if a in ["count", "max", "min", "avg", "pop"]:
            continue
        nPieceCount=sIn[a]
        nT1=int(a/piece)
        pieceName="P"+str(nT1)
        nT1=int(nPieceCount*100/nCount)
        result[pieceName]+=nT1
        if popCount<result[pieceName]:
            popCount=result[pieceName]
            popName=pieceName
    result["count"]=sIn["count"]
    result["max"]=sIn["max"]
    result["min"]=sIn["min"]
    result["popName"]=popName
    return result
    

def anaACTypeByPower(powerList):
    result={}
    motorList=[]
    motorIntList=[]
    fanList=[]
    fanIntList=[]
    nHighCount, nLowCount=0, 0
    nTotal=0
    aList=powerList
    for a in aList:
        nT1=int(a/CONST_POWER_DIVIDNUM)*CONST_POWER_DIVIDNUM
        if a>=CONST_MOTOR_THRESHOLD:
            motorList.append(a)
            motorIntList.append(nT1)
            nHighCount+=1
        if a <=CONST_FAN_THRESHOLD and a >0:
            fanList.append(a)
            fanIntList.append(nT1)
            nLowCount+=1
        nTotal+=1
    if nHighCount>0:
        set1=calPopNum(motorIntList)
        set2=calMotorDist(set1)
        set3=calStDevAvg(motorList)
        if nLowCount>0:
            set4=calPopNum(fanIntList)
            set5=calStDevAvg(fanList)
        result=set2
        result["total"]=nTotal
        result["stDev"]=set3["stDev"]
    return result

def getDivide(avg):
    result=50
    aDataList=[
    [0, 500, 50], [500, 800, 100], [800, 1200, 150], [1200, 1700, 200], [1700, 10000, 250]
    ]
    for a in aDataList:
        nLow=a[0]
        nHigh=a[1]
        if avg>nLow and avg<=nHigh:
            result=a[2]
    return result

def calDerivative(dataList, timeList,nAvg, nCount):
    nDivide=getDivide(nAvg)
    aDerivative=[]
    aDerivativePower=[]
    aDerivativeTime=[]
    
    dericative=0
    preData=int(dataList[0]/nDivide)
    preTime=timeList[0]
    nNum=0
    for i in range(1, nCount):
        currData=int(dataList[i]/nDivide)
        currTime=timeList[i]
        nT1=float(currData-preData)
        t=currTime-preTime
        preTime=currTime
        nT2=t.days*86400+t.seconds # 60*60*24=86400
        if nT2<=0 or nT2>CONST_IGNORE_TIMESLOT:
            continue
        else:
            nT3=nT1/nT2
        aDerivative.append(nT3)

        if abs(nT3)>CONST_DERICATIVE_IGNORE_THRESHOLD:
            continue
        aDerivativePower.append(currData)
        aDerivativeTime.append(currTime)
        nNum+=1
        dericative+=abs(nT3)
    if nNum>0:
        dericative=int(dericative/nNum*CONST_DERICATIVE)
    else:
        dericative=0
    return dericative, aDerivativePower, aDerivativeTime

#2015/11/5
def split2MLData(powerList, splitCount, splitPower):
    result=[]
    aList=[0 for i in range(splitCount)]
    nCount=0
    for a in powerList:
        if a==0:
            index=0
        else:
            index=int(a/splitPower)+1
        if index>=splitCount:
            continue
        aList[index]+=1
        nCount+=1
    if nCount <>0:        
        for a in aList:
            nT1=int((a*CONST_SCALE_RATE)/nCount)
    #        nT1=float(a)/nCount
            result.append(nT1)
    return result

#2015/11/5
def split2MLData2(powerList, splitCount):
    result=[]
    aList=[0 for i in range(splitCount)]
    max=0
    for a in powerList:
        if max<a:
            max=a
    splitPower=int(max/splitCount)+1
    
    nCount=0
    for a in powerList:
        if a==0:
            index=0
        else:
            index=int(a/splitPower)+1
        if index>=splitCount:
            continue
        aList[index]+=1
        nCount+=1
    if nCount <>0:        
        for a in aList:
            nT1=int((a*CONST_SCALE_RATE)/nCount)
    #        nT1=float(a)/nCount
            result.append(nT1)
    return result


def anaACTypeByPowerDerivative(powerList, timeList):
    result={}
    # motor list
    motorList=[]
    motorTimeList=[]
    motorIntList=[]
    nMotorCount, nMotorAvg, nMotorSum=0, 0, 0
    #fan list
    fanList=[]
    fanTimeList=[]
    fanIntList=[]
    nFanCount, nFanAvg, nFanSum=0, 0, 0

    nTotal=0
    aList=powerList
    i=0
    for a in aList:
        nT1=int(a/CONST_POWER_DIVIDNUM)*CONST_POWER_DIVIDNUM
        if a>=CONST_MOTOR_THRESHOLD:
            motorList.append(a)
            motorTimeList.append(timeList[i])
            nMotorSum+=a
            motorIntList.append(nT1)
            nMotorCount+=1
        if a <=CONST_FAN_THRESHOLD and a >0:
            fanList.append(a)
            fanTimeList.append(timeList[i])
            nFanSum+=a
            fanIntList.append(nT1)
            nFanCount+=1
        nTotal+=1
        i+=1
    if nMotorCount>0:
        nMotorAvg=int(nMotorSum/nMotorCount)
        powerDericative, aPowerDericativeList, aPowerDericativeTimeList=calDerivative(motorList,motorTimeList, nMotorAvg, nMotorCount)

        set1=calPopNum(motorIntList)
        set2=calMotorDist(set1)
        set3=calStDevAvg(motorList)
        result=set2
        if nFanCount>0:
            nFanAvg=int(nFanSum/nFanCount)
            set4=calPopNum(fanList)
            #set5=calMotorDist(set4)
            #set6=calStDevAvg(fanList)
            result["fanAvg"]=set4["avg"]
            result["fanCount"]=set4["count"]
        result["avg"]=set1["avg"]
        result["total"]=nTotal
        result["stDev"]=set3["stDev"]
        stDev=result["stDev"]
        result["dericative"]=powerDericative
        if nMotorCount>CONST_MININUM_NUM:
            
            if "fanAvg" in result:
                nT1=int(result["fanCount"]/result["count"]*100)
                nT2=result["fanAvg"]
                nT3=result["avg"]
            else:
                nT1=0
                nT2=0
                nT3=0
            if nT1>CONST_FANCOUNT_THRESHOLD or ( nT2>CONST_FANPOWER_THRESHOLD and nT3>nT2):
                if powerDericative > CONST_DERICATIVE_THRESHOLD:
                    result["dericativeType"]="BIANPIN"
                else:
                    result["dericativeType"]="DINGPIN"
            else:
                result["dericativeType"]="KG"
        else:
            result["dericativeType"]="TOOSHORT"
        if stDev>CONST_STDEV_THRESHOLD:
            result["stDevType"]="BIANPIN"
        else:
            result["stDevType"]="DINGPIN"
    else:
        aPowerDericativeList=[]
        aPowerDericativeTimeList=[]
    return result, aPowerDericativeList, aPowerDericativeTimeList


def anaACTypeByDev(devID, devSummarySet):
    rtn, result=0, {}
    pList={"P0":0,"P1":0, "P2":0, "P3":0, "P4":0,"P5":0,"P6":0, "P7":0, "P8":0, "P9":0, "P10":0}
    try:
        result["devID"]=devID
        maxP=devSummarySet["max"]
        maxPower=devSummarySet["motorPower"]
        motorPowerAvg=devSummarySet["motorPowerAvg"]
        KGHWCount=devSummarySet["KGHWCount"]
        popName=devSummarySet["popName"]
        result["maxP"]=maxP
        result["maxPower"]=maxPower
        result["motorPowerAvg"]=motorPowerAvg
        if popName in ["P9", "P10"]:
            pHigh=devSummarySet["P8"]+devSummarySet["P9"]+devSummarySet["P10"]
            pMid=devSummarySet["P5"]+devSummarySet["P6"]+devSummarySet["P7"]
            plow=devSummarySet["P2"]+devSummarySet["P3"]+devSummarySet["P4"]
        elif popName in ["P7","P8"]:
            pHigh=devSummarySet["P7"]+devSummarySet["P8"]+devSummarySet["P9"]
            pMid=devSummarySet["P4"]+devSummarySet["P5"]+devSummarySet["P6"]
            plow=devSummarySet["P1"]+devSummarySet["P2"]+devSummarySet["P3"]
        elif popName in ["P5", "P6"]:
            pHigh=devSummarySet["P8"]+devSummarySet["P9"]+devSummarySet["P10"]
            pMid=devSummarySet["P5"]+devSummarySet["P6"]+devSummarySet["P7"]
            plow=devSummarySet["P2"]+devSummarySet["P3"]+devSummarySet["P4"]
        else:
            pHigh=devSummarySet["P7"]+devSummarySet["P8"]+devSummarySet["P9"]
            pMid=devSummarySet["P3"]+devSummarySet["P4"]+devSummarySet["P5"]
            plow=devSummarySet["P0"]+devSummarySet["P1"]+devSummarySet["P2"]
        if KGHWCount>CONST_KGHW_THRESHOLD: # KGHW
            result["bigType"]="KGHW"
            devSummarySet["bigType"]="KGHW"
#            if popName in ["P7","P8","P9", "P10"] and pHigh>90:
#                result["ACType"]="DINGPIN"
#            elif popName in ["P5", "P6", "P7", "P8","P9"] and pMid>30:
#                result["ACType"]="BIANPIN"
#            elif popName in ["P1", "P2", "P3", "P4"] and maxP>1500:
#                result["ACType"]="BIANPIN"
#            else:
#                result["ACType"]="NA"
            stDev = devSummarySet["stDev"]
            dericative =  devSummarySet["dericative"]
            if stDev > CONST_BIANPIN_STDEV and dericative>CONST_BIANPIN_DERICATIVE:
                ACType="BIANPIN"
            else:
                ACType="DINGPIN"
                pass
            result["ACType"]=ACType
            devSummarySet["ACType"]=ACType
            set1=getACPowerType(result)
            result=dict(result, **set1)
        else:
            result["bigType"]="KG"
            devSummarySet["bigType"]="KG"
    except:
        rtn=-1
    return rtn, result

#************************************************************************************#
# to Calculate the air codition type, and determine if its status is nomal function: ACEND
#********************"**************************************************************#

def isACInst(inst, option="T"):
    result=-1
    if len(inst)==6:
        if inst[0] in ["0", "1"]:
            try:
                switch=int(inst[0])
                if inst[1] in ["0", "1", "2", "3", "4"]:
                    mode=int(inst[1])
                    temp=int(inst[2:4], 16)+16
                    fan=int(inst[4])
                    dir=int(inst[5])
                    if option=="T":
                        result=temp
                    elif option=="M":
                        result=mode
                    elif option=="F":
                        result=fan
                    elif option =="D":
                        result=dir
                    elif option=="S":
                        result=switch
                    else:
                        result=100
            except:
                result=-2
    return result

#**********************************************************************************#
# to filter the Air Condition power data,  2015/11/6
# condition: power count: 50 at least, power interval :60-150 seconds
#**********************************************************************************#
CONST_AC_POWER_COUNT = 50
CONST_AC_TIMER_MIN=60
CONST_AC_TIMER_MAX=150
CONST_AC_TIMER_OVER=600 # 10 minues 
def filterACPowerData(powerList, timeList):
    result=[]
    newSampleList=[]
    aList=[]
    nCount =0
    nLen=len(powerList)
    if nLen >0:
        prePower=powerList[0]
        preTime=timeList[0]
        for i in range(1, nLen):
            currPower=powerList[i]
            currTime=timeList[i]
#            t=(currTime-preTime).total_seconds()
            t=currTime-preTime
            t=t.days*86400+t.seconds
            if t > CONST_AC_TIMER_MIN and t < CONST_AC_TIMER_MAX:
                aList.append(currPower)
                nCount+=1
            elif t>CONST_AC_TIMER_OVER or i==nLen:
                if nCount>=CONST_AC_POWER_COUNT:
                    result.extend(aList)
                    aNewList=aList[0:CONST_AC_POWER_COUNT]
                    newSampleList.append(aNewList)
                    nCount=0
                    aList=[]
            prePower=currPower
            preTime = currTime
    return result, newSampleList

    
#def main():
#    powerList=[0, 100, 121, 15, 20, 50,  888, 999, 823, 232, 999, 1000, 0, 129, 232, 23, 88, 679, 400, 500, 1000, 1001]
#    set1=anaACType(powerList)
#    print set1
#main()
