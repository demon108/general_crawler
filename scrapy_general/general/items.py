# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/topics/items.html

from scrapy.item import Item, Field

class PageMetaItem(Item):
    url = Field()
    http_code = Field()
    content = Field()
    resp_time = Field()
    encoding = Field()
#     flag = Field()
#     depth = Field()

class PendingItem(Item):
    url = Field()
    depth = Field()
    #score = Field() #parent score

class LinkItem(Item):
    src_url = Field()
    url = Field()

