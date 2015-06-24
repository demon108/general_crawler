import redis

db = redis.StrictRedis(unix_socket_path="/tmp/redis.sock") 
total = db.zcard("plist2")

trim_to = 150000

max = total - trim_to
start = 0

if max > 0:
    while True:
        tmp = db.zrange("plist2",start,start+1000)
        for url in tmp:
            #delete from plist2, and plist_layer
            db.zrem("plist2",url)
            db.hdel("plist_layer",url) 
        start += len(tmp)
        if start > max:
            break
        if start >= 150000:
            break
    print "delete ", start+1000 ," urls"
