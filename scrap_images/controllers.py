import crochet
from .api_model import scrap_api
from flask_restplus import Resource
from user.permissions import admin_required
from flask_jwt_extended import jwt_required
from compeition.models import Competition
from scrap_images.spiders.PremierLeagueSpider import PremiesLeagueSpider
from scrapy.crawler import CrawlerRunner
from club.models import Club
from player.models import Player
from config import db

crawl_runner = CrawlerRunner()
crochet.setup()
premier_data = []


@scrap_api.route('/premier_league')
@scrap_api.doc(doc="")
class PremierLeague(Resource):
    @jwt_required
    @admin_required
    def get(self):
        """
        There are 20 clubs and 619 players in site https://www.premierleague.com/
        that 579 players have image.
        Use this endpoint first to download the images, after that you sure all
        the images have been downloaded use it again to update database.
        the images are saved in 'media/premier_league' path
        """
        scraped_data_stats = {'clubs': 0, 'players': 0}
        database_stats = {'clubs': 0, 'players': 0}
        not_found_players = []
        pl_code = 2021
        premier_league = Competition.query.filter_by(id=pl_code).first()
        if not premier_league:
            return {'message': 'competition not fount.'}, 404

        database_stats['clubs'] = premier_league.clubs.count()
        clubs = premier_league.clubs.all()
        if not clubs:
            return {'message': "clubs not exist."}, 400
        for club in clubs:
            database_stats['players'] += club.players.count()

        global premier_data
        if len(premier_data) == 0:
            scrape_with_crochet(premier_data)
            return {"message": "start premier league scrape."}, 200

        elif premier_data[-1] == "$":
            scraped_data_stats['clubs'] = len(premier_data) - 1

            for club_data in premier_data[0:-1]:
                scraped_data_stats['players'] += len(club_data['players'])
                club = premier_league.clubs.filter(Club.name.contains(club_data['name'])).first()
                if not club:
                    club = self.find_club(premier_league, club_data['name'])
                    if not club:
                        for player_data in club_data['players']:
                            not_found_players.append(player_data)
                        continue
                for player_data in club_data['players']:
                    player = club.players.filter(Player.name.contains(player_data['name'])).first()
                    if not player:
                        player = self.find_player(club, player_data['name'])
                        if not player:
                            not_found_players.append(player_data)
                        continue
                    player.image = "premier_league/" + player_data['code']
            db.session.commit()
            return {"message": "submitted image for {} players".format(scraped_data_stats['players'] - len(not_found_players)),
                    'scraped_data_stats': scraped_data_stats, 'database_stats': database_stats,
                    'not_found_player_in_db': len(not_found_players)}, 200

        return {"message": "premier league scrape in progress."}, 200

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
def scrape_with_crochet(premier_data):
    crawl_runner.crawl(PremiesLeagueSpider, premier_data=premier_data)
