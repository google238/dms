# -- coding: utf8 --
import sys
sys.path.insert(0,'..')
from model.data_model import *
import common.common as common

def main():
    daylist = common.getdaylist('20151201','20151222')
    for day in daylist:
        print day
        tablename = 'devpower_detail_' + day
        data_model(tablename).drop()

if __name__ == "__main__":
    main()
