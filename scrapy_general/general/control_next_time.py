# -*- encoding:utf-8 -*
import redis

from config import KEY_CONTROL_NEXT_TIME
'''
管理用于存储url刷新时间的key
'''
def get_redis_db():
    return redis.StrictRedis('127.0.0.1',port=6379)

def control_key_next_time():
    del_urls_num = 0
    db = get_redis_db()
    for i,key in enumerate(db.smembers(KEY_CONTROL_NEXT_TIME)):
        try:
            db.delete(key)
            db.srem(KEY_CONTROL_NEXT_TIME,key)
            del_urls_num = del_urls_num + 1
        except:
            print 'err key: ', key
    return del_urls_num

del_urls_num = control_key_next_time()
print del_urls_num
