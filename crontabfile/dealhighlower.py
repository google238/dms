# -- coding: utf8 --
import sys
sys.path.insert(0,'..')
from model.data_model import *
import common.common as common
from bson.objectid import ObjectId

def main():
    data = data_model('temperature').find(conditions={'time':{'$gt':'201512'}})
    for item in data:
        high = int(item['high'])
        lower = int(item['lower'])
        print lower,high
        if high<lower:
            _id = item['_id']
            data_model('temperature').update_set(condition={'_id':ObjectId(_id)},values={'high':lower,'lower':high},upsert=True) 
            print 'ok'
if __name__ == "__main__":
    main()
