# -*- coding: utf-8 -*-
import urlparse
import codecs
import os
import csv
import re
import urllib
import select
import socket
import sys
import threading
import time
import signal
import copy
import random
from datetime import datetime

from urlparse import urljoin
from posixpath import normpath
import urlparse


from scrapy.http import Request
from scrapy.exceptions import DropItem
import scrapy
from scrapy.conf import settings
# from scrapy.settings import CrawlerSettings
# print CrawlerSettings.overrides
global scrapy_version
if scrapy.__version__!='0.15.1':
    from scrapy.spider import Spider as BaseSpider
    from scrapy.selector import Selector as HtmlXPathSelector
    scrapy_version = 'new'
else:
    from scrapy.spider import BaseSpider
    from scrapy.selector import HtmlXPathSelector
    scrapy_version = 'old'
from scrapy import log
global stats_flag
try:
    from scrapy.stats import stats
    stats_flag = 0
except ImportError:
    stats_flag = 1
    
from general.items import *
from general.mxutil import *
from general.config import *
from general.keyword_in_url import KeywordInURL
from general.bbs_rule import * 
from general.bbs_url_handler import discuz_pipe_line


########global vars#########
mylock = threading.RLock() 
g_sock_dict = dict()
g_quit_flag = False
def signal_handler(signal, frame):
    global g_sock_dict
    global g_quit_flag

    g_quit_flag = True
    print 'You pressed Ctrl+C!'
    print 'key',g_sock_dict.keys()
    for k in g_sock_dict.keys():
        for v in g_sock_dict[k]:
            if v:
                v.close()
    g_sock_dict.clear()
    sys.exit()

class URLRcver(threading.Thread):

    def __init__(self, threadname, dict_no2host ):
        threading.Thread.__init__(self, name = threadname)
        #self.socket_list = socket_list
        self.partnerURLs = []
        self.dict_no2host = dict_no2host
    def run(self):
        global mylock
        global g_sock_dict
        HOST = ''                 # Symbolic name meaning all available interfaces
        PORT = 50007              # Arbitrary non-privileged port
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((HOST, PORT))
        s.listen(1)
        accept_cnt = len(self.dict_no2host)
        while accept_cnt>0:
            conn, addr = s.accept()
            print 'accept connection from::',addr
            conn.setblocking(1)
            mylock.acquire()
            host = addr[0]
            if host in g_sock_dict:
                #has created by sending socket,sending socket has added,[recv,send]
                #g_sock_dict:{host:[conn,]}
                g_sock_dict[host][0] = conn
            else:
                #g_sock_dict:{host:[conn,'']}
                g_sock_dict[host]=[conn,'']
            accept_cnt -= 1
            mylock.release()
        #here all acceptok, start to receiveing
        self.receive_daemon()

    def consume_partner_urls(self):
        global mylock
        mylock.acquire()
        urls = copy.deepcopy(self.partnerURLs)
        self.partnerURLs = []
        mylock.release()
        return urls

    def receive_daemon(self):
        global mylock
        global g_sock_dict
        recv_sockets = [conns[0] for addr, conns in g_sock_dict.iteritems()]
        total = len(self.dict_no2host)

        while True:
            try:
                infds,outfds,errfds = select.select(recv_sockets,[],[],2)
#                 print "select.select() infds: ",infds
#                 print "select.select() outfds: ",outfds
#                 print "select.select() errfds: ",errfds
                if not infds :
                    continue
            except Exception as e:
