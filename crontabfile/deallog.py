# -- coding: utf8 --
import sys
sys.path.insert(0,'..')
import json
import datetime
from model.data_model import *
from bson.objectid import ObjectId

def main():
    testFlag="ALL"
    print "Begin"
    if testFlag=="ALL":
        # 从日志获得文件，利用logformat.py处理
        time = datetime.datetime.now()
        pre_time = time - datetime.timedelta(days=1)
        a = pre_time.strftime('%Y%m%d')    
        #strT='devlog' + a + '_details.json'
        suffixlist = ['.159','.99']
        for suffix in suffixlist:
            strT = 'devlog.s3001' + a +suffix
            powerFileName=os.path.join('/data/CKR/log/back/', strT)
            powerDataSet=loadJsonData(powerFileName,a)
            os.remove(powerFileName)
    print "End"

# to read the data that powerPrepareData.py generated.
def loadJsonData(fileName, t):
    tablename = 'devpower_log_' + t
    data_model(tablename).addIndex([('devid',1),('time',-1)])
    with open (fileName, "r") as hFile:
        lines=hFile.readlines()
        result=[]
        for l in lines:
        if l == '\n':
            continue
            if not l.startswith('{'):
                continue
            a=json.loads(l)
        print a 
            if a["CMD"]=="3001":
                w = a["socketOut_W"].encode("utf-8")
                w = float('%0.4f'%(float(w)))
                p = int(a["socketOut_P"].encode("utf-8") )
                #dt = a["dateTime"]
                dt = a['postTime']
                #time = dt[0:4]+dt[5:7]+dt[8:10]+dt[11:13]+dt[14:16]+dt[17:19] #+dt[20::]
                time = dt
                print time
                if time > t + '235959':
                    continue
                devID = a["devID"].encode("utf-8")
                if p > 0:
                    insertdata = {'time':time,'devid':devID,'W':w,'P':p}
                    data_model(tablename).insert(insertdata)
                elif p == 0:
                    findone = data_model(tablename).find(conditions={'devid':devID},sort=[('time',-1)],limit=1)
                    if len(findone) == 0 or findone[0]['P']>0: 
                        insertdata = {'time':time,'devid':devID,'W':w,'P':p}
                        data_model(tablename).insert(insertdata)
                    elif findone[0]['P'] == 0:
                        insertdata = {'time':time,'devid':devID,'W':w,'P':-1}
                        data_model(tablename).insert(insertdata)
                    elif findone[0]['P'] < 0:
                        P1 = findone[0]['P']
                        time1 = findone[0]['time']
                        _id = findone[0]['_id']
                        P2 = P1 - 1
                        data_model(tablename).update_set(condition={'_id':ObjectId(_id)},values={'time':time,'P':P2},upsert=True)   
    return result


main()
