# -*- encoding:utf-8 -*
import codecs

from scrapy.exceptions import DropItem
class Test(object):
    def __init__(self):
        self.open_file()

    def open_file(self):
            self.reqes = codecs.open('req.my','a+','utf-8', errors='ignore')
            self.res = codecs.open('response_get.my','a+','utf-8', errors='ignore')
            self.expand = codecs.open('expand_urls.my', 'a+', 'utf-8', errors='ignore')
            self.calc = codecs.open('calc_url.my', 'a+', 'utf-8', errors='ignore')
            self.db_urls = codecs.open('db_urls.my', 'a+', 'utf-8', errors='ignore')
            self.get_candi = codecs.open('get_candi_urls.my', 'a+', 'utf-8', errors='ignore')
            
            
            

    def test_write(self):
        str1 = '这是一段测试句子'
        num = 100
        self.reqes.write('%s, %s\n'%(str1,int(num)))


if __name__ == '__main__':
#     test = Test()
#     test.test_write()
    item = "test"
    print DropItem("UNKOWN_ITEM_%s" % str(type(item)))
    
    
    
    
    
    