#                 info=sys.exc_info()
#                 err_msg = 'select error>>%s:%s'%(info[0],info[1])
#                 print err_msg
#                 log.msg( err_msg,level=log.WARNING)
#                 break
                print "ERROR++URLRcver.receive_daemon++",e
                continue

            if len(infds) != 0:
                for s in infds:
                    try:
                        #reading data
                        data = s.recv(1024)
                        r_cnt = len(data)
                        if r_cnt == 0:
                            continue; 
                        #sbyte+"\n"+depth+"`"
                        if data[r_cnt-1] != '`':
                            while 1:
                                chr = s.recv(1)
                                data += chr
                                if chr == '`' :
                                    break
                        try:
                            #mylock.acquire()
                            tmp_decoded_data = data.decode('utf-8','ignore')
                            arr1 = tmp_decoded_data.split("`")
                            for tmp_str in arr1:
                                if tmp_str == "":
                                    continue

                                arr2 = tmp_str.split("\n")
                                if len(arr2) == 2:
                                    url = arr2[0].encode("utf-8")
                                    depth = arr2[1].encode("utf-8")

                                    #if not do_url_pattern_filter(url):
                                    #    log.msg('/YOU_LOG_MM_RECV_FILTER_BAD/ %s'%(url),level=log.DEBUG)
                                    #    continue;
                                    link_flag = check_link_base(url)
                                    if not link_flag:
                                        #log.msg('/YOU_LOG_MM_DUP_LINKBASE/ %s'%(url),level=log.DEBUG)
                                        continue
                                    if check_unfetching(url):
                                        #log.msg('/YOU_LOG_MM_DUP_FETCH/ %s'%(url),level=log.DEBUG)
                                        continue
                                    if check_pending_list(url,depth):
                                        #log.msg('/YOU_LOG_MM_DUP_PENDING/ %s'%(url),level=log.DEBUG)
                                        continue
                                    add_to_plist(url, int(depth))
                                    #log.msg('/YOU_LOG_MM_RECV/ %s(%s)'%(url, depth),level=log.DEBUG)
                        except UnicodeEncodeError, e: #url decode
                            err_msg = 'decode_error:%s(%s)'%(e,data)
                            print err_msg
                            log.msg( err_msg,level=log.WARNING)
                    except socket.error,(value,message):
                        err_msg =  'socket.error:%s(%s)'%(value,message)
                        print err_msg
                        log.msg( err_msg,level=log.CRITICAL)
                    except:
                        info=sys.exc_info()
                        err_msg = 'exception_in_receive_bytes_decode>>%s:%s'%(info[0],info[1])
                        print err_msg
                        log.msg( err_msg,level=log.WARNING)

class ConnectionBuilder(threading.Thread):
    '''
        the buidler will try to connect other machines in hosts.conf,
        it start the urlreceiver thread to setup server for accepting connection
        when ready, the connection has been built up successfully in cloud mode
    '''
    def __init__(self, threadname ):
        print '---init'
        threading.Thread.__init__(self, name = threadname)
        #self.socket_list = socket_list
        self.work_ready = False
        self.dict_no2host = dict()
        self.local_ip = self.get_local_ip()

    def get_localIP(self):
        return self.local_ip

#     def get_local_ip(self,ifname = 'eth1'):  
#         import socket, fcntl, struct  
#         s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  
#         inet = fcntl.ioctl(s.fileno(), 0x8915, struct.pack('256s', ifname[:15]))  
#         ret = socket.inet_ntoa(inet[20:24])  
#         return ret 
    def get_local_ip(self,ethname='eth0'):
        import socket, fcntl, struct
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        inet = fcntl.ioctl(s.fileno(), 0x8915, struct.pack('256s', 'enp8s0'))
        ip = socket.inet_ntoa(inet[20:24])
        return ip
    
    def run(self):
        print '__run'
        self.build_connection()
    def get_partner_urls(self):
        return self.urlreceiver.consume_partner_urls()
    def get_state_ready(self):
        return self.work_ready
    def get_dict_hosts(self):
        return self.dict_no2host
    def read_host_conf(self,file):
        self.dict_no2host.clear()
        i = 0
        with open(file,'r') as fi:
            for line in fi:
                line = line.strip()
                if not line:
                    continue

                if line == self.local_ip:
                    i += 1
                    continue
                self.dict_no2host[i] = line
                i += 1

    def startserver(self):
        self.urlreceiver = URLRcver('url_recv',self.dict_no2host)
        #self.urlreceiver.setDaemon(True)
        self.urlreceiver.start()

    def build_connection(self):
        global g_sock_dict
        self.read_host_conf(HOSTS_CONF)
        print "hosts.conf: ",self.dict_no2host
        #HOST = '192.168.241.10'    # The remote host
        self.startserver()
        PORT = 50007              # The same port as used by the server
        #dict_no2host:存放host.conf内容
        #g_sock_dict：全局变量，存放dict_no2host
        for HOST in self.dict_no2host.values():
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(60)
            while 1:
                try:
                    print 'try connect...',HOST
                    s.connect((HOST, PORT))
                    
                    mylock.acquire()
                    if HOST in g_sock_dict:
                        #has created by sending socket,sending socket has added,[recv,send]
                        ##g_sock_dict：{HOST:['',s]}
                        g_sock_dict[HOST][1] = s
                    else:
                        #g_sock_dict：{HOST:['',s]}
                        g_sock_dict[HOST]=['',s]
                    mylock.release()
                    print 'connected to..',HOST
                    break
                except socket.error as e:
                    time.sleep(1)
                    continue

        print 'checking ready...'
        ready = False
        while not ready:
            time.sleep(0.1)
            if len(g_sock_dict) == len(self.dict_no2host):
                for k,values in g_sock_dict.iteritems():
                    if k in self.dict_no2host.values() and values[0] and values[1]:
                        ready = True
                    else:
                        ready = False
                        break
            else:
                #for k,values in g_sock_dict.iteritems():
                    #print k,values
                print 'socklen:%s'%len(g_sock_dict)
                print 'hostlen"%s'%len(self.dict_no2host)
        
        print 'g_sock_dict: ',g_sock_dict
        self.work_ready = True
        print '##########ready_time:%s'%time.time()

