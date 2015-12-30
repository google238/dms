#! /usr/bin/env python
#encoding: utf-8

#Filename: powerAnalysisbyML.py  
#Author: Steven Lian
#E-mail: steven.lian@gmail.com  
#Date: 2015-12-3
#Description:   

import sys, os.path, platform
if platform.system() <> 'Linux' :
    sys.path.append("D:\\Stevenlian documents\\0030. Project\\CKR\\bigData")
sys.path.insert(0,'..')
import json
import time, datetime, types
import pymongo
import numpy as np
import machlearning.miscCommon as miscCommon
import machlearning.bigDataCommon as bigDataCommon

from sklearn.cluster import KMeans,MiniBatchKMeans
from sklearn.cluster import MeanShift, estimate_bandwidth


class readConfig:
    def __init__(self, fileName):
        self.devList=[]
        self.devCount=0
        self.devSet={}
        with open(fileName, "r") as hFile:
            lineList= hFile.readlines()
            for a in lineList:
                strT=a.strip()
                set1=json.loads(strT)
                self.devList.append(set1)
                devID=set1["devID"]
                if devID not in self.devSet:
                    self.devSet[devID]=set1
                self.devCount+=1
            
  
def drawSavePict(aPower, aTime, devType={}, extName=""):
    if devType<>{}:
        devID=devType["devID"]
    else:
        devID="None"
    if len(aPower)<1:
        return -1
    nLen=len(aPower)
    firstTime=aTime[0]
    lastTime=aTime[-1]
    timeRange=lastTime-firstTime
    dpiSize=72
    high = 8
    width = int(nLen/dpiSize)*4+high
    if width> 300:
        width=300
    fig=plt.figure(figsize=(width,high), dpi=dpiSize,edgecolor="k")
    axes = plt.subplot(111)  
    axes.cla()    #清空坐标轴内的所有内容
    #指定图形的字体  
    font = {'family' : 'serif',  
        'color'  : 'darkred',  
        'weight' : 'normal',  
        'size'   : 14,  
        }  
    ax = plt.gca()
    #fig, ax = plt.subplots()
    ax.autoscale_view()

    ax.xaxis.reset_ticks()
    #设置label  
    ax.set_ylabel('Power(w)',fontdict=font)  
    ax.set_xlabel('Time',fontdict=font) 
    #设置title  
    if "bigType" in devType:
        titleStr=str(devID) + "_"+devType["bigType"]
    else:
        titleStr=str(devID) 
    if "ACType" in devType:
        titleStr+="_ac_"+devType["ACType"]
    if "dericativeType" in devType:
        titleStr+="_de_"+devType["dericativeType"]
    if "dericative" in devType:
        titleStr+="_"+str(devType["dericative"])
    if "stDevType" in devType:
        titleStr+="_st_"+devType["stDevType"]
    if "powerAlias" in devType:
        titleStr+="_"+devType["powerAlias"]

    plt.title(titleStr)  


    if timeRange > datetime.timedelta(days = 1):
        ax.xaxis.set_major_locator(dates.DayLocator(bymonthday=range(1,32), interval=1))
        ax.xaxis.set_major_formatter(dates.DateFormatter('%Y-%m-%d'))
    else:
        ax.xaxis.set_major_locator(dates.HourLocator(byhour=range(0,24,2)))
        ax.xaxis.set_major_formatter(dates.DateFormatter('%H:%M'))
    
    ax.xaxis.grid(True)
    
    ax.plot_date(aTime, aPower, "-")
    #ax.plot(aTime, aPower, '-')
    #ax.fmt_xdata = DateFormatter('%Y-%m-%d')
    #fig.autofmt_xdate()
    plt.setp(ax.get_xticklabels(), rotation='vertical', fontsize=14)
    #ax.tick_params(axis='both', which='major', labelsize=10)
    #ax.tick_params(axis='both', which='minor', labelsize=8)
    figName=titleStr+extName+'.png'
    figName=os.path.join(outputImgFileDir, figName)
    plt.savefig(figName, dpi = dpiSize, bbox_inches='tight')

#    plt.show()
    plt.clf()#清除图形  
    #plt.figure()
    plt.close("all")
    #plt.savefig(path +"node.png", dpi = 300, bbox_inches='tight')


#    pl.plot(aTime, aPower)
#    title=str(devID)
#    pl.title(str(devID))
#    pl.xlabel("Time")
#    pl.ylabel("Power(w)")
#    
#    pl.show()
    pass
    


