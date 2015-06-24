# Scrapy settings for you project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/topics/settings.html
#

BOT_NAME = 'general'

SPIDER_MODULES = ['general.spiders']
NEWSPIDER_MODULE = 'general.spiders'

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'you (+http://www.yourdomain.com)'
USER_AGENT = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.168 Safari/535.19'
user_agent = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.168 Safari/535.19'
#DEPTH_LIMIT=1

# ITEM_PIPELINES = [
#     'general.pipelines_my.GeneralPipeline'
# ]
ITEM_PIPELINES = {
    'general.pipelines.GeneralPipeline':0
}

#MEMDEBUG_ENABLED=True
RANDOMIZE_DOWNLOAD_DELAY=True
#(0.5-1.5)*DOWNLOAD_DELAY, second
DOWNLOAD_DELAY = 0 

#default 180secs
DOWNLOAD_TIMEOUT = 60
download_timeout = 60

#REDIRECT_MAX_TIMES=5
#SELECTORS_BACKEND = 'lxml'
RETRY_ENABLED = False
RETRY_TIMES = 1
RETRY_HTTP_CODES = [400,408,502,504]

CONCURRENT_REQUESTS = 10
CONCURRENT_ITEMS = 4
#CONCURRENT_REQUESTS_PER_DOMAIN = 2
CONCURRENT_REQUESTS_PER_IP = 2

LOG_LEVEL='INFO'
#LOG_LEVEL='DEBUG'
LOG_FILE='scrapy.log'
LOG_ENCODING='utf-8'

#================================
#which spider should use WEBKIT
#WEBKIT_DOWNLOADER=['demo']
 
#DOWNLOADER_MIDDLEWARES = {
    #'demo.WebkitDownloader.WebkitDownloader': 543,
#}   
DEPTH_PRIORITY = 1
SCHEDULER_DISK_QUEUE = 'scrapy.squeue.PickleFifoDiskQueue'
SCHEDULER_MEMORY_QUEUE = 'scrapy.squeue.FifoMemoryQueue'

#STATS_CLASS = ''
