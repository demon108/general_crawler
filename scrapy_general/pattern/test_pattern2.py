# from you.config import PROJECT
from auto.pattern import PatternSys
import urlparse

f = open("calc_url.my","r")

pattern = PatternSys()
# print urlparse.urlparse('http://k.autohome.com.cn/spec/18431/view_438411_1.html')
# print pattern.pattern(urlparse.urlparse('http://k.autohome.com.cn/spec/18431/view_438411_1.html').netloc, 'http://k.autohome.com.cn/spec/18431/view_438411_1.html')
'''
k.autohome.com.cn`((k.autohome.com.cn/spec/\d+/(?!ge))|(k.autohome.com.cn/spec/\d+/$)|(k.autohome.com.cn/\d+/(?!ge))|(k.autohome.com.cn/\w+/$))`(/\d+/ge\d+|form/carinput)
'''
 
while True:
    line = f.readline()
    if not line:
        break
    if line.startswith("----"):
        continue
     
#     print '============='
    print pattern.pattern(line)
#     print '------------------------'
#     print pattern.is_hub_page(line)
