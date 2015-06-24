import re

#forum-viewthread-
# src = "http://bbs.ce.cn/bbs/viewthread.php?tid=420398&extra=page%3D1&page=8&sid=l4ZGtR"
pattern = "(?P<prev>.*)viewthread\\.php\?.*tid=(?P<tid>\\d+)(.*page=(?P<page>\\d+)|.*?)"
re1 = re.compile(pattern)
def __view_thread_a(url):
    global re1
    ret = False
    rst = re1.search(url)
    if rst:
        data = rst.groupdict()
        if data["page"]:
            ret = "%sviewthread.php?tid=%s&page=%s"%(data['prev'],data['tid'],data['page'])
        else:
            ret = "%sviewthread.php?tid=%s"%(data['prev'],data['tid'])
    return ret

# print __view_thread_a(src)

# src = "http://bbs.paipai.com/forum.php?mod=viewthread&tid=2563795&extra=page%3D1&"
pattern = "(?P<prev>.*)forum\\.php\?mod=viewthread.*tid=(?P<tid>\\d+)(.*page=(?P<page>\\d+)|.*?)"
re2 = re.compile(pattern)
def __view_thread_b(url):
    global re2
    ret = False
    rst = re2.search(url)
    if rst:
        data = rst.groupdict()
#         print data
        if data["page"]:
            ret = "%sforum.php?mod=viewthread&tid=%s&page=%s"%(data['prev'],data['tid'],data['page'])
        else:
            ret = "%sforum.php?mod=viewthread&tid=%s"%(data['prev'],data['tid'])
    return ret
# print __view_thread_b(src)

# src = "http://space.aili.com/forum-viewthread-tid-1752943-extra-page%3D1%26orderby%3Ddateline-page-2.html"
pattern = "(?P<prev>.*)forum-viewthread.*tid-(?P<tid>\\d+)(.*page-(?P<page>\\d+).*html|.*html)"
re3 = re.compile(pattern)
def __view_thread_c(url):
    global re3
    ret = False
    rst = re3.search(url)
    if rst:
        data = rst.groupdict()
        print data
        if data["page"]:
            ret = "%sforum-viewthread-tid-%s-page-%s.html"%(data['prev'],data['tid'],data['page'])
        else:
            ret = "%sforum-viewthread-tid-%s.html"%(data['prev'],data['tid'])
    return ret
# print __view_thread_c(src)

#src = "http://bbs.ce.cn/bbs/forumdisplay.php?fid=102&page=6&sid=ph5aZs"
pattern = "(?P<prev>.*)forumdisplay.php\?.*fid=(?P<fid>\\d+)(.*page=(?P<page>\\d+)|.*)"
re4 = re.compile(pattern)
def __forum_a(url):
    global re4
    ret = False
    rst = re4.search(url)
    if rst:
        data = rst.groupdict()
        if data["page"]:
            ret = "%sforumdisplay.php?fid=%s&page=%s"%(data['prev'],data['fid'],data['page'])
        else:
            ret = "%sforumdisplay.php?fid=%s"%(data['prev'],data['fid'])
    return ret

#src = http://piebbs.pconline.com.cn/forum-2_postat.html
#src = http://www.19lou.com/forum-464781-4.html?order=createdat
#src = http://bbs.pcgames.com.cn/forum-28165.html

pattern = "(?P<prev>.*)forum-(?P<p1>\\d+)(-(?P<p2>\\d+).*html|.*html)"
re5 = re.compile(pattern)
def __forum_b(url):
    global re5
    ret = False
    rst = re5.search(url)
    if rst:
        data = rst.groupdict()
        if data["p2"]:
            ret = "%sforum-%s-%s.html"%(data['prev'],data['p1'],data['p2'])
        else:
            ret = "%sforum-%s.html"%(data['prev'],data['p1'])
    return ret

#src = "http://bbs.21cn.com/forum_250_1.html"
#src = "http://club.pchome.net/forum_1_15____md__3_windyboy55.html"
pattern = "(?P<prev>.*)forum_(?P<p1>\\d+)(_(?P<p2>\\d+).*html|.*html)"
re6 = re.compile(pattern)
def __forum_c(url):
    global re6
    ret = False
    rst = re6.search(url)
    if rst:
        data = rst.groupdict()
        if data["p2"]:
            ret = "%sforum_%s_%s.html"%(data['prev'],data['p1'],data['p2'])
        else:
            ret = "%sforum_%s.html"%(data['prev'],data['p1'])
    return ret

