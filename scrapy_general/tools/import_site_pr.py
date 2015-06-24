import redis

db = redis.StrictRedis(unix_socket_path="/tmp/redis.sock")

fp = open("maixun_url.csv","r")
for line in fp:
    new_line = line.strip()
    t = new_line.split(',')
    db.hset("site_pr",t[0],t[1])

fp.close()