def disp_strategy(link_str,num_nodes,encoding):
    import md5
    try:
        input_str = link_str.encode(encoding,errors='ignore')
        val = int(md5.md5(input_str).hexdigest(),16)
    except UnicodeEncodeError as e:
        log.msg("encode_error_url in:%s(%s)"%(input_str,e.message),level=log.ERROR)
        return 0
    return val%num_nodes

def is_valid_url(url_input):
    url_input=url_input.lower()
    if url_input.endswith('.jpg') | url_input.endswith('.pdf') | url_input.endswith('.doc') | url_input.endswith('.apk') | url_input.endswith('.exe')| url_input.endswith('.xls')| url_input.endswith('.rar') | url_input.endswith('.mht')| url_input.endswith(".png"):
        return False
    return True

#########spider start code#############################
class GeneralSpider(BaseSpider):
    name = "general"
    start_urls = [ ]
    kws = []
#     allowed_domains = ["k.autohome.com.cn"]
    sending = 0
    single_scrapy = False
    
    def open_file(self):
        self.flag = 0
        self.reqes = codecs.open('req.my','a+','utf-8', errors='ignore')
        self.res = codecs.open('response_get.my','a+','utf-8', errors='ignore')
#         self.expand = codecs.open('expand_urls.my', 'a+', 'utf-8', errors='ignore')
#         self.calc = codecs.open('calc_url.my', 'a+', 'utf-8', errors='ignore')
#         self.db_urls = codecs.open('db_urls.my', 'a+', 'utf-8', errors='ignore')
#         self.get_candi = codecs.open('get_candi_urls.my', 'a+', 'utf-8', errors='ignore')
        
    def __init__(self, name=None, **kwargs):
        self.open_file()
        #重连socket
        self.send_to_other_flag = {}
        self.dict_hosts_remove = {}
#         self.g_sock_dict_remove = {}
        
        if not 'seed' in kwargs:
            err =  'failed to find seed file (seed=seeds.dat)'
            print err
            log.msg( err, level=log.ERROR)
            return
        
        if not 'sites' in kwargs:
            err =  'failed to find sites file (seed=sites.dat)'
            print err
            log.msg( err, level=log.ERROR)
            return
        
        if 'single_scrapy' in kwargs:
            if kwargs['single_scrapy'] == 'true':
                self.single_scrapy = True
                
        self.seed_file = kwargs['seed']
        self.sites_file= kwargs['sites']
        self.sites = read_sites(self.sites_file)
        self.req_urls = read_seedfile(self.seed_file)
        reload(sys)
        sys.setdefaultencoding('utf8')
        init_util()
        self.decide_key = KeywordInURL(KEYWORD_IN_URL_FILE)
        super(GeneralSpider,self).__init__(name)
    
    def reload_user_agent(self):
        user_agents=["Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:26.0) Gecko/20100101 Firefox/26.0",
                    "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.114 Safari/537.36",
                    "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.63 Safari/537.36 SE 2.X MetaSr 1.0"
                    ]
