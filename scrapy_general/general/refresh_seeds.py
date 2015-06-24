import redis
import time
import codecs
import sys

from config import REFRESH_TIME

db = redis.StrictRedis('127.0.0.1',port=6379)

class ReSeeds(object):
    
    def __init__(self,filename):
        self.filename = filename
        
    def add_to_db(self,url):
        db.zadd('plist0',0,url)
    
    def refresh(self):
        
        while True:
            SReader =  codecs.open(self.filename,'r','utf-8', errors='ignore')
            for line in SReader:
                link = line.strip()
                if not link :
                    break
                if not link.startswith('http:') :
                    continue
                self.add_to_db(link)
            SReader.close()
            time.sleep(REFRESH_TIME)
            
            
            
if __name__ == "__main__":
    reader = ReSeeds(sys.argv[1])
    reader.refresh()
    
        
                