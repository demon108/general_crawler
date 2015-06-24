# -*- encoding:utf-8 -*

import codecs
import re
import urlparse
# import time

from config import PATTERN_SITE,PATTERN_DOMAIN
'''
regex1 = 
re.compile('http://k.autohome.com.cn/\d+/$|http://k.autohome.com.cn/spec/\d+/$')
'''
class PatternSys(object):
    
    def __init__(self):
        self.common_white,self.common_black,self.sites_pcre,self.domains_pcre = self.open_pattern_file()
    
    def skip_tag_reader(self,reader):
        try:
            line = reader.readline()
            while True:
                if line.startswith('#'):
                    line = reader.readline()
                elif line.strip()=='\n':
                    line = reader.readline()
                else:
                    break
            line = line.rstrip('\n')
        except StopIteration:
            return reader,''
        return reader,line
    
    def open_pattern_file(self):
        pattern_site = codecs.open(PATTERN_SITE, 'r', 'utf-8', errors='ignore')
        pattern_domain = codecs.open(PATTERN_DOMAIN, 'r', 'utf-8', errors='ignore')
        #共用白名单
        pattern_domain,com_whi = self.skip_tag_reader(pattern_domain)
        if com_whi=='':
            common_white=''
        else:
            common_white = re.compile(com_whi)
        #共用黑名单
        pattern_domain,com_bla = self.skip_tag_reader(pattern_domain)
        if com_bla=='':
            common_black = ''
        else:
            common_black = re.compile(com_bla)
        
        #所有domains黑白名单集合
        domains_pcre = {}
#         for domain_pcre in pattern_domain.readline():
        while True:
            domain_pcre = pattern_domain.readline()
            if not domain_pcre:
                break
            if domain_pcre=='\n' or domain_pcre.startswith('#'):
                continue
            domain_list = domain_pcre.split('`')
            domain_list_white = re.compile(domain_list[1]) if domain_list[1]!='' else None
            domain_list_black = re.compile(domain_list[2]) if domain_list[2]!='' else None
            domain_list_hub = re.compile(domain_list[3]) if domain_list[3]!='' else None
            domain_list_leaf = re.compile(domain_list[4].rstrip('\n')) if domain_list[4].strip('\n')!='' else None
            domains_pcre.update({domain_list[0]:[domain_list_white,domain_list_black,domain_list_hub,domain_list_leaf]})

        
        #所有sites黑白名单集合
        sites_pcre = {}
        for site_pcre in pattern_site:
            if site_pcre=='\n' or site_pcre.startswith('#'):
                continue
            site_list = site_pcre.split('`')
            site_list_white = re.compile(site_list[1]) if site_list[1]!='' else None
            site_list_black = re.compile(site_list[2]) if site_list[2]!='' else None
            site_list_hub = re.compile(site_list[3]) if site_list[3]!='' else None
            site_list_leaf = re.compile(site_list[4].rstrip('\n')) if site_list[4].rstrip('\n')!='' else None
            sites_pcre.update({site_list[0]:[site_list_white,site_list_black,site_list_hub,site_list_leaf]})
        
        return [common_white,common_black,sites_pcre,domains_pcre]
    
    
    def get_base_domain(self,url_input):
#         print url_input
        second_domain = urlparse.urlparse(url_input).hostname
        if second_domain.startswith("www."):
            second_domain = second_domain[4:]
        list_host = second_domain.split('.')
        one_domain=''
        if list_host[-1] == 'cn' and list_host[-2] in ('com','net','gov','org'):
            one_domain = '.'.join(second_domain.split('.')[-3:])
        else:
            one_domain = '.'.join(second_domain.split('.')[-2:])
        return one_domain,second_domain
    
    
    def pattern(self,url):
#         common_white,common_black,sites_pcre = self.open_pattern_file()
#         try:
        one_domain,second_domain = self.get_base_domain(url)
#         print 'one_domain: ',one_domain
#         print 'second_domain: ',second_domain
        #在sites站点中查找
        if self.sites_pcre.has_key(second_domain):
            if self.sites_pcre.get(second_domain)[0] and self.sites_pcre.get(second_domain)[0].search(url):
#                 print '-------T'
                return True
            elif self.sites_pcre.get(second_domain)[1] and self.sites_pcre.get(second_domain)[1].search(url):
#                 print '-----F'
                return False
            
        #在domains站点中查找
        elif self.domains_pcre.has_key(one_domain):
            if self.domains_pcre.get(one_domain)[0] and self.domains_pcre.get(one_domain)[0].search(url):
                return True
            if self.domains_pcre.get(one_domain)[1] and self.domains_pcre.get(one_domain)[1].search(url):
                return False
        
        #在黑名单中查找到
        elif self.common_black!='' and self.common_black.search(url):
            return False
        
        #在白名单中查找
        elif self.common_white!='' and self.common_white.search(url):
            return True
        #全部没有匹配上时返回True
        return True
            
#         except:
#             print 'ERROR: pattern compile error'
        
    def is_hub_page(self,url):
        one_domain,second_domain = self.get_base_domain(url)
        if self.sites_pcre.has_key(second_domain) and self.sites_pcre.get(second_domain)[2] and self.sites_pcre.get(second_domain)[2].search(url):
            return True
        elif self.domains_pcre.has_key(one_domain) and self.domains_pcre.get(one_domain)[2] and self.domains_pcre.get(one_domain)[2].search(url):
            return True
        else:
            return False
    
    def is_leaf_page(self,url):
        one_domain,second_domain = self.get_base_domain(url)
        if self.sites_pcre.has_key(second_domain) and self.sites_pcre.get(second_domain)[3] and self.sites_pcre.get(second_domain)[3].search(url):
            return True
        elif self.domains_pcre.has_key(one_domain) and self.domains_pcre.get(one_domain)[3] and self.domains_pcre.get(one_domain)[3].search(url):
            return True
        else:
            return False

if __name__ == '__main__':
    pattern = PatternSys()
    s = ['http://www.autohome.com.cn/a00/','http://k.autohome.com.cn/1/ge2/','http://k.autohome.com.cn/3126']
    for u in s:
        print pattern.pattern('k.autohome.com.cn',u)
#         time.sleep(10)
#     s = r''+'/\d+/ge\d+/'
#     s2 = r'((k.autohome.com.cn/spec/\d+/(?!ge))|(k.autohome.com.cn/spec/\d+/$)|(k.autohome.com.cn/\d+/(?!ge))|(k.autohome.com.cn/\w+/$))'
#     f = re.compile(s)
#     f2 = re.compile(s2)
#     print f.search('/1/ge2/')
#      
#     print f2.search('k.autohome.com.cn/spec/112/')