def drawSavePictByDate(aPower, aTime, devType={}, extName=""):
    if devType<>{}:
        devID=devType["devID"]
    else:
        devID="None"
    if len(aPower)<1:
        return -1
    nLen=len(aPower)
    firstTime=aTime[0]
    lastTime=aTime[-1]
    timeRange=lastTime-firstTime
    dpiSize=72
    high = 8
    width = int(nLen/dpiSize)*4+high
    if width> 300:
        width=300
    fig=plt.figure(figsize=(width,high), dpi=dpiSize,edgecolor="k")
    axes = plt.subplot(111)  
    axes.cla()    #清空坐标轴内的所有内容
    #指定图形的字体  
    font = {'family' : 'serif',  
        'color'  : 'darkred',  
        'weight' : 'normal',  
        'size'   : 14,  
        }  
    ax = plt.gca()
    #fig, ax = plt.subplots()
    ax.autoscale_view()

    ax.xaxis.reset_ticks()
    #设置label  
    ax.set_ylabel('Power(w)',fontdict=font)  
    ax.set_xlabel('Time',fontdict=font) 
    #设置title  
    titleStr=str(devID)  
    plt.title(titleStr)  


    if timeRange > datetime.timedelta(days = 1):
        ax.xaxis.set_major_locator(dates.DayLocator(bymonthday=range(1,32), interval=1))
        ax.xaxis.set_major_formatter(dates.DateFormatter('%Y-%m-%d'))
    else:
        ax.xaxis.set_major_locator(dates.HourLocator(byhour=range(0,24,2)))
        ax.xaxis.set_major_formatter(dates.DateFormatter('%H:%M'))
    
    ax.xaxis.grid(True)
    
    ax.plot_date(aTime, aPower, "-")
    #ax.plot(aTime, aPower, '-')
    #ax.fmt_xdata = DateFormatter('%Y-%m-%d')
    #fig.autofmt_xdate()
    plt.setp(ax.get_xticklabels(), rotation='vertical', fontsize=14)
    #ax.tick_params(axis='both', which='major', labelsize=10)
    #ax.tick_params(axis='both', which='minor', labelsize=8)
    figName=devID+'.png'
    figName=os.path.join(outputImgFileDir, figName)
    plt.savefig(figName, dpi = dpiSize, bbox_inches='tight')

#    plt.show()
    plt.clf()#清除图形  
    #plt.savefig(path +"node.png", dpi = 300, bbox_inches='tight')


#    pl.plot(aTime, aPower)
#    title=str(devID)
#    pl.title(str(devID))
#    pl.xlabel("Time")
#    pl.ylabel("Power(w)")
#    
#    pl.show()
    pass
    

def calStartEndDateList(startYMDHM, endYMDHM, nDays):
    result=[]
    nLoop=True
    if len(startYMDHM)<=12:
        startYMDHM+="00"
    if len(endYMDHM)<=12:
        endYMDHM+="00"
    strStart=startYMDHM
    while nLoop:
        aList=[]
        aList.append(strStart)
        t=miscCommon.addTime(strStart, nDays*86400) # 24*60*60=86400
        if t>endYMDHM:
            t=endYMDHM
            nLoop=False
        aList.append(t)
        strStart=t
        result.append(aList)
    return result

def saveData2Local(devList, nDuration):
    result=[]
    global db
    global t_powershowgrid
    global t_poweranalysis
    global t_actypeana10
    global fileDir, outputListDir,devResultExtName,  devMidSetExtName
    
    try:
        nDevNum=0
        for d in devList:
            devID=d["devID"]
            startHM=d["timeBegin"][0:2]+d["timeBegin"][3:5]
            endHM=d["timeEnd"][0:2]+d["timeEnd"][3:5]
            startYMD=d["dateBegin"]
            startYMDHM=startYMD+startHM
            endYMD=d["dateEnd"]
            endYMDHM=endYMD+endHM
            val=d["val"]
            alias=d["alias"]
            memo=d["memo"]
            startEndList=calStartEndDateList(startYMDHM, endYMDHM, nDuration)
            #devID="321501275002078" # debug
            #rows=db[t_powershowgrid].find()
            #rows=db[t_powershowgrid].find({"devid":devID, "starttime":{$gt:startTime}})
            for st in startEndList:
                coditionDict={"devid":devID, "starttime":{"$gt":st[0], "$lte":st[1]}}
                #columnDict={}
                #rows=db[t_powershowgrid].find(coditionDict, columnDict, skip=0, limit=0)
                #rows=db[t_powershowgrid].find(coditionDict).sort("starttime")
                rows=db[t_powershowgrid].find(coditionDict)
                
                devResultList=[]
                devResultCount=0
                startTime, endTime="5000", ""
                if _writeFileFlag==True:
                    strT="devID"+"\t"+"datetime"+"\t"+"Power"+"\n"
                    hFile.write(strT)
                tST=""
                tET=""
                for a in rows:
                    tST=a["starttime"]
                    tET=a["endtime"]
                    if _displayFlag==True:
                        print devID+"_"+tST
                    if startTime>tST:
                        startTime=tST
                    if endTime<tET:
                        endTime=tET
                    for r in a["result"]:
                        devResultList.append(r)
                        devResultCount+=1
                nDevNum+=1
                _id=devID+"_"+st[0]+":"+st[1]
                print "No:",nDevNum,"devID:",_id, " count:", devResultCount
                if devResultCount>0:
                    strT=devID+devResultExtName
                    fileName=os.path.join(outputListDir, strT)
                    miscCommon.saveJsonData(fileName, devResultList)
                    strT=devID+devMidSetExtName
                    midSet  = bigDataCommon.transPowerUsageData(devResultList)
    
                    midSet.pop("powerTimeList")
    
                    fileName=os.path.join(outputListDir, strT)
                    miscCommon.saveJsonData(fileName, midSet)
                    result.append(devID)
    except Exception as e:
        print "ERROR:read/save data", devID,  str(e)
    return result

