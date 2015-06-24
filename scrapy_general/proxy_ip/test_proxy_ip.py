import random

class ProxyMiddleware(object):
    def process_request(self, request, spider):
        #data in proxy_ip.txt: 211.161.152.108,8000
        fd = open('proxy_ip.txt','r')
        data = fd.readlines()
        fd.close()
        length = len(data)
        index  = random.randint(0, length -1)
        item   = data[index]
        arr    = item.split(',')
        request.meta['proxy'] = 'http://%s:%s' % (arr[0],arr[1])
        
        

'''

DOWNLOADER_MIDDLEWARES = {
    'scrapy.contrib.downloadermiddleware.httpproxy.HttpProxyMiddleware': 110,
    'sitemap.middlewares.ProxyMiddleware': 100,
    }
'''