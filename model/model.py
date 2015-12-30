# -- coding: utf8 --
#__author__ = 'michael'

import pymongo
from config.config_default import *
import web

connection = pymongo.MongoClient(serv_name, mongo_port)
db = connection.test1

class model(object):
    _tb = None
    page_size=10
    def __init__(self, tb = None):
        """

        :rtype : object
        """
        self._tb = tb
        self.collection = db

    def map_reduce(self, map, reduce, out):
        return self.collection[self._tb].map_reduce(map,reduce,out)


    def addIndex(self, indexCondition):
        if not indexCondition:
            return
        return self.collection[self._tb].ensure_index(indexCondition)


    def drop(self):
        return self.collection[self._tb].drop()

    def count(self, conditions=None):
        if not conditions:
            conditions = {}
        return self.collection[self._tb].find(conditions).count()

    def find_one(self, conditions=None):
        #注意这里conditions是dict类型
        if not conditions:
            conditions = {}
        if type(conditions) is not dict:
             print 'the type of query isn\'t dict'
             return
        return self.collection[self._tb].find_one(conditions)		

    def find(self, conditions=None, sort=None, limit=None, skip=None, returnq=None):
        """
        :param conditions:
        :param sort:
        sort = []
        db.Account.find().sort("UserName")
        db.Account.find().sort("UserName",pymongo.ASCENDING)
        db.Account.find().sort("UserName",pymongo.DESCENDING)
        db.Account.find().sort([("UserName",pymongo.ASCENDING),("Email",pymongo.DESCENDING)])
        :param limit:
        :param skip:
        :return:
        """
        if not sort:
            sort = []
        if not conditions:
            conditions = {}
        #注意这里conditions是dict类型
        if type(conditions) is not dict:
             print 'the type of query isn\'t dict'
             return

        cursor = self.collection[self._tb].find(conditions,returnq)
        if len(sort) != 0:
            cursor.sort(sort)
        if limit :
            cursor.limit(limit)
        if skip :
            cursor.skip(skip)
        return list(cursor)

    def insert(self, document=None):
        if not document:
            document = {}
        if len(document) == 0 :
            return
        self.collection[self._tb].insert(document)
        return document

    def update_set(self, condition=None, values=None, upsert=False, multi=True):
        """
        "$set"用来指定一个键的值。如果这个键不存在，则创建它。
        :param condition:
        :param values:
        :param upsert:
        如果不存在update的记录，是否插入objNew,true为插入，默认是false，不插入
        :param multi:
        mongodb默认是false,只更新找到的第一条记录，如果这个参数为true,就把按条件查出来多条记录全部更新
        :return:
        """
        if not values:
            values = {}
        if not condition:
            condition = {}
        self.collection[self._tb].update(condition,{"$set":values},upsert=upsert,multi=multi)

    def update_unset(self, condition, values=None, upsert=False, multi=True):
        """
        从文档中移除指定的键
        :param condition:
        :param values:
        :param upsert:
        :param multi:
        :return:
        """
        if not values:
            values = {}
        self.collection[self._tb].update(condition,{"$unset":values},upsert,multi)

    def update_inc(self, condition, values=None, upsert=False, multi=True):
        """
        "$inc"修改器用来增加已有键的值，或者在键不存在时创建一个键。
        "$inc"就是专门来增加（和减少）数字的。
        "$inc"只能用于整数、长整数或双精度浮点数。要是用在其他类型的数据上就会导致操作失败。
        :param condition:
        :param values:
        :param upsert:
        :param multi:
        :return:
        """
        if not values:
            values = {}
        self.collection[self._tb].update(condition,{"$inc":values},upsert,multi)

    def update_setOnInsert(self, condition, values=None, upsert=False, multi=True):
        """

        :param condition:
        :param values:
        :param upsert:
        :param multi:
        :return:
        """
        if not values:
            values = {}
        self.collection[self._tb].update(condition,{"$setOnInsert":values},upsert,multi)

    def update_push(self, condition, values=None, upsert=False, multi=True):
        """
        如果指定的键已经存在，会向已有的数组末尾加入一个元素，要是没有就会创建一个新的数组.
        :param condition:
        :param values:
        :param upsert:
        :param multi:
        :return:
        """
        if not values:
            values = {}
        self.collection[self._tb].update(condition,{"$push":values},upsert,multi)


    def update_pushAll(self, condition, values=None, upsert=False, multi=True):
        """
        同$push,只是一次可以追加多个值到一个数组字段内.
        :param condition:
        :param values:
        :param upsert:
        :param multi:
        :return:
        """
        if not values:
            values = {}
        self.collection[self._tb].update(condition,{"$pushAll":values},upsert,multi)


    def update_pull(self, condition, values=None, upsert=False, multi=True):
        """
        语法：db.collection.update( { field: <query> }, { $pull: { field: <query> } } );
        $pull操作符移除指定字段值为数组，且匹配$pull语句声明的查询条件的所有元素。
        :param condition:
        :param values:
        :param upsert:
        :param multi:
        :return:
        """
        if not values:
            values = {}

        self.collection[self._tb].update(condition,{"$pull":values},upsert,multi)


    def update_pullAll(self, condition, values=None, upsert=False, multi=True):
        """
        语法：db.collection.update( { field: <query> }, { $pull: { field: <query> } } );
        $pull操作符移除指定字段值为数组，且匹配$pull语句声明的查询条件的所有元素。
        :param condition:
        :param values:
        :param upsert:
        :param multi:
        :return:
        """
        if not values:
            values = {}

        self.collection[self._tb].update(condition,{"$pullAll":values},upsert,multi)

    def update_addToSet(self, condition, values=None, upsert=False, multi=True):
        """
        增加一个值到数组内，而且只有当这个值不在数组内才增加
        :param condition:
        :param values:{ "test": {$each : ["111","222"] } }
        :param upsert:
        :param multi:
        :return:
        """
        if not values:
            values = {}
        self.collection[self._tb].update(condition,{"$addToSet":values},upsert,multi)


    def update_pop(self, condition, values=None):
        """
        删除数组内的一个值
        删除最后一个值：{ $pop : { field : 1  } }
        删除第一个值：{ $pop : { field : -1  } }
        :param condition:
        :param values:
        :return:
        """
        if not values:
            values = {}
        self.collection[self._tb].update(condition,{"$pop":values})


    def remove(self, condition=None):
        """
        :param condition:
        if condition is None , will removes all documents from the self._tb collection
        :return:
        """
        if not condition:
            condition = {}
        self.collection[self._tb].remove(condition)

    def table_name(self):
        return self._tb
    
    def page(self,conditions , p=1, total=0):
        Page = []
        page_count = self.page_count(total)

        if p > page_count:
            return Page

        if page_count != 1:
            def link(l):
                
                href = str(l) + '?'
                for key in conditions.keys():
                    href = href + key + '=' + conditions[key] + '&'
                Page.append('<a href="' + href + '">' + str(l) + '</a>')

            if p != 1:
                Page.append('<a href="' + str(p - 1) + '">' + u'<上一页' + '</a>')
            if p > 11:
                for i in range(p - 10, p):
                    link(i)
            else:
                for i in range(1, p):
                    link(i)

            Page.append('<a href="' + str(p) + '"><b>' + str(p) + '</b></a>')

            if p + 10 <= page_count:
                for i in range(p + 1, p + 11):
                    link(i)
            else:
                pass
                for i in range(p + 1, page_count + 1):
                    link(i)

            if p != page_count:
                Page.append('<a href="' + str(p + 1) + '">' + u'下一页>' + '</a>')
        return Page



    def page_count(self, total=0):
        
        if total < self.page_size:
            page_count = 1
        elif total % self.page_size:
            page_count = total / self.page_size + 1
        else:
            page_count = total / self.page_size

        return page_count

    def get_page(self, p, conditions=None):
        if not conditions:
            conditions = {}
        total = self.count(conditions )
        print conditions
        return self.page(conditions, p, total)	#获取分页数据


    def get_page_scroll(self, conditions=None):
        if not conditions:
            conditions = {}
        total = self.count(conditions )
        return self.page_count(total)	#获取分页数据


    def find_page(self, conditions=None, sort=None, pagenum=1):
        #注意这里conditions是dict类型
        if not sort:
            sort = []

        if not conditions:
            conditions = {}

        if type(conditions) is not dict:
            print 'the type of query isn\'t dict'
            return
             
        cursor = self.collection[self._tb].find(conditions)
        if len(sort) != 0:
            cursor.sort(sort)
        if pagenum :
            cursor.limit(self.page_size)
            cursor.skip((pagenum - 1) * self.page_size)
        return list(cursor)