def calLabelPercentage(aList):
    result={}
    set1={}
    count=0
    for a in aList:
        label=str(a)
        if label not in set1:
            set1[label]=1
        else:
            set1[label]+=1
        count+=1
    set2={}
    for a in set1:
        nT1=set1[a]
        set2[a]=float(nT1)/count
    result["count"]=set1
    result["percentage"]=set2
    return result

def calMeansCluster(X, clusterNum):
    labelList=[]
    result={}
    maxP=X.max()
    divide=float(maxP+1)/clusterNum
    set1={}
    summarySet={}
    for i in range(clusterNum):
        set1[str(i)]=0
        summarySet[str(i)]=0.0
    count=0
    for a in X:
        if a==0:
            label=0
        else:
            nT1=a/divide
            nT2=int(nT1)
            if nT2==0:
                nT2=1
            elif nT2>=clusterNum:
                nT2=clusterNum
            label=nT2
        set1[str(label)]+=1
        summarySet[str(label)]+=float(a)
        count+=1
        labelList.append(label)

    set2={}
    aList=[]
    for a in set1:
        nT1=set1[a]
        set2[a]=float(nT1)/count
        if nT1>0:
            tList=[summarySet[a]/nT1]
            aList.append(tList)
    result["count"]=set1
    result["percentage"]=set2
    result["centers"]=aList
        
    return labelList, result

def testMeanShift(dataList, minPowerCount,powerBandWidth):
    result=[]
    global testShapeFlag
    global fileDir
    global fileDir, outputListDir,devResultExtName,  devMidSetExtName, devMidSetLabelExtName
    minValidPowerCount=100
    for devID in dataList:
        try:
            strT=devID+devMidSetExtName
            fileName=os.path.join(outputListDir, strT)
            midSet=miscCommon.loadJsonData(fileName)
            midSet=midSet[0]
            powerCount=midSet["powerCount"]
            if powerCount < minPowerCount:
                continue
            powerList=midSet["powerList"]
            # shape the data
            if testShapeFlag>1:
                i=0
                for a in powerList:
                    if a>0:
                        a=int(a/testShapeFlag)*testShapeFlag
                        powerList[i]=a
                    i+=1
            # filter all 0 power data
            aList=[]
            aCount=0
            for a in powerList:
                if a>0:
                    aList.append(a)
                    aCount+=1
            if aCount<minValidPowerCount:
                continue
            #prepare data
#            X=np.array(powerList).reshape((powerCount, 1))
            X=np.array(aList).reshape((powerCount, 1))
            maxPower=X.max()
            minPower=X.min()
            midSet["maxPower"]=int(maxPower)
            midSet["minPower"]=int(minPower)
            
            
            # mean shift training
