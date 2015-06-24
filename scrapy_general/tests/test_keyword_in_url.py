# encoding:utf-8
import re
import codecs

from you.config import KEYWERD_IN_URL_FILE

def skip_tag_reader(reader):
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

def compile_keyword_file(filename):
    reader = codecs.open(filename, 'r', 'utf-8','ignore')
    reader,goodquality = skip_tag_reader(reader)
    reader,badquality = skip_tag_reader(reader)
    print goodquality
    print badquality
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
    
def keyword_in_url(url):
#     url = 'http://baidu.com/长城'.decode('utf-8')
    goods,bads = compile_keyword_file(KEYWERD_IN_URL_FILE)
    if goods!=[]:
        for good in goods:
            if good.search(url):
                return 0
    if bads!=[]:
        for bad in bads:
            if bad.search(url):
                return 1
    return 2
    
# tag = keyword_in_url('')
# print tag

