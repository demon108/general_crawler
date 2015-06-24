import redis

global db
db = redis.StrictRedis('127.0.0.1',port=6379)




len = db.llen("plist0")
value = db.lrange("plist0", 0, len)
print "plist0_len: ",len
print "plist0_value: ",value

len = db.llen("plist1")
value = db.lrange("plist1", 0, len)
print "plist1_len: ",len
print "plist1_value: ",value

len = db.llen("plist2")
value = db.lrange("plist2", 0, len)
print "plist2_len: ",len
print "plist2_value: ",value

len = db.hlen("site_pr")
value = db.hgetall("site_pr")
print "site_pr: ",len
print "site_pr_value: ",value


len = db.hlen("plist_layer")
value = db.hgetall("plist_layer")
print "plist_layer: ",len
print "plist_layer_value: ",value











