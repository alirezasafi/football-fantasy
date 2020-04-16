from scrapy.pipelines.images import ImagesPipeline
from io import BytesIO
from PIL import Image
import scrapy


class CustomImagesPipeline(ImagesPipeline):

    def convert_image(self, image, size=None):
        if size:
            image = image.copy()
            image.thumbnail(size, Image.ANTIALIAS)

        buf = BytesIO()
        image.save(buf, 'PNG')
        return image, buf

    def get_media_requests(self, item, info):
        for image_url in item['image_urls']:
            yield scrapy.Request(image_url)

    def file_path(self, request, response=None, info=None):
        player_code = request.url.split('/')[-1]
        return player_code
