import redis
import hashlib


global db
db = redis.StrictRedis('127.0.0.1',port=6379)

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
    #new_md5:4479E73D311B3302B3FF7D9BA8EF6F0C
    new_md5 =  hashlib.md5(content).hexdigest().upper()

    is_new = True
    if meta_info['last']:# found in link base
        is_new = False
        if meta_info['md5'] == new_md5:
            is_update = False

    time_span = int(meta_info['next']) - int(meta_info['last'])
    #next_time:1406029415
    next_time = get_next_fetch_time(url,is_new,resp_time,time_span,is_update,http_code)
    meta_info['md5'] = new_md5
    meta_info['last'] = resp_time
    meta_info['next'] = next_time
    global db
    key = "lb:%s"%url
    db.hmset(key,meta_info)
    db.expire(key,86400*8)
    

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

