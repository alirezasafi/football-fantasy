import scrapy
import os
from scrap_images.spiders.items import Club, Player
from scrap_images.items import ImageItem


class PremiesLeagueSpider(scrapy.Spider):
    custom_settings = {
        'DOWNLOAD_DELAY': 2,
        'IMAGES_STORE': 'media/premier_league',
        'ITEM_PIPELINES': {
            'scrap_images.pipelines.PremiesLeaguePipeline': 300
        }
    }
    clubs_number = 0
    name = "premier_league"
    image_url = "https://resources.premierleague.com/premierleague/photos/players/250x250/{}.png"
    main_domain = 'https://www.premierleague.com'
    downloaded = False

    def start_requests(self):
        if os.path.exists(self.custom_settings.get("IMAGES_STORE")):
            if len(os.listdir(self.custom_settings.get("IMAGES_STORE"))) == 579:
                self.downloaded = True

        clubs_url = self.main_domain + '/clubs'
        yield scrapy.Request(url=clubs_url, callback=self.parse_clubs)

    def parse_clubs(self, response):
        clubs_url = response.xpath('//main[@id="mainContent"]/div[@class="clubIndex"]//li/a/@href').getall()
        clubs_name = response.xpath('//main[@id="mainContent"]/div[@class="clubIndex"]//li/a//h4[@class="clubName"]/text()').getall()
        if len(clubs_name) != 20 and len(clubs_url) != 20:
            print("parse clubs failed")
            return

        for i in range(len(clubs_url)):
            club_url = clubs_url[i].replace('overview', 'squad')
            self.data.append(Club(id=i, name=clubs_name[i], url=club_url, players=[]))
        for club in self.data:
            yield scrapy.Request(url=self.main_domain + club['url'], callback=self.parse_club, cb_kwargs=dict(club=club))

    def parse_club(self, response, club):
        print("parse club {}".format(club['name']))
        self.clubs_number += 1
        players_url = response.xpath('//main[@id="mainContent"]//li/a[@class="playerOverviewCard active"]/@href').getall()
        players_code = response.xpath('//main[@id="mainContent"]//li/a[@class="playerOverviewCard active"]//img/@data-player').getall()
        players_name =response.xpath('//main[@id="mainContent"]//li//span[@class="playerCardInfo"]/h4/text()').getall()
        if len(players_url) == len(players_code) == len(players_name):
            for i in range(len(players_name)):
                club['players'].append(Player(name=players_name[i], code=players_code[i]))
                if not self.downloaded:
                    yield scrapy.Request(url=self.main_domain + players_url[i], callback=self.parse_player)

        if len(self.data) == self.clubs_number:
            self.data.append("$")
            print("scrape completed.")
            print("downloading...")

    def parse_player(self, response):
        name = response.xpath('//main[@id="mainContent"]//div[@class="playerDetails"]/h1/div/text()').get()
        image_code = response.xpath('//main[@id="mainContent"]//div[@class="imgContainer"]/img/@data-player').get()
        yield ImageItem(image_name=name, image_url=self.image_url.format(image_code))
