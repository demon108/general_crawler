import codecs
import os
import redis
import re

PROJECT = os.path.split(os.path.dirname(os.path.realpath(__file__)))[0]
s = 'http://k.autohome.com.cn/111/' 
',_depth0 ,2014-07-30 10:29:03 081851, my_flag_1'

regex1 = re.compile('http://k.autohome.com.cn/\d+/$|http://k.autohome.com.cn/spec/\d+/$')# print regex1.search(s)

class CountSites(object):
    
    def __init__(self):
#         self.redis_db = redis.StrictRedis('127.0.0.1',port=6379)
        self.filename = PROJECT+'/conf/data_073002/response_get.my'
        self.reader = codecs.open(self.filename, 'r', encoding='utf-8', errors='ignore')
        self.sites = []
        self.writer = codecs.open('test_sites', 'a+', encoding='utf-8', errors='ignore')
        self.writer2 = codecs.open('test_sites2', 'a+', encoding='utf-8', errors='ignore')
    def test(self):
        st = 'http://k.autohome.com.cn/spec/18492/view_422200_1.html'
        
    def analysis_sites(self):
        while True:
            line = self.reader.readline()
            if not line:
                break
            site = str(line.split(',')[0]).strip()
            if self.sites.count(site) == 0:
                try:
                    for sit in self.sites:
                        if len(site) >= len(sit):
                            if site.find(sit) != -1:
                                raise 
                        else :
                            if sit.find(site) != -1:
                                raise
                except:
                    continue
            else:
                continue
            self.sites.append(site)
    
    
    def analysis_sites2(self):
        while True:
            line = self.reader.readline()
            if not line:
                break
            site = str(line.split(',')[0]).strip()
            if regex1.search(site):
                self.writer2.write('%s\n'%site)
    
    def write_sites(self):
        for site in self.sites:
            self.writer.write('%s\n'%site)
    
    


if __name__  == '__main__':
    cs = CountSites()
    cs.analysis_sites2()
#     cs.write_sites()
# s1 = 'http://k.autohome.com.cn/110/index_6.html'
# s2 = 'http://k.autohome.com.cn/111/?medalType=1'
# s3 = 'http://k.autohome.com.cn/110/?medalType=2'
# s4 = 'http://k.autohome.com.cn/110/?medalType=1'
# s =  'http://k.autohome.com.cn/110'
# sk = 'http://qq.com'
# print s1.find(s)    
# print s1.find(sk)    
# print s.find(s1)



# li = ['http://k.autohome.com.cn/spec/18492/']
# site = 'http://k.autohome.com.cn/spec/18492/index.html'
# if li.count(site) == 0:
#     print '----1'
#     for sit in li :
#         if len(site) >= len(sit):
#             if site.find(sit) != -1:
#                 print '-----2'
#         else :
#             if sit.find(site) != -1:
#                 print '==3'
