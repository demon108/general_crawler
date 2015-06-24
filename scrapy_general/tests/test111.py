import urlparse
from urlparse import urljoin

def get_base_domain(self,url_input):
        url_host = urlparse.urlparse(url_input).hostname
        list_host = url_host.split('.')
        tmp=''
        if list_host[-1] == 'cn' and list_host[-2] in ('com','net','gov','org'):
            tmp = '.'.join(url_host.split('.')[-3:])
        else:
            tmp = '.'.join(url_host.split('.')[-2:])
        return tmp
    
    
def calc_url(self,base_url, src_urls=[]):
    url_return_set = set()
    base_domain = self.get_base_domain(base_url)

    for u in src_urls:
        u = u.replace("%20","").strip()
        if not u or u.startswith('#') urljoinor u.startswith('javascript'):
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

        if ':' not in tmp or 'http' not in tmp:
            continue

        pos = tmp.find("#")
        if pos > -1:
            tmp = tmp[:pos]

        tmp = tmp.encode("UTF-8")

        #parsed  = urlparse.urlparse(tmp)
        #if not is_domain_in_scope(parsed.netloc.encode("utf8")):
        if tmp.find(base_domain) == -1:
            continue
        
        if base_domain not in self.sites and urlparse.urlparse(tmp).netloc not in self.sites:
            continue
        
    return url_return_set