import unittest, os, sys
currentdir = os.path.dirname(os.path.abspath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)
from Testcase import AbstractTestCase
from match.models import Match
from compeition.models import Competition
from player.models import Player
import datetime
from club.models import Club
from team.test_team import create_sample_competition, create_sample_clubs, create_sample_players
from config import db


clubs = ['arsenal', 'chelsea', 'bournemouth', 'brighton', 'everton', 'liverpool', 'city', 'butnley']


def create_sample_match(utcdate):
    create_sample_competition()
    create_sample_clubs()
    create_sample_players()
    teams = Club.query.all()[:2]
    players = Player.query.all()[:3]

    match = Match(
        competition_id = 2021,
        utcDate = utcdate,
        lastUpdated = datetime.datetime.utcnow(),
        status = "FINISHED",
        homeTeam_id = teams[0].id,
        awayTeam_id = teams[1].id,
        homeTeamCaptain_id = players[0].id,
        awayTeamCaptain_id = players[1].id
    )
    db.session.add(match)
    db.session.commit()
    return match.id

class TestMatch(AbstractTestCase):
    def test_get_match_list(self):
        match_id = create_sample_match(datetime.datetime.utcnow())
        get_match_response = self.client.get('/match/2021/current-week-matches')
        self.assertTrue(get_match_response.json.get('Matches')[0].get("id") == match_id)
    def test_no_matches_available(self):
        date = datetime.datetime.utcnow() + datetime.timedelta(days=10)
        match_id = create_sample_match(date)
        get_match_response = self.client.get('/match/2021/current-week-matches')
        self.assertTrue(get_match_response.json.get('Matches') == "there are no mathces available.")

if __name__ == "__main__":
    unittest.main()