#         try:
#             settings.set('USER_AGENT', random.choice(user_agents), priority='cmdline')
#         except AttributeError:
#             settings.overrides['USER_AGENT'] = random.choice(user_agents)
        user_agent = random.choice(user_agents)
        return user_agent
    def start_requests(self):
        info_msg = 'seeds_number:'+str(len(self.req_urls))
        log.msg(info_msg,level=log.INFO)
        print info_msg
        
        if self.single_scrapy == False:
            self.con = ConnectionBuilder('con_builder')
            self.con.setDaemon(True)
            signal.signal(signal.SIGINT, signal_handler)
            signal.signal(signal.SIGTERM, signal_handler)
            self.con.start()
            while 1:
                if self.con.get_state_ready():
                    break
                else:
                    time.sleep(0.1)
                    continue
            self.num_nodes = len(g_sock_dict) + 1
            self.dict_hosts = self.con.get_dict_hosts()
            self.local_ip = self.con.get_localIP()
            #self.sending = len(self.test_urls) 
        
        self.reload_user_agent()
        reqs = []
        db = get_db()
        start_url = "http://www.maixunbytes.com/"
        if self.single_scrapy:
            self.req_urls = self.unsort_seeds()
        for link in self.req_urls:
            if self.single_scrapy:
                db.zadd("plist0"+KEY_FOR_REDIS,0,link)
            else:
                index = disp_strategy(link,self.num_nodes,"UTF-8")
                if not index in self.dict_hosts:
                    db.zadd("plist0"+KEY_FOR_REDIS,0,link)
        user_agent = self.reload_user_agent()
        reqs.append( Request(start_url, callback=self.parse, meta={"handle_httpstatus_all":1,'_depth':0}, headers={'User-Agent':user_agent},dont_filter=False))
        self.sending += 1
        return reqs
    
    def unsort_seeds(self):
        unsort_req_urls = []
        while True:
            if len(self.req_urls)<=0:
                break
            unsort_req_urls.append(self.req_urls.pop(random.randint(0,(len(self.req_urls)-1))))
        return unsort_req_urls
    
    def mysend(self,s, msg):
        totalsent = 0
        msg_len = len(msg)
        while totalsent < msg_len:
            sent = s.send(msg[totalsent:])
            if sent == 0:
                raise RuntimeError("socket connection broken")
            totalsent = totalsent + sent
    
    def retry_conn(self):
        global g_sock_dict
        for index,host in self.dict_hosts_remove.iteritems():
            disconn_time = time.time() - self.send_to_other_flag[index][1]
            if disconn_time>RETRY_CONN:
                #尝试重连
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(60)
                PORT = 50007
                print 'retry connect ...',host
                try:
                    s.connect((host, PORT))
                    self.send_to_other_flag.pop(index)
                    self.dict_hosts.update({index:host})
                    g_sock_dict[host][1] = s
#                     g_sock_dict.update({host:[self.g_sock_dict_remove[host][0],s]})
                    print 'success retry ',host
                    print 'retry connect the lost connect'
                    print 'dict_hosts: ',self.dict_hosts
                    print 'g_sock_dict: ',g_sock_dict
                    print 'dict_hosts_reomve: ',self.dict_hosts_remove
                    print 'send_to_other_flag: ',self.send_to_other_flag
                    raise Exception('remove the lose connect')
                except:
                    self.send_to_other_flag[index][1] = time.time()
                    print 'error retry connect ',host
                    print 'retry error send_to_other_flag: ',self.send_to_other_flag
    
    def dispatch_url(self,sites,encoding,src_url,depth):
        mysites = []
        
        if BBS_POWER:
            sites = bbs_rule(src_url,sites,depth)
        for t_str in sites:
            if self.single_scrapy:
                mysites.append(t_str)
                continue
            index = disp_strategy(t_str,self.num_nodes,encoding)
            # No to host: 0-->192.168.24.3
            global g_sock_dict
            self.retry_conn()
            if index in self.dict_hosts:
                try:
                    host = self.dict_hosts[index]
                    s = g_sock_dict[host][1]
                    if not s:
                        continue
                    sbyte = t_str.encode('utf-8','ignore')
                    try:
#                         s.sendall(sbyte+"\n"+depth+"`")
                        self.mysend(s, sbyte+"\n"+depth+"`")
