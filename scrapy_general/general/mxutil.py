# encoding:utf-8
import hashlib
import time
import urlparse
import ctypes
import re
import codecs

import redis
from scrapy import log

from pattern import PatternSys
from config import *

global db
db = False
pattern_so = False
site_pattern = False
news_re = False
site_pr = False

def get_db():   
    global db
    return db

def is_homepage(url):
    #get how many slashes in url
    max_slash_sum = 4
    slash_count = url.count("/")
    if url.startswith("http://"):
        slash_count = slash_count - 2

    if slash_count == 0:
        return True

    if url[-1] == '/':
        if slash_count <= max_slash_sum:
            return True
        else:
            return False

    r_slash_index = url.rfind("/")
    key_name = ["main","default","index","home"]
    if r_slash_index == -1:
        tmp_url = url
    else:
        tmp_url = url[r_slash_index:]

    for key in key_name:
        if tmp_url.find(key) > -1:
            if slash_count <= max_slash_sum:
                return True
    return False
# url = "http://auto.sina.com.cn/a"
# print is_homepage(url)


def init_util():
    global db
#     db = redis.StrictRedis(unix_socket_path="/tmp/redis.sock")
    db = redis.StrictRedis('127.0.0.1',port=6379,db='0')
    
    #clean up downloading list, pending list
    for i in range(MAX_DEPTH):
        db.delete('plist'+str(i)+KEY_FOR_REDIS)
#     db.delete("fetching_list")
    db.delete("plist_layer"+KEY_FOR_REDIS)
    
    #site pr
    global site_pr
    site_pr = db.hgetall("site_pr")

    global pattern_so
    pattern_so = ctypes.CDLL("./scrapy_pattern.so")
#     pattern_so.init_pfilter()
    pattern_so.init_wrapper()
    pattern_so.scope_init()
    
    global pattern
    pattern = PatternSys()
    
    global seed_urls
    
    global news_re
    news_re = re.compile("[-_/][a-zA-Z]*[-_]?(201\d)[-_/]?((0?[1-9])|10|11|12)[-_/]?(([0-2]?[1-9])|10|20|30|31)([-_/]|.*(html|shtml|htm))")
    
#     global url_to_db
#     url_to_db = codecs.open('url_to_db.my','a+','utf-8', errors='ignore')
#     global url_base
#     url_base = codecs.open('base_to_db.my','a+','utf-8', errors='ignore')
#     global url_fetching
#     url_fetching = codecs.open('fetching_to_db.my','a+','utf-8', errors='ignore')
#     global url_pending
#     url_pending = codecs.open('pending_to_db.my','a+','utf-8', errors='ignore')
    
def cleanup_util():
    #global db
    #db.save()
    global pattern_so
    pattern_so.cleanup_pfilter()
    pattern_so.clean_wrapper()
    pattern_so.scope_destory()
    return True

def read_seedfile(seed_file):
    global seed_urls
    seed_urls = []
    with codecs.open(seed_file,'r','utf-8') as f:
        for line in f:
            link = line.strip()
            if not link or not link.startswith('http'):
                continue
            if link=='\n':
                    continue
            if link.startswith('#'):
                continue
            seed_urls.append(link)
    return seed_urls

def read_sites(sites_dat):
        sites = set()
        with codecs.open(sites_dat,'r','utf-8') as f:
            for line in f:
                link = line.strip()
                if link=='\n':
                    continue
                if link.startswith('#'):
                    continue
                sites.add(link)
        return sites

def is_post_page(url):
    global pattern_so
    if pattern_so.wp_is_post_page(url):
        return True
    return False

def is_list_page(url):
    global pattern_so
    if pattern_so.wp_is_list_page(url):
        return True
    return False

