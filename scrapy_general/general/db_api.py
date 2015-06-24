import re

from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from pymongo.errors import InvalidName

class db_cursor:
    def __init__(self,c):
        self.c = c

    def __iter__(self):
        return self

    def fetchone(self):
        try:
            return self.next()
        except:
            return None

    def next(self):
        return self.c.next()

    def close(self):
        self.c.close()

pattern = "(?P<column>.*?)(?P<op>(>=|>|<=|<|=))(?P<d1>.*)"
re1 = re.compile(pattern)

pattern2 = "(?P<d1>.*)(?P<op>(>=|>|<=|<))(?P<column>.*)(?P<op2>(>=|>|<=|<))(?P<d2>.*)"
re2 = re.compile(pattern2)

#connect to db and return the connection
#   (in facet the database object)
def connect(dsn='localhost:next_raw',user='',password=''):
    if not dsn:
        raise Exception,"dsn is null"

    dns_args = dsn.split(":")
    if len(dns_args) != 2:
        raise Exception, "dsn format error"
    host = dns_args[0]
    db = dns_args[1]

    if not host or not db:
        raise Exception, "dsn format error/host or db is null"

    #basic authentification
    try:
        mongo_client = MongoClient(host,27017)
        conn = mongo_client[db]
    except ConnectionFailure, e:
        raise Exception,e.args[0]
    except InvalidName,e:
        raise Exception,e.args[0]
    return conn

def close(handler):
    handler.connection.close()

def db_read_data(handler, table_name, expression, *column):
    op_map = {">":'$gt',">=":"$gte","<":"$lt","<=":"$lte"}
    #op_map = {">":'$gt',">=":"$gte","<":"$lt","<=":"$lte"}
    op_map2 = {"<":"$gt","<=":"$gte"}


    global re1,re2
    condition = {}
    if expression:
        rst = re2.search(expression)
        if rst:
            data = rst.groupdict()
            op1 = op_map2[data['op'].strip()]
            op2 = op_map[data['op2'].strip()]
            column = data['column'].strip()
            d1 = data['d1'].strip()
            d2 = data['d2'].strip()
            condition = {column:{op1:d1,op2:d2}}
        else:
            rst = re1.search(expression)
            if rst:
                data=rst.groupdict()
                column = data['column'].strip()
                d1 = data['d1'].strip()
                op1_str = data['op'].strip()
                if op1_str == "=":
                    condition = {column:d1}
                else:
                    op1 = op_map2[data['op'].strip()]
                    condition = {column:{op1:d1}}
            else:
                raise Exception, "expression %s is not support"%(expression)

    fields = None
    if len(column)>0:
        for i in column:
            fields[i]=1

    try:
        cur = handler[table_name].find(condition,fields=fields)
        if cur:
            return db_cursor(cur)
        else:
            return None
    except Exception,e:
        raise Exception, e.args[0]

def db_read_data_by_key(handler, table_name, key, *column):
    fields = {"_id":0}
    for i in column:
        fields[i]=1
    return handler[table_name].find_one({"_id":key},fields=fields)

def db_write_data(handler,table_name,key,value_pair,upsert=True):
    if upsert:
        rec = handler[table_name].find_one({"_id":key})
        if rec:
            return 0
            #for k,v in value_pair.iteritems():
            #    rec[k] = v
            #handler[table_name].save(rec)
            #return 0
    new_data = {}
    new_data["_id"] = key
    for k,v in value_pair.iteritems():
        new_data[k] = v
    try:
        handler[table_name].insert(new_data)
    except Exception, e:
        print e
        return -1
    return 0
