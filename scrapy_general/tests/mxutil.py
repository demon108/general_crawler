import hashlib
import time
import urlparse
import ctypes
import re
import codecs

import redis
from scrapy import log

global db
db = False
pattern_so = False
site_pattern = False
news_re = False
site_pr = False

def get_db():   
    global db
    return db

def init_util():
    global db
#     db = redis.StrictRedis(unix_socket_path="/tmp/redis.sock")
    db = redis.StrictRedis('127.0.0.1',port=6379,db='0')
    #clean up downloading list, pending list
    db.delete("plist0_auto");
    db.delete("plist1_auto")
    db.delete("plist2_auto")
    db.delete("plist3_auto")
    db.delete("plist4_auto")
    db.delete("fetching_list")
    db.delete("plist_new")
    db.delete("plist_layer_auto")
    #site pr
    global site_pr
    site_pr = db.hgetall("site_pr")

    global pattern_so
    pattern_so = ctypes.CDLL("./scrapy_pattern.so")
    pattern_so.init_pfilter()
    pattern_so.init_wrapper()
    pattern_so.scope_init()

    global news_re
    news_re = re.compile("[-_/][a-zA-Z]*[-_]?(201\d)[-_/]?((0?[1-9])|10|11|12)[-_/]?(([0-2]?[1-9])|10|20|30|31)([-_/]|.*(html|shtml|htm))")
    
    global url_to_db
    url_to_db = codecs.open('url_to_db.my','a+','utf-8', errors='ignore')
    global url_base
    url_base = codecs.open('base_to_db.my','a+','utf-8', errors='ignore')
    global url_fetching
    url_fetching = codecs.open('fetching_to_db.my','a+','utf-8', errors='ignore')
    global url_pending
    url_pending = codecs.open('pending_to_db.my','a+','utf-8', errors='ignore')
    global url_add
    url_add = codecs.open('add_to_db.my','a+','utf-8', errors='ignore')
def cleanup_util():
    #global db
    #db.save()
    global pattern_so
    pattern_so.cleanup_pfilter()
    pattern_so.clean_wrapper()
    pattern_so.scope_destory()
    return True

def is_domain_in_scope(site):
    global pattern_so
    ret = pattern_so.in_domain_scope(site)
    return ret

#pattern logic
#return True when url is ok
#return False when matched shows bad
def do_url_pattern_filter(url):
    global pattern_so
    parsed  = urlparse.urlparse(url)
    if pattern_so.do_pfilter(parsed.netloc,url):
        return True
    return False 
#check the link base 
# return False when found in link base and 
# 	earlier than the next fetch time
# return 1 when new url
# return 2 when to be fresh
def check_link_base(url):
    meta_info = get_meta_info(url)
    next = int(meta_info['next'])
    
    if int(time.time()) - next < 0:
        global url_base
        url_base.write('%s\n'%(url))
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
    key = "plist%d_auto"%_depth
    d1 = db.hget("plist_layer_auto",url)
    if d1:
        d1 = int(d1)
        if d1 <= _depth:
            global url_pending
            url_pending.write('%s,%s\n'%(url,'_depth'+str(depth)))
            return True
        if d1 > _depth: #more important
            #db.hset("plist_layer",url,depth)
            db.zrem("plist%d_auto"%d1,url) #remove the high layer
            return False
    return False 

def is_refresh_url(url):
    global db
    return db.hget("plist_new",url)

def get_next_fetch_time(url,is_new,cur,time_span,is_update,http_code):
    global pattern_so

    if pattern_so.wp_is_post_page(url) or pattern_so.wp_is_blog_page(url):
        return cur + 30*86400

    if pattern_so.wp_is_leaf_page(url):
        return cur+ 15*86400 

    is_static = False
    if( url.endswith('.html') | url.endswith('.htm') | url.endswith('.shtml')):
        is_static = True

    if pattern_so.wp_is_hub_page(url):
        is_static = False
    #print url, is_new, cur, time_span, is_update, is_static, http_code
    if is_new:
        if is_static:
            return 86400 * 7 + cur
        else :
            return 3600 * 3 + cur

    if 200 <= http_code < 300:
        if is_update:
            t = time_span * 0.75
        else:
            t = time_span * 1.5
    elif 300 <= http_code < 400:
        t = time_span * 2
    elif 400 <= http_code < 500:
        t = time_span * 20
    elif 500 < http_code:
        t = time_span * 1.5
    else:
        t = time_span * 2

    if is_static and t < 86400:
        t = 86400
    if not is_static and t < 3600:
        t = 3600
    return int(cur+ t)

def load_site_pr():
    global db

def is_news(url):
    #global pattern_so
    #if pattern_so.wp_is_news_page(url):
    #    return True
    #return False

    if url.find("news") >= 0:
        return True
    if url.find("epaper") >= 0:
        return True
    #news_re
    global news_re
    if news_re.search(url):
        return True
    return False

def get_site_pr(site_name):
    global site_pr
    if site_name in site_pr:
        return int(site_pr[site_name])+1
    return 2

