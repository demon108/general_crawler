# -*- encoding:utf-8 -*
import os
#配置文件

'''
scrapy_pattern.so库文件必须放置于conf目录中，运行crawler时，也需到conf目录下运行
eg:
    cd ../scrapy_genaral/conf
    scrapy crawl you -a seed=seed.urls -a sites=sites.dat -a single_scrapy=true 
'''
PROJECT = os.path.split(os.path.dirname(os.path.realpath(__file__)))[0]
#pipelines.py  --->path_par
DATA_FILES = PROJECT +'/data_files'
#The final location to save the file of file
#DBFILE_MOVE_TARGET = DATA_FILES + '/output_eb/'
DBFILE_MOVE_TARGET = '/disk2/list_crawler/output_eb/'

#DBFILE_MAKING_DIR = DATA_FILES + '/list_crawler/'
DBFILE_MAKING_DIR = '/disk2/list_crawler/'
# dbfile_making_dir = PROJ_HOME+'/list_crawler/'

#hosts.conf
HOSTS_CONF = PROJECT+'/conf/hosts.conf'

#urls = get_candi_urls(4000,1000)
#The total urls get from Redis one time
URLS_NUM = 4000
#The total seeds 
HOST_NUM = 1000

#The max depth that your spider crawl
MAX_DEPTH = 4

#The max depth that you want your spider record back_link
MAX_BACK_LINK = 1

#libbkdb.so的位置是否需要提出来，便于统一管理？（加载伯克利数据库） 

#刷新seeds的时间,单位为：seconds
REFRESH_TIME = 3

#想其它服务器发送失败多少次就停止向该服务器发送url
SEND_URL_TIMES = 10
#其它机器当掉之后重新连接的时间间隔 单位(秒)
RETRY_CONN = 43200

'''
redis数据库部分
'''
#keyword for redis lists 
#plist,plist_layer,unfetching
KEY_FOR_REDIS = '_general'

#control the next time
KEY_CONTROL_NEXT_TIME = 'general:'

'''
pattern.dat
'''
PATTERN_SITE = PROJECT+'/conf/pattern_site.dat'
PATTERN_DOMAIN = PROJECT+'/conf/pattern_domain.dat'

'''
keyword in url
'''
KEYWORD_IN_URL_FILE = PROJECT+'/conf/keyword_in_url.dat'
KEYWORD_POWER = True

'''
score
'''
#score = (1/depth)^wd × sitepr^ws × type_weight^wt
#some weight of score
#depth
WD = 2
#site_pr
WS = 2
#type of page
WT = 1

LIST = 1
POST = 1

HUB = 2
BLOG = 2
NEWS = 2
LEAF = 2

USER_PAGE = 0

OTHER_TYPE = 1



'''
BBS
'''
BBS_POWER = False

'''
write to bkb
'''
WRITE_TO_BKB = True

'''
write to monogo
'''
WRITE_TO_MONOGO = False

BBS_EXPAND_POWER = False
