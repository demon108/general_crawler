import ctypes

#lib = ctypes.CDLL("./patch.so")
lib = ctypes.CDLL("./scrapy_pattern.so")

lib.init_pfilter()
print lib.do_pfilter("u.fumu.com","home.php?mod=space&do=lama")
#print lib.do_pfilter()
lib.cleanup_pfilter()
'''
print "wp_get_media_type----"
lib.init_wrapper()
print lib.wp_get_media_type("http://www.1313s.com/cgi-bin/topic.cgi?forum=306&topic=576")
print lib.wp_get_media_type("http://blog.ifeng.com/article/4376444.html")
print lib.wp_get_media_type("http://internet.ccw.com.cn/news/search_engine/htm2010/20100225_847998.shtml")
print lib.wp_get_media_type("http://www.baidu.com/test.php")
print "---"
print lib.wp_is_blog_page("http://blog.cnfol.com/cjsh/article/9735612.html")
lib.clean_wrapper()

print  "----domain_scope"
lib.scope_init()
print lib.in_domain_scope("www.maixunbytes.com")
print lib.in_domain_scope("news.sohu.com")
print lib.in_domain_scope("blog.soufun.com")
lib.scope_destory()
'''