#            bandwidth = estimate_bandwidth(X, quantile=0.2, n_samples=500)
            bandwidth = powerBandWidth
            ms = MeanShift(bandwidth=bandwidth, bin_seeding=True)
            ms.fit(X)
            msLabels = ms.labels_
            msClusterCenters = ms.cluster_centers_
            msLabelsUnique = np.unique(msLabels)
            msNClusters = len(msLabelsUnique)
            msLabelPercentage=calLabelPercentage(msLabels)
            # save data
            midSet["msLabel"]=msLabels.tolist()
            midSet["msClusterCount"]=msNClusters
            midSet["msLabelPercentage"]=msLabelPercentage
            midSet["msClusterCenters"]=msClusterCenters.tolist()
            
            # save data
            strT=devID+devMidSetLabelExtName
            fileName=os.path.join(outputListDir, strT)
            miscCommon.saveJsonData(fileName, midSet)
            set1={}
            set1["devID"]=devID
            set1["count"]=powerCount
            set1["msClusterCount"]=midSet["msClusterCount"]
            set1["msClusterCenters"]=midSet["msClusterCenters"]
            set1["msLabelPercentage"]=midSet["msLabelPercentage"]
            result.append(set1)
            print "OK:", str(set1["msClusterCount"]).ljust(6), str(devID).ljust(24), str(powerCount).ljust(10)
        except Exception as e:
            print "ERROR:", str(devID), powerCount,  str(e)
            pass
    return result

def testMeanShiftKMeans(dataList):
    result=[]
    global testShapeFlag
    global fileDir
    global fileDir, outputListDir,devResultExtName,  devMidSetExtName, devMidSetLabelExtName
    KMeansClusterNum=10
    minPowerCount=1000
    powerBandWidth=100
    for devID in dataList:
        try:
            strT=devID+devMidSetExtName
            fileName=os.path.join(outputListDir, strT)
            midSet=miscCommon.loadJsonData(fileName)
            midSet=midSet[0]
            powerCount=midSet["powerCount"]
            if powerCount < minPowerCount:
                continue
            powerList=midSet["powerList"]
            # shape the data
            if testShapeFlag>1:
                i=0
                for a in powerList:
                    if a>0:
                        a=int(a/testShapeFlag)*testShapeFlag
                        powerList[i]=a
                    i+=1

            #prepare data
            X=np.array(powerList).reshape((powerCount, 1))
            maxPower=X.max()
            minPower=X.min()
            midSet["maxPower"]=int(maxPower)
            midSet["minPower"]=int(minPower)
            
            # cal stand split
            stLabels, stSet=calMeansCluster(X, KMeansClusterNum)
            # save data
            midSet["stLabel"]=stLabels
            midSet["stClusterCount"]=KMeansClusterNum
            midSet["stLabelPercentage"]={}
            midSet["stLabelPercentage"]["count"]=stSet["count"]
            midSet["stLabelPercentage"]["percentage"]=stSet["percentage"]
            midSet["stClusterCenters"]=stSet["centers"]
            
            # mean shift training
#            bandwidth = estimate_bandwidth(X, quantile=0.2, n_samples=500)
            bandwidth = powerBandWidth
            ms = MeanShift(bandwidth=bandwidth, bin_seeding=True)
            ms.fit(X)
            msLabels = ms.labels_
            msClusterCenters = ms.cluster_centers_
            msLabelsUnique = np.unique(msLabels)
            msNClusters = len(msLabelsUnique)
            msLabelPercentage=calLabelPercentage(msLabels)
            # save data
            midSet["msLabel"]=msLabels.tolist()
            midSet["msClusterCount"]=msNClusters
            midSet["msLabelPercentage"]=msLabelPercentage
            midSet["msClusterCenters"]=msClusterCenters.tolist()
            
            #Kmeans training
            km = KMeans(n_clusters = KMeansClusterNum)
            km.fit(X)

            kmLabels = km.labels_
            kmClusterCenters = km.cluster_centers_
            kmLabelsUnique = np.unique(kmLabels)
            kmNClusters = len(kmLabelsUnique)
            kmLabelPercentage=calLabelPercentage(kmLabels)

            # save data
            midSet["kmLabel"]=kmLabels.tolist()
            midSet["kmLabelPercentage"]=kmLabelPercentage
            midSet["kmClusterCount"]=kmNClusters
            midSet["kmClusterCenters"]=kmClusterCenters.tolist()

            strT=devID+devMidSetLabelExtName
            fileName=os.path.join(outputListDir, strT)
            miscCommon.saveJsonData(fileName, midSet)
            set1={}
            set1["devID"]=devID
            set1["count"]=powerCount
            set1["stClusterCount"]=midSet["stClusterCount"]
            set1["stClusterCenters"]=midSet["stClusterCenters"]
            set1["stLabelPercentage"]=midSet["stLabelPercentage"]
            set1["msClusterCount"]=midSet["msClusterCount"]
            set1["msClusterCenters"]=midSet["msClusterCenters"]
            set1["msLabelPercentage"]=midSet["msLabelPercentage"]
            set1["kmClusterCount"]=midSet["kmClusterCount"]
            set1["kmClusterCenters"]=midSet["kmClusterCenters"]
            set1["kmLabelPercentage"]=midSet["kmLabelPercentage"]
            result.append(set1)
            print "OK:", str(set1["msClusterCount"]).ljust(6), str(devID).ljust(24), str(powerCount).ljust(10)
        except Exception as e:
            print "ERROR:", str(devID), powerCount,  str(e)
            pass
    return result

   
