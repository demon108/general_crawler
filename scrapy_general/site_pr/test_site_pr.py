import json
import redis
db = redis.StrictRedis('127.0.0.1',port=6379)

f = open('site_pr.dat','r')
 
site = f.readline().replace('\'','"')
s = json.loads(site)
for key,value in s.iteritems():
    try:
        db.hset("site_pr", key.strip(), value.strip())
    except TypeError as e:
        print e
        print key,"---",value


# print db.hget("site_pr", 'www.zjypw.com')
        