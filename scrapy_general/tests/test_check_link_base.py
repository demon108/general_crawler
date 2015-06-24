import redis

global db
db = redis.StrictRedis('127.0.0.1', port=6379)

def check_link_base(url):
    meta_info = get_meta_info(url)
    next = int(meta_info['next'])
    if next:
        return 2 if int(time.time()) - next >= 0 else 0
    return 1


def get_meta_info(url):
    global db
    key = "lb:%s"%url
    rst = db.hgetall(key)
    if rst:
        if rst['next'] > 2145888000:#should before 2038-01-01
            rst['next'] = int(rst['last'])+86400
        return rst
    return {'last':0, 'next':0, 'md5':''}


value = check_link_base('auto.qq.com')
print value