def linkDevData2MLData(devSet, msList):
    result = []
    labelSummary={}; labelSummary2={}
    for msData in msList:
        msDevID=msData["devID"]
        if msDevID not in devSet:
            continue
        devData=devSet[msDevID]
        devID=devData["devID"]
        if "param1" in devData:
            devTypeName=devData["param1"]
        else:
            devTypeName=devData["memo"]
        if "param2" in devData:
            devTypeMemo=devData["param2"]
        else:
            devTypeMemo=""
        if "param3" in devData:
            devTypeLabel=devData["param3"]
        else:
            devTypeLabel=""
        msData["devTypeLabel"]=devTypeLabel
        msData["devTypeMemo"]=devTypeMemo
        msData["typeName"]=devTypeName
        if devTypeLabel not in labelSummary:
            labelSummary[devTypeLabel]={"clusterList":[], "devIDList":[],"dataList":[] }
        labelSummary[devTypeLabel]["devIDList"].append(devID)
        labelSummary[devTypeLabel]["clusterList"].append(msData["msClusterCount"])
        labelSummary[devTypeLabel]["dataList"].append(msData)

        msClusterCount=msData["msClusterCount"]
        nLabel=str(msClusterCount)
        if nLabel not in labelSummary2:
            labelSummary2[nLabel]={"clusterList":[], "devIDList":[],"dataList":[] }
        labelSummary2[nLabel]["devIDList"].append(devID)
        labelSummary2[nLabel]["clusterList"].append(msData["msClusterCount"])
        labelSummary2[nLabel]["dataList"].append(msData)
            
        pass
    return labelSummary, labelSummary2

    
def write2summaryfile(labelSummary, labelSummary2):
    strT="labelsummary.txt"
    fileName=os.path.join(fileDir, strT)
    with open (fileName, "w") as hFile:
        # mean shift result summary
        strT="*********************************\n"
        hFile.write(strT)
        strT="* mean shift result summary *\n"
        hFile.write(strT)
        strT="*********************************\n"
        hFile.write(strT)
        for a in labelSummary:
            strT=str(a)+":"+"\n"
            hFile.write(strT)
            strT="----------\n"
            hFile.write(strT)
#            dataList=sorted(labelSummary[a]["clusterList"])
            dataList=set(labelSummary[a]["clusterList"])
            strT=""
            for b in dataList:
                strT+=str(b)+"\t"
            strT+="\n"
            hFile.write(strT)
            pass
        strT="\n"
        hFile.write(strT)

        # mean shift result details
        strT="*********************************\n"
        hFile.write(strT)
        strT="* mean shift result details *\n"
        hFile.write(strT)
        strT="*********************************\n"
        hFile.write(strT)
        for a in labelSummary:
            strT=str(a)+":"+"\n"
            hFile.write(strT)
            strT="----------\n"
            hFile.write(strT)
#            dataList=sorted(labelSummary[a]["clusterList"])
            dataList=labelSummary[a]["dataList"]
            strT=""
            for b in dataList:
                strT=str(b["devID"])+"\t"
                centers=b["msClusterCenters"]
                aList=[]
                for c in centers:
                    aList.append(int(c[0]))
                aList.sort()
                for c in aList:
                    strT+=str(c)+"\t"
                strT+="\n"
                hFile.write(strT)
                pass
            strT="\n"
            hFile.write(strT)            

        # Kmeans  result details
        strT="************************\n"
        hFile.write(strT)
        strT="* Kmeans  result details *\n"
        hFile.write(strT)
        strT="*********************************\n"
        hFile.write(strT)
        for a in labelSummary:
            strT=str(a)+":"+"\n"
            hFile.write(strT)
            strT="----------\n"
            hFile.write(strT)
