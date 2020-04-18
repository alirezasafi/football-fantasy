from scrapy.pipelines.images import ImagesPipeline
from io import BytesIO
from PIL import Image
import scrapy


class PremiesLeaguePipeline(ImagesPipeline):

    def convert_image(self, image, size=None):
        if size:
            image = image.copy()
            image.thumbnail(size, Image.ANTIALIAS)

        buf = BytesIO()
        image.save(buf, 'PNG')
        return image, buf

    def get_media_requests(self, item, info):
        yield scrapy.Request(item.get("image_urls"))

    def file_path(self, request, response=None, info=None):
        player_code = request.url.split('/')[-1]
        return player_code


class LaligaPipeline(PremiesLeaguePipeline):

    def file_path(self, request, response=None, info=None):
        player_code = request.url.split('/')[-3] + ".png"
        return player_code
