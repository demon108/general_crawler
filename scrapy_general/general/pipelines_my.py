# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/topics/item-pipeline.html

import codecs
import os
import sys
from datetime import datetime
import time
import shutil
import re

#from pymongo import MongoClient

from scrapy import log
from scrapy.exceptions import DropItem
from scrapy.utils.python import unicode_to_str

from items import *
from mxutil import *
from config import DATA_FILES
# from bkdbWrapper import *


# path_par='/home/dy/scrapy_workspace/scrapy_general_bak/data_files'
path_par = DATA_FILES

def unicode_to_gbk(src):
    return unicode_to_str(src,'gbk',errors='ignore')

class GeneralPipeline(object):
    total_cnt = 0
    total = 0
    #dbfile_move_target = '/disk2/list_crawler/output'
    dbfile_move_target = path_par+'/output_eb/'
    dbfile_making_dir = path_par+'/list_crawler/'
    nums_in_eachDBFile = 1000
    _pa_reset_encoding = re.compile(r'charset=([\w-]+)', re.I)
    time_stamp = 0
    back_link_ts = 0
    back_link_fp = False

    def __init__(self):
        self.pid = os.getpid()
        self.time_start = datetime.now()
        #self.conn = MongoClient("192.168.241.8",27017)
        #self.links = self.conn.linkrelativeDB.link

    def _createNewDBFile(self):
        self.time_stamp = time.time()
        db_file_name = "RawDataY_"+str(self.time_stamp)+'_'+str(self.pid)+'.db'
        self.db_file = os.path.join( self.dbfile_making_dir,db_file_name)
        try:
            self.db = BKDB()
            self.db.createDb(self.db_file)
        except:
            log.msg( 'exception in create db',level=log.ERROR)
            sys.exit(-1)

    def open_spider(self,spider):
        self.time_stamp = datetime.now().isoformat()
        self.file = codecs.open("ok_%s_%d.dat"%(time.strftime("%Y%m%d%H%M%S"),os.getpid()),'w','utf-8', errors='ignore')
#         self._createNewDBFile()
        self.back_link_ts = time.mktime(time.strptime(time.strftime("%Y%m%d%H",time.localtime()),"%Y%m%d%H"))
        fn = "back_link_"+time.strftime("%Y%m%d%H")+".dat"
        self.back_link_fp = codecs.open(fn,"w","utf-8",errors='ignore')

    def _writeDBFile(self,item):
        try:
            wpd = TWebPageData()
            if item['encoding'] == 'big5':
                self.db.appendToDb(wpd,item['url'], "", item['content'] )
            else:
                gbk_body_charset = self._pa_reset_encoding.sub('charset=gbk',item['content'])
                #gbk_title = unicode_to_gbk(item['title']) if item['title'] else ' '
                self.db.appendToDb(wpd,item['url'], "",unicode_to_gbk(gbk_body_charset) )
        except:
            print 'wrong url:',item['url']
            info=sys.exc_info()
            print info[0],":",info[1]

    def process_item(self, item, spider):
#         print "---iteme: ",item
#         print "----spider: ",item
        self.total_cnt += 1
        if isinstance(item, PendingItem):
            if not do_url_pattern_filter(item['url']):
                #raise DropItem("BAD_PATTERN_%s" % item['url'])
                return

            #check the next fetch time	
            link_flag = check_link_base(item['url'])
            if not link_flag:
                #raise DropItem("FOUND_IN_LINK_BASE_%s" % item['url'])
                return

#             if check_fetching_list(item['url']):
#                 #raise DropItem("DUP_URL_%s" % item['url'])
#                 return

            #check pending list and fetching list	
            if check_pending_list(item['url'], item['depth']):
                #raise DropItem("DUP_URL_%s" % item['url'])
                return

            add_to_plist(item['url'], item['depth'],link_flag)
        elif isinstance(item, PageMetaItem):
            save_page_meta(item['url'],item['http_code'],item['content'],item['resp_time'])
            remove_pending_list(item['url'])
#             remove_fetching_list(item['url'])
            self.file.write("%s\n" % (item['url']))
            
            #save to RawDB
#             http_code = item['http_code']
#             if http_code >= 200 and http_code < 300:
#                 self.total += 1
#                 try:
#                     if self.total % self.nums_in_eachDBFile == 0:
#                         self.db.closeDb()
#                         if os.path.exists(self.db_file):
#                             shutil.move(self.db_file,self.dbfile_move_target)
#                         else:
#                             err = '+++no_db_file:',self.db_file
#                             print err
#                             log.msg(err,level=log.ERROR)
#                         self._createNewDBFile()
# 
#                     if item['url'] and item['content']:
#                         self._writeDBFile(item)
#                 except:
#                     print '=URL=',item['url'],'=body=',item['content']
#                     info=sys.exc_info()
#                     print info[0],":",info[1]
        elif isinstance(item, LinkItem):
            if time.time() - self.back_link_ts > 3600:
                self.back_link_ts = time.mktime(time.strptime(time.strftime("%Y%m%d%H",time.localtime()),"%Y%m%d%H"))
                self.back_link_fp.close()
                fn = "back_link_"+time.strftime("%Y%m%d%H")+".dat"
                self.back_link_fp = codecs.open(fn,"w","utf-8",errors='ignore')
            self.back_link_fp.write("%s\t%s\t%s\n"%(item['url'],item['src_url'],datetime.now()))
            #raise DropItem("LINK_ITEM_%s" % str(type(item)))
        else:
            raise DropItem("UNKOWN_ITEM_%s" % str(type(item)))
        #return item

    def close_spider(self,spider):
        print 'total_item:%s'%self.total_cnt
        log.msg('time:%s, links: %s'%(self.time_stamp, self.total_cnt),level=log.INFO)
        print 'time:', self.time_stamp, ' ,total link:', self.total_cnt
        time_end = datetime.now()
        f1 = open('total_time.my','w')
        print >> f1, 'total_time: ',time_end - self.time_start
        self.file.close()
        cleanup_util()
        #self.conn.close()
        self.back_link_fp.close()

        #close db and move to the final dir
#         self.db.closeDb()
#         if os.path.exists(self.db_file):
#             shutil.move(self.db_file,self.dbfile_move_target)
#         else:
#             err = '+++no_db_file:',self.db_file
#             print err
#             log.msg(err,level=log.ERROR)