#            dataList=sorted(labelSummary[a]["clusterList"])
            dataList=labelSummary[a]["dataList"]
            strT=""
            for b in dataList:
                strT=str(b["devID"])+"\t"
                centers=b["kmClusterCenters"]
                aList=[]
                for c in centers:
                    aList.append(int(c[0]))
                aList.sort()
                for c in aList:
                    strT+=str(c)+"\t"
                strT+="\n"
                hFile.write(strT)
                pass
            strT="\n"
            hFile.write(strT)            

        # standard 20 split details
        strT="************************\n"
        hFile.write(strT)
        strT="* standard 20 split details *\n"
        hFile.write(strT)
        strT="*********************************\n"
        hFile.write(strT)
        for a in labelSummary:
            strT=str(a)+":"+"\n"
            hFile.write(strT)
            strT="----------\n"
            hFile.write(strT)
#            dataList=sorted(labelSummary[a]["clusterList"])
            dataList=labelSummary[a]["dataList"]
            strT=""
            for b in dataList:
                strT=str(b["devID"])+"\t"
                centers=b["stClusterCenters"]
                aList=[]
                for c in centers:
                    aList.append(int(c[0]))
                aList.sort()
                for c in aList:
                    strT+=str(c)+"\t"
                strT+="\n"
                hFile.write(strT)
                pass
            strT="\n"
            hFile.write(strT)            

        # standard 20 percentage details
        strT="************************\n"
        hFile.write(strT)
        strT="* standard 20 percentage details *\n"
        hFile.write(strT)
        strT="*********************************\n"
        hFile.write(strT)
        for a in labelSummary:
            strT=str(a)+":"+"\n"
            hFile.write(strT)
            strT="----------\n"
            hFile.write(strT)
#            dataList=sorted(labelSummary[a]["clusterList"])
            dataList=labelSummary[a]["dataList"]
            strT=""
            for b in dataList:
                strT=str(b["devID"])+"\t"
                LabelPercentage=b["stLabelPercentage"]["percentage"]
                aList=[]
                for c in LabelPercentage:
                    aList.append(LabelPercentage[c])
                aList.sort()
                for c in aList:
                    strT+="{0:5.1%}".format(c)+"\t"
                strT+="\n"
                hFile.write(strT)
                pass
            strT="\n"
            hFile.write(strT)            

        # mean shift result details by label count
        strT="*********************************\n"
        hFile.write(strT)
        strT="* mean shift by lablel count*\n"
        hFile.write(strT)
        strT="*********************************\n"
        hFile.write(strT)
        for a in labelSummary2:
            strT=str(a)+":"+"\n"
            hFile.write(strT)
            strT="----------\n"
            hFile.write(strT)
#            dataList=sorted(labelSummary[a]["clusterList"])
            dataList=labelSummary2[a]["dataList"]
            strT=""
            for b in dataList:
                strT=str(b["devID"])+"\t"
                hFile.write(strT)
                strT=b["typeName"].encode("gbk")
                hFile.write(strT)
                strT="\t"+b["devTypeLabel"]+" "
                hFile.write(strT)
                strT=b["devTypeMemo"].encode("gbk")
                hFile.write(strT)
                hFile.write("\t")
                strT="\n\t"
                hFile.write(strT)
                centers=b["msClusterCenters"]
                percentage=b["msLabelPercentage"]["percentage"]
                aList=[]
                for c in centers:
                    aList.append(int(c[0]))
                aList.sort()
                strT=""
                for c in aList:
                    strT+=str(c)+"\t"
                strT+="\n"
                hFile.write(strT)
                
                aList=[]
                i=0
                for c in centers:
                    tList=[]
                    tList.append(int(c[0]))
                    nT1="{0:5.2%}".format(percentage[str(i)])
                    tList.append(nT1)
                    aList.append(tList)
                    i+=1
                strT=""
                for c in aList:
                    strT+=str(c)+"\t"
                strT+="\n\n"
                hFile.write(strT)            
                pass
            strT="\n"
            hFile.write(strT)            

def filterLabelSummary(labelSummary, minPercent):
    set1={}
    for a in labelSummary:
        dataList=labelSummary[a]["dataList"]
        devIDList=labelSummary[a]["devIDList"]
        k=0
        for data in dataList:
            devID=devIDList[k]
            msClusterCenters=data["msClusterCenters"]
            msLabelPercentage=data["msLabelPercentage"]["percentage"]
            nLen=len(msLabelPercentage)
            newCenters=[]
            newPercentage={}
            nCount=0
            for i in range(nLen):
                label=str(i)
                nT1=msLabelPercentage[label]
                if nT1<minPercent:
                    continue
                newCenters.append(msClusterCenters[i])
                newLabel=str(nCount)
                newPercentage[newLabel]=nT1
                nCount+=1
                pass
            newLabel=str(nCount)
            if newLabel not in set1:
                set1[newLabel]={"dataList":[], "devIDList":[]}
            set2={}
            set2["devID"]=devID
            set2["devTypeLabel"]=data["devTypeLabel"]
            set2["devTypeMemo"]=data["devTypeMemo"]
            set2["msClusterCenters"]=newCenters
            set2["msLabelPercentage"]={}
            set2["msLabelPercentage"]["percentage"]=newPercentage
            set2["msLabelPercentage"]["count"]=nCount 
            set2["typeName"] = data["typeName"]     
            set1[newLabel]["dataList"].append(set2)
            set1[newLabel]["devIDList"].append(devID)
                
            k+=1
    return set1

    
