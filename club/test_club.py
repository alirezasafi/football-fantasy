import unittest, os, sys
currentdir = os.path.dirname(os.path.abspath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir) 
from Testcase import AbstractTestCase
from config import db
from user.models import User
from club.models import Club
from compeition.models import Competition
from flask_jwt_extended import create_access_token
from user.test_user_management import create_sample_user

class TestClubBYCompetition(AbstractTestCase):

    def test_not_found_competition(self):
        access_token = create_sample_user()
        headers = {"authorization":"Bearer %s" % access_token}
        response = self.client.get('club/2021/clubs', headers=headers)
        self.assertTrue(response.json.get('message')=="There's no such competition in database")

    def test_get_clubs_successfuly(self):
        access_token = create_sample_user()
        competition = Competition(
            name = 'la liga',
            id = 2021
        )
        club = Club(
            name = 'barcelona',
            shortName = 'barca',

        )
        db.session.add(competition)
        db.session.add(club)
        db.session.commit()
        competition.clubs.append(club)
        db.session.add(club)
        db.session.commit()
        
        

        headers = {"authorization":"Bearer %s" % access_token}
        response = self.client.get('club/2021/clubs', headers=headers)

        self.assertTrue(response.json.get('clubs')[0].get('name')=="barcelona")
if __name__ == "__main__":
    unittest.main()