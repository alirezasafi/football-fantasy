import scrapy
import json
from scrap_images.spiders.items import Club, Player
from scrap_images.items import ImageItem


class LaligSpider(scrapy.Spider):
    custom_settings = {
        'DOWNLOAD_DELAY': 2,
        'IMAGES_STORE': 'media/laliga',
        'ITEM_PIPELINES': {
            'scrap_images.pipelines.LaligaPipeline': 300
        }
    }
    name = "laliga"
    main_domain = 'https://www.laliga.com'
    clubs_number = 0
    players_stats = {'have_image': 0, 'not_have_image': 0}
    def start_requests(self):
        clubs_url = self.main_domain + '/laliga-santander/clubes'
        yield scrapy.Request(url=clubs_url, callback=self.parse_clubs)

    def parse_clubs(self, response):
        clubs_url = response.xpath('//body/div//div[@class="styled__GridStyled-sc-120de73-0 cfKKJh"]//a[@class="link"][@target="_self"]/@href').getall()
        clubs_name = response.xpath('//body/div//div[@class="styled__GridStyled-sc-120de73-0 cfKKJh"]//h2/text()').getall()
        if len(clubs_name) != 20 and len(clubs_url) != 20:
            print("parse clubs failed")
            return
        for i in range(len(clubs_url)):
            self.data.append(Club(name=clubs_name[i], url=clubs_url[i], players=[]))
        for club in self.data:
            yield scrapy.Request(url=self.main_domain + club['url'], callback=self.parse_club, cb_kwargs=dict(club=club))

    def parse_club(self, response, club):
        print("parse club {}".format(club['name']))
        self.clubs_number += 1
        club_data = json.loads(response.xpath('//body/script[@type="application/json"]/text()').get())
        squads = club_data.get("props").get("pageProps").get("squad").get("squads")
        for player in squads:
            if player.get("role").get("name") != "Jugador":  # not player role
                continue
            name = player.get("person").get("name")
            url = player.get("photos").get("001").get("512x556")
            if not url.split('/')[-3].startswith("p"):  # haven't image
                code = None
                self.players_stats['not_have_image'] += 1
                club['players'].append(Player(name=name, code=code))
            else:
                code = player.get("opta_id")
                self.players_stats['have_image'] += 1
                club['players'].append(Player(name=name, code=code))
                # yield ImageItem(image_name=name, image_urls=url)

        if len(self.data) == self.clubs_number:
            self.data.append("$")
            print("scrape completed.")
            print("downloading...")