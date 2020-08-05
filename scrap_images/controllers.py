import crochet
from .api_model import scrap_api
from flask_restplus import Resource
from user.permissions import admin_required
from flask_jwt_extended import jwt_required
from compeition.models import Competition
from scrap_images.spiders.LaligSpider import LaligSpider
from scrap_images.spiders.Bundesliga import BundesligaSpider
from scrap_images.spiders.PremierLeagueSpider import PremiesLeagueSpider
from scrapy.crawler import CrawlerRunner
from club.models import Club
from player.models import Player
from config import db

crawl_runner = CrawlerRunner()
crochet.setup()


@scrap_api.route('/<int:competition_id>')
class ScrapImage(Resource):
    @jwt_required
    @admin_required
    def get(self, competition_id):
        """
        There are 20 clubs and 619 players in site https://www.premierleague.com/
        that 579 players have image.
        There are 20 clubs and 566 player in site https://www.laliga.com/ that
        527 players have image.
        There are 18 clubs and 536 player in site "https://www.bundesliga.com" that
        507 players have image.
        Use this endpoint to download images.
        """

        comp_detail = {2021: {'spider': PremiesLeagueSpider, 'img_path': 'premier_league/'},
                       2014: {'spider': LaligSpider, 'img_path': 'laliga/'},
                       2002: {'spider': BundesligaSpider, 'img_path': 'bundesliga/'}}

        scraped_data_stats = {'clubs': 0, 'players': 0}
        database_stats = {'clubs': 0, 'players': 0}
        not_found_players = []
        competition = Competition.query.filter_by(id=competition_id).first()
        if not competition:
            return {'message': 'competition not fount.'}, 404

        database_stats['clubs'] = competition.clubs.count()
        clubs = competition.clubs.all()
        if not clubs:
            return {'message': "clubs not exist."}, 400
        for club in clubs:
            database_stats['players'] += club.players.count()

        data = []
        scrape_with_crochet(spider=comp_detail[competition_id].get("spider"), data=data)
        while True:
            if len(data) > 0:
                if data[-1] == "$":
                    break
        scraped_data_stats['clubs'] = len(data) - 1

        for club_data in data[0:-1]:
            scraped_data_stats['players'] += len(club_data['players'])
            club = competition.clubs.filter(Club.name.contains(club_data['name'])).first()
            if not club:
                club = self.find_club(competition, club_data['name'])
                if not club:
                    for player_data in club_data['players']:
                        not_found_players.append(player_data)
                    continue
            for player_data in club_data['players']:
                if player_data['code'] is None:
                    path = "default"
                else:
                    path = comp_detail[competition_id].get('img_path') + player_data['code']
                player = club.players.filter(Player.name.contains(player_data['name'])).first()
                if not player:
                    player = self.find_player(club, player_data['name'])
                    if not player:
                        not_found_players.append(player_data)
                        continue

                player.image = path
        db.session.commit()
        data.clear()
        return {"message": "submitted image for {} players".format(
            scraped_data_stats['players'] - len(not_found_players)),
                'scraped_data_stats': scraped_data_stats, 'database_stats': database_stats,
                'not_found_player_in_db': len(not_found_players)}, 200

    def find_club(self, league, club_name):
        for name in club_name.split(' '):
            club = league.clubs.filter(Club.name.contains(name)).first()
            if club:
                return club
        print("club {} not found.".format(club_name))
        return None

    def find_player(self, club, player_name):
        for name in player_name.split(' '):
            player = club.players.filter(Player.name.contains(name)).first()
            if player:
                return player
        print("player {} not found.".format(player_name))
        return None


@crochet.run_in_reactor
def scrape_with_crochet(spider, data):
    crawl_runner.crawl(spider, data=data)