#                     except socket.error,(value,message):
                    except Exception as e:
                        print "socket.errer: ",host,t_str
                        print e
                        if self.send_to_other_flag.has_key(index):
                            if self.send_to_other_flag[index][0]<SEND_URL_TIMES:
                                self.send_to_other_flag[index][0] = self.send_to_other_flag[index][0]+1
                                print 'error2 send_to_other_flag: ',self.send_to_other_flag
                            if self.send_to_other_flag[index][0]>=SEND_URL_TIMES:
                                if not self.send_to_other_flag[index][1]:
                                    #设置移除index机器的时间
                                    self.send_to_other_flag[index][1] = time.time()
                                    print 'error3 send_to_other_flag: ',self.send_to_other_flag
                                #大于发送失败次数，将该socket连接从连接池中移除
                                if self.dict_hosts.has_key(index):
                                    host = self.dict_hosts[index]
                                    v = self.dict_hosts.pop(index)
                                    self.dict_hosts_remove.update({index:v})
                                    print 'remove the lost connect'
                                    print 'dict_hosts: ',self.dict_hosts
                                    print 'g_sock_dict: ',g_sock_dict
                                    print 'dict_hosts_reomve: ',self.dict_hosts_remove
#                                     print 'g_sock_dict: ',self.g_sock_dict_remove
                                    print 'send_to_other_flag: ',self.send_to_other_flag
                        else:
                            self.send_to_other_flag[index] = [1,'']
                            print 'error1 send_to_other_flag: ',self.send_to_other_flag
                        mysites.append(t_str)
                        
                except KeyError as e:
                    self.socket_error_log = open('socket_error.log','a+')
                    self.socket_error_log.write("/YOU_LOG_MM_SEND_KEY_ERR/: %s\n"%(e))
                    self.socket_error_log.write('index: %s\n'%(index))
                    self.socket_error_log.write('self.dict_hosts: %s\n'%(str(self.dict_hosts)))
                    self.socket_error_log.write('g_sock_dict: %s\n'%(str(g_sock_dict)))
                    self.socket_error_log.flush()
#                     log.msg( "/YOU_LOG_MM_SEND_KEY_ERR/ (%s) not in sock_dict"%(e.message), level=log.ERROR)
#                     log.msg('index: %s'%(index), level=log.ERROR)
#                     log.msg('self.dict_hosts: %s'%(str(self.dict_hosts)), level=log.ERROR)
#                     log.msg('g_sock_dict: %s'%(str(g_sock_dict)), level=log.ERROR)
                    mysites.append(t_str)
                except UnicodeEncodeError as e:
                    log.msg("/YOU_LOG_MM_SEND_ENCODE_ERR/ %s(%s)(type:%s)"%(t_str,e.message,str(type(t_str))),level=log.DEBUG)
            else:
                mysites.append(t_str)

        return mysites

    
    def calc_url(self,base_url, src_urls=[]):
        url_return_set = set()

        for u in src_urls:
            u = u.replace("%20","").strip()
            if not u or u.startswith('#') or u.startswith('javascript'):
                continue
            tmp = ''
            if u.startswith('http:') or u.startswith('https:'):
                tmp = u
            else:
                full_url = urljoin(base_url,u)
                list_url = urlparse.urlparse(full_url)
                path = normpath(list_url.path)
                final_url = urlparse.urlunparse((list_url.scheme,list_url.netloc,path,list_url.params,list_url.query,list_url.fragment))

                if final_url == base_url:
                    continue
                tmp = final_url
                if ':' not in tmp or 'http' not in tmp:
                    continue

            if not is_valid_url(tmp):
                continue

            if ':' not in tmp or 'http' not in tmp:
                continue

            pos = tmp.find("#")
            if pos > -1:
                tmp = tmp[:pos]
                
            if len(tmp)<10:
                continue

            tmp = tmp.encode("UTF-8","ignore")
            base_domain,second_domain = get_base_domain(tmp)
            #parsed  = urlparse.urlparse(tmp)
            #if not is_domain_in_scope(parsed.netloc.encode("utf8")):
            if tmp.find(base_domain) == -1:
                continue
            
            if self.sites!=set([]) and base_domain not in self.sites and second_domain not in self.sites:
                continue
            
            if not do_url_pattern_filter(tmp):
                continue;
            if BBS_POWER:
                tmp = discuz_pipe_line(tmp)
            url_return_set.add(tmp)

        return url_return_set

    def parse(self, response):
        http_code = response.status
        strf_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S %f')
        self.flag = self.flag + 1
        myFlag = 'my_flag_'+str(self.flag)
        try:
            depthFlag = '_depth'+str(response.request.meta['_depth'])
            depthFlag2 = '_depth'+str(response.request.meta['_depth']+1)
        except:
            depthFlag = '_erroFlag'
            depthFlag2 = '_erroFlag2'
        self.res.write('%s ,%s ,%s, %s\n'%(response.url,depthFlag,strf_time,myFlag))
                       
        try:
            encoding = response.encoding
            if encoding.lower() == 'big5':
                content = response.body.strip()
            else:
                content = response.body_as_unicode().strip()
        except AttributeError as e:
            encoding = "UTF-8"
            content = response.body.strip()
        
        page_info= PageMetaItem()
        page_info['url'] = response.url
        page_info['http_code'] = http_code
        page_info['resp_time'] = int(time.time())
        page_info['encoding'] = encoding
        page_info['content'] = content

        yield page_info

        #return no more extending
        if g_quit_flag:
            #log.msg( "quit_in_parse:", level=log.WARNING)
            return

        # bad http_code 
        if http_code >= 200 and http_code < 300:
            cur_depth = response.request.meta['_depth']
            if cur_depth < MAX_DEPTH-1:
                #hxs = HtmlXPathSelector(response)
                hxs = HtmlXPathSelector(text=content)
                global scrapy_version
                if scrapy_version=='new':
                    expand_urls = hxs.xpath('//a/@href').extract()
                elif scrapy_version=='old':
                    expand_urls = hxs.select('//a/@href').extract()
