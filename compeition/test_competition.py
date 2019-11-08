import unittest, os, sys
currentdir = os.path.dirname(os.path.abspath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir) 
from Testcase import AbstractTestCase
from config import db
from user.models import User
from flask_jwt_extended import create_access_token
from compeition.models import Competition


class TestCompetitionListView(AbstractTestCase):
    def create_user(self):
        user = User(
            username="asdff",
            password="asdfdf",
            email="sample@gmal.com",
            is_confirmed = True
        )
        db.session.add(user)
        db.session.commit()
        access_token = create_access_token(
            identity={
                "id" : user.id ,
                "username": user.username,
                'is_admin': user.is_admin,
                'email': user.email,
                'is_confirmed':user.is_confirmed
            }
        )
        return access_token

    def test_competition_listview(self):
        access_token = self.create_user()
        competition = Competition(
            name = 'la liga',
            id = 2021
        )
        competition2 = Competition(
            name = 'premier',
            id = 2022
        )
        db.session.add(competition)
        db.session.add(competition2)
        db.session.commit()
        headers = {"authorization":"Bearer %s" % access_token}
        response = self.client.get('competition/list',headers=headers)
        competitions = response.json.get('competitions')
        self.assertTrue('la liga' in competitions[0]['name'] or 'la liga' in competitions[1]['name'])



if __name__ == "__main__":
    unittest.main()