# input = "http://news.sina.com.cn?a=1&b=2"
#output: sina.com.cn,news.sina.com.cn 取得的url都不带www与http
def get_base_domain(url_input):
    second_domain = urlparse.urlparse(url_input).hostname
    if not second_domain:
        return 'None','None'
    if second_domain.startswith("www."):
        second_domain = second_domain[4:]
    list_host = second_domain.split('.')
    one_domain = ''
    if list_host[-1] == 'cn' and list_host[-2] in ('com','net','gov','org'):
        one_domain = '.'.join(second_domain.split('.')[-3:])
    else:
        one_domain = '.'.join(second_domain.split('.')[-2:])
    return one_domain,second_domain


#pattern logic
#return True when url is ok
#return False when matched shows bad
def do_url_pattern_filter(url):
    global pattern
    if pattern.pattern(url):
        return True
    return False 

#check the link base 
# return False when found in link base and 
#     earlier than the next fetch time
# return 1 when new url
# return 2 when to be fresh
def check_link_base(url):
    meta_info = get_meta_info(url)
    next = int(meta_info['next'])
    
#     if int(time.time()) - next < 0:
#         global url_base
#         url_base.write('%s\n'%(url))
    if next:
        return 2 if int(time.time()) - next >= 0 else 0
    return 1

#check the fetching and pending list
# return True when found in fetchling list and pending list
# when found a lower depth, delete the higher queue and 
# insert to the lower queue
# using  plist0,plist1,plist2,plist3,plist4,plist_layer
# zset and hash
def check_pending_list(url,depth):
    global db
    _depth = int(depth)
#     key = "plist%d_auto"%_depth
    dep = db.hget("plist_layer"+KEY_FOR_REDIS,url)
    if dep:
        dep = int(dep)
        if dep <= _depth:
#             global url_pending
#             url_pending.write('%s,%s\n'%(url,'_depth'+str(depth)))
            return True
        if dep > _depth: #more important
            db.zrem("plist"+str(dep)+KEY_FOR_REDIS,url) #remove the high layer
            return False
    return False 


#get_next_fetch_time(url,is_new,resp_time,time_span,is_update,http_code)
def next_fetch_time(url,cur):
    global pattern_so
    global pattern
    global seed_urls
#     print 'seed_urls:',seed_urls
    if url in seed_urls:
        return cur + 3600
    
    if pattern.is_hub_page(url):
        return cur + 3600*8
    
    if pattern.is_leaf_page(url):
        return -1
    
    if(pattern_so.wp_is_hub_page(url)):
        return cur + 3600*8
    
    #forum list
    if(pattern_so.wp_is_list_page(url)):
        return cur + 3600*24
    #其它类型网页
    if(pattern_so.wp_get_media_type(url)==4):
        return cur + 3600*24*2
    else:
        return -1


# 
def get_site_pr(site_name):
    global site_pr
    if site_name in site_pr:
        return int(site_pr[site_name])
    return 1

def check_bbs_page(url):
    global pattern_so
    #论坛列表页
    if pattern_so.wp_is_list_page(url): 
        return True
    #论坛内容页
    if pattern_so.wp_is_post_page(url):
        return True
    else:
        return False    

def get_url_type(url):
    global pattern_so
    #论坛列表页
    if pattern_so.wp_is_list_page(url): 
        return LIST
    #论坛内容页
    if pattern_so.wp_is_post_page(url):
        return POST
    #导航页
    if pattern_so.wp_is_hub_page(url):
        return HUB
    #具体博客内容页
    if pattern_so.wp_is_blog_page(url):
        return BLOG
    #新闻内容网页
    if pattern_so.wp_is_news_page(url):
        return NEWS
    if pattern_so.wp_is_user_page(url):
        return USER_PAGE
    #内容页面
    if pattern_so.wp_is_leaf_page(url):
        return LEAF 
    else:
        return OTHER_TYPE

def pageclean_url_type(url):
    global pattern_so
    #论坛列表页
    if pattern_so.wp_is_list_page(url): 
        return 'L'
    #论坛内容页
    if pattern_so.wp_is_post_page(url):
        return 'P'
    #导航页
    if pattern_so.wp_is_hub_page(url):
        return 'H'
    #具体博客内容页
    if pattern_so.wp_is_blog_page(url):
        return 'B'
    #新闻内容网页
    if pattern_so.wp_is_news_page(url):
        return 'N'
    #用户页面
    if pattern_so.wp_is_user_page(url):
        return 'U'
    #内容页面
    if pattern_so.wp_is_leaf_page(url):
        return 'C' 
    #其它页面
    else:
        return 'O'
    
