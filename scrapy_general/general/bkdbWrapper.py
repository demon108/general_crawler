#encoding:utf-8
from ctypes import *
from config import PROJECT

lib = cdll.LoadLibrary(PROJECT+'/conf/libbkdb.so')
class TWebPageData(Structure):
    _fields_ = [("DownDate", c_int),
             ("DataProp", c_uint),
             ("LastMod", c_int),
             ("LastVisit", c_int),
             ("Weight", c_int),
             ("Reserved", c_int),
             ("DataLen", c_int),
             ("UrlPos", c_int),
             ("UrlLen", c_int),
             ("IpAddressPos", c_int),
             ("IpAddressLen", c_int),
             ("HeadPos", c_int),
             ("HeadLen", c_int),
             ("HeadOrgnLen", c_int),
             ("ContentPos", c_int),
             ("ContentLen", c_int),
             ("ContentOrgnLen", c_int),
             ("Digest", c_char*16),
             ("Data", c_char),
        ]
class BKDB(object):
    db =    c_void_p()
    record = c_char_p()
    #cnt = 0
    def __init__(self):
        pass
    
    #appendToDb(wpd,item['url'], "", item['content'] )
    def appendToDb(self,srcData, url, head, content):
        re = lib.appendToDb(self.db, byref(srcData),c_char_p(url), c_char_p(head), c_char_p(content))
        if re== 0:
            #BKDB.cnt += 1
            #print 'appendToDb db ok',str(BKDB.cnt)
            return
        else:
            print 'failed appendToDb db, code: %d'%re
    
    #byref（n）返回的相当于C的指针右值&n，本身没有被分派空间：
    def readRec(self,desData, url, head, content, recno):
        re = lib.readRec(self.db,byref(desData) ,byref(url), byref(head), byref(content), c_int(recno))
        if re== 0:
            print 'readRec db ok'
        else:
            print 'failed readRec db, code: %d'%re

        return re
    def createDb(self,path):
        re = lib.createDb(byref(self.db), path)
        if re== 0:
            #print 'create db ok'
            return
        else:
            print 'failed creat db, code: %d'%re
    def openDb(self,path):
        re = lib.openDb(byref(self.db),path)
        if re== 0:
            #print 'open db ok'
            return
        else:
            print 'failed open db, code: %d'%re
    def appendDb(self, content):
        re = lib.appendDb(self.db, content, len(content))
        if re== 0:
            #print 'appendDb db ok'
            return
        else:
            print 'failed append db, code: %d'%re
    def readDb(self, recNo):
        re = lib.readDb(self.db, byref(self.record),c_int(recNo))
        if re > 0:
            #print 'read db ok'
            return self.record.value
        else:
            print 'failed read db, code: %d'%re
    def syncDb(self):
        re = lib.syncDb(self.db)
        if re== 0:
            #print 'sync db ok'
            return
        else:
            print 'failed sync db, code: %d'%re
    def getRecNum(self):
        re = lib.getRecNum(self.db)
        if re < 0:
            print 'failed getRecNum db, code: %d'%re
        return re
    def closeDb(self):
        re = lib.closeDb(self.db)
        if re== 0:
            #print 'close db ok'
            return
        else:
            print 'failed close db, code: %d'%re
