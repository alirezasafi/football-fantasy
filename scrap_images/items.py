import scrapy


class ImageItem(scrapy.Item):
    image_urls = scrapy.Field()
    image_name = scrapy.Field()