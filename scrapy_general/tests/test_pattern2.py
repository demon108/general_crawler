# from you.config import PROJECT
from you.pattern import PatternSys
import urlparse

f = open("calc_url.my","r")

pattern = PatternSys()
# print urlparse.urlparse('http://k.autohome.com.cn/spec/18431/view_438411_1.html')
# print pattern.pattern(urlparse.urlparse('http://k.autohome.com.cn/spec/18431/view_438411_1.html').netloc, 'http://k.autohome.com.cn/spec/18431/view_438411_1.html')
 
while True:
    line = f.readline()
    if not line:
        break
    if line.startswith("----"):
        continue
     
    print '============='
    print pattern.pattern(urlparse.urlparse(line).netloc, line)
    print '------------------------'