#src = "http://www.hupub.com/forum-forumdisplay-fid-29-orderby-lastpost-filter-dateline-dateline-7948800.html"
#src = "http://www.hupub.com/forum-forumdisplay-fid-29-orderby-lastpost-filter-dateline-dateline-7948800-page-2.html"
# pattern = "(?P<prev>.*)forum-forumdisplay-fid-(?P<fid>\\d+)(.*page-(?P<page>\\d+).*html|.*html)"
# re7 = re.compile(pattern)
# def __forum_d(url):
#     global re7
#     ret = False
#     rst = re7.search(url)
#     if rst:
#         data = rst.groupdict()
#         if data["page"]:
#             ret = "%sforum-forumdisplay-fid-%s-page-%s.html"%(data['prev'],data['fid'],data['page'])
#         else:
#             ret = "%sforum-forumdisplay-fid-%s.html"%(data['prev'],data['fid'])
#     return ret

pattern = "(?P<prev>.*)forum-forumdisplay-fid-(?P<fid>\\d+)(.*page-(?P<page>\\d+).*html|.*html)"
re8 = re.compile(pattern)
def __forum_d(url):
    print 'def'
    global re8
    ret = False
    rst = re8.search(url)
    if rst:
        data = rst.groupdict()
        #print data
        if data["page"]:
            ret = "%sforum-forumdisplay-fid-%s-page-%s.html"%(data['prev'],data['fid'],data['page'])
        else:
            ret = "%sforum-forumdisplay-fid-%s.html"%(data['prev'],data['fid'])
    return ret

#src = "http://bbs.21cn.com/forum.php?mod=forumdisplay&fid=1206&isNews=1&operationId=9416"
#src = "http://bbs.21cn.com/forum.php?mod=forumdisplay&fid=1206&isNews=1&operationId=9416&pageNo=2"
#src = "http://bbs.33oz.com/forum.php?mod=forumdisplay&fid=33&page=116"
pattern = "(?P<prev>.*)forum\\.php\?mod=forumdisplay.*fid=(?P<fid>\\d+)(.*(?P<page>page.*=\\d+)|.*)"
re9 = re.compile(pattern)
def __forum_e(url):
    global re9
    ret = False
    rst = re9.search(url)
    if rst:
        data = rst.groupdict()
        if data["page"]:
            ret = "%sforum.php?mod=forumdisplay&fid=%s&%s"%(data['prev'],data['fid'],data['page'])
        else:
            ret = "%sforum.php?mod=forumdisplay&tid=%s"%(data['prev'],data['fid'])
    return ret


# src = "http://club.autohome.com.cn/bbs/forum-c-692-1.html#pvareaid=101061"
pattern = "(?P<prev>.*)forum-(?P<p1>\\w+)-(?P<p2>\\d+)(-(?P<p3>\\d+).*html|.*html)"
re11 = re.compile(pattern)
def __forum_f(url):
    global re11
    ret = False
    rst = re11.search(url)
    if rst:
        data = rst.groupdict()
#         print data
        if data["p3"]:
            ret = "%sforum-%s-%s-%s.html"%(data['prev'],data['p1'],data['p2'],data['p3'])
        else:
            ret = url
    return ret

# print "__thread_b: ", __forum_f(src)

#src = "http://bbs.21cn.com/b268/b268/thread-5354100-1-1.html?ordertype=1"
pattern = "(?P<prev>.*)thread-(?P<p1>\\d+)-(?P<p2>\\d+)(-(?P<p3>\\d+).*html|.*html)"
re10 = re.compile(pattern)
def __thread_a(url):
    global re10
    ret = False
    rst = re10.search(url)
    if rst:
        data = rst.groupdict()
        #print data
        if data["p3"]:
            ret = "%sthread-%s-%s-1.html"%(data['prev'],data['p1'],data['p2'])
        else:
            ret = "%sthread-%s-%s.html"%(data['prev'],data['p1'],data['p2'])
    return ret


def discuz_pipe_line(url):
    rst = False
    while True:
        rst = __view_thread_a(url)
        if rst:
            break
        rst = __view_thread_b(url)
        if rst:
            break
        rst = __view_thread_c(url)
        if rst:
            break
        rst = __thread_a(url)
        if rst:
            break
        rst = __forum_a(url)
        if rst:
            break
        rst = __forum_b(url)
        if rst:
            break
        rst = __forum_c(url)
        if rst:
            break
#         print '---1'
        rst = __forum_d(url)
#         print '----2'
        if rst:
            break
        rst = __forum_e(url)
        if rst:
            break
        break
    
#     print rst
    if rst:
        return rst
    return url

# src = 'http://club.autohome.com.cn/bbs/forum-c-692-1.html#pvareaid=101061'
# print discuz_pipe_line(src)

