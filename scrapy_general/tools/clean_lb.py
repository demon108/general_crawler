import redis

db = redis.StrictRedis(unix_socket_path="/tmp/redis.sock")

rst = db.keys("lb:*")
print len(rst) , "pages found"
for key in rst:
    #print key
    db.delete(key)