# 1, plain page
# 4, blog
# 5, bbs
# 9, news(would not returned)
def get_url_type(url):
    #global pattern_so
    #type = pattern_so.wp_get_media_type(url)
    #if type == 1:#bbs
    #    return 5
    #elif type == 2:#news
    #    return 9
    #elif type == 3:#blog
    #    return 4
    #else:
    #    return  1
    #bbs
    if url.find("/bbs") >= 0 or url.find("wenda.") >=0 or url.find("forum")>=0 :
        return 5
    if url.find("blog") >= 0:
        return 4
    #if is_news(url):
    #    return 9
    return 1

def cal_url_score(url,depth):
    score = 0
    #depth
    score += 100 *(5-depth)

    parsed  = urlparse.urlparse(url)
    s = get_site_pr(parsed.netloc)
    inews = is_news(url)
    if inews:
        score += 100 + s * 9
    else:
        t = get_url_type(url)
        score += s * t

    #log.msg("/YOU_LOG_SCORE/%s(%d)"%(url,score),level=log.DEBUG)
    return score


#todo: update higher score
def add_to_pending_list(url,depth,is_new):
    global db
    key = "plist%d_auto"%depth
    score = cal_url_score(url,depth)
    global url_add
    if depth == 2 and score < 400:
        url_add.write('%s, %s\n'%(url,'_depth'+str(depth)))
        return False
    if depth == 3 and score < 300:
        url_add.write('%s, %s\n'%(url,'_depth'+str(depth)))
        return False
    
    global url_to_db
    url_to_db.write('%s, %s\n'%(url,'_depth'+str(depth)))
    db.zadd(key,score,url)
    db.hset("plist_layer_auto",url,depth)
    #db.hset("plist_new", url, is_new)
    return True

#remove from pending list.
#should be invoked by get_candi_urls
def remove_pending_list(url):
    global db
    #db.zrem("plist%d"%depth,url)
    db.hdel("plist_layer_auto",url)
    #db.hdel("plist_new",url)

#the status when crawl-ing
#using  "fetching_list" set
def check_fetching_list(url):
    global db
    if db.sismember("fetching_list",url):
        global url_fetching
        url_fetching.write('%s\n'%(url))
    return db.sismember("fetching_list",url)

def add_to_fetching_list(url):
    global db
    if db.sadd("fetching_list",url):
        return True
    return False

def remove_fetching_list(url):
    global db
    if db.srem("fetching_list",url):
        return True
    return False

def get_meta_info(url):
    global db
    key = "lb:%s"%url
    rst = db.hgetall(key)
    if rst:              
        if rst['next'] > 2145888000:#should before 2038-01-01
            rst['next'] = int(rst['last'])+86400
        return rst
    return {'last':0, 'next':0, 'md5':''}

def save_page_meta(url, http_code, content, resp_time):
    meta_info = get_meta_info(url)

    is_update = True#Todo: need compare the content and last md5
    new_md5 =  hashlib.md5(content).hexdigest().upper()

    is_new = True
    if meta_info['last']:# found in link base
        is_new = False
        if meta_info['md5'] == new_md5:
            is_update = False

    time_span = int(meta_info['next']) - int(meta_info['last'])
    next_time = get_next_fetch_time(url,is_new,resp_time,time_span,is_update,http_code)
    meta_info['md5'] = new_md5
    meta_info['last'] = resp_time
    meta_info['next'] = next_time
    global db
    key = "lb:%s"%url
    db.hmset(key,meta_info)
    db.expire(key,86400*8)

def get_candi_urls(url_count,host_count):
    rst = dict() 
    # seeds should add to pending list first
    global db;  
    left = url_count
    layer0 = db.zrange("plist0_auto",0,-1)
    if layer0:
        for url in layer0:
            if left <= 0:
                break;
            db.zrem("plist0_auto",url)#delete url from layer
            rst[url]=0
            left -= 1

    if rst:
        return rst

    left = url_count * 4

    url_layer = {}
    urls = []
    while True:
        layer1 = db.zrevrange("plist1_auto",0,left-1)
        if layer1:
            for url in layer1:
                if left <= 0:
                    break
                url_layer[url]=1
                urls.append(url)
                left -= 1
            break

        if left <= 0:
            break

        layer2 = db.zrevrange("plist2_auto",0,left-1)
        if layer2:
            for url in layer2:
                if left <= 0:
                    break
                url_layer[url]=2
                urls.append(url)
                left -= 1
            break

        if left <= 0:
            break

        layer3 = db.zrevrange("plist3_auto",0,left-1)
        if layer3:
            for url in layer3:
                if left <= 0:
                    break
                url_layer[url]=3
                urls.append(url)
                left -= 1
            break

        if left <= 0:
            break

        layer4 = db.zrevrange("plist4_auto",0,left-1)
        if layer4:
            for url in layer4:
                if left <= 0:
                    break
                url_layer[url]=4
                urls.append(url)
                left -= 1

        break

    if len(urls) == 0:
        return rst

    #---2013-06-20, select the priority site automaticly
    avr = url_count / host_count
    hosts = dict()
    h_counter = 0
    u_counter = 0

    for url in urls:
        parsed  = urlparse.urlparse(url)
        host = parsed.netloc
        if host in hosts:
            if hosts[host] >= avr:
                continue
            hosts[host] += 1
        else:
            if h_counter > host_count:
                continue
            hosts[host] = 1

        layer = url_layer[url]
        db.zrem("plist%s_auto"%layer,url)
        rst[url] = layer
        u_counter += 1

        if u_counter > url_count:
            break
    return rst

