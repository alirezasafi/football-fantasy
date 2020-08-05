import scrapy


class Club(scrapy.Item):
    id = scrapy.Field()
    name = scrapy.Field()
    url = scrapy.Field()
    players = scrapy.Field()


class Player(scrapy.Item):
    name = scrapy.Field()
    code = scrapy.Field()
