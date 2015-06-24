import urlparse
import sys
import codecs
from urlparse import urljoin
from posixpath import normpath

from mxutil import do_url_pattern_filter
def calc_url(base_url, src_urls=[]):
        url_return_set = set()
        base_domain = get_base_domain(base_url)
        
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
                #log.msg('/YOU_LOG_INVALID_URL/ %s(%s)'%(u,base_url),level=log.DEBUG)
                continue

            pos = tmp.find("#")
            if pos > -1:
                tmp = tmp[:pos]

            tmp = tmp.encode("UTF-8")

            #parsed  = urlparse.urlparse(tmp)
            #if not is_domain_in_scope(parsed.netloc.encode("utf8")):
                #log.msg("/YOU_LOG_MM_SEND_BAD_DOMAIN/ %s"%(tmp), level=log.DEBUG)
            #    continue
            if tmp.find(base_domain) == -1:
                continue
            
            if tmp.find('k.autohome.com.cn') == -1:
                continue
            
            if tmp.find('account.autohome.com.cn') != -1:
                continue
            
            if tmp.find('k.autohome.com.cn/form/carinput/add') != -1:
                continue
            
#             if not do_url_pattern_filter(tmp):
#                 #log.msg('/YOU_LOG_MM_SEND_FILTER_BAD/ %s'%(tmp),level=log.DEBUG)
#                 continue;
            url_return_set.add(tmp)

        return url_return_set
    
    

#autohome.com.cn    
def get_base_domain(url_input):
    print urlparse.urlparse(url_input)
    url_host = urlparse.urlparse(url_input).hostname
    print url_host
    print urlparse.urlparse(url_input).netloc 
    list_host = url_host.split('.')
    tmp=''
    if list_host[-1] == 'cn' and list_host[-2] in ('com','net','gov','org'):
        tmp = '.'.join(url_host.split('.')[-3:])
    else:
        tmp = '.'.join(url_host.split('.')[-2:])
    return tmp

print get_base_domain('http://www.autohome.com.cn/')

# print get_base_domain('http://k.autohome.com.cn/spec/1001')

def is_valid_url(url_input):
    url_input=url_input.lower()
    if url_input.endswith('.jpg') | url_input.endswith('.pdf') | url_input.endswith('.doc') | url_input.endswith('.apk') | url_input.endswith('.exe')| url_input.endswith('.xls')| url_input.endswith('.rar') | url_input.endswith('.mht')| url_input.endswith(".png"):
        return False
    return True

def open_file(filename):
    f = open(filename,'r')


if __name__ == '__main__':
    filename = 'expand_test_urls'
    f = open(filename,'r') 
    urls = [] 
    while True:
        url = f.readline()
        if not url:
            break
        urls.append(url)
    domain = 'http://k.autohome.com.cn/spec/1001'
    valid_sites_set = calc_url(domain,urls)
    fw = codecs.open('test_expand','a+','utf-8', errors='ignore')
    for url_get in valid_sites_set:
        fw.write('%s\n'%url_get)    
        
# base_url = 'http://k.autohome.com.cn'
# u = '/630/'
# url = calc_url(base_url,['../../a.html','/630?key=2'])       
# print url
        
        
        
        