#                 self.expand.write('------------------%s, %s, %s, %s\n'%(len(expand_urls),depthFlag2,myFlag,response.url))
                if BBS_EXPAND_POWER:
                    if check_bbs_page(response.url):
                        expand_urls = []
#                 for expand_url in expand_urls:
#                     self.expand.write('%s\n'%(expand_url))
                #select the url#         total_tmp = total
                valid_sites_set = self.calc_url(response.url,expand_urls)
                if cur_depth < 1:
                    for url in valid_sites_set:
                        item = LinkItem()
                        item['src_url'] = response.url
                        item['url'] = url
                        yield item

                #dispatch to peers and leave my own
                mysites = self.dispatch_url(valid_sites_set,encoding,response.url,str(cur_depth+1))
#                 self.calc.write('------------------%s, %s, %s, %s\n'%(len(mysites),depthFlag2,myFlag,response.url))
#                 for mysite in mysites:
#                     self.calc.write('%s\n'%(mysite))
                
                flag_my = 0
                for url in mysites:
                    url_depth = int(cur_depth) + 1
                    
                    if KEYWORD_POWER:
                        url_flag = self.decide_key.keyword_in_url(url)
                        if url_flag==0:
                            url_depth = 0
                        elif url_flag==1:
                            continue
                    link_flag = check_link_base(url)
                    if not link_flag:
                        continue
                    if check_unfetching(url):
                        continue
                    if check_pending_list(url,url_depth):
                        continue
                    add_to_plist(url, url_depth)
#                     self.db_urls.write('%s\n'%(url))
                    flag_my = flag_my + 1
#                 self.db_urls.write('------------------%s ,%s, %s\n'%(flag_my,depthFlag2,myFlag))
        cnt = self.get_spider_pending_cnt(self.sending)
        if cnt < 2200:
            urls = get_candi_urls(URLS_NUM,HOST_NUM)
#             self.get_candi.write('------------------%s, %s\n'%(len(urls),myFlag))
#             for url in urls:
#                 self.get_candi.write('%s\n'%(url))
            self.sending += len(urls)
            
            for url,layer in urls.items():
                if not url.startswith('http'):
                    self.sending -= 1
                    continue
#                 self.reload_user_agent()
                user_agent = self.reload_user_agent()
                req = Request(url, callback=self.parse,meta={"handle_httpstatus_all":1},headers={'User-Agent':user_agent},dont_filter=False)
                req.meta['_depth'] = layer
                self.reqes.write('%s, %s, %s\n'%(req,'_depth'+str(layer),myFlag))
                yield req

    def get_spider_pending_cnt(self,total):
        global stats_flag
        if stats_flag==0:
            c_stats = stats._stats[self]
            total2 = c_stats['scheduler/memory_enqueued']
        else:
            c_stats = self.crawler.stats.get_stats()
            total2 = c_stats['scheduler/enqueued/memory']
        if "scheduler/disk_enqueued" in c_stats:
            total2 += c_stats['scheduler/disk_enqueued']

        exception_cnt = 0
        rsp_cnt = 0
        if "downloader/response_count" in c_stats:
            rsp_cnt = c_stats['downloader/response_count']
        if "downloader/exception_count" in c_stats:
            exception_cnt = c_stats['downloader/exception_count']
        return total - rsp_cnt - exception_cnt


