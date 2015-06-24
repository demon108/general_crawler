from auto.pattern import PatternSys
import time
import codecs
# pattern = PatternSys()
# s = ['k.autohome.com.cn','autohome.com.cn']
# for u in s:
#     print pattern.pattern(u,u)
#     time.sleep(10)


pattern = codecs.open('test', 'r', 'utf-8', errors='ignore')
print pattern.next()
# print '--------'
if pattern.next() == '\n':
    print '--------'
