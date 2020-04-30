import scrapy
from slugify import slugify_de
from scrap_images.spiders.items import Club, Player
from scrap_images.items import ImageItem


class BundesligaSpider(scrapy.Spider):
    custom_settings = {
        'DOWNLOAD_DELAY': 2,
        'IMAGES_STORE': 'media/bundesliga',
        'ITEM_PIPELINES': {
            'scrap_images.pipelines.BundesligaPipline': 300
        }
    }
    name = "bundesliga"
    main_url = 'https://www.bundesliga.com'
    club_url = 'https://www.bundesliga.com/en/bundesliga/clubs/{}/squad'
    player_counter = 0

    def start_requests(self):
        clubs_url = self.main_url + '/en/bundesliga/clubs'
        yield scrapy.Request(url=clubs_url, callback=self.parse_clubs)

    def parse_clubs(self, response):
        clubs_name = response.xpath('//body//clubs-page//club-tile//span[@class="clubName d-none d-md-flex"]/text()').getall()
        if not clubs_name:
            print("clubs not found")
            return

        exception_club_url = "hertha-bsc"  # exception url for hertha berlin.
        for i in range(len(clubs_name)):
            if clubs_name[i] == "Hertha Berlin":
                self.data.append(Club(id=i, name=clubs_name[i], url=exception_club_url, players=[]))
                continue
            self.data.append(Club(id=i, name=clubs_name[i], url=slugify_de(clubs_name[i], to_lower=True), players=[]))

        for club in self.data:
            yield scrapy.Request(url=self.club_url.format(club['url']), callback=self.parse_club, cb_kwargs=dict(club=club))

    def parse_club(self, response, club):
        print("parse club {}".format(club['name']))
        players_url = response.xpath('//body//squad-list//div[@class="playercard"]/a/@href').getall()
        base_code = 1000 + (club['id'] * 100)
        for player_url in players_url:
            player = Player(name="", code="")
            club['players'].append(player)
            yield scrapy.Request(url=self.main_url + player_url, callback=self.parse_player, cb_kwargs=dict(player=player, base_code=base_code))

    def parse_player(self, response, player, base_code):
        self.player_counter += 1
        f_name = response.xpath('//body//div[@class="main"]//header//div[@class="firstName"]/text()').get()
        l_name = response.xpath('//body//div[@class="main"]//header//div[@class="lastName"]/text()').get()
        image_url = response.xpath('//body//div[@class="main"]//header//div[@class="playerImage"]/@style').get()
        shirt_num = response.xpath('//body//div[@class="main"]//header//div[@class="shirtNumberBox"]/text()').get()
        image_url = image_url[image_url.find('https'):-2]
        player['name'] = (str(f_name or "") + " " + str(l_name or "")).lstrip()
        player['code'] = "p{}".format(base_code + int(shirt_num or 0))
        print("{}-parse player {} ...".format(self.player_counter, player['name']))
        yield ImageItem(image_name=player['code'], image_url=image_url)
        if self.player_counter == 536:
            self.data.append("$")
            print("download is complete.")