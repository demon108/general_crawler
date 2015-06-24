# encoding:utf-8
import re
import codecs


class KeywordInURL(object):
    
    def __init__(self,filename):
        self.goods,self.bads = self.compile_keyword_file(filename)
        
    def skip_tag_reader(self,reader):
        try:
            line = reader.readline()
            while True:
                if line.startswith('#'):
                    line = reader.readline()
                else:
                    break
            line = line.strip('\n')
        except StopIteration:
            return 
        return reader,line
    
    def compile_keyword_file(self,filename):
        reader = codecs.open(filename, 'r', 'utf-8','ignore')
        reader,goodquality = self.skip_tag_reader(reader)
        reader,badquality = self.skip_tag_reader(reader)
        goods = []
        bads = []
        if goodquality!='':
            good_words = goodquality.split('`')
            for good_word in good_words:
                goods.append(re.compile(good_word.decode('utf-8','ignore')))
        if badquality!='':
            bad_words = badquality.split('`')
            for bad_word in bad_words:
                bads.append(re.compile(bad_word.decode('utf-8','ignore')))
        return goods,bads
        
    def keyword_in_url(self,url):
        if self.goods!=[]:
            for good in self.goods:
                if good.search(url):
                    return 0
        if self.bads!=[]:
            for bad in self.bads:
                if bad.search(url):
                    return 1
        return 2
        

# from you.config import KEYWERD_IN_URL_FILE
# key = KeywordInURL(KEYWERD_IN_URL_FILE)
# print key.goods
# print key.bads
# 
# print key.keyword_in_url('http://baidu.com/长城'.decode('utf-8'))