def write2meanshiftfile(labelSummary, labelSummary2):
    currTime=miscCommon.getNow()
    strT="msResult_"+currTime.YMDHMS+".txt"
    fileName=os.path.join(fileDir, strT)
    with open (fileName, "w") as hFile:
        # mean shift result details by label count
        strT="*********************************\n"
        hFile.write(strT)
        strT="* mean shift by lablel count*\n"
        hFile.write(strT)
        strT="*********************************\n"
        hFile.write(strT)
        for a in labelSummary2:
            strT = "Label:"+str(a)+":"+"\n"
            hFile.write(strT)
            strT="----------\n"
            hFile.write(strT)
#            dataList=sorted(labelSummary[a]["clusterList"])
            dataList=labelSummary2[a]["dataList"]
            strT=""
            for b in dataList:
                strT=str(b["devID"])+"\t"
                hFile.write(strT)
                strT=b["typeName"].encode("gbk")
                hFile.write(strT)
                strT="\t"+b["devTypeLabel"]+" "
                hFile.write(strT)
                strT=b["devTypeMemo"].encode("gbk")
                hFile.write(strT)
                hFile.write("\t")
                strT="\n\t"
                hFile.write(strT)
                centers=b["msClusterCenters"]
                percentage=b["msLabelPercentage"]["percentage"]
                aList=[]
                for c in centers:
                    aList.append(int(c[0]))
                aList.sort()
                strT=""
                for c in aList:
                    strT+=str(c)+"\t"
                strT+="\n"
                hFile.write(strT)
                
                aList=[]
                i=0
                for c in centers:
                    tList=[]
                    tList.append(int(c[0]))
                    nT1="{0:5.2%}".format(percentage[str(i)])
                    tList.append(nT1)
                    aList.append(tList)
                    i+=1
                strT="\t"
                for c in aList:
                    strT+=str(c)+"\t"
                strT+="\n\n"
                hFile.write(strT)            
                pass
            strT="\n"
            hFile.write(strT)            
        
        minPercent=0.01
        labelSummary2=filterLabelSummary(labelSummary2, minPercent)
        
        strT="*********************************\n"
        hFile.write(strT)
        for a in labelSummary2:
            strT = "Label:"+str(a)+":"+"\n"
            hFile.write(strT)
            strT="----------\n"
            hFile.write(strT)
#            dataList=sorted(labelSummary[a]["clusterList"])
            dataList=labelSummary2[a]["dataList"]
            strT=""
            for b in dataList:
                strT=str(b["devID"])+"\t"
                hFile.write(strT)
                strT=b["typeName"].encode("gbk")
                hFile.write(strT)
                strT="\t"+b["devTypeLabel"]+" "
                hFile.write(strT)
                strT=b["devTypeMemo"].encode("gbk")
                hFile.write(strT)
                hFile.write("\t")
                strT="\n\t"
                hFile.write(strT)
                centers=b["msClusterCenters"]
                percentage=b["msLabelPercentage"]["percentage"]
                
                aList=[]
                i=0
                for c in centers:
                    per=percentage[str(i)]
                    if per<minPercent:
                        continue
                    aList.append(int(c[0]))
                    i+=1
                aList.sort()
                strT=""
                for c in aList:
                    strT+=str(c)+"\t"
                strT+="\n"
                hFile.write(strT)
                
                aList=[]
                i=0
                for c in centers:
                    per=percentage[str(i)]
                    if per<minPercent:
                        continue
                    tList=[]
                    tList.append(int(c[0]))
                    nT1="{0:5.2%}".format(percentage[str(i)])
                    tList.append(nT1)
                    aList.append(tList)
                    i+=1
                strT="\t"
                for c in aList:
                    strT+=str(c)+"\t"
                strT+="\n\n"
                hFile.write(strT)            
                pass
            strT="\n"
            hFile.write(strT)            








#************************************************************************************#
# to define the global var
#************************************************************************************#
testFlag="analysis" #,all, train, predict

