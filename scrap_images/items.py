import scrapy


class ImageItem(scrapy.Item):
    image_url = scrapy.Field()
    image_name = scrapy.Field()