from bkdbWrapper import BKDB,TWebPageData
from ctypes import *

bkb = BKDB()
bkb.openDb('RawDataY_1406784640.93_28800.db')
desData = TWebPageData()
url = c_char_p()
head = c_char_p()
content = c_char_p()
re = bkb.readRec(desData, url, head, content, 1)
print url.value
print head.value
print content.value