#score = (1/depth)**wd × sitepr**ws × type_weigh**twt
def get_url_score(url,depth):
    type_weight = float(get_url_type(url))
    parsed  = urlparse.urlparse(url)
    sitepr = get_site_pr(parsed.netloc)
    score = 1/float(depth)**WD * sitepr**WS * type_weight**WT
    return score

#todo: update higher score
def add_to_plist(url,depth):
    global db
    key = "plist"+str(depth)+KEY_FOR_REDIS
    if depth==0:
        score = 1
    else:
        score = get_url_score(url,depth)
#     global url_to_db
#     url_to_db.write('%s, %s\n'%(url,'_depth'+str(depth)))
    db.zadd(key,score,url)
    db.hset("plist_layer"+KEY_FOR_REDIS,url,depth)
    return True

#remove from pending list.
#should be invokedsites by get_candi_urls
def remove_pending_list(url):
    global db
    db.hdel("plist_layer"+KEY_FOR_REDIS,url)

#the status when crawl-ing
#using  "fetching_list" set
def check_unfetching(url):
    global db
#     if db.sismember("unfetching_list"+KEY_FOR_REDIS,url):
#         global url_fetching
#         url_fetching.write('%s\n'%(url))
    return db.sismember("unfetching_list"+KEY_FOR_REDIS,url)

def add_to_unfetching(url):
    global db
    if db.sadd("unfetching_list"+KEY_FOR_REDIS,url):
        return True
    return False

def remove_unfetching(url):
    global db
    if db.srem("unfetching_list"+KEY_FOR_REDIS,url):
        return True
    return False

def get_meta_info(url):
    global db
    key = KEY_FOR_REDIS+url
    rst = db.hgetall(key)
    if rst:              
        return rst
    return {'next':0}    
#     return {'last':0, 'next':0, 'md5':''}

def save_page_meta(url, http_code, content, resp_time):
    meta_info = get_meta_info(url)
    next_time = next_fetch_time(url,resp_time)
#     new_md5 =  hashlib.md5(content).hexdigest().upper()
    if next_time==-1:
        add_to_unfetching(url)
    meta_info['next'] = next_time
    global db
    key = KEY_FOR_REDIS+url
    db.hmset(key,meta_info)
    db.expire(key,86400*8)
    db.sadd(KEY_CONTROL_NEXT_TIME,key)

def get_candi_urls(url_count,host_count):
    global db
    
    rst = dict() 
    left = url_count
    url_layer = {}
    urls = []
    while True:
        try :
            for i in range(MAX_DEPTH):
                left = url_count*100 if i > 0 else url_count
                plist = "plist"+str(i)+KEY_FOR_REDIS
                layer_urls_num = db.zrevrange(plist,0,left-1)
                if layer_urls_num:
                    for url in layer_urls_num:
                        if left <= 0:
                            raise
                        url_layer[url] = i
                        urls.append(url)
                        left -= 1
                    raise
                if i == MAX_DEPTH-1 and layer_urls_num == []:
                    raise 
        except:
            break
            
    if len(urls) == 0:
        return rst

    #---2013-06-20, select the priority site automaticly
    avr = url_count / host_count
    hosts = dict()
    u_counter = 0

    for url in urls:
        layer = url_layer[url]
        if layer > 0:
            parsed  = urlparse.urlparse(url)
            host = parsed.netloc
            if host in hosts:
                if hosts[host] >= avr:
                    continue
                hosts[host] += 1
            else:
                hosts[host] = 1

        db.zrem("plist"+str(layer)+KEY_FOR_REDIS,url)
        rst[url] = layer
        u_counter += 1

        if u_counter > url_count:
            break
    return rst


