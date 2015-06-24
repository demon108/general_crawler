
import redis

global db
db = redis.StrictRedis('127.0.0.1',port=6379)

#check the fetching and pending list
# return True when found in fetchling list and pending list
# when found a lower depth, delete the higher queue and 
# insert to the lower queue
# using  plist0,plist1,plist2,plist3,plist4,plist_layer
# zset and hash
def check_pending_list(url,depth):
    global db
    _depth = int(depth)
    key = "plist%d"%_depth
    d1 = db.hget("plist_layer",url)
    print d1
    if d1:
        d1 = int(d1)
        if d1 <= _depth:
            return True
        if d1 > _depth: #more important
            #db.hset("plist_layer",url,depth)
            db.zrem("plist%d"%d1,url) #remove the high layer
            return False
    return False 

url = 'auto.qq.com'
depth = 0
print check_pending_list(url,depth)


