# coding:utf-8
import redis
import re
import urlparse

global db
db = redis.StrictRedis('127.0.0.1',port=6379)
global site_pr
site_pr = db.hgetall("site_pr")
global news_re
news_re = re.compile("[-_/][a-zA-Z]*[-_]?(201\d)[-_/]?((0?[1-9])|10|11|12)[-_/]?(([0-2]?[1-9])|10|20|30|31)([-_/]|.*(html|shtml|htm))")

#todo: update higher score
def add_to_pending_list(url,depth,is_new):
    global db
    key = "plist%d"%depth
    score = cal_url_score(url,depth)

    if depth == 2 and score < 400:
        return False
    if depth == 3 and score < 300:
        return False

    db.zadd(key,score,url)
    db.hset("plist_layer",url,depth)
    #db.hset("plist_new", url, is_new)
    return True


#calculation the url's score
#估算url的score
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

    return score

#判断该站点是否在“site_pr”列表中，在列表中则该站点所对应的值加1，不在则返回2
#site_pr中所对应的key的值为空，所以返回值全部为2
def get_site_pr(site_name):
    global site_pr
    if site_name in site_pr:
        return int(site_pr[site_name])+1
    return 2

#判断该url是否为新闻网址
def is_news(url):

    if url.find("news") >= 0:
        return True
    if url.find("epaper") >= 0:
        return True
    #news_re
    global news_re
    if news_re.search(url):
        return True
    return False

#根据url的不同类型，返回不同的值
def get_url_type(url):
    if url.find("/bbs") >= 0 or url.find("wenda.") >=0 or url.find("forum")>=0 :
        return 5
    if url.find("blog") >= 0:
        return 4
    return 1


# url = "http://auto.qq.com"
url = "http://bbs.qq.com"
# print urlparse.urlparse('http://auto.qq.com/map?qq=123')
print is_news(url)

print get_site_pr("auto.qq.com")

print get_url_type(url)

print cal_url_score(url,2)