testFlagAllList=["all"]
testFlagTrainList=["all","train"]
testFlagAnalysisList=["all","train","analysis",]
testFlagPredictList=["all","train","analysis","predict"]
testShapeFlag=1 # default ==1, 


dbName="dmsdata" # database name
t_powershowgrid="powershowgrid" # collection name，原始数据
t_poweranalysis="poweranalysis" # collection name，中间存储数据
t_powerresult="sl_powerResult" # collection name，所选设备和给定时间的电量结果
t_powerresult10="sl_powerResult10" # collection name，所选设备和给定时间的电量结果
t_actypeanalysis="sl_ACtypeAnalysis" # collection name，空调型号判断结果
t_actypeana10="sl_ACtypeAna10" # collection name，空调型号判断结果
# flags
_savePictFlag=False
_writeFileFlag=False
_displayFlag=False

if _savePictFlag==True:
    #import pylab as pl
    import matplotlib.pyplot as plt
    import matplotlib.dates as dates


#************************************************************************************#
# determine the OS system
#************************************************************************************#

if platform.system() == 'Linux' :
    client = pymongo.MongoClient("10.10.160.75", 28088)# 27017 is the default mongodb server port
    fileDir="/data/CKR/src/dms/file/"
else:
    #client = pymongo.MongoClient("180.150.187.99", 28088)
#    client = pymongo.MongoClient("118.192.76.159", 28088)
    #client = pymongo.MongoClient("180.150.177.70", 28088)
    fileDir="\\data\\powerAnalysis\\"

# connect to defined database
if testFlag in testFlagAllList:
    db = client[dbName]

configFileName=os.path.join(fileDir, "powerList1.conf")
tempFileName=os.path.join(fileDir, "powerHandle.conf")
outputListDir=os.path.join(fileDir,"allpowerdata")
outputImgFileDir=os.path.join(fileDir,"img")
devResultExtName="devResult.json"
devMidSetExtName="devMidSet.json"
devMidSetLabelExtName="devMidSetWithLabel.json"

#define Global monitor devie ID List



def main():
    global fileDir
    print "Begin"
    beginTime=miscCommon.getNow()
    print beginTime.YMDHMS
    
    devData = readConfig(configFileName)
    print "data Count:", devData.devCount
    
    argvList=sys.argv
    
    if len(argvList)>1:
        argvOption=argvList[1].lower()
    else:
        argvOption=""
    
    if argvOption=="h":
        print 
        print "Usage: python powerAnalysis.py"
        print "       ", "h: help"
        print "       ", "p: save picture"
        print 
        return 0
    elif argvOption=="p":
        _savePictFlag=True
    
    if testFlag in testFlagAllList:
        days=1000
        try:
#            dataList=devData.devList[93::]
            dataList=devData.devList
            devIDList=saveData2Local(dataList, days)
        except Exception as e:
            print "ERROR:save file", str(e)
        strT="devIDList.json"
        fileName=os.path.join(fileDir, strT)
        miscCommon.saveJsonData(fileName, devIDList)
    '''
    minPowerCount=10000
    powerBandWidth=100
    # train 
    if testFlag in testFlagTrainList:
        strT="devIDList.json"
        fileName=os.path.join(fileDir, strT)
        devIDList=miscCommon.loadJsonData(fileName)
#        msData=testMeanShiftKMeans(devIDList)
        
        msData=testMeanShift(devIDList, minPowerCount, powerBandWidth)
        strT="devIDMeanShiftList.json"
        fileName=os.path.join(fileDir, strT)
        miscCommon.saveJsonData(fileName, msData)

    # analysis, temp solution
    if testFlag in testFlagAnalysisList:
        strT="devIDMeanShiftList.json"
        fileName=os.path.join(fileDir, strT)
        msData=miscCommon.loadJsonData(fileName)
        dataList=devData.devList
        dataSet=devData.devSet
        labelSummary, labelSummary2=linkDevData2MLData(dataSet, msData)
        strT="devLabelSummary.json"
        fileName=os.path.join(fileDir, strT)
        miscCommon.saveJsonData(fileName, labelSummary)
        strT="devLabelSummary2.json"
        fileName=os.path.join(fileDir, strT)
        miscCommon.saveJsonData(fileName, labelSummary2)
#        write2summaryfile(labelSummary, labelSummary2)
        write2meanshiftfile(labelSummary, labelSummary2)
        pass
        
    '''
    endTime=miscCommon.getNow()
    
    print endTime.YMDHMS
    print endTime.diff(beginTime.now)
    print "End"
   
main()

